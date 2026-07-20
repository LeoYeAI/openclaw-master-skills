---
name: unipile-linkedin-sdk
description: LinkedIn integration via Unipile's official Node.js SDK. Send messages, InMail, view profiles, manage connections, create posts, and interact with content. Use for LinkedIn automation, messaging, profile retrieval, connection requests, or post interactions. Trigger phrases: "linkedin api", "scrape linkedin", "linkedin profile", "linkedin posts", "send linkedin message".
version: 1.5.0
metadata:
  openclaw:
    requires:
      env:
        - UNIPILE_DSN
        - UNIPILE_ACCESS_TOKEN
      optionalEnv:
        - UNIPILE_PERMISSIONS
    primaryEnv: UNIPILE_ACCESS_TOKEN
    emoji: "🔗"
    homepage: https://clawhub.ai/skills/unipile-linkedin-sdk
    source: https://clawhub.ai/skills/unipile-linkedin-sdk
---

# Unipile LinkedIn SDK

LinkedIn API via official Unipile Node.js SDK for messaging, profiles, posts, and invitations.

## ⚠️ Security: Use Least Privilege

**Recommended:** Set `UNIPILE_PERMISSIONS=read` for read-only access.

```bash
# RECOMMENDED: Read-only mode (safe, no write operations)
UNIPILE_PERMISSIONS=read node scripts/linkedin.mjs posts <account> andrewyng

# ONLY if you need to send messages or create posts
UNIPILE_PERMISSIONS=read,write node scripts/linkedin.mjs create-post <account> "text"
```

Your access token can perform actions on your behalf. Limit its scope with `UNIPILE_PERMISSIONS`.

## Setup

### Installation

```bash
npm install unipile-node-sdk
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `UNIPILE_DSN` | ✅ Yes | API endpoint (e.g., `https://api34.unipile.com:16473`) |
| `UNIPILE_ACCESS_TOKEN` | ✅ Yes | Access token from [dashboard.unipile.com](https://dashboard.unipile.com) |
| `UNIPILE_PERMISSIONS` | Optional | `read`, `write`, or `read,write`. **Recommended: `read`** |

### Permission Modes

| Mode | UNIPILE_PERMISSIONS | Allowed Operations | Use Case |
|------|---------------------|-------------------|----------|
| **Read-only** ⭐ | `read` | List profiles, posts, chats, messages, connections | Data scraping, dashboards, analysis |
| Write-only | `write` | Send messages, create posts, react, comment | Automation bots |
| Full access | `read,write` | All operations | Complete LinkedIn automation |

**Default:** `read,write` (full access) — **Change to `read` for safety.**

### Least-Privilege Best Practice

```bash
# 1. Start with read-only (safest)
export UNIPILE_PERMISSIONS=read

# 2. Only enable write when specifically needed
export UNIPILE_PERMISSIONS=read,write  # Temporarily for a specific task

# 3. Revert to read-only after
export UNIPILE_PERMISSIONS=read
```

### Client Initialization

```javascript
import { UnipileClient } from 'unipile-node-sdk';

const client = new UnipileClient(
  process.env.UNIPILE_DSN,
  process.env.UNIPILE_ACCESS_TOKEN
);

// Check permissions before operations
const canWrite = (process.env.UNIPILE_PERMISSIONS || 'read,write').includes('write');
const canRead = (process.env.UNIPILE_PERMISSIONS || 'read,write').includes('read');
```

### Credential Storage

**Recommended approaches (in order of security):**

1. **Environment variables** — Set in shell profile or .env (add .env to .gitignore)
2. **Secrets manager** — AWS Secrets Manager, HashiCorp Vault, etc.
3. **CI/CD secrets** — GitHub Actions secrets, GitLab CI variables

**Avoid:** Storing tokens in plaintext files, especially in shared or version-controlled directories.

### Get Credentials

1. Sign up at [dashboard.unipile.com](https://dashboard.unipile.com)
2. Create an app to get your DSN and access token
3. Connect a LinkedIn account via the dashboard or API

## Invocation Examples

### Setup & Account Discovery

```
"Connect to my LinkedIn account via Unipile"
"List my connected LinkedIn accounts"
"What's my LinkedIn profile info?"
```

**Pattern:** First get the account ID, then use it for all other operations.

```javascript
// Step 1: Get your LinkedIn account ID
const accounts = await client.account.getAll();
const linkedin = accounts.items.find(a => a.type === 'LINKEDIN');
const accountId = linkedin.id;  // Use this for all operations

// Step 2: Get your own profile
const me = await client.users.getOwnProfile(accountId);
```

### Profile Lookup

```
"Look up Andrew Ng's LinkedIn profile"
"Get Satya Nadella's LinkedIn experience section"
"Find the company profile for OpenAI on LinkedIn"
```

```javascript
// User profile by public identifier (URL slug)
const profile = await client.users.getProfile({
  account_id: accountId,
  identifier: 'andrewyng'  // from linkedin.com/in/andrewyng
});

// With specific sections
const profile = await client.users.getProfile({
  account_id: accountId,
  identifier: 'satyanadella',
  linkedin_sections: ['experience', 'education', 'skills'],
  notify: true  // sends profile view notification
});

// Company profile
const company = await client.users.getCompanyProfile({
  account_id: accountId,
  identifier: 'openai'  // company URL slug
});
```

### Posts & Content

```
"List posts from Andrew Ng on LinkedIn from last week"
"Get the latest 5 posts from Sundar Pichai"
"Show me Microsoft's recent LinkedIn posts"
"What did Andrew Ng post about AI recently?"
```

```javascript
// Get posts from a user
const posts = await client.users.getAllPosts({
  account_id: accountId,
  identifier: 'andrewyng',  // or use provider_id from profile lookup
  limit: 10
});

// Filter by date range (client-side)
const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
const recentPosts = posts.items.filter(p => 
  new Date(p.parsed_datetime) >= oneWeekAgo
);

// Get specific post details
const post = await client.users.getPost({
  account_id: accountId,
  post_id: posts.items[0].id
});
// Returns: reactions, comments count, share_url, text, etc.

// Create a post on your own profile
await client.users.createPost({
  account_id: accountId,
  text: 'Excited to share my latest project! 🚀'
});
```

### Messaging

```
"List my LinkedIn chats"
"Show unread messages on LinkedIn"
"Send a message to my last LinkedIn conversation"
```

```javascript
// List all chats
const chats = await client.messaging.getAllChats({
  account_type: 'LINKEDIN',
  account_id: accountId,
  limit: 20
});

// Filter unread
const unreadChats = chats.items.filter(c => c.unread_count > 0);

// Get messages from a chat
const messages = await client.messaging.getAllMessagesFromChat({
  chat_id: chats.items[0].id,
  limit: 50
});

// Send message to existing chat
await client.messaging.sendMessage({
  chat_id: 'chat_id',
  text: 'Thanks for connecting!'
});

// Start new chat with someone
await client.messaging.startNewChat({
  account_id: accountId,
  attendees_ids: ['provider_id_from_profile'],
  text: 'Hi, I wanted to reach out about...'
});
```

### InMail (Non-Connections)

```
"Send an InMail to someone outside my network"
"Message a LinkedIn user I'm not connected to"
```

```javascript
await client.messaging.startNewChat({
  account_id: accountId,
  attendees_ids: ['target_provider_id'],
  text: 'Hi, I came across your profile...',
  options: {
    linkedin: {
      api: 'classic',  // or 'recruiter', 'sales_navigator'
      inmail: true
    }
  }
});
```

Note: InMail requires LinkedIn Premium.

### Connections & Invitations

```
"List my LinkedIn connections"
"Show my pending connection requests"
"Send a connection request to [profile]"
"Cancel my pending invitation to [name]"
```

```javascript
// List your connections
const connections = await client.users.getAllRelations({
  account_id: accountId,
  limit: 100
});

// Send connection request
await client.users.sendInvitation({
  account_id: accountId,
  provider_id: 'ACoAAA...',  // from profile lookup
  message: 'Hi, I enjoyed your recent post about AI!'
});

// List pending invitations you've sent
const invitations = await client.users.getAllInvitationsSent({
  account_id: accountId
});

// Cancel an invitation
await client.users.cancelInvitationSent({
  account_id: accountId,
  invitation_id: invitations.items[0].id
});
```

### Reactions & Comments

```
"Like Andrew Ng's latest post"
"Add a comment on [post]"
"React with celebrate on [post]"
```

```javascript
// React to a post
await client.users.sendPostReaction({
  account_id: accountId,
  post_id: '7440079959160913920',
  reaction_type: 'like'  // 'celebrate', 'support', 'love', 'insightful', 'funny'
});

// Comment on a post
await client.users.sendPostComment({
  account_id: accountId,
  post_id: '7440079959160913920',
  text: 'Great insights! Thanks for sharing.'
});
```

### Account Connection

```
"Generate a link to connect my LinkedIn account"
"Create a hosted auth link for LinkedIn"
```

```javascript
// Hosted auth (for multi-user apps)
const link = await client.account.createHostedAuthLink({
  type: 'create',
  expiresOn: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
  providers: ['LINKEDIN'],
  success_redirect_url: 'https://yourapp.com/success',
  failure_redirect_url: 'https://yourapp.com/fail',
  notify_url: 'https://yourapp.com/webhook'
});
// Share link.url with user to connect their account

// Handle 2FA checkpoint
await client.account.solveCodeCheckpoint({
  account_id: accountId,
  provider: 'LINKEDIN',
  code: '123456'
});
```

## Quick Reference

### Read Operations (require `read` permission)

| Task | Method |
|------|--------|
| List accounts | `client.account.getAll()` |
| Get profile | `client.users.getProfile({ account_id, identifier })` |
| Get own profile | `client.users.getOwnProfile(account_id)` |
| Get company | `client.users.getCompanyProfile({ account_id, identifier })` |
| Get connections | `client.users.getAllRelations({ account_id })` |
| List posts | `client.users.getAllPosts({ account_id, identifier })` |
| Get post | `client.users.getPost({ account_id, post_id })` |
| List chats | `client.messaging.getAllChats({ account_type: 'LINKEDIN', account_id })` |
| Get messages | `client.messaging.getAllMessagesFromChat({ chat_id })` |
| List invitations | `client.users.getAllInvitationsSent({ account_id })` |

### Write Operations (require `write` permission)

| Task | Method |
|------|--------|
| Create post | `client.users.createPost({ account_id, text })` |
| React to post | `client.users.sendPostReaction({ account_id, post_id, reaction_type })` |
| Comment on post | `client.users.sendPostComment({ account_id, post_id, text })` |
| Send message | `client.messaging.sendMessage({ chat_id, text })` |
| Start chat | `client.messaging.startNewChat({ account_id, attendees_ids, text })` |
| Send invitation | `client.users.sendInvitation({ account_id, provider_id, message? })` |
| Cancel invitation | `client.users.cancelInvitationSent({ account_id, invitation_id })` |

### Implementing Permission Checks

```javascript
const PERMISSIONS = (process.env.UNIPILE_PERMISSIONS || 'read,write').split(',');

function requireWrite() {
  if (!PERMISSIONS.includes('write')) {
    throw new Error('Operation requires write permission. Set UNIPILE_PERMISSIONS=write');
  }
}

function requireRead() {
  if (!PERMISSIONS.includes('read')) {
    throw new Error('Operation requires read permission. Set UNIPILE_PERMISSIONS=read');
  }
}

// Usage
async function safeCreatePost(accountId, text) {
  requireWrite();
  return client.users.createPost({ account_id: accountId, text });
}
```

## Response Patterns

### List Endpoints

Return `{ object: '...List', items: [...], cursor: string | null }`

- Filter with `limit`, `after` (ISO date), `cursor` for pagination
- Date filtering done client-side on `parsed_datetime` field

### Account Object

```javascript
{
  id: 'MvbNEuYTTZ-o-QCHITLGnw',  // Use as account_id
  type: 'LINKEDIN',
  name: 'John Doe',
  sources: [{ id: '...', status: 'OK' }]
}
```

### Profile Object

```javascript
{
  provider_id: 'ACoAAA...',       // Use for invitations
  public_identifier: 'john-doe',  // URL slug
  first_name: 'John',
  last_name: 'Doe',
  headline: 'CEO at Company',
  location: 'San Francisco, CA',
  profile_picture_url: 'https://...'
}
```

### Post Object

```javascript
{
  id: '7440079959160913920',
  text: 'Post content...',
  parsed_datetime: '2026-03-18T17:01:32.265Z',
  reaction_counter: 2064,
  comment_counter: 130,
  share_url: 'https://www.linkedin.com/posts/...',
  author: { name: '...', public_identifier: '...' }
}
```

## Error Handling

```javascript
import { UnsuccessfulRequestError } from 'unipile-node-sdk';

try {
  await client.users.getProfile({ account_id, identifier });
} catch (err) {
  if (err instanceof UnsuccessfulRequestError) {
    const { status, type, detail } = err.body;
    
    switch (type) {
      case 'errors/invalid_credentials':
        // Reconnect account
        break;
      case 'errors/checkpoint_error':
        // Prompt for 2FA code
        break;
      case 'errors/disconnected_account':
        // Account needs reconnection
        break;
      case 'errors/resource_not_found':
        // Invalid ID or profile doesn't exist
        break;
      case 'errors/invalid_recipient':
        // Profile identifier not found
        break;
    }
  }
}
```

### Common Error Types

| Type | Status | Meaning | Action |
|------|--------|---------|--------|
| `errors/invalid_credentials` | 401 | Wrong username/password | Reconnect account |
| `errors/expired_credentials` | 401 | Session expired | Reconnect account |
| `errors/checkpoint_error` | 403 | 2FA/OTP required | Call `solveCodeCheckpoint` |
| `errors/invalid_checkpoint_solution` | 400 | Wrong 2FA code | Retry with correct code |
| `errors/disconnected_account` | 403 | Account disconnected | Reconnect |
| `errors/insufficient_privileges` | 403 | Account lacks permission | Check LinkedIn tier |
| `errors/resource_not_found` | 404 | Invalid ID | Verify the ID exists |
| `errors/invalid_recipient` | 422 | Profile not found | Check identifier spelling |
| `errors/invalid_parameters` | 400 | Bad request params | Check parameter format |
| `errors/malformed_request` | 400 | Invalid request body | Check API requirements |

## Limitations

- **Post Comments API**: `getAllPostComments` may return errors for some posts due to API limitations
- **InMail**: Requires LinkedIn Premium subscription
- **Rate Limits**: LinkedIn has strict rate limits; implement backoff for bulk operations
- **Date Filtering**: Must be done client-side on `parsed_datetime` field

## Resources

- [SDK Repository](https://github.com/unipile/unipile-node-sdk)
- [Unipile API Docs](https://developer.unipile.com/docs/list-provider-features)
- [Unipile Dashboard](https://dashboard.unipile.com)

## Security & Trust

### What This Skill Does

This skill provides a wrapper around the official [unipile-node-sdk](https://github.com/unipile/unipile-node-sdk) npm package. It only makes API calls to your configured Unipile DSN endpoint.

**Network calls:** Only to `UNIPILE_DSN` (your Unipile API endpoint)

**Data handling:** Credentials are read from environment variables only — never stored or transmitted elsewhere

### Required Credentials

| Variable | Purpose | How to Get |
|----------|---------|------------|
| `UNIPILE_DSN` | Your Unipile API endpoint | From [dashboard.unipile.com](https://dashboard.unipile.com) |
| `UNIPILE_ACCESS_TOKEN` | API authentication token | From [dashboard.unipile.com](https://dashboard.unipile.com) |

**Best practices:**
- Store in environment variables or a secrets manager
- Never commit tokens to git or version control
- Avoid storing in workspace files that may be shared or synced

### Verify the SDK

The underlying SDK is open source and can be audited:
- **npm:** `npm info unipile-node-sdk`
- **GitHub:** https://github.com/unipile/unipile-node-sdk
- **Install from source:** `npm install git+https://github.com/unipile/unipile-node-sdk.git`

### Scope Considerations

This skill can:
- Read your LinkedIn profile and connections
- Send messages and create posts on your behalf
- View other users' profiles and posts

**Recommendations:**
- Use a dedicated LinkedIn account for automation
- Review Unipile's OAuth scopes before connecting
- Monitor activity via Unipile dashboard
- **Use `UNIPILE_PERMISSIONS=read` for least privilege**

### Provenance

- **Publisher:** @Mohit21GoJs on ClawHub
- **Skill Source:** https://clawhub.ai/skills/unipile-linkedin-sdk
- **SDK Source:** https://github.com/unipile/unipile-node-sdk
- **SDK License:** MIT (official Unipile package)
