#!/usr/bin/env node
/**
 * 由 Agent 自动生成做市用 worker 密钥，无需用户提供。
 * 生成 N 个随机私钥及对应地址，按生成时间命名导出到本地文件，并输出地址列表（供 setAllowedCallers 使用）。
 *
 * 用法：node scripts/mm-generate-workers.js [N]  或  WORKER_COUNT=20 node scripts/mm-generate-workers.js
 * 默认 N=20。文件名：mm-workers-<YYYYMMDD>-<HHmmss>.json（按生成时间命名）。
 * 输出：--json 时 stdout 输出 { "addresses": [...], "file": "<绝对路径>" }；否则每行一个地址，文件路径写 stderr。
 */

import { generatePrivateKey } from "viem/accounts";
import { privateKeyToAccount } from "viem/accounts";
import fs from "fs";
import path from "path";

const argv = process.argv.slice(2).filter((a) => a !== "--json");
const N = Math.min(Math.max(parseInt(process.env.WORKER_COUNT || argv[0] || "20", 10) || 20, 2), 20);
const asJson = process.argv.includes("--json");
const outDir = process.cwd();

const now = new Date();
const timeTag =
  now.getFullYear() +
  String(now.getMonth() + 1).padStart(2, "0") +
  String(now.getDate()).padStart(2, "0") +
  "-" +
  String(now.getHours()).padStart(2, "0") +
  String(now.getMinutes()).padStart(2, "0") +
  String(now.getSeconds()).padStart(2, "0");
const fileName = `mm-workers-${timeTag}.json`;
const outPath = path.join(outDir, fileName);

const privateKeys = [];
const addresses = [];
for (let i = 0; i < N; i++) {
  const pk = generatePrivateKey();
  privateKeys.push(pk);
  addresses.push(privateKeyToAccount(pk).address);
}

const data = { privateKeys, addresses, generatedAt: now.toISOString() };
fs.writeFileSync(outPath, JSON.stringify(data, null, 2), "utf8");
const absPath = path.resolve(outPath);
process.stderr.write(`已生成 ${N} 个 worker 并写入 ${absPath}\n`);

if (asJson) {
  process.stdout.write(JSON.stringify({ addresses, file: absPath }));
} else {
  addresses.forEach((a) => process.stdout.write(a + "\n"));
}
