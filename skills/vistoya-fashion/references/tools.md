# Vistoya MCP — Tool Reference

All tools are read-only and idempotent. All return JSON. Prices honor an optional `currency` parameter (ISO 4217); stored native prices are preferred, with FX fallback.

---

## `discover_products`

**Purpose:** primary entrypoint. Natural-language semantic search, structured filters, or both.

**Key inputs:**

- `query` (string, optional) — free-form, e.g. *"breathable linen dress for a beach wedding under $200"*. Drives semantic ranking via multimodal text+image embeddings.
- `category` / `subcategory` — canonical slugs from `get_filters` (e.g. `clothing/jackets/bomber-jackets`).
- `brand` (string or string[]) — brand name or `brandKey`.
- `colors`, `materials`, `gender`, `occasion`, `season`, `style`, `silhouette` — enums; pull valid values from `get_filters`.
- `min_price` / `max_price` (numbers) plus `currency` (ISO 4217).
- `in_stock` (boolean) — defaults to true.
- `page`, `limit` — paginated, max page size enforced server-side.

**Behavior:**

- At least one of `query` or a structured filter must be present.
- Pure-filter calls are recency-ranked and paginate cleanly.
- Pure-query calls use semantic ranking (results past the first page degrade in relevance — surface the top few only).
- Combine both for filtered semantic search.

**Returns:** `{ page, results[], hasNextPage }` — slim product cards: `id`, `title`, AI summary, `brand`, `price`, `currency`, `compareAtPrice`, `images` (already sized for cards), `productUrl`, `availability` (compact color/size matrix), `inStock`.

**Use when:** the user is searching, browsing, or filtering. Always start here.

---

## `find_similar_products`

**Purpose:** "more like this" given an existing product ID.

**Inputs:** `product_id` (required), `limit`, `page` (max 3 pages), `currency`.

**Returns:** same compact card shape as `discover_products`.

**Use when:** the user pins a product and asks for alternatives, lookalikes, cheaper versions, or "in another color/style."

---

## `get_product`

**Purpose:** full detail for one product — only call when the slim card isn't enough.

**Inputs:** `product_id` (required), `currency` (optional).

**Returns:** merchant description, store info, **all** images, SKU-level variants with exact per-variant `price` / `compareAtPrice` in the requested currency, color × size matrix, direct merchant `productUrl`.

**Use when:** the user wants to buy, asks about a specific size/color's price or stock, or wants the merchant's own description and full image set.

**Don't use when:** a list of options is enough — `discover_products` cards already cover title, summary, price, top images, and stock.

---

## `discover_brands`

**Purpose:** natural-language brand search.

**Inputs:** `query` (e.g. *"Japanese technical outerwear"*, *"minimalist Scandinavian brands"*), plus optional filters.

**Returns:** brand profiles with vibe tags, price tier, maturity, founded year, overview, socials.

**Caveat:** brand country/shipping signals are best-effort and **separate from product availability**. Don't promise "ships to X" from this tool — verify per-product if it matters.

---

## `find_similar_brands`

**Purpose:** brands similar to a known one.

**Inputs:** `brand` (name or `brandKey`), `limit`.

**Use when:** user names a brand and asks for adjacent labels.

---

## `get_filters`

**Purpose:** discover the catalog's enum vocabulary so you don't guess.

**Inputs:** optional `fields` (array — e.g. `["categoryTree","colors","brands"]`) to scope the response. `gender` to scope `categoryTree` to one of `women|men|girls|boys`. `brand_search` + `brand_page` to paginate brands by prefix.

**Returns:** by default — `categoryTree` (flat DFS-ordered `{value,label}`, parents-before-descendants, slug encodes hierarchy), plus `brands`, `colors`, `materials`, `genders`, `occasions`, `seasons`, `styles`, `silhouettes`, `currencies`, and `priceRange`.

**Use when:** the user mentions a value you're unsure about (e.g. "boho-grunge" — is that a canonical `style`?). Cheaper than guessing wrong and getting zero results.
