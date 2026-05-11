---
name: mrscraper
description: Run AI-powered, unblockable web scraping, data extraction with natural language via the MrScraper API
tags: [scraping, data-extraction, web-crawling, stealth-browser, web-automation]

homepage: https://mrscraper.com/
vendor: MrScraper
support_email: support@mrscraper.com

required_env_vars: [MRSCRAPER_API_TOKEN]
primary_credential: MRSCRAPER_API_TOKEN

metadata: {"openclaw":{"requires":{"env":["MRSCRAPER_API_TOKEN"]},"primaryEnv":"MRSCRAPER_API_TOKEN"}}

network: {"allowed_hosts":["api.mrscraper.com","api.app.mrscraper.com","sync.scraper.mrscraper.com"]}
---

# MrScraper

Run AI-powered, unblockable web scraping, data extraction with natural language via the MrScraper API

## Actions

This skill supports:

- Opening blocked pages through unblocker (stealth browser + IP rotation)
- Starting AI scraper runs from natural-language instructions
- Rerunning existing scraper configurations on one or multiple URLs
- Running manual workflow-based reruns
- Fetching paginated results and detailed results by ID

This skill is API-only and does not depend on bundled local scripts.

## Base URLs

- Unblocker API: `https://api.mrscraper.com`
- Platform API: `https://api.app.mrscraper.com`

## Authentication

### Unblocker API auth

Use query-param auth on unblocker endpoint:

- `token=<MRSCRAPER_API_TOKEN>`

### Platform API auth

Use header-based auth on platform endpoints:

```http
x-api-token: <MRSCRAPER_API_TOKEN>
accept: application/json
content-type: application/json
```

### How to get `MRSCRAPER_API_TOKEN`?

An API token lets your applications securely interact with MrScraper APIs and rerun scrapers created in the dashboard.

Follow these steps in the dashboard:

1. Click your **User Profile** at the top-right corner.
2. Select **API Tokens**.
3. Click **New Token**.
4. Enter a **name** and set an **expiration date**.
5. Click **Create**.
6. Copy the new token and store it securely as `MRSCRAPER_API_TOKEN`.
7. Use it in requests through the `x-api-token` header.

Security rule:

- Never expose tokens in client-side code (browser/mobile app bundles).
- Store tokens in environment variables or server-side secret managers.

Notes from the auth docs:

- The API key works for all V3 Platform endpoints.
- The same key can be used for endpoints on `sync.scraper.mrscraper.com`.
- For access to endpoints on other hosts, contact `support@mrscraper.com`.

## Install and Runtime

- No local install step is required by this skill document.
- No bundled `scripts/` are required.
- Calls are direct HTTPS requests to the two base URLs above.

## Data and Scope

- Data is sent only to `api.app.mrscraper.com` and `api.mrscraper.com`.
- Responses may contain extracted page content and scrape metadata.
- This skill does not define hidden persistence or background jobs.
- Never expose tokens in logs, commits, or output.

## Endpoints

### 1. Unblocker

- Method: `GET`
- URL: `https://api.mrscraper.com`
- Auth: `token` query parameter

Opens a target URL through stealth browsing and IP rotation, then returns HTML. Use this when direct access is blocked by captcha or anti-bot protections.

#### Query parameters:

| Field            | Type      | Required | Default | Description                             |
| ---------------- | --------- | -------- | ------- | --------------------------------------- |
| `token`          | `string`  | Yes      | —       | Unblocker token (`MRSCRAPER_API_TOKEN`) |
| `url`            | `string`  | Yes      | —       | URL-encoded target URL                  |
| `timeout`        | `number`  | No       | 60      | Max wait in seconds (example `120`)     |
| `geoCode`        | `string`  | No       | None    | Geographic routing code (example `SG`)  |
| `blockResources` | `boolean` | No       | false   | Block non-essential resources           |

#### Request example:

```bash
curl --location 'https://api.mrscraper.com?token=<MRSCRAPER_API_TOKEN>&timeout=120&geoCode=SG&url=https%3A%2F%2Fwww.lazada.sg%2Fproducts%2Fpdp-i111650098-s23209659764.html&blockResources=false'
```

#### Response example:

```html
<!doctype html>
<html>
  <head>...</head>
  <body>...</body>
</html>
```

#### Notes:

- Prefer explicit `geoCode` and practical timeouts for repeatable behavior.
- Only pass cookies when session-specific content is required.

### 2. Create AI Scraper

- Method: `POST`
- Host: `https://api.app.mrscraper.com`
- Path: `/api/v1/scrapers-ai`
- Auth: `x-api-token`

Create a new AI scraper run from natural-language instructions.

#### Payload parameters (for `agent`: `general` or `agent`: `listing`):

| Field          | Type     | Required | Default  | Description                                                |
| -------------- | -------- | -------- | -------- | ---------------------------------------------------------- |
| `url`          | string   | Yes      | —        | Target URL                                                 |
| `message`      | string   | Yes      | —        | Extraction instruction                                     |
| `agent`        | string   | No       | general  | The AI agent type to use for scraping: `general`, `listing`, or `map`  |
| `proxyCountry` | string   | No       | None     | ISO country code for proxy-based scraping                  |

#### Payload parameters (for `agent`: `map`):

| Field             | Type     | Required | Default   | Description                                                                                                   |
| ----------------- | -------- | -------- | --------- | ------------------------------------------------------------------------------------------------------------- |
| `url`             | `string` | Yes      | —         | Target URL                                           |
| `agent`           | `string` | No       | map       | The AI agent type to use for scraping (for this case it is `map`)                                             |
| `maxDepth`        | `number` | No       | 2         | Maximum depth level for crawling links from the starting URL.<br>0 = only the starting URL, 1 = +direct links |
| `maxPages`        | `number` | No       | 50        | Maximum number of pages to scrape during the crawling process.                                                |
| `limit`           | `number` | No       | 1000      | Maximum number of data records to extract across all pages. Scraping stops when this limit is reached.        |
| `includePatterns` | `string` | No       | ""        | Regex patterns to include (separate multiple with `\|\|`)    |
| `excludePatterns` | `string` | No       | ""        | Regex patterns to exclude (separate multiple with `\|\|`)                                      |

#### Request example:

```bash
curl -X POST "https://api.app.mrscraper.com/api/v1/scrapers-ai" \
  -H "x-api-token: <MRSCRAPER_API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "message": "Extract title, price, stocks, and rating",
    "agent": "general"
  }'
```

#### Response example:

```json
{
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "createdAt": "2019-08-24T14:15:22Z",
  "createdById": "e13e432a-5323-4484-a91d-b5969bc564d9",
  "updatedAt": "2019-08-24T14:15:22Z",
  "updatedById": "d8bc6076-4141-4a88-80b9-0eb31643066f",
  "deletedAt": "2019-08-24T14:15:22Z",
  "deletedById": "8ef578ad-7f1e-4656-b48b-b1b4a9aaa1cb",
  "userId": "2c4a230c-5085-4924-a3e1-25fb4fc5965b",
  "scraperId": "6695bf87-aaa6-46b0-b1ee-88586b222b0b",
  "type": "AI",
  "url": "http://example.com",
  "status": "Finished",
  "error": "string",
  "tokenUsage": 0,
  "runtime": 0,
  "data": {}, // MAIN SCRAPED DATA
  "htmlPath": "string",
  "recordingPath": "string",
  "screenshotPath": "string",
  "dataPath": "string"
}
```

#### Notes:

- Choose agent type correctly as each agent is specialized for specified use cases. Use `general` for most standard web scraping tasks. The go to agent if the user doesn't specify or the connected LLM is not confident about the type of page. But mostly used for scraping product page, but handles any type of page very well as well. Use `listing` for scraping listing pages like product listings, job listings, etc. Choose this if the connected LLM can confidently identify whether the given URL is a listing page. Use `map` for crawling and getting all subdomain or subpages of a website. Choose this if the user specifies that the given URL is a website and not a specific page. For `map` agent type, there is a special args that can be used to configure the scraping process.
- For the `map` agent, you can use special arguments to control crawling:<br>`maxDepth` (lower values 1–2 for focused scraping, max 3 recommended),<br>`maxPages` (limits total pages regardless of depth),<br>`limit` (caps total records extracted),<br>and `includePatterns`/`excludePatterns` (regex patterns separated by `||` to specify which URLs to crawl or skip, e.g., `*/products/*||*/blog/*` or `*/cart/*||*.pdf`).<br>If `includePatterns` is an empty string, all URLs are included. If `excludePatterns` is an empty string, no URLs are excluded.

### 3. Rerun AI Scraper

- Method: `POST`
- Host: `https://api.app.mrscraper.com`
- Path: `/api/v1/scrapers-ai-rerun`
- Auth: `x-api-token`

Reruns an existing scraper configuration on a new URL.

#### Payload parameters:

| Field        | Type     | Required | Default | Description                                  |
| ------------ | -------- | -------- | ------- | -------------------------------------------- |
| `scraperId`  | `string` | Yes      | —       | Scraper ID retrieved from created AI scraper |
| `url`        | `string` | Yes      | —       | Target URL                                   |

#### Optional payload parameters for `map` agent:

| Field             | Type   | Required | Default | Description                                                               |
|-------------------|--------|----------|---------|---------------------------------------------------------------------------|
| `maxDepth`        | number | No       | 2       | Crawl depth                                                               |
| `maxPages`        | number | No       | 50      | Maximum pages to crawl                                                    |
| `limit`           | number | No       | 1000    | Result limit                                                              |
| `includePatterns` | string | No       | ""      | Regex patterns to include (separate multiple with `\|\|`)                 |
| `excludePatterns` | string | No       | ""      | Regex patterns to exclude (separate multiple with `\|\|`)                 |

#### Request example:

```bash
curl -X POST "https://api.app.mrscraper.com/api/v1/scrapers-ai-rerun" \
  -H "accept: application/json" \
  -H "x-api-token: <MRSCRAPER_API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "scraperId": "6695bf87-aaa6-46b0-b1ee-88586b222b0b",
    "url": "https://shopee.sg/"
  }'
```

#### Response example:

```json
{
  "message": "Successful operation!",
  "data": {
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "createdAt": "2019-08-24T14:15:22Z",
    "createdById": "e13e432a-5323-4484-a91d-b5969bc564d9",
    "updatedAt": "2019-08-24T14:15:22Z",
    "updatedById": "d8bc6076-4141-4a88-80b9-0eb31643066f",
    "deletedAt": "2019-08-24T14:15:22Z",
    "deletedById": "8ef578ad-7f1e-4656-b48b-b1b4a9aaa1cb",
    "userId": "2c4a230c-5085-4924-a3e1-25fb4fc5965b",
    "scraperId": "6695bf87-aaa6-46b0-b1ee-88586b222b0b",
    "type": "Rerun-AI",
    "url": "http://example.com",
    "status": "Finished",
    "error": "string",
    "tokenUsage": 0,
    "runtime": 0,
    "data": {}, // MAIN SCRAPED DATA
    "htmlPath": "string",
    "recordingPath": "string",
    "screenshotPath": "string",
    "dataPath": "string",
    "htmlContent": "string"
  }
}
```

### 4. Bulk Rerun AI Scraper

- Method: `POST`
- Host: `https://api.app.mrscraper.com`
- Path: `/api/v1/scrapers-ai-rerun/bulk`
- Auth: `x-api-token`

Runs one scraper configuration over multiple URLs.

#### Payload parameters:

| Field       | Type            | Required | Default | Description                       |
| ----------- | --------------- | -------- | ------- | --------------------------------- |
| `scraperId` | `string`        | Yes      | —       | Existing AI scraper configuration ID |
| `urls`      | `array[string]` | Yes      | —       | Target URLs to run                |

#### Request example:

```bash
curl -X POST "https://api.app.mrscraper.com/api/v1/scrapers-ai-rerun/bulk" \
  -H "x-api-token: " \
  -H "Content-Type: application/json" \
  -d '{
    "scraperId": "6695bf87-aaa6-46b0-b1ee-88586b222b0b",
    "urls": [
      "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
      "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
      "https://books.toscrape.com/catalogue/soumission_998/index.html"
    ]
  }'
```

#### Response example:

```json
{
  "message": "Bulk rerun started successfully",
  "data": {
    "bulkResultId": "f89f8f58-3c9a-42e5-a72e-59fa6c389f09",
    "status": "Running",
    "totalUrls": 3
  }
}
```

### 5. Rerun Manual Scraper

- Method: `POST`
- Host: `https://api.app.mrscraper.com`
- Path: `/api/v1/scrapers-manual-rerun`
- Auth: `x-api-token`

Executes a rerun using a manual browser workflow.

#### Creating a Manual Scraper

Before calling the manual rerun endpoint, you need to create and save a manual scraper from the dashboard. Follow these steps:

1. Open the `MrScraper` dashboard and go to `Scraper`.
2. Click `New Manual Scraper +`.
3. Enter your target URL.
4. Add workflow steps that match your site's behavior (e.g., `Input`, `Click`, `Delay`, `Extract`, `Inject JavaScript`).
5. Configure pagination if needed (using options like `Query Pagination`, `Directory Pagination`, or `Next Page Link`).
6. Test and save the scraper, then copy its `scraperId` to use in API reruns.

#### Payload parameters:

| Field        | Type           | Required | Default | Description                                                                                                      |
|--------------|----------------|----------|---------|------------------------------------------------------------------------------------------------------------------|
| `scraperId`  | `string`       | Yes      | —       | ID of the manual scraper to rerun.                                                                               |
| `url`        | `string`       | Yes      | —       | Target URL for the rerun.                                                                                        |
| `workflow`   | `array<object>`| No       | None    | Allows overriding the saved workflow steps. By default, uses the workflow saved during manual creation.|

#### Request example:

```bash
curl -X POST "https://api.app.mrscraper.com/api/v1/scrapers-manual-rerun" \
  -H "accept: application/json" \
  -H "x-api-token: " \
  -H "Content-Type: application/json" \
  -d '{
    "scraperId": "6695bf87-aaa6-46b0-b1ee-88586b222b0b",
    "url": "https://books.toscrape.com/",
    "workflow": [
      {
        "type": "extract",
        "data": {
          "extraction_type": "text",
          "attribute": null,
          "name": "book",
          "selector": "h3 a"
        }
      }
    ],
    "record": false,
    "paginator": {
      "type": "query_pagination",
      "max_page": 1,
      "enabled": false
    }
  }'
```

#### Response example:

```json
{
  "message": "Successful operation!",
  "data": {
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "createdAt": "2019-08-24T14:15:22Z",
    "createdById": "e13e432a-5323-4484-a91d-b5969bc564d9",
    "updatedAt": "2019-08-24T14:15:22Z",
    "updatedById": "d8bc6076-4141-4a88-80b9-0eb31643066f",
    "deletedAt": "2019-08-24T14:15:22Z",
    "deletedById": "8ef578ad-7f1e-4656-b48b-b1b4a9aaa1cb",
    "userId": "2c4a230c-5085-4924-a3e1-25fb4fc5965b",
    "scraperId": "6695bf87-aaa6-46b0-b1ee-88586b222b0b",
    "type": "Rerun-AI",
    "url": "http://example.com",
    "status": "Finished",
    "error": "string",
    "tokenUsage": 0,
    "runtime": 0,
    "data": {}, // MAIN SCRAPED DATA
    "htmlPath": "string",
    "recordingPath": "string",
    "screenshotPath": "string",
    "dataPath": "string",
    "htmlContent": "string"
  }
}
```

### 6. Bulk Rerun Manual Scraper

- Method: `POST`
- Host: `https://api.app.mrscraper.com`
- Path: `/api/v1/scrapers-manual-rerun/bulk`
- Auth: `x-api-token`

Runs one scraper configuration over multiple URLs.

#### Payload parameters:

| Field       | Type            | Required | Default | Description                       |
| ----------- | --------------- | -------- | ------- | --------------------------------- |
| `scraperId` | `string`        | Yes      | —       | Existing manual scraper configuration ID |
| `urls`      | `array[string]` | Yes      | —       | Target URLs to run                |

#### Request example:

```bash
curl -X POST "https://api.app.mrscraper.com/api/v1/scrapers-manual-rerun/bulk" \
  -H "x-api-token: " \
  -H "Content-Type: application/json" \
  -d '{
    "scraperId": "6695bf87-aaa6-46b0-b1ee-88586b222b0b",
    "urls": [
      "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
      "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
      "https://books.toscrape.com/catalogue/soumission_998/index.html"
    ]
  }'
```

#### Response example:

```json
{
  "message": "Bulk rerun started successfully",
  "data": {
    "bulkResultId": "f89f8f58-3c9a-42e5-a72e-59fa6c389f09",
    "status": "Running",
    "totalUrls": 3
  }
}
```

### 7. Fetch Results

- Method: `GET`
- Host: `https://api.app.mrscraper.com`
- Path: `/api/v1/results`
- Auth: `x-api-token`

Returns paginated scrape results.

#### Query parameters:

| Field             | Type   | Required | Default     | Description               |
|-------------------|--------|----------|-------------|---------------------------|
| `sortField`       | string | Yes      | `updatedAt` | Sort column               |
| `sortOrder`       | string | Yes      | `DESC`      | Sort direction            |
| `page`            | number | Yes      | 1           | Page number               |
| `pageSize`        | number | Yes      | 10          | Items per page            |
| `search`          | string | No       | None        | Search keyword            |
| `dateRangeColumn` | string | No       | `createdAt` | Date field to filter      |
| `startAt`         | string | No       | None        | Date range start (ISO)    |
| `endAt`           | string | No       | None        | Date range end (ISO)      |

#### Notes:

- `sortField` options: `createdAt`, `updatedAt`, `id`, `type`, `url`, `status`, `error`, `tokenUsage`, `runtime`
- `sortOrder` options: `ASC`, `DESC`
- `dateRangeColumn` options: `createdAt`, `updatedAt`

#### Request example:

```bash
curl -X GET "https://api.app.mrscraper.com/api/v1/results?sortField=updatedAt&sortOrder=DESC&pageSize=10&page=1" \
  -H "accept: application/json" \
  -H "x-api-token: <MRSCRAPER_API_TOKEN>"
```

#### Response example:

```json
{
  "message": "Successful fetch",
  "data": [
    {
      "createdAt": "2025-11-11T09:50:09.722Z",
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "userId": "2c4a230c-5085-4924-a3e1-25fb4fc5965b",
      "scraperId": "6695bf87-aaa6-46b0-b1ee-88586b222b0b",
      "type": "AI",
      "url": "http://example.com",
      "status": "Finished",
      "error": "string",
      "tokenUsage": 5,
      "runtime": 0,
      "data": "{ \"title\": \"Product A\", \"price\": \"$10\" }",
      "htmlPath": "string",
      "recordingPath": "string",
      "screenshotPath": "string",
      "dataPath": "string"
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 10,
    "total": 1,
    "totalPage": 1
  }
}
```

### 8. Fetch Detailed Result by ID

- Method: `GET`
- Host: `https://api.app.mrscraper.com`
- Path: `/api/v1/results/{id}`
- Auth: `x-api-token`

Returns one detailed result object for a specific result ID.

#### Query parameters:

| Field | Type     | Required | Default | Description |
| ----- | -------- | -------- | ------- | ----------- |
| `id`  | `string` | Yes      | —       | Result ID   |

#### Request example:

```bash
curl -X GET "https://api.app.mrscraper.com/api/v1/results/497f6eca-6276-4993-bfeb-53cbbbba6f08" \
  -H "accept: application/json" \
  -H "x-api-token: <MRSCRAPER_API_TOKEN>"
```

#### Response example:

```json
{
  "message": "Successful fetch",
  "data": [
    {
      "createdAt": "2025-11-11T09:50:09.722Z",
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "userId": "2c4a230c-5085-4924-a3e1-25fb4fc5965b",
      "scraperId": "6695bf87-aaa6-46b0-b1ee-88586b222b0b",
      "type": "AI",
      "url": "http://example.com",
      "status": "Finished",
      "error": "string",
      "tokenUsage": 5,
      "runtime": 0,
      "data": "string",
      "htmlPath": "string",
      "recordingPath": "string",
      "screenshotPath": "string",
      "dataPath": "string"
    }
  ]
}
```

## Errors

Standard platform API errors:

| Status | Meaning                      |
| ------ | ---------------------------- |
| `400`  | Invalid request payload      |
| `401`  | Missing or invalid API token |
| `404`  | Scraper or result not found  |
| `429`  | Rate limit exceeded          |
| `500`  | Internal scraper error       |

Error format:

```json
{
  "message": "string",
  "error": "string",
  "statusCode": "number"
}
```

## Operating Rules

- Validate required fields before every call.
- Use pagination for large result sets.
- Retry on `429` with exponential backoff.
- Never expose credentials in outputs.
