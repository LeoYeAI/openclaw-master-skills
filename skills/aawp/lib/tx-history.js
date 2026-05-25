'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const HISTORY_FILE = path.join(os.homedir(), '.aawp-history.json');
const MAX_ENTRIES = 1000;

/**
 * Append a tx entry to history.
 * @param {object} entry - { ts, chain, type, from, to, amount, token, txHash, status, gasUsed }
 */
function append(entry) {
  let history = [];
  try {
    if (fs.existsSync(HISTORY_FILE)) {
      history = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
    }
  } catch { history = []; }

  entry.ts = entry.ts || new Date().toISOString();
  history.push(entry);

  // Keep only last MAX_ENTRIES
  if (history.length > MAX_ENTRIES) {
    history = history.slice(history.length - MAX_ENTRIES);
  }

  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));
}

/**
 * Query tx history with optional filters.
 * @param {object} opts - { chain, limit, type }
 * @returns {Array}
 */
function query({ chain, limit = 20, type } = {}) {
  let history = [];
  try {
    if (fs.existsSync(HISTORY_FILE)) {
      history = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
    }
  } catch { return []; }

  if (chain) history = history.filter(e => e.chain === chain.toLowerCase());
  if (type) history = history.filter(e => e.type === type.toLowerCase());

  return history.slice(-limit);
}

module.exports = { append, query };
