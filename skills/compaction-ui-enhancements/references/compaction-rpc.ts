/**
 * Compaction settings RPC handlers.
 *
 * Manages per-agent compaction configuration:
 *   - Auto-compact toggle + threshold percentage
 *   - Store last compaction result for review
 *   - Retrieve settings & last result
 *
 * Config stored at: {agentDir}/compaction-config.json
 */

import fs from "node:fs/promises";
import path from "node:path";
import { resolveOpenClawAgentDir } from "../../agents/agent-paths.js";
import type { GatewayRequestHandler } from "./types.js";

// ─── Types ───────────────────────────────────────────────────────────────────

export interface CompactionSettings {
  /** Enable automatic compaction when token usage exceeds threshold */
  autoEnabled: boolean;
  /** Token usage percentage (0-100) at which auto-compaction triggers */
  autoThresholdPercent: number;
  /** Store the last compaction result for review */
  storeLastResult: boolean;
  /** Custom model for compaction in "provider/model" format, empty or undefined = use session default */
  compactionModel?: string;
}

export interface CompactionLastResult {
  timestamp: number;
  trigger: "manual" | "auto" | "overflow";
  tokensBefore: number;
  tokensAfter: number;
  tokensSaved: number;
  percentReduction: number;
  sessionKey?: string;
  /** Compacted summary text (only stored when storeLastResult is enabled) */
  summary?: string;
}

interface CompactionConfigFile {
  settings: CompactionSettings;
  lastResult?: CompactionLastResult;
}

// ─── Defaults ────────────────────────────────────────────────────────────────

const DEFAULT_SETTINGS: CompactionSettings = {
  autoEnabled: true,
  autoThresholdPercent: 60,
  storeLastResult: false,
};

// ─── File I/O ────────────────────────────────────────────────────────────────

function getConfigPath(agentDir?: string): string {
  const dir = agentDir ?? resolveOpenClawAgentDir();
  return path.join(dir, "compaction-config.json");
}

export async function loadCompactionConfig(agentDir?: string): Promise<CompactionConfigFile> {
  const configPath = getConfigPath(agentDir);
  try {
    const raw = await fs.readFile(configPath, "utf-8");
    const parsed = JSON.parse(raw) as Partial<CompactionConfigFile>;
    return {
      settings: { ...DEFAULT_SETTINGS, ...parsed.settings },
      lastResult: parsed.lastResult,
    };
  } catch {
    return { settings: { ...DEFAULT_SETTINGS } };
  }
}

async function saveCompactionConfig(config: CompactionConfigFile, agentDir?: string): Promise<void> {
  const configPath = getConfigPath(agentDir);
  await fs.mkdir(path.dirname(configPath), { recursive: true });
  await fs.writeFile(configPath, JSON.stringify(config, null, 2), "utf-8");
}

/**
 * Called by the compaction engine to record a result.
 * Exported for use by the sessions.compact RPC and auto-compaction trigger.
 */
export async function recordCompactionResult(
  result: CompactionLastResult,
  agentDir?: string,
): Promise<void> {
  const config = await loadCompactionConfig(agentDir);
  if (config.settings.storeLastResult) {
    config.lastResult = result;
  } else {
    // Still store metadata, just not the summary
    config.lastResult = { ...result, summary: undefined };
  }
  await saveCompactionConfig(config, agentDir);
}

// ─── RPC Handlers ────────────────────────────────────────────────────────────

const compactionGetSettings: GatewayRequestHandler = async ({ respond }) => {
  const config = await loadCompactionConfig();
  respond(true, { ok: true, settings: config.settings }, undefined);
};

const compactionSaveSettings: GatewayRequestHandler = async ({ params, respond }) => {
  const p = params as Partial<CompactionSettings> | undefined;
  const config = await loadCompactionConfig();

  if (p?.autoEnabled !== undefined) config.settings.autoEnabled = !!p.autoEnabled;
  if (typeof p?.autoThresholdPercent === "number") {
    config.settings.autoThresholdPercent = Math.max(10, Math.min(95, p.autoThresholdPercent));
  }
  if (p?.storeLastResult !== undefined) config.settings.storeLastResult = !!p.storeLastResult;
  if (p && "compactionModel" in p) {
    config.settings.compactionModel = typeof p.compactionModel === "string" && p.compactionModel.includes("/")
      ? p.compactionModel : undefined;
  }

  await saveCompactionConfig(config);
  respond(true, { ok: true, settings: config.settings }, undefined);
};

const compactionGetLastResult: GatewayRequestHandler = async ({ respond }) => {
  const config = await loadCompactionConfig();
  respond(
    true,
    { ok: true, lastResult: config.lastResult ?? null },
    undefined,
  );
};

const compactionClearLastResult: GatewayRequestHandler = async ({ respond }) => {
  const config = await loadCompactionConfig();
  config.lastResult = undefined;
  await saveCompactionConfig(config);
  respond(true, { ok: true }, undefined);
};

// ─── Exports ─────────────────────────────────────────────────────────────────

export const compactionMethods: Record<string, GatewayRequestHandler> = {
  "compaction.getSettings": compactionGetSettings,
  "compaction.saveSettings": compactionSaveSettings,
  "compaction.getLastResult": compactionGetLastResult,
  "compaction.clearLastResult": compactionClearLastResult,
};
