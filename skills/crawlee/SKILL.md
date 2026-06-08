---
name: crawlee
description: >
  Expert guide for building web scrapers and crawlers using Crawlee (JavaScript/TypeScript and Python).
  Use this skill whenever the user wants to: scrape a website, build a web crawler, extract data from web pages,
  automate browser navigation, handle anti-bot blocking, manage proxies or sessions for scraping, use
  Playwright/Puppeteer/Cheerio/BeautifulSoup for web data extraction, crawl sitemaps, download files from URLs,
  or deploy a scraper to the cloud. Trigger even for loosely related phrases like "get data from a website",
  "automate browser", "scrape prices", "extract links", "crawl URLs", or "bypass bot detection".
  Covers CheerioCrawler, PlaywrightCrawler, PuppeteerCrawler, HttpCrawler, JSDOMCrawler (JS),
  and BeautifulSoupCrawler, ParselCrawler, PlaywrightCrawler (Python).
---

# Crawlee Skill

Crawlee is a production-grade web scraping and browser automation library for **JavaScript/TypeScript** (Node.js 16+)
and **Python** (3.10+). It handles anti-blocking, proxies, session management, storage, and concurrency out of the box.

> **Docs**: https://crawlee.dev/js/docs | https://crawlee.dev/python/docs  
> **GitHub**: https://github.com/apify/crawlee

---

## 1. Choose Your Crawler

### JavaScript / TypeScript

| Crawler | When to Use | JS Required |
|---|---|---|
| `CheerioCrawler` | Fast HTML parsing, no JS rendering needed | ❌ |
| `HttpCrawler` | Raw HTTP responses, custom parsing | ❌ |
| `JSDOMCrawler` | DOM manipulation without full browser | ❌ |
| `PlaywrightCrawler` | Modern headless browser (Chromium/Firefox/WebKit) | ✅ |
| `PuppeteerCrawler` | Chromium/Chrome headless automation | ✅ |
| `AdaptivePlaywrightCrawler` | Auto-detects if JS rendering is needed | Auto |
| `BasicCrawler` | Custom HTTP logic from scratch | ❌ |

**Rule of thumb**: Start with `CheerioCrawler`. Upgrade to `PlaywrightCrawler` only when JS rendering is required.

### Python

| Crawler | When to Use |
|---|---|
| `BeautifulSoupCrawler` | HTML parsing with BeautifulSoup (fast, no JS) |
| `ParselCrawler` | CSS/XPath selectors, Scrapy-style (fast, no JS) |
| `PlaywrightCrawler` | Full browser automation (Chromium/Firefox/WebKit) |
| `AdaptivePlaywrightCrawler` | Auto HTTP vs browser decision |

---

## 2. Installation

### JavaScript
```bash
# Recommended: use the CLI
npx crawlee create my-crawler
cd my-crawler && npm install

# Or manually:
npm install crawlee

# For Playwright:
npm install crawlee playwright
npx playwright install

# For Puppeteer:
npm install crawlee puppeteer
```

Add to `package.json`:
```json
{ "type": "module" }
```

### Python
```bash
pip install crawlee

# With BeautifulSoup:
pip install 'crawlee[beautifulsoup]'

# With Playwright:
pip install 'crawlee[playwright]'
playwright install
```

---

## 3. Core Concepts

### The Two Questions Every Crawler Answers
1. **Where to go?** → `Request` objects in a `RequestQueue`
2. **What to do there?** → `requestHandler` function (JS) / decorated handler (Python)

### Key Classes (JS)
- `Request` — A single URL + metadata to crawl
- `RequestQueue` — Dynamic, deduplicated queue of URLs
- `Dataset` — Append-only structured result storage (like a table)
- `KeyValueStore` — Blob storage for screenshots, PDFs, state
- `ProxyConfiguration` — Manages proxy rotation
- `SessionPool` — Manages browser sessions + cookies

---

## 4. Quick Start Examples

### JavaScript — CheerioCrawler (Recommended Start)
```javascript
import { CheerioCrawler, Dataset } from 'crawlee';

const crawler = new CheerioCrawler({
  async requestHandler({ $, request, enqueueLinks, log }) {
    const title = $('title').text();
    log.info(`Title of ${request.loadedUrl}: ${title}`);

    await Dataset.pushData({ url: request.loadedUrl, title });

    // Enqueue all links found on this page
    await enqueueLinks();
  },
  maxRequestsPerCrawl: 100, // Safety limit
});

await crawler.run(['https://example.com']);
```

### JavaScript — PlaywrightCrawler
```javascript
import { PlaywrightCrawler, Dataset } from 'crawlee';

const crawler = new PlaywrightCrawler({
  // headless: false, // Uncomment to see the browser
  async requestHandler({ page, request, enqueueLinks, log }) {
    const title = await page.title();
    log.info(`${request.loadedUrl}: ${title}`);
    await Dataset.pushData({ url: request.loadedUrl, title });
    await enqueueLinks();
  },
});

await crawler.run(['https://example.com']);
```

### Python — BeautifulSoupCrawler
```python
import asyncio
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

async def main() -> None:
    crawler = BeautifulSoupCrawler(max_requests_per_crawl=50)

    @crawler.router.default_handler
    async def handler(context: BeautifulSoupCrawlingContext) -> None:
        title = context.soup.title.string if context.soup.title else None
        context.log.info(f'Processing {context.request.url}: {title}')
        await context.push_data({'url': context.request.url, 'title': title})
        await context.enqueue_links()

    await crawler.run(['https://example.com'])

if __name__ == '__main__':
    asyncio.run(main())
```

### Python — PlaywrightCrawler
```python
import asyncio
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

async def main() -> None:
    crawler = PlaywrightCrawler(headless=True, browser_type='chromium')

    @crawler.router.default_handler
    async def handler(context: PlaywrightCrawlingContext) -> None:
        title = await context.page.title()
        await context.push_data({'url': context.request.url, 'title': title})
        await context.enqueue_links()

    await crawler.run(['https://example.com'])

if __name__ == '__main__':
    asyncio.run(main())
```

---

## 5. Routing — Handling Multiple Page Types

Use labels + router to handle different kinds of pages (list pages, detail pages, etc.).

### JavaScript
```javascript
import { PlaywrightCrawler, Dataset } from 'crawlee';
import { router } from './routes.js';

const crawler = new PlaywrightCrawler({ requestHandler: router });

await crawler.run([{ url: 'https://shop.example.com', label: 'START' }]);
```

```javascript
// routes.js
import { createPlaywrightRouter } from 'crawlee';

export const router = createPlaywrightRouter();

router.addHandler('START', async ({ page, enqueueLinks }) => {
  await enqueueLinks({ selector: 'a.category', label: 'CATEGORY' });
});

router.addHandler('CATEGORY', async ({ page, enqueueLinks }) => {
  await enqueueLinks({ selector: 'a.product', label: 'DETAIL' });
  // Enqueue next page
  const next = await page.$('a.next-page');
  if (next) await enqueueLinks({ selector: 'a.next-page', label: 'CATEGORY' });
});

router.addDefaultHandler(async ({ page, request, pushData }) => {
  // DETAIL pages
  const title = await page.title();
  const price = await page.$eval('.price', el => el.textContent);
  await pushData({ url: request.url, title, price });
});
```

### Python
```python
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

crawler = BeautifulSoupCrawler()

@crawler.router.handler('CATEGORY')
async def category_handler(context: BeautifulSoupCrawlingContext) -> None:
    await context.enqueue_links(selector='a.product', label='DETAIL')

@crawler.router.default_handler
async def detail_handler(context: BeautifulSoupCrawlingContext) -> None:
    title = context.soup.title.string
    await context.push_data({'url': context.request.url, 'title': title})
```

---

## 6. Enqueuing Links

### JavaScript — `enqueueLinks()`
```javascript
// Enqueue all links on page
await enqueueLinks();

// Filter by glob pattern
await enqueueLinks({ globs: ['https://example.com/products/**'] });

// Filter by regex
await enqueueLinks({ regexps: [/\/product\/\d+/] });

// Enqueue only specific selector
await enqueueLinks({ selector: 'a.pagination', label: 'LIST' });

// Enqueue with custom label and transformations
await enqueueLinks({
  selector: 'a.item',
  label: 'DETAIL',
  transformRequestFunction: (req) => {
    req.userData.scrapedAt = new Date().toISOString();
    return req;
  },
});
```

### Python
```python
await context.enqueue_links()
await context.enqueue_links(selector='a.product', label='DETAIL')
await context.enqueue_links(include=[re.compile(r'/products/\d+')])
```

---

## 7. Storage

### Dataset (structured results)
```javascript
// JS — Write
await Dataset.pushData({ url, title, price });
await Dataset.pushData([item1, item2, item3]); // batch write

// JS — Read / Export
const dataset = await Dataset.open();
await dataset.exportToCSV('results'); // saves to KV store
await dataset.exportToJSON('results');

for await (const item of dataset) { console.log(item); }
```

```python
# Python — Write
await context.push_data({'url': url, 'title': title})

# Python — Read / Export
from crawlee.storages import Dataset
dataset = await Dataset.open()
await dataset.export_to(key='results', content_type='csv')
```

Data is saved to `./storage/datasets/default/*.json` by default.

### KeyValueStore (blobs, screenshots, state)
```javascript
// JS
await KeyValueStore.setValue('OUTPUT', { results: [...] });
const value = await KeyValueStore.getValue('OUTPUT');

// Save a screenshot
const store = await KeyValueStore.open();
await store.setValue('screenshot', await page.screenshot(), { contentType: 'image/png' });
```

```python
# Python
from crawlee.storages import KeyValueStore
kvs = await KeyValueStore.open()
await kvs.set_value('result', {'data': 'value'})
value = await kvs.get_value('result')
```

### Storage location
```
./storage/
  datasets/default/     # Dataset rows as JSON files
  key_value_stores/default/  # KV store entries
  request_queues/default/    # Request queue state
```

Override with env var: `CRAWLEE_STORAGE_DIR=/path/to/storage`

---

## 8. Proxy Management

```javascript
// JS — Basic proxy rotation
import { ProxyConfiguration } from 'crawlee';

const proxyConfiguration = new ProxyConfiguration({
  proxyUrls: [
    'http://user:pass@proxy1.example.com:8000',
    'http://user:pass@proxy2.example.com:8000',
  ],
});

const crawler = new CheerioCrawler({
  proxyConfiguration,
  useSessionPool: true,
  persistCookiesPerSession: true,
  async requestHandler({ proxyInfo, request }) {
    console.log('Using proxy:', proxyInfo?.url);
  },
});
```

```javascript
// JS — Tiered proxies (smart cost/reliability balancing)
const proxyConfiguration = new ProxyConfiguration({
  tieredProxyUrls: [
    [null],                              // Tier 0: no proxy (cheapest)
    ['http://cheap-datacenter-proxy'],   // Tier 1: datacenter
    ['http://expensive-residential'],    // Tier 2: residential (most reliable)
  ],
});
// Crawlee auto-escalates tiers when blocking is detected, then drops back when clear
```

```python
# Python
from crawlee.proxy_configuration import ProxyConfiguration

proxy_configuration = ProxyConfiguration(
    proxy_urls=['http://proxy1.com/', 'http://proxy2.com/'],
)
crawler = BeautifulSoupCrawler(
    proxy_configuration=proxy_configuration,
    use_session_pool=True,
)
```

---

## 9. Session Management

Sessions tie together cookies, proxy IPs, and headers to simulate a consistent user identity.

```javascript
// JS
const crawler = new CheerioCrawler({
  useSessionPool: true,         // Enable (default: true)
  persistCookiesPerSession: true,
  sessionPoolOptions: { maxPoolSize: 100 },

  async requestHandler({ session, $ }) {
    const title = $('title').text();
    if (title === 'Access Denied') {
      session?.retire();  // Mark this IP+cookie combo as blocked
    } else if (title === 'Slow') {
      session?.markBad(); // Penalize but don't retire
    }
    // session.markGood() is called automatically on success
  },
});
```

```python
# Python
from crawlee.sessions import SessionPool

crawler = BeautifulSoupCrawler(
    use_session_pool=True,
    session_pool=SessionPool(max_pool_size=100),
)

@crawler.router.default_handler
async def handler(context: BeautifulSoupCrawlingContext) -> None:
    title = context.soup.title.string if context.soup.title else ''
    if title == 'Access Denied':
        context.session.retire()
```

---

## 10. Avoiding Blocks

```javascript
// JS — Playwright with fingerprint rotation (built-in, zero config needed)
const crawler = new PlaywrightCrawler({
  // Fingerprints automatically randomized by default in Playwright/Puppeteer crawlers
  // headless: false,  // Use headful for harder targets
  async requestHandler({ page }) {
    // Add realistic delays
    await page.waitForTimeout(1000 + Math.random() * 2000);
  },
});

// Use got-scraping for HTTP (built into CheerioCrawler/HttpCrawler)
// It automatically sets realistic headers and TLS fingerprints
```

**Anti-blocking checklist:**
- ✅ Use `CheerioCrawler` — it uses `got-scraping` which mimics real browser HTTP
- ✅ Enable `useSessionPool: true` with a `proxyConfiguration`
- ✅ Use tiered proxies for automatic failover
- ✅ Set `maxRequestsPerMinute` to avoid rate limits
- ✅ For browser crawlers — fingerprints are rotated automatically
- ✅ Use `persistCookiesPerSession: true`
- ✅ Retire sessions on blocks: `session.retire()`

---

## 11. Concurrency & Scaling

```javascript
// JS
const crawler = new CheerioCrawler({
  maxConcurrency: 50,         // Max parallel requests (default: 200)
  minConcurrency: 1,          // Don't set too high!
  maxRequestsPerMinute: 120,  // Rate limit
  maxRequestsPerCrawl: 1000,  // Total request cap (safety)
  requestHandlerTimeoutSecs: 30,
});
```

```python
# Python
from crawlee import ConcurrencySettings

crawler = BeautifulSoupCrawler(
    concurrency_settings=ConcurrencySettings(
        max_concurrency=50,
        max_tasks_per_minute=120,
    ),
    max_requests_per_crawl=1000,
)
```

**Scaling notes:**
- Crawlee auto-scales concurrency based on CPU/memory
- Don't set `minConcurrency` high — it can crash under load
- `maxRequestsPerMinute` is smoother than raw concurrency throttling

---

## 12. Configuration & Environment Variables

| Env Variable | Default | Purpose |
|---|---|---|
| `CRAWLEE_STORAGE_DIR` | `./storage` | Storage root directory |
| `CRAWLEE_DEFAULT_DATASET_ID` | `default` | Override default dataset ID |
| `CRAWLEE_DEFAULT_KEY_VALUE_STORE_ID` | `default` | Override default KVS ID |
| `CRAWLEE_DEFAULT_REQUEST_QUEUE_ID` | `default` | Override default queue ID |
| `CRAWLEE_PURGE_ON_START` | `true` | Clear storage before each run |

```javascript
// JS — Programmatic configuration
import { Configuration } from 'crawlee';

const config = new Configuration({
  storageDir: '/data/crawlee',
  persistStateIntervalMillis: 30_000,
});

const crawler = new CheerioCrawler({ /* ... */ }, config);
```

---

## 13. Docker Deployment

```dockerfile
FROM apify/actor-node-playwright-chrome:20

COPY package*.json ./
RUN npm ci --only=prod

COPY . ./

CMD ["node", "src/main.js"]
```

For Cheerio (smaller image):
```dockerfile
FROM apify/actor-node:20
```

---

## 14. Common Patterns

### Pagination
```javascript
// JS — Enqueue next page
router.addHandler('LIST', async ({ page, enqueueLinks }) => {
  await enqueueLinks({ selector: '.product', label: 'DETAIL' });
  const hasNext = await page.$('a.next');
  if (hasNext) await enqueueLinks({ selector: 'a.next', label: 'LIST' });
});
```

### Downloading Files
```javascript
// JS — Save to KeyValueStore
const { body } = await sendRequest({ responseType: 'buffer' });
await KeyValueStore.setValue('file.pdf', body, { contentType: 'application/pdf' });
```

### Taking Screenshots
```javascript
// JS — Playwright
async requestHandler({ page, request }) {
  const screenshot = await page.screenshot({ fullPage: true });
  await KeyValueStore.setValue(
    `screenshot-${Date.now()}`,
    screenshot,
    { contentType: 'image/png' }
  );
}
```

### Shared State Across Handlers
```javascript
// JS — useState()
async requestHandler({ useState }) {
  const state = await useState({ count: 0 });
  state.count++;
  console.log('Total processed:', state.count);
}
```

### Error Handling & Retries
```javascript
// JS
const crawler = new CheerioCrawler({
  maxRequestRetries: 3, // Retry failed requests up to 3 times
  failedRequestHandler: async ({ request, error }) => {
    console.error(`Failed: ${request.url}`, error.message);
    await Dataset.pushData({ url: request.url, error: error.message });
  },
});
```

```python
# Python
crawler = BeautifulSoupCrawler(max_request_retries=3)

@crawler.failed_request_handler
async def on_failed(context: BasicCrawlingContext, error: Exception) -> None:
    context.log.error(f'Failed {context.request.url}: {error}')
```

### Sitemap Crawling
```javascript
import { CheerioCrawler } from 'crawlee';
import { Sitemap } from '@crawlee/utils';

const { urls } = await Sitemap.load('https://example.com/sitemap.xml');
const crawler = new CheerioCrawler({ /* ... */ });
await crawler.run(urls);
```

### Run as Web Server
```javascript
import { CheerioCrawler } from 'crawlee';
import { createServer } from 'http';

const server = createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost').searchParams.get('url');
  const crawler = new CheerioCrawler({
    maxRequestsPerCrawl: 1,
    async requestHandler({ $ }) {
      res.end(JSON.stringify({ title: $('title').text() }));
    },
  });
  await crawler.run([url]);
});
server.listen(3000);
```

---

## 15. TypeScript Support

```typescript
import { CheerioCrawler, CheerioCrawlingContext, Dataset } from 'crawlee';

interface Product {
  url: string;
  title: string;
  price: number;
}

const crawler = new CheerioCrawler({
  async requestHandler({ $, request }: CheerioCrawlingContext) {
    const title = $('h1').text();
    const price = parseFloat($('.price').text().replace('$', ''));
    await Dataset.pushData<Product>({ url: request.url, title, price });
  },
});
```

---

## 16. Cloud Deployment (Apify Platform)

```javascript
import { Actor } from 'apify';
import { CheerioCrawler } from 'crawlee';

await Actor.init();

const input = await Actor.getInput();
const { startUrls } = input;

const crawler = new CheerioCrawler({
  async requestHandler({ $, request }) {
    await Actor.pushData({ url: request.url, title: $('title').text() });
  },
});

await crawler.run(startUrls);
await Actor.exit();
```

Deploy with: `apify push`

---

## 17. Debugging Tips

```javascript
// Enable verbose logging
import { Log } from 'crawlee';
Log.setLevel(Log.LEVELS.DEBUG);

// Run headful (browser crawlers only)
const crawler = new PlaywrightCrawler({
  headless: false,
  // ...
});

// Limit requests while developing
const crawler = new CheerioCrawler({
  maxRequestsPerCrawl: 10,
  // ...
});
```

---

## 18. Reference Files

For advanced topics, see:
- `references/js-api.md` — Full JS API quick reference
- `references/python-api.md` — Full Python API quick reference

Both language docs: https://crawlee.dev
