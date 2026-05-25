/**
 * Kevros OpenClaw Plugin — Configuration
 *
 * Defines the plugin configuration schema with sensible defaults.
 * All settings can be overridden via openclaw.plugin.json configSchema
 * or programmatic registration.
 */

import { hostname } from "node:os";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type EnforcementMode = "enforce" | "advisory" | "deny";

export interface KevrosPluginConfig {
  /** Kevros gateway base URL. */
  gatewayUrl: string;

  /** API key for authenticated governance calls. Auto-provisions if absent. */
  apiKey?: string;

  /** Agent identifier for governance tracking. */
  agentId: string;

  /** Tools that require governance verification before execution. */
  highRiskTools: string[];

  /**
   * Enforcement mode:
   *  - "enforce"  — fail-closed: block if gateway unreachable or DENY
   *  - "advisory" — log-only: warn but never block
   *  - "deny"     — hard block all high-risk tool calls unconditionally
   */
  mode: EnforcementMode;

  /** Automatically attest after every tool call to build provenance history. */
  autoAttest: boolean;
}

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

const DEFAULT_GATEWAY_URL = "https://governance.taskhawktech.com";

const DEFAULT_HIGH_RISK_TOOLS: string[] = [
  "bash",
  "computer",
  "terminal",
  "exec",
  "write_file",
  "edit_file",
];

// ---------------------------------------------------------------------------
// Resolver
// ---------------------------------------------------------------------------

/**
 * Resolve partial user-supplied config into a complete KevrosPluginConfig,
 * filling in defaults for any omitted fields.
 */
export function resolveConfig(
  raw: Partial<KevrosPluginConfig> | undefined,
): KevrosPluginConfig {
  const partial = raw ?? {};
  return {
    gatewayUrl: stripTrailingSlash(partial.gatewayUrl ?? DEFAULT_GATEWAY_URL),
    apiKey: partial.apiKey,
    agentId: partial.agentId ?? safeHostname(),
    highRiskTools: partial.highRiskTools ?? [...DEFAULT_HIGH_RISK_TOOLS],
    mode: partial.mode ?? "enforce",
    autoAttest: partial.autoAttest ?? true,
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function stripTrailingSlash(url: string): string {
  return url.endsWith("/") ? url.slice(0, -1) : url;
}

function safeHostname(): string {
  try {
    return hostname();
  } catch {
    return "unknown-agent";
  }
}
