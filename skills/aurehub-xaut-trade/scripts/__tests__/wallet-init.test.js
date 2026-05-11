/**
 * wallet-init.test.js — Simulate wallet initialization and mode switching.
 *
 * Tests:
 *   1. WDK vault creation → decrypt → derive same address (round-trip)
 *   2. createSigner() with WDK mode
 *   3. createSigner() with Foundry mode (using ethers-generated keystore)
 *   4. Mode switching: WDK → Foundry → WDK (same config object, different WALLET_MODE)
 *   5. Error paths: missing WALLET_MODE, unknown mode, bad password, missing vault
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { mkdtempSync, writeFileSync, mkdirSync, readFileSync, rmSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import { execFileSync } from 'child_process';
import { Wallet } from 'ethers6';

const SCRIPTS_DIR = join(import.meta.dirname, '..');
const CREATE_WALLET = join(SCRIPTS_DIR, 'lib', 'create-wallet.js');

describe('wallet initialization & mode switching', () => {
  let tmpDir;
  let wdkPasswordFile;
  let wdkVaultFile;
  let foundryKeystoreDir;
  let foundryPasswordFile;
  let wdkAddress;
  let foundryAddress;

  const WDK_PASSWORD = 'test-password-long-enough';
  const FOUNDRY_PASSWORD = 'foundry-pw-12chars';
  const FOUNDRY_ACCOUNT = 'test-account';

  beforeAll(async () => {
    tmpDir = mkdtempSync(join(tmpdir(), 'wallet-init-test-'));

    // --- WDK setup ---
    wdkPasswordFile = join(tmpDir, '.wdk_password');
    wdkVaultFile = join(tmpDir, '.wdk_vault');
    writeFileSync(wdkPasswordFile, WDK_PASSWORD, { mode: 0o600 });

    // Create WDK vault via create-wallet.js CLI
    const out = execFileSync('node', [
      CREATE_WALLET,
      '--password-file', wdkPasswordFile,
      '--vault-file', wdkVaultFile,
    ], { encoding: 'utf8', cwd: SCRIPTS_DIR });

    const result = JSON.parse(out.trim());
    wdkAddress = result.address;
    expect(wdkAddress).toMatch(/^0x[0-9a-fA-F]{40}$/);

    // --- Foundry keystore setup (simulate with ethers) ---
    foundryKeystoreDir = join(tmpDir, 'keystores');
    mkdirSync(foundryKeystoreDir, { recursive: true });
    foundryPasswordFile = join(tmpDir, '.foundry_password');
    writeFileSync(foundryPasswordFile, FOUNDRY_PASSWORD, { mode: 0o600 });

    const foundryWallet = Wallet.createRandom();
    foundryAddress = foundryWallet.address;
    const keystoreJson = await foundryWallet.encrypt(FOUNDRY_PASSWORD);
    writeFileSync(join(foundryKeystoreDir, FOUNDRY_ACCOUNT), keystoreJson);
  });

  afterAll(() => {
    if (tmpDir) rmSync(tmpDir, { recursive: true, force: true });
  });

  // -----------------------------------------------------------------------
  // 1. WDK round-trip: create → decrypt → same address
  // -----------------------------------------------------------------------

  it('WDK: vault round-trip produces consistent address', async () => {
    const { createSigner } = await import('../lib/signer.js');

    const cfg = {
      env: {
        WALLET_MODE: 'wdk',
        WDK_VAULT_FILE: wdkVaultFile,
        WDK_PASSWORD_FILE: wdkPasswordFile,
      },
    };

    const wallet = await createSigner(cfg, null);
    expect(wallet.address).toBe(wdkAddress);
  });

  // -----------------------------------------------------------------------
  // 2. Foundry mode: keystore decrypt → correct address
  // -----------------------------------------------------------------------

  it('Foundry: keystore decrypt produces correct address', async () => {
    const { createSigner } = await import('../lib/signer.js');

    const cfg = {
      env: {
        WALLET_MODE: 'foundry',
        FOUNDRY_ACCOUNT: FOUNDRY_ACCOUNT,
        KEYSTORE_PASSWORD_FILE: foundryPasswordFile,
      },
    };

    const wallet = await createSigner(cfg, null, { keystoreDir: foundryKeystoreDir });
    expect(wallet.address).toBe(foundryAddress);
  });

  // -----------------------------------------------------------------------
  // 3. Mode switching: WDK → Foundry → WDK
  // -----------------------------------------------------------------------

  it('switches from WDK to Foundry and back', async () => {
    const { createSigner } = await import('../lib/signer.js');

    // Start with WDK
    const wdkCfg = {
      env: {
        WALLET_MODE: 'wdk',
        WDK_VAULT_FILE: wdkVaultFile,
        WDK_PASSWORD_FILE: wdkPasswordFile,
      },
    };
    const w1 = await createSigner(wdkCfg, null);
    expect(w1.address).toBe(wdkAddress);

    // Switch to Foundry (simulates user changing WALLET_MODE in .env)
    const foundryCfg = {
      env: {
        WALLET_MODE: 'foundry',
        FOUNDRY_ACCOUNT: FOUNDRY_ACCOUNT,
        KEYSTORE_PASSWORD_FILE: foundryPasswordFile,
      },
    };
    const w2 = await createSigner(foundryCfg, null, { keystoreDir: foundryKeystoreDir });
    expect(w2.address).toBe(foundryAddress);
    expect(w2.address).not.toBe(w1.address); // different wallets

    // Switch back to WDK
    const w3 = await createSigner(wdkCfg, null);
    expect(w3.address).toBe(wdkAddress);
    expect(w3.address).toBe(w1.address); // same wallet as before
  });

  // -----------------------------------------------------------------------
  // 4. Config loader integration: loadConfig → createSigner
  // -----------------------------------------------------------------------

  it('loadConfig + createSigner integration for WDK', async () => {
    const { loadConfig } = await import('../lib/config.js');
    const { createSigner } = await import('../lib/signer.js');

    // Write a .env in tmpDir
    const envContent = [
      `WALLET_MODE=wdk`,
      `WDK_VAULT_FILE=${wdkVaultFile}`,
      `WDK_PASSWORD_FILE=${wdkPasswordFile}`,
    ].join('\n');
    writeFileSync(join(tmpDir, '.env'), envContent);

    const cfg = loadConfig(tmpDir);
    expect(cfg.env.WALLET_MODE).toBe('wdk');

    const wallet = await createSigner(cfg, null);
    expect(wallet.address).toBe(wdkAddress);
  });

  it('loadConfig + createSigner integration for Foundry', async () => {
    const { loadConfig } = await import('../lib/config.js');
    const { createSigner } = await import('../lib/signer.js');

    const envContent = [
      `WALLET_MODE=foundry`,
      `FOUNDRY_ACCOUNT=${FOUNDRY_ACCOUNT}`,
      `KEYSTORE_PASSWORD_FILE=${foundryPasswordFile}`,
    ].join('\n');
    writeFileSync(join(tmpDir, '.env'), envContent);

    const cfg = loadConfig(tmpDir);
    expect(cfg.env.WALLET_MODE).toBe('foundry');

    const wallet = await createSigner(cfg, null, { keystoreDir: foundryKeystoreDir });
    expect(wallet.address).toBe(foundryAddress);
  });

  // -----------------------------------------------------------------------
  // 5. Error paths
  // -----------------------------------------------------------------------

  describe('error handling', () => {
    it('throws when WALLET_MODE is missing', async () => {
      const { createSigner } = await import('../lib/signer.js');
      await expect(createSigner({ env: {} }, null)).rejects.toThrow(/WALLET_MODE not set/);
    });

    it('throws when WALLET_MODE is empty', async () => {
      const { createSigner } = await import('../lib/signer.js');
      await expect(createSigner({ env: { WALLET_MODE: '' } }, null)).rejects.toThrow(/WALLET_MODE not set/);
    });

    it('throws on unknown wallet mode', async () => {
      const { createSigner } = await import('../lib/signer.js');
      await expect(createSigner({ env: { WALLET_MODE: 'metamask' } }, null)).rejects.toThrow(/Unknown wallet_mode "metamask"/);
    });

    it('throws when WDK vault file is missing', async () => {
      const { createSigner } = await import('../lib/signer.js');
      const cfg = {
        env: {
          WALLET_MODE: 'wdk',
          WDK_VAULT_FILE: join(tmpDir, 'nonexistent_vault'),
          WDK_PASSWORD_FILE: wdkPasswordFile,
        },
      };
      await expect(createSigner(cfg, null)).rejects.toThrow(/vault not found/i);
    });

    it('throws when WDK password is wrong', async () => {
      const { createSigner } = await import('../lib/signer.js');
      const badPwFile = join(tmpDir, '.bad_password');
      writeFileSync(badPwFile, 'wrong-password-here');

      const cfg = {
        env: {
          WALLET_MODE: 'wdk',
          WDK_VAULT_FILE: wdkVaultFile,
          WDK_PASSWORD_FILE: badPwFile,
        },
      };
      await expect(createSigner(cfg, null)).rejects.toThrow(/decryption failed|wrong password/i);
    });

    it('throws when Foundry keystore is missing', async () => {
      const { createSigner } = await import('../lib/signer.js');
      const cfg = {
        env: {
          WALLET_MODE: 'foundry',
          FOUNDRY_ACCOUNT: 'nonexistent-account',
          KEYSTORE_PASSWORD_FILE: foundryPasswordFile,
        },
      };
      await expect(createSigner(cfg, null, { keystoreDir: foundryKeystoreDir })).rejects.toThrow(/keystore not found/i);
    });

    it('throws when Foundry password file is missing', async () => {
      const { createSigner } = await import('../lib/signer.js');
      const cfg = {
        env: {
          WALLET_MODE: 'foundry',
          FOUNDRY_ACCOUNT: FOUNDRY_ACCOUNT,
          KEYSTORE_PASSWORD_FILE: join(tmpDir, 'no-such-file'),
        },
      };
      await expect(createSigner(cfg, null, { keystoreDir: foundryKeystoreDir })).rejects.toThrow(/Cannot read KEYSTORE_PASSWORD_FILE/);
    });

    it('create-wallet.js rejects short password', () => {
      const shortPwFile = join(tmpDir, '.short_pw');
      writeFileSync(shortPwFile, 'short');

      expect(() => {
        execFileSync('node', [
          CREATE_WALLET,
          '--password-file', shortPwFile,
          '--vault-file', join(tmpDir, '.vault_short'),
        ], { encoding: 'utf8', cwd: SCRIPTS_DIR });
      }).toThrow();
    });

    it('create-wallet.js rejects overwrite without --force', () => {
      // wdkVaultFile already exists from beforeAll
      expect(() => {
        execFileSync('node', [
          CREATE_WALLET,
          '--password-file', wdkPasswordFile,
          '--vault-file', wdkVaultFile,
        ], { encoding: 'utf8', cwd: SCRIPTS_DIR });
      }).toThrow();
    });

    it('export-seed.js refuses to run in non-TTY environment', () => {
      const EXPORT_SEED = join(SCRIPTS_DIR, 'lib', 'export-seed.js');
      expect(() => {
        execFileSync('node', [
          EXPORT_SEED,
          '--password-file', wdkPasswordFile,
          '--vault-file', wdkVaultFile,
        ], { encoding: 'utf8', cwd: SCRIPTS_DIR });
      }).toThrow(/interactive terminal/i);
    });

    it('create-wallet.js allows overwrite with --force', () => {
      const out = execFileSync('node', [
        CREATE_WALLET,
        '--password-file', wdkPasswordFile,
        '--vault-file', wdkVaultFile,
        '--force',
      ], { encoding: 'utf8', cwd: SCRIPTS_DIR });

      const result = JSON.parse(out.trim());
      expect(result.address).toMatch(/^0x[0-9a-fA-F]{40}$/);
      // Address will differ since new entropy is generated
    });
  });
});
