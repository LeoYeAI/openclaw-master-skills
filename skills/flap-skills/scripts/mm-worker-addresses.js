#!/usr/bin/env node
/**
 * 从环境变量 PRIVATE_KEYS_MM（逗号分隔的私钥）输出对应地址列表，供 Agent 调用 setAllowedCallers 或配置 mm-bot 使用。
 * 用法：PRIVATE_KEYS_MM=0xkey1,0xkey2 node scripts/mm-worker-addresses.js
 * 输出：每行一个地址，或 --json 输出 JSON 数组。
 */

import { privateKeyToAccount } from "viem/accounts";

const raw = process.env.PRIVATE_KEYS_MM || "";
const keys = raw
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);

if (keys.length === 0) {
  process.stderr.write("请设置环境变量 PRIVATE_KEYS_MM（逗号分隔的做市 worker 私钥，2～20 个）\n");
  process.exit(1);
}

const addresses = keys.map((pk) => privateKeyToAccount(pk).address);

if (process.argv.includes("--json")) {
  process.stdout.write(JSON.stringify(addresses));
} else {
  addresses.forEach((a) => process.stdout.write(a + "\n"));
}
