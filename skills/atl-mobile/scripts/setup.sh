#!/usr/bin/env bash
# ATL Setup Script - Clone repo, boot simulator, build & install ATL, verify server
set -euo pipefail

ATL_ROOT="${ATL_ROOT:-$HOME/Atl}"
ATL_REPO="$ATL_ROOT/core/AtlBrowser"
DEVICE="${DEVICE:-iPhone 17}"
ATL_PORT="${ATL_PORT:-9222}"

echo "📱 ATL Setup"
echo "============"

# 0. Clone ATL if needed
if [ ! -d "$ATL_ROOT" ]; then
  echo ""
  echo "0️⃣  Cloning ATL repository..."
  git clone https://github.com/JordanCoin/Atl "$ATL_ROOT"
  echo "   ✅ Cloned to $ATL_ROOT"
fi

# 1. Find or boot simulator
echo ""
echo "1️⃣  Finding simulator..."
UDID=$(xcrun simctl list devices available | grep -E "^\s+$DEVICE" | grep -oE '[A-F0-9-]{36}' | head -1)

if [ -z "$UDID" ]; then
  echo "❌ Device '$DEVICE' not found. Available devices:"
  xcrun simctl list devices available | grep -E "iPhone|iPad" | head -10
  echo ""
  echo "Set DEVICE env var to choose a different device."
  exit 1
fi

echo "   Found: $DEVICE ($UDID)"

# Check if booted
STATE=$(xcrun simctl list devices | grep "$UDID" | grep -o "(Booted)" || true)
if [ -z "$STATE" ]; then
  echo "   Booting simulator..."
  xcrun simctl boot "$UDID"
  sleep 3
fi

# Open Simulator app
open -a Simulator
echo "   ✅ Simulator running"

# 2. Build ATL (if repo exists)
echo ""
echo "2️⃣  Building ATL..."
if [ -d "$ATL_REPO" ]; then
  cd "$ATL_REPO"
  
  # Build targeting the booted simulator
  xcodebuild -workspace AtlBrowser.xcworkspace \
    -scheme AtlBrowser \
    -destination "id=$UDID" \
    -derivedDataPath /tmp/atl-dd \
    build 2>/dev/null | grep -E "^(Build|Compile|Link|===)" || true
  
  echo "   ✅ Build complete"
  
  # 3. Install
  echo ""
  echo "3️⃣  Installing ATL..."
  APP_PATH="/tmp/atl-dd/Build/Products/Debug-iphonesimulator/AtlBrowser.app"
  if [ -d "$APP_PATH" ]; then
    xcrun simctl install "$UDID" "$APP_PATH"
    echo "   ✅ Installed"
  else
    echo "   ⚠️  App not found at $APP_PATH"
    echo "   Try building manually: cd $ATL_REPO && xcodebuild ..."
  fi
else
  echo "   ⚠️  ATL repo not found at $ATL_REPO"
  echo "   Clone it: git clone https://github.com/JordanCoin/Atl ~/Atl"
fi

# 4. Launch ATL
echo ""
echo "4️⃣  Launching ATL..."
xcrun simctl terminate "$UDID" com.atl.browser 2>/dev/null || true
sleep 1
xcrun simctl launch "$UDID" com.atl.browser
sleep 2
echo "   ✅ Launched"

# 5. Verify server
echo ""
echo "5️⃣  Verifying server..."
for i in {1..5}; do
  if curl -s "http://localhost:$ATL_PORT/ping" | grep -q '"status":"ok"'; then
    echo "   ✅ ATL server running on port $ATL_PORT"
    echo ""
    echo "🎉 Setup complete! Try:"
    echo "   curl http://localhost:$ATL_PORT/ping"
    echo ""
    exit 0
  fi
  sleep 1
done

echo "   ❌ Server not responding on port $ATL_PORT"
echo "   Check simulator and ATL app logs"
exit 1
