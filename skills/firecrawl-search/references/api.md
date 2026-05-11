# Firecrawl API Reference

## Environment

Set your API key:
```bash
export FIRECRAWL_API_KEY=fc-xxxxxxxxxx
```

## API Endpoints

### Search
```bash
POST https://api.firecrawl.dev/v1/search
```

Request body:
```json
{
  "query": "search terms",
  "limit": 10,
  "lang": "en",
  "country": "us"
}
```

### Scrape
```bash
POST https://api.firecrawl.dev/v1/scrape
```

Request body:
```json
{
  "url": "https://example.com",
  "formats": ["markdown", "html", "screenshot"],
  "onlyMainContent": true,
  "includeTags": ["h1", "p", "article"],
  "excludeTags": ["nav", "footer", "aside"]
}
```

### Crawl
```bash
POST https://api.firecrawl.dev/v1/crawl
```

Request body:
```json
{
  "url": "https://example.com",
  "limit": 50,
  "excludePaths": ["/blog", "/admin"],
  "scrapeOptions": {
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}
```

Check status:
```bash
GET https://api.firecrawl.dev/v1/crawl/{job_id}
```

## Response Format

All responses follow this structure:
```json
{
  "success": true,
  "data": { ... },
  "status": "completed"
}
```

## Rate Limits

- Search: Check your Firecrawl dashboard
- Scrape: Check your Firecrawl dashboard
- Crawl: Check your Firecrawl dashboard

## Pricing

See https://firecrawl.dev/pricing for current rates.
