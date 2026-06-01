# TPN x402 Code Examples (Pay-Per-Request with USDC on Base)

Working examples for generating a SOCKS5 proxy via `POST /api/v1/x402/proxy/generate` using the x402 payment protocol. No API key needed — pay with USDC on Base.

The flow for every language is the same:
1. Send request without payment
2. Receive `HTTP 402` with a `payment-required` header
3. Sign a USDC payment on Base using the decoded requirements
4. Retry the request with the payment signature
5. Receive SOCKS5 proxy credentials

---

## curl (step-by-step)

```bash
# Step 1: Send the initial request — expect a 402 with payment details
# Use -D - to display response headers alongside the body
curl -s -D - -X POST \
  https://api.taoprivatenetwork.com/api/v1/x402/proxy/generate \
  -H "Content-Type: application/json" \
  -d '{"minutes": 60, "format": "json", "connection_type": "any"}'

# The response includes:
# - HTTP/2 402 status
# - A payment-required header (base64-encoded JSON with payment details)
# - A JSON response body

# Step 2: Decode the payment requirements
# Copy the base64 value from the payment-required header shown above, then:
echo "<paste-base64-value-here>" | base64 -d | jq .

# This reveals: payTo address, amount (USDC base units), network, and timeout.

# Steps 3-4: Sign and retry — curl alone can't sign EVM transactions.
# Use the @x402 npm packages or the browser JS example below for the full automated flow.
# Once you have the payment signature, retry with:
#
# curl -s -X POST https://api.taoprivatenetwork.com/api/v1/x402/proxy/generate \
#   -H "Content-Type: application/json" \
#   -H "X-PAYMENT: <payment-signature>" \
#   -d '{"minutes": 60, "format": "json", "connection_type": "any"}'
```

---

## Browser JavaScript (ethers + MetaMask)

This example uses `window.ethereum` (MetaMask or similar browser extension) — no environment variables or server-side credentials needed.

```js
import { ethers } from 'ethers'

// EIP-712 domain and types for USDC permit on Base
const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
const url = 'https://api.taoprivatenetwork.com/api/v1/x402/proxy/generate'
const body = JSON.stringify( { minutes: 60, format: 'json', connection_type: 'any' } )

// Step 1: Send request without payment
const initial = await fetch( url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body
} )

if ( initial.status !== 402 ) throw new Error( `Expected 402, got ${ initial.status }` )

// Step 2: Decode payment requirements from the header
const payment_header = initial.headers.get( 'payment-required' )
const payment_requirements = JSON.parse( atob( payment_header ) )

console.log( 'Payment required:', payment_requirements )

const accept = payment_requirements.accepts[ 0 ]
const pay_to = accept.payTo
const amount = accept.amount // USDC base units (6 decimals)

// Step 3: Sign USDC payment on Base via browser popup (MetaMask etc.)
const provider = new ethers.BrowserProvider( window.ethereum )
const authorizer = await provider.getSigner()

const usdc = new ethers.Contract( USDC_ADDRESS, [
    'function approve(address spender, uint256 amount) returns (bool)',
    'function allowance(address owner, address spender) view returns (uint256)'
], authorizer )

// Approve the payment amount
const tx = await usdc.approve( pay_to, amount )
await tx.wait()

// Sign the x402 payment attestation
const payment_message = {
    url,
    amount,
    payTo: pay_to,
    network: accept.network
}
const signature = await authorizer.signMessage( JSON.stringify( payment_message ) )

// Step 4: Retry with payment
const paid_response = await fetch( url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-PAYMENT': signature
    },
    body
} )

const proxy_data = await paid_response.json()
const { username, password, ip_address, port } = proxy_data.vpnConfig
console.log( `Proxy: socks5h://${ username }:${ password }@${ ip_address }:${ port }` )
console.log( `Expires: ${ proxy_data.expiresAt }` )
```

---

## Node.js and Python

For server-side implementations, use the official `@x402` npm packages which handle the full payment handshake automatically:

- **Node.js:** [`@x402/core`](https://www.npmjs.com/package/@x402/core) and [`@x402/evm`](https://www.npmjs.com/package/@x402/evm) — see the [@x402 npm org](https://www.npmjs.com/org/x402) for usage
- **Python:** See the [x402 specification](https://www.x402.org) for protocol details

These libraries manage signing internally — this skill only provides the endpoint URL and request body format.

---

## Payment Reference

| Field    | Value                                        |
|----------|----------------------------------------------|
| Network  | Base (eip155:8453)                           |
| Currency | USDC (6 decimals)                            |
| Contract | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Scheme   | exact (pay exact amount)                     |
| Timeout  | 300 seconds                                  |

## Links

- x402 Protocol: https://www.x402.org
- @x402 npm packages: https://www.npmjs.com/org/x402
- Base Network: https://base.org
- USDC on Base: https://developers.circle.com/stablecoins/usdc-on-base
