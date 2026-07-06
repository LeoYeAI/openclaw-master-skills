/**
 * Vault management for ClawSend.
 *
 * The vault IS the identity. It stores keypairs, contacts, and message history.
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync, chmodSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { randomUUID } from 'crypto';
import * as crypto from './crypto.js';

// Default vault location
export const DEFAULT_VAULT_DIR = join(homedir(), '.openclaw', 'vault');

// File names within vault
const IDENTITY_FILE = 'identity.json';
const SIGNING_KEY_FILE = 'signing_key.bin';
const ENCRYPTION_KEY_FILE = 'encryption_key.bin';
const CONTACTS_FILE = 'contacts.json';
const HISTORY_DIR = 'history';
const QUARANTINE_DIR = 'quarantine';

export class VaultError extends Error {
  constructor(message) {
    super(message);
    this.name = 'VaultError';
  }
}

export class VaultNotFoundError extends VaultError {
  constructor(message) {
    super(message);
    this.name = 'VaultNotFoundError';
  }
}

export class VaultExistsError extends VaultError {
  constructor(message) {
    super(message);
    this.name = 'VaultExistsError';
  }
}

export class Vault {
  constructor(vaultDir = null) {
    this.vaultDir = vaultDir || DEFAULT_VAULT_DIR;
    this._identity = null;
    this._signingPrivateKey = null;
    this._encryptionPrivateKey = null;
  }

  get identityPath() {
    return join(this.vaultDir, IDENTITY_FILE);
  }

  get signingKeyPath() {
    return join(this.vaultDir, SIGNING_KEY_FILE);
  }

  get encryptionKeyPath() {
    return join(this.vaultDir, ENCRYPTION_KEY_FILE);
  }

  get contactsPath() {
    return join(this.vaultDir, CONTACTS_FILE);
  }

  get historyPath() {
    return join(this.vaultDir, HISTORY_DIR);
  }

  get quarantinePath() {
    return join(this.vaultDir, QUARANTINE_DIR);
  }

  get exists() {
    return existsSync(this.identityPath);
  }

  /**
   * Create a new vault with fresh keypairs.
   */
  create(alias = null) {
    if (this.exists) {
      throw new VaultExistsError(`Vault already exists at ${this.vaultDir}`);
    }

    // Create directory structure
    mkdirSync(this.vaultDir, { recursive: true });
    mkdirSync(this.historyPath, { recursive: true });
    mkdirSync(this.quarantinePath, { recursive: true });

    // Generate keypairs
    const signing = crypto.generateSigningKeypair();
    const encryption = crypto.generateEncryptionKeypair();

    // Generate vault ID
    const vaultId = `vault_${randomUUID().replace(/-/g, '')}`;

    // Create identity
    const identity = {
      vault_id: vaultId,
      alias: alias,
      signing_public_key: crypto.toBase64(signing.publicKey),
      encryption_public_key: crypto.toBase64(encryption.publicKey),
      created_at: new Date().toISOString(),
    };

    // Save private keys (binary format)
    writeFileSync(this.signingKeyPath, signing.privateKey);
    writeFileSync(this.encryptionKeyPath, encryption.privateKey);

    // Set restrictive permissions on key files
    try {
      chmodSync(this.signingKeyPath, 0o600);
      chmodSync(this.encryptionKeyPath, 0o600);
    } catch {
      // Permissions may not work on all platforms
    }

    // Save identity
    writeFileSync(this.identityPath, JSON.stringify(identity, null, 2));

    // Initialize empty contacts
    writeFileSync(this.contactsPath, JSON.stringify({ contacts: {}, quarantine_unknown: true }, null, 2));

    // Cache loaded data
    this._identity = identity;
    this._signingPrivateKey = signing.privateKey;
    this._encryptionPrivateKey = encryption.privateKey;

    return identity;
  }

  /**
   * Load an existing vault.
   */
  load() {
    if (!this.exists) {
      throw new VaultNotFoundError(`No vault found at ${this.vaultDir}`);
    }

    // Load identity
    this._identity = JSON.parse(readFileSync(this.identityPath, 'utf-8'));

    // Load private keys
    this._signingPrivateKey = new Uint8Array(readFileSync(this.signingKeyPath));
    this._encryptionPrivateKey = new Uint8Array(readFileSync(this.encryptionKeyPath));

    return this._identity;
  }

  /**
   * Get vault identity, loading if necessary.
   */
  getIdentity() {
    if (!this._identity) {
      this.load();
    }
    return this._identity;
  }

  get vaultId() {
    return this.getIdentity().vault_id;
  }

  get alias() {
    return this.getIdentity().alias;
  }

  get signingPublicKeyB64() {
    return this.getIdentity().signing_public_key;
  }

  get encryptionPublicKeyB64() {
    return this.getIdentity().encryption_public_key;
  }

  getSigningPrivateKey() {
    if (!this._signingPrivateKey) {
      this.load();
    }
    return this._signingPrivateKey;
  }

  getEncryptionPrivateKey() {
    if (!this._encryptionPrivateKey) {
      this.load();
    }
    return this._encryptionPrivateKey;
  }

  getSigningPublicKey() {
    return crypto.fromBase64(this.signingPublicKeyB64);
  }

  getEncryptionPublicKey() {
    return crypto.fromBase64(this.encryptionPublicKeyB64);
  }

  // =========================================================================
  // Signing and Encryption
  // =========================================================================

  sign(data) {
    return crypto.signJson(this.getSigningPrivateKey(), data);
  }

  decrypt(encrypted) {
    return crypto.decryptJson(this.getEncryptionPrivateKey(), encrypted);
  }

  // =========================================================================
  // Contact Management
  // =========================================================================

  getContacts() {
    if (!existsSync(this.contactsPath)) {
      return { contacts: {}, quarantine_unknown: true };
    }
    return JSON.parse(readFileSync(this.contactsPath, 'utf-8'));
  }

  addContact(vaultId, { alias = null, signingPublicKey = null, encryptionPublicKey = null, notes = null } = {}) {
    const contactsData = this.getContacts();
    const contact = contactsData.contacts[vaultId] || {};

    contact.vault_id = vaultId;
    contact.added_at = contact.added_at || new Date().toISOString();
    contact.updated_at = new Date().toISOString();

    if (alias !== null) contact.alias = alias;
    if (signingPublicKey !== null) contact.signing_public_key = signingPublicKey;
    if (encryptionPublicKey !== null) contact.encryption_public_key = encryptionPublicKey;
    if (notes !== null) contact.notes = notes;

    contactsData.contacts[vaultId] = contact;
    writeFileSync(this.contactsPath, JSON.stringify(contactsData, null, 2));

    return contact;
  }

  removeContact(vaultId) {
    const contactsData = this.getContacts();
    if (vaultId in contactsData.contacts) {
      delete contactsData.contacts[vaultId];
      writeFileSync(this.contactsPath, JSON.stringify(contactsData, null, 2));
      return true;
    }
    return false;
  }

  getContact(vaultId) {
    return this.getContacts().contacts[vaultId] || null;
  }

  isKnownContact(vaultId) {
    return vaultId in this.getContacts().contacts;
  }

  shouldQuarantine(senderVaultId) {
    const contactsData = this.getContacts();
    if (!contactsData.quarantine_unknown) {
      return false;
    }
    return !this.isKnownContact(senderVaultId);
  }

  // =========================================================================
  // Server Registration State
  // =========================================================================

  _normalizeServerUrl(serverUrl) {
    return serverUrl.replace(/\/+$/, '');
  }

  getServerState(serverUrl) {
    const identity = this.getIdentity();
    const servers = identity.servers || {};
    const normalized = this._normalizeServerUrl(serverUrl);
    return servers[serverUrl] || servers[normalized] || servers[normalized + '/'] || null;
  }

  setServerState(serverUrl, state) {
    const identity = this.getIdentity();
    if (!identity.servers) {
      identity.servers = {};
    }
    const normalized = this._normalizeServerUrl(serverUrl);
    identity.servers[normalized] = state;
    writeFileSync(this.identityPath, JSON.stringify(identity, null, 2));
    this._identity = identity;
  }

  isRegistered(serverUrl) {
    const state = this.getServerState(serverUrl);
    return state !== null && state.registered === true;
  }

  // =========================================================================
  // Message History
  // =========================================================================

  saveMessage(message, direction) {
    const msgId = message.envelope?.id || `unknown_${randomUUID().replace(/-/g, '')}`;
    const timestamp = new Date().toISOString();

    const historyEntry = {
      direction,
      saved_at: timestamp,
      message,
    };

    const filename = `${timestamp.replace(/:/g, '-')}_${direction}_${msgId}.json`;
    const filepath = join(this.historyPath, filename);
    writeFileSync(filepath, JSON.stringify(historyEntry, null, 2));
  }

  saveToQuarantine(message, reason) {
    const msgId = message.envelope?.id || `unknown_${randomUUID().replace(/-/g, '')}`;
    const timestamp = new Date().toISOString();

    const quarantineEntry = {
      reason,
      quarantined_at: timestamp,
      message,
    };

    const filename = `${timestamp.replace(/:/g, '-')}_${msgId}.json`;
    const filepath = join(this.quarantinePath, filename);
    writeFileSync(filepath, JSON.stringify(quarantineEntry, null, 2));
  }

  // =========================================================================
  // Export
  // =========================================================================

  exportPublicIdentity() {
    const identity = this.getIdentity();
    return {
      vault_id: identity.vault_id,
      alias: identity.alias,
      signing_public_key: identity.signing_public_key,
      encryption_public_key: identity.encryption_public_key,
    };
  }
}

/**
 * Get a Vault instance for the default location.
 */
export function getDefaultVault() {
  return new Vault();
}

/**
 * Get the default vault, creating it if it doesn't exist.
 */
export function ensureVault() {
  const vault = getDefaultVault();
  if (!vault.exists) {
    vault.create();
  } else {
    vault.load();
  }
  return vault;
}
