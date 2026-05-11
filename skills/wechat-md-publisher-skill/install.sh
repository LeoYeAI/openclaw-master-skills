#!/bin/bash
# OpenClaw Skill Installation Script for wechat-md-publisher

set -e

echo "🚀 Setting up wechat-md-publisher OpenClaw Skill..."

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    echo "Please install Node.js and npm first: https://nodejs.org/"
    exit 1
fi

# Check if wechat-md-publisher is already installed
if command -v wechat-pub &> /dev/null; then
    echo "✓ wechat-pub is already installed"
    wechat-pub --version
else
    echo ""
    echo "⚠️  wechat-md-publisher is not installed."
    echo ""
    echo "To install, please run the following command manually:"
    echo ""
    echo "    npm install -g wechat-md-publisher"
    echo ""
    echo "This skill requires user confirmation before installing packages."
    exit 1
fi

# Make scripts executable
echo "🔧 Setting up permissions..."
chmod +x scripts/publish.sh

echo ""
echo "🎉 Setup complete!"
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
