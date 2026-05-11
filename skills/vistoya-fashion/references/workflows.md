# Vistoya — Workflow Patterns

Reach for these in order. Don't chain three tools when one will do.

## 1. Open-ended discovery

> *"I need a linen suit for a summer wedding under $500."*

1. `discover_products({ query: "linen suit summer wedding", max_price: 500, currency: "USD" })`.
2. Surface the top 3–5 cards with title, brand, price, and a one-line take.
3. Ask if they want to see one in detail or filter further (color, brand, size).

## 2. Pure browse / filter

> *"Show me all bomber jackets from Acne Studios in black."*

1. (If unsure of the slug) `get_filters({ fields: ["categoryTree","brands","colors"] })`.
2. `discover_products({ category: "clothing/jackets/bomber-jackets", brand: "Acne Studios", colors: ["black"] })`.
3. No `query` here — pure filter, recency-ranked, paginates cleanly.

## 3. "More like this"

> *"Got anything similar but cheaper?"*

1. Take the `id` from the user's chosen card.
2. `find_similar_products({ product_id: id, limit: 5 })`.
3. Optionally re-filter the displayed list client-side by price; don't call `discover_products` with a half-remembered query.

## 4. Buy intent / variant question

> *"Is the navy one in M still in stock?"* / *"Send me the link."*

1. `get_product({ product_id: id, currency: <user's currency> })`.
2. Read the SKU matrix — confirm size/color availability and exact variant price.
3. Hand over `productUrl` so they can check out on the merchant site.

## 5. Brand exploration

> *"Recommend Italian streetwear labels."*

1. `discover_brands({ query: "Italian streetwear" })`.
2. To pivot from a brand to its products: pass the brand name into `discover_products({ brand: "...", query: "...", ... })`.
3. To find adjacent brands: `find_similar_brands({ brand: "..." })`.

## 6. Multi-currency

> *"Under 200 zł."*

1. Either `discover_products({ query: "...", max_price: 200, currency: "PLN" })`,
2. Or pass `currency: "PLN"` on `get_product` / `find_similar_products` to render returned prices in PLN.
3. Always render the **resolved** `{ price, currency, approximate }` from the response. If `approximate: true`, prefix with "~".

## Pagination

- `discover_products`: paginates cleanly for filter-heavy queries; for semantic queries, the first page is the highest-quality slice — don't paginate deep just to fill space.
- `find_similar_products`: capped at 3 pages by design. Stop there.

## Anti-patterns

- ❌ Calling `get_product` for every result in a list "just in case" — it's expensive and the cards already cover what the user can see at a glance.
- ❌ Inventing `category` / `style` slugs — call `get_filters` first.
- ❌ Re-querying `discover_products` with a slightly reworded query when the user already pinned a result — use `find_similar_products`.
- ❌ Quoting prices in the user's requested currency when the response says `approximate: true` without flagging it.
- ❌ Hard-coding `currency: "USD"` when the user spoke in another currency.
