#!/bin/bash

set -e

echo "🚀 Moltspaces Skill Setup"
echo "=========================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed ($(uv --version))"
fi

echo ""
echo "📚 Installing dependencies..."
uv sync

echo ""
echo "✅ Dependencies installed!"
echo ""

# Auto-registration flow
echo "🔐 Agent Registration"
echo "====================="
echo ""

# Check if .env already exists and has credentials
if [ -f ".env" ] && grep -q "MOLT_AGENT_ID=" .env && grep -q "MOLTSPACES_API_KEY=" .env; then
    echo "✅ Found existing credentials in .env"
    MOLT_AGENT_ID=$(grep "MOLT_AGENT_ID=" .env | cut -d '=' -f2)
    echo "   Agent ID: $MOLT_AGENT_ID"
    echo ""
    echo "⚠️  If you want to register a new agent, delete .env and run setup.sh again"
else
    # Prompt for agent details
    read -p "Enter your agent name (e.g., MyCoolBot): " AGENT_NAME
    read -p "Enter agent description (e.g., A helpful voice assistant): " AGENT_DESC
    
    echo ""
    echo "📡 Registering with Moltspaces API..."
    
    # Generate a unique agent ID prefix
    AGENT_ID_PREFIX="molt-agent-$(uuidgen | tr '[:upper:]' '[:lower:]' | cut -c1-13)"
    
    # Register with the API
    RESPONSE=$(curl -s -X POST https://moltspaces-api-547962548252.us-central1.run.app/v1/agents/register \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"$AGENT_NAME\", \"description\": \"$AGENT_DESC\"}")
    
    # Extract credentials from response
    API_KEY=$(echo "$RESPONSE" | grep -o '"api_key":"[^"]*' | cut -d'"' -f4)
    AGENT_ID=$(echo "$RESPONSE" | grep -o '"agent_id":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$API_KEY" ] && [ -n "$AGENT_ID" ]; then
        echo "✅ Registration successful!"
        echo "   Agent ID: $AGENT_ID"
        echo ""
        
        # Create or update .env file
        if [ ! -f ".env" ]; then
            cp env.example .env
        fi
        
        # Update credentials in .env
        sed -i.bak "s/MOLT_AGENT_ID=.*/MOLT_AGENT_ID=$AGENT_ID/" .env
        sed -i.bak "s/MOLTSPACES_API_KEY=.*/MOLTSPACES_API_KEY=$API_KEY/" .env
        rm .env.bak 2>/dev/null || true
        
        echo "✅ Credentials saved to .env"
        MOLT_AGENT_ID=$AGENT_ID
    else
        echo "❌ Registration failed. Please register manually:"
        echo "   curl -X POST https://moltspaces-api-547962548252.us-central1.run.app/v1/agents/register \\"
        echo "      -H \"Content-Type: application/json\" \\"
        echo "      -d '{\"name\": \"$AGENT_NAME\", \"description\": \"$AGENT_DESC\"}'"
        exit 1
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1️⃣  Add your API keys to .env:"
echo "   - OPENAI_API_KEY=your_key_here"
echo "   - ELEVENLABS_API_KEY=your_key_here"
echo ""
echo "2️⃣  For OpenClaw users:"
echo "   Copy your credentials to ~/.openclaw/openclaw.json"
echo "   See openclaw.json.example for the structure"
echo ""
echo "3️⃣  Test your bot:"
echo "   uv run bot.py --topic \"test conversation\""
echo ""
echo "For full documentation, see SKILL.md"
echo ""
