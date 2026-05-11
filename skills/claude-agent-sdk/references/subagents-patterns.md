# Subagents Patterns

Guide to designing and orchestrating specialized subagents.

---

## What Are Subagents?

Specialized agents with:
- **Specific expertise** - Focused domain knowledge
- **Custom tools** - Only tools they need
- **Different models** - Match capability to task cost
- **Dedicated prompts** - Tailored instructions

---

## When to Use Subagents

### ✅ Use Subagents When:

- Task requires different expertise areas
- Some subtasks need different models (cost optimization)
- Tool access should be restricted per role
- Clear separation of concerns needed
- Multiple steps with specialized knowledge

### ❌ Don't Use Subagents When:

- Single straightforward task
- All work can be done by one agent
- Overhead of orchestration > benefit
- Tools/permissions don't vary

---

## AgentDefinition Structure

```typescript
type AgentDefinition = {
  description: string;        // When to use this agent
  prompt: string;             // System prompt for agent
  tools?: string[];           // Allowed tools (optional)
  model?: 'sonnet' | 'opus' | 'haiku' | 'inherit';  // Model (optional)
}
```

### Field Guidelines

**description**:
- Clear, action-oriented
- When to invoke this agent
- 1-2 sentences
- Examples: "Run test suites", "Deploy to production"

**prompt**:
- Agent's role and behavior
- Instructions and constraints
- What to do and what not to do
- Can be detailed (100-500 tokens)

**tools**:
- If omitted, inherits all tools from main agent
- Use to restrict agent to specific tools
- Examples: `["Read", "Grep"]` for read-only

**model**:
- `"haiku"` - Fast, cost-effective ($0.25/$1.25 per MTok)
- `"sonnet"` - Balanced ($3/$15 per MTok)
- `"opus"` - Maximum capability ($15/$75 per MTok)
- `"inherit"` - Use main agent's model
- If omitted, inherits main agent's model

---

## Design Patterns

### Pattern 1: DevOps Pipeline

```typescript
agents: {
  "test-runner": {
    description: "Run automated test suites and verify coverage",
    prompt: `You run tests.

Execute:
- Unit tests
- Integration tests
- End-to-end tests

FAIL if any tests fail. Report clear errors.`,
    tools: ["Bash", "Read"],
    model: "haiku"  // Fast, cost-effective
  },

  "security-checker": {
    description: "Security audits and vulnerability scanning",
    prompt: `You check security.

Scan for:
- Exposed secrets
- Dependency vulnerabilities
- Permission issues
- OWASP compliance

Block deployment if critical issues found.`,
    tools: ["Read", "Grep", "Bash"],
    model: "sonnet"  // Balance for analysis
  },

  "deployer": {
    description: "Application deployment and rollbacks",
    prompt: `You deploy applications.

Process:
1. Deploy to staging
2. Verify health checks
3. Deploy to production
4. Create rollback plan

ALWAYS have rollback ready.`,
    tools: ["Bash", "Read"],
    model: "sonnet"  // Reliable for critical ops
  }
}
```

### Pattern 2: Code Review Workflow

```typescript
agents: {
  "syntax-checker": {
    description: "Check syntax, formatting, and linting",
    prompt: `You check syntax and formatting.

Run:
- ESLint
- Prettier
- TypeScript type checking

Report all violations clearly.`,
    tools: ["Bash", "Read"],
    model: "haiku"  // Fast checks
  },

  "logic-reviewer": {
    description: "Review logic, algorithms, and architecture",
    prompt: `You review code logic.

Check:
- Algorithmic correctness
- Edge cases
- Performance issues
- Design patterns

Suggest improvements.`,
    tools: ["Read", "Grep"],
    model: "sonnet"  // Complex analysis
  },

  "security-reviewer": {
    description: "Review for security vulnerabilities",
    prompt: `You review security.

Check:
- SQL injection
- XSS vulnerabilities
- Authentication bypass
- Data exposure

FAIL on critical issues.`,
    tools: ["Read", "Grep"],
    model: "sonnet"  // Security expertise
  }
}
```

### Pattern 3: Content Generation

```typescript
agents: {
  "researcher": {
    description: "Research topics and gather information",
    prompt: `You research topics.

Gather:
- Relevant information
- Latest trends
- Best practices
- Examples

Provide comprehensive research.`,
    tools: ["WebSearch", "WebFetch", "Read"],
    model: "haiku"  // Fast research
  },

  "writer": {
    description: "Write content based on research",
    prompt: `You write content.

Write:
- Clear, engaging prose
- Well-structured
- Audience-appropriate
- Fact-based

Use research provided.`,
    tools: ["Write", "Read"],
    model: "sonnet"  // Quality writing
  },

  "editor": {
    description: "Edit and polish content",
    prompt: `You edit content.

Check:
- Grammar and spelling
- Clarity and flow
- Consistency
- Formatting

Polish to perfection.`,
    tools: ["Read", "Edit"],
    model: "sonnet"  // Quality editing
  }
}
```

### Pattern 4: Incident Response

```typescript
agents: {
  "incident-detector": {
    description: "Detect and triage incidents",
    prompt: `You detect incidents.

Monitor:
- Error rates
- Response times
- System health
- Alerts

Assess severity and impact.`,
    tools: ["Bash", "Read"],
    model: "haiku"  // Fast detection
  },

  "root-cause-analyzer": {
    description: "Analyze root cause of incidents",
    prompt: `You analyze root causes.

Investigate:
- Logs
- Metrics
- Recent changes
- Dependencies

Identify exact cause.`,
    tools: ["Bash", "Read", "Grep"],
    model: "sonnet"  // Deep analysis
  },

  "fix-implementer": {
    description: "Implement fixes for incidents",
    prompt: `You implement fixes.

Fix:
- Apply patches
- Rollback changes
- Update config
- Deploy hotfixes

Verify fix resolves issue.`,
    tools: ["Read", "Edit", "Bash"],
    model: "sonnet"  // Careful fixes
  }
}
```

---

## Orchestration Strategies

### Sequential Execution

Main agent coordinates agents in order:

```
test-runner → security-checker → deployer
```

**Use when**: Steps must happen in order

### Parallel Execution

Main agent delegates to multiple agents at once:

```
test-runner
security-checker  } in parallel
code-reviewer
```

**Use when**: Steps are independent

### Conditional Execution

Main agent decides which agents to use based on context:

```
if (tests fail) → test-fixer
if (security issue) → security-fixer
if (all pass) → deployer
```

**Use when**: Different paths needed

---

## Model Selection Strategy

### Cost vs Capability

| Model | Cost (in/out) | Speed | Use For |
|-------|---------------|-------|---------|
| Haiku | $0.25/$1.25 | Fastest | Monitoring, simple checks |
| Sonnet | $3/$15 | Medium | Code review, analysis |
| Opus | $15/$75 | Slowest | Complex reasoning |

### Optimization Tips

```typescript
// ✅ Good: Match model to task
agents: {
  "monitor": { model: "haiku" },      // Simple checks
  "reviewer": { model: "sonnet" },     // Analysis
  "architect": { model: "opus" }       // Complex design
}

// ❌ Bad: Opus for everything
agents: {
  "monitor": { model: "opus" },   // Wasteful
  "reviewer": { model: "opus" },  // Wasteful
  "simple-task": { model: "opus" } // Wasteful
}
```

---

## Tool Restriction Patterns

### Read-Only Agent

```typescript
{
  description: "Analyze code without modifications",
  tools: ["Read", "Grep", "Glob"],
  model: "haiku"
}
```

### Write-Only Agent

```typescript
{
  description: "Generate new files",
  tools: ["Write"],
  model: "sonnet"
}
```

### Modify Agent

```typescript
{
  description: "Edit existing files",
  tools: ["Read", "Edit"],
  model: "sonnet"
}
```

### Full Access Agent

```typescript
{
  description: "Complete control",
  tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
  model: "sonnet"
}
```

---

## Communication Between Agents

Agents communicate through the main agent:

```
Main Agent: "Run tests"
  ↓
Test Runner: "Tests passed"
  ↓
Main Agent: "Deploy to staging"
  ↓
Deployer: "Deployed to staging"
  ↓
Main Agent: "Verify health"
  ↓
Monitor: "Health checks passing"
  ↓
Main Agent: "Deploy to production"
```

**No direct agent-to-agent communication**.

---

## Best Practices

### ✅ Do

- Give agents clear, specific roles
- Match model to task complexity
- Restrict tools per agent's needs
- Write detailed prompts with constraints
- Use descriptive agent names
- Test agents independently
- Monitor which agents are invoked

### ❌ Don't

- Create overlapping responsibilities
- Use Opus for simple tasks
- Give all agents all tools
- Write vague prompts
- Use generic names like "agent1"
- Skip testing in isolation
- Assume agents will coordinate perfectly

---

## Troubleshooting

### Agent Not Invoked

**Problem**: Main agent doesn't call subagent

**Solution**: Improve `description` to be more specific

### Wrong Agent Invoked

**Problem**: Main agent calls incorrect subagent

**Solution**: Make descriptions more distinct

### Agent Lacks Capability

**Problem**: Agent can't complete task

**Solution**: Add required tools or upgrade model

---

**For more details**: See SKILL.md
**Examples**: templates/subagents-orchestration.ts
