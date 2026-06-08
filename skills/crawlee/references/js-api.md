# Crawlee JavaScript API Quick Reference

## Crawler Classes

### CheerioCrawler
```typescript
new CheerioCrawler({
  requestHandler: async ({ $, request, response, enqueueLinks, pushData, log, session, proxyInfo, useState, sendRequest, getKeyValueStore }) => {},
  failedRequestHandler: async ({ request, error }) => {},
  maxConcurrency: 200,
  minConcurrency: 1,
  maxRequestsPerCrawl: Infinity,
  maxRequestsPerMinute: Infinity,
  maxRequestRetries: 3,
  requestHandlerTimeoutSecs: 60,
  useSessionPool: true,
  persistCookiesPerSession: true,
  sessionPoolOptions: { maxPoolSize: 1000 },
  proxyConfiguration: ProxyConfiguration,
  navigationTimeoutSecs: 60,
  ignoreSslErrors: false,
  additionalMimeTypes: [],
  suggestResponseEncoding: undefined,
})
```

### PlaywrightCrawler
```typescript
new PlaywrightCrawler({
  requestHandler: async ({ page, request, response, enqueueLinks, pushData, log, session, proxyInfo, browserController, crawler }) => {},
  launchContext: {
    launcher: playwright.chromium,
    launchOptions: { headless: true, args: [] },
    useIncognitoPages: false,
    userDataDir: undefined,
  },
  browserPoolOptions: { maxOpenPagesPerBrowser: 50 },
  preNavigationHooks: [async ({ page, request }) => {}],
  postNavigationHooks: [async ({ page, request }) => {}],
  // ...same base options as CheerioCrawler
})
```

### HttpCrawler
Like CheerioCrawler but handler receives raw `body` and `contentType` instead of `$`.

## requestHandler Context Properties

| Property | Type | Description |
|---|---|---|
| `request` | `Request` | Current request object |
| `response` | `IncomingMessage` | HTTP response |
| `$` | `CheerioAPI` | Parsed HTML (CheerioCrawler only) |
| `page` | `Page` | Playwright page (PlaywrightCrawler only) |
| `body` | `string\|Buffer` | Raw response body (HttpCrawler) |
| `json` | `object` | Parsed JSON if content-type is JSON |
| `log` | `Log` | Logger |
| `session` | `Session\|null` | Current session |
| `proxyInfo` | `ProxyInfo\|null` | Current proxy info |
| `enqueueLinks` | `Function` | Enqueue found links |
| `pushData` | `Function` | Shortcut for Dataset.pushData |
| `useState` | `Function` | Persistent state across requests |
| `sendRequest` | `Function` | Custom HTTP request via got-scraping |
| `getKeyValueStore` | `Function` | Access a KV store |
| `crawler` | `Crawler` | The crawler instance |

## Request Class
```typescript
new Request({
  url: 'https://example.com',
  uniqueKey: undefined,   // auto-derived from URL by default
  method: 'GET',
  headers: {},
  payload: undefined,
  userData: {},           // arbitrary metadata
  label: undefined,       // for router.addHandler(label, ...)
  keepUrlFragment: false,
  useExtendedUniqueKey: false,
  noRetry: false,
  skipNavigation: false,
})
```

## enqueueLinks Options
```typescript
await enqueueLinks({
  selector: 'a',                    // CSS selector
  globs: ['https://example.com/**'],
  pseudoUrls: [],                    // legacy, prefer globs
  regexps: [/\/products\//],
  exclude: ['**.pdf'],               // glob patterns to exclude
  label: 'DETAIL',
  baseUrl: undefined,
  transformRequestFunction: (req) => req,
  strategy: 'all' | 'same-domain' | 'same-hostname' | 'same-origin',
  limit: undefined,
});
```

## Dataset API
```typescript
// Static helpers (default dataset)
await Dataset.pushData(item | item[]);
await Dataset.exportToCSV('key');
await Dataset.exportToJSON('key');
await Dataset.getData({ limit, offset, desc, fields });

// Instance
const ds = await Dataset.open('name-or-id');
await ds.pushData(item);
for await (const item of ds) { }
for await (const [index, item] of ds.entries()) { }
await ds.drop();
```

## KeyValueStore API
```typescript
// Static helpers
await KeyValueStore.getValue('key');
await KeyValueStore.setValue('key', value, { contentType: 'text/html' });
await KeyValueStore.getInput();  // reads INPUT key

// Instance
const kvs = await KeyValueStore.open('name-or-id');
await kvs.getValue('key');
await kvs.setValue('key', value);
for await (const [key, val] of kvs.entries()) { }
await kvs.forEachKey(async (key, index, info) => { });
```

## RequestQueue API
```typescript
const rq = await RequestQueue.open();
await rq.addRequest({ url: 'https://example.com' });
await rq.addRequests([...]);
const req = await rq.fetchNextRequest();
await rq.markRequestHandled(req);
await rq.reclaimRequest(req);
const info = await rq.getInfo(); // { totalCount, handledCount, pendingCount }
```

## ProxyConfiguration API
```typescript
const proxy = new ProxyConfiguration({
  proxyUrls: ['http://proxy1', 'http://proxy2'],
  // OR
  tieredProxyUrls: [
    [null],                    // no proxy
    ['http://cheap-proxy'],    // datacenter
    ['http://pricey-proxy'],   // residential
  ],
  // OR
  newUrlFunction: async (sessionId, { request }) => 'http://custom-proxy',
});

const url = await proxy.newUrl(sessionId);
const info = await proxy.newProxyInfo(sessionId);
```

## SessionPool API
```typescript
const pool = await SessionPool.open({
  maxPoolSize: 1000,
  sessionOptions: {
    maxAgeSecs: 3000,
    maxErrorScore: 3,
    maxUsageCount: 50,
  },
  persistStateKeyValueStoreId: undefined,
  persistStateKey: 'SESSION_POOL_STATE',
  createSessionFunction: async (pool) => new Session({ ... }),
});

const session = await pool.getSession();
session.retire();     // Mark as blocked, never reuse
session.markBad();    // Reduce score, may reuse later
session.markGood();   // (auto-called on success)
```

## Configuration
```typescript
const config = new Configuration({
  storageDir: './storage',
  persistStateIntervalMillis: 60_000,
  systemInfoIntervalMillis: 60_000,
  defaultDatasetId: 'default',
  defaultKeyValueStoreId: 'default',
  defaultRequestQueueId: 'default',
  purgeOnStart: true,
  maxUsedCpuRatio: 0.95,
  availableMemoryRatio: 0.25,
});
```

## Router
```typescript
import { createCheerioRouter, createPlaywrightRouter } from 'crawlee';

const router = createCheerioRouter();

router.addHandler('LABEL', async (ctx) => { });
router.addDefaultHandler(async (ctx) => { });

// Use in crawler:
new CheerioCrawler({ requestHandler: router });
```

## Logging
```typescript
import { Log } from 'crawlee';

const log = new Log({ prefix: 'MyModule' });
log.debug('msg', { extra: 'data' });
log.info('msg');
log.warning('msg');
log.error('msg');
log.exception(error, 'msg');

Log.setLevel(Log.LEVELS.DEBUG); // Global
```
