import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mkdirSync, rmSync, writeFileSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import { pbkdf2Sync } from 'crypto';
import { BaseWallet, HDNodeWallet, Wallet } from 'ethers6';

import { createSigner } from '../signer.js';

// sodium-native and bip39-mnemonic are CJS; load via createRequire
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const sodium = require('sodium-native');
const b4a = require('b4a');
const bip39 = require('bip39-mnemonic');

// ---------------------------------------------------------------------------
// Helpers to create test fixtures
// ---------------------------------------------------------------------------

/**
 * Encrypt a buffer using the same algorithm as WdkSecretManager.
 * (Replicates WdkSecretManager#encrypt — see signer.js for details.)
 */
function wdkEncrypt(buffer, key) {
  const NONCEBYTES = sodium.crypto_secretbox_NONCEBYTES;
  const MACBYTES = sodium.crypto_secretbox_MACBYTES;
  const buffLength = buffer.byteLength;

  const nonce = b4a.alloc(NONCEBYTES);
  sodium.randombytes_buf(nonce);

  const payload = b4a.alloc(1 + NONCEBYTES + 1 + buffLength + MACBYTES);
  payload[0] = 0; // version
  payload.set(nonce, 1);

  const cipher = payload.subarray(1 + nonce.byteLength);
  const plain = cipher.subarray(0, cipher.byteLength - MACBYTES);
  plain[0] = buffLength;
  plain.set(buffer, 1);

  sodium.crypto_secretbox_easy(cipher, plain, nonce, key);

  return payload;
}

/**
 * Create a minimal WDK vault JSON string for a given password + mnemonic.
 */
function createWdkVault(password, mnemonic) {
  const salt = b4a.alloc(16);
  sodium.randombytes_buf(salt);

  const key = pbkdf2Sync(password, salt, 100_000, 32, 'sha256');

  // Convert mnemonic back to entropy
  const entropy = Buffer.from(bip39.mnemonicToEntropy(mnemonic), 'hex');
  const encryptedEntropy = wdkEncrypt(entropy, key);

  return JSON.stringify({
    encryptedEntropy: encryptedEntropy.toString('hex'),
    salt: salt.toString('hex'),
  });
}

// ---------------------------------------------------------------------------
// Test fixtures
// ---------------------------------------------------------------------------

let testDir;

beforeEach(() => {
  testDir = join(
    tmpdir(),
    `signer-test-${Date.now()}-${Math.random().toString(36).slice(2)}`,
  );
  mkdirSync(testDir, { recursive: true });
});

afterEach(() => {
  rmSync(testDir, { recursive: true, force: true });
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('createSigner', () => {
  it('throws when WALLET_MODE is not set in .env', async () => {
    const cfg = { env: {}, yaml: {}, configDir: testDir };

    await expect(createSigner(cfg, null)).rejects.toThrow(
      /WALLET_MODE not set in \.env/i,
    );
  });

  it('throws for unknown wallet_mode', async () => {
    const cfg = { env: { WALLET_MODE: 'ledger' }, yaml: {}, configDir: testDir };

    await expect(createSigner(cfg, null)).rejects.toThrow(
      /unknown wallet_mode/i,
    );
  });

  describe('foundry mode', () => {
    it('creates a wallet from a Foundry keystore', async () => {
      // Create a random wallet and encrypt its keystore
      const originalWallet = Wallet.createRandom();
      const password = 'test-password-foundry';
      const keystoreJson = await originalWallet.encrypt(password);

      // Write keystore to temp dir using account name
      const accountName = 'test-account';
      const keystoreDir = join(testDir, 'foundry-keystores');
      mkdirSync(keystoreDir, { recursive: true });
      writeFileSync(join(keystoreDir, accountName), keystoreJson);

      // Write password file
      const passwordFile = join(testDir, '.keystore-password');
      writeFileSync(passwordFile, password);

      const cfg = {
        env: {
          WALLET_MODE: 'foundry',
          FOUNDRY_ACCOUNT: accountName,
          KEYSTORE_PASSWORD_FILE: passwordFile,
        },
        yaml: {},
        configDir: testDir,
      };

      const wallet = await createSigner(cfg, null, { keystoreDir });

      // ethers v6 returns HDNodeWallet (a BaseWallet subclass) from both
      // fromEncryptedJson and fromPhrase
      expect(wallet).toBeInstanceOf(BaseWallet);
      expect(wallet.address.toLowerCase()).toBe(
        originalWallet.address.toLowerCase(),
      );
    });

    it('throws when FOUNDRY_ACCOUNT is missing', async () => {
      const cfg = {
        env: { WALLET_MODE: 'foundry' },
        yaml: {},
        configDir: testDir,
      };

      await expect(createSigner(cfg, null)).rejects.toThrow(
        /FOUNDRY_ACCOUNT not set/i,
      );
    });

    it('throws when keystore file does not exist', async () => {
      const passwordFile = join(testDir, '.pass');
      writeFileSync(passwordFile, 'password');

      const cfg = {
        env: {
          WALLET_MODE: 'foundry',
          FOUNDRY_ACCOUNT: 'nonexistent-account',
          KEYSTORE_PASSWORD_FILE: passwordFile,
        },
        yaml: {},
        configDir: testDir,
      };

      await expect(
        createSigner(cfg, null, { keystoreDir: testDir }),
      ).rejects.toThrow(/keystore not found/i);
    });
  });

  describe('wdk mode', () => {
    it('creates a wallet from a WDK encrypted vault', async () => {
      // Create a deterministic mnemonic via a random wallet
      const originalWallet = Wallet.createRandom();
      const mnemonic = originalWallet.mnemonic.phrase;

      const password = 'test-password-wdk';
      const vaultJson = createWdkVault(password, mnemonic);

      // Write vault and password files
      const vaultFile = join(testDir, '.wdk_vault');
      const passwordFile = join(testDir, '.wdk_password');
      writeFileSync(vaultFile, vaultJson);
      writeFileSync(passwordFile, password);

      const cfg = {
        env: {
          WALLET_MODE: 'wdk',
          WDK_VAULT_FILE: vaultFile,
          WDK_PASSWORD_FILE: passwordFile,
        },
        yaml: {},
        configDir: testDir,
      };

      const wallet = await createSigner(cfg, null);

      expect(wallet).toBeInstanceOf(BaseWallet);
      expect(wallet.address.toLowerCase()).toBe(
        originalWallet.address.toLowerCase(),
      );
    });

    it('throws when vault file does not exist', async () => {
      const passwordFile = join(testDir, '.wdk_password');
      writeFileSync(passwordFile, 'password');

      const cfg = {
        env: {
          WALLET_MODE: 'wdk',
          WDK_VAULT_FILE: join(testDir, 'nonexistent.vault'),
          WDK_PASSWORD_FILE: passwordFile,
        },
        yaml: {},
        configDir: testDir,
      };

      await expect(createSigner(cfg, null)).rejects.toThrow(
        /wdk vault not found/i,
      );
    });

    it('throws when decryption fails (wrong password)', async () => {
      const originalWallet = Wallet.createRandom();
      const mnemonic = originalWallet.mnemonic.phrase;

      // Encrypt with one password, decrypt with another
      const vaultJson = createWdkVault('correct-password', mnemonic);

      const vaultFile = join(testDir, '.wdk_vault');
      const passwordFile = join(testDir, '.wdk_password');
      writeFileSync(vaultFile, vaultJson);
      writeFileSync(passwordFile, 'wrong-password');

      const cfg = {
        env: {
          WALLET_MODE: 'wdk',
          WDK_VAULT_FILE: vaultFile,
          WDK_PASSWORD_FILE: passwordFile,
        },
        yaml: {},
        configDir: testDir,
      };

      await expect(createSigner(cfg, null)).rejects.toThrow(
        /decryption failed/i,
      );
    });
  });
});
