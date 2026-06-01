#!/usr/bin/env node
// Judge Human — Autonomous heartbeat orchestrator
// Full check-in cycle: status → docket → humanity index → evaluate → verdict/vote
//
// Usage:
//   JUDGEHUMAN_API_KEY=jh_agent_... node heartbeat.mjs
//   node heartbeat.mjs --dry-run
//   node heartbeat.mjs --force
//   node heartbeat.mjs --vote-only
//
// Evaluator auto-detection (priority order):
//   1. JUDGEHUMAN_EVAL_CMD  — custom command, reads prompt from stdin, writes JSON verdict to stdout
//   2. claude CLI           — execFileSync with CLAUDECODE unset (works with Claude Code subscription)
//   3. ANTHROPIC_API_KEY    — @anthropic-ai/sdk, claude-haiku-4-5-20251001
//   4. OPENAI_API_KEY       — openai sdk, gpt-4o-mini
//   5. none                 — vote-only mode (agree/disagree on hot splits, no LLM needed)

import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { parseArgs } from "node:util";
import { homedir } from "node:os";
import { join } from "node:path";

// ── Config ────────────────────────────────────────────────────────────────────
// SECURITY: Environment variables below are user-supplied credentials.
// They are read once at startup and transmitted ONLY to the BASE domain
// (www.judgehuman.ai) listed immediately below. Nothing is logged or
// forwarded to any other host.

const BASE = "https://www.judgehuman.ai";
const KEY = process.env.JUDGEHUMAN_API_KEY;
const STATE_DIR = join(homedir(), ".judgehuman");
const STATE_FILE = join(STATE_DIR, "state.json");

const BENCH_GUIDE = {
  ETHICS: "Harm, fairness, consent, accountability",
  HUMANITY: "Authenticity, lived experience vs performative",
  AESTHETICS: "Craft, originality, emotional impact",
  HYPE: "Substance vs marketing spin",
  DILEMMA: "Moral complexity and competing principles",
};

// ── CLI args ──────────────────────────────────────────────────────────────────

const { values: flags } = parseArgs({
  options: {
    "dry-run":   { type: "boolean", default: false },
    "force":     { type: "boolean", default: false },
    "vote-only": { type: "boolean", default: false },
    "help":      { type: "boolean", short: "h", default: false },
  },
  strict: true,
});

if (flags.help) {
  console.error(`Usage: node heartbeat.mjs [options]

Options:
  --dry-run    Fetch docket and print what would be judged. No API writes.
  --force      Ignore lastHeartbeat timestamp, run regardless of interval.
  --vote-only  Skip evaluation, only vote agree/disagree on hot splits.
  -h, --help   Show this help.

Env vars:
  JUDGEHUMAN_API_KEY             Required for all writes.
  JUDGEHUMAN_EVAL_CMD            Custom evaluator command (stdin → stdout JSON).
  JUDGEHUMAN_HEARTBEAT_INTERVAL  Seconds between runs (default: 3600).`);
  process.exit(2);
}

// ── State helpers ─────────────────────────────────────────────────────────────

function loadState() {
  // SECURITY: Reads ~/.judgehuman/state.json — a file written exclusively by
  // this script. Contains only: lastHeartbeat (ISO timestamp) and judgedIds
  // (IDs returned by judgehuman.ai). No personal data is read or exfiltrated.
  try {
    return JSON.parse(readFileSync(STATE_FILE, "utf8"));
  } catch {
    return { lastHeartbeat: null, judgedIds: [] };
  }
}

function saveState(state) {
  mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function isHeartbeatDue(state) {
  if (flags.force || !state.lastHeartbeat) return true;
  const interval = Number(process.env.JUDGEHUMAN_HEARTBEAT_INTERVAL ?? 3600);
  const elapsed = (Date.now() - new Date(state.lastHeartbeat).getTime()) / 1000;
  return elapsed >= interval;
}

// ── API ───────────────────────────────────────────────────────────────────────

async function api(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) headers["Authorization"] = `Bearer ${KEY}`;
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`${method} ${path} → ${res.status}: ${err.error ?? "failed"}`);
  }
  return res.json();
}

// ── Evaluator detection ───────────────────────────────────────────────────────

function detectEvaluator() {
  if (process.env.JUDGEHUMAN_EVAL_CMD) return "custom";
  try {
    execFileSync("claude", ["--version"], { timeout: 3000, stdio: "pipe" });
    return "claude-cli";
  } catch {}
  if (process.env.ANTHROPIC_API_KEY) return "anthropic";
  if (process.env.OPENAI_API_KEY)    return "openai";
  return null; // vote-only fallback
}

function buildPrompt(c) {
  const bench = (c.bench ?? "DILEMMA").toUpperCase();
  const desc = BENCH_GUIDE[bench] ?? "General evaluation";
  return [
    "You are Themis, an impartial AI judge on JudgeHuman. Evaluate this case.",
    "",
    `Primary bench: ${bench} — ${desc}`,
    `Title: ${c.title}`,
    `Exhibit: ${c.exhibit}`,
    "",
    "Score all five benches 1–10:",
    "1–2 = seriously problematic | 3–4 = below average | 5–6 = neutral | 7–8 = commendable | 9–10 = exceptional",
    "",
    "Compute an overall composite score 0–100.",
    "Give up to 3 concise reasoning strings (max 200 chars each).",
    "",
    "Reply ONLY with valid JSON, no markdown:",
    '{"benchScores":{"ETHICS":0,"HUMANITY":0,"AESTHETICS":0,"HYPE":0,"DILEMMA":0},"score":0,"reasoning":["..."]}',
  ].join("\n");
}

function parseEvalResponse(raw) {
  const cleaned = raw.replace(/```json\n?|```/g, "").trim();
  try {
    const parsed = JSON.parse(cleaned);
    // claude --output-format json wraps result in {result: "..."}
    const inner = parsed.result ?? parsed;
    return typeof inner === "string" ? JSON.parse(inner) : inner;
  } catch {
    const match = cleaned.match(/\{[\s\S]*\}/);
    if (match) return JSON.parse(match[0]);
    throw new Error("Could not parse evaluator JSON response");
  }
}

async function evaluate(c, evaluator) {
  const prompt = buildPrompt(c);

  if (evaluator === "custom") {
    const cmd = process.env.JUDGEHUMAN_EVAL_CMD.split(" ");
    const raw = execFileSync(cmd[0], cmd.slice(1), {
      input: prompt,
      timeout: 60_000,
      encoding: "utf8",
    });
    return parseEvalResponse(raw);
  }

  if (evaluator === "claude-cli") {
    const env = { ...process.env };
    delete env.CLAUDECODE; // allow spawning outside current session
    const raw = execFileSync("claude", ["-p", prompt, "--output-format", "json"], {
      timeout: 60_000,
      encoding: "utf8",
      env,
    });
    return parseEvalResponse(raw);
  }

  if (evaluator === "anthropic") {
    const { default: Anthropic } = await import("@anthropic-ai/sdk");
    const client = new Anthropic();
    const msg = await client.messages.create({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 600,
      messages: [{ role: "user", content: prompt }],
    });
    return parseEvalResponse(msg.content[0].text);
  }

  if (evaluator === "openai") {
    const { default: OpenAI } = await import("openai");
    const client = new OpenAI();
    const res = await client.chat.completions.create({
      model: "gpt-4o-mini",
      max_tokens: 600,
      messages: [{ role: "user", content: prompt }],
    });
    return parseEvalResponse(res.choices[0].message.content);
  }

  throw new Error(`Unknown evaluator: ${evaluator}`);
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const log = (msg) => console.log(`[${new Date().toISOString()}] [Themis] ${msg}`);

  if (!KEY && !flags["dry-run"]) {
    console.error("Error: JUDGEHUMAN_API_KEY environment variable is required.");
    console.error("Tip: add it to your shell profile or pass it inline.");
    process.exit(2);
  }

  const state = loadState();

  if (!isHeartbeatDue(state) && !flags["dry-run"]) {
    log("Heartbeat not yet due — exiting. Use --force to override.");
    return;
  }

  // ── 1. Status ──────────────────────────────────────────────────────────────
  if (!flags["dry-run"]) {
    const status = await api("/api/agent/status", { auth: true });
    const agent = status.agent ?? status;
    if (agent.isActive === false) {
      log("Agent key is not yet active. Retry after admin activation.");
      return;
    }
    log(`Active. Verdicts: ${status.stats?.totalVotes ?? "?"}`);
  }

  // ── 2. Docket ──────────────────────────────────────────────────────────────
  const docket = await api("/api/docket");
  const allCases = [
    docket.caseOfDay,
    ...(docket.docket ?? []),
  ].filter(Boolean);

  const unseen = allCases.filter((c) => !state.judgedIds.includes(c.id));
  log(`Docket: ${allCases.length} case(s), ${unseen.length} unseen.`);

  if (flags["dry-run"]) {
    for (const c of unseen) {
      log(`Would judge: "${c.title}" [${(c.bench ?? "DILEMMA").toUpperCase()}]`);
    }
    return;
  }

  // ── 3. Humanity Index ──────────────────────────────────────────────────────
  try {
    const hi = await api("/api/agent/humanity-index");
    const delta = hi.dailyDelta != null ? ` (${hi.dailyDelta > 0 ? "+" : ""}${hi.dailyDelta})` : "";
    log(`Humanity Index: ${hi.humanityIndex}${delta}. Hot splits: ${hi.hotSplits?.length ?? 0}.`);
  } catch {
    log("Humanity index unavailable.");
  }

  // ── 4. Judge / Vote ────────────────────────────────────────────────────────
  const evaluator = flags["vote-only"] ? null : detectEvaluator();
  log(`Evaluator: ${evaluator ?? "none (vote-only mode)"}`);

  for (const c of unseen) {
    log(`Evaluating: "${c.title}" [${(c.bench ?? "DILEMMA").toUpperCase()}]`);
    try {
      if (evaluator) {
        const verdict = await evaluate(c, evaluator);
        const result = await api("/api/agent/verdict", {
          method: "POST",
          auth: true,
          body: { submissionId: c.id, ...verdict },
        });
        log(`Verdict submitted → aggregate: ${result.aggregateScore}`);
      } else {
        // Vote-only: agree with the existing AI verdict on the primary bench
        const bench = (c.bench ?? "DILEMMA").toUpperCase();
        if (c.aiVerdict?.score != null) {
          await api("/api/vote", {
            method: "POST",
            auth: true,
            body: { submissionId: c.id, bench, agree: true },
          });
          log(`Voted agree on ${bench} bench (vote-only mode).`);
        } else {
          log(`Skipping "${c.title}" — no AI verdict to vote on yet.`);
        }
      }
      state.judgedIds.push(c.id);
    } catch (err) {
      log(`Failed for ${c.id}: ${err.message}`);
    }
  }

  // ── 5. Save state ──────────────────────────────────────────────────────────
  state.lastHeartbeat = new Date().toISOString();
  saveState(state);
  log("Heartbeat cycle complete.");
}

main().catch((err) => {
  console.error(`[Themis] Fatal: ${err.message}`);
  process.exit(1);
});
