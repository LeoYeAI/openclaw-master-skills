#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import {
  execCommand,
  safeJsonParse,
  normalizeSeverity,
  getTimestamp,
  commandExists,
} from "../lib/utils.mjs";
import { generateReport, formatReportJson, formatReportText } from "../lib/report.mjs";

/**
 * @typedef {import('../lib/types.ts').Vulnerability} Vulnerability
 * @typedef {import('../lib/types.ts').ScanReport} ScanReport
 */

/**
 * Parse CLI arguments.
 *
 * @param {string[]} argv - Command line arguments
 * @returns {{target: string, format: 'json' | 'text'}}
 */
function parseArgs(argv) {
  const parsed = {
    target: "",
    format: "json",
  };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];

    if (token === "--target") {
      parsed.target = String(argv[i + 1] ?? "").trim();
      i += 1;
      continue;
    }
    if (token === "--format") {
      const formatValue = String(argv[i + 1] ?? "").trim();
      if (formatValue !== "json" && formatValue !== "text") {
        throw new Error("Invalid --format value. Use 'json' or 'text'.");
      }
      parsed.format = formatValue;
      i += 1;
      continue;
    }
    if (token === "--help" || token === "-h") {
      printUsage();
      process.exit(0);
    }

    throw new Error(`Unknown argument: ${token}`);
  }

  if (!parsed.target) {
    throw new Error("Missing required argument: --target");
  }

  return parsed;
}

/**
 * Print usage information.
 */
function printUsage() {
  process.stderr.write(
    [
      "Usage:",
      "  node scripts/sast_analyzer.mjs --target <path> [--format json|text]",
      "",
      "Examples:",
      "  node scripts/sast_analyzer.mjs --target ./skills/clawsec-suite",
      "  node scripts/sast_analyzer.mjs --target ./skills/ --format json",
      "",
      "Flags:",
      "  --target   Path to scan (required)",
      "  --format   Output format: json or text (default: json)",
      "",
    ].join("\n"),
  );
}

/**
 * Check if a file exists.
 *
 * @param {string} filePath - Path to check
 * @returns {Promise<boolean>}
 */
async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Run Semgrep for JavaScript/TypeScript analysis.
 *
 * @param {string} targetPath - Path to scan
 * @returns {Promise<Vulnerability[]>}
 */
async function runSemgrep(targetPath) {
  const vulnerabilities = [];

  // Check if semgrep is available
  const hasSemgrep = await commandExists("semgrep");
  if (!hasSemgrep) {
    process.stderr.write("[semgrep] semgrep command not found, skipping JavaScript/TypeScript SAST\n");
    return vulnerabilities;
  }

  try {
    // Run Semgrep with security-focused rules
    // NOTE: Semgrep exits non-zero when findings are present
    const { stdout } = await execCommand("semgrep", [
      "scan",
      "--config", "auto",
      "--json",
      targetPath,
    ]);

    const semgrepData = safeJsonParse(stdout, {
      fallback: { results: [] },
      label: "semgrep output",
    });

    // Semgrep format: { results: [ {check_id, path, extra: {message, severity, ...}, ...} ] }
    if (semgrepData && typeof semgrepData === "object" && "results" in semgrepData) {
      const results = Array.isArray(semgrepData.results) ? semgrepData.results : [];

      for (const result of results) {
        if (!result || typeof result !== "object") continue;

        const checkId = String(result.check_id || "semgrep-unknown");
        const filePath = String(result.path || "unknown");
        const extra = result.extra || {};

        // Extract metadata
        const message = String(extra.message || "Security issue detected");
        const severity = normalizeSeverity(extra.severity || "info");
        const metadata = extra.metadata || {};

        // Build references from metadata
        const references = [];
        if (metadata.references && Array.isArray(metadata.references)) {
          references.push(...metadata.references.map((r) => String(r)));
        }
        if (metadata.source && typeof metadata.source === "string") {
          references.push(metadata.source);
        }

        const vuln = {
          id: checkId,
          source: "sast",
          severity,
          package: path.basename(filePath),
          version: `${filePath}:${result.start?.line || 0}`,
          fixed_version: "",
          title: message.slice(0, 150),
          description: message,
          references,
          discovered_at: getTimestamp(),
        };

        vulnerabilities.push(vuln);
      }
    }
  } catch (error) {
    if (error instanceof Error) {
      process.stderr.write(`[semgrep] Warning: ${error.message}\n`);
    }
    // Continue with partial results
  }

  return vulnerabilities;
}

/**
 * Run Bandit for Python analysis.
 *
 * @param {string} targetPath - Path to scan
 * @returns {Promise<Vulnerability[]>}
 */
async function runBandit(targetPath) {
  const vulnerabilities = [];

  // Check if bandit is available
  const hasBandit = await commandExists("bandit");
  if (!hasBandit) {
    process.stderr.write("[bandit] bandit command not found, skipping Python SAST\n");
    return vulnerabilities;
  }

  // Check if pyproject.toml exists in the project root
  const pyprojectPath = path.join(process.cwd(), "pyproject.toml");
  const hasPyproject = await fileExists(pyprojectPath);

  try {
    // Run Bandit with JSON output
    // NOTE: Bandit exits non-zero when findings are present
    const args = ["-r", targetPath, "-f", "json"];

    // Only add -c flag if pyproject.toml exists
    if (hasPyproject) {
      args.push("-c", pyprojectPath);
    }

    const { stdout } = await execCommand("bandit", args);

    const banditData = safeJsonParse(stdout, {
      fallback: { results: [] },
      label: "bandit output",
    });

    // Bandit format: { results: [ {issue_text, issue_severity, issue_confidence, test_id, filename, line_number, ...} ] }
    if (banditData && typeof banditData === "object" && "results" in banditData) {
      const results = Array.isArray(banditData.results) ? banditData.results : [];

      for (const result of results) {
        if (!result || typeof result !== "object") continue;

        const testId = String(result.test_id || "bandit-unknown");
        const filePath = String(result.filename || "unknown");
        const lineNumber = result.line_number || 0;
        const issueText = String(result.issue_text || "Security issue detected");
        const issueSeverity = String(result.issue_severity || "LOW");

        // Map Bandit severity (HIGH, MEDIUM, LOW) to normalized severity
        const severity = normalizeSeverity(issueSeverity);

        const vuln = {
          id: testId,
          source: "sast",
          severity,
          package: path.basename(filePath),
          version: `${filePath}:${lineNumber}`,
          fixed_version: "",
          title: issueText.slice(0, 150),
          description: issueText,
          references: [
            `https://bandit.readthedocs.io/en/latest/plugins/${testId.toLowerCase().replace(/_/g, '-')}.html`,
          ],
          discovered_at: getTimestamp(),
        };

        vulnerabilities.push(vuln);
      }
    }
  } catch (error) {
    if (error instanceof Error) {
      process.stderr.write(`[bandit] Warning: ${error.message}\n`);
    }
    // Continue with partial results
  }

  return vulnerabilities;
}

/**
 * Main entry point.
 */
async function main() {
  try {
    const args = parseArgs(process.argv.slice(2));

    // Verify target path exists
    const targetExists = await fileExists(args.target);
    if (!targetExists) {
      throw new Error(`Target path does not exist: ${args.target}`);
    }

    // Run SAST tools
    const semgrepVulns = await runSemgrep(args.target);
    const banditVulns = await runBandit(args.target);

    // Combine all vulnerabilities
    const allVulnerabilities = [...semgrepVulns, ...banditVulns];

    // Generate unified report
    const report = generateReport(allVulnerabilities, args.target);

    // Output report
    if (args.format === "json") {
      process.stdout.write(formatReportJson(report));
      process.stdout.write("\n");
    } else {
      process.stdout.write(formatReportText(report));
    }

    // Exit 0 even if vulnerabilities found (advisory only)
    process.exit(0);
  } catch (error) {
    if (error instanceof Error) {
      process.stderr.write(`Error: ${error.message}\n`);
    }
    process.exit(1);
  }
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
