#!/bin/bash
# Derive Nostr keys from Archon DID mnemonic
# Requires: node, npx @didcid/keymaster

set -e

DEPS_DIR="/tmp/archon-nostr-deps"

# Get mnemonic from keymaster
MNEMONIC=$(npx @didcid/keymaster show-mnemonic 2>/dev/null)

if [ -z "$MNEMONIC" ]; then
  echo "Error: Could not get mnemonic. Is ARCHON_PASSPHRASE set?" >&2
  exit 1
fi

# Install dependencies if needed
if [ ! -f "$DEPS_DIR/node_modules/bip39/package.json" ]; then
  echo "Installing dependencies..." >&2
  mkdir -p "$DEPS_DIR"
  cd "$DEPS_DIR"
  npm install --silent bip39 @scure/bip32 secp256k1 bech32 >/dev/null 2>&1
  cd - >/dev/null
fi

# Run derivation
cd "$DEPS_DIR"
node --input-type=commonjs <<EOF
const bip39 = require('bip39');
const { HDKey } = require('@scure/bip32');
const secp256k1 = require('secp256k1');
const { bech32 } = require('bech32');

const mnemonic = '${MNEMONIC}';
const seed = bip39.mnemonicToSeedSync(mnemonic);
const hdkey = HDKey.fromMasterSeed(seed);

// Archon uses Bitcoin BIP44 path
const derived = hdkey.derive("m/44'/0'/0'/0/0");
const privKey = derived.privateKey;
const pubKey = secp256k1.publicKeyCreate(privKey, false);
const pubKeyX = Buffer.from(pubKey.slice(1, 33)).toString('hex');

function toBech32(prefix, hex) {
  const bytes = Buffer.from(hex, 'hex');
  const words = bech32.toWords(bytes);
  return bech32.encode(prefix, words, 1000);
}

const nsec = toBech32('nsec', Buffer.from(privKey).toString('hex'));
const npub = toBech32('npub', pubKeyX);

console.log('nsec:', nsec);
console.log('npub:', npub);
console.log('pubkey:', pubKeyX);
EOF
