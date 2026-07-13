#!/usr/bin/env node
// opentable-check.js — Query OpenTable availability using Playwright
// Usage: node opentable-check.js <restaurant_id> <date> <party_size> [time]
// Output: JSON with restaurant info and available slots
//
// Uses saved session from opentable-login.js (manual login flow).
// Session file: ~/.openclaw/data/resy-hunter/opentable-session.json
// If session is missing or expired, returns {session_expired: true}.

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const DATA_DIR = path.join(process.env.HOME, '.openclaw/data/resy-hunter');
const SESSION_FILE = path.join(DATA_DIR, 'opentable-session.json');

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
    console.error(JSON.stringify({ error: 'Usage: opentable-check.js <restaurant_id> <date> <party_size> [time]' }));
    process.exit(1);
  }

  const restaurantId = args[0];
  const date = args[1];
  const partySize = parseInt(args[2], 10);
  const time = args[3] || '19:00';

  // Check for saved session
  if (!fs.existsSync(SESSION_FILE)) {
    console.log(JSON.stringify({
      platform: 'opentable',
      restaurant_id: restaurantId,
      date: date,
      party_size: partySize,
      slots: [],
      session_expired: true,
      message: 'No OpenTable session found. Run opentable-login.js to authenticate.',
    }));
    return;
  }

  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
      ],
    });

    // Load saved session
    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      viewport: { width: 1280, height: 800 },
      storageState: SESSION_FILE,
    });

    const page = await context.newPage();

    // Collect availability data from network responses
    let availabilityData = null;

    page.on('response', async (response) => {
      const url = response.url();
      if (url.includes('/availability') || url.includes('/dtp') || url.includes('timeslots')) {
        try {
          const contentType = response.headers()['content-type'] || '';
          if (contentType.includes('json') && response.status() === 200) {
            const data = await response.json();
            if (!availabilityData) {
              availabilityData = data;
            }
          }
        } catch (e) {
          // Non-JSON response, skip
        }
      }
    });

    // Build the OpenTable URL
    const dateTime = `${date}T${time}`;
    const otUrl = `https://www.opentable.com/restref/client/?rid=${restaurantId}&restref=${restaurantId}&datetime=${dateTime}&covers=${partySize}&searchdatetime=${dateTime}&partysize=${partySize}`;

    await page.goto(otUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });

    // Check if session expired (login wall detected)
    await page.waitForTimeout(3000);
    const sessionExpired = await detectLoginWall(page);

    if (sessionExpired) {
      console.log(JSON.stringify({
        platform: 'opentable',
        restaurant_id: restaurantId,
        date: date,
        party_size: partySize,
        slots: [],
        session_expired: true,
        message: 'OpenTable session expired. Run opentable-login.js to re-authenticate.',
      }));
      await browser.close();
      return;
    }

    // Wait for availability to load
    await page.waitForTimeout(5000);

    // Extract slots
    let slots = [];

    if (availabilityData) {
      slots = parseAvailabilityResponse(availabilityData, date);
    }

    if (slots.length === 0) {
      slots = await extractSlotsFromDOM(page, date);
    }

    // Refresh session for next run
    try {
      await context.storageState({ path: SESSION_FILE });
    } catch (e) {
      // Non-critical
    }

    // Convert times to 12-hour format
    slots = slots.map(s => {
      const fmt = formatTo12h(s.time_start);
      return { ...s, time_start: fmt.display, time_24h: fmt.time_24h };
    });

    const output = {
      platform: 'opentable',
      restaurant_id: restaurantId,
      date: date,
      party_size: partySize,
      slots: slots,
      url: `https://www.opentable.com/restref/client/?rid=${restaurantId}&restref=${restaurantId}&datetime=${dateTime}&covers=${partySize}`,
    };

    console.log(JSON.stringify(output, null, 2));
  } catch (err) {
    console.error(JSON.stringify({
      error: `OpenTable check failed: ${err.message}`,
      platform: 'opentable',
      restaurant_id: restaurantId,
      date: date,
      party_size: partySize,
      slots: [],
    }));
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
}

async function detectLoginWall(page) {
  try {
    const isOnLogin = page.url().includes('login') || page.url().includes('signin') || page.url().includes('/auth/');
    if (isOnLogin) return true;

    const loginForm = await page.$('input[type="email"], input[name="email"], #Email');
    const loginButton = await page.$('button[data-test="login-button"], a[href*="login"], #login-button, [data-test="sign-in"]');
    if (loginForm && loginButton) return true;

    return false;
  } catch (e) {
    return false;
  }
}

function parseAvailabilityResponse(data, date) {
  const slots = [];

  try {
    if (data.availability && Array.isArray(data.availability)) {
      for (const slot of data.availability) {
        const timeStr = slot.datetime || slot.time || slot.dateTime;
        if (timeStr) {
          slots.push({
            time_start: timeStr,
            type: slot.type || slot.areaName || 'Standard',
          });
        }
      }
    }

    if (data.times && Array.isArray(data.times)) {
      for (const slot of data.times) {
        slots.push({
          time_start: slot.dateTime || slot.time || `${date}T${slot.timeString}`,
          type: slot.type || slot.experienceType || 'Standard',
        });
      }
    }

    if (data.data) {
      const nested = data.data.availability || data.data.times || data.data.timeslots;
      if (Array.isArray(nested)) {
        for (const slot of nested) {
          const timeStr = slot.datetime || slot.dateTime || slot.time;
          if (timeStr) {
            slots.push({
              time_start: timeStr,
              type: slot.type || slot.areaName || 'Standard',
            });
          }
        }
      }
    }

    if (data.timeslots && Array.isArray(data.timeslots)) {
      for (const slot of data.timeslots) {
        slots.push({
          time_start: slot.dateTime || slot.time,
          type: slot.experienceType || slot.type || 'Standard',
        });
      }
    }
  } catch (e) {
    // Parsing failed
  }

  return slots;
}

async function extractSlotsFromDOM(page, date) {
  const slots = [];

  try {
    const slotData = await page.evaluate((targetDate) => {
      const results = [];
      const timeElements = document.querySelectorAll(
        '[data-test*="time"], [class*="timeslot"], [class*="time-slot"], ' +
        'button[class*="slot"], a[class*="slot"], ' +
        '[data-test="availability-time"], [class*="TimeSlot"], ' +
        'button[data-time], [data-timeslot]'
      );

      for (const el of timeElements) {
        const timeText = el.textContent?.trim();
        const dataTime = el.getAttribute('data-time') || el.getAttribute('data-timeslot') || el.getAttribute('data-datetime');

        if (timeText || dataTime) {
          let time = dataTime || '';
          if (!time && timeText) {
            const match = timeText.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
            if (match) {
              let hours = parseInt(match[1]);
              const mins = match[2];
              const period = match[3].toUpperCase();
              if (period === 'PM' && hours !== 12) hours += 12;
              if (period === 'AM' && hours === 12) hours = 0;
              time = `${targetDate}T${String(hours).padStart(2, '0')}:${mins}`;
            }
          }

          if (time) {
            const parent = el.closest('[class*="area"], [class*="section"], [data-test*="area"]');
            const type = parent?.getAttribute('data-area') || parent?.querySelector('[class*="area-name"], [class*="section-title"]')?.textContent?.trim() || 'Standard';

            results.push({
              time_start: time,
              type: type,
            });
          }
        }
      }

      const seen = new Set();
      return results.filter((s) => {
        const key = s.time_start;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
    }, date);

    slots.push(...slotData);
  } catch (e) {
    // DOM extraction failed
  }

  return slots;
}

main();
