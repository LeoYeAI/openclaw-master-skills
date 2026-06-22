# Express.js Integration

Add x402 payment protection to Express.js APIs using `paymentMiddleware` from `@nevermined-io/payments/express`.

## Installation

```bash
npm install @nevermined-io/payments express
```

## Quick Start

```typescript
import express from 'express'
import { Payments } from '@nevermined-io/payments'
import { paymentMiddleware } from '@nevermined-io/payments/express'

const app = express()
app.use(express.json())

const payments = Payments.getInstance({
  nvmApiKey: process.env.NVM_API_KEY!,
  environment: process.env.NVM_ENVIRONMENT === 'live' ? 'live' : 'sandbox'
})

// Protect routes with one line
app.use(
  paymentMiddleware(payments, {
    'POST /ask': {
      planId: process.env.NVM_PLAN_ID!,
      credits: 1
    }
  })
)

// Route handler — no payment logic needed
app.post('/ask', async (req, res) => {
  const { query } = req.body
  const response = await generateAIResponse(query)
  res.json({ response })
})

app.listen(3000, () => console.log('Server running on http://localhost:3000'))
```

The middleware automatically:
- Returns `402` with `payment-required` header when no token is provided
- Verifies the x402 token via the Nevermined facilitator
- Burns credits after request completion
- Returns `payment-response` header with settlement receipt

## Route Configuration

### Fixed Credits

```typescript
paymentMiddleware(payments, {
  'POST /ask': { planId: PLAN_ID, credits: 1 },
  'POST /generate': { planId: PLAN_ID, credits: 5 }
})
```

### Dynamic Credits

Calculate credits based on request/response:

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

### Path Parameters

```typescript
paymentMiddleware(payments, {
  'GET /users/:id': { planId: PLAN_ID, credits: 1 },
  'POST /agents/:agentId/task': { planId: PLAN_ID, credits: 2 }
})
```

### With Agent ID

```typescript
paymentMiddleware(payments, {
  'POST /task': {
    planId: PLAN_ID,
    agentId: AGENT_ID,  // Required for plans with multiple agents
    credits: 5
  }
})
```

## Middleware Options

```typescript
paymentMiddleware(payments, routes, {
  tokenHeader: 'payment-signature',

  onBeforeVerify: (req, paymentRequired) => {
    console.log(`Verifying payment for ${req.path}`)
  },

  onAfterVerify: (req, verification) => {
    const agentRequest = verification.agentRequest
    if (agentRequest) {
      console.log(`Agent: ${agentRequest.agentName}`)
    }
  },

  onAfterSettle: (req, creditsUsed, settlement) => {
    console.log(`Settled ${creditsUsed} credits, tx: ${settlement.txHash}`)
  },

  onPaymentError: (error, req, res) => {
    res.status(402).json({ error: error.message })
  }
})
```

## Complete Example

```typescript
import express from 'express'
import OpenAI from 'openai'
import { Payments } from '@nevermined-io/payments'
import { paymentMiddleware } from '@nevermined-io/payments/express'

const app = express()
app.use(express.json())

const payments = Payments.getInstance({
  nvmApiKey: process.env.NVM_API_KEY!,
  environment: 'sandbox'
})

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })

app.use(
  paymentMiddleware(payments, {
    'POST /ask': {
      planId: process.env.NVM_PLAN_ID!,
      credits: 1
    }
  }, {
    onBeforeVerify: (req) => {
      console.log(`[Payment] Verifying request to ${req.path}`)
    },
    onAfterSettle: (req, credits) => {
      console.log(`[Payment] Settled ${credits} credits`)
    }
  })
)

app.post('/ask', async (req, res) => {
  const { query } = req.body
  const completion = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [{ role: 'user', content: query }]
  })
  res.json({ response: completion.choices[0]?.message?.content })
})

app.get('/health', (req, res) => {
  res.json({ status: 'ok' })
})

const PORT = process.env.PORT || 3000
app.listen(PORT, () => {
  console.log(`Agent running on http://localhost:${PORT}`)
})
```

## Environment Variables

```bash
NVM_API_KEY=nvm:your-api-key
NVM_ENVIRONMENT=sandbox
NVM_PLAN_ID=your-plan-id
OPENAI_API_KEY=sk-your-openai-api-key
PORT=3000
```

## Tutorial

Complete working example: [github.com/nevermined-io/tutorials/tree/main/http-simple-agent](https://github.com/nevermined-io/tutorials/tree/main/http-simple-agent)
