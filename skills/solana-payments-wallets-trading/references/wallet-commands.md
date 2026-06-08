# Wallet Commands Reference

## Create a Wallet

```bash
sol wallet create                         # auto-named (wallet-1, wallet-2, ...)
sol wallet create --name trading          # pick a name
sol wallet create --name bot --count 5    # batch-create 5 wallets
```

Creates a new Ed25519 keypair and stores it as a JSON key file in
`~/.sol/wallets/<name>.json` (Solana CLI compatible format, chmod 600).

The first wallet created becomes the default for all commands.

### Example Output

```
Created wallet "trading"
  Address: 7nY...xyz
```

## List Wallets

```bash
sol wallet list                           # all wallets with SOL balances
sol wallet list --label trading           # filter by label
```

Shows wallet name, address, SOL balance, and whether it's the default.
Hints at `sol wallet balance <name>` for full token breakdown.

### Example Output

```
Name        Address                                          SOL     Labels
──────────────────────────────────────────────────────────────────────────────
* main      7nYz...xyzABCDEFGH1234567890abcdef1234567890   12.5000 SOL  trading
  cold      C9dz...hVVABCDEFGH1234567890abcdef1234567890    5.0000 SOL  —

Run `sol wallet balance` for full token balances and USD values.
```

## Check Balances

```bash
sol wallet balance                        # default wallet, all tokens + USD
sol wallet balance trading                # specific wallet
```

Displays every token held with current USD values.

### Example Output

```
Wallet: main (7nY...xyz)

Token   Balance        Price       Value
──────────────────────────────────────────────
SOL     12.500000      $150.25     $1,878.13
USDC    250.000000     $1.00       $250.00
BONK    5000000.000000 $0.000020   $100.00

Total: $2,228.13
```

## Import an Existing Wallet

```bash
sol wallet import --solana-cli            # from ~/.config/solana/id.json
sol wallet import ./keypair.json --name cold
sol wallet import /path/to/key.json
```

Copies the key file into `~/.sol/wallets/`. The `--solana-cli` flag
imports from the default Solana CLI keypair location.

## Export / Show Key File Path

```bash
sol wallet export main
```

Prints the file system path to the key file. Does NOT print the
private key itself.

## Remove a Wallet

```bash
sol wallet remove old-wallet
```

Removes the wallet from the registry. The key file is renamed with a
`.deleted` suffix (not permanently deleted) so it can be recovered.

## Set Default Wallet

```bash
sol wallet set-default trading
```

Changes which wallet is used when `--wallet` is not specified.

## Labels

```bash
sol wallet label main --add trading       # add a label
sol wallet label main --add defi --add bot  # multiple labels
sol wallet label main --remove trading    # remove a label
```

Labels are freeform tags for organizing wallets. Use them with
`sol wallet list --label <label>` to filter.

## Transaction History

```bash
sol wallet history                        # recent transactions
sol wallet history --limit 20            # more results
sol wallet history --type swap           # filter by type (swap, send, stake, lend)
sol wallet history trading               # specific wallet
```

Shows transactions from the local log — type, tokens, amounts, USD
values at execution time, and timestamps.

## Fund via Fiat Onramp

```bash
sol wallet fund                          # default wallet, default amount
sol wallet fund --amount 50              # specify USD amount
sol wallet fund trading --provider moonpay
```

Generates a URL to purchase SOL via a fiat onramp provider. Opens
in your browser.

## Wallet Flag

Any command accepts `--wallet <name>` to override the default wallet:

```bash
sol wallet balance --wallet trading
sol token swap 50 usdc bonk --wallet trading
sol stake new 10 --wallet cold
sol lend deposit 100 usdc --wallet defi
sol portfolio --wallet trading
```

## Data Storage

- Key files: `~/.sol/wallets/<name>.json`
- Wallet registry: `~/.sol/data.db` (SQLite)
- Config: `~/.sol/config.toml`
