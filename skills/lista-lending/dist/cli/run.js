import { cmdDeposit } from "../commands/deposit.js";
import { cmdWithdraw } from "../commands/withdraw.js";
import { cmdConfig } from "../commands/config.js";
import { cmdVaults } from "../commands/vaults.js";
import { cmdMarkets } from "../commands/markets.js";
import { cmdHoldings } from "../commands/holdings.js";
import { cmdSelect } from "../commands/select.js";
import { cmdSupply } from "../commands/supply.js";
import { cmdBorrow } from "../commands/borrow.js";
import { cmdRepay } from "../commands/repay.js";
import { cmdMarketWithdraw } from "../commands/market-withdraw.js";
export async function runCommand(command, routedArgs, meta) {
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
            console.log(JSON.stringify({
                skill: meta.skillName,
                version: meta.skillVersion,
                dependencies: {
                    "lista-wallet-connect": meta.walletConnectVersion,
                },
                hint: "If version mismatch, run: npm install && npm run build",
            }));
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
