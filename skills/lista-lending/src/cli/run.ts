import { cmdDeposit } from "../commands/deposit.js";
import { cmdWithdraw } from "../commands/withdraw.js";
import { cmdConfig, type ConfigArgs } from "../commands/config.js";
import { cmdVaults, type VaultsArgs } from "../commands/vaults.js";
import { cmdMarkets, type MarketsArgs } from "../commands/markets.js";
import { cmdHoldings, type HoldingsArgs } from "../commands/holdings.js";
import { cmdSelect, type SelectArgs } from "../commands/select.js";
import { cmdSupply } from "../commands/supply.js";
import { cmdBorrow } from "../commands/borrow.js";
import { cmdRepay } from "../commands/repay.js";
import { cmdMarketWithdraw } from "../commands/market-withdraw.js";
import type { ParsedArgs } from "../types.js";
import type { CliMeta } from "./meta.js";

export interface RoutedArgs {
  args: ParsedArgs;
  configArgs: ConfigArgs;
  vaultsArgs: VaultsArgs;
  marketsArgs: MarketsArgs;
  holdingsArgs: HoldingsArgs;
  selectArgs: SelectArgs;
}

export async function runCommand(
  command: string,
  routedArgs: RoutedArgs,
  meta: CliMeta
): Promise<void> {
  const { args, configArgs, vaultsArgs, marketsArgs, holdingsArgs, selectArgs } = routedArgs;
  switch (command) {
    case "config":
      await cmdConfig(configArgs);
      return;
    case "holdings":
      await cmdHoldings(holdingsArgs);
      return;
    case "select":
      await cmdSelect(selectArgs);
      return;
    case "version":
      console.log(
        JSON.stringify({
          skill: meta.skillName,
          version: meta.skillVersion,
          dependencies: {
            "lista-wallet-connect": meta.walletConnectVersion,
          },
          hint: "If version mismatch, run: npm install && npm run build",
        })
      );
      return;
    case "vaults":
      await cmdVaults(vaultsArgs);
      return;
    case "deposit":
      await cmdDeposit(args);
      return;
    case "withdraw":
      await cmdWithdraw(args);
      return;
    case "markets":
      await cmdMarkets(marketsArgs);
      return;
    case "supply":
      await cmdSupply(args);
      return;
    case "borrow":
      await cmdBorrow(args);
      return;
    case "repay":
      await cmdRepay(args);
      return;
    case "market-withdraw":
      await cmdMarketWithdraw(args);
      return;
    default:
      console.error(`Unknown command: ${command}`);
      console.error("Run with --help for usage information");
      process.exit(1);
  }
}
