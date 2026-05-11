# Wallet Setup

Use this rule when the agent needs an Ethereum wallet for SIWE signing on the Agentic Gateway.

## Important Security Rules

- **NEVER** ask the user to paste a private key in chat
- **NEVER** store private keys in files (no `wallet.json`)
- Private keys must only be accessed via environment variables

## Determine Wallet Source

Check if `WALLET_PRIVATE_KEY` is set in the environment.

---

## If `WALLET_PRIVATE_KEY` Is Set

Derive the account and proceed to [Fund the Wallet](#fund-the-wallet).

```typescript
import { privateKeyToAccount } from "viem/accounts";

const account = privateKeyToAccount(process.env.WALLET_PRIVATE_KEY as `0x${string}`);
console.log("Wallet address:", account.address);
```

---

## If `WALLET_PRIVATE_KEY` Is NOT Set

Tell the user they need to set it up. Provide these instructions:

### Option A: Use an Existing Wallet

> Add your wallet's private key to your shell environment:
>
> ```bash
> export WALLET_PRIVATE_KEY=0x<your_private_key>
> ```
>
> Or add it to your `.env` file (make sure `.env` is in `.gitignore`):
>
> ```
> WALLET_PRIVATE_KEY=0x<your_private_key>
> ```

### Option B: Create a New Wallet

> Generate a new wallet and set it as an env var:
>
> ```bash
> export WALLET_PRIVATE_KEY=$(npx tsx -e "import { generatePrivateKey } from 'viem/accounts'; console.log(generatePrivateKey())")
> ```
>
> Save the output somewhere safe. Then derive the address:
>
> ```bash
> npx tsx -e "import { privateKeyToAccount } from 'viem/accounts'; console.log(privateKeyToAccount(process.env.WALLET_PRIVATE_KEY as \`0x\${string}\`).address)"
> ```

After the user has set the env var, restart the agent session so it picks up the new variable. Then proceed to [Fund the Wallet](#fund-the-wallet).

---

## Fund the Wallet

### Testnet (Base Sepolia)

1. Go to the [Circle USDC faucet](https://faucet.circle.com/)
2. Select **Base Sepolia**
3. Paste your wallet address
4. Request testnet USDC

The USDC will arrive at your address on Base Sepolia (`0x036CbD53842c5426634e7929541eC2318f3dCF7e`).

### Mainnet

Transfer USDC to your wallet address on Base Mainnet.

## Load the Wallet in Code

```typescript
import { privateKeyToAccount } from "viem/accounts";

const account = privateKeyToAccount(process.env.WALLET_PRIVATE_KEY as `0x${string}`);
```

Use this `account` for SIWE token generation (see [authentication](authentication.md)) and payment signing (see [making-requests](making-requests.md)).
