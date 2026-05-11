import { isAddress, getAddress, formatUnits, type Address } from "viem"
import { readConfig, getFomoToken } from "../lib/config.js"
import { getPublicClient } from "../lib/client.js"
import { getTokenBalance } from "../lib/erc20.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"
import {
  PORTAL_ADDRESSES, TOKEN_STATUS,
  queryTokenStatus, type TokenStateResult,
} from "../lib/flap.js"
import { privateKeyToAccount } from "viem/accounts"

// 获取账户地址（读操作不需要 walletClient）
function resolveAccount(args: string[], privateKey: string): Address | undefined {
  const addressFlag = getFlagValue(args, "--address")
  if (addressFlag) {
    if (!isAddress(addressFlag)) fatal(`Invalid address: "${addressFlag}"`)
    return getAddress(addressFlag)
  }
  if (!privateKey) return undefined
  const key = privateKey.startsWith("0x") ? privateKey : `0x${privateKey}`
  return privateKeyToAccount(key as `0x${string}`).address
}

export async function tokenInfo(args: string[]) {
  const config = readConfig()
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const fomoToken = getFomoToken(config)
  const portal = PORTAL_ADDRESSES[config.network]
  const account = resolveAccount(args, config.privateKey)

  // Portal 状态 + 余额并行查询
  const [tokenStatusResult, balances] = await Promise.all([
    queryTokenStatus(publicClient, portal, fomoToken),
    account
      ? Promise.all([getTokenBalance(publicClient, fomoToken, account), publicClient.getBalance({ address: account })])
      : Promise.resolve([0n, 0n] as const),
  ])

  const { statusCode, tokenState } = tokenStatusResult
  const [fomoBalance, bnbBalance] = balances

  if (tokenState) {
    // FLAP 代币，有 Portal 状态
    const statusName = TOKEN_STATUS[statusCode] ?? "Unknown"
    const phase = statusCode === 1 ? "内盘 (Portal)" : statusCode === 4 ? "外盘 (PancakeSwap)" : statusName
    const quoteToken = tokenState.quoteTokenAddress === "0x0000000000000000000000000000000000000000" ? "BNB (native)" : tokenState.quoteTokenAddress

    output({
      token: fomoToken,
      network: config.network,
      portal,
      status: statusName,
      statusCode,
      phase,
      quoteToken,
      price: tokenState.price.toString(),
      reserve: tokenState.reserve.toString(),
      circulatingSupply: tokenState.circulatingSupply.toString(),
      taxRate: Number(tokenState.taxRate),
      progress: tokenState.progress.toString(),
      fomoBalance: fomoBalance.toString(),
      bnbBalance: bnbBalance.toString(),
      account: account ?? "N/A",
    }, (d) => {
      log(`\nFOMO Token Info (${d.network})`)
      log(`Token: ${d.token}`)
      log(`Portal: ${d.portal}`)
      log(`Phase: ${d.phase}`)
      log(`Status: ${d.status} (${d.statusCode})`)
      log(`Quote Token: ${d.quoteToken}`)
      log(`Price: ${formatUnits(BigInt(d.price), 18)} BNB`)
      log(`Tax Rate: ${d.taxRate / 10}%`)
      log(`Progress: ${formatUnits(BigInt(d.progress), 16)}%`)
      if (account) {
        log(`\nYour Balances:`)
        log(`FOMO: ${formatUnits(BigInt(d.fomoBalance), 18)}`)
        log(`BNB: ${formatUnits(BigInt(d.bnbBalance), 18)}`)
      }
      log("")
    })
  } else {
    // 非 FLAP 代币（PancakeSwap 外部代币）
    output({
      token: fomoToken,
      network: config.network,
      status: "N/A (not on FLAP)",
      phase: "外盘 (PancakeSwap)",
      fomoBalance: fomoBalance.toString(),
      bnbBalance: bnbBalance.toString(),
      account: account ?? "N/A",
    }, (d) => {
      log(`\nToken Info (${d.network})`)
      log(`Token: ${d.token}`)
      log(`Phase: ${d.phase}`)
      log(`Status: ${d.status}`)
      if (account) {
        log(`\nYour Balances:`)
        log(`Token: ${formatUnits(BigInt(d.fomoBalance), 18)}`)
        log(`BNB: ${formatUnits(BigInt(d.bnbBalance), 18)}`)
      }
      log("")
    })
  }
}
