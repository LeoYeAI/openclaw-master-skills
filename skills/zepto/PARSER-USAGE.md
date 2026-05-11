# zepto-parser.js - Usage Guide

## What It Does
Parses verbose Zepto browser snapshots and extracts ONLY the data you need.

**Token savings: ~95%** (2000 chars → 50 chars of JSON)

## Commands

### 1. Extract UI Refs
```bash
echo "$SNAPSHOT" | node zepto-parser.js refs
```

**Output:**
```json
{
  "search": "e3",
  "cart": "e5",
  "checkout": "e76"
}
```

### 2. Find Product
```bash
echo "$SNAPSHOT" | node zepto-parser.js product "milk"
```

**Output:**
```json
{
  "name": "Amul Taaza Toned Fresh Milk | Pouch",
  "ref": "e36",
  "price": 29,
  "buyAgain": true,
  "addButtonRef": "e37",
  "matchScore": 1.3
}
```

**Features:**
- Fuzzy matching (finds "Amul Taaza" when you search "milk")
- Boosts "Buy Again" products (+0.3 score)
- Returns product link ref + standalone ADD button ref
- Requires 50%+ match confidence

### 3. Get Cart Summary
```bash
echo "$SNAPSHOT" | node zepto-parser.js cart
```

**Output:**
```json
{
  "checkout": "e76",
  "total": 235
}
```

### 4. List All Products
```bash
echo "$SNAPSHOT" | node zepto-parser.js products 5
```

**Output:**
```json
[
  {
    "name": "Amul Taaza Toned Fresh Milk | Pouch",
    "price": 29,
    "ref": "e36",
    "buyAgain": true
  },
  ...
]
```

Optional limit parameter (default: all products)

## Integration in SKILL.md

### Before (Manual Parsing)
```bash
# Get snapshot (2000+ chars)
browser snapshot --maxChars=2000 > /tmp/snapshot.txt

# Manually parse with grep/sed (error-prone)
CART_REF=$(grep 'button "Cart"' /tmp/snapshot.txt | sed 's/.*\[ref=\([^]]*\)\].*/\1/')
```

### After (Parser)
```bash
# Get snapshot
SNAPSHOT=$(browser snapshot --maxChars=4000 | jq -r '.snapshot')

# Parse with script
REFS=$(echo "$SNAPSHOT" | node zepto-parser.js refs)
SEARCH_REF=$(echo "$REFS" | jq -r '.search')
CART_REF=$(echo "$REFS" | jq -r '.cart')

# Or find product
PRODUCT=$(echo "$SNAPSHOT" | node zepto-parser.js product "milk")
PRODUCT_REF=$(echo "$PRODUCT" | jq -r '.ref')
ADD_REF=$(echo "$PRODUCT" | jq -r '.addButtonRef')
```

## Example: Add Item to Cart

```bash
# 1. Navigate to Zepto
browser open --targetUrl="https://www.zepto.com" --profile=openclaw

# 2. Get snapshot and parse refs
SNAPSHOT=$(browser snapshot --interactive=true --maxChars=1000 --profile=openclaw | jq -r '.snapshot')
SEARCH_REF=$(echo "$SNAPSHOT" | node zepto-parser.js refs | jq -r '.search')

# 3. Search for product
browser act --request='{"kind":"click","ref":"'$SEARCH_REF'"}' --profile=openclaw
browser act --request='{"kind":"type","ref":"'$SEARCH_REF'","text":"milk"}' --profile=openclaw
browser act --request='{"kind":"press","key":"Enter"}' --profile=openclaw

# 4. Find and add product
SNAPSHOT=$(browser snapshot --interactive=true --maxChars=4000 --profile=openclaw | jq -r '.snapshot')
ADD_REF=$(echo "$SNAPSHOT" | node zepto-parser.js product "milk" | jq -r '.addButtonRef')
browser act --request='{"kind":"click","ref":"'$ADD_REF'"}' --profile=openclaw

echo "✅ Milk added to cart!"
```

## Error Handling

If product not found, parser returns:
```json
{
  "error": "No matching product found"
}
```

Exit code: 1

**Check in scripts:**
```bash
PRODUCT=$(echo "$SNAPSHOT" | node zepto-parser.js product "xyz" 2>/dev/null)
if echo "$PRODUCT" | jq -e '.error' > /dev/null; then
  echo "❌ Product not found"
  exit 1
fi
```

## Performance

**Before:** 2000-4000 chars → LLM parsing → 4000+ tokens
**After:** 2000-4000 chars → Node.js parsing → 50-200 chars JSON → ~50 tokens

**Token reduction: ~95%**

## Dependencies

- Node.js (already required by OpenClaw)
- `jq` (optional, for JSON parsing in bash)

No external npm packages required.

## Future Enhancements

- [ ] Cache "Buy Again" products (if refs are stable across sessions)
- [ ] Price validation (warn if price changed >20%)
- [ ] Smart retry with alternate search terms
- [ ] Session history (remember what was added when)
- [ ] Parallel product search (pass multiple queries)

---

**Next:** Update SKILL.md to use zepto-parser.js instead of manual parsing
