import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mkdtemp, rm, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { ethers } from 'ethers'
import {
  cryptoWaitReady,
  Keyring,
  address as formatAddress,
} from '@autonomys/auto-utils'

/**
 * Wallet round-trip tests.
 *
 * These create real wallet files in a temp directory, then read them back
 * and verify the keys decrypt correctly. This exercises the full
 * encrypt → persist → read → decrypt path without hitting the network.
 *
 * We call the internal helpers directly rather than going through the
 * public API (createWallet/loadWallet) because those depend on a
 * hard-coded WALLETS_DIR. Instead we replicate the core encrypt/decrypt
 * logic against the same file format.
 */

const TEST_PASSPHRASE = 'test-passphrase-for-roundtrip'
const TEST_MNEMONIC = 'test test test test test test test test test test test junk'

interface WalletFile {
  keyring: { address: string; encoded: string; encoding: unknown; meta: unknown }
  evmAddress: string
  evmKeystore: string
}

describe('wallet file round-trip', () => {
  let tempDir: string

  beforeEach(async () => {
    await cryptoWaitReady()
    tempDir = await mkdtemp(join(tmpdir(), 'auto-respawn-test-'))
  })

  afterEach(async () => {
    await rm(tempDir, { recursive: true, force: true })
  })

  it('encrypts and decrypts a consensus keypair', async () => {
    // Create a keypair from test mnemonic
    const keyring = new Keyring({ type: 'sr25519' })
    const pair = keyring.addFromMnemonic(TEST_MNEMONIC)
    const originalAddress = formatAddress(pair.address)

    // Encrypt and save (replicating encryptAndSave logic)
    const keyringJson = pair.toJson(TEST_PASSPHRASE)
    keyringJson.meta = { ...keyringJson.meta, name: 'test', whenCreated: Date.now() }

    const walletFile: WalletFile = {
      keyring: keyringJson as WalletFile['keyring'],
      evmAddress: '0x0000000000000000000000000000000000000000',
      evmKeystore: '{}',
    }

    const filepath = join(tempDir, 'test.json')
    const { writeFile } = await import('node:fs/promises')
    await writeFile(filepath, JSON.stringify(walletFile, null, 2))

    // Read back and decrypt
    const raw = await readFile(filepath, 'utf-8')
    const loaded = JSON.parse(raw) as WalletFile

    const keyring2 = new Keyring({ type: 'sr25519' })
    const restored = keyring2.addFromJson(loaded.keyring as Parameters<typeof keyring2.addFromJson>[0])
    restored.decodePkcs8(TEST_PASSPHRASE)

    expect(formatAddress(restored.address)).toBe(originalAddress)
    // Verify the restored pair can sign (proves decryption was real)
    const message = new Uint8Array([1, 2, 3, 4])
    const signature = restored.sign(message)
    expect(signature.length).toBeGreaterThan(0)
  })

  it('encrypts and decrypts an EVM private key', async () => {
    // Derive EVM key from mnemonic
    const mnemonicObj = ethers.Mnemonic.fromPhrase(TEST_MNEMONIC)
    const hdWallet = ethers.HDNodeWallet.fromMnemonic(mnemonicObj, "m/44'/60'/0'/0/0")
    const originalKey = hdWallet.privateKey
    const originalAddress = hdWallet.address

    // Encrypt via ethers V3 Keystore
    const evmWallet = new ethers.Wallet(originalKey)
    const evmKeystore = evmWallet.encryptSync(TEST_PASSPHRASE)

    // Write to file
    const filepath = join(tempDir, 'test-evm.json')
    const { writeFile } = await import('node:fs/promises')
    await writeFile(filepath, JSON.stringify({
      keyring: {},
      evmAddress: originalAddress,
      evmKeystore,
    }))

    // Read back and decrypt
    const raw = await readFile(filepath, 'utf-8')
    const loaded = JSON.parse(raw) as WalletFile
    const decrypted = ethers.Wallet.fromEncryptedJsonSync(loaded.evmKeystore, TEST_PASSPHRASE)

    expect(decrypted.privateKey).toBe(originalKey)
    expect(decrypted.address).toBe(originalAddress)
  })

  it('rejects wrong passphrase for consensus key', async () => {
    const keyring = new Keyring({ type: 'sr25519' })
    const pair = keyring.addFromMnemonic(TEST_MNEMONIC)
    const keyringJson = pair.toJson(TEST_PASSPHRASE)

    const keyring2 = new Keyring({ type: 'sr25519' })
    const restored = keyring2.addFromJson(keyringJson as Parameters<typeof keyring2.addFromJson>[0])

    expect(() => restored.decodePkcs8('wrong-passphrase')).toThrow()
  })

  it('rejects wrong passphrase for EVM key', () => {
    const evmWallet = new ethers.Wallet(ethers.Wallet.createRandom().privateKey)
    const keystore = evmWallet.encryptSync(TEST_PASSPHRASE)

    expect(() => ethers.Wallet.fromEncryptedJsonSync(keystore, 'wrong-passphrase')).toThrow()
  })

  it('full round-trip: both keys from same mnemonic match after decrypt', async () => {
    // --- Encrypt both keys (mimics encryptAndSave) ---
    const keyring = new Keyring({ type: 'sr25519' })
    const pair = keyring.addFromMnemonic(TEST_MNEMONIC)
    const keyringJson = pair.toJson(TEST_PASSPHRASE)
    keyringJson.meta = { ...keyringJson.meta, name: 'roundtrip', whenCreated: Date.now() }

    const mnemonicObj = ethers.Mnemonic.fromPhrase(TEST_MNEMONIC)
    const hdWallet = ethers.HDNodeWallet.fromMnemonic(mnemonicObj, "m/44'/60'/0'/0/0")
    const evmWallet = new ethers.Wallet(hdWallet.privateKey)
    const evmKeystore = evmWallet.encryptSync(TEST_PASSPHRASE)

    const walletFile = {
      keyring: keyringJson,
      evmAddress: hdWallet.address,
      evmKeystore,
    }

    const filepath = join(tempDir, 'full-roundtrip.json')
    const { writeFile } = await import('node:fs/promises')
    await writeFile(filepath, JSON.stringify(walletFile, null, 2))

    // --- Read back and decrypt both ---
    const raw = await readFile(filepath, 'utf-8')
    const loaded = JSON.parse(raw) as WalletFile

    // Consensus
    const keyring2 = new Keyring({ type: 'sr25519' })
    const restoredPair = keyring2.addFromJson(loaded.keyring as Parameters<typeof keyring2.addFromJson>[0])
    restoredPair.decodePkcs8(TEST_PASSPHRASE)
    expect(formatAddress(restoredPair.address)).toBe(formatAddress(pair.address))

    // EVM
    const restoredEvm = ethers.Wallet.fromEncryptedJsonSync(loaded.evmKeystore, TEST_PASSPHRASE)
    expect(restoredEvm.address).toBe(hdWallet.address)
    expect(restoredEvm.privateKey).toBe(hdWallet.privateKey)

    // Public EVM address stored in plaintext should match
    expect(loaded.evmAddress).toBe(hdWallet.address)
  })
})
