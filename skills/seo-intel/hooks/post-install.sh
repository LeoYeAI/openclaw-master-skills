#!/bin/bash
# SEO Intel — Post-install hook for OpenClaw skill
# Runs after skill installation or update via ClawHub

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SEO_INTEL_DIR="$SKILL_DIR/seo-intel"

echo "🐸 SEO Intel — Setting up..."

# 1. Install Node dependencies
if [ -f "$SEO_INTEL_DIR/package.json" ]; then
  echo "  Installing dependencies..."
  cd "$SEO_INTEL_DIR"
  npm install --production --silent 2>&1 | tail -1
  echo "  ✓ Dependencies installed"
fi

# 2. Install Playwright browsers (chromium only)
echo "  Installing Playwright Chromium..."
cd "$SEO_INTEL_DIR"
npx playwright install chromium 2>&1 | tail -1
echo "  ✓ Playwright ready"

# 3. Create .env from template if missing
if [ ! -f "$SEO_INTEL_DIR/.env" ] && [ -f "$SEO_INTEL_DIR/.env.example" ]; then
  cp "$SEO_INTEL_DIR/.env.example" "$SEO_INTEL_DIR/.env"
  echo "  ✓ Created .env from template"
fi

# 4. Make CLI executable
chmod +x "$SEO_INTEL_DIR/cli.js" 2>/dev/null || true

# 5. Check Ollama
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "  ✓ Ollama detected"
  # Check for recommended model
  if curl -s http://localhost:11434/api/tags | grep -q "qwen"; then
    echo "  ✓ Qwen model available"
  else
    echo "  ⚠ No Qwen model found. Run: ollama pull qwen3.5:9b"
  fi
else
  echo "  ⚠ Ollama not running. Install from https://ollama.ai"
fi

echo ""
echo "  ✓ SEO Intel installed!"
echo "  → Run the setup wizard: node cli.js setup-web"
echo "  → Or ask me: 'Set up SEO Intel for my site'"
echo ""
