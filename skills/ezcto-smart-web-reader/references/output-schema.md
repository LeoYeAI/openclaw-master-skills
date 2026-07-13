# EZCTO Output JSON Schema (OpenClaw Edition)

All translation output MUST conform to this schema. Fields marked as **required** must always be present.

---

## OpenClaw Wrapper Format

When used as an OpenClaw skill, the business data MUST be wrapped in this envelope:

```json
{
  "skill": "ezcto-web-translator-openclaw",
  "version": "1.0.0",
  "status": "success" | "error",

  "result": {
    // Full translation JSON (see Business Data Schema below)
  },

  "metadata": {
    "source": "cache" | "fresh_translation",
    "cache_key": "~/.ezcto/cache/{url_hash}.json",
    "markdown_summary": "~/.ezcto/cache/{url_hash}.meta.md",
    "translation_time_ms": 1234,
    "token_cost": 0 | 1500,
    "html_hash": "sha256:abc123...",
    "html_size_kb": 120,
    "translated_at": "2026-02-16T12:34:56Z",
    "site_types_detected": ["crypto", "ecommerce"]
  },

  "agent_suggestions": {
    "primary_action": {
      "label": "Buy Now",
      "url": "/checkout",
      "purpose": "complete_purchase",
      "priority": "high"
    },
    "next_actions": [
      {
        "action": "visit_url",
        "url": "/reviews",
        "reason": "Check product reviews before purchase",
        "priority": 1
      }
    ],
    "skills_to_chain": [
      {
        "skill": "price-tracker",
        "input": "{{ result.extensions.ecommerce.products[0] }}",
        "reason": "Track price history for this product"
      }
    ],
    "cache_freshness": {
      "cached_at": "2026-02-16T10:00:00Z",
      "should_refresh_after": "2026-02-17T10:00:00Z",
      "refresh_priority": "low" | "medium" | "high"
    }
  },

  "error": null | {
    "code": "fetch_failed" | "translation_failed" | "validation_failed",
    "message": "Human-readable error description",
    "details": {},
    "suggestion": "Try checking if the URL is accessible"
  }
}
```

---

## Business Data Schema (inside `result`)

### Complete Structure

```json
{
  "meta": {
    "url": "(required) Original website URL",
    "title": "(required) Page title from <title> or <h1>",
    "description": "(required) Page description from meta description or first paragraph",
    "language": "(required) Page language (ISO 639-1 code, e.g., 'en', 'zh', 'ja')",
    "site_type": "(required) Array of detected types: ['general'], ['crypto'], ['ecommerce'], etc.",
    "translated_at": "(required) Translation timestamp in ISO 8601 format",

    "favicon": "Favicon URL if available",
    "site_name": "Site/organization name",
    "canonical_url": "Canonical URL from <link rel='canonical'>",
    "breadcrumb": [
      {"label": "Home", "url": "/"},
      {"label": "Products", "url": "/products"},
      {"label": "Current Page", "url": "/products/item"}
    ],
    "parent_url": "/products",

    "seo": {
      "keywords": ["keyword1", "keyword2"],
      "author": "Article author name",
      "published_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-02-10T14:30:00Z",
      "og_image": "https://...",
      "og_type": "website | article | product"
    },

    "technical": {
      "rendering_type": "static | client-side | hybrid",
      "requires_javascript": true | false,
      "http_status": 200,
      "page_status": "normal | error | maintenance | login_required"
    }
  },

  "navigation": [
    {
      "label": "(required) Navigation item text",
      "url": "(required) Link URL",
      "is_external": "Boolean — true if link points to external domain",
      "is_current": "Boolean — true if this is the current page"
    }
  ],

  "content": [
    {
      "section": "(required) Section name: hero / about / features / pricing / team / faq / footer / etc.",
      "role": "banner | main | complementary | contentinfo (ARIA roles)",
      "heading": "Section heading text",
      "heading_level": 1-6,
      "text": "Section body text content",
      "items": ["List items if the section contains a list"],
      "subsections": [
        {
          "section": "nested_section_name",
          "heading": "Subsection heading",
          "text": "Subsection text"
        }
      ]
    }
  ],

  "entities": {
    "organization": "Organization / company / project name",
    "people": ["List of people mentioned"],
    "contact": {
      "email": "Contact email",
      "phone": "Contact phone",
      "address": "Physical address",
      "form_url": "Contact form URL"
    },
    "social_links": {
      "twitter": "Twitter/X URL",
      "telegram": "Telegram URL",
      "discord": "Discord URL",
      "github": "GitHub URL",
      "linkedin": "LinkedIn URL",
      "facebook": "Facebook URL",
      "instagram": "Instagram URL",
      "youtube": "YouTube URL",
      "medium": "Medium URL",
      "reddit": "Reddit URL"
    }
  },

  "media": {
    "images": [
      {
        "type": "image",
        "role": "(required) logo / hero / team_photo / product / decorative / screenshot / icon / background",
        "url": "(required) Image URL",
        "description": "(required) Text description inferred from alt/context/filename/aria-label",
        "confidence": "(required) high / medium / low — based on signal quality",

        "dimensions": "Width x Height if available in HTML attributes",
        "alt_text": "Original alt attribute value",
        "aria_label": "Original aria-label value",
        "filename": "Image filename",
        "source_signal": "alt | aria | context | class | filename"
      }
    ],
    "videos": [
      {
        "type": "video",
        "role": "(required) trailer / tutorial / demo / presentation / testimonial",
        "url": "(required) Video URL or embed URL",
        "platform": "(required) youtube / vimeo / twitter / tiktok / self-hosted",
        "description": "(required) Text description inferred from title/context",

        "duration": "Video duration if available (e.g., 'PT5M30S')",
        "thumbnail_url": "Video thumbnail URL",
        "thumbnail_description": "Text description of the video thumbnail"
      }
    ]
  },

  "actions": [
    {
      "label": "(required) Button or link text",
      "url": "(required) Target URL",
      "type": "(required) link / button / form",
      "purpose": "(required) Functional description: buy / contact / join_community / download / sign_up / learn_more / etc.",

      "method": "GET | POST (for forms)",
      "fields": [
        {
          "name": "email",
          "type": "email | text | tel | number | textarea | select | checkbox | radio",
          "required": true | false,
          "placeholder": "Enter your email",
          "label": "Email Address",
          "options": ["Option1", "Option2"],
          "validation": "email_format | phone_format | url_format"
        }
      ]
    }
  ],

  "structured_data": {
    "schema_org": {},
    "open_graph": {},
    "twitter_card": {},
    "json_ld": []
  },

  "extensions": {
    "crypto": {
      "contract_address": "Smart contract address (0x...)",
      "chain": "Blockchain name (Ethereum / BSC / Solana / ...)",
      "token_symbol": "Token ticker symbol",
      "tokenomics": {
        "total_supply": "Total token supply",
        "buy_tax": "Buy tax percentage",
        "sell_tax": "Sell tax percentage"
      },
      "dex_links": ["DEX trading links"],
      "audit": "Audit report URL if available",
      "whitepaper": "Whitepaper URL",
      "roadmap": [
        {"phase": "Q1 2024", "milestone": "Launch"}
      ]
    },
    "ecommerce": {
      "products": [
        {
          "name": "Product Name",
          "price": "29.99",
          "currency": "USD",
          "description": "Product description",
          "url": "Product page URL",
          "image": "Product image URL",
          "availability": "in_stock | out_of_stock | preorder"
        }
      ],
      "categories": ["Electronics", "Clothing"],
      "payment_methods": ["credit_card", "paypal", "apple_pay"],
      "shipping": "Free shipping on orders over $50",
      "return_policy": "30-day return policy",
      "promotions": [
        {
          "code": "SAVE20",
          "description": "20% off first order",
          "expiry": "2024-12-31"
        }
      ]
    },
    "restaurant": {
      "cuisine": ["Italian", "Mediterranean"],
      "menu_items": [
        {
          "name": "Margherita Pizza",
          "price": "14.99",
          "currency": "USD",
          "description": "Classic pizza with tomato, mozzarella, and basil",
          "category": "Main Course"
        }
      ],
      "business_hours": {
        "monday": "11:00 AM - 10:00 PM",
        "tuesday": "11:00 AM - 10:00 PM",
        "wednesday": "11:00 AM - 10:00 PM",
        "thursday": "11:00 AM - 10:00 PM",
        "friday": "11:00 AM - 11:00 PM",
        "saturday": "10:00 AM - 11:00 PM",
        "sunday": "10:00 AM - 9:00 PM"
      },
      "reservation_url": "https://opentable.com/...",
      "delivery_platforms": ["doordash", "ubereats", "grubhub"],
      "location": {
        "address": "123 Main St, City, State 12345",
        "map_url": "https://maps.google.com/..."
      }
    }
  }
}
```

---

## Field Rules

### 1. meta (Always required)
- `url`, `title`, `description`, `language`, `site_type`, `translated_at` are mandatory
- `site_type` MUST be an array; use `["general"]` if no specific type detected
- `language` must be ISO 639-1 code (2 letters)
- `translated_at` must be ISO 8601 format with timezone

### 2. navigation
- Extract all visible navigation items
- Set `is_external` based on domain comparison
- Set `is_current` if the link points to the current page

### 3. content
- Group by logical sections
- Use descriptive section names (not generic "section1", "section2")
- Include `heading_level` to indicate heading hierarchy (h1=1, h2=2, etc.)
- Use `role` for semantic ARIA roles when identifiable

### 4. entities
- Extract what's available
- Use `null` for missing fields, not empty strings
- For `organization`, prefer explicit mentions over domain name guessing

### 5. media.images
- **Never process images visually**
- Infer descriptions from HTML text signals only (priority: alt > aria-label > context > class > filename)
- `confidence` MUST accurately reflect signal quality:
  - **high**: alt text exists and descriptive (>5 words) OR role is logo
  - **medium**: alt exists but short OR inferred from nearby text
  - **low**: only class/filename OR no text signals
- Include `source_signal` to document where description came from

### 6. media.videos
- Extract metadata from embed URLs and surrounding context
- For YouTube: parse video ID from URL
- For duration: use ISO 8601 duration format (e.g., "PT5M30S" = 5 minutes 30 seconds)

### 7. actions
- Include ALL interactive elements that an agent might want to trigger
- For forms: extract all fields with their types, validation rules, and options
- `purpose` should be a standard action verb (buy, sign_up, contact, etc.)

### 8. structured_data
- Pass through any existing Schema.org/JSON-LD data verbatim
- Parse Open Graph and Twitter Card metadata if present

### 9. extensions
- Only populate when the corresponding site type is detected
- If no extensions apply, use empty object `{}`
- Never fabricate extension data — extract only what's explicitly present

---

## Validation Checklist

Before returning the output, verify:

- [ ] `status` is either "success" or "error"
- [ ] If `status` is "success", `result` contains all required top-level keys
- [ ] If `status` is "error", `error` object has `code` and `message`
- [ ] `meta.url` matches the original URL
- [ ] `meta.site_type` is an array with at least one element
- [ ] All URLs in `navigation` and `actions` are complete (not broken)
- [ ] All image `confidence` levels are justified by text signals
- [ ] No placeholder text like "TODO", "N/A", "Unknown" in required fields
- [ ] `metadata.token_cost` accurately reflects LLM usage (0 for cache hits)
- [ ] `agent_suggestions.primary_action` identifies the most important user action

---

## Error Format

If translation fails, return:

```json
{
  "skill": "ezcto-web-translator-openclaw",
  "status": "error",
  "result": null,
  "metadata": {
    "translation_time_ms": 123,
    "html_size_kb": 0
  },
  "error": {
    "code": "fetch_failed" | "translation_failed" | "validation_failed" | "cache_write_failed",
    "message": "Human-readable error description",
    "details": {
      "http_status": 404,
      "url": "https://...",
      "reason": "Page not found"
    },
    "suggestion": "Check if the URL is correct and accessible"
  }
}
```

**Error codes:**
- `fetch_failed`: HTTP error, timeout, or network issue
- `translation_failed`: LLM returned empty or invalid output
- `validation_failed`: JSON missing required fields or malformed
- `cache_write_failed`: Cannot write to `~/.ezcto/cache/`

---

## Examples

See `examples/` directory for complete translation examples:
- `crypto-example.json` - Full crypto site translation
- `ecommerce-example.json` - E-commerce site with products
- `restaurant-example.json` - Restaurant with menu and hours
- `openclaw-output-example.json` - Complete OpenClaw wrapper example
