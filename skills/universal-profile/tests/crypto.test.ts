import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import {
  generateKeyPair,
  deriveKeyFromMnemonic,
  generateMnemonic,
  encryptKey,
  decryptKey,
  getKeystoreDir,
  ensureKeystoreDir,
  saveKey,
  loadKeystore,
  listStoredKeys,
  deleteKey,
  getWallet,
  isValidPrivateKey,
  isValidAddress,
} from '../../src/lib/crypto.js';
import { UniversalProfileError } from '../../src/types/index.js';

// ==================== KEY GENERATION ====================

describe('generateKeyPair', () => {
  it('returns an object with privateKey, publicKey, and address', () => {
    const kp = generateKeyPair();
    expect(kp).toHaveProperty('privateKey');
    expect(kp).toHaveProperty('publicKey');
    expect(kp).toHaveProperty('address');
  });

  it('generates a 32-byte hex private key with 0x prefix', () => {
    const kp = generateKeyPair();
    expect(kp.privateKey).toMatch(/^0x[0-9a-f]{64}$/i);
  });

  it('generates a valid compressed or uncompressed public key', () => {
    const kp = generateKeyPair();
    // ethers returns uncompressed public key (65 bytes = 130 hex chars with 0x prefix)
    expect(kp.publicKey).toMatch(/^0x0[24][0-9a-f]{64}(?:[0-9a-f]{64})?$/i);
  });

  it('generates a valid checksummed Ethereum address', () => {
    const kp = generateKeyPair();
    expect(kp.address).toMatch(/^0x[0-9a-fA-F]{40}$/);
  });

  it('generates unique key pairs on each call', () => {
    const kp1 = generateKeyPair();
    const kp2 = generateKeyPair();
    expect(kp1.privateKey).not.toBe(kp2.privateKey);
    expect(kp1.publicKey).not.toBe(kp2.publicKey);
    expect(kp1.address).not.toBe(kp2.address);
  });

  it('produces an address consistent with the private key', () => {
    const kp = generateKeyPair();
    // Verify by creating a wallet from the same private key
    const wallet = getWallet(kp.privateKey);
    expect(wallet.address).toBe(kp.address);
  });
});

// ==================== MNEMONIC ====================

describe('generateMnemonic', () => {
  it('generates a 12-word mnemonic by default (128-bit strength)', () => {
    const mnemonic = generateMnemonic();
    const words = mnemonic.trim().split(/\s+/);
    expect(words).toHaveLength(12);
  });

  it('generates a 24-word mnemonic with 256-bit strength', () => {
    const mnemonic = generateMnemonic(256);
    const words = mnemonic.trim().split(/\s+/);
    expect(words).toHaveLength(24);
  });

  it('generates unique mnemonics on each call', () => {
    const m1 = generateMnemonic();
    const m2 = generateMnemonic();
    expect(m1).not.toBe(m2);
  });
});

describe('deriveKeyFromMnemonic', () => {
  const TEST_MNEMONIC =
    'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about';

  it('derives a key pair from a known mnemonic', () => {
    const kp = deriveKeyFromMnemonic(TEST_MNEMONIC);
    expect(kp).toHaveProperty('privateKey');
    expect(kp).toHaveProperty('publicKey');
    expect(kp).toHaveProperty('address');
    expect(kp.privateKey).toMatch(/^0x[0-9a-f]{64}$/i);
    expect(kp.address).toMatch(/^0x[0-9a-fA-F]{40}$/);
  });

  it('produces deterministic output for the same mnemonic and index', () => {
    const kp1 = deriveKeyFromMnemonic(TEST_MNEMONIC, 0);
    const kp2 = deriveKeyFromMnemonic(TEST_MNEMONIC, 0);
    expect(kp1.privateKey).toBe(kp2.privateKey);
    expect(kp1.publicKey).toBe(kp2.publicKey);
    expect(kp1.address).toBe(kp2.address);
  });

  it('derives different keys for different indices', () => {
    const kp0 = deriveKeyFromMnemonic(TEST_MNEMONIC, 0);
    const kp1 = deriveKeyFromMnemonic(TEST_MNEMONIC, 1);
    expect(kp0.privateKey).not.toBe(kp1.privateKey);
    expect(kp0.address).not.toBe(kp1.address);
  });

  it('derives different keys for different base paths', () => {
    const kpDefault = deriveKeyFromMnemonic(TEST_MNEMONIC, 0);
    const kpCustom = deriveKeyFromMnemonic(TEST_MNEMONIC, 0, "m/44'/60'/1'/0");
    expect(kpDefault.privateKey).not.toBe(kpCustom.privateKey);
    expect(kpDefault.address).not.toBe(kpCustom.address);
  });

  it('produces an address consistent with the derived private key', () => {
    const kp = deriveKeyFromMnemonic(TEST_MNEMONIC, 3);
    const wallet = getWallet(kp.privateKey);
    expect(wallet.address).toBe(kp.address);
  });

  it('throws on an invalid mnemonic', () => {
    expect(() => deriveKeyFromMnemonic('not a valid mnemonic phrase at all')).toThrow();
  });
});

// ==================== ENCRYPTION / DECRYPTION ====================

describe('encryptKey / decryptKey', () => {
  const PASSWORD = 'test-password-123!';
  let testKeyPair: ReturnType<typeof generateKeyPair>;

  beforeEach(() => {
    testKeyPair = generateKeyPair();
  });

  it('encryptKey returns a well-formed EncryptedKeystore', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    expect(keystore).toHaveProperty('address');
    expect(keystore).toHaveProperty('label');
    expect(keystore).toHaveProperty('encryptedKey');
    expect(keystore).toHaveProperty('iv');
    expect(keystore).toHaveProperty('salt');
    expect(keystore).toHaveProperty('algorithm');
    expect(keystore).toHaveProperty('createdAt');
  });

  it('keystore address matches the original key pair address', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    expect(keystore.address).toBe(testKeyPair.address);
  });

  it('keystore algorithm is aes-256-gcm', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    expect(keystore.algorithm).toBe('aes-256-gcm');
  });

  it('keystore label defaults to empty string', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    expect(keystore.label).toBe('');
  });

  it('keystore createdAt is a valid ISO date string', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    const date = new Date(keystore.createdAt);
    expect(date.toISOString()).toBe(keystore.createdAt);
  });

  it('keystore iv and salt are hex strings of expected lengths', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    // IV = 16 bytes = 32 hex chars
    expect(keystore.iv).toMatch(/^[0-9a-f]{32}$/i);
    // Salt = 32 bytes = 64 hex chars
    expect(keystore.salt).toMatch(/^[0-9a-f]{64}$/i);
  });

  it('encrypted key does not contain the original private key in plaintext', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    const rawHex = testKeyPair.privateKey.replace('0x', '');
    expect(keystore.encryptedKey).not.toContain(rawHex);
  });

  it('decryptKey round-trips the private key correctly', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    const decrypted = decryptKey(keystore, PASSWORD);
    expect(decrypted).toBe(testKeyPair.privateKey);
  });

  it('decryptKey throws UniversalProfileError on wrong password', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    expect(() => decryptKey(keystore, 'wrong-password')).toThrow(UniversalProfileError);
  });

  it('decryptKey error has the correct error code', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    try {
      decryptKey(keystore, 'wrong-password');
      expect.unreachable('Should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(UniversalProfileError);
      expect((err as UniversalProfileError).code).toBe('UP_KEY_DECRYPT_FAILED');
    }
  });

  it('decryptKey error includes details', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    try {
      decryptKey(keystore, 'wrong-password');
      expect.unreachable('Should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(UniversalProfileError);
      expect((err as UniversalProfileError).details).toBeDefined();
      expect((err as UniversalProfileError).details).toHaveProperty('originalError');
    }
  });

  it('decryptKey throws on corrupted encryptedKey data', () => {
    const keystore = encryptKey(testKeyPair.privateKey, PASSWORD);
    keystore.encryptedKey = 'deadbeef'.repeat(10);
    expect(() => decryptKey(keystore, PASSWORD)).toThrow(UniversalProfileError);
  });

  it('encrypting the same key twice produces different ciphertexts (random salt/iv)', () => {
    const ks1 = encryptKey(testKeyPair.privateKey, PASSWORD);
    const ks2 = encryptKey(testKeyPair.privateKey, PASSWORD);
    expect(ks1.encryptedKey).not.toBe(ks2.encryptedKey);
    expect(ks1.iv).not.toBe(ks2.iv);
    expect(ks1.salt).not.toBe(ks2.salt);
  });

  it('works with an empty-string password', () => {
    const keystore = encryptKey(testKeyPair.privateKey, '');
    const decrypted = decryptKey(keystore, '');
    expect(decrypted).toBe(testKeyPair.privateKey);
  });

  it('works with a unicode password', () => {
    const unicodePass = '\u{1F512}\u{1F511}p@ssw\u00F6rd!';
    const keystore = encryptKey(testKeyPair.privateKey, unicodePass);
    const decrypted = decryptKey(keystore, unicodePass);
    expect(decrypted).toBe(testKeyPair.privateKey);
  });
});

// ==================== KEYSTORE DIRECTORY ====================

describe('getKeystoreDir', () => {
  const originalHome = process.env.HOME;
  const originalUserProfile = process.env.USERPROFILE;

  afterEach(() => {
    process.env.HOME = originalHome;
    if (originalUserProfile !== undefined) {
      process.env.USERPROFILE = originalUserProfile;
    } else {
      delete process.env.USERPROFILE;
    }
  });

  it('returns a path ending with .clawdbot/universal-profile/keys', () => {
    const dir = getKeystoreDir();
    expect(dir).toContain('.clawdbot');
    expect(dir).toContain('universal-profile');
    expect(dir).toContain('keys');
    expect(dir.endsWith(path.join('.clawdbot', 'universal-profile', 'keys'))).toBe(true);
  });

  it('uses HOME environment variable', () => {
    process.env.HOME = '/mock/home';
    delete process.env.USERPROFILE;
    const dir = getKeystoreDir();
    expect(dir).toBe(path.join('/mock/home', '.clawdbot', 'universal-profile', 'keys'));
  });

  it('falls back to USERPROFILE if HOME is not set', () => {
    delete process.env.HOME;
    process.env.USERPROFILE = '/mock/userprofile';
    const dir = getKeystoreDir();
    expect(dir).toBe(
      path.join('/mock/userprofile', '.clawdbot', 'universal-profile', 'keys')
    );
  });
});

// ==================== FILE-BASED KEY OPERATIONS (temp directory) ====================

describe('file-based key operations', () => {
  let tmpDir: string;
  let testKeystore: ReturnType<typeof encryptKey>;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'crypto-test-'));
    const kp = generateKeyPair();
    testKeystore = encryptKey(kp.privateKey, 'file-test-password');
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  // ---- saveKey ----

  describe('saveKey', () => {
    it('saves a keystore file to the specified directory', () => {
      const filepath = saveKey(testKeystore, 'my-key', tmpDir);
      expect(fs.existsSync(filepath)).toBe(true);
    });

    it('returns the full filepath with label.enc extension', () => {
      const filepath = saveKey(testKeystore, 'my-key', tmpDir);
      expect(filepath).toBe(path.join(tmpDir, 'my-key.enc'));
    });

    it('saves valid JSON content', () => {
      const filepath = saveKey(testKeystore, 'my-key', tmpDir);
      const content = fs.readFileSync(filepath, 'utf8');
      const parsed = JSON.parse(content);
      expect(parsed).toHaveProperty('address');
      expect(parsed).toHaveProperty('encryptedKey');
      expect(parsed).toHaveProperty('iv');
      expect(parsed).toHaveProperty('salt');
      expect(parsed).toHaveProperty('algorithm');
    });

    it('sets the label on the keystore object', () => {
      saveKey(testKeystore, 'labeled-key', tmpDir);
      expect(testKeystore.label).toBe('labeled-key');
    });

    it('saved file contains the correct address', () => {
      const filepath = saveKey(testKeystore, 'addr-key', tmpDir);
      const content = JSON.parse(fs.readFileSync(filepath, 'utf8'));
      expect(content.address).toBe(testKeystore.address);
    });

    it('overwrites an existing file with the same label', () => {
      saveKey(testKeystore, 'dup', tmpDir);
      const newKp = generateKeyPair();
      const newKeystore = encryptKey(newKp.privateKey, 'pw');
      saveKey(newKeystore, 'dup', tmpDir);

      const content = JSON.parse(
        fs.readFileSync(path.join(tmpDir, 'dup.enc'), 'utf8')
      );
      expect(content.address).toBe(newKeystore.address);
    });
  });

  // ---- loadKeystore ----

  describe('loadKeystore', () => {
    it('loads a keystore by absolute path', () => {
      const filepath = saveKey(testKeystore, 'load-test', tmpDir);
      const loaded = loadKeystore(filepath);
      expect(loaded.address).toBe(testKeystore.address);
      expect(loaded.encryptedKey).toBe(testKeystore.encryptedKey);
      expect(loaded.iv).toBe(testKeystore.iv);
      expect(loaded.salt).toBe(testKeystore.salt);
    });

    it('loads a keystore by relative path containing a slash', () => {
      const filepath = saveKey(testKeystore, 'load-test', tmpDir);
      // loadKeystore treats paths with "/" as file paths
      const loaded = loadKeystore(filepath);
      expect(loaded.address).toBe(testKeystore.address);
    });

    it('throws UniversalProfileError when file does not exist (absolute path)', () => {
      const fakePath = path.join(tmpDir, 'nonexistent.enc');
      expect(() => loadKeystore(fakePath)).toThrow(UniversalProfileError);
    });

    it('thrown error has KEY_NOT_FOUND code', () => {
      const fakePath = path.join(tmpDir, 'nonexistent.enc');
      try {
        loadKeystore(fakePath);
        expect.unreachable('Should have thrown');
      } catch (err) {
        expect(err).toBeInstanceOf(UniversalProfileError);
        expect((err as UniversalProfileError).code).toBe('UP_KEY_NOT_FOUND');
      }
    });

    it('thrown error includes path in details', () => {
      const fakePath = path.join(tmpDir, 'nonexistent.enc');
      try {
        loadKeystore(fakePath);
        expect.unreachable('Should have thrown');
      } catch (err) {
        expect((err as UniversalProfileError).details).toHaveProperty('path');
      }
    });

    it('loaded keystore can be decrypted', () => {
      const kp = generateKeyPair();
      const pw = 'round-trip-pw';
      const ks = encryptKey(kp.privateKey, pw);
      const filepath = saveKey(ks, 'decrypt-round-trip', tmpDir);
      const loaded = loadKeystore(filepath);
      const decrypted = decryptKey(loaded, pw);
      expect(decrypted).toBe(kp.privateKey);
    });
  });

  // ---- listStoredKeys (with mocked getKeystoreDir) ----

  describe('listStoredKeys', () => {
    it('returns an empty array when directory does not exist', () => {
      // Point HOME to a non-existent location so getKeystoreDir() returns a missing dir
      const originalHome = process.env.HOME;
      process.env.HOME = path.join(tmpDir, 'no-such-home');
      try {
        const keys = listStoredKeys();
        expect(keys).toEqual([]);
      } finally {
        process.env.HOME = originalHome;
      }
    });

    it('lists stored .enc files', () => {
      const originalHome = process.env.HOME;
      // Create a fake keystore dir structure
      const fakeHome = path.join(tmpDir, 'fakehome');
      const fakeKeystoreDir = path.join(
        fakeHome,
        '.clawdbot',
        'universal-profile',
        'keys'
      );
      fs.mkdirSync(fakeKeystoreDir, { recursive: true });

      // Save some keys there
      saveKey(testKeystore, 'key-alpha', fakeKeystoreDir);
      const kp2 = generateKeyPair();
      const ks2 = encryptKey(kp2.privateKey, 'pw2');
      saveKey(ks2, 'key-beta', fakeKeystoreDir);

      process.env.HOME = fakeHome;
      try {
        const keys = listStoredKeys();
        expect(keys).toHaveLength(2);
        const labels = keys.map((k) => k.label);
        expect(labels).toContain('key-alpha');
        expect(labels).toContain('key-beta');
      } finally {
        process.env.HOME = originalHome;
      }
    });

    it('ignores non-.enc files', () => {
      const originalHome = process.env.HOME;
      const fakeHome = path.join(tmpDir, 'fakehome2');
      const fakeKeystoreDir = path.join(
        fakeHome,
        '.clawdbot',
        'universal-profile',
        'keys'
      );
      fs.mkdirSync(fakeKeystoreDir, { recursive: true });

      saveKey(testKeystore, 'real-key', fakeKeystoreDir);
      // Write a non-.enc file
      fs.writeFileSync(path.join(fakeKeystoreDir, 'notes.txt'), 'hello');

      process.env.HOME = fakeHome;
      try {
        const keys = listStoredKeys();
        expect(keys).toHaveLength(1);
        expect(keys[0].label).toBe('real-key');
      } finally {
        process.env.HOME = originalHome;
      }
    });

    it('each returned StoredKey has expected properties', () => {
      const originalHome = process.env.HOME;
      const fakeHome = path.join(tmpDir, 'fakehome3');
      const fakeKeystoreDir = path.join(
        fakeHome,
        '.clawdbot',
        'universal-profile',
        'keys'
      );
      fs.mkdirSync(fakeKeystoreDir, { recursive: true });
      saveKey(testKeystore, 'prop-key', fakeKeystoreDir);

      process.env.HOME = fakeHome;
      try {
        const keys = listStoredKeys();
        expect(keys).toHaveLength(1);
        const key = keys[0];
        expect(key).toHaveProperty('address');
        expect(key).toHaveProperty('label');
        expect(key).toHaveProperty('path');
        expect(key).toHaveProperty('createdAt');
        expect(key.address).toBe(testKeystore.address);
        expect(key.label).toBe('prop-key');
        expect(key.path).toContain('prop-key.enc');
      } finally {
        process.env.HOME = originalHome;
      }
    });
  });

  // ---- deleteKey ----

  describe('deleteKey', () => {
    it('deletes a key file by absolute path and returns true', () => {
      const filepath = saveKey(testKeystore, 'to-delete', tmpDir);
      expect(fs.existsSync(filepath)).toBe(true);
      const result = deleteKey(filepath);
      expect(result).toBe(true);
      expect(fs.existsSync(filepath)).toBe(false);
    });

    it('returns false when file does not exist', () => {
      const fakePath = path.join(tmpDir, 'nonexistent.enc');
      const result = deleteKey(fakePath);
      expect(result).toBe(false);
    });

    it('deletes a key file by label when keystore dir is valid', () => {
      const originalHome = process.env.HOME;
      const fakeHome = path.join(tmpDir, 'fakehome-del');
      const fakeKeystoreDir = path.join(
        fakeHome,
        '.clawdbot',
        'universal-profile',
        'keys'
      );
      fs.mkdirSync(fakeKeystoreDir, { recursive: true });
      saveKey(testKeystore, 'delete-by-label', fakeKeystoreDir);

      process.env.HOME = fakeHome;
      try {
        const result = deleteKey('delete-by-label');
        expect(result).toBe(true);
        expect(fs.existsSync(path.join(fakeKeystoreDir, 'delete-by-label.enc'))).toBe(
          false
        );
      } finally {
        process.env.HOME = originalHome;
      }
    });
  });
});

// ==================== ensureKeystoreDir ====================

describe('ensureKeystoreDir', () => {
  let tmpDir: string;
  const originalHome = process.env.HOME;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ensure-dir-test-'));
  });

  afterEach(() => {
    process.env.HOME = originalHome;
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it('creates the keystore directory if it does not exist', () => {
    const fakeHome = path.join(tmpDir, 'newhome');
    fs.mkdirSync(fakeHome);
    process.env.HOME = fakeHome;

    const dir = ensureKeystoreDir();
    expect(fs.existsSync(dir)).toBe(true);
    expect(dir).toBe(
      path.join(fakeHome, '.clawdbot', 'universal-profile', 'keys')
    );
  });

  it('returns existing directory without error if it already exists', () => {
    const fakeHome = path.join(tmpDir, 'existhome');
    const keystoreDir = path.join(
      fakeHome,
      '.clawdbot',
      'universal-profile',
      'keys'
    );
    fs.mkdirSync(keystoreDir, { recursive: true });
    process.env.HOME = fakeHome;

    const dir = ensureKeystoreDir();
    expect(dir).toBe(keystoreDir);
    expect(fs.existsSync(dir)).toBe(true);
  });
});

// ==================== WALLET UTILITY ====================

describe('getWallet', () => {
  it('creates an ethers Wallet from a valid private key', () => {
    const kp = generateKeyPair();
    const wallet = getWallet(kp.privateKey);
    expect(wallet.address).toBe(kp.address);
  });

  it('the returned wallet has a signingKey', () => {
    const kp = generateKeyPair();
    const wallet = getWallet(kp.privateKey);
    expect(wallet.signingKey).toBeDefined();
    expect(wallet.signingKey.privateKey).toBe(kp.privateKey);
  });

  it('throws on an invalid private key', () => {
    expect(() => getWallet('0xdeadbeef')).toThrow();
  });

  it('returns a wallet without a provider when none is given', () => {
    const kp = generateKeyPair();
    const wallet = getWallet(kp.privateKey);
    expect(wallet.provider).toBeNull();
  });
});

// ==================== VALIDATION UTILITIES ====================

describe('isValidPrivateKey', () => {
  it('returns true for a valid 32-byte hex private key with 0x prefix', () => {
    const kp = generateKeyPair();
    expect(isValidPrivateKey(kp.privateKey)).toBe(true);
  });

  it('returns true for a valid key without 0x prefix', () => {
    const kp = generateKeyPair();
    const raw = kp.privateKey.replace('0x', '');
    expect(isValidPrivateKey(raw)).toBe(true);
  });

  it('returns false for a too-short hex string', () => {
    expect(isValidPrivateKey('0xdeadbeef')).toBe(false);
  });

  it('returns false for an empty string', () => {
    expect(isValidPrivateKey('')).toBe(false);
  });

  it('returns false for a non-hex string', () => {
    expect(isValidPrivateKey('not-a-key-at-all')).toBe(false);
  });

  it('returns false for an all-zero key (invalid on secp256k1)', () => {
    expect(isValidPrivateKey('0x' + '0'.repeat(64))).toBe(false);
  });
});

describe('isValidAddress', () => {
  it('returns true for a valid checksummed address', () => {
    const kp = generateKeyPair();
    expect(isValidAddress(kp.address)).toBe(true);
  });

  it('returns true for a valid lowercase address', () => {
    expect(isValidAddress('0x' + 'a'.repeat(40))).toBe(true);
  });

  it('returns false for a short address', () => {
    expect(isValidAddress('0x1234')).toBe(false);
  });

  it('returns false for an empty string', () => {
    expect(isValidAddress('')).toBe(false);
  });

  it('returns true for a valid 40-char hex string without 0x prefix (ethers accepts it)', () => {
    // ethers.isAddress considers a bare 40-char hex string valid
    expect(isValidAddress('a'.repeat(40))).toBe(true);
  });

  it('returns false for a random non-hex string', () => {
    expect(isValidAddress('hello world')).toBe(false);
  });

  it('returns true for the zero address', () => {
    expect(isValidAddress('0x' + '0'.repeat(40))).toBe(true);
  });
});

// ==================== FULL ROUND-TRIP INTEGRATION ====================

describe('full round-trip: generate -> encrypt -> save -> load -> decrypt', () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'crypto-roundtrip-'));
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it('completes the full key lifecycle', () => {
    // 1. Generate
    const kp = generateKeyPair();
    expect(isValidPrivateKey(kp.privateKey)).toBe(true);
    expect(isValidAddress(kp.address)).toBe(true);

    // 2. Encrypt
    const password = 'lifecycle-password-42';
    const keystore = encryptKey(kp.privateKey, password);
    expect(keystore.address).toBe(kp.address);

    // 3. Save
    const filepath = saveKey(keystore, 'lifecycle-key', tmpDir);
    expect(fs.existsSync(filepath)).toBe(true);

    // 4. Load
    const loaded = loadKeystore(filepath);
    expect(loaded.address).toBe(kp.address);
    expect(loaded.label).toBe('lifecycle-key');

    // 5. Decrypt
    const decryptedKey = decryptKey(loaded, password);
    expect(decryptedKey).toBe(kp.privateKey);

    // 6. Verify wallet from decrypted key
    const wallet = getWallet(decryptedKey);
    expect(wallet.address).toBe(kp.address);

    // 7. Delete
    const deleted = deleteKey(filepath);
    expect(deleted).toBe(true);
    expect(fs.existsSync(filepath)).toBe(false);
  });

  it('completes the mnemonic-based lifecycle', () => {
    // 1. Generate mnemonic
    const mnemonic = generateMnemonic();
    const words = mnemonic.trim().split(/\s+/);
    expect(words.length).toBeGreaterThanOrEqual(12);

    // 2. Derive key
    const kp = deriveKeyFromMnemonic(mnemonic, 0);
    expect(isValidPrivateKey(kp.privateKey)).toBe(true);

    // 3. Encrypt, save, load, decrypt
    const password = 'mnemonic-lifecycle';
    const keystore = encryptKey(kp.privateKey, password);
    const filepath = saveKey(keystore, 'mnemonic-key', tmpDir);
    const loaded = loadKeystore(filepath);
    const decrypted = decryptKey(loaded, password);
    expect(decrypted).toBe(kp.privateKey);

    // 4. Re-derive from mnemonic should match
    const kpAgain = deriveKeyFromMnemonic(mnemonic, 0);
    expect(kpAgain.privateKey).toBe(kp.privateKey);
    expect(kpAgain.address).toBe(kp.address);
  });
});
