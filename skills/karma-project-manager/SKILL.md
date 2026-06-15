---
name: project-manager
description: Manage projects, grants, milestones, and updates on the Karma protocol. Use when user says "create a project", "new project", "add a grant", "record funding", "add milestone", "complete milestone", "post an update", "project progress", "grant update", "update project", "edit project", "edit grant", "complete grant", "add roadmap milestone", "report impact", "endorse project", "add team member", "set up agent", "configure API key", or any on-chain project management action.
version: 2.0.0
tags: [agent, project, grant, milestone, update, create, manage, impact, endorsement, members]
metadata:
  author: Karma
  category: on-chain
---

# Project Manager

Manage projects, grants, milestones, and updates on the Karma protocol. All actions create on-chain attestations via a single API.

Full API docs: `https://gapapi.karmahq.xyz/v2/docs/static/index.html`

```bash
BASE_URL="${KARMA_API_URL:-https://gapapi.karmahq.xyz}"
API_KEY="${KARMA_API_KEY}"
INVOCATION_ID=$(uuidgen)
```

**CRITICAL: Every `curl` call must include these tracking headers:**

```bash
-H "X-Source: skill:project-manager"
-H "X-Invocation-Id: $INVOCATION_ID"
-H "X-Skill-Version: 2.0.0"
```

---

## Setup

If `KARMA_API_KEY` is already set, skip to [Verify](#verify).

Otherwise use the `AskUserQuestion` tool with these options:

- Question: "You need a Karma API key to continue. How would you like to set it up?"
- Options: ["Quick start — Generate instantly (no account needed)", "Email login — Link to existing Karma account", "I already have a key"]

### Quick Start (No Account Needed)

```bash
curl -s -X POST "${BASE_URL}/v2/agent/register" \
  -H "Content-Type: application/json" \
  -H "X-Source: skill:project-manager" -H "X-Invocation-Id: $INVOCATION_ID" -H "X-Skill-Version: 2.0.0" \
  -d '{}'
```

Returns `{ "apiKey": "karma_..." }` — shown only once.

**Important**: Always send `-d '{}'` — an empty body causes a 400 error.

### Email Login

1. Ask for email
2. `POST ${BASE_URL}/v2/api-keys/auth/init` with `{ "email": "..." }`
3. Ask for code → `POST ${BASE_URL}/v2/api-keys/auth/verify` with `{ "email": "...", "code": "...", "name": "claude-agent" }`
4. Returns `{ "key": "karma_..." }`

| Error | Action |
|-------|--------|
| `400 Invalid or expired code` | Ask to recheck or request new code |
| `409 Active key already exists` | Use existing key or revoke from website |

### Save API Key

After obtaining the key (from quick start, email login, or user pasting it), **ask permission** to save it permanently:

> Would you like me to save your API key to your shell config so you don't have to paste it every time?

If yes, detect the user's shell and append the export:

```bash
# Detect shell config file
if [ -f "$HOME/.zshrc" ]; then
  SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
  SHELL_RC="$HOME/.bashrc"
fi

# Append only if not already present
grep -q 'KARMA_API_KEY' "$SHELL_RC" || echo '\n# Karma API Key\nexport KARMA_API_KEY="karma_..."' >> "$SHELL_RC"

# Also export for current session
export KARMA_API_KEY="karma_..."
```

If the key already exists in the file, replace the old value instead of appending a duplicate.

If the user declines, just set it for the current session:

```bash
export KARMA_API_KEY="karma_..."
```

### Verify

```bash
curl -s "${BASE_URL}/v2/agent/info" \
  -H "x-api-key: ${API_KEY}" \
  -H "X-Source: skill:project-manager" -H "X-Invocation-Id: $INVOCATION_ID" -H "X-Skill-Version: 2.0.0"
```

If response includes `walletAddress` and `supportedActions` → ready. Do NOT show wallet/chain details to the user. Tell them:

> Your Karma agent is ready! You can now create projects, grants, milestones, and post updates.

---

## Execute Endpoint

All actions use:

```bash
curl -s -X POST "${BASE_URL}/v2/agent/execute" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -H "X-Source: skill:project-manager" -H "X-Invocation-Id: $INVOCATION_ID" -H "X-Skill-Version: 2.0.0" \
  -d '{ "action": "<ACTION>", "params": { ... } }'
```

### Success Output

```
[Action] completed successfully!

- Project: {title}
- Chain: {chainName} ({chainId})
- Transaction: {transactionHash}
```

---

## Supported Chains

| Chain | ID |
|-------|-----|
| Arbitrum | 42161 |
| Base | 8453 |
| Celo | 42220 |
| Lisk | 1135 |
| Optimism | 10 |
| Polygon | 137 |
| Scroll | 534352 |
| Sei | 1329 |
| **Testnets** | |
| Base Sepolia | 84532 |
| OP Sepolia | 11155420 |

### Default Chain Behavior

When the user does NOT specify a chain, default to **Base (8453)** and confirm:

> Your project will be created on **Base**. Continue?
>
> - **Yes**
> - **Choose another chain**: Arbitrum, Base, Celo, Lisk, Optimism, Polygon, Scroll, Sei

### Chain Inheritance

Child attestations **must** use the same chain as their parent:

- **Grant** → uses `project.chainId`
- **Grant Update** → uses `grant.chainId`
- **Update Grant Details** → uses `grant.chainId`
- **Complete Grant** → uses `grant.chainId`
- **Milestone** → uses `grant.chainId`
- **Complete Milestone** → uses `milestone.chainId`
- **Project Update** → uses `project.chainId`
- **Project Milestone** → uses `project.chainId`
- **Project Impact** → uses `project.chainId`
- **Endorse Project** → uses `project.chainId`
- **Add Members** → uses `project.chainId`

Look up the parent's chain from the API — never ask the user for a chain on child attestations.

---

## Actions

### createProject

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Blockchain ID (default: Base 8453) |
| `title` | Yes | Project name (1-200 chars) |
| `description` | Yes | Project description (1-5000 chars) |

**Optional fields:**

| Param | Description |
|-------|-------------|
| `imageURL` | Logo/image URL |
| `links` | Array of `{ type, url }` — github, website, twitter, discord |
| `tags` | Array of strings (max 20) — e.g. "defi", "infrastructure" |
| `problem` | What problem does this project solve? (1-5000 chars) |
| `solution` | What is the solution? (1-5000 chars) |
| `missionSummary` | Brief mission statement (1-1000 chars) |
| `locationOfImpact` | Geographic or domain focus (1-1000 chars) |
| `businessModel` | How does the project sustain itself? (1-1000 chars) |
| `stageIn` | Development stage: Idea, MVP, Beta, Production, Growth, Mature (1-1000 chars) |
| `raisedMoney` | Funding raised so far (1-1000 chars) |
| `pathToTake` | Future roadmap (1-1000 chars) |

#### Gathering Project Information

When the user wants to create a project, present all fields at once and let them fill in what they want:

> To create your project, provide the following. Only **title** and **description** are required — the rest helps your project stand out:
>
> - **Title**: Project name
> - **Description**: What does the project do?
> - **Problem**: What problem are you solving?
> - **Solution**: How does your project solve it?
> - **Mission**: Sum up your mission in one sentence
> - **Stage**: Idea / MVP / Beta / Production / Growth / Mature
> - **Location of Impact**: Where or who does it impact?
> - **Business Model**: How do you sustain the project?
> - **Funding Raised**: What funding have you received?
> - **Roadmap**: What's your plan ahead?
> - **Links**: GitHub, website, Twitter, Discord URLs
> - **Tags**: Category tags (e.g. defi, infrastructure, public-goods)
> - **Image**: Logo or banner URL

Include only the fields the user provides — all metadata fields are optional.

#### After Project Creation

After a successful project creation, display:

> Your project has been created on {chainName}!
>
> - **Project**: {title}
> - **Chain**: {chainName} ({chainId})
> - **Transaction**: {transactionHash}
>
> Want to post your first update? Share something you just built, a milestone you hit, or what's coming next.

---

### updateProjectDetails

Update an existing project. **Replaces all fields** — fetch current details first for partial updates.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Chain where the project lives |
| `projectUID` | Yes | Project attestation UID |
| `title` | Yes | Project name (1-200 chars) |
| `description` | Yes | Project description (1-5000 chars) |

Plus all optional fields from `createProject` (imageURL, links, tags, problem, solution, missionSummary, locationOfImpact, businessModel, stageIn, raisedMoney, pathToTake).

**Important**: Always include existing fields alongside changes since the update replaces everything.

---

### createProjectUpdate

Post a progress update on a project.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match project's chain |
| `projectUID` | Yes | Project attestation UID |
| `title` | Yes | Update title (1-200 chars) |
| `text` | Yes | Update content (1-10000 chars) |

---

### createGrant

Add a grant (funding) to a project.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match project's chain |
| `projectUID` | Yes | Project attestation UID |
| `communityUID` | Yes | Community attestation UID |
| `title` | Yes | Grant title (1-200 chars) |
| `description` | No | Grant description (1-5000 chars) |
| `amount` | No | Funding amount (e.g. "50000 USDC") |
| `proposalURL` | No | Link to grant proposal |
| `programId` | No | Program ID (look up via programs API) |

---

### createGrantUpdate

Post a progress update on a grant.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match grant's chain |
| `grantUID` | Yes | Grant attestation UID |
| `title` | Yes | Update title (1-200 chars) |
| `text` | Yes | Update content (1-10000 chars) |

---

### createMilestone

Add a milestone to a grant.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match grant's chain |
| `grantUID` | Yes | Grant attestation UID |
| `title` | Yes | Milestone title (1-200 chars) |
| `description` | Yes | What will be delivered (1-5000 chars) |
| `endsAt` | Yes | Deadline as Unix timestamp in **seconds** |
| `priority` | No | Priority level (0-4) |

Date conversion: `Math.floor(new Date("2025-06-30").getTime() / 1000)`

---

### completeMilestone

Mark a milestone as completed.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match milestone's chain |
| `milestoneUID` | Yes | Milestone attestation UID |
| `reason` | Yes | Completion summary (1-5000 chars) |
| `proofOfWork` | No | URL to proof (PR, demo, report) |

---

### createProjectWithGrant

Create a project and grant in a single transaction (4 attestations).

All `createProject` params plus:

| Param | Required | Description |
|-------|----------|-------------|
| `communityUID` | Yes | Community attestation UID |
| `grant.title` | Yes | Grant title (1-200 chars) |
| `grant.description` | No | Grant description |
| `grant.amount` | No | Funding amount |
| `grant.proposalURL` | No | Proposal link |
| `grant.programId` | No | Program ID |

After success, use the same post-creation message as `createProject`.

---

### updateGrantDetails

Update an existing grant's details. Attests new details — the indexer uses the latest one.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match grant's chain |
| `grantUID` | Yes | Grant attestation UID |
| `title` | Yes | Grant title (1-200 chars) |
| `description` | No | Grant description (1-5000 chars) |
| `amount` | No | Funding amount (e.g. "50000 USDC") |
| `proposalURL` | No | Link to grant proposal |
| `programId` | No | Program ID |

**Important**: Fetch current grant details first, merge user's changes with existing values, then send all fields.

---

### completeGrant

Mark a grant as fully completed with a final summary.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match grant's chain |
| `grantUID` | Yes | Grant attestation UID |
| `title` | Yes | Completion title (1-200 chars) |
| `text` | Yes | Completion summary (1-10000 chars) |
| `proofOfWork` | No | URL to proof (demo, report, repo) |
| `pitchDeck` | No | URL to pitch deck |
| `demoVideo` | No | URL to demo video |
| `trackExplanations` | No | Array of `{ trackId, trackName, explanation }` — how the grant fulfilled each track |

After completion:

> Grant **{title}** has been marked as completed!
>
> - **Grant**: {title}
> - **Chain**: {chainName} ({chainId})
> - **Transaction**: {transactionHash}

---

### createProjectMilestone

Create a project-level roadmap milestone (not tied to a specific grant).

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match project's chain |
| `projectUID` | Yes | Project attestation UID |
| `title` | Yes | Milestone title (1-200 chars) |
| `text` | Yes | Milestone description (1-5000 chars) |

---

### createProjectImpact

Report impact achieved by a project.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match project's chain |
| `projectUID` | Yes | Project attestation UID |
| `work` | Yes | Description of work done (1-5000 chars) |
| `impact` | Yes | Description of impact achieved (1-5000 chars) |
| `proof` | Yes | Proof of impact — URL or description (1-5000 chars) |
| `startedAt` | No | When work started (Unix timestamp in seconds) |
| `completedAt` | Yes | When work was completed (Unix timestamp in seconds) |

---

### endorseProject

Endorse a project with an optional comment.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match project's chain |
| `projectUID` | Yes | Project attestation UID |
| `comment` | No | Endorsement comment (1-5000 chars) |

---

### addProjectMembers

Add team members to a project.

| Param | Required | Description |
|-------|----------|-------------|
| `chainId` | Yes | Must match project's chain |
| `projectUID` | Yes | Project attestation UID |
| `members` | Yes | Array of members (1-20) |

Each member object:

| Field | Required | Description |
|-------|----------|-------------|
| `address` | Yes | Ethereum address of the member |
| `name` | No | Member's display name |
| `profilePictureURL` | No | Member's profile picture URL |

---

## Looking Up Data

### Find a Project

```bash
curl -s -H "X-Source: skill:project-manager" -H "X-Invocation-Id: $INVOCATION_ID" -H "X-Skill-Version: 2.0.0" \
  "${BASE_URL}/v2/projects?q=SEARCH_TERM&limit=5&page=1"
```

Each result has: `uid`, `chainID`, `details.title`, `details.slug`, `details.description`

### Get Project by UID or Slug

```bash
curl -s -H "X-Source: skill:project-manager" -H "X-Invocation-Id: $INVOCATION_ID" -H "X-Skill-Version: 2.0.0" \
  "${BASE_URL}/v2/projects/PROJECT_UID_OR_SLUG"
```

### Get Project Grants

```bash
curl -s -H "X-Source: skill:project-manager" -H "X-Invocation-Id: $INVOCATION_ID" -H "X-Skill-Version: 2.0.0" \
  "${BASE_URL}/v2/projects/PROJECT_UID_OR_SLUG/grants"
```

Each grant has: `uid`, `details.title`, `milestones[]`

### Search Communities

```bash
curl -s -H "X-Source: skill:project-manager" -H "X-Invocation-Id: $INVOCATION_ID" -H "X-Skill-Version: 2.0.0" \
  "${BASE_URL}/v2/communities/?limit=5&page=1"
```

### Get Community Programs

```bash
curl -s -H "X-Source: skill:project-manager" -H "X-Invocation-Id: $INVOCATION_ID" -H "X-Skill-Version: 2.0.0" \
  "${BASE_URL}/communities/COMMUNITY_SLUG_OR_UID/programs"
```

Each program has: `programId`, `metadata.title`. Always include `programId` when the user mentions a specific program.

---

## Natural Language Mapping

| User says | Action |
|-----------|--------|
| "create a project", "new project" | `createProject` — present all fields, default Base |
| "create a DeFi project on Optimism" | `createProject` with tags: ["defi"], chainId: 10 |
| "update project details", "rename project", "enrich my project" | `updateProjectDetails` — fetch current details first |
| "post an update", "project progress" | `createProjectUpdate` — look up projectUID, inherit chain |
| "add a grant", "record funding" | `createGrant` — look up projectUID + communityUID, inherit chain |
| "grant update", "grant progress" | `createGrantUpdate` — look up grantUID, inherit chain |
| "edit grant", "update grant details", "change grant amount" | `updateGrantDetails` — fetch current grant, merge changes |
| "complete grant", "finish grant", "close grant" | `completeGrant` — look up grantUID, inherit chain |
| "add milestone", "set deliverable" | `createMilestone` — look up grantUID, inherit chain |
| "complete milestone", "mark done" | `completeMilestone` — look up milestoneUID, inherit chain |
| "add roadmap milestone", "project milestone" | `createProjectMilestone` — look up projectUID, inherit chain |
| "report impact", "log impact", "share impact" | `createProjectImpact` — look up projectUID, inherit chain |
| "endorse project", "support project" | `endorseProject` — look up projectUID, inherit chain |
| "add team member", "add member", "invite to project" | `addProjectMembers` — look up projectUID, inherit chain |
| "create project with grant" | `createProjectWithGrant` |

---

## Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 400 | Bad params | Show error, help fix |
| 401 | Invalid API key | Tell user to check `KARMA_API_KEY` or run setup |
| 429 | Rate limited (60/min) | Wait and retry |
| 500 | Server error | Retry once, then report |

## Edge Cases

| Scenario | Response |
|----------|----------|
| Missing required field | Ask user for it |
| Chain not specified (root action) | Default to Base, confirm with user |
| Chain not specified (child action) | Inherit from parent — never ask |
| API key not set | Run setup flow |
| Title too long (>200) | Truncate and confirm |
| Need UID but user gave name | Search API to find the UID |
| Partial project update | Fetch current details, merge changes, then update |
| Multiple grants on project | Show list, ask which one |
| Date given as string | Convert to Unix timestamp in seconds |
