#!/usr/bin/env bash
# Validate Nimble Search API configuration and test queries

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if API key is set
if [ -z "${NIMBLE_API_KEY:-}" ]; then
    print_error "NIMBLE_API_KEY environment variable is not set"
    echo "Set it with: export NIMBLE_API_KEY='your-api-key'"
    exit 1
fi

print_success "API key is configured"

# Parse arguments
QUERY="${1:-test query}"
FOCUS="${2:-general}"

# Validate focus mode
VALID_MODES=("general" "coding" "news" "academic" "shopping" "social" "geo" "location")
if [[ ! " ${VALID_MODES[@]} " =~ " ${FOCUS} " ]]; then
    print_error "Invalid focus mode: $FOCUS"
    echo "Valid modes: ${VALID_MODES[*]}"
    exit 1
fi

print_success "Focus mode '$FOCUS' is valid"

# API endpoint
API_URL="https://nimble-retriever.webit.live/search"

# Test API connectivity
echo "Testing API connectivity..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$API_URL" \
    -H "Authorization: Bearer $NIMBLE_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "'"$QUERY"'",
        "focus": "'"$FOCUS"'",
        "max_results": 3
    }')

if [ "$HTTP_CODE" -eq 200 ]; then
    print_success "API request successful (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" -eq 401 ]; then
    print_error "Authentication failed (HTTP $HTTP_CODE)"
    echo "Check your API key at https://www.nimbleway.com/"
    exit 1
elif [ "$HTTP_CODE" -eq 429 ]; then
    print_warning "Rate limit exceeded (HTTP $HTTP_CODE)"
    echo "Wait a moment and try again"
    exit 1
else
    print_error "API request failed (HTTP $HTTP_CODE)"
    exit 1
fi

# Test with actual response
echo "Testing query: '$QUERY' with focus: '$FOCUS'"
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Authorization: Bearer $NIMBLE_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "'"$QUERY"'",
        "focus": "'"$FOCUS"'",
        "max_results": 3,
        "include_answer": false
    }')

# Check if response contains results
RESULT_COUNT=$(echo "$RESPONSE" | grep -o '"total_results":[0-9]*' | grep -o '[0-9]*' || echo "0")

if [ "$RESULT_COUNT" -gt 0 ]; then
    print_success "Found $RESULT_COUNT results"
    echo ""
    echo "Sample results:"
    echo "$RESPONSE" | grep -o '"url":"[^"]*"' | head -3 | sed 's/"url":"//g' | sed 's/"$//g' | while read -r url; do
        echo "  - $url"
    done
else
    print_warning "No results found for query"
fi

echo ""
print_success "Validation complete!"
