# Payment Plans

How to register agents and create payment plans programmatically using the Nevermined SDK.

## Plan Types

| Type | Description | Use Case |
|---|---|---|
| **Credits-based** | Prepaid credits, deducted per request | Per-request API billing |
| **Time-based** | Access for a fixed duration | Monthly/yearly subscriptions |
| **Pay-as-you-go** | Settle in USDC per request | On-demand, no prepaid balance |
| **Trial** | Free limited access, one-time claim | Let users try your service |
| **Hybrid** | Credits with time expiry | e.g., 1000 credits valid for 30 days |

## Register Agent + Plan (Combined)

### TypeScript

```typescript
import { Payments } from '@nevermined-io/payments'

const USDC_ADDRESS = '0x036CbD53842c5426634e7929541eC2318f3dCF7e'

async function main() {
  const payments = Payments.getInstance({
    nvmApiKey: process.env.NVM_API_KEY!,
    environment: 'sandbox'
  })

  const { agentId, planId } = await payments.agents.registerAgentAndPlan(
    // Agent metadata
    {
      name: 'My AI Assistant',
      description: 'A paid AI service',
      tags: ['ai', 'payments'],
      dateCreated: new Date()
    },
    // Agent interface
    {
      endpoints: [{ POST: 'https://your-api.com/query' }]
    },
    // Plan metadata
    {
      name: 'Starter Plan',
      description: '100 requests for $10',
      dateCreated: new Date()
    },
    // Price: 10 USDC (6 decimals)
    payments.plans.getERC20PriceConfig(
      10_000_000n,
      USDC_ADDRESS,
      process.env.BUILDER_ADDRESS!
    ),
    // Credits: 100 requests, 1 credit each
    payments.plans.getFixedCreditsConfig(100n, 1n)
  )

  console.log(`Agent ID: ${agentId}`)
  console.log(`Plan ID: ${planId}`)
}

main().catch(console.error)
```

### Python

```python
import os
from payments_py import Payments, PaymentOptions
from payments_py.plans import get_erc20_price_config, get_fixed_credits_config

USDC_ADDRESS = '0x036CbD53842c5426634e7929541eC2318f3dCF7e'

def main():
    payments = Payments.get_instance(
        PaymentOptions(
            nvm_api_key=os.environ['NVM_API_KEY'],
            environment='sandbox'
        )
    )

    result = payments.agents.register_agent_and_plan(
        agent_metadata={
            'name': 'My AI Assistant',
            'description': 'A paid AI service',
            'tags': ['ai', 'payments']
        },
        agent_api={
            'endpoints': [{'POST': 'https://your-api.com/query'}]
        },
        plan_metadata={
            'name': 'Starter Plan',
            'description': '100 requests for $10'
        },
        price_config=get_erc20_price_config(
            10_000_000,
            USDC_ADDRESS,
            os.environ['BUILDER_ADDRESS']
        ),
        credits_config=get_fixed_credits_config(100, 1),
        access_limit='credits'
    )

    print(f"Agent ID: {result['agentId']}")
    print(f"Plan ID: {result['planId']}")

if __name__ == '__main__':
    main()
```

## Using the Nevermined App (No-Code)

You can also register agents and create plans through the [Nevermined App](https://nevermined.app) UI:

1. Go to [nevermined.app](https://nevermined.app) and sign in
2. Click "My agents" to register a new agent
3. Fill in metadata: name, description, tags
4. Register API endpoints (HTTP URLs for APIs, logical MCP URLs for MCP servers)
5. Create a payment plan: set pricing, credits, and duration
6. Link the plan to your agent and publish
7. Copy the `agentId` and `planId` for your integration

## Plan Configuration Details

### Credits Config

```typescript
// TypeScript
payments.plans.getFixedCreditsConfig(
  100n,  // Total credits in the plan
  1n     // Credits consumed per request
)
```

```python
# Python
get_fixed_credits_config(
    100,  # Total credits in the plan
    1     # Credits consumed per request
)
```

### Variable Credits (Dynamic Pricing)

When using dynamic credits (a function instead of fixed value), configure the plan with a price range:

- Enable "Want to set a price range per request?" in the App
- Set min and max price per request
- If your code calculates credits outside the range, it gets capped to the configured limits

### Price Config

```typescript
// ERC-20 token payment (USDC on Base Sepolia)
payments.plans.getERC20PriceConfig(
  10_000_000n,           // Price in token smallest unit (10 USDC = 10 * 10^6)
  USDC_ADDRESS,          // Token contract address
  process.env.BUILDER_ADDRESS!  // Recipient wallet
)
```

## Example Plans

| Plan | Price | Credits | Duration | Use Case |
|---|---|---|---|---|
| Starter | $10 USDC | 100 | None | Small-scale API testing |
| Pro | $49 USDC | 1000 | 30 days | Production usage |
| Unlimited | $99 USDC | Unlimited | 30 days | High-volume access |
| Trial | Free | 10 | 7 days | Try before you buy |
