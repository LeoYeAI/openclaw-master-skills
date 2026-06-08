# Staking Commands Reference

## Create a New Stake

```bash
sol stake new <amount>
```

Creates a stake account, funds it with `<amount>` SOL, and delegates
to a validator — all in a single transaction.

### Examples

```bash
sol stake new 10                          # stake 10 SOL (default validator)
sol stake new 5 --validator DPm...xyz     # specific validator
sol stake new 10 --wallet cold            # from a specific wallet
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--validator <vote-address>` | Solana Compass | Validator to delegate to |
| `--wallet <name>` | default | Wallet to fund the stake from |

### Example Output

```
Staked 10 SOL with Solana Compass (Comp4F...xYz)
  Stake account: 7gK...def
  Tx: https://solscan.io/tx/3xY...abc
```

## List Stake Accounts

```bash
sol stake list
sol stake list --wallet cold
```

Shows all stake accounts for the wallet — address, amount staked,
validator, status (activating/active/deactivating/inactive), and
any claimable MEV tips.

Hints at `sol stake claim-mev` when tips are available.

### Example Output

```
Stake Account   Balance        Status  Validator
─────────────────────────────────────────────────────────
7gK3a2...def    10.0500 SOL *  active  Comp4F...xYz

* 0.050000 SOL claimable MEV across 1 account. Run `sol stake claim-mev` to compound.
```

## Claim MEV Tips

```bash
sol stake claim-mev
sol stake claim-mev --withdraw
sol stake claim-mev 7gK...def
```

Claims MEV tips earned by your stake accounts.

| Flag | Default | Description |
|------|---------|-------------|
| `--withdraw` | false | Send tips to wallet instead of re-staking (compounding) |
| `--wallet <name>` | default | Wallet that owns the stake accounts |

By default, tips are compounded (re-staked). Use `--withdraw` to
withdraw them to your wallet instead.

You can specify a single stake account address to claim from, or
omit it to claim from all accounts.

## Withdraw / Unstake

```bash
sol stake withdraw <stake-account> [amount]
```

Withdraws SOL from a stake account. Handles the deactivation process
automatically:

- **Active stake**: Deactivates first, then you can withdraw after the
  cooldown epoch
- **Inactive stake**: Withdraws immediately
- **Partially withdraw**: Specify an amount to split and withdraw

### Examples

```bash
sol stake withdraw 7gK...abc              # withdraw all from this account
sol stake withdraw 7gK...abc 5            # withdraw 5 SOL (splits if needed)
sol stake withdraw 7gK...abc --force      # force deactivate active stake
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--wallet <name>` | default | Authority wallet |
| `--force` | false | Force deactivation of active stake |

## Validator Selection

The default validator is Solana Compass. Override with `--validator`:

```bash
sol stake new 10 --validator DPmsofDi1YBSvDJzeUSGMiHjEGkzKFKMZRiM7GYsTKcf
```

Use a vote account address (not the node identity).
