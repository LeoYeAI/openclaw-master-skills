# Token Launcher — Direct Mode Reference

Direct Mode means integrating with Clanker, Flaunch, or Pump.fun directly from your agent's code. You keep 100% of creator fees — no interface cut, no platform overhead.

**Source:** https://github.com/Quick-Intel/openclaw-skills/tree/main/token-launcher
**Publisher:** Quick Intel / Web3 Collective — https://quickintel.io

---

## ⚠️ Security First

Direct Mode requires private key access for transaction signing. Before implementing:

1. **Create a dedicated launch wallet** — never reuse your main wallet or a wallet holding significant funds
2. **Use a secrets manager** — load private keys from AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault, or equivalent. Never hardcode keys or store them in plaintext `.env` files in production
3. **Test with minimal funds** — fund your launch wallet with only what's needed for gas. On Base, ~0.01 ETH is sufficient. On Solana, ~0.05 SOL
4. **Verify contract addresses** — before calling any contract, verify the address matches the official deployment. Check Basescan, Arbiscan, or Solscan
5. **Audit third-party SDKs** — Clanker SDK, Flaunch contracts, and Pump.fun programs are maintained by their respective teams, not by Quick Intel. Review their repos before trusting them with real value

Code examples in this reference and the per-platform guides use placeholder variable names like `PRIVATE_KEY` and `RPC_URL`. These represent values that should be loaded securely at runtime — they are never sent to any external service.

---

## What You Need

| Requirement | Why | Security Note |
|-------------|-----|---------------|
| **RPC endpoint** | Talk to the blockchain | Use authenticated endpoints from Alchemy, QuickNode, or Helius. Not sensitive but keep private to avoid rate limit abuse |
| **Signing wallet** | Sign transactions your agent creates | **Dedicated launch wallet only.** Store key in a secrets manager, never in plaintext. Fund with minimal gas |
| **SDK / libraries** | Clanker SDK, viem/ethers for EVM, @solana/web3.js for Solana | Verify package integrity. Pin versions in package.json |
| **IPFS upload** | For token metadata (name, image, description) | API keys for Pinata/web3.storage are sensitive — store securely |
| **Native token for gas** | ETH on EVM chains, SOL on Solana | Only fund what's needed. ~0.01 ETH on Base, ~0.05 SOL on Solana |

---

## Fee Economics Deep Dive

Understanding how fees flow on each platform is critical. This is where you make your money.

### Clanker Fee Structure

Every swap on a Clanker token incurs a **1.2% total fee**:

```
Swap amount: $1,000
├── 1.0% pool fee ($10.00)
│   ├── Reward recipient 1: configurable BPS (e.g., 100% to you)
│   ├── Reward recipient 2: configurable BPS (e.g., 0% — or split with a partner)
│   └── You define up to N recipients with basis points totaling 10,000
└── 0.2% Clanker protocol fee ($2.00) — goes to Clanker, you can't change this
```

**In Direct Mode, you set the reward recipients.** You can send 100% of the 1% pool fee to yourself. Or split it across multiple wallets (a treasury, a dev fund, a co-creator). The 0.2% Clanker protocol fee always goes to Clanker — that's the cost of using their infrastructure.

**In Easy Mode (Tator API),** the split is automatically set to 90% you / 10% Tator. Tator's 10% comes out of the 1% pool fee — not on top of it.

**Reward configuration:**
- `recipients`: Array of `{ recipient, admin, bps, token }` — who gets paid, who can update, basis points (out of 10,000), which tokens ("Both" for pool fee token + paired token)
- `sniperFees`: Decaying fee to punish bots — starts high (66.7%), decays to normal (4.2%) over configurable seconds
- `pool.pairedToken`: WETH by default, or a stablecoin (USDC on Base/Arb/Mainnet, USDT on BSC)

### Flaunch Fee Structure

Flaunch uses an `AddressFeeSplitManager` contract to handle fee distribution:

```
Token swap fee
└── creatorFeeAllocation (set at launch, e.g., 100%)
    └── AddressFeeSplitManager
        ├── Recipient 1: 90% (your wallet)
        └── Recipient 2: 10% (another wallet, or 0% if you want 100%)
```

**In Direct Mode,** you deploy a custom fee split manager with whatever split you want. Set `recipientShares` to `[{ your_wallet, 100_00000 }]` for 100% to yourself. The basis points are in `share * 100000` format (so 90% = `90_00000`, 100% = `100_00000`).

**Key difference from Clanker:** Flaunch's fee manager is a separate deployed contract. You create it via `TreasuryManagerFactory.deployAndInitializeManager()` before launching the token, then pass it as the `treasuryManagerParams.manager` in the launch call.

### Pump.fun Fee Structure

Pump.fun uses a `SharingConfig` PDA to define fee splits:

```
Pre-graduation (bonding curve):
  Swap fees → Creator Vault (native SOL) → distributed to shareholders

Post-graduation (Raydium AMM):
  Swap fees → AMM Coin Creator Vault (WSOL)
  ↓ (transfer_creator_fees_to_pump instruction)
  → Creator Vault (native SOL)
  ↓ (distribute_creator_fees instruction)
  → Shareholders per sharing config BPS
```

**In Direct Mode,** you set up the sharing config with your own split. The fee sharing requires two instructions: `create_fee_sharing_config` (creates the config PDA) then `update_fee_shares` (sets the shareholders and their BPS). Total BPS must equal 10,000.

**Graduation matters:** Once a Pump.fun token hits the bonding curve threshold and migrates to Raydium, fees accumulate as WSOL in the AMM vault instead of native SOL in the pump vault. To claim post-graduation, you need to first run `transfer_creator_fees_to_pump` (unwraps WSOL → SOL into pump vault) then `distribute_creator_fees` (pays out shareholders). Both can be in one transaction.

---

## The 100% vs 90/10 Decision

| Factor | Direct Mode (100%) | Easy Mode (90/10) |
|--------|-------------------|-------------------|
| **Setup time** | Hours to days | Minutes |
| **Code required** | SDK integration, wallet management, RPC | One HTTP call |
| **Maintenance** | You handle upgrades, errors, RPC issues | Tator handles it |
| **Fee claiming** | You build the claim logic | One prompt |
| **Multi-chain** | You integrate each chain separately | One API, all chains |
| **Cost per launch** | Gas only | $0.20 API + gas |
| **Creator fee share** | 100% of pool fees | 90% of pool fees |
| **Best for** | High-volume launchers, custom integrations | Most agents and developers |

**Rule of thumb:** If you're launching 1-2 tokens, Easy Mode saves you days of work for a 10% fee that's negligible on small volume. If you're launching dozens of tokens or driving millions in volume, Direct Mode's 10% savings compounds into real money.

---

## Shared Patterns

### IPFS Metadata Upload

All three platforms need token metadata uploaded to IPFS. The metadata JSON:

```json
{
  "name": "Galaxy Cat",
  "symbol": "GCAT",
  "description": "Galaxy Cat ($GCAT) - The first feline in the cosmos",
  "image": "ipfs://QmYourImageHash",
  "external_link": ""
}
```

Upload the JSON to IPFS and use the returned URI as the token's `tokenUri` (Clanker/Flaunch) or `metadataUri` (Pump.fun). Services like Pinata, web3.storage, or Infura IPFS all work.

### Unsigned Transaction Pattern (EVM)

For agent wallets that sign externally (OpenClaw, Lobster.cash, Coinbase Agentic), you need to return unsigned transactions rather than executing directly. Both Clanker and Flaunch support this:

```typescript
// Get the transaction config from the SDK
const txConfig = await sdk.getSomeTransaction({ ... });

// Encode the calldata
const data = encodeFunctionData({
  abi: txConfig.abi,
  functionName: txConfig.functionName,
  args: txConfig.args,
});

// Return unsigned transaction for the agent to sign
return {
  to: txConfig.address,
  data: data,
  value: (txConfig.value || 0).toString(),
  gas: '300000',
};
```

Pump.fun on Solana works differently — it uses a bot wallet that signs and submits directly, because Solana transactions require all signers present at signing time. See [references/pumpfun.md](./references/pumpfun.md) for details.

### Fee Recipient Configuration

All three platforms let you set who receives creator fees at launch time. All three also let you update the recipient after launch:

| Platform | Set at Launch | Update After Launch | Who Can Update |
|----------|--------------|-------------------|----------------|
| Clanker | `rewards.recipients[].recipient` | `updateRewardRecipient()` | The `admin` of that reward entry |
| Flaunch | `recipientShares[].recipient` in the fee manager | `transferRecipientShare()` | The current recipient |
| Pump.fun | Shareholders in `update_fee_shares` | `update_fee_shares` with new shareholders | The config admin (bot wallet) |

### Security Scanning

After deploying via any platform, run a Quick Intel scan to verify the contract looks clean from an external perspective:

```bash
curl -X POST https://x402.quickintel.io/v1/scan/full \
  -H "Content-Type: application/json" \
  -H "PAYMENT-SIGNATURE: <x402_payment>" \
  -d '{"chain": "base", "tokenAddress": "0xYourDeployedToken"}'
```

This catches false positives that might scare off buyers (even legit tokens sometimes trip scanner heuristics) and verifies the deployed contract behaves as expected.

---

## Platform Implementation Guides

Each platform has its own reference file with full implementation details:

| Platform | Chains | Guide |
|----------|--------|-------|
| **Clanker v4** | Base, Arbitrum, Mainnet, Unichain, Abstract, Monad, BSC | [references/clanker.md](./references/clanker.md) |
| **Flaunch** | Base | [references/flaunch.md](./references/flaunch.md) |
| **Pump.fun** | Solana | [references/pumpfun.md](./references/pumpfun.md) |
