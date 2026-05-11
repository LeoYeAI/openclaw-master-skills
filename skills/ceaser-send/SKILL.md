---
name: ceaser-send
description: Fully automated private ETH transfer via Ceaser Protocol on Base L2 using the ceaser-mcp MCP tools. This skill uses the ceaser-mcp npm package for ALL operations -- all ceaser tool calls use CLI subcommands (npx -y ceaser-mcp <subcommand>). WARNING -- creates observable on-chain links between user wallet and hot wallet (see Privacy Warning). Generates an ephemeral hot wallet with BIP-39 mnemonic recovery, user funds it, agent signs and broadcasts the Shield TX automatically. Exactly one manual step required (funding the hot wallet with ETH). Uses Noir/UltraHonk zero-knowledge proofs.
user-invocable: true
allowed-tools: Bash
homepage: https://ceaser.org
metadata: { "openclaw": { "requires": { "bins": ["curl", "jq", "node", "npx"] }, "homepage": "https://ceaser.org" } }
---

# Ceaser Private Send

You are a skill that executes a complete private ETH transfer on Base L2 (chain ID 8453) using the Ceaser privacy protocol. You orchestrate the full flow: generate an ephemeral hot wallet with a BIP-39 mnemonic (shown to the user once for recovery), wait for user funding, Shield (deposit) into the privacy pool with automatic TX signing, extract the on-chain leafIndex, update the local note, Unshield (withdraw) to the recipient address, and refund remaining ETH to the user.

**Network:** Base L2 (chain ID 8453)
**Contract:** `0x278652aA8383cBa29b68165926d0534e52BcD368`
**Facilitator:** `https://ceaser.org`
**Protocol Fee:** 0.25% (25 bps) per operation
**Valid Denominations:** 0.001, 0.01, 0.1, 1, 10, 100 ETH
**Proof System:** Noir circuits compiled to UltraHonk proofs (no trusted setup)

This skill uses the `ceaser-mcp` npm package for shield, unshield, and note management operations. All ceaser tool calls use CLI subcommands:

```bash
npx -y ceaser-mcp <subcommand> [args]
```

Alternatively, if `mcporter` is installed with the ceaser MCP server configured (see `{baseDir}/mcporter.json`), you may use `mcporter call ceaser.TOOL_NAME` as an equivalent method. CLI is the primary and recommended approach.

Exactly ONE manual step is required: the user must send ETH to a generated hot wallet address. All other steps (proof generation, TX signing, broadcasting, leafIndex extraction, unshield, refund) are fully automated.

---

## PRIVACY WARNING

Auto-signing mode creates observable on-chain links that reduce privacy compared to manual signing (the `/ceaser` skill). Specifically:

1. **Funding link**: The user's main wallet (A) sends ETH to the hot wallet (H). This transfer is publicly visible on-chain, linking A to H.
2. **Shield link**: The hot wallet (H) calls `shieldETH()` on the contract. H is now linked to the shield deposit.
3. **Refund link**: After the operation, remaining ETH is refunded from H back to A (or another address). This creates another public link.
4. **Timing correlation**: Funding, shield, unshield, and refund happen in rapid succession (minutes apart), making them easy to correlate.
5. **Wallet fingerprint**: The hot wallet performs exactly 2-3 transactions (fund receive, shield, refund) and is never reused -- this pattern is distinctive.

**Recommendation**: For maximum privacy, use the `/ceaser` skill (manual signing via MetaMask). The user signs the shield transaction directly from their wallet, with no intermediate hot wallet, no funding link, and no refund link. Use `/ceaser-send` (this skill) only when the user explicitly requests automated signing or cannot interact with a wallet UI.

---

## Prerequisites

Before executing this skill, verify:

1. **node** and **npx** are installed (for ceaser-mcp CLI and wallet-ops helper)
2. **curl** and **jq** are installed (for TX receipt parsing and notes.json manipulation)
3. **node_modules** are installed in the skill directory (test: `node {baseDir}/helpers/wallet-ops.js --help`)
4. User has a **wallet** capable of sending ETH on Base Mainnet (for funding the hot wallet)
5. Wallet has enough **ETH** for the desired amount + 0.25% protocol fee + ~0.0005 ETH gas reserve

---

## Pre-Flight Checks

Execute ALL of these checks BEFORE starting the flow. Abort if any check fails.

### Check 1: Facilitator Status

Run:

```bash
curl -s "https://ceaser.org/status" | jq .
```

Verify:
- Facilitator is operational (response received without error)
- `circuitBreaker.tripped` is `false`
- `indexer.synced` is `true`
- Facilitator has enough balance for gas (balance > 0.001 ETH)

If the facilitator is down or circuit breaker is tripped, inform the user and abort.

### Check 2: Denomination Validation

Run:

```bash
curl -s "https://ceaser.org/api/ceaser/denominations" | jq .
```

Verify:
- The user's requested amount is in the denominations list
- Valid: 0.001, 0.01, 0.1, 1, 10, 100 ETH

If the amount is not a valid denomination, show the user the valid options and ask them to choose.

### Check 3: Fee Calculation

Run:

```bash
curl -s "https://ceaser.org/api/ceaser/fees/AMOUNT_WEI" | jq .
```

Replace `AMOUNT_WEI` with the amount in wei (e.g., `1000000000000000` for 0.001 ETH).

Present to the user:
- Gross amount (what they send)
- Protocol fee (0.25%)
- Net amount (what the recipient receives after unshield fee)
- Note: Fees apply on BOTH shield and unshield. Total round-trip fee is approximately 0.5%.

Store internally: `amountWei` and `feeWei` from the response (needed for funding calculation in Wallet Generation Phase).

Ask the user to confirm they want to proceed.

### Check 4: Recipient Address Validation

Validate the recipient address format: must match `/^0x[0-9a-fA-F]{40}$/`.

If invalid, inform the user and ask for a correct Ethereum address.

### Check 5: Existing Notes

Run:

```bash
npx -y ceaser-mcp notes
```

Check for existing unspent notes:

- **If unspent notes with valid leafIndex exist:** Ask the user whether to use an existing note (skip shield, go directly to unshield) or create a new shield.
- **If unspent notes with leafIndex=null exist:** Inform the user: "A note exists but its leafIndex is missing. The shield transaction may not have confirmed yet. If you have the TX hash, we can extract the leafIndex."
- **If no suitable notes exist:** Proceed with the full Shield flow.

### Check 6: Helper Script Availability

Run:

```bash
node {baseDir}/helpers/wallet-ops.js --help
```

Verify: valid JSON output listing available commands (generate, balance, sign-and-send, refund).

If this check fails: inform the user and abort. Message: "Helper script not available. Please run `npm install` in the skill directory."

---

## Flow Decision

Based on Pre-Flight Check 5:

**Path A -- Use Existing Note:**
If the user wants to use an existing unspent note with a valid leafIndex, skip directly to the **Unshield Phase**.

**Path B -- Update Existing Note:**
If a note has leafIndex=null and the user has the TX hash, skip to the **TX Confirmation and leafIndex Extraction** phase.

**Path C -- Full Shield Flow:**
No suitable note exists. Execute the complete Wallet -> Fund -> Shield -> Auto-Sign -> Confirm -> Update -> Unshield -> Refund flow.

---

## Wallet Generation Phase

**Only execute for Path C (Full Shield Flow).**

### Step 1: Generate Hot Wallet

Run:

```bash
node {baseDir}/helpers/wallet-ops.js generate
```

Store internally (in your working context):
- `mnemonic` -- The 12-word BIP-39 recovery phrase.
- `address` -- The hot wallet address to show the user.

### Step 1.5: Show Mnemonic to User

**IMPORTANT:** Show the mnemonic to the user EXACTLY ONCE with a clear security warning:

> **RECOVERY MNEMONIC (save this securely):**
>
> `word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12`
>
> **SAVE THIS MNEMONIC SECURELY.** It controls the hot wallet funds.
> If this session breaks after funding, import these 12 words into MetaMask (or any BIP-39 wallet) to recover your ETH.
> Do NOT share this mnemonic. Anyone with these words can access the hot wallet.

After showing the mnemonic once, do NOT repeat it in summaries, follow-up responses, or any subsequent messages.

### Step 2: Calculate Funding Amount

Use the fee data from Pre-Flight Check 3:
- Shield cost: `amountWei` + `feeWei` from `ceaser_get_fees` response
- Gas reserve: 500000000000000 wei (0.0005 ETH -- conservative, covers ~500k gas at 1 gwei on Base L2)
- Total funding = (`amountWei` + `feeWei`) + 500000000000000

Convert total funding to ETH for display. Round UP to a human-friendly value if needed.

### Step 3: Ask for Refund Address

Before showing the funding instructions, ask the user:
> "Where should I send any remaining ETH after the operation? Please provide your wallet address for the refund."

Store the refund address internally. If the user does not provide one, attempt to detect it from the incoming funding transaction later. If detection fails, ask again after the shield completes.

Note: If the session breaks after funding, the user can also recover hot wallet funds by importing the mnemonic into MetaMask.

### Step 4: Show Funding Instructions

Present to the user:

> **Hot Wallet Address:** `HOT_WALLET_ADDRESS`
>
> **Send exactly:** `FUNDING_AMOUNT` ETH (or slightly more)
>
> **Network:** Base Mainnet (Chain ID 8453)
>
> Send EXACTLY the specified amount or slightly more. Sending less will cause the shield to fail. Any excess ETH will be automatically refunded after completion.
>
> If you lose the mnemonic, you cannot recover funds from this wallet. The mnemonic will NOT be shown again.
> In case of session interruption, use the mnemonic to recover funds via MetaMask.

---

## Balance Monitoring Phase

**Only execute for Path C, after showing funding instructions.**

### Polling Logic

Repeatedly execute:

```bash
node {baseDir}/helpers/wallet-ops.js balance --address HOT_WALLET_ADDRESS
```

- Polling interval: 10 seconds
- Check: `balanceWei` >= required funding amount (in wei)
- Maximum polling duration: 10 minutes (60 cycles)

### Cancel Handling

The user can say "cancel" or "abbrechen" at any time during the funding wait.

- **Cancel BEFORE funding (balance == 0):** Clean abort. No loss. Key discarded.
- **Cancel AFTER partial funding (balance > 0):** Execute refund to user's address first, then abort.

To refund on cancel:

```bash
CEASER_HOT_MNEMONIC="MNEMONIC_PHRASE" node {baseDir}/helpers/wallet-ops.js refund --recipient REFUND_ADDRESS --rpc https://mainnet.base.org
```

### Timeout Handling

- After 5 minutes without funding: Remind user: "Still waiting for ETH at `HOT_WALLET_ADDRESS`..."
- After 10 minutes: Abort with clear message.
- On abort with balance > 0: Automatic refund to user address.
- On abort with balance == 0: Clean abort, no loss.
- Warning on timeout: "If you saved the mnemonic, you can still recover funds via MetaMask. Otherwise, do not send ETH after the timeout."

### Partial Funding

If balance > 0 but less than required:
> "Received: X ETH. Required: Y ETH. Please send an additional Z ETH."

Continue polling.

### Funding Confirmed

When balance >= required amount:
> "Funding received. Proceeding with Shield operation."

If the user provided excess ETH:
> "Received more ETH than required. Excess will be refunded after completion."

---

## Shield Phase

Run:

```bash
npx -y ceaser-mcp shield USER_AMOUNT
```

Replace USER_AMOUNT with the ETH denomination (e.g., `0.1`).

### Expected Response Fields

- `note.id` -- Internal ID for later reference
- `note.commitment` -- bytes32 commitment hash
- `note.leafIndex` -- Will be `null` (expected)
- `unsignedTx.to` -- Must be `0x278652aA8383cBa29b68165926d0534e52BcD368`
- `unsignedTx.data` -- ABI-encoded calldata
- `unsignedTx.value` -- Amount + fee in wei
- `unsignedTx.chainId` -- Must be `8453`
- `backup` -- Base64-encoded backup string (SECURITY CRITICAL)
- `instructions` -- Array of guidance messages

### Validation

Verify after receiving the response:
- `unsignedTx.value` from shield response matches (`amountWei` + `feeWei`) from `ceaser_get_fees`
- `unsignedTx.chainId` == 8453
- `unsignedTx.to` == `0x278652aA8383cBa29b68165926d0534e52BcD368`

### Backup String Handling

**SECURITY CRITICAL:**
- Show the backup string to the user EXACTLY ONCE with a clear warning:
  > **SAVE THIS BACKUP STRING SECURELY. It contains your private ZK secrets (secret + nullifier). Anyone with this string can withdraw your shielded ETH. Store it offline. Do not share it.**
- Do NOT repeat the backup string in subsequent messages.
- Do NOT include the backup string in summaries or follow-up responses.

### Internal State

Remember these values for later steps (keep in your working context, do not output again):
- `note.id`
- `note.commitment`
- `backup` (needed for leafIndex update)
- `pendingTxFile` (path to the saved unsigned TX -- auto-detected by sign-and-send, no need to pass manually)

### Shield Error After Funding (Edge Case)

If `ceaser_shield_eth` fails (proof error, facilitator down, etc.):
- ETH is still in the hot wallet (untouched)
- Retry up to 2 times
- If failure persists: automatic refund to user address
- Inform user: "Shield proof generation failed. Your ETH has been refunded."

---

## Automatic TX Signing Phase

**This replaces the previous manual signing phase.** The agent signs and broadcasts the Shield TX automatically using the mnemonic-derived hot wallet.

### Execute Sign-and-Send

The `ceaser-mcp shield` command automatically saves the unsigned transaction to `~/.ceaser-mcp/pending-tx.json`. The sign-and-send helper auto-detects this file, so you do NOT need to pass the transaction data as a CLI argument.

Run:

```bash
CEASER_HOT_MNEMONIC="MNEMONIC_PHRASE" node {baseDir}/helpers/wallet-ops.js sign-and-send --rpc https://mainnet.base.org
```

The helper automatically reads the unsigned TX from `~/.ceaser-mcp/pending-tx.json` and deletes the file after a successful send.

Where:
- `MNEMONIC_PHRASE`: The 12-word mnemonic from Wallet Generation Phase (passed via environment variable, NEVER as CLI argument)

**Alternative:** You can also specify the file explicitly or pass the JSON directly:

```bash
# Explicit file path
CEASER_HOT_MNEMONIC="..." node {baseDir}/helpers/wallet-ops.js sign-and-send --unsigned-tx-file ~/.ceaser-mcp/pending-tx.json --rpc https://mainnet.base.org

# Legacy: pass JSON directly (NOT recommended -- the data field is 4000-9000 chars)
CEASER_HOT_MNEMONIC="..." node {baseDir}/helpers/wallet-ops.js sign-and-send --unsigned-tx 'JSON_STRING' --rpc https://mainnet.base.org
```

**IMPORTANT:** Do NOT pass the `unsignedTx` JSON as a CLI argument unless absolutely necessary. The `data` field contains 4000-9000 characters of hex-encoded ZK proof, which can cause issues with shell argument handling. Always prefer the automatic file-based approach.

**Security notes:**
- Mnemonic is passed via environment variable (`CEASER_HOT_MNEMONIC`), NOT as a CLI argument
- BIP-39 mnemonic words contain only ASCII lowercase letters (a-z), no shell special characters
- The pending-tx.json file is created with 0600 permissions and deleted after successful send

Set exec timeout: 60 seconds (covers gas estimation + signing + broadcasting + 1 block confirmation).

### Process TX Result

- **Success** (`status == 1`): Extract `txHash`, proceed to TX Confirmation phase.
- **"insufficient funds"**: Inform user. Show required vs. available balance. Suggest sending more ETH.
- **"execution reverted"**: Inform user. Possible causes: invalid proof, denomination mismatch, contract pause.
- **"nonce too low"**: Handled automatically by the helper script (retry with fresh nonce).
- **Timeout / no confirmation**: TX may still be pending. Extract `txHash` if available and proceed to manual confirmation check.

---

## TX Confirmation and leafIndex Extraction

Using the `txHash` from the automatic sign-and-send operation, extract the leafIndex from the on-chain Shield event.

**Note:** The helper script already waits for 1 block confirmation. In most cases, the receipt is already available. The steps below serve as verification and leafIndex extraction.

### Step 1: Fetch TX Receipt

Use Bash to query the Base Mainnet RPC:

```bash
curl -s -X POST https://mainnet.base.org \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getTransactionReceipt","params":["TX_HASH"],"id":1}' | jq '.result'
```

Replace `TX_HASH` with the actual hash.

### Step 2: Check TX Status

- `status == "0x1"`: Success. Continue to Step 3.
- `status == "0x0"`: TX failed on-chain. Inform the user: "Transaction reverted. Possible causes: insufficient funds, gas limit too low, or contract error." Attempt refund of remaining hot wallet balance.
- `status == null` or no result: TX still pending. Wait 10 seconds and retry. Maximum 5 retries. If still pending, inform the user and provide the TX hash for manual checking.

### Step 3: Find Shield Event in Logs

Search the `logs` array for an entry matching:
- `address` == `0x278652aa8383cba29b68165926d0534e52bcd368` (case-insensitive)
- `topics[0]` == `0x39b0d8da40fd574f8fb61ef14d4f466fb3bceb268547c27680755e9b08fd8677` (Shield event signature)

If no matching log found: "No Shield event found in this transaction. This may not be a Shield transaction. Please verify the TX hash." Abort.

### Step 4: Extract leafIndex

The Shield event structure:
- `topics[0]`: Event signature hash
- `topics[1]`: `commitment` (indexed, bytes32)
- `topics[2]`: `assetId` (indexed, uint256)
- `data`: ABI-encoded `(uint32 leafIndex, uint256 timestamp)`

Extract leafIndex from data:

```bash
# data is hex string like 0x000000000000000000000000000000000000000000000000000000000000000600000000...
# First 32 bytes (64 hex chars after 0x) = leafIndex (uint32 zero-padded)
LEAF_INDEX_HEX=$(echo "DATA_FIELD" | cut -c3-66)
LEAF_INDEX=$(node -e "console.log(parseInt('0x$LEAF_INDEX_HEX', 16))")
```

### Step 5: Validate Commitment

Extract `topics[1]` from the log and compare against the stored `note.commitment`.

**CRITICAL:** If the commitment does not match, WARN the user: "The Shield event commitment does not match the generated note. This TX hash may belong to a different shield operation. Aborting leafIndex extraction to prevent data corruption."

### Step 6: Validate leafIndex

The extracted leafIndex must be a non-negative integer. If it is `NaN` or negative, abort with an error.

### Edge Case: Multiple Shield Events

If the TX contains multiple Shield events (unusual but possible in batch operations), use the commitment match from Step 5 to identify the correct event.

---

## Note Update (notes.json Workaround)

The shield tool stores the note with `leafIndex=null`. The unshield tool requires `leafIndex != null`. No MCP tool exists for updating the leafIndex directly. This workaround uses Bash to manipulate the backup string and notes.json.

### Why This Is Necessary

- `ceaser_shield_eth` saves note with `leafIndex=null` (TX not yet sent at proof time)
- `ceaser_unshield` requires `leafIndex != null` (needed for Merkle proof)
- `ceaser_import_note` rejects duplicates by commitment (including spent notes)
- Old entry must be PHYSICALLY removed from notes.json before re-import

### Step 1: Decode Backup String

```bash
echo "BACKUP_STRING" | base64 -d
```

This yields a JSON object with fields: `s` (secret), `n` (nullifier), `a` (amount), `am` (amountWei), `c` (commitment), `i` (leafIndex -- currently null), `ai` (assetId), `as` (assetSym), `ad` (contractAddress).

### Step 2: Update leafIndex in Backup

```bash
UPDATED_JSON=$(echo "BACKUP_STRING" | base64 -d | jq --argjson idx LEAF_INDEX '.i = $idx')
```

Replace `LEAF_INDEX` with the extracted decimal value. This sets the `i` field from `null` to the actual leafIndex.

### Step 3: Re-encode to Base64

```bash
UPDATED_BACKUP=$(echo "$UPDATED_JSON" | base64 -w 0)
```

### Step 4: Remove Old Note from notes.json

**CRITICAL:** Only remove the specific entry matching the commitment. Do NOT modify other notes.

```bash
COMMITMENT="NOTE_COMMITMENT_VALUE"
jq --arg c "$COMMITMENT" '[.[] | select(.commitment != $c)]' ~/.ceaser-mcp/notes.json > ~/.ceaser-mcp/notes.json.tmp && mv ~/.ceaser-mcp/notes.json.tmp ~/.ceaser-mcp/notes.json && chmod 600 ~/.ceaser-mcp/notes.json
```

**IMPORTANT:** Always restore file permissions to 0600 after modification.

### Step 5: Import Updated Note

Run:

```bash
npx -y ceaser-mcp import "$UPDATED_BACKUP"
```

### Step 6: Verify Import

Run:

```bash
npx -y ceaser-mcp notes
```

Verify:
- Note exists with the same commitment
- `leafIndex` is the correct value (NOT null, NOT 0 unless actually the first leaf)
- `spent` is `false`

### Edge Cases

- **parseBackup null-leafIndex bug:** `Number(null)` returns `0` in JavaScript. ALWAYS set the leafIndex in the backup string BEFORE importing. Never import with `i=null`.
- **File permissions:** After ANY modification to notes.json, run `chmod 600 ~/.ceaser-mcp/notes.json`.
- **Other notes:** The jq filter must preserve all other note entries. Only remove the one matching the specific commitment.

---

## Unshield Phase

### Pre-Checks

Before calling unshield, verify:
- The note ID is known (from shield phase or from `npx -y ceaser-mcp notes`)
- The note has `leafIndex != null`
- The note is `spent == false`
- The recipient address is valid

### Execute Unshield

Inform the user: "Generating burn proof and submitting to facilitator. This may take 15-60 seconds depending on tree size and hardware."

Run:

```bash
npx -y ceaser-mcp unshield NOTE_ID RECIPIENT_ADDRESS
```

Replace NOTE_ID and RECIPIENT_ADDRESS with actual values.

### Expected Success Response

- `success`: `true`
- `txHash`: Facilitator settlement TX hash
- `recipient`: Target address
- `grossAmount`: Gross amount in wei
- `feeWei`: Fee in wei
- `netAmount`: Net amount in wei
- `noteId`: The used note ID

### Expected Error Responses

- `"Note does not have a leaf index"`: leafIndex update failed. Check notes.json.
- `"Note has already been spent"`: Double-spend attempt. Note was already unshielded.
- `"Unshield proof generation failed"`: Proof generation error. May retry.

The unshield is GASLESS -- the facilitator pays all gas costs.

---

## Gas Refund Phase

**Only execute for Path C, after successful Unshield.** Refunds remaining ETH from the hot wallet to the user.

### Execute Refund

Run:

```bash
CEASER_HOT_MNEMONIC="MNEMONIC_PHRASE" node {baseDir}/helpers/wallet-ops.js refund --recipient REFUND_ADDRESS --rpc https://mainnet.base.org
```

Where:
- `MNEMONIC_PHRASE`: The 12-word mnemonic (from Wallet Generation Phase)
- `REFUND_ADDRESS`: The user's refund address (from Step 3 of Wallet Generation Phase, or detected from funding TX)

### Process Refund Result

- **`refunded: true`**: Show amount and TX hash to user. "Refunded X ETH to your address."
- **`refunded: false` (balance too low for gas + L1 fee)**: Inform user: "Remaining balance is too small to cover gas + L1 data fee for a refund transfer. Import the mnemonic into MetaMask to recover manually."
- **Error (network, RPC)**: Inform user of the error. Show hot wallet address and remaining balance so user is aware.

**The refund is a best-effort operation.** Refund failure does NOT affect the main operation (Shield + Unshield already completed successfully).

---

## Result Presentation

### On Success

Present to the user:
- **Recipient:** The target address
- **Net amount:** Convert `netAmount` from wei to ETH (human-readable)
- **Fee:** Convert `feeWei` from wei to ETH
- **Shield TX:** Clickable link: `https://basescan.org/tx/SHIELD_TX_HASH`
- **Settlement TX:** Clickable link: `https://basescan.org/tx/UNSHIELD_TX_HASH`
- **Refund:** Amount refunded (if any) with TX link
- Confirmation: "Private transfer complete. ETH has been sent to the recipient. The temporary wallet mnemonic has been discarded from this session."

### On Shield Success but Unshield Failure

Present:
- Note status (unspent, with leafIndex)
- Message: "Your ETH is safely in the privacy pool. The unshield can be retried later."
- Note ID for future reference
- Suggestion: "Try again with: /ceaser-send (use existing note)"
- Refund: Attempt refund of remaining hot wallet ETH.

### On Complete Flow Abort

Present:
- Current status summary
- Whether ETH was moved (NO if shield TX was not sent/confirmed)
- If hot wallet has balance: refund status
- Reminder: "As long as you have the backup string, your shielded ETH can always be recovered."
- Next steps based on where the flow stopped
- Note: "The temporary wallet mnemonic has been discarded. Use your saved mnemonic to recover any remaining hot wallet funds."

---

## Error Handling Reference

| Error | Cause | Data Loss? | Action |
|-------|-------|-----------|--------|
| Hot wallet generation fails | Node.js crypto issue | None | Retry |
| Insufficient funding | User sent too little ETH | ETH in hot wallet | Inform user, wait for more ETH |
| Funding timeout (10 min) | User did not fund | None (no ETH sent) | Retry flow |
| Funding timeout with balance | User sent partial amount | ETH in hot wallet | Auto-refund, retry flow |
| User cancels funding | User choice | None or ETH in hot wallet | Auto-refund if balance > 0 |
| Shield proof fails after funding | Facilitator down, circuit error | ETH in hot wallet | Retry (2x), then auto-refund |
| Sign-and-send fails | Gas, nonce, RPC issue | ETH in hot wallet | Retry or auto-refund |
| TX reverts (status=0x0) | Insufficient funds, gas, revert | ETH partially in hot wallet | Auto-refund remainder |
| TX pending too long | Network congestion | ETH spent on TX | Provide TX hash, check later |
| No Shield event in TX | Wrong TX hash | None | Verify TX hash |
| Commitment mismatch | Wrong TX for this note | None | Verify TX hash matches shield operation |
| notes.json manipulation fails | Permissions, syntax | Note still in backup | Manual recovery with backup string |
| Unshield proof fails | Facilitator down, indexer desync | None (note unspent) | Retry later |
| ceaser.org unreachable | Server down | None | Check status, retry later |
| Invalid mnemonic in env var | Env var corrupted or wrong format | None | Re-run generate, use fresh mnemonic |
| Refund fails | Gas too high for remainder | Small dust in hot wallet | Inform user |

**Recovery guarantee:** The backup string is ALWAYS the ultimate fallback. As long as the user has it, shielded ETH can be recovered.

---

## Session Interruption

If the session aborts during the flow:

| Phase | State | Loss Risk | Recovery |
|-------|-------|-----------|----------|
| Before funding | No ETH sent | None | Restart flow |
| After funding, before Shield TX | ETH in hot wallet | Recoverable via mnemonic | User imports mnemonic into MetaMask to access hot wallet |
| After Shield TX, before Unshield | Note in notes.json, backup with user | None | Resume with Path A or B using backup |
| After Unshield, before refund | Main operation complete | Small dust in hot wallet | User can recover dust via mnemonic if desired |

**Risk minimization:** The agent executes the Shield TX as quickly as possible after funding is confirmed. The window between funding and Shield TX is minimized. Additionally, the user has the mnemonic phrase as a safety net. Even if the session breaks after funding, the user can recover funds by importing the mnemonic into any BIP-39 compatible wallet (e.g., MetaMask).

---

## Security Warnings

### Backup String

- The backup string contains private ZK secrets (secret + nullifier)
- Anyone with the backup string can withdraw the shielded ETH
- The agent MUST show it ONCE and never repeat it
- The agent MUST NOT store it in session summaries or memory
- Instruct the user to save it offline immediately

### Hot Wallet Security

- The agent generates a temporary BIP-39 mnemonic that is shown to the user ONCE as a recovery mechanism
- After the session ends, the mnemonic is only available if the user saved it. The agent discards it.
- The mnemonic appears in session logs (same risk level as the backup string)
- The user should ONLY send the displayed funding amount to the hot wallet
- Do NOT send ETH to the hot wallet address after the operation completes
- The agent MUST show the mnemonic ONCE to the user with a recovery warning. After that, do NOT repeat the mnemonic.
- The agent MUST NOT repeat the mnemonic in summaries or follow-up responses
- After flow completion: inform user "The temporary wallet mnemonic has been discarded from this session. Recover funds using your saved mnemonic if needed."

### Privacy Notice

- The agent sees the backup string during the flow (contains ZK secrets)
- The agent generates and shows a temporary mnemonic phrase during the flow
- OpenClaw session logs may contain both the backup string and the mnemonic
- For maximum privacy: save backup offline and clear chat history after completion
- Auto-signing creates on-chain links between user wallet and hot wallet (see PRIVACY WARNING section above)

### Recipient Verification

- The recipient address CANNOT be changed after unshield is submitted
- Ask the user to double-check the recipient address before executing unshield

### Fee Transparency

- 0.25% protocol fee applies on EACH shield and unshield operation
- Always show: gross amount, fee amount, and net amount
- Total round-trip cost for a complete private send: approximately 0.5%

### Concurrent Execution

- Each execution generates its own hot wallet -- no conflicts between parallel runs
- However, `ceaser-mcp` stores notes in a shared `notes.json` file -- parallel writes may conflict
- Recommendation: do not run multiple ceaser-send flows in parallel
