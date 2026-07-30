# OAuth Flow Patterns for MCP Servers

Some MCP servers require OAuth authentication instead of simple API tokens. This guide covers the common OAuth flows.

## Google OAuth (Drive, Gmail, Calendar)

Google services require OAuth 2.0 with a service account or user consent flow.

### Option A: Service Account (Recommended for server-to-server)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the required API (Drive API, Gmail API, Calendar API)
4. Go to **IAM & Admin → Service Accounts**
5. Create a service account and download the JSON key file
6. Set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```
7. Share relevant resources (Drive folders, calendars) with the service account email

### Option B: OAuth 2.0 User Consent

1. Go to [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Create **OAuth 2.0 Client ID** (type: Desktop App)
3. Download the `credentials.json` file
4. Run the server's auth flow (usually `python3 -m <module> --auth`) — this opens a browser for consent
5. The server stores refresh tokens locally (typically in `~/.config/<server>/token.json`)

## Slack OAuth

Slack MCP servers typically use Bot tokens, not user OAuth.

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Create a new app (or select existing)
3. Under **OAuth & Permissions**, add required scopes (channels:read, chat:write, etc.)
4. Install the app to your workspace
5. Copy the **Bot User OAuth Token** (starts with `xoxb-`)
6. Set: `export SLACK_BOT_TOKEN=xoxb-your-token-here`

## GitHub Apps (vs Personal Access Tokens)

Some servers support GitHub App authentication for organization-level access.

### Personal Access Token (Simple)

1. Go to [GitHub Settings → Developer → Personal Access Tokens](https://github.com/settings/tokens/new)
2. Select required scopes (typically `repo`, `read:org`)
3. Generate and copy the token
4. Set: `export GITHUB_TOKEN=ghp_your-token-here`

### GitHub App (Organization)

1. Go to **Organization Settings → Developer Settings → GitHub Apps**
2. Create a new GitHub App with required permissions
3. Install the app on the organization
4. Generate a private key and download the `.pem` file
5. Set environment variables:
   ```bash
   export GITHUB_APP_ID=12345
   export GITHUB_APP_PRIVATE_KEY_PATH=/path/to/private-key.pem
   export GITHUB_APP_INSTALLATION_ID=67890
   ```

## Generic OAuth 2.0

For servers using standard OAuth 2.0:

1. Register your application with the service provider
2. Note the **Client ID** and **Client Secret**
3. Set environment variables:
   ```bash
   export OAUTH_CLIENT_ID=your-client-id
   export OAUTH_CLIENT_SECRET=your-client-secret
   ```
4. Some servers handle the token exchange automatically on first run
5. Others may require running an initial auth command

## Security Notes

- **Never commit** OAuth credentials, private keys, or client secrets to version control
- **Service account keys** should have minimal permissions scoped to required APIs only
- **Refresh tokens** are stored locally by the server — they're long-lived but can be revoked
- **Client secrets** should be treated with the same care as API tokens
- Store all credentials using environment variables or a secrets manager
