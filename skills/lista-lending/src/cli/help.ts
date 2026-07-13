import type { CliMeta } from "./meta.js";

export function renderHelp(meta: CliMeta): string {
  return `${meta.skillName} v${meta.skillVersion}

Usage: dist/cli/cli.bundle.mjs <command> [options]

Vault Commands:
  vaults           List available vaults
  deposit          Deposit assets into selected vault
  withdraw         Withdraw assets from selected vault

Market Commands:
  markets          List available markets (excludes SmartLending & Fixed)
  supply           Supply collateral to selected market
  borrow           Borrow loan tokens (use --simulate to check max)
  repay            Repay borrowed loan tokens (use --simulate to preview impact)
  market-withdraw  Withdraw collateral from selected market

Common Commands:
  holdings         Query user's positions (vault + market)
  select           Select a vault or market for operations
  config           Manage RPC URLs and settings
  version          Show version information

Discovery:
  node dist/cli/cli.bundle.mjs vaults [--chain eip155:56]
  node dist/cli/cli.bundle.mjs markets [--chain eip155:56]
  node dist/cli/cli.bundle.mjs holdings --address 0x...

Selection:
  node dist/cli/cli.bundle.mjs select --vault 0x... --wallet-topic <t> --wallet-address 0x...
  node dist/cli/cli.bundle.mjs select --market 0x... --wallet-topic <t> --wallet-address 0x...
  node dist/cli/cli.bundle.mjs select --show
  node dist/cli/cli.bundle.mjs select --clear

Vault Operations:
  node dist/cli/cli.bundle.mjs deposit --amount 100
  node dist/cli/cli.bundle.mjs withdraw --amount 50
  node dist/cli/cli.bundle.mjs withdraw --withdraw-all

Market Operations:
  node dist/cli/cli.bundle.mjs supply --amount 1
  node dist/cli/cli.bundle.mjs borrow --simulate
  node dist/cli/cli.bundle.mjs borrow --simulate --simulate-supply 1
  node dist/cli/cli.bundle.mjs borrow --amount 100
  node dist/cli/cli.bundle.mjs repay --simulate --amount 50
  node dist/cli/cli.bundle.mjs repay --simulate --repay-all
  node dist/cli/cli.bundle.mjs repay --amount 50
  node dist/cli/cli.bundle.mjs repay --repay-all
  node dist/cli/cli.bundle.mjs market-withdraw --amount 0.5
  node dist/cli/cli.bundle.mjs market-withdraw --withdraw-all

Options:
  --vault <address>          Vault contract address
  --market <address>         Market ID (contract address)
  --amount <number>          Amount in token units
  --chain <chain>            Chain ID (default: eip155:56)
  --page <number>            List page
  --page-size <number>       List page size
  --sort <field>             Sort field
  --order <asc|desc>         Sort direction
  --zone <zone>              Zone filter
  --keyword <text>           Search keyword
  --assets <a,b>             Asset filter (vaults)
  --curators <a,b>           Curator filter (vaults)
  --loans <a,b>              Loan token filter (markets)
  --collaterals <a,b>        Collateral token filter (markets)
  --withdraw-all             Withdraw entire vault position
  --repay-all                Repay entire loan
  --simulate                 Simulate borrow/repay impact without executing
  --simulate-supply <amt>    Show max borrowable after hypothetical supply
  --wallet-topic <topic>     WalletConnect session topic
  --wallet-address <addr>    Connected wallet address
  --address <addr>           User address for holdings query
  --scope <type>             Holdings scope: all|vault|market|selected
  --show                     Show current selection/config
  --clear                    Clear selection
  --debug-log-file <path>    Append structured stdout/stderr logs to a file (jsonl)

Workflow Examples:
  Vault:
    1. holdings --address 0xUSER
    2. select --vault 0xVAULT --wallet-topic ... --wallet-address ...
    3. deposit --amount 100
    4. withdraw --amount 50

  Market:
    1. markets --chain eip155:56
    2. select --market 0xMARKET --wallet-topic ... --wallet-address ...
    3. supply --amount 1
    4. borrow --simulate
    5. borrow --amount 500
    6. repay --amount 250
    7. market-withdraw --amount 0.5

Supported Chains:
  eip155:56   BSC (default)
  eip155:1    Ethereum`;
}
