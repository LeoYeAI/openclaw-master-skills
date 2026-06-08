/**
 * Kevros OpenClaw Plugin — Gateway HTTP Client
 *
 * Lightweight client using native fetch (Node 18+). Zero external
 * dependencies. All governance logic, cryptography, and provenance
 * stay server-side; this client only shuttles JSON and checks status.
 */
// ---------------------------------------------------------------------------
// Error type
// ---------------------------------------------------------------------------
export class KevrosApiError extends Error {
    status;
    path;
    detail;
    constructor(status, path, detail) {
        super(`Kevros gateway ${status} on ${path}: ${detail}`);
        this.status = status;
        this.path = path;
        this.detail = detail;
        this.name = "KevrosApiError";
    }
}
// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------
export class KevrosClient {
    baseUrl;
    apiKey;
    agentId;
    /** Timeout for HTTP requests in milliseconds. */
    timeoutMs;
    constructor(opts) {
        this.baseUrl = opts.gatewayUrl;
        this.apiKey = opts.apiKey;
        this.agentId = opts.agentId;
        this.timeoutMs = opts.timeoutMs ?? 10_000;
    }
    // ── Core operations ───────────────────────────────────────────────
    /**
     * Verify an action before execution.
     * Returns ALLOW / CLAMP / DENY with a cryptographic release token.
     */
    async verify(req) {
        await this.ensureApiKey();
        return this.post("/governance/verify", {
            action_type: req.action_type,
            action_payload: req.action_payload,
            agent_id: req.agent_id ?? this.agentId,
            ...(req.policy_context ? { policy_context: req.policy_context } : {}),
        });
    }
    /**
     * Attest a completed action to build hash-chained provenance.
     */
    async attest(req) {
        await this.ensureApiKey();
        return this.post("/governance/attest", {
            agent_id: req.agent_id ?? this.agentId,
            action_description: req.action_description,
            action_payload: req.action_payload,
            ...(req.context ? { context: req.context } : {}),
        });
    }
    /**
     * Auto-signup for a free-tier API key (1,000 calls/month).
     * The key is stored internally for subsequent calls.
     */
    async signup(agentId) {
        const res = await this.post("/signup", {
            agent_id: agentId ?? this.agentId,
        }, /* auth */ false);
        this.apiKey = res.api_key;
        return res;
    }
    /**
     * Get an agent's trust passport (score, tier, badges).
     * Public endpoint, no auth required.
     */
    async passport(agentId) {
        const id = agentId ?? this.agentId;
        return this.get(`/passport/${encodeURIComponent(id)}`);
    }
    // ── Internal HTTP helpers ─────────────────────────────────────────
    get hasApiKey() {
        return typeof this.apiKey === "string" && this.apiKey.length > 0;
    }
    /**
     * Ensure we have an API key. If none is configured, auto-provision
     * via the free-tier signup endpoint.
     */
    async ensureApiKey() {
        if (this.hasApiKey)
            return;
        await this.signup();
    }
    async post(path, body, auth = true) {
        const headers = {
            "Content-Type": "application/json",
        };
        if (auth && this.apiKey) {
            headers["X-API-Key"] = this.apiKey;
        }
        const url = `${this.baseUrl}${path}`;
        const res = await this.fetchWithTimeout(url, {
            method: "POST",
            headers,
            body: JSON.stringify(body),
        });
        if (!res.ok) {
            const detail = await res.text().catch(() => "unknown error");
            throw new KevrosApiError(res.status, path, detail);
        }
        return (await res.json());
    }
    async get(path) {
        const url = `${this.baseUrl}${path}`;
        const res = await this.fetchWithTimeout(url, { method: "GET" });
        if (!res.ok) {
            const detail = await res.text().catch(() => "unknown error");
            throw new KevrosApiError(res.status, path, detail);
        }
        return (await res.json());
    }
    async fetchWithTimeout(url, init) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), this.timeoutMs);
        try {
            return await fetch(url, { ...init, signal: controller.signal });
        }
        finally {
            clearTimeout(timer);
        }
    }
}
//# sourceMappingURL=client.js.map