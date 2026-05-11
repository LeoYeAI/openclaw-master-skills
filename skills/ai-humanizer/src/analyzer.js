/**
 * analyzer.js — Text analysis engine.
 *
 * Combines pattern detection with statistical analysis to produce a
 * comprehensive AI writing score. The score uses three signal types:
 *
 *   1. Pattern matches — vocabulary, phrases, structural patterns (24 detectors)
 *   2. Text statistics — burstiness, sentence variation, type-token ratio
 *   3. Category breadth — how many different AI signal types are present
 *
 * Based on research from:
 *   - Wikipedia:Signs of AI writing
 *   - Copyleaks stylistic fingerprint analysis (arxiv 2503.01659v1)
 *   - StyloAI 31-feature stylometric analysis
 */

const { patterns, wordCount } = require('./patterns');
const { computeStats, computeUniformityScore } = require('./stats');

// ─── Category Labels ────────────────────────────────────

const CATEGORY_LABELS = {
  content: 'Content patterns',
  language: 'Language & grammar',
  style: 'Style patterns',
  communication: 'Communication artifacts',
  filler: 'Filler & hedging',
};

// ─── Analysis Engine ─────────────────────────────────────

/**
 * Analyze text for AI writing patterns and compute statistics.
 *
 * @param {string} text  — The text to analyze
 * @param {object} opts  — Options:
 *   - verbose {boolean}     Show all matches (not just top 5 per pattern)
 *   - patternsToCheck {number[]}  Only run specific pattern IDs
 *   - includeStats {boolean}  Include full text statistics (default: true)
 *   - config {object}       Custom config overrides
 * @returns {object}     — Full analysis result
 */
function analyze(text, opts = {}) {
  const { verbose = false, patternsToCheck = null, includeStats = true } = opts;

  if (!text || typeof text !== 'string') {
    return emptyResult();
  }

  const trimmed = text.trim();
  if (trimmed.length === 0) return emptyResult();

  const words = wordCount(trimmed);

  // ── Compute text statistics ────────────────────────
  const stats = includeStats ? computeStats(trimmed) : null;
  // Only compute uniformity for text with enough structure to be meaningful
  const uniformityScore =
    stats && stats.wordCount >= 20 && stats.sentenceCount >= 3 ? computeUniformityScore(stats) : 0;

  // ── Run pattern detectors ──────────────────────────
  const findings = [];
  const categoryScores = {};
  for (const cat of Object.keys(CATEGORY_LABELS)) {
    categoryScores[cat] = { matches: 0, weightedScore: 0, patterns: [] };
  }

  const activePatterns = patternsToCheck
    ? patterns.filter((p) => patternsToCheck.includes(p.id))
    : patterns;

  for (const pattern of activePatterns) {
    const matches = pattern.detect(trimmed);
    if (matches.length > 0) {
      const finding = {
        patternId: pattern.id,
        patternName: pattern.name,
        category: pattern.category,
        description: pattern.description,
        weight: pattern.weight,
        matchCount: matches.length,
        matches: verbose ? matches : matches.slice(0, 5),
        truncated: !verbose && matches.length > 5,
      };

      findings.push(finding);
      categoryScores[pattern.category].matches += matches.length;
      categoryScores[pattern.category].weightedScore += matches.length * pattern.weight;
      categoryScores[pattern.category].patterns.push(pattern.name);
    }
  }

  // ── Calculate composite score ──────────────────────
  const patternScore = calculatePatternScore(findings, words);
  const compositeScore = calculateCompositeScore(patternScore, uniformityScore, findings);

  // ── Build category summary ─────────────────────────
  const categories = {};
  for (const [cat, label] of Object.entries(CATEGORY_LABELS)) {
    const data = categoryScores[cat];
    categories[cat] = {
      label,
      matches: data.matches,
      weightedScore: data.weightedScore,
      patternsDetected: data.patterns,
    };
  }

  const totalMatches = findings.reduce((sum, f) => sum + f.matchCount, 0);

  return {
    score: compositeScore,
    patternScore,
    uniformityScore,
    totalMatches,
    wordCount: words,
    stats,
    categories,
    findings,
    summary: buildSummary(compositeScore, totalMatches, findings, words, stats),
  };
}

// ─── Scoring ─────────────────────────────────────────────

/**
 * Pattern-based score component (0-100).
 * Uses density, breadth, and category diversity.
 */
function calculatePatternScore(findings, words) {
  if (words === 0 || findings.length === 0) return 0;

  let weightedTotal = 0;
  for (const f of findings) {
    weightedTotal += f.matchCount * f.weight;
  }

  // Density: weighted hits per 100 words (log scale)
  const density = (weightedTotal / words) * 100;
  const densityScore = Math.min(Math.log2(density + 1) * 13, 65);

  // Breadth: unique pattern types (max 20)
  const breadthBonus = Math.min(findings.length * 2, 20);

  // Category diversity (max 15)
  const categoriesHit = new Set(findings.map((f) => f.category)).size;
  const categoryBonus = Math.min(categoriesHit * 3, 15);

  return Math.min(Math.round(densityScore + breadthBonus + categoryBonus), 100);
}

/**
 * Composite score combining pattern detection and statistical analysis.
 *
 * Pattern score is the primary signal (70% weight).
 * Uniformity score adds statistical evidence (30% weight).
 * But only when both are present — stats alone aren't enough.
 */
function calculateCompositeScore(patternScore, uniformityScore, findings) {
  if (patternScore === 0 && uniformityScore === 0) return 0;

  // If no patterns detected, uniformity alone isn't enough to accuse
  if (findings.length === 0) return Math.min(Math.round(uniformityScore * 0.15), 15);

  // Weighted blend: patterns dominate, stats supplement
  const blended = patternScore * 0.7 + uniformityScore * 0.3;
  return Math.min(Math.round(blended), 100);
}

/**
 * Build human-readable summary.
 */
function buildSummary(finalScore, totalMatches, findings, words, stats) {
  if (totalMatches === 0 && finalScore < 10) {
    return 'No significant AI writing patterns detected. The text looks human-written.';
  }

  const level =
    finalScore >= 70
      ? 'heavily AI-generated'
      : finalScore >= 45
        ? 'moderately AI-influenced'
        : finalScore >= 20
          ? 'lightly AI-touched'
          : 'mostly human-sounding';

  const topPatterns = findings
    .sort((a, b) => b.matchCount * b.weight - a.matchCount * a.weight)
    .slice(0, 3)
    .map((f) => f.patternName);

  let summary = `Score: ${finalScore}/100 (${level}). Found ${totalMatches} matches across ${findings.length} pattern types in ${words} words.`;

  if (topPatterns.length > 0) {
    summary += ` Top issues: ${topPatterns.join(', ')}.`;
  }

  if (stats && stats.sentenceCount > 3) {
    if (stats.burstiness < 0.25) {
      summary += ' Sentence rhythm is very uniform (low burstiness) — typical of AI text.';
    }
    if (stats.typeTokenRatio < 0.4 && words > 100) {
      summary += ' Vocabulary diversity is low.';
    }
  }

  return summary;
}

// ─── Quick Score ─────────────────────────────────────────

/**
 * Quick score — returns just the number (0-100).
 */
function score(text) {
  return analyze(text).score;
}

// ─── Formatting ──────────────────────────────────────────

/**
 * Format analysis as human-readable terminal report.
 */
function formatReport(result) {
  const lines = [];

  lines.push('');
  lines.push('╔══════════════════════════════════════════════════╗');
  lines.push('║          AI WRITING PATTERN ANALYSIS             ║');
  lines.push('╚══════════════════════════════════════════════════╝');
  lines.push('');

  // Score bar
  const filled = Math.round(result.score / 5);
  const bar = '█'.repeat(filled) + '░'.repeat(20 - filled);
  lines.push(`  Score: ${result.score}/100  [${bar}]`);
  lines.push(
    `  Words: ${result.wordCount}  |  Matches: ${result.totalMatches}  |  Pattern: ${result.patternScore}  |  Uniformity: ${result.uniformityScore}`,
  );
  lines.push('');
  lines.push(`  ${result.summary}`);
  lines.push('');

  // Stats section
  if (result.stats) {
    const s = result.stats;
    lines.push('── Text Statistics ─────────────────────────────────');
    lines.push(`  Sentences: ${s.sentenceCount}  |  Paragraphs: ${s.paragraphCount}`);
    lines.push(`  Avg sentence length: ${s.avgSentenceLength} words (σ ${s.sentenceLengthStdDev})`);
    lines.push(`  Burstiness: ${s.burstiness} ${burstinessLabel(s.burstiness)}`);
    lines.push(
      `  Vocabulary diversity (TTR): ${s.typeTokenRatio} ${ttrLabel(s.typeTokenRatio, s.wordCount)}`,
    );
    lines.push(`  Function word ratio: ${s.functionWordRatio}`);
    lines.push(`  Trigram repetition: ${s.trigramRepetition}`);
    lines.push(`  Readability (FK grade): ${s.fleschKincaid}`);
    lines.push('');
  }

  // Category breakdown
  lines.push('── Categories ──────────────────────────────────────');
  for (const [, data] of Object.entries(result.categories)) {
    if (data.matches > 0) {
      lines.push(`  ${data.label}: ${data.matches} matches (${data.patternsDetected.join(', ')})`);
    }
  }
  lines.push('');

  // Findings detail
  if (result.findings.length > 0) {
    lines.push('── Findings ────────────────────────────────────────');
    for (const finding of result.findings) {
      lines.push('');
      lines.push(
        `  [${finding.patternId}] ${finding.patternName} (×${finding.matchCount}, weight: ${finding.weight})`,
      );
      lines.push(`      ${finding.description}`);
      for (const match of finding.matches) {
        const loc = match.line ? `L${match.line}:${match.column || ''}` : '';
        const preview =
          typeof match.match === 'string'
            ? match.match.substring(0, 80) + (match.match.length > 80 ? '...' : '')
            : '';
        const conf = match.confidence ? ` [${match.confidence}]` : '';
        lines.push(`      ${loc}: "${preview}"${conf}`);
        if (match.suggestion) {
          lines.push(`            → ${match.suggestion}`);
        }
      }
      if (finding.truncated) {
        lines.push(`      ... and ${finding.matchCount - finding.matches.length} more`);
      }
    }
  }

  lines.push('');
  lines.push('════════════════════════════════════════════════════');
  return lines.join('\n');
}

/**
 * Format analysis as markdown report.
 */
function formatMarkdown(result) {
  const lines = [];

  lines.push('# AI writing pattern analysis');
  lines.push('');
  lines.push(`**Score: ${result.score}/100** — ${scoreLabel(result.score)}`);
  lines.push('');
  lines.push(
    `Words: ${result.wordCount} | Matches: ${result.totalMatches} | Pattern score: ${result.patternScore} | Uniformity score: ${result.uniformityScore}`,
  );
  lines.push('');
  lines.push(result.summary);
  lines.push('');

  if (result.stats) {
    const s = result.stats;
    lines.push('## Text statistics');
    lines.push('');
    lines.push('| Metric | Value | Assessment |');
    lines.push('|--------|-------|------------|');
    lines.push(
      `| Avg sentence length | ${s.avgSentenceLength} words | ${s.avgSentenceLength > 25 ? 'Long' : s.avgSentenceLength < 12 ? 'Short' : 'Normal'} |`,
    );
    lines.push(
      `| Sentence variation | σ ${s.sentenceLengthStdDev} | ${s.sentenceLengthStdDev > 8 ? 'High (human-like)' : s.sentenceLengthStdDev < 4 ? 'Low (AI-like)' : 'Moderate'} |`,
    );
    lines.push(`| Burstiness | ${s.burstiness} | ${burstinessLabel(s.burstiness)} |`);
    lines.push(
      `| Vocabulary diversity | ${s.typeTokenRatio} | ${ttrLabel(s.typeTokenRatio, s.wordCount)} |`,
    );
    lines.push(
      `| Trigram repetition | ${s.trigramRepetition} | ${s.trigramRepetition > 0.1 ? 'High (AI-like)' : 'Normal'} |`,
    );
    lines.push(
      `| Readability | FK grade ${s.fleschKincaid} | ${s.fleschKincaid > 12 ? 'Academic' : s.fleschKincaid > 8 ? 'Standard' : 'Easy'} |`,
    );
    lines.push('');
  }

  if (result.findings.length > 0) {
    lines.push('## Findings');
    lines.push('');
    for (const finding of result.findings) {
      lines.push(`### ${finding.patternId}. ${finding.patternName} (×${finding.matchCount})`);
      lines.push(`*${finding.description}*`);
      lines.push('');
      for (const match of finding.matches) {
        const loc = match.line ? `Line ${match.line}` : '';
        lines.push(
          `- ${loc}: \`${typeof match.match === 'string' ? match.match.substring(0, 80) : ''}\``,
        );
        if (match.suggestion) lines.push(`  - ${match.suggestion}`);
      }
      lines.push('');
    }
  }

  return lines.join('\n');
}

/**
 * Format analysis as JSON.
 */
function formatJSON(result) {
  return JSON.stringify(result, null, 2);
}

// ─── Label Helpers ───────────────────────────────────────

function scoreLabel(s) {
  if (s >= 70) return 'Heavily AI-generated';
  if (s >= 45) return 'Moderately AI-influenced';
  if (s >= 20) return 'Lightly AI-touched';
  return 'Mostly human-sounding';
}

function burstinessLabel(b) {
  if (b >= 0.7) return '(high — human-like)';
  if (b >= 0.45) return '(moderate)';
  if (b >= 0.25) return '(low — somewhat uniform)';
  return '(very low — AI-like uniformity)';
}

function ttrLabel(ttr, wc) {
  if (wc < 100) return '(too short to assess)';
  if (ttr >= 0.6) return '(high — diverse vocabulary)';
  if (ttr >= 0.45) return '(moderate)';
  return '(low — repetitive vocabulary)';
}

function emptyResult() {
  return {
    score: 0,
    patternScore: 0,
    uniformityScore: 0,
    totalMatches: 0,
    wordCount: 0,
    stats: null,
    categories: {},
    findings: [],
    summary: 'No text provided.',
  };
}

// ─── Exports ─────────────────────────────────────────────

module.exports = {
  analyze,
  score,
  calculatePatternScore,
  calculateCompositeScore,
  formatReport,
  formatMarkdown,
  formatJSON,
  CATEGORY_LABELS,
};
