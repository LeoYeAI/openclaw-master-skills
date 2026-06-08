# Binance Authentication

All trading endpoints require HMAC SHA256 signed requests.

## Base URLs

| Environment | URL |
|-------------|-----|
| Mainnet | https://fapi.binance.com |
| Testnet | https://demo-fapi.binance.com |

## Required Headers

* `X-MBX-APIKEY`: your_api_key
* `User-Agent`: binance-derivatives-trading-usds-futures/1.0.0 (Skill)

## Signing Process

### Step 1: Build Query String

Include all parameters plus `timestamp` (current Unix time in milliseconds):
`symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1234567890123`

**Optional:** Add `recvWindow` (default 5000ms) for timestamp tolerance.

### Step 2: Percent‑Encode Parameters

Before generating the signature, **percent‑encode all parameter names and values using UTF‑8 encoding according to RFC 3986.**
Unreserved characters that must not be encoded: `A-Z a-z 0-9 - _ . ~`

- Chinese characters example:
`symbol=这是测试币456`

Percent‑encoded:
`symbol=%E8%BF%99%E6%98%AF%E6%B5%8B%E8%AF%95%E5%B8%81456`

**Important:**
The exact encoded query string must be used for both signing and the HTTP request.

### Step 3: Generate Signature

Generate the signature from the encoded query string.

#### HMAC SHA256 signature

Create HMAC SHA256 signature of the query string using your secret key:

```bash
# Example using openssl
echo -n "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1234567890123" | \
  openssl dgst -sha256 -hmac "your_secret_key"
```

#### RSA signature

Create RSA signature of the query string using your private key:

```bash
# Example using openssl
echo -n "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1234567890123" | \
  openssl dgst -sha256 -sign private_key.pem | base64
```

#### Ed25519 signature

Create Ed25519 signature of the query string using your private key:

```bash
# Example using openssl
echo -n "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1234567890123" | \
  openssl pkeyut -pubout -in private_key.pem -outform DER | \
  openssl dgst -sha256 -sign private_key.pem | base64
```

### Step 4: Append Signature

Add signature parameter to the query string:
`symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1234567890123&signature=abc123...`

### Step 5: Add Product User Agent Header

Include `User-Agent` header with the following string: `binance-derivatives-trading-usds-futures/1.0.0 (Skill)`

#### Complete Example

Request:
```bash
curl -X POST "https://fapi.binance.com/fapi/v1/order" \
  -H "X-MBX-APIKEY: your_api_key" \
  -H "User-Agent: binance-derivatives-trading-usds-futures/1.0.0 (Skill)" \
  -d "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1234567890123&signature=..."
```

```bash
#!/bin/bash
API_KEY="your_api_key"
SECRET_KEY="your_secret_key"
BASE_URL="https://fapi.binance.com"  # or https://demo-fapi.binance.com

# Get current timestamp
TIMESTAMP=$(date +%s000)

# Build query string (without signature)
QUERY="symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=${TIMESTAMP}"

# Generate signature
SIGNATURE=$(echo -n "$QUERY" | openssl dgst -sha256 -hmac "$SECRET_KEY" | cut -d' ' -f2)

# Make request
curl -X POST "${BASE_URL}/fapi/v1/order?${QUERY}&signature=${SIGNATURE}" \
  -H "X-MBX-APIKEY: ${API_KEY}"\
  -H "User-Agent: binance-derivatives-trading-usds-futures/1.0.0 (Skill)"
```

If you get -1021 Timestamp outside recvWindow:

1. Check server time: GET /fapi/v1/time
2. Sync your clock or adjust timestamp
3. Increase recvWindow (max 60000ms)

### Security Notes

* Never share your secret key
* Use IP whitelist in Binance API settings
* Enable only required permissions (spot trading, no withdrawals)
* Use testnet for development: https://demo-fapi.binance.com
* Testnet credentials are separate from mainnet
