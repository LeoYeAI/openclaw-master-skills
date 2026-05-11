#!/usr/bin/env node
/**
 * 做市结束后资金归集：将各 worker 地址上的代币与 BNB 归集到指定地址。
 * 环境变量：TARGET_ADDRESS（归集目标）, TOKEN_CA（要归集的代币）, PRIVATE_KEYS_FILE（worker 密钥文件）
 */

import { createPublicClient, createWalletClient, http, parseAbi, getAddress, formatEther, parseEther } from "viem";
import fs from "fs";
import path from "path";
import { privateKeyToAccount } from "viem/accounts";
import { bsc } from "viem/chains";

const ERC20_ABI = parseAbi([
  "function balanceOf(address account) external view returns (uint256)",
  "function transfer(address to, uint256 amount) external returns (bool)",
]);

function env(key, def) {
  const v = process.env[key];
  return v !== undefined && v !== "" ? v : def;
}

function loadWorkerKeys() {
  const filePath = env("PRIVATE_KEYS_FILE", "");
  if (!filePath) return [];
  const abs = path.isAbsolute(filePath) ? filePath : path.join(process.cwd(), filePath);
  if (!fs.existsSync(abs)) return [];
  const data = JSON.parse(fs.readFileSync(abs, "utf8"));
  const keys = Array.isArray(data.privateKeys) ? data.privateKeys : [];
  return keys.filter((k) => typeof k === "string" && k.length > 0);
}

async function main() {
  const targetRaw = env("TARGET_ADDRESS", process.argv[2]);
  const tokenCa = env("TOKEN_CA", process.argv[3]);
  if (!targetRaw || !tokenCa) {
    console.error("用法: TARGET_ADDRESS=0x... TOKEN_CA=0x... PRIVATE_KEYS_FILE=mm-workers-xxx.json node scripts/mm-collect.js");
    console.error("  或: node scripts/mm-collect.js <TARGET_ADDRESS> <TOKEN_CA>");
    process.exit(1);
  }
  const target = getAddress(targetRaw);
  const token = getAddress(tokenCa);
  const rpcUrl = env("RPC_URL", "https://bsc-dataseed.binance.org");
  const workerKeys = loadWorkerKeys();
  if (workerKeys.length === 0) {
    console.error("请设置 PRIVATE_KEYS_FILE 指向 worker 密钥文件（如 mm-workers-*.json）");
    process.exit(1);
  }

  const transport = http(rpcUrl);
  const publicClient = createPublicClient({ chain: bsc, transport });
  const tokenContract = { address: token, abi: ERC20_ABI };
  const gasReserve = parseEther("0.0001");

  console.log("归集目标:", target);
  console.log("代币:", token);
  console.log("Worker 数:", workerKeys.length);

  for (let i = 0; i < workerKeys.length; i++) {
    const account = privateKeyToAccount(workerKeys[i]);
    const walletClient = createWalletClient({ account, chain: bsc, transport });
    const addr = account.address;

    const [tokenBalance, bnbBalance] = await Promise.all([
      publicClient.readContract({ ...tokenContract, functionName: "balanceOf", args: [addr] }),
      publicClient.getBalance({ address: addr }),
    ]);

    if (tokenBalance > 0n) {
      try {
        const hash = await walletClient.writeContract({
          ...tokenContract,
          functionName: "transfer",
          args: [target, tokenBalance],
          account,
        });
        await publicClient.waitForTransactionReceipt({ hash });
        console.log(`  [${i + 1}/${workerKeys.length}] ${addr.slice(0, 10)}… 代币 ${tokenBalance} → 已转`);
      } catch (e) {
        console.error(`  [${i + 1}/${workerKeys.length}] ${addr.slice(0, 10)}… 代币转账失败:`, e.message || e);
      }
    }

    const bnbLeft = await publicClient.getBalance({ address: addr });
    if (bnbLeft > gasReserve) {
      const sendAmount = bnbLeft - gasReserve;
      try {
        const hash = await walletClient.sendTransaction({
          to: target,
          value: sendAmount,
          account,
        });
        await publicClient.waitForTransactionReceipt({ hash });
        console.log(`  [${i + 1}/${workerKeys.length}] ${addr.slice(0, 10)}… BNB ${formatEther(sendAmount)} → 已转`);
      } catch (e) {
        console.error(`  [${i + 1}/${workerKeys.length}] ${addr.slice(0, 10)}… BNB 转账失败:`, e.message || e);
      }
    }
  }

  console.log("归集完成。");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
