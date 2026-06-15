/**
 * Lightweight LLM Caller
 *
 * Makes API calls to Anthropic for plan generation and reflection.
 * Uses fetch directly to avoid heavy SDK dependencies.
 */
import fs from "node:fs";
import path from "node:path";
// ============================================================================
// API Key Resolution
// ============================================================================
function resolveApiKey(config) {
    // 1. Explicit config (from enhanced-loop-hook, which resolves via auth profile chain)
    if (config?.apiKey)
        return config.apiKey;
    // 2. Environment variable
    if (process.env.ANTHROPIC_API_KEY)
        return process.env.ANTHROPIC_API_KEY;
    // 3. Try to read from OpenClaw auth storage (with OAuth/token priority)
    const home = process.env.HOME || process.env.USERPROFILE || "";
    const authPaths = [
        path.join(home, ".openclaw", "agents", "main", "agent", "auth-profiles.json"),
        path.join(home, ".openclaw", "auth-profiles.json"),
        path.join(home, ".config", "openclaw", "auth-profiles.json"),
    ];
    for (const authPath of authPaths) {
        try {
            if (fs.existsSync(authPath)) {
                const content = fs.readFileSync(authPath, "utf-8");
                const auth = JSON.parse(content);
                const profiles = auth.profiles || {};
                const order = auth.order?.anthropic;
                // Follow configured order if available
                if (order?.length) {
                    for (const profileId of order) {
                        const p = profiles[profileId];
                        if (!p || p.provider !== "anthropic") continue;
                        const key = p.token || p.key || p.apiKey;
                        if (key) return key;
                    }
                }
                // Fallback: prefer token/oauth profiles over api_key
                const sorted = Object.entries(profiles)
                    .filter(([, p]) => p.provider === "anthropic")
                    .sort(([, a], [, b]) => {
                    const rank = (t) => (t === "token" || t === "oauth" ? 0 : 1);
                    return rank(a.type ?? "api_key") - rank(b.type ?? "api_key");
                });
                for (const [, profile] of sorted) {
                    const key = profile.token || profile.key || profile.apiKey;
                    if (key) return key;
                }
            }
        }
        catch {
            // Continue to next path
        }
    }
    return null;
}
function isOAuthToken(key) {
    return key.startsWith("sk-ant-oat") || key.startsWith("Bearer ");
}
// ============================================================================
// LLM Caller
// ============================================================================
const DEFAULT_MODEL = "claude-haiku-4-5";
const DEFAULT_MAX_TOKENS = 1024;
const ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages";
export class LLMCaller {
    apiKey;
    model;
    maxTokens;
    baseUrl;
    constructor(config) {
        this.apiKey = resolveApiKey(config);
        this.model = config?.model || DEFAULT_MODEL;
        this.maxTokens = config?.maxTokens || DEFAULT_MAX_TOKENS;
        this.baseUrl = config?.baseUrl || ANTHROPIC_API_URL;
    }
    /**
     * Check if the caller is configured with an API key
     */
    isConfigured() {
        return !!this.apiKey;
    }
    /**
     * Make an LLM call
     */
    async call(options) {
        if (!this.apiKey) {
            throw new Error("No API key configured for LLM caller");
        }
        // Separate system message from other messages
        const systemMessage = options.messages.find(m => m.role === "system");
        const otherMessages = options.messages.filter(m => m.role !== "system");
        const body = {
            model: options.model || this.model,
            max_tokens: options.maxTokens || this.maxTokens,
            temperature: options.temperature ?? 0.7,
            system: systemMessage?.content,
            messages: otherMessages.map(m => ({
                role: m.role,
                content: m.content,
            })),
        };
        const response = await fetch(this.baseUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                // Use Authorization header for OAuth/setup tokens, x-api-key for standard API keys
                ...(isOAuthToken(this.apiKey)
                    ? { "Authorization": `Bearer ${this.apiKey.replace(/^Bearer\s*/i, "")}`, "anthropic-beta": "oauth-2025-04-20" }
                    : { "x-api-key": this.apiKey }),
                "anthropic-version": "2023-06-01",
            },
            body: JSON.stringify(body),
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`LLM API error (${response.status}): ${errorText}`);
        }
        const data = await response.json();
        const textContent = data.content
            .filter(c => c.type === "text")
            .map(c => c.text || "")
            .join("");
        return {
            content: textContent,
            usage: data.usage ? {
                inputTokens: data.usage.input_tokens,
                outputTokens: data.usage.output_tokens,
            } : undefined,
        };
    }
    /**
     * Convenience method matching the LLMCaller type expected by orchestrator
     */
    async invoke(options) {
        const messages = options.messages.map(m => ({
            role: m.role,
            content: typeof m.content === "string" ? m.content : JSON.stringify(m.content),
        }));
        return this.call({ messages, maxTokens: options.maxTokens });
    }
}
// ============================================================================
// Factory
// ============================================================================
let defaultCaller = null;
export function getLLMCaller(config) {
    if (!defaultCaller) {
        defaultCaller = new LLMCaller(config);
    }
    return defaultCaller;
}
export function createLLMCaller(config) {
    return new LLMCaller(config);
}
export function resetLLMCaller() {
    defaultCaller = null;
}
// ============================================================================
// Wrapper for orchestrator compatibility
// ============================================================================
export function createOrchestratorLLMCaller(config) {
    const caller = createLLMCaller(config);
    if (!caller.isConfigured()) {
        // Return a no-op caller that throws helpful error
        return async () => {
            throw new Error("LLM caller not configured. Set ANTHROPIC_API_KEY environment variable " +
                "or configure an Anthropic auth profile in OpenClaw.");
        };
    }
    return (options) => caller.invoke(options);
}
//# sourceMappingURL=caller.js.map