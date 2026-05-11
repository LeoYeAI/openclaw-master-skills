# Limit Order Cancellation

All commands below assume CWD is `$SCRIPTS_DIR` and env is sourced. Each Bash block must begin with:

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
```

## 0. Pre-confirmation

Cancelling a limit order is an on-chain operation (gas required). Confirm before cancelling:
- orderHash
- Current order status (recommended: query first to avoid cancelling an already-filled or expired order)

## 1. Fetch Cancellation Parameters

**Preferred: use `--order-hash`** (auto-reads nonce from `~/.aurehub/orders/`):

```bash
CANCEL_PARAMS=$(node limit-order.js cancel \
  --order-hash "$ORDER_HASH")

WORD_POS=$(echo "$CANCEL_PARAMS" | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).wordPos")
MASK=$(echo "$CANCEL_PARAMS"     | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).mask")
```

Supports prefix matching (e.g. `0x9079c4f2` matches the full hash). Falls back to `--nonce` if no local order file is found.

**Fallback: use `--nonce` directly** (if local order file is missing):

```bash
CANCEL_PARAMS=$(node limit-order.js cancel \
  --nonce "$NONCE")
```

## 2. Execute Cancellation

Display the command and wait for user confirmation:

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
CANCEL_JSON=$(node swap.js cancel-nonce --word-pos "$WORD_POS" --mask "$MASK")
STATUS=$(echo "$CANCEL_JSON" | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).status")
TX_HASH=$(echo "$CANCEL_JSON" | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).txHash")
echo "Cancel tx: https://etherscan.io/tx/$TX_HASH"
if [ "$STATUS" != "success" ]; then echo "WARNING: on-chain cancellation failed (status=$STATUS)"; fi
```

## 3. Output

- tx hash
- Note: No assets were locked — Permit2 uses signature-based authorization, not asset custody. Cancellation revokes the signature on-chain; no token return operation is needed.

## 4. Special Cases

| Case | Action |
|------|--------|
| Order already filled | No cancellation needed; inform the user |
| Order already expired | Nonce has auto-invalidated; no on-chain cancellation needed |
| Cancel succeeds but Filler is still processing | Very low probability; the Filler transaction will revert once the nonce is invalidated on-chain |
