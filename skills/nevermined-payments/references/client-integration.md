# Client-Side Integration (Subscriber Flow)

How to purchase plans, generate x402 tokens, and call payment-protected APIs as a subscriber.

## Overview

As a subscriber (consumer of a paid API/agent), you:
1. Order a payment plan
2. Check your credit balance
3. Generate an x402 access token
4. Send requests with the `payment-signature` header
5. Decode the settlement receipt from the `payment-response` header

## Order a Plan and Get a Token

### TypeScript

```typescript
import { Payments } from '@nevermined-io/payments'

const payments = Payments.getInstance({
  nvmApiKey: process.env.NVM_API_KEY!,
  environment: 'sandbox'
})

// Order the plan
await payments.plans.orderPlan(PLAN_ID)

// Check balance
const balance = await payments.plans.getPlanBalance(PLAN_ID)
console.log(`Credits remaining: ${balance}`)

// Generate x402 access token
const { accessToken } = await payments.x402.getX402AccessToken(PLAN_ID, AGENT_ID)
```

### Python

```python
import os
from payments_py import Payments, PaymentOptions

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=os.environ["NVM_API_KEY"], environment="sandbox")
)

# Order the plan
payments.plans.order_plan(plan_id)

# Check balance
balance = payments.plans.get_plan_balance(plan_id)
print(f"Credits remaining: {balance}")

# Generate x402 access token
token_res = payments.x402.get_x402_access_token(plan_id, agent_id)
access_token = token_res["accessToken"]
```

## Call a Protected HTTP API

### TypeScript

```typescript
import { Payments } from '@nevermined-io/payments'
import { X402_HEADERS } from '@nevermined-io/payments/express'

const payments = Payments.getInstance({
  nvmApiKey: process.env.NVM_API_KEY!,
  environment: 'sandbox'
})

async function callProtectedAPI() {
  const SERVER_URL = 'http://localhost:3000'

  // Step 1: Request without token → 402
  const response1 = await fetch(`${SERVER_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: 'What is 2+2?' })
  })

  if (response1.status === 402) {
    // Step 2: Decode payment requirements
    const paymentRequired = JSON.parse(
      Buffer.from(
        response1.headers.get(X402_HEADERS.PAYMENT_REQUIRED)!,
        'base64'
      ).toString()
    )

    const { planId, extra } = paymentRequired.accepts[0]
    const agentId = extra?.agentId

    // Step 3: Generate x402 token
    const { accessToken } = await payments.x402.getX402AccessToken(planId, agentId)

    // Step 4: Request with token → 200
    const response2 = await fetch(`${SERVER_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        [X402_HEADERS.PAYMENT_SIGNATURE]: accessToken
      },
      body: JSON.stringify({ query: 'What is 2+2?' })
    })

    const data = await response2.json()
    console.log('Response:', data.response)

    // Step 5: Decode settlement receipt
    const settlement = JSON.parse(
      Buffer.from(
        response2.headers.get(X402_HEADERS.PAYMENT_RESPONSE)!,
        'base64'
      ).toString()
    )
    console.log('Credits used:', settlement.creditsRedeemed)
  }
}
```

### Python

```python
import os
import base64
import json
import httpx
from payments_py import Payments, PaymentOptions

payments = Payments.get_instance(
    PaymentOptions(
        nvm_api_key=os.environ["NVM_API_KEY"],
        environment=os.environ.get("NVM_ENVIRONMENT", "sandbox")
    )
)

def call_protected_api():
    SERVER_URL = "http://localhost:3000"

    with httpx.Client(timeout=60.0) as client:
        # Step 1: Request without token → 402
        response1 = client.post(
            f"{SERVER_URL}/ask",
            json={"query": "What is 2+2?"}
        )

        if response1.status_code == 402:
            # Step 2: Decode payment requirements
            payment_required = json.loads(
                base64.b64decode(
                    response1.headers.get("payment-required")
                ).decode()
            )

            plan_id = payment_required["accepts"][0]["planId"]
            agent_id = payment_required["accepts"][0].get("extra", {}).get("agentId")

            # Step 3: Generate x402 token
            token_result = payments.x402.get_x402_access_token(plan_id, agent_id)
            access_token = token_result["accessToken"]

            # Step 4: Request with token → 200
            response2 = client.post(
                f"{SERVER_URL}/ask",
                headers={"payment-signature": access_token},
                json={"query": "What is 2+2?"}
            )

            data = response2.json()
            print(f"Response: {data['response']}")

            # Step 5: Decode settlement receipt
            settlement = json.loads(
                base64.b64decode(
                    response2.headers.get("payment-response")
                ).decode()
            )
            print(f"Credits used: {settlement.get('creditsRedeemed')}")

if __name__ == "__main__":
    call_protected_api()
```

## Connect to a Protected MCP Server

### TypeScript

```typescript
import { Client } from "@modelcontextprotocol/sdk/client"
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp"

const { accessToken } = await payments.x402.getX402AccessToken(planId, agentId)

const transport = new StreamableHTTPClientTransport(
  new URL("http://localhost:3000/mcp"),
  {
    requestInit: {
      headers: { 'payment-signature': accessToken }
    }
  }
)

const client = new Client({ name: "my-client" })
await client.connect(transport)

const result = await client.callTool({
  name: "weather.today",
  arguments: { city: "Madrid" }
})
```

## Call a Protected Strands Agent

### Python

```python
from payments_py.x402.strands import extract_payment_required
from agent import agent, payments

# Step 1: Call without token — triggers PaymentRequired
result = agent("Analyze sales trends")

# Step 2: Extract payment requirements
payment_required = extract_payment_required(agent.messages)

if payment_required:
    chosen_plan = payment_required["accepts"][0]
    plan_id = chosen_plan["planId"]
    agent_id = (chosen_plan.get("extra") or {}).get("agentId")

    # Step 3: Get token
    token_response = payments.x402.get_x402_access_token(plan_id, agent_id)
    access_token = token_response["accessToken"]

    # Step 4: Retry with token
    state = {"payment_token": access_token}
    result = agent("Analyze sales trends", invocation_state=state)
```

## Environment Variables

```bash
NVM_API_KEY=nvm:your-subscriber-api-key
NVM_ENVIRONMENT=sandbox
```
