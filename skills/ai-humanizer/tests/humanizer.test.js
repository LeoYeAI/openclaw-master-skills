/**
 * humanizer.test.js — Tests for the humanization engine.
 */

import { describe, it, expect } from 'vitest';
import { humanize, autoFix, formatSuggestions } from '../src/humanizer.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function loadFixture(name) {
  return fs.readFileSync(path.join(__dirname, 'fixtures', name), 'utf-8');
}

// ─── autoFix ─────────────────────────────────────────────

describe('autoFix', () => {
  it('replaces curly double quotes with straight quotes', () => {
    const { text, fixes } = autoFix('He said \u201Chello\u201D to her.');
    expect(text).toBe('He said "hello" to her.');
    expect(fixes.length).toBeGreaterThan(0);
  });

  it('replaces curly single quotes with straight quotes', () => {
    const { text } = autoFix('It\u2019s a fine day.');
    expect(text).toBe("It's a fine day.");
  });

  it('replaces "in order to" with "to"', () => {
    const { text } = autoFix('In order to succeed, we must work hard.');
    expect(text).toContain('to succeed');
    expect(text).not.toContain('In order to');
  });

  it('replaces "due to the fact that" with "because"', () => {
    const { text } = autoFix('We stopped due to the fact that it was raining.');
    expect(text).toContain('because');
    expect(text).not.toContain('due to the fact that');
  });

  it('replaces "at this point in time" with "now"', () => {
    const { text } = autoFix('At this point in time, we are ready.');
    expect(text).toContain('now');
  });

  it('replaces "in the event that" with "if"', () => {
    const { text } = autoFix('In the event that you need help, call us.');
    expect(text).toContain('if');
    expect(text).not.toContain('In the event that');
  });

  it('replaces "has the ability to" with "can"', () => {
    const { text } = autoFix('The system has the ability to process data.');
    expect(text).toContain('can');
  });

  it('removes chatbot opening artifacts', () => {
    const { text, fixes } = autoFix('Great question! Here is the answer to your question.');
    expect(text).not.toContain('Great question!');
    expect(fixes.some((f) => f.includes('chatbot'))).toBe(true);
  });

  it('removes chatbot closing artifacts', () => {
    const { text, fixes } = autoFix('The answer is 42. I hope this helps!');
    expect(text).not.toContain('I hope this helps');
    expect(fixes.some((f) => f.includes('chatbot'))).toBe(true);
  });

  it('handles text with no fixable issues', () => {
    const { text, fixes } = autoFix('The cat sat on the mat.');
    expect(text).toBe('The cat sat on the mat.');
    expect(fixes.length).toBe(0);
  });

  it('applies multiple fixes in one pass', () => {
    const input =
      'Great question! In order to help, due to the fact that you asked, here\u2019s the answer. I hope this helps!';
    const { text, fixes } = autoFix(input);
    expect(fixes.length).toBeGreaterThanOrEqual(3);
    expect(text).not.toContain('In order to');
    expect(text).not.toContain('\u2019');
  });
});

// ─── humanize ────────────────────────────────────────────

describe('humanize', () => {
  it('returns a valid suggestion object', () => {
    const result = humanize('This is a testament to great things.');
    expect(result).toHaveProperty('score');
    expect(result).toHaveProperty('critical');
    expect(result).toHaveProperty('important');
    expect(result).toHaveProperty('minor');
    expect(result).toHaveProperty('guidance');
    expect(result).toHaveProperty('totalIssues');
    expect(result).toHaveProperty('styleTips');
  });

  it('categorizes issues by severity', () => {
    const text = loadFixture('ai-sample-1.txt');
    const result = humanize(text);
    expect(result.critical.length).toBeGreaterThan(0);
    expect(result.important.length).toBeGreaterThan(0);
  });

  it('provides guidance tips', () => {
    const text = loadFixture('ai-sample-1.txt');
    const result = humanize(text);
    expect(result.guidance.length).toBeGreaterThan(0);
    expect(result.guidance.some((g) => typeof g === 'string' && g.length > 10)).toBe(true);
  });

  it('returns autofix results when requested', () => {
    const text = 'In order to help, I hope this helps!';
    const result = humanize(text, { autofix: true });
    expect(result.autofix).not.toBeNull();
    expect(result.autofix.text).not.toContain('In order to');
    expect(result.autofix.fixes.length).toBeGreaterThan(0);
  });

  it('returns null autofix when not requested', () => {
    const result = humanize('Some text here.', { autofix: false });
    expect(result.autofix).toBeNull();
  });

  it('scores human text low', () => {
    const text = loadFixture('human-sample-1.txt');
    const result = humanize(text);
    expect(result.score).toBeLessThan(30);
  });

  it('each suggestion has required fields', () => {
    const text = loadFixture('ai-sample-1.txt');
    const result = humanize(text);
    const allSuggestions = [...result.critical, ...result.important, ...result.minor];
    for (const s of allSuggestions) {
      expect(s).toHaveProperty('pattern');
      expect(s).toHaveProperty('patternId');
      expect(s).toHaveProperty('category');
      expect(s).toHaveProperty('suggestion');
      expect(s).toHaveProperty('line');
    }
  });

  it('includes style tips for AI-like text', () => {
    const text = loadFixture('ai-sample-1.txt');
    const result = humanize(text);
    expect(result.styleTips).toBeDefined();
    expect(Array.isArray(result.styleTips)).toBe(true);
  });
});

// ─── formatSuggestions ───────────────────────────────────

describe('formatSuggestions', () => {
  it('produces readable output', () => {
    const text = loadFixture('ai-sample-1.txt');
    const result = humanize(text);
    const output = formatSuggestions(result);
    expect(typeof output).toBe('string');
    expect(output).toContain('HUMANIZATION SUGGESTIONS');
    expect(output).toContain('AI Score:');
  });

  it('includes guidance section', () => {
    const text = loadFixture('ai-sample-1.txt');
    const result = humanize(text);
    const output = formatSuggestions(result);
    expect(output).toContain('GUIDANCE');
  });
});
