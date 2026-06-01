#!/usr/bin/env node

/**
 * 生成 / 复用 Crab API 签名头
 *
 * 用法：
 *   node skills/scripts/crab-sign.js              # 输出 JSON 格式的签名头
 *   node skills/scripts/crab-sign.js --header     # 输出 curl -H 格式
 *   node skills/scripts/crab-sign.js --refresh    # 强制重新生成签名
 *
 * 流程：
 *   1. 首次运行：生成密钥对 + 签名，保存到 ~/.config/crab/credentials.json
 *   2. 后续运行：检查已保存的签名是否在 24h 内，有效则直接复用
 *   3. 过期或 --refresh：重新签名并保存
 *
 * 依赖：Node.js >= 16（使用内置 crypto 模块，无额外依赖）
 */

const {
  loadCredentials,
  generateWallet,
  signRequest,
  CREDENTIALS_PATH,
} = require("./crab_auth");
const fs = require("fs");
const path = require("path");

const TOLERANCE_S = 86400; // 24 小时

function isHeadersValid(credentials) {
  if (!credentials.cachedHeaders) return false;
  const ts = parseInt(credentials.cachedHeaders["X-Crab-Timestamp"], 10);
  if (Number.isNaN(ts)) return false;
  const now = Math.floor(Date.now() / 1000);
  return Math.abs(now - ts) <= TOLERANCE_S;
}

function saveCredentials(credentials) {
  const dir = path.dirname(CREDENTIALS_PATH);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(CREDENTIALS_PATH, JSON.stringify(credentials, null, 2), {
    mode: 0o600,
  });
}

// --- 加载或生成凭证 ---

let credentials = loadCredentials();

if (!credentials) {
  credentials = generateWallet();
  saveCredentials(credentials);
  process.stderr.write(`[crab] 已生成凭证: ${CREDENTIALS_PATH}\n`);
  process.stderr.write(`[crab] 地址: ${credentials.address}\n`);
}

// --- 检查缓存的签名是否有效 ---

const forceRefresh = process.argv.includes("--refresh");

if (!forceRefresh && isHeadersValid(credentials)) {
  process.stderr.write(`[crab] 复用已有签名 (未过期)\n`);
} else {
  // 生成新签名并持久化
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = signRequest(
    credentials.privateKey,
    timestamp,
    credentials.address,
  );
  credentials.cachedHeaders = {
    "X-Crab-Timestamp": timestamp,
    "X-Crab-Signature": signature,
    "X-Crab-Key": credentials.publicKey,
    "X-Crab-Address": credentials.address,
  };
  saveCredentials(credentials);
  process.stderr.write(`[crab] 已生成新签名\n`);
}

// --- 输出 ---

const headers = credentials.cachedHeaders;

if (process.argv.includes("--header")) {
  for (const [key, value] of Object.entries(headers)) {
    console.log(`-H '${key}: ${value}'`);
  }
} else {
  console.log(JSON.stringify(headers));
}
