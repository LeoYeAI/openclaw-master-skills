# Troubleshooting Guide

This guide helps diagnose and resolve common issues when using nstbrowser-ai-agent with NST profiles.

## Connection Issues

### "NST_API_KEY is required"

**Symptom**: Commands fail with error message about missing API key.

**Cause**: NST_API_KEY environment variable is not set.

**Solution**:
```bash
# Set the API key
export NST_API_KEY="your-api-key-here"

# Or add to .nstbrowser-ai-agent.env
echo "NST_API_KEY=your-api-key-here" >> .nstbrowser-ai-agent.env
```

**Diagnostic Commands**:
```bash
# Check if API key is set
echo $NST_API_KEY

# Verify environment file exists
cat .nstbrowser-ai-agent.env
```

### "Failed to connect to Nstbrowser"

**Symptom**: Commands fail with connection error.

**Causes**:
- NST client is not running
- Wrong host or port configuration
- Firewall blocking connection

**Solutions**:

1. Check if NST client is running:
```bash
# Check if NST is listening on the configured port
lsof -i :8848  # Replace 8848 with your NST_PORT

# Or use netstat
netstat -an | grep 8848
```

2. Verify host and port configuration:
```bash
# Check environment variables
echo $NST_HOST
echo $NST_PORT

# Test connection
curl http://$NST_HOST:$NST_PORT/api/v1/profiles
```

3. Start NST client if not running:
```bash
# Start NST client (method depends on your setup)
# Follow NST documentation for your platform
```

4. Check firewall settings:
```bash
# macOS: Check if port is allowed
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps

# Linux: Check iptables
sudo iptables -L -n | grep 8848
```

**Diagnostic Commands**:
```bash
# Test API connectivity
nstbrowser-ai-agent profile list

# Check NST client status
curl -v http://127.0.0.1:8848/api/v1/profiles
```

### Network Connectivity Problems

**Symptom**: Intermittent connection failures or timeouts.

**Causes**:
- Network instability
- NST client overloaded
- Too many concurrent requests

**Solutions**:

1. Increase timeout:
```bash
# Set longer timeout
export NSTBROWSER_AI_AGENT_DEFAULT_TIMEOUT=60000  # 60 seconds
```

2. Reduce concurrent operations:
```bash
# Process profiles in smaller batches
# Instead of updating 100 profiles at once, do 10 at a time
```

3. Check NST client logs for errors

**Diagnostic Commands**:
```bash
# Test connection stability
for i in {1..10}; do
  echo "Test $i"
  nstbrowser-ai-agent profile list > /dev/null && echo "OK" || echo "FAIL"
  sleep 1
done
```

## Profile Issues

### "Profile not found"

**Symptom**: Commands fail with "Profile not found" error.

**Causes**:
- Profile name or ID is incorrect
- Profile was deleted
- Typo in profile name

**Solutions**:

1. List all profiles to verify:
```bash
# List all profiles
nstbrowser-ai-agent profile list

# Search for profile by name pattern
nstbrowser-ai-agent profile list | grep "profile-name"
```

2. Use profile ID instead of name:
```bash
# Show profile by ID (more reliable)
nstbrowser-ai-agent profile show af2f775b-0d6a-4d09-9544-aacfec118364
```

3. Check for typos in profile name:
```bash
# Profile names are case-sensitive
# "MyProfile" ≠ "myprofile"
```

**Diagnostic Commands**:
```bash
# List profiles with JSON output for detailed info
nstbrowser-ai-agent profile list --json

# Search for profile by partial name
nstbrowser-ai-agent profile list --json | jq '.[] | select(.name | contains("partial"))'
```

### Profile Name Resolution Failures

**Symptom**: Wrong profile is selected or profile not found despite correct name.

**Cause**: Multiple profiles with similar names or confusion between name and ID.

**Solution**: Use the `--profile` flag with either profile name or UUID:

```bash
# Use profile name
nstbrowser-ai-agent --profile "MyProfile" browser start

# Use profile UUID directly (auto-detected)
nstbrowser-ai-agent --profile af2f775b-0d6a-4d09-9544-aacfec118364 browser start
```

**Diagnostic Commands**:
```bash
# Check which profile would be selected
echo "Profile ID: $NST_PROFILE_ID"
echo "Profile Name: $NST_PROFILE"

# List profiles to find the correct ID
nstbrowser-ai-agent profile list --json | jq '.[] | {name, profileId}'
```

### Profile Creation Failures

**Symptom**: Profile creation fails or creates profile with unexpected settings.

**Causes**:
- Invalid parameters
- Insufficient permissions
- NST client limitations

**Solutions**:

1. Verify parameters:
```bash
# Check valid platform values
# Valid: Windows, macOS, Linux

# Check proxy configuration
# Ensure proxy-host and proxy-port are correct
```

2. Create profile with minimal options first:
```bash
# Create basic profile
nstbrowser-ai-agent profile create "test-profile"

# Then update with additional settings
nstbrowser-ai-agent profile proxy update test-profile \
  --proxy-host proxy.example.com \
  --proxy-port 8080
```

3. Check NST client logs for detailed error messages

**Diagnostic Commands**:
```bash
# Test profile creation
nstbrowser-ai-agent profile create "test-$(date +%s)"

# Verify profile was created
nstbrowser-ai-agent profile list | grep "test-"

# Clean up test profile
nstbrowser-ai-agent profile delete <profile-name-or-id>
```

## Proxy Issues

### Proxy Connection Failures

**Symptom**: Browser fails to connect through proxy or shows "proxy connection refused".

**Causes**:
- Proxy server is down
- Incorrect proxy host or port
- Proxy requires authentication but credentials not provided
- Proxy type mismatch (http vs socks5)

**Solutions**:

1. Test proxy connectivity:
```bash
# Test HTTP proxy
curl -x http://proxy.example.com:8080 https://api.ipify.org

# Test SOCKS5 proxy
curl --socks5 proxy.example.com:1080 https://api.ipify.org
```

2. Verify proxy configuration:
```bash
# Show profile proxy settings
nstbrowser-ai-agent profile proxy show <profile-name> --json

# Update proxy settings
nstbrowser-ai-agent profile proxy update <profile-name> \
  --proxy-host proxy.example.com \
  --proxy-port 8080 \
  --proxy-type http
```

3. Add authentication if required:
```bash
# Update proxy with credentials
nstbrowser-ai-agent profile proxy update <profile-name> \
  --proxy-host proxy.example.com \
  --proxy-port 8080 \
  --proxy-username user \
  --proxy-password pass
```

**Diagnostic Commands**:
```bash
# Check proxy settings
nstbrowser-ai-agent profile proxy show <profile-name>

# Test proxy with curl
curl -x http://user:pass@proxy.example.com:8080 https://api.ipify.org

# Check if proxy is reachable
nc -zv proxy.example.com 8080
```

### Proxy Authentication Errors

**Symptom**: "407 Proxy Authentication Required" or similar errors.

**Cause**: Proxy requires authentication but credentials are missing or incorrect.

**Solutions**:

1. Add or update proxy credentials:
```bash
# Update proxy with authentication
nstbrowser-ai-agent profile proxy update <profile-name> \
  --proxy-username your-username \
  --proxy-password your-password
```

2. Verify credentials are correct:
```bash
# Test proxy authentication with curl
curl -x http://username:password@proxy.example.com:8080 https://api.ipify.org
```

3. Check if password contains special characters:
```bash
# URL-encode special characters in password
# Or use environment variables to avoid shell escaping issues
export PROXY_PASSWORD='your-password-with-special-chars'
```

**Diagnostic Commands**:
```bash
# Show proxy configuration (password will be masked)
nstbrowser-ai-agent profile proxy show <profile-name>

# Test authentication
curl -v -x http://user:pass@proxy.example.com:8080 https://api.ipify.org 2>&1 | grep "407"
```

### Proxy Timeout Issues

**Symptom**: Browser hangs or times out when using proxy.

**Causes**:
- Slow proxy server
- Proxy server overloaded
- Network latency
- Proxy server blocking certain domains

**Solutions**:

1. Increase timeout:
```bash
# Set longer timeout
export NSTBROWSER_AI_AGENT_DEFAULT_TIMEOUT=60000  # 60 seconds

# Or use --timeout flag
nstbrowser-ai-agent --timeout 60000 browser start <profile-name>
```

2. Test proxy speed:
```bash
# Measure proxy response time
time curl -x http://proxy.example.com:8080 https://example.com
```

3. Try different proxy:
```bash
# Update to faster proxy
nstbrowser-ai-agent profile proxy update <profile-name> \
  --proxy-host faster-proxy.example.com \
  --proxy-port 8080
```

4. Check if proxy is blocking the target domain:
```bash
# Test specific domain through proxy
curl -x http://proxy.example.com:8080 https://target-domain.com
```

**Diagnostic Commands**:
```bash
# Test proxy latency
for i in {1..5}; do
  time curl -x http://proxy.example.com:8080 https://example.com > /dev/null 2>&1
done

# Check proxy server status
curl -x http://proxy.example.com:8080 https://api.ipify.org
```

## Browser Instance Issues

### Browser Fails to Start

**Symptom**: `browser start` command fails or hangs.

**Causes**:
- Chrome/Chromium not installed
- Insufficient system resources
- Profile corruption
- Port conflicts

**Solutions**:

1. Verify Chrome is installed:
```bash
# Check Chrome installation
which google-chrome || which chromium || which chrome

# Install Chrome if missing (macOS)
brew install --cask google-chrome

# Install Chrome if missing (Linux)
sudo apt-get install google-chrome-stable
```

2. Check system resources:
```bash
# Check available memory
free -h  # Linux
vm_stat  # macOS

# Check CPU usage
top -l 1 | grep "CPU usage"  # macOS
top -bn1 | grep "Cpu(s)"     # Linux
```

3. Try with a different profile:
```bash
# Create fresh profile
nstbrowser-ai-agent profile create "test-profile"

# Try starting browser with new profile
nstbrowser-ai-agent browser start test-profile
```

4. Check for port conflicts:
```bash
# List all browser instances
nstbrowser-ai-agent browser list

# Stop all browsers
nstbrowser-ai-agent browser stop-all
```

**Diagnostic Commands**:
```bash
# Check Chrome version
google-chrome --version

# Test browser launch with debug output
NSTBROWSER_AI_AGENT_DEBUG=1 nstbrowser-ai-agent browser start <profile-name>

# Check NST client logs for errors
```

### Browser Crashes

**Symptom**: Browser starts but crashes shortly after or during operation.

**Causes**:
- Insufficient memory
- Incompatible Chrome version
- Corrupted profile data
- Extension conflicts

**Solutions**:

1. Clear profile cache and cookies:
```bash
# Clear cache
nstbrowser-ai-agent profile cache clear <profile-name-or-id>

# Clear cookies
nstbrowser-ai-agent profile cookies clear <profile-name-or-id>
```

2. Update Chrome to latest version:
```bash
# macOS
brew upgrade google-chrome

# Linux
sudo apt-get update && sudo apt-get upgrade google-chrome-stable
```

3. Increase memory allocation:
```bash
# Close other applications to free memory
# Or use a machine with more RAM
```

4. Create new profile:
```bash
# If profile is corrupted, create new one
nstbrowser-ai-agent profile create "new-profile" \
  --platform Windows \
  --kernel 126
```

**Diagnostic Commands**:
```bash
# Monitor browser process
ps aux | grep chrome

# Check system memory during browser operation
watch -n 1 free -h  # Linux
watch -n 1 vm_stat  # macOS

# Check Chrome crash logs
# macOS: ~/Library/Application Support/Google/Chrome/Crash Reports/
# Linux: ~/.config/google-chrome/Crash Reports/
```

### Browser Becomes Unresponsive

**Symptom**: Browser hangs or stops responding to commands.

**Causes**:
- Page loading timeout
- JavaScript infinite loop
- Memory leak
- Network issues

**Solutions**:

1. Stop and restart browser:
```bash
# Stop browser
nstbrowser-ai-agent browser stop <profile-name>

# Wait a few seconds
sleep 5

# Start again
nstbrowser-ai-agent browser start <profile-name>
```

2. Use shorter timeouts:
```bash
# Set timeout for page loads
nstbrowser-ai-agent --timeout 30000 open https://example.com
```

3. Check browser debugger:
```bash
# Get debugger URL
nstbrowser-ai-agent browser debugger <profile-name>

# Open in Chrome DevTools to inspect
```

4. Force stop if necessary:
```bash
# Stop all browsers
nstbrowser-ai-agent browser stop-all

# Or kill Chrome processes manually
pkill -f chrome
```

**Diagnostic Commands**:
```bash
# Check browser status
nstbrowser-ai-agent browser list

# Get debugger URL for inspection
nstbrowser-ai-agent browser debugger <profile-name> --json

# Check browser pages
nstbrowser-ai-agent browser pages <profile-name>
```

## Ref System Issues

### Refs Not Working with Modern Frameworks

**Symptom**: Refs fail to find elements in React, Vue, or other SPA frameworks.

**Cause**: Modern frameworks use dynamic rendering and refs may not be stable.

**Solutions**:

1. Use CSS selectors instead:
```bash
# Instead of refs
nstbrowser-ai-agent click "button[data-testid='submit']"

# Or use text content
nstbrowser-ai-agent click "text=Submit"
```

2. Wait for elements to be ready:
```bash
# Take snapshot first to ensure page is loaded
nstbrowser-ai-agent snapshot

# Then interact with elements
nstbrowser-ai-agent click "ref:123"
```

3. Use stable selectors:
```bash
# Use data attributes that don't change
nstbrowser-ai-agent click "[data-testid='login-button']"

# Or use ARIA labels
nstbrowser-ai-agent click "[aria-label='Login']"
```

**Diagnostic Commands**:
```bash
# Take snapshot to see available refs
nstbrowser-ai-agent snapshot --json

# Check if element exists with CSS selector
nstbrowser-ai-agent eval "document.querySelector('button[data-testid=\"submit\"]')"
```

### Stale Refs After Page Changes

**Symptom**: Refs work initially but fail after navigation or dynamic updates.

**Cause**: Refs are tied to specific page state and become invalid after changes.

**Solutions**:

1. Take new snapshot after page changes:
```bash
# Navigate to page
nstbrowser-ai-agent open https://example.com

# Take snapshot
nstbrowser-ai-agent snapshot

# Interact with page
nstbrowser-ai-agent click "ref:123"

# After page change, take new snapshot
nstbrowser-ai-agent snapshot

# Use new refs
nstbrowser-ai-agent click "ref:456"
```

2. Use CSS selectors for dynamic content:
```bash
# More reliable for SPAs
nstbrowser-ai-agent click "button.submit-btn"
```

3. Implement retry logic:
```bash
# Retry with new snapshot if ref fails
nstbrowser-ai-agent click "ref:123" || {
  nstbrowser-ai-agent snapshot
  nstbrowser-ai-agent click "button.submit-btn"
}
```

**Diagnostic Commands**:
```bash
# Check current page state
nstbrowser-ai-agent snapshot --json | jq '.url'

# List available refs
nstbrowser-ai-agent snapshot --json | jq '.refs[]'
```

## General Troubleshooting

### Checking NST Client Status

```bash
# Check if NST client is running
ps aux | grep nst

# Check NST client port
lsof -i :8848  # Replace with your NST_PORT

# Test API connectivity
curl http://127.0.0.1:8848/api/v1/profiles
```

### Verifying API Connectivity

```bash
# Test profile list
nstbrowser-ai-agent profile list

# Test with JSON output
nstbrowser-ai-agent profile list --json

# Test specific profile
nstbrowser-ai-agent profile show <profile-name>
```

### Reviewing Logs

```bash
# Enable debug mode
export NSTBROWSER_AI_AGENT_DEBUG=1

# Run command with debug output
nstbrowser-ai-agent browser start <profile-name>

# Check NST client logs (location depends on your setup)
# Common locations:
# - ~/.nstbrowser/logs/
# - /var/log/nstbrowser/
# - Application-specific log directory
```

### Getting Help

If you're still experiencing issues:

1. Check the documentation:
   - README.md for general usage
   - references/nst-api-reference.md for API details
   - references/profile-management.md for profile issues
   - references/proxy-configuration.md for proxy issues

2. Enable debug mode and collect logs:
```bash
export NSTBROWSER_AI_AGENT_DEBUG=1
nstbrowser-ai-agent <command> 2>&1 | tee debug.log
```

3. Check GitHub issues:
   - Search existing issues: https://github.com/pandapro-project/nstbrowser-ai-agent/issues
   - Create new issue with debug logs and reproduction steps

4. Contact NST support for NST client issues:
   - NST client configuration
   - NST API problems
   - Profile synchronization issues

## Quick Reference

### Common Error Messages

| Error Message | Likely Cause | Quick Fix |
|--------------|--------------|-----------|
| "NST_API_KEY is required" | Missing API key | Set NST_API_KEY environment variable |
| "Failed to connect to Nstbrowser" | NST client not running | Start NST client |
| "Profile not found" | Wrong profile name/ID | List profiles and verify name |
| "407 Proxy Authentication Required" | Missing proxy credentials | Add proxy username and password |
| "Browser failed to start" | Chrome not installed | Install Chrome/Chromium |
| "Timeout waiting for page" | Slow page load | Increase timeout value |
| "Ref not found" | Stale ref or dynamic content | Take new snapshot or use CSS selector |

### Diagnostic Command Checklist

```bash
# 1. Check environment
echo $NST_API_KEY
echo $NST_HOST
echo $NST_PORT

# 2. Test NST connectivity
curl http://127.0.0.1:8848/api/v1/profiles

# 3. List profiles
nstbrowser-ai-agent profile list

# 4. Check browser instances
nstbrowser-ai-agent browser list

# 5. Test browser launch
nstbrowser-ai-agent browser start <profile-name>

# 6. Check browser status
nstbrowser-ai-agent browser pages <profile-name>

# 7. Get debugger URL
nstbrowser-ai-agent browser debugger <profile-name>
```
