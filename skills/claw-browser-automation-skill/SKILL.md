---
name: claw-browser-automation
version: 2.0.0
description: Complete browser automation with agent-browser CLI. Supports navigation, forms, screenshots, data extraction, and parallel sessions.
category: automation
license: MIT
---

# Agent-Browser Skill v2.0

## Overview

Complete browser automation using `agent-browser` CLI with local Chrome/Chromium. Supports parallel sessions, state persistence, visual debugging, and complex workflows.

## Installation & Setup

### Step 1: Install agent-browser
```bash
npm install -g agent-browser
```

### Step 2: Configure Chrome Path

**macOS:**
```bash
export AGENT_BROWSER_EXECUTABLE_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Add to ~/.zshrc for persistence
echo 'export AGENT_BROWSER_EXECUTABLE_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"' >> ~/.zshrc
```

**Linux:**
```bash
export AGENT_BROWSER_EXECUTABLE_PATH="/usr/bin/google-chrome"
# Or for Chromium
export AGENT_BROWSER_EXECUTABLE_PATH="/usr/bin/chromium-browser"
```

**Windows:**
```powershell
$env:AGENT_BROWSER_EXECUTABLE_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
```

### Step 3: Verify Installation
```bash
agent-browser --version
agent-browser open https://example.com
agent-browser snapshot -i
```

## Core Workflow

Every browser automation follows this 4-step pattern:

```bash
# 1. Navigate to URL
agent-browser open https://example.com/form

# 2. Get snapshot with interactive element refs
agent-browser snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

# 3. Interact using refs
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3

# 4. Wait and verify
agent-browser wait --load networkidle
agent-browser snapshot -i
```

## Complete Command Reference

### Navigation Commands

```bash
# Open URL
agent-browser open <url>                    # Navigate to URL
agent-browser open <url> --session <name>   # Open in named session
agent-browser open <url> --headless         # Headless mode

# Navigation control
agent-browser back                          # Go back
agent-browser forward                       # Go forward
agent-browser refresh                       # Refresh page
agent-browser close                         # Close browser
agent-browser close --session <name>        # Close specific session
```

### Snapshot Commands

```bash
# Basic snapshot
agent-browser snapshot                      # Full page snapshot
agent-browser snapshot -i                   # Interactive elements only (recommended)
agent-browser snapshot -i -C                # Include cursor-interactive (onclick, cursor:pointer)
agent-browser snapshot -s "#selector"       # Scope to CSS selector
agent-browser snapshot --json               # Output as JSON
agent-browser snapshot --depth 3            # Limit DOM depth
```

### Interaction Commands

```bash
# Click actions
agent-browser click @e1                     # Click element
agent-browser click @e1 --double            # Double click
agent-browser click @e1 --right             # Right click
agent-browser click @e1 --modifiers Ctrl    # With modifier (Ctrl, Alt, Shift, Meta)

# Text input
agent-browser fill @e2 "text"               # Clear then type
agent-browser type @e2 "text"               # Type without clearing
agent-browser type @e2 "text" --slowly      # Type slowly (for rate-limited inputs)

# Selection
agent-browser select @e3 "option"           # Select dropdown option
agent-browser select @e3 --index 2          # Select by index
agent-browser check @e4                     # Check checkbox
agent-browser uncheck @e4                   # Uncheck checkbox
agent-browser radio @e5                     # Select radio button

# Keyboard
agent-browser press Enter                   # Press key
agent-browser press Tab                     # Tab key
agent-browser press Escape                  # Escape key
agent-browser press Ctrl+A                  # Select all
agent-browser press Ctrl+C                  # Copy
agent-browser press Ctrl+V                  # Paste

# Mouse actions
agent-browser hover @e1                     # Hover over element
agent-browser scroll down 500               # Scroll down 500px
agent-browser scroll up 300                 # Scroll up
agent-browser scroll to @e1                 # Scroll to element
```

### Wait Commands

```bash
# Wait for element
agent-browser wait @e1                      # Wait for element visible
agent-browser wait @e1 --timeout 10000      # Custom timeout (ms)

# Wait for page state
agent-browser wait --load networkidle       # Wait for network idle
agent-browser wait --load domcontentloaded  # Wait for DOMContentLoaded
agent-browser wait --load load              # Wait for full page load

# Wait for URL
agent-browser wait --url "**/dashboard"     # Wait for URL pattern
agent-browser wait --url "**/login" --gone  # Wait for URL to disappear

# Wait for text
agent-browser wait --text "Welcome"         # Wait for text visible
agent-browser wait --text "Error" --gone    # Wait for text to disappear

# Time wait
agent-browser wait 2000                     # Wait 2 seconds
```

### Get Information

```bash
agent-browser get text @e1                  # Get element text
agent-browser get text @e1 --json           # JSON output
agent-browser get html @e1                  # Get element HTML
agent-browser get attribute @e1 href        # Get attribute value
agent-browser get url                       # Get current URL
agent-browser get title                     # Get page title
agent-browser get count ".product"          # Count elements matching selector
```

### Capture Commands

```bash
# Screenshots
agent-browser screenshot                    # Screenshot to temp dir
agent-browser screenshot --full             # Full page screenshot
agent-browser screenshot --output ./img.png # Save to specific path
agent-browser screenshot --element @e1      # Screenshot specific element

# PDF
agent-browser pdf output.pdf                # Save page as PDF
agent-browser pdf output.pdf --landscape    # Landscape orientation

# Video (requires extension)
agent-browser record start                  # Start recording
agent-browser record stop                   # Stop recording
```

### Session Management

```bash
# List sessions
agent-browser session list

# Save/Load state
agent-browser state save auth.json          # Save session state
agent-browser state load auth.json          # Load saved state
agent-browser state clear                   # Clear all saved states

# Parallel sessions
agent-browser --session site1 open https://site-a.com
agent-browser --session site2 open https://site-b.com
agent-browser --session site1 click @e1
agent-browser --session site2 click @e2
```

## Common Patterns & Recipes

### Pattern 1: Form Submission with Validation

```bash
#!/bin/bash
# submit-form.sh

set -e

# Navigate to form
agent-browser open https://example.com/signup

# Wait for form and get snapshot
agent-browser wait @e1 --timeout 10000
agent-browser snapshot -i

# Fill form fields
agent-browser fill @e1 "John Doe"           # Name
agent-browser fill @e2 "john@example.com"   # Email
agent-browser fill @e3 "SecurePass123!"     # Password
agent-browser fill @e4 "SecurePass123!"     # Confirm password

# Accept terms
agent-browser check @e5

# Submit
agent-browser click @e6

# Wait for success
agent-browser wait --text "Welcome" --timeout 15000

# Verify and capture
agent-browser screenshot --output ./success.png
echo "Form submitted successfully!"
```

### Pattern 2: Authentication with State Persistence

```bash
#!/bin/bash
# auth-flow.sh

STATE_FILE="auth-state.json"

# Check if we have saved state
if [ -f "$STATE_FILE" ]; then
    echo "Loading saved authentication state..."
    agent-browser state load "$STATE_FILE"
    agent-browser open https://app.example.com/dashboard
    
    # Verify still logged in
    if agent-browser wait --text "Dashboard" --timeout 5000 2>/dev/null; then
        echo "✓ Authenticated with saved state"
        exit 0
    else
        echo "Session expired, re-authenticating..."
    fi
fi

# Fresh login
echo "Performing fresh login..."
agent-browser open https://app.example.com/login
agent-browser snapshot -i

agent-browser fill @e1 "$USERNAME"
agent-browser fill @e2 "$PASSWORD"
agent-browser click @e3

# Wait for dashboard
agent-browser wait --url "**/dashboard" --timeout 15000

# Save state for future use
agent-browser state save "$STATE_FILE"
echo "✓ Login successful, state saved"
```

### Pattern 3: Data Extraction from Tables

```bash
#!/bin/bash
# extract-data.sh

agent-browser open https://example.com/products
agent-browser wait --load networkidle
agent-browser snapshot -i

# Extract all product data
OUTPUT_FILE="products.json"
echo "[" > "$OUTPUT_FILE"

# Get product count
COUNT=$(agent-browser get count ".product-item")
echo "Found $COUNT products"

# Extract each product
for i in $(seq 0 $((COUNT-1))); do
    REF=".product-item:nth-child($((i+1)))"
    
    NAME=$(agent-browser get text "$REF .product-name" --json)
    PRICE=$(agent-browser get text "$REF .product-price" --json)
    STOCK=$(agent-browser get text "$REF .product-stock" --json)
    
    # Add comma for all but last item
    if [ $i -lt $((COUNT-1)) ]; then
        echo "  {\"name\": $NAME, \"price\": $PRICE, \"stock\": $Stock}," >> "$OUTPUT_FILE"
    else
        echo "  {\"name\": $NAME, \"price\": $PRICE, \"stock\": $Stock}" >> "$OUTPUT_FILE"
    fi
done

echo "]" >> "$OUTPUT_FILE"
echo "Data extracted to $OUTPUT_FILE"
```

### Pattern 4: Multi-Page Pagination

```bash
#!/bin/bash
# paginate.sh

PAGE=1
MAX_PAGES=10

while [ $PAGE -le $MAX_PAGES ]; do
    echo "Processing page $PAGE..."
    
    # Navigate to page
    agent-browser open "https://example.com/items?page=$PAGE"
    agent-browser wait --load networkidle
    
    # Extract data from this page
    agent-browser snapshot -i
    # ... extraction logic ...
    
    # Check for next page button
    if agent-browser wait @next-page --timeout 3000 2>/dev/null; then
        agent-browser click @next-page
        PAGE=$((PAGE + 1))
    else
        echo "No more pages"
        break
    fi
done
```

### Pattern 5: Visual Regression Testing

```bash
#!/bin/bash
# visual-test.sh

BASELINE_DIR="./baseline"
CURRENT_DIR="./current"
DIFF_DIR="./diff"

mkdir -p "$BASELINE_DIR" "$CURRENT_DIR" "$DIFF_DIR"

# Capture current state
agent-browser open https://example.com
agent-browser wait --load networkidle
agent-browser screenshot --full --output "$CURRENT_DIR/homepage.png"

# Compare with baseline (requires imagemagick)
if [ -f "$BASELINE_DIR/homepage.png" ]; then
    compare -metric AE "$BASELINE_DIR/homepage.png" "$CURRENT_DIR/homepage.png" "$DIFF_DIR/homepage-diff.png" 2>&1 || true
    echo "Visual diff saved to $DIFF_DIR/homepage-diff.png"
else
    echo "No baseline found. Creating baseline..."
    cp "$CURRENT_DIR/homepage.png" "$BASELINE_DIR/homepage.png"
fi
```

### Pattern 6: API Testing via Browser DevTools

```bash
#!/bin/bash
# api-test.sh

agent-browser open https://api.example.com/docs
agent-browser snapshot -i

# Execute JavaScript in browser context
RESPONSE=$(agent-browser eval '
    fetch("/api/v1/users", {
        headers: { "Authorization": "Bearer TOKEN" }
    }).then(r => r.json()).then(d => JSON.stringify(d))
')

echo "API Response: $RESPONSE"
```

## Error Handling & Troubleshooting

### Common Errors and Solutions

#### Error: "No browser found"
```bash
# Solution: Set Chrome path explicitly
export AGENT_BROWSER_EXECUTABLE_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Or use flag
agent-browser --executable-path /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome open https://example.com
```

#### Error: "Element not found @e1"
```bash
# Solution 1: Wait for element
agent-browser wait @e1 --timeout 10000

# Solution 2: Re-snapshot after page load
agent-browser wait --load networkidle
agent-browser snapshot -i

# Solution 3: Check selector scope
agent-browser snapshot -s "#form-container"
```

#### Error: "Navigation timeout"
```bash
# Solution: Increase timeout
agent-browser open https://slow-site.com --timeout 60000

# Or wait for specific event
agent-browser wait --load domcontentloaded
```

#### Error: "Session already exists"
```bash
# Solution: Close existing session
agent-browser close --session <name>

# Or use different session name
agent-browser --session <new-name> open <url>
```

### Debugging Tips

```bash
# Enable verbose logging
agent-browser open https://example.com --verbose

# Take screenshot at any point
agent-browser screenshot --output ./debug-$(date +%s).png

# Get current URL to verify navigation
agent-browser get url

# Check console logs
agent-browser console

# Evaluate JavaScript to inspect state
agent-browser eval 'document.querySelectorAll(".product").length'
```

## Best Practices

### 1. Always Wait for Elements
```bash
# ❌ BAD - May fail if element not ready
agent-browser click @e1

# ✅ GOOD - Wait first
agent-browser wait @e1 --timeout 10000
agent-browser click @e1
```

### 2. Use Specific Selectors
```bash
# ❌ BAD - Too generic
agent-browser snapshot -s "div"

# ✅ GOOD - Specific and stable
agent-browser snapshot -s "#login-form button[type='submit']"
```

### 3. Handle Dynamic Content
```bash
# Wait for network to settle
agent-browser wait --load networkidle

# Or wait for specific content
agent-browser wait --text "Loading complete"
```

### 4. Save Authentication State
```bash
# Login once, reuse many times
agent-browser state save auth.json

# Load in subsequent runs
agent-browser state load auth.json
```

### 5. Use Sessions for Parallel Work
```bash
# Run multiple independent sessions
agent-browser --session user1 open https://app.com
agent-browser --session user2 open https://app.com

# Each session maintains its own state
```

### 6. Handle Rate Limiting
```bash
# Add delays between actions
agent-browser type @e1 "text" --slowly
agent-browser wait 1000  # 1 second delay
```

## Advanced Features

### Custom JavaScript Execution

```bash
# Execute arbitrary JavaScript
agent-browser eval 'document.title'
agent-browser eval 'window.innerWidth'
agent-browser eval 'document.querySelectorAll(".item").length'

# Complex operations
agent-browser eval '
    Array.from(document.querySelectorAll(".product")).map(p => ({
        name: p.querySelector(".name").textContent,
        price: p.querySelector(".price").textContent
    }))
'
```

### File Upload

```bash
# Upload file to file input
agent-browser upload @file-input ./document.pdf

# Or with absolute path
agent-browser upload @file-input /absolute/path/to/file.txt
```

### Dialog Handling

```bash
# Accept alert/confirm
agent-browser dialog accept

# Dismiss
agent-browser dialog dismiss

# Handle prompt with text
agent-browser dialog accept --text "Default value"
```

### Cookie Management

```bash
# Get cookies
agent-browser cookie get

# Set cookie
agent-browser cookie set name=value --domain example.com

# Clear cookies
agent-browser cookie clear
```

## Performance Optimization

### 1. Use Headless Mode for CI/CD
```bash
agent-browser open https://example.com --headless
```

### 2. Limit Snapshot Depth
```bash
agent-browser snapshot --depth 2  # Faster on complex pages
```

### 3. Reuse Sessions
```bash
# Keep session alive for multiple operations
agent-browser --session main open https://example.com
agent-browser --session main click @e1
agent-browser --session main click @e2
agent-browser --session main close
```

### 4. Parallel Execution
```bash
# Run multiple sessions in parallel
agent-browser --session s1 open https://site1.com &
agent-browser --session s2 open https://site2.com &
wait
```

## Security Considerations

### 1. Never Hardcode Credentials
```bash
# ❌ BAD
agent-browser fill @password "MySecret123"

# ✅ GOOD - Use environment variables
agent-browser fill @password "$PASSWORD"
```

### 2. Clear Sensitive State
```bash
# After handling sensitive data
agent-browser state clear
agent-browser cookie clear
```

### 3. Use HTTPS Only
```bash
# Always use HTTPS URLs
agent-browser open https://example.com  # ✅
agent-browser open http://example.com   # ❌
```

## Dependencies

- **Node.js**: Version 18 or higher
- **Chrome/Chromium**: Latest version recommended
- **agent-browser**: `npm install -g agent-browser`

## Testing Your Setup

Run this quick test to verify everything works:

```bash
#!/bin/bash
# test-setup.sh

echo "Testing agent-browser setup..."

# Test 1: Version check
echo "1. Checking version..."
agent-browser --version

# Test 2: Open page
echo "2. Opening test page..."
agent-browser open https://example.com

# Test 3: Get title
echo "3. Getting page title..."
TITLE=$(agent-browser get title)
echo "Title: $TITLE"

# Test 4: Screenshot
echo "4. Taking screenshot..."
agent-browser screenshot --output ./test-screenshot.png

# Test 5: Snapshot
echo "5. Getting snapshot..."
agent-browser snapshot -i | head -5

echo "✓ All tests passed!"
```

## License

MIT License - See LICENSE file for details.

## Support

For issues and feature requests, visit the agent-browser repository.
