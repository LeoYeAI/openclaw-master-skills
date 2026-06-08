# Crawlee Python API Quick Reference

## Crawler Classes

All crawlers are in `crawlee.crawlers`.

### BeautifulSoupCrawler
```python
from crawlee.crawlers import BeautifulSoupCrawler

crawler = BeautifulSoupCrawler(
    parser='lxml',                          # or 'html.parser', 'html5lib'
    max_request_retries=3,
    max_requests_per_crawl=None,            # None = unlimited
    max_session_rotations=10,
    max_crawl_depth=None,
    use_session_pool=True,
    session_pool=SessionPool(...),
    proxy_configuration=ProxyConfiguration(...),
    concurrency_settings=ConcurrencySettings(...),
    request_handler_timeout=timedelta(seconds=60),
    respect_robots_txt_file=False,
)
```

### PlaywrightCrawler
```python
from crawlee.crawlers import PlaywrightCrawler

crawler = PlaywrightCrawler(
    headless=True,
    browser_type='chromium',               # 'firefox', 'webkit'
    # ...same base params as BeautifulSoupCrawler
)
```

### ParselCrawler
```python
from crawlee.crawlers import ParselCrawler
# Same params as BeautifulSoupCrawler, uses Parsel (Scrapy-style selectors)
```

### AdaptivePlaywrightCrawler
```python
from crawlee.crawlers import AdaptivePlaywrightCrawler

crawler = AdaptivePlaywrightCrawler.with_parsel_static_parser()
# Or with BS4:
crawler = AdaptivePlaywrightCrawler.with_beautifulsoup_static_parser()
```

## Handler Context Properties

### BeautifulSoupCrawlingContext
| Property | Type | Description |
|---|---|---|
| `request` | `Request` | Current request |
| `soup` | `BeautifulSoup` | Parsed HTML |
| `http_response` | `HttpResponse` | Raw HTTP response |
| `log` | `Logger` | Logger |
| `session` | `Session\|None` | Current session |
| `proxy_info` | `ProxyInfo\|None` | Current proxy |
| `push_data` | `async (data)` | Write to dataset |
| `enqueue_links` | `async (...)` | Enqueue found links |
| `add_requests` | `async ([...])` | Add custom requests |

### PlaywrightCrawlingContext
Adds: `page` (Playwright Page), `browser_controller`

## Request Class
```python
from crawlee import Request

req = Request.from_url(
    url='https://example.com',
    method='GET',
    headers=HttpHeaders({'X-Custom': 'value'}),
    payload=None,
    user_data={},
    label=None,          # Used with router.handler('LABEL')
    unique_key=None,     # Auto-derived from URL
    no_retry=False,
)
```

## enqueue_links
```python
await context.enqueue_links()

await context.enqueue_links(
    selector='a.product',
    label='DETAIL',
    include=[re.compile(r'/products/')],
    exclude=[re.compile(r'/login')],
    strategy='all',          # 'all' | 'same-domain' | 'same-hostname' | 'same-origin'
    transform_request_function=lambda req: req,
    limit=None,
)
```

## Dataset API
```python
from crawlee.storages import Dataset

# Open a dataset
ds = await Dataset.open()              # default
ds = await Dataset.open(name='my-ds') # named (persists across runs)
ds = await Dataset.open(alias='temp') # alias (purged on start)

# Write
await ds.push_data({'key': 'value'})
await ds.push_data([item1, item2])

# Read
data = await ds.get_data(limit=100, offset=0, desc=False)
async for item in ds.iterate_items():
    print(item)

# Export
await ds.export_to(key='results', content_type='csv')
await ds.export_to(key='results', content_type='json')

# Cleanup
await ds.drop()
```

## KeyValueStore API
```python
from crawlee.storages import KeyValueStore

kvs = await KeyValueStore.open()
kvs = await KeyValueStore.open(name='my-store')

await kvs.set_value('key', {'data': 123})
await kvs.set_value('image', bytes_data, content_type='image/png')
value = await kvs.get_value('key')

async for key, value, info in kvs.iterate_keys():
    print(key, info.size)

await kvs.drop()
```

## RequestQueue API
```python
from crawlee.storages import RequestQueue

rq = await RequestQueue.open()
await rq.add_request(Request.from_url('https://example.com'))
await rq.add_requests_batched([req1, req2])
info = await rq.get_info()  # total_count, handled_count, pending_count
```

## ProxyConfiguration
```python
from crawlee.proxy_configuration import ProxyConfiguration

proxy = ProxyConfiguration(
    proxy_urls=['http://user:pass@proxy1:8000', 'http://user:pass@proxy2:8000'],
)

# Tiered proxies
proxy = ProxyConfiguration(
    tiered_proxy_urls=[
        [None],                         # no proxy
        ['http://datacenter-proxy'],    # tier 1
        ['http://residential-proxy'],   # tier 2
    ]
)

url = await proxy.new_url(session_id='session-1')
```

## SessionPool
```python
from crawlee.sessions import SessionPool, Session

pool = SessionPool(
    max_pool_size=1000,
    create_session_settings=SessionSettings(
        max_age=timedelta(seconds=3000),
        max_error_score=3.0,
        max_usage_count=50,
        blocked_status_codes=[401, 403, 429],
    ),
)

# In handler:
context.session.retire()    # Permanently remove session
context.session.mark_bad()  # Penalize
```

## ConcurrencySettings
```python
from crawlee import ConcurrencySettings

settings = ConcurrencySettings(
    min_concurrency=1,
    max_concurrency=200,
    max_tasks_per_minute=float('inf'),
    desired_concurrency_ratio=0.90,
    scale_up_step_ratio=0.05,
    scale_down_step_ratio=0.05,
)
```

## Configuration
```python
from crawlee.configuration import Configuration

config = Configuration(
    storage_dir='./storage',
    purge_on_start=True,
    default_dataset_id='default',
    default_key_value_store_id='default',
    default_request_queue_id='default',
    persist_state_interval=timedelta(seconds=60),
)

crawler = BeautifulSoupCrawler(configuration=config)
```

## Router
```python
# Handlers attached directly to crawler via decorator
@crawler.router.default_handler
async def default_handler(context: BeautifulSoupCrawlingContext) -> None:
    ...

@crawler.router.handler('CATEGORY')
async def category_handler(context: BeautifulSoupCrawlingContext) -> None:
    ...

# Request with label routes to matching handler:
await context.add_requests([
    Request.from_url('https://example.com/cat/1', label='CATEGORY')
])
```

## Error Handling
```python
@crawler.error_handler
async def error_handler(context: BasicCrawlingContext, error: Exception) -> None:
    context.log.error(f'Error on {context.request.url}: {error}')
    if not isinstance(error, (SessionError, HttpStatusCodeError)):
        context.request.no_retry = True

@crawler.failed_request_handler
async def failed_handler(context: BasicCrawlingContext, error: Exception) -> None:
    await context.push_data({'url': context.request.url, 'error': str(error)})
```

## Pre/Post Navigation Hooks (Playwright)
```python
@crawler.pre_navigation_hook
async def before_nav(context: PlaywrightCrawlingContext) -> None:
    await context.page.set_extra_http_headers({'X-Custom': 'value'})

@crawler.post_navigation_hook  
async def after_nav(context: PlaywrightCrawlingContext) -> None:
    await context.page.wait_for_timeout(500)
```

## Running the Crawler
```python
import asyncio

async def main() -> None:
    crawler = BeautifulSoupCrawler(max_requests_per_crawl=100)

    @crawler.router.default_handler
    async def handler(context: BeautifulSoupCrawlingContext) -> None:
        await context.push_data({'url': context.request.url})
        await context.enqueue_links()

    stats = await crawler.run(['https://example.com'])
    print(f'Done. Requests: {stats.requests_total}, Failed: {stats.requests_failed}')

if __name__ == '__main__':
    asyncio.run(main())
```
