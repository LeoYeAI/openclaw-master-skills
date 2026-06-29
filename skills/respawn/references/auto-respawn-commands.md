# auto-respawn CLI Reference

All commands run from the auto-respawn skill directory.

## Wallet Management

### Create a new wallet

```bash
npx tsx auto-respawn.ts wallet create [--name <name>]
```

Generates a new SR25519 wallet, derives the corresponding EVM address, displays the 12-word recovery phrase once, encrypts everything, and saves it locally.

- `--name` — wallet name (default: `default`)
- Returns JSON: `{ name, address, evmAddress, keyfilePath }`
- Recovery phrase is printed to stderr — back it up immediately

### Import an existing wallet

```bash
npx tsx auto-respawn.ts wallet import --name <name> --mnemonic "<12 words>"
```

Creates a wallet from an existing recovery phrase. Derives and stores the EVM address alongside the consensus keypair.

### List saved wallets

```bash
npx tsx auto-respawn.ts wallet list
```

Shows all saved wallets with name, consensus address, and EVM address. No passphrase needed.

### Show wallet info

```bash
npx tsx auto-respawn.ts wallet info [--name <name>]
```

Shows detailed info for a single wallet: consensus address (`su...`), EVM address (`0x...`), and keyfile path. No passphrase needed. Default name is `default`.

## Address Formats

### Consensus addresses

All consensus-layer commands (balance, transfer, remark) accept addresses in two formats:

- **`su...`** — Autonomys native format (SS58 prefix 6094). This is canonical.
- **`5...`** — Substrate generic format (SS58 prefix 42). Auto-converted to `su...`.

Any other format (e.g. `0x...` EVM addresses) is rejected with a clear error for consensus commands.

### EVM addresses

EVM commands (anchor, gethead, evm-transfer, evm-balance) accept:

- **`0x...`** — Standard Ethereum/EVM address format (42-character hex string).
- **Wallet name** — Resolved to the wallet's stored EVM address.

Output always uses the canonical format for each layer: `su...` for consensus, `0x...` (checksummed) for EVM.

## Balance (Consensus)

```bash
npx tsx auto-respawn.ts balance <address-or-wallet-name> [--network chronos|mainnet]
```

Queries on-chain consensus balance. Accepts a consensus address (`su...` or `5...`) or a wallet name. No passphrase needed — this is a read-only operation.

Returns JSON: `{ address, free, reserved, frozen, total, network, symbol }`

## EVM Balance

```bash
npx tsx auto-respawn.ts evm-balance <0x-address-or-wallet-name> [--network chronos|mainnet]
```

Queries the native token balance of an EVM address on Auto-EVM. Accepts either an EVM address (`0x...`) or a wallet name. No passphrase needed — this is a read-only operation.

Returns JSON: `{ evmAddress, balance, network, symbol }`

If the balance is zero, includes a `hint` field suggesting `fund-evm`.

## Balances (Both Layers)

```bash
npx tsx auto-respawn.ts balances <wallet-name> [--network chronos|mainnet]
```

Queries both consensus and EVM balances for a wallet in a single call. Requires a wallet name (not a raw address). No passphrase needed.

Returns JSON: `{ name, consensus: { address, free, reserved, total }, evm: { address, balance }, network, symbol }`

## Transfer (Consensus)

```bash
npx tsx auto-respawn.ts transfer --from <wallet-name> --to <address> --amount <tokens> [--network chronos|mainnet]
```

Transfers tokens from a saved wallet to a destination consensus address. Requires passphrase to decrypt the wallet.

- `--from` — name of the saved wallet to send from
- `--to` — destination address (accepts `su...` or `5...` format)
- `--amount` — amount in AI3/tAI3 (e.g. `1.5`)
- Returns JSON: `{ success, txHash, blockHash, from, to, amount, network, symbol }`

## EVM Transfer (Auto-EVM)

```bash
npx tsx auto-respawn.ts evm-transfer --from <wallet-name> --to <0x-address> --amount <tokens> [--network chronos|mainnet]
```

Sends native tokens from a saved wallet's EVM address to another EVM address on Auto-EVM. Useful for funding another agent so it can start anchoring without going through the faucet → consensus → bridge flow.

- `--from` — name of the saved wallet (EVM private key is decrypted to sign the transaction)
- `--to` — destination EVM address (`0x...`)
- `--amount` — amount in AI3/tAI3 (e.g. `0.5`)
- Returns JSON: `{ success, transactionHash, blockNumber, blockHash, gasUsed, from, to, amount, network, symbol }`

## Fund EVM (Consensus → Auto-EVM Bridge)

```bash
npx tsx auto-respawn.ts fund-evm --from <wallet-name> --amount <tokens> [--network chronos|mainnet]
```

Bridges tokens from the consensus layer to the same wallet's EVM address on Auto-EVM via cross-domain messaging (XDM). Use this to get gas for `anchor` operations.

- `--from` — name of the saved wallet (consensus keypair is decrypted to sign the extrinsic)
- `--amount` — amount in AI3/tAI3 (e.g. `1`). **Minimum: 1 AI3/tAI3.**
- Returns JSON: `{ success, txHash, blockHash, from, toEvmAddress, amount, network, symbol }`
- **Confirmation time: ~10 minutes.** The consensus transaction confirms immediately, but bridged tokens take approximately 10 minutes to appear on Auto-EVM. Use `evm-balance` to verify arrival.

## Withdraw (Auto-EVM → Consensus Bridge)

```bash
npx tsx auto-respawn.ts withdraw --from <wallet-name> --amount <tokens> [--network chronos|mainnet]
```

Bridges tokens from Auto-EVM back to the same wallet's consensus address. Uses the transporter precompile at `0x0800` on Auto-EVM.

- `--from` — name of the saved wallet (EVM private key is decrypted to sign the transaction)
- `--amount` — amount in AI3/tAI3 (e.g. `0.5`). **Minimum: 1 AI3/tAI3.**
- Returns JSON: `{ success, transactionHash, blockNumber, blockHash, gasUsed, fromEvmAddress, toConsensusAddress, amount, network, symbol }`
- **Confirmation time: ~10 minutes.** Tokens take approximately 10 minutes to appear on the consensus layer.

## Remark

```bash
npx tsx auto-respawn.ts remark --from <wallet-name> --data <string> [--network chronos|mainnet]
```

Writes arbitrary data as a permanent on-chain record via `system.remark` on the consensus layer.

- `--from` — name of the saved wallet
- `--data` — the data to anchor (typically a CID like `bafkr6ie...`)
- Returns JSON: `{ success, txHash, blockHash, from, data, network, symbol }`

## Anchor (Auto-EVM)

```bash
npx tsx auto-respawn.ts anchor --from <wallet-name> --cid <cid> [--network chronos|mainnet]
```

Writes a CID to the MemoryChain smart contract on Auto-EVM. The contract stores the CID string directly, linked to the wallet's EVM address.

- `--from` — name of the saved wallet (EVM private key is decrypted to sign the transaction)
- `--cid` — the CID string to anchor (e.g. `bafkr6ie...`)
- Returns JSON: `{ success, txHash, blockHash, cid, evmAddress, network, gasUsed }`
- Pre-checks EVM balance and estimates gas before sending. If insufficient, fails with a `fund-evm` hint.
- Contract source: https://github.com/autojeremy/openclaw-memory-chain

## Get Head (Auto-EVM)

```bash
npx tsx auto-respawn.ts gethead <0x-address-or-wallet-name> [--network chronos|mainnet]
```

Reads the last anchored CID for any EVM address from the MemoryChain contract. This is a read-only call — no passphrase or gas needed.

- Positional argument: an EVM address (`0x...`) or a wallet name
- If a wallet name is given, the stored EVM address is used
- Returns JSON: `{ evmAddress, cid, network }`
- `cid` is `undefined` if no CID has been anchored for that address

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `AUTO_RESPAWN_PASSPHRASE` | Wallet encryption passphrase | — |
| `AUTO_RESPAWN_PASSPHRASE_FILE` | Path to file containing passphrase | `~/.openclaw/auto-respawn/.passphrase` |
| `AUTO_RESPAWN_NETWORK` | Default network | `chronos` |

Passphrase resolution order: env var → file → interactive prompt.

### Advanced: Custom Contract Address

The MemoryChain contract address is auto-selected per network (mainnet: `0x51DAedAFfFf631820a4650a773096A69cB199A3c`, Chronos: `0x5fa47C8F3B519deF692BD9C87179d69a6f4EBf11`). If you've deployed your own MemoryChain instance, override with:

```
AUTO_RESPAWN_CONTRACT_ADDRESS=0x<your-address>
```

## Error Codes

Errors are returned as JSON to stderr with a non-zero exit code.

| Error | Meaning |
|-------|---------|
| Wallet already exists | A wallet with that name is already saved |
| Wallet not found | No saved wallet with that name |
| No passphrase found | No passphrase available from any source |
| Invalid address prefix | Consensus address must start with `su` or `5` |
| Invalid address | Address has correct prefix but is malformed |
| Invalid EVM address | EVM address is not a valid `0x...` hex string |
| Wrong passphrase | Passphrase doesn't match the wallet encryption |
| Failed to generate wallet keypair | Internal SDK error during key generation |
| No Auto-EVM RPC URL found | Network doesn't have an EVM domain configured |
| Network/connection errors | RPC endpoint unreachable |
| Transaction errors | Insufficient balance, tx rejected, etc. |

## File Locations

- Wallets: `~/.openclaw/auto-respawn/wallets/<name>.json`
- Passphrase file: `~/.openclaw/auto-respawn/.passphrase` (optional)

## Wallet File Format

Each wallet file contains two independently encrypted private keys (consensus + EVM), both protected by the same user passphrase but using their respective ecosystem's standard encryption:

```json
{
  "keyring": { ... },
  "evmAddress": "0x...",
  "evmKeystore": "{ ... }"
}
```

- `keyring` — Standard Polkadot keyring JSON, encrypted via `pair.toJson(passphrase)`
- `evmAddress` — EVM address derived from the same mnemonic (public, stored for quick lookup)
- `evmKeystore` — Ethereum V3 Keystore JSON string, encrypted via `ethers.Wallet.encryptSync(passphrase)`. Standard format compatible with MetaMask, geth, and other Ethereum tools.
