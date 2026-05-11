import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mkdirSync, rmSync, writeFileSync, existsSync, statSync, readFileSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import { execFileSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// sodium-native and bip39-mnemonic are CJS; load via createRequire
import { createRequire } from 'module';
const require = createRequire(import.meta.url);

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const CREATE_WALLET_SCRIPT = join(__dirname, '..', 'create-wallet.js');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function runCreateWallet(args, { expectSuccess = true } = {}) {
  try {
    const output = execFileSync(process.execPath, [CREATE_WALLET_SCRIPT, ...args], {
      encoding: 'utf8',
      env: { ...process.env },
    });
    if (!expectSuccess) {
      throw new Error(`Expected failure but succeeded with output: ${output}`);
    }
    return { stdout: output, exitCode: 0 };
  } catch (err) {
    if (expectSuccess) {
      throw err;
    }
    return {
      stdout: err.stdout || '',
      stderr: err.stderr || '',
      exitCode: err.status || 1,
    };
  }
}

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

let testDir;

beforeEach(() => {
  testDir = join(
    tmpdir(),
    `create-wallet-test-${Date.now()}-${Math.random().toString(36).slice(2)}`,
  );
  mkdirSync(testDir, { recursive: true });
});

afterEach(() => {
  rmSync(testDir, { recursive: true, force: true });
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('create-wallet.js', () => {
  it('creates vault file and outputs valid Ethereum address', () => {
    const passwordFile = join(testDir, '.wdk_password');
    const vaultFile = join(testDir, '.wdk_vault');
    writeFileSync(passwordFile, 'my-strong-password-123');

    const { stdout } = runCreateWallet([
      '--password-file', passwordFile,
      '--vault-file', vaultFile,
    ]);

    const result = JSON.parse(stdout);
    expect(result).toHaveProperty('address');
    expect(result).toHaveProperty('vaultFile');
    expect(result.address).toMatch(/^0x[0-9a-fA-F]{40}$/);
    expect(result.vaultFile).toBe(vaultFile);
    expect(existsSync(vaultFile)).toBe(true);
  });

  it('vault file has correct JSON structure', () => {
    const passwordFile = join(testDir, '.wdk_password');
    const vaultFile = join(testDir, '.wdk_vault');
    writeFileSync(passwordFile, 'my-strong-password-123');

    runCreateWallet([
      '--password-file', passwordFile,
      '--vault-file', vaultFile,
    ]);

    const vault = JSON.parse(readFileSync(vaultFile, 'utf8'));
    expect(vault).toHaveProperty('encryptedEntropy');
    expect(vault).toHaveProperty('salt');
    expect(typeof vault.encryptedEntropy).toBe('string');
    expect(typeof vault.salt).toBe('string');
    // salt should be 16 bytes = 32 hex chars
    expect(vault.salt).toHaveLength(32);
  });

  it('errors if vault already exists without --force', () => {
    const passwordFile = join(testDir, '.wdk_password');
    const vaultFile = join(testDir, '.wdk_vault');
    writeFileSync(passwordFile, 'my-strong-password-123');
    writeFileSync(vaultFile, '{}'); // pre-existing vault

    const result = runCreateWallet([
      '--password-file', passwordFile,
      '--vault-file', vaultFile,
    ], { expectSuccess: false });

    expect(result.exitCode).not.toBe(0);
    expect(result.stderr).toMatch(/already exists/i);
  });

  it('overwrites existing vault with --force', () => {
    const passwordFile = join(testDir, '.wdk_password');
    const vaultFile = join(testDir, '.wdk_vault');
    writeFileSync(passwordFile, 'my-strong-password-123');
    writeFileSync(vaultFile, '{}'); // pre-existing vault

    const { stdout } = runCreateWallet([
      '--password-file', passwordFile,
      '--vault-file', vaultFile,
      '--force',
    ]);

    const result = JSON.parse(stdout);
    expect(result.address).toMatch(/^0x[0-9a-fA-F]{40}$/);
  });

  it('errors if password is too short (< 12 characters)', () => {
    const passwordFile = join(testDir, '.wdk_password');
    const vaultFile = join(testDir, '.wdk_vault');
    writeFileSync(passwordFile, 'short');

    const result = runCreateWallet([
      '--password-file', passwordFile,
      '--vault-file', vaultFile,
    ], { expectSuccess: false });

    expect(result.exitCode).not.toBe(0);
    expect(result.stderr).toMatch(/password/i);
  });

  it('vault is decryptable by signer.js (round-trip test)', async () => {
    const passwordFile = join(testDir, '.wdk_password');
    const vaultFile = join(testDir, '.wdk_vault');
    const password = 'my-strong-password-123';
    writeFileSync(passwordFile, password);

    const { stdout } = runCreateWallet([
      '--password-file', passwordFile,
      '--vault-file', vaultFile,
    ]);

    const { address: createdAddress } = JSON.parse(stdout);

    // Now use signer.js to decrypt the vault and verify we get the same address
    const { createSigner } = await import('../signer.js');
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
    expect(wallet.address.toLowerCase()).toBe(createdAddress.toLowerCase());
  });

  it('sets vault file permissions to 600', () => {
    const passwordFile = join(testDir, '.wdk_password');
    const vaultFile = join(testDir, '.wdk_vault');
    writeFileSync(passwordFile, 'my-strong-password-123');

    runCreateWallet([
      '--password-file', passwordFile,
      '--vault-file', vaultFile,
    ]);

    const stat = statSync(vaultFile);
    // mode & 0o777 should be 0o600
    expect(stat.mode & 0o777).toBe(0o600);
  });
});
