import { readFile, stat, writeFile, mkdir } from 'fs/promises';
import { resolve, dirname, join } from 'path';
import chalk from 'chalk';
import { glob } from 'glob';

interface Rule {
  id: string;
  name: string;
  pattern: RegExp;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  message: string;
  fix: string;
}

interface Finding {
  rule_id: string;
  rule_name: string;
  severity: string;
  line: number;
  code: string;
  message: string;
  fix: string;
}

const RULES: Rule[] = [
  {
    id: 'A001',
    name: 'missing-alt-text',
    pattern: /<img(?![^>]*alt=)[^>]*>/i,
    severity: 'CRITICAL',
    message: 'Image missing alt attribute — WCAG 1.1.1 violation',
    fix: 'Add alt="" for decorative images or descriptive alt text for informational images',
  },
  {
    id: 'A002',
    name: 'missing-aria-label',
    pattern: /<button(?![^>]*(?:aria-label|aria-labelledby))[^>]*>\s*<(?:svg|img|i|span)/i,
    severity: 'WARNING',
    message: 'Icon-only button without aria-label',
    fix: 'Add aria-label describing the button action',
  },
  {
    id: 'A003',
    name: 'hardcoded-color',
    pattern: /(?:color|background|border):\s*#[0-9a-fA-F]{3,8}/i,
    severity: 'INFO',
    message: 'Hardcoded color value — use design tokens instead',
    fix: 'Replace with CSS custom property: var(--color-primary-500)',
  },
  {
    id: 'A004',
    name: 'px-font-size',
    pattern: /font-size:\s*\d+px/i,
    severity: 'WARNING',
    message: 'Font size in px — use rem for accessibility',
    fix: 'Convert to rem: 16px = 1rem',
  },
  {
    id: 'A005',
    name: 'magic-z-index',
    pattern: /z-index:\s*(?:999|9999|99999)/i,
    severity: 'WARNING',
    message: 'Magic z-index value — use token scale',
    fix: 'Define z-index tokens: --z-dropdown: 100, --z-modal: 200, --z-toast: 300',
  },
  {
    id: 'A006',
    name: 'important-override',
    pattern: /!important/i,
    severity: 'WARNING',
    message: '!important override detected — indicates specificity issues',
    fix: 'Refactor CSS specificity instead of using !important',
  },
  {
    id: 'A007',
    name: 'inline-style',
    pattern: /style=\{?\{[^}]+\}\}?|style="[^"]*"/i,
    severity: 'INFO',
    message: 'Inline style detected — extract to CSS module or styled-component',
    fix: 'Move styles to external stylesheet or CSS-in-JS',
  },
  {
    id: 'A008',
    name: 'missing-focus-visible',
    pattern: /:focus\s*\{[^}]*outline:\s*(?:none|0)/i,
    severity: 'CRITICAL',
    message: 'Focus outline removed — WCAG 2.4.7 violation',
    fix: 'Use :focus-visible instead and provide visible focus indicator',
  },
  {
    id: 'A009',
    name: 'low-tap-target',
    pattern: /(?:width|height|min-width|min-height):\s*(?:[1-3][0-9]|[0-9])px/i,
    severity: 'WARNING',
    message: 'Potential low tap target — minimum 44px recommended',
    fix: 'Ensure interactive elements are at least 44x44px',
  },
  {
    id: 'A010',
    name: 'missing-lang',
    pattern: /<html(?![^>]*lang=)/i,
    severity: 'CRITICAL',
    message: 'HTML element missing lang attribute',
    fix: 'Add lang="en" (or appropriate language) to <html>',
  },
  {
    id: 'A011',
    name: 'autoplaying-media',
    pattern: /<(?:video|audio)(?=[^>]*autoplay)/i,
    severity: 'WARNING',
    message: 'Autoplaying media — may cause accessibility issues',
    fix: 'Add muted attribute or provide pause controls',
  },
  {
    id: 'A012',
    name: 'color-only-indicator',
    pattern: /(?:color|background-color):\s*(?:red|green|#(?:f00|0f0|ff0000|00ff00))/i,
    severity: 'WARNING',
    message: 'Color-only status indicator — add icon or text for colorblind users',
    fix: 'Add supporting icon, text, or pattern to convey meaning',
  },
  // --- AI Hallucination Checks (2026 Deep Research) ---
  {
    id: 'AI001',
    name: 'dynamic-class-interpolation',
    pattern: /className=\{`[^`]*\$\{[^}]*\}[^`]*`\}/,
    severity: 'CRITICAL',
    message: 'Tailwind interpolation detected — JIT compiler cannot extract these classes',
    fix: 'Use a safelist map object: className={colorMap[props.color]}',
  },
  {
    id: 'AI005',
    name: 'non-existent-utility',
    pattern: /text-shadow-(?:sm|md|lg|xl)/,
    severity: 'WARNING',
    message: 'Hallucinated utility "text-shadow" — does not exist in Tailwind defaults',
    fix: 'Use drop-shadow-md or a custom plugin',
  },
  {
    id: 'AI008',
    name: 'pseudo-transparency-contrast',
    pattern: /bg-(?:black|white|slate-\d{3})\/(?:10|20|30|40|50)(?!\d)/,
    severity: 'WARNING',
    message: 'Low contrast pseudo-transparency used on potential text background',
    fix: 'Use glassmorphism: backdrop-filter: blur(4px) brightness(0.5)',
  },
  {
    id: 'AI010',
    name: 'arbitrary-calc-spacing',
    pattern: /w-\[calc\([^]]*?[+\-/*](?![_])[^]]*?\)\]/,
    severity: 'CRITICAL',
    message: 'Tailwind arbitrary value missing underscores in calc()',
    fix: 'Replace spaces with underscores: w-[calc(100%_-_20px)]',
  },
  {
    id: 'AI013',
    name: 'vh-mobile-bug',
    pattern: /(?:h|min-h)-screen/,
    severity: 'WARNING',
    message: 'h-screen causes layout shifts on mobile browsers (address bar resize)',
    fix: 'Use dynamic viewport height: h-[100dvh]',
  },
  {
    id: 'AI015',
    name: 'target-blank-vuln',
    pattern: /target="_blank"(?![^>]*rel=)/,
    severity: 'WARNING',
    message: 'target="_blank" validation missing rel="noopener noreferrer"',
    fix: 'Add rel="noopener noreferrer" to prevent tabnabbing',
  },
];

async function auditFile(filepath: string): Promise<Finding[]> {
  try {
    const stats = await stat(filepath);
    if (stats.isDirectory()) return [];
    
    const content = await readFile(filepath, 'utf-8');
    const lines = content.split('\n');
    const findings: Finding[] = [];

    for (const rule of RULES) {
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (!line) continue;

        if (rule.pattern.test(line)) {
          findings.push({
            rule_id: rule.id,
            rule_name: rule.name,
            severity: rule.severity,
            line: i + 1,
            code: line.trim().substring(0, 80),
            message: rule.message,
            fix: rule.fix,
          });
        }
      }
    }
    return findings;
  } catch (err) {
    console.warn(chalk.yellow(`Could not read file ${filepath}:`), err);
    return [];
  }
}



// ... (existing imports)

export async function auditCommand(files: string | string[], options: { format?: string; output?: string }) {
  // ... (existing file expansion logic)
  const filePatterns = Array.isArray(files) ? files : [files];
  const expandedFiles: string[] = [];
  
  for (const pattern of filePatterns) {
    const matches = await glob(pattern);
    if (matches.length > 0) expandedFiles.push(...matches);
    else expandedFiles.push(pattern);
  }

  const allFindings: { file: string; findings: Finding[] }[] = [];
  let totalIssueCount = 0;

  for (const file of expandedFiles) {
    const findings = await auditFile(file);
    if (findings.length > 0) {
      allFindings.push({ file, findings });
      totalIssueCount += findings.length;
    }
  }

  // Determine output path and format
  let outputPath = options.output;
  let format = options.format || 'text';

  if (outputPath) {
    // Enforce 'output/' directory if not present and not an absolute path
    if (!outputPath.startsWith('/') && !outputPath.startsWith('output/')) {
        outputPath = join('output', outputPath);
    }
    
    if (outputPath.endsWith('.json')) format = 'json';
    if (outputPath.endsWith('.md')) format = 'markdown';
  }

  let outputContent = '';

  if (format === 'json') {
     // ... (JSON generation)
    outputContent = JSON.stringify({ 
      summary: { totalBytes: 0, totalFiles: expandedFiles.length, issues: totalIssueCount },
      details: allFindings 
    }, null, 2);
  } else if (format === 'markdown') {
     // ... (Markdown generation)
    outputContent = `# UI Design System Audit Report\n\n`;
    outputContent += `**Date:** ${new Date().toLocaleString()}\n`;
    outputContent += `**Files Scanned:** ${expandedFiles.length}\n`;
    outputContent += `**Total Issues:** ${totalIssueCount}\n\n`;

    if (totalIssueCount === 0) {
      outputContent += `✅ **No issues found.** Great job!\n`;
    } else {
      for (const { file, findings } of allFindings) {
        const critical = findings.filter(f => f.severity === 'CRITICAL').length;
        const warning = findings.filter(f => f.severity === 'WARNING').length;
        const info = findings.filter(f => f.severity === 'INFO').length;

        outputContent += `## 📄 \`${file}\`\n`;
        outputContent += `Summary: 🔴 ${critical} Critical | 🟡 ${warning} Warnings | 🔵 ${info} Info\n\n`;
        outputContent += `| Line | Severity | Rule | Message | Fix |\n`;
        outputContent += `| :--- | :--- | :--- | :--- | :--- |\n`;

        const sorted = findings.sort((a, b) => {
           if (a.severity === 'CRITICAL' && b.severity !== 'CRITICAL') return -1;
           if (b.severity === 'CRITICAL' && a.severity !== 'CRITICAL') return 1;
           return a.line - b.line;
        });

        for (const f of sorted) {
          const icon = f.severity === 'CRITICAL' ? '🔴' : f.severity === 'WARNING' ? '🟡' : '🔵';
          outputContent += `| ${f.line} | ${icon} ${f.severity} | \`${f.rule_id}\` | ${f.message} <br> _Code:_ \`${f.code.replaceAll('|', '\\|')}\` | ${f.fix} |\n`;
        }
        outputContent += `\n`;
      }
    }
  } else {
    // ... (Text generation)
    if (totalIssueCount === 0) {
      outputContent = chalk.green('\n  No issues found!');
    } else {
      for (const { file, findings } of allFindings) {
        const critical = findings.filter(f => f.severity === 'CRITICAL').length;
        const warning = findings.filter(f => f.severity === 'WARNING').length;
        const info = findings.filter(f => f.severity === 'INFO').length;

        outputContent += `\n  ${chalk.bold('UI AUDIT')}: ${file}\n`;
        outputContent += `  ${chalk.red(critical + ' critical')} | ${chalk.yellow(warning + ' warnings')} | ${chalk.blue(info + ' info')}\n\n`;

        const sorted = findings.sort((a, b) => {
           if (a.severity === 'CRITICAL' && b.severity !== 'CRITICAL') return -1;
           if (b.severity === 'CRITICAL' && a.severity !== 'CRITICAL') return 1;
           return a.line - b.line;
        });

        for (const f of sorted) {
          const icon = f.severity === 'CRITICAL' ? '🔴' : f.severity === 'WARNING' ? '🟡' : '🔵';
          outputContent += `  ${icon} L${f.line} [${f.rule_id}] ${chalk.bold(f.message)}\n`;
          outputContent += `     ${chalk.gray('Code:')} ${f.code}\n`;
          outputContent += `     ${chalk.green('Fix:')}  ${f.fix}\n\n`;
        }
      }
    }
  }

  if (outputPath) {
    const dir = dirname(outputPath);
    if (dir !== '.') {
        await mkdir(dir, { recursive: true });
    }
    await writeFile(outputPath, outputContent);
    console.log(chalk.green(`\nAudit report saved to ${outputPath}`));
  } else {
    console.log(outputContent);
  }
}
