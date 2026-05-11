#!/bin/bash
# Setup script for TotalReclaw OpenClaw plugin
# Run this on the HOST before starting Docker containers

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installing plugin dependencies..."
npm install --production

echo ""
echo "Plugin ready! Start the containers with:"
echo "  cd testbed/functional-test"
echo "  docker compose -f docker-compose.functional-test.yml up -d"
echo ""
echo "The plugin will auto-register on first use."
echo "Set TOTALRECLAW_RECOVERY_PHRASE in your .env file."
