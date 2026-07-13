#!/usr/bin/env node

import { connectApi, disconnectApi, disconnectEvmProvider, resolveNetwork, isMainnet } from './lib/network.js'
import { createWallet, importWallet, listWallets, loadWallet, getWalletInfo, loadEvmAddress, loadEvmPrivateKey } from './lib/wallet.js'
import { queryBalance } from './lib/balance.js'
import { queryEvmBalance } from './lib/evm-balance.js'
import { transferTokens } from './lib/transfer.js'
import { submitRemark } from './lib/remark.js'
import { connectEvmProvider, createEvmSigner, getMemoryChainContract } from './lib/evm.js'
import { anchorCid, getHeadCid } from './lib/memory-chain.js'
import { fundEvm, withdrawToConsensus } from './lib/xdm.js'
import { transferEvmTokens } from './lib/evm-transfer.js'
import { normalizeEvmAddress, isConsensusAddress, isEvmAddress } from './lib/address.js'
import { parseArgs, validateAmount as validateAmountOrThrow } from './lib/cli.js'

function output(data: unknown): void {
  console.log(JSON.stringify(data, null, 2))
}

function error(message: string, code = 1): never {
  console.error(JSON.stringify({ error: message }))
  process.exit(code)
}

/**
 * Validate an amount, exiting on failure.
 * Wraps the throwing validateAmount from lib/cli.ts.
 */
function validateAmount(amount: string, minimum?: number): void {
  try {
    validateAmountOrThrow(amount, minimum)
  } catch (err) {
    error(err instanceof Error ? err.message : String(err))
  }
}

async function handleWallet(subcommand: string | undefined, flags: Record<string, string>): Promise<void> {
  switch (subcommand) {
    case 'create': {
      const name = flags.name || 'default'
      const result = await createWallet(name, flags.passphrase)
      // Output mnemonic to stderr so it's visible to the user but separable from JSON output
      console.error('')
      console.error('=== IMPORTANT: BACKUP YOUR RECOVERY PHRASE ===')
      console.error('')
      console.error(`  ${result.mnemonic}`)
      console.error('')
      console.error('Write these 12 words down and store them securely.')
      console.error('This is the ONLY time they will be displayed.')
      console.error('Anyone with these words can access your wallet.')
      console.error('')
      console.error('===============================================')
      console.error('')
      output({
        name: result.name,
        address: result.address,
        evmAddress: result.evmAddress,
        keyfilePath: result.keyfilePath,
      })
      break
    }

    case 'import': {
      const name = flags.name
      const mnemonic = flags.mnemonic
      if (!name) error('--name is required for wallet import')
      if (!mnemonic) error('--mnemonic is required for wallet import')
      const result = await importWallet(name, mnemonic, flags.passphrase)
      output(result)
      break
    }

    case 'list': {
      const wallets = await listWallets()
      output({ wallets })
      break
    }

    case 'info': {
      const name = flags.name || 'default'
      const info = await getWalletInfo(name)
      output(info)
      break
    }

    default:
      error(`Unknown wallet subcommand: "${subcommand}". Use: create, import, list, info`)
  }
}

async function handleBalance(flags: Record<string, string>, positional: string[]): Promise<void> {
  const target = positional[0] || flags.address || flags.name
  if (!target) error('Address or wallet name is required. Usage: balance <address-or-wallet> [--network chronos|mainnet]')

  const network = resolveNetwork(flags.network)

  let address: string
  if (isEvmAddress(target)) {
    error('EVM addresses are not supported for consensus balance. Use evm-balance instead, or use balances <wallet> for both.')
  } else if (isConsensusAddress(target)) {
    address = target
  } else {
    const info = await getWalletInfo(target)
    address = info.address
  }

  const api = await connectApi(network)

  try {
    const result = await queryBalance(api, address, network)
    output(result)
  } finally {
    await disconnectApi(api)
  }
}

async function handleTransfer(flags: Record<string, string>): Promise<void> {
  const from = flags.from
  const to = flags.to
  const amount = flags.amount

  if (!from) error('--from <wallet-name> is required')
  if (!to) error('--to <address> is required')
  if (!amount) error('--amount <tokens> is required')
  validateAmount(amount)

  const network = resolveNetwork(flags.network)
  const pair = await loadWallet(from)
  const api = await connectApi(network)

  try {
    const result = await transferTokens(api, pair, to, amount, network)
    output(result)
  } finally {
    await disconnectApi(api)
  }
}

async function handleRemark(flags: Record<string, string>): Promise<void> {
  const from = flags.from
  const data = flags.data

  if (!from) error('--from <wallet-name> is required')
  if (!data) error('--data <string> is required')

  const network = resolveNetwork(flags.network)
  const pair = await loadWallet(from)
  const api = await connectApi(network)

  try {
    const result = await submitRemark(api, pair, data, network)
    output(result)
  } finally {
    await disconnectApi(api)
  }
}

async function handleAnchor(flags: Record<string, string>): Promise<void> {
  const from = flags.from
  const cid = flags.cid

  if (!from) error('--from <wallet-name> is required')
  if (!cid) error('--cid <cid-string> is required')

  const network = resolveNetwork(flags.network)

  // Load EVM private key from wallet (requires passphrase)
  const { privateKey, address: evmAddress } = await loadEvmPrivateKey(from)

  // Connect to Auto-EVM
  const provider = connectEvmProvider(network)

  try {
    const signer = createEvmSigner(privateKey, provider)
    const contract = getMemoryChainContract(signer, network)
    const result = await anchorCid(contract, cid, evmAddress, network)

    if (isMainnet(network)) {
      result.warning = 'This was a mainnet transaction on Auto-EVM with real AI3 tokens.'
    }

    output(result)
  } finally {
    await disconnectEvmProvider(provider)
  }
}

async function handleGetHead(flags: Record<string, string>, positional: string[]): Promise<void> {
  const target = positional[0] || flags.address || flags.name

  if (!target) {
    error('Address or wallet name is required. Usage: gethead <0x-address-or-wallet-name> [--network chronos|mainnet]')
  }

  const network = resolveNetwork(flags.network)

  let evmAddress: string
  if (isEvmAddress(target)) {
    evmAddress = normalizeEvmAddress(target)
  } else {
    evmAddress = await loadEvmAddress(target)
  }

  // Connect to Auto-EVM (read-only — no signer needed)
  const provider = connectEvmProvider(network)

  try {
    const contract = getMemoryChainContract(provider, network)
    const result = await getHeadCid(contract, evmAddress, network)
    output(result)
  } finally {
    await disconnectEvmProvider(provider)
  }
}

async function handleFundEvm(flags: Record<string, string>): Promise<void> {
  const from = flags.from
  const amount = flags.amount

  if (!from) error('--from <wallet-name> is required')
  if (!amount) error('--amount <tokens> is required (amount in AI3/tAI3)')
  validateAmount(amount, 1)

  const network = resolveNetwork(flags.network)

  // Load both consensus keypair (to sign the XDM extrinsic) and EVM address (destination)
  const pair = await loadWallet(from)
  const evmAddress = await loadEvmAddress(from)

  const api = await connectApi(network)

  try {
    const result = await fundEvm(api, pair, evmAddress, amount, network)
    output(result)
  } finally {
    await disconnectApi(api)
  }
}

async function handleWithdraw(flags: Record<string, string>): Promise<void> {
  const from = flags.from
  const amount = flags.amount

  if (!from) error('--from <wallet-name> is required')
  if (!amount) error('--amount <tokens> is required (amount in AI3/tAI3)')
  validateAmount(amount, 1)

  const network = resolveNetwork(flags.network)

  // Load EVM private key (to sign the precompile tx) and wallet info (for consensus address)
  const { privateKey } = await loadEvmPrivateKey(from)
  const info = await getWalletInfo(from)

  const provider = connectEvmProvider(network)

  try {
    const signer = createEvmSigner(privateKey, provider)
    const result = await withdrawToConsensus(signer, info.address, amount, network)
    output(result)
  } finally {
    await disconnectEvmProvider(provider)
  }
}

async function handleEvmTransfer(flags: Record<string, string>): Promise<void> {
  const from = flags.from
  const to = flags.to
  const amount = flags.amount

  if (!from) error('--from <wallet-name> is required')
  if (!to) error('--to <0x-address> is required')
  if (!amount) error('--amount <tokens> is required')
  validateAmount(amount)

  const network = resolveNetwork(flags.network)

  // Validate destination is an EVM address
  const toAddress = normalizeEvmAddress(to)

  // Load EVM private key from wallet (requires passphrase)
  const { privateKey } = await loadEvmPrivateKey(from)

  const provider = connectEvmProvider(network)

  try {
    const signer = createEvmSigner(privateKey, provider)
    const result = await transferEvmTokens(signer, toAddress, amount, network)
    output(result)
  } finally {
    await disconnectEvmProvider(provider)
  }
}

async function handleBalances(flags: Record<string, string>, positional: string[]): Promise<void> {
  const target = positional[0] || flags.name
  if (!target) error('Wallet name is required. Usage: balances <wallet-name> [--network chronos|mainnet]')

  const network = resolveNetwork(flags.network)
  const info = await getWalletInfo(target)

  // Query both balances concurrently.
  // Both connections are created inside the try block so the finally
  // block can clean them up even if the second connection fails.
  let api: Awaited<ReturnType<typeof connectApi>> | undefined
  let provider: ReturnType<typeof connectEvmProvider> | undefined

  try {
    api = await connectApi(network)
    provider = connectEvmProvider(network)

    const [consensus, evm] = await Promise.all([
      queryBalance(api, info.address, network),
      queryEvmBalance(provider, info.evmAddress, network),
    ])

    output({
      name: target,
      consensus: {
        address: consensus.address,
        free: consensus.free,
        reserved: consensus.reserved,
        total: consensus.total,
      },
      evm: {
        address: evm.evmAddress,
        balance: evm.balance,
      },
      network,
      symbol: consensus.symbol,
    })
  } finally {
    if (api) await disconnectApi(api)
    if (provider) await disconnectEvmProvider(provider)
  }
}

async function handleEvmBalance(flags: Record<string, string>, positional: string[]): Promise<void> {
  const target = positional[0] || flags.address || flags.name

  if (!target) {
    error('EVM address or wallet name is required. Usage: evm-balance <0x-address-or-wallet-name> [--network chronos|mainnet]')
  }

  const network = resolveNetwork(flags.network)

  let evmAddress: string
  if (isEvmAddress(target)) {
    evmAddress = normalizeEvmAddress(target)
  } else {
    evmAddress = await loadEvmAddress(target)
  }

  const provider = connectEvmProvider(network)

  try {
    const result = await queryEvmBalance(provider, evmAddress, network)
    output(result)
  } finally {
    await disconnectEvmProvider(provider)
  }
}

function printUsage(): void {
  console.error(`auto-respawn — Anchor agent identity on the Autonomys Network

Commands:
  wallet create [--name <name>]                          Create a new wallet
  wallet import --name <name> --mnemonic "<words>"       Import from recovery phrase
  wallet list                                            List saved wallets
  wallet info [--name <name>]                            Show wallet addresses (consensus + EVM)

  balance <address-or-wallet> [--network chronos|mainnet] Check consensus balance
  evm-balance <0x-addr-or-wallet> [--network ...]        Check Auto-EVM balance
  balances <wallet-name> [--network chronos|mainnet]     Check both consensus + EVM balances

  transfer --from <wallet> --to <address> --amount <n>   Transfer tokens (consensus)
           [--network chronos|mainnet]

  evm-transfer --from <wallet> --to <0x-addr>            Transfer tokens (Auto-EVM)
               --amount <n> [--network chronos|mainnet]

  fund-evm --from <wallet> --amount <n>                  Bridge tokens: consensus → Auto-EVM
           [--network chronos|mainnet]

  withdraw --from <wallet> --amount <n>                  Bridge tokens: Auto-EVM → consensus
           [--network chronos|mainnet]

  remark --from <wallet> --data <string>                 Write on-chain remark
         [--network chronos|mainnet]

  anchor --from <wallet> --cid <cid>                     Anchor a CID on the MemoryChain contract
         [--network chronos|mainnet]

  gethead <0x-address-or-wallet-name>                    Read last anchored CID
          [--network chronos|mainnet]

Environment:
  AUTO_RESPAWN_PASSPHRASE       Wallet encryption passphrase
  AUTO_RESPAWN_PASSPHRASE_FILE  Path to passphrase file
  AUTO_RESPAWN_NETWORK          Default network (chronos|mainnet)`)
}

async function main(): Promise<void> {
  const { command, subcommand, flags, positional } = parseArgs(process.argv)

  try {
    switch (command) {
      case 'wallet':
        await handleWallet(subcommand, flags)
        break
      case 'balance':
        await handleBalance(flags, positional)
        break
      case 'balances':
        await handleBalances(flags, positional)
        break
      case 'evm-balance':
        await handleEvmBalance(flags, positional)
        break
      case 'transfer':
        await handleTransfer(flags)
        break
      case 'evm-transfer':
        await handleEvmTransfer(flags)
        break
      case 'fund-evm':
        await handleFundEvm(flags)
        break
      case 'withdraw':
        await handleWithdraw(flags)
        break
      case 'remark':
        await handleRemark(flags)
        break
      case 'anchor':
        await handleAnchor(flags)
        break
      case 'gethead':
        await handleGetHead(flags, positional)
        break
      case 'help':
      case '--help':
      case '-h':
      case '':
        printUsage()
        break
      default:
        error(`Unknown command: "${command}". Run with --help for usage.`)
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    error(message)
  }
}

// Catch unhandled rejections (e.g. from RPC errors)
process.on('unhandledRejection', (err) => {
  const message = err instanceof Error ? err.message : String(err)
  error(message)
})

main()
