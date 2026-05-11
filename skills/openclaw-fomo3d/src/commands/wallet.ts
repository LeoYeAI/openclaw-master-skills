import { formatEther, type Address } from "viem"
import { readConfig, requirePrivateKey, getDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { FOMO3D_ABI, ERC20_ABI } from "../lib/contracts.js"
import { getTokenBalance } from "../lib/erc20.js"
import { output, log } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

export async function wallet(args: string[]) {
  const config = readConfig()
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const diamond = getDiamondAddress(config)

  // 确定地址：--address 参数 或 从私钥推导
  let address: Address
  const addrArg = getFlagValue(args, "--address")
  if (addrArg) {
    address = addrArg as Address
  } else {
    const pk = requirePrivateKey(config)
    const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
    address = walletClient.account!.address
  }

  // 获取 token 地址
  const gameConfig = await publicClient.readContract({
    address: diamond,
    abi: FOMO3D_ABI,
    functionName: "getConfig",
  }) as [Address, ...unknown[]]
  const tokenAddress = gameConfig[0]

  // 并行查询
  const [bnbBalance, tokenBalance, tokenSymbol, tokenDecimals] = await Promise.all([
    publicClient.getBalance({ address }),
    getTokenBalance(publicClient, tokenAddress, address),
    publicClient.readContract({ address: tokenAddress, abi: ERC20_ABI, functionName: "symbol" }) as Promise<string>,
    publicClient.readContract({ address: tokenAddress, abi: ERC20_ABI, functionName: "decimals" }) as Promise<number>,
  ])

  const data = {
    address,
    network: config.network,
    bnb: formatEther(bnbBalance),
    bnbWei: bnbBalance.toString(),
    token: {
      address: tokenAddress,
      symbol: tokenSymbol,
      decimals: tokenDecimals,
      balance: tokenBalance.toString(),
      formatted: formatEther(tokenBalance),
    },
  }

  output(data, (d) => {
    log(`\n=== Wallet (${d.network}) ===`)
    log(`Address:  ${d.address}`)
    log(`BNB:      ${d.bnb}`)
    log(`${d.token.symbol}:  ${d.token.formatted}`)
    log("")
  })
}
