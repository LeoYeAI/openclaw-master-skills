# Session Management Guide

Complete guide to sessions, resuming, and forking in Claude Agent SDK.

---

## What Are Sessions?

Sessions enable:
- **Persistent conversations** - Resume where you left off
- **Context preservation** - Agent remembers everything
- **Alternative paths** - Fork to explore different approaches

---

## Session Lifecycle

```
Start → Capture Session ID → Resume → Resume → ... → End
                                  ↓
                                Fork (alternative path)
```

---

## Starting a Session

Every `query()` call creates a session.

```typescript
let sessionId: string | undefined;

const response = query({
  prompt: "Build a REST API",
  options: { model: "sonnet" }
});

for await (const message of response) {
  if (message.type === 'system' && message.subtype === 'init') {
    sessionId = message.session_id;
    console.log(`Session started: ${sessionId}`);
  }
}
```

**CRITICAL**: Capture `session_id` from `system` init message.

---

## Resuming a Session

Continue a previous conversation.

```typescript
const resumed = query({
  prompt: "Now add authentication",
  options: {
    resume: sessionId,  // Resume previous session
    model: "sonnet"
  }
});
```

**What's preserved**:
- All previous messages
- Agent's understanding of context
- Files created/modified
- Decisions made

**What's NOT preserved**:
- Environment variables
- Tool availability (specify again)
- Permission settings (specify again)

---

## Forking a Session

Create alternative path without modifying original.

```typescript
const forked = query({
  prompt: "Actually, make it GraphQL instead",
  options: {
    resume: sessionId,
    forkSession: true,  // Creates new branch
    model: "sonnet"
  }
});
```

**Result**:
- New session created
- Starts from same point as original
- Original session unchanged
- Can compare approaches

---

## Use Case Patterns

### Pattern 1: Sequential Development

Step-by-step feature building.

```typescript
// Step 1: Initial implementation
let session = await startSession("Create user authentication");

// Step 2: Add feature
session = await resumeSession(session, "Add OAuth support");

// Step 3: Add tests
session = await resumeSession(session, "Write integration tests");

// Step 4: Deploy
session = await resumeSession(session, "Deploy to production");
```

### Pattern 2: Exploration & Decision

Try multiple approaches, choose best.

```typescript
// Start main conversation
let mainSession = await startSession("Design payment system");

// Explore option A
let optionA = await forkSession(mainSession, "Use Stripe");

// Explore option B
let optionB = await forkSession(mainSession, "Use PayPal");

// Explore option C
let optionC = await forkSession(mainSession, "Use Square");

// Choose winner
let chosenSession = optionA;  // Decision made
await resumeSession(chosenSession, "Implement chosen approach");
```

### Pattern 3: Multi-User Collaboration

Multiple developers, independent work.

```typescript
// Developer A starts work
let sessionA = await startSession("Implement user profile page");

// Developer B forks for different feature
let sessionB = await forkSession(sessionA, "Add avatar upload");

// Developer C forks for another feature
let sessionC = await forkSession(sessionA, "Implement search");

// All can work independently
```

### Pattern 4: Error Recovery

Backup and restore points.

```typescript
// Save checkpoint before risky operation
let checkpoint = sessionId;

try {
  await resumeSession(checkpoint, "Refactor entire auth system");
} catch (error) {
  console.log("Refactor failed, restoring from checkpoint");
  await forkSession(checkpoint, "Try safer incremental refactor");
}
```

### Pattern 5: A/B Testing

Test different implementations.

```typescript
let baseline = await startSession("Implement feature X");

// Approach A
let approachA = await forkSession(baseline, "Use algorithm A");
const metricsA = await measurePerformance(approachA);

// Approach B
let approachB = await forkSession(baseline, "Use algorithm B");
const metricsB = await measurePerformance(approachB);

// Compare and choose
const winner = metricsA.better(metricsB) ? approachA : approachB;
```

---

## Session Best Practices

### ✅ Do

- Always capture `session_id` from init message
- Store session IDs for later use
- Use descriptive prompts when resuming
- Fork for alternative approaches
- Test resuming before deploying
- Consider session lifetime limits

### ❌ Don't

- Forget to capture session ID
- Assume sessions last forever
- Resume with completely unrelated prompts
- Fork excessively (creates many branches)
- Rely on sessions for critical state
- Skip testing resume functionality

---

## Helper Functions

```typescript
async function startSession(prompt: string): Promise<string> {
  let sessionId: string | undefined;

  const response = query({ prompt, options: { model: "sonnet" } });

  for await (const message of response) {
    if (message.type === 'system' && message.subtype === 'init') {
      sessionId = message.session_id;
    }
  }

  if (!sessionId) throw new Error('Failed to start session');
  return sessionId;
}

async function resumeSession(
  sessionId: string,
  prompt: string
): Promise<void> {
  const response = query({
    prompt,
    options: { resume: sessionId, model: "sonnet" }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

async function forkSession(
  sessionId: string,
  prompt: string
): Promise<string> {
  let newSessionId: string | undefined;

  const response = query({
    prompt,
    options: {
      resume: sessionId,
      forkSession: true,
      model: "sonnet"
    }
  });

  for await (const message of response) {
    if (message.type === 'system' && message.subtype === 'init') {
      newSessionId = message.session_id;
    } else if (message.type === 'assistant') {
      console.log(message.content);
    }
  }

  if (!newSessionId) throw new Error('Failed to fork session');
  return newSessionId;
}
```

---

## Session Storage

Store sessions for later use:

```typescript
// In-memory storage
const sessions = new Map<string, { id: string; created: Date }>();

async function saveSession(prompt: string) {
  const id = await startSession(prompt);
  sessions.set(id, { id, created: new Date() });
  return id;
}

function getSession(id: string) {
  return sessions.get(id);
}

// Database storage
async function saveSessionToDb(sessionId: string, metadata: any) {
  await db.insert('sessions', {
    id: sessionId,
    created_at: new Date(),
    metadata
  });
}
```

---

## Session Limits

### Context Window

Sessions have context window limits (200k tokens for Sonnet).

**Strategies**:
- SDK auto-compacts context
- Fork to start fresh from a point
- Summarize and start new session

### Lifetime

Sessions may expire after inactivity.

**Strategies**:
- Don't rely on sessions lasting indefinitely
- Store important state separately
- Test resume functionality

---

## Troubleshooting

### Session Not Found

**Problem**: `"Invalid session ID"`

**Causes**:
- Session expired
- Invalid session ID
- Session from different CLI instance

**Solution**: Start new session

### Context Preserved Incorrectly

**Problem**: Agent doesn't remember previous work

**Causes**:
- Different settings/tools specified
- Context window exceeded
- Fork instead of resume

**Solution**: Verify using `resume` not `forkSession`

### Too Many Forks

**Problem**: Hard to track branches

**Solution**: Limit forking, clean up unused branches

---

## Complete Example

```typescript
class SessionManager {
  private sessions = new Map<string, string>();

  async start(name: string, prompt: string): Promise<string> {
    const id = await startSession(prompt);
    this.sessions.set(name, id);
    console.log(`✨ Started: ${name}`);
    return id;
  }

  async resume(name: string, prompt: string): Promise<void> {
    const id = this.sessions.get(name);
    if (!id) throw new Error(`Session ${name} not found`);
    console.log(`↪️  Resuming: ${name}`);
    await resumeSession(id, prompt);
  }

  async fork(
    fromName: string,
    newName: string,
    prompt: string
  ): Promise<string> {
    const fromId = this.sessions.get(fromName);
    if (!fromId) throw new Error(`Session ${fromName} not found`);
    console.log(`🔀 Forking: ${fromName} → ${newName}`);
    const newId = await forkSession(fromId, prompt);
    this.sessions.set(newName, newId);
    return newId;
  }

  list(): string[] {
    return Array.from(this.sessions.keys());
  }
}

// Usage
const manager = new SessionManager();

await manager.start("main", "Build a web app");
await manager.resume("main", "Add authentication");
await manager.fork("main", "option-a", "Use JWT tokens");
await manager.fork("main", "option-b", "Use sessions");

console.log("Sessions:", manager.list());
// ["main", "option-a", "option-b"]
```

---

**For more details**: See SKILL.md
**Template**: templates/session-management.ts
