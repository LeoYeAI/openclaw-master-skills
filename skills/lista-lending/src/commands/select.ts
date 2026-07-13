import { clearContext } from "../context.js";
import { printJson, exitWithCode } from "./shared/output.js";
import { runSelectMarket } from "./select/market.js";
import { buildSelectClearedPayload, buildSelectShowPayload } from "./select/show.js";
import type { SelectArgs } from "./select/types.js";
import { runSelectVault } from "./select/vault.js";

export type { SelectArgs };

export async function cmdSelect(args: SelectArgs): Promise<void> {
  if (args.clear) {
    clearContext();
    printJson(buildSelectClearedPayload());
    exitWithCode(0);
  }

  if (args.show) {
    printJson(buildSelectShowPayload());
    exitWithCode(0);
  }

  if (!args.vault && !args.market) {
    printJson({
      status: "error",
      reason: "--vault or --market required (or use --show to see current selection)",
    });
    exitWithCode(1);
  }

  if (args.vault && args.market) {
    printJson({
      status: "error",
      reason: "Cannot select both --vault and --market at the same time",
    });
    exitWithCode(1);
  }

  const result = args.market
    ? await runSelectMarket(args)
    : await runSelectVault(args);
  printJson(result.payload);
  exitWithCode(result.exitCode);
}
