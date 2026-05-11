# ClawLaunch Error Handling Reference

Complete guide to handling errors from the ClawLaunch API.

## Error Response Format

All errors follow this structure:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "hint": "Suggestion for resolution"
}
```

Additional fields may be included depending on the error type.

## Error Codes Reference

### Authentication Errors

#### UNAUTHORIZED (401)
**Cause:** Invalid or missing API key.

**Response:**
```json
{
  "error": "Invalid or missing API key",
  "code": "UNAUTHORIZED",
  "hint": "Include a valid API key in the x-api-key header"
}
```

**Resolution:**
1. Check API key is set in `x-api-key` header
2. Verify API key is correct (no extra whitespace)
3. Ensure API key hasn't been revoked
4. Contact support if key should be valid

#### FORBIDDEN (403)
**Cause:** API key is valid but lacks required scope.

**Response:**
```json
{
  "error": "Insufficient permissions",
  "code": "FORBIDDEN",
  "required": "launch",
  "clientScopes": ["read"]
}
```

**Resolution:**
1. Check which scope is required (`required` field)
2. Compare with your key's scopes (`clientScopes` field)
3. Request additional scopes from admin

**Scopes:**
- `read` - List tokens, get quotes
- `trade` - Buy and sell tokens
- `launch` - Launch new tokens

### Rate Limiting Errors

#### RATE_LIMITED (429)
**Cause:** Too many requests in time window.

**Response:**
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMITED",
  "retryAfter": 1800,
  "limitType": "launch",
  "limit": "10 per hour"
}
```

**Resolution:**
1. Wait for `retryAfter` seconds before retrying
2. Check `Retry-After` response header
3. Implement exponential backoff
4. Cache responses where possible

**Rate Limits by Endpoint:**
| Endpoint | Limit | Window |
|----------|-------|--------|
| `/agent/launch` | 10 | 1 hour |
| `/token/buy` | 50 | 1 hour |
| `/token/sell` | 50 | 1 hour |
| `/token/quote` | 100 | 1 minute |
| `/tokens` | 100 | 1 minute |

### Validation Errors

#### VALIDATION_ERROR (400)
**Cause:** Invalid request body or parameters.

**Response:**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "issues": [
    { "field": "symbol", "message": "Symbol must be uppercase letters and numbers only" },
    { "field": "name", "message": "Name must be 1-32 characters" }
  ]
}
```

**Resolution:**
1. Check each issue in `issues` array
2. Fix the specific field mentioned
3. Refer to API docs for field requirements

**Common Validation Issues:**
| Field | Requirement |
|-------|-------------|
| name | 1-32 characters |
| symbol | 1-8 characters, A-Z0-9 only |
| tokenAddress | Valid Ethereum address (0x...) |
| amount | Positive integer string (wei) |
| slippageBps | 0-1000 (0-10%) |

### Token-Specific Errors

#### NOT_FOUND (404)
**Cause:** Token address not found in ClawLaunch factory.

**Response:**
```json
{
  "error": "Token not found in ClawLaunch factory",
  "code": "NOT_FOUND",
  "hint": "Verify the token address from /tokens endpoint"
}
```

**Resolution:**
1. Verify token address is correct
2. Check if token exists via `/tokens` endpoint
3. Ensure token was launched through ClawLaunch (not external)

#### TOKEN_GRADUATED (400)
**Cause:** Token has migrated to Uniswap V3.

**Response:**
```json
{
  "error": "Token has graduated to Uniswap V3",
  "code": "TOKEN_GRADUATED",
  "hint": "Trade this token on Uniswap V3 instead",
  "uniswapUrl": "https://app.uniswap.org/swap?chain=base&inputCurrency=ETH&outputCurrency=0x..."
}
```

**Resolution:**
1. Use Uniswap V3 for trading this token
2. Check `isGraduated` field before attempting trades
3. Use provided `uniswapUrl` for trading

### Trading Errors

#### BELOW_MIN_TRADE (400)
**Cause:** Trade amount below 0.0001 ETH minimum.

**Response:**
```json
{
  "error": "Trade amount below minimum",
  "code": "BELOW_MIN_TRADE",
  "minimum": "100000000000000",
  "provided": "50000000000000",
  "hint": "Minimum trade is 0.0001 ETH"
}
```

**Resolution:**
1. Increase trade amount to at least 0.0001 ETH (100000000000000 wei)
2. For sells, ensure token amount converts to >= 0.0001 ETH value

#### INSUFFICIENT_BALANCE (400)
**Cause:** Wallet doesn't have enough tokens to sell.

**Response:**
```json
{
  "error": "Insufficient token balance",
  "code": "INSUFFICIENT_BALANCE",
  "requested": "1000000000000000000000",
  "available": "500000000000000000000",
  "hint": "Check balance or use sellAll: true"
}
```

**Resolution:**
1. Check token balance before selling
2. Use `sellAll: true` to sell entire balance
3. Reduce `tokenAmount` to available balance

#### INSUFFICIENT_FUNDS (400)
**Cause:** Wallet doesn't have enough ETH for gas.

**Response:**
```json
{
  "error": "Insufficient funds for gas",
  "code": "INSUFFICIENT_FUNDS",
  "hint": "The wallet needs ETH for gas. Send ETH to the wallet address.",
  "estimatedGas": "150000",
  "walletAddress": "0x..."
}
```

**Resolution:**
1. Send ETH to the wallet address
2. Minimum recommended: 0.01 ETH
3. Typical operation costs: 0.0001-0.003 ETH on Base

#### ZERO_AMOUNT (400)
**Cause:** Sell amount is zero.

**Response:**
```json
{
  "error": "Cannot sell zero tokens",
  "code": "ZERO_AMOUNT",
  "hint": "Provide tokenAmount or set sellAll: true"
}
```

**Resolution:**
1. Provide a non-zero `tokenAmount`
2. Or set `sellAll: true` to sell entire balance

#### SIGNATURE_ERROR (400)
**Cause:** EIP-712 signature verification failed.

**Response:**
```json
{
  "error": "Signature verification failed",
  "code": "SIGNATURE_ERROR",
  "hint": "Regenerate the signature with correct parameters"
}
```

**Resolution:**
1. Ensure signing with correct wallet
2. Verify signature parameters match request
3. Check chainId matches network (8453 for Base mainnet)

### Server Errors

#### CONFIG_ERROR (500)
**Cause:** Server configuration issue.

**Response:**
```json
{
  "error": "Server configuration error",
  "code": "CONFIG_ERROR"
}
```

**Resolution:**
1. This is a server-side issue
2. Retry after a few minutes
3. Contact support if persistent

#### INTERNAL_ERROR (500)
**Cause:** Unhandled server error.

**Response:**
```json
{
  "error": "Internal server error",
  "code": "INTERNAL_ERROR"
}
```

**Resolution:**
1. Retry with exponential backoff
2. Check service status
3. Contact support with request details

## Error Handling Best Practices

### Retry Strategy

```python
import time
import requests

def api_call_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 429:
                # Rate limited - wait and retry
                retry_after = int(response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                continue

            if response.status_code >= 500:
                # Server error - exponential backoff
                time.sleep(2 ** attempt)
                continue

            return response.json()

        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

    raise Exception("Max retries exceeded")
```

### Pre-validation

```python
def validate_before_trading(token_address, action, amount):
    """Validate trade before making API call."""

    # Check token exists and not graduated
    tokens = get_tokens()
    token = next((t for t in tokens if t['address'] == token_address), None)

    if not token:
        raise ValueError(f"Token {token_address} not found")

    if token['isGraduated']:
        raise ValueError("Token graduated - use Uniswap V3")

    # For sells, check balance
    if action == 'sell':
        balance = get_token_balance(token_address, wallet_address)
        if int(amount) > balance:
            raise ValueError(f"Insufficient balance: have {balance}, want {amount}")

    # Get quote to validate amount
    quote = get_quote(token_address, action, amount)
    if not quote.get('success'):
        raise ValueError(f"Quote failed: {quote.get('error')}")

    return quote
```

### Error Logging

```python
def log_api_error(response, request_data):
    """Log API errors for debugging."""

    error_data = response.json()

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'status': response.status_code,
        'code': error_data.get('code'),
        'error': error_data.get('error'),
        'hint': error_data.get('hint'),
        'request': request_data,
    }

    logger.error(f"ClawLaunch API error: {log_entry}")
```

## HTTP Status Code Summary

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Fix request parameters |
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | Check scope permissions |
| 404 | Not Found | Verify token address |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Retry with backoff |

## Support

If errors persist after following troubleshooting steps:
- **Website:** https://www.clawlaunch.fun
- **GitHub Issues:** Report persistent API issues
- Include: error code, request details, timestamp
