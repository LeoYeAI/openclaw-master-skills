#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "[SocialVault] Installing dependencies..."
npm install --production

echo "[SocialVault] Verifying tsx is available..."
npx tsx --version

echo "[SocialVault] Initializing vault..."
npx tsx scripts/vault-crypto.ts init vault

echo "[SocialVault] Setup complete."
