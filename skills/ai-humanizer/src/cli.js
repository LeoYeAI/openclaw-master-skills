#!/usr/bin/env node

/**
 * cli.js — Command-line interface for the humanizer.
 *
 * Usage:
 *   humanizer analyze <file>                # Full analysis report
 *   humanizer score <file>                  # Just the score (0-100)
 *   humanizer humanize <file>               # Humanization suggestions
 *   humanizer report <file>                 # Full markdown report
 *   humanizer suggest <file>                # Suggestions grouped by priority
 *   humanizer stats <file>                  # Statistical analysis only
 *   humanizer analyze --json < input.txt    # JSON output
 *   humanizer analyze -f file.txt           # Read from file
 *   echo "text" | humanizer score           # Pipe text
 *
 * @module cli
 */

const fs = require('fs');
const { analyze, score, formatMarkdown, formatJSON } = require('./analyzer');
const { humanize, formatSuggestions } = require('./humanizer');
const { computeStats } = require('./stats');

// ─── Tiny Color Helper (no chalk dependency) ─────────────

/**
 * ANSI escape code helpers for terminal coloring.
 * Disables color when stdout is not a TTY or NO_COLOR is set.
 *
 * @namespace color
 */
const supportsColor = process.stdout.isTTY && !process.env.NO_COLOR;

const color = {
  /** @param {string} s */
  red: (s) => (supportsColor ? `\x1b[31m${s}\x1b[0m` : s),
  /** @param {string} s */
  green: (s) => (supportsColor ? `\x1b[32m${s}\x1b[0m` : s),
  /** @param {string} s */
  yellow: (s) => (supportsColor ? `\x1b[33m${s}\x1b[0m` : s),
  /** @param {string} s */
  blue: (s) => (supportsColor ? `\x1b[34m${s}\x1b[0m` : s),
  /** @param {string} s */
  magenta: (s) => (supportsColor ? `\x1b[35m${s}\x1b[0m` : s),
  /** @param {string} s */
  cyan: (s) => (supportsColor ? `\x1b[36m${s}\x1b[0m` : s),
  /** @param {string} s */
  gray: (s) => (supportsColor ? `\x1b[90m${s}\x1b[0m` : s),
  /** @param {string} s */
  bold: (s) => (supportsColor ? `\x1b[1m${s}\x1b[0m` : s),
  /** @param {string} s */
  dim: (s) => (supportsColor ? `\x1b[2m${s}\x1b[0m` : s),
};

/**
 * Get a colored score badge based on score value.
 *
 * @param {number} s - Score value 0-100
 * @returns {string} Colored badge string
 */
function scoreBadge(s) {
  if (s <= 25) return color.green(`🟢 ${s}/100`);
  if (s <= 50) return color.yellow(`🟡 ${s}/100`);
  if (s <= 75) return color.magenta(`🟠 ${s}/100`);
  return color.red(`🔴 ${s}/100`);
}

/**
 * Get a score label based on score value.
 *
 * @param {number} s - Score value 0-100
 * @returns {string} Human-readable label
 */
function scoreLabel(s) {
  if (s <= 19) return 'Mostly human-sounding';
  if (s <= 44) return 'Lightly AI-touched';
  if (s <= 69) return 'Moderately AI-influenced';
  return 'Heavily AI-generated';
}

// ─── CLI Arg Parsing ─────────────────────────────────────

const args = process.argv.slice(2);
const command = args[0];

const flags = {
  json: args.includes('--json'),
  verbose: args.includes('--verbose') || args.includes('-v'),
  autofix: args.includes('--autofix'),
  help: args.includes('--help') || args.includes('-h'),
  file: null,
  patterns: null,
  threshold: null,
  config: null,
};

// Parse -f / --file flag
const fileIdx = args.indexOf('-f') !== -1 ? args.indexOf('-f') : args.indexOf('--file');
if (fileIdx !== -1 && args[fileIdx + 1]) {
  flags.file = args[fileIdx + 1];
}

// Parse positional file argument (command <file>)
if (!flags.file && args[1] && !args[1].startsWith('-')) {
  const commands = ['analyze', 'score', 'humanize', 'report', 'suggest', 'stats'];
  if (!commands.includes(args[1])) {
    flags.file = args[1];
  }
}

// Parse --patterns flag (comma-separated pattern IDs)
const patIdx = args.indexOf('--patterns');
if (patIdx !== -1 && args[patIdx + 1]) {
  flags.patterns = args[patIdx + 1]
    .split(',')
    .map(Number)
    .filter((n) => n > 0);
}

// Parse --threshold flag
const threshIdx = args.indexOf('--threshold');
if (threshIdx !== -1 && args[threshIdx + 1]) {
  flags.threshold = parseInt(args[threshIdx + 1], 10);
}

// Parse --config flag
const configIdx = args.indexOf('--config');
if (configIdx !== -1 && args[configIdx + 1]) {
  flags.config = args[configIdx + 1];
}

// ─── Help ────────────────────────────────────────────────

/**
 * Display CLI help text.
 */
function showHelp() {
  console.log(`
${color.bold('humanizer')} — Detect and remove AI writing patterns

${color.bold('Usage:')}
  humanizer <command> [file] [options]

${color.bold('Commands:')}
  ${color.cyan('analyze')}      Full analysis report with pattern matches
  ${color.cyan('score')}        Quick score (0-100, higher = more AI-like)
  ${color.cyan('humanize')}     Humanization suggestions with guidance
  ${color.cyan('report')}       Full markdown report (for piping to files)
  ${color.cyan('suggest')}      Show only suggestions, grouped by priority
  ${color.cyan('stats')}        Show statistical text analysis only

${color.bold('Options:')}
  -f, --file <path>       Read text from file (otherwise reads stdin)
  --json                  Output as JSON
  --verbose, -v           Show all matches (not just top 5 per pattern)
  --autofix               Apply safe mechanical fixes (humanize only)
  --patterns <ids>        Only check specific pattern IDs (comma-separated)
  --threshold <n>         Only show patterns with weight above threshold
  --config <file>         Custom config file (JSON)
  --help, -h              Show this help

${color.bold('Examples:')}
  ${color.gray('# Quick score')}
  echo "This is a testament to..." | humanizer score

  ${color.gray('# Analyze a file')}
  humanizer analyze essay.txt

  ${color.gray('# Full markdown report')}
  humanizer report article.txt > report.md

  ${color.gray('# Just suggestions')}
  humanizer suggest article.txt

  ${color.gray('# Statistical analysis')}
  humanizer stats essay.txt

  ${color.gray('# Humanize with auto-fixes')}
  humanizer humanize --autofix -f article.txt

${color.bold('Score badges:')}
  🟢 0-25    Mostly human-sounding
  🟡 26-50   Lightly AI-touched
  🟠 51-75   Moderately AI-influenced
  🔴 76-100  Heavily AI-generated
`);
}

// ─── Read Input ──────────────────────────────────────────

/**
 * Read input text from file or stdin.
 *
 * @returns {Promise<string>} The input text
 */
function readInput() {
  return new Promise((resolve, reject) => {
    if (flags.file) {
      try {
        const text = fs.readFileSync(flags.file, 'utf-8');
        resolve(text);
      } catch (err) {
        reject(new Error(`Could not read file: ${flags.file} (${err.message})`));
      }
      return;
    }

    if (process.stdin.isTTY) {
      reject(new Error('No input. Pipe text or use -f <file>. Run with --help for usage.'));
      return;
    }

    let data = '';
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (chunk) => {
      data += chunk;
    });
    process.stdin.on('end', () => resolve(data));
    process.stdin.on('error', reject);
  });
}

// ─── Stats Formatter ─────────────────────────────────────

/**
 * Format text statistics as a terminal report.
 *
 * @param {object} stats - Stats object from computeStats()
 * @returns {string} Formatted report
 */
function formatStatsReport(stats) {
  const lines = [];

  lines.push('');
  lines.push(color.bold('  ┌──────────────────────────────────────────────┐'));
  lines.push(color.bold('  │          TEXT STATISTICS ANALYSIS             │'));
  lines.push(color.bold('  └──────────────────────────────────────────────┘'));
  lines.push('');

  lines.push(color.bold('  ── Sentences ──────────────────────────────────'));
  lines.push(`    Count:            ${stats.sentenceCount}`);
  lines.push(`    Avg length:       ${stats.avgSentenceLength} words`);
  lines.push(`    Std deviation:    ${stats.sentenceLengthStdDev}`);
  lines.push(`    Burstiness:       ${stats.burstiness}  ${burstLabel(stats.burstiness)}`);
  lines.push('');

  lines.push(color.bold('  ── Vocabulary ─────────────────────────────────'));
  lines.push(`    Total words:      ${stats.wordCount}`);
  lines.push(`    Unique words:     ${stats.uniqueWordCount}`);
  lines.push(
    `    Type-token ratio: ${stats.typeTokenRatio}  ${ttrLabel(stats.typeTokenRatio, stats.wordCount)}`,
  );
  lines.push(`    Avg word length:  ${stats.avgWordLength}`);
  lines.push('');

  lines.push(color.bold('  ── Structure ──────────────────────────────────'));
  lines.push(`    Paragraphs:       ${stats.paragraphCount}`);
  lines.push(`    Avg para length:  ${stats.avgParagraphLength} words`);
  lines.push(`    Trigram repeat:   ${stats.trigramRepetition}`);
  lines.push('');

  lines.push(color.bold('  ── Readability ────────────────────────────────'));
  lines.push(`    Flesch-Kincaid:   ${stats.fleschKincaid} grade level`);
  lines.push(
    `    Function words:   ${stats.functionWordRatio} (${(stats.functionWordRatio * 100).toFixed(1)}%)`,
  );
  lines.push('');

  return lines.join('\n');
}

/**
 * Get burstiness label.
 *
 * @param {number} b
 * @returns {string}
 */
function burstLabel(b) {
  if (b >= 0.7) return color.green('(high — human-like)');
  if (b >= 0.45) return color.yellow('(moderate)');
  if (b >= 0.25) return color.yellow('(low — somewhat uniform)');
  return color.red('(very low — AI-like)');
}

/**
 * Get type-token ratio label.
 *
 * @param {number} ttr
 * @param {number} wc
 * @returns {string}
 */
function ttrLabel(ttr, wc) {
  if (wc < 100) return color.gray('(too short to assess)');
  if (ttr >= 0.6) return color.green('(high — diverse)');
  if (ttr >= 0.45) return color.yellow('(moderate)');
  return color.red('(low — repetitive)');
}

// ─── Colored Report Formatter ────────────────────────────

/**
 * Format analysis with enhanced terminal formatting and colors.
 *
 * @param {object} result - Analysis result from analyze()
 * @returns {string} Colored terminal report
 */
function formatColoredReport(result) {
  const lines = [];

  lines.push('');
  lines.push(color.bold('  ┌──────────────────────────────────────────────┐'));
  lines.push(color.bold('  │        AI WRITING PATTERN ANALYSIS           │'));
  lines.push(color.bold('  └──────────────────────────────────────────────┘'));
  lines.push('');

  // Score bar with color
  const filled = Math.round(result.score / 5);
  const barColor =
    result.score <= 25
      ? color.green
      : result.score <= 50
        ? color.yellow
        : result.score <= 75
          ? color.magenta
          : color.red;
  const bar = barColor('█'.repeat(filled)) + color.dim('░'.repeat(20 - filled));
  lines.push(`  Score: ${scoreBadge(result.score)}  [${bar}]`);
  lines.push(
    `  ${color.dim(`Words: ${result.wordCount}  |  Matches: ${result.totalMatches}  |  Pattern: ${result.patternScore}  |  Uniformity: ${result.uniformityScore}`)}`,
  );
  lines.push('');
  lines.push(`  ${result.summary}`);
  lines.push('');

  // Statistics
  if (result.stats) {
    const s = result.stats;
    lines.push(color.bold('  ── Statistics ──────────────────────────────────'));
    lines.push(`  Burstiness: ${s.burstiness}  ${burstLabel(s.burstiness)}`);
    lines.push(
      `  Type-token ratio: ${s.typeTokenRatio}  ${ttrLabel(s.typeTokenRatio, s.wordCount)}`,
    );
    lines.push(`  Trigram repetition: ${s.trigramRepetition}`);
    lines.push(`  Readability: ${s.fleschKincaid} grade level`);
    lines.push('');
  }

  // Category breakdown
  lines.push(color.bold('  ── Categories ──────────────────────────────────'));
  for (const [, data] of Object.entries(result.categories)) {
    if (data.matches > 0) {
      lines.push(
        `  ${color.cyan(data.label)}: ${data.matches} matches ${color.dim(`(${data.patternsDetected.join(', ')})`)}`,
      );
    }
  }
  lines.push('');

  // Findings detail
  if (result.findings.length > 0) {
    lines.push(color.bold('  ── Findings ──────────────────────────────────'));
    for (const finding of result.findings) {
      if (flags.threshold && finding.weight < flags.threshold) continue;

      lines.push('');
      const weightColor =
        finding.weight >= 4 ? color.red : finding.weight >= 2 ? color.yellow : color.blue;
      lines.push(
        `  ${weightColor(`[${finding.patternId}]`)} ${color.bold(finding.patternName)} ${color.dim(`(×${finding.matchCount}, weight: ${finding.weight})`)}`,
      );
      lines.push(`      ${color.dim(finding.description)}`);
      for (const match of finding.matches) {
        const loc = match.line ? `L${match.line}` : '';
        const preview =
          typeof match.match === 'string'
            ? match.match.substring(0, 80) + (match.match.length > 80 ? '...' : '')
            : '';
        lines.push(`      ${color.dim(loc)}: "${preview}"`);
        if (match.suggestion) {
          lines.push(`            ${color.green('→')} ${match.suggestion}`);
        }
      }
      if (finding.truncated) {
        lines.push(
          `      ${color.dim(`... and ${finding.matchCount - finding.matches.length} more`)}`,
        );
      }
    }
  }

  lines.push('');
  lines.push(color.dim('  ──────────────────────────────────────────────'));
  return lines.join('\n');
}

// ─── Grouped Suggestions Formatter ───────────────────────

/**
 * Format suggestions grouped by priority with color.
 *
 * @param {object} result - Humanization result from humanize()
 * @returns {string} Formatted suggestion report
 */
function formatGroupedSuggestions(result) {
  const lines = [];

  lines.push('');
  lines.push(color.bold(`  Score: ${scoreBadge(result.score)}  (${scoreLabel(result.score)})`));
  lines.push(`  ${color.dim(`${result.totalIssues} issues found in ${result.wordCount} words`)}`);
  lines.push('');

  if (result.critical.length > 0) {
    lines.push(color.red(color.bold('  ━━ CRITICAL (remove these first) ━━━━━━━━━━━━')));
    for (const s of result.critical) {
      lines.push(`  ${color.red('●')} L${s.line}: ${color.bold(s.pattern)}`);
      lines.push(`    ${color.dim(truncate(s.text, 60))}`);
      lines.push(`    ${color.green('→')} ${s.suggestion}`);
    }
    lines.push('');
  }

  if (result.important.length > 0) {
    lines.push(color.yellow(color.bold('  ━━ IMPORTANT (noticeable AI patterns) ━━━━━━━')));
    for (const s of result.important) {
      lines.push(`  ${color.yellow('●')} L${s.line}: ${color.bold(s.pattern)}`);
      lines.push(`    ${color.dim(truncate(s.text, 60))}`);
      lines.push(`    ${color.green('→')} ${s.suggestion}`);
    }
    lines.push('');
  }

  if (result.minor.length > 0) {
    lines.push(color.blue(color.bold('  ━━ MINOR (subtle tells) ━━━━━━━━━━━━━━━━━━━━')));
    for (const s of result.minor) {
      lines.push(`  ${color.blue('●')} L${s.line}: ${color.bold(s.pattern)}`);
      lines.push(`    ${color.dim(truncate(s.text, 60))}`);
      lines.push(`    ${color.green('→')} ${s.suggestion}`);
    }
    lines.push('');
  }

  if (result.guidance.length > 0) {
    lines.push(color.cyan(color.bold('  ━━ GUIDANCE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')));
    for (const tip of result.guidance) {
      lines.push(`  ${color.cyan('•')} ${tip}`);
    }
    lines.push('');
  }

  if (result.styleTips && result.styleTips.length > 0) {
    lines.push(color.magenta(color.bold('  ━━ STYLE TIPS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')));
    for (const t of result.styleTips) {
      lines.push(`  ${color.magenta('◦')} ${t.tip}`);
    }
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Truncate a string to a max length.
 *
 * @param {string} str
 * @param {number} len
 * @returns {string}
 */
function truncate(str, len) {
  if (typeof str !== 'string') return '';
  return str.length > len ? `${str.substring(0, len)}...` : str;
}

// ─── Main ────────────────────────────────────────────────

/**
 * Main CLI entry point.
 */
async function main() {
  if (flags.help || !command) {
    showHelp();
    process.exit(command ? 0 : 1);
  }

  let text;
  try {
    text = await readInput();
  } catch (err) {
    console.error(color.red(`Error: ${err.message}`));
    process.exit(1);
  }

  if (!text.trim()) {
    console.error(color.red('Error: Empty input.'));
    process.exit(1);
  }

  const opts = {
    verbose: flags.verbose,
    patternsToCheck: flags.patterns,
  };

  switch (command) {
    case 'analyze': {
      const result = analyze(text, opts);
      if (flags.json) {
        console.log(formatJSON(result));
      } else {
        console.log(formatColoredReport(result));
      }
      break;
    }

    case 'score': {
      const s = score(text);
      if (flags.json) {
        console.log(JSON.stringify({ score: s }));
      } else {
        console.log(scoreBadge(s));
      }
      break;
    }

    case 'humanize': {
      const result = humanize(text, { autofix: flags.autofix, verbose: flags.verbose });
      if (flags.json) {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.log(formatSuggestions(result));
        if (flags.autofix && result.autofix) {
          console.log(`\n${color.bold('── AUTO-FIXED TEXT ──────────────────────────────')}\n`);
          console.log(result.autofix.text);
          console.log(`\n${color.dim('════════════════════════════════════════════════')}`);
        }
      }
      break;
    }

    case 'report': {
      const result = analyze(text, { ...opts, verbose: true });
      console.log(formatMarkdown(result));
      break;
    }

    case 'suggest': {
      const result = humanize(text, { verbose: flags.verbose });
      if (flags.json) {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.log(formatGroupedSuggestions(result));
      }
      break;
    }

    case 'stats': {
      const stats = computeStats(text);
      if (flags.json) {
        console.log(JSON.stringify(stats, null, 2));
      } else {
        console.log(formatStatsReport(stats));
      }
      break;
    }

    default:
      console.error(color.red(`Unknown command: ${command}. Run with --help for usage.`));
      process.exit(1);
  }
}

main().catch((err) => {
  console.error(color.red(`Fatal: ${err.message}`));
  process.exit(1);
});
