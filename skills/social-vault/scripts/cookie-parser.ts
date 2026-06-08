/**
 * SocialVault Cookie 解析模块
 *
 * 支持三种 Cookie 输入格式的自动识别和解析：
 * 1. JSON 数组格式（Cookie-Editor 导出）
 * 2. Raw header 格式（key=value; key2=value2）
 * 3. Netscape/curl 格式（制表符分隔）
 *
 * 所有格式统一输出标准化的 CookieEntry 数组。
 */

import type { CookieEntry, CookieFormat } from "./types.js";

/**
 * 自动识别输入的 Cookie 格式。
 * @param input - 原始 Cookie 字符串
 * @returns 识别出的格式类型
 * @throws 无法识别格式时抛出异常
 */
export function detectFormat(input: string): CookieFormat {
  const trimmed = input.trim();

  // JSON 数组：以 [ 开头
  if (trimmed.startsWith("[")) {
    return "json_array";
  }

  // Netscape 格式：包含制表符分隔的行，通常以域名或注释行开头
  const lines = trimmed.split("\n").filter((l) => l.trim() && !l.trim().startsWith("#"));
  if (lines.length > 0 && lines[0].includes("\t") && lines[0].split("\t").length >= 6) {
    return "netscape";
  }

  // Raw header 格式：单行或多行 key=value; 结构
  if (trimmed.includes("=")) {
    return "raw_header";
  }

  throw new Error("无法识别 Cookie 格式。支持的格式：JSON 数组、raw header（key=value; ...）、Netscape/curl 格式。");
}

/**
 * 解析 JSON 数组格式的 Cookie（Cookie-Editor 导出格式）。
 *
 * 期望格式示例：
 * ```json
 * [{"name":"session","value":"abc","domain":".example.com","path":"/"}]
 * ```
 *
 * @param input - JSON 字符串
 * @returns 标准化的 CookieEntry 数组
 * @throws JSON 解析失败或格式不匹配时抛出异常
 */
export function parseJsonArray(input: string): CookieEntry[] {
  let parsed: unknown[];
  try {
    parsed = JSON.parse(input.trim());
  } catch {
    throw new Error("JSON 解析失败，请检查输入是否为合法的 JSON 数组。");
  }

  if (!Array.isArray(parsed)) {
    throw new Error("输入不是 JSON 数组。");
  }

  if (parsed.length === 0) {
    throw new Error("Cookie 数组为空。");
  }

  return parsed.map((item, idx) => {
    const obj = item as Record<string, unknown>;
    if (!obj.name || !obj.value || !obj.domain) {
      throw new Error(`第 ${idx + 1} 条 Cookie 缺少必要字段（name/value/domain）。`);
    }
    return {
      name: String(obj.name),
      value: String(obj.value),
      domain: String(obj.domain),
      path: String(obj.path ?? "/"),
      expires: obj.expirationDate != null ? Number(obj.expirationDate) : (obj.expires != null ? Number(obj.expires) : undefined),
      httpOnly: obj.httpOnly === true,
      secure: obj.secure === true,
      sameSite: normalizeSameSite(obj.sameSite),
    };
  });
}

/**
 * 解析 raw header 格式的 Cookie。
 *
 * 格式示例：`session=abc; token=xyz; lang=en`
 *
 * raw header 格式不包含 domain 等元数据，调用方需额外提供 domain。
 *
 * @param input - raw header 字符串
 * @param domain - 目标域名，如 `.bilibili.com`
 * @returns 标准化的 CookieEntry 数组
 * @throws 解析失败时抛出异常
 */
export function parseRawHeader(input: string, domain: string = ""): CookieEntry[] {
  const trimmed = input.trim();
  if (!trimmed) {
    throw new Error("Cookie header 内容为空。");
  }

  const pairs = trimmed.split(";").map((p) => p.trim()).filter(Boolean);
  if (pairs.length === 0) {
    throw new Error("未找到任何 Cookie 键值对。");
  }

  return pairs.map((pair) => {
    const eqIndex = pair.indexOf("=");
    if (eqIndex <= 0) {
      throw new Error(`Cookie 格式错误: "${pair}" 不是合法的 key=value 格式。`);
    }
    return {
      name: pair.substring(0, eqIndex).trim(),
      value: pair.substring(eqIndex + 1).trim(),
      domain,
      path: "/",
    };
  });
}

/**
 * 解析 Netscape/curl 格式的 Cookie。
 *
 * 每行 7 个制表符分隔的字段：
 * domain  flag  path  secure  expires  name  value
 *
 * @param input - Netscape 格式字符串
 * @returns 标准化的 CookieEntry 数组
 * @throws 解析失败时抛出异常
 */
export function parseNetscape(input: string): CookieEntry[] {
  const lines = input.trim().split("\n")
    .map((l) => l.trim())
    .filter((l) => l && !l.startsWith("#"));

  if (lines.length === 0) {
    throw new Error("Netscape Cookie 文件为空。");
  }

  return lines.map((line, idx) => {
    const fields = line.split("\t");
    if (fields.length < 7) {
      throw new Error(`第 ${idx + 1} 行格式错误：期望至少 7 个制表符分隔字段，实际 ${fields.length} 个。`);
    }
    const [domain, , path, secure, expires, name, value] = fields;
    return {
      name: name.trim(),
      value: value.trim(),
      domain: domain.trim(),
      path: path.trim() || "/",
      secure: secure.trim().toUpperCase() === "TRUE",
      expires: expires.trim() !== "0" ? Number(expires.trim()) : undefined,
    };
  });
}

/**
 * 统一入口：自动识别格式并解析 Cookie。
 * @param input - 用户提供的原始 Cookie 文本
 * @param defaultDomain - raw header 格式时使用的默认域名
 * @returns 解析结果，包含格式、Cookie 数组和原始 header 字符串
 * @throws 识别或解析失败时抛出异常
 */
export function parseCookies(
  input: string,
  defaultDomain: string = ""
): { format: CookieFormat; cookies: CookieEntry[]; rawHeader: string } {
  const format = detectFormat(input);
  let cookies: CookieEntry[];

  switch (format) {
    case "json_array":
      cookies = parseJsonArray(input);
      break;
    case "raw_header":
      cookies = parseRawHeader(input, defaultDomain);
      break;
    case "netscape":
      cookies = parseNetscape(input);
      break;
  }

  const rawHeader = cookies.map((c) => `${c.name}=${c.value}`).join("; ");

  return { format, cookies, rawHeader };
}

/**
 * 标准化 sameSite 值。
 * @param value - 原始 sameSite 值
 * @returns 标准化后的值
 */
function normalizeSameSite(value: unknown): "Strict" | "Lax" | "None" | undefined {
  if (value == null) return undefined;
  const str = String(value).toLowerCase();
  switch (str) {
    case "strict": return "Strict";
    case "lax": return "Lax";
    case "none": return "None";
    case "no_restriction": return "None";
    case "unspecified": return undefined;
    default: return undefined;
  }
}

// CLI 入口
if (process.argv[1]?.replace(/\\/g, "/").endsWith("scripts/cookie-parser.ts")) {
  const input = process.argv[2];
  const domain = process.argv[3] || "";

  if (!input) {
    console.log("用法: npx tsx scripts/cookie-parser.ts <cookie-string> [domain]");
    process.exit(1);
  }

  try {
    const result = parseCookies(input, domain);
    console.log(JSON.stringify({
      format: result.format,
      cookieCount: result.cookies.length,
      domains: [...new Set(result.cookies.map((c) => c.domain))],
      names: result.cookies.map((c) => c.name),
    }, null, 2));
  } catch (err) {
    console.error(`解析失败: ${(err as Error).message}`);
    process.exit(1);
  }
}
