/**
 * @kevros/openclaw-plugin — Governance for Agent Tool Calls
 *
 * Gates high-risk tool calls through the Kevros governance gateway.
 * Every action verified before execution, every result attested after.
 * Hash-chained provenance builds a trust score for the agent.
 *
 * Hooks:
 *   before_tool_call — POST /governance/verify (ALLOW / CLAMP / DENY)
 *   after_tool_call  — POST /governance/attest (hash-chained record)
 *
 * Tools:
 *   kevros_verify   — Expose verify as a callable tool
 *   kevros_passport — Expose trust passport lookup as a callable tool
 */
import { type KevrosPluginConfig } from "./config.js";
/** Minimal OpenClaw hook event for before_tool_call. */
interface BeforeToolCallEvent {
    tool: {
        name: string;
        input: Record<string, unknown>;
    };
    metadata: Record<string, unknown>;
}
/** Minimal OpenClaw hook event for after_tool_call. */
interface AfterToolCallEvent {
    tool: {
        name: string;
        input: Record<string, unknown>;
    };
    result: unknown;
    metadata: Record<string, unknown>;
}
/** Return value for before_tool_call hook. */
interface BeforeToolCallResult {
    allow?: boolean;
    block?: boolean;
    blockReason?: string;
}
/** OpenClaw plugin registration API. */
interface OpenClawPluginApi {
    registerHook(events: string[], handler: (event: BeforeToolCallEvent | AfterToolCallEvent) => Promise<BeforeToolCallResult | void>): void;
    registerTool(name: string, definition: {
        description: string;
        parameters: Record<string, unknown>;
        handler: (params: Record<string, unknown>) => Promise<unknown>;
    }): void;
    getConfig(): Partial<KevrosPluginConfig> | undefined;
}
export declare function register(api: OpenClawPluginApi): void;
export { KevrosClient, KevrosApiError } from "./client.js";
export { resolveConfig } from "./config.js";
export type { KevrosPluginConfig, EnforcementMode } from "./config.js";
export type { VerifyResponse, AttestResponse, SignupResponse, PassportResponse, } from "./client.js";
//# sourceMappingURL=index.d.ts.map