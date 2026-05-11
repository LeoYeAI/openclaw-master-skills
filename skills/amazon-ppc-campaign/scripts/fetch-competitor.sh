#!/usr/bin/env bash
# Amazon Competitor Fetcher for PPC — extracts keywords from competitor listings
# Usage: fetch-competitor.sh <ASIN> [marketplace]
# Output: title, brand, bullets, price, category, BSR — data needed for keyword extraction

set -uo pipefail

ASIN="${1:?Usage: fetch-competitor.sh <ASIN> [marketplace]}"
MP="${2:-us}"

declare -A DOMAINS=(
  [us]="www.amazon.com" [uk]="www.amazon.co.uk" [de]="www.amazon.de"
  [fr]="www.amazon.fr" [it]="www.amazon.it" [es]="www.amazon.es"
  [jp]="www.amazon.co.jp" [ca]="www.amazon.ca" [au]="www.amazon.com.au"
  [in]="www.amazon.in" [mx]="www.amazon.com.mx" [br]="www.amazon.com.br"
)

DOMAIN="${DOMAINS[$MP]:-www.amazon.com}"
URL="https://${DOMAIN}/dp/${ASIN}"

PAGE=$(curl -sL \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
  -H "Accept-Encoding: gzip, deflate" \
  --compressed \
  --max-time 15 \
  "$URL" 2>/dev/null)

if [ -z "$PAGE" ]; then
  echo "ERROR: Failed to fetch $URL"
  exit 1
fi

echo "=== COMPETITOR: $ASIN ($MP) ==="
echo "URL: $URL"
echo ""

# Title — primary keyword source
echo "=== TITLE ==="
echo "$PAGE" | grep -o 'productTitle"[^>]*>[^<]*' | sed 's/productTitle"[^>]*>//;s/^[[:space:]]*//;s/[[:space:]]*$//' | head -1
echo ""

# Brand
echo "=== BRAND ==="
echo "$PAGE" | grep -o 'bylineInfo"[^>]*>[^<]*' | sed 's/bylineInfo"[^>]*>//;s/^[[:space:]]*Visit the //;s/ Store$//' | head -1
echo ""

# Price
echo "=== PRICE ==="
echo "$PAGE" | grep -o '<span class="a-offscreen">[^<]*</span>' | head -1 | sed 's/<[^>]*>//g'
echo ""

# Bullet points — rich keyword source
echo "=== BULLET POINTS ==="
echo "$PAGE" | grep -o 'a-list-item">[A-Z][^<]\{15,\}' | sed 's/a-list-item">//' | head -10
echo ""

# Category
echo "=== CATEGORY ==="
echo "$PAGE" | grep -o 'a-link-normal a-color-tertiary"[^>]*>[^<]*' | sed 's/.*>//;s/^[[:space:]]*//;s/[[:space:]]*$//' | head -5
echo ""

# BSR — indicates sales volume
echo "=== BEST SELLERS RANK ==="
echo "$PAGE" | grep -o '#[0-9,]* in [^<]*' | head -3
echo ""

# Review count — indicates market strength
echo "=== REVIEW COUNT ==="
echo "$PAGE" | grep -o 'acrCustomerReviewText"[^>]*>[^<]*' | sed 's/acrCustomerReviewText"[^>]*>//' | head -1
echo ""

echo "=== END ==="
