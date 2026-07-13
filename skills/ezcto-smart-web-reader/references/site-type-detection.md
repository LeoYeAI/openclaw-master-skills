# Site Type Auto-Detection Rules (Enhanced)

Before LLM translation, scan the HTML content using **pure text matching** to detect website type. This step costs **zero tokens**.

---

## Detection Logic

For each type, count matching signals. If **3 or more signals match**, classify as that type.

**A page can match multiple types** (e.g., an NFT marketplace can be both `crypto` and `ecommerce`).

---

## Crypto / Web3 Project

Match **3 or more** of the following signals:

### Signal 1: Contract Address Format
- Contains a `0x`-prefixed 40-character hexadecimal string **AND**
- Within 50 characters of keywords: `contract` / `CA` / `token address` / `address:`
- OR appears in a `<code>` tag or monospace font element
- OR appears next to a "Copy" button or clipboard icon

**Example patterns:**
```regex
0x[a-fA-F0-9]{40}
```

**Context validation:**
```javascript
const contractMatches = html.match(/0x[a-fA-F0-9]{40}/g)
if (contractMatches) {
  for (const addr of contractMatches) {
    const context = getContext(html, addr, 50) // 50 chars before/after
    if (/contract|CA|token address|address:/i.test(context)) {
      return true
    }
  }
}
```

### Signal 2: Tokenomics Keywords
- Contains keywords: `tokenomics` / `token distribution` / `total supply` / `buy tax` / `sell tax`
- OR contains phrases: `max supply` / `circulating supply` / `token allocation`

### Signal 3: DEX Links
- Links point to decentralized exchanges:
  - `dexscreener.com` / `dextools.io` / `pancakeswap.finance`
  - `uniswap.org` / `raydium.io` / `jupiter.ag`
  - `sushiswap.com` / `balancer.fi` / `curve.fi`

### Signal 4: Blockchain Keywords
- Contains keywords: `smart contract` / `blockchain` / `DeFi` / `NFT` / `staking` / `web3`
- OR: `liquidity pool` / `yield farming` / `governance token` / `DAO`

### Signal 5: Community Links
- HTML contains Telegram (`t.me/`) or Discord (`discord.gg/` or `discord.com/invite/`) community links
- These are strong signals as almost all crypto projects have community channels

### Signal 6: Chain-Specific Indicators
- Mentions specific blockchains:
  - `Ethereum` / `ETH` / `etherscan.io`
  - `BSC` / `BNB` / `Binance Smart Chain` / `bscscan.com`
  - `Solana` / `SOL` / `solscan.io` / `solana.fm`
  - `Base` / `basescan.org`
  - `Arbitrum` / `ARB` / `arbiscan.io`
  - `Polygon` / `MATIC` / `polygonscan.com`

### Signal 7: Audit/Security
- Links to audit providers: `certik.com` / `hacken.io` / `peckshield.com`
- Keywords: `audit report` / `security audit` / `verified contract`

**If matched:** Set `site_type` to `["crypto"]`, load `extensions/crypto-fields.md`

---

## E-commerce

Match **3 or more** of the following signals:

### Signal 1: Shopping Cart Keywords
- Contains keywords: `add to cart` / `buy now` / `checkout` / `shopping cart` / `view cart`

### Signal 2: Price Formats
- Contains currency price patterns:
  - `$\d+\.\d{2}` (USD: $99.99)
  - `¥\d+` (JPY/CNY: ¥999)
  - `€\d+` (EUR: €99)
  - `£\d+` (GBP: £99)
  - `₹\d+` (INR: ₹999)

### Signal 3: Schema.org Product Markup
- Schema.org `@type` is `Product` or `Offer`
- Check for JSON-LD with `"@type": "Product"`

### Signal 4: E-commerce Platform Links
- Links point to: `shopify.com` / `stripe.com` / `paypal.com` / `square.com`
- OR cart/checkout URLs contain: `/cart` / `/checkout` / `/basket`

### Signal 5: E-commerce Keywords
- Contains keywords: `shipping` / `returns` / `warranty` / `inventory` / `in stock` / `out of stock`
- OR: `free shipping` / `product details` / `size chart`

### Signal 6: Product Listing Indicators
- Multiple elements with class names containing: `product-card` / `product-item` / `product-grid`
- OR repeated price patterns (3+ occurrences of currency + number)

**Exclusion rule:** If also matches Restaurant signals with higher score, deprioritize ecommerce classification.

**If matched:** Set `site_type` to `["ecommerce"]`, load `extensions/ecommerce-fields.md`

---

## Restaurant / Food Service

Match **3 or more** of the following signals:

### Signal 1: Menu/Ordering Keywords
- Contains keywords: `\bmenu\b` (word boundary) / `reservation` / `order online` / `delivery` / `takeout`
- Note: Use word boundary for "menu" to avoid matching "menubar" in nav code

### Signal 2: Schema.org Restaurant Markup
- Schema.org `@type` is `Restaurant` or `FoodEstablishment`
- Check for JSON-LD with `"@type": "Restaurant"`

### Signal 3: Delivery Platform Links
- Links point to: `doordash.com` / `ubereats.com` / `opentable.com` / `grubhub.com`
- OR: `seamless.com` / `postmates.com` / `caviar.com`

### Signal 4: Business Hours Format
- Contains day-of-week patterns: `Mon-Fri` / `Monday-Friday` / `Monday - Friday`
- AND time patterns: `\d{1,2}:\d{2}\s*[AP]M` / `\d{1,2}[ap]m`
- OR phrases: `opening hours` / `hours of operation`

### Signal 5: Food Service Keywords
- Contains keywords: `cuisine` / `dine-in` / `takeout` / `catering` / `reservations`
- OR: `chef` / `culinary` / `dining` / `brunch` / `lunch` / `dinner`

### Signal 6: Menu Item Indicators
- Multiple food-related words in list format:
  - `appetizers` / `entrees` / `desserts` / `beverages`
  - `starters` / `main course` / `sides`

**Exclusion rule:** If matches E-commerce with "shopping cart" + product listings, classify as ecommerce instead.

**If matched:** Set `site_type` to `["restaurant"]`, load `extensions/restaurant-fields.md`

---

## General (Default)

If no type matches 3+ signals, classify as `["general"]`. Use only the base translation prompt without any extension fields.

---

## Multi-Type Detection

**A page can have multiple types.** Examples:

### Example 1: NFT Marketplace
- Matches Crypto: contract addresses, blockchain, Discord → **4 signals**
- Matches E-commerce: "buy now", prices, shopping cart → **3 signals**
- **Result:** `site_type = ["crypto", "ecommerce"]`
- **Load extensions:** Both `crypto-fields.md` and `ecommerce-fields.md`

### Example 2: Restaurant with Crypto Payment
- Matches Restaurant: menu, reservation, business hours, cuisine → **4 signals**
- Matches Crypto: accepts BTC, ETH payment → **1 signal only**
- **Result:** `site_type = ["restaurant"]` (crypto didn't meet threshold)

### Example 3: Crypto Project Landing Page
- Matches Crypto: tokenomics, contract, Telegram, DexTools, staking → **5 signals**
- Matches E-commerce: "buy now" button (for token purchase) → **1 signal only**
- **Result:** `site_type = ["crypto"]`

---

## Implementation Reference

```javascript
function detectSiteTypes(html) {
  const types = []
  const extensions = []

  // Crypto detection
  let cryptoScore = 0
  if (/0x[a-fA-F0-9]{40}/.test(html) && /contract|CA|token address/i.test(html)) cryptoScore++
  if (/tokenomics|token distribution|total supply|buy tax|sell tax/i.test(html)) cryptoScore++
  if (/dexscreener|dextools|pancakeswap|uniswap|raydium/i.test(html)) cryptoScore++
  if (/smart contract|blockchain|DeFi|NFT|staking|web3/i.test(html)) cryptoScore++
  if (/t\.me\/|discord\.gg\/|discord\.com\/invite\//i.test(html)) cryptoScore++
  if (/ethereum|etherscan|BSC|bscscan|solana|solscan/i.test(html)) cryptoScore++
  if (/certik|hacken|peckshield|audit report/i.test(html)) cryptoScore++

  if (cryptoScore >= 3) {
    types.push("crypto")
    extensions.push("references/extensions/crypto-fields.md")
  }

  // E-commerce detection
  let ecommerceScore = 0
  if (/add to cart|buy now|checkout|shopping cart/i.test(html)) ecommerceScore++
  if (/\$\d+\.\d{2}|¥\d+|€\d+|£\d+/.test(html)) ecommerceScore++
  if (/"@type"\s*:\s*"(Product|Offer)"/.test(html)) ecommerceScore++
  if (/shopify|stripe|paypal|square/i.test(html)) ecommerceScore++
  if (/shipping|returns|warranty|inventory/i.test(html)) ecommerceScore++
  if ((html.match(/product-card|product-item/gi) || []).length >= 3) ecommerceScore++

  if (ecommerceScore >= 3) {
    types.push("ecommerce")
    extensions.push("references/extensions/ecommerce-fields.md")
  }

  // Restaurant detection
  let restaurantScore = 0
  if (/\bmenu\b|reservation|order online|delivery/i.test(html)) restaurantScore++
  if (/"@type"\s*:\s*"(Restaurant|FoodEstablishment)"/.test(html)) restaurantScore++
  if (/doordash|ubereats|opentable|grubhub/i.test(html)) restaurantScore++
  if (/Mon-Fri|Monday-Friday/i.test(html) && /\d{1,2}:\d{2}\s*[AP]M/i.test(html)) restaurantScore++
  if (/cuisine|dine-in|takeout|catering/i.test(html)) restaurantScore++
  if (/appetizers|entrees|desserts|main course/i.test(html)) restaurantScore++

  if (restaurantScore >= 3) {
    types.push("restaurant")
    extensions.push("references/extensions/restaurant-fields.md")
  }

  // Default to general if nothing matched
  if (types.length === 0) {
    types.push("general")
  }

  return { types, extensions }
}
```

---

## Testing Your Detection

```bash
# Test with known crypto site
echo "Testing pump.fun (should be crypto)"
curl -s https://pump.fun | node detect.js
# Expected: ["crypto"]

# Test with e-commerce
echo "Testing shopify site (should be ecommerce)"
curl -s https://www.shopify.com | node detect.js
# Expected: ["ecommerce"]

# Test with restaurant
echo "Testing restaurant site (should be restaurant)"
curl -s https://www.opentable.com/restaurant-profile | node detect.js
# Expected: ["restaurant"]

# Test with multi-type (NFT marketplace)
echo "Testing NFT marketplace (should be crypto + ecommerce)"
curl -s https://opensea.io | node detect.js
# Expected: ["crypto", "ecommerce"]
```

---

## Performance Notes

- **Token cost:** 0 (pure regex/string matching, no LLM calls)
- **Execution time:** <10ms for typical HTML
- **Accuracy:** ~90% on common sites (based on EZCTO internal testing)

---

## Future Extensions

Potential new types to add:

- **SaaS:** API docs, pricing tiers, "free trial"
- **Blog:** Article structure, author bylines, comments
- **Portfolio:** Project showcase, case studies
- **News:** Article feeds, timestamps, bylines
- **Job Board:** Job listings, "apply now"

To add a new type, follow the same pattern: define 5-7 signals, require 3+ matches, create an extension file.
