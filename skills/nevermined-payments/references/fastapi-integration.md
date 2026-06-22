# FastAPI Integration

Add x402 payment protection to FastAPI applications using `PaymentMiddleware` from `payments_py.x402.fastapi`.

## Installation

```bash
pip install payments-py[fastapi] fastapi uvicorn
```

The `[fastapi]` extra installs FastAPI and Starlette dependencies required for the middleware.

## Quick Start

```python
import os
from fastapi import FastAPI, Request
from payments_py import Payments, PaymentOptions
from payments_py.x402.fastapi import PaymentMiddleware

app = FastAPI()

payments = Payments.get_instance(
    PaymentOptions(
        nvm_api_key=os.environ["NVM_API_KEY"],
        environment="live" if os.environ.get("ENV") == "production" else "sandbox"
    )
)

# Protect routes with one line
app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={
        "POST /ask": {"plan_id": os.environ["NVM_PLAN_ID"], "credits": 1}
    }
)

# Route handler — no payment logic needed
@app.post("/ask")
async def ask(request: Request):
    body = await request.json()
    response = await generate_ai_response(body.get("query"))
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
```

The middleware automatically:
- Returns `402` with `payment-required` header when no token is provided
- Verifies the x402 token via the Nevermined facilitator
- Burns credits after request completion
- Returns `payment-response` header with settlement receipt

## Route Configuration

### Fixed Credits

```python
app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={
        "POST /ask": {"plan_id": PLAN_ID, "credits": 1},
        "POST /generate": {"plan_id": PLAN_ID, "credits": 5}
    }
)
```

### Dynamic Credits

```python
async def calculate_credits(request: Request) -> int:
    """Charge based on requested token count."""
    body = await request.json()
    max_tokens = body.get("max_tokens", 100)
    return max(1, max_tokens // 100)

app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={
        "POST /generate": {
            "plan_id": PLAN_ID,
            "credits": calculate_credits  # Pass function instead of int
        }
    }
)
```

Sync functions also work:

```python
app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={
        "POST /analyze": {
            "plan_id": PLAN_ID,
            "credits": lambda req: 5 if req.headers.get("priority") == "high" else 1
        }
    }
)
```

### Path Parameters

```python
app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={
        "GET /users/:id": {"plan_id": PLAN_ID, "credits": 1},
        "POST /agents/:agentId/task": {"plan_id": PLAN_ID, "credits": 2}
    }
)
```

### With Agent ID

```python
app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={
        "POST /task": {
            "plan_id": PLAN_ID,
            "agent_id": AGENT_ID,  # Required for plans with multiple agents
            "credits": 5
        }
    }
)
```

### Using RouteConfig

```python
from payments_py.x402.fastapi import PaymentMiddleware, RouteConfig

app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={
        "POST /ask": RouteConfig(
            plan_id=PLAN_ID,
            credits=1,
            agent_id=AGENT_ID,
            network="eip155:84532"
        )
    }
)
```

## Middleware Options

```python
from payments_py.x402.fastapi import PaymentMiddleware, PaymentMiddlewareOptions

async def before_verify(request, payment_required):
    print(f"Verifying payment for {request.url.path}")

async def after_verify(request, verification):
    if verification.agent_request:
        print(f"Agent: {verification.agent_request.agent_name}")

async def after_settle(request, credits_used, settlement):
    print(f"Settled {credits_used} credits")

async def payment_error(error, request):
    return None  # Return custom response or None to use default

app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={"POST /ask": {"plan_id": PLAN_ID, "credits": 1}},
    options=PaymentMiddlewareOptions(
        token_header=["payment-signature"],
        on_before_verify=before_verify,
        on_after_verify=after_verify,
        on_after_settle=after_settle,
        on_payment_error=payment_error
    )
)
```

## Accessing Payment Context

After verification, the payment context is available in `request.state.payment_context`:

```python
from payments_py.x402.fastapi import PaymentContext

@app.post("/ask")
async def ask(request: Request):
    payment_context: PaymentContext = request.state.payment_context

    print(f"Token: {payment_context.token}")
    print(f"Credits to settle: {payment_context.credits_to_settle}")
    print(f"Agent request ID: {payment_context.agent_request_id}")

    if payment_context.agent_request:
        print(f"Agent: {payment_context.agent_request.agent_name}")
        print(f"Balance: {payment_context.agent_request.balance}")

    body = await request.json()
    response = await generate_ai_response(body.get("query"))
    return {"response": response}
```

## Complete Example

```python
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from openai import OpenAI
from payments_py import Payments, PaymentOptions
from payments_py.x402.fastapi import PaymentMiddleware, PaymentMiddlewareOptions

app = FastAPI(title="AI Agent with Nevermined Payments")

payments = Payments.get_instance(
    PaymentOptions(
        nvm_api_key=os.environ["NVM_API_KEY"],
        environment=os.environ.get("NVM_ENVIRONMENT", "sandbox")
    )
)
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PLAN_ID = os.environ["NVM_PLAN_ID"]

app.add_middleware(
    PaymentMiddleware,
    payments=payments,
    routes={
        "POST /ask": {"plan_id": PLAN_ID, "credits": 1}
    },
    options=PaymentMiddlewareOptions(
        on_before_verify=lambda req, pr: print(f"[Payment] Verifying request to {req.url.path}"),
        on_after_settle=lambda req, credits, settlement: print(f"[Payment] Settled {credits} credits")
    )
)

@app.post("/ask")
async def ask(request: Request):
    body = await request.json()
    query = body.get("query", "")
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}]
    )
    return {"response": completion.choices[0].message.content}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
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

Complete working example: [github.com/nevermined-io/tutorials/tree/main/http-simple-agent-py](https://github.com/nevermined-io/tutorials/tree/main/http-simple-agent-py)
