# Google A2A Integration

Integrate Nevermined payments with [Google A2A (Agent-to-Agent)](https://a2a-protocol.org/) to enable multi-agent systems to authorize and charge per request between agents.

## Features

- **Agent Card with payment extension**: publish at `/.well-known/agent.json`
- **Bearer Token Authentication**: tokens extracted from HTTP headers (`payment-signature`)
- **Credits Validation**: verify sufficient credits before executing a task
- **Credits Burning/Redemption**: burn credits specified in `metadata.creditsUsed` after execution
- **Streaming**: supports `message/stream` and `tasks/resubscribe`
- **Push Notifications**: standard A2A push notification flow
- **Async Task Handling**: intermediate and final state events, compatible with polling and streaming

## Installation

### TypeScript

```bash
npm install @nevermined-io/payments
```

### Python

```bash
pip install payments-py
```

## A2A Server

### Build the Payment Agent Card

Add a Nevermined payment extension to your A2A agent card to advertise that your agent charges for requests.

#### TypeScript

```typescript
import { Payments } from "@nevermined-io/payments"

const payments = Payments.getInstance({
  nvmApiKey: process.env.NVM_API_KEY!,
  environment: 'sandbox',
})

const baseAgentCard = {
  name: 'My A2A Server',
  description: 'A2A agent that requires payment',
  capabilities: {
    streaming: true,
    pushNotifications: true,
    stateTransitionHistory: true,
  },
  defaultInputModes: ['text'],
  defaultOutputModes: ['text'],
  skills: [],
  url: 'http://localhost:3005/a2a/',
  version: '1.0.0',
}

const agentCard = payments.a2a.buildPaymentAgentCard(baseAgentCard, {
  paymentType: "dynamic",
  credits: 1,
  planId: process.env.NVM_PLAN_ID!,
  agentId: process.env.NVM_AGENT_ID!,
})
```

#### Python

```python
from payments_py import Payments, PaymentOptions
from payments_py.a2a.agent_card import build_payment_agent_card

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=os.environ["NVM_API_KEY"], environment="sandbox")
)

base_agent_card = {
    "name": "My A2A Agent",
    "description": "A2A agent that requires payment",
    "capabilities": {
        "streaming": True,
        "pushNotifications": True,
        "stateTransitionHistory": True,
    },
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "skills": [],
    "url": "https://your-agent.example.com/a2a/",
    "version": "1.0.0",
}

agent_card = build_payment_agent_card(base_agent_card, {
    "paymentType": "dynamic",
    "credits": 1,
    "costDescription": "Dynamic cost per request",
    "planId": os.environ["NVM_PLAN_ID"],
    "agentId": os.environ["NVM_AGENT_ID"],
})
```

### Payment Extension JSON

The `buildPaymentAgentCard` helper adds this extension to your agent card:

```json
{
  "capabilities": {
    "extensions": [
      {
        "uri": "urn:nevermined:payment",
        "description": "Dynamic cost per request",
        "required": false,
        "params": {
          "paymentType": "dynamic",
          "credits": 1,
          "planId": "<planId>",
          "agentId": "<agentId>"
        }
      }
    ]
  }
}
```

Important: the `url` in the agent card must match the URL registered in Nevermined for the agent/plan.

### Start the A2A Server

#### TypeScript

```typescript
class Executor implements AgentExecutor {
  async handleTask(context, eventBus) {
    // Your business logic here
    // Returns { result: TaskHandlerResult, expectsMoreUpdates: boolean }
  }
  async cancelTask(taskId) { /* ... */ }

  async execute(requestContext, eventBus) {
    const { result, expectsMoreUpdates } = await this.handleTask(requestContext, eventBus)
    if (expectsMoreUpdates) return
    // Publish final status-update event with metadata.creditsUsed
  }
}

const serverResult = await payments.a2a.start({
  port: 3005,
  basePath: '/a2a/',
  agentCard: agentCard,
  executor: new Executor(),
})
```

#### Python

```python
from payments_py.a2a.server import PaymentsA2AServer

class MyExecutor:
    async def execute(self, ctx, event_queue):
        # Your business logic here
        event_queue.publish({
            "kind": "status-update",
            "taskId": ctx.taskId,
            "contextId": ctx.userMessage.get("contextId"),
            "status": {"state": "completed"},
            "metadata": {"creditsUsed": 1},
            "final": True,
        })
        event_queue.finished()

server = PaymentsA2AServer.start(
    agent_card=agent_card,
    executor=MyExecutor(),
    payments_service=payments,
    port=3005,
    base_path="/a2a/",
)
```

The final streaming event must include `metadata.creditsUsed` with the consumed cost. Nevermined validates and burns credits accordingly.

## A2A Client

### Initialize the Client

#### TypeScript

```typescript
const paymentsSubscriber = Payments.getInstance({
  nvmApiKey: process.env.NVM_API_KEY!,
  environment: 'sandbox',
})

const client = paymentsSubscriber.a2a.getClient({
  agentBaseUrl: 'http://localhost:3005/a2a/',
  agentId: process.env.NVM_AGENT_ID!,
  planId: process.env.NVM_PLAN_ID!,
})
```

#### Python

```python
payments_subscriber = Payments.get_instance(
    PaymentOptions(nvm_api_key=os.environ["NVM_API_KEY"], environment="sandbox")
)

client = payments_subscriber.a2a.get_client(
    agent_base_url="https://your-agent.example.com/a2a/",
    agent_id=os.environ["NVM_AGENT_ID"],
    plan_id=os.environ["NVM_PLAN_ID"],
)
```

### Send a Task

#### TypeScript

```typescript
// Purchase the plan
await paymentsSubscriber.plans.orderPlan(planId)

// Get the x402 access token
const { accessToken } = await paymentsSubscriber.x402.getX402AccessToken(planId, agentId)

// Send an A2A message
const response = await client.sendMessage("Hello, analyze this data!", accessToken)
const taskId = response?.result?.id
```

#### Python

```python
# Send a simple request
result = await client.send_message({
    "message": {
        "kind": "message",
        "role": "user",
        "messageId": "123",
        "parts": [{"kind": "text", "text": "Hello"}]
    }
})

# Stream events
async for event in client.send_message_stream({
    "message": {
        "kind": "message",
        "role": "user",
        "messageId": "124",
        "parts": [{"kind": "text", "text": "Stream this"}]
    }
}):
    if event.get("result", {}).get("final"):
        break
```

## Environment Variables

```bash
NVM_API_KEY=nvm:your-api-key
NVM_ENVIRONMENT=sandbox
NVM_PLAN_ID=your-plan-id
NVM_AGENT_ID=your-agent-id
```

## Tutorial

Complete working example: [github.com/nevermined-io/a2a-agent-client-sample](https://github.com/nevermined-io/a2a-agent-client-sample)
