/**
 * SocialVault 适配器生成模块
 *
 * 根据用户提供的平台信息自动生成 Markdown 适配器文件。
 * Agent 通过对话收集信息后调用此脚本生成文件。
 * 生成前会校验 session_check 端点域名是否受信任。
 *
 * 运行：npx tsx scripts/adapter-generator.ts <json-params>
 */

import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { validateEndpointDomain } from "./session-verifier.js";

/** 适配器生成参数 */
export interface AdapterParams {
  platformId: string;
  platformName: string;
  authMethods: Array<{
    type: "cookie_paste" | "api_token" | "qrcode";
    priority: number;
    label: string;
  }>;
  capabilities: string[];
  sessionCheckMethod: "api" | "browser";
  sessionCheckEndpoint: string;
  sessionCheckIndicator: string;
  estimatedSessionDays: number;
  autoRefreshSupported: boolean;
  cookieGuide?: string;
  rateLimits?: Record<string, number>;
  authSteps?: string;
  validationDescription?: string;
  operationDescriptions?: Record<string, string>;
  knownIssues?: string[];
}

/**
 * 生成适配器 frontmatter YAML。
 * @param params - 适配器参数
 * @returns YAML frontmatter 字符串
 */
function generateFrontmatter(params: AdapterParams): string {
  const lines: string[] = [
    "---",
    `platform_id: "${params.platformId}"`,
    `platform_name: "${params.platformName}"`,
    "auth_methods:",
  ];

  for (const method of params.authMethods) {
    lines.push(`  - type: "${method.type}"`);
    lines.push(`    priority: ${method.priority}`);
    lines.push(`    label: "${method.label}"`);
  }

  lines.push("capabilities:");
  for (const cap of params.capabilities) {
    lines.push(`  - ${cap}`);
  }

  if (params.cookieGuide) {
    lines.push(`cookie_guide: "${params.cookieGuide}"`);
  }

  lines.push("session_check:");
  lines.push(`  method: "${params.sessionCheckMethod}"`);
  lines.push(`  endpoint: "${params.sessionCheckEndpoint}"`);
  lines.push(`  success_indicator: "${params.sessionCheckIndicator}"`);
  lines.push(`estimated_session_duration_days: ${params.estimatedSessionDays}`);
  lines.push(`auto_refresh_supported: ${params.autoRefreshSupported}`);

  if (params.rateLimits && Object.keys(params.rateLimits).length > 0) {
    lines.push("rate_limits:");
    for (const [key, value] of Object.entries(params.rateLimits)) {
      lines.push(`  ${key}: ${value}`);
    }
  }

  lines.push("---");
  return lines.join("\n");
}

/**
 * 生成适配器正文 Markdown。
 * @param params - 适配器参数
 * @returns Markdown 正文
 */
function generateBody(params: AdapterParams): string {
  const sections: string[] = [];

  // 认证流程
  sections.push("## 认证流程");
  sections.push("");
  if (params.authSteps) {
    sections.push(params.authSteps);
  } else {
    for (const method of params.authMethods) {
      sections.push(`### ${method.label}`);
      sections.push("");
      if (method.type === "cookie_paste") {
        sections.push("用户在浏览器中登录后，通过 Cookie-Editor 插件导出 Cookie 并粘贴给 SocialVault。");
        sections.push("");
        if (params.cookieGuide) {
          sections.push(`**Cookie 获取步骤**：参见 ${params.cookieGuide}`);
        }
      } else if (method.type === "api_token") {
        sections.push("用户获取平台 API 凭证后提供给 SocialVault。");
      } else if (method.type === "qrcode") {
        sections.push("通过 headless browser 打开登录页面生成二维码，用户使用手机 APP 扫码完成登录。");
      }
      sections.push("");
    }
  }

  // 登录态验证
  sections.push("## 登录态验证");
  sections.push("");
  if (params.validationDescription) {
    sections.push(params.validationDescription);
  } else if (params.sessionCheckMethod === "browser") {
    sections.push(`使用 browser 工具访问 \`${params.sessionCheckEndpoint}\`，检查页面是否包含 "${params.sessionCheckIndicator}"。`);
    sections.push("");
    sections.push("判定逻辑：");
    sections.push(`- 页面包含 "${params.sessionCheckIndicator}" → \`healthy\``);
    sections.push("- 页面重定向到登录页面 → `expired`");
    sections.push("- 页面加载超时 → `unknown`");
  } else {
    sections.push(`发送请求到 \`${params.sessionCheckEndpoint}\`，检查响应中是否包含 "${params.sessionCheckIndicator}"。`);
    sections.push("");
    sections.push("判定逻辑：");
    sections.push(`- 响应 200 且包含 "${params.sessionCheckIndicator}" → \`healthy\``);
    sections.push("- 响应 401/403 → `expired`");
    sections.push("- 网络错误 → `unknown`");
  }
  sections.push("");

  // 操作指令
  sections.push("## 操作指令");
  sections.push("");
  if (params.operationDescriptions) {
    for (const [cap, desc] of Object.entries(params.operationDescriptions)) {
      sections.push(`### ${cap}`);
      sections.push("");
      sections.push(desc);
      sections.push("");
    }
  } else {
    for (const cap of params.capabilities) {
      sections.push(`### ${cap}`);
      sections.push("");
      sections.push(`（待补充 ${cap} 操作的具体步骤）`);
      sections.push("");
    }
  }

  // 频率控制
  sections.push("## 频率控制");
  sections.push("");
  if (params.rateLimits && Object.keys(params.rateLimits).length > 0) {
    sections.push("| 操作 | 建议频率 |");
    sections.push("|------|----------|");
    for (const [key, value] of Object.entries(params.rateLimits)) {
      sections.push(`| ${key} | ${value} |`);
    }
  } else {
    sections.push("（请根据平台实际情况补充频率限制建议）");
  }
  sections.push("");

  // 已知问题
  sections.push("## 已知问题");
  sections.push("");
  if (params.knownIssues && params.knownIssues.length > 0) {
    for (let i = 0; i < params.knownIssues.length; i++) {
      sections.push(`${i + 1}. ${params.knownIssues[i]}`);
    }
  } else {
    sections.push("（暂无已知问题）");
  }

  return sections.join("\n");
}

/**
 * 生成完整的适配器 Markdown 文件内容。
 * @param params - 适配器参数
 * @returns 完整的 Markdown 文件内容
 */
export function generateAdapter(params: AdapterParams): string {
  const frontmatter = generateFrontmatter(params);
  const body = generateBody(params);
  return `${frontmatter}\n\n${body}\n`;
}

/**
 * 将生成的适配器写入文件。
 * @param skillDir - skill 根目录
 * @param params - 适配器参数
 * @param isCustom - 是否为用户自建适配器（存入 custom/ 目录）
 * @returns 生成的文件路径
 * @throws 文件已存在时抛出异常
 */
export function writeAdapter(
  skillDir: string,
  params: AdapterParams,
  isCustom: boolean = true
): string {
  const domainCheck = validateEndpointDomain(params.sessionCheckEndpoint);
  if (!domainCheck.trusted) {
    throw new Error(
      `安全拒绝：session_check 端点域名 "${domainCheck.domain}" 不在受信任白名单中。` +
      `请使用平台的官方域名，或联系维护者将该域名添加到白名单。`
    );
  }

  const dir = isCustom ? join(skillDir, "adapters", "custom") : join(skillDir, "adapters");
  const fileName = `${params.platformId}.md`;
  const filePath = join(dir, fileName);

  if (existsSync(filePath)) {
    throw new Error(`适配器文件已存在: ${filePath}。如需覆盖，请先删除现有文件。`);
  }

  const content = generateAdapter(params);
  try {
    writeFileSync(filePath, content, "utf-8");
  } catch (err) {
    throw new Error(`适配器文件写入失败: ${(err as Error).message}`);
  }
  return filePath;
}

/**
 * 列出所有适配器信息。
 * @param skillDir - skill 根目录
 * @returns 适配器信息数组
 */
export function listAdapters(
  skillDir: string
): Array<{ platformId: string; platformName: string; source: string; filePath: string }> {
  const adapters: Array<{ platformId: string; platformName: string; source: string; filePath: string }> = [];

  const scanDir = (dir: string, source: string) => {
    if (!existsSync(dir)) return;
    let files: string[];
    try {
      files = readdirSync(dir) as string[];
    } catch {
      return;
    }
    for (const file of files) {
      if (!file.endsWith(".md") || file.startsWith("_")) continue;
      const filePath = join(dir, file);
      try {
        const content = readFileSync(filePath, "utf-8");
        const idMatch = content.match(/platform_id:\s*["']?([^"'\n]+)["']?/);
        const nameMatch = content.match(/platform_name:\s*["']?([^"'\n]+)["']?/);
        if (idMatch && nameMatch) {
          adapters.push({
            platformId: idMatch[1].trim(),
            platformName: nameMatch[1].trim(),
            source,
            filePath: filePath,
          });
        }
      } catch {
        // 跳过无法读取的文件
      }
    }
  };

  scanDir(join(skillDir, "adapters"), "官方");
  scanDir(join(skillDir, "adapters", "custom"), "自建");

  return adapters;
}

// CLI 入口
if (process.argv[1]?.replace(/\\/g, "/").endsWith("scripts/adapter-generator.ts")) {
  const command = process.argv[2];
  const skillDir = resolve(process.argv[3] || ".");

  switch (command) {
    case "generate": {
      const jsonInput = process.argv[4];
      if (!jsonInput) {
        console.error("用法: npx tsx scripts/adapter-generator.ts generate <skill-dir> <json-params>");
        process.exit(1);
      }
      try {
        const params = JSON.parse(jsonInput) as AdapterParams;
        const filePath = writeAdapter(skillDir, params, true);
        console.log(`适配器已生成: ${filePath}`);
      } catch (err) {
        console.error(`生成失败: ${(err as Error).message}`);
        process.exit(1);
      }
      break;
    }
    case "list": {
      const adapters = listAdapters(skillDir);
      if (adapters.length === 0) {
        console.log("未找到任何适配器。");
      } else {
        console.log("可用适配器：");
        for (const a of adapters) {
          console.log(`  [${a.source}] ${a.platformName} (${a.platformId})`);
        }
      }
      break;
    }
    default:
      console.log("用法: npx tsx scripts/adapter-generator.ts <generate|list> [args]");
  }
}
