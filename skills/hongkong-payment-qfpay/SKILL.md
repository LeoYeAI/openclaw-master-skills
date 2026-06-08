---
name: HONGKONG-PAYMENT-QFPAY
description: QFPay API is a comprehensive payment solution that offers various payment methods to meet the needs of different businesses. This skill provides complete API integration guidelines including environment configuration, request formats, signature generation, payment types, supported currencies, and status codes.
--- 

# QFPay Payment API Skill

## Overview

QFPay API is a comprehensive payment solution that offers various payment methods to meet the needs of different businesses. This skill provides complete API integration guidelines including environment configuration, request formats, signature generation, payment types, supported currencies, and status codes.


## Environment Configuration

QFPay API is accessible via three main environments:

| Environment | Base URL | Description |
|-------------|----------|-------------|
| Sandbox | `https://openapi-int.qfapi.com` | For simulating payments without real fund deduction |
| Testing | `https://test-openapi-hk.qfapi.com` | Real payment flow but linked to test accounts (no settlement) |
| Production | `https://openapi-hk.qfapi.com` | Real live payments with actual settlement |

**Important Notes:**
- Transactions in Testing environment using test accounts will NOT be settled
- Always ensure refunds are triggered immediately for test transactions
- Mixing credentials or endpoints across environments will result in signature or authorization errors

### Environment Variables Setup

Configure these environment variables before using the API:

```bash
export QFPAY_APPCODE="your_app_code_here"
export QFPAY_KEY="your_client_key_here"
export QFPAY_MCHID="your_merchant_id"  # Optional, depends on account setup
export QFPAY_ENV="sandbox"  # Options: prod, test, sandbox
```

## API Usage Guidelines

### Rate Limiting

To ensure fair usage and optimal performance:

- **Limit**: Maximum 100 requests per second (RPS) and 400 requests per minute per merchant
- **Exceeding Limit**: API responds with HTTP 429 (Too Many Requests)

### Best Practices

1. **Batch Requests**: Use batch processing to minimize individual requests
2. **Efficient Queries**: Utilize filtering and pagination
3. **Caching**: Implement response caching to avoid repeated requests
4. **Monitoring**: Track API usage and implement logging for request patterns

### Error Handling

When receiving HTTP 429:
1. Pause further requests for a specified duration
2. Implement exponential backoff for retries
3. Log errors for monitoring

### Traffic Spike Management

For anticipated traffic spikes (e.g., promotional events), contact:
- **Technical Support**: technical.support@qfpay.com

## Request Format

### HTTP Request

```
POST /trade/v1/payment
```

### Public Payment Request Parameters

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `txamt` | Yes | Int(11) | Transaction amount in cents (100 = $1). Suggest > 200 to avoid risk control |
| `txcurrcd` | Yes | String(3) | Transaction currency. See Currencies section for full list |
| `pay_type` | Yes | String(6) | Payment type code. See Payment Types section |
| `out_trade_no` | Yes | String(128) | External transaction number. Must be unique per merchant account |
| `txdtm` | Yes | String(20) | Transaction time format: YYYY-MM-DD hh:mm:ss |
| `auth_code` | Yes (CPM only) | String(128) | Authorization code for scanning barcode/QR. Expires within one day |
| `expired_time` | No (MPM only) | String(3) | QR expiration in minutes. Default: 30, Min: 5, Max: 120 |
| `goods_name` | No | String(64) | Item description. Max 20 chars, UTF-8 for Chinese. Required for App payments |
| `mchid` | No | String(16) | Merchant ID. Required if assigned, must NOT be included if not assigned |
| `udid` | No | String(40) | Unique device ID for internal tracking |
| `notify_url` | No | String(256) | URL for asynchronous payment notifications |

### HTTP Header Requirements

| Field | Required | Description |
|-------|----------|-------------|
| `X-QF-APPCODE` | Yes | App code assigned to merchant |
| `X-QF-SIGN` | Yes | Signature generated per signature algorithm |
| `X-QF-SIGNTYPE` | No | Signature algorithm. Use `SHA256` or defaults to `MD5` |

### Content Specifications

- **Character Encoding**: UTF-8
- **Method**: POST/GET (depends on endpoint)
- **Content-Type**: application/x-www-form-urlencoded

## Response Format

### Success Response Structure

```json
{
  "respcd": "0000",
  "respmsg": "success",
  "data": {
    "txamt": "100",
    "out_trade_no": "20231101000001",
    "txcurrcd": "HKD",
    "txstatus": "SUCCESS",
    "qf_trade_no": "9000020231101000001",
    "pay_type": "800101",
    "txdtm": "2023-11-01 10:00:00"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `respcd` | String(4) | Return code. "0000" means success |
| `respmsg` | String(64) | Message description of respcd |
| `data` | Object | Payment transaction data |

### Data Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `txamt` | String | Transaction amount in cents |
| `out_trade_no` | String | Merchant's original order number |
| `txcurrcd` | String | Currency code (e.g., HKD) |
| `txstatus` | String | Payment status: SUCCESS, FAILED, PENDING |
| `qf_trade_no` | String | QFPay's unique transaction number |
| `pay_type` | String | Payment method code |
| `txdtm` | String | Payment time (YYYY-MM-DD HH:mm:ss) |

### Signature Verification

Response may include `X-QF-SIGN` and `X-QF-SIGNTYPE` headers. Verify by:
1. Extracting data fields in sorted order
2. Concatenating as key1=value1&key2=value2&...
3. Appending client key
4. Generating MD5 hash and comparing

## Signature Generation

All API requests must include a digital signature in the HTTP header:

```
X-QF-SIGN: <your_signature>
```

### Step-by-Step Guide

#### Step 1: Sort Parameters

Sort all request parameters by parameter name in ASCII ascending order.

**Example:**

| Parameter | Value |
|-----------|-------|
| `mchid` | `ZaMVg12345` |
| `txamt` | `100` |
| `txcurrcd` | `HKD` |

Sorted result:
```
mchid=ZaMVg12345&txamt=100&txcurrcd=HKD
```

#### Step 2: Append Client Key

Append your secret `client_key` to the string.

If `client_key = abcd1234`:
```
mchid=ZaMVg12345&txamt=100&txcurrcd=HKDabcd1234
```

#### Step 3: Hash the String

Hash using MD5 or SHA256 (SHA256 recommended):

```
SHA256("mchid=ZaMVg12345&txamt=100&txcurrcd=HKDabcd1234")
```

#### Step 4: Add to Header

```
X-QF-SIGN: <your_hashed_signature>
```

### Important Notes

- Do NOT insert line breaks, tabs, or extra spaces
- Parameter names and values are case-sensitive
- Double-check parameter order and encoding if signature fails

### Code Examples

#### Python

```python
import os
import hashlib

APPCODE = os.getenv('QFPAY_APPCODE')
KEY = os.getenv('QFPAY_KEY')

def generate_signature(params, key):
    """Generate MD5 signature"""
    keys = list(params.keys())
    keys.sort()
    query = []
    for k in keys:
        if k not in ('sign', 'sign_type') and (params[k] or params[k] == 0):
            query.append(f'{k}={params[k]}')
    
    data = '&'.join(query) + key
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest().upper()

def generate_signature_sha256(params, key):
    """Generate SHA256 signature"""
    keys = list(params.keys())
    keys.sort()
    query = []
    for k in keys:
        if k not in ('sign', 'sign_type') and (params[k] or params[k] == 0):
            query.append(f'{k}={params[k]}')
    
    data = '&'.join(query) + key
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    return sha256.hexdigest().upper()
```

## Payment Types

The `pay_type` parameter specifies which payment method to use. This affects transaction routing and UI requirements.

**Note**: Not all `pay_type` values are enabled for every merchant. Contact technical.support@qfpay.com for clarification.

### Supported Payment Types

| Code | Description |
|------|-------------|
| 800008 | CPM for WeChat, Alipay, UnionPay QuickPass, PayMe |
| 800101 | Alipay MPM (Overseas Merchants) |
| 800108 | Alipay CPM (Overseas & HK Merchants) |
| 801101 | Alipay Web Payment (Overseas) |
| 801107 | Alipay WAP Payment (Overseas) |
| 801110 | Alipay In-App Payment (Overseas) |
| 800107 | Alipay Service Window H5 Payment |
| 801501 | Alipay MPM (HK Merchants) |
| 801510 | Alipay In-App (HK Merchants) |
| 801512 | Alipay WAP (HK Merchants) |
| 801514 | Alipay Web (HK Merchants) |
| 800201 | WeChat MPM (Overseas & HK) |
| 800208 | WeChat CPM (Overseas & HK) |
| 800207 | WeChat JSAPI Payment (Overseas & HK) |
| 800212 | WeChat H5 Payment |
| 800210 | WeChat In-App Payment (Overseas & HK) |
| 800213 | WeChat Mini-Program Payment |
| 801008 | WeChat Pay HK CPM (Direct Settlement, HK) |
| 801010 | WeChat Pay HK In-App (Direct Settlement, HK) |
| 805801 | PayMe MPM (HK Merchants) |
| 805808 | PayMe CPM (HK Merchants) |
| 805814 | PayMe Web Payment (HK Merchants) |
| 805812 | PayMe WAP Payment (HK Merchants) |
| 800701 | UnionPay QuickPass MPM |
| 800708 | UnionPay QuickPass CPM |
| 800712 | UnionPay WAP Payment (HK) |
| 800714 | UnionPay PC-Web Payment (HK) |
| 802001 | FPS MPM (HK Merchants) |
| 803701 | Octopus MPM (HK Merchants) |
| 803712 | Octopus WAP Payment (HK) |
| 803714 | Octopus PC-Web Payment (HK) |
| 802801 | Visa / Mastercard Online |
| 802808 | Visa / Mastercard Offline |
| 806527 | ApplePay Online |
| 806708 | UnionPay Card Offline |
| 806808 | American Express Card Offline |

### Special Remarks

- **801101**: Transaction amount must be greater than 1 HKD
- **802001**: This payment method does not support refunds

## Supported Currencies

All codes follow ISO 4217 format (3-letter uppercase):

| Code | Description |
|------|-------------|
| AED | Arab Emirates Dirham |
| CNY | Chinese Yuan |
| EUR | Euro |
| HKD | Hong Kong Dollar |
| IDR | Indonesian Rupiah |
| JPY | Japanese Yen |
| MMK | Myanmar Kyat |
| MYR | Malaysian Ringgit |
| SGD | Singapore Dollar |
| THB | Thai Baht |
| USD | United States Dollar |
| CAD | Canadian Dollar |
| AUD | Australian Dollar |

**Note**: Some payment methods may only support HKD. Verify with your integration manager before non-HKD transactions.

## Status Codes

Standard `respcd` values returned by QFPay API:

| Code | Description |
|------|-------------|
| 0000 | Transaction successful |
| 1100 | System under maintenance |
| 1101 | Reversal error |
| 1102 | Duplicate request |
| 1103 | Request format error |
| 1104 | Request parameter error |
| 1105 | Device not activated |
| 1106 | Invalid device |
| 1107 | Device not allowed |
| 1108 | Signature error |
| 1125 | Transaction already refunded |
| 1136 | Transaction does not exist or not operational |
| 1142 | Order already closed |
| 1143 | Order not paid, password being entered |
| 1145 | Processing, please wait |
| 1147 | WeChat Pay transaction error |
| 1150 | T0 billing method does not support cancellation |
| 1155 | Refund request denied |
| 1181 | Order expired |
| 1201 | Insufficient balance |
| 1202 | Incorrect or expired payment code |
| 1203 | Merchant account error |
| 1204 | Bank error |
| 1205 | Transaction failed, try again later |
| 1212 | Please use UnionPay overseas payment code |
| 1241 | Store does not exist or status incorrect |
| 1242 | Store not configured correctly |
| 1243 | Store has been disabled |
| 1250 | Transaction forbidden |
| 1251 | Store configuration error |
| 1252 | System error making order request |
| 1254 | Problem occurred, resolving issue |
| 1260 | Order already paid |
| 1261 | Order not paid |
| 1262 | Order already refunded |
| 1263 | Order already cancelled |
| 1264 | Order already closed |
| 1265 | Transaction cannot be refunded (11:30pm-0:30am) |
| 1266 | Transaction amount wrong |
| 1267 | Order information mismatch |
| 1268 | Order does not exist |
| 1269 | Insufficient unsettled balance for refund |
| 1270 | Currency does not support partial refund |
| 1271 | Transaction does not support partial refund |
| 1272 | Refund amount exceeds maximum refundable |
| 1294 | Transaction non-compliant, prohibited by bank |
| 1295 | Connection slow, waiting for network response |
| 1296 | Connection slow, try again later |
| 1297 | Banking system busy |
| 1298 | Connection slow, do not repeat payment if already paid |
| 2005 | Customer payment code incorrect or expired |
| 2011 | Transaction serial number repeats |

## Usage Examples

### Complete Payment Flow (Python)

```python
import os
import requests
import hashlib
import datetime
import time

# Load configuration from environment variables
APPCODE = os.getenv('QFPAY_APPCODE')
KEY = os.getenv('QFPAY_KEY')
MCHID = os.getenv('QFPAY_MCHID')
ENV = os.getenv('QFPAY_ENV', 'test')

# Environment URLs
ENV_URLS = {
    'prod': 'https://openapi-hk.qfapi.com',
    'test': 'https://test-openapi-hk.qfapi.com',
    'sandbox': 'https://openapi-int.qfapi.com'
}

BASE_URL = ENV_URLS.get(ENV, ENV_URLS['test'])

def generate_signature(params, key, sign_type='SHA256'):
    """Generate signature for QFPay API request"""
    keys = list(params.keys())
    keys.sort()
    query = []
    for k in keys:
        if k not in ('sign', 'sign_type') and (params[k] or params[k] == 0):
            query.append(f'{k}={params[k]}')
    
    data = '&'.join(query) + key
    
    if sign_type == 'SHA256':
        sha256 = hashlib.sha256()
        sha256.update(data.encode('utf-8'))
        return sha256.hexdigest().upper()
    else:
        md5 = hashlib.md5()
        md5.update(data.encode('utf-8'))
        return md5.hexdigest().upper()

def create_payment(amount, currency, pay_type, goods_name, notify_url=None):
    """Create a payment request"""
    params = {
        'txamt': str(amount),
        'txcurrcd': currency,
        'pay_type': pay_type,
        'out_trade_no': f"ORDER{int(time.time() * 10000)}",
        'txdtm': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'goods_name': goods_name
    }
    
    if MCHID:
        params['mchid'] = MCHID
    
    if notify_url:
        params['notify_url'] = notify_url
    
    signature = generate_signature(params, KEY)
    
    headers = {
        'X-QF-APPCODE': APPCODE,
        'X-QF-SIGN': signature,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(
        f'{BASE_URL}/trade/v1/payment',
        data=params,
        headers=headers
    )
    
    return response.json()

def query_transaction(out_trade_no):
    """Query transaction status"""
    params = {
        'out_trade_no': out_trade_no,
        'txdtm': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if MCHID:
        params['mchid'] = MCHID
    
    signature = generate_signature(params, KEY)
    
    headers = {
        'X-QF-APPCODE': APPCODE,
        'X-QF-SIGN': signature,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(
        f'{BASE_URL}/trade/v1/query',
        data=params,
        headers=headers
    )
    
    return response.json()

def refund_transaction(out_trade_no, txamt, qf_trade_no=None):
    """Process a refund"""
    params = {
        'out_trade_no': out_trade_no,
        'txamt': str(txamt),
        'txdtm': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if qf_trade_no:
        params['qf_trade_no'] = qf_trade_no
    
    if MCHID:
        params['mchid'] = MCHID
    
    signature = generate_signature(params, KEY)
    
    headers = {
        'X-QF-APPCODE': APPCODE,
        'X-QF-SIGN': signature,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(
        f'{BASE_URL}/trade/v1/refund',
        data=params,
        headers=headers
    )
    
    return response.json()

# Example usage
if __name__ == '__main__':
    # Create a payment
    result = create_payment(
        amount=100,  # $1.00 HKD
        currency='HKD',
        pay_type='800101',
        goods_name='Test Product'
    )
    print(f"Payment created: {result}")
    
    if result.get('respcd') == '0000':
        out_trade_no = result['data']['out_trade_no']
        
        # Query transaction
        query_result = query_transaction(out_trade_no)
        print(f"Transaction status: {query_result}")
```

### Environment Configuration with Multiple Merchants

```python
import os

# Configuration loader from environment
class QFPayConfig:
    def __init__(self, env='sandbox'):
        self.env = env
        self.appcode = os.getenv(f'QFPAY_{env.upper()}_APPCODE') or os.getenv('QFPAY_APPCODE')
        self.key = os.getenv(f'QFPAY_{env.upper()}_KEY') or os.getenv('QFPAY_KEY')
        self.mchid = os.getenv(f'QFPAY_{env.upper()}_MCHID') or os.getenv('QFPAY_MCHID')
        
    @property
    def base_url(self):
        urls = {
            'prod': 'https://openapi-hk.qfapi.com',
            'test': 'https://test-openapi-hk.qfapi.com',
            'sandbox': 'https://openapi-int.qfapi.com'
        }
        return urls.get(self.env, urls['sandbox'])

# Usage
config = QFPayConfig(env=os.getenv('QFPAY_ENV', 'sandbox'))
print(f"Using base URL: {config.base_url}")
```

## Important Notes

1. **Signature Security**: Never expose your `client_key` in frontend code or client-side applications. Always compute signatures on the server side.

2. **Order Number Uniqueness**: `out_trade_no` must be unique across all payment and refund requests under the same merchant account.

3. **Character Encoding**: All requests and responses use UTF-8 encoding.

4. **Timeout Handling**: For payment requests that don't return promptly, implement a polling mechanism to query transaction status.

5. **Async Notifications**: Configure `notify_url` to receive asynchronous payment completion notifications and verify notification signatures.

6. **Refund Limitations**: FPS (802001) payment type does not support refunds. Confirm business requirements before integration.

7. **Amount Format**: Amount is in cents. For example, 100 represents 1 HKD.

8. **Timezone**: The `txdtm` parameter uses the merchant's local timezone.

9. **Environment Variables**: Always load sensitive credentials from environment variables, never hardcode them in source files.

## Technical Support

For any integration issues, contact:

- **Email**: technical.support@qfpay.com
- **Documentation**: https://sdk.qfapi.com
- **Postman Collection**: https://sdk.qfapi.com/assets/files/qfpay_openapi_payment_request.postman_collection-c8de8c8fe69f3fcd5a7653d41c289a29.json

## See Also

- [QFPay Developer Center](https://sdk.qfapi.com)
- [Payment Integration Guides](https://sdk.qfapi.com/docs/category/integration-by-payment-type)
- [Checkout Integration](https://sdk.qfapi.com/docs/category/checkout-integration)
