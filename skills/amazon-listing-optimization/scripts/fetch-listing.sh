#!/usr/bin/env bash
# Amazon Listing Fetcher — extracts listing data from an Amazon product page
# Usage: fetch-listing.sh <ASIN> [marketplace]
# Marketplaces: us (default), uk, de, fr, it, es, jp, ca, au, in, mx, br

set -uo pipefail

ASIN="${1:?Usage: fetch-listing.sh <ASIN> [marketplace]}"
MP="${2:-us}"

declare -A DOMAINS=(
  [us]="www.amazon.com" [uk]="www.amazon.co.uk" [de]="www.amazon.de"
  [fr]="www.amazon.fr" [it]="www.amazon.it" [es]="www.amazon.es"
  [jp]="www.amazon.co.jp" [ca]="www.amazon.ca" [au]="www.amazon.com.au"
  [in]="www.amazon.in" [mx]="www.amazon.com.mx" [br]="www.amazon.com.br"
)

DOMAIN="${DOMAINS[$MP]:-www.amazon.com}"
URL="https://${DOMAIN}/dp/${ASIN}"

# Fetch the page
PAGE=$(curl -sL \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -H "Accept: text/html,application/xhtml+xml" \
  --max-time 15 \
  "$URL" 2>/dev/null)

if [ -z "$PAGE" ]; then
  echo "ERROR: Failed to fetch $URL"
  exit 1
fi

echo "=== LISTING DATA FOR $ASIN ($MP) ==="
echo "URL: $URL"
echo ""

# Title
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

# Rating
echo "=== RATING ==="
echo "$PAGE" | grep -o '[0-9]\.[0-9] out of 5 stars' | head -1
echo ""

# Review count
echo "=== REVIEW COUNT ==="
echo "$PAGE" | grep -o 'acrCustomerReviewText"[^>]*>[^<]*' | sed 's/acrCustomerReviewText"[^>]*>//' | head -1
echo ""

# Bullet points
echo "=== BULLET POINTS ==="
echo "$PAGE" | grep -o 'a-list-item">[A-Z][^<]\{15,\}' | sed 's/a-list-item">//' | head -10
echo ""

# Description
echo "=== DESCRIPTION ==="
echo "$PAGE" | grep -o 'productDescription"[^>]*>.*</div>' | head -1 | sed 's/<[^>]*>//g;s/^[[:space:]]*//;s/[[:space:]]*$//' | head -5
echo ""

# Image count (main images)
echo "=== IMAGE COUNT ==="
IMG_COUNT=$(echo "$PAGE" | grep -o '"hiRes":"https://[^"]*"' | wc -l)
echo "$IMG_COUNT main images"
echo ""

# A+ Content detection
echo "=== A+ CONTENT ==="
if echo "$PAGE" | grep -q 'aplus-v2\|a-plus-content\|aplusPageWidget'; then
  echo "YES — A+ Content detected"
else
  echo "NO — No A+ Content found"
fi
echo ""

# BSR
echo "=== BEST SELLERS RANK ==="
echo "$PAGE" | grep -o '#[0-9,]* in [^<]*' | head -3
echo ""

# Category
echo "=== CATEGORY ==="
echo "$PAGE" | grep -o 'a-link-normal a-color-tertiary"[^>]*>[^<]*' | sed 's/.*>//;s/^[[:space:]]*//;s/[[:space:]]*$//' | head -5
echo ""

# Date first available
echo "=== DATE FIRST AVAILABLE ==="
echo "$PAGE" | grep -o 'Date First Available[^<]*' | sed 's/Date First Available//;s/[^A-Za-z0-9, ]//g;s/^[[:space:]]*//;s/[[:space:]]*$//' | head -1
echo ""

echo "=== END ==="
