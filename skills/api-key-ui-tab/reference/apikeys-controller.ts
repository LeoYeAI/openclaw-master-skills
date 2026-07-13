import type { GatewayBrowserClient } from "../gateway";

export type DiscoveredKey = {
  id: string;
  path: string[];
  pathStr: string;
  name: string;
  description: string;
  configured: boolean;
  maskedValue?: string;
  docsUrl?: string;
  provider?: string;
  /** Whether this key is stored in the vault (vs plaintext config) */
  inVault?: boolean;
};

export type VaultStatus = {
  vaultExists: boolean;
  vaultPath: string;
  keyCount: number;
  providerConfigured: boolean;
  plaintextCount: number;
};

export type AuthProfile = {
  id: string;
  type: "api_key" | "token" | "oauth";
  provider: string;
  email: string | null;
  inVault: boolean;
  hasCredential: boolean;
  status: "active" | "error" | "cooldown" | "unused";
  isLastGood: boolean;
  lastUsed: number | null;
  errorCount: number;
  lastFailureAt: number | null;
  cooldownUntil: number | null;
};

export type ApiKeysState = {
  client: GatewayBrowserClient | null;
  connected: boolean;
  apikeysLoading?: boolean;
  apikeysError?: string | null;
  apikeysKeys?: DiscoveredKey[];
  apikeysEdits?: Record<string, string>;
  apikeysBusyKey?: string | null;
  apikeysMessage?: { kind: "success" | "error"; text: string } | null;
  apikeysConfigHash?: string | null;
  apikeysRefreshSuccess?: boolean;
  apikeysVaultStatus?: VaultStatus | null;
  apikeysMigrating?: boolean;
  authProfiles?: AuthProfile[];
  authProfilesLoading?: boolean;
};

/**
 * Known provider metadata for better UX on recognized keys
 */
const KNOWN_PROVIDERS: Record<string, { name: string; description: string; docsUrl?: string }> = {
  // env keys
  ANTHROPIC_API_KEY: {
    name: "Anthropic",
    description: "Claude models",
    docsUrl: "https://console.anthropic.com/settings/keys",
  },
  OPENAI_API_KEY: {
    name: "OpenAI",
    description: "GPT, Whisper, DALL-E, embeddings",
    docsUrl: "https://platform.openai.com/api-keys",
  },
  BRAVE_API_KEY: {
    name: "Brave Search",
    description: "Web search API",
    docsUrl: "https://brave.com/search/api/",
  },
  DEEPGRAM_API_KEY: {
    name: "Deepgram",
    description: "Speech-to-text",
    docsUrl: "https://console.deepgram.com/",
  },
  GOOGLE_API_KEY: {
    name: "Google",
    description: "Gemini models, Google APIs",
    docsUrl: "https://aistudio.google.com/apikey",
  },
  GEMINI_API_KEY: {
    name: "Google Gemini",
    description: "Gemini models",
    docsUrl: "https://aistudio.google.com/apikey",
  },
  ELEVENLABS_API_KEY: {
    name: "ElevenLabs",
    description: "Text-to-speech",
    docsUrl: "https://elevenlabs.io/app/settings/api-keys",
  },
  OPENROUTER_API_KEY: {
    name: "OpenRouter",
    description: "Multi-provider LLM access",
    docsUrl: "https://openrouter.ai/settings/keys",
  },
  GROQ_API_KEY: {
    name: "Groq",
    description: "Fast Llama/Mixtral inference",
    docsUrl: "https://console.groq.com/keys",
  },
  FIREWORKS_API_KEY: {
    name: "Fireworks AI",
    description: "Open-source model inference",
    docsUrl: "https://fireworks.ai/account/api-keys",
  },
  MISTRAL_API_KEY: {
    name: "Mistral AI",
    description: "Mistral models",
    docsUrl: "https://console.mistral.ai/api-keys/",
  },
  XAI_API_KEY: { name: "xAI (Grok)", description: "Grok models", docsUrl: "https://console.x.ai/" },
  PERPLEXITY_API_KEY: {
    name: "Perplexity",
    description: "AI-powered search",
    docsUrl: "https://www.perplexity.ai/settings/api",
  },
  GITHUB_TOKEN: {
    name: "GitHub",
    description: "GitHub API access",
    docsUrl: "https://github.com/settings/tokens",
  },
  HUME_API_KEY: {
    name: "Hume AI",
    description: "Emotion AI",
    docsUrl: "https://platform.hume.ai/",
  },
  HUME_SECRET_KEY: {
    name: "Hume AI Secret",
    description: "Hume AI secret key",
    docsUrl: "https://platform.hume.ai/",
  },
  MATON_API_KEY: {
    name: "Maton",
    description: "Maton API",
  },
  // Common nested paths
  elevenlabs: {
    name: "ElevenLabs",
    description: "Text-to-speech",
    docsUrl: "https://elevenlabs.io/app/settings/api-keys",
  },
  openai: {
    name: "OpenAI",
    description: "GPT, Whisper, DALL-E",
    docsUrl: "https://platform.openai.com/api-keys",
  },
  anthropic: {
    name: "Anthropic",
    description: "Claude models",
    docsUrl: "https://console.anthropic.com/settings/keys",
  },
  deepgram: {
    name: "Deepgram",
    description: "Speech-to-text",
    docsUrl: "https://console.deepgram.com/",
  },
  sag: {
    name: "ElevenLabs (sag)",
    description: "TTS skill",
    docsUrl: "https://elevenlabs.io/app/settings/api-keys",
  },
  "openai-whisper-api": {
    name: "OpenAI Whisper",
    description: "Transcription skill",
    docsUrl: "https://platform.openai.com/api-keys",
  },
  "openai-image-gen": {
    name: "OpenAI Images",
    description: "DALL-E skill",
    docsUrl: "https://platform.openai.com/api-keys",
  },
  "deepgram-streaming": {
    name: "Deepgram Streaming",
    description: "Live transcription",
    docsUrl: "https://console.deepgram.com/",
  },
};

/**
 * Patterns that indicate an API key field
 */
const KEY_PATTERNS = [
  /apiKey$/i,
  /api_key$/i,
  /^token$/i,
  /secret$/i,
  /_KEY$/,
  /_TOKEN$/,
  /_SECRET$/,
];

/**
 * Paths to skip when scanning (not API keys)
 */
const SKIP_PATHS = [
  "meta",
  "wizard",
  "update",
  "browser",
  "auth.profiles",
  "gateway.auth.token",
  "channels.telegram.botToken",
  "channels.discord.token",
];

function isKeyField(fieldName: string): boolean {
  return KEY_PATTERNS.some((pattern) => pattern.test(fieldName));
}

function shouldSkipPath(path: string[]): boolean {
  const pathStr = path.join(".");
  return SKIP_PATHS.some((skip) => pathStr.startsWith(skip));
}

function maskKey(key: string): string {
  if (!key || key.length <= 8) return "••••••••";
  return `${key.slice(0, 4)}...${key.slice(-4)}`;
}

const REDACTED_SENTINEL = "__OPENCLAW_REDACTED__";

function isSecretRef(value: unknown): boolean {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const v = value as Record<string, unknown>;
  return (v.source === "env" || v.source === "file" || v.source === "exec") &&
    typeof v.provider === "string" && typeof v.id === "string";
}

function isRedacted(value: unknown): boolean {
  return value === REDACTED_SENTINEL;
}

function generateName(path: string[]): string {
  for (const segment of path) {
    const known = KNOWN_PROVIDERS[segment];
    if (known) return known.name;
  }
  if (path[0] === "env" && path[1]) {
    const known = KNOWN_PROVIDERS[path[1]];
    if (known) return known.name;
    return path[1]
      .replace(/_API_KEY$|_KEY$|_TOKEN$|_SECRET$/i, "")
      .split("_")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
      .join(" ");
  }
  if (path[0] === "skills" && path[1] === "entries" && path[2]) {
    const known = KNOWN_PROVIDERS[path[2]];
    if (known) return known.name;
    return `Skill: ${path[2]}`;
  }
  const secondToLast = path[path.length - 2];
  if (secondToLast) {
    const known = KNOWN_PROVIDERS[secondToLast];
    if (known) return known.name;
    return secondToLast.charAt(0).toUpperCase() + secondToLast.slice(1);
  }
  return path.join(".");
}

function generateDescription(path: string[]): string {
  for (const segment of path) {
    const known = KNOWN_PROVIDERS[segment];
    if (known) return known.description;
  }
  if (path[0] === "env" && path[1]) {
    const known = KNOWN_PROVIDERS[path[1]];
    if (known) return known.description;
  }
  if (path[0] === "skills" && path[1] === "entries") {
    return `API key for ${path[2]} skill`;
  }
  if (path[0] === "env") return `Environment variable`;
  return `Config: ${path.slice(0, -1).join(".")}`;
}

function getDocsUrl(path: string[]): string | undefined {
  for (const segment of path) {
    const known = KNOWN_PROVIDERS[segment];
    if (known?.docsUrl) return known.docsUrl;
  }
  if (path[0] === "env" && path[1]) {
    const known = KNOWN_PROVIDERS[path[1]];
    if (known?.docsUrl) return known.docsUrl;
  }
  return undefined;
}

/**
 * Recursively scan config for API keys, detecting both plaintext and SecretRef values
 */
function scanForKeys(
  obj: Record<string, unknown>,
  path: string[] = [],
  results: DiscoveredKey[] = [],
): DiscoveredKey[] {
  if (!obj || typeof obj !== "object") return results;

  for (const [key, value] of Object.entries(obj)) {
    const currentPath = [...path, key];
    if (shouldSkipPath(currentPath)) continue;

    if (isKeyField(key)) {
      const pathStr = currentPath.join(".");
      const isRef = isSecretRef(value);
      const redacted = isRedacted(value);
      const hasValue = isRef || redacted || (typeof value === "string" && value.length > 0 && value !== REDACTED_SENTINEL);

      // Redacted values mean the gateway scrubbed a real value — it's configured.
      // Could be a SecretRef that got flattened, or a plaintext key that was masked.
      results.push({
        id: pathStr,
        path: currentPath,
        pathStr,
        name: generateName(currentPath),
        description: generateDescription(currentPath),
        configured: hasValue,
        maskedValue: hasValue
          ? isRef ? "🔒 vault"
          : redacted ? "••••••••"
          : maskKey(value as string)
          : undefined,
        docsUrl: getDocsUrl(currentPath),
        inVault: isRef,
      });
    }

    if (value && typeof value === "object" && !Array.isArray(value) && !isSecretRef(value)) {
      scanForKeys(value as Record<string, unknown>, currentPath, results);
    }
  }

  return results;
}

function addMissingCommonKeys(
  keys: DiscoveredKey[],
): DiscoveredKey[] {
  const existingEnvKeys = new Set(keys.filter((k) => k.path[0] === "env").map((k) => k.path[1]));

  const commonEnvKeys = [
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "BRAVE_API_KEY",
    "DEEPGRAM_API_KEY",
    "GOOGLE_API_KEY",
    "ELEVENLABS_API_KEY",
    "GITHUB_TOKEN",
  ];

  for (const envKey of commonEnvKeys) {
    if (!existingEnvKeys.has(envKey)) {
      const path = ["env", envKey];
      const known = KNOWN_PROVIDERS[envKey];
      keys.push({
        id: path.join("."),
        path,
        pathStr: path.join("."),
        name: known?.name || envKey,
        description: known?.description || "Not configured",
        configured: false,
        docsUrl: known?.docsUrl,
        inVault: false,
      });
    }
  }

  return keys;
}

function sortKeys(keys: DiscoveredKey[]): DiscoveredKey[] {
  return keys.toSorted((a, b) => {
    const aIsEnv = a.path[0] === "env" ? 0 : 1;
    const bIsEnv = b.path[0] === "env" ? 0 : 1;
    if (aIsEnv !== bIsEnv) return aIsEnv - bIsEnv;
    return a.name.localeCompare(b.name);
  });
}

/**
 * Merge vault keys with config-scanned keys.
 * Vault keys get masked values from the vault list response.
 */
function mergeVaultKeys(
  keys: DiscoveredKey[],
  vaultKeys: Array<{ id: string; masked: string }>,
): DiscoveredKey[] {
  const vaultMap = new Map(vaultKeys.map((k) => [k.id, k.masked]));

  for (const key of keys) {
    // Already detected as vault ref by config scan
    if (key.inVault) continue;

    // For env keys, check if they exist in the vault
    if (key.path[0] === "env" && key.path[1]) {
      const vaultMasked = vaultMap.get(key.path[1]);
      if (vaultMasked) {
        key.inVault = true;
        key.configured = true;
        key.maskedValue = vaultMasked;
      }
    }
  }

  return keys;
}

/**
 * Load API keys by scanning config + vault status
 */
export async function loadApiKeys(state: ApiKeysState): Promise<void> {
  if (!state.client || !state.connected) return;

  state.apikeysError = null;

  try {
    // Fetch config, vault status, and vault keys in parallel
    const [configRes, vaultStatusRes, vaultListRes] = await Promise.all([
      state.client.request<{ config?: Record<string, unknown>; hash?: string }>("config.get", {}),
      state.client.request<{ ok: boolean } & VaultStatus>("secrets.status", {}).catch(() => null),
      state.client.request<{ ok: boolean; keys: Array<{ id: string; masked: string }> }>("secrets.list", {}).catch(() => null),
    ]);

    const config = configRes?.config ?? {};
    state.apikeysConfigHash = configRes?.hash || null;

    // Update vault status
    if (vaultStatusRes?.ok) {
      state.apikeysVaultStatus = {
        vaultExists: vaultStatusRes.vaultExists,
        vaultPath: vaultStatusRes.vaultPath,
        keyCount: vaultStatusRes.keyCount,
        providerConfigured: vaultStatusRes.providerConfigured,
        plaintextCount: vaultStatusRes.plaintextCount,
      };
    }

    // Scan config for all API keys
    let keys = scanForKeys(config);
    keys = addMissingCommonKeys(keys);

    // Merge vault info if available
    if (vaultListRes?.ok && vaultListRes.keys) {
      keys = mergeVaultKeys(keys, vaultListRes.keys);
    }

    keys = sortKeys(keys);

    state.apikeysKeys = keys;
    state.apikeysError = null;
    state.apikeysLoading = false;
    state.apikeysRefreshSuccess = true;

    setTimeout(() => {
      state.apikeysRefreshSuccess = false;
    }, 2000);
  } catch (err) {
    state.apikeysError = err instanceof Error ? err.message : String(err);
    state.apikeysLoading = false;
  }
}

export async function loadAuthProfiles(state: ApiKeysState): Promise<void> {
  if (!state.client || !state.connected) return;
  state.authProfilesLoading = true;
  try {
    const res = await state.client.request<{ ok: boolean; profiles: AuthProfile[] }>(
      "secrets.authProfiles.list",
      {},
    );
    state.authProfiles = res.profiles ?? [];
  } catch {
    state.authProfiles = [];
  } finally {
    state.authProfilesLoading = false;
  }
}

export async function resetAuthProfileErrors(state: ApiKeysState, profileId: string): Promise<void> {
  if (!state.client || !state.connected) return;
  try {
    await state.client.request("secrets.authProfiles.resetErrors", { profileId });
    state.apikeysMessage = { kind: "success", text: `Reset errors for ${profileId}` };
    await loadAuthProfiles(state);
  } catch (err) {
    state.apikeysMessage = { kind: "error", text: `Failed: ${err instanceof Error ? err.message : String(err)}` };
  }
}

export async function deleteAuthProfile(state: ApiKeysState, profileId: string): Promise<void> {
  if (!state.client || !state.connected) return;
  try {
    await state.client.request("secrets.authProfiles.delete", { profileId });
    state.apikeysMessage = { kind: "success", text: `Removed ${profileId}` };
    await loadAuthProfiles(state);
  } catch (err) {
    state.apikeysMessage = { kind: "error", text: `Failed: ${err instanceof Error ? err.message : String(err)}` };
  }
}

export function updateApiKeyEdit(state: ApiKeysState, keyId: string, value: string): void {
  state.apikeysEdits = { ...state.apikeysEdits, [keyId]: value };
}

/**
 * Save an API key — always goes through vault now
 */
export async function saveApiKey(state: ApiKeysState, keyId: string): Promise<void> {
  if (!state.client || !state.connected) return;

  const key = state.apikeysKeys?.find((k) => k.id === keyId);
  if (!key) return;

  const value = state.apikeysEdits?.[keyId];
  if (!value || value.trim().length === 0) return;

  state.apikeysBusyKey = keyId;
  state.apikeysError = null;
  state.apikeysMessage = null;

  try {
    // Extract the secret ID (env key name like OPENAI_API_KEY)
    const secretId = key.path[0] === "env" ? key.path[1] : key.pathStr;

    await state.client.request("secrets.write", {
      id: secretId,
      value: value.trim(),
    });

    // Clear edit buffer
    const edits = { ...state.apikeysEdits };
    delete edits[keyId];
    state.apikeysEdits = edits;

    state.apikeysMessage = {
      kind: "success",
      text: `${key.name} saved to vault. Restart the gateway for changes to take effect.`,
    };
    (state as Record<string, unknown>).restartNeeded = true;

    // Reload after brief delay
    setTimeout(() => loadApiKeys(state), 1500);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    state.apikeysError = message;
    state.apikeysMessage = {
      kind: "error",
      text: `Failed to save ${key.name}: ${message}`,
    };
  } finally {
    state.apikeysBusyKey = null;
  }
}

/**
 * Clear an API key from vault and config
 */
export async function clearApiKey(state: ApiKeysState, keyId: string): Promise<void> {
  if (!state.client || !state.connected) return;

  const key = state.apikeysKeys?.find((k) => k.id === keyId);
  if (!key) return;

  state.apikeysBusyKey = keyId;
  state.apikeysError = null;
  state.apikeysMessage = null;

  try {
    const secretId = key.path[0] === "env" ? key.path[1] : key.pathStr;

    await state.client.request("secrets.delete", { id: secretId });

    state.apikeysMessage = {
      kind: "success",
      text: `${key.name} removed.`,
    };

    setTimeout(() => loadApiKeys(state), 1500);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    state.apikeysError = message;
    state.apikeysMessage = {
      kind: "error",
      text: `Failed to clear ${key.name}: ${message}`,
    };
  } finally {
    state.apikeysBusyKey = null;
  }
}

/**
 * Migrate all plaintext keys to vault
 */
export async function migrateToVault(state: ApiKeysState): Promise<void> {
  if (!state.client || !state.connected) return;

  state.apikeysMigrating = true;
  state.apikeysMessage = null;

  try {
    const result = await state.client.request<{
      ok: boolean;
      migrated: number;
      keys: string[];
    }>("secrets.migrate", {});

    if (result.migrated === 0) {
      state.apikeysMessage = {
        kind: "success",
        text: "All keys are already in the vault. Nothing to migrate.",
      };
    } else {
      state.apikeysMessage = {
        kind: "success",
        text: `Migrated ${result.migrated} key${result.migrated === 1 ? "" : "s"} to vault: ${result.keys.join(", ")}`,
      };
    }

    // Reload
    setTimeout(() => loadApiKeys(state), 1500);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    state.apikeysMessage = {
      kind: "error",
      text: `Migration failed: ${message}`,
    };
  } finally {
    state.apikeysMigrating = false;
  }
}

export async function addVaultSecret(
  state: ApiKeysState,
  name: string,
  value: string,
  envEntry = false,
): Promise<boolean> {
  if (!state.client || !state.connected) return false;

  try {
    await state.client.request("secrets.write", {
      id: name.trim(),
      value: value.trim(),
      envEntry,
    });

    state.apikeysMessage = {
      kind: "success",
      text: `Secret "${name}" added to vault. Restart the gateway for the key to take effect.`,
    };
    (state as Record<string, unknown>).restartNeeded = true;

    setTimeout(() => loadApiKeys(state), 1000);
    return true;
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    state.apikeysMessage = {
      kind: "error",
      text: `Failed to add secret: ${message}`,
    };
    return false;
  }
}

export async function loadVaultOnlyKeys(state: ApiKeysState): Promise<void> {
  if (!state.client || !state.connected) return;
  try {
    const res = await state.client.request<{ keys: { id: string; masked: string }[] }>("secrets.list", {});
    (state as Record<string, unknown>).vaultAllKeys = res?.keys ?? [];
  } catch {
    (state as Record<string, unknown>).vaultAllKeys = [];
  }
}
