# console.agent - Complete Implementation Reference

**Version 1.2.0**
Pavel
February 2026

> **Note:**
> This document is for AI agents and LLMs to follow when helping users
> implement, debug, or extend `console.agent()` in their codebases.
> Humans may also find it useful as a comprehensive reference.

---

## Abstract

Complete implementation guide for `@console-agent/agent` (npm) and `console-agent` (PyPI) — the jQuery of AI Agents. Covers zero-config setup, 4 AI personas, 4 built-in tools, structured output, file attachments, thinking mode, budget controls, and privacy features. Each section includes real-world examples with incorrect vs. correct patterns.

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Core API](#2-core-api)
   - 2.1 [Fire-and-Forget (Default)](#21-fire-and-forget-default)
   - 2.2 [Blocking Mode (Await)](#22-blocking-mode-await)
   - 2.3 [Persona Shortcuts](#23-persona-shortcuts)
3. [AI Personas](#3-ai-personas)
   - 3.1 [Security Persona](#31-security-persona)
   - 3.2 [Debugger Persona](#32-debugger-persona)
   - 3.3 [Architect Persona](#33-architect-persona)
   - 3.4 [General Persona](#34-general-persona)
   - 3.5 [Auto-Detection](#35-auto-detection)
4. [Built-in Tools](#4-built-in-tools)
   - 4.1 [Google Search](#41-google-search)
   - 4.2 [Code Execution](#42-code-execution)
   - 4.3 [URL Context](#43-url-context)
   - 4.4 [File Analysis](#44-file-analysis)
   - 4.5 [Combining Tools](#45-combining-tools)
5. [Advanced Features](#5-advanced-features)
   - 5.1 [Structured Output (Zod)](#51-structured-output-zod)
   - 5.2 [Structured Output (JSON Schema)](#52-structured-output-json-schema)
   - 5.3 [File Attachments](#53-file-attachments)
   - 5.4 [Thinking Mode](#54-thinking-mode)
   - 5.5 [Caller Source Context](#55-caller-source-context)
6. [Configuration](#6-configuration)
   - 6.1 [Global Configuration](#61-global-configuration)
   - 6.2 [Per-Call Options](#62-per-call-options)
   - 6.3 [Budget Controls](#63-budget-controls)
   - 6.4 [Privacy & Anonymization](#64-privacy--anonymization)
7. [Common Patterns](#7-common-patterns)
   - 7.1 [Security Auditing](#71-security-auditing)
   - 7.2 [Debugging Failed Tests](#72-debugging-failed-tests)
   - 7.3 [Data Validation](#73-data-validation)
   - 7.4 [Architecture Review](#74-architecture-review)
   - 7.5 [Performance Analysis](#75-performance-analysis)
   - 7.6 [Research with Tools](#76-research-with-tools)
8. [Python API](#8-python-api)
9. [Ollama (Local Models)](#9-ollama-local-models)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Quick Start

### JavaScript/TypeScript

```bash
npm install @console-agent/agent
export GEMINI_API_KEY="your-key-here"
```

```javascript
import '@console-agent/agent';

// That's it! Zero config required.
console.agent("analyze this error", error);
```

### Python

```bash
pip install console-agent
export GEMINI_API_KEY="your-key-here"
```

```python
from console_agent import agent

agent("analyze this error", error)
```

### Get a Free API Key

https://aistudio.google.com/apikey

---

## 2. Core API

### 2.1 Fire-and-Forget (Default)

**Impact: Most common usage — non-blocking**

Fire-and-forget is the default mode. The call returns immediately and the agent runs asynchronously in the background. Results are printed to console.

```javascript
// Returns immediately, agent runs async in background
console.agent("analyze this error", error);
console.agent("check security", userInput);
// Code continues executing without waiting...
```

**When to use:** Logging, analysis, monitoring — anything where you don't need the result inline.

### 2.2 Blocking Mode (Await)

**Impact: When you need structured results**

Await the call to get a full `AgentResult` object with structured data.

**Incorrect: ignoring the result when you need it**

```javascript
// ❌ Fire-and-forget when result is needed for logic
console.agent("validate email", email);
// Can't use result here — it's fire-and-forget!
sendEmail(email); // May send invalid email
```

**Correct: await when result drives logic**

```javascript
// ✅ Await to get structured result
const result = await console.agent("validate email", email);
if (!result.success) {
  throw new Error(result.summary);
}
sendEmail(email); // Only if validated
```

### 2.3 Persona Shortcuts

Shortcut methods auto-select the right persona:

```javascript
// These are equivalent:
console.agent("audit SQL", query, { persona: 'security' });
console.agent.security("audit SQL", query);

// All shortcuts:
console.agent.security(prompt, context?, options?);
console.agent.debug(prompt, context?, options?);
console.agent.architect(prompt, context?, options?);
```

---

## 3. AI Personas

### 3.1 Security Persona

**Icon:** 🛡️ | **Label:** Security audit | **Default tools:** `google_search`

OWASP security expert and penetration testing specialist. Audits code/inputs for SQL injection, XSS, CSRF, SSRF, and more.

**Output format:** Starts with risk level (SAFE / LOW RISK / MEDIUM RISK / HIGH RISK / CRITICAL), lists each vulnerability with type, location, impact, and fix.

**Auto-detected keywords:** security, vuln, vulnerability, exploit, injection, xss, csrf, ssrf, sql injection, auth, authentication, authorization, sanitize, escape, encrypt, hash, token, secret, api key, password, credential, owasp, cve

```javascript
const audit = await console.agent.security(
  "check for SQL injection",
  req.body.q
);

if (audit.data.severity === 'critical') {
  return res.status(400).json({ error: "Invalid input" });
}
```

### 3.2 Debugger Persona

**Icon:** 🐛 | **Label:** Debugging | **Default tools:** `code_execution`, `google_search`

Senior debugging expert and performance engineer. Analyzes errors, stack traces, and performance issues.

**Output format:** One-line summary, root cause explanation, concrete fix with code, severity rating, confidence score.

**Auto-detected keywords:** slow, perf, performance, optimize, debug, error, bug, crash, exception, stack, trace, memory, leak, timeout, latency, bottleneck, hang, freeze, deadlock, race condition

```javascript
await console.agent.debug("why did payment fail?", {
  order,
  result,
  error: paymentError,
  testName: 'payment processing'
});
```

### 3.3 Architect Persona

**Icon:** 🏗️ | **Label:** Architecture review | **Default tools:** `google_search`, `file_analysis`

Principal software engineer and system architect. Reviews system design, API design, code architecture.

**Output format:** Overall assessment (SOLID / NEEDS IMPROVEMENT / SIGNIFICANT CONCERNS), strengths, concerns with severity, concrete recommendations with trade-offs.

**Auto-detected keywords:** design, architecture, architect, pattern, scalab, microservice, monolith, api design, schema, database, system design, infrastructure, deploy, ci/cd, refactor, modular, coupling, cohesion, solid, clean architecture, domain driven, event driven

```javascript
console.agent.architect("review API design", {
  endpoint: '/api/users',
  method: 'POST',
  handler: userController,
  middleware: [auth, rateLimit]
});
```

### 3.4 General Persona

**Icon:** 🔍 | **Label:** Analyzing | **Default tools:** `code_execution`, `google_search`, `file_analysis`

Helpful senior full-stack engineer with broad expertise. Default fallback for any prompt not matching specific personas.

**Output format:** Clear one-line answer, supporting details, code examples when relevant, caveats, confidence score.

```javascript
console.agent("validate email format", email);
console.agent("explain this regex", /^[a-z]+$/i);
```

### 3.5 Auto-Detection

Personas are auto-detected based on prompt keywords. The system scans the prompt for matching keywords and selects the most relevant persona. If no keywords match, falls back to `general`.

```javascript
// Auto-selects security (keyword: "injection")
console.agent("check for injection vulnerabilities", code);

// Auto-selects debugger (keyword: "slow")
console.agent("why is this endpoint slow?", metrics);

// Auto-selects architect (keyword: "design")
console.agent("review this API design", schema);

// Falls back to general (no matching keywords)
console.agent("summarize this data", records);
```

---

## 4. Built-in Tools

**CRITICAL:** Tools are **opt-in**. They are NOT activated by default. You must explicitly pass them via `tools: [...]`.

### 4.1 Google Search

Real-time web grounding — searches for current information, CVEs, documentation.

```javascript
const result = await console.agent(
  "What are the latest CVEs for log4j?",
  null,
  { tools: ['google_search'] }
);
```

### 4.2 Code Execution

Python sandbox (Gemini-hosted) — calculations, data processing, algorithm verification.

```javascript
const result = await console.agent(
  "Calculate compound interest: $10000 at 5% for 10 years",
  null,
  { tools: ['code_execution'] }
);
// result.data contains the computed answer
```

### 4.3 URL Context

Fetch and analyze web pages — read docs, analyze APIs, extract content.

```javascript
const result = await console.agent(
  "Summarize the API at https://api.example.com/docs",
  null,
  { tools: ['url_context'] }
);
```

### 4.4 File Analysis

Analyze uploaded files (PDFs, images, code files).

```javascript
const result = await console.agent(
  "What's in this PDF?",
  null,
  {
    tools: ['file_analysis'],
    files: [{
      data: readFileSync('./report.pdf'),
      mediaType: 'application/pdf',
      fileName: 'report.pdf'
    }]
  }
);
```

### 4.5 Combining Tools

The agent decides which tools to use based on the prompt:

```javascript
const result = await console.agent(
  "Search for current world population, then calculate 1% of it",
  null,
  { tools: ['google_search', 'code_execution'] }
);
// 1. Uses google_search to find population
// 2. Uses code_execution to calculate 1%
// 3. Returns combined result
```

**Incorrect: enabling tools you don't need**

```javascript
// ❌ Enabling all tools wastes tokens and slows response
const result = await console.agent(
  "explain async/await",
  null,
  { tools: ['google_search', 'code_execution', 'url_context', 'file_analysis'] }
);
```

**Correct: only enable what's needed**

```javascript
// ✅ No tools needed — pure LLM knowledge
const result = await console.agent("explain async/await");
```

---

## 5. Advanced Features

### 5.1 Structured Output (Zod)

Use Zod schemas for typed, validated structured output:

```javascript
import { z } from 'zod';

const result = await console.agent(
  "analyze sentiment",
  customerReview,
  {
    schema: z.object({
      sentiment: z.enum(["positive", "negative", "neutral"]),
      score: z.number().min(0).max(1),
      keywords: z.array(z.string()),
      summary: z.string()
    })
  }
);

// result.data is typed and validated:
result.data.sentiment;  // "positive" ✅
result.data.score;      // 0.87 ✅
```

### 5.2 Structured Output (JSON Schema)

For projects without Zod, use plain JSON Schema:

```javascript
const result = await console.agent(
  "analyze sentiment",
  review,
  {
    responseFormat: {
      type: 'json_object',
      schema: {
        type: 'object',
        properties: {
          sentiment: { type: 'string', enum: ['positive', 'negative', 'neutral'] },
          score: { type: 'number' },
          keywords: { type: 'array', items: { type: 'string' } }
        },
        required: ['sentiment', 'score']
      }
    }
  }
);
```

### 5.3 File Attachments

Send PDFs, images, and other files for AI analysis:

```javascript
import { readFileSync } from 'fs';

const result = await console.agent(
  "What does this document say about revenue?",
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

Supported types: PDF, PNG, JPEG, GIF, WebP, plain text, and more.

### 5.4 Thinking Mode

Extended reasoning for complex problems. Requires `gemini-3-flash-preview` model.

```javascript
const result = await console.agent(
  "design optimal database schema for multi-tenant SaaS",
  requirements,
  {
    model: 'gemini-3-flash-preview',
    thinking: {
      level: 'high',           // 'minimal' | 'low' | 'medium' | 'high'
      includeThoughts: true    // Return reasoning summary
    }
  }
);

console.log(result.reasoning);  // Extended thought process
```

For `gemini-2.5` models, use `budget` instead of `level`:

```javascript
{
  thinking: {
    budget: 8192,            // Token budget for thinking
    includeThoughts: true
  }
}
```

### 5.5 Caller Source Context

By default, `console.agent()` automatically reads the source file where it was called and sends it as context to the AI. This gives the agent full understanding of surrounding code.

```javascript
// In myApp.js line 47:
console.agent("why does this fail?", error);
// Agent automatically sees myApp.js source code as context!

// Disable per-call:
console.agent("question", data, { includeCallerSource: false });

// Disable globally:
init({ includeCallerSource: false });
```

---

## 6. Configuration

### 6.1 Global Configuration

```javascript
import { init } from '@console-agent/agent';

init({
  // Core
  provider: 'google',                   // 'google' | 'ollama'
  apiKey: process.env.GEMINI_API_KEY,   // Default: GEMINI_API_KEY env
  model: 'gemini-2.5-flash-lite',       // Default model
  persona: 'general',                   // Default persona

  // Execution
  mode: 'fire-and-forget',             // 'fire-and-forget' | 'blocking'
  timeout: 10000,                       // 10s default

  // Budget
  budget: {
    maxCallsPerDay: 100,               // Hard limit
    maxTokensPerCall: 8000,            // Per-call token cap
    costCapDaily: 1.00                 // USD daily cap
  },

  // Privacy
  anonymize: true,                     // Auto-strip secrets/PII
  localOnly: false,                    // Disable cloud tools

  // Output
  verbose: false,                      // Show execution trace
  logLevel: 'info',                    // 'silent' | 'errors' | 'info' | 'debug'
  includeCallerSource: true,           // Auto-read source file

  // Debug
  dryRun: false                        // Log without sending
});
```

### 6.2 Per-Call Options

Every option can be overridden per-call:

```javascript
const result = await console.agent("complex analysis", data, {
  model: 'gemini-3-flash-preview',     // Override model
  persona: 'security',                  // Force persona
  verbose: true,                        // Show trace
  timeout: 30000,                       // 30s timeout
  tools: ['google_search', 'code_execution'],
  thinking: { level: 'high', includeThoughts: true },
  schema: myZodSchema,                  // Structured output
  includeCallerSource: false,           // Disable source context
  files: [{ data, mediaType, fileName }] // Attachments
});
```

### 6.3 Budget Controls

Hard limits prevent cost explosion:

```javascript
init({
  budget: {
    maxCallsPerDay: 100,      // Max 100 API calls per day
    maxTokensPerCall: 8000,   // Max 8K tokens per call
    costCapDaily: 1.00        // Max $1.00/day
  }
});
```

Rate limiting uses a token bucket algorithm that spreads calls evenly across 24 hours with graceful degradation.

### 6.4 Privacy & Anonymization

When `anonymize: true` (default), automatically strips before sending to AI:
- API keys and secrets (Bearer tokens, AWS keys, etc.)
- Email addresses
- IP addresses (IPv4 and IPv6)
- Private keys (RSA, SSH, PGP)
- Database connection strings
- JWT tokens

```javascript
// Data is auto-sanitized before sending
console.agent("analyze this config", {
  dbUrl: "postgres://user:secretpass@db.example.com/mydb",
  apiKey: "sk-abc123xyz",
  userEmail: "john@example.com"
});
// AI sees: dbUrl: "[REDACTED_DB_URL]", apiKey: "[REDACTED]", ...
```

---

## 7. Common Patterns

### 7.1 Security Auditing

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

### 7.2 Debugging Failed Tests

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

### 7.3 Data Validation

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

### 7.4 Architecture Review

```javascript
console.agent.architect("review API design", {
  endpoint: '/api/users',
  method: 'POST',
  handler: userController,
  middleware: [auth, rateLimit]
});
```

### 7.5 Performance Analysis

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

### 7.6 Research with Tools

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

## 8. Python API

### Basic Usage

```python
from console_agent import agent, init_agent

# Optional configuration
init_agent(
    api_key=os.getenv('GEMINI_API_KEY'),
    model='gemini-2.5-flash-lite',
    persona='general',
    budget={'maxCallsPerDay': 100}
)

# Fire-and-forget
agent("analyze this error", error)

# Blocking
result = agent("validate input", data)
if not result.success:
    raise ValueError(result.summary)
```

### Persona Shortcuts

```python
agent.security("audit SQL query", query)
agent.debug("why is this slow?", metrics)
agent.architect("review design", schema)
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

### Async Usage

```python
import asyncio
from console_agent import agent

async def analyze_batch(items):
    tasks = [
        agent("analyze item", item)
        for item in items
    ]
    results = await asyncio.gather(*tasks)
    return results
```

---

## 9. Ollama (Local Models)

Run completely local with Ollama — no API key needed:

### JavaScript

```javascript
import { init } from '@console-agent/agent';

init({
  provider: 'ollama',
  model: 'llama3.2',
  ollamaHost: 'http://localhost:11434'
});

console.agent("analyze this code", myCode);
```

### Python

```python
from console_agent import init_agent, agent

init_agent(
    provider='ollama',
    model='llama3.2',
    ollama_host='http://localhost:11434'
)

agent("analyze this code", my_code)
```

**Note:** With Ollama, tools like `google_search` and `code_execution` are not available (these are Gemini-specific). The agent uses pure LLM inference only.

---

## 10. Troubleshooting

### Issue: "No API key configured"

```bash
# Set environment variable
export GEMINI_API_KEY="your-key"

# Or configure explicitly
init({ apiKey: 'your-key' });
```

### Issue: "Budget exceeded"

```javascript
init({
  budget: {
    maxCallsPerDay: 200,
    costCapDaily: 2.00
  }
});
```

### Issue: "Agent timeout"

```javascript
agent("complex task", data, { timeout: 30000 });  // 30s
```

### Issue: "Results not specific enough"

**Incorrect:**

```javascript
// ❌ Vague prompt, no context
agent("help");
```

**Correct:**

```javascript
// ✅ Specific prompt with rich context
agent.debug("why does API return 500?", {
  endpoint: '/api/users',
  request: { method: 'POST', body },
  response: { status: 500, body: errorBody },
  logs: recentLogs,
  environment: process.env.NODE_ENV
});
```

### Issue: "Wrong persona selected"

```javascript
// Force persona explicitly
agent("analyze this", data, { persona: 'security' });
// Or use shortcuts
agent.security("analyze this", data);
```

---

## Type Reference

### AgentResult

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

### AgentCallOptions

```typescript
interface AgentCallOptions {
  model?: string;
  tools?: Array<'code_execution' | 'google_search' | 'url_context' | 'file_analysis'>;
  thinking?: {
    level?: 'minimal' | 'low' | 'medium' | 'high';  // gemini-3
    budget?: number;                                   // gemini-2.5
    includeThoughts?: boolean;
  };
  persona?: 'debugger' | 'security' | 'architect' | 'general';
  mode?: 'fire-and-forget' | 'blocking';
  verbose?: boolean;
  schema?: ZodSchema;
  responseFormat?: { type: 'json_object'; schema: JSONSchema };
  includeCallerSource?: boolean;
  files?: Array<{ data: Buffer; mediaType: string; fileName?: string }>;
}
```

### AgentConfig (init options)

```typescript
interface AgentConfig {
  provider: 'google' | 'ollama';
  apiKey?: string;
  model: string;
  ollamaHost: string;
  persona: 'debugger' | 'security' | 'architect' | 'general';
  budget: {
    maxCallsPerDay: number;    // Default: 100
    maxTokensPerCall: number;  // Default: 8000
    costCapDaily: number;      // Default: 1.00
  };
  mode: 'fire-and-forget' | 'blocking';
  timeout: number;             // Default: 10000
  anonymize: boolean;          // Default: true
  localOnly: boolean;          // Default: false
  dryRun: boolean;             // Default: false
  verbose: boolean;            // Default: false
  logLevel: 'silent' | 'errors' | 'info' | 'debug';
  includeCallerSource: boolean; // Default: true
}
```

---

## Available Models

| Model | Best For | Speed | Cost | Default |
|-------|----------|-------|------|---------|
| `gemini-2.5-flash-lite` | General purpose, fast | ~200ms | Very low | ✅ Default |
| `gemini-3-flash-preview` | Complex reasoning, thinking mode | ~400ms | Low | |

---

## Key Differences from Other Agents

| Feature | console.agent | LangChain | Agno |
|---------|---------------|-----------|------|
| Setup | 0 lines (env var) | 100+ lines | 50+ lines |
| API | Like console.log() | Complex classes | Framework |
| Blocking | Optional (await) | Always | Configurable |
| Tools | Opt-in per call | Pre-configured | Pre-configured |
| Best for | Runtime utilities | Chat apps | Multi-agent systems |

---

## Best Practices Summary

1. **Default to fire-and-forget** unless you need the result for logic
2. **Auto-suggest personas** based on task context (security → security persona)
3. **Include rich context** — pass relevant data objects, not just strings
4. **Tools are opt-in** — only enable what the task actually needs
5. **Budget controls in production** — set daily limits before deploying
6. **Zero-config first** — just set `GEMINI_API_KEY` and import
7. **Test debugging** — use in test suites to debug failures automatically
8. **Structured output** — use Zod schemas for typed results

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

This AGENTS.md is for `@console-agent/agent` v1.2.0

**License:** MIT © Pavel
