/**
 * SocialVault 健康检查模块
 *
 * 遍历所有非 expired 账号，加载适配器配置、更新状态。
 * 失效账号推送告警，临近过期账号推送预警。
 *
 * 本模块仅处理本地文件 I/O（accounts.json、适配器文件）。
 * 不导入任何网络请求模块。网络验证通过 verifier 回调注入，
 * 由调用方（CLI 入口或 Agent）负责提供。
 *
 * 通过 OpenClaw Cron 每 6 小时调用: npx tsx scripts/health-check.ts [vault-dir]
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";
import type { AccountsStore, AccountMeta, HealthCheckResult, AccountStatus, VaultEntry } from "./types.js";
import { getCredentials, clearCredentials } from "./vault-crypto.js";

const DEFAULT_WARN_DAYS = 3;

/** API 验证器函数签名，由调用方注入 */
export type ApiVerifier = (
  endpoint: string,
  successIndicator: string,
  credential: VaultEntry
) => Promise<{ status: AccountStatus; message: string }>;

/**
 * 读取 accounts.json。
 * @param vaultDir - vault 数据目录
 * @returns 账号存储对象
 * @throws 文件不存在或格式错误时抛出异常
 */
export function loadAccounts(vaultDir: string): AccountsStore {
  const filePath = join(vaultDir, "accounts.json");
  if (!existsSync(filePath)) {
    return { accounts: [] };
  }
  try {
    const content = readFileSync(filePath, "utf-8");
    return JSON.parse(content) as AccountsStore;
  } catch {
    throw new Error("accounts.json 文件格式错误或读取失败。");
  }
}

/**
 * 保存 accounts.json。
 * @param vaultDir - vault 数据目录
 * @param store - 账号存储对象
 */
export function saveAccounts(vaultDir: string, store: AccountsStore): void {
  const filePath = join(vaultDir, "accounts.json");
  try {
    writeFileSync(filePath, JSON.stringify(store, null, 2), "utf-8");
  } catch (err) {
    throw new Error(`accounts.json 保存失败: ${(err as Error).message}`);
  }
}

/**
 * 添加或更新一个账号的元数据。
 * @param vaultDir - vault 数据目录
 * @param account - 账号元数据
 */
export function upsertAccount(vaultDir: string, account: AccountMeta): void {
  const store = loadAccounts(vaultDir);
  const idx = store.accounts.findIndex((a) => a.id === account.id);
  if (idx >= 0) {
    store.accounts[idx] = account;
  } else {
    store.accounts.push(account);
  }
  saveAccounts(vaultDir, store);
}

/**
 * 从 accounts.json 删除指定账号。
 * @param vaultDir - vault 数据目录
 * @param accountId - 账号 ID
 * @returns 是否成功删除
 */
export function removeAccount(vaultDir: string, accountId: string): boolean {
  const store = loadAccounts(vaultDir);
  const prevLen = store.accounts.length;
  store.accounts = store.accounts.filter((a) => a.id !== accountId);
  if (store.accounts.length < prevLen) {
    saveAccounts(vaultDir, store);
    return true;
  }
  return false;
}

/**
 * 读取适配器文件的 frontmatter 中的 session_check 配置。
 * 如果账号使用 cookie_paste 认证且适配器定义了 session_check_cookie，
 * 优先使用 cookie 专用的检查配置。
 * @param adapterPath - 适配器文件路径（相对于 skill 根目录）
 * @param skillDir - skill 根目录
 * @param authMethod - 账号的认证方式，用于选择合适的检查配置
 * @returns session_check 配置
 */
export function loadAdapterSessionCheck(
  adapterPath: string,
  skillDir: string,
  authMethod?: string
): { method: string; endpoint: string; successIndicator: string } {
  const fullPath = join(skillDir, adapterPath);
  if (!existsSync(fullPath)) {
    throw new Error(`适配器文件不存在: ${adapterPath}`);
  }

  const content = readFileSync(fullPath, "utf-8");
  const fmMatch = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!fmMatch) {
    throw new Error(`适配器文件 ${adapterPath} 缺少 YAML frontmatter。`);
  }

  const fm = fmMatch[1];

  if (authMethod === "cookie_paste") {
    const cookieSection = fm.match(/session_check_cookie:\s*\n((?:\s+\S.*\n)*)/);
    if (cookieSection) {
      const section = cookieSection[1];
      const m = section.match(/method:\s*["']?(\w+)["']?/);
      const e = section.match(/endpoint:\s*["']?([^"'\n]+)["']?/);
      const s = section.match(/success_indicator:\s*["']?([^"'\n]+)["']?/);
      if (m && e && s) {
        return {
          method: m[1],
          endpoint: e[1].trim(),
          successIndicator: s[1].trim(),
        };
      }
    }
  }

  const sessionSection = fm.match(/session_check:\s*\n((?:\s+\S.*\n)*)/);
  if (sessionSection) {
    const section = sessionSection[1];
    const m = section.match(/method:\s*["']?(\w+)["']?/);
    const e = section.match(/endpoint:\s*["']?([^"'\n]+)["']?/);
    const s = section.match(/success_indicator:\s*["']?([^"'\n]+)["']?/);
    if (m && e && s) {
      return {
        method: m[1],
        endpoint: e[1].trim(),
        successIndicator: s[1].trim(),
      };
    }
  }

  const methodMatch = fm.match(/method:\s*["']?(\w+)["']?/);
  const endpointMatch = fm.match(/endpoint:\s*["']?([^"'\n]+)["']?/);
  const indicatorMatch = fm.match(/success_indicator:\s*["']?([^"'\n]+)["']?/);

  if (!methodMatch || !endpointMatch || !indicatorMatch) {
    throw new Error(`适配器文件 ${adapterPath} 的 session_check 配置不完整。`);
  }

  return {
    method: methodMatch[1],
    endpoint: endpointMatch[1].trim(),
    successIndicator: indicatorMatch[1].trim(),
  };
}

/**
 * 检查账号是否临近过期并生成预警。
 * @param account - 账号元数据
 * @param warnDays - 提前预警天数
 * @returns 是否需要预警
 */
export function isNearingExpiry(account: AccountMeta, warnDays: number = DEFAULT_WARN_DAYS): boolean {
  if (!account.estimatedExpiry) return false;

  const expiryDate = new Date(account.estimatedExpiry);
  const now = new Date();
  const daysLeft = (expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);

  return daysLeft > 0 && daysLeft <= warnDays;
}

/**
 * 计算距过期还剩多少天。
 * @param estimatedExpiry - ISO 8601 过期时间
 * @returns 剩余天数（负数表示已过期）
 */
export function daysUntilExpiry(estimatedExpiry: string): number {
  const expiry = new Date(estimatedExpiry);
  const now = new Date();
  return Math.round((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

/**
 * 对所有非 expired 账号执行健康检查。
 * 网络验证通过 apiVerifier 回调注入，本函数不直接发起任何网络请求。
 * @param vaultDir - vault 数据目录
 * @param skillDir - skill 根目录（用于定位适配器文件）
 * @param apiVerifier - API 验证回调（由调用方从 session-verifier.ts 注入）
 * @returns 所有检查结果
 */
export async function runHealthCheck(
  vaultDir: string,
  skillDir: string,
  apiVerifier?: ApiVerifier
): Promise<HealthCheckResult[]> {
  const store = loadAccounts(vaultDir);
  const results: HealthCheckResult[] = [];
  const now = new Date().toISOString();

  for (const account of store.accounts) {
    if (account.status === "expired") {
      continue;
    }

    const result: HealthCheckResult = {
      accountId: account.id,
      platform: account.platform,
      previousStatus: account.status,
      currentStatus: "unknown",
      displayName: account.displayName,
      checkedAt: now,
    };

    try {
      if (!account.adapter) {
        result.currentStatus = "unknown";
        result.message = "账号未关联适配器文件，无法执行验证。";
        results.push(result);
        continue;
      }

      const sessionCheck = loadAdapterSessionCheck(account.adapter, skillDir, account.authMethod);
      const credential = getCredentials(vaultDir, account.id);

      if (!credential) {
        result.currentStatus = "expired";
        result.message = "未找到凭证数据。";
      } else if (sessionCheck.method === "api" && apiVerifier) {
        const verification = await apiVerifier(
          sessionCheck.endpoint,
          sessionCheck.successIndicator,
          credential
        );
        result.currentStatus = verification.status;
        result.message = verification.message;

        clearCredentials(credential);
      } else if (sessionCheck.method === "api" && !apiVerifier) {
        result.currentStatus = account.status;
        result.message = "API 验证器未注入，保持当前状态。";
      } else {
        result.currentStatus = account.status;
        result.message = "Browser 验证方式需通过 Agent 执行，跳过自动检查。";
      }
    } catch (err) {
      result.currentStatus = "unknown";
      result.message = `检查异常: ${(err as Error).message}`;
    }

    account.status = result.currentStatus;
    account.lastValidatedAt = now;

    if (account.status === "healthy" && isNearingExpiry(account)) {
      const days = daysUntilExpiry(account.estimatedExpiry!);
      result.message = `登录态有效，但预计 ${days} 天后过期，建议尽快更新。`;
    }

    results.push(result);
  }

  saveAccounts(vaultDir, store);
  return results;
}

/**
 * 格式化健康检查结果为可读报告。
 * @param results - 检查结果数组
 * @returns 格式化的报告文本
 */
export function formatReport(results: HealthCheckResult[]): string {
  if (results.length === 0) {
    return "没有需要检查的账号。";
  }

  const statusIcons: Record<AccountStatus, string> = {
    healthy: "✅",
    degraded: "⚠️",
    expired: "❌",
    unknown: "❓",
  };

  const lines = ["[SocialVault] 账号健康检查报告", `检查时间: ${new Date().toLocaleString()}`, ""];

  const expired = results.filter((r) => r.currentStatus === "expired");
  const degraded = results.filter((r) => r.currentStatus === "degraded");
  const healthy = results.filter((r) => r.currentStatus === "healthy");
  const unknown = results.filter((r) => r.currentStatus === "unknown");

  if (expired.length > 0) {
    lines.push("🚨 失效账号:");
    for (const r of expired) {
      lines.push(`  ${statusIcons.expired} ${r.displayName} (${r.platform}) - ${r.message || "已失效"}`);
    }
    lines.push("");
  }

  if (degraded.length > 0) {
    lines.push("⚠️ 异常账号:");
    for (const r of degraded) {
      lines.push(`  ${statusIcons.degraded} ${r.displayName} (${r.platform}) - ${r.message || "状态异常"}`);
    }
    lines.push("");
  }

  if (healthy.length > 0) {
    lines.push("✅ 正常账号:");
    for (const r of healthy) {
      lines.push(`  ${statusIcons.healthy} ${r.displayName} (${r.platform})${r.message ? " - " + r.message : ""}`);
    }
    lines.push("");
  }

  if (unknown.length > 0) {
    lines.push("❓ 未知状态:");
    for (const r of unknown) {
      lines.push(`  ${statusIcons.unknown} ${r.displayName} (${r.platform}) - ${r.message || "无法确认"}`);
    }
    lines.push("");
  }

  lines.push(`总计: ${results.length} 个账号 | ✅ ${healthy.length} | ⚠️ ${degraded.length} | ❌ ${expired.length} | ❓ ${unknown.length}`);

  return lines.join("\n");
}
