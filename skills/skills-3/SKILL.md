---
name: console-agent
description: Build AI agents with console.agent() - the jQuery of AI Agents. Drop console.agent(...) anywhere in your code for agentic workflows with the simplicity of console.log(). Use when adding AI agent capabilities, debugging with AI, security auditing, intelligent logging, or runtime analysis.
license: MIT
metadata:
  author: pavel
  version: "1.2.0"
  tags: [ai-agent, debugging, security, console, gemini, runtime-analysis]
---

# console.agent - The jQuery of AI Agents

Comprehensive guide for implementing `@console-agent/agent` — drop `console.agent(...)` anywhere in your code to execute agentic workflows with the simplicity of `console.log()`.

**Official Documentation:** https://console-agent.github.io  
**Package:** `@console-agent/agent` (npm) / `console-agent` (PyPI)  
**Version:** v1.2.0  
**Provider:** Google Gemini (gemini-2.5-flash-lite, gemini-3-flash-preview)

## When to Apply

Reference this skill when:
- User wants to add AI agent capabilities to their code
- User asks about debugging with AI assistance
- User mentions "console.agent" or agentic workflows
- User wants runtime analysis, security audits, or code review
- User needs intelligent logging, testing assistance, or data validation
- User asks about tools like code execution, Google Search, or file analysis

## Core Concepts

### 1. Fire-and-Forget by Default (Non-blocking)
```javascript
// Returns immediately, agent runs async in background
console.agent("analyze this error", error);
// Code continues executing...
```

### 2. Blocking Mode (Await for Structured Results)
```javascript
// Wait for complete AgentResult
const result = await console.agent("validate email", email);
if (!result.success) throw new Error(result.summary);
```

### 3. AI Personas (Auto-detected or Explicit)
- **Security** 🛡️ - OWASP expert (detects: injection, xss, vulnerability, csrf)
- **Debugger** 🐛 - Senior debugging expert (detects: slow, error, optimize, crash)
- **Architect** 🏗️ - Principal engineer (detects: design, architecture, schema)
- **General** 🔍 - Full-stack senior engineer (default fallback)

### 4. Output Modes

**Default (verbose: false):**
```
SQL injection detected in user input
fix: Use parameterized queries
severity: critical
```

**Verbose (verbose: true):**
```
[AGENT] ✓ 🛡️ Security audit Complete
[AGENT] ├─ ✓ SQL injection detected in user input
[AGENT] ├─ Tool: google_search
[AGENT] ├─ fix: Use parameterized queries
[AGENT] └─ confidence: 0.94 | 247ms | 156 tokens | model: gemini-2.5-flash-lite
```

---

## Installation & Setup

### JavaScript/TypeScript
```bash
npm install @console-agent/agent
```

### Python
```bash
pip install console-agent
```

### Get Free API Key
https://aistudio.google.com/apikey

### Minimal Setup (Zero Config Works!)
```javascript
// Just set environment variable
export GEMINI_API_KEY="your-key-here"

// Import and use
import '@console-agent/agent';
console.agent("analyze this", data);
```

### Optional Configuration
```javascript
import { init } from '@console-agent/agent';

init({
  apiKey: process.env.GEMINI_API_KEY,
  model: 'gemini-2.5-flash-lite',  // Default
  persona: 'general',
  mode: 'fire-and-forget',
  timeout: 10000,
  
  budget: {
    maxCallsPerDay: 100,
    maxTokensPerCall: 8000,
    costCapDaily: 1.00  // USD
  },
  
  anonymize: true,              // Auto-strip secrets/PII
  localOnly: false,             // Disable cloud tools
  includeCallerSource: true,    // Auto-read source file
  logLevel: 'info'
});
```

### Python Configuration
```python
from console_agent import init_agent, agent

init_agent(
    api_key=os.getenv('GEMINI_API_KEY'),
    model='gemini-2.5-flash-lite',
    persona='general',
    budget={'maxCallsPerDay': 100}
)
```

---

## API Reference

### `console.agent(prompt, context?, options?)`
Main API - call it like `console.log()`.

```javascript
// Simple fire-and-forget
console.agent("explain this error", error);

// Await structured results
const result = await console.agent("analyze", data, {
  persona: 'security',
  model: 'gemini-3-flash-preview',
  thinking: { level: 'high', includeThoughts: true },
  tools: ['google_search', 'code_execution']
});
```

### Return Type: `AgentResult`
```typescript
interface AgentResult {
  success: boolean;           // Overall task success
  summary: string;            // Human-readable conclusion
  reasoning?: string;         // Agent's thought process (if thinking enabled)
  data: Record<string, any>;  // Structured findings
  actions: string[];          // Tools used / steps taken
  confidence: number;         // 0-1 confidence score
  metadata: {
    model: string;
    tokensUsed: number;
    latencyMs: number;
    toolCalls: ToolCall[];
    cached: boolean;
  };
}
```

### Persona Shortcuts
```javascript
// Auto-selects security persona
console.agent.security("audit this query", sql);

// Auto-selects debugger persona
console.agent.debug("why is this slow?", metrics);

// Auto-selects architect persona
console.agent.architect("review API design", endpoint);
```

---

## Built-in Tools

**IMPORTANT:** Tools are opt-in. Only activated when explicitly passed via `tools: [...]`.

### 1. Google Search 🔍
Real-time web grounding - search for current info, CVEs, documentation.

```javascript
const result = await console.agent(
  "What is the current population of Tokyo?",
  null,
  { tools: ['google_search'] }
);
```

### 2. Code Execution 💻
Python sandbox (Gemini-hosted) - calculations, data processing, algorithm verification.

```javascript
const result = await console.agent(
  "Calculate the 20th Fibonacci number",
  null,
  { tools: ['code_execution'] }
);
// result.data.result → 6765
```

### 3. URL Context 🌐
Fetch and analyze web pages - read docs, analyze APIs, extract content.

```javascript
const result = await console.agent(
  "Summarize this page",
  null,
  { tools: ['url_context'] }
);
```

### Combining Multiple Tools
```javascript
// Agent decides which tools to use based on prompt
const result = await console.agent(
  "Search for current world population, then calculate 1% of it",
  null,
  { tools: ['google_search', 'code_execution'] }
);
// 1. Uses google_search to find population
// 2. Uses code_execution to calculate 1%
// 3. Returns combined result
```

---

## Common Use Cases

### 1. Security Auditing 🛡️
```javascript
app.post('/api/search', async (req, res) => {
  const query = req.body.q;
  
  const audit = await console.agent.security(
    "check for SQL injection", 
    query
  );
  
  if (audit.data.severity === 'critical') {
    return res.status(400).json({ error: "Invalid input" });
  }
  
  const results = await db.search(query);
  res.json(results);
});
```

### 2. Debugging Failed Tests 🐛
```javascript
import { agent } from '@console-agent/agent';
import { test, expect } from 'vitest';

test('payment processing', async () => {
  const result = await processPayment(order);
  
  if (!result.success) {
    await agent.debug("why did payment fail?", {
      order,
      result,
      testName: 'payment processing'
    });
  }
  
  expect(result.success).toBe(true);
});
```

**Output:**
```
Likely cause: Missing await on async fn
Suggested fix: Add 'await' on line 47
Confidence: 0.92 | 312ms | 189 tokens
```

### 3. Data Validation 📊
```javascript
const records = await fetchBatch();

const validation = await console.agent(
  "validate batch meets schema", 
  records,
  { 
    schema: z.object({
      valid: z.boolean(),
      errors: z.array(z.string()),
      quality_score: z.number()
    })
  }
);

if (!validation.data.valid) {
  console.log("Issues:", validation.data.errors);
}
```

### 4. Architecture Review 🏗️
```javascript
console.agent.architect("review API design", {
  endpoint: '/api/users',
  method: 'POST',
  handler: userController,
  middleware: [auth, rateLimit]
});
```

### 5. Performance Analysis
```javascript
const startTime = Date.now();
const result = await slowOperation();
const duration = Date.now() - startTime;

if (duration > 1000) {
  agent.debug("why is this slow?", {
    operation: 'slowOperation',
    duration,
    input: operationInput
  });
}
```

### 6. Research with Tools 🔍
```javascript
const research = await console.agent(
  "research known CVEs for lodash@4.17.20",
  null,
  { 
    tools: ['google_search'],
    persona: 'security'
  }
);
console.log(research.summary);
```

---

## Advanced Features

### Structured Output with Zod Schema
```javascript
import { z } from 'zod';

const result = await console.agent(
  "analyze sentiment", 
  review,
  {
    schema: z.object({
      sentiment: z.enum(["positive", "negative", "neutral"]),
      score: z.number(),
      keywords: z.array(z.string())
    })
  }
);

result.data.sentiment;  // "positive" ✅ typed and validated
```

### File Attachments
```javascript
import { readFileSync } from 'fs';

const doc = await console.agent(
  "What does this document say?", 
  null,
  {
    files: [{
      data: readFileSync('./data/report.pdf'),
      mediaType: 'application/pdf',
      fileName: 'report.pdf'
    }]
  }
);
```

### Thinking Mode (Extended Reasoning)
```javascript
const result = await console.agent(
  "design optimal database schema for multi-tenant SaaS",
  requirements,
  {
    model: 'gemini-3-flash-preview',
    thinking: { 
      level: 'high',          // 'low' | 'medium' | 'high'
      includeThoughts: true   // Return reasoning summary
    }
  }
);

console.log(result.reasoning);  // Extended thought process
```

---

## Best Practices

### 1. Provide Rich Context
```javascript
// ❌ Too vague
agent("fix this");

// ✅ Specific with context
agent.debug("why does payment fail?", {
  error,
  order,
  user,
  timestamp,
  environment: process.env.NODE_ENV,
  recentLogs: logs.slice(-10)
});
```

### 2. Use Appropriate Personas
```javascript
// Security tasks
agent.security("audit SQL query", query);

// Performance tasks
agent.debug("analyze slow response", { duration, query });

// Architecture tasks
agent.architect("review this pattern", codeStructure);

// General tasks (auto-detected)
agent("validate email format", email);
```

### 3. Handle Results Properly
```javascript
// Fire-and-forget for logging/analysis
agent("log unusual event", eventData);

// Await for decisions that affect flow
const isValid = await agent("validate input", userInput);
if (!isValid.success) {
  throw new ValidationError(isValid.summary);
}
```

### 4. Enable Tools When Needed
```javascript
// No tools - uses only LLM knowledge
agent("explain async/await");

// With search - gets current info
agent("latest React best practices", null, { 
  tools: ['google_search'] 
});

// With code execution - performs calculations
agent("optimize this algorithm", code, { 
  tools: ['code_execution'] 
});
```

### 5. Budget Monitoring
```javascript
init({
  budget: {
    maxCallsPerDay: 50,
    costCapDaily: 0.50
  },
  onBudgetWarning: (usage) => {
    console.warn(`Budget: ${usage.calls}/50 calls used`);
  }
});
```

---

## Available Models

| Model | Best For | Speed | Cost | Default |
|-------|----------|-------|------|---------|
| `gemini-2.5-flash-lite` | General purpose, fast | ~200ms | Very low | ✅ Default |
| `gemini-3-flash-preview` | Complex reasoning, thinking | ~400ms | Low | |

---

## Configuration Options Reference

### Full InitOptions
```typescript
interface InitOptions {
  // Core
  apiKey?: string;                      // Default: GEMINI_API_KEY env
  model?: 'gemini-2.5-flash-lite' | 'gemini-3-flash-preview';
  persona?: 'debugger' | 'security' | 'architect' | 'general';
  
  // Execution
  mode?: 'fire-and-forget' | 'blocking';
  timeout?: number;                     // Default: 10000ms
  
  // Budget
  budget?: {
    maxCallsPerDay?: number;            // Default: 100
    maxTokensPerCall?: number;          // Default: 8000
    costCapDaily?: number;              // Default: 1.00 USD
  };
  
  // Privacy
  anonymize?: boolean;                  // Default: true
  localOnly?: boolean;                  // Default: false
  
  // Output
  logLevel?: 'silent' | 'errors' | 'info' | 'debug';
  includeCallerSource?: boolean;        // Default: true
  
  // Advanced
  dryRun?: boolean;                     // Default: false
}
```

### Per-Call Options
```typescript
agent(prompt, context, {
  persona?: string;
  model?: string;
  verbose?: boolean;
  timeout?: number;
  tools?: Array<'google_search' | 'code_execution' | 'url_context'>;
  thinking?: {
    level?: 'low' | 'medium' | 'high';
    includeThoughts?: boolean;
  };
  schema?: ZodSchema;                   // For structured output
  files?: Array<{
    data: Buffer;
    mediaType: string;
    fileName: string;
  }>;
});
```

---

## Privacy & Security

### Auto-Anonymization
When `anonymize: true` (default), automatically strips:
- API keys and secrets
- Email addresses
- IP addresses
- AWS keys
- Private keys
- Database connection strings

### Budget Controls
Hard limits prevent cost explosion:
- **maxCallsPerDay**: 100 calls/day default
- **maxTokensPerCall**: 8K tokens/call default
- **costCapDaily**: $1.00/day default

### Rate Limiting
Token bucket algorithm spreads calls evenly across 24 hours with graceful degradation.

---

## Troubleshooting

### Issue: "No API key configured"
```bash
# Solution: Set environment variable
export GEMINI_API_KEY="your-key"

# Or configure explicitly
init({ apiKey: 'your-key' });
```

### Issue: "Budget exceeded"
```javascript
// Increase limits
init({
  budget: { 
    maxCallsPerDay: 200,
    costCapDaily: 2.00
  }
});
```

### Issue: "Agent timeout"
```javascript
// Increase timeout
agent("complex task", data, { timeout: 30000 });  // 30s
```

### Issue: "Results not specific enough"
```javascript
// ❌ Vague
agent("help");

// ✅ Specific with rich context
agent.debug("why does API return 500?", {
  endpoint: '/api/users',
  request: { method: 'POST', body },
  response: { status: 500, body: errorBody },
  logs: recentLogs,
  environment: process.env.NODE_ENV
});
```

---

## Python-Specific Examples

### Basic Usage
```python
from console_agent import agent

# Fire-and-forget
agent("analyze this error", error)

# Blocking
result = agent("validate input", data)
if not result.valid:
    raise ValueError(result.reason)
```

### With Pytest
```python
import pytest
from console_agent import agent

def test_data_pipeline():
    result = process_batch(test_data)
    
    if result.errors:
        agent.debug("pipeline failure", {
            "input": test_data,
            "output": result,
            "errors": result.errors
        })
    
    assert len(result.errors) == 0
```

### Persona Shortcuts
```python
# Security persona
agent.security("audit SQL query", query)

# Debug persona
agent.debug("why is this slow?", metrics)

# Architect persona
agent.architect("review design", schema)
```

---

## Implementation Tips for AI Assistants

1. **Default to fire-and-forget** unless user needs the result
2. **Auto-suggest personas** based on task context
3. **Include rich context** in examples - show what data to pass
4. **Explain tools** - they're opt-in, not automatic
5. **Show budget controls** for production scenarios
6. **Emphasize zero-config** - just set GEMINI_API_KEY
7. **Use in tests** - highlight debugging failed tests use case
8. **Reference official docs** at https://console-agent.github.io

---

## Key Differences from Other Agents

| Feature | console.agent | Langchain | Agno |
|---------|---------------|-----------|------|
| Setup | 0 lines (env var) | 100+ lines | 50+ lines |
| API | Like console.log() | Complex classes | Framework |
| Blocking | Optional (await) | Always | Configurable |
| Tools | Opt-in per call | Pre-configured | Pre-configured |
| Best for | Runtime utilities | Chat apps | Multi-agent systems |

---

## Official Links

- **Homepage:** https://console-agent.github.io
- **API Reference:** https://console-agent.github.io/reference
- **npm:** https://www.npmjs.com/package/@console-agent/agent
- **PyPI:** https://pypi.org/project/console-agent/
- **GitHub (JS):** https://github.com/console-agent/console_agent
- **GitHub (Python):** https://github.com/console-agent/console_agent_python
- **Get API Key:** https://aistudio.google.com/apikey

---

## Version
This SKILL.md is for `@console-agent/agent` v1.2.0

**License:** MIT © Pavel
