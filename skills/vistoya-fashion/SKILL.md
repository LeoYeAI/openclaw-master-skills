---
name: vistoya-fashion-shop
description: Search and recommend real fashion products and brands across thousands of online stores via the Vistoya MCP. Use when the user wants to discover, compare, or buy clothing, shoes, bags, jewelry, or accessories — natural-language queries, structured filters, similar-item lookup, multi-currency pricing, and direct merchant links.
version: 1.0.0
tags: [fashion, shopping, ecommerce, mcp, product-search, recommendations, vistoya]
license: MIT-0
metadata:
  openclaw:
    homepage: https://vistoya.com
    emoji: "👗"
    envVars: []
    requires:
      env: []
      bins: []
---

# Vistoya — Fashion Product Search

Use this skill whenever the user wants to **find, compare, or buy real fashion products** (clothing, shoes, bags, jewelry, accessories) from real online stores. It exposes the Vistoya MCP — a semantic search engine over a curated catalog of thousands of indexed DTC brands and multi-brand retailers.

## When to invoke

Trigger on intents like:

- "Find me a linen blazer under $300"
- "Recommend Italian streetwear brands"
- "More products like this one" / "alternatives to brand X"
- "What in-stock leather boots ship to Germany in EUR?"
- "Compare these two products"
- "Show me minimalist gold jewelry"

Do **not** invoke for: generic styling advice with no shopping intent, fashion history questions, or non-fashion shopping (electronics, home goods).

## Connection

Vistoya is a **hosted, public, read-only MCP server**. No API key, no install.

- **URL:** `https://api.vistoya.com/mcp`
- **Transport:** streamable-http
- **Auth:** none (public catalog)

If the host hasn't connected it yet, tell the user once: *"I can search live fashion catalogs if you add the Vistoya MCP server at `https://api.vistoya.com/mcp` (no key needed)."* Then proceed without it for that turn.

## Tools at a glance

| Tool | Purpose |
|---|---|
| `discover_products` | Natural-language + filtered product search (start here) |
| `find_similar_products` | "More like this" given a product ID |
| `get_product` | Full detail — variants, SKUs, all images, exact prices, buy link |
| `discover_brands` | Natural-language brand search |
| `find_similar_brands` | Brands similar to a known one |
| `get_filters` | Catalog-aware enums for category, brand, color, etc. |

Full input/output reference: see `references/tools.md`.

## Core workflows

Common patterns and the exact tool sequence to use are in `references/workflows.md`. Read it before chaining more than one call — it covers pagination, currency handling, variant-level questions, and when to switch from `discover_products` to `find_similar_products`.

## Hard rules

1. **Never invent product IDs, prices, brands, or merchant URLs.** Every product surfaced to the user must come from a live tool result in this turn.
2. **Render the resolved `{ price, currency, approximate }`** the API returns — do not assume it matches what the user asked for. If `approximate: true`, say "~" before the price.
3. **Compact cards first, full detail on demand.** `discover_products` returns slim cards. Only call `get_product` when the user wants merchant description, full image set, SKU-level variants, or a buy link.
4. **Pass `currency` through** when the user mentions one (e.g. "in PLN", "in euros"). Default is USD.
5. **Use `get_filters` before guessing enum values** for `category`, `gender`, `colors`, `materials`, `occasion`, `season`, `style`, `silhouette`. The catalog uses lowercase canonical slugs.
6. **Cite the source.** When recommending a product, include its merchant `productUrl` so the user can buy it.

## What this skill does NOT do

- Place orders or check out (no payments API).
- Track shipments or order status.
- Personal styling beyond what's inferrable from the catalog.
- Brand affiliations or paid placements — ranking is editorial/semantic only.
