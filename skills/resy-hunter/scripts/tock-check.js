#!/usr/bin/env node
// tock-check.js — Query Tock availability using Playwright
// Usage: node tock-check.js <slug> <date> <party_size> [time]
// Output: JSON with restaurant info and available slots
//
// No credentials needed — Tock search pages are public.
// Playwright runs a real browser that passes Cloudflare Turnstile.

const { chromium } = require('playwright');

function formatTo12h(timeStr) {
  const match = timeStr.match(/(\d{1,2}):(\d{2})/);
  if (!match) return { display: timeStr, time_24h: '00:00' };
  const h = parseInt(match[1]);
  const m = match[2];
  const time_24h = `${String(h).padStart(2, '0')}:${m}`;
  let display;
  if (h === 0) display = `12:${m} AM`;
  else if (h < 12) display = `${h}:${m} AM`;
  else if (h === 12) display = `12:${m} PM`;
  else display = `${h - 12}:${m} PM`;
  return { display, time_24h };
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 3) {
    console.error(JSON.stringify({ error: 'Usage: tock-check.js <slug> <date> <party_size> [time]' }));
    process.exit(1);
  }

  const slug = args[0];
  const date = args[1];
  const partySize = parseInt(args[2], 10);
  const time = args[3] || '19:00';

  const tockUrl = `https://www.exploretock.com/${slug}/search?date=${date}&size=${partySize}&time=${time}`;

  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
      ],
    });

    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      viewport: { width: 1280, height: 800 },
    });

    const page = await context.newPage();

    // Navigate to the Tock search page
    await page.goto(tockUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });

    // Wait for either content or Cloudflare challenge
    let blocked = false;
    let waitAttempts = 0;
    const maxWaitAttempts = 6; // 6 x 3s = 18s max wait for Cloudflare

    while (waitAttempts < maxWaitAttempts) {
      // Check if Cloudflare challenge is active
      const isChallengeActive = await page.evaluate(() => {
        return !!(
          document.querySelector('#challenge-running') ||
          document.querySelector('#challenge-stage') ||
          document.querySelector('.cf-challenge') ||
          document.querySelector('[id*="turnstile"]') ||
          document.title.includes('Just a moment') ||
          document.title.includes('Checking')
        );
      });

      if (!isChallengeActive) break;

      await page.waitForTimeout(3000);
      waitAttempts++;
    }

    // Final check — are we still blocked?
    blocked = await page.evaluate(() => {
      return !!(
        document.querySelector('#challenge-running') ||
        document.title.includes('Just a moment') ||
        document.title.includes('Checking')
      );
    });

    let slots = [];

    if (blocked) {
      // Cloudflare won — return URL fallback
      const output = {
        platform: 'tock',
        slug: slug,
        date: date,
        party_size: partySize,
        blocked: true,
        slots: [],
        url: tockUrl,
        message: 'Cloudflare challenge could not be resolved. Check manually.',
      };
      console.log(JSON.stringify(output, null, 2));
      return;
    }

    // Wait a bit for the page to render availability
    await page.waitForTimeout(3000);

    // Strategy 1: Extract __NEXT_DATA__ from the page
    slots = await extractFromNextData(page, date);

    // Strategy 2: Extract from DOM if __NEXT_DATA__ didn't work
    if (slots.length === 0) {
      slots = await extractFromDOM(page, date, slug);
    }

    // Strategy 3: Check for "no availability" messaging
    if (slots.length === 0) {
      const noAvailability = await page.evaluate(() => {
        const text = document.body?.innerText?.toLowerCase() || '';
        return (
          text.includes('no availability') ||
          text.includes('no times available') ||
          text.includes('sold out') ||
          text.includes('no results') ||
          text.includes('not currently accepting') ||
          text.includes('no reservations available')
        );
      });

      if (noAvailability) {
        // Confirmed: no availability
      }
    }

    // Convert all times to 12-hour AM/PM format
    slots = slots.map(s => {
      const fmt = formatTo12h(s.time_start);
      return { ...s, time_start: fmt.display, time_24h: fmt.time_24h };
    });

    const output = {
      platform: 'tock',
      slug: slug,
      date: date,
      party_size: partySize,
      blocked: false,
      slots: slots,
      url: tockUrl,
    };

    console.log(JSON.stringify(output, null, 2));
  } catch (err) {
    console.error(JSON.stringify({
      error: `Tock check failed: ${err.message}`,
      platform: 'tock',
      slug: slug,
      date: date,
      party_size: partySize,
      slots: [],
      url: tockUrl,
    }));
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
}

async function extractFromNextData(page, date) {
  const slots = [];

  try {
    const nextData = await page.evaluate(() => {
      const el = document.querySelector('#__NEXT_DATA__');
      if (!el) return null;
      try {
        return JSON.parse(el.textContent);
      } catch {
        return null;
      }
    });

    if (!nextData) return slots;

    // Traverse the __NEXT_DATA__ structure to find availability
    const props = nextData.props?.pageProps;
    if (!props) return slots;

    // Look for slots/availability/experiences in various locations
    const searchPaths = [
      props.availabilities,
      props.availability,
      props.searchResults,
      props.experiences,
      props.timeslots,
      props.slots,
      props.initialData?.availability,
      props.initialData?.searchResults,
      props.dehydratedState?.queries?.[0]?.state?.data,
    ];

    for (const candidate of searchPaths) {
      if (!candidate) continue;

      const items = Array.isArray(candidate) ? candidate : [candidate];
      for (const item of items) {
        if (Array.isArray(item)) {
          // Array of slot objects
          for (const slot of item) {
            const parsed = parseTockSlot(slot, date);
            if (parsed) slots.push(parsed);
          }
        } else if (item && typeof item === 'object') {
          // Might be a single slot or an object with nested slots
          if (item.time || item.dateTime || item.startTime) {
            const parsed = parseTockSlot(item, date);
            if (parsed) slots.push(parsed);
          }
          // Check for nested arrays
          for (const key of Object.keys(item)) {
            if (Array.isArray(item[key])) {
              for (const slot of item[key]) {
                const parsed = parseTockSlot(slot, date);
                if (parsed) slots.push(parsed);
              }
            }
          }
        }
      }
    }
  } catch (e) {
    // __NEXT_DATA__ extraction failed
  }

  return slots;
}

function parseTockSlot(slot, date) {
  if (!slot || typeof slot !== 'object') return null;

  const time = slot.time || slot.dateTime || slot.startTime || slot.start_time || slot.startDate;
  if (!time) return null;

  let timeStart = time;
  // If time is just "19:00" or "7:00 PM", prepend date
  if (!timeStart.includes('T') && !timeStart.includes('-')) {
    // Try parsing AM/PM
    const match = timeStart.match(/(\d{1,2}):(\d{2})\s*(AM|PM)?/i);
    if (match) {
      let hours = parseInt(match[1]);
      const mins = match[2];
      const period = (match[3] || '').toUpperCase();
      if (period === 'PM' && hours !== 12) hours += 12;
      if (period === 'AM' && hours === 12) hours = 0;
      timeStart = `${date}T${String(hours).padStart(2, '0')}:${mins}`;
    } else {
      timeStart = `${date}T${time}`;
    }
  }

  return {
    time_start: timeStart,
    type: slot.type || slot.experienceName || slot.experience_name || slot.name || slot.mealType || 'Standard',
  };
}

async function extractFromDOM(page, date, slug) {
  const slots = [];

  try {
    const domSlots = await page.evaluate((targetDate) => {
      const results = [];

      // Tock uses various selectors for time slots
      const selectors = [
        '[class*="TimeSlot"]',
        '[class*="timeslot"]',
        '[class*="time-slot"]',
        'button[class*="slot"]',
        '[data-testid*="time"]',
        '[data-testid*="slot"]',
        '[class*="SearchResult"]',
        '[class*="search-result"]',
        '[class*="AvailableTime"]',
        'a[href*="/book"]',
        'button[data-time]',
      ];

      const elements = document.querySelectorAll(selectors.join(', '));

      for (const el of elements) {
        const text = el.textContent?.trim();
        const dataTime = el.getAttribute('data-time') || el.getAttribute('data-datetime');

        if (!text && !dataTime) continue;

        let time = dataTime || '';
        if (!time && text) {
          // Parse time from text like "7:30 PM" or "19:30"
          const match = text.match(/(\d{1,2}):(\d{2})\s*(AM|PM)?/i);
          if (match) {
            let hours = parseInt(match[1]);
            const mins = match[2];
            const period = (match[3] || '').toUpperCase();
            if (period === 'PM' && hours !== 12) hours += 12;
            if (period === 'AM' && hours === 12) hours = 0;
            time = `${targetDate}T${String(hours).padStart(2, '0')}:${mins}`;
          }
        }

        if (time) {
          // Try to get experience type from context
          const parent = el.closest('[class*="experience"], [class*="section"]');
          const typeEl = parent?.querySelector('[class*="title"], [class*="name"], h2, h3');
          const type = typeEl?.textContent?.trim() || 'Standard';

          results.push({
            time_start: time,
            type: type,
          });
        }
      }

      // Fallback: look for any time-like text in list items or buttons
      if (results.length === 0) {
        const allButtons = document.querySelectorAll('button, a[role="button"], [role="option"]');
        for (const btn of allButtons) {
          const text = btn.textContent?.trim();
          if (!text) continue;

          const match = text.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
          if (match) {
            let hours = parseInt(match[1]);
            const mins = match[2];
            const period = match[3].toUpperCase();
            if (period === 'PM' && hours !== 12) hours += 12;
            if (period === 'AM' && hours === 12) hours = 0;
            results.push({
              time_start: `${targetDate}T${String(hours).padStart(2, '0')}:${mins}`,
              type: 'Standard',
            });
          }
        }
      }

      // Deduplicate
      const seen = new Set();
      return results.filter((s) => {
        if (seen.has(s.time_start)) return false;
        seen.add(s.time_start);
        return true;
      });
    }, date);

    slots.push(...domSlots);
  } catch (e) {
    // DOM extraction failed
  }

  return slots;
}

main();
