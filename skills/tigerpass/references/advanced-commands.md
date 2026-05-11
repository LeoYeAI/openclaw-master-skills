# Advanced Commands — Smart Contracts, Signing & x402

> Moved from SKILL.md for brevity. For quick command lookup, see the summary table in SKILL.md.

## Smart Contract Execution & On-Chain Reads

For protocols without a built-in command (AAVE, Compound, etc.), use the universal `exec` and `call` commands. Read `references/defi-cookbook.md` for step-by-step recipes.

```bash
# Execute any contract (write)
tigerpass exec --to 0xContract \
  --fn "transfer(address,uint256)" \
  --fn-args '["0xRecipient","1000000"]'

# Dry-run before real execution (simulate via eth_call, no gas spent)
tigerpass exec --to 0xContract \
  --fn "riskyFunction(uint256)" \
  --fn-args '["1000"]' --simulate

# Don't wait for confirmation
tigerpass exec --to 0xContract --fn "someFunction()" --no-wait

# Batch calls (up to 10, atomic on Safe — sequential with --eoa)
tigerpass exec --calls '[{"to":"0xA","value":"0x0","data":"0x..."},{"to":"0xB","value":"0x0","data":"0x..."}]'

# Execute from EOA instead of Safe (any chain)
tigerpass exec --to 0xContract --fn "someFunction()" --eoa

# Read any contract (no gas)
tigerpass call --to 0xContract --fn "balanceOf(address)" --fn-args '["0xAddr"]'
tigerpass call --to 0xContract --fn "balanceOf(address)" --fn-args '["0xAddr"]' --block 0x1234  # historical

# ERC-20 operations
tigerpass approve --token USDC --spender 0xRouter --amount 100
tigerpass approve --token USDC --spender 0xRouter --amount max   # unlimited
tigerpass allowance --token USDC --spender 0xRouter
tigerpass token-info --token USDC

# Event logs
tigerpass logs --address 0xContract --topic 0xddf252... --from-block 0x100

# ABI tools
tigerpass abi encode --sig "transfer(address,uint256)" --args '["0xAddr","1000000"]'
tigerpass abi decode --sig "(uint256)" --data 0x000...00f4240
```

## Signing

```bash
# Raw secp256k1 ECDSA (32-byte hash)
tigerpass sign --data 0x<32-byte-hex>

# EIP-191 personal message
tigerpass sign-message --message "Hello World"
tigerpass sign-message --hex 0x...               # binary message

# EIP-712 typed data
tigerpass sign-typed-data --data '{"types":{...},"primaryType":"...","domain":{...},"message":{...}}'
```

## x402 HTTP Payments

x402 lets you pay for HTTP APIs using your EOA (not Safe wallet). When an API returns HTTP 402, sign the payment and retry.

**x402 pays from your EOA — pre-fund it first:**

```bash
# 1. Get your EOA address
tigerpass init
# 2. Transfer USDC from your Safe to your EOA
tigerpass pay --to <eoaAddress> --amount 10
# 3. Verify your EOA has funds
tigerpass balance --eoa --token USDC
```

**Sign x402 payment:**

```bash
# Known token (USDC on Base) — domain auto-resolved
tigerpass sign-x402 \
  --pay-to 0xMerchant --amount 10000 \
  --asset 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  --chain-id 8453

# With custom timeout
tigerpass sign-x402 \
  --pay-to 0xMerchant --amount 10000 \
  --asset 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  --chain-id 8453 --max-timeout 600
```

**Full x402 flow:**

1. HTTP request → API returns 402 + `PAYMENT-REQUIRED` header (base64 JSON)
2. Decode header → extract `payTo`, `amount`, `asset`, `network`, `maxTimeoutSeconds`
3. `tigerpass sign-x402` with those fields → outputs PaymentPayload JSON
4. Base64-encode payload → set as `PAYMENT-SIGNATURE` header
5. Retry original request with the header → 200 OK
