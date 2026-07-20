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
      "  node scripts/scan_dependencies.mjs --target <path> [--format json|text]",
      "",
      "Examples:",
      "  node scripts/scan_dependencies.mjs --target ./skills/clawsec-suite",
      "  node scripts/scan_dependencies.mjs --target ./skills/ --format json",
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
 * Run npm audit and parse vulnerabilities.
 *
 * @param {string} targetPath - Path to scan
 * @returns {Promise<Vulnerability[]>}
 */
async function scanNpmAudit(targetPath) {
  const vulnerabilities = [];

  // Check if package-lock.json exists
  const packageLockPath = path.join(targetPath, "package-lock.json");
  const hasPackageLock = await fileExists(packageLockPath);

  if (!hasPackageLock) {
    process.stderr.write(`[npm-audit] No package-lock.json found in ${targetPath}, skipping npm audit\n`);
    return vulnerabilities;
  }

  // Check if npm is available
  const hasNpm = await commandExists("npm");
  if (!hasNpm) {
    process.stderr.write("[npm-audit] npm command not found, skipping npm audit\n");
    return vulnerabilities;
  }

  try {
    // Run npm audit with JSON output
    // NOTE: npm audit exits non-zero when vulnerabilities are found
    const { stdout } = await execCommand("npm", ["audit", "--json"], { cwd: targetPath });

    const auditData = safeJsonParse(stdout, {
      fallback: { vulnerabilities: {} },
      label: "npm audit output",
    });

    // npm audit v7+ format: { vulnerabilities: { [package]: {...} } }
    if (auditData && typeof auditData === "object" && "vulnerabilities" in auditData) {
      const vulnsMap = auditData.vulnerabilities;

      if (vulnsMap && typeof vulnsMap === "object") {
        for (const [packageName, vulnData] of Object.entries(vulnsMap)) {
          if (!vulnData || typeof vulnData !== "object") continue;

          // Extract vulnerability data
          const severity = normalizeSeverity(vulnData.severity || "info");
          const version = String(vulnData.range || vulnData.version || "unknown");
          const via = Array.isArray(vulnData.via) ? vulnData.via : [];

          // npm audit can have multiple advisories via the 'via' field
          for (const viaItem of via) {
            if (typeof viaItem === "object" && viaItem !== null) {
              const vuln = {
                id: String(viaItem.source || viaItem.cve || `npm-${packageName}`),
                source: "npm-audit",
                severity,
                package: packageName,
                version,
                fixed_version: String(vulnData.fixAvailable?.version || ""),
                title: String(viaItem.title || `Vulnerability in ${packageName}`),
                description: String(viaItem.title || viaItem.name || "No description available"),
                references: viaItem.url ? [String(viaItem.url)] : [],
                discovered_at: getTimestamp(),
              };

              vulnerabilities.push(vuln);
            }
          }

          // If 'via' doesn't have objects, create a generic entry
          if (via.length === 0 || via.every((v) => typeof v !== "object")) {
            const vuln = {
              id: `npm-${packageName}`,
              source: "npm-audit",
              severity,
              package: packageName,
              version,
              fixed_version: String(vulnData.fixAvailable?.version || ""),
              title: `Vulnerability in ${packageName}`,
              description: String(vulnData.name || `Vulnerability detected in ${packageName}`),
              references: [],
              discovered_at: getTimestamp(),
            };

            vulnerabilities.push(vuln);
          }
        }
      }
    }
  } catch (error) {
    if (error instanceof Error) {
      process.stderr.write(`[npm-audit] Warning: ${error.message}\n`);
    }
    // Continue with partial results
  }

  return vulnerabilities;
}

/**
 * Run pip-audit and parse vulnerabilities.
 *
 * @param {string} targetPath - Path to scan
 * @returns {Promise<Vulnerability[]>}
 */
async function scanPipAudit(targetPath) {
  const vulnerabilities = [];

  // Check if pip-audit is available
  const hasPipAudit = await commandExists("pip-audit");
  if (!hasPipAudit) {
    process.stderr.write("[pip-audit] pip-audit command not found, skipping Python dependency scan\n");
    return vulnerabilities;
  }

  // Check if requirements.txt or setup.py exists
  const requirementsTxt = path.join(targetPath, "requirements.txt");
  const setupPy = path.join(targetPath, "setup.py");
  const pyprojectToml = path.join(targetPath, "pyproject.toml");

  const hasRequirements = await fileExists(requirementsTxt);
  const hasSetupPy = await fileExists(setupPy);
  const hasPyprojectToml = await fileExists(pyprojectToml);

  if (!hasRequirements && !hasSetupPy && !hasPyprojectToml) {
    process.stderr.write(
      `[pip-audit] No Python dependency files found in ${targetPath}, skipping pip-audit\n`,
    );
    return vulnerabilities;
  }

  try {
    // Prefer requirements.txt when present; otherwise scan project context in target dir.
    const pipAuditArgs = hasRequirements ? ["-f", "json", "-r", "requirements.txt"] : ["-f", "json"];
    const { stdout } = await execCommand("pip-audit", pipAuditArgs, { cwd: targetPath });

    const auditData = safeJsonParse(stdout, {
      fallback: { dependencies: [] },
      label: "pip-audit output",
    });

    // pip-audit format: { dependencies: [ {name, version, vulns: [{id, fix_versions, description, ...}]} ] }
    if (auditData && typeof auditData === "object" && "dependencies" in auditData) {
      const deps = Array.isArray(auditData.dependencies) ? auditData.dependencies : [];

      for (const dep of deps) {
        if (!dep || typeof dep !== "object") continue;

        const packageName = String(dep.name || "unknown");
        const version = String(dep.version || "unknown");
        const vulns = Array.isArray(dep.vulns) ? dep.vulns : [];

        for (const vulnData of vulns) {
          if (!vulnData || typeof vulnData !== "object") continue;

          const fixVersions = Array.isArray(vulnData.fix_versions) ? vulnData.fix_versions : [];
          const vuln = {
            id: String(vulnData.id || `pip-${packageName}`),
            source: "pip-audit",
            severity: normalizeSeverity(vulnData.severity || "info"),
            package: packageName,
            version,
            fixed_version: fixVersions.length > 0 ? String(fixVersions[0]) : "",
            title: String(vulnData.description || `Vulnerability in ${packageName}`).slice(0, 150),
            description: String(vulnData.description || "No description available"),
            references: vulnData.link ? [String(vulnData.link)] : [],
            discovered_at: getTimestamp(),
          };

          vulnerabilities.push(vuln);
        }
      }
    }
  } catch (error) {
    if (error instanceof Error) {
      process.stderr.write(`[pip-audit] Warning: ${error.message}\n`);
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

    // Run dependency scanners
    const npmVulns = await scanNpmAudit(args.target);
    const pipVulns = await scanPipAudit(args.target);

    // Combine all vulnerabilities
    const allVulnerabilities = [...npmVulns, ...pipVulns];

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
