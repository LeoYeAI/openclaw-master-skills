---
name: vultisig
description: Use this skill when an agent needs to create crypto wallets, send transactions, swap tokens, check balances, or perform any on-chain operation across 36+ blockchains using threshold signatures (TSS). Vultisig SDK provides self-custodial MPC vaults — no seed phrases, no single point of failure. Fast Vaults (2-of-2 with VultiServer) enable fully autonomous agent operations without human approval.
user-invocable: true
---

# Vultisig SDK Skill (agent-first)

## What this Skill is for

- Creating and managing self-custodial crypto vaults (Fast Vault for agents, Secure Vault for multi-device)
- Sending transactions across 36+ blockchains (Bitcoin, Ethereum, Solana, Cosmos, and more)
- Swapping tokens cross-chain via THORChain, MayaChain, 1inch, LiFi, KyberSwap
- Querying balances and gas fees across all supported chains
- Importing/exporting vault backups (.vult files)
- Importing existing wallets via BIP39 seedphrase
- Building automated strategies: DCA, rebalancing, conditional swaps, agent-to-agent payments

## Default stack decisions

1) **Fast Vault (2-of-2) for all agent use cases**
   - Agent holds one key share, VultiServer holds the other
   - VultiServer auto-co-signs based on policy rules — no human in the loop
   - Use Secure Vault only when multi-device human approval is required

2) **TypeScript SDK (`@vultisig/sdk`) as primary interface**
   - `npm install @vultisig/sdk`
   - Source: [github.com/vultisig/vultisig-sdk](https://github.com/vultisig/vultisig-sdk)
   - SDK Users Guide: [`docs/SDK-USERS-GUIDE.md`](https://github.com/vultisig/vultisig-sdk/blob/main/docs/SDK-USERS-GUIDE.md)

3) **`MemoryStorage` for ephemeral agents, implement `Storage` interface for persistent agents**
   - `MemoryStorage` is the only storage exported from the SDK
   - For persistent vaults, implement the `Storage` interface backed by your preferred store

4) **3-step transaction flow: prepare → sign → broadcast**
   - Never skip steps. Always prepare the keysign payload first, then sign, then broadcast.
   - Fast Vault signing is automatic (VultiServer co-signs). Secure Vault requires device coordination.

5) **Amounts as `bigint` (smallest unit) for sends, `number` (human-readable) for swaps**
   - `prepareSendTx` takes `amount: bigint` (e.g., `BigInt('100000000000000000')` for 0.1 ETH)
   - `getSwapQuote` takes `amount: number` (e.g., `0.1` for 0.1 ETH)

## Operating procedure

### 1. Initialize SDK

```typescript
import { Vultisig, MemoryStorage } from '@vultisig/sdk';

const sdk = new Vultisig({ storage: new MemoryStorage() });
await sdk.initialize();
```

> Source: [`Vultisig.ts`](https://github.com/vultisig/vultisig-sdk/blob/main/packages/sdk/src/Vultisig.ts)

### 2. Create a Fast Vault

Two-step process: create (triggers email verification) then verify.

```typescript
const vaultId = await sdk.createFastVault({
  name: 'my-agent-vault',
  email: 'agent@example.com',
  password: 'secure-password',
});

// Verify with the code sent to the email
const vault = await sdk.verifyVault(vaultId, '123456');
// Returns: FastVault instance — ready for operations
```

**Risk notes:**
- The password encrypts the vault share. If lost, the vault cannot be recovered.
- The email verification code is required — agents must have email access or an email relay.

### 2b. Create a Secure Vault (human co-signing)

When agents need human approval before executing transactions (high-value transfers, treasury ops, compliance flows), use a Secure Vault. The agent holds one share, the human holds the other. The human co-signs via the Vultisig mobile app by scanning a QR code — the transaction only executes when both parties agree.

```typescript
const { vault, vaultId, sessionId } = await sdk.createSecureVault({
  name: 'agent-with-human-approval',
  onQRCodeReady: (qrPayload) => {
    // Display QR for the human co-signer to scan with Vultisig app
    displayQRCode(qrPayload);
  },
  onDeviceJoined: (deviceId, total, required) => {
    console.log(`Device joined: ${total}/${required}`);
  },
});
```

Signing requires the human to participate:

```typescript
const signature = await vault.sign(payload, {
  onQRCodeReady: (qr) => {
    // Human must scan this QR with Vultisig app to co-sign
    displayQRCode(qr);
  },
  onDeviceJoined: (id, total, required) => {
    console.log(`Signing: ${total}/${required} devices ready`);
  },
});
// Completes only when the human co-signer participates
```

> Source: [`SecureVault.ts`](https://github.com/vultisig/vultisig-sdk/blob/main/packages/sdk/src/vault/SecureVault.ts)

**When to use Secure Vault over Fast Vault:**
- Transactions above a risk threshold that need human sign-off
- Treasury or DAO operations requiring human approval
- Compliance workflows where an agent should not act unilaterally

### 3. Get addresses

```typescript
const ethAddress = await vault.address('Ethereum');
const btcAddress = await vault.address('Bitcoin');
const solAddress = await vault.address('Solana');

// All addresses at once
const allAddresses = await vault.addresses();
// Returns: Record<string, string>
```

> Source: [`VaultBase.ts`](https://github.com/vultisig/vultisig-sdk/blob/main/packages/sdk/src/vault/VaultBase.ts)

Chain identifiers use PascalCase strings matching the `Chain` enum: `'Bitcoin'`, `'Ethereum'`, `'Solana'`, `'THORChain'`, `'Cosmos'`, `'Polygon'`, `'Arbitrum'`, `'Base'`, `'Optimism'`, `'Avalanche'`, `'BSC'`, etc.

> Full chain list: [`Chain.ts`](https://github.com/vultisig/vultisig-sdk/blob/main/packages/core/chain/Chain.ts)

### 4. Check balances

```typescript
// Native chain balance
const ethBalance = await vault.balance('Ethereum');
// Returns Balance: {
//   amount: string,      // Raw amount in smallest unit
//   decimals: number,    // Chain decimals (18 for ETH)
//   symbol: string,      // "ETH"
//   chainId: string,
//   fiatValue?: number,  // USD value if available
// }

// Multiple chains
const allBalances = await vault.balances();
// Returns: Record<string, Balance>

// Force refresh (clears cache)
const fresh = await vault.updateBalance('Ethereum');
```

#### Token balances (ERC-20, SPL, etc.)

```typescript
// Get a specific token balance by contract address
const usdcBalance = await vault.balance('Ethereum', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48');
// Returns Balance: { amount: "1000000", decimals: 6, symbol: "USDC", ... }

// Get all token balances on a chain
const ethTokens = await vault.tokenBalances('Ethereum');
// Returns: Token[] — all tokens with non-zero balances

// Include tokens when fetching multi-chain balances
const everything = await vault.balances(undefined, true); // includeTokens = true
```

**Risk notes:**
- Native balance and token balances are separate queries. `vault.balance('Ethereum')` returns only ETH, not ERC-20s.
- Token balances require the contract address as the `tokenId` parameter.

### 5. Estimate gas

```typescript
// Returns chain-specific gas info
const evmGas = await vault.gas('Ethereum');
// EvmGasInfo: { gasPrice, gasPriceGwei, maxFeePerGas, maxPriorityFeePerGas, gasLimit, estimatedCostUSD }

const utxoGas = await vault.gas('Bitcoin');
// UtxoGasInfo: { gasPrice, byteFee, estimatedCostUSD }

const cosmosGas = await vault.gas('Cosmos');
// CosmosGasInfo: { gasPrice, gas, estimatedCostUSD }
```

> Source: [`VaultBase.ts`](https://github.com/vultisig/vultisig-sdk/blob/main/packages/sdk/src/vault/VaultBase.ts) — `gas<C extends Chain>(chain: C): Promise<GasInfoForChain<C>>`

### 6. Send a transaction

3-step flow: `prepareSendTx` → `sign` → `broadcastTx`

```typescript
// Step 1: Prepare keysign payload
const payload = await vault.prepareSendTx({
  coin: {
    chain: 'Ethereum',
    address: ethAddress,     // Sender address (from vault.address())
    decimals: 18,
    ticker: 'ETH',
  },
  receiver: '0xRecipientAddress...',
  amount: BigInt('100000000000000000'), // 0.1 ETH in wei
  memo: '',                             // Optional
});
// Returns: KeysignPayload

// Step 2: Sign (Fast Vault — VultiServer co-signs automatically)
const signature = await vault.sign(payload);
// Returns: Signature { signature: string, recovery?: number, format: 'DER' | 'ECDSA' | 'EdDSA' }

// Step 3: Broadcast
const txHash = await vault.broadcastTx({
  chain: 'Ethereum',
  keysignPayload: payload,
  signature: signature,
});
// Returns: string (transaction hash)

// Explorer URL
const url = Vultisig.getTxExplorerUrl('Ethereum', txHash);
```

> Source: [`VaultBase.prepareSendTx()`](https://github.com/vultisig/vultisig-sdk/blob/main/packages/sdk/src/vault/VaultBase.ts), [`FastVault.sign()`](https://github.com/vultisig/vultisig-sdk/blob/main/packages/sdk/src/vault/FastVault.ts)

**Risk notes:**
- `amount` is in the chain's smallest unit (wei for ETH, satoshi for BTC). Miscalculating decimals will send wrong amounts.
- Always verify the receiver address. Transactions are irreversible.
- Check gas estimation before sending to avoid stuck transactions.

#### Sending ERC-20 / tokens

To send tokens instead of native currency, add the `id` field (contract address) to the `coin` object:

```typescript
// Send 10 USDC on Ethereum
const tokenPayload = await vault.prepareSendTx({
  coin: {
    chain: 'Ethereum',
    address: ethAddress,
    decimals: 6,            // USDC has 6 decimals
    ticker: 'USDC',
    id: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', // Token contract address
  },
  receiver: '0xRecipientAddress...',
  amount: BigInt('10000000'), // 10 USDC (6 decimals)
});

const sig = await vault.sign(tokenPayload);
const txHash = await vault.broadcastTx({
  chain: 'Ethereum',
  keysignPayload: tokenPayload,
  signature: sig,
});
```

**Risk notes:**
- The `id` field is the token contract address. Without it, the SDK treats it as a native transfer.
- Use the token's decimals, not the chain's. USDC = 6, WETH = 18, WBTC = 8.
- The sender still needs native ETH/gas token to pay transaction fees.

### 7. Swap tokens

4-step flow: `getSwapQuote` → `prepareSwapTx` → `sign` → `broadcastTx`

```typescript
// Step 1: Get quote
const quote = await vault.getSwapQuote({
  fromCoin: {
    chain: 'Ethereum',
    address: ethAddress,
    decimals: 18,
    ticker: 'ETH',
  },
  toCoin: {
    chain: 'Ethereum',
    address: usdcAddress,
    decimals: 6,
    ticker: 'USDC',
    id: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', // Token contract
  },
  amount: 0.1, // Human-readable (NOT bigint)
});
// Returns: SwapQuoteResult {
//   provider: string,
//   estimatedOutput: bigint,
//   estimatedOutputFiat?: number,
//   requiresApproval: boolean,
//   fees: SwapFees,
//   warnings: string[],
// }

// Step 2: Prepare swap transaction
const swapResult = await vault.prepareSwapTx({
  fromCoin: quote.fromCoin,
  toCoin: quote.toCoin,
  amount: 0.1,
  swapQuote: quote,
});
// Returns: SwapPrepareResult {
//   keysignPayload: KeysignPayload,
//   approvalPayload?: KeysignPayload,  // If token approval needed
//   quote: SwapQuoteResult,
// }

// Step 2.5: If approval required, sign and broadcast approval first
if (swapResult.approvalPayload) {
  const approvalSig = await vault.sign(swapResult.approvalPayload);
  await vault.broadcastTx({
    chain: 'Ethereum',
    keysignPayload: swapResult.approvalPayload,
    signature: approvalSig,
  });
}

// Step 3: Sign swap
const swapSig = await vault.sign(swapResult.keysignPayload);

// Step 4: Broadcast swap
const swapTxHash = await vault.broadcastTx({
  chain: 'Ethereum',
  keysignPayload: swapResult.keysignPayload,
  signature: swapSig,
});
```

**Swap providers** (auto-routed for best rate):
- **THORChain** — Native cross-chain (BTC <> ETH, etc.)
- **MayaChain** — Additional cross-chain pairs
- **1inch** — EVM DEX aggregation
- **LiFi** — Cross-chain + cross-DEX
- **KyberSwap** — EVM DEX aggregation

**Risk notes:**
- Swap amounts use human-readable numbers (`0.1`), not bigint. The SDK handles decimal conversion.
- Check `quote.warnings` before executing — may contain slippage or liquidity warnings.
- ERC-20 token swaps may require a separate approval transaction (`approvalPayload`).
- Cross-chain swaps take longer (minutes, not seconds) and have different failure modes.

### 8. Export / Import vault

```typescript
// Export to encrypted .vult file
const { filename, data } = await vault.export('backup-password');
// filename: string, data: Base64-encoded vault backup

// Import from .vult file
const importedVault = await sdk.importVault(data, 'backup-password');
```

### 9. Create vault from seedphrase

```typescript
// Validate BIP39 seedphrase
const validation = await sdk.validateSeedphrase('word1 word2 ...');
// Returns: { valid: boolean, wordCount: number, error?: string }

// Discover which chains have existing balances
const discovery = await sdk.discoverChainsFromSeedphrase('word1 word2 ...');
// Returns: ChainDiscoveryAggregate

// Create Fast Vault from seedphrase (still needs email verification)
const vaultId = await sdk.createFastVaultFromSeedphrase({
  name: 'imported-vault',
  email: 'agent@example.com',
  password: 'secure-password',
  mnemonic: 'word1 word2 ...',
});
const vault = await sdk.verifyVault(vaultId, 'email-code');
```

**Risk notes:**
- Seedphrase import creates a new TSS vault from the seed — the original seed-based wallet still exists independently.
- Handle seedphrases with extreme care. Never log, store in plaintext, or transmit unencrypted.

### 10. Vault lifecycle management

```typescript
// List all vaults
const vaults = await sdk.listVaults();

// Set active vault
await sdk.setActiveVault(vault);

// Get active vault
const active = await sdk.getActiveVault();

// Check vault type
if (Vultisig.isFastVault(vault)) { /* FastVault methods */ }
if (Vultisig.isSecureVault(vault)) { /* SecureVault methods */ }

// Delete vault
await sdk.deleteVault(vault);
```

### 11. Check transaction status

After broadcasting, use the explorer URL or chain-specific methods to confirm transactions:

```typescript
// Get explorer URL for any chain
const explorerUrl = Vultisig.getTxExplorerUrl('Ethereum', txHash);
// e.g., "https://etherscan.io/tx/0x..."

const addressUrl = Vultisig.getAddressExplorerUrl('Bitcoin', btcAddress);
// e.g., "https://mempool.space/address/bc1..."
```

For automated strategies that need to confirm completion before the next action, poll the balance or use an external RPC/indexer to check transaction finality. The SDK does not provide a built-in tx status poller — use `vault.updateBalance()` to force-refresh after a broadcast and compare before/after.

```typescript
// Pattern: confirm send completed
const balanceBefore = await vault.balance('Ethereum');
// ... broadcast transaction ...
await new Promise(r => setTimeout(r, 15000)); // Wait for block confirmation
const balanceAfter = await vault.updateBalance('Ethereum');
// Compare balanceBefore.amount vs balanceAfter.amount
```

### 12. Address book

Manage recurring recipients for automated transfers:

```typescript
// Get saved addresses (optionally filter by chain)
const allContacts = await sdk.getAddressBook();
const ethContacts = await sdk.getAddressBook('Ethereum');

// Add entries
await sdk.addAddressBookEntry([
  { chain: 'Ethereum', address: '0x...', name: 'Treasury' },
  { chain: 'Bitcoin', address: 'bc1...', name: 'Cold Storage' },
]);

// Update a name
await sdk.updateAddressBookEntry('Ethereum', '0x...', 'Main Treasury');

// Remove entries
await sdk.removeAddressBookEntry([
  { chain: 'Ethereum', address: '0x...' },
]);
```

> Source: [`Vultisig.ts`](https://github.com/vultisig/vultisig-sdk/blob/main/packages/sdk/src/Vultisig.ts)

### 13. $VULT discount tiers

Holding $VULT tokens reduces swap fees (up to 50%). The SDK can check and update the agent's discount tier:

```typescript
// Check current discount tier
const tier = await vault.getDiscountTier();
// Returns: string | null — e.g., "gold", "silver", or null if no discount

// Update tier (after acquiring more $VULT)
const newTier = await vault.updateDiscountTier();
```

> Token contract: [`0xb788144DF611029C60b859DF47e79B7726C4DEBa`](https://etherscan.io/token/0xb788144DF611029C60b859DF47e79B7726C4DEBa) (Ethereum)

### 14. Listen to events

```typescript
// SDK-level events
sdk.on('vaultCreationProgress', (data) => { /* keygen progress */ });
sdk.on('vaultCreationComplete', (data) => { /* vault ready */ });
sdk.on('vaultChanged', (data) => { /* active vault switched */ });

// Vault-level events
vault.on('balanceUpdated', (data) => { /* balance changed */ });
vault.on('transactionSigned', (data) => { /* signature complete */ });
vault.on('transactionBroadcast', (data) => { /* tx submitted */ });
vault.on('signingProgress', (data) => { /* signing steps */ });
vault.on('swapQuoteReceived', (data) => { /* quote ready */ });

// SecureVault only (multi-device coordination)
vault.on('qrCodeReady', (data) => { /* show QR for device pairing */ });
vault.on('deviceJoined', (data) => { /* co-signer connected */ });
vault.on('allDevicesReady', (data) => { /* threshold met, signing can proceed */ });

// Error handling
vault.on('error', (error) => { /* handle errors */ });
sdk.on('error', (error) => { /* handle SDK-level errors */ });
```

> Source: [`packages/sdk/src/events/`](https://github.com/vultisig/vultisig-sdk/tree/main/packages/sdk/src/events)

## Supported chains

> Source: [`Chain.ts`](https://github.com/vultisig/vultisig-sdk/blob/main/packages/core/chain/Chain.ts)

| Category | Chains | Signature |
|----------|--------|-----------|
| **UTXO** | Bitcoin, Litecoin, Dogecoin, Bitcoin Cash, Dash, Zcash | ECDSA |
| **EVM** | Ethereum, BSC, Polygon, Avalanche, Arbitrum, Optimism, Base, Blast, Cronos, zkSync, Hyperliquid, Mantle, Sei | ECDSA |
| **Cosmos/IBC** | THORChain, MayaChain, Cosmos Hub, Osmosis, Dydx, Kujira, Noble, Terra, Terra Classic, Akash | ECDSA |
| **Other** | Solana, Sui, Polkadot, TON, Ripple, Tron, Cardano | EdDSA / Mixed |

## Security model

- **No seed phrases** — vault shares replace 12/24 word seeds
- **No single point of failure** — no device holds a complete private key
- **No on-chain key registration** — unlike multi-sig wallets
- **DKLS23 protocol** — 3-round TSS, co-developed with Silence Laboratories
- **Open source and audited**
- Docs: [Security & Technology](https://docs.vultisig.com/security-and-technology/security-technology)

## CLI alternative

```bash
npm install -g @vultisig/sdk

vsig vault create --name agent-vault --type fast
vsig balance --chain Ethereum
vsig send --chain Ethereum --to 0x... --amount 0.1
vsig swap --from ETH --to USDC --amount 0.1
```

> Source: [`clients/cli/`](https://github.com/vultisig/vultisig-sdk/tree/main/clients/cli)

## Progressive disclosure

- [SDK Users Guide](https://github.com/vultisig/vultisig-sdk/blob/main/docs/SDK-USERS-GUIDE.md) — Complete API walkthrough
- [Architecture](https://github.com/vultisig/vultisig-sdk/blob/main/docs/architecture/ARCHITECTURE.md) — SDK internals, data flow, design patterns
- [Agent Integration Guide](https://github.com/vultisig/vultisig-sdk/blob/main/docs/agent.md) — Agent-specific patterns and best practices
- [Fast Vault Docs](https://docs.vultisig.com/infrastructure/what-is-vultisigner/how-does-vultisigner-work) — How VultiServer co-signing works
- [Marketplace Plugin Guide](https://docs.vultisig.com/developer-docs/marketplace/basics-quick-start) — Build automation plugins
- [llms.txt](https://vultisig.com/llms.txt) — Concise link index for web-browsing agents
- [llms-full.txt](https://vultisig.com/llms-full.txt) — Extended context with examples
