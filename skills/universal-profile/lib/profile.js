/**
 * Universal Profile Operations
 * Functions for interacting with Universal Profiles on LUKSO
 */

import { ethers } from 'ethers';
import crypto from 'crypto';
import { promises as fs } from 'fs';
import {
  ABIS,
  INTERFACE_IDS,
  DATA_KEYS,
  CHAINS,
} from './constants.js';
import {
  buildPermissionsDataKey,
  decodePermissions,
} from './permissions.js';
import { getConfigDir, getKeystorePath } from './config.js';

/**
 * Get a provider for a specific chain
 * @param {string|Object} chain - Chain name or config object
 * @returns {ethers.JsonRpcProvider}
 */
export function getProvider(chain) {
  let rpcUrl;
  
  if (typeof chain === 'string') {
    const chainConfig = CHAINS[chain];
    if (!chainConfig) {
      throw new Error(`Unknown chain: ${chain}`);
    }
    rpcUrl = chainConfig.rpcUrl;
  } else if (chain.rpcUrl) {
    rpcUrl = chain.rpcUrl;
  } else {
    throw new Error('Invalid chain configuration');
  }
  
  return new ethers.JsonRpcProvider(rpcUrl);
}

/**
 * Generate a new keypair for use as a controller
 * @returns {{ privateKey: string, publicKey: string, address: string }}
 */
export function generateKeyPair() {
  const privateKeyBytes = crypto.randomBytes(32);
  const privateKey = '0x' + privateKeyBytes.toString('hex');
  const wallet = new ethers.Wallet(privateKey);
  
  return {
    privateKey,
    publicKey: wallet.signingKey.publicKey,
    address: wallet.address,
  };
}

/**
 * Encrypt and store a private key
 * @param {string} privateKey - Private key to encrypt
 * @param {string} password - Encryption password
 * @param {string} [keystorePath] - Optional path to keystore file
 * @returns {Promise<Object>} Keystore entry
 */
export async function encryptAndStoreKey(privateKey, password, keystorePath) {
  const path = keystorePath || getKeystorePath();
  const wallet = new ethers.Wallet(privateKey);
  
  // Generate encryption parameters
  const salt = crypto.randomBytes(32);
  const key = crypto.pbkdf2Sync(password, salt, 100000, 32, 'sha256');
  const iv = crypto.randomBytes(16);
  
  // Encrypt
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  let encrypted = cipher.update(privateKey, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const authTag = cipher.getAuthTag();
  
  // Create keystore entry
  const entry = {
    address: wallet.address,
    encryptedKey: encrypted + authTag.toString('hex'),
    iv: iv.toString('hex'),
    salt: salt.toString('hex'),
    algorithm: 'aes-256-gcm',
    createdAt: new Date().toISOString(),
  };
  
  // Load existing keystore or create new
  let keystore = { keys: [] };
  try {
    const data = await fs.readFile(path, 'utf8');
    keystore = JSON.parse(data);
  } catch (err) {
    if (err.code !== 'ENOENT') throw err;
    // Create directory if needed
    const dir = getConfigDir();
    await fs.mkdir(dir, { recursive: true });
  }
  
  // Check if key already exists
  const existingIndex = keystore.keys.findIndex(
    k => k.address.toLowerCase() === wallet.address.toLowerCase()
  );
  
  if (existingIndex >= 0) {
    keystore.keys[existingIndex] = entry;
  } else {
    keystore.keys.push(entry);
  }
  
  // Save keystore
  await fs.writeFile(path, JSON.stringify(keystore, null, 2), 'utf8');
  
  return entry;
}

/**
 * Load and decrypt a private key from the keystore
 * @param {string} address - Address of the key to load
 * @param {string} password - Decryption password
 * @param {string} [keystorePath] - Optional path to keystore file
 * @returns {Promise<string>} Decrypted private key
 */
export async function loadKey(address, password, keystorePath) {
  const path = keystorePath || getKeystorePath();
  
  // Load keystore
  let keystore;
  try {
    const data = await fs.readFile(path, 'utf8');
    keystore = JSON.parse(data);
  } catch (err) {
    if (err.code === 'ENOENT') {
      throw new Error('Keystore not found. Generate a key first with "up key generate"');
    }
    throw err;
  }
  
  // Find key entry
  const entry = keystore.keys.find(
    k => k.address.toLowerCase() === address.toLowerCase()
  );
  
  if (!entry) {
    throw new Error(`Key not found for address: ${address}`);
  }
  
  // Decrypt
  const salt = Buffer.from(entry.salt, 'hex');
  const key = crypto.pbkdf2Sync(password, salt, 100000, 32, 'sha256');
  const iv = Buffer.from(entry.iv, 'hex');
  
  const encrypted = entry.encryptedKey.slice(0, -32);
  const authTag = Buffer.from(entry.encryptedKey.slice(-32), 'hex');
  
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
  decipher.setAuthTag(authTag);
  
  let decrypted;
  try {
    decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
  } catch (err) {
    throw new Error('Invalid password');
  }
  
  return decrypted;
}

/**
 * List all keys in the keystore
 * @param {string} [keystorePath] - Optional path to keystore file
 * @returns {Promise<Object[]>} Array of key metadata (without private keys)
 */
export async function listKeys(keystorePath) {
  const path = keystorePath || getKeystorePath();
  
  try {
    const data = await fs.readFile(path, 'utf8');
    const keystore = JSON.parse(data);
    
    return keystore.keys.map(k => ({
      address: k.address,
      createdAt: k.createdAt,
    }));
  } catch (err) {
    if (err.code === 'ENOENT') {
      return [];
    }
    throw err;
  }
}

/**
 * Check if an address is a Universal Profile
 * @param {string} address - Address to check
 * @param {ethers.Provider} provider - Provider to use
 * @returns {Promise<boolean>}
 */
export async function isUniversalProfile(address, provider) {
  try {
    const contract = new ethers.Contract(address, ABIS.LSP0, provider);
    const supportsLSP0 = await contract.supportsInterface(INTERFACE_IDS.LSP0);
    return supportsLSP0;
  } catch (err) {
    return false;
  }
}

/**
 * Get the Key Manager address for a Universal Profile
 * @param {string} upAddress - Universal Profile address
 * @param {ethers.Provider} provider - Provider to use
 * @returns {Promise<string|null>}
 */
export async function getKeyManager(upAddress, provider) {
  try {
    const contract = new ethers.Contract(upAddress, ABIS.LSP0, provider);
    const owner = await contract.owner();
    
    // Check if owner is a Key Manager
    const kmContract = new ethers.Contract(owner, ABIS.LSP6, provider);
    const target = await kmContract.target();
    
    if (target.toLowerCase() === upAddress.toLowerCase()) {
      return owner;
    }
    
    return null;
  } catch (err) {
    return null;
  }
}

/**
 * Get Universal Profile information
 * @param {string} upAddress - Universal Profile address
 * @param {ethers.Provider} provider - Provider to use
 * @returns {Promise<Object>} Profile information
 */
export async function getProfileInfo(upAddress, provider) {
  const up = new ethers.Contract(upAddress, ABIS.LSP0, provider);
  
  // Get basic info
  const [owner, balance, lsp3Data] = await Promise.all([
    up.owner(),
    provider.getBalance(upAddress),
    up.getData(DATA_KEYS.LSP3Profile).catch(() => '0x'),
  ]);
  
  // Parse LSP3 metadata if available
  let profileMetadata = null;
  if (lsp3Data && lsp3Data !== '0x') {
    try {
      // LSP3 data is typically a VerifiableURI
      // Format: 0x + 4 bytes hashFunction + 32 bytes hash + url
      // For simplicity, we just note it exists
      profileMetadata = { hasMetadata: true, raw: lsp3Data };
    } catch (err) {
      // Ignore parsing errors
    }
  }
  
  // Get Key Manager if owner is one
  const keyManager = await getKeyManager(upAddress, provider);
  
  // Get controllers count
  let controllersCount = 0;
  if (keyManager) {
    try {
      const lengthData = await up.getData(DATA_KEYS['AddressPermissions[]']);
      if (lengthData && lengthData !== '0x') {
        controllersCount = parseInt(lengthData, 16);
      }
    } catch (err) {
      // Ignore
    }
  }
  
  // Get received assets count
  let assetsCount = 0;
  try {
    const assetsLengthData = await up.getData(DATA_KEYS['LSP5ReceivedAssets[]']);
    if (assetsLengthData && assetsLengthData !== '0x') {
      assetsCount = parseInt(assetsLengthData, 16);
    }
  } catch (err) {
    // Ignore
  }
  
  return {
    address: upAddress,
    owner,
    keyManager,
    balance: ethers.formatEther(balance),
    balanceWei: balance.toString(),
    controllersCount,
    assetsCount,
    profileMetadata,
    isUniversalProfile: true,
  };
}

/**
 * Get permissions for a controller on a Universal Profile
 * @param {string} upAddress - Universal Profile address
 * @param {string} controllerAddress - Controller address
 * @param {ethers.Provider} provider - Provider to use
 * @returns {Promise<Object>} Permission information
 */
export async function getControllerPermissions(upAddress, controllerAddress, provider) {
  const up = new ethers.Contract(upAddress, ABIS.LSP0, provider);
  
  const permissionsKey = buildPermissionsDataKey(controllerAddress);
  const permissionsData = await up.getData(permissionsKey);
  
  if (!permissionsData || permissionsData === '0x') {
    return {
      address: controllerAddress,
      permissions: '0x0000000000000000000000000000000000000000000000000000000000000000',
      permissionNames: [],
      hasAccess: false,
    };
  }
  
  const permissionNames = decodePermissions(permissionsData);
  
  return {
    address: controllerAddress,
    permissions: permissionsData,
    permissionNames,
    hasAccess: permissionNames.length > 0,
  };
}

/**
 * List all controllers of a Universal Profile
 * @param {string} upAddress - Universal Profile address
 * @param {ethers.Provider} provider - Provider to use
 * @returns {Promise<Object[]>} Array of controller info
 */
export async function listControllers(upAddress, provider) {
  const up = new ethers.Contract(upAddress, ABIS.LSP0, provider);
  
  // Get controllers count
  const lengthData = await up.getData(DATA_KEYS['AddressPermissions[]']);
  if (!lengthData || lengthData === '0x') {
    return [];
  }
  
  const count = parseInt(lengthData, 16);
  const controllers = [];
  
  // Build keys for all controller addresses
  const indexKeys = [];
  for (let i = 0; i < count; i++) {
    const indexKey = DATA_KEYS['AddressPermissions[]'] + 
      i.toString(16).padStart(32, '0');
    indexKeys.push(indexKey);
  }
  
  // Get all addresses
  const addresses = await up.getDataBatch(indexKeys);
  
  // Get permissions for each
  for (let i = 0; i < addresses.length; i++) {
    if (addresses[i] && addresses[i] !== '0x') {
      // Extract address from bytes (might be padded)
      const addr = '0x' + addresses[i].slice(-40);
      const info = await getControllerPermissions(upAddress, addr, provider);
      controllers.push(info);
    }
  }
  
  return controllers;
}

/**
 * Create a wallet signer from a private key
 * @param {string} privateKey - Private key
 * @param {ethers.Provider} provider - Provider to use
 * @returns {ethers.Wallet}
 */
export function createSigner(privateKey, provider) {
  return new ethers.Wallet(privateKey, provider);
}

/**
 * Format profile info for display
 * @param {Object} info - Profile info object
 * @returns {string} Formatted string
 */
export function formatProfileInfo(info) {
  const lines = [];
  
  lines.push('┌─────────────────────────────────────┐');
  lines.push('│ Universal Profile Info              │');
  lines.push('├─────────────────────────────────────┤');
  lines.push(`│ Address: ${info.address.slice(0, 10)}...${info.address.slice(-4)}   │`);
  
  if (info.keyManager) {
    lines.push(`│ Key Manager: ${info.keyManager.slice(0, 10)}...│`);
  } else {
    lines.push(`│ Key Manager: Not set                │`);
  }
  
  lines.push(`│ Balance: ${info.balance.padEnd(22)} LYX │`);
  lines.push(`│ Controllers: ${String(info.controllersCount).padEnd(22)} │`);
  lines.push(`│ Received Assets: ${String(info.assetsCount).padEnd(18)} │`);
  
  if (info.profileMetadata?.hasMetadata) {
    lines.push(`│ Has LSP3 Metadata: Yes              │`);
  }
  
  lines.push('└─────────────────────────────────────┘');
  
  return lines.join('\n');
}

export default {
  getProvider,
  generateKeyPair,
  encryptAndStoreKey,
  loadKey,
  listKeys,
  isUniversalProfile,
  getKeyManager,
  getProfileInfo,
  getControllerPermissions,
  listControllers,
  createSigner,
  formatProfileInfo,
};
