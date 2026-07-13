import type { ParsedArgs } from "../types.js";
import type { ConfigArgs } from "../commands/config.js";
import type { HoldingsArgs } from "../commands/holdings.js";
import type { MarketsArgs } from "../commands/markets.js";
import type { SelectArgs } from "../commands/select.js";
import type { VaultsArgs } from "../commands/vaults.js";
export interface ParsedCliInput {
    command: string | undefined;
    help: boolean;
    debugLogFile?: string;
    args: ParsedArgs;
    configArgs: ConfigArgs;
    vaultsArgs: VaultsArgs;
    marketsArgs: MarketsArgs;
    holdingsArgs: HoldingsArgs;
    selectArgs: SelectArgs;
}
export declare function parseCliInput(): ParsedCliInput;
