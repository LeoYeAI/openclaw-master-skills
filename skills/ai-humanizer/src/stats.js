/**
 * stats.js — Text statistics engine.
 *
 * Computes stylometric features that distinguish AI from human writing.
 * Based on academic research (Copyleaks arxiv 2503.01659v1, StyloAI):
 *
 *   - Sentence length statistics (mean, std dev, variation coefficient)
 *   - Burstiness score (humans write in bursts/lulls; AI is uniform)
 *   - Vocabulary diversity (type-token ratio)
 *   - Function word ratio
 *   - N-gram repetition density
 *   - Readability metrics (Flesch-Kincaid)
 *   - Paragraph structure statistics
 */

const { FUNCTION_WORDS } = require('./vocabulary');

// ─── Sentence Splitting ─────────────────────────────────

/**
 * Split text into sentences. Handles abbreviations and edge cases better
 * than a naive split on period.
 */
function splitSentences(text) {
  // Handle common abbreviations that shouldn't split
  const cleaned = text
    .replace(/\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|etc|vs|approx|dept|est|vol)\./gi, '$1\u2024') // temp replace
    .replace(/\b([A-Z])\./g, '$1\u2024') // initials: "J. K. Rowling"
    .replace(/\b(\d+)\./g, '$1\u2024'); // numbered lists

  const sentences = cleaned
    .split(/(?<=[.!?])\s+(?=[A-Z"'\u201C])|(?<=[.!?])$/)
    .map((s) => s.replace(/\u2024/g, '.').trim())
    .filter((s) => s.length > 0);

  return sentences;
}

// ─── Core Statistics ─────────────────────────────────────

/**
 * Tokenize text into words (lowercase, stripped of punctuation).
 */
function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s'-]/g, ' ')
    .split(/\s+/)
    .filter((w) => w.length > 0);
}

/**
 * Compute all text statistics.
 *
 * @param {string} text — Input text
 * @returns {object}    — Statistics object
 */
function computeStats(text) {
  if (!text || typeof text !== 'string' || text.trim().length === 0) {
    return emptyStats();
  }

  const words = tokenize(text);
  const sentences = splitSentences(text);
  const paragraphs = text.split(/\n\s*\n/).filter((p) => p.trim().length > 0);

  if (words.length === 0) return emptyStats();

  // ── Word-level stats ────────────────────────────────
  const wordCount = words.length;
  const uniqueWords = new Set(words);
  const typeTokenRatio = uniqueWords.size / wordCount;

  // Average word length
  const avgWordLength = words.reduce((sum, w) => sum + w.length, 0) / wordCount;

  // ── Sentence-level stats ────────────────────────────
  const sentenceLengths = sentences.map((s) => tokenize(s).length).filter((n) => n > 0);
  const sentenceCount = sentenceLengths.length;

  let avgSentenceLength = 0;
  let sentenceLengthStdDev = 0;
  let sentenceLengthVariation = 0;
  let burstiness = 0;

  if (sentenceCount > 1) {
    avgSentenceLength = sentenceLengths.reduce((a, b) => a + b, 0) / sentenceCount;

    // Standard deviation
    const variance =
      sentenceLengths.reduce((sum, len) => sum + Math.pow(len - avgSentenceLength, 2), 0) /
      sentenceCount;
    sentenceLengthStdDev = Math.sqrt(variance);

    // Coefficient of variation (std dev / mean) — our burstiness proxy
    sentenceLengthVariation = avgSentenceLength > 0 ? sentenceLengthStdDev / avgSentenceLength : 0;

    // Burstiness: based on consecutive sentence length differences
    // High burstiness = human (lots of variation between consecutive sentences)
    // Low burstiness = AI (uniform sentence length throughout)
    let consecutiveDiffSum = 0;
    for (let i = 1; i < sentenceLengths.length; i++) {
      consecutiveDiffSum += Math.abs(sentenceLengths[i] - sentenceLengths[i - 1]);
    }
    const avgConsecutiveDiff = consecutiveDiffSum / (sentenceLengths.length - 1);
    burstiness = avgSentenceLength > 0 ? avgConsecutiveDiff / avgSentenceLength : 0;
  } else if (sentenceCount === 1) {
    avgSentenceLength = sentenceLengths[0];
  }

  // ── Function word ratio ─────────────────────────────
  const functionWordSet = new Set(FUNCTION_WORDS);
  const functionWordCount = words.filter((w) => functionWordSet.has(w)).length;
  const functionWordRatio = functionWordCount / wordCount;

  // ── N-gram repetition ───────────────────────────────
  const trigramRepetition = computeNgramRepetition(words, 3);

  // ── Paragraph stats ─────────────────────────────────
  const paragraphCount = paragraphs.length;
  const avgParagraphLength =
    paragraphCount > 0
      ? paragraphs.reduce((sum, p) => sum + tokenize(p).length, 0) / paragraphCount
      : 0;

  // ── Readability (Flesch-Kincaid Grade Level approximation) ──
  const syllableCount = words.reduce((sum, w) => sum + estimateSyllables(w), 0);
  const fleschKincaid =
    sentenceCount > 0
      ? 0.39 * (wordCount / sentenceCount) + 11.8 * (syllableCount / wordCount) - 15.59
      : 0;

  return {
    wordCount,
    uniqueWordCount: uniqueWords.size,
    sentenceCount,
    paragraphCount,
    avgWordLength: round(avgWordLength),
    avgSentenceLength: round(avgSentenceLength),
    sentenceLengthStdDev: round(sentenceLengthStdDev),
    sentenceLengthVariation: round(sentenceLengthVariation), // coefficient of variation
    burstiness: round(burstiness),
    typeTokenRatio: round(typeTokenRatio),
    functionWordRatio: round(functionWordRatio),
    trigramRepetition: round(trigramRepetition),
    avgParagraphLength: round(avgParagraphLength),
    fleschKincaid: round(fleschKincaid),
    sentenceLengths,
  };
}

/**
 * Compute n-gram repetition rate.
 * Returns the fraction of n-grams that appear more than once.
 * AI text tends to reuse similar n-grams more than human text.
 */
function computeNgramRepetition(words, n) {
  if (words.length < n) return 0;

  const ngrams = {};
  for (let i = 0; i <= words.length - n; i++) {
    const gram = words.slice(i, i + n).join(' ');
    ngrams[gram] = (ngrams[gram] || 0) + 1;
  }

  const totalNgrams = Object.keys(ngrams).length;
  if (totalNgrams === 0) return 0;

  const repeated = Object.values(ngrams).filter((c) => c > 1).length;
  return repeated / totalNgrams;
}

/**
 * Estimate syllable count for a word (English heuristic).
 */
function estimateSyllables(word) {
  word = word.toLowerCase().replace(/[^a-z]/g, '');
  if (word.length <= 3) return 1;

  // Count vowel groups
  const vowelGroups = word.match(/[aeiouy]+/g);
  let count = vowelGroups ? vowelGroups.length : 1;

  // Subtract silent e
  if (word.endsWith('e') && !word.endsWith('le')) count--;
  // Add for -ed that creates syllable
  if (word.endsWith('ed') && word.length > 3 && !/[aeiouy]ed$/.test(word)) count--;

  return Math.max(count, 1);
}

/**
 * Compute a "uniformity score" from text stats.
 * Higher = more uniform/AI-like. Lower = more varied/human-like.
 * Range: 0-100.
 */
function computeUniformityScore(stats) {
  if (stats.wordCount === 0) return 0;

  let score = 0;

  // Low burstiness = more AI-like (max 25 points)
  // Human burstiness is typically 0.5-1.0, AI is 0.1-0.3
  if (stats.burstiness < 0.2) score += 25;
  else if (stats.burstiness < 0.35) score += 18;
  else if (stats.burstiness < 0.5) score += 10;
  else if (stats.burstiness < 0.65) score += 5;

  // Low sentence length variation = more AI-like (max 25 points)
  // Human CoV is typically 0.4-0.8, AI is 0.15-0.35
  if (stats.sentenceLengthVariation < 0.2) score += 25;
  else if (stats.sentenceLengthVariation < 0.35) score += 18;
  else if (stats.sentenceLengthVariation < 0.5) score += 10;
  else if (stats.sentenceLengthVariation < 0.65) score += 5;

  // Low type-token ratio = more repetitive/AI-like (max 20 points)
  // But very short texts naturally have high TTR, so only penalize for longer texts
  if (stats.wordCount > 100) {
    if (stats.typeTokenRatio < 0.35) score += 20;
    else if (stats.typeTokenRatio < 0.45) score += 12;
    else if (stats.typeTokenRatio < 0.55) score += 5;
  }

  // High trigram repetition = more AI-like (max 15 points)
  if (stats.trigramRepetition > 0.15) score += 15;
  else if (stats.trigramRepetition > 0.1) score += 10;
  else if (stats.trigramRepetition > 0.05) score += 5;

  // Abnormally uniform paragraph lengths (max 15 points)
  // Only check if we have multiple paragraphs
  if (stats.paragraphCount >= 3 && stats.sentenceCount > 5) {
    // Check if all paragraphs are similar length
    // Use sentence length uniformity as a proxy for paragraph uniformity
    if (stats.sentenceLengthStdDev < 3 && stats.avgSentenceLength > 10) {
      score += 15; // Very uniform sentence lengths with moderate length = AI
    }
  }

  return Math.min(score, 100);
}

function emptyStats() {
  return {
    wordCount: 0,
    uniqueWordCount: 0,
    sentenceCount: 0,
    paragraphCount: 0,
    avgWordLength: 0,
    avgSentenceLength: 0,
    sentenceLengthStdDev: 0,
    sentenceLengthVariation: 0,
    burstiness: 0,
    typeTokenRatio: 0,
    functionWordRatio: 0,
    trigramRepetition: 0,
    avgParagraphLength: 0,
    fleschKincaid: 0,
    sentenceLengths: [],
  };
}

function round(n) {
  return Math.round(n * 1000) / 1000;
}

// ─── Exports ─────────────────────────────────────────────

module.exports = {
  computeStats,
  computeUniformityScore,
  computeNgramRepetition,
  splitSentences,
  tokenize,
  estimateSyllables,
};
