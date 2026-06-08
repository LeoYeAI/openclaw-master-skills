/**
 * Kevros OpenClaw Plugin — Gateway HTTP Client
 *
 * Lightweight client using native fetch (Node 18+). Zero external
 * dependencies. All governance logic, cryptography, and provenance
 * stay server-side; this client only shuttles JSON and checks status.
 */
export interface VerifyResponse {
    decision: "ALLOW" | "CLAMP" | "DENY";
    verification_id: string;
    release_token: string | null;
    token_preimage: string | null;
    applied_action: Record<string, unknown> | null;
    policy_applied: Record<string, unknown> | null;
    reason: string;
    epoch: number;
    provenance_hash: string;
}
export interface AttestResponse {
    attestation_id: string;
    epoch: number;
    hash_prev: string;
    hash_curr: string;
    pqc_block_ref: string | null;
    timestamp_utc: string;
    chain_length: number;
}
export interface SignupResponse {
    api_key: string;
    tier: string;
    monthly_limit: number;
    rate_limit_per_minute: number;
    upgrade_url: string;
    usage: Record<string, string>;
}
export interface PassportResponse {
    agent_id: string;
    trust_score: number;
    tier: string;
    total_verifications: number;
    total_attestations: number;
    chain_intact: boolean;
    active_days: number;
    badges: string[];
    claimed_by: string | null;
}
export declare class KevrosApiError extends Error {
    readonly status: number;
    readonly path: string;
    readonly detail: string;
    constructor(status: number, path: string, detail: string);
}
export declare class KevrosClient {
    private baseUrl;
    private apiKey;
    private readonly agentId;
    /** Timeout for HTTP requests in milliseconds. */
    private readonly timeoutMs;
    constructor(opts: {
        gatewayUrl: string;
        apiKey?: string;
        agentId: string;
        timeoutMs?: number;
    });
    /**
     * Verify an action before execution.
     * Returns ALLOW / CLAMP / DENY with a cryptographic release token.
     */
    verify(req: {
        action_type: string;
        action_payload: Record<string, unknown>;
        agent_id?: string;
        policy_context?: Record<string, unknown>;
    }): Promise<VerifyResponse>;
    /**
     * Attest a completed action to build hash-chained provenance.
     */
    attest(req: {
        agent_id?: string;
        action_description: string;
        action_payload: Record<string, unknown>;
        context?: Record<string, unknown>;
    }): Promise<AttestResponse>;
    /**
     * Auto-signup for a free-tier API key (1,000 calls/month).
     * The key is stored internally for subsequent calls.
     */
    signup(agentId?: string): Promise<SignupResponse>;
    /**
     * Get an agent's trust passport (score, tier, badges).
     * Public endpoint, no auth required.
     */
    passport(agentId?: string): Promise<PassportResponse>;
    get hasApiKey(): boolean;
    /**
     * Ensure we have an API key. If none is configured, auto-provision
     * via the free-tier signup endpoint.
     */
    private ensureApiKey;
    private post;
    private get;
    private fetchWithTimeout;
}
//# sourceMappingURL=client.d.ts.map