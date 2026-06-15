# Async Gateway Status - Design Proposal

## Current Problem (v1.1.3)

**Caching helps but still has delays:**
- First check: 500ms blocking
- Cache expiry (every 60s): 500ms blocking
- Most refreshes: instant (cached)

**User experience:**
- Mostly smooth
- Occasional brief pause every 60 seconds

## Proposed Solution: Fully Async

**Never block the dashboard refresh:**

```javascript
let gatewayStatusCache = {
  online: false,
  status: 'Checking...',
  emoji: '⏳'
};
let gatewayCheckInProgress = false;

function checkGatewayStatus() {
  // Immediately return cached value (never block)
  
  // Kick off async check if not already in progress
  if (!gatewayCheckInProgress) {
    gatewayCheckInProgress = true;
    
    // Run check in background
    const { exec } = require('child_process');
    exec('openclaw gateway status', { timeout: 500 }, (error, stdout) => {
      if (!error && stdout) {
        const isRunning = stdout.toLowerCase().includes('online');
        gatewayStatusCache = {
          online: isRunning,
          status: isRunning ? 'Online' : 'Offline',
          emoji: isRunning ? '🟢' : '🔴'
        };
      } else {
        // Keep last known status on error
        gatewayStatusCache = {
          ...gatewayStatusCache,
          status: gatewayStatusCache.status === 'Checking...' ? 'Unknown' : gatewayStatusCache.status
        };
      }
      
      gatewayCheckInProgress = false;
    });
  }
  
  return gatewayStatusCache;
}
```

## Benefits

**User Experience:**
- ✅ Dashboard refresh: instant (0ms) EVERY TIME
- ✅ No visible blocking ever
- ✅ Gateway status updates in background
- ✅ Smooth continuous updates

**Implementation:**
- ✅ Minimal code change (~20 lines)
- ✅ No breaking changes
- ✅ Backward compatible
- ✅ Uses built-in `child_process.exec` (already available)

## Behavior Flow

**First dashboard render:**
```
User runs: tide-watch dashboard --watch
│
├─ Dashboard renders immediately
│  └─ Gateway status: "⏳ Checking..."
│
├─ Background: Gateway check starts (async)
│
├─ 10s later: Dashboard refreshes (instant)
│  └─ Gateway status: "🟢 Online" (check completed)
│
└─ Every 10s: Instant refresh with current status
```

**Watch mode (continuous):**
```
T=0s:   Render (instant) → Status: "⏳ Checking..."
        Background check starts
        
T=10s:  Render (instant) → Status: "🟢 Online"
        (check completed, cache updated)
        
T=20s:  Render (instant) → Status: "🟢 Online"
        (using cached value)
        
T=30s:  Render (instant) → Status: "🟢 Online"
        Background check starts again (periodic)
        
T=40s:  Render (instant) → Status: "🟢 Online"
        ...
```

## Comparison

| Approach | First Refresh | Subsequent | Cache Expiry | Complexity |
|----------|--------------|------------|--------------|------------|
| v1.1.2 (broken) | 1-2.5s block | 1-2.5s block | N/A | Low |
| v1.1.3 (current) | 500ms block | Instant | 500ms block | Low |
| Async (proposed) | Instant | Instant | Instant | Medium |

## Implementation Strategy

### Option A: Simple Async (Recommended)

**When to check:**
- On first call (dashboard starts)
- Every 30-60 seconds (periodic background refresh)

**Pros:**
- Simple logic
- Always instant
- Predictable behavior

**Cons:**
- Gateway status may be slightly stale (up to 60s)

### Option B: Check on Every Refresh (Eager)

**When to check:**
- Kick off async check on EVERY dashboard refresh
- But never wait for it

**Pros:**
- More up-to-date status
- Still never blocks

**Cons:**
- More frequent system calls
- Check in progress flag needed to prevent overlapping checks

### Option C: Smart Refresh

**When to check:**
- On first call
- When cached status is older than 30s
- Only if no check currently in progress

**Pros:**
- Balance between freshness and efficiency
- Never blocks

**Cons:**
- Slightly more complex logic

## Recommended: Option C (Smart Refresh)

```javascript
let gatewayStatusCache = null;
let lastGatewayCheck = 0;
let gatewayCheckInProgress = false;
const GATEWAY_REFRESH_INTERVAL = 30000; // 30 seconds

function checkGatewayStatus() {
  const now = Date.now();
  
  // Start background check if needed
  if (!gatewayCheckInProgress && 
      (!gatewayStatusCache || (now - lastGatewayCheck > GATEWAY_REFRESH_INTERVAL))) {
    startBackgroundGatewayCheck();
  }
  
  // Always return cached value immediately (never block)
  return gatewayStatusCache || {
    online: false,
    status: 'Checking...',
    emoji: '⏳'
  };
}

function startBackgroundGatewayCheck() {
  gatewayCheckInProgress = true;
  
  const { exec } = require('child_process');
  exec('openclaw gateway status', { 
    timeout: 500,
    encoding: 'utf8' 
  }, (error, stdout) => {
    if (!error && stdout) {
      const isRunning = stdout.toLowerCase().includes('online') || 
                        stdout.toLowerCase().includes('running');
      gatewayStatusCache = {
        online: isRunning,
        status: isRunning ? 'Online' : 'Offline',
        emoji: isRunning ? '🟢' : '🔴',
        lastUpdated: Date.now()
      };
      lastGatewayCheck = Date.now();
    } else if (!gatewayStatusCache) {
      // First check failed, set to unknown
      gatewayStatusCache = {
        online: false,
        status: 'Unknown',
        emoji: '❓',
        error: error?.message
      };
      lastGatewayCheck = Date.now();
    }
    // If check fails but we have cache, keep the cache
    
    gatewayCheckInProgress = false;
  });
}
```

## Security Implications

**Analysis:**
- ✅ Uses `exec` (async) instead of `execSync` (blocking)
- ✅ Same command executed: `openclaw gateway status`
- ✅ Same timeout: 500ms
- ✅ No new system access
- ✅ Callback-based, no new dependencies

**Security posture:** BENIGN (same as v1.1.3, just async)

## Testing Plan

1. First dashboard load shows "⏳ Checking..."
2. After ~500ms, status updates to "🟢 Online" or "🔴 Offline"
3. All subsequent refreshes are instant (no flashing)
4. Gateway status updates every 30 seconds in background
5. Works in Terminal.app, iTerm2, Linux terminals

## Estimated Effort

- Implementation: 30 minutes
- Testing: 15 minutes
- Total: ~45 minutes

## Recommendation

✅ **Implement Option C (Smart Refresh)**

**Benefits over current v1.1.3:**
- Eliminates the last remaining blocking points
- Always instant dashboard refresh
- Gateway status updates more frequently (30s vs 60s)
- Better user experience

**Trade-off:**
- Slightly more complex code (callbacks)
- Gateway status may show "Checking..." on first load
- But never blocks the dashboard

Would you like me to implement this now?
