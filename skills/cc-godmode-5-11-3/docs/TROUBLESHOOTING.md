# CC_GodMode Troubleshooting

Common issues and solutions when using the CC_GodMode skill.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [MCP Server Issues](#mcp-server-issues)
3. [Agent Issues](#agent-issues)
4. [Workflow Issues](#workflow-issues)
5. [Quality Gate Issues](#quality-gate-issues)

---

## Installation Issues

### Skill not found after installation

**Symptoms:**
- `clawdhub list` doesn't show cc-godmode
- Agent doesn't recognize CC_GodMode commands

**Solutions:**

1. Verify installation:
```bash
clawdhub list | grep cc-godmode
```

2. Try reinstalling:
```bash
clawdhub uninstall cc-godmode
clawdhub install cc-godmode
```

3. Check skill directory:
```bash
ls ~/.clawdbot/skills/cc-godmode/
```

### Version mismatch

**Symptoms:**
- Skill reports different version than expected
- Features from newer version not working

**Solutions:**

1. Check installed version:
```bash
grep "version:" ~/.clawdbot/skills/cc-godmode/SKILL.md
```

2. Update to latest:
```bash
clawdhub update cc-godmode
```

---

## MCP Server Issues

### Playwright MCP not available

**Symptoms:**
- @tester fails to start
- "Playwright MCP not responding" error
- No screenshots generated

**Solutions:**

1. Check MCP status:
```bash
claude mcp list
```

2. Verify Playwright is configured:
```bash
# In your MCP config (mcp.json)
{
  "playwright": {
    "command": "npx",
    "args": ["playwright-mcp"]
  }
}
```

3. Install Playwright:
```bash
npm install -g playwright-mcp
npx playwright install
```

### GitHub MCP not responding

**Symptoms:**
- @github-manager can't create issues/PRs
- "GitHub API rate limit" errors

**Solutions:**

1. Check authentication:
```bash
gh auth status
```

2. Re-authenticate:
```bash
gh auth login
```

3. Check rate limit:
```bash
gh api rate_limit --jq '.rate.remaining'
```

---

## Agent Issues

### @researcher timeout

**Symptoms:**
- Research takes too long
- Partial results only

**Solutions:**

This is by design. @researcher has a 30-second hard timeout.

1. For complex research, break into smaller queries
2. Use the partial results and request follow-up research
3. Check if specific URLs are slow to fetch

### @architect not providing enough detail

**Symptoms:**
- Architecture report too brief
- Missing trade-off analysis

**Solutions:**

1. Provide more context in your request:
```
New Feature: Add user authentication
- Expected users: 10,000+
- Security requirements: OAuth2, MFA
- Target platforms: Web, Mobile
```

2. Ask for specific decisions:
```
@architect: Also evaluate caching strategy and session management
```

### @api-guardian missing consumers

**Symptoms:**
- Some consumers not found
- Breaking changes not detected

**Solutions:**

1. Ensure grep patterns are correct for your codebase
2. Check for unusual import patterns:
```javascript
// These might be missed
const { type } = await import('./types')
require('./types')
```

3. Add custom search patterns in request

### @builder not running tests

**Symptoms:**
- Tests skipped
- "No tests found" message

**Solutions:**

1. Verify test setup:
```bash
npm test
```

2. Check test configuration in package.json
3. Ensure test files follow naming conventions (`*.test.ts`, `*.spec.ts`)

---

## Workflow Issues

### Wrong workflow selected

**Symptoms:**
- Bug fix using full feature workflow
- API change not triggering @api-guardian

**Solutions:**

1. Be explicit in your command:
```
Bug Fix: [description]
API Change: [description]
```

2. For API changes, mention the path:
```
API Change: Update User type in shared/types/user.ts
```

### Agents not called in order

**Symptoms:**
- @builder called before @architect
- Quality gates skipped

**Solutions:**

This indicates orchestrator confusion. Be explicit:

```
I want the full feature workflow:
1. First @architect for design
2. Then @builder for implementation
3. Then both quality gates
4. Finally @scribe for documentation
```

### Workflow stuck in loop

**Symptoms:**
- @builder → @validator → @builder repeating
- Never reaching @scribe

**Solutions:**

1. Check @validator output for persistent issues
2. Ask @validator to list ALL remaining issues
3. Consider marking non-critical issues as "defer to next version"

---

## Quality Gate Issues

### @validator always failing

**Symptoms:**
- TypeScript errors persist
- Tests keep failing

**Solutions:**

1. Run locally first:
```bash
npm run typecheck
npm test
```

2. Check if @builder received correct specs from @architect
3. Review @api-guardian consumer list for missed updates

### @tester screenshots not generated

**Symptoms:**
- No files in `.playwright-mcp/`
- Screenshot section empty in report

**Solutions:**

1. Verify Playwright MCP is working:
```javascript
await mcp__playwright__browser_take_screenshot({
  filename: "test.png"
});
```

2. Check directory permissions:
```bash
ls -la .playwright-mcp/
```

3. Ensure dev server is running:
```bash
npm run dev
```

### Parallel gates not working

**Symptoms:**
- @validator and @tester running sequentially
- Taking longer than expected

**Solutions:**

Parallel execution requires proper orchestrator coordination. Check:

1. Both agents are called simultaneously via Task tool
2. Results are collected at sync point
3. Decision matrix is applied correctly

---

## General Tips

### Reset workflow state

If things get confused:

```
Status
```

Then start fresh with explicit command.

### Check MCP availability

Before starting work:

```bash
claude mcp list
```

Expected:
- `playwright` ✓
- `github` ✓
- `lighthouse` (optional)
- `a11y` (optional)

### Force specific agent

If orchestrator isn't calling the right agent:

```
Call @researcher to research [topic]
Call @architect to design [feature]
```

### Skip to documentation

For documentation-only changes:

```
Documentation only: Update README installation section
```

This goes directly to @scribe without quality gates.

---

## Getting Help

1. Check [SKILL.md](../SKILL.md) for complete reference
2. Review [WORKFLOWS.md](./WORKFLOWS.md) for workflow details
3. See [AGENTS.md](./AGENTS.md) for agent specifications
4. Open an issue on GitHub for bugs
