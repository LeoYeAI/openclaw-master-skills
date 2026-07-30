import { createHmac } from "crypto";
import { execSync } from "child_process";

interface HookEvent {
  type: string;
  action: string;
  sessionKey: string;
  timestamp: Date;
  messages: string[];
  context: {
    toolName?: string;
    args?: Record<string, unknown>;
    sessionId?: string;
    workspaceDir?: string;
    cfg?: Record<string, unknown>;
    [key: string]: unknown;
  };
}

interface MandateCheckResult {
  valid: boolean;
  mandate?: {
    id: string;
    scope: string;
    validUntil: string;
    constraints?: Record<string, unknown>;
  };
  reason?: string;
}

const SENSITIVE_KEYWORDS = [
  "payment",
  "transfer",
  "sign",
  "approve",
  "authorize",
  "send money",
  "wire",
  "invoice",
  "contract",
  "execute",
  "withdraw",
  "deposit",
];

function _getProtectedPatterns(): string[] {
  const envPatterns = process.env.VIA_PROTECTED_TOOLS;
  if (envPatterns) {
    return envPatterns.split(",").map((p) => p.trim());
  }
  return SENSITIVE_KEYWORDS;
}

function _requiresMandate(toolName: string, args: Record<string, unknown>): boolean {
  const patterns = _getProtectedPatterns();
  const argsStr = JSON.stringify(args).toLowerCase();
  const combined = `${toolName.toLowerCase()}:${argsStr}`;

  return patterns.some((pattern) => {
    try {
      return new RegExp(pattern.toLowerCase()).test(combined);
    } catch {
      return combined.includes(pattern.toLowerCase());
    }
  });
}

function _signRequest(body: string, timestamp: string): string {
  const secret = process.env.VIA_SIGNATURE_SECRET;
  if (!secret) throw new Error("VIA_SIGNATURE_SECRET not set");
  const payload = body ? `${timestamp}.${body}` : timestamp;
  return createHmac("sha256", secret).update(payload).digest("hex");
}

async function _checkMandateViaApi(
  toolName: string,
  scope: string
): Promise<MandateCheckResult> {
  const apiUrl = process.env.VIA_API_URL || "https://api.humanos.id";
  const apiKey = process.env.VIA_API_KEY;

  if (!apiKey) {
    return { valid: false, reason: "VIA API credentials not configured" };
  }

  try {
    const timestamp = Date.now().toString();
    const queryBody = "";
    const signature = _signRequest(queryBody, timestamp);

    const encodedScope = encodeURIComponent(scope);
    const result = execSync(
      `curl -s -X GET "${apiUrl}/v1/via/mandates?scope=${encodedScope}&toolName=${encodeURIComponent(toolName)}" ` +
        `-H "Authorization: Bearer ${apiKey}" ` +
        `-H "X-Timestamp: ${timestamp}" ` +
        `-H "X-Signature: ${signature}" ` +
        `-H "Content-Type: application/json"`,
      { timeout: 5000, encoding: "utf-8" }
    );

    const data = JSON.parse(result);

    if (data && Array.isArray(data) && data.length > 0) {
      const mandate = data[0];
      const now = new Date();
      const validUntil = new Date(mandate.valid_until || mandate.validUntil);

      if (mandate.revoked_at || mandate.revokedAt) {
        return { valid: false, reason: "Mandate has been revoked" };
      }

      if (validUntil < now) {
        return { valid: false, reason: "Mandate has expired" };
      }

      return {
        valid: true,
        mandate: {
          id: mandate.id,
          scope: mandate.scope,
          validUntil: validUntil.toISOString(),
          constraints: mandate.constraints,
        },
      };
    }

    return { valid: false, reason: "No valid mandate found for this action" };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`[humanos-guard] API check failed: ${message}`);
    return { valid: false, reason: `Mandate verification failed: ${message}` };
  }
}

function _extractScope(toolName: string, args: Record<string, unknown>): string {
  const argsStr = JSON.stringify(args).toLowerCase();

  if (argsStr.includes("payment") || argsStr.includes("transfer")) return "payments";
  if (argsStr.includes("sign") || argsStr.includes("contract")) return "signing";
  if (argsStr.includes("patient") || argsStr.includes("medical")) return "healthcare.data";
  if (argsStr.includes("employee") || argsStr.includes("onboard")) return "hr.onboarding";

  return `tool.${toolName}`;
}

const handler = async (event: HookEvent): Promise<void> => {
  if (event.type !== "tool" || event.action !== "pre") {
    return;
  }

  const toolName = event.context.toolName || "unknown";
  const args = (event.context.args || {}) as Record<string, unknown>;

  if (!_requiresMandate(toolName, args)) {
    return;
  }

  console.log(`[humanos-guard] Checking mandate for tool: ${toolName}`);

  const scope = _extractScope(toolName, args);
  const result = await _checkMandateViaApi(toolName, scope);

  if (!result.valid) {
    const reason = result.reason || "No valid mandate";
    event.messages.push(
      `Action blocked by VIA Mandate Guard. ${reason}. ` +
        `Use the humanos skill to create an approval request before proceeding. ` +
        `Example: "I need approval from manager@company.com to ${scope}"`
    );
    console.log(`[humanos-guard] BLOCKED: ${toolName} — ${reason}`);

    if (event.context && typeof event.context === "object") {
      (event.context as Record<string, unknown>).blocked = true;
      (event.context as Record<string, unknown>).blockReason = reason;
    }
  } else {
    console.log(
      `[humanos-guard] ALLOWED: ${toolName} — mandate ${result.mandate?.id} valid until ${result.mandate?.validUntil}`
    );
  }
};

export default handler;
