#!/bin/bash
set -e

echo "🚀 OpenClaw LaunchDaemon Installer"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

USERNAME=$(whoami)
PLIST_PATH="/Library/LaunchDaemons/ai.openclaw.gateway.plist"
TEMP_PLIST="/tmp/ai.openclaw.gateway.plist"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}❌ Don't run this script with sudo${NC}"
   echo "The script will ask for sudo password when needed."
   exit 1
fi

# Check if OpenClaw is installed
if ! command -v openclaw &> /dev/null; then
    echo -e "${RED}❌ OpenClaw not found. Install it first:${NC}"
    echo "   npm install -g openclaw"
    exit 1
fi

echo -e "${YELLOW}📋 Creating LaunchDaemon configuration...${NC}"

# Get OpenClaw gateway token
GATEWAY_TOKEN=$(openclaw config get gateway.auth.token 2>/dev/null | tr -d '"' || echo "")

# Detect node path (try common locations)
if [ -f /opt/homebrew/bin/node ]; then
    NODE_PATH="/opt/homebrew/bin/node"
elif [ -f /usr/local/bin/node ]; then
    NODE_PATH="/usr/local/bin/node"
else
    NODE_PATH=$(which node)
fi

# Detect openclaw path
OPENCLAW_PATH=$(npm root -g)/openclaw/dist/index.js

if [ ! -f "$OPENCLAW_PATH" ]; then
    echo -e "${RED}❌ Cannot find OpenClaw installation${NC}"
    echo "Searched at: $OPENCLAW_PATH"
    exit 1
fi

cat > "$TEMP_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>ai.openclaw.gateway</string>
    
    <key>Comment</key>
    <string>OpenClaw Gateway (System Daemon - Network Always On)</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <!-- Enhanced KeepAlive for network services -->
    <key>KeepAlive</key>
    <dict>
      <key>SuccessfulExit</key>
      <false/>
      <key>NetworkState</key>
      <true/>
      <key>Crashed</key>
      <true/>
    </dict>
    
    <!-- Prevent ANY throttling -->
    <key>ThrottleInterval</key>
    <integer>0</integer>
    
    <!-- Interactive process - highest priority -->
    <key>ProcessType</key>
    <string>Interactive</string>
    
    <!-- Enable network transactions -->
    <key>EnableTransactions</key>
    <true/>
    
    <key>UserName</key>
    <string>$USERNAME</string>
    
    <key>GroupName</key>
    <string>staff</string>
    
    <!-- Wrap with caffeinate to prevent sleep -->
    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/caffeinate</string>
      <string>-s</string>
      <string>$NODE_PATH</string>
      <string>$OPENCLAW_PATH</string>
      <string>gateway</string>
      <string>--port</string>
      <string>18789</string>
    </array>
    
    <key>StandardOutPath</key>
    <string>/Users/$USERNAME/.openclaw/logs/gateway.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/$USERNAME/.openclaw/logs/gateway.err.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
      <key>HOME</key>
      <string>/Users/$USERNAME</string>
      <key>PATH</key>
      <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
      <key>OPENCLAW_GATEWAY_PORT</key>
      <string>18789</string>
      <key>OPENCLAW_GATEWAY_TOKEN</key>
      <string>$GATEWAY_TOKEN</string>
    </dict>
  </dict>
</plist>
EOF

echo -e "${GREEN}✅ Configuration created${NC}"
echo "   Node: $NODE_PATH"
echo "   OpenClaw: $OPENCLAW_PATH"
echo "   User: $USERNAME"
echo ""

echo -e "${YELLOW}🛑 Stopping existing services...${NC}"

# Stop LaunchAgent
launchctl bootout gui/$(id -u)/ai.openclaw.gateway 2>/dev/null && echo "   Stopped LaunchAgent" || true

# Backup LaunchAgent plist
if [ -f ~/Library/LaunchAgents/ai.openclaw.gateway.plist ]; then
    mv ~/Library/LaunchAgents/ai.openclaw.gateway.plist ~/Library/LaunchAgents/ai.openclaw.gateway.plist.backup
    echo -e "${GREEN}   ✅ Backed up LaunchAgent plist${NC}"
fi

# Stop existing LaunchDaemon
sudo launchctl bootout system/ai.openclaw.gateway 2>/dev/null && echo "   Stopped existing LaunchDaemon" || true

echo ""
echo -e "${YELLOW}📦 Installing LaunchDaemon (requires sudo)...${NC}"

# Install plist
sudo cp "$TEMP_PLIST" "$PLIST_PATH"
sudo chown root:wheel "$PLIST_PATH"
sudo chmod 644 "$PLIST_PATH"

echo -e "${GREEN}   ✅ Installed to $PLIST_PATH${NC}"
echo ""

echo -e "${YELLOW}🚀 Starting service...${NC}"

# Start service
sudo launchctl bootstrap system "$PLIST_PATH"
sleep 3

# Verify
if ps aux | grep -q "[o]penclaw-gateway"; then
    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ LaunchDaemon installed successfully!${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
    echo "📊 Service Status:"
    ps aux | grep "[o]penclaw-gateway" | awk '{print "   PID: "$2", User: "$1", PPID: (should be 1)"}'
    
    # Show PPID
    OPENCLAW_PID=$(pgrep -f openclaw-gateway)
    PPID=$(ps -p $OPENCLAW_PID -o ppid= | tr -d ' ')
    if [ "$PPID" = "1" ]; then
        echo -e "   ${GREEN}✅ PPID = 1 (running as LaunchDaemon)${NC}"
    else
        echo -e "   ${YELLOW}⚠️  PPID = $PPID (expected 1)${NC}"
    fi
    
    echo ""
    echo "🧪 Test lock screen behavior:"
    echo "   1. Lock your Mac: ⌘ + Control + Q"
    echo "   2. Send 'ping' from your phone (Telegram/Feishu/etc.)"
    echo "   3. Bot should reply 'pong! 🎉' even while locked!"
    echo ""
    echo "📋 Management commands:"
    echo "   View logs:  tail -f ~/.openclaw/logs/gateway.log"
    echo "   Restart:    sudo launchctl kickstart -k system/ai.openclaw.gateway"
    echo "   Stop:       sudo launchctl bootout system/ai.openclaw.gateway"
    echo "   Status:     sudo launchctl print system/ai.openclaw.gateway"
    echo "   OpenClaw:   openclaw status"
    echo ""
else
    echo -e "${RED}════════════════════════════════════${NC}"
    echo -e "${RED}❌ Service failed to start${NC}"
    echo -e "${RED}════════════════════════════════════${NC}"
    echo ""
    echo "📋 Troubleshooting:"
    echo "   Check error logs:  tail -50 ~/.openclaw/logs/gateway.err.log"
    echo "   Check system log:  sudo log show --predicate 'process == \"launchd\"' --last 5m"
    echo "   Verify plist:      plutil -lint $PLIST_PATH"
    echo ""
    exit 1
fi
