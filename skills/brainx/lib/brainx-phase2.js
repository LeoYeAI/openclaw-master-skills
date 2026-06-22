function parseBoolEnv(name, fallback) {
  const raw = process.env[name];
  if (raw === undefined) return fallback;
  const v = String(raw).trim().toLowerCase();
  if (['1', 'true', 'yes', 'on'].includes(v)) return true;
  if (['0', 'false', 'no', 'off'].includes(v)) return false;
  return fallback;
}

function getPhase2Config() {
  const allowlistContexts = (process.env.BRAINX_PII_SCRUB_ALLOWLIST_CONTEXTS || '')
    .split(',')
    .map((v) => v.trim())
    .filter(Boolean);
  return {
    piiScrubEnabled: parseBoolEnv('BRAINX_PII_SCRUB_ENABLED', true),
    piiScrubReplacement: process.env.BRAINX_PII_SCRUB_REPLACEMENT || '[REDACTED]',
    piiScrubAllowlistContexts: allowlistContexts,
    dedupeSimThreshold: Number.parseFloat(process.env.BRAINX_DEDUPE_SIM_THRESHOLD || '0.92') || 0.92,
    dedupeRecentDays: Number.parseInt(process.env.BRAINX_DEDUPE_RECENT_DAYS || '30', 10) || 30
  };
}

const PII_PATTERNS = [
  { reason: 'email', regex: /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi },
  { reason: 'phone', regex: /(?<!\w)(?:\+?1[\s.\-]?)?(?:\(?\d{3}\)?[\s.\-]?)?\d{3}[\s.\-]?\d{4}(?!\w)/g },
  { reason: 'openai_key', regex: /\bsk-[A-Za-z0-9]{16,}\b/g },
  { reason: 'github_token', regex: /\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b/g },
  { reason: 'github_pat', regex: /\bgithub_pat_[A-Za-z0-9_]{20,}\b/g },
  { reason: 'aws_access_key', regex: /\bAKIA[0-9A-Z]{16}\b/g },
  { reason: 'slack_token', regex: /\bxox(?:b|p|a|r|s)-[A-Za-z0-9-]{10,}\b/g },
  { reason: 'bearer_token', regex: /\bBearer\s+[A-Za-z0-9._\-]{16,}\b/gi },
  { reason: 'api_key_assignment', regex: /\b(?:api|access|secret)[_-]?key\s*[:=]\s*['"]?[A-Za-z0-9._\-]{12,}['"]?/gi },
  { reason: 'jwt_token', regex: /\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b/g },
  { reason: 'private_key_block', regex: /-----BEGIN(?: RSA| EC| OPENSSH)? PRIVATE KEY-----[\s\S]*?-----END(?: RSA| EC| OPENSSH)? PRIVATE KEY-----/g },
  { reason: 'iban', regex: /\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b/g },
  { reason: 'credit_card', regex: /\b(?:\d[ -]*?){13,19}\b/g },
  { reason: 'ipv4', regex: /\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b/g },
  { reason: 'password_inline', regex: /(?:contraseña|password|passwd|pass|clave|secret)\s*(?:(?:es|is|actual|nueva|new|=|:)\s*){1,2}['"`]?[^\s'"`,]{4,}['"`]?/gi },
  { reason: 'password_quoted', regex: /(?:contraseña|password|passwd|clave)\s*[:=]\s*['"][^'"]{4,}['"]/gi },
];

function shouldScrubForContext(context, cfg = {}) {
  const enabled = cfg.piiScrubEnabled !== undefined ? !!cfg.piiScrubEnabled : true;
  if (!enabled) return false;
  const ctx = context == null ? '' : String(context).trim();
  if (!ctx) return true;
  const allow = new Set((cfg.piiScrubAllowlistContexts || []).map((v) => String(v).trim()).filter(Boolean));
  return !allow.has(ctx);
}

function scrubTextPII(text, opts = {}) {
  const input = text == null ? text : String(text);
  const enabled = opts.enabled !== undefined ? !!opts.enabled : true;
  const replacement = opts.replacement || '[REDACTED]';
  if (input == null || !enabled) {
    return { text: input, redacted: false, reasons: [] };
  }

  let out = input;
  const reasons = [];
  for (const { reason, regex } of PII_PATTERNS) {
    regex.lastIndex = 0;
    if (!regex.test(out)) continue;
    reasons.push(reason);
    regex.lastIndex = 0;
    out = out.replace(regex, replacement);
  }
  return { text: out, redacted: reasons.length > 0, reasons };
}

function mergeTagsWithMetadata(tags, meta = {}) {
  const input = Array.isArray(tags) ? tags.slice() : [];
  const seen = new Set(input.map(String));
  if (meta.redacted) {
    for (const tag of ['pii:redacted', ...(meta.reasons || []).map((r) => `pii:${r}`)]) {
      if (seen.has(tag)) continue;
      seen.add(tag);
      input.push(tag);
    }
  }
  return input;
}

function deriveMergePlan(existingRow, lifecycle, now) {
  const current = existingRow || null;
  const tsNow = now || new Date();
  if (!current) {
    return {
      found: false,
      finalId: null,
      finalRecurrence: Number(lifecycle.recurrence_count || 1),
      finalFirstSeen: lifecycle.first_seen || tsNow,
      finalLastSeen: lifecycle.last_seen || tsNow
    };
  }

  return {
    found: true,
    finalId: current.id,
    finalRecurrence: Math.max(
      Number(current.recurrence_count || 1) + 1,
      Number(lifecycle.recurrence_count || 0)
    ),
    finalFirstSeen: lifecycle.first_seen || current.first_seen || tsNow,
    finalLastSeen: lifecycle.last_seen || tsNow
  };
}

function cosineSimilarity(a, b) {
  if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length || a.length === 0) return 0;
  let dot = 0;
  let na = 0;
  let nb = 0;
  for (let i = 0; i < a.length; i++) {
    const x = Number(a[i]) || 0;
    const y = Number(b[i]) || 0;
    dot += x * y;
    na += x * x;
    nb += y * y;
  }
  if (!na || !nb) return 0;
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

module.exports = {
  getPhase2Config,
  shouldScrubForContext,
  scrubTextPII,
  mergeTagsWithMetadata,
  deriveMergePlan,
  cosineSimilarity
};
