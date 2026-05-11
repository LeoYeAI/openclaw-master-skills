#!/usr/bin/env node
/**
 * wallet-raw-call.mjs — 通过 awp-wallet 内部签名发送原始合约调用
 *
 * awp-wallet CLI 的 send 命令只支持代币转账（--to, --amount, --asset），
 * 不支持原始 calldata。此脚本直接使用 awp-wallet 的内部模块（keystore、session、viem）
 * 来签名并发送带有任意 calldata 的交易。
 *
 * 用法:
 *   node wallet-raw-call.mjs --token <session> --to <contract> --data <hex> [--value <wei>]
 *
 * 必须在 awp-wallet 目录下运行（或设置 AWP_WALLET_DIR 环境变量），
 * 以便正确解析 node_modules 和内部模块。
 */

import { parseArgs } from "node:util"
import { resolve, dirname } from "node:path"
import { realpathSync, existsSync } from "node:fs"

// ── 解析命令行参数 ──────────────────────────────────
const { values: args } = parseArgs({
  options: {
    token:  { type: "string" },
    to:     { type: "string" },
    data:   { type: "string" },
    value:  { type: "string", default: "0" },
    chain:  { type: "string", default: "base" },
  },
  strict: true,
})

if (!args.token || !args.to || !args.data) {
  console.error(JSON.stringify({ error: "Required: --token, --to, --data" }))
  process.exit(1)
}

// ── 格式校验 ──────────────────────────────────────────
if (!/^0x[0-9a-fA-F]{40}$/.test(args.to)) {
  console.error(JSON.stringify({ error: `Invalid --to address: ${args.to}` }))
  process.exit(1)
}
if (!/^0x(?:[0-9a-fA-F]{2}){4,}$/.test(args.data)) {
  console.error(JSON.stringify({ error: `Invalid --data hex: ${args.data}` }))
  process.exit(1)
}

// ── 定位 awp-wallet 安装目录 ──────────────────────────
function findAwpWalletDir() {
  // 1. 环境变量
  if (process.env.AWP_WALLET_DIR && existsSync(process.env.AWP_WALLET_DIR)) {
    return process.env.AWP_WALLET_DIR
  }
  // 2. 在 PATH 中查找 awp-wallet 可执行文件（纯 Node.js，无需 child_process）
  const pathDirs = (process.env.PATH || "").split(":")
  for (const dir of pathDirs) {
    const candidate = resolve(dir, "awp-wallet")
    if (existsSync(candidate)) {
      try {
        const real = realpathSync(candidate)
        // real = .../awp-wallet/scripts/wallet-cli.js → 上两级 = awp-wallet/
        return dirname(dirname(real))
      } catch { /* 跳过无法解析的符号链接 */ }
    }
  }
  {
    // 3. 默认路径
    const defaultDir = resolve(process.env.HOME, "awp-wallet")
    if (existsSync(resolve(defaultDir, "scripts/lib/keystore.js"))) return defaultDir
    console.error(JSON.stringify({ error: "Cannot locate awp-wallet installation. Set AWP_WALLET_DIR." }))
    process.exit(1)
  }
}

const AWP_DIR = findAwpWalletDir()

// ── 导入 awp-wallet 内部模块 ─────────────────────────
const { validateSession, requireScope } = await import(`${AWP_DIR}/scripts/lib/session.js`)
const { loadSigner, getAddress } = await import(`${AWP_DIR}/scripts/lib/keystore.js`)
const { resolveChainId, viemChain, publicClient, getRpcUrl } = await import(`${AWP_DIR}/scripts/lib/chains.js`)

const { createWalletClient, http } = await import(`${AWP_DIR}/node_modules/viem/index.js`)

// ── 验证 session ─────────────────────────────────────
try {
  validateSession(args.token)
  requireScope(args.token, "transfer")
} catch (e) {
  console.error(JSON.stringify({ error: `Session error: ${e.message}` }))
  process.exit(1)
}

// ── 构建并发送交易 ───────────────────────────────────
try {
  const chainId = resolveChainId(args.chain)
  const chainObj = viemChain(chainId)
  const { account: signer } = loadSigner()
  if (!signer) {
    console.error(JSON.stringify({ error: "Failed to load signer from keystore" }))
    process.exit(1)
  }

  const walletClient = createWalletClient({
    account: signer,
    chain: chainObj,
    transport: http(getRpcUrl(chainId)),
  })

  const tx = {
    to: args.to,
    data: args.data,
  }

  // 支持发送 ETH（value > 0 的合约调用）
  if (args.value && args.value !== "0") {
    try {
      tx.value = BigInt(args.value)
    } catch {
      console.error(JSON.stringify({ error: `Invalid --value (must be integer wei): ${args.value}` }))
      process.exit(1)
    }
  }

  const hash = await walletClient.sendTransaction(tx)

  // 等待确认
  const client = publicClient(chainId)
  const receipt = await client.waitForTransactionReceipt({
    hash,
    timeout: 90_000,
    confirmations: 1,
  })

  console.log(JSON.stringify({
    status: receipt.status === "success" ? "confirmed" : "reverted",
    txHash: hash,
    chain: chainObj.name,
    chainId,
    to: args.to,
    gasUsed: receipt.gasUsed.toString(),
    blockNumber: Number(receipt.blockNumber),
  }))
} catch (e) {
  console.error(JSON.stringify({ error: `Transaction failed: ${e.message}` }))
  process.exit(1)
}
