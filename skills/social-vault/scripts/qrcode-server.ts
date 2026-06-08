/**
 * SocialVault 扫码登录中转服务
 *
 * 在 VPS 上通过 headless browser 打开平台登录页，生成二维码，
 * 在 Agent 对话中直接展示给用户扫码，完成登录后自动捕获 Cookie。
 *
 * 此模块提供扫码流程的数据管理和状态追踪。
 * 实际的 browser 操作由 Agent 通过 OpenClaw 内置 browser 工具执行，无需额外凭证。
 *
 * 运行：npx tsx scripts/qrcode-server.ts <command> [args]
 */

import { randomBytes } from "node:crypto";
import { writeFileSync, readFileSync, existsSync, unlinkSync } from "node:fs";
import { join } from "node:path";

/** 扫码会话状态 */
export type QRSessionStatus = "pending" | "scanned" | "confirmed" | "expired" | "failed";

/**
 * 扫码会话。
 * 注意：捕获的 Cookie 不存储在会话文件中，而是由 Agent 在扫码成功后
 * 直接通过 vault-crypto 加密存储到 vault.enc，确保凭证不以明文形式落盘。
 */
export interface QRSession {
  sessionId: string;
  token: string;
  platform: string;
  accountId?: string;
  status: QRSessionStatus;
  loginUrl: string;
  createdAt: string;
  expiresAt: string;
  qrImagePath?: string;
}

const SESSION_EXPIRY_MS = 5 * 60 * 1000; // 5 分钟

/**
 * 创建一个新的扫码登录会话。
 * @param platform - 平台标识
 * @param loginUrl - 平台登录页 URL
 * @param vaultDir - vault 数据目录
 * @returns 新创建的 QR 会话
 */
export function createSession(
  platform: string,
  loginUrl: string,
  vaultDir: string
): QRSession {
  const sessionId = randomBytes(16).toString("hex");
  const token = randomBytes(32).toString("hex");
  const now = new Date();
  const expiresAt = new Date(now.getTime() + SESSION_EXPIRY_MS);

  const session: QRSession = {
    sessionId,
    token,
    platform,
    status: "pending",
    loginUrl,
    createdAt: now.toISOString(),
    expiresAt: expiresAt.toISOString(),
  };

  const filePath = join(vaultDir, `qr-session-${sessionId}.json`);
  try {
    writeFileSync(filePath, JSON.stringify(session, null, 2), "utf-8");
  } catch (err) {
    throw new Error(`扫码会话创建失败: ${(err as Error).message}`);
  }

  return session;
}

/**
 * 加载扫码会话。
 * @param sessionId - 会话 ID
 * @param vaultDir - vault 数据目录
 * @returns 会话对象，不存在时返回 null
 */
export function loadSession(sessionId: string, vaultDir: string): QRSession | null {
  const filePath = join(vaultDir, `qr-session-${sessionId}.json`);
  if (!existsSync(filePath)) {
    return null;
  }
  try {
    const content = readFileSync(filePath, "utf-8");
    return JSON.parse(content) as QRSession;
  } catch {
    return null;
  }
}

/**
 * 更新扫码会话状态。
 * @param sessionId - 会话 ID
 * @param vaultDir - vault 数据目录
 * @param updates - 要更新的字段
 * @returns 更新后的会话，不存在时返回 null
 */
export function updateSession(
  sessionId: string,
  vaultDir: string,
  updates: Partial<QRSession>
): QRSession | null {
  const session = loadSession(sessionId, vaultDir);
  if (!session) return null;

  Object.assign(session, updates);

  const filePath = join(vaultDir, `qr-session-${sessionId}.json`);
  try {
    writeFileSync(filePath, JSON.stringify(session, null, 2), "utf-8");
  } catch (err) {
    throw new Error(`扫码会话更新失败: ${(err as Error).message}`);
  }

  return session;
}

/**
 * 验证一次性 token。
 * @param sessionId - 会话 ID
 * @param token - 一次性 token
 * @param vaultDir - vault 数据目录
 * @returns 验证结果
 */
export function validateToken(
  sessionId: string,
  token: string,
  vaultDir: string
): { valid: boolean; reason?: string } {
  const session = loadSession(sessionId, vaultDir);
  if (!session) {
    return { valid: false, reason: "会话不存在。" };
  }

  if (session.token !== token) {
    return { valid: false, reason: "Token 无效。" };
  }

  if (new Date() > new Date(session.expiresAt)) {
    updateSession(sessionId, vaultDir, { status: "expired" });
    return { valid: false, reason: "会话已过期。" };
  }

  if (session.status === "confirmed") {
    return { valid: false, reason: "Token 已使用。" };
  }

  return { valid: true };
}

/**
 * 检查会话是否已过期。
 * @param session - QR 会话
 * @returns 是否已过期
 */
export function isSessionExpired(session: QRSession): boolean {
  return new Date() > new Date(session.expiresAt);
}

/**
 * 清理已完成或过期的扫码会话文件。
 * @param sessionId - 会话 ID
 * @param vaultDir - vault 数据目录
 */
export function cleanupSession(sessionId: string, vaultDir: string): void {
  const sessionFile = join(vaultDir, `qr-session-${sessionId}.json`);
  if (existsSync(sessionFile)) {
    try {
      unlinkSync(sessionFile);
    } catch {
      // 忽略删除失败
    }
  }
}

/**
 * 获取平台的登录页 URL。
 * @param platform - 平台标识
 * @returns 登录页 URL
 */
export function getLoginUrl(platform: string): string {
  const urls: Record<string, string> = {
    xiaohongshu: "https://www.xiaohongshu.com",
    weibo: "https://weibo.com/login.php",
    bilibili: "https://passport.bilibili.com/login",
    douyin: "https://www.douyin.com",
    zhihu: "https://www.zhihu.com/signin",
  };

  return urls[platform] || `https://${platform}.com/login`;
}

// CLI 入口
if (process.argv[1]?.replace(/\\/g, "/").endsWith("scripts/qrcode-server.ts")) {
  const command = process.argv[2];
  const vaultDir = process.argv[3] || join(process.cwd(), "vault");

  switch (command) {
    case "create": {
      const platform = process.argv[4];
      if (!platform) {
        console.error("用法: npx tsx scripts/qrcode-server.ts create <vault-dir> <platform>");
        process.exit(1);
      }
      const loginUrl = getLoginUrl(platform);
      const session = createSession(platform, loginUrl, vaultDir);
      console.log(JSON.stringify({
        sessionId: session.sessionId,
        tokenPresent: true,
        loginUrl: session.loginUrl,
        expiresAt: session.expiresAt,
      }, null, 2));
      break;
    }
    case "status": {
      const sessionId = process.argv[4];
      if (!sessionId) {
        console.error("用法: npx tsx scripts/qrcode-server.ts status <vault-dir> <session-id>");
        process.exit(1);
      }
      const session = loadSession(sessionId, vaultDir);
      if (session) {
        const expired = isSessionExpired(session);
        console.log(JSON.stringify({
          status: expired ? "expired" : session.status,
          platform: session.platform,
          expiresAt: session.expiresAt,
        }, null, 2));
      } else {
        console.log("会话不存在。");
      }
      break;
    }
    case "cleanup": {
      const sessionId = process.argv[4];
      if (!sessionId) {
        console.error("用法: npx tsx scripts/qrcode-server.ts cleanup <vault-dir> <session-id>");
        process.exit(1);
      }
      cleanupSession(sessionId, vaultDir);
      console.log("会话已清理。");
      break;
    }
    default:
      console.log("用法: npx tsx scripts/qrcode-server.ts <create|status|cleanup> <vault-dir> [args]");
  }
}
