# Troubleshooting

## Connection Issues

### Cannot connect to Home Assistant

**Symptoms:**
```
curl: (7) Failed to connect to homeassistant.local port 8123
```

**Solutions:**

1. **Verify HA is running:**
   ```bash
   curl -s "$HA_URL/api/" -H "Authorization: Bearer $HA_TOKEN"
   # Should return: {"message": "API running."}
   ```

2. **Check URL format:**
   ```bash
   echo $HA_URL
   # Must include protocol: http://192.168.1.100:8123
   # NOT just: 192.168.1.100:8123
   ```

3. **Use IP instead of hostname** (especially in Docker):
   ```bash
   # Instead of: http://homeassistant.local:8123
   # Use:        http://192.168.1.100:8123
   ```

4. **Check firewall:**
   ```bash
   # Port 8123 must be accessible
   nc -zv 192.168.1.100 8123
   ```

### SSL Certificate Errors

**Symptoms:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions:**

1. **Skip verification (self-signed certs):**
   ```bash
   curl -sk "$HA_URL/api/" -H "Authorization: Bearer $HA_TOKEN"
   ```

2. **Provide certificate:**
   ```bash
   curl --cacert /path/to/cert.pem "$HA_URL/api/" -H "Authorization: Bearer $HA_TOKEN"
   ```

### Docker / Container Networking

If running inside Docker and can't reach Home Assistant:

- **Use IP address** (recommended): `http://192.168.1.100:8123`
- **Tailscale**: `http://homeassistant.ts.net:8123`
- **mDNS doesn't work in Docker**: `homeassistant.local` won't resolve
- **Host network mode**: Add `--network host` to Docker run command
- **Nabu Casa**: `https://xxxxx.ui.nabu.casa` (cloud access)

## Authentication Issues

### 401 Unauthorized

**Symptoms:**
```json
{"message": "Invalid access token or no access token supplied"}
```

**Solutions:**

1. **Check token is set:**
   ```bash
   echo ${HA_TOKEN:0:20}...
   # Should show first 20 chars of your token
   ```

2. **Verify it's a Long-Lived Access Token** (not a session token):
   - Go to HA → Profile → Long-Lived Access Tokens
   - Create a new one if needed

3. **Check for extra whitespace or newlines:**
   ```bash
   echo -n "$HA_TOKEN" | wc -c
   # Should be consistent length, no extra chars
   ```

4. **Token may have been revoked:**
   - Check HA → Profile → Long-Lived Access Tokens
   - Regenerate if not listed

5. **Test with explicit token:**
   ```bash
   curl -s "$HA_URL/api/" -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

## Entity Issues

### Entity Not Found (404)

**Symptoms:**
```json
{"message": "Entity not found"}
```

**Solutions:**

1. **List all entities to find correct ID:**
   ```bash
   scripts/ha.sh list all | grep -i kitchen
   ```

2. **Entity naming rules:**
   - Always lowercase: `light.living_room` not `Light.Living_Room`
   - Underscores, not hyphens: `light.living_room` not `light.living-room`
   - Format: `domain.object_id`

3. **Entity may have been renamed or removed:**
   ```bash
   # Regenerate inventory to see current entities
   node scripts/inventory.js
   ```

### Service Not Found

**Symptoms:**
```json
{"message": "Service not found"}
```

**Solutions:**

1. **Check service format** — domain first, then service:
   - Correct: `light/turn_on`
   - Wrong: `turn_on/light`

2. **List available services:**
   ```bash
   curl -s "$HA_URL/api/services" -H "Authorization: Bearer $HA_TOKEN" \
     | jq -r '.[] | "\(.domain): \(.services | keys | join(", "))"'
   ```

3. **Verify service data format:**
   ```bash
   # entity_id must be a string or array of strings
   # Additional params depend on the service
   ```

## Timeout Issues

**Symptoms:**
```
curl: (28) Operation timed out
```

**Solutions:**

1. **Increase curl timeout:**
   ```bash
   curl -s --connect-timeout 10 --max-time 30 "$HA_URL/api/states" \
     -H "Authorization: Bearer $HA_TOKEN"
   ```

2. **Check network latency:**
   ```bash
   ping -c 3 192.168.1.100
   ```

3. **HA may be overloaded** — check HA system logs

## Common Gotchas

- **Case sensitivity**: Entity IDs are case-sensitive
- **Underscores vs hyphens**: Entity IDs use underscores, not hyphens
- **Domain prefix required**: Always use `domain.entity` format
- **brightness vs brightness_pct**: Raw value (0-255) vs percentage (0-100)
- **color_temp in mireds**: Lower = cooler (153), higher = warmer (500)
- **volume_level**: Float 0.0 to 1.0, not percentage
- **Batch entity_id**: Use JSON array `["light.a", "light.b"]`, not comma-separated string
- **Template API**: Returns plain text, not JSON (unless template outputs JSON)
- **History API**: Returns array of arrays — first index is always 0 for single entity
