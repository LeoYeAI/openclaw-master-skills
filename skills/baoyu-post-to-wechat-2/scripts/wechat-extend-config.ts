import fs from "node:fs";
import path from "node:path";
import os from "node:os";

export interface WechatAccount {
  name: string;
  alias: string;
  default?: boolean;
  default_publish_method?: string;
  default_author?: string;
  need_open_comment?: number;
  only_fans_can_comment?: number;
  app_id?: string;
  app_secret?: string;
  chrome_profile_path?: string;
}

export interface WechatExtendConfig {
  default_theme?: string;
  default_color?: string;
  default_publish_method?: string;
  default_author?: string;
  need_open_comment?: number;
  only_fans_can_comment?: number;
  chrome_profile_path?: string;
  accounts?: WechatAccount[];
}

export interface ResolvedAccount {
  name?: string;
  alias?: string;
  default_publish_method?: string;
  default_author?: string;
  need_open_comment: number;
  only_fans_can_comment: number;
  app_id?: string;
  app_secret?: string;
  chrome_profile_path?: string;
}

function stripQuotes(s: string): string {
  return s.replace(/^['"]|['"]$/g, "");
}

function toBool01(v: string): number {
  return v === "1" || v === "true" ? 1 : 0;
}

function parseWechatExtend(content: string): WechatExtendConfig {
  const config: WechatExtendConfig = {};
  const lines = content.split("\n");
  let inAccounts = false;
  let current: Record<string, string> | null = null;
  const rawAccounts: Record<string, string>[] = [];

  for (const raw of lines) {
    const trimmed = raw.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;

    if (trimmed === "accounts:") {
      inAccounts = true;
      continue;
    }

    if (inAccounts) {
      const listMatch = raw.match(/^\s+-\s+(.+)$/);
      if (listMatch) {
        if (current) rawAccounts.push(current);
        current = {};
        const kv = listMatch[1]!;
        const ci = kv.indexOf(":");
        if (ci > 0) {
          current[kv.slice(0, ci).trim()] = stripQuotes(kv.slice(ci + 1).trim());
        }
        continue;
      }

      if (current && /^\s{2,}/.test(raw) && !trimmed.startsWith("-")) {
        const ci = trimmed.indexOf(":");
        if (ci > 0) {
          current[trimmed.slice(0, ci).trim()] = stripQuotes(trimmed.slice(ci + 1).trim());
        }
        continue;
      }

      if (!/^\s/.test(raw)) {
        if (current) rawAccounts.push(current);
        current = null;
        inAccounts = false;
      } else {
        continue;
      }
    }

    const ci = trimmed.indexOf(":");
    if (ci < 0) continue;
    const key = trimmed.slice(0, ci).trim();
    const val = stripQuotes(trimmed.slice(ci + 1).trim());
    if (val === "null" || val === "") continue;

    switch (key) {
      case "default_theme": config.default_theme = val; break;
      case "default_color": config.default_color = val; break;
      case "default_publish_method": config.default_publish_method = val; break;
      case "default_author": config.default_author = val; break;
      case "need_open_comment": config.need_open_comment = toBool01(val); break;
      case "only_fans_can_comment": config.only_fans_can_comment = toBool01(val); break;
      case "chrome_profile_path": config.chrome_profile_path = val; break;
    }
  }

  if (current) rawAccounts.push(current);

  if (rawAccounts.length > 0) {
    config.accounts = rawAccounts.map(a => ({
      name: a.name || "",
      alias: a.alias || "",
      default: a.default === "true" || a.default === "1",
      default_publish_method: a.default_publish_method || undefined,
      default_author: a.default_author || undefined,
      need_open_comment: a.need_open_comment ? toBool01(a.need_open_comment) : undefined,
      only_fans_can_comment: a.only_fans_can_comment ? toBool01(a.only_fans_can_comment) : undefined,
      app_id: a.app_id || undefined,
      app_secret: a.app_secret || undefined,
      chrome_profile_path: a.chrome_profile_path || undefined,
    }));
  }

  return config;
}

export function loadWechatExtendConfig(): WechatExtendConfig {
  const paths = [
    path.join(process.cwd(), ".baoyu-skills", "baoyu-post-to-wechat", "EXTEND.md"),
    path.join(
      process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config"),
      "baoyu-skills", "baoyu-post-to-wechat", "EXTEND.md"
    ),
    path.join(os.homedir(), ".baoyu-skills", "baoyu-post-to-wechat", "EXTEND.md"),
  ];
  for (const p of paths) {
    try {
      const content = fs.readFileSync(p, "utf-8");
      return parseWechatExtend(content);
    } catch {
      continue;
    }
  }
  return {};
}

function selectAccount(config: WechatExtendConfig, alias?: string): WechatAccount | undefined {
  if (!config.accounts || config.accounts.length === 0) return undefined;
  if (alias) return config.accounts.find(a => a.alias === alias);
  if (config.accounts.length === 1) return config.accounts[0];
  return config.accounts.find(a => a.default);
}

export function resolveAccount(config: WechatExtendConfig, alias?: string): ResolvedAccount {
  const acct = selectAccount(config, alias);
  return {
    name: acct?.name,
    alias: acct?.alias,
    default_publish_method: acct?.default_publish_method ?? config.default_publish_method,
    default_author: acct?.default_author ?? config.default_author,
    need_open_comment: acct?.need_open_comment ?? config.need_open_comment ?? 1,
    only_fans_can_comment: acct?.only_fans_can_comment ?? config.only_fans_can_comment ?? 0,
    app_id: acct?.app_id,
    app_secret: acct?.app_secret,
    chrome_profile_path: acct?.chrome_profile_path ?? config.chrome_profile_path,
  };
}

function loadEnvFile(envPath: string): Record<string, string> {
  const env: Record<string, string> = {};
  if (!fs.existsSync(envPath)) return env;
  const content = fs.readFileSync(envPath, "utf-8");
  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx > 0) {
      const key = trimmed.slice(0, eqIdx).trim();
      let value = trimmed.slice(eqIdx + 1).trim();
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      env[key] = value;
    }
  }
  return env;
}

function aliasToEnvKey(alias: string): string {
  return alias.toUpperCase().replace(/-/g, "_");
}

export function loadCredentials(account?: ResolvedAccount): { appId: string; appSecret: string } {
  if (account?.app_id && account?.app_secret) {
    return { appId: account.app_id, appSecret: account.app_secret };
  }

  const cwdEnvPath = path.join(process.cwd(), ".baoyu-skills", ".env");
  const homeEnvPath = path.join(os.homedir(), ".baoyu-skills", ".env");
  const cwdEnv = loadEnvFile(cwdEnvPath);
  const homeEnv = loadEnvFile(homeEnvPath);

  const prefix = account?.alias ? `WECHAT_${aliasToEnvKey(account.alias)}_` : "";

  let appId = "";
  let appSecret = "";

  if (prefix) {
    appId = process.env[`${prefix}APP_ID`]
      || cwdEnv[`${prefix}APP_ID`]
      || homeEnv[`${prefix}APP_ID`]
      || "";
    appSecret = process.env[`${prefix}APP_SECRET`]
      || cwdEnv[`${prefix}APP_SECRET`]
      || homeEnv[`${prefix}APP_SECRET`]
      || "";
  }

  if (!appId) {
    appId = process.env.WECHAT_APP_ID || cwdEnv.WECHAT_APP_ID || homeEnv.WECHAT_APP_ID || "";
  }
  if (!appSecret) {
    appSecret = process.env.WECHAT_APP_SECRET || cwdEnv.WECHAT_APP_SECRET || homeEnv.WECHAT_APP_SECRET || "";
  }

  if (!appId || !appSecret) {
    const hint = account?.alias ? ` (account: ${account.alias})` : "";
    throw new Error(
      `Missing WECHAT_APP_ID or WECHAT_APP_SECRET${hint}.\n` +
      "Set via EXTEND.md account config, environment variables, or .baoyu-skills/.env file."
    );
  }

  return { appId, appSecret };
}

export function listAccounts(config: WechatExtendConfig): string[] {
  return (config.accounts || []).map(a => a.alias);
}
