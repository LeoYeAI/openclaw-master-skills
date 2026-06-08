/**
 * SocialVault 加密存储模块
 *
 * 提供 AES-256-GCM 加密的凭证存储能力。
 * 密钥本地随机生成，每次加密使用随机 96-bit IV。
 *
 * vault.enc 二进制格式：IV (12 bytes) || Auth Tag (16 bytes) || Ciphertext
 */

import { randomBytes, createCipheriv, createDecipheriv } from "node:crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync, chmodSync } from "node:fs";
import { join } from "node:path";
import type { VaultEntry } from "./types.js";

const ALGORITHM = "aes-256-gcm";
const KEY_LENGTH = 32;
const IV_LENGTH = 12;
const AUTH_TAG_LENGTH = 16;
const VAULT_FILE = "vault.enc";
const KEY_FILE = "vault-key";

/**
 * 初始化 vault 目录，如果密钥不存在则生成新密钥。
 * @param vaultDir - vault 数据目录的绝对路径
 * @throws 目录创建失败时抛出异常
 */
export function init(vaultDir: string): void {
  if (!existsSync(vaultDir)) {
    mkdirSync(vaultDir, { recursive: true });
  }

  const fingerprintsDir = join(vaultDir, "fingerprints");
  if (!existsSync(fingerprintsDir)) {
    mkdirSync(fingerprintsDir, { recursive: true });
  }

  const keyPath = join(vaultDir, KEY_FILE);
  if (!existsSync(keyPath)) {
    const key = randomBytes(KEY_LENGTH);
    try {
      writeFileSync(keyPath, key);
    } catch (err) {
      throw new Error(`密钥文件创建失败: ${(err as Error).message}`);
    }
    try {
      chmodSync(keyPath, 0o600);
    } catch {
      // Windows 不支持 Unix 权限，忽略
    }
  }

  const accountsPath = join(vaultDir, "accounts.json");
  if (!existsSync(accountsPath)) {
    try {
      writeFileSync(accountsPath, JSON.stringify({ accounts: [] }, null, 2), "utf-8");
    } catch (err) {
      throw new Error(`accounts.json 初始化失败: ${(err as Error).message}`);
    }
  }
}

/**
 * 读取加密密钥。
 * @param vaultDir - vault 数据目录
 * @returns 32 字节密钥 Buffer
 * @throws 密钥文件不存在或长度不正确时抛出异常
 */
function readKey(vaultDir: string): Buffer {
  const keyPath = join(vaultDir, KEY_FILE);
  if (!existsSync(keyPath)) {
    throw new Error("密钥文件不存在，请先执行 init 初始化 vault。");
  }
  const key = readFileSync(keyPath);
  if (key.length !== KEY_LENGTH) {
    throw new Error(`密钥长度异常：期望 ${KEY_LENGTH} 字节，实际 ${key.length} 字节。`);
  }
  return key;
}

/**
 * 将凭证条目数组加密后写入 vault.enc。
 * @param vaultDir - vault 数据目录
 * @param entries - 凭证条目数组
 * @throws 加密或写入失败时抛出异常
 */
export function encrypt(vaultDir: string, entries: VaultEntry[]): void {
  const key = readKey(vaultDir);
  const iv = randomBytes(IV_LENGTH);
  const plaintext = Buffer.from(JSON.stringify(entries), "utf-8");

  const cipher = createCipheriv(ALGORITHM, key, iv, { authTagLength: AUTH_TAG_LENGTH });
  const encrypted = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const authTag = cipher.getAuthTag();

  // 格式：IV (12) || Auth Tag (16) || Ciphertext
  const output = Buffer.concat([iv, authTag, encrypted]);
  try {
    writeFileSync(join(vaultDir, VAULT_FILE), output);
  } catch (err) {
    throw new Error(`vault.enc 写入失败: ${(err as Error).message}`);
  }
}

/**
 * 读取 vault.enc 并解密还原为凭证条目数组。
 * @param vaultDir - vault 数据目录
 * @returns 解密后的凭证条目数组；vault.enc 不存在时返回空数组
 * @throws 解密失败（密钥错误或数据损坏）时抛出异常
 */
export function decrypt(vaultDir: string): VaultEntry[] {
  const vaultPath = join(vaultDir, VAULT_FILE);
  if (!existsSync(vaultPath)) {
    return [];
  }

  const key = readKey(vaultDir);
  const data = readFileSync(vaultPath);

  if (data.length < IV_LENGTH + AUTH_TAG_LENGTH + 1) {
    throw new Error("vault.enc 文件格式无效：数据过短。");
  }

  const iv = data.subarray(0, IV_LENGTH);
  const authTag = data.subarray(IV_LENGTH, IV_LENGTH + AUTH_TAG_LENGTH);
  const ciphertext = data.subarray(IV_LENGTH + AUTH_TAG_LENGTH);

  const decipher = createDecipheriv(ALGORITHM, key, iv, { authTagLength: AUTH_TAG_LENGTH });
  decipher.setAuthTag(authTag);

  let decrypted: Buffer;
  try {
    decrypted = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  } catch {
    throw new Error("解密失败：密钥错误或数据已损坏。");
  }

  return JSON.parse(decrypted.toString("utf-8")) as VaultEntry[];
}

/**
 * 解密后获取指定账号的凭证。
 * @param vaultDir - vault 数据目录
 * @param accountId - 账号 ID
 * @returns 对应凭证条目，未找到时返回 null
 */
export function getCredentials(vaultDir: string, accountId: string): VaultEntry | null {
  const entries = decrypt(vaultDir);
  const entry = entries.find((e) => e.accountId === accountId) ?? null;

  // 清除其他账号的明文数据
  for (const e of entries) {
    if (e.accountId !== accountId) {
      clearEntry(e);
    }
  }

  return entry;
}

/**
 * 将指定凭证条目的敏感字段在内存中置空。
 * @param entry - 要清除的凭证条目
 */
function clearEntry(entry: VaultEntry): void {
  if (entry.cookies) {
    for (const c of entry.cookies) {
      c.value = "";
    }
    entry.cookies = undefined;
  }
  if (entry.rawCookieHeader) entry.rawCookieHeader = "";
  if (entry.accessToken) entry.accessToken = "";
  if (entry.refreshToken) entry.refreshToken = "";
  if (entry.clientId) entry.clientId = "";
  if (entry.clientSecret) entry.clientSecret = "";
}

/**
 * 清除指定账号在内存中的明文凭证。此函数用于操作完毕后的安全清理。
 * @param entry - 要清除的凭证条目
 */
export function clearCredentials(entry: VaultEntry): void {
  clearEntry(entry);
}

/**
 * 添加或更新一个凭证条目。
 * @param vaultDir - vault 数据目录
 * @param newEntry - 新的凭证条目
 */
export function upsertCredential(vaultDir: string, newEntry: VaultEntry): void {
  const entries = decrypt(vaultDir);
  const idx = entries.findIndex((e) => e.accountId === newEntry.accountId);
  if (idx >= 0) {
    entries[idx] = newEntry;
  } else {
    entries.push(newEntry);
  }
  encrypt(vaultDir, entries);
}

/**
 * 从 vault 中删除指定账号的凭证。
 * @param vaultDir - vault 数据目录
 * @param accountId - 要删除的账号 ID
 */
export function removeCredential(vaultDir: string, accountId: string): void {
  const entries = decrypt(vaultDir);
  const filtered = entries.filter((e) => e.accountId !== accountId);
  encrypt(vaultDir, filtered);
}

/**
 * 密钥轮换：用新密钥重新加密所有凭证。
 * @param vaultDir - vault 数据目录
 */
export function rotateKey(vaultDir: string): void {
  const entries = decrypt(vaultDir);

  const keyPath = join(vaultDir, KEY_FILE);
  const newKey = randomBytes(KEY_LENGTH);
  try {
    writeFileSync(keyPath, newKey);
  } catch (err) {
    throw new Error(`密钥轮换写入失败: ${(err as Error).message}`);
  }
  try {
    chmodSync(keyPath, 0o600);
  } catch {
    // Windows 不支持 Unix 权限
  }

  encrypt(vaultDir, entries);

  for (const e of entries) {
    clearEntry(e);
  }
}

// CLI 入口：支持通过命令行调用基本操作
if (process.argv[1]?.replace(/\\/g, "/").endsWith("scripts/vault-crypto.ts")) {
  const command = process.argv[2];
  const vaultDir = process.argv[3] || join(process.cwd(), "vault");

  switch (command) {
    case "init":
      init(vaultDir);
      console.log(`Vault 已初始化: ${vaultDir}`);
      break;
    case "rotate-key":
      rotateKey(vaultDir);
      console.log("密钥轮换完成。");
      break;
    default:
      console.log("用法: npx tsx scripts/vault-crypto.ts <init|rotate-key> [vault-dir]");
  }
}
