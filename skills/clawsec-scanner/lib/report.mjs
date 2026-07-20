import { generateUuid, getTimestamp } from "./utils.mjs";

/**
 * @typedef {import('./types.ts').Vulnerability} Vulnerability
 * @typedef {import('./types.ts').ScanReport} ScanReport
 * @typedef {import('./types.ts').SeverityLevel} SeverityLevel
 */

/**
 * Generate a unified vulnerability report from scan results.
 *
 * @param {Vulnerability[]} vulnerabilities - Array of detected vulnerabilities
 * @param {string} target - Target path that was scanned
 * @returns {ScanReport}
 */
export function generateReport(vulnerabilities, target = ".") {
  const summary = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    info: 0,
  };

  // Count vulnerabilities by severity
  for (const vuln of vulnerabilities) {
    const severity = vuln.severity;
    if (severity in summary) {
      summary[severity]++;
    }
  }

  return {
    scan_id: generateUuid(),
    timestamp: getTimestamp(),
    target,
    vulnerabilities,
    summary,
  };
}

/**
 * Format a scan report as JSON string.
 *
 * @param {ScanReport} report - Scan report to format
 * @param {boolean} pretty - Whether to pretty-print JSON
 * @returns {string}
 */
export function formatReportJson(report, pretty = true) {
  return pretty ? JSON.stringify(report, null, 2) : JSON.stringify(report);
}

/**
 * Format a scan report as human-readable text.
 *
 * @param {ScanReport} report - Scan report to format
 * @returns {string}
 */
export function formatReportText(report) {
  const lines = [];

  // Header
  lines.push("═══════════════════════════════════════════════════════════════");
  lines.push("                  VULNERABILITY SCAN REPORT");
  lines.push("═══════════════════════════════════════════════════════════════");
  lines.push("");
  lines.push(`Scan ID:   ${report.scan_id}`);
  lines.push(`Timestamp: ${report.timestamp}`);
  lines.push(`Target:    ${report.target}`);
  lines.push("");

  // Summary
  lines.push("───────────────────────────────────────────────────────────────");
  lines.push("SUMMARY");
  lines.push("───────────────────────────────────────────────────────────────");
  lines.push("");

  const total = report.vulnerabilities.length;
  const { critical, high, medium, low, info } = report.summary;

  lines.push(`Total Vulnerabilities: ${total}`);
  lines.push("");

  if (critical > 0) {
    lines.push(`  🔴 Critical: ${critical}`);
  }
  if (high > 0) {
    lines.push(`  🟠 High:     ${high}`);
  }
  if (medium > 0) {
    lines.push(`  🟡 Medium:   ${medium}`);
  }
  if (low > 0) {
    lines.push(`  🔵 Low:      ${low}`);
  }
  if (info > 0) {
    lines.push(`  ⚪ Info:     ${info}`);
  }

  if (total === 0) {
    lines.push("  ✓ No vulnerabilities detected");
  }

  lines.push("");

  // Detailed findings
  if (report.vulnerabilities.length > 0) {
    lines.push("───────────────────────────────────────────────────────────────");
    lines.push("DETAILED FINDINGS");
    lines.push("───────────────────────────────────────────────────────────────");
    lines.push("");

    // Group vulnerabilities by severity
    const bySeverity = {
      critical: [],
      high: [],
      medium: [],
      low: [],
      info: [],
    };

    for (const vuln of report.vulnerabilities) {
      bySeverity[vuln.severity].push(vuln);
    }

    // Display in order: critical -> high -> medium -> low -> info
    const severityOrder = ["critical", "high", "medium", "low", "info"];

    for (const severity of severityOrder) {
      const vulns = bySeverity[severity];
      if (vulns.length === 0) continue;

      const severityIcon = getSeverityIcon(severity);
      lines.push(`${severityIcon} ${severity.toUpperCase()}`);
      lines.push("");

      for (const vuln of vulns) {
        lines.push(`  ID:      ${vuln.id}`);
        lines.push(`  Package: ${vuln.package} @ ${vuln.version}`);
        if (vuln.fixed_version) {
          lines.push(`  Fix:     ${vuln.fixed_version}`);
        }
        lines.push(`  Source:  ${vuln.source}`);
        lines.push(`  Title:   ${vuln.title}`);

        // Wrap description at 60 chars
        const descLines = wrapText(vuln.description, 60);
        lines.push("  Description:");
        for (const line of descLines) {
          lines.push(`    ${line}`);
        }

        if (vuln.references.length > 0) {
          lines.push("  References:");
          for (const ref of vuln.references.slice(0, 3)) {
            lines.push(`    - ${ref}`);
          }
          if (vuln.references.length > 3) {
            lines.push(`    ... and ${vuln.references.length - 3} more`);
          }
        }

        lines.push("");
      }
    }
  }

  // Recommendations
  lines.push("───────────────────────────────────────────────────────────────");
  lines.push("RECOMMENDATIONS");
  lines.push("───────────────────────────────────────────────────────────────");
  lines.push("");

  if (critical > 0 || high > 0) {
    lines.push("⚠️  URGENT: Critical or high severity vulnerabilities detected!");
    lines.push("");
    lines.push("Recommended actions:");
    lines.push("  1. Review all critical and high severity findings immediately");
    lines.push("  2. Update vulnerable dependencies to fixed versions");
    lines.push("  3. Run scanner again to verify remediation");
    lines.push("");
  } else if (medium > 0) {
    lines.push("⚠️  Medium severity vulnerabilities detected.");
    lines.push("");
    lines.push("Recommended actions:");
    lines.push("  1. Review findings and assess impact on your use case");
    lines.push("  2. Plan updates during next maintenance window");
    lines.push("");
  } else if (low > 0 || info > 0) {
    lines.push("✓ No critical or high severity vulnerabilities detected.");
    lines.push("");
    lines.push("Recommended actions:");
    lines.push("  1. Review low/info findings for awareness");
    lines.push("  2. Consider updates when convenient");
    lines.push("");
  } else {
    lines.push("✓ No vulnerabilities detected. Your code is clean!");
    lines.push("");
  }

  lines.push("═══════════════════════════════════════════════════════════════");

  return lines.join("\n");
}

/**
 * Get emoji icon for severity level.
 *
 * @param {SeverityLevel} severity - Severity level
 * @returns {string}
 */
function getSeverityIcon(severity) {
  const icons = {
    critical: "🔴",
    high: "🟠",
    medium: "🟡",
    low: "🔵",
    info: "⚪",
  };
  return icons[severity] || "⚪";
}

/**
 * Wrap text to specified width.
 *
 * @param {string} text - Text to wrap
 * @param {number} width - Maximum line width
 * @returns {string[]}
 */
function wrapText(text, width) {
  const words = text.split(/\s+/);
  const lines = [];
  let currentLine = "";

  for (const word of words) {
    if (currentLine.length + word.length + 1 <= width) {
      currentLine += (currentLine ? " " : "") + word;
    } else {
      if (currentLine) {
        lines.push(currentLine);
      }
      currentLine = word;
    }
  }

  if (currentLine) {
    lines.push(currentLine);
  }

  return lines.length > 0 ? lines : [""];
}
