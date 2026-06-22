---
name: nevermined-payments
description: >
  Integrates Nevermined payment infrastructure into AI agents, MCP servers,
  Google A2A agents, and REST APIs. Handles x402 protocol, credit billing,
  payment plans, and SDK integration for TypeScript (@nevermined-io/payments)
  and Python (payments-py).
---

# Nevermined Payments Integration

## Overview

Nevermined provides financial rails for AI agents — real-time monetization, access control, and payments. This skill gives you everything needed to:

- Protect API endpoints with the **x402 payment protocol**
- Charge per-request using **credit-based billing**
- Integrate with **Express.js**, **FastAPI**, **Strands agents**, **MCP servers**, or **Google A2A agents**
- Support **subscriber-side** flows (purchase plans, generate tokens, call protected APIs)
- Enable **agent-to-agent** payments via the Google A2A protocol

The x402 protocol uses HTTP 402 responses to advertise payment requirements. Clients acquire an access token and retry the request. The server verifies permissions, executes the workload, then settles (burns credits).

## Quick Start Checklist

1. **Get an API key** at [nevermined.app](https://nevermined.app) → Settings → API Keys
2. **Install the SDK** (`npm install @nevermined-io/payments` or `pip install payments-py`)
3. **Register your agent and plan** (via the App UI or programmatically — see `references/payment-plans.md`)
4. **Add payment protection** to your routes/tools (see framework-specific references below)
5. **Test** — call without token (expect 402), then with token (expect 200)

## Environment Setup

| Variable | Required | Description |
|---|---|---|
| `NVM_API_KEY` | Yes | Your Nevermined API key (get it at [nevermined.app](https://nevermined.app) → Settings → API Keys) |
| `NVM_ENVIRONMENT` | Yes | `sandbox` for testing, `live` for production |
| `NVM_PLAN_ID` | Yes | The plan ID from registration |
| `NVM_AGENT_ID` | Sometimes | Required for MCP servers and plans with multiple agents |
| `BUILDER_ADDRESS` | For registration | Wallet address to receive payments |

### `.env` Template

```bash
# Required
NVM_API_KEY=your-api-key-here
NVM_ENVIRONMENT=sandbox
NVM_PLAN_ID=your-plan-id-here

# Required for MCP servers or multi-agent plans
NVM_AGENT_ID=your-agent-id-here

# Required for registration
BUILDER_ADDRESS=0xYourWalletAddress
```

### Prerequisites

- **TypeScript/Express.js**: Node.js 18+. Your `package.json` must include `"type": "module"` for the `@nevermined-io/payments/express` subpath import to work.
- **Python/FastAPI**: Python 3.9+. Install with `pip install payments-py[fastapi]` — the `[fastapi]` extra is required for the middleware.

### TypeScript

```bash
npm install @nevermined-io/payments
```

```typescript
import { Payments } from '@nevermined-io/payments'

const payments = Payments.getInstance({
  nvmApiKey: process.env.NVM_API_KEY!,
  environment: 'sandbox'
})
```

### Python

```bash
pip install payments-py
```

```python
import os
from payments_py import Payments, PaymentOptions

payments = Payments.get_instance(
    PaymentOptions(
        nvm_api_key=os.environ["NVM_API_KEY"],
        environment="sandbox"
    )
)
```

## Core Workflow (All Integrations)

Every Nevermined payment integration follows this 5-step pattern:

1. **Client sends request** without a payment token
2. **Server returns 402** with `payment-required` header (base64-encoded JSON with plan info)
3. **Client acquires x402 token** via `payments.x402.getX402AccessToken(planId, agentId)`
4. **Client retries** with `payment-signature` header containing the token
5. **Server verifies → executes → settles** (burns credits), returns response with `payment-response` header

## Framework Decision Tree

Choose the integration that matches your stack:

| Framework | Language | Reference | Key Import |
|---|---|---|---|
| **Express.js** | TypeScript/JS | `references/express-integration.md` | `paymentMiddleware` from `@nevermined-io/payments/express` |
| **FastAPI** | Python | `references/fastapi-integration.md` | `PaymentMiddleware` from `payments_py.x402.fastapi` |
| **Strands Agent** | Python | `references/strands-integration.md` | `@requires_payment` from `payments_py.x402.strands` |
| **MCP Server** | TypeScript | `references/mcp-paywall.md` | `payments.mcp.start()` / `payments.mcp.registerTool()` |
| **Google A2A** | TS / Python | `references/a2a-integration.md` | `payments.a2a.start()` / `payments.a2a.buildPaymentAgentCard()` |
| **Any HTTP** | Any | `references/x402-protocol.md` | Manual verify/settle via facilitator API |
| **Client-side** | TS / Python | `references/client-integration.md` | `payments.x402.getX402AccessToken()` |

## SDK Quick Reference

### TypeScript (`@nevermined-io/payments`)

```typescript
// Initialize
const payments = Payments.getInstance({ nvmApiKey, environment })

// Register agent + plan
const { agentId, planId } = await payments.agents.registerAgentAndPlan(
  agentMetadata, agentApi, planMetadata, priceConfig, creditsConfig
)

// Subscriber: order plan and get token
await payments.plans.orderPlan(planId)
const balance = await payments.plans.getPlanBalance(planId)
const { accessToken } = await payments.x402.getX402AccessToken(planId, agentId)

// Server: verify and settle
const verification = await payments.facilitator.verifyPermissions({
  paymentRequired, x402AccessToken: token, maxAmount: BigInt(credits)
})
const settlement = await payments.facilitator.settlePermissions({
  paymentRequired, x402AccessToken: token, maxAmount: BigInt(creditsUsed)
})

// Helpers
import { buildPaymentRequired } from '@nevermined-io/payments'
import { paymentMiddleware, X402_HEADERS } from '@nevermined-io/payments/express'

// MCP server
payments.mcp.registerTool(name, config, handler, { credits: 5n })
const { info, stop } = await payments.mcp.start({ port, agentId, serverName })

// A2A server
const agentCard = payments.a2a.buildPaymentAgentCard(baseCard, { paymentType, credits, planId, agentId })
const server = await payments.a2a.start({ port, basePath: '/a2a/', agentCard, executor })
// A2A client
const client = payments.a2a.getClient({ agentBaseUrl, agentId, planId })
await client.sendMessage("Hello", accessToken)
```

### Python (`payments-py`)

```python
# Initialize
payments = Payments.get_instance(PaymentOptions(nvm_api_key=key, environment="sandbox"))

# Register agent + plan
result = payments.agents.register_agent_and_plan(
    agent_metadata, agent_api, plan_metadata, price_config, credits_config
)

# Subscriber: order plan and get token
payments.plans.order_plan(plan_id)
balance = payments.plans.get_plan_balance(plan_id)
token_res = payments.x402.get_x402_access_token(plan_id, agent_id)

# Server: verify and settle
verification = payments.facilitator.verify_permissions(
    payment_required=pr, x402_access_token=token, max_amount=str(credits)
)
settlement = payments.facilitator.settle_permissions(
    payment_required=pr, x402_access_token=token, max_amount=str(credits_used)
)

# Helpers
from payments_py.x402.helpers import build_payment_required
from payments_py.x402.fastapi import PaymentMiddleware
from payments_py.x402.strands import requires_payment

# A2A server
from payments_py.a2a.agent_card import build_payment_agent_card
from payments_py.a2a.server import PaymentsA2AServer
agent_card = build_payment_agent_card(base_card, { ... })
server = PaymentsA2AServer.start(agent_card=agent_card, executor=executor, payments_service=payments, port=3005)
# A2A client
client = payments.a2a.get_client(agent_base_url=url, agent_id=agent_id, plan_id=plan_id)
```

## x402 Payment Headers

All x402 v2 integrations use these three HTTP headers:

| Header | Direction | Description |
|---|---|---|
| `payment-signature` | Client → Server | x402 access token |
| `payment-required` | Server → Client (402) | Base64-encoded JSON with plan requirements |
| `payment-response` | Server → Client (200) | Base64-encoded JSON settlement receipt |

The `payment-required` payload structure:
```json
{
  "x402Version": 2,
  "accepts": [{
    "scheme": "nvm:erc4337",
    "network": "eip155:84532",
    "planId": "<plan-id>",
    "extra": { "agentId": "<agent-id>" }
  }]
}
```

## Payment Plan Types

Nevermined supports several plan types:

- **Credits-based**: prepaid balance, deducted per request (most common for APIs)
- **Time-based**: access for a fixed duration (e.g., 30 days unlimited)
- **Pay-as-you-go (PAYG)**: settle in USDC per request, no credit balance
- **Trial**: free limited access, one-time claim per user
- **Hybrid**: combine credits with time expiry

See `references/payment-plans.md` for plan registration code.

## Common Patterns

### Express.js — Fixed credits per route

```typescript
import { paymentMiddleware } from '@nevermined-io/payments/express'

app.use(paymentMiddleware(payments, {
  'POST /ask': { planId: PLAN_ID, credits: 1 },
  'POST /generate': { planId: PLAN_ID, credits: 5 }
}))
```

### FastAPI — Fixed credits per route

```python
from payments_py.x402.fastapi import PaymentMiddleware

app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={
        "POST /ask": {"plan_id": PLAN_ID, "credits": 1},
        "POST /generate": {"plan_id": PLAN_ID, "credits": 5}
    }
)
```

### Express.js — Dynamic credits based on response

```typescript
paymentMiddleware(payments, {
  'POST /generate': {
    planId: PLAN_ID,
    credits: (req, res) => {
      const tokens = res.locals.tokenCount || 100
      return Math.ceil(tokens / 100)
    }
  }
})
```

### FastAPI — Dynamic credits based on request

```python
async def calculate_credits(request: Request) -> int:
    body = await request.json()
    max_tokens = body.get("max_tokens", 100)
    return max(1, max_tokens // 100)

app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={"POST /generate": {"plan_id": PLAN_ID, "credits": calculate_credits}}
)
```

### MCP Server — Register tool with paywall

```typescript
payments.mcp.registerTool(
  "weather.today",
  { title: "Today's Weather", inputSchema: z.object({ city: z.string() }) },
  async (args, extra, context) => ({
    content: [{ type: "text", text: `Weather in ${args.city}: Sunny, 25C` }]
  }),
  { credits: 5n }
)

const { info, stop } = await payments.mcp.start({
  port: 3000,
  agentId: process.env.NVM_AGENT_ID!,
  serverName: "my-server"
})
```

### Strands Agent — Decorator-based payment

```python
from strands import Agent, tool
from payments_py.x402.strands import requires_payment

@tool(context=True)
@requires_payment(payments=payments, plan_id=PLAN_ID, credits=1)
def analyze_data(query: str, tool_context=None) -> dict:
    return {"status": "success", "content": [{"text": f"Analysis: {query}"}]}

agent = Agent(tools=[analyze_data])
```

### Google A2A — Agent server with payment extension

#### TypeScript

```typescript
const agentCard = payments.a2a.buildPaymentAgentCard(baseAgentCard, {
  paymentType: "dynamic",
  credits: 1,
  planId: process.env.NVM_PLAN_ID!,
  agentId: process.env.NVM_AGENT_ID!,
})

const server = await payments.a2a.start({
  port: 3005,
  basePath: '/a2a/',
  agentCard,
  executor: new MyExecutor(),
})
```

#### Python

```python
from payments_py.a2a.agent_card import build_payment_agent_card
from payments_py.a2a.server import PaymentsA2AServer

agent_card = build_payment_agent_card(base_agent_card, {
    "paymentType": "dynamic",
    "credits": 1,
    "planId": os.environ["NVM_PLAN_ID"],
    "agentId": os.environ["NVM_AGENT_ID"],
})

server = PaymentsA2AServer.start(
    agent_card=agent_card,
    executor=MyExecutor(),
    payments_service=payments,
    port=3005,
    base_path="/a2a/",
)
```

### Google A2A — Client sending a paid task

```typescript
const client = payments.a2a.getClient({
  agentBaseUrl: 'http://localhost:3005/a2a/',
  agentId: AGENT_ID,
  planId: PLAN_ID,
})

const { accessToken } = await payments.x402.getX402AccessToken(PLAN_ID, AGENT_ID)
const response = await client.sendMessage("Analyze this data", accessToken)
```

## Gathering Developer Information Upfront

When a developer asks you to integrate Nevermined payments, gather ALL required information in a single question before generating code. This avoids multiple back-and-forth interactions.

**Ask the developer once for:**

1. **Framework**: Express.js, FastAPI, MCP server, Strands agent, Google A2A, or generic HTTP?
2. **Routes to protect**: Which endpoints need payment protection and how many credits each? (e.g., `POST /chat = 1 credit, POST /generate = 5 credits`)
3. **Pricing model**: Fixed credits per request, or dynamic pricing based on request/response parameters?
4. **Nevermined API Key**: Do they already have an `NVM_API_KEY`? If not, direct them to [nevermined.app](https://nevermined.app) → Settings → API Keys
5. **Plan ID**: Do they already have a `NVM_PLAN_ID`? If not, do they need a registration script too?
6. **Environment**: `sandbox` (testing) or `live` (production)?

**If they need plan registration, also ask:**

7. **Plan name and description**: e.g., "Starter Plan — 100 API requests"
8. **Pricing**: How much in USDC? (e.g., 10 USDC for 100 credits)
9. **Credits per plan**: Total credits included (e.g., 100)
10. **Builder wallet address** (`BUILDER_ADDRESS`): The wallet that receives payments

**Example combined prompt to offer the developer:**

> I need to set up Nevermined payments. Here's my info:
> - Framework: Express.js
> - Routes: POST /chat (1 credit), POST /summarize (3 credits)
> - I need a registration script too
> - Plan: "Starter Plan", 100 credits for 10 USDC
> - Environment: sandbox
> - My API key is in the NVM_API_KEY env var
> - My wallet: 0x1234...

With this information, generate both the registration script and the payment-protected server in a single response.

## Agent and Plan Registration

### Using the SDK (Recommended)

Register your agent and plan programmatically — see `references/payment-plans.md` for complete code.

```typescript
// TypeScript
const { agentId, planId } = await payments.agents.registerAgentAndPlan(
  { name: 'My Agent', description: 'AI service', tags: ['ai'], dateCreated: new Date() },
  { endpoints: [{ POST: 'https://your-api.com/query' }] },
  { name: 'Starter Plan', description: '100 requests for $10', dateCreated: new Date() },
  payments.plans.getERC20PriceConfig(10_000_000n, USDC_ADDRESS, process.env.BUILDER_ADDRESS!),
  payments.plans.getFixedCreditsConfig(100n, 1n)
)
```

```python
# Python
result = payments.agents.register_agent_and_plan(
    agent_metadata={'name': 'My Agent', 'description': 'AI service', 'tags': ['ai']},
    agent_api={'endpoints': [{'POST': 'https://your-api.com/query'}]},
    plan_metadata={'name': 'Starter Plan', 'description': '100 requests for $10'},
    price_config=get_erc20_price_config(10_000_000, USDC_ADDRESS, os.environ['BUILDER_ADDRESS']),
    credits_config=get_fixed_credits_config(100, 1)
)
```

### Using the Nevermined App (No-Code)

1. Go to [nevermined.app](https://nevermined.app) and sign in
2. Click "My agents" → register a new agent with metadata and endpoints
3. Create a payment plan: set pricing, credits, and duration
4. Link the plan to your agent and publish
5. Copy the `agentId` and `planId` for your `.env` file

### Using the CLI

```bash
# 1. Install CLI
npm install -g @nevermined-io/cli

# 2. Configure (use sandbox for testing)
nvm config init --api-key "$NVM_API_KEY" --environment sandbox

# 3. Register agent and plan together
nvm agents register-agent-and-plan \
  --agent-metadata '{"name":"My Agent","description":"AI service"}' \
  --agent-api '{"endpoints":[{"POST":"https://your-api.com/query"}]}' \
  --plan-metadata '{"name":"Starter Plan","description":"100 requests"}' \
  --price-config '{"tokenAddress":"0x036CbD53842c5426634e7929541eC2318f3dCF7e","price":10000000,"amountOfCredits":100}' \
  --credits-config '{"minCreditsRequired":1,"minCreditsToCharge":1,"maxCreditsToCharge":10}'

# 4. List your plans
nvm plans get-plans

# 5. As a subscriber: order a plan and get an x402 token
nvm plans order-plan $PLAN_ID
nvm x402token get-x402-access-token $PLAN_ID --agent-id $AGENT_ID

# 6. Test against your running server
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -H "payment-signature: $TOKEN" \
  -d '{"message": "Hello"}'
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| HTTP 402 returned | No `payment-signature` header or invalid/expired token | Generate a fresh token via `getX402AccessToken` |
| MCP error `-32003` | Payment Required — no token, invalid token, or insufficient credits | Check subscriber has purchased plan and has credits remaining |
| MCP error `-32002` | Server misconfiguration | Verify `NVM_API_KEY`, `NVM_PLAN_ID`, and `NVM_AGENT_ID` are set correctly |
| `verification.isValid` is false | Token expired, wrong plan, or insufficient credits | Re-order the plan or generate a new token |
| Credits not deducting | Settlement not called after request | Ensure you call `settlePermissions` after processing (middleware does this automatically) |
| `payment-required` header missing | Server not returning 402 properly | Use `buildPaymentRequired()` helper or framework middleware |

## Additional Resources

- **Documentation**: [nevermined.ai/docs](https://nevermined.ai/docs)
- **Nevermined App**: [nevermined.app](https://nevermined.app) — register agents, create plans, manage subscriptions
- **MCP Search Server**: `https://docs.nevermined.app/mcp` — search Nevermined docs from any MCP client
- **Tutorials**: [github.com/nevermined-io/tutorials](https://github.com/nevermined-io/tutorials)
- **Discord**: [discord.com/invite/GZju2qScKq](https://discord.com/invite/GZju2qScKq)
- **TypeScript SDK**: `@nevermined-io/payments` on npm
- **Python SDK**: `payments-py` on PyPI
