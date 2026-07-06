#!/usr/bin/env node
/**
 * 环境检查脚本
 */
import { existsSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = join(__dirname, '..');

let ok = true;

function check(label, pass, hint) {
  const icon = pass ? '✅' : '❌';
  console.log(`  ${icon} ${label}`);
  if (!pass) { console.log(`     → ${hint}`); ok = false; }
}

console.log('\n🔍 wemp-ops 环境检查\n');

// Node.js 版本
const nodeVer = process.versions.node.split('.').map(Number);
check('Node.js >= 18', nodeVer[0] >= 18, `当前版本 ${process.version}，请升级到 v18+`);

// Python3
let hasPython = false;
try { execSync('python3 --version', { stdio: 'pipe' }); hasPython = true; } catch {}
check('Python3 可用', hasPython, '安装 Python3：https://www.python.org/downloads/');

// 微信公众号配置（从 skill 自己的 config/default.json 读取）
const configPath = join(SKILL_ROOT, 'config', 'default.json');
let hasWemp = false;
if (existsSync(configPath)) {
  try {
    const config = JSON.parse(readFileSync(configPath, 'utf-8'));
    hasWemp = !!(config?.weixin?.appId && config?.weixin?.appSecret);
  } catch {}
}
check('微信公众号配置', hasWemp,
  `在 ${configPath} 的 weixin 字段配置 appId + appSecret\n     ⚠️ 不要写到 openclaw.json 的 channels 里，会导致 gateway 崩溃！`);

console.log(ok ? '\n✅ 环境就绪！\n' : '\n⚠️  请修复以上问题后重试。\n');
process.exit(ok ? 0 : 1);
