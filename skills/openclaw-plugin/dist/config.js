/**
 * Kevros OpenClaw Plugin — Configuration
 *
 * Defines the plugin configuration schema with sensible defaults.
 * All settings can be overridden via openclaw.plugin.json configSchema
 * or programmatic registration.
 */
import { hostname } from "node:os";
// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------
const DEFAULT_GATEWAY_URL = "https://governance.taskhawktech.com";
const DEFAULT_HIGH_RISK_TOOLS = [
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
export function resolveConfig(raw) {
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
function stripTrailingSlash(url) {
    return url.endsWith("/") ? url.slice(0, -1) : url;
}
function safeHostname() {
    try {
        return hostname();
    }
    catch {
        return "unknown-agent";
    }
}
//# sourceMappingURL=config.js.map