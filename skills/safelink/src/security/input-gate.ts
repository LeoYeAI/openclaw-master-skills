import { z } from "zod";
import { ValidationError } from "../utils/errors.js";
import { promises as dns } from "node:dns";
import { isIP } from "node:net";

// ── PII patterns to strip from any string input ──────────────────────────────

const PII_PATTERNS: Array<{ name: string; pattern: RegExp; replacement: string }> = [
  // Private keys (hex 64 chars)
  {
    name: "PRIVATE_KEY_HEX",
    pattern: /\b(0x)?[0-9a-fA-F]{64}\b/g,
    replacement: "[PRIVATE_KEY_REDACTED]",
  },
  // Seed phrases (12 or 24 BIP-39 words)
  {
    name: "SEED_PHRASE",
    pattern:
      /\b([a-z]+ ){11,23}[a-z]+\b/gi,
    replacement: "[SEED_PHRASE_REDACTED]",
  },
  // API keys (Anthropic, Privy patterns)
  {
    name: "API_KEY",
    pattern: /\bsk-ant-[A-Za-z0-9\-_]{20,}\b/g,
    replacement: "[API_KEY_REDACTED]",
  },
  {
    name: "PRIVY_SECRET",
    pattern: /\bprivy-[A-Za-z0-9\-_]{20,}\b/g,
    replacement: "[PRIVY_SECRET_REDACTED]",
  },
  // Social security numbers
  {
    name: "SSN",
    pattern: /\b\d{3}-\d{2}-\d{4}\b/g,
    replacement: "[SSN_REDACTED]",
  },
  // Credit card numbers (naive Luhn-adjacent: 13–19 digits with optional separators)
  {
    name: "CREDIT_CARD",
    pattern: /\b(?:\d[ -]?){13,19}\b/g,
    replacement: "[CC_REDACTED]",
  },
  // Email addresses
  {
    name: "EMAIL",
    pattern: /\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b/g,
    replacement: "[EMAIL_REDACTED]",
  },
  // Phone numbers (NANP and international)
  {
    name: "PHONE",
    pattern: /\b(\+?1[\s.-]?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b/g,
    replacement: "[PHONE_REDACTED]",
  },
];

/** Strip PII from a string. Returns sanitised version. */
export function stripPII(input: string): string {
  let result = input;
  for (const { pattern, replacement } of PII_PATTERNS) {
    result = result.replace(pattern, replacement);
  }
  return result;
}

/** Check if string contains any PII patterns (without stripping). */
export function hasPII(input: string): boolean {
  return PII_PATTERNS.some(({ pattern }) => {
    pattern.lastIndex = 0; // reset stateful global regex
    return pattern.test(input);
  });
}

// ── Shared field validators ───────────────────────────────────────────────────

/** EVM address that is NOT the zero address. */
export const EvmAddress = z
  .string()
  .regex(/^0x[a-fA-F0-9]{40}$/, "Must be a valid EVM address (0x + 40 hex chars)")
  .refine(
    (addr) => addr !== "0x0000000000000000000000000000000000000000",
    "Zero address not allowed"
  );

/** USDC rate: a positive number ≤ 100 (max $100 per operation). */
export const USDCRate = z
  .number()
  .positive("Rate must be positive")
  .max(100, "Rate cannot exceed 100 USDC — increase MAX_RATE in policy to change")
  .finite();

/** Safe task description: string, max 2000 chars, auto-stripped of PII. */
export const SafeTaskDescription = z
  .string()
  .min(1, "Task description cannot be empty")
  .max(2000, "Task description too long (max 2000 chars)")
  .transform(stripPII);

/** Payment model enum. */
export const PaymentModel = z.enum(["per_request", "per_min", "per_execution"]);

// ── Policy object shape ───────────────────────────────────────────────────────

export const PolicySchema = z.object({
  max_task_seconds: z.number().int().positive().max(3600).default(300),
  allowed_chains: z
    .array(z.enum(["base-sepolia", "base-mainnet", "ethereum"]))
    .min(1)
    .default(["base-sepolia"]),
  require_escrow: z.boolean().default(true),
  max_rate_usdc: z.number().positive().max(1000).default(10),
  auto_approve_below_risk: z.number().min(0).max(100).default(30),
});

export type Policy = z.infer<typeof PolicySchema>;

// ── SSRF-safe endpoint URL validation ────────────────────────────────────────

/** Hostname/IP patterns that must never be fetched (loopback, private, link-local). */
const BLOCKED_IP_PATTERNS: RegExp[] = [
  /^127\./,                           // IPv4 loopback
  /^10\./,                            // RFC 1918 class A
  /^172\.(1[6-9]|2\d|3[01])\./,      // RFC 1918 class B
  /^192\.168\./,                      // RFC 1918 class C
  /^169\.254\./,                      // IPv4 link-local / AWS metadata
  /^0\./,                             // "this" network
  /^::1$/,                            // IPv6 loopback
  /^fc[0-9a-f][0-9a-f]:/i,            // IPv6 unique local (fc00::/7)
  /^fe[89ab][0-9a-f]:/i,              // IPv6 link-local (fe80::/10)
  /^100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\./,  // RFC 6598 shared address space
];

const BLOCKED_HOSTNAMES = new Set([
  "localhost",
  "metadata.google.internal",
  "169.254.169.254",   // AWS/GCP/Azure IMDS
  "instance-data",
  "link-local.internal",
]);

/**
 * Validate that a capability endpoint URL is safe to fetch.
 * Throws ValidationError for: non-https, loopback, private IP, metadata endpoints.
 */
export function validateEndpointUrl(rawUrl: string): URL {
  let parsed: URL;
  try {
    parsed = new URL(rawUrl);
  } catch {
    throw new ValidationError(`Invalid endpoint URL: "${rawUrl}"`);
  }

  if (parsed.protocol !== "https:") {
    throw new ValidationError(
      `Endpoint must use https:// — got "${parsed.protocol}". ` +
        `Plain http:// is not allowed for agent-to-agent task delivery.`
    );
  }

  const hostname = parsed.hostname.toLowerCase();

  assertHostNotBlocked(hostname);

  return parsed;
}

function assertHostNotBlocked(hostname: string): void {
  if (BLOCKED_HOSTNAMES.has(hostname)) {
    throw new ValidationError(
      `Endpoint hostname "${hostname}" is not permitted (reserved/internal address).`
    );
  }

  for (const pattern of BLOCKED_IP_PATTERNS) {
    if (pattern.test(hostname)) {
      throw new ValidationError(
        `Endpoint address "${hostname}" is in a private/reserved IP range. ` +
          `Only public HTTPS endpoints are allowed.`
      );
    }
  }
}

/**
 * Strict endpoint validation including DNS resolution.
 * Rejects domains that resolve to private/loopback/link-local/internal IP ranges.
 */
export async function validateEndpointUrlStrict(
  rawUrl: string,
  resolver: typeof dns.lookup = dns.lookup
): Promise<URL> {
  const parsed = validateEndpointUrl(rawUrl);
  const hostname = parsed.hostname.toLowerCase();

  if (isIP(hostname)) {
    assertHostNotBlocked(hostname);
    return parsed;
  }

  let resolved: Array<{ address: string }> = [];
  try {
    const out = await resolver(hostname, { all: true });
    resolved = out as Array<{ address: string }>;
  } catch {
    throw new ValidationError(`Could not resolve endpoint hostname "${hostname}"`);
  }

  if (resolved.length === 0) {
    throw new ValidationError(`Endpoint hostname "${hostname}" did not resolve to any address`);
  }

  for (const entry of resolved) {
    assertHostNotBlocked(entry.address.toLowerCase());
  }

  return parsed;
}

// ── Validate + throw helper ───────────────────────────────────────────────────

export function validateInput<T>(schema: z.ZodType<T>, raw: unknown): T {
  const result = schema.safeParse(raw);
  if (!result.success) {
    const msg = result.error.issues
      .map((i) => `${i.path.join(".")}: ${i.message}`)
      .join("; ");
    throw new ValidationError(`Input validation failed — ${msg}`);
  }
  return result.data;
}
