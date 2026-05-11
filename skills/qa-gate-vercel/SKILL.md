---
name: qa-gate-vercel
description: Pre-production validation gate for Vercel/Supabase/Firebase stack — generates test plans, executes test suites, validates APIs, UI, toasts, LLM output quality, and produces go/no-go reports
user-invocable: true
---

# qa-gate-vercel

## Role

You are a senior QA architect responsible for the final validation gate before production deployment. You do NOT write individual unit tests (that is test-sentinel's job). Instead, you orchestrate a comprehensive validation sweep: you generate a detailed test plan covering every critical surface, execute automated tests, validate API contracts, check UI/UX flows including toast notifications, assess LLM output quality using rule-based checks and LLM-as-judge, and produce a structured go/no-go report. This skill creates test plan documents, validation scripts, and JSON reports. It never reads or modifies `.env`, `.env.local`, or credential files directly.

## Credential Scope

`OPENROUTER_API_KEY` is used in generated validation scripts to run LLM-as-judge evaluations on content quality. `SUPABASE_URL` and `SUPABASE_ANON_KEY` are referenced in generated API validation scripts to test Supabase endpoints. `VERCEL_TOKEN` is referenced for checking deployment status. All env vars are accessed via `process.env` or `os.environ.get()` in generated code only.

## Planning Protocol (MANDATORY)

Same structure as other skills but specific to this context:

1. Understand the scope — what is being validated (full app, specific feature, specific release)
2. Survey the project — detect test framework (Vitest/Jest/Playwright/Cypress), check existing test coverage, read package.json, read app structure
3. Identify all validation surfaces: API routes, Server Actions, database operations, auth flows, UI pages, toast notifications, LLM-powered features
4. Build the master test plan (JSON document)
5. Identify risks and blockers
6. Execute the validation pipeline
7. Produce the go/no-go report

## Part 1 — Test Plan Generation

The agent MUST generate a structured test plan before running anything. The plan is a JSON file saved to `qa-reports/test-plan.json`:

```json
{
  "project": "project-name",
  "version": "x.y.z",
  "date": "ISO-8601",
  "validator": "qa-gate-vercel",
  "surfaces": {
    "api_routes": [
      {
        "route": "/api/entities",
        "methods": ["GET", "POST"],
        "auth_required": true,
        "validations": ["status_codes", "response_schema", "error_handling", "rate_limiting", "auth_guard"]
      }
    ],
    "server_actions": [
      {
        "name": "createEntity",
        "file": "src/app/actions/entities.ts",
        "validations": ["input_validation", "auth_check", "db_write", "revalidation", "error_response"]
      }
    ],
    "ui_pages": [
      {
        "path": "/dashboard",
        "auth_required": true,
        "validations": ["renders_correctly", "responsive", "loading_states", "error_states", "accessibility"]
      }
    ],
    "toast_notifications": [
      {
        "trigger": "entity_created",
        "type": "success",
        "expected_message_pattern": "Entity .* created",
        "auto_dismiss": true,
        "validations": ["appears", "correct_type", "dismisses", "no_duplicate"]
      }
    ],
    "auth_flows": [
      {
        "flow": "email_login",
        "steps": ["navigate_to_login", "fill_form", "submit", "redirect_to_dashboard"],
        "error_cases": ["invalid_credentials", "unverified_email", "rate_limited"]
      }
    ],
    "llm_features": [
      {
        "feature": "content_generation",
        "endpoint": "/api/generate",
        "validations": ["response_format", "content_quality", "safety", "latency", "token_usage"]
      }
    ],
    "database_integrity": [
      {
        "table": "entities",
        "validations": ["rls_enforced", "constraints_valid", "indexes_exist", "no_orphans"]
      }
    ]
  }
}
```

### How to discover surfaces:

- API routes: scan `src/app/api/**/route.ts`
- Server Actions: scan for `"use server"` in `src/app/**/actions.ts` or similar
- UI pages: scan `src/app/**/page.tsx`
- Toast notifications: grep for toast library usage (sonner, react-hot-toast, shadcn toast)
- Auth flows: check firebase-auth-setup patterns, middleware.ts
- LLM features: grep for OpenAI/OpenRouter/Anthropic API calls
- Database: read Supabase migrations in `supabase/migrations/`

## Part 2 — API Validation

For each API route in the test plan, generate and execute a validation script.

### Framework Detection

```bash
# Detect test framework
if [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ]; then
  FRAMEWORK="vitest"
elif [ -f "jest.config.ts" ] || [ -f "jest.config.js" ]; then
  FRAMEWORK="jest"
else
  FRAMEWORK="vitest"  # default
fi
```

### API Route Validation Template (TypeScript)

Generate test files in `qa-tests/api/`:

```typescript
// qa-tests/api/entities.validation.test.ts
import { describe, it, expect, beforeAll } from "vitest"; // or jest

const BASE_URL = process.env.VALIDATION_BASE_URL || "http://localhost:3000";

describe("API Validation: /api/entities", () => {
  // 1. Status codes
  it("returns 200 for authenticated GET", async () => {
    const res = await fetch(`${BASE_URL}/api/entities`, {
      headers: { Authorization: `Bearer ${process.env.TEST_AUTH_TOKEN}` },
    });
    expect(res.status).toBe(200);
  });

  it("returns 401 for unauthenticated request", async () => {
    const res = await fetch(`${BASE_URL}/api/entities`);
    expect(res.status).toBe(401);
  });

  // 2. Response schema validation
  it("response matches expected schema", async () => {
    const res = await fetch(`${BASE_URL}/api/entities`, {
      headers: { Authorization: `Bearer ${process.env.TEST_AUTH_TOKEN}` },
    });
    const data = await res.json();
    expect(Array.isArray(data)).toBe(true);
    if (data.length > 0) {
      expect(data[0]).toHaveProperty("id");
      expect(data[0]).toHaveProperty("name");
      expect(data[0]).toHaveProperty("created_at");
    }
  });

  // 3. Error handling
  it("returns proper error for invalid input", async () => {
    const res = await fetch(`${BASE_URL}/api/entities`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.TEST_AUTH_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}), // missing required fields
    });
    expect(res.status).toBe(400);
    const err = await res.json();
    expect(err).toHaveProperty("error");
  });

  // 4. Method validation
  it("returns 405 for unsupported methods", async () => {
    const res = await fetch(`${BASE_URL}/api/entities`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${process.env.TEST_AUTH_TOKEN}` },
    });
    expect(res.status).toBe(405);
  });
});
```

### Supabase-Specific Validations

```typescript
// qa-tests/db/rls-validation.test.ts
describe("Supabase RLS Validation", () => {
  it("anon key cannot access other users' data", async () => {
    // Use Supabase JS client with anon key
    // Attempt to read data belonging to another user
    // Expect empty result or error
  });

  it("service role key bypasses RLS (server-only check)", async () => {
    // Verify service role has full access
    // This confirms RLS is active (anon is restricted, service role is not)
  });
});
```

## Part 3 — UI & Toast Validation

### Framework Detection for E2E

```bash
if [ -f "playwright.config.ts" ]; then
  E2E="playwright"
elif [ -f "cypress.config.ts" ] || [ -f "cypress.config.js" ]; then
  E2E="cypress"
else
  E2E="playwright"  # default, install if missing
fi
```

### Playwright UI Validation Template

```typescript
// qa-tests/ui/dashboard.validation.spec.ts
import { test, expect } from "@playwright/test";

test.describe("UI Validation: /dashboard", () => {
  test.beforeEach(async ({ page }) => {
    // Auth setup — use storageState or login flow
    await page.goto("/login");
    await page.fill('[name="email"]', process.env.TEST_USER_EMAIL!);
    await page.fill('[name="password"]', process.env.TEST_USER_PASSWORD!);
    await page.click('button[type="submit"]');
    await page.waitForURL("/dashboard");
  });

  test("page renders correctly", async ({ page }) => {
    await expect(page.locator("h1")).toBeVisible();
    await expect(page.locator("nav")).toBeVisible();
  });

  test("loading states display correctly", async ({ page }) => {
    // Intercept API to delay response
    await page.route("**/api/entities", async (route) => {
      await new Promise((r) => setTimeout(r, 2000));
      await route.continue();
    });
    await page.goto("/dashboard");
    await expect(page.locator('[data-testid="skeleton"]')).toBeVisible();
  });

  test("error states display correctly", async ({ page }) => {
    await page.route("**/api/entities", (route) =>
      route.fulfill({ status: 500, body: JSON.stringify({ error: "Server error" }) })
    );
    await page.goto("/dashboard");
    await expect(page.locator('[role="alert"]')).toBeVisible();
  });

  test("responsive layout", async ({ page }) => {
    // Mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator("nav")).toBeVisible();
    // Desktop
    await page.setViewportSize({ width: 1280, height: 720 });
    await expect(page.locator("aside")).toBeVisible();
  });
});
```

### Toast Notification Validation Template

```typescript
// qa-tests/ui/toasts.validation.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Toast Validation", () => {
  test("success toast appears on entity creation", async ({ page }) => {
    await page.goto("/entities/new");
    await page.fill('[name="name"]', "Test Entity");
    await page.click('button[type="submit"]');

    // Wait for toast (supports sonner, shadcn toast, react-hot-toast)
    const toast = page.locator('[data-sonner-toast], [role="status"], .Toastify__toast');
    await expect(toast).toBeVisible({ timeout: 5000 });
    await expect(toast).toContainText(/created|success/i);
  });

  test("error toast appears on failed submission", async ({ page }) => {
    // Simulate API error
    await page.route("**/api/entities", (route) =>
      route.fulfill({ status: 500, body: JSON.stringify({ error: "Failed" }) })
    );
    await page.goto("/entities/new");
    await page.fill('[name="name"]', "Test");
    await page.click('button[type="submit"]');

    const toast = page.locator('[data-sonner-toast][data-type="error"], .Toastify__toast--error, [role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });
  });

  test("toast auto-dismisses", async ({ page }) => {
    await page.goto("/entities/new");
    await page.fill('[name="name"]', "Test");
    await page.click('button[type="submit"]');
    const toast = page.locator('[data-sonner-toast], [role="status"]');
    await expect(toast).toBeVisible();
    await expect(toast).not.toBeVisible({ timeout: 10000 });
  });

  test("no duplicate toasts on rapid clicks", async ({ page }) => {
    await page.goto("/entities/new");
    await page.fill('[name="name"]', "Test");
    // Rapid double-click
    await page.click('button[type="submit"]');
    await page.click('button[type="submit"]');
    const toasts = page.locator('[data-sonner-toast], [role="status"]');
    const count = await toasts.count();
    expect(count).toBeLessThanOrEqual(1);
  });
});
```

## Part 4 — Auth Flow Validation

### Firebase Auth Validation

```typescript
// qa-tests/auth/auth-flows.validation.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Auth Flow Validation", () => {
  test("login with valid credentials redirects to dashboard", async ({ page }) => {
    await page.goto("/login");
    await page.fill('[name="email"]', process.env.TEST_USER_EMAIL!);
    await page.fill('[name="password"]', process.env.TEST_USER_PASSWORD!);
    await page.click('button[type="submit"]');
    await page.waitForURL("/dashboard", { timeout: 10000 });
    expect(page.url()).toContain("/dashboard");
  });

  test("login with invalid credentials shows error", async ({ page }) => {
    await page.goto("/login");
    await page.fill('[name="email"]', "wrong@example.com");
    await page.fill('[name="password"]', "wrongpass");
    await page.click('button[type="submit"]');
    await expect(page.locator('[role="alert"], .error, [data-testid="auth-error"]')).toBeVisible();
    expect(page.url()).toContain("/login");
  });

  test("protected routes redirect unauthenticated users", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForURL(/\/(login|auth)/);
  });

  test("logout clears session and redirects", async ({ page }) => {
    // Login first, then logout
    // ...login steps...
    await page.click('[data-testid="logout"], button:has-text("Logout"), button:has-text("Sair")');
    await page.waitForURL(/\/(login|auth|$)/);
    // Verify protected route is no longer accessible
    await page.goto("/dashboard");
    await page.waitForURL(/\/(login|auth)/);
  });
});
```

## Part 5 — LLM Output Quality Validation

### Two-Layer Approach: Rule-Based + LLM-as-Judge

#### Layer 1: Rule-Based Checks (always run first)

```typescript
// qa-tests/llm/rule-based-checks.ts
export interface LLMOutput {
  content: string;
  model: string;
  tokens_used: number;
  latency_ms: number;
}

export interface RuleCheckResult {
  rule: string;
  passed: boolean;
  details: string;
}

export function runRuleBasedChecks(output: LLMOutput, config: {
  maxTokens?: number;
  maxLatencyMs?: number;
  minLength?: number;
  maxLength?: number;
  requiredSections?: string[];
  forbiddenPatterns?: RegExp[];
  requiredFormat?: "json" | "markdown" | "plain";
  language?: string;
}): RuleCheckResult[] {
  const results: RuleCheckResult[] = [];

  // Length checks
  if (config.minLength) {
    results.push({
      rule: "min_length",
      passed: output.content.length >= config.minLength,
      details: `Content length: ${output.content.length}, minimum: ${config.minLength}`,
    });
  }
  if (config.maxLength) {
    results.push({
      rule: "max_length",
      passed: output.content.length <= config.maxLength,
      details: `Content length: ${output.content.length}, maximum: ${config.maxLength}`,
    });
  }

  // Token usage
  if (config.maxTokens) {
    results.push({
      rule: "token_budget",
      passed: output.tokens_used <= config.maxTokens,
      details: `Tokens used: ${output.tokens_used}, budget: ${config.maxTokens}`,
    });
  }

  // Latency
  if (config.maxLatencyMs) {
    results.push({
      rule: "latency",
      passed: output.latency_ms <= config.maxLatencyMs,
      details: `Latency: ${output.latency_ms}ms, max: ${config.maxLatencyMs}ms`,
    });
  }

  // Required sections
  if (config.requiredSections) {
    for (const section of config.requiredSections) {
      results.push({
        rule: `required_section:${section}`,
        passed: output.content.toLowerCase().includes(section.toLowerCase()),
        details: `Section "${section}" ${output.content.toLowerCase().includes(section.toLowerCase()) ? "found" : "missing"}`,
      });
    }
  }

  // Forbidden patterns (PII, hallucination markers, etc.)
  if (config.forbiddenPatterns) {
    for (const pattern of config.forbiddenPatterns) {
      const match = pattern.exec(output.content);
      results.push({
        rule: `forbidden_pattern:${pattern.source}`,
        passed: !match,
        details: match ? `Found forbidden pattern: "${match[0]}"` : "No forbidden patterns found",
      });
    }
  }

  // Format validation
  if (config.requiredFormat === "json") {
    try {
      JSON.parse(output.content);
      results.push({ rule: "valid_json", passed: true, details: "Valid JSON" });
    } catch {
      results.push({ rule: "valid_json", passed: false, details: "Invalid JSON" });
    }
  }

  // Empty/garbage check
  results.push({
    rule: "not_empty",
    passed: output.content.trim().length > 0,
    details: output.content.trim().length === 0 ? "Output is empty" : "Output has content",
  });

  results.push({
    rule: "not_truncated",
    passed: !output.content.endsWith("...") && !output.content.endsWith("…"),
    details: "Check for truncation markers",
  });

  return results;
}
```

#### Layer 2: LLM-as-Judge (runs for content quality assessment)

```typescript
// qa-tests/llm/llm-judge.ts
export async function llmJudge(
  output: string,
  prompt: string,
  criteria: {
    relevance: boolean;
    accuracy: boolean;
    completeness: boolean;
    tone: boolean;
    safety: boolean;
  }
): Promise<{
  overall_score: number; // 1-5
  criteria_scores: Record<string, number>;
  issues: string[];
  recommendation: "pass" | "review" | "fail";
}> {
  const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
  if (!OPENROUTER_API_KEY) {
    return {
      overall_score: 0,
      criteria_scores: {},
      issues: ["OPENROUTER_API_KEY not set — skipping LLM judge"],
      recommendation: "review",
    };
  }

  const judgingPrompt = `You are a strict QA evaluator. Assess the following LLM output against the original prompt.

ORIGINAL PROMPT:
${prompt}

LLM OUTPUT:
${output}

Score each criterion from 1 (terrible) to 5 (excellent):
${criteria.relevance ? "- RELEVANCE: Does the output address the prompt?" : ""}
${criteria.accuracy ? "- ACCURACY: Is the information correct and not hallucinated?" : ""}
${criteria.completeness ? "- COMPLETENESS: Does the output cover all requested aspects?" : ""}
${criteria.tone ? "- TONE: Is the tone appropriate for the context?" : ""}
${criteria.safety ? "- SAFETY: Is the content free of harmful, biased, or inappropriate material?" : ""}

Respond in JSON:
{
  "criteria_scores": { "relevance": N, "accuracy": N, ... },
  "overall_score": N,
  "issues": ["list of specific issues found"],
  "recommendation": "pass|review|fail"
}

Rules:
- overall_score < 3 = "fail"
- overall_score >= 3 and < 4 = "review"
- overall_score >= 4 = "pass"
- Any safety score < 3 = automatic "fail"`;

  const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "google/gemini-flash-1.5",
      messages: [{ role: "user", content: judgingPrompt }],
      temperature: 0.1,
      response_format: { type: "json_object" },
    }),
  });

  const data = await response.json();
  return JSON.parse(data.choices[0].message.content);
}
```

### LLM Validation Test Template

```typescript
// qa-tests/llm/content-quality.validation.test.ts
import { describe, it, expect } from "vitest";
import { runRuleBasedChecks } from "./rule-based-checks";
import { llmJudge } from "./llm-judge";

describe("LLM Output Quality Validation", () => {
  it("content generation meets quality standards", async () => {
    // 1. Call the actual LLM endpoint
    const res = await fetch(`${BASE_URL}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${TOKEN}` },
      body: JSON.stringify({ prompt: "Describe the benefits of remote work" }),
    });
    const output = await res.json();

    // 2. Rule-based checks first
    const ruleResults = runRuleBasedChecks(output, {
      minLength: 100,
      maxLength: 5000,
      maxLatencyMs: 10000,
      forbiddenPatterns: [
        /\b(SSN|social security)\b/i,     // PII
        /\b(as an AI|I cannot)\b/i,         // AI disclosure leaks
        /\b(undefined|null|NaN)\b/,         // Code leaks
      ],
    });
    const ruleFailures = ruleResults.filter((r) => !r.passed);
    expect(ruleFailures).toHaveLength(0);

    // 3. LLM-as-judge for content quality
    const judgment = await llmJudge(output.content, "Describe the benefits of remote work", {
      relevance: true,
      accuracy: true,
      completeness: true,
      tone: true,
      safety: true,
    });
    expect(judgment.recommendation).not.toBe("fail");
    expect(judgment.overall_score).toBeGreaterThanOrEqual(3);
  });
});
```

## Part 6 — Integration & Workflow Validation

### Vercel Deployment Status Check

```typescript
// qa-tests/infra/vercel-status.validation.test.ts
describe("Vercel Deployment Validation", () => {
  it("latest deployment is ready", async () => {
    const res = await fetch("https://api.vercel.com/v6/deployments?limit=1", {
      headers: { Authorization: `Bearer ${process.env.VERCEL_TOKEN}` },
    });
    const { deployments } = await res.json();
    expect(deployments[0].state).toBe("READY");
  });

  it("preview deployment matches current branch", async () => {
    // Check that the preview URL for the current PR is live and healthy
  });

  it("environment variables are set", async () => {
    // Verify all required env vars exist in the Vercel project
    // (without reading their values)
  });
});
```

### Supabase Health Check

```typescript
// qa-tests/infra/supabase-health.validation.test.ts
describe("Supabase Health Validation", () => {
  it("database is reachable", async () => {
    const res = await fetch(`${process.env.SUPABASE_URL}/rest/v1/`, {
      headers: {
        apikey: process.env.SUPABASE_ANON_KEY!,
        Authorization: `Bearer ${process.env.SUPABASE_ANON_KEY}`,
      },
    });
    expect(res.status).toBe(200);
  });

  it("auth service is healthy", async () => {
    const res = await fetch(`${process.env.SUPABASE_URL}/auth/v1/health`);
    expect(res.ok).toBe(true);
  });

  it("realtime is connected", async () => {
    // Test WebSocket connection to Supabase Realtime
  });
});
```

## Part 7 — Go/No-Go Report

After executing all validations, generate a comprehensive report:

```json
{
  "report": {
    "project": "project-name",
    "version": "x.y.z",
    "date": "ISO-8601",
    "validator": "qa-gate-vercel",
    "verdict": "GO | NO-GO | CONDITIONAL",
    "summary": {
      "total_checks": 45,
      "passed": 42,
      "failed": 2,
      "skipped": 1,
      "pass_rate": "93.3%"
    },
    "sections": {
      "api_routes": {
        "status": "PASS",
        "checks_run": 12,
        "checks_passed": 12,
        "details": []
      },
      "ui_pages": {
        "status": "PASS",
        "checks_run": 8,
        "checks_passed": 8,
        "details": []
      },
      "toast_notifications": {
        "status": "FAIL",
        "checks_run": 6,
        "checks_passed": 4,
        "failures": [
          {
            "test": "no_duplicate_toasts",
            "page": "/entities/new",
            "expected": "single toast on rapid clicks",
            "actual": "2 toasts appeared",
            "severity": "medium",
            "recommendation": "Add debounce to form submission"
          }
        ]
      },
      "auth_flows": {
        "status": "PASS",
        "checks_run": 5,
        "checks_passed": 5
      },
      "llm_quality": {
        "status": "CONDITIONAL",
        "rule_based": { "passed": 8, "failed": 0 },
        "llm_judge": {
          "average_score": 3.8,
          "recommendation": "review",
          "issues": ["Tone slightly too formal for target audience"]
        }
      },
      "database_integrity": {
        "status": "PASS",
        "rls_enforced": true,
        "orphan_records": 0
      },
      "infrastructure": {
        "status": "PASS",
        "vercel_deployment": "READY",
        "supabase_health": "OK"
      }
    },
    "blockers": [
      {
        "id": "BLOCK-001",
        "severity": "high",
        "description": "Duplicate toasts on /entities/new",
        "recommendation": "Fix before production"
      }
    ],
    "warnings": [
      {
        "id": "WARN-001",
        "severity": "low",
        "description": "LLM output tone slightly formal",
        "recommendation": "Review prompt engineering, not blocking"
      }
    ],
    "go_conditions": {
      "all_api_tests_pass": true,
      "all_auth_tests_pass": true,
      "no_high_severity_blockers": false,
      "llm_quality_above_threshold": true,
      "deployment_healthy": true
    }
  }
}
```

### Verdict Logic:

- **GO**: All checks pass, no blockers, no high-severity failures.
- **NO-GO**: Any high-severity blocker OR any auth failure OR any data integrity failure.
- **CONDITIONAL**: Medium-severity issues that can be accepted with stakeholder approval.

Save the report to `qa-reports/go-no-go-report.json` and also produce a human-readable markdown version at `qa-reports/go-no-go-report.md`.

## Part 8 — Execution Pipeline

The agent follows this execution order:

```
1. Generate test plan          → qa-reports/test-plan.json
2. Run existing test suite     → npx vitest run (or jest) + npx playwright test
3. Generate validation tests   → qa-tests/**/*.validation.test.ts
4. Run API validations         → qa-tests/api/
5. Run UI/toast validations    → qa-tests/ui/
6. Run auth flow validations   → qa-tests/auth/
7. Run LLM quality validations → qa-tests/llm/
8. Run infra health checks     → qa-tests/infra/
9. Aggregate results           → qa-reports/go-no-go-report.json
10. Generate human report      → qa-reports/go-no-go-report.md
```

### Commands

```bash
# Step 2: Existing tests
npx vitest run --reporter=json --outputFile=qa-reports/vitest-results.json 2>/dev/null || true
npx playwright test --reporter=json --output=qa-reports/playwright-results.json 2>/dev/null || true

# Step 3-7: Validation tests (separate config to avoid mixing with app tests)
npx vitest run --config qa-tests/vitest.config.ts --reporter=json --outputFile=qa-reports/validation-results.json

# Step 8: Playwright validation tests
npx playwright test --config qa-tests/playwright.config.ts --reporter=json --output=qa-reports/playwright-validation-results.json
```

### Validation Test Config (isolate from app tests)

```typescript
// qa-tests/vitest.config.ts
import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    include: ["qa-tests/**/*.validation.test.ts"],
    environment: "node",
    globals: true,
  },
  resolve: {
    alias: { "@": path.resolve(__dirname, "../src") },
  },
});
```

## Best Practices (DO)

- Always run the existing test suite FIRST before adding validation tests
- Use separate directories (`qa-tests/`, `qa-reports/`) to avoid polluting the app
- Detect and adapt to the project's test framework (Vitest/Jest, Playwright/Cypress)
- Run rule-based LLM checks before LLM-as-judge (cheaper, faster, catches obvious issues)
- Include severity levels in all failures (high/medium/low)
- Generate both JSON (machine-readable) and Markdown (human-readable) reports
- Check for toast libraries dynamically (sonner, react-hot-toast, shadcn toast)
- Validate responsive layout at mobile (375px), tablet (768px), and desktop (1280px) breakpoints
- Test auth error cases, not just happy paths
- Validate Supabase RLS separately (critical security check)

## Anti-Patterns (AVOID)

- NEVER skip the test plan generation step
- NEVER mix validation tests with app tests (separate config files)
- NEVER hardcode auth tokens in test files — always use process.env
- NEVER run LLM-as-judge without rule-based checks first (waste of tokens)
- NEVER mark a test as "skipped" without documenting why in the report
- NEVER auto-approve a NO-GO verdict — always surface blockers to the human
- NEVER test against production data — use test accounts and seed data
- NEVER ignore toast validation — toast bugs are the #1 user-facing UX complaint

## Safety Rules

- NEVER read or modify `.env`, `.env.local`, or any credential file directly
- All env var references are in generated test code via `process.env.*`
- NEVER auto-deploy after a CONDITIONAL or NO-GO verdict
- NEVER delete test data from production databases
- NEVER expose API keys in test reports — redact before writing to disk
- If OPENROUTER_API_KEY is not set, skip LLM-as-judge checks and mark as "review"
