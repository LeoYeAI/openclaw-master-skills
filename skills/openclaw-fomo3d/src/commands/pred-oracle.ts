import { readConfig, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

// 查看 Oracle 市场配置（价格源、条件、当前价格）
export async function predOracle(args: string[]) {
  const idStr = getFlagValue(args, "--id")
  if (!idStr) fatal("Missing --id <marketId>")

  const marketId = BigInt(idStr)
  const config = readConfig()
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const diamond = getPredictionDiamondAddress(config)

  const oracleConfig = await publicClient.readContract({
    address: diamond, abi: PREDICTION_ABI, functionName: "getOracleConfig", args: [marketId],
  }) as {
    feedAddress: string; strikePrice: bigint; isAbove: boolean;
    settlementPrice: bigint; feedDecimals: number; currentPrice: bigint;
    feedDescription: string
  }

  const decimals = Number(oracleConfig.feedDecimals)
  const formatPrice = (p: bigint) => {
    if (p === 0n) return "N/A"
    const factor = 10 ** decimals
    return (Number(p) / factor).toFixed(decimals)
  }

  const data = {
    marketId: Number(marketId),
    feedAddress: oracleConfig.feedAddress,
    feedDescription: oracleConfig.feedDescription,
    feedDecimals: decimals,
    strikePrice: oracleConfig.strikePrice.toString(),
    strikePriceFormatted: formatPrice(oracleConfig.strikePrice),
    isAbove: oracleConfig.isAbove,
    condition: oracleConfig.isAbove ? "Price >= Strike → Yes" : "Price <= Strike → Yes",
    currentPrice: oracleConfig.currentPrice.toString(),
    currentPriceFormatted: formatPrice(oracleConfig.currentPrice),
    settlementPrice: oracleConfig.settlementPrice.toString(),
    settlementPriceFormatted: oracleConfig.settlementPrice !== 0n ? formatPrice(oracleConfig.settlementPrice) : null,
  }

  output(data, (d) => {
    log(`\n=== Oracle Config for Market #${d.marketId} ===`)
    log(`Feed:         ${d.feedDescription}`)
    log(`Feed Address: ${d.feedAddress}`)
    log(`Condition:    ${d.condition}`)
    log(`Strike Price: ${d.strikePriceFormatted}`)
    log(`Current:      ${d.currentPriceFormatted}`)
    if (d.settlementPriceFormatted) log(`Settlement:   ${d.settlementPriceFormatted}`)
    log("")
  })
}
