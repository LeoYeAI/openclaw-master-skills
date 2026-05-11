#!/usr/bin/env node
/**
 * 做市/刷量机器人：资金在 MCP 钱包（funder），MCP 仅对 FlapSkill 合约授权 USDT 并 setAllowedCallers；
 * 买卖由 worker 调用 FlapSkill.buyForCaller / sellForCaller 完成，不是 MCP 直接买卖。
 *
 * 环境变量：FUNDER_ADDRESS, TOKEN_CA 必填。私钥二选一：PRIVATE_KEYS 或 PRIVATE_KEYS_FILE。可选 COLLECT_TO_ADDRESS：停止时（用户停止或 Ctrl+C）自动将 worker 剩余代币与 BNB 归集到该地址。做市不设磨损上限，仅由用户停止。
 * 若 MCP 钱包（funder）无 USDT 导致 buyForCaller 失败（TRANSFER_FROM_FAILED），则自动将所有 worker 持有的该代币通过 sellForCaller 卖给 funder（USDT 回到 funder），然后继续刷量，不停止。
 */

import { createPublicClient, createWalletClient, http, parseAbi, parseUnits, getAddress } from "viem";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
import { privateKeyToAccount } from "viem/accounts";
import { bsc } from "viem/chains";

const FLAP_SKILL = getAddress("0x482970490d06fc3a480bfd0e9e58141667cffedc");
const USDT_DECIMALS = 18;
const MAX_WORKERS = 20;
/** 每轮同时买入/卖出的地址数：BATCH 个同时买，BATCH 个同时卖（买与卖地址不重合） */
const BATCH = 5;

const FLAP_SKILL_ABI = parseAbi([
  "function buyForCaller(address _token, uint256 _usdtAmount, address _funder) external",
  "function sellForCaller(address _token, uint256 _tokenAmount, address _funder) external",
]);
const ERC20_ABI = parseAbi([
  "function approve(address spender, uint256 amount) external returns (bool)",
  "function balanceOf(address account) external view returns (uint256)",
  "function transfer(address to, uint256 amount) external returns (bool)",
]);

function env(key, def) {
  const v = process.env[key];
  return v !== undefined && v !== "" ? v : def;
}

function parseNum(s, def) {
  if (s === undefined || s === "") return def;
  const n = Number(s);
  if (Number.isNaN(n)) return def;
  return n;
}

function randomInRange(min, max) {
  const m = Math.min(min, max);
  const M = Math.max(min, max);
  const r = m + Math.random() * (M - m);
  return Math.round(r * 1e4) / 1e4;
}

/** 返回当前北京时间字符串，用于日志 */
function beijingTime() {
  return new Date().toLocaleString("zh-CN", { timeZone: "Asia/Shanghai", hour12: false });
}

function parsePrivateKeys(input) {
  if (!input || typeof input !== "string") return [];
  return input
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function loadWorkerKeys() {
  const fromEnv = parsePrivateKeys(env("PRIVATE_KEYS", ""));
  if (fromEnv.length >= 2) return fromEnv;
  const filePath = env("PRIVATE_KEYS_FILE", "");
  if (!filePath) return [];
  const abs = path.isAbsolute(filePath) ? filePath : path.join(process.cwd(), filePath);
  if (!fs.existsSync(abs)) return [];
  const data = JSON.parse(fs.readFileSync(abs, "utf8"));
  const keys = Array.isArray(data.privateKeys) ? data.privateKeys : [];
  return keys.filter((k) => typeof k === "string" && k.length > 0);
}

async function main() {
  const tokenCa = env("TOKEN_CA", process.argv[2]);
  if (!tokenCa) {
    console.error("用法: TOKEN_CA=0x... node scripts/mm-bot.js  或  node scripts/mm-bot.js <TOKEN_CA> [usdtMin] [usdtMax] [intervalSec] [rounds]");
    console.error("必须: FUNDER_ADDRESS (MCP 钱包地址), TOKEN_CA");
    console.error("私钥二选一: PRIVATE_KEYS (2～20 个逗号分隔) 或 PRIVATE_KEYS_FILE=.mm-workers.json（由 mm-generate-workers.js 生成）");
    console.error("必填: COLLECT_TO_ADDRESS（资金归集地址）。可选: RPC_URL, USDT_MIN, USDT_MAX, INTERVAL_SEC, ROUNDS");
    process.exit(1);
  }
  const token = getAddress(tokenCa);
  const collectTo = env("COLLECT_TO_ADDRESS", "");
  if (!collectTo) {
    console.error("请设置环境变量 COLLECT_TO_ADDRESS（资金归集地址；停止时将 worker 剩余代币与 BNB 归集到该地址）");
    process.exit(1);
  }
  getAddress(collectTo);
  const rpcUrl = env("RPC_URL", "https://bsc-dataseed.binance.org");
  const funderAddressRaw = env("FUNDER_ADDRESS", "");
  if (!funderAddressRaw) {
    console.error("请设置环境变量 FUNDER_ADDRESS（MCP 钱包地址，资金方；须已对 FlapSkill approve USDT）");
    process.exit(1);
  }
  const funderAddress = getAddress(funderAddressRaw);
  const workerKeys = loadWorkerKeys();
  const minWorkers = 2 * BATCH;
  if (workerKeys.length < minWorkers || workerKeys.length > MAX_WORKERS) {
    console.error(`请设置 PRIVATE_KEYS 或 PRIVATE_KEYS_FILE（.mm-workers.json），需 ${minWorkers}～${MAX_WORKERS} 个 worker 私钥（当前每轮 ${BATCH} 个同时买、${BATCH} 个同时卖）`);
    process.exit(1);
  }

  const usdtMin = parseNum(env("USDT_MIN", process.argv[3]), 0.005);
  const usdtMax = parseNum(env("USDT_MAX", process.argv[4]), 0.02);
  const intervalSec = parseNum(env("INTERVAL_SEC", process.argv[5]), 15);
  const rounds = parseNum(env("ROUNDS", process.argv[6]), 0);

  let collected = false;
  const runCollectOnExit = () => {
    if (collected) return;
    collected = true;
    const keysFile = env("PRIVATE_KEYS_FILE", "");
    if (!keysFile) return;
    console.log("正在将 worker 剩余资金归集到", collectTo, "...");
    try {
      execSync(`node "${path.join(__dirname, "mm-collect.js")}"`, {
        env: { ...process.env, TARGET_ADDRESS: collectTo, TOKEN_CA: tokenCa },
        cwd: process.cwd(),
        stdio: "inherit",
      });
    } catch (e) {
      console.error("归集失败:", e.message || e);
    }
  };

  process.on("SIGINT", () => {
    console.log("收到停止信号，做市将在本轮结束后停止并执行归集…");
    stopRequested = true;
  });
  process.on("SIGTERM", () => {
    console.log("收到停止信号，做市将在本轮结束后停止并执行归集…");
    stopRequested = true;
  });

  const transport = http(rpcUrl);
  const chain = bsc;
  const publicClient = createPublicClient({ chain, transport });
  const accounts = workerKeys.map((pk) => privateKeyToAccount(pk));
  const walletClients = accounts.map((account) => createWalletClient({ account, chain, transport }));

  const tokenContract = { address: token, abi: ERC20_ABI };

  console.log("做市机器人配置:");
  console.log("  FlapSkill:", FLAP_SKILL);
  console.log("  资金方(funder):", funderAddress);
  console.log("  代币:", token);
  console.log("  交易地址数:", accounts.length, `（每轮 ${BATCH} 个同时买、${BATCH} 个同时卖）`);
  console.log("  每笔 USDT 范围:", usdtMin, "~", usdtMax);
  console.log("  间隔(秒):", intervalSec, "  轮数(0=无限):", rounds);
  console.log("---");
  console.log("请确认已通过 MCP 用 funder 钱包：1) 对 FlapSkill approve USDT  2) 调用 setAllowedCallers(" + token + ", [上述 " + accounts.length + " 个地址])，以区分不同人、不同代币的刷量会话。");
  console.log("---");

  let done = 0;
  let stopRequested = false;

  const isGasRelatedError = (msg) => {
    if (!msg || typeof msg !== "string") return false;
    const s = msg.toLowerCase();
    return (
      s.includes("insufficient") ||
      s.includes("exceeds the balance") ||
      s.includes("not enough") ||
      s.includes("balance of the account")
    );
  };

  /** funder 无 USDT 导致 buyForCaller 扣款失败 */
  const isFunderNoUsdtError = (msg) => {
    if (!msg || typeof msg !== "string") return false;
    const s = msg.toLowerCase();
    return s.includes("transfer_from_failed") || s.includes("transferhelper");
  };

  /** 将当前所有 worker 持有的该代币通过 sellForCaller 卖给 funder，然后退出并归集 */
  const runSellAllWorkersToFunder = async () => {
    console.log(`[${beijingTime()}] [MCP 无 USDT] 正在将各 worker 持有的代币全部卖给 funder…`);
    let soldCount = 0;
    for (let i = 0; i < accounts.length; i++) {
      const account = accounts[i];
      const wallet = walletClients[i];
      try {
        const balance = await publicClient.readContract({
          ...tokenContract,
          functionName: "balanceOf",
          args: [account.address],
        });
        if (balance === 0n) continue;
        const approveHash = await wallet.writeContract({
          ...tokenContract,
          functionName: "approve",
          args: [FLAP_SKILL, balance],
          account,
        });
        await publicClient.waitForTransactionReceipt({ hash: approveHash });
        const sellHash = await wallet.writeContract({
          address: FLAP_SKILL,
          abi: FLAP_SKILL_ABI,
          functionName: "sellForCaller",
          args: [token, balance, funderAddress],
          account,
        });
        await publicClient.waitForTransactionReceipt({ hash: sellHash });
        soldCount++;
        console.log(`  worker ${account.address.slice(0, 10)}… 已卖出，tx ${sellHash.slice(0, 10)}…`);
      } catch (e) {
        console.error(`  worker ${account.address} 卖出失败:`, (e && e.message) || e);
      }
    }
    console.log(`[${beijingTime()}] [MCP 无 USDT] 已将所有 worker 代币卖给 funder，共 ${soldCount} 笔。funder 已收回 USDT，继续刷量。`);
  };

  /** 打乱数组并取前 n 个 */
  const shuffle = (arr, n) => {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a.slice(0, n);
  };

  const runOne = async () => {
    const L = accounts.length;
    const allIndices = [...Array(L).keys()];
    const chosen = shuffle(allIndices, 2 * BATCH);
    const buyerIndices = chosen.slice(0, BATCH);
    const sellerIndices = chosen.slice(BATCH, 2 * BATCH);

    const buyers = buyerIndices.map((i) => accounts[i]);
    const sellerAccounts = sellerIndices.map((i) => accounts[i]);
    const buyerWallets = buyerIndices.map((i) => walletClients[i]);
    const sellerWallets = sellerIndices.map((i) => walletClients[i]);

    try {
      // 1) BATCH 个地址同时买入（并行发 tx，再等全部确认）
      const buyAmounts = Array.from({ length: BATCH }, () => randomInRange(usdtMin, usdtMax));
      const buyPromises = buyAmounts.map((amount, i) =>
        buyerWallets[i].writeContract({
          address: FLAP_SKILL,
          abi: FLAP_SKILL_ABI,
          functionName: "buyForCaller",
          args: [token, parseUnits(String(amount), USDT_DECIMALS), funderAddress],
          account: buyers[i],
        })
      );
      const buyHashes = await Promise.all(buyPromises);
      await Promise.all(buyHashes.map((hash) => publicClient.waitForTransactionReceipt({ hash })));

      // 2) 读取 5 个买家的代币余额，再 BATCH 笔并行转给对应卖家（每人转 50%～100% 随机）
      const buyerBalances = await Promise.all(
        buyers.map((acc) =>
          publicClient.readContract({
            ...tokenContract,
            functionName: "balanceOf",
            args: [acc.address],
          })
        )
      );
      const transferAmounts = buyerBalances.map((bal) => {
        const ratioBps = 5000 + Math.floor(Math.random() * 5001);
        let amt = (bal * BigInt(ratioBps)) / 10000n;
        if (amt < 1n) amt = 1n;
        return amt;
      });
      const transferPromises = transferAmounts.map((amt, i) =>
        buyerWallets[i].writeContract({
          ...tokenContract,
          functionName: "transfer",
          args: [sellerAccounts[i].address, amt],
          account: buyers[i],
        })
      );
      const transferHashes = await Promise.all(transferPromises);
      await Promise.all(transferHashes.map((hash) => publicClient.waitForTransactionReceipt({ hash })));

      // 3) BATCH 个卖家同时授权并卖出（先并行 approve，再并行 sellForCaller）
      const sellerBalances = await Promise.all(
        sellerAccounts.map((acc) =>
          publicClient.readContract({
            ...tokenContract,
            functionName: "balanceOf",
            args: [acc.address],
          })
        )
      );
      const approvePromises = sellerBalances.map((bal, i) =>
        sellerWallets[i].writeContract({
          ...tokenContract,
          functionName: "approve",
          args: [FLAP_SKILL, bal],
          account: sellerAccounts[i],
        })
      );
      const approveHashes = await Promise.all(approvePromises);
      await Promise.all(approveHashes.map((hash) => publicClient.waitForTransactionReceipt({ hash })));
      const sellPromises = sellerBalances.map((bal, i) =>
        sellerWallets[i].writeContract({
          address: FLAP_SKILL,
          abi: FLAP_SKILL_ABI,
          functionName: "sellForCaller",
          args: [token, bal, funderAddress],
          account: sellerAccounts[i],
        })
      );
      const sellHashes = await Promise.all(sellPromises);
      await Promise.all(sellHashes.map((hash) => publicClient.waitForTransactionReceipt({ hash })));

      const totalBuyU = buyAmounts.reduce((a, b) => a + b, 0).toFixed(2);
      console.log(
        `[${beijingTime()}] 轮 ${done + 1} ${BATCH} 买 ${totalBuyU} U | ${BATCH} 卖 | 买 ${buyHashes[0].slice(0, 8)}… 卖 ${sellHashes[0].slice(0, 8)}…`
      );
      done++;
    } catch (e) {
      const errMsg = (e && e.message) ? String(e.message) : "";
      if (isFunderNoUsdtError(errMsg)) {
        console.error(`[${beijingTime()}] 轮 ${done + 1} 失败: MCP 钱包(funder)无 USDT，无法扣款。`);
        await runSellAllWorkersToFunder();
        return;
      }
      if (isGasRelatedError(errMsg)) {
        const addrs = [...buyerIndices.map((i) => accounts[i].address), ...sellerIndices.map((i) => accounts[i].address)];
        console.error(
          `[${beijingTime()}] 轮 ${done + 1} 失败(可能 worker Gas 不足):`,
          errMsg.slice(0, 200)
        );
        console.error(
          `[Agent 自主补 Gas] 请用 MCP transfer_native_token 向可能缺 Gas 的 worker 各转 0.001 BNB：`,
          addrs.slice(0, 3).join(", "),
          "..."
        );
      }
      throw e;
    }
  };

  const loop = async () => {
    while (!stopRequested && (rounds === 0 || done < rounds)) {
      try {
        await runOne();
      } catch (e) {
        const errMsg = (e && e.message) ? String(e.message) : "";
        if (!isGasRelatedError(errMsg)) {
          console.error(`[${beijingTime()}] 轮 ${done + 1} 失败:`, errMsg || e);
        }
      }
      if (stopRequested || (rounds > 0 && done >= rounds)) break;
      await new Promise((r) => setTimeout(r, intervalSec * 1000));
    }
    console.log("做市结束，共执行", done, "轮");
  };

  await loop();
  runCollectOnExit();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
