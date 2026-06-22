# Strands Agent Integration

Add x402 payment protection to Strands AI agent tools using the `@requires_payment` decorator from `payments_py.x402.strands`.

## Installation

```bash
pip install payments-py[strands] strands-agents
```

The `[strands]` extra installs the Strands SDK dependency required for the decorator.

## Quick Start

**Important:** You must use `@tool(context=True)` instead of plain `@tool`. This tells Strands to inject `tool_context`, which the decorator needs to access `invocation_state` for the payment token.

```python
import os
from dotenv import load_dotenv
from strands import Agent, tool
from payments_py import Payments, PaymentOptions
from payments_py.x402.strands import requires_payment

load_dotenv()

payments = Payments.get_instance(
    PaymentOptions(
        nvm_api_key=os.environ["NVM_API_KEY"],
        environment=os.environ.get("NVM_ENVIRONMENT", "sandbox"),
    )
)

PLAN_ID = os.environ["NVM_PLAN_ID"]

@tool(context=True)
@requires_payment(payments=payments, plan_id=PLAN_ID, credits=1)
def analyze_data(query: str, tool_context=None) -> dict:
    """Analyze data based on a query. Costs 1 credit per request.

    Args:
        query: The data analysis query to process.
    """
    return {
        "status": "success",
        "content": [{"text": f"Analysis complete for: {query}"}],
    }

agent = Agent(tools=[analyze_data])
```

The decorator automatically:
- Returns a `PaymentRequired` error when no token is provided
- Verifies the x402 token via the Nevermined facilitator
- Executes the tool function on successful verification
- Burns credits after successful execution

## Payment Error Flow

The `@requires_payment` decorator follows the x402 MCP transport spec — payment errors are returned as **tool results** with `status: "error"`, not raised as exceptions. Each error includes:

1. A human-readable text block explaining the payment requirement
2. A structured JSON block containing the full `PaymentRequired` object

In Strands, the LLM sees the error and relays it to the user in natural language. Clients use `extract_payment_required(agent.messages)` to get the structured data.

## Client-Side: Payment Discovery

```python
from payments_py import Payments, PaymentOptions
from payments_py.x402.strands import extract_payment_required
from agent import agent, payments

# Step 1: Call agent without token — triggers PaymentRequired
result = agent("Analyze the latest sales trends")

# Step 2: Extract PaymentRequired from conversation history
payment_required = extract_payment_required(agent.messages)

if payment_required:
    # Step 3: Choose a plan and acquire token
    chosen_plan = payment_required["accepts"][0]
    plan_id = chosen_plan["planId"]
    agent_id = (chosen_plan.get("extra") or {}).get("agentId")

    token_response = payments.x402.get_x402_access_token(
        plan_id=plan_id,
        agent_id=agent_id,
    )
    access_token = token_response["accessToken"]

    # Step 4: Call agent with payment token
    state = {"payment_token": access_token}
    result = agent("Analyze the latest sales trends", invocation_state=state)
    print(f"Result: {result}")

    # Step 5: Check settlement
    settlement = state.get("payment_settlement")
    if settlement:
        print(f"Credits redeemed: {settlement.credits_redeemed}")
```

## Decorator Configuration

### Single Plan

```python
@tool(context=True)
@requires_payment(payments=payments, plan_id="plan-123", credits=1)
def my_tool(query: str, tool_context=None) -> dict:
    ...
```

### Multiple Plans

```python
@tool(context=True)
@requires_payment(
    payments=payments,
    plan_ids=["plan-basic", "plan-premium"],
    credits=1,
)
def my_tool(query: str, tool_context=None) -> dict:
    ...
```

### Dynamic Credits

```python
def calc_credits(kwargs):
    """Charge based on complexity."""
    return kwargs.get("complexity", 1) * 2

@tool(context=True)
@requires_payment(payments=payments, plan_id=PLAN_ID, credits=calc_credits)
def my_tool(query: str, complexity: int = 1, tool_context=None) -> dict:
    ...
```

### With Agent ID

```python
@tool(context=True)
@requires_payment(
    payments=payments,
    plan_id=PLAN_ID,
    credits=1,
    agent_id=os.environ.get("NVM_AGENT_ID"),
)
def my_tool(query: str, tool_context=None) -> dict:
    ...
```

### Lifecycle Hooks

```python
def on_before_verify(payment_required):
    print(f"Verifying payment for {len(payment_required.accepts)} plans")

def on_after_verify(verification):
    print(f"Verified! Request ID: {verification.agent_request_id}")

def on_after_settle(credits_used, settlement):
    print(f"Settled {credits_used} credits")

def on_payment_error(error):
    return None  # Return custom error dict or None for default

@tool(context=True)
@requires_payment(
    payments=payments,
    plan_id=PLAN_ID,
    credits=1,
    on_before_verify=on_before_verify,
    on_after_verify=on_after_verify,
    on_after_settle=on_after_settle,
    on_payment_error=on_payment_error,
)
def my_tool(query: str, tool_context=None) -> dict:
    ...
```

## Accessing Payment Context

```python
from payments_py.x402.strands import PaymentContext

@tool(context=True)
@requires_payment(payments=payments, plan_id=PLAN_ID, credits=1)
def my_tool(query: str, tool_context=None) -> dict:
    ctx = tool_context.invocation_state.get("payment_context")
    if ctx and isinstance(ctx, PaymentContext):
        print(f"Token: {ctx.token}")
        print(f"Credits: {ctx.credits_to_settle}")
        print(f"Request ID: {ctx.agent_request_id}")
        print(f"Verified: {ctx.verified}")

    return {"status": "success", "content": [{"text": "Done"}]}
```

## Environment Variables

```bash
NVM_API_KEY=nvm:your-api-key
NVM_ENVIRONMENT=sandbox
NVM_PLAN_ID=your-plan-id
NVM_AGENT_ID=your-agent-id          # Optional
OPENAI_API_KEY=sk-your-openai-key   # Or your preferred model provider
```

## Tutorial

Complete working example: [github.com/nevermined-io/hackathons/tree/main/agents/strands-simple-agent](https://github.com/nevermined-io/hackathons/tree/main/agents/strands-simple-agent)
