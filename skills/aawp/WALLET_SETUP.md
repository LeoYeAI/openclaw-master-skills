# AAWP Wallet Setup

For newly installed users.

## Goal

Safely complete this flow:
1. Check environment
2. Create wallet
3. Pin the real wallet address
4. Fund the wallet
5. Run first status / quote / small swap
6. Backup

## Core model

- **AI Signer**: signs transactions via daemon
- **Guardian**: submits tx, pays gas, can emergency freeze/unfreeze
- **Wallet**: onchain contract wallet that actually holds funds

Important: after creation, **fund the Wallet**, not the Guardian.

## Health check

```bash
cd /root/clawd/skills/aawp
bash scripts/doctor.sh
bash scripts/ensure-daemon.sh
```

If you hit:
- `E_AI_GATE`
- `hmac_mismatch`
- daemon / signer desync

run:

```bash
bash scripts/restart-daemon.sh
```

## Before create

Confirm:
- skill installed correctly
- daemon is healthy
- guardian exists
- guardian has a small amount of native gas token

## Create wallet

```bash
cd /root/clawd/skills/aawp
node scripts/wallet-manager.js --chain base create
```

This handles:
- predicted address
- commit / reveal
- cooldown / block wait
- proof request from daemon
- onchain wallet creation

Save the final wallet address.

## Pin the real wallet address

Do this immediately after creation:

```bash
export AAWP_WALLET=0xYourCreatedWallet
```

One-shot form:

```bash
AAWP_WALLET=0xYourCreatedWallet node scripts/wallet-manager.js --chain base status
```

Reason: predicted address can change when `binaryHash` changes. Real deployed wallets should be pinned explicitly.

## First funding

Send a small amount of native token to the **Wallet** address.
Do not confuse wallet balance with guardian balance.

## First test flow

```bash
AAWP_WALLET=0xYourCreatedWallet node scripts/wallet-manager.js --chain base status
AAWP_WALLET=0xYourCreatedWallet node scripts/wallet-manager.js --chain base balance
AAWP_WALLET=0xYourCreatedWallet node scripts/wallet-manager.js --chain base quote ETH USDC 0.00001
AAWP_WALLET=0xYourCreatedWallet node scripts/wallet-manager.js --chain base swap ETH USDC 0.00001
```

Recommended order:
1. `status`
2. `balance`
3. `quote`
4. very small `swap`
5. only then increase size

## Common mistakes

- Wallet created, but wallet has no funds
- Looking at guardian balance instead of wallet balance
- Not pinning `AAWP_WALLET`
- Retrying after `E_AI_GATE` instead of restarting daemon
- Putting seed / private key / token / recovery material into chat or logs

## Useful commands

```bash
node scripts/wallet-manager.js --chain base status
node scripts/wallet-manager.js --chain base balance
node scripts/wallet-manager.js compute-address
node scripts/wallet-manager.js portfolio

node scripts/wallet-manager.js --chain base send 0xRecipient 0.001
node scripts/wallet-manager.js --chain base send-token USDC 0xRecipient 1

node scripts/wallet-manager.js --chain base quote ETH USDC 0.01
node scripts/wallet-manager.js --chain base swap ETH USDC 0.01
node scripts/wallet-manager.js bridge base arb ETH ETH 0.05

node scripts/wallet-manager.js --chain base approve USDC 0xSpender 100
node scripts/wallet-manager.js --chain base allowance USDC 0xSpender
node scripts/wallet-manager.js --chain base revoke USDC 0xSpender

node scripts/wallet-manager.js --chain base call 0xTarget "transfer(address,uint256)" 0xRecipient 1000000
node scripts/wallet-manager.js --chain base read 0xTarget "balanceOf(address) returns (uint256)" 0xYourWallet
node scripts/wallet-manager.js --chain base batch ./calls.json

node scripts/wallet-manager.js addr add treasury 0x1234...
node scripts/wallet-manager.js addr list
node scripts/wallet-manager.js addr get treasury
node scripts/wallet-manager.js addr remove treasury

node scripts/wallet-manager.js get-rpc
node scripts/wallet-manager.js --chain base set-rpc https://your-rpc
node scripts/wallet-manager.js --chain base set-rpc default

node scripts/wallet-manager.js backup ./aawp-backup.tar.gz
node scripts/wallet-manager.js restore ./aawp-backup.tar.gz
```

## Backup

Backup soon after creation:

```bash
node scripts/wallet-manager.js backup ./aawp-backup.tar.gz
```

Restore:

```bash
node scripts/wallet-manager.js restore ./aawp-backup.tar.gz
```

Keep backups offline. Never commit recovery material to public repos.

## Minimal safe path

```bash
cd /root/clawd/skills/aawp
bash scripts/doctor.sh
bash scripts/ensure-daemon.sh
node scripts/wallet-manager.js --chain base create
export AAWP_WALLET=0xYourCreatedWallet
node scripts/wallet-manager.js --chain base status
node scripts/wallet-manager.js --chain base balance
node scripts/wallet-manager.js --chain base quote ETH USDC 0.00001
node scripts/wallet-manager.js --chain base swap ETH USDC 0.00001
node scripts/wallet-manager.js backup ./aawp-backup.tar.gz
```