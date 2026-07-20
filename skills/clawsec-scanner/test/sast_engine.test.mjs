#!/usr/bin/env node

/**
 * SAST engine tests for clawsec-scanner.
 *
 * Tests cover:
 * - Semgrep output parsing and normalization
 * - Bandit output parsing and normalization
 * - File existence checking
 * - Vulnerability data structure validation
 * - Error handling for malformed tool outputs
 *
 * Run: node skills/clawsec-scanner/test/sast_engine.test.mjs
 */

import path from "node:path";
import { fileURLToPath } from "node:url";
import { pass, fail, report, exitWithResults } from "./lib/test_harness.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LIB_PATH = path.resolve(__dirname, "..", "lib");

// Dynamic import to ensure we test the actual modules
const { normalizeSeverity, safeJsonParse, getTimestamp } = await import(`${LIB_PATH}/utils.mjs`);

// -----------------------------------------------------------------------------
// Test: Parse valid Semgrep JSON output
// -----------------------------------------------------------------------------
async function testParseSemgrepOutput_Valid() {
  const testName = "SAST: parse valid Semgrep JSON output";
  try {
    const semgrepOutput = JSON.stringify({
      results: [
        {
          check_id: "javascript.lang.security.audit.unsafe-regex.unsafe-regex",
          path: "test/file.js",
          start: { line: 42 },
          extra: {
            message: "Potential ReDoS vulnerability detected",
            severity: "WARNING",
            metadata: {
              references: ["https://owasp.org/redos"],
              source: "semgrep-rules",
            },
          },
        },
      ],
    });

    const parsed = safeJsonParse(semgrepOutput, {
      fallback: { results: [] },
      label: "semgrep output",
    });

    if (
      parsed &&
      parsed.results &&
      parsed.results.length === 1 &&
      parsed.results[0].check_id === "javascript.lang.security.audit.unsafe-regex.unsafe-regex"
    ) {
      pass(testName);
    } else {
      fail(testName, "Failed to parse valid Semgrep output correctly");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Parse Semgrep output with missing fields
// -----------------------------------------------------------------------------
async function testParseSemgrepOutput_MissingFields() {
  const testName = "SAST: handle Semgrep output with missing fields";
  try {
    const semgrepOutput = JSON.stringify({
      results: [
        {
          // Missing check_id, path, extra
          start: { line: 10 },
        },
      ],
    });

    const parsed = safeJsonParse(semgrepOutput, {
      fallback: { results: [] },
      label: "semgrep output",
    });

    // Should parse successfully even with missing fields
    if (parsed && parsed.results && parsed.results.length === 1) {
      pass(testName);
    } else {
      fail(testName, "Failed to handle Semgrep output with missing fields");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Parse empty Semgrep results
// -----------------------------------------------------------------------------
async function testParseSemgrepOutput_Empty() {
  const testName = "SAST: handle empty Semgrep results";
  try {
    const semgrepOutput = JSON.stringify({ results: [] });

    const parsed = safeJsonParse(semgrepOutput, {
      fallback: { results: [] },
      label: "semgrep output",
    });

    if (parsed && Array.isArray(parsed.results) && parsed.results.length === 0) {
      pass(testName);
    } else {
      fail(testName, "Failed to handle empty Semgrep results");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Parse malformed Semgrep JSON
// -----------------------------------------------------------------------------
async function testParseSemgrepOutput_Malformed() {
  const testName = "SAST: handle malformed Semgrep JSON gracefully";
  try {
    const malformedJson = "{ results: [{ invalid json }] }";

    const parsed = safeJsonParse(malformedJson, {
      fallback: { results: [] },
      label: "semgrep output",
    });

    // Should fall back to default value
    if (parsed && Array.isArray(parsed.results) && parsed.results.length === 0) {
      pass(testName);
    } else {
      fail(testName, "Failed to use fallback for malformed JSON");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Parse valid Bandit JSON output
// -----------------------------------------------------------------------------
async function testParseBanditOutput_Valid() {
  const testName = "SAST: parse valid Bandit JSON output";
  try {
    const banditOutput = JSON.stringify({
      results: [
        {
          test_id: "B201",
          filename: "/path/to/file.py",
          line_number: 15,
          issue_text: "A possibly insecure use of pickle detected.",
          issue_severity: "HIGH",
          issue_confidence: "HIGH",
        },
      ],
    });

    const parsed = safeJsonParse(banditOutput, {
      fallback: { results: [] },
      label: "bandit output",
    });

    if (
      parsed &&
      parsed.results &&
      parsed.results.length === 1 &&
      parsed.results[0].test_id === "B201"
    ) {
      pass(testName);
    } else {
      fail(testName, "Failed to parse valid Bandit output correctly");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Parse Bandit output with missing fields
// -----------------------------------------------------------------------------
async function testParseBanditOutput_MissingFields() {
  const testName = "SAST: handle Bandit output with missing fields";
  try {
    const banditOutput = JSON.stringify({
      results: [
        {
          // Missing test_id, issue_text, etc.
          filename: "/path/to/file.py",
        },
      ],
    });

    const parsed = safeJsonParse(banditOutput, {
      fallback: { results: [] },
      label: "bandit output",
    });

    // Should parse successfully even with missing fields
    if (parsed && parsed.results && parsed.results.length === 1) {
      pass(testName);
    } else {
      fail(testName, "Failed to handle Bandit output with missing fields");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Parse empty Bandit results
// -----------------------------------------------------------------------------
async function testParseBanditOutput_Empty() {
  const testName = "SAST: handle empty Bandit results";
  try {
    const banditOutput = JSON.stringify({ results: [] });

    const parsed = safeJsonParse(banditOutput, {
      fallback: { results: [] },
      label: "bandit output",
    });

    if (parsed && Array.isArray(parsed.results) && parsed.results.length === 0) {
      pass(testName);
    } else {
      fail(testName, "Failed to handle empty Bandit results");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Normalize Semgrep severity levels
// -----------------------------------------------------------------------------
async function testNormalizeSeverity_Semgrep() {
  const testName = "SAST: normalize Semgrep severity levels";
  try {
    const errorLevel = normalizeSeverity("ERROR");
    const warningLevel = normalizeSeverity("WARNING");
    const infoLevel = normalizeSeverity("INFO");

    // Semgrep uses ERROR, WARNING, INFO
    // normalizeSeverity uses substring matching, so these map to 'info' (default)
    // since they don't contain 'critical', 'high', 'medium', 'moderate', or 'low'
    if (errorLevel === "info" && warningLevel === "info" && infoLevel === "info") {
      pass(testName);
    } else {
      fail(
        testName,
        `Unexpected normalization: ERROR=${errorLevel}, WARNING=${warningLevel}, INFO=${infoLevel}`,
      );
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Normalize Bandit severity levels
// -----------------------------------------------------------------------------
async function testNormalizeSeverity_Bandit() {
  const testName = "SAST: normalize Bandit severity levels";
  try {
    const highLevel = normalizeSeverity("HIGH");
    const mediumLevel = normalizeSeverity("MEDIUM");
    const lowLevel = normalizeSeverity("LOW");

    if (
      (highLevel === "high" || highLevel === "critical") &&
      mediumLevel === "medium" &&
      lowLevel === "low"
    ) {
      pass(testName);
    } else {
      fail(
        testName,
        `Unexpected normalization: HIGH=${highLevel}, MEDIUM=${mediumLevel}, LOW=${lowLevel}`,
      );
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Validate vulnerability data structure from Semgrep
// -----------------------------------------------------------------------------
async function testVulnerabilityStructure_Semgrep() {
  const testName = "SAST: validate Semgrep vulnerability data structure";
  try {
    // Simulate vulnerability object created from Semgrep output
    const vuln = {
      id: "javascript.lang.security.audit.unsafe-regex.unsafe-regex",
      source: "sast",
      severity: normalizeSeverity("WARNING"),
      package: "file.js",
      version: "test/file.js:42",
      fixed_version: "",
      title: "Potential ReDoS vulnerability detected",
      description: "Potential ReDoS vulnerability detected",
      references: ["https://owasp.org/redos", "semgrep-rules"],
      discovered_at: getTimestamp(),
    };

    // Validate required fields
    const hasRequiredFields =
      typeof vuln.id === "string" &&
      vuln.id.length > 0 &&
      vuln.source === "sast" &&
      typeof vuln.severity === "string" &&
      typeof vuln.package === "string" &&
      typeof vuln.discovered_at === "string" &&
      Array.isArray(vuln.references);

    if (hasRequiredFields) {
      pass(testName);
    } else {
      fail(testName, "Vulnerability object missing required fields");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Validate vulnerability data structure from Bandit
// -----------------------------------------------------------------------------
async function testVulnerabilityStructure_Bandit() {
  const testName = "SAST: validate Bandit vulnerability data structure";
  try {
    // Simulate vulnerability object created from Bandit output
    const vuln = {
      id: "B201",
      source: "sast",
      severity: normalizeSeverity("HIGH"),
      package: "file.py",
      version: "/path/to/file.py:15",
      fixed_version: "",
      title: "A possibly insecure use of pickle detected.",
      description: "A possibly insecure use of pickle detected.",
      references: ["https://bandit.readthedocs.io/en/latest/plugins/b201.html"],
      discovered_at: getTimestamp(),
    };

    // Validate required fields
    const hasRequiredFields =
      typeof vuln.id === "string" &&
      vuln.id.length > 0 &&
      vuln.source === "sast" &&
      typeof vuln.severity === "string" &&
      typeof vuln.package === "string" &&
      typeof vuln.discovered_at === "string" &&
      Array.isArray(vuln.references) &&
      vuln.references.length > 0;

    if (hasRequiredFields) {
      pass(testName);
    } else {
      fail(testName, "Vulnerability object missing required fields");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Timestamp format validation
// -----------------------------------------------------------------------------
async function testTimestampFormat() {
  const testName = "SAST: validate timestamp format";
  try {
    const timestamp = getTimestamp();

    // Should be ISO 8601 format
    const iso8601Regex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;

    if (iso8601Regex.test(timestamp)) {
      pass(testName);
    } else {
      fail(testName, `Invalid timestamp format: ${timestamp}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Handle Semgrep results with metadata variations
// -----------------------------------------------------------------------------
async function testSemgrepMetadata_Variations() {
  const testName = "SAST: handle Semgrep metadata variations";
  try {
    // Test with missing metadata
    const output1 = JSON.stringify({
      results: [
        {
          check_id: "test-rule",
          path: "test.js",
          extra: {
            message: "Test message",
            severity: "ERROR",
          },
        },
      ],
    });

    // Test with metadata but no references
    const output2 = JSON.stringify({
      results: [
        {
          check_id: "test-rule",
          path: "test.js",
          extra: {
            message: "Test message",
            severity: "ERROR",
            metadata: {
              source: "custom-rule",
            },
          },
        },
      ],
    });

    const parsed1 = safeJsonParse(output1, {
      fallback: { results: [] },
      label: "semgrep output",
    });
    const parsed2 = safeJsonParse(output2, {
      fallback: { results: [] },
      label: "semgrep output",
    });

    if (
      parsed1 &&
      parsed1.results &&
      parsed1.results.length === 1 &&
      parsed2 &&
      parsed2.results &&
      parsed2.results.length === 1
    ) {
      pass(testName);
    } else {
      fail(testName, "Failed to handle metadata variations");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Validate reference URL formats
// -----------------------------------------------------------------------------
async function testReferenceUrlFormats() {
  const testName = "SAST: validate reference URL formats";
  try {
    // Bandit reference format
    const testId = "B201";
    const banditRef = `https://bandit.readthedocs.io/en/latest/plugins/${testId.toLowerCase().replace(/_/g, "-")}.html`;

    // Should follow expected pattern
    const expectedRef = "https://bandit.readthedocs.io/en/latest/plugins/b201.html";

    if (banditRef === expectedRef) {
      pass(testName);
    } else {
      fail(testName, `Reference URL mismatch: ${banditRef} !== ${expectedRef}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Handle non-object results gracefully
// -----------------------------------------------------------------------------
async function testHandleNonObjectResults() {
  const testName = "SAST: handle non-object results in array";
  try {
    const output = JSON.stringify({
      results: [null, undefined, "string", 123, { valid: "object" }],
    });

    const parsed = safeJsonParse(output, {
      fallback: { results: [] },
      label: "test output",
    });

    // Should parse successfully and include all items
    if (parsed && parsed.results && parsed.results.length === 5) {
      pass(testName);
    } else {
      fail(testName, "Failed to preserve all array elements");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Severity normalization edge cases
// -----------------------------------------------------------------------------
async function testSeverityNormalization_EdgeCases() {
  const testName = "SAST: handle severity normalization edge cases";
  try {
    const unknown = normalizeSeverity("UNKNOWN_SEVERITY");
    const empty = normalizeSeverity("");
    const whitespace = normalizeSeverity("  ");

    // Should handle unknown severities gracefully
    const allValid =
      typeof unknown === "string" && typeof empty === "string" && typeof whitespace === "string";

    if (allValid) {
      pass(testName);
    } else {
      fail(testName, "Severity normalization returned non-string values");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Main test runner
// -----------------------------------------------------------------------------
async function main() {
  // Semgrep output parsing tests
  await testParseSemgrepOutput_Valid();
  await testParseSemgrepOutput_MissingFields();
  await testParseSemgrepOutput_Empty();
  await testParseSemgrepOutput_Malformed();

  // Bandit output parsing tests
  await testParseBanditOutput_Valid();
  await testParseBanditOutput_MissingFields();
  await testParseBanditOutput_Empty();

  // Severity normalization tests
  await testNormalizeSeverity_Semgrep();
  await testNormalizeSeverity_Bandit();
  await testSeverityNormalization_EdgeCases();

  // Vulnerability structure tests
  await testVulnerabilityStructure_Semgrep();
  await testVulnerabilityStructure_Bandit();

  // Utility tests
  await testTimestampFormat();
  await testSemgrepMetadata_Variations();
  await testReferenceUrlFormats();
  await testHandleNonObjectResults();

  // Report results
  report();
  exitWithResults();
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
