#!/usr/bin/env bash
#
# verify-endpoint.sh - Verify Yatta! API endpoint is legitimate
#
# Usage: bash scripts/verify-endpoint.sh
#

set -euo pipefail

ENDPOINT="${YATTA_API_URL:-https://zunahvofybvxpptjkwxk.supabase.co/functions/v1}"
HOST=$(echo "$ENDPOINT" | sed 's|https://||;s|http://||' | cut -d/ -f1)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Yatta! API Endpoint Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Endpoint: $ENDPOINT"
echo "Host:     $HOST"
echo ""

# Test 1: SSL certificate
echo "1️⃣  Checking SSL certificate..."
if command -v openssl &>/dev/null; then
  CERT_SUBJECT=$(echo | openssl s_client -connect "$HOST:443" -servername "$HOST" 2>/dev/null | \
    openssl x509 -noout -subject 2>/dev/null | sed 's/subject=//' || echo "Failed to retrieve")
  CERT_ISSUER=$(echo | openssl s_client -connect "$HOST:443" -servername "$HOST" 2>/dev/null | \
    openssl x509 -noout -issuer 2>/dev/null | sed 's/issuer=//' || echo "Failed to retrieve")
  
  echo "   Subject: $CERT_SUBJECT"
  echo "   Issuer:  $CERT_ISSUER"
  
  if [[ "$CERT_SUBJECT" == *"supabase.co"* ]]; then
    echo "   ✅ Valid Supabase certificate"
  else
    echo "   ⚠️  Certificate does not match expected Supabase pattern"
  fi
else
  echo "   ⚠️  openssl not found, skipping certificate check"
fi
echo ""

# Test 2: DNS resolution
echo "2️⃣  Checking DNS resolution..."
if command -v dig &>/dev/null; then
  IP=$(dig +short "$HOST" | head -1 || echo "Failed to resolve")
  echo "   Host resolves to: $IP"
  
  if [[ -n "$IP" && "$IP" != "Failed to resolve" ]]; then
    echo "   ✅ DNS resolution successful"
  else
    echo "   ❌ DNS resolution failed"
  fi
elif command -v nslookup &>/dev/null; then
  IP=$(nslookup "$HOST" 2>/dev/null | grep -A1 "Name:" | tail -1 | awk '{print $2}' || echo "Failed")
  echo "   Host resolves to: $IP"
  
  if [[ -n "$IP" && "$IP" != "Failed" ]]; then
    echo "   ✅ DNS resolution successful"
  else
    echo "   ❌ DNS resolution failed"
  fi
else
  echo "   ⚠️  dig/nslookup not found, skipping DNS check"
fi
echo ""

# Test 3: HTTP connectivity
echo "3️⃣  Checking HTTP connectivity..."
if command -v curl &>/dev/null; then
  # Try health check (might not exist, but we can test connectivity)
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT/health" 2>/dev/null || echo "000")
  
  if [[ "$HTTP_STATUS" == "200" ]]; then
    echo "   HTTP Status: $HTTP_STATUS (OK)"
    echo "   ✅ Endpoint is reachable and healthy"
  elif [[ "$HTTP_STATUS" == "404" ]]; then
    echo "   HTTP Status: $HTTP_STATUS (Not Found)"
    echo "   ℹ️  Endpoint reachable (health check endpoint may not exist)"
  elif [[ "$HTTP_STATUS" == "401" || "$HTTP_STATUS" == "403" ]]; then
    echo "   HTTP Status: $HTTP_STATUS (Auth required)"
    echo "   ✅ Endpoint is reachable (requires authentication)"
  else
    echo "   HTTP Status: $HTTP_STATUS"
    echo "   ⚠️  Unexpected HTTP status"
  fi
else
  echo "   ⚠️  curl not found, skipping HTTP check"
fi
echo ""

# Test 4: Supabase project identification
if [[ "$HOST" == *".supabase.co" ]]; then
  PROJECT_ID=$(echo "$HOST" | cut -d. -f1)
  echo "4️⃣  Supabase project details:"
  echo "   Project ID: $PROJECT_ID"
  echo "   Expected:   zunahvofybvxpptjkwxk"
  
  if [[ "$PROJECT_ID" == "zunahvofybvxpptjkwxk" ]]; then
    echo "   ✅ Matches expected Yatta! production project"
  else
    echo "   ⚠️  Project ID does not match expected value"
  fi
else
  echo "4️⃣  Not a Supabase URL"
  echo "   ℹ️  Custom domain or different backend"
fi
echo ""

# Final assessment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Assessment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if this is the expected Supabase project
if [[ "$HOST" == "zunahvofybvxpptjkwxk.supabase.co" ]]; then
  echo "✅ This is the official Yatta! production API endpoint"
  echo ""
  echo "   - Hosted on Supabase (Yatta! backend infrastructure)"
  echo "   - Project owner: Chris Giddings (chris@chrisgiddings.net)"
  echo "   - App: https://yattadone.com"
  echo ""
  echo "   Safe to use with your YATTA_API_KEY."
else
  echo "⚠️  This endpoint does not match the expected Yatta! production URL"
  echo ""
  echo "   Expected: zunahvofybvxpptjkwxk.supabase.co"
  echo "   Current:  $HOST"
  echo ""
  echo "   If you intentionally set a custom YATTA_API_URL, verify it's correct."
  echo "   If not, check your environment variables."
fi
echo ""

# Additional verification steps
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Additional Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Visit https://yattadone.com and confirm it's the correct app"
echo "2. Check Settings → About for API endpoint confirmation"
echo "3. Contact support@yattadone.com if you have any concerns"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
