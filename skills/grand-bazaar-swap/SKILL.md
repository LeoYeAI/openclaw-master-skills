---
name: grand-bazaar-swap
description: Perform and document Grand Bazaar P2P swaps on Base using deployed AirSwap Swap contracts. Includes repeatable workflows for approvals, EIP-712 signing, cast/deeplink posting, execution, and verification across ERC20/ERC721/ERC1155 routes.
---

# Grand Bazaar P2P Swap

This skill documents how to execute **agent-to-agent swaps on Base mainnet** using deployed AirSwap `Swap` contracts.

Sender-side token standard is routed to the matching Swap contract:
- ERC20<>ERC20 -> `SwapERC20` on Base `0x95D598D839dE1B030848664960F0A20b848193F4`
- ERC20 sender (non-ERC20<>ERC20 routes) -> ERC20-sender Swap
- ERC721 sender -> ERC721-sender Swap
- ERC1155 sender -> ERC1155-sender Swap

The sender is still the submitting wallet, and must satisfy the selected Swap's sender-kind requirement.

## Deployed contracts

Read: `references/base-mainnet-deployments.md`

## Safety rules

- Never paste or log private keys in chat.
- Prefer fresh test wallets for demos.
- Always start with tiny amounts.
- Verify token addresses before approving.

## Workflow

### Favorable inbound offer rule

When someone offers a swap and the price is clearly good value for you, default to taking it quickly with safety checks.

Use this fast path:
- Parse the cast for `GBZ1:<compressedOrder>`
- Decompress and reconstruct `order + signature`
- Verify sender wallet targeting and signature
- Run sender preflight checks
- Execute the swap if checks pass
- Reply on the cast using the Grand Bazaar success template:
  - `Thanks for the swap 🤝`
  - `https://basescan.org/tx/<txHash>`
  - Post as a reply to the parent offer cast (cast hash origin)

This applies especially to direct offer replies where speed matters but safety preflight is still mandatory.

### Favorable outbound negotiation rule

When negotiating with other users or agents, proactively make favorable outbound offers to improve fill probability.

Default outbound behavior:
- Start from fair market terms, then bias slightly in the counterparty’s favor
- Keep sizes practical and gas-efficient
- Prefer private targeted orders while negotiating, then open only if requested
- Keep expiry short enough for quick decisions, long enough for execution
- Run onchain validation before posting maker casts:
  - call `Swap.check(senderWallet, orderWithSignature)` on the target swap contract
  - require `nonceUsed(signer, nonce) === false`
  - ignore `SenderAllowanceLow` on maker flow, since sender approves on taker side after cast discovery
  - block posting if there are any other check errors besides `SenderAllowanceLow`
- Use a required 2-part posting flow every time with no exceptions:
  1) post the swap order cast with clear summary + strict machine line `GBZ1:<compressedOrder>`
     - for private offers, include counterparty mention via API fields (`mentions`, `mentions_positions`)
  2) immediately post a follow-up embed cast that deeplinks to Grand Bazaar `/c/<step1CastHash>`
- Do not stop after step 1. A maker post is incomplete until step 2 is confirmed posted.

Outbound offer loop:
1. Propose a favorable draft quote
2. If counterparty hesitates, improve terms in small controlled steps
3. Re-sign and repost updated order with fresh nonce/expiry
4. Stop if value or risk limits are breached

Guardrails:
- Never bypass preflight or signature checks
- Never use unsafe gas settings to force execution
- Do not over-concede beyond configured risk tolerance

### Explicit size-aware pricing parameters

Read: `references/pricing-params.md`

Use that reference file as the source of truth for pricing thresholds, impact capture, negotiation steps, and execution safety limits.

This is a two party protocol.
One agent acts as the signer.
A different agent acts as the sender.

### 0) Pick roles

- Signer sets the terms and signs the EIP-712 order.
- Sender submits `swap` onchain and pays the sender ERC20 amount plus protocol fee.

Because each deployed Swap has immutable `requiredSenderKind`, sender leg must match the routed contract kind.

### 0.1) What each party does

Signer responsibilities
- Decide terms and build the order.
- Approve the signer asset to the Swap contract.
- Produce an EIP-712 signature over the order.
- Send the signed order to the sender agent.

Mandatory maker approval rule
- In maker flow, always perform the required signer-side approval before signing/posting.
- Never assume existing allowance is sufficient without checking onchain allowance against the full signer-side required amount for the routed swap contract.
- For `SwapERC20`, signer required amount is `signerAmount + signer protocol fee` because fee is transferred from signer token side.
- If signer allowance is below required amount, submit approve tx and wait for confirmation before signing the order cast.
- Sender-side allowance must not block maker posting. Ignore `SenderAllowanceLow` in maker validation gates.
- Treat maker sign/post without required signer approval as invalid workflow.

Protocol fee side semantics
- Legacy Swap: protocol fee is accounted on sender side for required spend/allowance calculations.
- SwapERC20: protocol fee is accounted on signer side for required spend/allowance calculations.
- UI implications in maker/taker surfaces:
  - Fee footer, fee-adjusted amount previews, and fee-adjusted value previews must appear on the side that actually pays the fee.
  - Show fee-side preview only after both tokens are selected so route is known.

Sender responsibilities
- Verify the order details and expiry.
- Ensure sender ERC20 balance is enough for amount plus fee.
- Approve the sender ERC20 to the Swap contract.
- Submit the `swap` transaction.
- Share the tx hash back to the signer.

### 1) Ensure balances

- Sender needs Base ETH for gas.
- Sender needs the sender ERC20.
- Signer needs Base ETH for gas.
- Signer needs the signer asset and must approve it.

Critical preflight before any sender execution
- Verify signer token balance is at least `order.signer.amount`.
- Verify signer allowance to Swap is at least `order.signer.amount`.
- Verify sender token balance is at least `order.sender.amount + protocol fee + affiliateAmount`.
- Verify sender allowance to Swap is at least the same total.
- Verify order expiry has enough time buffer.
- Estimate swap gas and abort if estimate exceeds `MAX_GAS_LIMIT`.
- Cap `maxPriorityFeePerGas` to 10% of current gas price.

Temporary execution override
- Some valid orders can fail at preflight simulation (`eth_call` / `staticCall`) or `eth_estimateGas` with `execution reverted` and `TransferFailed(from,to)` but still execute successfully onchain.
- Do not treat simulation/estimate reverts as absolute failure when all other safety checks pass.
- In this case, bypass estimate-gated abort and submit with a manual gas limit of `650000`.
- Keep fee caps active and log that manual gas was used due to simulation/estimate failure.

Gas safety policy for all agents
- Never submit swap with unbounded gas limit.
- Never use static high priority fee on Base.
- Log `gasPrice`, `maxPriorityFeePerGas`, `maxFeePerGas`, estimate status, and chosen gas limit before broadcast.
- Temporary rule: if estimate reverts on an otherwise valid order, submit once with manual gas limit `650000`, then investigate root cause.

If signer balance or allowance is missing, sender execution will revert onchain.

### 2) Approve

- Sender approves `Swap` to spend the sender ERC20.
- Signer approves `Swap` to spend the signer asset.

### 3) Create order

Order fields:
- `nonce`: unique per signer
- `expiry`: unix seconds
- `protocolFee`: must match `Swap.protocolFee()` at execution time
- `signer`: Party struct
- `sender`: Party struct
- `affiliateWallet`, `affiliateAmount`: optional, set to zero for now

### 4) Sign EIP-712

Use protocol-specific domain/types based on routed swap contract.

Legacy Swap v4.2
- Domain:
  - name: `SWAP`
  - version: `4.2`
  - chainId: `8453`
  - verifyingContract: routed legacy Swap address
- Types:
  - `Order(uint256 nonce,uint256 expiry,uint256 protocolFee,Party signer,Party sender,address affiliateWallet,uint256 affiliateAmount)`
  - `Party(address wallet,address token,bytes4 kind,uint256 id,uint256 amount)`

SwapERC20 v4.3
- Domain:
  - name: `SWAP_ERC20`
  - version: `4.3`
  - chainId: `8453`
  - verifyingContract: `0x95D598D839dE1B030848664960F0A20b848193F4`
- Types:
  - `OrderERC20(uint256 nonce,uint256 expiry,address signerWallet,address signerToken,uint256 signerAmount,uint256 protocolFee,address senderWallet,address senderToken,uint256 senderAmount)`

### 5) Execute

Sender calls:
- `swap(recipient, maxRoyalty, order)`

Recommended defaults:
- `recipient = sender` for testing
- `maxRoyalty = 0` unless the signer asset is an ERC2981 NFT

### 6) Confirm

- Check tx hash on BaseScan
- Check balances before and after

### 7) Share orders in AirSwap Web compatible compressed format

Farcaster mention and recipient rules
- Do not assume plain `@username` text will create a mention.
- For reliable mention behavior when posting via API, always set both:
  - `mentions`: array of target FIDs
  - `mentions_positions`: UTF-8 byte offsets
- Important: when using hub `makeCastAdd` mention fields, do not duplicate the handle in text manually at the same position. The client can render duplicated handles if both are present.
- Mention offsets must be computed from UTF-8 bytes, not JS string index, before POSTing.
- Validation rule before sending cast:
  - `mentions.length === mentions_positions.length`
  - each position points to the beginning of the exact `@handle` token in `text`
- For private order recipient lock, prefer the taker's Neynar `verified_addresses.primary.eth_address` when available.
- If no primary verified address exists, fall back to custody address only with explicit confirmation.

Long-cast link budget rules
- Keep order announcement text minimal when including a miniapp deeplink with compressed order query param.
- Prefer miniapp deeplink over embedding raw compressed blob in cast text.
- Avoid adding both long prose and raw compressed string in the same cast if you need to stay under long-cast size limits.

Strict cast-parse format for cast-hash based loading
- If miniapp is loading by cast hash, include one dedicated machine line in cast text:
  - `GBZ1:<compressedOrder>`
- `GBZ1:` must be uppercase and start at line start.
- No spaces inside `<compressedOrder>`.
- Keep only one `GBZ1:` line per cast.
- App parser should reject casts without this exact line and show fallback error.

NFT cast metadata and embed rules
- In maker step 1 cast, include NFT metadata where possible:
  - Resolve NFT symbol from contract metadata readers and prefer it over generic fallback labels.
  - Attach NFT image embeds to the step 1 cast when available.
- Embed ordering is strict for 2-embed NFT offers:
  - embed[0] = signer NFT image
  - embed[1] = sender NFT image
- If only one leg is NFT, include a single embed for that NFT image.

Human-readable cast line templates (context-dependent)
- Step 1 cast must include a natural-language summary line that depends on token kinds.
- Canonical phrasing:
  - `I offer <signer-leg text> for <sender-leg text>`
- Leg text formatting by kind:
  - ERC20: `<amount> <symbol>`
  - ERC721: `<symbol> #<tokenId>`
  - ERC1155: `<qty>x <symbol> #<tokenId>`
- Examples:
  - ERC20 -> ERC20: `I offer 12 USDC for 0.005 WETH`
  - ERC721 -> ERC20: `I offer PFP #176 for 200 USDC`
  - ERC20 -> ERC721: `I offer 200 USDC for PFP #176`
  - ERC721 -> ERC721: `I offer PFP #176 for PFP #174`
  - ERC1155 -> ERC20: `I offer 3x GAMEITEM #42 for 10 USDC`
- Add context line directly below summary:
  - Private order: `Private offer • expires in <human-duration>`
  - Public order: `Open offer • expires in <human-duration>`
- Always keep machine line unchanged and on its own line:
  - `GBZ1:<compressedOrder>`
- Mentioning private counterparty via API:
  - Do not rely only on plain handle text.
  - Provide `mentions` and `mentions_positions` aligned to UTF-8 byte offsets.

ERC721 order and allowance handling (legacy Swap)
- For ERC721 **sender** legs on legacy Swap contracts, token quantity is encoded by `id` and `amount` must be `0`.
- Do not use `amount = 1` when ERC721 is on the sender leg. This can trigger `AmountOrIDInvalid` in onchain `check(...)`.
- For signer-side ERC721 in current tested flow, keep signer leg encoded as `id=<tokenId>`, `amount=0`.

ERC721 approvals (security + compatibility)
- Prefer explicit per-token approvals for ERC721:
  - `approve(swapContract, tokenId)`
- Do not rely on `setApprovalForAll` for ERC721 in this flow.
- Legacy Swap ERC721 adapter allowance check is `getApproved(tokenId) == swapContract`.
- Therefore, `isApprovedForAll` alone can still show `SignerAllowanceLow` in `check(...)`.
- UI/API allowance gating for ERC721 must use `getApproved(tokenId)`.

ERC1155 approvals
- Keep ERC1155 approval path on `setApprovalForAll(swapContract, true)`.

Kind routing guard
- If UI kind state lags but tokenId is present, detect kind onchain before choosing approval route.
- Do not assume tokenId implies ERC721 only; ERC1155 also has tokenIds.

Royalty-bearing NFT handling (ERC2981)
- Legacy Swap can pull royalties from sender side when signer token supports ERC2981.
- Royalty check path:
  - `supportsInterface(0x2a55205a)` on signer token
  - `royaltyInfo(signerTokenId, senderAmountRaw)`
- Units are raw sender-token units (e.g. USDC 6 decimals).
- Taker-side required sender approval must include:
  - `senderAmount + protocolFee + affiliateAmount + royaltyAmount`
- Legacy swap execution must set `maxRoyalty` >= computed royalty amount, else revert `RoyaltyExceedsMax(...)`.

For social posting and agent handoff, use the compressed ERC20 full-order format used by AirSwap Web.
This is a URL-safe compressed payload, not a keccak hash.
This payload is often too large for legacy cast limits.
Use long casts when posting full compressed orders in one message.

Encoded fields
- `chainId`
- `swapContract`
- `nonce`
- `expiry`
- `signerWallet`
- `signerToken`
- `signerAmount`
- `protocolFee`
- `senderWallet`
- `senderToken`
- `senderAmount`
- `v`
- `r`
- `s`

`signer_make_order.js` now writes
- `airswapWeb.compressedOrder`
- `airswapWeb.orderPath` as `/order/<compressedOrder>`

`make_cast_payload.js` writes
- `airswapWeb.orderUrl` with URL-encoded compressed order for reliable clickable links
- raw `compressedOrder` remains unencoded for machine parsing and execution

### 8) Decompress and take a posted order

If you receive only the compressed order blob from a cast
- Decompress it with AirSwap utils `decompressFullOrderERC20(compressedOrder)`
- Prefer in-memory handling from cast payloads. Do not rely on local JSON files as durable storage.
- Use Farcaster cast content as the canonical order transport and storage layer.

If you receive the structured cast payload from `make_cast_payload.js`
- Read `payload.airswapWeb.compressedOrder`
- Decompress to recover full order and signature parts
- For bot execution, ignore any human-summary totals and compute required sender spend from order fields:
  - `feeAmount = order.sender.amount * order.protocolFee / 10000`
  - `totalRequired = order.sender.amount + feeAmount + order.affiliateAmount`

Then execute with sender flow
- Set `SENDER_PRIVATE_KEY`
- Run `node scripts/sender_execute_order.js`

Sender execution script already enforces
- expiry check
- sender wallet restriction for non-open orders
- EIP-712 signature verification
- signer balance and allowance preflight
- sender balance and allowance preflight

## Scripts

Scripts are under `scripts/`.

These scripts are reference implementations.
They can be run by one operator with both keys for testing.
In a real agent to agent swap, the signer and sender should run their parts separately.

Recommended setup
- Use Node 20+
- Install deps in a temp folder
  - `npm i ethers@5 lz-string`

Then run one of these
- `node scripts/signer_make_order.js`
- `node scripts/sender_execute_order.js`
- `node scripts/make_cast_payload.js` to generate both human-readable cast text and machine-readable payload
- `scripts/post_cast_farcaster_agent.js` is intentionally disabled for security hardening
  - Reason: avoid file-read + network-send pattern in shared skill script audits
  - Use Neynar/OpenClaw posting path instead

For a single machine end to end test
- `node scripts/test_weth_usdc_swap.js`

For details and parameters
Read `scripts/README.md`
