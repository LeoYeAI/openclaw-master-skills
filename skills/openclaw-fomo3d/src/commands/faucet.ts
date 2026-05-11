import { readConfig, requirePrivateKey } from "../lib/config.js"
import { getWalletClient } from "../lib/client.js"
import { output, log, fatal } from "../lib/output.js"

// Supabase Edge Function URL（testnet only）
const FAUCET_URL = "https://ukppfcznttdfkqzqxrse.supabase.co/functions/v1/faucet"

export async function faucet(args: string[]) {
  const config = readConfig()

  if (config.network !== "testnet") {
    fatal("Faucet is only available on testnet.")
  }

  const pk = requirePrivateKey(config)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const account = walletClient.account!.address

  log(`Claiming 10000 FOMO tokens for ${account}...`)

  const res = await fetch(FAUCET_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ address: account }),
  })

  const data = await res.json()

  if (!res.ok) {
    if (data.retryAfter) {
      fatal(`Rate limited. Retry in ${Math.ceil(data.retryAfter / 60)} minutes.`)
    }
    fatal(data.error ?? `Faucet error (${res.status})`)
  }

  output({
    txHash: data.txHash,
    amount: data.amount,
    token: data.token,
    account,
  }, (d) => {
    log(`\nFaucet claim successful!`)
    log(`Amount: ${d.amount} FOMO`)
    log(`Tx: ${d.txHash}`)
    log("")
  })
}
