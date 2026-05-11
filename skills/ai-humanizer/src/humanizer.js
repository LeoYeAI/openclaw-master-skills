/**
 * humanizer.js — Humanization engine.
 *
 * Takes analysis results and produces actionable rewrite suggestions.
 * Includes both:
 *   - autoFix: safe mechanical transforms (curly quotes, filler phrases, chatbot artifacts)
 *   - humanize: full suggestion report with prioritized guidance
 *
 * Humanization techniques based on 2025 research:
 *   - Sentence length variation (mix short with long)
 *   - Burstiness injection (fragments, questions, varied rhythm)
 *   - Concrete specificity (replace vague with numbers/names/dates)
 *   - First-person injection (where appropriate)
 *   - Opinion injection (humans have preferences, AI is neutral)
 */

const { analyze } = require('./analyzer');

// ─── Automatic Fixes ─────────────────────────────────────

/**
 * Apply safe, mechanical fixes that don't require judgment.
 * Only transforms where the "right" answer is unambiguous.
 *
 * @param {string} text — Input text
 * @returns {{ text: string, fixes: string[] }}
 */
function autoFix(text) {
  let result = text;
  const fixes = [];

  // Curly quotes → straight quotes
  if (/[\u201C\u201D]/.test(result)) {
    result = result.replace(/[\u201C\u201D]/g, '"');
    fixes.push('Replaced curly double quotes with straight quotes');
  }
  if (/[\u2018\u2019]/.test(result)) {
    result = result.replace(/[\u2018\u2019]/g, "'");
    fixes.push('Replaced curly single quotes with straight quotes');
  }

  // Filler phrase replacements (unambiguous)
  const safeFills = [
    { from: /\bin order to\b/gi, to: 'to', label: '"in order to" → "to"' },
    {
      from: /\bdue to the fact that\b/gi,
      to: 'because',
      label: '"due to the fact that" → "because"',
    },
    { from: /\bat this point in time\b/gi, to: 'now', label: '"at this point in time" → "now"' },
    { from: /\bin the event that\b/gi, to: 'if', label: '"in the event that" → "if"' },
    { from: /\bhas the ability to\b/gi, to: 'can', label: '"has the ability to" → "can"' },
    { from: /\bfor the purpose of\b/gi, to: 'to', label: '"for the purpose of" → "to"' },
    { from: /\bfirst and foremost\b/gi, to: 'first', label: '"first and foremost" → "first"' },
    {
      from: /\bin light of the fact that\b/gi,
      to: 'because',
      label: '"in light of the fact that" → "because"',
    },
    { from: /\bin the realm of\b/gi, to: 'in', label: '"in the realm of" → "in"' },
    { from: /\butilize\b/gi, to: 'use', label: '"utilize" → "use"' },
    { from: /\butilizing\b/gi, to: 'using', label: '"utilizing" → "using"' },
    { from: /\butilization\b/gi, to: 'use', label: '"utilization" → "use"' },
  ];

  for (const { from, to, label } of safeFills) {
    if (from.test(result)) {
      result = result.replace(from, to);
      fixes.push(label);
    }
  }

  // Chatbot artifact removal (start/end of text)
  const chatbotStart = [
    /^(Here is|Here's) (a |an |the )?(comprehensive |brief |quick )?(overview|summary|breakdown|list|guide|explanation|look)[^.]*\.\s*/i,
    /^(Of course|Certainly|Absolutely|Sure)!\s*/i,
    /^(Great|Excellent|Good|Wonderful|Fantastic) question!\s*/i,
    /^(That's|That is) a (great|excellent|good|wonderful|fantastic) (question|point)!\s*/i,
  ];
  for (const regex of chatbotStart) {
    if (regex.test(result)) {
      result = result.replace(regex, '');
      fixes.push('Removed chatbot opening artifact');
    }
  }

  const chatbotEnd = [
    /\s*(I hope this helps|Let me know if you('d| would) like|Feel free to|Don't hesitate to|Is there anything else)[^.]*[.!]\s*$/i,
    /\s*Happy to help[.!]?\s*$/i,
  ];
  for (const regex of chatbotEnd) {
    if (regex.test(result)) {
      result = result.replace(regex, '');
      fixes.push('Removed chatbot closing artifact');
    }
  }

  result = result.trim();
  return { text: result, fixes };
}

// ─── Suggestion Engine ───────────────────────────────────

/**
 * Generate humanization suggestions.
 *
 * @param {string} text    — Input text
 * @param {object} opts    — Options:
 *   - autofix {boolean}   Apply safe auto-fixes
 *   - verbose {boolean}   Show all matches
 *   - includeStats {boolean}  Include statistical suggestions
 * @returns {object}       — Suggestions report
 */
function humanize(text, opts = {}) {
  const { autofix = false, includeStats = true } = opts;

  const analysis = analyze(text, { verbose: true, includeStats });

  // Group by priority
  const critical = []; // weight 4-5: dead giveaways
  const important = []; // weight 2-3: noticeable
  const minor = []; // weight 1: subtle

  for (const finding of analysis.findings) {
    const suggestions = finding.matches.map((m) => ({
      pattern: finding.patternName,
      patternId: finding.patternId,
      category: finding.category,
      weight: finding.weight,
      text: m.match,
      line: m.line,
      column: m.column,
      suggestion: m.suggestion,
      confidence: m.confidence || 'high',
    }));

    if (finding.weight >= 4) critical.push(...suggestions);
    else if (finding.weight >= 2) important.push(...suggestions);
    else minor.push(...suggestions);
  }

  // Auto-fix
  let fixedText = null;
  let appliedFixes = [];
  if (autofix) {
    const result = autoFix(text);
    fixedText = result.text;
    appliedFixes = result.fixes;
  }

  // Build guidance (pattern-based + statistical)
  const guidance = buildGuidance(analysis);
  const styleTips = includeStats && analysis.stats ? buildStyleTips(analysis.stats) : [];

  return {
    score: analysis.score,
    patternScore: analysis.patternScore,
    uniformityScore: analysis.uniformityScore,
    wordCount: analysis.wordCount,
    totalIssues: analysis.totalMatches,
    stats: analysis.stats,
    critical,
    important,
    minor,
    autofix: autofix ? { text: fixedText, fixes: appliedFixes } : null,
    guidance,
    styleTips,
  };
}

/**
 * Build pattern-based guidance.
 */
function buildGuidance(analysis) {
  const tips = [];
  const ids = new Set(analysis.findings.map((f) => f.patternId));

  if (ids.has(1) || ids.has(4)) {
    tips.push(
      'Replace inflated/promotional language with concrete facts. What specifically happened? Give dates, numbers, names.',
    );
  }
  if (ids.has(3)) {
    tips.push(
      'Cut trailing -ing phrases. If the point matters enough to mention, give it its own sentence.',
    );
  }
  if (ids.has(5)) {
    tips.push('Name your sources. "Experts say" means nothing — who said it, when, and where?');
  }
  if (ids.has(6)) {
    tips.push(
      'Replace formulaic "despite challenges" sections with specific problems and concrete outcomes.',
    );
  }
  if (ids.has(7)) {
    tips.push(
      'Swap AI vocabulary for plainer words. "Delve" → "look at". "Tapestry" → (be specific). "Showcase" → "show".',
    );
  }
  if (ids.has(8)) {
    tips.push('Use "is" and "has" freely. "Serves as" and "boasts" are needlessly fancy.');
  }
  if (ids.has(9)) {
    tips.push('Drop "not just X, it\'s Y" frames. Just say what the thing is.');
  }
  if (ids.has(10)) {
    tips.push("Break up triads. You don't always need three of everything.");
  }
  if (ids.has(13)) {
    tips.push('Ease up on em dashes. Use commas, periods, or parentheses for variety.');
  }
  if (ids.has(14) || ids.has(15)) {
    tips.push('Strip mechanical bold formatting and inline-header lists. Let prose do the work.');
  }
  if (ids.has(17)) {
    tips.push('Remove emojis from professional text. They signal chatbot output.');
  }
  if (ids.has(19) || ids.has(21)) {
    tips.push(
      'Remove chatbot filler ("I hope this helps!", "Great question!"). Just deliver the content.',
    );
  }
  if (ids.has(20)) {
    tips.push('Delete knowledge-cutoff disclaimers. Either research it or leave it out.');
  }
  if (ids.has(22) || ids.has(23)) {
    tips.push('Trim filler and hedging. "In order to" → "to". One qualifier per claim is enough.');
  }
  if (ids.has(24)) {
    tips.push(
      'Cut generic conclusions. End with a specific fact instead of "the future looks bright".',
    );
  }

  if (analysis.score >= 50) {
    tips.push(
      "Consider rewriting from scratch. When AI patterns are this dense, patching individual phrases isn't enough — the structure itself needs rethinking.",
    );
  }

  return tips;
}

/**
 * Build statistical style tips based on text metrics.
 * These suggest structural improvements beyond word choice.
 */
function buildStyleTips(stats) {
  const tips = [];

  // Burstiness
  if (stats.burstiness < 0.25 && stats.sentenceCount > 4) {
    tips.push({
      metric: 'burstiness',
      value: stats.burstiness,
      tip: 'Sentence rhythm is very uniform. Mix short punchy sentences (3-8 words) with longer flowing ones (20+). Fragments work too. Like this.',
    });
  }

  // Sentence length variation
  if (stats.sentenceLengthVariation < 0.3 && stats.sentenceCount > 4) {
    tips.push({
      metric: 'sentenceLengthVariation',
      value: stats.sentenceLengthVariation,
      tip: `Sentences are all roughly ${Math.round(stats.avgSentenceLength)} words. Vary your rhythm — alternate between short and long.`,
    });
  }

  // Very long average sentences
  if (stats.avgSentenceLength > 28) {
    tips.push({
      metric: 'avgSentenceLength',
      value: stats.avgSentenceLength,
      tip: 'Average sentence is quite long. Break some into shorter ones. Not every thought needs a subordinate clause.',
    });
  }

  // Low vocabulary diversity
  if (stats.typeTokenRatio < 0.4 && stats.wordCount > 100) {
    tips.push({
      metric: 'typeTokenRatio',
      value: stats.typeTokenRatio,
      tip: "Vocabulary is repetitive. Try using more varied word choices — but don't synonym-cycle (that's also an AI tell).",
    });
  }

  // High trigram repetition
  if (stats.trigramRepetition > 0.1 && stats.wordCount > 100) {
    tips.push({
      metric: 'trigramRepetition',
      value: stats.trigramRepetition,
      tip: 'Repeated 3-word phrases detected. Vary your sentence structures.',
    });
  }

  // Add humanization techniques if text scores poorly
  if (tips.length >= 2) {
    tips.push({
      metric: 'general',
      value: null,
      tip: "Try the read-aloud test: read the text out loud. If it sounds weird or robotic, rewrite those parts until they sound like something you'd actually say.",
    });
    tips.push({
      metric: 'general',
      value: null,
      tip: 'Add first-person perspective where it fits: "I found", "We noticed", "In my experience". Real humans write from a point of view.',
    });
  }

  return tips;
}

// ─── Report Formatting ──────────────────────────────────

/**
 * Format humanization suggestions as readable terminal output.
 */
function formatSuggestions(result) {
  const lines = [];

  lines.push('');
  lines.push('╔══════════════════════════════════════════════════╗');
  lines.push('║           HUMANIZATION SUGGESTIONS               ║');
  lines.push('╚══════════════════════════════════════════════════╝');
  lines.push('');

  const filled = Math.round(result.score / 5);
  const bar = '█'.repeat(filled) + '░'.repeat(20 - filled);
  lines.push(`  AI Score: ${result.score}/100  [${bar}]`);
  lines.push(
    `  Issues: ${result.totalIssues}  |  Pattern: ${result.patternScore}  |  Uniformity: ${result.uniformityScore}`,
  );
  lines.push('');

  if (result.critical.length > 0) {
    lines.push('── CRITICAL (dead giveaways) ───────────────────────');
    for (const s of result.critical) {
      lines.push(`  L${s.line}: [${s.pattern}] "${truncate(s.text, 60)}" [${s.confidence}]`);
      lines.push(`       → ${s.suggestion}`);
    }
    lines.push('');
  }

  if (result.important.length > 0) {
    lines.push('── IMPORTANT (noticeable patterns) ─────────────────');
    for (const s of result.important.slice(0, 15)) {
      lines.push(`  L${s.line}: [${s.pattern}] "${truncate(s.text, 60)}"`);
      lines.push(`       → ${s.suggestion}`);
    }
    if (result.important.length > 15) {
      lines.push(`  ... and ${result.important.length - 15} more`);
    }
    lines.push('');
  }

  if (result.minor.length > 0) {
    lines.push('── MINOR (subtle tells) ────────────────────────────');
    for (const s of result.minor.slice(0, 10)) {
      lines.push(`  L${s.line}: [${s.pattern}] "${truncate(s.text, 60)}"`);
      lines.push(`       → ${s.suggestion}`);
    }
    if (result.minor.length > 10) {
      lines.push(`  ... and ${result.minor.length - 10} more`);
    }
    lines.push('');
  }

  if (result.autofix) {
    lines.push('── AUTO-FIXES APPLIED ──────────────────────────────');
    for (const fix of result.autofix.fixes) {
      lines.push(`  ✓ ${fix}`);
    }
    lines.push('');
  }

  if (result.guidance.length > 0) {
    lines.push('── GUIDANCE ────────────────────────────────────────');
    for (const tip of result.guidance) {
      lines.push(`  • ${tip}`);
    }
    lines.push('');
  }

  if (result.styleTips.length > 0) {
    lines.push('── STYLE TIPS (statistical) ────────────────────────');
    for (const t of result.styleTips) {
      const metric = t.value !== null ? ` [${t.metric}: ${t.value}]` : '';
      lines.push(`  ◦ ${t.tip}${metric}`);
    }
    lines.push('');
  }

  lines.push('════════════════════════════════════════════════════');
  return lines.join('\n');
}

function truncate(str, len) {
  if (typeof str !== 'string') return '';
  return str.length > len ? `${str.substring(0, len)}...` : str;
}

// ─── Exports ─────────────────────────────────────────────

module.exports = {
  humanize,
  autoFix,
  formatSuggestions,
  buildGuidance,
  buildStyleTips,
};
