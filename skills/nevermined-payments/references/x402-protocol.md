# x402 Protocol — Generic HTTP Integration

The x402 protocol defines a payment-enforced HTTP 402 mechanism for any HTTP server or framework. Use this when Express.js or FastAPI middleware isn't available.

## The x402 Payment Flow

```
Client → Server:  Request (no payment proof)
Server → Client:  402 Payment Required + payment-required header
Client:           Build x402 payment proof via SDK
Client → Server:  Retry request + payment-signature header
Server → Facilitator:  Verify/settle via SDK
Server → Client:  200 OK + payment-response header
```

## x402 Headers

| Header | Direction | Description |
|---|---|---|
| `payment-signature` | Client → Server | x402 access token |
| `payment-required` | Server → Client (402) | Base64-encoded payment requirements |
| `payment-response` | Server → Client (200) | Base64-encoded settlement receipt |

## Implementation Steps

### Step 1: Extract the x402 token

Read the `payment-signature` header from the request.

### Step 2: Return 402 if token is missing

#### TypeScript

```typescript
import { Payments, buildPaymentRequired } from '@nevermined-io/payments'

const PLAN_ID = process.env.NVM_PLAN_ID!
const AGENT_ID = process.env.NVM_AGENT_ID

const paymentRequired = buildPaymentRequired(PLAN_ID, {
  endpoint: req.path,
  agentId: AGENT_ID,
  httpVerb: req.method
})

const token = req.headers['payment-signature']
if (!token) {
  const paymentRequiredBase64 = Buffer.from(
    JSON.stringify(paymentRequired)
  ).toString('base64')

  return res
    .status(402)
    .setHeader('payment-required', paymentRequiredBase64)
    .json({ error: 'Payment Required', message: 'Missing x402 access token' })
}
```

#### Python

```python
import base64
import json
from payments_py.x402.helpers import build_payment_required

PLAN_ID = os.environ["NVM_PLAN_ID"]
AGENT_ID = os.environ.get("NVM_AGENT_ID")

payment_required = build_payment_required(
    plan_id=PLAN_ID,
    endpoint=request.path,
    agent_id=AGENT_ID,
    http_verb=request.method
)

token = request.headers.get("payment-signature")
if not token:
    payment_required_json = payment_required.model_dump_json(by_alias=True)
    payment_required_base64 = base64.b64encode(
        payment_required_json.encode()
    ).decode()

    return JSONResponse(
        status_code=402,
        content={"error": "Payment Required", "message": "Missing x402 access token"},
        headers={"payment-required": payment_required_base64}
    )
```

### Step 3: Verify permissions with the Facilitator

#### TypeScript

```typescript
const payments = Payments.getInstance({
  nvmApiKey: process.env.NVM_API_KEY!,
  environment: 'sandbox'
})

const verification = await payments.facilitator.verifyPermissions({
  paymentRequired,
  x402AccessToken: token,
  maxAmount: BigInt(creditsRequired)
})

if (!verification.isValid) {
  const paymentRequiredBase64 = Buffer.from(
    JSON.stringify(paymentRequired)
  ).toString('base64')

  return res
    .status(402)
    .setHeader('payment-required', paymentRequiredBase64)
    .json({ error: 'Payment Required', message: verification.invalidReason })
}
```

#### Python

```python
from payments_py import Payments, PaymentOptions

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=os.environ["NVM_API_KEY"], environment="sandbox")
)

verification = payments.facilitator.verify_permissions(
    payment_required=payment_required,
    x402_access_token=token,
    max_amount=str(credits_required)
)

if not verification.is_valid:
    payment_required_json = payment_required.model_dump_json(by_alias=True)
    payment_required_base64 = base64.b64encode(
        payment_required_json.encode()
    ).decode()

    return JSONResponse(
        status_code=402,
        content={"error": "Payment Required", "message": verification.invalid_reason},
        headers={"payment-required": payment_required_base64}
    )
```

### Step 4: Process the request

Execute your business logic after verification passes.

### Step 5: Settle (burn credits) after successful response

#### TypeScript

```typescript
const settlement = await payments.facilitator.settlePermissions({
  paymentRequired,
  x402AccessToken: token,
  maxAmount: BigInt(creditsUsed)
})

const settlementBase64 = Buffer.from(JSON.stringify(settlement)).toString('base64')

return res
  .setHeader('payment-response', settlementBase64)
  .json({ result: yourResponseData })
```

#### Python

```python
settlement = payments.facilitator.settle_permissions(
    payment_required=payment_required,
    x402_access_token=token,
    max_amount=str(credits_used)
)

settlement_json = settlement.model_dump_json(by_alias=True)
settlement_base64 = base64.b64encode(settlement_json.encode()).decode()

return JSONResponse(
    content={"result": your_response_data},
    headers={"payment-response": settlement_base64}
)
```

## HTTP Response Codes

| Code | Meaning | When to Use |
|---|---|---|
| `200` | Success | Valid payment proof, request processed |
| `402` | Payment Required | Missing/invalid payment proof, insufficient credits |
| `500` | Server Error | Validation system failure |

## PaymentRequired Object Structure

```json
{
  "x402Version": 2,
  "error": "Payment required to access resource",
  "resource": {
    "url": "/api/endpoint",
    "description": "AI agent task execution",
    "mimeType": "application/json"
  },
  "accepts": [{
    "scheme": "nvm:erc4337",
    "network": "eip155:84532",
    "planId": "<plan-id>",
    "extra": {
      "version": "1",
      "agentId": "<agent-id>"
    }
  }]
}
```

## Using Framework Middleware (Recommended)

For Express.js and FastAPI, use the built-in middleware instead of manual integration:

### Express.js

```typescript
import { paymentMiddleware } from '@nevermined-io/payments/express'

app.use(paymentMiddleware(payments, {
  'POST /ask': { planId: PLAN_ID, credits: 1 }
}))
```

### FastAPI

```python
from payments_py.x402.fastapi import PaymentMiddleware

app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={"POST /ask": {"plan_id": PLAN_ID, "credits": 1}}
)
```

## Best Practices

- **Cache validation results** briefly (5–30 seconds) for high-traffic endpoints
- **Set reasonable timeouts** (5–10 seconds) for validation calls
- **Log payment events** — token hash, validation result, credits consumed, timestamp
- **Return helpful 402 responses** — always include plan information
- **Never log full tokens** — hash them if identification is needed
- **Use HTTPS** — tokens should only travel over encrypted connections
- **Validate on server** — never trust client-side validation
