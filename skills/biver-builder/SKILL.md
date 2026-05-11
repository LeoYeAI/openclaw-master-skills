---
name: biver-builder
description: |
  Integration skill for Biver Landing Page Builder API. Use when:
  (1) Creating, updating, or deleting landing pages
  (2) Managing subdomains (.lp.biver.id) or custom domains
  (3) Generating pages/sections with AI
  (4) Managing products, forms, or gallery assets
  (5) Configuring workspace settings and branding
metadata:
  version: 1.0.4
  primaryEnv: BIVER_API_KEY
  requiredEnvVars:
    - BIVER_API_KEY
  optionalEnvVars:
    - BIVER_API_BASE_URL
  author: RamaAditya49
  repository: https://github.com/RamaAditya49/biver-builder
---

# Biver Builder API Skill

## Before You Install

> **Security Checklist**
>
> Before installing or supplying credentials, please review:
>
> 1. **Credential Required**: This skill requires `BIVER_API_KEY` to operate
> 2. **Start with Test Keys**: Use `bvr_test_` prefix keys for initial testing — never use `bvr_live_` keys until you trust the skill
> 3. **Verify Scopes**: Check required API key scopes below and use least-privilege principle
> 4. **Rotate Keys**: Periodically rotate your API keys for security
> 5. **Inspect Source**: If using manual installation, inspect the GitHub repository code before cloning

---

## Installation

### Via ClawdHub (Recommended)
```bash
clawdhub install biver-builder
```

### Manual

> **Warning**: Cloning external repositories can introduce arbitrary code. **Inspect the repository first** before running:
>
> ```bash
> # Step 1: Review the source code
> git clone https://github.com/RamaAditya49/biver-builder.git /tmp/biver-builder-review
> # Review files in /tmp/biver-builder-review before proceeding
>
> # Step 2: Only after review, install to your skills directory
> git clone https://github.com/RamaAditya49/biver-builder.git ~/.openclaw/skills/biver-builder
> ```

---

## Credential Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BIVER_API_KEY` | Your Biver API key | `bvr_live_xxxxx` or `bvr_test_xxxxx` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BIVER_API_BASE_URL` | Custom API base URL | `https://api.biver.id` |

### Setting Up Credentials

**Via OpenClaw Dashboard:**
1. Navigate to Settings > Environment Variables
2. Add `BIVER_API_KEY` with your API key value
3. (Optional) Add `BIVER_API_BASE_URL` for custom endpoints

**Security Best Practices:**
- Use `bvr_test_` prefix keys for development/testing
- Use `bvr_live_` prefix keys only in production **after you trust the skill**
- **Verify required scopes** before creating your API key — only grant minimum permissions needed
- Never commit API keys to version control
- Rotate keys periodically
- **Do not supply credentials** until you have reviewed the skill or confirmed it from a verified source

### How to Get Your API Key

1. Log in to [Biver Dashboard](https://biver.id)
2. Go to **Settings** > **API Keys**
3. Click **Generate New Key**
4. **Select required scopes** (see Required Scopes section below — grant only what you need)
5. Choose key type: `bvr_test_` for testing, `bvr_live_` for production
6. Copy and store securely (shown only once)

> **Scope Recommendation**: Start with read-only scopes (`*:read`) for testing. Add write scopes only when needed.

---

## Quick Reference

### Base URL
```
https://api.biver.id
```

### Authentication Headers
```typescript
// Use environment variables for security
const apiKey = process.env.BIVER_API_KEY;

// Headers configuration
{
  'X-API-Key': apiKey,
  'Authorization': `Bearer ${apiKey}`
}
```

### API Key Prefixes
| Prefix | Environment | Usage |
|--------|-------------|-------|
| `bvr_live_` | Production | Real data operations |
| `bvr_test_` | Sandbox | Testing without affecting real data |

### Endpoint Lookup

| Task | Endpoint | Method | Auth | Scope |
|------|----------|--------|------|-------|
| List pages | `/v1/pages` | GET | Yes | pages:read |
| Create page | `/v1/pages` | POST | Yes | pages:write |
| Get page | `/v1/pages/:id` | GET | Yes | pages:read |
| Update page | `/v1/pages/:id` | PATCH | Yes | pages:write |
| Delete page | `/v1/pages/:id` | DELETE | Yes | pages:write |
| Deploy page | `/v1/pages/:id/deploy` | POST | Yes | pages:write |
| List subdomains | `/v1/subdomains` | GET | Yes | pages:read |
| Create subdomain | `/v1/subdomains` | POST | Yes | pages:write |
| Update subdomain | `/v1/subdomains/:id` | PATCH | Yes | pages:write |
| Delete subdomain | `/v1/subdomains/:id` | DELETE | Yes | pages:write |
| List domains | `/v1/domains` | GET | Yes | domains:read |
| Add custom domain | `/v1/domains` | POST | Yes | domains:write |
| Set primary domain | `/v1/domains/:id/primary` | POST | Yes | domains:write |
| Delete domain | `/v1/domains/:id` | DELETE | Yes | domains:write |
| List sections | `/v1/sections` | GET | Yes | sections:read |
| Create section | `/v1/sections` | POST | Yes | sections:write |
| Update section | `/v1/sections/:id` | PATCH | Yes | sections:write |
| Delete section | `/v1/sections/:id` | DELETE | Yes | sections:write |
| List products | `/v1/products` | GET | Yes | products:read |
| Create product | `/v1/products` | POST | Yes | products:write |
| Update product | `/v1/products/:id` | PATCH | Yes | products:write |
| Delete product | `/v1/products/:id` | DELETE | Yes | products:write |
| List forms | `/v1/forms` | GET | Yes | forms:read |
| Create form | `/v1/forms` | POST | Yes | forms:write |
| Get submissions | `/v1/forms/:id/submissions` | GET | Yes | forms:read |
| Submit form | `/v1/forms/:id/submit` | POST | **No** | - |
| List gallery | `/v1/gallery` | GET | Yes | gallery:read |
| Upload asset | `/v1/gallery` | POST | Yes | gallery:read |
| Delete asset | `/v1/gallery/:id` | DELETE | Yes | gallery:read |
| Get workspace | `/v1/workspace/settings` | GET | Yes | workspace:read |
| Update workspace | `/v1/workspace/settings` | PUT | Yes | workspace:write |
| Update branding | `/v1/workspace/branding` | PUT | Yes | workspace:write |
| Update SEO | `/v1/workspace/seo` | PUT | Yes | workspace:write |
| AI generate page | `/v1/ai/pages` | POST | Yes | ai:generate |
| AI generate section | `/v1/ai/sections` | POST | Yes | ai:generate |
| Health check | `/health` | GET | **No** | - |

---

## Authentication

### Required Scopes

| Scope | Description |
|-------|-------------|
| `pages:read` | Read pages |
| `pages:write` | Create, update, delete pages |
| `sections:read` | Read sections |
| `sections:write` | Create, update, delete sections |
| `products:read` | Read products |
| `products:write` | Manage product catalog |
| `forms:read` | Read forms and submissions |
| `forms:write` | Create/update forms |
| `gallery:read` | Access gallery assets |
| `domains:read` | View custom domains |
| `domains:write` | Add/remove custom domains |
| `subdomains:read` | View subdomains |
| `subdomains:write` | Create/update/delete subdomains |
| `workspace:read` | Read workspace settings |
| `workspace:write` | Update workspace settings |
| `ai:generate` | Generate pages/sections with AI |

---

## Common Workflows

### Workflow 1: Create Landing Page with Subdomain

```typescript
const API_KEY = process.env.BIVER_API_KEY;
const BASE_URL = process.env.BIVER_API_BASE_URL || 'https://api.biver.id';

// Step 1: Create subdomain
const subdomain = await fetch(`${BASE_URL}/v1/subdomains`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  body: JSON.stringify({
    subdomain: 'my-store',
    title: 'Summer Sale 2026',
    description: 'Our biggest sale event',
    pathSlug: 'summer-sale'
  })
});
// Result: my-store.lp.biver.id/summer-sale

// Step 2: Create sections for the page
const section = await fetch(`${BASE_URL}/v1/sections?pageId=PAGE_ID`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  body: JSON.stringify({
    type: 'hero',
    name: 'Hero Section',
    htmlContent: '<div class="hero">...</div>',
    cssContent: '.hero { ... }',
    visible: true,
    order: 0
  })
});

// Step 3: Update subdomain status to publish
await fetch(`${BASE_URL}/v1/subdomains/${subdomainId}`, {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  body: JSON.stringify({
    status: 'published'
  })
});
```

### Workflow 2: Setup Custom Domain

```typescript
const API_KEY = process.env.BIVER_API_KEY;
const BASE_URL = process.env.BIVER_API_BASE_URL || 'https://api.biver.id';

// Step 1: Add custom domain
const domain = await fetch(`${BASE_URL}/v1/domains`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  body: JSON.stringify({
    domain: 'example.com',
    isPrimary: true,
    landingPageId: 'page_123'
  })
});

// Step 2: Configure DNS (outside API)
// Add verification token to DNS records
// Token provided in response: verificationToken

// Step 3: Set as primary (optional)
await fetch(`${BASE_URL}/v1/domains/${domainId}/primary`, {
  method: 'POST',
  headers: { 'X-API-Key': API_KEY }
});
```

### Workflow 3: Generate Page with AI

```typescript
const API_KEY = process.env.BIVER_API_KEY;
const BASE_URL = process.env.BIVER_API_BASE_URL || 'https://api.biver.id';

const aiPage = await fetch(`${BASE_URL}/v1/ai/pages`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  body: JSON.stringify({
    prompt: 'Create a landing page for a coffee shop called Morning Brew',
    style: 'modern',
    industry: 'fnb',
    language: 'en'
  })
});
// Returns: title, content.sections[], suggestedSlug
```

### Workflow 4: Upload Asset and Create Page

```typescript
const API_KEY = process.env.BIVER_API_KEY;
const BASE_URL = process.env.BIVER_API_BASE_URL || 'https://api.biver.id';

// Step 1: Upload image to gallery
const formData = new FormData();
formData.append('file', imageFile);

const asset = await fetch(`${BASE_URL}/v1/gallery`, {
  method: 'POST',
  headers: { 'X-API-Key': API_KEY },
  body: formData
});

// Step 2: Use asset URL in page content
const page = await fetch(`${BASE_URL}/v1/pages`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  body: JSON.stringify({
    title: 'Product Catalog',
    slug: 'catalog',
    content: {
      sections: [{
        type: 'image',
        imageUrl: asset.data.url
      }]
    }
  })
});
```

---

## API Reference

### Pages API

**Base:** `/v1/pages` | **Scope:** `pages:read` / `pages:write`

| Endpoint | Method | Description | Query Params / Body |
|----------|--------|-------------|---------------------|
| `/v1/pages` | GET | List pages | `page`, `limit`, `status`, `search` |
| `/v1/pages` | POST | Create page | `title`, `slug`, `content`, `meta`, `status` |
| `/v1/pages/:id` | GET | Get page detail | - |
| `/v1/pages/:id` | PATCH | Update page | Partial body |
| `/v1/pages/:id` | DELETE | Delete page | - |
| `/v1/pages/:id/deploy` | POST | Publish page | - |

**Page Object:**
```json
{
  "id": "page_123",
  "title": "Summer Sale",
  "slug": "summer-sale",
  "status": "published",
  "publishedAt_ms": 1708704000000,
  "createdAt_ms": 1708617600000
}
```

**Create Page Body:**
```json
{
  "title": "Page Title",
  "slug": "page-slug",
  "content": { "sections": [] },
  "meta": {
    "description": "SEO description",
    "keywords": "keyword1, keyword2"
  },
  "status": "draft"
}
```

---

### Sections API

**Base:** `/v1/sections` | **Scope:** `sections:read` / `sections:write`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/sections` | GET | List sections (`?type=`, `?pageId=`) |
| `/v1/sections` | POST | Create section |
| `/v1/sections/:id` | GET | Get section detail |
| `/v1/sections/:id` | PATCH | Update section |
| `/v1/sections/:id` | DELETE | Delete section |

**Section Types:** `hero`, `text`, `image`, `image_slider`, `faq`, `features`, `pricing`, `cta`, `testimonials`, `contact`

**Create Section Body:**
```json
{
  "type": "hero",
  "name": "Hero Section",
  "htmlContent": "<div>...</div>",
  "cssContent": ".class { ... }",
  "visible": true,
  "order": 0,
  "customClass": "my-custom",
  "anchorId": "hero"
}
```

---

### Products API

**Base:** `/v1/products` | **Scope:** `products:read` / `products:write`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/products` | GET | List products (`?page`, `?limit`, `?category`) |
| `/v1/products` | POST | Create product |
| `/v1/products/:id` | GET | Get product detail |
| `/v1/products/:id` | PATCH | Update product |
| `/v1/products/:id` | DELETE | Delete product |

**Create Product Body:**
```json
{
  "name": "Product Name",
  "description": "Full description",
  "price": 99000,
  "compareAtPrice": 149000,
  "sku": "PROD-001",
  "stock": 100,
  "category": "electronics",
  "images": ["url1", "url2"],
  "isActive": true
}
```

---

### Forms API

**Base:** `/v1/forms` | **Scope:** `forms:read` / `forms:write`

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/v1/forms` | GET | List forms | Yes |
| `/v1/forms` | POST | Create form | Yes |
| `/v1/forms/:id` | GET | Get form detail | Yes |
| `/v1/forms/:id` | PATCH | Update form | Yes |
| `/v1/forms/:id` | DELETE | Delete form | Yes |
| `/v1/forms/:id/submit` | POST | Submit form | **No** |
| `/v1/forms/:id/submissions` | GET | Get submissions | Yes |

**Submit Form Body (Public - No Auth):**
```json
{
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello!"
  }
}
```

---

### Gallery API

**Base:** `/v1/gallery` | **Scope:** `gallery:read`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/gallery` | GET | List items (`?type=image|video|document`, `?search`) |
| `/v1/gallery` | POST | Upload asset (multipart/form-data) |
| `/v1/gallery/:id` | GET | Get asset detail |
| `/v1/gallery/:id` | DELETE | Delete asset |

**Gallery Item Response:**
```json
{
  "id": "gallery_123",
  "filename": "hero-image.png",
  "url": "https://cdn.biver.id/assets/xxx.png",
  "type": "image",
  "mimeType": "image/png",
  "size": 102400,
  "width": 1920,
  "height": 1080
}
```

---

### Subdomains API

**Base:** `/v1/subdomains` | **Scope:** `pages:read` / `pages:write`

Subdomains create landing pages at `{name}.lp.biver.id`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/subdomains` | GET | List subdomains (`?page`, `?limit`, `?status`) |
| `/v1/subdomains` | POST | Create subdomain |
| `/v1/subdomains/:id` | GET | Get subdomain detail |
| `/v1/subdomains/:id` | PATCH | Update subdomain |
| `/v1/subdomains/:id` | DELETE | Delete subdomain |

**Create Subdomain Body:**
```json
{
  "subdomain": "my-store",
  "title": "My Store",
  "description": "Store description",
  "pathSlug": "promo"
}
```

**Subdomain Rules:**
- `subdomain`: 3-63 chars, lowercase a-z, 0-9, hyphens
- `pathSlug`: Optional, creates additional URL at `{subdomain}.lp.biver.id/{pathSlug}`
- `status`: `draft`, `published`, `archived`

**Update Subdomain Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Page title |
| `description` | string | Page description |
| `pathSlug` | string \| null | URL path (null to remove) |
| `status` | string | `draft`, `published`, `archived` |
| `metaTitle` | string | SEO title |
| `metaDescription` | string | SEO description |
| `favicon` | string (URL) | Favicon URL |
| `ogImage` | string (URL) | Open Graph image |
| `noIndex` | boolean | Prevent indexing |
| `noFollow` | boolean | Prevent link following |

---

### Domains API (Custom Domains)

**Base:** `/v1/domains` | **Scope:** `domains:read` / `domains:write`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/domains` | GET | List custom domains |
| `/v1/domains` | POST | Add custom domain |
| `/v1/domains/:id` | GET | Get domain detail (includes DNS records) |
| `/v1/domains/:id` | PATCH | Update domain |
| `/v1/domains/:id` | DELETE | Remove domain |
| `/v1/domains/:id/primary` | POST | Set as primary domain |

**Add Domain Body:**
```json
{
  "domain": "example.com",
  "isPrimary": true,
  "landingPageId": "page_123"
}
```

**Domain Response:**
```json
{
  "id": "domain_123",
  "domain": "example.com",
  "isPrimary": true,
  "isVerified": true,
  "sslStatus": "active",
  "verificationStatus": "verified",
  "verificationToken": "bvr_verify_xxx",
  "landingPageId": "page_123"
}
```

**DNS Configuration (CNAME Setup):**

> **AI Agent:** When helping users set up custom domains, explain the following CNAME configuration steps clearly.

After adding a custom domain via the API, configure your DNS records with your DNS provider:

1. **Point your CNAME record to:**
   ```
   custom.biver.id
   ```

2. **Example Configuration:**
   | Record Type | Name/Host | Value/Target |
   |-------------|-----------|--------------|
   | CNAME | `shop` (or `www`) | `custom.biver.id` |

3. **What this does:**
   - If your domain is `shop.example.com`, add a CNAME record with name `shop` pointing to `custom.biver.id`
   - If using apex domain (`example.com`), check if your DNS provider supports CNAME flattening or use A records as provided in the domain detail response

4. **Propagation:** DNS changes may take 5-60 minutes to propagate globally.

---

### Workspace API

**Base:** `/v1/workspace` | **Scope:** `workspace:read` / `workspace:write`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/workspace/settings` | GET | Get workspace settings |
| `/v1/workspace/settings` | PUT | Update settings |
| `/v1/workspace/branding` | PUT | Update branding |
| `/v1/workspace/seo` | PUT | Update SEO settings |
| `/v1/workspace/public` | GET | Public workspace info (no auth) |

**Workspace Settings:**
```json
{
  "id": "workspace_123",
  "name": "My Workspace",
  "slug": "my-workspace",
  "plan": "ARCHITECT",
  "settings": {
    "timezone": "Asia/Jakarta",
    "language": "en",
    "currency": "USD"
  },
  "branding": {
    "logo": "https://cdn.biver.id/logos/xxx.png",
    "primaryColor": "#3B82F6",
    "fontFamily": "Inter"
  },
  "seo": {
    "title": "My Business",
    "description": "We build great landing pages",
    "keywords": "landing page, builder"
  }
}
```

---

### AI Generation API

**Base:** `/v1/ai` | **Scope:** `ai:generate`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/ai/pages` | POST | Generate page with AI |
| `/v1/ai/sections` | POST | Generate section with AI |
| `/v1/ai/context` | GET | Get AI templates/context |

**Generate Page Body:**
```json
{
  "prompt": "Create a landing page for a coffee shop",
  "style": "modern",
  "industry": "fnb",
  "language": "en"
}
```

**Style Options:** `modern`, `minimal`, `bold`, `elegant`, `playful`
**Industry Options:** `saas`, `fnb`, `ecommerce`, `agency`, `healthcare`, `education`, `finance`, `realestate`

---

## Error Codes

| Code | HTTP | Description | Solution |
|------|------|-------------|----------|
| `UNAUTHORIZED` | 401 | Invalid or missing API key | Check authentication header |
| `KEY_EXPIRED` | 401 | API key has expired | Generate new key from dashboard |
| `KEY_REVOKED` | 401 | API key was revoked | Generate new key from dashboard |
| `FORBIDDEN` | 403 | Insufficient scope permission | Check API key scopes |
| `NOT_FOUND` | 404 | Resource not found | Verify resource ID |
| `DUPLICATE_SUBDOMAIN` | 409 | Subdomain already taken | Choose different subdomain |
| `DUPLICATE_DOMAIN` | 409 | Domain already exists | Use different domain |
| `VALIDATION_ERROR` | 422 | Request validation failed | Check request body format |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Wait for reset or upgrade plan |
| `INTERNAL_ERROR` | 500 | Server error | Retry or contact support |

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": [
        { "field": "title", "message": "Title is required", "code": "required" }
      ]
    }
  }
}
```

---

## Rate Limits

| Plan | Requests/Minute | Target User |
|------|-----------------|-------------|
| SCOUT | 30 | Free tier |
| CRAFTSMAN | 60 | Small businesses |
| ARCHITECT | 120 | Growing businesses |
| ENGINEER | 300 | Medium businesses |
| FOUNDER | 600 | Agencies |
| CHIEF | 2000 | Enterprise |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1708704000000
X-RateLimit-Plan: CRAFTSMAN
```

---

## Response Format

All responses follow this structure:

**Success:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Paginated:**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "totalPages": 3
    }
  }
}
```

---

## Security Considerations

### API Key Safety
- **Never** hardcode API keys in source code
- **Always** use environment variables or secure secret stores
- **Use test keys** (`bvr_test_`) for development
- **Limit scopes** to minimum required for your use case

### DNS Configuration
- Custom domain setup requires DNS changes outside this API
- Always verify domain ownership before making DNS changes
- Keep DNS verification tokens secure

### Rate Limiting
- Respect rate limits based on your plan
- Implement retry logic with exponential backoff
- Monitor `X-RateLimit-Remaining` header

---

## Support

- **Dashboard:** https://biver.id/dashboard
- **Email:** support@biver.id
- **Health Check:** `GET /health` (no auth required)
