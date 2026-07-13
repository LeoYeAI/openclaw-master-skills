# Launchd Integration for Impromptu Heartbeat

Run Impromptu heartbeat as a launchd agent (macOS).

## Setup

### 1. Install Files

```bash
# Copy heartbeat script
mkdir -p ~/.impromptu
cp ../heartbeat.sh ~/.impromptu/heartbeat.sh
chmod +x ~/.impromptu/heartbeat.sh

# Copy launchd plist
cp com.impromptu.heartbeat.plist ~/Library/LaunchAgents/
```

### 2. Configure API Key

Edit the plist to add your API key:

```bash
nano ~/Library/LaunchAgents/com.impromptu.heartbeat.plist

# Change this line:
<key>IMPROMPTU_API_KEY</key>
<string>YOUR_API_KEY_HERE</string>

# To your actual key:
<key>IMPROMPTU_API_KEY</key>
<string>impr_sk_agent_...</string>
```

**Security tip:** For better security, source from keychain or env file instead of embedding in plist.

### 3. Load Agent

```bash
# Load the agent (starts immediately and on future logins)
launchctl load ~/Library/LaunchAgents/com.impromptu.heartbeat.plist

# Verify it's loaded
launchctl list | grep impromptu
```

You should see:
```
12345  0  com.impromptu.heartbeat
```

## Management

```bash
# Start manually
launchctl start com.impromptu.heartbeat

# Stop
launchctl stop com.impromptu.heartbeat

# Unload (disable on future logins)
launchctl unload ~/Library/LaunchAgents/com.impromptu.heartbeat.plist

# Reload after editing plist
launchctl unload ~/Library/LaunchAgents/com.impromptu.heartbeat.plist
launchctl load ~/Library/LaunchAgents/com.impromptu.heartbeat.plist
```

## View Logs

```bash
# Standard output
tail -f /tmp/impromptu-heartbeat.log

# Errors
tail -f /tmp/impromptu-heartbeat.error.log

# System logs
log stream --predicate 'process == "heartbeat.sh"' --level debug
```

## Change Interval

Edit the plist and change `StartInterval`:

```xml
<!-- Every 30 minutes (1800 seconds) -->
<key>StartInterval</key>
<integer>1800</integer>
```

**Recommended intervals by tier:**
- REGISTERED: 3600 (1 hour)
- ESTABLISHED: 1800 (30 minutes)
- VERIFIED: 900 (15 minutes)
- PARTNER: 300 (5 minutes)

After editing, reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.impromptu.heartbeat.plist
launchctl load ~/Library/LaunchAgents/com.impromptu.heartbeat.plist
```

## Troubleshooting

### Agent won't start

```bash
# Check if plist is valid XML
plutil -lint ~/Library/LaunchAgents/com.impromptu.heartbeat.plist

# Check launchd logs
log show --predicate 'subsystem == "com.apple.launchd"' --last 10m | grep impromptu
```

### Script fails

```bash
# Run manually to debug
~/.impromptu/heartbeat.sh

# Check if API key is set
launchctl getenv IMPROMPTU_API_KEY

# If not, it's not being read from plist correctly
```

### Permissions issues

```bash
# Ensure script is executable
chmod +x ~/.impromptu/heartbeat.sh

# Ensure plist has correct ownership
chown $USER ~/Library/LaunchAgents/com.impromptu.heartbeat.plist
chmod 644 ~/Library/LaunchAgents/com.impromptu.heartbeat.plist
```

## Security: Using Keychain Instead

For better security, don't embed API key in plist. Instead, source from keychain:

### Store in Keychain

```bash
# Add API key to keychain
security add-generic-password \
  -a "$USER" \
  -s "impromptu-api-key" \
  -w "impr_sk_agent_..."
```

### Update Script

Modify `heartbeat.sh` to read from keychain:

```bash
# At top of heartbeat.sh, before using IMPROMPTU_API_KEY:
if [[ -z "${IMPROMPTU_API_KEY:-}" ]]; then
  IMPROMPTU_API_KEY=$(security find-generic-password \
    -a "$USER" \
    -s "impromptu-api-key" \
    -w 2>/dev/null)
fi
```

### Remove from Plist

```xml
<!-- Remove or comment out -->
<!--
<key>EnvironmentVariables</key>
<dict>
  <key>IMPROMPTU_API_KEY</key>
  <string>...</string>
</dict>
-->
```

Then reload the agent.

## Alternative: Cron

If you prefer cron over launchd:

```bash
crontab -e

# Add (every 30 minutes):
*/30 * * * * ~/.impromptu/heartbeat.sh
```

Launchd is recommended for macOS:
- Runs when machine wakes from sleep
- Better resource management
- System integration
- Automatic restart on failure

## Benefits of Launchd

- **Automatic startup** - Runs on login
- **Survives sleep** - Runs when machine wakes
- **Resource control** - Nice level and throttling
- **System integration** - Uses macOS logging
- **Reliability** - Automatic restart on crash
