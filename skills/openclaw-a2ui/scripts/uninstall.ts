#!/usr/bin/env node --experimental-strip-types
/**
 * uninstall.ts - 卸载 openclaw-a2ui 技能
 *
 * 执行内容：
 *   1. 从 openclaw.json 移除 skill-ui-bridge plugin 注册
 *   2. 可选：删除 plugin 文件夹（--remove-plugin-files）
 *
 * 用法:
 *   node --experimental-strip-types uninstall.ts [--openclaw-config PATH] [--extensions-dir PATH] [--remove-plugin-files]
 */

import fs from "node:fs";
import path from "node:path";

const DEFAULT_CONFIG_CANDIDATES = [
  path.join(process.env.HOME ?? "/root", ".openclaw", "openclaw.json"),
  "/root/.openclaw/openclaw.json",
];
const DEFAULT_EXTENSIONS_CANDIDATES = [
  path.join(process.env.HOME ?? "/root", ".openclaw", "extensions"),
  "/root/.openclaw/extensions",
];

function findPath(candidates: string[], label: string): string | null {
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return null;
}

function parseArgs(): {
  config?: string;
  extensions?: string;
  removePluginFiles: boolean;
} {
  const args = process.argv.slice(2);
  const get = (flag: string) => {
    const i = args.indexOf(flag);
    return i >= 0 ? args[i + 1] : undefined;
  };
  return {
    config: get("--openclaw-config"),
    extensions: get("--extensions-dir"),
    removePluginFiles: args.includes("--remove-plugin-files"),
  };
}

function main(): void {
  const args = parseArgs();

  const configPath = args.config ?? findPath(DEFAULT_CONFIG_CANDIDATES, "openclaw.json");
  const extDir = args.extensions ?? findPath(DEFAULT_EXTENSIONS_CANDIDATES, "extensions dir");
  const pluginId = "skill-ui-bridge";

  // 1. 从 openclaw.json 移除 plugin 注册
  if (configPath && fs.existsSync(configPath)) {
    const cfg = JSON.parse(fs.readFileSync(configPath, "utf-8"));
    const plugins = cfg.plugins ?? {};
    let changed = false;

    if (Array.isArray(plugins.allow) && plugins.allow.includes(pluginId)) {
      plugins.allow = plugins.allow.filter((id: string) => id !== pluginId);
      changed = true;
    }
    if (plugins.entries?.[pluginId]) {
      delete plugins.entries[pluginId];
      changed = true;
    }

    if (changed) {
      fs.writeFileSync(configPath, JSON.stringify(cfg, null, 2), "utf-8");
      console.log(`[OK] Removed plugin registration from ${configPath}`);
    } else {
      console.log(`[SKIP] skill-ui-bridge not found in ${configPath}`);
    }
  }

  // 2. 可选：删除 plugin 文件夹
  if (args.removePluginFiles && extDir) {
    const pluginDir = path.join(extDir, pluginId);
    if (fs.existsSync(pluginDir)) {
      fs.rmSync(pluginDir, { recursive: true });
      console.log(`[OK] Deleted plugin directory ${pluginDir}`);
    }
  }

  console.log("\n✅ Uninstall complete! Restart gateway to apply.");
  console.log("   Run: openclaw gateway restart");
}

main();
