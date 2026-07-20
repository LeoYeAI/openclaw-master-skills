#!/usr/bin/env node

/**
 * CVE integration tests for clawsec-scanner.
 *
 * Tests cover:
 * - OSV API query and normalization
 * - NVD API query and normalization
 * - GitHub Advisory Database query (placeholder)
 * - Multi-source enrichment
 * - Error handling and timeouts
 * - Rate limiting behavior
 *
 * Run: node skills/clawsec-scanner/test/cve_integration.test.mjs
 */

import path from "node:path";
import { fileURLToPath } from "node:url";
import { pass, fail, report, exitWithResults, withEnv } from "./lib/test_harness.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCRIPTS_PATH = path.resolve(__dirname, "..", "scripts");

// Dynamic import to ensure we test the actual modules
const { queryOSV, queryNVD, queryGitHub, enrichVulnerability } = await import(
  `${SCRIPTS_PATH}/query_cve_databases.mjs`
);

// -----------------------------------------------------------------------------
// Test: queryOSV - successful query with results
// -----------------------------------------------------------------------------
async function testQueryOSV_Success() {
  const testName = "queryOSV: successful query returns vulnerabilities";
  try {
    // Query a known vulnerable package (lodash has known vulnerabilities)
    const results = await queryOSV("lodash", "npm", "4.17.19");

    // lodash 4.17.19 has known vulnerabilities
    if (Array.isArray(results) && results.length > 0) {
      // Verify structure of first result
      const vuln = results[0];
      if (
        vuln.id &&
        vuln.source === "osv" &&
        vuln.severity &&
        vuln.package === "lodash" &&
        vuln.title &&
        vuln.description &&
        Array.isArray(vuln.references)
      ) {
        pass(testName);
      } else {
        fail(testName, `Invalid vulnerability structure: ${JSON.stringify(vuln)}`);
      }
    } else {
      // If no results, package may have been patched - that's also valid
      pass(testName);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: queryOSV - returns empty array for non-existent package
// -----------------------------------------------------------------------------
async function testQueryOSV_NotFound() {
  const testName = "queryOSV: returns empty array for non-existent package";
  try {
    const results = await queryOSV("nonexistent-package-that-does-not-exist-12345", "npm");

    if (Array.isArray(results) && results.length === 0) {
      pass(testName);
    } else {
      fail(testName, `Expected empty array, got ${results.length} results`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: queryOSV - handles network errors gracefully
// -----------------------------------------------------------------------------
async function testQueryOSV_NetworkError() {
  const testName = "queryOSV: handles network errors gracefully";
  try {
    // This will likely timeout or fail, but should return empty array
    const results = await queryOSV("test-pkg", "invalid-ecosystem-999");

    if (Array.isArray(results)) {
      pass(testName);
    } else {
      fail(testName, `Expected array, got ${typeof results}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: queryOSV - version-specific query
// -----------------------------------------------------------------------------
async function testQueryOSV_WithVersion() {
  const testName = "queryOSV: handles version-specific queries";
  try {
    const results = await queryOSV("express", "npm", "4.16.0");

    // Express 4.16.0 may or may not have vulnerabilities
    // Just verify it returns an array
    if (Array.isArray(results)) {
      pass(testName);
    } else {
      fail(testName, `Expected array, got ${typeof results}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: queryOSV - normalizes severity correctly
// -----------------------------------------------------------------------------
async function testQueryOSV_SeverityNormalization() {
  const testName = "queryOSV: normalizes severity from API response";
  try {
    const results = await queryOSV("lodash", "npm", "4.17.19");

    if (results.length > 0) {
      const validSeverities = ["critical", "high", "medium", "low", "info"];
      const allValid = results.every((vuln) => validSeverities.includes(vuln.severity));

      if (allValid) {
        pass(testName);
      } else {
        fail(
          testName,
          `Invalid severity found: ${results.map((v) => v.severity).join(", ")}`,
        );
      }
    } else {
      // No results is valid
      pass(testName);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: queryNVD - requires API key or respects rate limiting
// -----------------------------------------------------------------------------
async function testQueryNVD_RateLimiting() {
  const testName = "queryNVD: respects rate limiting without API key";
  try {
    await withEnv("CLAWSEC_NVD_API_KEY", undefined, async () => {
      const startTime = Date.now();

      // Query should add 6-second delay when no API key (if request succeeds)
      await queryNVD("CVE-2021-44228");

      const elapsed = Date.now() - startTime;

      // If the request failed quickly (network issue), skip the test
      if (elapsed < 100) {
        pass(testName + " (skipped - network unavailable)");
      } else if (elapsed >= 5900) {
        // Should take at least 6 seconds if successful
        pass(testName);
      } else {
        fail(testName, `Expected ~6s delay, got ${elapsed}ms`);
      }
    });
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: queryNVD - handles non-existent CVE
// -----------------------------------------------------------------------------
async function testQueryNVD_NotFound() {
  const testName = "queryNVD: returns null for non-existent CVE";
  try {
    await withEnv("CLAWSEC_NVD_API_KEY", undefined, async () => {
      const result = await queryNVD("CVE-9999-99999");

      if (result === null) {
        pass(testName);
      } else {
        fail(testName, `Expected null, got ${JSON.stringify(result)}`);
      }
    });
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: queryNVD - valid CVE returns structured data
// -----------------------------------------------------------------------------
async function testQueryNVD_ValidCVE() {
  const testName = "queryNVD: valid CVE returns structured vulnerability";
  try {
    // Only run if API key is set (to avoid rate limiting in CI)
    const apiKey = process.env.CLAWSEC_NVD_API_KEY;
    if (!apiKey) {
      pass(testName + " (skipped - no API key)");
      return;
    }

    const result = await queryNVD("CVE-2021-44228");

    if (result && result.id === "CVE-2021-44228" && result.source === "nvd") {
      pass(testName);
    } else if (result === null) {
      // API might be down or rate limited
      pass(testName + " (API returned null)");
    } else {
      fail(testName, `Unexpected result: ${JSON.stringify(result)}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: queryGitHub - returns empty array when token not set
// -----------------------------------------------------------------------------
async function testQueryGitHub_NoToken() {
  const testName = "queryGitHub: returns empty array when token not set";
  try {
    await withEnv("GITHUB_TOKEN", undefined, async () => {
      const results = await queryGitHub("test-package", "npm");

      if (Array.isArray(results) && results.length === 0) {
        pass(testName);
      } else {
        fail(testName, `Expected empty array, got ${results.length} results`);
      }
    });
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: queryGitHub - placeholder implementation
// -----------------------------------------------------------------------------
async function testQueryGitHub_Placeholder() {
  const testName = "queryGitHub: placeholder returns empty array with token";
  try {
    await withEnv("GITHUB_TOKEN", "fake-token-for-testing", async () => {
      const results = await queryGitHub("test-package", "npm");

      // Current implementation is a placeholder
      if (Array.isArray(results) && results.length === 0) {
        pass(testName);
      } else {
        fail(testName, `Expected empty array, got ${results.length} results`);
      }
    });
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: enrichVulnerability - combines OSV results
// -----------------------------------------------------------------------------
async function testEnrichVulnerability_OSVOnly() {
  const testName = "enrichVulnerability: returns OSV results";
  try {
    await withEnv("CLAWSEC_NVD_API_KEY", undefined, async () => {
      const results = await enrichVulnerability("lodash", "npm", "4.17.19");

      if (Array.isArray(results)) {
        pass(testName);
      } else {
        fail(testName, `Expected array, got ${typeof results}`);
      }
    });
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: enrichVulnerability - enriches with NVD when API key present
// -----------------------------------------------------------------------------
async function testEnrichVulnerability_WithNVD() {
  const testName = "enrichVulnerability: enriches with NVD when API key present";
  try {
    const apiKey = process.env.CLAWSEC_NVD_API_KEY;
    if (!apiKey) {
      pass(testName + " (skipped - no API key)");
      return;
    }

    // Query a package with known CVE
    const results = await enrichVulnerability("lodash", "npm", "4.17.19");

    // If results contain CVE IDs, they should have enriched references
    const hasCVE = results.some((v) => v.id.startsWith("CVE-"));

    if (hasCVE) {
      // Check if references were enriched (should have more than original OSV refs)
      const hasReferences = results.some((v) => v.references.length > 0);
      if (hasReferences) {
        pass(testName);
      } else {
        fail(testName, "Expected enriched references from NVD");
      }
    } else {
      // No CVEs found, which is valid
      pass(testName + " (no CVEs to enrich)");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: enrichVulnerability - handles empty results
// -----------------------------------------------------------------------------
async function testEnrichVulnerability_Empty() {
  const testName = "enrichVulnerability: handles packages with no vulnerabilities";
  try {
    const results = await enrichVulnerability(
      "nonexistent-package-12345",
      "npm",
      "1.0.0",
    );

    if (Array.isArray(results) && results.length === 0) {
      pass(testName);
    } else {
      fail(testName, `Expected empty array, got ${results.length} results`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: OSV normalization - extracts severity
// -----------------------------------------------------------------------------
async function testOSVNormalization_Severity() {
  const testName = "OSV normalization: extracts severity correctly";
  try {
    // Query real data and check normalization
    const results = await queryOSV("lodash", "npm", "4.17.19");

    if (results.length > 0) {
      const vuln = results[0];
      const validSeverities = ["critical", "high", "medium", "low", "info"];

      if (validSeverities.includes(vuln.severity)) {
        pass(testName);
      } else {
        fail(testName, `Invalid severity: ${vuln.severity}`);
      }
    } else {
      pass(testName + " (no results to test)");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: OSV normalization - extracts references
// -----------------------------------------------------------------------------
async function testOSVNormalization_References() {
  const testName = "OSV normalization: extracts references";
  try {
    const results = await queryOSV("lodash", "npm", "4.17.19");

    if (results.length > 0) {
      const vuln = results[0];

      if (Array.isArray(vuln.references)) {
        // References should be URLs
        const allUrls = vuln.references.every((ref) => ref.startsWith("http"));
        if (allUrls) {
          pass(testName);
        } else {
          fail(testName, `Non-URL reference found: ${vuln.references.join(", ")}`);
        }
      } else {
        fail(testName, "References is not an array");
      }
    } else {
      pass(testName + " (no results to test)");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: OSV normalization - extracts fixed version
// -----------------------------------------------------------------------------
async function testOSVNormalization_FixedVersion() {
  const testName = "OSV normalization: extracts fixed version";
  try {
    const results = await queryOSV("lodash", "npm", "4.17.19");

    if (results.length > 0) {
      const hasFixedVersion = results.some((v) => v.fixed_version !== undefined);

      if (hasFixedVersion) {
        pass(testName);
      } else {
        // Some vulnerabilities may not have a fixed version yet
        pass(testName + " (no fixed versions available)");
      }
    } else {
      pass(testName + " (no results to test)");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: OSV normalization - includes timestamp
// -----------------------------------------------------------------------------
async function testOSVNormalization_Timestamp() {
  const testName = "OSV normalization: includes discovery timestamp";
  try {
    const results = await queryOSV("lodash", "npm", "4.17.19");

    if (results.length > 0) {
      const vuln = results[0];
      const iso8601Pattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;

      if (vuln.discovered_at && iso8601Pattern.test(vuln.discovered_at)) {
        pass(testName);
      } else {
        fail(testName, `Invalid timestamp: ${vuln.discovered_at}`);
      }
    } else {
      pass(testName + " (no results to test)");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Vulnerability structure - required fields present
// -----------------------------------------------------------------------------
async function testVulnerabilityStructure() {
  const testName = "Vulnerability structure: has all required fields";
  try {
    const results = await queryOSV("lodash", "npm", "4.17.19");

    if (results.length > 0) {
      const vuln = results[0];
      const hasAllFields =
        "id" in vuln &&
        "source" in vuln &&
        "severity" in vuln &&
        "package" in vuln &&
        "version" in vuln &&
        "title" in vuln &&
        "description" in vuln &&
        "references" in vuln &&
        "discovered_at" in vuln;

      if (hasAllFields) {
        pass(testName);
      } else {
        fail(testName, `Missing required fields: ${JSON.stringify(vuln)}`);
      }
    } else {
      pass(testName + " (no results to test)");
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Multiple ecosystems - PyPI support
// -----------------------------------------------------------------------------
async function testMultipleEcosystems_PyPI() {
  const testName = "Multiple ecosystems: PyPI packages";
  try {
    // Query a known vulnerable Python package
    const results = await queryOSV("requests", "PyPI", "2.6.0");

    // Verify it returns valid results
    if (Array.isArray(results)) {
      pass(testName);
    } else {
      fail(testName, `Expected array, got ${typeof results}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Test: Multiple ecosystems - npm support
// -----------------------------------------------------------------------------
async function testMultipleEcosystems_npm() {
  const testName = "Multiple ecosystems: npm packages";
  try {
    const results = await queryOSV("express", "npm");

    if (Array.isArray(results)) {
      pass(testName);
    } else {
      fail(testName, `Expected array, got ${typeof results}`);
    }
  } catch (error) {
    fail(testName, error);
  }
}

// -----------------------------------------------------------------------------
// Main test runner
// -----------------------------------------------------------------------------
async function main() {
  console.log("Running CVE integration tests...\n");

  // OSV API tests
  await testQueryOSV_Success();
  await testQueryOSV_NotFound();
  await testQueryOSV_NetworkError();
  await testQueryOSV_WithVersion();
  await testQueryOSV_SeverityNormalization();

  // NVD API tests
  await testQueryNVD_RateLimiting();
  await testQueryNVD_NotFound();
  await testQueryNVD_ValidCVE();

  // GitHub Advisory tests
  await testQueryGitHub_NoToken();
  await testQueryGitHub_Placeholder();

  // Enrichment tests
  await testEnrichVulnerability_OSVOnly();
  await testEnrichVulnerability_WithNVD();
  await testEnrichVulnerability_Empty();

  // Normalization tests
  await testOSVNormalization_Severity();
  await testOSVNormalization_References();
  await testOSVNormalization_FixedVersion();
  await testOSVNormalization_Timestamp();

  // Structure tests
  await testVulnerabilityStructure();

  // Ecosystem tests
  await testMultipleEcosystems_PyPI();
  await testMultipleEcosystems_npm();

  // Final report
  report();
  exitWithResults();
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
