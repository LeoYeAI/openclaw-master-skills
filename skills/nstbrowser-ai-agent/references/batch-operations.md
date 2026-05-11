# Batch Operations Guide

Guide for performing efficient operations on multiple Nstbrowser profiles.

## Table of Contents

- [Batch Operations Overview](#batch-operations-overview)
- [Batch Proxy Operations](#batch-proxy-operations)
- [Batch Tag Operations](#batch-tag-operations)
- [Batch Group Operations](#batch-group-operations)
- [Batch Local Data Operations](#batch-local-data-operations)
- [Best Practices](#best-practices)

## Batch Operations Overview

### Benefits of Batch Operations

**Efficiency:**
- Single API call instead of multiple calls
- Faster execution for large numbers of profiles
- Reduced network overhead

**Consistency:**
- All profiles updated with same configuration
- Atomic operations (all succeed or all fail)
- Easier to track and verify changes

**Simplicity:**
- One command instead of loops
- Less code to write and maintain
- Clearer intent

### When to Use Batch Operations

**Use batch operations when:**
- Updating 3+ profiles with same configuration
- Need consistent settings across profiles
- Want faster execution
- Performing routine maintenance

**Use individual operations when:**
- Each profile needs different configuration
- Need fine-grained control
- Want to handle errors per profile
- Testing configuration changes

### Performance Considerations

**Batch Size:**
- Recommended: 10-50 profiles per batch
- Maximum: 100 profiles per batch
- Larger batches may timeout

**Execution Time:**
- ~1-2 seconds per batch (regardless of size)
- Individual operations: ~0.5 seconds each
- Batch of 10 profiles: 10x faster than individual

**Error Handling:**
- Batch operations are atomic
- If one profile fails, entire batch fails
- Check individual profile status after failure

## Batch Proxy Operations

### Batch Update Proxy

Update proxy configuration for multiple profiles:

```bash
nstbrowser-ai-agent profile proxy batch-update <id-1> <id-2> <id-3> \
  --host proxy.example.com \
  --port 8080 \
  --type http \
  --username user \
  --password pass
```

**Example - Update 10 Profiles:**
```bash
# Get profile IDs
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | jq -r '.data.profiles[0:10] | map(.profileId) | join(" ")')

# Batch update
nstbrowser-ai-agent profile proxy batch-update $PROFILE_IDS \
  --host proxy.example.com \
  --port 8080 \
  --type http
```

**Use Cases:**
- Switch all profiles to new proxy server
- Update proxy credentials after rotation
- Configure proxies for new project
- Migrate profiles to different proxy provider

### Batch Reset Proxy

Remove proxy configuration from multiple profiles:

```bash
nstbrowser-ai-agent profile proxy batch-reset <id-1> <id-2> <id-3>
```

**Example - Reset All Profiles in Group:**
```bash
# Get profile IDs from specific group
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles[] | select(.group.name == "Testing") | .profileId' | \
  tr '\n' ' ')

# Batch reset
nstbrowser-ai-agent profile proxy batch-reset $PROFILE_IDS
```

**Use Cases:**
- Remove proxies from test profiles
- Clean up after project completion
- Prepare profiles for different use case
- Troubleshoot proxy issues

## Batch Tag Operations

### Batch Create Tags

Add tags to multiple profiles:

```bash
nstbrowser-ai-agent profile tags batch-create <id-1> <id-2> <id-3> \
  production:blue automated:green
```

**Example - Tag All Active Profiles:**
```bash
# Get active profile IDs
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles[] | select(.tags[] | .name == "active") | .profileId' | \
  tr '\n' ' ')

# Add tags
nstbrowser-ai-agent profile tags batch-create $PROFILE_IDS \
  verified:green updated:blue
```

**Use Cases:**
- Mark profiles as verified after testing
- Tag profiles with deployment date
- Add project identifier to profiles
- Mark profiles for specific purpose

### Batch Update Tags

Replace all tags for multiple profiles:

```bash
nstbrowser-ai-agent profile tags batch-update <id-1> <id-2> <id-3> \
  updated:red verified:green
```

**Example - Update Tags for Production Profiles:**
```bash
# Get production profile IDs
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles[] | select(.group.name == "Production") | .profileId' | \
  tr '\n' ' ')

# Update tags
nstbrowser-ai-agent profile tags batch-update $PROFILE_IDS \
  production:blue active:green verified:green
```

**Use Cases:**
- Standardize tags across profiles
- Update status tags after deployment
- Replace old tags with new taxonomy
- Clean up inconsistent tagging

### Batch Clear Tags

Remove all tags from multiple profiles:

```bash
nstbrowser-ai-agent profile tags batch-clear <id-1> <id-2> <id-3>
```

**Example - Clear Tags from Archived Profiles:**
```bash
# Get archived profile IDs
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles[] | select(.tags[] | .name == "archived") | .profileId' | \
  tr '\n' ' ')

# Clear tags
nstbrowser-ai-agent profile tags batch-clear $PROFILE_IDS
```

**Use Cases:**
- Clean up before re-tagging
- Remove tags from archived profiles
- Reset profiles for new purpose
- Simplify profile organization

## Batch Group Operations

### Batch Change Group

Move multiple profiles to a different group:

```bash
nstbrowser-ai-agent profile groups batch-change <group-id> <id-1> <id-2> <id-3>
```

**Example - Move Profiles to Production:**
```bash
# Get group ID
GROUP_ID=$(nstbrowser-ai-agent profile groups list --json | \
  jq -r '.data.groups[] | select(.name == "Production") | .groupId')

# Get profile IDs to move
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles[] | select(.tags[] | .name == "ready") | .profileId' | \
  tr '\n' ' ')

# Move profiles
nstbrowser-ai-agent profile groups batch-change $GROUP_ID $PROFILE_IDS
```

**Use Cases:**
- Promote profiles from staging to production
- Organize profiles by project
- Move profiles to archive group
- Reorganize after team changes

## Batch Local Data Operations

### Batch Clear Cache

Clear browser cache for multiple profiles:

```bash
nstbrowser-ai-agent profile cache clear <id-1> <id-2> <id-3>
```

**Example - Clear Cache for All Profiles:**
```bash
# Get all profile IDs
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles | map(.profileId) | join(" ")')

# Clear cache
nstbrowser-ai-agent profile cache clear $PROFILE_IDS
```

**Use Cases:**
- Routine maintenance
- Free up disk space
- Troubleshoot loading issues
- Prepare for fresh testing

### Batch Clear Cookies

Clear cookies for multiple profiles:

```bash
nstbrowser-ai-agent profile cookies clear <id-1> <id-2> <id-3>
```

**Example - Clear Cookies for Test Profiles:**
```bash
# Get test profile IDs
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles[] | select(.group.name == "Testing") | .profileId' | \
  tr '\n' ' ')

# Clear cookies
nstbrowser-ai-agent profile cookies clear $PROFILE_IDS
```

**Use Cases:**
- Reset login sessions
- Clear test data
- Troubleshoot authentication issues
- Prepare profiles for new tests

## Best Practices

### Profile Selection Strategies

**By Group:**
```bash
# Select all profiles in a group
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles[] | select(.group.name == "Production") | .profileId' | \
  tr '\n' ' ')
```

**By Tag:**
```bash
# Select profiles with specific tag
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles[] | select(.tags[] | .name == "automated") | .profileId' | \
  tr '\n' ' ')
```

**By Multiple Criteria:**
```bash
# Select profiles in group with specific tag
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles[] | select(.group.name == "Production" and (.tags[] | .name == "active")) | .profileId' | \
  tr '\n' ' ')
```

**By Range:**
```bash
# Select first 10 profiles
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | \
  jq -r '.data.profiles[0:10] | map(.profileId) | join(" ")')
```

### Error Handling in Batch Operations

**Check Before Batch:**
```bash
# Verify profiles exist
PROFILE_IDS="id-1 id-2 id-3"
for ID in $PROFILE_IDS; do
  nstbrowser-ai-agent profile show "$ID" > /dev/null 2>&1 || echo "Profile $ID not found"
done
```

**Verify After Batch:**
```bash
# Verify proxy was updated
for ID in $PROFILE_IDS; do
  nstbrowser-ai-agent profile proxy show "$ID" --json | jq '.data.proxy.host'
done
```

**Handle Failures:**
```bash
# Try batch operation
if nstbrowser-ai-agent profile proxy batch-update $PROFILE_IDS --host proxy.com --port 8080 --type http; then
  echo "Batch update successful"
else
  echo "Batch update failed, trying individual updates"
  for ID in $PROFILE_IDS; do
    nstbrowser-ai-agent profile proxy update "$ID" --host proxy.com --port 8080 --type http || echo "Failed: $ID"
  done
fi
```

### Performance Optimization

**Optimal Batch Size:**
```bash
# Split large lists into batches of 50
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | jq -r '.data.profiles | map(.profileId) | join(" ")')

# Process in batches
echo "$PROFILE_IDS" | xargs -n 50 | while read BATCH; do
  nstbrowser-ai-agent profile proxy batch-update $BATCH \
    --host proxy.com --port 8080 --type http
  sleep 1  # Rate limiting
done
```

**Parallel Batches:**
```bash
# Process multiple batches in parallel (use with caution)
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | jq -r '.data.profiles | map(.profileId) | join(" ")')

echo "$PROFILE_IDS" | xargs -n 50 -P 3 | while read BATCH; do
  nstbrowser-ai-agent profile proxy batch-update $BATCH \
    --host proxy.com --port 8080 --type http
done
```

### Logging and Verification

**Log Batch Operations:**
```bash
# Log to file
LOG_FILE="batch-operations-$(date +%Y%m%d-%H%M%S).log"

echo "Starting batch proxy update at $(date)" >> "$LOG_FILE"
nstbrowser-ai-agent profile proxy batch-update $PROFILE_IDS \
  --host proxy.com --port 8080 --type http 2>&1 | tee -a "$LOG_FILE"
echo "Completed at $(date)" >> "$LOG_FILE"
```

**Verify Results:**
```bash
# Count successful updates
SUCCESS_COUNT=0
FAIL_COUNT=0

for ID in $PROFILE_IDS; do
  if nstbrowser-ai-agent profile proxy show "$ID" --json | grep -q "proxy.com"; then
    ((SUCCESS_COUNT++))
  else
    ((FAIL_COUNT++))
    echo "Failed: $ID"
  fi
done

echo "Success: $SUCCESS_COUNT, Failed: $FAIL_COUNT"
```

## See Also

- [NST API Reference](nst-api-reference.md)
- [Profile Management Guide](profile-management.md)
- [Proxy Configuration Guide](proxy-configuration.md)
- [Troubleshooting Guide](troubleshooting.md)
