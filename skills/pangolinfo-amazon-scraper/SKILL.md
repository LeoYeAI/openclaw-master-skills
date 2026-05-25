---
name: pangolinfo-amazon-scraper
description: >
  Scrape Amazon product data using Pangolin APIs. Use this skill when the user
  wants to: look up Amazon products by ASIN, search Amazon by keyword, check
  bestsellers/new releases, get product reviews or pricing, compare products
  across Amazon regions, browse categories, or research sellers.
  Requires PANGOLIN_EMAIL + PANGOLIN_PASSWORD env vars (or PANGOLIN_API_KEY).
---

# Pangolinfo Amazon Scraper

Scrape Amazon product data via Pangolin's structured APIs. Returns parsed JSON with product details, search results, rankings, reviews, and more across 13 Amazon regions.

## When to Use This Skill

Activate this skill when the user's intent matches any of these patterns:

| Intent (English) | Intent (Chinese) | Action |
|---|---|---|
| Look up an Amazon product / ASIN | 查一下亚马逊上的这个商品 / ASIN | Product detail lookup |
| Search Amazon for a keyword | 在亚马逊搜索关键词 | Keyword search |
| Show bestsellers in a category | 看看某个类目的畅销榜 | Bestsellers |
| Show new releases | 看看最新上架的商品 | New releases |
| Browse a category on Amazon | 浏览亚马逊某个分类 | Category products |
| Find products from a seller | 查看某个卖家的商品 | Seller products |
| Get reviews for a product | 看看这个产品的评论 | Product reviews |
| Compare prices across regions | 对比不同国家亚马逊的价格 | Multi-region lookup |
| Check seller/variant options | 查看其他卖家选项 | Follow seller |

**Keywords that trigger this skill:** Amazon, ASIN, B0-prefixed codes, product reviews, bestseller, new release, Amazon category, Amazon seller, amz_us/amz_uk/etc., product detail, Amazon search, price comparison across Amazon sites.

## Prerequisites

### Required

- **Python 3.8+** (uses only the standard library -- zero external dependencies)
- **Pangolin account** at [pangolinfo.com](https://www.pangolinfo.com)
- **Environment variables** (one of the following):
  - `PANGOLIN_API_KEY` -- API key (skips login), OR
  - `PANGOLIN_EMAIL` + `PANGOLIN_PASSWORD` -- auto-login with caching

### macOS SSL Certificate Fix

On macOS, Python may fail with `CERTIFICATE_VERIFY_FAILED` because it ships without root certificates by default.

**Symptoms:** The script exits with error code `SSL_CERT`.

**Solutions (pick one):**

1. Run the certificate installer bundled with Python:
   ```bash
   /Applications/Python\ 3.x/Install\ Certificates.command
   ```
   (Replace `3.x` with your Python version, e.g., `3.11`)

2. Set `SSL_CERT_FILE` from the `certifi` package:
   ```bash
   pip3 install certifi
   export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
   ```

3. Add the export to your shell profile (`~/.zshrc` or `~/.bashrc`) so it persists.

## First-Time Setup Guide

When a user tries to use this skill and authentication fails (error code `MISSING_ENV`), **do not just repeat the error hint**. Instead, walk the user through the full setup process interactively:

### Step 1: Explain what's needed

Tell the user (in their language):

> To use this skill, you need a Pangolin API account. Pangolin provides Amazon product data scraping through its APIs.
>
> 使用本技能需要 Pangolin API 账号。Pangolin 提供亚马逊商品数据抓取的 API 服务。

### Step 2: Guide registration

> 1. Go to [pangolinfo.com](https://www.pangolinfo.com) and create an account
> 2. After login, find your API Key in the dashboard
>
> 1. 访问 [pangolinfo.com](https://www.pangolinfo.com) 注册账号
> 2. 登录后在控制台找到你的 API Key

### Step 3: Collect credentials and authenticate automatically

When the user provides their credentials, **you (the AI agent) should configure them securely**. The script will automatically cache the API key at `~/.pangolin_api_key` for all future calls.

**If user provides an API key (recommended):**
Write it directly to the cache file — avoids shell history entirely:
```bash
echo "<api_key>" > ~/.pangolin_api_key
chmod 600 ~/.pangolin_api_key 2>/dev/null
python3 scripts/pangolin.py --auth-only
```

**If user provides email + password:**
Set env vars in the session and clean up after auth:
```bash
export PANGOLIN_EMAIL="user@example.com"
export PANGOLIN_PASSWORD="their-password"
python3 scripts/pangolin.py --auth-only
unset PANGOLIN_EMAIL PANGOLIN_PASSWORD
```

This avoids passwords appearing in shell history (unlike inline `VAR=x command` syntax) and cleans up credentials after the API key is cached.

Both methods cache the API key automatically. After this one-time setup, **no environment variables are needed** — all future calls will use the cached API key at `~/.pangolin_api_key`.

### Step 4: Confirm and proceed

After auth returns `"success": true`:
1. Tell the user: "认证成功！API Key 已自动缓存，后续使用无需再次输入。" / "Authentication successful! API Key cached — no need to enter credentials again."
2. Immediately retry their original request.

### Important

- **The user only needs to provide credentials ONCE** — the script caches the API key permanently at `~/.pangolin_api_key`
- Do not ask the user to manually edit `.bashrc` or `.zshrc` — the script handles persistence automatically
- If the user doesn't have an account yet, explain Pangolin's credit system (1 credit per Amazon json request, 5 credits per review page) and direct them to [pangolinfo.com](https://www.pangolinfo.com)
- If auth succeeds but credits are exhausted (error code `2001`), tell the user to top up at pangolinfo.com
- The API key is permanent and does not expire unless the account is deactivated

## Script Execution

The script is located at `scripts/pangolin.py` relative to this skill's root directory.

**Path resolution:** When invoking the script, resolve the absolute path from the skill directory. For example, if this skill is installed at `/path/to/pangolinfo-amazon-scraper/`:

```bash
python3 /path/to/pangolinfo-amazon-scraper/scripts/pangolin.py --content B0DYTF8L2W --mode amazon --site amz_us
```

## Intent-to-Command Mapping

### 1. Product Detail by ASIN

User says: "Look up B0DYTF8L2W on Amazon" / "查一下 B0DYTF8L2W 这个产品"

```bash
python3 scripts/pangolin.py --content B0DYTF8L2W --mode amazon --site amz_us
# Or using the --asin shortcut:
python3 scripts/pangolin.py --asin B0DYTF8L2W --site amz_us
```

The script auto-detects 10-character alphanumeric codes as ASINs and selects `amzProductDetail`. The `--asin` flag is a convenience shortcut that sets `--content` and defaults to `amzProductDetail` parser automatically.

### 2. Keyword Search

User says: "Search Amazon for wireless mouse" / "在亚马逊搜索无线鼠标"

```bash
python3 scripts/pangolin.py --q "wireless mouse" --mode amazon --site amz_us
```

Non-ASIN text auto-selects `amzKeyword` parser.

### 3. Bestsellers

User says: "Show me electronics bestsellers" / "看看电子产品畅销榜"

```bash
python3 scripts/pangolin.py --content "electronics" --mode amazon --parser amzBestSellers --site amz_us
```

### 4. New Releases

User says: "What's new in toys on Amazon?" / "亚马逊玩具类有什么新品？"

```bash
python3 scripts/pangolin.py --content "toys" --mode amazon --parser amzNewReleases --site amz_us
```

### 5. Category Products

User says: "Browse category 172282 on Amazon" / "浏览亚马逊分类 172282"

```bash
python3 scripts/pangolin.py --content "172282" --mode amazon --parser amzProductOfCategory --site amz_us
```

### 6. Seller Products

User says: "Show products from seller A1B2C3D4E5" / "查看卖家 A1B2C3D4E5 的商品"

```bash
python3 scripts/pangolin.py --content "A1B2C3D4E5" --mode amazon --parser amzProductOfSeller --site amz_us
```

### 7. Follow Seller (Variant / Seller Options)

User says: "Show other seller options for B0G4QPYK4Z" / "查看 B0G4QPYK4Z 的其他卖家选项"

```bash
python3 scripts/pangolin.py --asin B0G4QPYK4Z --parser amzFollowSeller --site amz_us
```

Uses a dedicated API endpoint (`/api/v1/scrape/follow-seller`). Returns variant options including price, delivery, fulfillment, and seller info for the given ASIN.

### 8. Product Reviews

User says: "Get critical reviews for B00163U4LK" / "看看 B00163U4LK 的差评"

```bash
python3 scripts/pangolin.py --content B00163U4LK --mode review --site amz_us --filter-star critical
```

**Star filter mapping:**

| User says (EN) | User says (CN) | `--filter-star` value |
|---|---|---|
| all reviews | 所有评论 | `all_stars` |
| 5-star / excellent | 五星 / 好评 | `five_star` |
| 4-star | 四星 | `four_star` |
| 3-star | 三星 | `three_star` |
| 2-star | 两星 | `two_star` |
| 1-star / terrible | 一星 / 最差评 | `one_star` |
| positive / good | 好评 / 正面评价 | `positive` |
| critical / negative / bad | 差评 / 负面评价 | `critical` |

**Sort mapping:**

| User says (EN) | User says (CN) | `--sort-by` value |
|---|---|---|
| newest / most recent | 最新的 | `recent` |
| most helpful / top | 最有帮助的 | `helpful` |

**Multiple pages:** Add `--pages N` (each page costs 5 credits).

### 9. Product by URL (Legacy)

User says: "Scrape this Amazon page: https://www.amazon.com/dp/B0DYTF8L2W"

```bash
python3 scripts/pangolin.py --url "https://www.amazon.com/dp/B0DYTF8L2W" --mode amazon
```

The site code is auto-inferred from the URL domain.

### 10. Different Region

User says: "Check price on Amazon Japan" / "看看日本亚马逊的价格"

**Region mapping:**

| User says (EN) | User says (CN) | `--site` code |
|---|---|---|
| US / America | 美国 | `amz_us` |
| UK / Britain | 英国 | `amz_uk` |
| Canada | 加拿大 | `amz_ca` |
| Germany | 德国 | `amz_de` |
| France | 法国 | `amz_fr` |
| Japan | 日本 | `amz_jp` |
| Italy | 意大利 | `amz_it` |
| Spain | 西班牙 | `amz_es` |
| Australia | 澳大利亚 | `amz_au` |
| Mexico | 墨西哥 | `amz_mx` |
| Saudi Arabia | 沙特 | `amz_sa` |
| UAE | 阿联酋 | `amz_ae` |
| Brazil | 巴西 | `amz_br` |

## Smart Defaults

The script automatically:

1. **Detects ASINs** -- 10-character alphanumeric strings like `B0DYTF8L2W` auto-select `amzProductDetail`
2. **Detects keywords** -- non-ASIN text like `"wireless mouse"` auto-selects `amzKeyword`
3. **Defaults to `amz_us`** if no `--site` is provided
4. **Switches to review mode** if `--filter-star` is used or `--parser amzReviewV2` is set
5. **Infers site from URL** when using `--url` with an Amazon domain

You generally only need `--parser` for bestsellers, new releases, category, and seller lookups.

## Output Format

### Amazon Mode (product/keyword/ranking/category/seller)

```json
{
  "success": true,
  "task_id": "02b3e90810f0450ca6d41244d6009d0f",
  "url": "https://www.amazon.com/dp/B0DYTF8L2W",
  "metadata": {
    "executionTime": 1791,
    "parserType": "amzProductDetail",
    "parsedAt": "2026-01-13T06:42:01.861Z"
  },
  "results": [ ... ],
  "results_count": 1
}
```

### Review Mode

Same envelope structure. Each result object contains review fields: `date`, `country`, `star`, `author`, `title`, `content`, `purchased`, `vineVoice`, `helpful`, `reviewId`.

### Error Output

All errors use a unified envelope written to stderr:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "hint": "Actionable suggestion"
  }
}
```

See [references/output-schema.md](references/output-schema.md) for complete field documentation.

## Response Presentation

When presenting results to the user, follow these guidelines per parser type. **Always match the user's language** (respond in Chinese if the user wrote in Chinese, etc.).

### Product Detail (`amzProductDetail`)

Present as a structured product card:

- **Title** and brand
- **Price** (include strikethrough/coupon if present)
- **Rating**: star rating + number of reviews
- **Stock status** and delivery estimate
- **Key features** (bullet list, up to 5)
- **Bestseller rank** and category
- Include the product image if available
- Note Amazon's Choice badge if `acBadge` is present

### Keyword Search (`amzKeyword`)

Present as a **numbered list** of products:

1. **Title** -- price -- star rating (N reviews) -- delivery info
2. ...

Highlight sponsored results. Show the total results count. If the user asked about a specific need, recommend the best match.

### Bestsellers / New Releases (`amzBestSellers` / `amzNewReleases`)

Present as a **ranked list**:

1. #1: **Title** -- price -- star rating
2. #2: ...

Emphasize rank position. Note trends if multiple queries are compared.

### Category / Seller Products (`amzProductOfCategory` / `amzProductOfSeller`)

Present as a numbered product list similar to keyword search. Group by price range or rating if the user is comparing.

### Follow Seller (`amzFollowSeller`)

Present variant options clearly:

- Option 1: price, delivery, ships from, sold by
- Option 2: ...

Help the user compare variants (color, size, seller).

### Reviews (`amzReviewV2`)

Present as:

1. **Summary**: average sentiment, common themes, verified purchase ratio
2. **Individual reviews** (top 3-5): star + title + excerpt + date + verified badge
3. **Pattern analysis**: recurring praise/complaints

### Empty Results

If `results_count` is 0:
- Suggest checking the ASIN/keyword spelling
- Suggest trying a different Amazon region
- Suggest broadening the search terms

### Error Results

If `success` is false:
- Present the error message in friendly, non-technical language
- Provide the hint from the error object
- Offer to retry or suggest an alternative approach

## All CLI Options

| Flag | Description | Default |
|---|---|---|
| `--q` | Search query or keyword | -- |
| `--url` | Target Amazon URL (legacy mode) | -- |
| `--content` | Content ID: ASIN, keyword, category Node ID, seller ID | -- |
| `--asin ASIN` | Amazon ASIN (shortcut for `--content <ASIN> --parser amzProductDetail`) | -- |
| `--site` / `--region` | Amazon site/region code (e.g., `amz_us`) | `amz_us` |
| `--mode` | `amazon` or `review` | `amazon` |
| `--parser` | Parser name (auto-inferred when possible) | `amzProductDetail` |
| `--zipcode` | US zipcode for localized pricing | `10041` |
| `--format` | Response format: `json`, `rawHtml`, `markdown` | `json` |
| `--filter-star` | Star filter for reviews | `all_stars` |
| `--sort-by` | Sort order for reviews: `recent` or `helpful` | `recent` |
| `--pages` | Number of review pages (5 credits/page) | `1` |
| `--auth-only` | Test authentication only | -- |
| `--raw` | Output raw API response (no extraction) | -- |
| `--timeout` | API request timeout in seconds | `120` |

## Output Schema

See [references/output-schema.md](references/output-schema.md) for the complete JSON output schema, including per-parser field documentation and guaranteed vs optional fields.

## Amazon Parsers Reference

| Parser | Use Case | Content Value |
|---|---|---|
| `amzProductDetail` | Single product page | ASIN (e.g., `B0DYTF8L2W`) |
| `amzKeyword` | Keyword search results | Keyword (e.g., `wireless mouse`) |
| `amzProductOfCategory` | Category listing | Category Node ID (e.g., `172282`) |
| `amzProductOfSeller` | Seller's products | Seller ID (e.g., `A1B2C3D4E5`) |
| `amzBestSellers` | Best sellers ranking | Category keyword (e.g., `electronics`) |
| `amzNewReleases` | New releases ranking | Category keyword (e.g., `toys`) |
| `amzFollowSeller` | Variants / other sellers | ASIN (e.g., `B0DYTF8L2W`) |
| `amzReviewV2` | Product reviews | ASIN (via `--mode review`) |

## Amazon Sites Reference

| Site Code | Region | Domain |
|---|---|---|
| `amz_us` | United States | amazon.com |
| `amz_uk` | United Kingdom | amazon.co.uk |
| `amz_ca` | Canada | amazon.ca |
| `amz_de` | Germany | amazon.de |
| `amz_fr` | France | amazon.fr |
| `amz_jp` | Japan | amazon.co.jp |
| `amz_it` | Italy | amazon.it |
| `amz_es` | Spain | amazon.es |
| `amz_au` | Australia | amazon.com.au |
| `amz_mx` | Mexico | amazon.com.mx |
| `amz_sa` | Saudi Arabia | amazon.sa |
| `amz_ae` | UAE | amazon.ae |
| `amz_br` | Brazil | amazon.com.br |

## Cost

| Operation | Credits |
|---|---|
| Amazon scrape (`json` format) | 1 per request |
| Amazon scrape (`rawHtml` / `markdown`) | 0.75 per request |
| Follow Seller | 1 per request |
| Review page | 5 per page |

Credits are only consumed on successful requests (API code 0). Average response time is approximately 5 seconds.

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | API error (non-zero response code) |
| 2 | Usage error (bad arguments) |
| 3 | Network error (connection, SSL, rate limit) |
| 4 | Authentication error |

## Troubleshooting

| Error Code | Meaning | User-Friendly Message | Resolution |
|---|---|---|---|
| `MISSING_ENV` | No credentials set | "I need your Pangolin credentials to access Amazon data." | Set `PANGOLIN_EMAIL` + `PANGOLIN_PASSWORD` or `PANGOLIN_API_KEY` |
| `AUTH_FAILED` | Bad email/password | "Authentication failed. Please check your Pangolin credentials." | Verify email and password |
| `RATE_LIMIT` | Too many requests | "The API is rate-limiting us. Let me wait and retry." | Wait and retry |
| `NETWORK` | Connection failed | "I couldn't reach the API. Please check your connection." | Check internet, retry |
| `SSL_CERT` | SSL verification failed | "SSL error -- likely a macOS Python issue." | See macOS SSL section above |
| `API_ERROR` | API returned error | "The API returned an error." | Check error details, retry |
| `USAGE_ERROR` | Bad CLI arguments | "I need more information to run this query." | Provide required arguments |

**API error codes from the server:**

| API Code | Meaning | Resolution |
|---|---|---|
| 1004 | Expired/invalid API key | Auto-refreshed by the script |
| 2001 | Insufficient credits | Top up at pangolinfo.com |
| 2007 | Account expired | Renew subscription |
| 10000/10001 | Task execution failed | Retry the request |
| 404 | Bad URL format | Verify the target URL |

## Important Notes for AI Agents

1. **Never dump raw JSON** to the user. Always parse and present results in a structured, readable format following the Response Presentation guidelines above.

2. **Match the user's language.** If the user writes in Chinese, respond in Chinese. If English, respond in English. This applies to product descriptions, error messages, and suggestions.

3. **Be proactive.** If a keyword search returns results, highlight the best match. If reviews show a pattern, summarize it. If a product is out of stock, say so immediately.

4. **Handle multi-step requests.** If the user says "compare this product on US and Japan Amazon," run two queries with different `--site` values and present a comparison table.

5. **Credit awareness.** Each request costs credits. Avoid unnecessary duplicate requests. If the user asks for reviews across multiple pages, warn them about the cost (5 credits per page).

6. **Error recovery.** If a request fails, check the error code and suggest a fix before retrying. Do not retry blindly.

7. **ASIN detection.** If the user provides a 10-character code starting with B0, it is almost certainly an ASIN. Auto-detect and use `--content` with no extra prompting.

8. **Default to `amz_us`** unless the user specifies a region or the context implies a different marketplace.

9. **Security.** Never expose API keys, passwords, or full API responses containing authentication data in the conversation.

10. **Combine results.** When the user asks a compound question (e.g., "find a good wireless mouse under $30 with good reviews"), run a keyword search first, then fetch reviews for the top candidates. Present a consolidated recommendation.
