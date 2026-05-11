import fs from 'node:fs';
import path from 'node:path';
import { PublicKey } from '@solana/web3.js';
import { CONFIG_DIR } from './config.js';
import { SdkError } from './errors.js';

const CONTACTS_FILE = path.join(CONFIG_DIR, 'contacts.json');

export interface Contact {
  name: string;
  address: string;
}

export interface ContactsStore {
  contacts: Contact[];
}

export function loadContacts(): ContactsStore {
  try {
    const raw = fs.readFileSync(CONTACTS_FILE, 'utf-8');
    return JSON.parse(raw) as ContactsStore;
  } catch {
    return { contacts: [] };
  }
}

export function saveContacts(store: ContactsStore): void {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONTACTS_FILE, JSON.stringify(store, null, 2), 'utf-8');
}

function isValidSolanaAddress(address: string): boolean {
  try {
    new PublicKey(address);
    return true;
  } catch {
    return false;
  }
}

export function addContact(name: string, address: string): void {
  const normalized = name.toLowerCase();

  if (isValidSolanaAddress(normalized)) {
    throw new SdkError('INVALID_CONTACT_NAME', 'Contact name cannot be a valid Solana address');
  }

  if (!isValidSolanaAddress(address)) {
    throw new SdkError('INVALID_ADDRESS', `"${address}" is not a valid Solana address`);
  }

  const store = loadContacts();
  const existing = store.contacts.find((c) => c.name === normalized);
  if (existing) {
    throw new SdkError('CONTACT_EXISTS', `Contact "${normalized}" already exists (${existing.address})`);
  }

  store.contacts.push({ name: normalized, address });
  saveContacts(store);
}

export function removeContact(name: string): void {
  const normalized = name.toLowerCase();
  const store = loadContacts();
  const index = store.contacts.findIndex((c) => c.name === normalized);
  if (index === -1) {
    throw new SdkError('CONTACT_NOT_FOUND', `Contact "${normalized}" not found`);
  }
  store.contacts.splice(index, 1);
  saveContacts(store);
}

export function getContact(name: string): Contact | null {
  const normalized = name.toLowerCase();
  const store = loadContacts();
  return store.contacts.find((c) => c.name === normalized) || null;
}

export function listContacts(): Contact[] {
  return loadContacts().contacts;
}

export function resolveRecipient(recipient: string): string {
  const contact = getContact(recipient);
  return contact ? contact.address : recipient;
}

export function initContacts(): boolean {
  if (fs.existsSync(CONTACTS_FILE)) {
    return false;
  }
  saveContacts({ contacts: [] });
  return true;
}
