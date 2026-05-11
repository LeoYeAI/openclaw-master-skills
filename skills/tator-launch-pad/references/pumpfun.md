# Pump.fun — Direct Mode Reference

Launch SPL tokens on Solana with bonding curves that graduate to Raydium. Manual instruction building required due to Anchor IDL constraints. Supports custom fee sharing with configurable shareholder splits.

**Publisher:** Quick Intel / Web3 Collective — https://quickintel.io
**Source:** https://github.com/Quick-Intel/openclaw-skills/tree/main/token-launcher
**Pump.fun docs:** https://github.com/pump-fun/pump-public-docs

---

## Setup

```bash
npm install @solana/web3.js @solana/spl-token
```

```typescript
import {
  Connection,
  PublicKey,
  Transaction,
  TransactionInstruction,
  SystemProgram,
  Keypair,
  LAMPORTS_PER_SOL,
  ComputeBudgetProgram,
} from "@solana/web3.js";
import {
  TOKEN_2022_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
  getAssociatedTokenAddressSync,
} from "@solana/spl-token";

// Load securely from secrets manager — never hardcode
const connection = new Connection(process.env.SOLANA_RPC_URL, "confirmed");
const botWallet = Keypair.fromSecretKey(
  Buffer.from(JSON.parse(process.env.LAUNCH_WALLET_PRIVATE_KEY))
);
```

> **Security: Bot Wallet Model.** Pump.fun requires a signing wallet (Solana transactions need all signers present). This wallet is the on-chain "creator" of the token. **Use a dedicated wallet funded with only ~0.05 SOL for gas.** Never use your main wallet. The private key must be stored in a secrets manager — never in plaintext. This wallet signs launch and fee-sharing transactions but never holds token value. See the [Security section in REFERENCE.md](../REFERENCE.md) for details.

---

## Why Manual Instruction Building

Pump.fun uses Anchor, but the IDL has compatibility issues with many client environments. The reliable approach is building instructions manually with the correct discriminators and account layouts. This is what production implementations use.

---

## Program IDs

```typescript
const PUMP_PROGRAM_ID = new PublicKey("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P");
const PUMP_FEES_PROGRAM_ID = new PublicKey("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ");
const PUMP_AMM_PROGRAM_ID = new PublicKey("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA");
const GLOBAL_PDA = new PublicKey("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf");
const MINT_AUTHORITY_PDA = new PublicKey("TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM");
const EVENT_AUTHORITY_PDA = new PublicKey("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1");
const MAYHEM_PROGRAM_ID = new PublicKey("MAyhSmzXzV1pTf7LsNkrNwkWKTo4ougAJ1PPg47MD4e");
const WSOL_MINT = new PublicKey("So11111111111111111111111111111111111111112");
const SPL_TOKEN_PROGRAM_ID = new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA");
```

---

## Instruction Discriminators

These are the first 8 bytes of each instruction (Anchor convention — SHA256 of `global:<function_name>`):

```typescript
const CREATE_V2 = Buffer.from([214, 144, 76, 236, 95, 139, 49, 180]);
const CREATE_FEE_SHARING_CONFIG = Buffer.from([195, 78, 86, 76, 111, 52, 251, 213]);
const UPDATE_FEE_SHARES = Buffer.from([189, 13, 136, 99, 187, 164, 237, 35]);
const DISTRIBUTE_CREATOR_FEES = Buffer.from([165, 114, 103, 0, 121, 206, 247, 81]);
const TRANSFER_CREATOR_FEES_TO_PUMP = Buffer.from([0x8b, 0x34, 0x86, 0x55, 0xe4, 0xe5, 0x6c, 0xf1]);
```

---

## Borsh Serialization Helper

Solana instructions use Borsh serialization for strings:

```typescript
function serializeString(str: string): Buffer {
  const strBuffer = Buffer.from(str, "utf8");
  const lengthBuffer = Buffer.alloc(4);
  lengthBuffer.writeUInt32LE(strBuffer.length, 0);
  return Buffer.concat([lengthBuffer, strBuffer]);
}
```

---

## Launch a Token

### Step 1: Create the Token (createV2)

```typescript
const mintKeypair = Keypair.generate();

// Derive PDAs
const [bondingCurve] = PublicKey.findProgramAddressSync(
  [Buffer.from("bonding-curve"), mintKeypair.publicKey.toBuffer()],
  PUMP_PROGRAM_ID
);

const [associatedBondingCurve] = PublicKey.findProgramAddressSync(
  [
    bondingCurve.toBuffer(),
    TOKEN_2022_PROGRAM_ID.toBuffer(),
    mintKeypair.publicKey.toBuffer(),
  ],
  ASSOCIATED_TOKEN_PROGRAM_ID
);

const [creatorVault] = PublicKey.findProgramAddressSync(
  [Buffer.from("creator-vault"), botWallet.publicKey.toBuffer()],
  PUMP_PROGRAM_ID
);

const [globalParams] = PublicKey.findProgramAddressSync(
  [Buffer.from("global-params")],
  MAYHEM_PROGRAM_ID
);

const [solVault] = PublicKey.findProgramAddressSync(
  [Buffer.from("sol-vault")],
  MAYHEM_PROGRAM_ID
);

const [mayhemState] = PublicKey.findProgramAddressSync(
  [Buffer.from("mayhem-state"), mintKeypair.publicKey.toBuffer()],
  MAYHEM_PROGRAM_ID
);

// Build instruction data
const instructionData = Buffer.concat([
  CREATE_V2,
  serializeString("Galaxy Cat"),           // name
  serializeString("GCAT"),                 // symbol
  serializeString(METADATA_IPFS_URI),      // metadata URI
  botWallet.publicKey.toBuffer(),          // creator (bot wallet is on-chain creator)
  Buffer.from([0]),                        // is_mayhem_mode: false
]);

// Account metas (must match IDL order exactly)
const keys = [
  { pubkey: mintKeypair.publicKey, isSigner: true, isWritable: true },
  { pubkey: MINT_AUTHORITY_PDA, isSigner: false, isWritable: false },
  { pubkey: bondingCurve, isSigner: false, isWritable: true },
  { pubkey: associatedBondingCurve, isSigner: false, isWritable: true },
  { pubkey: GLOBAL_PDA, isSigner: false, isWritable: false },
  { pubkey: botWallet.publicKey, isSigner: true, isWritable: true },
  { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
  { pubkey: TOKEN_2022_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: MAYHEM_PROGRAM_ID, isSigner: false, isWritable: true },
  { pubkey: globalParams, isSigner: false, isWritable: false },
  { pubkey: solVault, isSigner: false, isWritable: true },
  { pubkey: mayhemState, isSigner: false, isWritable: true },
  { pubkey: associatedBondingCurve, isSigner: false, isWritable: true },
  { pubkey: EVENT_AUTHORITY_PDA, isSigner: false, isWritable: false },
  { pubkey: PUMP_PROGRAM_ID, isSigner: false, isWritable: false },
];

const createInstruction = new TransactionInstruction({
  keys,
  programId: PUMP_PROGRAM_ID,
  data: instructionData,
});

// Build and send transaction
const transaction = new Transaction();
transaction.add(
  ComputeBudgetProgram.setComputeUnitLimit({ units: 400_000 }),
  ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 1_000_000 })
);
transaction.add(createInstruction);

const { blockhash } = await connection.getLatestBlockhash("confirmed");
transaction.recentBlockhash = blockhash;
transaction.feePayer = botWallet.publicKey;
transaction.sign(botWallet, mintKeypair); // Both must sign

const txHash = await connection.sendRawTransaction(transaction.serialize(), {
  skipPreflight: false,
  maxRetries: 3,
});
await connection.confirmTransaction(txHash, "confirmed");
```

### Step 2: Set Up Fee Sharing

Fee sharing requires TWO instructions in a single transaction:

1. `create_fee_sharing_config` — creates the sharing config PDA
2. `update_fee_shares` — sets the shareholders and their BPS

```typescript
const [sharingConfig] = PublicKey.findProgramAddressSync(
  [Buffer.from("sharing-config"), mintKeypair.publicKey.toBuffer()],
  PUMP_FEES_PROGRAM_ID
);

const [feesEventAuthority] = PublicKey.findProgramAddressSync(
  [Buffer.from("__event_authority")],
  PUMP_FEES_PROGRAM_ID
);

const [pumpEventAuthority] = PublicKey.findProgramAddressSync(
  [Buffer.from("__event_authority")],
  PUMP_PROGRAM_ID
);

const [ammEventAuthority] = PublicKey.findProgramAddressSync(
  [Buffer.from("__event_authority")],
  PUMP_AMM_PROGRAM_ID
);

// === Instruction 1: create_fee_sharing_config ===

const createConfigKeys = [
  { pubkey: feesEventAuthority, isSigner: false, isWritable: false },
  { pubkey: PUMP_FEES_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: botWallet.publicKey, isSigner: true, isWritable: true },
  { pubkey: GLOBAL_PDA, isSigner: false, isWritable: false },
  { pubkey: mintKeypair.publicKey, isSigner: false, isWritable: false },
  { pubkey: sharingConfig, isSigner: false, isWritable: true },
  { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
  { pubkey: bondingCurve, isSigner: false, isWritable: true },
  { pubkey: PUMP_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: pumpEventAuthority, isSigner: false, isWritable: false },
  { pubkey: PUMP_FEES_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: PUMP_AMM_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: ammEventAuthority, isSigner: false, isWritable: false },
];

const createConfigIx = new TransactionInstruction({
  keys: createConfigKeys,
  programId: PUMP_FEES_PROGRAM_ID,
  data: CREATE_FEE_SHARING_CONFIG,
});

// === Instruction 2: update_fee_shares ===

const [pumpCreatorVault] = PublicKey.findProgramAddressSync(
  [Buffer.from("creator-vault"), sharingConfig.toBuffer()],
  PUMP_PROGRAM_ID
);

const [coinCreatorVaultAuthority] = PublicKey.findProgramAddressSync(
  [Buffer.from("creator_vault"), sharingConfig.toBuffer()],
  PUMP_AMM_PROGRAM_ID
);

const coinCreatorVaultAta = getAssociatedTokenAddressSync(
  WSOL_MINT,
  coinCreatorVaultAuthority,
  true,
  SPL_TOKEN_PROGRAM_ID
);

// Serialize shareholders: 100% to your wallet
const shareholdersCount = Buffer.alloc(4);
shareholdersCount.writeUInt32LE(1, 0); // 1 shareholder

const feeBps = Buffer.alloc(2);
feeBps.writeUInt16LE(10000, 0); // 100% = 10000 BPS

const shareholder = Buffer.concat([
  YOUR_SOLANA_WALLET.toBuffer(), // Your wallet gets 100%
  feeBps,
]);

const updateFeesData = Buffer.concat([
  UPDATE_FEE_SHARES,
  shareholdersCount,
  shareholder,
]);

const updateFeesKeys = [
  { pubkey: feesEventAuthority, isSigner: false, isWritable: false },
  { pubkey: PUMP_FEES_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: botWallet.publicKey, isSigner: true, isWritable: true },
  { pubkey: GLOBAL_PDA, isSigner: false, isWritable: false },
  { pubkey: mintKeypair.publicKey, isSigner: false, isWritable: false },
  { pubkey: sharingConfig, isSigner: false, isWritable: true },
  { pubkey: bondingCurve, isSigner: false, isWritable: false },
  { pubkey: pumpCreatorVault, isSigner: false, isWritable: true },
  { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
  { pubkey: PUMP_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: pumpEventAuthority, isSigner: false, isWritable: false },
  { pubkey: PUMP_AMM_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: ammEventAuthority, isSigner: false, isWritable: false },
  { pubkey: WSOL_MINT, isSigner: false, isWritable: false },
  { pubkey: SPL_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: coinCreatorVaultAuthority, isSigner: false, isWritable: true },
  { pubkey: coinCreatorVaultAta, isSigner: false, isWritable: true },
  { pubkey: botWallet.publicKey, isSigner: false, isWritable: false },
];

const updateFeesIx = new TransactionInstruction({
  keys: updateFeesKeys,
  programId: PUMP_FEES_PROGRAM_ID,
  data: updateFeesData,
});

// Both instructions in one transaction
const feeTx = new Transaction();
feeTx.add(
  ComputeBudgetProgram.setComputeUnitLimit({ units: 300_000 }),
  ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 1_000_000 })
);
feeTx.add(createConfigIx);
feeTx.add(updateFeesIx);
// Sign and send...
```

### Multiple Shareholders

```typescript
// 70% to creator, 30% to treasury
const shareholdersCount = Buffer.alloc(4);
shareholdersCount.writeUInt32LE(2, 0);

const bps1 = Buffer.alloc(2);
bps1.writeUInt16LE(7000, 0); // 70%

const bps2 = Buffer.alloc(2);
bps2.writeUInt16LE(3000, 0); // 30%

const shareholder1 = Buffer.concat([CREATOR_PUBKEY.toBuffer(), bps1]);
const shareholder2 = Buffer.concat([TREASURY_PUBKEY.toBuffer(), bps2]);

const data = Buffer.concat([
  UPDATE_FEE_SHARES,
  shareholdersCount,
  shareholder1,
  shareholder2,
]);
```

Total BPS must equal 10,000.

---

## Graduation: Pre vs Post

Pump.fun tokens start on a bonding curve. Once the market cap threshold is hit, the token "graduates" to Raydium AMM. This changes how fees accumulate:

```
PRE-GRADUATION:
  Swap fees → Creator Vault (native SOL)
  └── distribute_creator_fees → shareholders

POST-GRADUATION:
  Swap fees → AMM Coin Creator Vault (WSOL)
  └── transfer_creator_fees_to_pump → unwrap WSOL → Creator Vault (SOL)
      └── distribute_creator_fees → shareholders
```

### Detecting Graduation

Read the bonding curve account and check the `complete` field at byte offset 48:

```typescript
const [bondingCurve] = PublicKey.findProgramAddressSync(
  [Buffer.from("bonding-curve"), tokenMint.toBuffer()],
  PUMP_PROGRAM_ID
);

const accountInfo = await connection.getAccountInfo(bondingCurve);
// Layout: 8 byte discriminator + 5x u64 (40 bytes) = offset 48
const isGraduated = accountInfo.data[48] === 1;
```

---

## Check Unclaimed Fees

Check both vaults — pump vault (native SOL) and AMM vault (WSOL):

```typescript
const [sharingConfig] = PublicKey.findProgramAddressSync(
  [Buffer.from("sharing-config"), tokenMint.toBuffer()],
  PUMP_FEES_PROGRAM_ID
);

const [pumpCreatorVault] = PublicKey.findProgramAddressSync(
  [Buffer.from("creator-vault"), sharingConfig.toBuffer()],
  PUMP_PROGRAM_ID
);

// Always check pump vault (native SOL)
const pumpBalance = await connection.getBalance(pumpCreatorVault);
const pumpSOL = pumpBalance / LAMPORTS_PER_SOL;

// If graduated, also check AMM vault (WSOL)
let ammWSOL = 0;
if (isGraduated) {
  const [vaultAuthority] = PublicKey.findProgramAddressSync(
    [Buffer.from("creator_vault"), sharingConfig.toBuffer()],
    PUMP_AMM_PROGRAM_ID
  );

  const vaultAta = getAssociatedTokenAddressSync(
    WSOL_MINT,
    vaultAuthority,
    true,
    SPL_TOKEN_PROGRAM_ID
  );

  try {
    const tokenBalance = await connection.getTokenAccountBalance(vaultAta);
    ammWSOL = parseFloat(tokenBalance.value.uiAmountString || "0");
  } catch {
    ammWSOL = 0; // ATA may not exist yet
  }
}

const totalUnclaimed = pumpSOL + ammWSOL;
```

---

## Claim Fees

### Pre-Graduation (SOL only)

One instruction — `distribute_creator_fees`:

```typescript
const distributeKeys = [
  { pubkey: tokenMint, isSigner: false, isWritable: false },
  { pubkey: bondingCurve, isSigner: false, isWritable: false },
  { pubkey: sharingConfig, isSigner: false, isWritable: false },
  { pubkey: pumpCreatorVault, isSigner: false, isWritable: true },
  { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
  { pubkey: pumpEventAuthority, isSigner: false, isWritable: false },
  { pubkey: PUMP_PROGRAM_ID, isSigner: false, isWritable: false },
  // Append ALL shareholders as remaining accounts (writable, signer if it's the bot)
  ...shareholders.map((s) => ({
    pubkey: s.address,
    isSigner: s.address.equals(botWallet.publicKey),
    isWritable: true,
  })),
];

const distributeIx = new TransactionInstruction({
  keys: distributeKeys,
  programId: PUMP_PROGRAM_ID,
  data: DISTRIBUTE_CREATOR_FEES,
});
```

### Post-Graduation (WSOL → SOL → Shareholders)

Two instructions in one transaction:

```typescript
const transaction = new Transaction();
transaction.add(
  ComputeBudgetProgram.setComputeUnitLimit({ units: 200_000 }),
  ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 1_000_000 })
);

// Instruction 1: Transfer WSOL from AMM vault → unwrap → pump vault
const transferKeys = [
  { pubkey: WSOL_MINT, isSigner: false, isWritable: false },
  { pubkey: SPL_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
  { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
  { pubkey: sharingConfig, isSigner: false, isWritable: false },         // coin_creator
  { pubkey: ammCoinCreatorVaultAuthority, isSigner: false, isWritable: true },
  { pubkey: ammCoinCreatorVaultAta, isSigner: false, isWritable: true },
  { pubkey: pumpCreatorVault, isSigner: false, isWritable: true },
  { pubkey: ammEventAuthority, isSigner: false, isWritable: false },
  { pubkey: PUMP_AMM_PROGRAM_ID, isSigner: false, isWritable: false },
];

transaction.add(
  new TransactionInstruction({
    keys: transferKeys,
    programId: PUMP_AMM_PROGRAM_ID,
    data: TRANSFER_CREATOR_FEES_TO_PUMP,
  })
);

// Instruction 2: Distribute SOL from pump vault to shareholders
transaction.add(distributeIx); // Same as pre-graduation

// Sign and send
```

### Minimum Claimable Amount

Pump.fun requires a minimum balance in the creator vault before distribution will succeed:

```typescript
const MIN_DISTRIBUTABLE_LAMPORTS = 9_799_680; // ~0.0098 SOL
```

Check the vault balance exceeds this before attempting to claim.

---

## Update Fee Recipient

Use `update_fee_shares` with the new shareholders in the instruction data and the **current** shareholders as remaining accounts:

```typescript
// New shareholders (what you're updating TO)
const newShareholderData = Buffer.concat([
  UPDATE_FEE_SHARES,
  shareholdersCount,
  Buffer.concat([NEW_RECIPIENT.toBuffer(), newBps]),  // New shareholder
]);

// Account keys — current shareholders go as remaining accounts
const updateKeys = [
  // ... fixed accounts (same as initial setup) ...
  // REMAINING ACCOUNTS: Current shareholders for validation
  { pubkey: CURRENT_RECIPIENT, isSigner: false, isWritable: true },
];
```

**The key insight:** The instruction data contains the NEW shareholders, but the remaining accounts must contain the CURRENT shareholders. The program validates that the current state matches before allowing the update.

---

## Parsing Shareholders from Account Data

Read the sharing config PDA to see current shareholders:

```typescript
// SharingConfig layout:
//   8  bytes - Anchor discriminator
//   1  byte  - bump
//   1  byte  - version
//   1  byte  - status (0=Paused, 1=Active)
//   32 bytes - mint pubkey
//   32 bytes - admin pubkey
//   1  byte  - admin_revoked
//   4  bytes - shareholders vec length (u32 LE)
//   N × 34  - each Shareholder { address: 32 bytes, share_bps: u16 }

const VEC_OFFSET = 76; // 8 + 1 + 1 + 1 + 32 + 32 + 1

function parseShareholders(data: Buffer) {
  const count = data.readUInt32LE(VEC_OFFSET);
  const shareholders = [];
  let offset = VEC_OFFSET + 4;

  for (let i = 0; i < count; i++) {
    const address = new PublicKey(data.slice(offset, offset + 32));
    offset += 32;
    const shareBps = data.readUInt16LE(offset);
    offset += 2;
    shareholders.push({ address, shareBps });
  }

  return shareholders;
}
```

---

## Bot Wallet Model

Unlike Clanker and Flaunch where the user's wallet can sign transactions directly, Pump.fun requires a **bot wallet** pattern:

- The bot wallet is the on-chain "creator" (it signs the `createV2` instruction)
- The bot wallet signs fee sharing and claim transactions
- The actual user/agent is set as a shareholder to receive fees
- The bot wallet needs SOL for gas (minimum ~0.02 SOL per launch)

**This means:** For Pump.fun, your agent needs a dedicated Solana keypair that stays funded. This is different from the EVM model where you can return unsigned transactions for any external wallet to sign.

---

## Metadata Upload

Pump.fun expects metadata at an IPFS URI. Upload a JSON file:

```json
{
  "name": "Galaxy Cat",
  "symbol": "GCAT",
  "description": "Galaxy Cat ($GCAT) - The first feline in the cosmos",
  "image": "https://example.com/gcat.png",
  "twitter": ""
}
```

You can use pump.fun's own IPFS endpoint or any IPFS pinning service.

---

## Important Notes

- **Solana only** — Pump.fun doesn't support EVM chains
- **Token-2022 standard** — not legacy SPL tokens
- **Bot wallet required** — Solana's signing model means you can't return unsigned transactions for an external wallet to sign (all signers must be present)
- **Graduation is one-way** — once graduated to Raydium, the bonding curve is permanently closed
- **Minimum claim threshold** — ~0.0098 SOL must be in the vault before distribution works
- **Fee sharing config is per-token** — each token has its own sharing config PDA derived from the mint
- **Admin can be revoked** — once admin is revoked on the sharing config, no more shareholder updates are possible
