#!/usr/bin/env tsx

import { parseCliInput } from "./cli/args.js";
import { setupDebugLogFile } from "./cli/debug-log.js";
import { renderHelp } from "./cli/help.js";
import { loadCliMeta } from "./cli/meta.js";
import { runCommand } from "./cli/run.js";
import { printErrorJson } from "./commands/shared/output.js";

const parsed = parseCliInput();
setupDebugLogFile("@lista-dao/lista-lending-skill", parsed.debugLogFile);
const meta = loadCliMeta();

export const SKILL_VERSION = meta.skillVersion;
export const SKILL_NAME = meta.skillName;
export const WALLET_CONNECT_VERSION = meta.walletConnectVersion;

if (!parsed.command || parsed.help) {
  console.log(renderHelp(meta));
  process.exit(0);
}

runCommand(
  parsed.command,
  {
    args: parsed.args,
    configArgs: parsed.configArgs,
    vaultsArgs: parsed.vaultsArgs,
    marketsArgs: parsed.marketsArgs,
    holdingsArgs: parsed.holdingsArgs,
    selectArgs: parsed.selectArgs,
  },
  meta
).catch((err: Error) => {
  printErrorJson({ error: err.message });
  process.exit(1);
});
