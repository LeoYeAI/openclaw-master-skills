#!/usr/bin/env node --experimental-strip-types
/**
 * install.ts — 安装 openclaw-a2ui 技能到 OpenClaw 实例
 *
 * 工作原理（v2）：
 *   skill-ui-bridge plugin 在 gateway_start 时会：
 *   1. 读取 workspace/skills/ 下所有 ui-config.json，生成 manifest
 *   2. 将 manifest + bootstrap JS 合并写成 skill-ui-init.js，放到 control-ui 静态目录
 *   3. 在 index.html 中注入 <script src="./skill-ui-init.js">（同源，通过 CSP）
 *   4. gateway_stop 时还原 index.html，删除 skill-ui-init.js
 *
 * 本脚本执行内容：
 *   1. 将 skill-ui-bridge plugin 文件复制到 extensions 目录
 *   2. 在 openclaw.json 注册 skill-ui-bridge plugin
 *   3. 将 ui-config.json 复制到 workspace/skills/openclaw-a2ui/
 *
 * 用法:
 *   node --experimental-strip-types install.ts [options]
 *
 * 选项:
 *   --openclaw-config PATH   openclaw.json 路径（自动探测）
 *   --extensions-dir PATH    extensions 目录（自动探测）
 *   --workspace-dir PATH     workspace 目录（自动探测）
 */

import fs from "node:fs";
import path from "node:path";

const SKILL_DIR = path.resolve(import.meta.dirname, "..");
const ASSETS_DIR = path.join(SKILL_DIR, "assets");

const DEFAULT_CONFIG_CANDIDATES = [
  path.join(process.env.HOME ?? "/root", ".openclaw", "openclaw.json"),
  "/root/.openclaw/openclaw.json",
  "/home/openclaw/.openclaw/openclaw.json",
];
const DEFAULT_EXTENSIONS_DIR =
  path.join(process.env.HOME ?? "/root", ".openclaw", "extensions");
const DEFAULT_WORKSPACE_DIR =
  path.join(process.env.HOME ?? "/root", ".openclaw", "workspace");

function findPath(candidates: string[], label: string): string | null {
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  console.warn(`[WARN] Could not auto-detect ${label}.`);
  return null;
}

function parseArgs(): { config?: string; extensions?: string; workspace?: string } {
  const args = process.argv.slice(2);
  const get = (flag: string) => {
    const i = args.indexOf(flag);
    return i >= 0 ? args[i + 1] : undefined;
  };
  return {
    config: get("--openclaw-config"),
    extensions: get("--extensions-dir"),
    workspace: get("--workspace-dir"),
  };
}

function installPlugin(extensionsDir: string, configPath: string): void {
  const pluginId = "skill-ui-bridge";
  const dest = path.join(extensionsDir, pluginId);
  fs.mkdirSync(dest, { recursive: true });

  // 复制三个必需文件
  fs.copyFileSync(
    path.join(ASSETS_DIR, "skill-ui-bridge-plugin.js"),
    path.join(dest, "index.js")
  );
  fs.copyFileSync(
    path.join(ASSETS_DIR, "skill-ui-bridge-plugin.json"),
    path.join(dest, "openclaw.plugin.json")
  );
  fs.copyFileSync(
    path.join(ASSETS_DIR, "skill-ui-bridge.js"),
    path.join(dest, "skill-ui-bridge.js")
  );
  console.log(`[OK] Plugin files copied to ${dest}`);

  // 注册到 openclaw.json
  const cfg = JSON.parse(fs.readFileSync(configPath, "utf-8"));
  const plugins = (cfg.plugins ??= {});

  const allow: string[] = (plugins.allow ??= []);
  if (!allow.includes(pluginId)) allow.push(pluginId);

  const load = (plugins.load ??= {});
  const paths: string[] = (load.paths ??= []);
  if (!paths.includes(extensionsDir)) paths.push(extensionsDir);

  const entries = (plugins.entries ??= {});
  if (!entries[pluginId]) entries[pluginId] = { enabled: true };

  fs.writeFileSync(configPath, JSON.stringify(cfg, null, 2), "utf-8");
  console.log(`[OK] Plugin '${pluginId}' registered in ${configPath}`);
}

function installSkillConfig(workspaceDir: string): void {
  const skillsDir = path.join(workspaceDir, "skills", "openclaw-a2ui");
  fs.mkdirSync(skillsDir, { recursive: true });

  const src = path.join(SKILL_DIR, "ui-config.json");
  const dest = path.join(skillsDir, "ui-config.json");

  if (!fs.existsSync(dest)) {
    fs.copyFileSync(src, dest);
    console.log(`[OK] ui-config.json copied to ${skillsDir}`);
  } else {
    console.log(`[SKIP] ui-config.json already exists at ${skillsDir}`);
  }
}

function main(): void {
  const args = parseArgs();

  const configPath = args.config ?? findPath(DEFAULT_CONFIG_CANDIDATES, "openclaw.json");
  const extDir = args.extensions ?? DEFAULT_EXTENSIONS_DIR;
  const workspaceDir = args.workspace ?? DEFAULT_WORKSPACE_DIR;

  if (!configPath) {
    console.error("\n[ERROR] Could not locate openclaw.json. Use --openclaw-config to specify.");
    process.exit(1);
  }

  console.log(`\nInstalling openclaw-a2ui (skill-ui-bridge v2)...`);
  console.log(`  config:     ${configPath}`);
  console.log(`  extensions: ${extDir}`);
  console.log(`  workspace:  ${workspaceDir}`);
  console.log();

  installPlugin(extDir, configPath);
  installSkillConfig(workspaceDir);

  console.log("\n✅ Installation complete!");
  console.log("\nNext steps:");
  console.log("  1. Restart gateway:  docker compose restart openclaw");
  console.log("                   or: openclaw gateway restart");
  console.log("  2. Force-refresh browser: Ctrl+Shift+R");
  console.log("  3. Check F12 Console for: [skill-ui-bridge] boot ok, tags: 45 attrs: 34");
}

main();
