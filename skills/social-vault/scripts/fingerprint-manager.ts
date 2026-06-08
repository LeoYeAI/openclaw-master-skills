/**
 * SocialVault 浏览器指纹管理模块
 *
 * 采集、存储、恢复浏览器指纹。首次导入账号时记录关联的浏览器环境参数，
 * 每次使用该账号操作时自动配置 OpenClaw browser profile 以匹配首次环境。
 *
 * 运行：npx tsx scripts/fingerprint-manager.ts <command> [args]
 */

import { readFileSync, writeFileSync, existsSync, unlinkSync } from "node:fs";
import { join } from "node:path";
import type { BrowserFingerprint } from "./types.js";

/** 默认指纹值，模拟常见的 Windows Chrome 环境 */
const DEFAULT_FINGERPRINT: BrowserFingerprint = {
  userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
  viewport: { width: 1920, height: 1080 },
  locale: "en-US",
  timezone: "America/New_York",
  platform: "Win32",
  deviceScaleFactor: 1,
  colorScheme: "light",
  capturedAt: new Date().toISOString(),
  capturedFrom: "cookie_paste_infer",
};

/**
 * 从 Cookie-Editor JSON 数据中推断浏览器指纹。
 * Cookie-Editor 导出的 JSON 不直接包含指纹信息，但可以从 Cookie 域名推断地域设置。
 * @param cookies - Cookie-Editor 导出的 JSON 数组
 * @param userAgent - 可选的 User-Agent 字符串
 * @returns 推断的浏览器指纹
 */
export function inferFromCookies(
  cookies: Array<{ name: string; value: string; domain: string }>,
  userAgent?: string
): BrowserFingerprint {
  const fingerprint: BrowserFingerprint = {
    ...DEFAULT_FINGERPRINT,
    capturedAt: new Date().toISOString(),
    capturedFrom: "cookie_paste_infer",
  };

  if (userAgent) {
    fingerprint.userAgent = userAgent;
  }

  // 从 Cookie 域名推断区域设置
  const domains = cookies.map((c) => c.domain.toLowerCase());
  const hasCNDomain = domains.some((d) =>
    d.includes(".cn") || d.includes("xiaohongshu") || d.includes("weibo") || d.includes("bilibili")
  );
  const hasJPDomain = domains.some((d) => d.includes(".jp") || d.includes(".co.jp"));

  if (hasCNDomain) {
    fingerprint.locale = "zh-CN";
    fingerprint.timezone = "Asia/Shanghai";
  } else if (hasJPDomain) {
    fingerprint.locale = "ja-JP";
    fingerprint.timezone = "Asia/Tokyo";
  }

  return fingerprint;
}

/**
 * 创建手动指定的浏览器指纹。
 * @param params - 用户指定的指纹参数（部分字段可选，使用默认值填充）
 * @returns 完整的浏览器指纹
 */
export function createFingerprint(params: Partial<BrowserFingerprint>): BrowserFingerprint {
  return {
    ...DEFAULT_FINGERPRINT,
    ...params,
    capturedAt: new Date().toISOString(),
    capturedFrom: params.capturedFrom ?? "manual",
  };
}

/**
 * 将指纹保存到文件。
 * @param vaultDir - vault 数据目录
 * @param accountId - 关联的账号 ID
 * @param fingerprint - 浏览器指纹
 * @returns 指纹文件名
 */
export function saveFingerprint(
  vaultDir: string,
  accountId: string,
  fingerprint: BrowserFingerprint
): string {
  const fileName = `${accountId}.json`;
  const filePath = join(vaultDir, "fingerprints", fileName);
  try {
    writeFileSync(filePath, JSON.stringify(fingerprint, null, 2), "utf-8");
  } catch (err) {
    throw new Error(`指纹文件保存失败: ${(err as Error).message}`);
  }
  return fileName;
}

/**
 * 加载指定账号的指纹。
 * @param vaultDir - vault 数据目录
 * @param accountId - 账号 ID
 * @returns 浏览器指纹，文件不存在时返回 null
 */
export function loadFingerprint(
  vaultDir: string,
  accountId: string
): BrowserFingerprint | null {
  const filePath = join(vaultDir, "fingerprints", `${accountId}.json`);
  if (!existsSync(filePath)) {
    return null;
  }
  try {
    const content = readFileSync(filePath, "utf-8");
    return JSON.parse(content) as BrowserFingerprint;
  } catch {
    return null;
  }
}

/**
 * 删除指定账号的指纹文件。
 * @param vaultDir - vault 数据目录
 * @param accountId - 账号 ID
 * @returns 是否成功删除
 */
export function deleteFingerprint(vaultDir: string, accountId: string): boolean {
  const filePath = join(vaultDir, "fingerprints", `${accountId}.json`);
  if (!existsSync(filePath)) {
    return false;
  }
  try {
    unlinkSync(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * 生成 OpenClaw browser profile 配置命令序列。
 * Agent 在 SKILL.md 中使用这些命令配置 browser 工具的设备参数。
 * @param fingerprint - 浏览器指纹
 * @param profileName - browser profile 名称
 * @returns 配置命令数组
 */
export function generateBrowserCommands(
  fingerprint: BrowserFingerprint,
  profileName: string
): string[] {
  return [
    `browser set profile "${profileName}"`,
    `browser set user-agent "${fingerprint.userAgent}"`,
    `browser set viewport ${fingerprint.viewport.width} ${fingerprint.viewport.height}`,
    `browser set locale "${fingerprint.locale}"`,
    `browser set timezone "${fingerprint.timezone}"`,
    `browser set device-scale-factor ${fingerprint.deviceScaleFactor}`,
    ...(fingerprint.colorScheme ? [`browser set color-scheme "${fingerprint.colorScheme}"`] : []),
  ];
}

// CLI 入口
if (process.argv[1]?.replace(/\\/g, "/").endsWith("scripts/fingerprint-manager.ts")) {
  const command = process.argv[2];
  const vaultDir = process.argv[3] || join(process.cwd(), "vault");
  const accountId = process.argv[4] || "";

  switch (command) {
    case "load": {
      if (!accountId) {
        console.error("用法: npx tsx scripts/fingerprint-manager.ts load <vault-dir> <account-id>");
        process.exit(1);
      }
      const fp = loadFingerprint(vaultDir, accountId);
      if (fp) {
        console.log(JSON.stringify(fp, null, 2));
      } else {
        console.log(`未找到账号 ${accountId} 的指纹文件。`);
      }
      break;
    }
    case "commands": {
      if (!accountId) {
        console.error("用法: npx tsx scripts/fingerprint-manager.ts commands <vault-dir> <account-id>");
        process.exit(1);
      }
      const fp = loadFingerprint(vaultDir, accountId);
      if (fp) {
        const commands = generateBrowserCommands(fp, `sv-${accountId}`);
        for (const cmd of commands) {
          console.log(cmd);
        }
      } else {
        console.log(`未找到账号 ${accountId} 的指纹文件。`);
      }
      break;
    }
    default:
      console.log("用法: npx tsx scripts/fingerprint-manager.ts <load|commands> <vault-dir> <account-id>");
  }
}
