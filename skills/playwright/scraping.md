# Scraping Patterns

## Basic Extraction

```typescript
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('https://example.com/products');

const products = await page.$$eval('.product-card', cards =>
  cards.map(card => ({
    name: card.querySelector('.name')?.textContent?.trim(),
    price: card.querySelector('.price')?.textContent?.trim(),
    url: card.querySelector('a')?.href,
  }))
);

await browser.close();
```

## Wait Strategies for SPAs

```typescript
// Wait for specific element
await page.waitForSelector('[data-loaded="true"]');

// Wait for network idle (careful with SPAs)
await page.goto(url, { waitUntil: 'networkidle' });

// Wait for loading indicator to disappear
await page.waitForSelector('.loading-spinner', { state: 'hidden' });

// Custom condition with polling
await expect.poll(async () => {
  return await page.locator('.product').count();
}).toBeGreaterThan(0);
```

## Infinite Scroll

```typescript
async function scrollToBottom(page: Page) {
  let previousHeight = 0;
  
  while (true) {
    const currentHeight = await page.evaluate(() => document.body.scrollHeight);
    if (currentHeight === previousHeight) break;
    
    previousHeight = currentHeight;
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForLoadState('domcontentloaded');
  }
}
```

## Pagination

```typescript
// Click-based pagination
async function scrapeAllPages(page: Page) {
  const allData = [];
  
  while (true) {
    const pageData = await extractData(page);
    allData.push(...pageData);
    
    const nextButton = page.getByRole('button', { name: 'Next' });
    if (await nextButton.isDisabled()) break;
    
    await nextButton.click();
    await page.waitForLoadState('networkidle');
  }
  
  return allData;
}
```

## Session Persistence

```typescript
// Save cookies and localStorage for later reuse
await context.storageState({ path: 'session.json' });

// Restore session in new context
const context = await browser.newContext({
  storageState: 'session.json',
});
```

## Error Handling with Retries

```typescript
async function scrapeWithRetry(url: string, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const page = await context.newPage();
      await page.goto(url, { timeout: 30000 });
      return await extractData(page);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(r => setTimeout(r, 2000 * (i + 1)));
    } finally {
      await page.close();
    }
  }
}
```

## Rate Limiting (Be Respectful)

```typescript
class RateLimiter {
  private lastRequest = 0;
  
  constructor(private minDelay: number) {}
  
  async wait() {
    const elapsed = Date.now() - this.lastRequest;
    if (elapsed < this.minDelay) {
      await new Promise(r => setTimeout(r, this.minDelay - elapsed));
    }
    this.lastRequest = Date.now();
  }
}

const limiter = new RateLimiter(2000);  // 2s between requests

for (const url of urls) {
  await limiter.wait();
  await scrape(url);
}
```

## Structured Data Extraction

```typescript
// Extract with JSON-LD
const jsonLd = await page.$eval(
  'script[type="application/ld+json"]',
  el => JSON.parse(el.textContent || '{}')
);

// Extract table to array
const tableData = await page.$$eval('table tbody tr', rows =>
  rows.map(row => 
    Array.from(row.querySelectorAll('td')).map(td => td.textContent?.trim())
  )
);
```
