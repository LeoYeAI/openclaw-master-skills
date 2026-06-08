#!/bin/bash
# OpenClaw Skill Installation Script for wechat-md-publisher

set -e

echo "🚀 Installing wechat-md-publisher OpenClaw Skill..."

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    echo "Please install Node.js and npm first: https://nodejs.org/"
    exit 1
fi

# Install the main package
echo "📦 Installing wechat-md-publisher package..."
npm install -g wechat-md-publisher

# Make scripts executable
echo "🔧 Setting up permissions..."
chmod +x scripts/publish.sh

# Verify installation
echo "✅ Verifying installation..."
if command -v wechat-pub &> /dev/null; then
    echo "✓ wechat-pub command is available"
    wechat-pub --version
else
    echo "⚠️  Warning: wechat-pub command not found in PATH"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📚 Next steps:"
echo "1. Configure your WeChat account:"
echo "   wechat-pub account add --name \"公众号\" --app-id xxx --app-secret xxx"
echo ""
echo "2. Check IP whitelist configuration:"
echo "   curl ifconfig.me"
echo "   Then add this IP to WeChat Official Account platform"
echo ""
echo "3. Read the documentation:"
echo "   - Quick Start: ./references/quick-start.md"
echo "   - IP Whitelist Guide: ./references/ip-whitelist-guide.md"
echo "   - Full Documentation: ./SKILL.md"
echo ""
