import { readConfig, requirePrivateKey, getFomoToken } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { ensureAllowance, getTokenBalance } from "../lib/erc20.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"
import {
  PORTAL_ADDRESSES, PORTAL_ABI, NATIVE_BNB,
  PANCAKE_ROUTER_ADDRESSES, PANCAKE_ROUTER_ABI, WBNB_ADDRESSES,
  TOKEN_STATUS, queryTokenStatus,
} from "../lib/flap.js"
import { parseBigInt } from "../lib/utils.js"

function resolveTokenAmount(amountStr: string | undefined, percentStr: string | undefined, balance: bigint): bigint {
  if (amountStr) {
    const amount = parseBigInt(amountStr, "amount")
    if (amount <= 0n) fatal("Amount must be positive")
    if (balance < amount) fatal(`Insufficient FOMO balance: have ${balance}, need ${amount}`)
    return amount
  }
  const percentBps = parseBigInt(percentStr!, "percent")
  if (percentBps <= 0n || percentBps > 10000n) fatal("Percent must be 1-10000 (bps, 10000=100%)")
  if (balance === 0n) fatal("No FOMO tokens to sell")
  const amount = (balance * percentBps) / 10000n
  if (amount === 0n) fatal("Calculated sell amount is 0")
  return amount
}

export async function sell(args: string[]) {
  const amountStr = getFlagValue(args, "--amount")
  const percentStr = getFlagValue(args, "--percent")

  if (!amountStr && !percentStr) {
    fatal("Missing --amount <token_wei> or --percent <bps>. Usage: fomo3d sell --amount 1000000000000000000 or fomo3d sell --percent 5000")
  }
  if (amountStr && percentStr) {
    fatal("Cannot use both --amount and --percent")
  }

  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const fomoToken = getFomoToken(config)
  const portal = PORTAL_ADDRESSES[config.network]
  const account = walletClient.account!.address

  // 计算卖出数量
  const balance = await getTokenBalance(publicClient, fomoToken, account)
  const tokenAmount = resolveTokenAmount(amountStr, percentStr, balance)

  // 查代币市场状态
  const { statusCode, tokenState } = await queryTokenStatus(publicClient, portal, fomoToken)
  if (!tokenState) log("Token not found on FLAP Portal, using PancakeSwap...")
  const statusName = TOKEN_STATUS[statusCode] ?? "Unknown"

  if (statusCode === 1) {
    // 内盘 — approve Portal, 调用 swapExactInput
    await ensureAllowance(publicClient, walletClient, fomoToken, portal, tokenAmount)

    log(`Selling ${tokenAmount} FOMO on 内盘 (Portal)...`)
    const hash = await walletClient.writeContract({
      address: portal,
      abi: PORTAL_ABI,
      functionName: "swapExactInput",
      args: [{
        inputToken: fomoToken,
        outputToken: NATIVE_BNB,
        inputAmount: tokenAmount,
        minOutputAmount: 0n,
        permitData: "0x",
      }],
      chain: walletClient.chain,
    })

    log(`Transaction: ${hash}`)
    const receipt = await publicClient.waitForTransactionReceipt({ hash })

    output({
      txHash: hash,
      blockNumber: Number(receipt.blockNumber),
      status: receipt.status,
      tokensSold: tokenAmount.toString(),
      market: "内盘 (Portal)",
      method: percentStr ? `sellByPercent(${percentStr}bps)` : "sellByAmount",
    }, (d) => {
      log(`\nSell ${d.status === "success" ? "successful" : "failed"}!`)
      log(`Tokens sold: ${d.tokensSold}`)
      log(`Market: ${d.market}`)
      log(`Block: ${d.blockNumber}`)
      log("")
    })
  } else if (statusCode === 4) {
    // 外盘 — approve PancakeSwap Router, swapExactTokensForETH
    const pancakeRouter = PANCAKE_ROUTER_ADDRESSES[config.network]
    const wbnb = WBNB_ADDRESSES[config.network]
    await ensureAllowance(publicClient, walletClient, fomoToken, pancakeRouter, tokenAmount)

    log(`Selling ${tokenAmount} FOMO on 外盘 (PancakeSwap)...`)
    const deadline = BigInt(Math.floor(Date.now() / 1000) + 300)

    const hash = await walletClient.writeContract({
      address: pancakeRouter,
      abi: PANCAKE_ROUTER_ABI,
      functionName: "swapExactTokensForETHSupportingFeeOnTransferTokens",
      args: [tokenAmount, 0n, [fomoToken, wbnb], account, deadline],
      chain: walletClient.chain,
    })

    log(`Transaction: ${hash}`)
    const receipt = await publicClient.waitForTransactionReceipt({ hash })

    output({
      txHash: hash,
      blockNumber: Number(receipt.blockNumber),
      status: receipt.status,
      tokensSold: tokenAmount.toString(),
      market: "外盘 (PancakeSwap)",
      method: percentStr ? `sellByPercent(${percentStr}bps)` : "sellByAmount",
    }, (d) => {
      log(`\nSell ${d.status === "success" ? "successful" : "failed"}!`)
      log(`Tokens sold: ${d.tokensSold}`)
      log(`Market: ${d.market}`)
      log(`Block: ${d.blockNumber}`)
      log("")
    })
  } else {
    fatal(`Token is not tradable. Status: ${statusName} (${statusCode})`)
  }
}
