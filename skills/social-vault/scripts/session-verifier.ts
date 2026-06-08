/**
 * SocialVault 登录态验证模块
 *
 * 独立处理网络请求验证。与 health-check.ts 分离以确保
 * 文件 I/O 和网络请求不在同一模块中混合。
 *
 * 安全机制：
 * - 内置域名白名单，仅允许向已知的官方社交平台域名发送请求
 * - 拒绝向白名单外的任何端点发送认证头或 Cookie
 * - 白名单不可通过适配器文件修改
 */

import type { AccountStatus, VaultEntry } from "./types.js";

/**
 * 受信任的社交平台官方域名白名单。
 * 仅这些域名允许接收认证头。
 * 新增平台时需在此处显式添加域名。
 */
const TRUSTED_DOMAINS: readonly string[] = [
  "xiaohongshu.com",
  "www.xiaohongshu.com",
  "edith.xiaohongshu.com",
  "bilibili.com",
  "www.bilibili.com",
  "api.bilibili.com",
  "space.bilibili.com",
  "passport.bilibili.com",
  "weibo.com",
  "www.weibo.com",
  "api.weibo.com",
  "douyin.com",
  "www.douyin.com",
  "zhihu.com",
  "www.zhihu.com",
  "tieba.baidu.com",
  "baidu.com",
  "www.baidu.com",
];

/**
 * 校验端点 URL 的域名是否在受信任白名单中。
 * @param endpoint - 要验证的端点 URL
 * @returns 校验结果
 */
export function validateEndpointDomain(endpoint: string): { trusted: boolean; domain: string } {
  let url: URL;
  try {
    url = new URL(endpoint);
  } catch {
    return { trusted: false, domain: endpoint };
  }

  const hostname = url.hostname.toLowerCase();
  const trusted = TRUSTED_DOMAINS.some((d) => hostname === d || hostname.endsWith(`.${d}`));
  return { trusted, domain: hostname };
}

/**
 * 通过 API 方式验证账号登录态。
 * 使用凭证中的 access_token 或 cookies 发起 HTTP 请求到平台验证端点。
 *
 * 安全约束：仅向 TRUSTED_DOMAINS 白名单中的域名发送认证头。
 * 如果端点不在白名单中，拒绝请求并返回错误。
 *
 * @param endpoint - 验证端点 URL（来自适配器 session_check 配置）
 * @param successIndicator - 成功判定关键字
 * @param credential - 凭证条目（仅提取认证头，不传输完整凭证）
 * @returns 验证结果状态和消息
 */
export async function verifyViaApi(
  endpoint: string,
  successIndicator: string,
  credential: VaultEntry
): Promise<{ status: AccountStatus; message: string }> {
  const domainCheck = validateEndpointDomain(endpoint);
  if (!domainCheck.trusted) {
    return {
      status: "unknown",
      message: `安全拒绝：端点域名 "${domainCheck.domain}" 不在受信任白名单中。请检查适配器的 session_check 配置。`,
    };
  }

  try {
    const headers: Record<string, string> = {
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9",
      "Accept-Encoding": "gzip, deflate, br",
      "Cache-Control": "max-age=0",
      "Sec-Fetch-Dest": "document",
      "Sec-Fetch-Mode": "navigate",
      "Sec-Fetch-Site": "none",
      "Sec-Fetch-User": "?1",
      "Upgrade-Insecure-Requests": "1",
      "Sec-Ch-Ua": "\"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
      "Sec-Ch-Ua-Mobile": "?0",
      "Sec-Ch-Ua-Platform": "\"Windows\"",
    };

    if (credential.authMethod === "api_token" && credential.accessToken) {
      headers["Authorization"] = `Bearer ${credential.accessToken}`;
      headers["User-Agent"] = "SocialVault/0.1.0";
    } else if (credential.cookies || credential.rawCookieHeader) {
      const cookieHeader = credential.rawCookieHeader
        || credential.cookies!.map((c) => `${c.name}=${c.value}`).join("; ");
      headers["Cookie"] = cookieHeader;
      headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";
    } else {
      return { status: "expired", message: "凭证信息不完整，无法验证。" };
    }

    const response = await fetch(endpoint, { headers, redirect: "follow" });

    if (!response.ok) {
      const errBody = await response.text().catch(() => "");
      const bodyHint = errBody.slice(0, 200);
      if (response.status === 401 || response.status === 403) {
        return { status: "expired", message: `验证失败：HTTP ${response.status}，登录态已失效。${bodyHint ? ` 响应: ${bodyHint}` : ""}` };
      }
      return { status: "degraded", message: `验证异常：HTTP ${response.status}。${bodyHint ? ` 响应: ${bodyHint}` : ""}` };
    }

    const body = await response.text();
    if (body.includes(successIndicator)) {
      return { status: "healthy", message: "登录态有效。" };
    }

    return { status: "degraded", message: `验证响应中未包含预期标志 "${successIndicator}"。` };
  } catch (err) {
    return { status: "unknown", message: `验证请求失败: ${(err as Error).message}` };
  }
}
