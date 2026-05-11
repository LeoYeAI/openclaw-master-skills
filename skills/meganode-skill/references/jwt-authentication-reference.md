# JWT Authentication Reference

## Overview

MegaNode supports JSON Web Token (JWT) authentication as an alternative to API key authentication. JWT provides enhanced security for production deployments by enabling token-based access control with expiration.

---

## Table of Contents

1. [When to Use JWT vs API Key](#when-to-use-jwt-vs-api-key) -- Authentication method comparison
2. [JWT Token Generation](#jwt-token-generation) -- Create tokens in JS/Python
3. [Using JWT with RPC Requests](#using-jwt-with-rpc-requests) -- HTTPS and WebSocket usage
4. [Token Lifecycle](#token-lifecycle) -- Generate, use, refresh, rotate
5. [Best Practices](#best-practices) -- Security recommendations

---

## When to Use JWT vs API Key

| Feature | API Key | JWT |
|---------|---------|-----|
| **Setup complexity** | Simple — append to URL | Requires token generation |
| **Security** | Key in URL (can leak in logs) | Token in header (more secure) |
| **Expiration** | No expiration | Configurable expiration |
| **Rotation** | Manual key regeneration | Automatic token refresh |
| **Use case** | Development, testing | Production, server-side |

---

## JWT Token Generation

### Step 1: Get JWT Secret

Obtain your JWT secret from the [MegaNode Dashboard](https://nodereal.io/meganode) under API Key settings.

### Step 2: Generate Token

```javascript
import jwt from "jsonwebtoken";

function generateMeganodeJWT(secret, expiresIn = "1h") {
  const payload = {
    iat: Math.floor(Date.now() / 1000),
  };

  return jwt.sign(payload, secret, {
    algorithm: "HS256",
    expiresIn,
  });
}

const token = generateMeganodeJWT(process.env.NODEREAL_JWT_SECRET);
```

### Python

```python
import jwt
import time

def generate_meganode_jwt(secret, expires_in=3600):
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + expires_in,
    }
    return jwt.encode(payload, secret, algorithm="HS256")

token = generate_meganode_jwt(os.environ["NODEREAL_JWT_SECRET"])
```

---

## Using JWT with RPC Requests

### HTTPS with Bearer Token

```javascript
const response = await fetch(
  "https://bsc-mainnet.nodereal.io/v1/",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${jwtToken}`,
    },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "eth_blockNumber",
      params: [],
    }),
  }
);
```

### WebSocket with JWT

```javascript
import WebSocket from "ws";

const ws = new WebSocket(
  "wss://bsc-mainnet.nodereal.io/ws/v1/",
  {
    headers: {
      "Authorization": `Bearer ${jwtToken}`,
    },
  }
);
```

---

## Token Lifecycle

1. **Generate** — Create a JWT with short expiration (1 hour recommended)
2. **Use** — Include in `Authorization: Bearer <token>` header
3. **Refresh** — Generate a new token before expiration
4. **Rotate** — Periodically rotate the JWT secret from the dashboard

---

## Best Practices

- Set short expiration times (1 hour or less) for production tokens
- Never hardcode JWT secrets — use environment variables
- Implement automatic token refresh before expiration
- Use JWT for server-side applications; API key is acceptable for local development
- Rotate JWT secrets periodically from the MegaNode dashboard
- Never expose JWT tokens in client-side JavaScript or logs
