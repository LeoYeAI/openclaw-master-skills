/**
 * Kevros OpenClaw Plugin — Gateway HTTP Client
 *
 * Lightweight client using native fetch (Node 18+). Zero external
 * dependencies. All governance logic, cryptography, and provenance
 * stay server-side; this client only shuttles JSON and checks status.
 */

// ---------------------------------------------------------------------------
// Response types (match gateway API contracts)
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Error type
// ---------------------------------------------------------------------------

export class KevrosApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly path: string,
    public readonly detail: string,
  ) {
    super(`Kevros gateway ${status} on ${path}: ${detail}`);
    this.name = "KevrosApiError";
  }
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export class KevrosClient {
  private baseUrl: string;
  private apiKey: string | undefined;
  private readonly agentId: string;

  /** Timeout for HTTP requests in milliseconds. */
  private readonly timeoutMs: number;

  constructor(opts: {
    gatewayUrl: string;
    apiKey?: string;
    agentId: string;
    timeoutMs?: number;
  }) {
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
  async verify(req: {
    action_type: string;
    action_payload: Record<string, unknown>;
    agent_id?: string;
    policy_context?: Record<string, unknown>;
  }): Promise<VerifyResponse> {
    await this.ensureApiKey();
    return this.post<VerifyResponse>("/governance/verify", {
      action_type: req.action_type,
      action_payload: req.action_payload,
      agent_id: req.agent_id ?? this.agentId,
      ...(req.policy_context ? { policy_context: req.policy_context } : {}),
    });
  }

  /**
   * Attest a completed action to build hash-chained provenance.
   */
  async attest(req: {
    agent_id?: string;
    action_description: string;
    action_payload: Record<string, unknown>;
    context?: Record<string, unknown>;
  }): Promise<AttestResponse> {
    await this.ensureApiKey();
    return this.post<AttestResponse>("/governance/attest", {
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
  async signup(agentId?: string): Promise<SignupResponse> {
    const res = await this.post<SignupResponse>("/signup", {
      agent_id: agentId ?? this.agentId,
    }, /* auth */ false);
    this.apiKey = res.api_key;
    return res;
  }

  /**
   * Get an agent's trust passport (score, tier, badges).
   * Public endpoint, no auth required.
   */
  async passport(agentId?: string): Promise<PassportResponse> {
    const id = agentId ?? this.agentId;
    return this.get<PassportResponse>(
      `/passport/${encodeURIComponent(id)}`,
    );
  }

  // ── Internal HTTP helpers ─────────────────────────────────────────

  get hasApiKey(): boolean {
    return typeof this.apiKey === "string" && this.apiKey.length > 0;
  }

  /**
   * Ensure we have an API key. If none is configured, auto-provision
   * via the free-tier signup endpoint.
   */
  private async ensureApiKey(): Promise<void> {
    if (this.hasApiKey) return;
    await this.signup();
  }

  private async post<T>(
    path: string,
    body: Record<string, unknown>,
    auth: boolean = true,
  ): Promise<T> {
    const headers: Record<string, string> = {
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

    return (await res.json()) as T;
  }

  private async get<T>(path: string): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const res = await this.fetchWithTimeout(url, { method: "GET" });

    if (!res.ok) {
      const detail = await res.text().catch(() => "unknown error");
      throw new KevrosApiError(res.status, path, detail);
    }

    return (await res.json()) as T;
  }

  private async fetchWithTimeout(
    url: string,
    init: RequestInit,
  ): Promise<Response> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);
    try {
      return await fetch(url, { ...init, signal: controller.signal });
    } finally {
      clearTimeout(timer);
    }
  }
}
