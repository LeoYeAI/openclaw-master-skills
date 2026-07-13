import { readdir, readFile, writeFile, mkdir } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { join, resolve, basename } from 'node:path'
import { createInterface } from 'node:readline'
import { ethers } from 'ethers'
import {
  Keyring,
  cryptoWaitReady,
  generateWallet as sdkGenerateWallet,
  setupWallet as sdkSetupWallet,
  address as formatAddress,
} from '@autonomys/auto-utils'
import type { KeyringPair, KeyringPair$Json } from '@polkadot/keyring/types'
import { deriveEvmKey } from './evm.js'

const WALLETS_DIR = join(
  process.env.HOME || process.env.USERPROFILE || '~',
  '.openclaw',
  'auto-respawn',
  'wallets',
)

const PASSPHRASE_FILE_DEFAULT = join(
  process.env.HOME || process.env.USERPROFILE || '~',
  '.openclaw',
  'auto-respawn',
  '.passphrase',
)

// --- Wallet file format ---

/**
 * auto-respawn wallet file format.
 *
 * Contains two independently encrypted private keys (consensus + EVM),
 * both protected by the same user passphrase but using their respective
 * ecosystem's standard encryption:
 *
 *   - Consensus key: Polkadot keyring JSON via `pair.toJson(passphrase)`
 *   - EVM key: Ethereum V3 Keystore via `ethers.Wallet.encryptSync(passphrase)`
 *
 * The EVM address is stored in plaintext (it's public information).
 */
interface WalletFile {
  /** Standard Polkadot keyring JSON — encrypted consensus keypair */
  keyring: KeyringPair$Json
  /** EVM address derived from the same mnemonic (public, stored for quick lookup) */
  evmAddress: string
  /** Ethereum V3 Keystore JSON — encrypted EVM private key (standard format, compatible with MetaMask/geth) */
  evmKeystore: string
}

export interface WalletInfo {
  name: string
  address: string
  evmAddress: string
  keyfilePath: string
}

export interface CreatedWallet extends WalletInfo {
  mnemonic: string
}

async function ensureWalletsDir(): Promise<void> {
  if (!existsSync(WALLETS_DIR)) {
    await mkdir(WALLETS_DIR, { recursive: true, mode: 0o700 })
  }
}

function keyfilePath(name: string): string {
  const filepath = resolve(WALLETS_DIR, `${basename(name)}.json`)
  if (!filepath.startsWith(WALLETS_DIR)) {
    throw new Error(`Invalid wallet name: "${name}". Wallet names must not contain path separators.`)
  }
  return filepath
}

async function readWalletFile(filepath: string): Promise<WalletFile> {
  const raw = await readFile(filepath, 'utf-8')
  return JSON.parse(raw) as WalletFile
}

export async function resolvePassphrase(passphrase?: string): Promise<string> {
  // 0. Explicit argument (e.g. --passphrase flag)
  if (passphrase) return passphrase

  // 1. Environment variable
  const envPassphrase = process.env.AUTO_RESPAWN_PASSPHRASE
  if (envPassphrase) return envPassphrase

  // 2. Passphrase file
  const passphraseFilePath =
    process.env.AUTO_RESPAWN_PASSPHRASE_FILE || PASSPHRASE_FILE_DEFAULT
  try {
    const contents = await readFile(passphraseFilePath, 'utf-8')
    const trimmed = contents.trim()
    if (trimmed) return trimmed
  } catch {
    // File doesn't exist or can't be read — fall through
  }

  // 3. Interactive stdin prompt
  if (process.stdin.isTTY) {
    return new Promise<string>((resolve, reject) => {
      const rl = createInterface({ input: process.stdin, output: process.stderr })
      rl.question('Passphrase: ', (answer) => {
        rl.close()
        if (!answer) reject(new Error('No passphrase provided'))
        else resolve(answer)
      })
    })
  }

  throw new Error(
    'No passphrase found. Set AUTO_RESPAWN_PASSPHRASE env var, ' +
      'write it to ~/.openclaw/auto-respawn/.passphrase, ' +
      'or run interactively.',
  )
}

/**
 * Encrypt both keys (consensus + EVM) and persist the wallet file.
 *
 * Shared by createWallet and importWallet — any change to the file format,
 * encryption scheme, or stored fields only needs updating here.
 */
async function encryptAndSave(
  pair: KeyringPair,
  mnemonic: string,
  name: string,
  filepath: string,
  passphrase?: string,
): Promise<{ address: string; evmAddress: string }> {
  const resolved = await resolvePassphrase(passphrase)

  // Encrypt consensus key (Polkadot PKCS8: scrypt + XSalsa20-Poly1305)
  const keyringJson = pair.toJson(resolved)
  keyringJson.meta = { ...keyringJson.meta, name, whenCreated: Date.now() }

  // Derive EVM key and encrypt it via ethers V3 Keystore
  const evm = deriveEvmKey(mnemonic)
  const evmWallet = new ethers.Wallet(evm.privateKey)
  const evmKeystore = evmWallet.encryptSync(resolved)

  const walletFile: WalletFile = {
    keyring: keyringJson,
    evmAddress: evm.address,
    evmKeystore,
  }

  await writeFile(filepath, JSON.stringify(walletFile, null, 2), { mode: 0o600 })

  return { address: formatAddress(pair.address), evmAddress: evm.address }
}

export async function createWallet(name: string, passphrase?: string): Promise<CreatedWallet> {
  await cryptoWaitReady()
  await ensureWalletsDir()

  const filepath = keyfilePath(name)
  if (existsSync(filepath)) {
    throw new Error(`Wallet "${name}" already exists at ${filepath}`)
  }

  const wallet = sdkGenerateWallet()
  if (!wallet.keyringPair) throw new Error('Failed to generate wallet keypair')

  const { address, evmAddress } = await encryptAndSave(wallet.keyringPair, wallet.mnemonic, name, filepath, passphrase)

  return { name, address, evmAddress, mnemonic: wallet.mnemonic, keyfilePath: filepath }
}

export async function importWallet(name: string, mnemonic: string, passphrase?: string): Promise<WalletInfo> {
  await cryptoWaitReady()
  await ensureWalletsDir()

  const filepath = keyfilePath(name)
  if (existsSync(filepath)) {
    throw new Error(`Wallet "${name}" already exists at ${filepath}`)
  }

  const wallet = sdkSetupWallet({ mnemonic })
  if (!wallet.keyringPair) throw new Error('Failed to setup wallet keypair from mnemonic')

  const { address, evmAddress } = await encryptAndSave(wallet.keyringPair, mnemonic, name, filepath, passphrase)

  return { name, address, evmAddress, keyfilePath: filepath }
}

export async function listWallets(): Promise<WalletInfo[]> {
  await cryptoWaitReady()

  if (!existsSync(WALLETS_DIR)) return []

  const files = await readdir(WALLETS_DIR)
  const wallets: WalletInfo[] = []

  for (const file of files) {
    if (!file.endsWith('.json')) continue
    try {
      const filepath = join(WALLETS_DIR, file)
      const walletFile = await readWalletFile(filepath)
      const name = (walletFile.keyring.meta?.name as string) || file.replace('.json', '')
      const autonomysAddress = formatAddress(walletFile.keyring.address)
      wallets.push({
        name,
        address: autonomysAddress,
        evmAddress: walletFile.evmAddress,
        keyfilePath: filepath,
      })
    } catch {
      // Skip malformed files
    }
  }

  return wallets
}

/**
 * Load and decrypt a consensus keypair from a saved wallet.
 */
export async function loadWallet(name: string): Promise<KeyringPair> {
  await cryptoWaitReady()

  const filepath = keyfilePath(name)
  if (!existsSync(filepath)) {
    throw new Error(`Wallet "${name}" not found at ${filepath}`)
  }

  const walletFile = await readWalletFile(filepath)

  const keyring = new Keyring({ type: 'sr25519' })
  const pair = keyring.addFromJson(walletFile.keyring)

  const passphrase = await resolvePassphrase()
  try {
    pair.decodePkcs8(passphrase)
  } catch {
    throw new Error('Wrong passphrase — could not decrypt wallet')
  }

  return pair
}

/**
 * Get wallet info (both addresses) without decrypting. No passphrase needed.
 */
export async function getWalletInfo(name: string): Promise<WalletInfo> {
  await cryptoWaitReady()

  const filepath = keyfilePath(name)
  if (!existsSync(filepath)) {
    throw new Error(`Wallet "${name}" not found at ${filepath}`)
  }

  const walletFile = await readWalletFile(filepath)
  const autonomysAddress = formatAddress(walletFile.keyring.address)

  return {
    name,
    address: autonomysAddress,
    evmAddress: walletFile.evmAddress,
    keyfilePath: filepath,
  }
}

/**
 * Load a wallet's EVM address. No passphrase needed (stored in plaintext metadata).
 */
export async function loadEvmAddress(name: string): Promise<string> {
  const info = await getWalletInfo(name)
  return info.evmAddress
}

/**
 * Load and decrypt a wallet's EVM private key. Requires passphrase.
 * Uses ethers.js to decrypt the standard Ethereum V3 Keystore.
 */
export async function loadEvmPrivateKey(name: string): Promise<{ privateKey: string; address: string }> {
  const filepath = keyfilePath(name)
  if (!existsSync(filepath)) {
    throw new Error(`Wallet "${name}" not found at ${filepath}`)
  }

  const walletFile = await readWalletFile(filepath)

  const passphrase = await resolvePassphrase()
  try {
    const evmWallet = ethers.Wallet.fromEncryptedJsonSync(walletFile.evmKeystore, passphrase)
    return { privateKey: evmWallet.privateKey, address: walletFile.evmAddress }
  } catch {
    throw new Error('Wrong passphrase — could not decrypt EVM key')
  }
}
