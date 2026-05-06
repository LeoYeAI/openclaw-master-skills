# Binance Authentication

All trading endpoints require HMAC SHA256 signed requests.

## Base URLs

| Environment | URL |
|-------------|-----|
| Mainnet | https://api.binance.com |
| Testnet | https://testnet.binance.vision |

## Required Headers
X-MBX-APIKEY: your_api_key

## Signing Process

### Step 1: Build Query String

Include all parameters plus `timestamp` (current Unix time in milliseconds):
`symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1234567890123`

**Optional:** Add `recvWindow` (default 5000ms) for timestamp tolerance.

### Step 2: Generate Signature

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

### Step 3: Append Signature

Add signature parameter to the query string:
`symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1234567890123&signature=abc123...`

### Step 4: Add Product User Agent Header

Include `User-Agent` header with the following string: `binance-spot/1.0.1 (Skill)`

#### Complete Example

Request:
```bash
curl -X POST "https://api.binance.com/api/v3/order" \
  -H "X-MBX-APIKEY: your_api_key" \
  -H "User-Agent: binance-spot/1.0.1 (Skill)" \
  -d "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1234567890123&signature=..."
```

```bash
#!/bin/bash
API_KEY="your_api_key"
SECRET_KEY="your_secret_key"
BASE_URL="https://api.binance.com"  # or https://testnet.binance.vision

# Get current timestamp
TIMESTAMP=$(date +%s000)

# Build query string (without signature)
QUERY="symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=${TIMESTAMP}"

# Generate signature
SIGNATURE=$(echo -n "$QUERY" | openssl dgst -sha256 -hmac "$SECRET_KEY" | cut -d' ' -f2)

# Make request
curl -X POST "${BASE_URL}/api/v3/order?${QUERY}&signature=${SIGNATURE}" \
  -H "X-MBX-APIKEY: ${API_KEY}"\
  -H "User-Agent: binance-spot/1.0.1 (Skill)"
```

If you get -1021 Timestamp outside recvWindow:

1. Check server time: GET /api/v3/time
2. Sync your clock or adjust timestamp
3. Increase recvWindow (max 60000ms)

### Security Notes

* Never share your secret key
* Use IP whitelist in Binance API settings
* Enable only required permissions (spot trading, no withdrawals)
* Use testnet for development: https://testnet.binance.vision
* Testnet credentials are separate from mainnet