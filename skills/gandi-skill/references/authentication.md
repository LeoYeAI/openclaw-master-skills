# Authentication

Every request to Gandi's API requires authentication using an Authorization header.

## Personal Access Token (Recommended)

Personal Access Tokens (PAT) are the recommended authentication method. They provide:
- **Scoped permissions** - Fine-grained access control
- **Resource restrictions** - Limited to specific resources
- **Auditability** - Organization owners can track token usage
- **Rotation support** - Can be renewed via API

### Creating a Personal Access Token

1. Go to [Gandi Admin application](https://admin.gandi.net/organizations/account/pat)
2. Select an organization
3. Click "Create a token"
4. Choose fine-grained scopes for the token
5. Copy and securely store the token

**For Sandbox testing:** Create tokens at [Gandi Sandbox Admin](https://admin.sandbox.gandi.net/organizations/account/pat)

### Using a Personal Access Token

Include the Bearer scheme in the Authorization header:

```bash
Authorization: Bearer YOUR_PAT_TOKEN
```

**Example:**
```bash
curl -H "Authorization: Bearer pat_abc-123" \\
     -H "Accept-Version: v5" \\
     https://api.gandi.net/v5/domain/domains
```

### Token Renewal

PATs expire for security reasons. To renew:

**Endpoint:** `POST /v5/organization/personal-access-tokens/{pat_id}`

See [Organization API documentation](https://api.gandi.net/docs/organization/) for details.

## API Key (Deprecated)

⚠️ **API Keys are deprecated and should not be used for new integrations.**

**Limitations compared to PATs:**
- Cannot be scoped
- Same permissions as the owner
- Users can only have one API key
- No organization-level auditing
- Cannot create new keys, only regenerate existing ones

### Using an API Key (Legacy)

If you still have an API key:

```bash
Authorization: Apikey YOUR_API_KEY
```

**Example:**
```bash
curl -H "Authorization: Apikey 0123456" \\
     -H "Accept-Version: v5" \\
     https://api.gandi.net/v5/domain/domains
```

### Managing API Keys (Legacy)

- **Production:** [API Key Page](https://account.gandi.net/) (Authentication section)
- **Sandbox:** [Sandbox API Key Page](https://account.sandbox.gandi.net/)

You cannot create a new API key if you don't have one - you can only regenerate an existing one.

## Authentication Setup for Moltbot Skill

The skill will support Personal Access Tokens stored securely in the user's config directory.

**Recommended storage location:**
```bash
~/.config/gandi/api_token
```

**Example setup script:**
```bash
#!/bin/bash
mkdir -p ~/.config/gandi
echo "YOUR_PERSONAL_ACCESS_TOKEN" > ~/.config/gandi/api_token
chmod 600 ~/.config/gandi/api_token
```

## Security Best Practices

1. **Never commit tokens to version control** - Use `.gitignore` to exclude credential files
2. **Use environment variables** - For CI/CD and automated scripts
3. **Rotate tokens regularly** - Implement a token rotation strategy
4. **Use scoped tokens** - Give each token only the permissions it needs
5. **Monitor token usage** - Check organization audit logs for unexpected activity
6. **Revoke unused tokens** - Remove tokens that are no longer needed
7. **Use sandbox for testing** - Never test with production tokens

## Token Scopes

When creating a PAT, you can scope it to specific operations:

**Common scopes:**
- Domain management (read, write)
- DNS management (read, write)
- Certificate management (read, write)
- Email management (read, write)
- Billing (read)
- Organization management (read, write)

Always use the minimum required scopes for your use case.

## Troubleshooting

### 401 Unauthorized
- Check that your token is correctly formatted
- Verify the token hasn't expired
- Ensure you're using the correct authentication scheme (Bearer vs Apikey)

### 403 Forbidden
- Token may have expired
- Token doesn't have sufficient permissions for the requested operation
- Token is scoped to different resources
- Organization membership or permissions changed

### Token Renewal
When approaching expiration, renew your token:

```bash
curl -X POST "https://api.gandi.net/v5/organization/personal-access-tokens/{pat_id}" \\
     -H "Authorization: Bearer YOUR_CURRENT_PAT" \\
     -H "Content-Type: application/json"
```

## Further Reading

- [API Overview](./api-overview.md)
- [Domain Management](./domains.md)
- [Official Authentication Docs](https://api.gandi.net/docs/authentication/)
