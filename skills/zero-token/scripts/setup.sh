#!/usr/bin/env bash
# Zero Token Setup — Install Free-Way gateway + configure OpenClaw fallback
set -euo pipefail

echo "🦾 Zero Token Setup"
echo "===================="
echo ""

# Check Node.js
if ! command -v node &>/dev/null; then
    echo "❌ Node.js required. Install: https://nodejs.org"
    exit 1
fi

FREE_WAY_DIR="$HOME/free-way"

# Clone Free-Way if not already
if [ ! -d "$FREE_WAY_DIR" ]; then
    echo "📦 Installing Free-Way gateway..."
    git clone --depth 1 https://github.com/GoDiao/Free-Way.git "$FREE_WAY_DIR"
    cd "$FREE_WAY_DIR"
    npm install --omit=dev 2>/dev/null || npm install
    npm run build 2>/dev/null || true
    echo "✅ Free-Way installed at $FREE_WAY_DIR"
else
    echo "✅ Free-Way already installed at $FREE_WAY_DIR"
fi

# Start Free-Way in background if not running
if ! curl -s http://localhost:8787/health &>/dev/null; then
    echo "🚀 Starting Free-Way gateway..."
    cd "$FREE_WAY_DIR"
    nohup npm start > "$FREE_WAY_DIR/free-way.log" 2>&1 &
    sleep 3
    if curl -s http://localhost:8787/health &>/dev/null; then
        echo "✅ Free-Way running at http://localhost:8787"
    else
        echo "⚠️  Free-Way may need manual start: cd $FREE_WAY_DIR && npm start"
    fi
else
    echo "✅ Free-Way already running at http://localhost:8787"
fi

echo ""
echo "📋 Next steps:"
echo ""
echo "1. Open http://localhost:8787 in your browser"
echo "2. Click 'API Keys' tab"
echo "3. Add free API keys from these providers:"
echo ""
echo "   🔑 Groq          → https://console.groq.com/keys          (1000 req/day)"
echo "   🔑 Gemini Flash   → https://aistudio.google.com/apikey    (1500 req/day)"
echo "   🔑 Cerebras       → https://cloud.cerebras.ai              (1700 req/day)"
echo "   🔑 OpenRouter     → https://openrouter.ai/keys             (200 req/day)"
echo ""
echo "   Get at least ONE key (Gemini is easiest — 30 seconds)"
echo "   More keys = more capacity = less chance of hitting limits"
echo ""
echo "4. Add this model as fallback in OpenClaw:"
echo ""
echo "   openclaw config add-model zero-token \\"
echo "     --provider openai \\"
echo "     --base-url http://localhost:8787/v1 \\"
echo "     --model llama-3.3-70b"
echo ""
echo "5. Set it as your backup model in OpenClaw settings"
echo ""
echo "🎉 Done. Your agent uses free models when the main one is down."
