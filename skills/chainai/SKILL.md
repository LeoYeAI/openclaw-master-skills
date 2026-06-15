---
name: chainai
description: 'Ethereum & EVM blockchain CLI skill — sign messages, send tokens, swap via 1inch Fusion, check balances, broadcast transactions, and manage wallets across Ethereum and BNB Smart Chain.'
metadata:
  author: kvhnuke
  version: 0.0.10
  openclaw:
    requires:
      env:
        - CHAINAI_PRIVATE_KEY
      bins:
        - npx
        - node
    primaryEnv: CHAINAI_PRIVATE_KEY
    emoji: '⧫'
    homepage: https://github.com/kvhnuke/chainai
    install:
      - kind: node
        package: chainai
        bins: [chainai]
---

# chainai — Ethereum Transactions Skill

> **⚠️ DISCLAIMER — USE AT YOUR OWN RISK**
>
> This tool interacts with real blockchain networks and real funds. The author(s) of this tool are **not responsible for any loss of funds**, damages, or unintended consequences arising from its use. By using this skill, you accept full responsibility for all operations performed.

> **🔒 MANDATORY SECURITY REQUIREMENTS FOR ALL AGENTS**
>
> Agents **MUST** take every possible action to safeguard `CHAINAI_PRIVATE_KEY` and all other private keys from exposure. Specifically:
>
> 1. **NEVER log, print, echo, or display private keys** in any user-facing output, logs, chat messages, or debug traces.
> 2. **NEVER store private keys** in plain text files, version control, or any persistent storage that is not explicitly encrypted and access-controlled.
> 3. **NEVER transmit private keys** over unencrypted channels or include them in URLs, query parameters, or request bodies to third-party services.
> 4. **NEVER include private keys** in error messages, stack traces, or diagnostic output.
> 5. **ALWAYS prefer the `CHAINAI_PRIVATE_KEY` environment variable** over the `-k` flag to minimize key exposure in shell history and process listings.
> 6. **ALWAYS treat private keys as the highest-sensitivity secret.** A leaked private key grants full, irrevocable control over all funds in the associated wallet.

> **� ADDRESS FORMATTING RULES**
>
> 1. **Always use ERC-55 checksum addresses** when passing addresses to any command (wallet addresses, token contract addresses, recipient addresses, etc.).
> 2. **If you do not know the correct checksum**, use **all lowercase** addresses (e.g. `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` instead of guessing the mixed-case checksum).
> 3. **Never guess a token contract address.** If you are unsure of the correct token contract address, **always ask the user** to provide it. Do not fabricate or assume token addresses.

> **�🚀 BEFORE YOU BEGIN**
>
> 1. **Verify your private key is set**: Run `npx chainai@0.0.10 who-am-i` to confirm `CHAINAI_PRIVATE_KEY` is properly configured and resolves to the expected address before proceeding with any other command.
> 2. **No private key?** Use `npx chainai@0.0.10 gen-wallet` to generate a new wallet. Save the returned private key securely (e.g. as an environment variable) — it will not be shown again.
> 3. **Fund your account**: You must deposit the necessary funds (native tokens for gas + any tokens you intend to send or swap) to the wallet address before using `send`, `swap`, or any transaction-submitting command. Commands will fail if the account has insufficient balance.

## Overview

`chainai` is a non-interactive CLI tool for Ethereum and EVM-compatible blockchain operations. It handles signing, sending, broadcasting transactions, token swaps (1inch Fusion), balance queries, and wallet generation.

## Invocation

```
npx chainai@0.0.10 <command> [options]
```

- **Runtime**: Node.js (>=18)
- **Non-interactive**: All parameters must be passed as arguments or flags. Never prompts for input.

## Authentication

Most commands accept a private key via:

- `-k, --private-key <key>` flag (hex string starting with `0x`)
- `CHAINAI_PRIVATE_KEY` environment variable (fallback when `-k` is not provided)

## Supported Networks

| Name            | Chain ID | Aliases                      | Native Token |
| --------------- | -------- | ---------------------------- | ------------ |
| Ethereum        | 1        | `mainnet`, `ethereum`, `eth` | ETH          |
| BNB Smart Chain | 56       | `bsc`, `binance`, `bnb`      | BNB          |

Use `-n, --network` to specify a network by name, alias, or chain ID. Defaults to `mainnet`.

## Exit Codes

| Code | Meaning                                                            |
| ---- | ------------------------------------------------------------------ |
| `0`  | Operation completed successfully.                                  |
| `1`  | Operation failed. Inspect `stderr` for a structured error message. |

## Message Contract

### Success (stdout)

```
CHAINAI_OK: <description>
{ ... }
```

### Errors (stderr)

```
CHAINAI_ERR: <ERROR_CODE> — <description>
```

| Error Code         | Description                                                             | Agent Action                                         |
| ------------------ | ----------------------------------------------------------------------- | ---------------------------------------------------- |
| `INVALID_INPUT`    | Malformed or missing required fields.                                   | Re-validate input parameters and retry.              |
| `EXECUTION_FAILED` | Operation could not be completed. Description contains failure details. | Inspect description and adjust approach.             |
| `TIMEOUT`          | Operation exceeded the allowed time limit.                              | Retry with a longer timeout or simplify the request. |
| `UNKNOWN`          | Unexpected error.                                                       | Report to orchestrator for manual inspection.        |

## Retry Strategy

For `TIMEOUT` and `EXECUTION_FAILED` errors, retry up to 2 times with exponential backoff before escalating.

---

## Commands

### `gen-wallet`

Generate a new random wallet (private key and address).

```bash
npx chainai@0.0.10 gen-wallet
```

**Options**: None.

**Output (stdout)**:

```json
{
  "address": "0x...",
  "privateKey": "0x..."
}
```

Usage instructions are printed to `stderr`.

---

### `who-am-i`

Return the Ethereum address derived from a private key.

```bash
npx chainai@0.0.10 who-am-i -k 0xKEY
# or
CHAINAI_PRIVATE_KEY=0xKEY npx chainai@0.0.10 who-am-i
```

**Options**:

| Flag                      | Required | Description                                       |
| ------------------------- | -------- | ------------------------------------------------- |
| `-k, --private-key <key>` | No       | Private key. Falls back to `CHAINAI_PRIVATE_KEY`. |

**Output (stdout)**:

```json
{
  "address": "0x..."
}
```

---

### `sign-message`

Sign a message using EIP-191 personal sign.

```bash
npx chainai@0.0.10 sign-message -k 0xKEY -m "Hello World"
npx chainai@0.0.10 sign-message -k 0xKEY -m 0x68656c6c6f --raw
```

**Options**:

| Flag                      | Required | Description                                       |
| ------------------------- | -------- | ------------------------------------------------- |
| `-k, --private-key <key>` | No       | Private key. Falls back to `CHAINAI_PRIVATE_KEY`. |
| `-m, --message <message>` | Yes      | The message to sign.                              |
| `-r, --raw`               | No       | Treat message as raw hex data (`0x`-prefixed).    |

**Output (stdout)**:

```json
{
  "address": "0x...",
  "message": "<original message>",
  "signature": "0x..."
}
```

---

### `sign`

> **⚠️ CRITICAL SECURITY WARNING**: Signs a raw hash (secp256k1) without any prefix. The resulting signature can authorize any on-chain action. **Use `sign-message` instead unless raw hash signing is explicitly required.** Before using, verify the hash is legitimate and no safer alternative exists.

```bash
npx chainai@0.0.10 sign -k 0xKEY -h 0xHASH
```

**Options**:

| Flag                      | Required | Description                                       |
| ------------------------- | -------- | ------------------------------------------------- |
| `-k, --private-key <key>` | No       | Private key. Falls back to `CHAINAI_PRIVATE_KEY`. |
| `-h, --hash <hash>`       | Yes      | The hash to sign (`0x`-prefixed hex string).      |

**Output (stdout)**:

```json
{
  "address": "0x...",
  "hash": "0x...",
  "signature": "0x..."
}
```

---

### `sign-typed-data`

Sign EIP-712 typed data.

```bash
npx chainai@0.0.10 sign-typed-data -k 0xKEY -d '<json>'
```

**Options**:

| Flag                      | Required | Description                                                                  |
| ------------------------- | -------- | ---------------------------------------------------------------------------- |
| `-k, --private-key <key>` | No       | Private key. Falls back to `CHAINAI_PRIVATE_KEY`.                            |
| `-d, --data <json>`       | Yes      | EIP-712 typed data as JSON with `domain`, `types`, `primaryType`, `message`. |

**Data Format**:

```json
{
  "domain": {
    "name": "AppName",
    "version": "1",
    "chainId": 1,
    "verifyingContract": "0x..."
  },
  "types": { "TypeName": [{ "name": "fieldName", "type": "fieldType" }] },
  "primaryType": "TypeName",
  "message": { "fieldName": "value" }
}
```

**Output (stdout)**:

```json
{
  "address": "0x...",
  "signature": "0x..."
}
```

---

### `sign-transaction`

Sign a transaction (legacy, EIP-2930, or EIP-1559). Returns a serialized signed transaction ready to broadcast.

```bash
npx chainai@0.0.10 sign-transaction -k 0xKEY -t '<json>'
```

**Options**:

| Flag                       | Required | Description                                       |
| -------------------------- | -------- | ------------------------------------------------- |
| `-k, --private-key <key>`  | No       | Private key. Falls back to `CHAINAI_PRIVATE_KEY`. |
| `-t, --transaction <json>` | Yes      | Transaction object as JSON string.                |

**Transaction Formats**:

Legacy:

```json
{
  "to": "0x...",
  "value": "1000000000000000000",
  "gasPrice": "20000000000",
  "gas": "21000",
  "nonce": 0,
  "chainId": 1
}
```

EIP-1559:

```json
{
  "to": "0x...",
  "value": "1000000000000000000",
  "maxFeePerGas": "30000000000",
  "maxPriorityFeePerGas": "1000000000",
  "gas": "21000",
  "nonce": 0,
  "chainId": 1
}
```

Omit `to` for contract deployment. Numeric values can be strings or numbers.

**Output (stdout)**:

```json
{
  "address": "0x...",
  "serializedTransaction": "0x..."
}
```

---

### `get-balance`

Get native or ERC-20 token balances.

```bash
npx chainai@0.0.10 get-balance -a 0xADDRESS
npx chainai@0.0.10 get-balance -a 0xADDRESS -n bsc
npx chainai@0.0.10 get-balance -a 0xADDRESS -t 0xTOKEN_CONTRACT
npx chainai@0.0.10 get-balance -a 0xADDRESS --all
```

**Options**:

| Flag                      | Required | Description                                                                             |
| ------------------------- | -------- | --------------------------------------------------------------------------------------- |
| `-a, --address <address>` | No       | Wallet address. Falls back to address derived from `CHAINAI_PRIVATE_KEY`.               |
| `-n, --network <network>` | No       | Network (default: `mainnet`).                                                           |
| `-t, --token <token>`     | No       | Token contract address. Default: `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee` (native). |
| `--all`                   | No       | Return all token balances (native + ERC-20). `-t` is ignored when set.                  |

**Output (stdout)** — single token:

```json
{
  "address": "0x...",
  "network": "Ethereum",
  "token": "ETH",
  "balance": "1.5",
  "rawBalance": "1500000000000000000",
  "decimals": 18,
  "contract": null
}
```

With `--all`, returns an array of balance objects.

---

### `send`

Build and sign a transaction to send native tokens or ERC-20 tokens. Automatically fetches nonce, gas, and fee data from the network.

```bash
npx chainai@0.0.10 send -k 0xKEY --to 0xRECIPIENT --amount 1.5 -t 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
npx chainai@0.0.10 send -k 0xKEY --to 0xRECIPIENT --amount 100 -t 0xTOKEN_CONTRACT -n bsc
```

**Options**:

| Flag                      | Required | Description                                                                          |
| ------------------------- | -------- | ------------------------------------------------------------------------------------ |
| `-k, --private-key <key>` | No       | Private key. Falls back to `CHAINAI_PRIVATE_KEY`.                                    |
| `--to <address>`          | Yes      | Recipient address.                                                                   |
| `-t, --token <token>`     | Yes      | Token contract address. Use `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee` for native. |
| `--amount <amount>`       | Yes      | Amount in human-readable units (e.g. `"1.5"`).                                       |
| `-n, --network <network>` | No       | Network (default: `mainnet`).                                                        |
| `-b, --broadcast`         | No       | Automatically broadcast after signing.                                               |

**Output (stdout)**:

```json
{
  "from": "0x...",
  "to": "0x...",
  "token": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "amount": "1.5",
  "network": "Ethereum",
  "serializedTransaction": "0x..."
}
```

---

### `broadcast`

Broadcast a serialized signed transaction to the network.

```bash
npx chainai@0.0.10 broadcast -s 0xSERIALIZED_TX
npx chainai@0.0.10 broadcast -s 0xSERIALIZED_TX -n bsc
```

**Options**:

| Flag                                 | Required | Description                                    |
| ------------------------------------ | -------- | ---------------------------------------------- |
| `-s, --serialized-transaction <hex>` | Yes      | Serialized signed transaction (`0x`-prefixed). |
| `-n, --network <network>`            | No       | Network (default: `mainnet`).                  |

**Output (stdout)**:

```json
{
  "transactionHash": "0x...",
  "network": "Ethereum",
  "explorerUrl": "https://etherscan.io/tx/0x..."
}
```

---

### `tx-status`

Get the status of a transaction by hash.

```bash
npx chainai@0.0.10 tx-status -h 0xTX_HASH
npx chainai@0.0.10 tx-status -h 0xTX_HASH -n bsc
```

**Options**:

| Flag                      | Required | Description                                 |
| ------------------------- | -------- | ------------------------------------------- |
| `-h, --hash <hash>`       | Yes      | Transaction hash (`0x`-prefixed, 32 bytes). |
| `-n, --network <network>` | No       | Network (default: `mainnet`).               |

**Output (stdout)**:

```json
{
  "transactionHash": "0x...",
  "status": "success",
  "network": "Ethereum",
  "blockNumber": "12345678",
  "from": "0x...",
  "to": "0x...",
  "gasUsed": "21000",
  "effectiveGasPrice": "30000000000",
  "explorerUrl": "https://etherscan.io/tx/0x..."
}
```

For pending transactions, `status` is `"pending"` and `blockNumber`, `from`, `to`, `gasUsed`, `effectiveGasPrice` will be `null`.

---

### `swap`

Swap tokens via 1inch Fusion. Gets a quote first, then optionally submits the order. Use `-y` to skip confirmation and submit immediately.

```bash
npx chainai@0.0.10 swap -k 0xKEY --from-token 0xFROM --to-token 0xTO --amount 1.5
npx chainai@0.0.10 swap -k 0xKEY --from-token 0xFROM --to-token 0xTO --amount 1.5 -y
npx chainai@0.0.10 swap -k 0xKEY --from-token 0xFROM --to-token 0xTO --amount 0.5 -n bsc
```

Use `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee` for native tokens.

**Options**:

| Flag                      | Required | Description                                       |
| ------------------------- | -------- | ------------------------------------------------- |
| `-k, --private-key <key>` | No       | Private key. Falls back to `CHAINAI_PRIVATE_KEY`. |
| `--from-token <address>`  | Yes      | Source token contract address.                    |
| `--to-token <address>`    | Yes      | Destination token contract address.               |
| `--amount <amount>`       | Yes      | Amount in human-readable units (e.g. `"1.5"`).    |
| `-n, --network <network>` | No       | Network (default: `mainnet`).                     |
| `-y, --yes`               | No       | Skip confirmation prompt and submit immediately.  |

**Output (stdout)** — quote:

```json
{
  "from": "0x...",
  "fromToken": "0x...",
  "toToken": "0x...",
  "amount": "1.5",
  "estimatedReturn": "1500",
  "estimatedReturnMin": "1400",
  "estimatedReturnAvg": "1450",
  "network": "Ethereum"
}
```

**Output (stdout)** — order submission:

```json
{
  "from": "0x...",
  "fromToken": "0x...",
  "toToken": "0x...",
  "amount": "1.5",
  "estimatedReturn": "1500",
  "estimatedReturnMin": "1400",
  "estimatedReturnAvg": "1450",
  "network": "Ethereum",
  "orderHash": "0x...",
  "approvalTxHash": "0x..."
}
```

`approvalTxHash` is non-null only when an ERC-20 token approval was required. For native token swaps or already-approved tokens, it is `null`.

---

### `swap-order-status`

Get the status of a 1inch Fusion swap order by its order hash.

```bash
npx chainai@0.0.10 swap-order-status -k 0xKEY --order-hash 0xORDER_HASH
npx chainai@0.0.10 swap-order-status -k 0xKEY --order-hash 0xORDER_HASH -n bsc
```

**Options**:

| Flag                      | Required | Description                                       |
| ------------------------- | -------- | ------------------------------------------------- |
| `-k, --private-key <key>` | No       | Private key. Falls back to `CHAINAI_PRIVATE_KEY`. |
| `--order-hash <hash>`     | Yes      | Order hash returned from the `swap` command.      |
| `-n, --network <network>` | No       | Network (default: `mainnet`).                     |

**Output (stdout)**:

```json
{
  "orderHash": "0x...",
  "status": "filled",
  "network": "Ethereum",
  "createdAt": 1700000000,
  "duration": 180,
  "fills": [{ "txHash": "0x..." }],
  "cancelTx": null,
  "finalToAmount": "1500000000"
}
```

Possible `status` values: `"pending"`, `"filled"`, `"expired"`, `"cancelled"`. For pending/cancelled orders, `finalToAmount` is `null` and `fills` is empty.
