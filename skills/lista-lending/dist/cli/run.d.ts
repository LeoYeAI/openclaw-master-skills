import { type ConfigArgs } from "../commands/config.js";
import { type VaultsArgs } from "../commands/vaults.js";
import { type MarketsArgs } from "../commands/markets.js";
import { type HoldingsArgs } from "../commands/holdings.js";
import { type SelectArgs } from "../commands/select.js";
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
export declare function runCommand(command: string, routedArgs: RoutedArgs, meta: CliMeta): Promise<void>;
