# Aster Futures Authentication

All trading endpoints require EIP-712 ECDSA signed requests.

## Base URLs

| Environment | URL |
|-------------|-----|
| Mainnet | https://fapi.asterdex.com |

## Required Headers

No special headers required. Authentication parameters are included in the request body or query string.

## Authentication Parameters

| Parameter | Description |
|-----------|-------------|
| user | Main wallet address |
| signer | API wallet address (AGENT credential from Pro API registration) |
| nonce | Microsecond timestamp |
| signature | ECDSA signature (EIP-712) |

### Security Types

| Type | Description |
|------|-------------|
| NONE | No authentication required |
| TRADE | Requires signer + signature |
| USER_DATA | Requires signer + signature |
| USER_STREAM | Requires signer + signature |
| MARKET_DATA | Requires signer + signature |

## Signing Process (EIP-712)

### Step 1: Sort Parameters

Sort all API parameters by ASCII key order. All parameter values must be converted to strings.

For example, given parameters `symbol=BTCUSDT`, `side=BUY`, `quantity=0.001`:
```
quantity=0.001&side=BUY&symbol=BTCUSDT
```

### Step 2: ABI Encode

Combine the sorted parameters with `user`, `signer`, and `nonce` using Web3 ABI encoding.

### Step 3: Generate Keccak256 Hash

Hash the ABI-encoded data using Keccak256.

### Step 4: Sign with ECDSA

Sign the resulting hash with the API wallet's private key via ECDSA to produce the `signature`.

### Step 5: Include Auth Parameters

Add `user`, `signer`, `nonce`, and `signature` to the request.

## Timestamp / recvWindow

- The `nonce` parameter must be a current microsecond timestamp
- Requests are valid within `recvWindow` (default 5000ms)
- Recommended `recvWindow`: 5000ms or less

## Complete Example (Python)

```python
import time
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct

# Configuration
BASE_URL = "https://fapi.asterdex.com"
USER_ADDRESS = "0xYourMainWalletAddress"
SIGNER_ADDRESS = "0xYourApiWalletAddress"
SIGNER_PRIVATE_KEY = "0xYourApiWalletPrivateKey"

def sign_request(params: dict) -> dict:
    """Sign a request using EIP-712 ECDSA."""

    # Step 1: Sort parameters by ASCII key order, all values as strings
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    sorted_str_params = [(k, str(v)) for k, v in sorted_params]

    # Step 2: Generate nonce (microsecond timestamp)
    nonce = int(time.time() * 1_000_000)

    # Step 3: ABI encode the sorted parameters with user, signer, nonce
    # Build the data to encode
    param_types = ["address", "address", "uint256"]  # user, signer, nonce
    param_values = [USER_ADDRESS, SIGNER_ADDRESS, nonce]

    for key, value in sorted_str_params:
        param_types.append("string")
        param_values.append(f"{key}={value}")

    encoded = Web3.solidity_keccak(param_types, param_values)

    # Step 4: Sign the hash with the API wallet's private key
    message = encode_defunct(encoded)
    signed = Account.sign_message(message, private_key=SIGNER_PRIVATE_KEY)
    signature = signed.signature.hex()

    # Step 5: Build final request parameters
    auth_params = {
        "user": USER_ADDRESS,
        "signer": SIGNER_ADDRESS,
        "nonce": nonce,
        "signature": signature,
    }

    return {**dict(sorted_str_params), **auth_params}


# Example: Place a limit order
import requests

order_params = {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "quantity": "0.001",
    "price": "50000",
    "timeInForce": "GTC",
}

signed_params = sign_request(order_params)

response = requests.post(
    f"{BASE_URL}/fapi/v1/order",
    data=signed_params,
)
print(response.json())
```

## Security Notes

* Never share your API wallet private key
* Use a dedicated API wallet (AGENT credential) separate from your main wallet
* Register for Pro API access at asterdex.com to obtain AGENT credentials
* Keep `recvWindow` at 5000ms or less to minimize replay attack window
* Use IP restrictions where possible
* TESTUSDT or any symbols starting with TEST are for Aster's internal testing only
