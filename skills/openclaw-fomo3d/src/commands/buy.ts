import { readConfig, requirePrivateKey, getFomoToken } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"
import {
  PORTAL_ADDRESSES, PORTAL_ABI, NATIVE_BNB,
  PANCAKE_ROUTER_ADDRESSES, PANCAKE_ROUTER_ABI, WBNB_ADDRESSES,
  TOKEN_STATUS, queryTokenStatus,
} from "../lib/flap.js"
import { parseBigInt } from "../lib/utils.js"

export async function buy(args: string[]) {
  const amountStr = getFlagValue(args, "--amount")
  if (!amountStr) fatal("Missing --amount <bnb_wei>. Usage: fomo3d buy --amount 10000000000000000 (0.01 BNB)")

  const bnbAmount = parseBigInt(amountStr, "amount")
  if (bnbAmount <= 0n) fatal("Amount must be positive")

  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const fomoToken = getFomoToken(config)
  const portal = PORTAL_ADDRESSES[config.network]
  const account = walletClient.account!.address

  // 检查 BNB 余额
  const bnbBalance = await publicClient.getBalance({ address: account })
  if (bnbBalance < bnbAmount) {
    fatal(`Insufficient BNB balance: have ${bnbBalance}, need ${bnbAmount}`)
  }

  // 查代币市场状态
  const { statusCode, tokenState } = await queryTokenStatus(publicClient, portal, fomoToken)
  if (!tokenState) log("Token not found on FLAP Portal, using PancakeSwap...")
  const statusName = TOKEN_STATUS[statusCode] ?? "Unknown"

  if (statusCode === 1) {
    // 内盘（Tradable）— 直接调用 Portal.swapExactInput 用 BNB
    log(`Buying FOMO on 内盘 (Portal) with ${bnbAmount} BNB (wei)...`)
    const hash = await walletClient.writeContract({
      address: portal,
      abi: PORTAL_ABI,
      functionName: "swapExactInput",
      args: [{
        inputToken: NATIVE_BNB,
        outputToken: fomoToken,
        inputAmount: bnbAmount,
        minOutputAmount: 0n,
        permitData: "0x",
      }],
      value: bnbAmount,
      chain: walletClient.chain,
    })

    log(`Transaction: ${hash}`)
    const receipt = await publicClient.waitForTransactionReceipt({ hash })

    output({
      txHash: hash,
      blockNumber: Number(receipt.blockNumber),
      status: receipt.status,
      bnbSpent: bnbAmount.toString(),
      token: fomoToken,
      market: "内盘 (Portal)",
    }, (d) => {
      log(`\nBuy ${d.status === "success" ? "successful" : "failed"}!`)
      log(`BNB spent: ${d.bnbSpent}`)
      log(`Market: ${d.market}`)
      log(`Block: ${d.blockNumber}`)
      log("")
    })
  } else if (statusCode === 4) {
    // 外盘（DEX）— PancakeSwap V2 Router (swapExactETHForTokens)
    const pancakeRouter = PANCAKE_ROUTER_ADDRESSES[config.network]
    const wbnb = WBNB_ADDRESSES[config.network]
    log(`Buying FOMO on 外盘 (PancakeSwap) with ${bnbAmount} BNB (wei)...`)
    const deadline = BigInt(Math.floor(Date.now() / 1000) + 300) // 5 分钟

    const hash = await walletClient.writeContract({
      address: pancakeRouter,
      abi: PANCAKE_ROUTER_ABI,
      functionName: "swapExactETHForTokensSupportingFeeOnTransferTokens",
      args: [0n, [wbnb, fomoToken], account, deadline],
      value: bnbAmount,
      chain: walletClient.chain,
    })

    log(`Transaction: ${hash}`)
    const receipt = await publicClient.waitForTransactionReceipt({ hash })

    output({
      txHash: hash,
      blockNumber: Number(receipt.blockNumber),
      status: receipt.status,
      bnbSpent: bnbAmount.toString(),
      token: fomoToken,
      market: "外盘 (PancakeSwap)",
    }, (d) => {
      log(`\nBuy ${d.status === "success" ? "successful" : "failed"}!`)
      log(`BNB spent: ${d.bnbSpent}`)
      log(`Market: ${d.market}`)
      log(`Block: ${d.blockNumber}`)
      log("")
    })
  } else {
    fatal(`Token is not tradable. Status: ${statusName} (${statusCode})`)
  }
}
