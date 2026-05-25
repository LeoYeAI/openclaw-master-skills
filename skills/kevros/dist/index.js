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
import { KevrosClient, KevrosApiError } from "./client.js";
import { resolveConfig, } from "./config.js";
// ---------------------------------------------------------------------------
// Logging helper
// ---------------------------------------------------------------------------
const LOG_PREFIX = "[kevros]";
function logInfo(msg, ...args) {
    console.log(`${LOG_PREFIX} ${msg}`, ...args);
}
function logWarn(msg, ...args) {
    console.warn(`${LOG_PREFIX} ${msg}`, ...args);
}
function logError(msg, ...args) {
    console.error(`${LOG_PREFIX} ${msg}`, ...args);
}
// ---------------------------------------------------------------------------
// String truncation for attestation payloads
// ---------------------------------------------------------------------------
function truncate(value, maxLen) {
    if (value === null || value === undefined)
        return "";
    const s = typeof value === "string" ? value : JSON.stringify(value);
    if (s.length <= maxLen)
        return s;
    return s.slice(0, maxLen - 3) + "...";
}
// ---------------------------------------------------------------------------
// Plugin entry point
// ---------------------------------------------------------------------------
export function register(api) {
    const config = resolveConfig(api.getConfig());
    const client = new KevrosClient({
        gatewayUrl: config.gatewayUrl,
        apiKey: config.apiKey,
        agentId: config.agentId,
    });
    logInfo("initializing (mode=%s, agent=%s, high-risk=%s, autoAttest=%s)", config.mode, config.agentId, config.highRiskTools.join(","), config.autoAttest);
    // ── before_tool_call hook ───────────────────────────────────────
    api.registerHook(["before_tool_call"], async (event) => {
        const toolEvent = event;
        const toolName = toolEvent.tool.name;
        // Skip tools that are not on the high-risk list
        if (!config.highRiskTools.includes(toolName)) {
            return { allow: true };
        }
        // Deny mode: hard-block all high-risk tools unconditionally
        if (config.mode === "deny") {
            logWarn("DENY mode: blocking tool=%s", toolName);
            return {
                block: true,
                blockReason: `Kevros: DENY mode active -- all high-risk tools blocked`,
            };
        }
        try {
            const result = await client.verify({
                action_type: `tool:${toolName}`,
                action_payload: {
                    tool: toolName,
                    input: toolEvent.tool.input,
                },
                agent_id: config.agentId,
            });
            // DENY decision from gateway
            if (result.decision === "DENY") {
                if (config.mode === "advisory") {
                    logWarn("ADVISORY: gateway returned DENY for tool=%s reason=%s (allowing anyway)", toolName, result.reason);
                    return { allow: true };
                }
                logWarn("DENY: tool=%s reason=%s", toolName, result.reason);
                return {
                    block: true,
                    blockReason: `Kevros: DENY -- ${result.reason}`,
                };
            }
            // CLAMP decision: constrained but allowed
            if (result.decision === "CLAMP") {
                logInfo("CLAMP: tool=%s reason=%s (proceeding with constraints)", toolName, result.reason);
            }
            // Store release token and epoch for post-execution attestation
            toolEvent.metadata.kevrosToken = result.release_token;
            toolEvent.metadata.kevrosEpoch = result.epoch;
            toolEvent.metadata.kevrosVerificationId = result.verification_id;
            return { allow: true };
        }
        catch (err) {
            return handleGatewayError(err, config.mode, toolName);
        }
    });
    // ── after_tool_call hook ────────────────────────────────────────
    api.registerHook(["after_tool_call"], async (event) => {
        const toolEvent = event;
        if (!config.autoAttest)
            return;
        // Only attest high-risk tools (or all if metadata has a token)
        const isHighRisk = config.highRiskTools.includes(toolEvent.tool.name);
        if (!isHighRisk && !toolEvent.metadata.kevrosToken)
            return;
        try {
            await client.attest({
                agent_id: config.agentId,
                action_description: `Executed tool: ${toolEvent.tool.name}`,
                action_payload: {
                    tool: toolEvent.tool.name,
                    input: toolEvent.tool.input,
                    output_summary: truncate(toolEvent.result, 500),
                    release_token: toolEvent.metadata.kevrosToken ?? null,
                    epoch: toolEvent.metadata.kevrosEpoch ?? null,
                    verification_id: toolEvent.metadata.kevrosVerificationId ?? null,
                },
            });
        }
        catch (err) {
            // Attestation failure is never fatal; log and continue
            const detail = err instanceof KevrosApiError
                ? `${err.status} ${err.detail}`
                : String(err);
            logWarn("attestation failed for tool=%s: %s", toolEvent.tool.name, detail);
        }
    });
    // ── kevros_verify tool ──────────────────────────────────────────
    api.registerTool("kevros_verify", {
        description: "Verify an action against Kevros governance policy. Returns ALLOW, CLAMP, or DENY " +
            "with a cryptographic release token proving the decision.",
        parameters: {
            type: "object",
            properties: {
                action_type: {
                    type: "string",
                    description: "Type of action to verify (e.g. 'tool:bash', 'api_call', 'transaction').",
                },
                action_payload: {
                    type: "object",
                    description: "The action details to verify against policy.",
                },
            },
            required: ["action_type", "action_payload"],
        },
        handler: async (params) => {
            try {
                const result = await client.verify({
                    action_type: params.action_type,
                    action_payload: (params.action_payload ?? {}),
                    agent_id: config.agentId,
                });
                return {
                    decision: result.decision,
                    verification_id: result.verification_id,
                    reason: result.reason,
                    epoch: result.epoch,
                    applied_action: result.applied_action,
                    policy_applied: result.policy_applied,
                    release_token: result.release_token,
                };
            }
            catch (err) {
                const detail = err instanceof KevrosApiError
                    ? `${err.status}: ${err.detail}`
                    : String(err);
                return { error: true, detail };
            }
        },
    });
    // ── kevros_passport tool ────────────────────────────────────────
    api.registerTool("kevros_passport", {
        description: "Look up an agent's trust passport -- score, tier, badges, and governance stats. " +
            "The credit score for AI agents.",
        parameters: {
            type: "object",
            properties: {
                agent_id: {
                    type: "string",
                    description: "Agent identifier to look up. Defaults to the current agent if omitted.",
                },
            },
            required: [],
        },
        handler: async (params) => {
            try {
                const agentId = params.agent_id || config.agentId;
                const passport = await client.passport(agentId);
                return {
                    agent_id: passport.agent_id,
                    trust_score: passport.trust_score,
                    tier: passport.tier,
                    total_verifications: passport.total_verifications,
                    total_attestations: passport.total_attestations,
                    chain_intact: passport.chain_intact,
                    active_days: passport.active_days,
                    badges: passport.badges,
                };
            }
            catch (err) {
                if (err instanceof KevrosApiError && err.status === 404) {
                    return {
                        error: false,
                        message: "No passport found. Make governance calls to build a trust profile.",
                    };
                }
                const detail = err instanceof KevrosApiError
                    ? `${err.status}: ${err.detail}`
                    : String(err);
                return { error: true, detail };
            }
        },
    });
    logInfo("registered hooks and tools");
}
// ---------------------------------------------------------------------------
// Gateway error handling
// ---------------------------------------------------------------------------
/**
 * Handle gateway communication errors per enforcement mode.
 *
 * enforce  -> fail-closed: BLOCK the tool call
 * advisory -> fail-open: ALLOW with warning
 * deny     -> already handled above (never reaches here)
 */
function handleGatewayError(err, mode, toolName) {
    const isAbort = err instanceof Error && err.name === "AbortError";
    const detail = isAbort
        ? "gateway request timed out"
        : err instanceof KevrosApiError
            ? `${err.status} ${err.detail}`
            : String(err);
    if (mode === "advisory") {
        logWarn("ADVISORY: gateway unreachable for tool=%s (%s), allowing", toolName, detail);
        return { allow: true };
    }
    // enforce mode: fail-closed
    logError("ENFORCE: gateway unreachable for tool=%s (%s), BLOCKING", toolName, detail);
    return {
        block: true,
        blockReason: `Kevros: gateway unreachable -- ${detail}`,
    };
}
// ---------------------------------------------------------------------------
// Re-exports
// ---------------------------------------------------------------------------
export { KevrosClient, KevrosApiError } from "./client.js";
export { resolveConfig } from "./config.js";
//# sourceMappingURL=index.js.map