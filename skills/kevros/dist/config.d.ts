/**
 * Kevros OpenClaw Plugin — Configuration
 *
 * Defines the plugin configuration schema with sensible defaults.
 * All settings can be overridden via openclaw.plugin.json configSchema
 * or programmatic registration.
 */
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
/**
 * Resolve partial user-supplied config into a complete KevrosPluginConfig,
 * filling in defaults for any omitted fields.
 */
export declare function resolveConfig(raw: Partial<KevrosPluginConfig> | undefined): KevrosPluginConfig;
//# sourceMappingURL=config.d.ts.map