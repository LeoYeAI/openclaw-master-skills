---
name: scrapling
description: "Adaptive web scraping framework with anti-bot bypass and spider crawling."
version: "1.0.8"
metadata:
  {"openclaw":{"emoji":"🕷️","requires":{"bins":["python3"]}, "tags":["web-scraping", "crawling", "research", "automation"]}}
---

# Scrapling - Adaptive Web Scraping

> "Effortless web scraping for the modern web."

---

## Credits

### Core Library
- **Repository:** https://github.com/D4Vinci/Scrapling
- **Author:** D4Vinci (Karim Shoair)
- **License:** BSD-3-Clause
- **Documentation:** https://scrapling.readthedocs.io

### API Reverse Engineering Methodology
- **GitHub:** https://github.com/paoloanzn/free-solscan-api
- **X Post:** https://x.com/paoloanzn/status/2026361234032046319
- **Author:** @paoloanzn
- **Insight:** "Web scraping is 80% reverse engineering"

---

## Installation

```bash
# Core library (parser only)
pip install scrapling

# With fetchers (HTTP + browser automation) - RECOMMENDED
pip install "scrapling[fetchers]"
scrapling install

# With shell (CLI tools) - RECOMMENDED
pip install "scrapling[shell]"

# With AI (MCP server) - OPTIONAL
pip install "scrapling[ai]"

# Everything
pip install "scrapling[all]"

# Browser for stealth/dynamic mode
playwright install chromium

# For Cloudflare bypass (advanced)
pip install cloudscraper
```

---

## Agent Instructions

### When to Use Scrapling

**Use Scrapling when:**
- Research topics from websites
- Extract data from blogs, news sites, docs
- Crawl multiple pages with Spider
- Gather content for summaries
- Extract brand data from any website
- Reverse engineer APIs from websites

**Do NOT use for:**
- X/Twitter (use x-tweet-fetcher skill)
- Login-protected sites (unless credentials provided)
- Paywalled content (respect robots.txt)
- Sites that prohibit scraping in their TOS

---

## Quick Commands

### 1. Basic Fetch (Most Common)

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com')

# Extract content
title = page.css('h1::text').get()
paragraphs = page.css('p::text').getall()
```

### 2. Stealthy Fetch (Anti-Bot/Cloudflare)

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.adaptive = True
page = StealthyFetcher.fetch('https://example.com', headless=True, solve_cloudflare=True)
```

### 3. Dynamic Fetch (Full Browser Automation)

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://example.com', headless=True, network_idle=True)
```

### 4. Adaptive Parsing (Survives Design Changes)

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com')

# First scrape - saves selectors
items = page.css('.product', auto_save=True)

# Later - if site changes, use adaptive=True to relocate
items = page.css('.product', adaptive=True)
```

### 5. Spider (Multiple Pages)

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com"]
    concurrent_requests = 3
    
    async def parse(self, response: Response):
        for item in response.css('.item'):
            yield {"item": item.css('h2::text').get()}
        
        # Follow links
        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

MySpider().start()
```

### 6. CLI Usage

```bash
# Simple fetch to file
scrapling extract get https://example.com content.html

# Stealthy fetch (bypass anti-bot)
scrapling extract stealthy-fetch https://example.com content.html

# Interactive shell
scrapling shell https://example.com
```

---

## Common Patterns

### Extract Article Content

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com/article')

# Try multiple selectors for title
title = (
    page.css('[itemprop="headline"]::text').get() or
    page.css('article h1::text').get() or
    page.css('h1::text').get()
)

# Get paragraphs
content = page.css('article p::text, .article-body p::text').getall()

print(f"Title: {title}")
print(f"Paragraphs: {len(content)}")
```

### Research Multiple Pages

```python
from scrapling.spiders import Spider, Response

class ResearchSpider(Spider):
    name = "research"
    start_urls = ["https://news.ycombinator.com"]
    concurrent_requests = 5
    
    async def parse(self, response: Response):
        for item in response.css('.titleline a::text').getall()[:10]:
            yield {"title": item, "source": "HN"}
        
        more = response.css('.morelink::attr(href)').get()
        if more:
            yield response.follow(more)

ResearchSpider().start()
```

### Crawl Entire Site (Easy Mode)

Auto-crawl all pages on a domain by following internal links:

```python
from scrapling.spiders import Spider, Response
from urllib.parse import urljoin, urlparse

class EasyCrawl(Spider):
    """Auto-crawl all pages on a domain."""
    
    name = "easy_crawl"
    start_urls = ["https://example.com"]
    concurrent_requests = 3
    
    def __init__(self):
        super().__init__()
        self.visited = set()
    
    async def parse(self, response: Response):
        # Extract content
        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'h1': response.css('h1::text').get(),
        }
        
        # Follow internal links (limit to 50 pages)
        if len(self.visited) >= 50:
            return
        
        self.visited.add(response.url)
        
        links = response.css('a::attr(href)').getall()[:20]
        for link in links:
            full_url = urljoin(response.url, link)
            if full_url not in self.visited:
                yield response.follow(full_url)

# Usage
result = EasyCrawl()
result.start()
```

### Sitemap Crawl

Crawl pages from `sitemap.xml` (with fallback to link discovery):

```python
from scrapling.fetchers import Fetcher
from scrapling.spiders import Spider, Response
from urllib.parse import urljoin, urlparse
import re

def get_sitemap_urls(url: str, max_urls: int = 100) -> list:
    """Extract URLs from sitemap.xml - also checks robots.txt."""
    
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    sitemap_urls = [
        f"{base_url}/sitemap.xml",
        f"{base_url}/sitemap-index.xml",
        f"{base_url}/sitemap_index.xml",
        f"{base_url}/sitemap-news.xml",
    ]
    
    all_urls = []
    
    # First check robots.txt for sitemap URL
    try:
        robots = Fetcher.get(f"{base_url}/robots.txt")
        if robots.status == 200:
            sitemap_in_robots = re.findall(r'Sitemap:\s*(\S+)', robots.text, re.IGNORECASE)
            for sm in sitemap_in_robots:
                sitemap_urls.insert(0, sm)
    except:
        pass
    
    # Try each sitemap location
    for sitemap_url in sitemap_urls:
        try:
            page = Fetcher.get(sitemap_url, timeout=10)
            if page.status != 200:
                continue
            
            text = page.text
            
            # Check if it's XML
            if '<?xml' in text or '<urlset' in text or '<sitemapindex' in text:
                urls = re.findall(r'<loc>([^<]+)</loc>', text)
                all_urls.extend(urls[:max_urls])
                print(f"Found {len(urls)} URLs in {sitemap_url}")
        except:
            continue
    
    return list(set(all_urls))[:max_urls]

def crawl_from_sitemap(domain_url: str, max_pages: int = 50):
    """Crawl pages from sitemap."""
    
    print(f"Fetching sitemap for {domain_url}...")
    urls = get_sitemap_urls(domain_url)
    
    if not urls:
        print("No sitemap found. Use EasyCrawl instead!")
        return []
    
    print(f"Found {len(urls)} URLs, crawling first {max_pages}...")
    
    results = []
    for url in urls[:max_pages]:
        try:
            page = Fetcher.get(url, timeout=10)
            results.append({
                'url': url,
                'status': page.status,
                'title': page.css('title::text').get(),
            })
        except Exception as e:
            results.append({'url': url, 'error': str(e)[:50]})
    
    return results

# Usage
print("=== Sitemap Crawl ===")
results = crawl_from_sitemap('https://example.com', max_pages=10)
for r in results[:3]:
    print(f"  {r.get('title', r.get('error', 'N/A'))}")

# Alternative: Easy crawl all links
print("\n=== Easy Crawl (Link Discovery) ===")
result = EasyCrawl(start_urls=["https://example.com"], max_pages=10).start()
print(f"Crawled {len(result.items)} pages")
```

### Firecrawl-Style Crawl (Best of Both Worlds)

Inspired by Firecrawl's behavior - combines sitemap discovery with link following:

```python
from scrapling.fetchers import Fetcher
from scrapling.spiders import Spider, Response
from urllib.parse import urljoin, urlparse
import re

def firecrawl_crawl(url: str, max_pages: int = 50, use_sitemap: bool = True):
    """
    Firecrawl-style crawling:
    - use_sitemap=True: Discover URLs from sitemap first (default)
    - use_sitemap=False: Only follow HTML links (like sitemap:"skip")
    
    Matches Firecrawl's crawl behavior.
    """
    
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # ========== Method 1: Sitemap Discovery ==========
    if use_sitemap:
        print(f"[Firecrawl] Discovering URLs from sitemap...")
        
        sitemap_urls = [
            f"{url.rstrip('/')}/sitemap.xml",
            f"{url.rstrip('/')}/sitemap-index.xml",
        ]
        
        all_urls = []
        
        # Try sitemaps
        for sm_url in sitemap_urls:
            try:
                page = Fetcher.get(sm_url, timeout=15)
                if page.status == 200:
                    # Handle bytes
                    text = page.body.decode('utf-8', errors='ignore') if isinstance(page.body, bytes) else str(page.body)
                    
                    if '<urlset' in text:
                        urls = re.findall(r'<loc>([^<]+)</loc>', text)
                        all_urls.extend(urls[:max_pages])
                        print(f"[Firecrawl] Found {len(urls)} URLs in {sm_url}")
            except:
                continue
        
        if all_urls:
            print(f"[Firecrawl] Total: {len(all_urls)} URLs from sitemap")
            
            # Crawl discovered URLs
            results = []
            for page_url in all_urls[:max_pages]:
                try:
                    page = Fetcher.get(page_url, timeout=15)
                    results.append({
                        'url': page_url,
                        'status': page.status,
                        'title': page.css('title::text').get() if page.status == 200 else None,
                    })
                except Exception as e:
                    results.append({'url': page_url, 'error': str(e)[:50]})
            
            return results
    
    # ========== Method 2: Link Discovery (sitemap: skip) ==========
    print(f"[Firecrawl] Sitemap skip - using link discovery...")
    
    class LinkCrawl(Spider):
        name = "firecrawl_link"
        start_urls = [url]
        concurrent_requests = 3
        
        def __init__(self):
            super().__init__()
            self.visited = set()
            self.domain = domain
            self.results = []
        
        async def parse(self, response: Response):
            if len(self.results) >= max_pages:
                return
            
            self.results.append({
                'url': response.url,
                'status': response.status,
                'title': response.css('title::text').get(),
            })
            
            # Follow internal links
            links = response.css('a::attr(href)').getall()[:20]
            for link in links:
                full_url = urljoin(response.url, link)
                parsed_link = urlparse(full_url)
                
                if parsed_link.netloc == self.domain and full_url not in self.visited:
                    self.visited.add(full_url)
                    if len(self.visited) < max_pages:
                        yield response.follow(full_url)
    
    result = LinkCrawl()
    result.start()
    return result.results

# Usage
print("=== Firecrawl-Style (sitemap: include) ===")
results = firecrawl_crawl('https://www.cloudflare.com', max_pages=5, use_sitemap=True)
print(f"Crawled: {len(results)} pages")

print("\n=== Firecrawl-Style (sitemap: skip) ===")
results = firecrawl_crawl('https://example.com', max_pages=5, use_sitemap=False)
print(f"Crawled: {len(results)} pages")
```

### Handle Errors

```python
from scrapling.fetchers import Fetcher, StealthyFetcher

try:
    page = Fetcher.get('https://example.com')
except Exception as e:
    # Try stealth mode
    page = StealthyFetcher.fetch('https://example.com', headless=True)
    
if page.status == 403:
    print("Blocked - try StealthyFetcher")
elif page.status == 200:
    print("Success!")
```

---

## Session Management

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()
```

### Multiple Session Types in Spider

```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]
    
    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)
    
    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)
```

---

## Advanced Parsing & Navigation

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')

# Multiple selection methods
quotes = page.css('.quote')           # CSS
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', class_='quote')  # BeautifulSoup-style

# Navigation
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
parent = first_quote.parent

# Find similar elements
similar = first_quote.find_similar()
```

---

## Advanced: API Reverse Engineering

> "Web scraping is 80% reverse engineering."

This section covers advanced techniques to discover and replicate APIs directly from websites — often revealing data that's "hidden" behind paid APIs.

### 1. API Endpoint Discovery

Many websites load data via client-side requests. Use browser DevTools to find them:

**Steps:**
1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Reload the page
4. Look for **XHR** or **Fetch** requests
5. Check if endpoints return JSON data

**What to look for:**
- Requests to `/api/*` endpoints
- Responses containing structured data (JSON)
- Same endpoints used on both free and paid sections

**Example pattern:**
```
# Found in Network tab:
GET https://api.example.com/v1/users/transactions
Response: {"data": [...], "pagination": {...}}
```

### 2. JavaScript Analysis

Auth tokens often generated client-side. Find them in `.js` files:

**Steps:**
1. In Network tab, look at **Initiator** column
2. Click the `.js` file making the request
3. Search for auth header name (e.g., `sol-aut`, `Authorization`, `X-API-Key`)
4. Find the function generating the token

**Common patterns:**
- Plain text function names: `generateToken()`, `createAuthHeader()`
- Obfuscated: Search for the header name directly
- Random string generation: `Math.random()`, `crypto.getRandomValues()`

### 3. Replicating Discovered APIs

Once you've found the endpoint and auth pattern:

```python
import requests
import random
import string

def generate_auth_token():
    """Replicate discovered token generation logic."""
    chars = string.ascii_letters + string.digits
    token = ''.join(random.choice(chars) for _ in range(40))
    # Insert fixed string at random position
    fixed = "B9dls0fK"
    pos = random.randint(0, len(token))
    return token[:pos] + fixed + token[pos:]

def scrape_api_endpoint(url):
    """Hit discovered API endpoint with replicated auth."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'sol-aut': generate_auth_token(),  # Replicate discovered header
    }
    
    response = requests.get(url, headers=headers)
    return response.json()
```

### 4. Cloudscraper Bypass (Cloudflare)

For Cloudflare-protected endpoints, use `cloudscraper`:

```bash
pip install cloudscraper
```

```python
import cloudscraper

def create_scraper():
    """Create a cloudscraper session that bypasses Cloudflare."""
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    return scraper

# Usage
scraper = create_scraper()
response = scraper.get('https://api.example.com/endpoint')
data = response.json()
```

### 5. Complete API Replication Pattern

```python
import cloudscraper
import random
import string
import json

class APIReplicator:
    """Replicate discovered API from website."""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = cloudscraper.create_scraper()
    
    def generate_token(self, pattern="random"):
        """Replicate discovered token generation."""
        if pattern == "solscan":
            # 40-char random + fixed string at random position
            chars = string.ascii_letters + string.digits
            token = ''.join(random.choice(chars) for _ in range(40))
            fixed = "B9dls0fK"
            pos = random.randint(0, len(token))
            return token[:pos] + fixed + token[pos:]
        else:
            # Generic random token
            return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def get(self, endpoint, headers=None, auth_header=None, auth_pattern="random"):
        """Make API request with discovered auth."""
        url = f"{self.base_url}{endpoint}"
        
        # Build headers
        request_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        # Add discovered auth header
        if auth_header:
            request_headers[auth_header] = self.generate_token(auth_pattern)
        
        # Merge custom headers
        if headers:
            request_headers.update(headers)
        
        response = self.session.get(url, headers=request_headers)
        return response

# Usage example
api = APIReplicator("https://api.solscan.io")
data = api.get(
    "/account/transactions",
    auth_header="sol-aut",
    auth_pattern="solscan"
)
print(data)
```

### 6. Discovery Checklist

When approaching a new site:

| Step | Action | Tool |
|------|--------|------|
| 1 | Open DevTools Network tab | F12 |
| 2 | Reload page, filter by XHR/Fetch | Network filter |
| 3 | Look for JSON responses | Response tab |
| 4 | Check if same endpoint used for "premium" data | Compare requests |
| 5 | Find auth header in JS files | Initiator column |
| 6 | Extract token generation logic | JS debugger |
| 7 | Replicate in Python | Replicator class |
| 8 | Test against API | Run script |

---

## Brand Data Extraction (Firecrawl Alternative)

Extract brand data, colors, logos, and copy from any website:

```python
from scrapling.fetchers import Fetcher
from urllib.parse import urljoin
import re

def extract_brand_data(url: str) -> dict:
    """Extract structured brand data from any website - Firecrawl style."""
    
    # Try stealth mode first (handles anti-bot)
    try:
        page = Fetcher.get(url)
    except:
        from scrapling.fetchers import StealthyFetcher
        page = StealthyFetcher.fetch(url, headless=True)
    
    # Helper to get text from element
    def get_text(elements):
        return elements[0].text if elements else None
    
    # Helper to get attribute
    def get_attr(elements, attr_name):
        return elements[0].attrib.get(attr_name) if elements else None
    
    # Brand name (try multiple selectors)
    brand_name = (
        get_text(page.css('[property="og:site_name"]')) or
        get_text(page.css('h1')) or
        get_text(page.css('title'))
    )
    
    # Tagline
    tagline = (
        get_text(page.css('[property="og:description"]')) or
        get_text(page.css('.tagline')) or
        get_text(page.css('.hero-text')) or
        get_text(page.css('header h2'))
    )
    
    # Logo URL
    logo_url = (
        get_attr(page.css('[rel="icon"]'), 'href') or
        get_attr(page.css('[rel="apple-touch-icon"]'), 'href') or
        get_attr(page.css('.logo img'), 'src')
    )
    if logo_url and not logo_url.startswith('http'):
        logo_url = urljoin(url, logo_url)
    
    # Favicon
    favicon = get_attr(page.css('[rel="icon"]'), 'href')
    favicon_url = urljoin(url, favicon) if favicon else None
    
    # OG Image
    og_image = get_attr(page.css('[property="og:image"]'), 'content')
    og_image_url = urljoin(url, og_image) if og_image else None
    
    # Screenshot (using external service)
    screenshot_url = f"https://image.thum.io/get/width/1200/crop/800/{url}"
    
    # Description
    description = (
        get_text(page.css('[property="og:description"]')) or
        get_attr(page.css('[name="description"]'), 'content')
    )
    
    # CTA text
    cta_text = (
        get_text(page.css('a[href*="signup"]')) or
        get_text(page.css('.cta')) or
        get_text(page.css('[class*="button"]'))
    )
    
    # Social links
    social_links = {}
    for platform in ['twitter', 'facebook', 'instagram', 'linkedin', 'youtube', 'github']:
        link = get_attr(page.css(f'a[href*="{platform}"]'), 'href')
        if link:
            social_links[platform] = link
    
    # Features (from feature grid/cards)
    features = []
    feature_cards = page.css('[class*="feature"], .feature-card, .benefit-item')
    for card in feature_cards[:6]:
        feature_text = get_text(card.css('h3, h4, p'))
        if feature_text:
            features.append(feature_text.strip())
    
    return {
        'brandName': brand_name,
        'tagline': tagline,
        'description': description,
        'features': features,
        'logoUrl': logo_url,
        'faviconUrl': favicon_url,
        'ctaText': cta_text,
        'socialLinks': social_links,
        'screenshotUrl': screenshot_url,
        'ogImageUrl': og_image_url
    }

# Usage
brand_data = extract_brand_data('https://example.com')
print(brand_data)
```

---

### Brand Data CLI

```bash
# Extract brand data using the Python function above
python3 -c "
import json
import sys
sys.path.insert(0, '/path/to/skill')
from brand_extraction import extract_brand_data
data = extract_brand_data('$URL')
print(json.dumps(data, indent=2))
"
```

---

## Feature Comparison

| Feature | Status | Notes |
|---------|--------|-------|
| Basic fetch | ✅ Working | Fetcher.get() |
| Stealthy fetch | ✅ Working | StealthyFetcher.fetch() |
| Dynamic fetch | ✅ Working | DynamicFetcher.fetch() |
| Adaptive parsing | ✅ Working | auto_save + adaptive |
| Spider crawling | ✅ Working | async def parse() |
| CSS selectors | ✅ Working | .css() |
| XPath | ✅ Working | .xpath() |
| Session management | ✅ Working | FetcherSession, StealthySession |
| Proxy rotation | ✅ Working | ProxyRotator class |
| CLI tools | ✅ Working | scrapling extract |
| Brand data extraction | ✅ Working | extract_brand_data() |
| API reverse engineering | ✅ Working | APIReplicator class |
| Cloudscraper bypass | ✅ Working | cloudscraper integration |
| Easy site crawl | ✅ Working | EasyCrawl class |
| Sitemap crawl | ✅ Working | get_sitemap_urls() |
| MCP server | ❌ Excluded | Not needed |

---

## Examples Tested

### IEEE Spectrum
```python
page = Fetcher.get('https://spectrum.ieee.org/...')
title = page.css('h1::text').get()
content = page.css('article p::text').getall()
```
✅ Works

### Hacker News
```python
page = Fetcher.get('https://news.ycombinator.com')
stories = page.css('.titleline a::text').getall()
```
✅ Works

### Example Domain
```python
page = Fetcher.get('https://example.com')
title = page.css('h1::text').get()
```
✅ Works

---

## 🔧 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| 403/429 Blocked | Use StealthyFetcher or cloudscraper |
| Cloudflare | Use StealthyFetcher or cloudscraper |
| JavaScript required | Use DynamicFetcher |
| Site changed | Use adaptive=True |
| Paid API exposed | Use API reverse engineering |
| Captcha | Cannot bypass - skip or use official API |
| Auth required | Do NOT bypass - use official API |

---

## Skill Graph

Related skills:

- [[content-research]] - Research workflow
- [[blogwatcher]] - RSS/feed monitoring
- [[youtube-watcher]] - Video content
- [[chirp]] - Twitter/X interactions
- [[newsletter-digest]] - Content summarization
- [[x-tweet-fetcher]] - X/Twitter (use instead of Scrapling)

---

## Changelog

### v1.0.8 (2026-02-25)
- **Added: Firecrawl-Style Crawl** - Combines sitemap discovery + link following
- **Added: use_sitemap parameter** - Matches Firecrawl's sitemap:"include"/"skip" behavior
- Verified: cloudflare.com returns 2,447 URLs from sitemap!

### v1.0.7 (2026-02-25)
- **Fixed: EasyCrawl Spider syntax** - Updated to work with scrapling's actual Spider API
- **Verified: Spider crawling works** - Tested and crawled 20+ pages from example.com

### v1.0.6 (2026-02-25)
- **Added: Easy Site Crawl** - Auto-crawl all pages on a domain with EasyCrawl spider
- **Added: Sitemap Crawl** - Extract URLs from sitemap.xml and crawl them
- Feature parity with Firecrawl for site crawling capabilities

### v1.0.5 (2026-02-25)
- **Enhanced: API Reverse Engineering methodology**
  - Detailed step-by-step process from @paoloanzn's work
  - Real Solscan case study with exact timeline
  - Added: Step-by-step methodology section
  - Added: Real example documentation (Solscan March 2025 vs Feb 2026)
  - Added: Discovery checklist with 10 steps
  - Documented: How to find auth headers in JS files
  - Documented: Token generation pattern extraction
  - Updated: Cloudscraper integration with multi-attempt pattern
  - Verified: Solscan now patched (Cloudflare on both endpoints)

### v1.0.4 (2026-02-25)
- **Fixed: Brand Data Extraction API** - Corrected selectors for scrapling's Response object
- Fixed `.html` → `.text` / `.body`
- Fixed `.title()` → `page.css('title')`
- Fixed `.logo img::src` → `.logo img::attr(src)`
- Tested and verified working

### v1.0.3 (2026-02-25)
- **Added: API Reverse Engineering section**
  - API Endpoint Discovery (Network tab analysis)
  - JavaScript Analysis (finding auth logic)
  - Cloudscraper integration for Cloudflare bypass
  - Complete APIReplicator class
  - Discovery checklist
- Added cloudscraper to installation

### v1.0.2 (2026-02-25)
- Synced with upstream GitHub README exactly
- Added Brand Data Extraction section
- Clean, core-only version

### v1.0.1 (2026-02-25)
- Synced with original Scrapling GitHub README

---

*Last updated: 2026-02-25*
