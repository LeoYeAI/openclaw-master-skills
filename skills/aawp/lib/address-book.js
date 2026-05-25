#!/usr/bin/env node
/**
 * AAWP Address Book — name → address mappings
 * Storage: ~/.aawp-address-book.json
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { ethers } = require('ethers');

const BOOK_PATH = path.join(process.env.HOME || '/root', '.aawp-address-book.json');

function load() {
  try { return JSON.parse(fs.readFileSync(BOOK_PATH, 'utf8')); }
  catch { return {}; }
}

function save(book) {
  fs.writeFileSync(BOOK_PATH, JSON.stringify(book, null, 2));
}

function add(name, address) {
  if (!ethers.isAddress(address)) throw new Error(`Invalid address: ${address}`);
  const book = load();
  book[name.toLowerCase()] = ethers.getAddress(address);
  save(book);
  return book[name.toLowerCase()];
}

function get(name) {
  const book = load();
  return book[name.toLowerCase()] || null;
}

function list() {
  return load();
}

function remove(name) {
  const book = load();
  const key = name.toLowerCase();
  if (!book[key]) return false;
  delete book[key];
  save(book);
  return true;
}

/**
 * resolve — if it looks like an address (0x..., 42 chars), return as-is.
 * Otherwise look up in address book. Returns address or throws.
 */
function resolve(nameOrAddress) {
  if (!nameOrAddress) throw new Error('Empty address/name');
  if (nameOrAddress.startsWith('0x') && nameOrAddress.length === 42) {
    return nameOrAddress;
  }
  const addr = get(nameOrAddress);
  if (addr) return addr;
  throw new Error(`"${nameOrAddress}" is not a valid address and not found in address book. Use: addr add <name> <address>`);
}

module.exports = { add, get, list, remove, resolve };
