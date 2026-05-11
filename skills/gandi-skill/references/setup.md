# Setup Guide

How to set up and configure the Gandi skill for Moltbot.

## Prerequisites

1. **Gandi Account** - Active account at [gandi.net](https://www.gandi.net)
2. **Personal Access Token** - Created from Gandi Admin
3. **Moltbot** - Version 2026.1 or higher

## Step 1: Create Personal Access Token

1. Log in to [Gandi Admin](https://admin.gandi.net)
2. Navigate to **Organizations** → **Account** → **Personal Access Tokens**
3. Click **"Create a token"**
4. Configure token settings:
   - **Name:** Moltbot Gandi Skill
   - **Organization:** Select your organization
   - **Scopes:** Select required permissions:
     - ✅ Domain management (read, write)
     - ✅ DNS management (read, write)
     - ✅ Certificate management (read) - optional
     - ✅ Email management (read, write) - optional
5. Click **Create**
6. **Copy the token immediately** - you won't be able to see it again!

### Recommended Scopes

**Minimum (read-only):**
- Domain: read
- LiveDNS: read

**Standard (full management):**
- Domain: read, write
- LiveDNS: read, write
- Certificate: read
- Email: read, write

**Production (restricted):**
- Create separate tokens for different operations
- Use minimal required scopes
- Rotate tokens regularly

## Step 2: Store API Credentials

Store your Personal Access Token securely in your config directory:

```bash
# Create config directory
mkdir -p ~/.config/gandi

# Store token (replace YOUR_TOKEN with actual token)
echo "YOUR_PERSONAL_ACCESS_TOKEN" > ~/.config/gandi/api_token

# Set secure permissions (owner read-only)
chmod 600 ~/.config/gandi/api_token

# Optionally store API URL (defaults to production)
echo "https://api.gandi.net" > ~/.config/gandi/api_url
```

### File Locations

The skill expects credentials at:

| File | Purpose |
|------|---------|
| `~/.config/gandi/api_token` | Personal Access Token |
| `~/.config/gandi/api_url` | API endpoint (optional) |

### Using Sandbox Environment

For testing without affecting production:

```bash
# Create sandbox token at: https://admin.sandbox.gandi.net
echo "YOUR_SANDBOX_TOKEN" > ~/.config/gandi/api_token
echo "https://api.sandbox.gandi.net" > ~/.config/gandi/api_url
```

## Step 3: Install the Skill

### Via Moltbot (when published)

```bash
moltbot skills install gandi-skill
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/chrisagiddings/moltbot-gandi-skill.git

# Copy to Moltbot skills directory
cp -r moltbot-gandi-skill/gandi-skill ~/.local/share/moltbot/skills/

# Restart Moltbot
moltbot restart
```

## Step 4: Verify Setup

Test that authentication works:

```bash
# Test credential loading (manual verification)
cat ~/.config/gandi/api_token
```

Expected output: Your Personal Access Token (should be a long alphanumeric string starting with `pat_`)

## Troubleshooting

### Token Not Found

**Error:** `Cannot find API token`

**Solution:**
```bash
# Verify file exists
ls -la ~/.config/gandi/api_token

# Check permissions
# Should show: -rw------- (600)
ls -l ~/.config/gandi/api_token

# Recreate if needed
echo "YOUR_TOKEN" > ~/.config/gandi/api_token
chmod 600 ~/.config/gandi/api_token
```

### Authentication Failed (401)

**Error:** `401 Unauthorized`

**Causes:**
- Token is incorrect or expired
- Token was deleted from Gandi Admin
- Wrong authentication format

**Solution:**
1. Verify token in Gandi Admin
2. Create new token if expired
3. Update stored token file
4. Restart Moltbot

### Permission Denied (403)

**Error:** `403 Forbidden`

**Causes:**
- Token doesn't have required scopes
- Token is scoped to different organization
- Token has expired

**Solution:**
1. Check token scopes in Gandi Admin
2. Create new token with required permissions
3. Update stored token
4. Verify organization membership

### API Rate Limit (429)

**Error:** `429 Too Many Requests`

**Cause:** Exceeded 1000 requests per minute limit

**Solution:**
- Wait 60 seconds
- Implement request throttling
- Reduce API call frequency
- Consider caching results

## Security Best Practices

### Token Storage

✅ **DO:**
- Store in `~/.config/gandi/` with 600 permissions
- Use different tokens for different environments
- Rotate tokens regularly (monthly/quarterly)
- Revoke unused tokens
- Keep tokens out of version control

❌ **DON'T:**
- Commit tokens to git repositories
- Share tokens between users/systems
- Use API keys (deprecated)
- Store tokens in plain text in scripts
- Give tokens unnecessary scopes

### .gitignore

Ensure your `.gitignore` includes:

```gitignore
# Gandi credentials
**/.config/gandi/
**/api_token
**/api_key
*.key
*.pem
```

### Environment Variables

For CI/CD or scripts, use environment variables:

```bash
export GANDI_API_TOKEN="your_token_here"
```

Then modify the skill to read from `$GANDI_API_TOKEN` if file doesn't exist.

## Multiple Organizations

If you manage multiple Gandi organizations:

### Option 1: Organization Selection

Use `sharing_id` parameter in API calls to specify which organization to use:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \\
     "https://api.gandi.net/v5/domain/domains?sharing_id=org-uuid"
```

### Option 2: Multiple Tokens

Create separate tokens for each organization:

```bash
~/.config/gandi/
├── api_token_org1
├── api_token_org2
└── api_token_org3
```

Configure the skill to use the appropriate token file based on context.

### Option 3: Profile System

Create a profile configuration:

```json
{
  "profiles": {
    "personal": {
      "token_file": "~/.config/gandi/personal_token",
      "org_id": "uuid-1"
    },
    "work": {
      "token_file": "~/.config/gandi/work_token",
      "org_id": "uuid-2"
    }
  },
  "default_profile": "personal"
}
```

## Testing

### Test Domain List

```bash
# Should return list of your domains
curl -H "Authorization: Bearer $(cat ~/.config/gandi/api_token)" \\
     https://api.gandi.net/v5/domain/domains
```

### Test DNS Query

```bash
# Replace example.com with your domain
curl -H "Authorization: Bearer $(cat ~/.config/gandi/api_token)" \\
     https://api.gandi.net/v5/livedns/domains/example.com/records
```

### Test Organization Access

```bash
# Should return your organizations
curl -H "Authorization: Bearer $(cat ~/.config/gandi/api_token)" \\
     https://api.gandi.net/v5/organization/organizations
```

## Next Steps

Once setup is complete:

1. Read [Domain Management](./domains.md) guide
2. Read [LiveDNS Management](./livedns.md) guide
3. Explore [API Overview](./api-overview.md)
4. Try example commands with Moltbot

## Support

**Issues:** [GitHub Issues](https://github.com/chrisagiddings/moltbot-gandi-skill/issues)

**Gandi Support:**
- [Help Center](https://help.gandi.net/)
- [API Documentation](https://api.gandi.net/docs/)
- [Community Forum](https://community.gandi.net/)

**Moltbot:**
- [Documentation](https://github.com/openclaw/openclaw)
- [Discord Community](https://discord.gg/clawd)
