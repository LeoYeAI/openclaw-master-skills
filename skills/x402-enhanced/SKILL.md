---
name: x402
description: "Internet-native payments using the HTTP 402 Payment Required standard. Set up as a buyer to pay for API access, or as a seller to monetize your APIs."
metadata: {"openclaw":{"emoji":"💸"}}
---

# x402 Payment Protocol

x402 is an open, internet-native payment standard built around the HTTP `402 Payment Required` status code. It enables programmatic payments between clients and servers without accounts, sessions, or credential management.

**Key Benefits:**
- Zero protocol fees (only blockchain network fees)
- Zero friction (no accounts or KYC required)
- Instant settlement via stablecoins
- Works with AI agents and automated systems

**Documentation:** https://docs.x402.org | **GitHub:** https://github.com/coinbase/x402

---

## How x402 Works

1. Client requests a resource from a server
2. Server responds with `402 Payment Required` + payment instructions
3. Client signs and submits a payment payload
4. Server verifies payment, optionally via a facilitator
5. Server returns the requested resource

---

## Environment Variables

### For Buyers (Clients)
```bash
# EVM wallet private key (Ethereum/Base/Polygon)
EVM_PRIVATE_KEY=0x...

# Solana wallet private key (base58 encoded)
SVM_PRIVATE_KEY=...

# Target server URL
RESOURCE_SERVER_URL=http://localhost:4021
ENDPOINT_PATH=/weather
```

### For Sellers (Servers)
```bash
# Your EVM wallet address to receive payments
EVM_ADDRESS=0x...

# Your Solana wallet address to receive payments
SVM_ADDRESS=...

# Facilitator URL (see list below)
FACILITATOR_URL=https://x402.org/facilitator
```

---

## Network Identifiers (CAIP-2)

| Network | CAIP-2 ID | Description |
|---------|-----------|-------------|
| **Base** | | |
| Base Mainnet | `eip155:8453` | Base L2 mainnet |
| Base Sepolia | `eip155:84532` | Base L2 testnet |
| **Solana** | | |
| Solana Mainnet | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` | Solana mainnet |
| Solana Devnet | `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1` | Solana testnet |
| **Polygon** | | |
| Polygon Mainnet | `eip155:137` | Polygon PoS mainnet |
| Polygon Amoy | `eip155:80002` | Polygon testnet |
| **Avalanche** | | |
| Avalanche C-Chain | `eip155:43114` | Avalanche mainnet |
| Avalanche Fuji | `eip155:43113` | Avalanche testnet |
| **Sei** | | |
| Sei Mainnet | `eip155:1329` | Sei EVM mainnet |
| Sei Testnet | `eip155:713715` | Sei EVM testnet |
| **X Layer** | | |
| X Layer Mainnet | `eip155:196` | OKX L2 mainnet |
| X Layer Testnet | `eip155:1952` | OKX L2 testnet |
| **SKALE** | | |
| SKALE Base | `eip155:1187947933` | SKALE mainnet |
| SKALE Base Sepolia | `eip155:324705682` | SKALE testnet |


---

## Facilitators

Facilitators handle payment verification and blockchain settlement. Choose one:

| Name | URL | Notes |
|------|-----|-------|
| x402.org | `https://x402.org/facilitator` | Default, testnet only |
| Coinbase | `https://api.cdp.coinbase.com/platform/v2/x402` | Production |
| PayAI | `https://facilitator.payai.network` | Production |
| Corbits | `https://facilitator.corbits.dev` | Production |
| x402rs | `https://facilitator.x402.rs` | Production |
| Dexter | `https://x402.dexter.cash` | Production |
| Heurist | `https://facilitator.heurist.xyz` | Production |
| Kobaru | `https://gateway.kobaru.io` | Production |
| Mogami | `https://facilitator.mogami.tech` | Production |
| Nevermined | `https://api.live.nevermined.app/api/v1/` | Production |
| Openfacilitator | `https://pay.openfacilitator.io` | Production |
| Solpay | `https://x402.solpay.cash` | Production |
| Primer | `https://x402.primer.systems` | Production |
| xEcho | `https://facilitator.xechoai.xyz` | Production |

---

# Buyer Examples (Client)

## TypeScript with fetch

Install dependencies:
```bash
npm install @x402/fetch @x402/evm @x402/svm viem @solana/kit @scure/base dotenv
```

Code:
```typescript
import { config } from "dotenv";
import { x402Client, wrapFetchWithPayment, x402HTTPClient } from "@x402/fetch";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { registerExactSvmScheme } from "@x402/svm/exact/client";
import { privateKeyToAccount } from "viem/accounts";
import { createKeyPairSignerFromBytes } from "@solana/kit";
import { base58 } from "@scure/base";

config();

const evmPrivateKey = process.env.EVM_PRIVATE_KEY as `0x${string}`;
const svmPrivateKey = process.env.SVM_PRIVATE_KEY as string;
const url = `${process.env.RESOURCE_SERVER_URL}${process.env.ENDPOINT_PATH}`;

async function main(): Promise<void> {
  const evmSigner = privateKeyToAccount(evmPrivateKey);
  const svmSigner = await createKeyPairSignerFromBytes(base58.decode(svmPrivateKey));

  const client = new x402Client();
  registerExactEvmScheme(client, { signer: evmSigner });
  registerExactSvmScheme(client, { signer: svmSigner });

  const fetchWithPayment = wrapFetchWithPayment(fetch, client);

  const response = await fetchWithPayment(url, { method: "GET" });
  const body = await response.json();
  console.log("Response:", body);

  if (response.ok) {
    const paymentResponse = new x402HTTPClient(client).getPaymentSettleResponse(
      name => response.headers.get(name)
    );
    console.log("Payment:", JSON.stringify(paymentResponse, null, 2));
  }
}

main().catch(console.error);
```

## TypeScript with axios

Install dependencies:
```bash
npm install @x402/axios @x402/evm @x402/svm axios viem @solana/kit @scure/base dotenv
```

Code:
```typescript
import { config } from "dotenv";
import { x402Client, wrapAxiosWithPayment, x402HTTPClient } from "@x402/axios";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { registerExactSvmScheme } from "@x402/svm/exact/client";
import { privateKeyToAccount } from "viem/accounts";
import { createKeyPairSignerFromBytes } from "@solana/kit";
import { base58 } from "@scure/base";
import axios from "axios";

config();

const evmPrivateKey = process.env.EVM_PRIVATE_KEY as `0x${string}`;
const svmPrivateKey = process.env.SVM_PRIVATE_KEY as string;
const url = `${process.env.RESOURCE_SERVER_URL}${process.env.ENDPOINT_PATH}`;

async function main(): Promise<void> {
  const evmSigner = privateKeyToAccount(evmPrivateKey);
  const svmSigner = await createKeyPairSignerFromBytes(base58.decode(svmPrivateKey));

  const client = new x402Client();
  registerExactEvmScheme(client, { signer: evmSigner });
  registerExactSvmScheme(client, { signer: svmSigner });

  const api = wrapAxiosWithPayment(axios.create(), client);

  const response = await api.get(url);
  console.log("Response:", response.data);

  if (response.status < 400) {
    const paymentResponse = new x402HTTPClient(client).getPaymentSettleResponse(
      name => response.headers[name.toLowerCase()]
    );
    console.log("Payment:", paymentResponse);
  }
}

main().catch(console.error);
```

## Python with httpx (async)

Install dependencies:
```bash
pip install "x402[httpx,evm,svm]" python-dotenv
```

Code:
```python
import asyncio
import os
from dotenv import load_dotenv
from eth_account import Account

from x402 import x402Client
from x402.http import x402HTTPClient
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client
from x402.mechanisms.svm import KeypairSigner
from x402.mechanisms.svm.exact.register import register_exact_svm_client

load_dotenv()

async def main() -> None:
    evm_private_key = os.getenv("EVM_PRIVATE_KEY")
    svm_private_key = os.getenv("SVM_PRIVATE_KEY")
    base_url = os.getenv("RESOURCE_SERVER_URL")
    endpoint_path = os.getenv("ENDPOINT_PATH")

    client = x402Client()

    if evm_private_key:
        account = Account.from_key(evm_private_key)
        register_exact_evm_client(client, EthAccountSigner(account))

    if svm_private_key:
        svm_signer = KeypairSigner.from_base58(svm_private_key)
        register_exact_svm_client(client, svm_signer)

    http_client = x402HTTPClient(client)
    url = f"{base_url}{endpoint_path}"

    async with x402HttpxClient(client) as http:
        response = await http.get(url)
        await response.aread()
        print(f"Response: {response.text}")

        if response.is_success:
            try:
                settle_response = http_client.get_payment_settle_response(
                    lambda name: response.headers.get(name)
                )
                print(f"Payment: {settle_response.model_dump_json(indent=2)}")
            except ValueError:
                print("No payment response header found")

if __name__ == "__main__":
    asyncio.run(main())
```

## Python with requests (sync)

Install dependencies:
```bash
pip install "x402[requests,evm,svm]" python-dotenv
```

Code:
```python
import os
from dotenv import load_dotenv
from eth_account import Account

from x402 import x402ClientSync
from x402.http import x402HTTPClientSync
from x402.http.clients import x402_requests
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client
from x402.mechanisms.svm import KeypairSigner
from x402.mechanisms.svm.exact.register import register_exact_svm_client

load_dotenv()

def main() -> None:
    evm_private_key = os.getenv("EVM_PRIVATE_KEY")
    svm_private_key = os.getenv("SVM_PRIVATE_KEY")
    base_url = os.getenv("RESOURCE_SERVER_URL")
    endpoint_path = os.getenv("ENDPOINT_PATH")

    client = x402ClientSync()

    if evm_private_key:
        account = Account.from_key(evm_private_key)
        register_exact_evm_client(client, EthAccountSigner(account))

    if svm_private_key:
        svm_signer = KeypairSigner.from_base58(svm_private_key)
        register_exact_svm_client(client, svm_signer)

    http_client = x402HTTPClientSync(client)
    url = f"{base_url}{endpoint_path}"

    with x402_requests(client) as session:
        response = session.get(url)
        print(f"Response: {response.text}")

        if response.ok:
            try:
                settle_response = http_client.get_payment_settle_response(
                    lambda name: response.headers.get(name)
                )
                print(f"Payment: {settle_response.model_dump_json(indent=2)}")
            except ValueError:
                print("No payment response header found")

if __name__ == "__main__":
    main()
```

## Go with net/http

Install dependencies:
```bash
go get github.com/coinbase/x402/go
go get github.com/joho/godotenv
```

Code:
```go
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"

	x402 "github.com/coinbase/x402/go"
	"github.com/joho/godotenv"
)

func main() {
	godotenv.Load()

	evmPrivateKey := os.Getenv("EVM_PRIVATE_KEY")
	svmPrivateKey := os.Getenv("SVM_PRIVATE_KEY")
	url := os.Getenv("SERVER_URL")
	if url == "" {
		url = "http://localhost:4021/weather"
	}

	// Create x402 client with EVM and SVM support
	client, err := x402.NewClientBuilder().
		WithEvmSigner(evmPrivateKey).
		WithSvmSigner(svmPrivateKey).
		Build()
	if err != nil {
		fmt.Printf("Failed to create client: %v\n", err)
		os.Exit(1)
	}

	// Wrap HTTP client with payment handling
	httpClient := client.WrapHTTPClient(&http.Client{Timeout: 30 * time.Second})

	ctx := context.Background()
	req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
	resp, err := httpClient.Do(req)
	if err != nil {
		fmt.Printf("Request failed: %v\n", err)
		os.Exit(1)
	}
	defer resp.Body.Close()

	var responseData interface{}
	json.NewDecoder(resp.Body).Decode(&responseData)
	prettyJSON, _ := json.MarshalIndent(responseData, "", "  ")
	fmt.Printf("Response: %s\n", string(prettyJSON))
}
```

---

# Seller Examples (Server)

## TypeScript with Express

Install dependencies:
```bash
npm install express @x402/express @x402/core @x402/evm @x402/svm dotenv
```

Code:
```typescript
import { config } from "dotenv";
import express from "express";
import { paymentMiddleware, x402ResourceServer } from "@x402/express";
import { ExactEvmScheme } from "@x402/evm/exact/server";
import { ExactSvmScheme } from "@x402/svm/exact/server";
import { HTTPFacilitatorClient } from "@x402/core/server";

config();

const evmAddress = process.env.EVM_ADDRESS as `0x${string}`;
const svmAddress = process.env.SVM_ADDRESS;
const facilitatorUrl = process.env.FACILITATOR_URL || "https://x402.org/facilitator";

const facilitatorClient = new HTTPFacilitatorClient({ url: facilitatorUrl });
const app = express();

app.use(
  paymentMiddleware(
    {
      "GET /weather": {
        accepts: [
          { scheme: "exact", price: "$0.001", network: "eip155:84532", payTo: evmAddress },
          { scheme: "exact", price: "$0.001", network: "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1", payTo: svmAddress },
        ],
        description: "Weather data",
        mimeType: "application/json",
      },
    },
    new x402ResourceServer(facilitatorClient)
      .register("eip155:84532", new ExactEvmScheme())
      .register("solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1", new ExactSvmScheme()),
  ),
);

app.get("/weather", (req, res) => {
  res.send({ report: { weather: "sunny", temperature: 70 } });
});

app.listen(4021, () => console.log("Server listening at http://localhost:4021"));
```

## TypeScript with Hono

Install dependencies:
```bash
npm install hono @hono/node-server @x402/hono @x402/core @x402/evm @x402/svm dotenv
```

Code:
```typescript
import { config } from "dotenv";
import { paymentMiddleware, x402ResourceServer } from "@x402/hono";
import { ExactEvmScheme } from "@x402/evm/exact/server";
import { ExactSvmScheme } from "@x402/svm/exact/server";
import { HTTPFacilitatorClient } from "@x402/core/server";
import { Hono } from "hono";
import { serve } from "@hono/node-server";

config();

const evmAddress = process.env.EVM_ADDRESS as `0x${string}`;
const svmAddress = process.env.SVM_ADDRESS;
const facilitatorUrl = process.env.FACILITATOR_URL || "https://x402.org/facilitator";

const facilitatorClient = new HTTPFacilitatorClient({ url: facilitatorUrl });
const app = new Hono();

app.use(
  paymentMiddleware(
    {
      "GET /weather": {
        accepts: [
          { scheme: "exact", price: "$0.001", network: "eip155:84532", payTo: evmAddress },
          { scheme: "exact", price: "$0.001", network: "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1", payTo: svmAddress },
        ],
        description: "Weather data",
        mimeType: "application/json",
      },
    },
    new x402ResourceServer(facilitatorClient)
      .register("eip155:84532", new ExactEvmScheme())
      .register("solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1", new ExactSvmScheme()),
  ),
);

app.get("/weather", c => c.json({ report: { weather: "sunny", temperature: 70 } }));

serve({ fetch: app.fetch, port: 4021 });
console.log("Server listening at http://localhost:4021");
```

## Python with FastAPI

Install dependencies:
```bash
pip install "x402[fastapi,evm,svm]" python-dotenv uvicorn
```

Code:
```python
import os
from dotenv import load_dotenv
from fastapi import FastAPI

from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.mechanisms.svm.exact import ExactSvmServerScheme
from x402.schemas import Network
from x402.server import x402ResourceServer

load_dotenv()

EVM_ADDRESS = os.getenv("EVM_ADDRESS")
SVM_ADDRESS = os.getenv("SVM_ADDRESS")
EVM_NETWORK: Network = "eip155:84532"
SVM_NETWORK: Network = "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1"
FACILITATOR_URL = os.getenv("FACILITATOR_URL", "https://x402.org/facilitator")

app = FastAPI()

facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=FACILITATOR_URL))
server = x402ResourceServer(facilitator)
server.register(EVM_NETWORK, ExactEvmServerScheme())
server.register(SVM_NETWORK, ExactSvmServerScheme())

routes = {
    "GET /weather": RouteConfig(
        accepts=[
            PaymentOption(scheme="exact", pay_to=EVM_ADDRESS, price="$0.01", network=EVM_NETWORK),
            PaymentOption(scheme="exact", pay_to=SVM_ADDRESS, price="$0.01", network=SVM_NETWORK),
        ],
        mime_type="application/json",
        description="Weather report",
    ),
}

app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/weather")
async def get_weather():
    return {"report": {"weather": "sunny", "temperature": 70}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4021)
```

## Python with Flask

Install dependencies:
```bash
pip install "x402[flask,evm,svm]" python-dotenv
```

Code:
```python
import os
from dotenv import load_dotenv
from flask import Flask, jsonify

from x402.http import FacilitatorConfig, HTTPFacilitatorClientSync, PaymentOption
from x402.http.middleware.flask import payment_middleware
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.mechanisms.svm.exact import ExactSvmServerScheme
from x402.schemas import Network
from x402.server import x402ResourceServerSync

load_dotenv()

EVM_ADDRESS = os.getenv("EVM_ADDRESS")
SVM_ADDRESS = os.getenv("SVM_ADDRESS")
EVM_NETWORK: Network = "eip155:84532"
SVM_NETWORK: Network = "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1"
FACILITATOR_URL = os.getenv("FACILITATOR_URL", "https://x402.org/facilitator")

app = Flask(__name__)

facilitator = HTTPFacilitatorClientSync(FacilitatorConfig(url=FACILITATOR_URL))
server = x402ResourceServerSync(facilitator)
server.register(EVM_NETWORK, ExactEvmServerScheme())
server.register(SVM_NETWORK, ExactSvmServerScheme())

routes = {
    "GET /weather": RouteConfig(
        accepts=[
            PaymentOption(scheme="exact", pay_to=EVM_ADDRESS, price="$0.01", network=EVM_NETWORK),
            PaymentOption(scheme="exact", pay_to=SVM_ADDRESS, price="$0.01", network=SVM_NETWORK),
        ],
        mime_type="application/json",
        description="Weather report",
    ),
}

payment_middleware(app, routes=routes, server=server)

@app.route("/health")
def health_check():
    return jsonify({"status": "ok"})

@app.route("/weather")
def get_weather():
    return jsonify({"report": {"weather": "sunny", "temperature": 70}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4021)
```

## Go with Gin

Install dependencies:
```bash
go get github.com/coinbase/x402/go
go get github.com/gin-gonic/gin
go get github.com/joho/godotenv
```

Code:
```go
package main

import (
	"net/http"
	"os"
	"time"

	x402 "github.com/coinbase/x402/go"
	x402http "github.com/coinbase/x402/go/http"
	ginmw "github.com/coinbase/x402/go/http/gin"
	evm "github.com/coinbase/x402/go/mechanisms/evm/exact/server"
	svm "github.com/coinbase/x402/go/mechanisms/svm/exact/server"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	godotenv.Load()

	evmAddress := os.Getenv("EVM_PAYEE_ADDRESS")
	svmAddress := os.Getenv("SVM_PAYEE_ADDRESS")
	facilitatorURL := os.Getenv("FACILITATOR_URL")

	r := gin.Default()

	facilitatorClient := x402http.NewHTTPFacilitatorClient(&x402http.FacilitatorConfig{
		URL: facilitatorURL,
	})

	routes := x402http.RoutesConfig{
		"GET /weather": {
			Accepts: x402http.PaymentOptions{
				{Scheme: "exact", Price: "$0.001", Network: "eip155:84532", PayTo: evmAddress},
				{Scheme: "exact", Price: "$0.001", Network: "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1", PayTo: svmAddress},
			},
			Description: "Get weather data",
			MimeType:    "application/json",
		},
	}

	r.Use(ginmw.X402Payment(ginmw.Config{
		Routes:      routes,
		Facilitator: facilitatorClient,
		Schemes: []ginmw.SchemeConfig{
			{Network: "eip155:84532", Server: evm.NewExactEvmScheme()},
			{Network: "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1", Server: svm.NewExactSvmScheme()},
		},
		Timeout: 30 * time.Second,
	}))

	r.GET("/weather", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"weather":     "sunny",
			"temperature": 70,
			"timestamp":   time.Now().Format(time.RFC3339),
		})
	})

	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	r.Run(":4021")
}
```

---

# Paywall UI (Server Middleware)

The `@x402/paywall` package provides a pre-built paywall UI that displays when users hit a 402 Payment Required response. It handles wallet connection (MetaMask, Coinbase Wallet, Phantom, etc.), USDC balance checking, and payment submission.

**Important:** This package is designed for **server-side use only**. It generates a complete, self-contained HTML page (~1.9MB) with embedded React, wagmi, and wallet adapters that the server returns when a 402 response is triggered. It is **not** a standalone React component library and **cannot** be imported into an existing React application.

**Looking for React components instead?**
- **For Solana React apps:** Use `@payai/x402-solana-react` - drop-in paywall components with themes
- **For custom EVM/Solana React:** Build with `wagmi` + `viem` (EVM) or `@solana/wallet-adapter-react` (Solana)
- **Multi-chain SDKs:** `@dexterai/x402`, `x402-solana`

See the [Custom React Frontend Integration](#custom-react-frontend-integration) section below for details.

---

## Installation (Server-Side)

```bash
npm install @x402/paywall
```

**Bundle sizes by import:**
| Import | Size | Networks |
|--------|------|----------|
| `@x402/paywall` | 3.5MB | EVM + Solana |
| `@x402/paywall/evm` | 3.4MB | EVM only |
| `@x402/paywall/svm` | 1.0MB | Solana only |

## Usage (Server Middleware)

### EVM Only

```typescript
import { createPaywall } from "@x402/paywall";
import { evmPaywall } from "@x402/paywall/evm";

const paywall = createPaywall()
  .withNetwork(evmPaywall)
  .withConfig({
    appName: "My App",
    appLogo: "/logo.png",
    testnet: true,
  })
  .build();
```

### Solana Only

```typescript
import { createPaywall } from "@x402/paywall";
import { svmPaywall } from "@x402/paywall/svm";

const paywall = createPaywall()
  .withNetwork(svmPaywall)
  .withConfig({
    appName: "My Solana App",
    testnet: true,
  })
  .build();
```

### Multi-Network

```typescript
import { createPaywall } from "@x402/paywall";
import { evmPaywall } from "@x402/paywall/evm";
import { svmPaywall } from "@x402/paywall/svm";

const paywall = createPaywall()
  .withNetwork(evmPaywall)  // First-match priority
  .withNetwork(svmPaywall)  // Fallback option
  .withConfig({
    appName: "Multi-chain App",
    testnet: true,
  })
  .build();
```

## Configuration Options

```typescript
interface PaywallConfig {
  appName?: string;    // App name shown in wallet connection
  appLogo?: string;    // App logo URL
  currentUrl?: string; // URL of protected resource
  testnet?: boolean;   // Use testnet (default: true)
}
```

## Integration with Express

```typescript
import express from "express";
import { paymentMiddleware, x402ResourceServer } from "@x402/express";
import { ExactEvmScheme } from "@x402/evm/exact/server";
import { HTTPFacilitatorClient } from "@x402/core/server";
import { createPaywall } from "@x402/paywall";
import { evmPaywall } from "@x402/paywall/evm";

const app = express();

const facilitatorClient = new HTTPFacilitatorClient({ url: "https://x402.org/facilitator" });

const paywall = createPaywall()
  .withNetwork(evmPaywall)
  .withConfig({ appName: "My API", testnet: true })
  .build();

app.use(
  paymentMiddleware(
    {
      "GET /premium": {
        accepts: [{ scheme: "exact", price: "$0.01", network: "eip155:84532", payTo: "0x..." }],
        description: "Premium content",
        mimeType: "application/json",
      },
    },
    new x402ResourceServer(facilitatorClient).register("eip155:84532", new ExactEvmScheme()),
    undefined,  // paywallConfig (using custom paywall instead)
    paywall,    // custom paywall provider
  ),
);

app.get("/premium", (req, res) => res.json({ content: "Premium data" }));
app.listen(4021);
```

## Auto-Detection (Simple Usage)

If you pass a `paywallConfig` object instead of a custom paywall, the middleware will automatically use `@x402/paywall` if installed:

```typescript
app.use(
  paymentMiddleware(
    routes,
    server,
    { appName: "My App", testnet: true },  // paywallConfig - auto-detects @x402/paywall
  ),
);
```

## How First-Match Selection Works

When the server returns multiple payment options, the paywall selects the first one that has a registered handler:

```typescript
// Server returns:
{ "accepts": [
  { "network": "solana:5eykt...", ... },  // First option
  { "network": "eip155:8453", ... }       // Second option
]}

// If both handlers registered, Solana is selected (first in accepts)
const paywall = createPaywall()
  .withNetwork(evmPaywall)
  .withNetwork(svmPaywall)
  .build();
```

---

## Pricing Configuration

### Simple USD Pricing
```typescript
{ scheme: "exact", price: "$0.001", network: "eip155:84532", payTo: evmAddress }
```

### Custom Token Amount (ERC-20)
```typescript
{
  scheme: "exact",
  price: {
    amount: "10000",  // atomic units ($0.01 USDC = 10000 because USDC has 6 decimals)
    asset: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  // USDC on Base Sepolia
    extra: { name: "USDC", version: "2" }  // EIP-712 params
  },
  network: "eip155:84532",
  payTo: evmAddress
}
```

---

## Testing

For testing, use:
- **Network:** `eip155:84532` (Base Sepolia) or `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1` (Solana Devnet)
- **Facilitator:** `https://x402.org/facilitator` (testnet only)
- **Faucets:** Get testnet USDC from Base Sepolia faucet

For production, switch to mainnet networks and a production facilitator.
