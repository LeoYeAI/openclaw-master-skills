import fs from "node:fs/promises";
import path from "node:path";
import { ErrorCodes, errorShape } from "../protocol/index.js";
import type { GatewayRequestHandlers } from "./types.js";
import { resolveUserPath } from "../../utils.js";
import { loadAuthProfileStore, saveAuthProfileStore } from "../../agents/auth-profiles.js";
import type { AuthProfileStore } from "../../agents/auth-profiles/types.js";
import { isSecretRef } from "../../config/types.secrets.js";

// ─── Constants ───────────────────────────────────────────────────────────────

const DEFAULT_SECRETS_PATH = "~/.openclaw/secrets.json";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function getSecretsFilePath(): string {
  return resolveUserPath(DEFAULT_SECRETS_PATH);
}

async function readSecretsFile(): Promise<Record<string, string>> {
  const filePath = getSecretsFilePath();
  try {
    const raw = await fs.readFile(filePath, "utf-8");
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return {};
    }
    return parsed as Record<string, string>;
  } catch {
    return {};
  }
}

async function writeSecretsFile(secrets: Record<string, string>): Promise<void> {
  const filePath = getSecretsFilePath();
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, JSON.stringify(secrets, null, 2) + "\n", { mode: 0o600 });
}

function maskSecret(value: string): string {
  if (!value || value.length <= 8) return "••••••••";
  return `${value.slice(0, 4)}...${value.slice(-4)}`;
}

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

// ─── Config helpers ──────────────────────────────────────────────────────────

/**
 * Read openclaw.json, apply a mutation, and write it back.
 */
async function patchConfig(
  mutate: (config: Record<string, unknown>) => void,
): Promise<void> {
  const configPath = resolveUserPath("~/.openclaw/openclaw.json");
  const raw = await fs.readFile(configPath, "utf-8");
  const config = JSON.parse(raw) as Record<string, unknown>;
  mutate(config);
  await fs.writeFile(configPath, JSON.stringify(config, null, 2) + "\n");
}

function ensureSecretsProvider(config: Record<string, unknown>): void {
  if (!config.secrets || typeof config.secrets !== "object") {
    config.secrets = {};
  }
  const secrets = config.secrets as Record<string, unknown>;
  if (!secrets.providers || typeof secrets.providers !== "object") {
    secrets.providers = {};
  }
  const providers = secrets.providers as Record<string, unknown>;
  if (!providers.default) {
    providers.default = {
      source: "file",
      path: DEFAULT_SECRETS_PATH,
      mode: "json",
    };
  }
  if (!secrets.defaults || typeof secrets.defaults !== "object") {
    secrets.defaults = {};
  }
  const defaults = secrets.defaults as Record<string, unknown>;
  if (!defaults.file) {
    defaults.file = "default";
  }
}

function makeSecretRef(secretId: string): { source: string; provider: string; id: string } {
  return { source: "file", provider: "default", id: `/${secretId}` };
}

// ─── Key pattern detection ───────────────────────────────────────────────────

const KEY_PATTERNS = [
  /apiKey$/i, /api_key$/i, /^token$/i, /secret$/i,
  /_KEY$/, /_TOKEN$/, /_SECRET$/,
];

const SKIP_PATHS = [
  "meta", "wizard", "update", "browser", "auth.profiles",
  "gateway.auth.token", "channels.telegram.botToken", "channels.discord.token",
];

function isKeyField(name: string): boolean {
  return KEY_PATTERNS.some(p => p.test(name));
}

function shouldSkipPath(pathStr: string): boolean {
  return SKIP_PATHS.some(s => pathStr.startsWith(s));
}

interface PlaintextKey {
  path: string[];
  pathStr: string;
  value: string;
}

function scanPlaintextKeys(
  obj: Record<string, unknown>,
  currentPath: string[] = [],
  results: PlaintextKey[] = [],
): PlaintextKey[] {
  if (!obj || typeof obj !== "object") return results;
  for (const [key, value] of Object.entries(obj)) {
    const p = [...currentPath, key];
    const pathStr = p.join(".");
    if (shouldSkipPath(pathStr)) continue;
    if (isKeyField(key) && typeof value === "string" && value.length > 0) {
      results.push({ path: p, pathStr, value });
    }
    if (value && typeof value === "object" && !Array.isArray(value)) {
      scanPlaintextKeys(value as Record<string, unknown>, p, results);
    }
  }
  return results;
}

function isSecretRef(value: unknown): boolean {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const v = value as Record<string, unknown>;
  return (v.source === "env" || v.source === "file" || v.source === "exec") &&
    typeof v.provider === "string" && typeof v.id === "string";
}

// ─── RPC Handlers ────────────────────────────────────────────────────────────

export function createSecretsHandlers(params: {
  reloadSecrets: () => Promise<{ warningCount: number }>;
}): GatewayRequestHandlers {
  return {
    "secrets.reload": async ({ respond }) => {
      try {
        const result = await params.reloadSecrets();
        respond(true, { ok: true, warningCount: result.warningCount });
      } catch (err) {
        respond(false, undefined, errorShape(ErrorCodes.UNAVAILABLE, String(err)));
      }
    },

    "secrets.status": async ({ respond }) => {
      try {
        const filePath = getSecretsFilePath();
        const exists = await fileExists(filePath);
        const secrets = exists ? await readSecretsFile() : {};
        const keyCount = Object.keys(secrets).length;

        // Check if config has secrets provider configured
        const configPath = resolveUserPath("~/.openclaw/openclaw.json");
        let providerConfigured = false;
        try {
          const raw = await fs.readFile(configPath, "utf-8");
          const config = JSON.parse(raw) as Record<string, unknown>;
          const sec = config.secrets as Record<string, unknown> | undefined;
          const providers = sec?.providers as Record<string, unknown> | undefined;
          providerConfigured = !!providers?.default;
        } catch { /* */ }

        // Count plaintext keys in config
        let plaintextCount = 0;
        try {
          const raw = await fs.readFile(configPath, "utf-8");
          const config = JSON.parse(raw) as Record<string, unknown>;
          plaintextCount = scanPlaintextKeys(config).length;
        } catch { /* */ }

        respond(true, {
          ok: true,
          vaultExists: exists,
          vaultPath: filePath,
          keyCount,
          providerConfigured,
          plaintextCount,
        });
      } catch (err) {
        respond(false, undefined, errorShape(ErrorCodes.UNAVAILABLE, String(err)));
      }
    },

    "secrets.list": async ({ respond }) => {
      try {
        const secrets = await readSecretsFile();
        const keys = Object.entries(secrets).map(([id, value]) => ({
          id,
          masked: maskSecret(typeof value === "string" ? value : ""),
        }));
        respond(true, { ok: true, keys });
      } catch (err) {
        respond(false, undefined, errorShape(ErrorCodes.UNAVAILABLE, String(err)));
      }
    },

    "secrets.write": async ({ params: p, respond }) => {
      try {
        const id = (p as { id?: string })?.id?.trim();
        const value = (p as { value?: string })?.value?.trim();
        const envEntry = (p as { envEntry?: boolean })?.envEntry !== false; // default true
        if (!id || !value) {
          respond(false, undefined, errorShape(ErrorCodes.INVALID_REQUEST, "id and value required"));
          return;
        }

        // 1. Write to secrets file
        const secrets = await readSecretsFile();
        secrets[id] = value;
        await writeSecretsFile(secrets);

        // 2. Update config: ensure provider + optionally add env entry
        let configChanged = false;
        await patchConfig((config) => {
          ensureSecretsProvider(config);

          if (envEntry) {
            const env = config.env as Record<string, unknown> | undefined;
            if (env && id in env) {
              env[id] = makeSecretRef(id);
            } else if (env) {
              env[id] = makeSecretRef(id);
            } else {
              config.env = { [id]: makeSecretRef(id) };
            }
            configChanged = true;
          }
        });

        // Don't auto-reload — let the UI prompt the user to restart
        // so we don't crash mid-session
        respond(true, { ok: true, id, masked: maskSecret(value), restartNeeded: true, configChanged });
      } catch (err) {
        respond(false, undefined, errorShape(ErrorCodes.UNAVAILABLE, String(err)));
      }
    },

    "secrets.delete": async ({ params: p, respond }) => {
      try {
        const id = (p as { id?: string })?.id?.trim();
        if (!id) {
          respond(false, undefined, errorShape(ErrorCodes.INVALID_REQUEST, "id required"));
          return;
        }

        // 1. Remove from secrets file
        const secrets = await readSecretsFile();
        delete secrets[id];
        await writeSecretsFile(secrets);

        // 2. Remove/null the config ref
        await patchConfig((config) => {
          const env = config.env as Record<string, unknown> | undefined;
          if (env && id in env) {
            delete env[id];
          }
        });

        // 3. Reload
        try {
          await params.reloadSecrets();
        } catch { /* non-fatal */ }

        respond(true, { ok: true, id });
      } catch (err) {
        respond(false, undefined, errorShape(ErrorCodes.UNAVAILABLE, String(err)));
      }
    },

    "secrets.migrate": async ({ respond }) => {
      try {
        const configPath = resolveUserPath("~/.openclaw/openclaw.json");
        const raw = await fs.readFile(configPath, "utf-8");
        const config = JSON.parse(raw) as Record<string, unknown>;

        // Find all plaintext keys in env block
        const env = config.env as Record<string, unknown> | undefined;
        if (!env) {
          respond(true, { ok: true, migrated: 0, keys: [] });
          return;
        }

        const migratedKeys: string[] = [];
        const secrets = await readSecretsFile();

        for (const [key, value] of Object.entries(env)) {
          // Skip if already a SecretRef
          if (isSecretRef(value)) continue;
          // Skip if not a string
          if (typeof value !== "string" || !value.trim()) continue;
          // Only migrate things that look like API keys
          if (!isKeyField(key)) continue;

          // Move to secrets file
          secrets[key] = value;
          // Replace with ref in config
          env[key] = makeSecretRef(key);
          migratedKeys.push(key);
        }

        if (migratedKeys.length === 0) {
          respond(true, { ok: true, migrated: 0, keys: [] });
          return;
        }

        // Write secrets file
        await writeSecretsFile(secrets);

        // Ensure provider in config and write back
        ensureSecretsProvider(config);
        await fs.writeFile(configPath, JSON.stringify(config, null, 2) + "\n");

        // Reload
        try {
          await params.reloadSecrets();
        } catch { /* non-fatal */ }

        respond(true, { ok: true, migrated: migratedKeys.length, keys: migratedKeys });
      } catch (err) {
        respond(false, undefined, errorShape(ErrorCodes.UNAVAILABLE, String(err)));
      }
    },

    "secrets.authProfiles.list": async ({ respond }) => {
      try {
        const agentDir = resolveUserPath("~/.openclaw/agents/main/agent");
        const store = loadAuthProfileStore(agentDir) as AuthProfileStore;
        const profiles = Object.entries(store.profiles ?? {}).map(([id, cred]) => {
          const stats = store.usageStats?.[id];
          const lastGoodProvider = Object.entries(store.lastGood ?? {}).find(
            ([, v]) => v === id,
          )?.[0];

          let status: "active" | "error" | "cooldown" | "unused" = "unused";
          if (stats?.cooldownUntil && stats.cooldownUntil > Date.now()) {
            status = "cooldown";
          } else if (stats?.errorCount && stats.errorCount > 0) {
            status = "error";
          } else if (stats?.lastUsed && stats.lastUsed > 0) {
            status = "active";
          }

          const inVault =
            ("keyRef" in cred && isSecretRef(cred.keyRef)) ||
            ("tokenRef" in cred && isSecretRef((cred as any).tokenRef));

          return {
            id,
            type: cred.type,
            provider: cred.provider,
            email: (cred as any).email ?? null,
            inVault,
            hasCredential:
              inVault ||
              !!("key" in cred && (cred as any).key) ||
              !!("token" in cred && (cred as any).token),
            status,
            isLastGood: !!lastGoodProvider,
            lastUsed: stats?.lastUsed ?? null,
            errorCount: stats?.errorCount ?? 0,
            lastFailureAt: stats?.lastFailureAt ?? null,
            cooldownUntil: stats?.cooldownUntil ?? null,
          };
        });

        respond(true, { ok: true, profiles });
      } catch (err) {
        respond(false, undefined, errorShape(ErrorCodes.UNAVAILABLE, String(err)));
      }
    },

    "secrets.authProfiles.resetErrors": async ({ params: p, respond }) => {
      try {
        const profileId = (p as { profileId?: string })?.profileId?.trim();
        if (!profileId) {
          respond(false, undefined, errorShape(ErrorCodes.INVALID_REQUEST, "profileId required"));
          return;
        }
        const agentDir = resolveUserPath("~/.openclaw/agents/main/agent");
        const store = loadAuthProfileStore(agentDir) as AuthProfileStore;
        if (store.usageStats?.[profileId]) {
          store.usageStats[profileId].errorCount = 0;
          store.usageStats[profileId].lastFailureAt = undefined;
          store.usageStats[profileId].cooldownUntil = undefined;
          store.usageStats[profileId].disabledUntil = undefined;
          store.usageStats[profileId].disabledReason = undefined;
          saveAuthProfileStore(agentDir, store);
        }
        respond(true, { ok: true, profileId });
      } catch (err) {
        respond(false, undefined, errorShape(ErrorCodes.UNAVAILABLE, String(err)));
      }
    },

    "secrets.authProfiles.delete": async ({ params: p, respond }) => {
      try {
        const profileId = (p as { profileId?: string })?.profileId?.trim();
        if (!profileId) {
          respond(false, undefined, errorShape(ErrorCodes.INVALID_REQUEST, "profileId required"));
          return;
        }
        const agentDir = resolveUserPath("~/.openclaw/agents/main/agent");
        const store = loadAuthProfileStore(agentDir) as AuthProfileStore;
        delete store.profiles[profileId];
        if (store.usageStats) delete store.usageStats[profileId];
        // Clean from order arrays
        if (store.order) {
          for (const [provider, ids] of Object.entries(store.order)) {
            store.order[provider] = ids.filter((id: string) => id !== profileId);
          }
        }
        // Clean from lastGood
        if (store.lastGood) {
          for (const [provider, id] of Object.entries(store.lastGood)) {
            if (id === profileId) delete store.lastGood[provider];
          }
        }
        saveAuthProfileStore(agentDir, store);
        respond(true, { ok: true, profileId });
      } catch (err) {
        respond(false, undefined, errorShape(ErrorCodes.UNAVAILABLE, String(err)));
      }
    },
  };
}
