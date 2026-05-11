/**
 * statistics.test.js — Tests for the text statistics engine (stats.js).
 */

import { describe, it, expect } from 'vitest';
import {
  computeStats,
  computeUniformityScore,
  computeNgramRepetition,
  splitSentences,
  tokenize,
  estimateSyllables,
} from '../src/stats.js';

// ─── Tokenize ────────────────────────────────────────────

describe('tokenize', () => {
  it('splits text into lowercase words', () => {
    const result = tokenize('Hello World');
    expect(result).toContain('hello');
    expect(result).toContain('world');
  });

  it('strips punctuation', () => {
    const result = tokenize('Hello, world! How are you?');
    expect(result).toContain('hello');
    expect(result).not.toContain('hello,');
  });

  it('handles empty input', () => {
    expect(tokenize('')).toEqual([]);
  });
});

// ─── Sentence Splitting ─────────────────────────────────

describe('splitSentences', () => {
  it('splits on periods', () => {
    const result = splitSentences('Hello world. How are you. Fine.');
    expect(result.length).toBeGreaterThanOrEqual(2);
  });

  it('splits on question marks and exclamation points', () => {
    const result = splitSentences('What? Really! Yes.');
    expect(result.length).toBeGreaterThanOrEqual(2);
  });

  it('handles single sentence', () => {
    const result = splitSentences('Just one sentence.');
    expect(result.length).toBe(1);
  });

  it('handles abbreviations', () => {
    const result = splitSentences('Dr. Smith went home. Mr. Jones followed.');
    // Should split into 2 sentences, not 4
    expect(result.length).toBe(2);
  });
});

// ─── Syllable Estimation ─────────────────────────────────

describe('estimateSyllables', () => {
  it('counts single-syllable words', () => {
    expect(estimateSyllables('cat')).toBe(1);
    expect(estimateSyllables('the')).toBe(1);
  });

  it('counts multi-syllable words', () => {
    expect(estimateSyllables('beautiful')).toBeGreaterThanOrEqual(2);
    expect(estimateSyllables('computer')).toBeGreaterThanOrEqual(2);
  });

  it('returns at least 1 for any word', () => {
    expect(estimateSyllables('a')).toBeGreaterThanOrEqual(1);
    expect(estimateSyllables('xyz')).toBeGreaterThanOrEqual(1);
  });
});

// ─── N-gram Repetition ──────────────────────────────────

describe('computeNgramRepetition', () => {
  it('returns 0 for short input', () => {
    expect(computeNgramRepetition(['the', 'cat'], 3)).toBe(0);
  });

  it('detects repeated trigrams', () => {
    const words = 'the cat sat the cat sat the cat sat'.split(' ');
    const rep = computeNgramRepetition(words, 3);
    expect(rep).toBeGreaterThan(0);
  });

  it('returns 0 for all unique trigrams', () => {
    const words = 'one two three four five six seven eight nine ten'.split(' ');
    const rep = computeNgramRepetition(words, 3);
    expect(rep).toBe(0);
  });
});

// ─── computeStats ────────────────────────────────────────

describe('computeStats', () => {
  it('returns valid structure for normal text', () => {
    const text = 'This is a test. Another sentence here. And a third one too.';
    const stats = computeStats(text);

    expect(stats).toHaveProperty('wordCount');
    expect(stats).toHaveProperty('sentenceCount');
    expect(stats).toHaveProperty('burstiness');
    expect(stats).toHaveProperty('typeTokenRatio');
    expect(stats).toHaveProperty('functionWordRatio');
    expect(stats).toHaveProperty('fleschKincaid');
    expect(stats).toHaveProperty('paragraphCount');
    expect(stats).toHaveProperty('trigramRepetition');
  });

  it('handles empty input', () => {
    const stats = computeStats('');
    expect(stats.wordCount).toBe(0);
    expect(stats.sentenceCount).toBe(0);
  });

  it('handles null input', () => {
    const stats = computeStats(null);
    expect(stats.wordCount).toBe(0);
  });

  // Sentence stats
  it('counts sentences correctly', () => {
    const text = 'First sentence. Second sentence. Third sentence.';
    const stats = computeStats(text);
    expect(stats.sentenceCount).toBe(3);
  });

  it('computes average sentence length', () => {
    const text = 'Short one. This is a bit longer sentence.';
    const stats = computeStats(text);
    expect(stats.avgSentenceLength).toBeGreaterThan(0);
  });

  it('computes burstiness', () => {
    // Very uniform sentences → low burstiness
    const uniform = 'The cat sat down. The dog ran fast. The cow ate hay. The fox was sly.';
    const uniformStats = computeStats(uniform);

    // Very varied sentences → higher burstiness
    const varied =
      'Hi. This is a much longer sentence with many more words in it that goes on and on for a while. OK.';
    const variedStats = computeStats(varied);

    expect(variedStats.burstiness).toBeGreaterThan(uniformStats.burstiness);
  });

  // Vocabulary stats
  it('counts total and unique words', () => {
    const text = 'The cat and the dog and the bird.';
    const stats = computeStats(text);
    expect(stats.wordCount).toBeGreaterThan(0);
    expect(stats.uniqueWordCount).toBeLessThanOrEqual(stats.wordCount);
  });

  it('computes type-token ratio', () => {
    const repetitive = 'the the the the dog the the the the cat';
    const repStats = computeStats(repetitive);

    const diverse = 'cats dogs birds fish horses cows sheep goats pigs';
    const divStats = computeStats(diverse);

    expect(divStats.typeTokenRatio).toBeGreaterThan(repStats.typeTokenRatio);
  });

  // Paragraph stats
  it('counts paragraphs', () => {
    const text = 'Paragraph one.\n\nParagraph two.\n\nParagraph three.';
    const stats = computeStats(text);
    expect(stats.paragraphCount).toBe(3);
  });

  // Readability
  it('computes Flesch-Kincaid grade level', () => {
    const text = 'The cat sat on the mat. The dog ate the bone. The bird flew away.';
    const stats = computeStats(text);
    expect(stats.fleschKincaid).toBeDefined();
    expect(typeof stats.fleschKincaid).toBe('number');
  });

  // Function word ratio
  it('computes function word ratio', () => {
    const text = 'The cat is in the box with the hat on the mat.';
    const stats = computeStats(text);
    expect(stats.functionWordRatio).toBeGreaterThan(0);
    expect(stats.functionWordRatio).toBeLessThan(1);
  });
});

// ─── computeUniformityScore ──────────────────────────────

describe('computeUniformityScore', () => {
  it('returns 0 for empty stats', () => {
    const stats = computeStats('');
    expect(computeUniformityScore(stats)).toBe(0);
  });

  it('returns higher score for uniform text', () => {
    // Uniform sentences — should score higher (more AI-like)
    const uniform =
      'This is a sentence. Here is another one. And there is one more. Plus yet another sentence. One final sentence too.';
    const uniformStats = computeStats(uniform);
    const uniformScore = computeUniformityScore(uniformStats);

    // Varied sentences — should score lower (more human-like)
    const varied =
      'Short. This is a much much longer sentence that really goes on for a while with many more words. Medium one here. Yes. And then this one wraps up with a moderate number of words.';
    const variedStats = computeStats(varied);
    const variedScore = computeUniformityScore(variedStats);

    expect(uniformScore).toBeGreaterThanOrEqual(variedScore);
  });

  it('returns a number between 0 and 100', () => {
    const text = 'The cat sat. The dog ran. The bird flew. The fish swam.';
    const stats = computeStats(text);
    const score = computeUniformityScore(stats);
    expect(score).toBeGreaterThanOrEqual(0);
    expect(score).toBeLessThanOrEqual(100);
  });
});
