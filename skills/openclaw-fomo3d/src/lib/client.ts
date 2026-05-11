import { createPublicClient, createWalletClient, http } from "viem"
import { privateKeyToAccount } from "viem/accounts"
import { bsc, bscTestnet } from "viem/chains"
import { RPC_URLS } from "./config.js"

function getChain(network: "testnet" | "mainnet") {
  return network === "mainnet" ? bsc : bscTestnet
}

export function getPublicClient(network: "testnet" | "mainnet", rpcUrl?: string) {
  return createPublicClient({
    chain: getChain(network),
    transport: http(rpcUrl ?? RPC_URLS[network]),
  })
}

export function getWalletClient(privateKey: `0x${string}`, network: "testnet" | "mainnet", rpcUrl?: string) {
  const account = privateKeyToAccount(privateKey)
  return createWalletClient({
    account,
    chain: getChain(network),
    transport: http(rpcUrl ?? RPC_URLS[network]),
  })
}
