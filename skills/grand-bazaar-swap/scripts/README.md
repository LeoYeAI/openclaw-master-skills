# grand-bazaar-swap scripts

These scripts are intended as reference implementations.

## Install

In the folder where you run scripts:

```bash
npm i ethers@5 lz-string
```


## Swap routing by sender token kind

Scripts now auto-route to the correct Swap contract based on sender token kind:

- ERC20 sender kind `0x36372b07` -> `0x8a9969ed0A9bb3cDA7521DDaA614aE86e72e0A57`
- ERC721 sender kind `0x80ac58cd` -> `0x2aa29F096257bc6B253bfA9F6404B20Ae0ef9C4d`
- ERC1155 sender kind `0xd9b67a26` -> `0xD19783B48b11AFE1544b001c6d807A513e5A95cf`

Override behavior with `SWAP_ADDRESS` if you need a specific contract.

## Two agent flow

The order and signature move from signer to sender via Farcaster casts.
Use `GBZ1:<compressedOrder>` as the canonical transport/storage layer for order blobs.
Local JSON files are optional temporary artifacts for debugging or script input, not the durable source of truth.

### signer_make_order.js

Inputs
- SIGNER_PRIVATE_KEY
- SIGNER_TOKEN
- SIGNER_AMOUNT
- SENDER_TOKEN
- SENDER_AMOUNT
- SENDER_WALLET unless OPEN_ORDER=true

Optional
- OPEN_ORDER=true to allow anyone to take the order
- SWAP_ADDRESS to force a specific swap contract instead of auto-routing

Output
- order JSON file. Default `order.json`
- includes `airswapWeb.compressedOrder` using AirSwap Web compatible encoding
- includes `airswapWeb.orderPath` in the form `/order/<compressedOrder>` for sharing

Example

```bash
export SIGNER_PRIVATE_KEY=0x...
export SIGNER_TOKEN=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
export SIGNER_AMOUNT=0.994
export SENDER_TOKEN=0x4200000000000000000000000000000000000006
export SENDER_AMOUNT=0.001
export SENDER_WALLET=0xSenderAddress
node scripts/signer_make_order.js
```

### sender_execute_order.js

Inputs
- SENDER_PRIVATE_KEY
- IN_FILE. Default `order.json`

Optional
- RECIPIENT. Default sender wallet
- MAX_ROYALTY. Default 0
- MAX_GAS_LIMIT. Default 650000
- SWAP_ADDRESS to force a specific swap contract instead of payload/kind routing

Behavior
- Verifies signature and order invariants.
- Verifies signer balance and signer allowance before submit.
- Verifies sender balance and allowance before submit.
- Caps `maxPriorityFeePerGas` to 10% of current `gasPrice`.
- Estimates swap gas; if estimate fails but preflight checks pass, falls back to manual gas limit `MAX_GAS_LIMIT` default `650000`.
- Uses bounded `gasLimit` for execution.
- Fails early with a clear error if preflight is not satisfied.

Example

```bash
export SENDER_PRIVATE_KEY=0x...
node scripts/sender_execute_order.js
```

### make_cast_payload.js

Inputs
- IN_FILE. Default `order.json`
- AIRSWAP_WEB_BASE. Default `https://dex.airswap.xyz/#/order/`
- OUT_FILE optional. If omitted, prints JSON to stdout

Output
- `text` with human readable cast text
- `payload` with machine parsable fields and `airswapWeb.compressedOrder`
- `payload.airswapWeb.orderUrl` uses URL-encoded compressed order for reliable clicking
- `payload.miniapp.orderUrl` includes a Grand Bazaar deeplink by default

Notes for Farcaster posting
- API mentions should be sent via `mentions` and `mentions_positions`, not text-only `@handle`
- For private recipient orders, prefer recipient `verified_addresses.primary.eth_address` from Neynar
- Keep cast copy short when deeplinking to avoid long-cast byte overflows
- For cast-hash driven miniapp parsing, include a strict machine line:
  - `GBZ1:<compressedOrder>`
  - no spaces, single line, one occurrence only
- `make_cast_payload.js` now emits `GBZ1:<compressedOrder>` in `text` when compressed order is present

Example

```bash
node scripts/make_cast_payload.js > cast-payload.json
```

### post_cast_farcaster_agent.js

This script is intentionally disabled for security hardening.

Reason
- Avoid file-read + network-send script pattern inside shared skill code.
- This pattern can trigger code-safety `potential-exfiltration` warnings.

Use instead
- OpenClaw/Neynar posting flow from the runtime agent tools.

## test_weth_usdc_swap.js

This is a reference end to end test.
It uses two private keys at once.
That is convenient for testing.
It is not the desired production flow for two agents.

Notes
- Sender must have the sender token amount plus fee.
- Signer must have the signer asset.
- Both must have ETH for gas.
