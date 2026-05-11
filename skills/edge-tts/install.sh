#!/bin/bash
# Edge-TTS Skill Installation Script

set -e

echo "Installing Edge-TTS Skill..."
echo ""

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd scripts
npm install --production
cd ..

echo ""
echo "✓ Edge-TTS Skill installed successfully!"
echo ""
echo "To test the installation:"
echo "  cd scripts"
echo "  npm test"
echo ""
echo "For configuration:"
echo "  cd scripts"
echo "  node config-manager.js --help"
