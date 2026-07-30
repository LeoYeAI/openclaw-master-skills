#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const COVERAGE_FILE = resolve(process.cwd(), "coverage", "coverage-final.json");

const MIN_OVERALL_STATEMENTS = 50;
const MIN_CRITICAL_TOOL_STATEMENTS = 80;

const CRITICAL_TOOLS = [
  "src/tools/hire.ts",
  "src/tools/execute_tx.ts",
  "src/tools/register.ts",
  "src/tools/listen.ts",
  "src/tools/checkpoint.ts",
];

function pct(covered, total) {
  if (total === 0) return 100;
  return (covered / total) * 100;
}

function toPosixPath(p) {
  return p.replace(/\\/g, "/");
}

function fileStatementCoverage(entry) {
  const counts = Object.values(entry.s ?? {});
  const total = counts.length;
  const covered = counts.filter((n) => Number(n) > 0).length;
  return {
    covered,
    total,
    percent: pct(covered, total),
  };
}

async function main() {
  let raw;
  try {
    raw = await readFile(COVERAGE_FILE, "utf8");
  } catch {
    console.error(`[coverage-gate] Missing file: ${COVERAGE_FILE}`);
    console.error("[coverage-gate] Run `npm run test:coverage` first.");
    process.exit(1);
  }

  const report = JSON.parse(raw);
  const entries = Object.entries(report);

  if (entries.length === 0) {
    console.error("[coverage-gate] Empty coverage report.");
    process.exit(1);
  }

  let overallCovered = 0;
  let overallTotal = 0;
  const perFile = new Map();

  for (const [absPath, data] of entries) {
    const rel = toPosixPath(absPath).split("/src/").length > 1
      ? `src/${toPosixPath(absPath).split("/src/")[1]}`
      : toPosixPath(absPath);

    const stats = fileStatementCoverage(data);
    perFile.set(rel, stats);
    overallCovered += stats.covered;
    overallTotal += stats.total;
  }

  const overallPct = pct(overallCovered, overallTotal);
  let failed = false;

  if (overallPct < MIN_OVERALL_STATEMENTS) {
    failed = true;
    console.error(
      `[coverage-gate] FAIL overall statements ${overallPct.toFixed(2)}% < ${MIN_OVERALL_STATEMENTS}%`
    );
  } else {
    console.log(
      `[coverage-gate] PASS overall statements ${overallPct.toFixed(2)}% >= ${MIN_OVERALL_STATEMENTS}%`
    );
  }

  for (const critical of CRITICAL_TOOLS) {
    const stats = perFile.get(critical);
    if (!stats) {
      failed = true;
      console.error(`[coverage-gate] FAIL missing critical file in coverage: ${critical}`);
      continue;
    }

    if (stats.percent < MIN_CRITICAL_TOOL_STATEMENTS) {
      failed = true;
      console.error(
        `[coverage-gate] FAIL ${critical} statements ${stats.percent.toFixed(2)}% < ${MIN_CRITICAL_TOOL_STATEMENTS}%`
      );
    } else {
      console.log(
        `[coverage-gate] PASS ${critical} statements ${stats.percent.toFixed(2)}% >= ${MIN_CRITICAL_TOOL_STATEMENTS}%`
      );
    }
  }

  if (failed) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("[coverage-gate] Unexpected error:", err);
  process.exit(1);
});

