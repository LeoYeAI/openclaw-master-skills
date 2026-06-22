---
name: jules-api
description: "Use the Jules REST API (v1alpha) via curl to list sources, create sessions, monitor activities, approve plans, send messages, and retrieve outputs (e.g., PR URLs). Use when the user wants to delegate coding tasks to Jules programmatically. Requires JULES_API_KEY env var (obtain from https://jules.google.com/settings#api)."
env:
  JULES_API_KEY:
    required: true
    description: "API key for the Jules service. Obtain from https://jules.google.com/settings#api"
dependencies:
  - name: curl
    required: true
    description: "Used for all API requests to jules.googleapis.com"
  - name: python3
    required: true
    description: "Used by jules_api.sh for safe JSON string escaping"
  - name: node
    required: false
    description: "Required only for scripts/jules.js CLI wrapper"
  - name: jules
    required: false
    description: "Jules CLI binary, required only for scripts/jules.js CLI wrapper"
---

# Jules REST API Skill

## Quick Start

```bash
# 0. Set your API key (required — get one at https://jules.google.com/settings#api)
export JULES_API_KEY="your-api-key-here"

# 1. Verify available sources (pre-flight check)
./scripts/jules_api.sh sources

# 2. Create a session with plan approval and auto PR creation
./scripts/jules_api.sh new-session \
  --source "sources/github/OWNER/REPO" \
  --title "Add unit tests" \
  --prompt "Add comprehensive unit tests for the authentication module" \
  --branch main \
  --require-plan-approval \
  --auto-pr

# 3. Monitor session progress and approve the plan
./scripts/jules_api.sh activities --session SESSION_ID
./scripts/jules_api.sh approve-plan --session SESSION_ID
```

**Note:** Use your GitHub username/org, not your local system username (e.g., `sources/github/octocat/Hello-World`, not `sources/github/$USER/Hello-World`).

## Overview

This skill enables programmatic interaction with the **Jules REST API (v1alpha)** for delegating coding tasks to Jules, Google's autonomous AI coding agent. It supports:

- **Task Assignment**: Create new coding sessions with specific prompts
- **Session Monitoring**: Track session state and activities in real-time
- **Plan Management**: Approve or review generated plans
- **Messaging**: Send follow-up messages to active sessions
- **Result Integration**: Retrieve PR URLs and code changes from completed sessions

## Before You Start

### 1. Get an API Key

Create a Jules API key in the Jules web app:
- Navigate to: https://jules.google.com/settings#api
- You can have at most **3 API keys** at a time

Export it on the machine running the agent:

```bash
export JULES_API_KEY="your-api-key-here"
```

### 2. Connect Your GitHub Repository

Before the API can operate on a GitHub repo, you must:
1. Install the **Jules GitHub app** via the Jules web UI
2. Grant access to the specific repositories you want Jules to work on

### 3. Verify Repository Access

```bash
# List available sources to verify access and see correct format
./scripts/jules_api.sh sources
```

You'll see entries like:
```json
{
  "sources": [
    {
      "name": "sources/github/octocat/Hello-World",
      "githubRepo": {
        "owner": "octocat",
        "repo": "Hello-World",
        "defaultBranch": { "displayName": "main" },
        "branches": [
          { "displayName": "main" },
          { "displayName": "develop" }
        ]
      }
    }
  ]
}
```

## Base URL & Authentication

| Property | Value |
|----------|-------|
| Base URL | `https://jules.googleapis.com/v1alpha` |
| Auth Header | `x-goog-api-key: $JULES_API_KEY` |

All requests authenticate with:
```bash
-H "x-goog-api-key: $JULES_API_KEY"
```

## Core Concepts

### Resources

| Resource | Description |
|----------|-------------|
| **Source** | A GitHub repository connected to Jules. Format: `sources/github/{owner}/{repo}` |
| **Session** | A unit of work where Jules executes a coding task. Contains state, activities, and outputs |
| **Activity** | An individual event within a session (plan generated, message sent, progress update, etc.) |

### Session States

| State | Description |
|-------|-------------|
| `QUEUED` | Session is waiting to start |
| `PLANNING` | Generating execution plan |
| `AWAITING_PLAN_APPROVAL` | Waiting for user to approve plan |
| `AWAITING_USER_FEEDBACK` | Needs user input to continue |
| `IN_PROGRESS` | Actively executing the task |
| `PAUSED` | Temporarily stopped |
| `COMPLETED` | Successfully finished |
| `FAILED` | Encountered an error |

### Activity Types

| Type | Description |
|------|-------------|
| Plan Generated | A plan was generated for the task |
| Plan Approved | The plan was approved (manually or auto) |
| User Message | User posted a message to the session |
| Agent Message | Jules posted a message |
| Progress Update | Status update on current work |
| Session Completed | Session finished successfully |
| Session Failed | Session encountered an error |

## Workflows

### Option 1: Session with Plan Approval and Auto-PR (Recommended)

Create a session that requires plan approval before execution and automatically creates a PR when complete:

```bash
./scripts/jules_api.sh new-session \
  --source "sources/github/octocat/Hello-World" \
  --title "Fix login bug" \
  --prompt "Fix the null pointer exception in the login handler when email is empty" \
  --branch main \
  --require-plan-approval \
  --auto-pr
```

**Why this is recommended:**
- You review and approve the plan before Jules executes changes
- PR is created automatically on completion
- Balances automation with human oversight

### Option 2: Fully Automated Session (No Plan Approval)

For low-risk or routine tasks in non-sensitive repos, you can skip plan approval:

```bash
# Create session without plan approval (use only for low-risk tasks)
./scripts/jules_api.sh new-session \
  --source "sources/github/octocat/Hello-World" \
  --title "Fix typo in README" \
  --prompt "Fix the typo in README.md line 5" \
  --branch main \
  --auto-pr
```

**Warning:** Without `--require-plan-approval`, Jules will automatically approve its own plan and execute changes. Only use this for low-risk tasks in non-critical repos.

### Option 3: Interactive Session

Send follow-up messages during an active session:

```bash
# Create session
./scripts/jules_api.sh new-session \
  --source "sources/github/octocat/Hello-World" \
  --title "Add API endpoints" \
  --prompt "Add REST API endpoints for user management" \
  --branch main

# Send additional instructions
./scripts/jules_api.sh send-message \
  --session SESSION_ID \
  --prompt "Also add input validation for all endpoints"
```

## API Reference

### Sources

#### List Sources
Lists all connected GitHub repositories.

```bash
curl -sS \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sources"
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pageSize` | integer | 30 | Number of sources to return (1-100) |
| `pageToken` | string | - | Token from previous response for pagination |
| `filter` | string | - | AIP-160 filter (e.g., `name=sources/source1`) |

**Response:**
```json
{
  "sources": [
    {
      "name": "sources/github/octocat/Hello-World",
      "githubRepo": {
        "owner": "octocat",
        "repo": "Hello-World",
        "isPrivate": false,
        "defaultBranch": { "displayName": "main" },
        "branches": [
          { "displayName": "main" },
          { "displayName": "develop" }
        ]
      }
    }
  ],
  "nextPageToken": "..."
}
```

#### Get Source
Retrieves a single source by name.

```bash
curl -sS \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sources/github/octocat/Hello-World"
```

Use this to see available branches before creating a session.

---

### Sessions

#### Create Session
Creates a new coding session.

```bash
curl -sS "https://jules.googleapis.com/v1alpha/sessions" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{
    "prompt": "Add unit tests for the login module",
    "title": "Add Login Tests",
    "sourceContext": {
      "source": "sources/github/octocat/Hello-World",
      "githubRepoContext": {
        "startingBranch": "main"
      }
    },
    "requirePlanApproval": true,
    "automationMode": "AUTO_CREATE_PR"
  }'
```

**Request Body Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | Yes | The task description for Jules |
| `title` | string | No | Short title for the session |
| `sourceContext.source` | string | Yes | Source name (e.g., `sources/github/owner/repo`) |
| `sourceContext.githubRepoContext.startingBranch` | string | Yes | Branch to start from |
| `requirePlanApproval` | boolean | No | If true, pause for plan approval. Recommended: true for production repos |
| `automationMode` | string | No | Set to `AUTO_CREATE_PR` for automatic PR creation |

**Response:**
```json
{
  "name": "sessions/31415926535897932384",
  "id": "31415926535897932384",
  "prompt": "Add unit tests for the login module",
  "title": "Add Login Tests",
  "state": "QUEUED",
  "url": "https://jules.google/session/31415926535897932384",
  "createTime": "2026-01-15T10:30:00Z",
  "updateTime": "2026-01-15T10:30:00Z"
}
```

#### List Sessions
Lists your sessions.

```bash
curl -sS \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions?pageSize=20"
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pageSize` | integer | 30 | Number of sessions to return (1-100) |
| `pageToken` | string | - | Token from previous response for pagination |

#### Get Session
Retrieves a single session by ID.

```bash
curl -sS \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID"
```

**Response includes outputs on completion:**
```json
{
  "name": "sessions/31415926535897932384",
  "id": "31415926535897932384",
  "state": "COMPLETED",
  "outputs": [
    {
      "pullRequest": {
        "url": "https://github.com/octocat/Hello-World/pull/42",
        "title": "Add Login Tests",
        "description": "This PR adds comprehensive unit tests..."
      }
    }
  ]
}
```

#### Send Message
Sends a message to an active session.

```bash
curl -sS \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:sendMessage" \
  -d '{"prompt": "Also add integration tests"}'
```

Use this to provide feedback, answer questions, or give additional instructions.

#### Approve Plan
Approves a pending plan (only needed if `requirePlanApproval` was true).

```bash
curl -sS \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:approvePlan"
```

#### Delete Session
Deletes a session.

```bash
curl -sS \
  -X DELETE \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID"
```

---

### Activities

#### List Activities
Lists activities for a session.

```bash
curl -sS \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID/activities?pageSize=30"
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pageSize` | integer | 50 | Number of activities to return (1-100) |
| `pageToken` | string | - | Token from previous response for pagination |

**Response:**
```json
{
  "activities": [
    {
      "name": "sessions/123/activities/456",
      "createTime": "2026-01-15T10:31:00Z",
      "planGenerated": {
        "plan": "1. Analyze existing code\n2. Create test files\n3. Write tests..."
      }
    },
    {
      "name": "sessions/123/activities/457",
      "createTime": "2026-01-15T10:32:00Z",
      "progressUpdate": {
        "title": "Writing tests",
        "details": "Creating test file for auth module..."
      }
    }
  ],
  "nextPageToken": "..."
}
```

Activities may include artifacts with code changes:
```json
{
  "artifacts": [
    {
      "changeSet": {
        "gitPatch": {
          "unidiffPatch": "diff --git a/...",
          "baseCommitId": "abc123",
          "suggestedCommitMessage": "Add unit tests for login"
        }
      }
    }
  ]
}
```

#### Get Activity
Retrieves a single activity by ID.

```bash
curl -sS \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID/activities/ACTIVITY_ID"
```

## Script Reference

### jules_api.sh

The `scripts/jules_api.sh` script provides a convenient wrapper for common API operations.

**Usage:**
```bash
# List sources
./scripts/jules_api.sh sources

# List sessions
./scripts/jules_api.sh sessions [--page-size N]

# List activities for a session
./scripts/jules_api.sh activities --session <id> [--page-size N]

# Send message to session
./scripts/jules_api.sh send-message --session <id> --prompt "..."

# Approve plan
./scripts/jules_api.sh approve-plan --session <id>

# Create new session
./scripts/jules_api.sh new-session \
  --source "sources/github/owner/repo" \
  --title "..." \
  --prompt "..." \
  [--branch main] \
  [--auto-pr] \
  [--no-plan-approval]
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--source` | Source name (format: `sources/github/owner/repo`) |
| `--title` | Session title |
| `--prompt` | Task description or message content |
| `--session` | Session ID |
| `--branch` | Starting branch (default: `main`) |
| `--auto-pr` | Enable automatic PR creation |
| `--require-plan-approval` | Require explicit plan approval (default) |
| `--no-plan-approval` | Skip plan approval (use for low-risk tasks only) |
| `--page-size` | Number of results to return |

### jules.js

The `scripts/jules.js` script wraps the Jules CLI for programmatic use.

**Usage:**
```bash
node scripts/jules.js version
node scripts/jules.js list-repos
node scripts/jules.js list-sessions
node scripts/jules.js new --repo owner/repo --task "Your task"
node scripts/jules.js pull --session SESSION_ID
```

## Common Error Patterns

### "Source not found" or "Repository not found"

**Cause:** Repository not connected or incorrect source name format.

**Solution:**
1. Run `./scripts/jules_api.sh sources` to list available sources
2. Ensure you've installed the Jules GitHub app for this repo
3. Use the exact source name from the list (e.g., `sources/github/octocat/Hello-World`)

### "Missing JULES_API_KEY"

**Cause:** API key not set in environment.

**Solution:**
```bash
export JULES_API_KEY="your-api-key"
```

### Authentication Errors

**Cause:** Invalid or expired API key.

**Solution:**
1. Generate a new API key at https://jules.google.com/settings#api
2. Update the `JULES_API_KEY` environment variable
3. Note: You can have at most 3 API keys at a time

### Session Stuck in AWAITING_PLAN_APPROVAL

**Cause:** Session was created with `requirePlanApproval: true`.

**Solution:**
```bash
./scripts/jules_api.sh approve-plan --session SESSION_ID
```

### Task Fails with Vague Error

**Cause:** Vague prompts may produce unexpected results.

**Solution:**
- Write clear, specific prompts
- Break large tasks into smaller, focused tasks
- Avoid prompts that require long-running commands (dev servers, watch scripts)

### Large Files Skipped

**Cause:** Files exceeding 768,000 tokens may be skipped.

**Solution:**
- Break down operations on very large files
- Consider splitting large files before processing

## Best Practices

### Writing Effective Prompts

1. **Be specific**: Instead of "fix the bug", say "fix the null pointer exception in `auth.js:45` when email is undefined"
2. **Provide context**: Mention relevant files, functions, or error messages
3. **Keep tasks focused**: One logical task per session

### Monitoring Sessions

1. Poll session state to track progress
2. Check activities for detailed progress updates
3. Handle `AWAITING_USER_FEEDBACK` state by sending clarifying messages

### Security

1. Never include secrets or credentials in prompts
2. Review generated PRs before merging
3. Use `requirePlanApproval: true` (recommended for all repos, especially production)
4. Only install the Jules GitHub app on repositories you intend to use with Jules — limit access scope
5. Treat `JULES_API_KEY` as a secret: store it securely, rotate it regularly, and never paste it into untrusted places

### Performance

1. Use `automationMode: AUTO_CREATE_PR` for streamlined workflows
2. Only skip plan approval (`requirePlanApproval: false`) for routine, low-risk tasks in non-critical repos
3. Break complex tasks into smaller sessions

## Extracting Results

When a session completes, retrieve the PR URL from outputs:

```bash
# Get session details
curl -sS \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID" \
  | jq '.outputs[].pullRequest.url'
```

## Known Limitations

- **Alpha API**: Specifications may change; API keys and definitions are experimental
- **No long-running commands**: Jules cannot run `npm run dev` or similar watch scripts
- **Context size**: Files > 768,000 tokens may be skipped
- **Prompt sensitivity**: Vague prompts may produce unexpected results

## References

- [Jules API Documentation](https://jules.google/docs/api/reference/overview/)
- [Sessions Reference](https://jules.google/docs/api/reference/sessions/)
- [Activities Reference](https://jules.google/docs/api/reference/activities/)
- [Sources Reference](https://jules.google/docs/api/reference/sources/)
- [Types Reference](https://jules.google/docs/api/reference/types/)
- [Google Developers - Jules API](https://developers.google.com/jules/api)
- [Jules Settings (API Keys)](https://jules.google.com/settings#api)
