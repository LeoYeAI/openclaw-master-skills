# Troubleshooting

## RPC Issues

### "Rate limited" or slow responses

The public Solana RPC (`api.mainnet-beta.solana.com`) rate-limits
aggressively. Set a dedicated RPC endpoint:

```bash
sol config set rpc.url https://your-rpc-endpoint.com
```

Free RPC tiers are available from Helius, Triton, and QuickNode.

### RPC resolution order

The CLI finds an RPC endpoint in this order:

1. `--rpc` flag on the command
2. `SOL_RPC_URL` environment variable
3. `~/.sol/config.toml` → `rpc.url`
4. Solana CLI config (`solana config get`)
5. Public mainnet RPC (with warning)

### "Failed to fetch blockhash" / connection errors

- Check that your RPC URL is correct: `sol config get rpc.url`
- Verify the endpoint is reachable: `curl <your-rpc-url> -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}'`
- Try a different RPC provider

## Token Resolution

### Wrong token resolved

Symbol search is ranked by liquidity, but ambiguous symbols can
resolve to the wrong token. To verify:

```bash
sol token info <symbol>       # check the mint address
```

To avoid ambiguity, use the mint address directly:

```bash
sol token swap 50 usdc EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

### "Token not found"

- Run `sol token sync` to refresh the local cache
- Use the full mint address instead of a symbol
- Check if the token exists on Jupiter: some very new or illiquid
  tokens may not be indexed yet

## Transaction Issues

### "Transaction simulation failed"

Common causes:
- **Insufficient balance**: Check with `sol wallet balance`
- **Slippage exceeded**: Increase with `--slippage <bps>` (e.g. `--slippage 200` for 2%)
- **Account not initialized**: The CLI creates associated token accounts
  automatically, but some edge cases may require manual setup

### "Transaction expired"

Solana transactions have a ~60-second lifetime. This can happen when:
- The RPC is slow to relay the transaction
- Network congestion is high

The CLI retries automatically with backoff. If it keeps failing, try
again or use a faster RPC endpoint.

### "Blockhash not found"

Usually means the transaction took too long to confirm. The CLI
handles retry logic, but persistent failures suggest RPC issues.

## Wallet Issues

### "No wallets found"

Create one:

```bash
sol wallet create --name main
```

Or import from Solana CLI:

```bash
sol wallet import --solana-cli
```

### "Wallet not found: <name>"

Check available wallets:

```bash
sol wallet list
```

Wallet names are case-sensitive.

### Recovering a removed wallet

`sol wallet remove` renames the key file to `<name>.json.deleted` in
`~/.sol/wallets/`. To recover, rename it back:

```bash
mv ~/.sol/wallets/old-wallet.json.deleted ~/.sol/wallets/old-wallet.json
```

Then re-import it:

```bash
sol wallet import ~/.sol/wallets/old-wallet.json --name old-wallet
```

## Staking Issues

### "Stake account is activating"

New stakes take 1 epoch (~2-3 days) to become active. During this
time, the account shows as "activating" and cannot be withdrawn.

### "Cannot withdraw active stake"

Active stake must be deactivated first. Use `--force` to deactivate:

```bash
sol stake withdraw 7gK...abc --force
```

After deactivation, wait one epoch for it to become inactive, then
withdraw.

## Database Issues

### Corrupted database

The SQLite database is at `~/.sol/data.db`. If it becomes corrupted:

```bash
rm ~/.sol/data.db
```

The CLI will recreate it on next run. You'll lose transaction history
and snapshots, but wallet key files are stored separately and are
not affected.

## General Tips

- Use `--verbose` on any command to see debug output
- Check `sol config list` to verify your settings
- Run `sol network` to verify RPC connectivity and see network status
