import readline from "readline"
import { readConfig, writeConfig } from "../lib/config.js"
import { log, output } from "../lib/output.js"

function question(rl: readline.Interface, prompt: string): Promise<string> {
  return new Promise((resolve) => rl.question(prompt, resolve))
}

export async function setup(_args: string[]) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })

  try {
    const existing = readConfig()
    log("\n=== Fomo3D Setup ===\n")

    // 私钥
    const currentKey = existing.privateKey ? `${existing.privateKey.slice(0, 6)}...${existing.privateKey.slice(-4)}` : "(not set)"
    log(`Current private key: ${currentKey}`)
    const keyInput = (await question(rl, "Private key (Enter to keep current): ")).trim()
    const privateKey = keyInput || existing.privateKey

    // 网络
    log(`\nCurrent network: ${existing.network}`)
    const netInput = (await question(rl, "Network (testnet/mainnet, Enter to keep): ")).trim()
    const network = (netInput === "testnet" || netInput === "mainnet") ? netInput : existing.network

    // RPC URL
    log(`\nCurrent RPC URL: ${existing.rpcUrl ?? "(default)"}`)
    const rpcInput = (await question(rl, "Custom RPC URL (Enter for default): ")).trim()
    const rpcUrl = rpcInput || existing.rpcUrl

    const config = { privateKey, network, ...(rpcUrl ? { rpcUrl } : {}) }
    writeConfig(config)

    output({ network, hasPrivateKey: !!privateKey, rpcUrl: rpcUrl ?? "default" }, (d) => {
      log(`\nConfiguration saved to config.json`)
      log(`  Network: ${d.network}`)
      log(`  Private key: ${d.hasPrivateKey ? "configured" : "not set"}`)
      log(`  RPC URL: ${d.rpcUrl}`)
      log(`\nRun 'fomo3d wallet' to check your balance.\n`)
    })
  } finally {
    rl.close()
  }
}
