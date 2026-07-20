#!/usr/bin/env node

/**
 * Dependency scanner tests for clawsec-scanner.
 *
 * Tests cover:
 * - Utility functions (normalizeSeverity, safeJsonParse, commandExists)
 * - Report generation and formatting
 * - Argument parsing
 * - Integration with temp directory setup
 *
 * Run: node skills/clawsec-scanner/test/dependency_scanner.test.mjs
 */

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { pass, fail, report, exitWithResults, createTempDir } from "./lib/test_harness.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LIB_PATH = path.resolve(__dirname, "..", "lib");

// Dynamic import to ensure we test the actual modules
const { normalizeSeverity, safeJsonParse, getTimestamp, generateUuid, commandExists } =
  await import(`${LIB_PATH}/utils.mjs`);
const { generateReport, formatReportJson, formatReportText } = await import(
  `${LIB_PATH}/report.mjs`
);

// -----------------------------------------------------------------------------
// Test: normalizeSeverity - critical variations
// -----------------------------------------------------------------------------
async function testNormalizeSeverity_Critical() {
  const testName = "normalizeSeverity: recognizes critical";
  try {
    const test1 = normalizeSeverity("critical");
    const test2 = normalizeSeverity("CRITICAL");
    const test3 = normalizeSeverity("  Critical  ");

    if (test1 === "critical" && test2 === "critical" && test3 === "critical") {
      pass(testName);
    } else {
      fail(testName, `Expected 'critical', got ${test1}, ${test2}, ${test3}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: normalizeSeverity - high variations
// -----------------------------------------------------------------------------
async function testNormalizeSeverity_High() {
  const testName = "normalizeSeverity: recognizes high";
  try {
    const test1 = normalizeSeverity("high");
    const test2 = normalizeSeverity("HIGH");

    if (test1 === "high" && test2 === "high") {
      pass(testName);
    } else {
      fail(testName, `Expected 'high', got ${test1}, ${test2}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: normalizeSeverity - medium variations (moderate, medium)
// -----------------------------------------------------------------------------
async function testNormalizeSeverity_Medium() {
  const testName = "normalizeSeverity: recognizes medium/moderate";
  try {
    const test1 = normalizeSeverity("medium");
    const test2 = normalizeSeverity("moderate");
    const test3 = normalizeSeverity("MODERATE");

    if (test1 === "medium" && test2 === "medium" && test3 === "medium") {
      pass(testName);
    } else {
      fail(testName, `Expected 'medium', got ${test1}, ${test2}, ${test3}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: normalizeSeverity - low variations
// -----------------------------------------------------------------------------
async function testNormalizeSeverity_Low() {
  const testName = "normalizeSeverity: recognizes low";
  try {
    const test1 = normalizeSeverity("low");
    const test2 = normalizeSeverity("LOW");

    if (test1 === "low" && test2 === "low") {
      pass(testName);
    } else {
      fail(testName, `Expected 'low', got ${test1}, ${test2}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: normalizeSeverity - defaults to info for unknown
// -----------------------------------------------------------------------------
async function testNormalizeSeverity_Unknown() {
  const testName = "normalizeSeverity: defaults to info for unknown";
  try {
    const test1 = normalizeSeverity("unknown");
    const test2 = normalizeSeverity("");
    const test3 = normalizeSeverity("garbage");

    if (test1 === "info" && test2 === "info" && test3 === "info") {
      pass(testName);
    } else {
      fail(testName, `Expected 'info', got ${test1}, ${test2}, ${test3}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: safeJsonParse - valid JSON
// -----------------------------------------------------------------------------
async function testSafeJsonParse_Valid() {
  const testName = "safeJsonParse: parses valid JSON";
  try {
    const json = '{"foo": "bar", "num": 42}';
    const result = safeJsonParse(json);

    if (
      result &&
      typeof result === "object" &&
      result.foo === "bar" &&
      result.num === 42
    ) {
      pass(testName);
    } else {
      fail(testName, `Unexpected result: ${JSON.stringify(result)}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: safeJsonParse - invalid JSON returns fallback
// -----------------------------------------------------------------------------
async function testSafeJsonParse_Invalid() {
  const testName = "safeJsonParse: returns fallback for invalid JSON";
  try {
    const invalid = "{not valid json}";
    const fallback = { error: true };
    const result = safeJsonParse(invalid, { fallback });

    if (result && result.error === true) {
      pass(testName);
    } else {
      fail(testName, `Expected fallback object, got ${JSON.stringify(result)}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: safeJsonParse - empty string returns fallback
// -----------------------------------------------------------------------------
async function testSafeJsonParse_Empty() {
  const testName = "safeJsonParse: returns fallback for empty string";
  try {
    const result = safeJsonParse("", { fallback: null });

    if (result === null) {
      pass(testName);
    } else {
      fail(testName, `Expected null, got ${JSON.stringify(result)}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: getTimestamp - returns ISO 8601 format
// -----------------------------------------------------------------------------
async function testGetTimestamp() {
  const testName = "getTimestamp: returns ISO 8601 format";
  try {
    const timestamp = getTimestamp();
    const iso8601Pattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;

    if (iso8601Pattern.test(timestamp)) {
      pass(testName);
    } else {
      fail(testName, `Expected ISO 8601 format, got ${timestamp}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: generateUuid - returns valid UUID v4 format
// -----------------------------------------------------------------------------
async function testGenerateUuid() {
  const testName = "generateUuid: returns valid UUID v4 format";
  try {
    const uuid = generateUuid();
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

    if (uuidPattern.test(uuid)) {
      pass(testName);
    } else {
      fail(testName, `Expected UUID v4 format, got ${uuid}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: generateUuid - generates unique IDs
// -----------------------------------------------------------------------------
async function testGenerateUuid_Unique() {
  const testName = "generateUuid: generates unique IDs";
  try {
    const uuid1 = generateUuid();
    const uuid2 = generateUuid();
    const uuid3 = generateUuid();

    if (uuid1 !== uuid2 && uuid2 !== uuid3 && uuid1 !== uuid3) {
      pass(testName);
    } else {
      fail(testName, `Expected unique UUIDs, got ${uuid1}, ${uuid2}, ${uuid3}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: generateReport - empty vulnerabilities
// -----------------------------------------------------------------------------
async function testGenerateReport_Empty() {
  const testName = "generateReport: handles empty vulnerabilities";
  try {
    const report = generateReport([], "/test/path");

    if (
      report &&
      report.vulnerabilities.length === 0 &&
      report.summary.critical === 0 &&
      report.summary.high === 0 &&
      report.summary.medium === 0 &&
      report.summary.low === 0 &&
      report.summary.info === 0 &&
      report.target === "/test/path"
    ) {
      pass(testName);
    } else {
      fail(testName, `Unexpected report structure: ${JSON.stringify(report)}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: generateReport - counts vulnerabilities by severity
// -----------------------------------------------------------------------------
async function testGenerateReport_Counts() {
  const testName = "generateReport: counts vulnerabilities by severity";
  try {
    const vulnerabilities = [
      {
        id: "TEST-001",
        source: "test",
        severity: "critical",
        package: "test-pkg",
        version: "1.0.0",
        fixed_version: "1.1.0",
        title: "Test Critical",
        description: "Test",
        references: [],
        discovered_at: "2026-01-01T00:00:00.000Z",
      },
      {
        id: "TEST-002",
        source: "test",
        severity: "high",
        package: "test-pkg",
        version: "1.0.0",
        fixed_version: "1.1.0",
        title: "Test High",
        description: "Test",
        references: [],
        discovered_at: "2026-01-01T00:00:00.000Z",
      },
      {
        id: "TEST-003",
        source: "test",
        severity: "high",
        package: "test-pkg-2",
        version: "2.0.0",
        fixed_version: "2.1.0",
        title: "Test High 2",
        description: "Test",
        references: [],
        discovered_at: "2026-01-01T00:00:00.000Z",
      },
      {
        id: "TEST-004",
        source: "test",
        severity: "medium",
        package: "test-pkg-3",
        version: "3.0.0",
        fixed_version: "3.1.0",
        title: "Test Medium",
        description: "Test",
        references: [],
        discovered_at: "2026-01-01T00:00:00.000Z",
      },
    ];

    const report = generateReport(vulnerabilities, ".");

    if (
      report.summary.critical === 1 &&
      report.summary.high === 2 &&
      report.summary.medium === 1 &&
      report.summary.low === 0 &&
      report.summary.info === 0 &&
      report.vulnerabilities.length === 4
    ) {
      pass(testName);
    } else {
      fail(testName, `Unexpected counts: ${JSON.stringify(report.summary)}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: formatReportJson - produces valid JSON
// -----------------------------------------------------------------------------
async function testFormatReportJson() {
  const testName = "formatReportJson: produces valid JSON";
  try {
    const report = generateReport([], "/test/path");
    const jsonString = formatReportJson(report);
    const parsed = JSON.parse(jsonString);

    if (parsed && parsed.target === "/test/path" && Array.isArray(parsed.vulnerabilities)) {
      pass(testName);
    } else {
      fail(testName, `Invalid JSON structure: ${jsonString}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: formatReportText - produces text output
// -----------------------------------------------------------------------------
async function testFormatReportText() {
  const testName = "formatReportText: produces text output";
  try {
    const report = generateReport([], "/test/path");
    const text = formatReportText(report);

    if (
      text.includes("VULNERABILITY SCAN REPORT") &&
      text.includes("Target:    /test/path") &&
      text.includes("No vulnerabilities detected")
    ) {
      pass(testName);
    } else {
      fail(testName, "Missing expected text output sections");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: formatReportText - includes vulnerability details
// -----------------------------------------------------------------------------
async function testFormatReportText_WithVulnerabilities() {
  const testName = "formatReportText: includes vulnerability details";
  try {
    const vulnerabilities = [
      {
        id: "CVE-2026-1234",
        source: "npm-audit",
        severity: "high",
        package: "test-package",
        version: "1.0.0",
        fixed_version: "1.1.0",
        title: "Test Vulnerability",
        description: "This is a test vulnerability description",
        references: ["https://example.com/cve-2026-1234"],
        discovered_at: "2026-01-01T00:00:00.000Z",
      },
    ];

    const report = generateReport(vulnerabilities, ".");
    const text = formatReportText(report);

    if (
      text.includes("CVE-2026-1234") &&
      text.includes("test-package") &&
      text.includes("1.0.0") &&
      text.includes("1.1.0") &&
      text.includes("Test Vulnerability") &&
      text.includes("HIGH")
    ) {
      pass(testName);
    } else {
      fail(testName, "Missing expected vulnerability details in text output");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: commandExists - detects existing command
// -----------------------------------------------------------------------------
async function testCommandExists_Found() {
  const testName = "commandExists: detects existing command (node)";
  try {
    // 'node' should always exist in the test environment
    const result = await commandExists("node");

    if (result === true) {
      pass(testName);
    } else {
      fail(testName, "Expected true for 'node' command");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: commandExists - returns false for non-existent command
// -----------------------------------------------------------------------------
async function testCommandExists_NotFound() {
  const testName = "commandExists: returns false for non-existent command";
  try {
    // Use a command that definitely doesn't exist
    const result = await commandExists("definitely-not-a-real-command-12345");

    if (result === false) {
      pass(testName);
    } else {
      fail(testName, "Expected false for non-existent command");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Report structure - has required fields
// -----------------------------------------------------------------------------
async function testReportStructure() {
  const testName = "Report structure: has all required fields";
  try {
    const report = generateReport([], ".");

    const hasAllFields =
      "scan_id" in report &&
      "timestamp" in report &&
      "target" in report &&
      "vulnerabilities" in report &&
      "summary" in report &&
      "critical" in report.summary &&
      "high" in report.summary &&
      "medium" in report.summary &&
      "low" in report.summary &&
      "info" in report.summary;

    if (hasAllFields) {
      pass(testName);
    } else {
      fail(testName, `Missing required fields in report: ${JSON.stringify(report)}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Temp directory creation
// -----------------------------------------------------------------------------
async function testTempDirCreation() {
  const testName = "createTempDir: creates and cleans up temp directory";
  try {
    const { path: tmpPath, cleanup } = await createTempDir();

    // Verify directory exists
    const stat = await fs.stat(tmpPath);
    if (!stat.isDirectory()) {
      fail(testName, "Created path is not a directory");
      return;
    }

    // Create a test file
    const testFilePath = path.join(tmpPath, "test.txt");
    await fs.writeFile(testFilePath, "test content");

    // Verify file exists
    const fileExists = await fs
      .access(testFilePath)
      .then(() => true)
      .catch(() => false);

    if (!fileExists) {
      fail(testName, "Test file was not created");
      return;
    }

    // Cleanup
    await cleanup();

    // Verify cleanup
    const dirExists = await fs
      .access(tmpPath)
      .then(() => true)
      .catch(() => false);

    if (dirExists) {
      fail(testName, "Temp directory was not cleaned up");
    } else {
      pass(testName);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Main test runner
// -----------------------------------------------------------------------------
async function main() {
  console.log("Running dependency scanner tests...\n");

  // Utility function tests
  await testNormalizeSeverity_Critical();
  await testNormalizeSeverity_High();
  await testNormalizeSeverity_Medium();
  await testNormalizeSeverity_Low();
  await testNormalizeSeverity_Unknown();

  await testSafeJsonParse_Valid();
  await testSafeJsonParse_Invalid();
  await testSafeJsonParse_Empty();

  await testGetTimestamp();
  await testGenerateUuid();
  await testGenerateUuid_Unique();

  await testCommandExists_Found();
  await testCommandExists_NotFound();

  // Report generation tests
  await testGenerateReport_Empty();
  await testGenerateReport_Counts();
  await testReportStructure();

  // Report formatting tests
  await testFormatReportJson();
  await testFormatReportText();
  await testFormatReportText_WithVulnerabilities();

  // Infrastructure tests
  await testTempDirCreation();

  // Final report
  report();
  exitWithResults();
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
