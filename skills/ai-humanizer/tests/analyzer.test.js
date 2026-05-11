/**
 * analyzer.test.js — Tests for the text analysis engine.
 */

import { describe, it, expect } from 'vitest';
import { analyze, score, formatReport, formatJSON, formatMarkdown } from '../src/analyzer.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function loadFixture(name) {
  return fs.readFileSync(path.join(__dirname, 'fixtures', name), 'utf-8');
}

// ─── Basic Functionality ─────────────────────────────────

describe('analyze', () => {
  it('returns a valid result object', () => {
    const result = analyze('Hello world.');
    expect(result).toHaveProperty('score');
    expect(result).toHaveProperty('patternScore');
    expect(result).toHaveProperty('uniformityScore');
    expect(result).toHaveProperty('totalMatches');
    expect(result).toHaveProperty('wordCount');
    expect(result).toHaveProperty('categories');
    expect(result).toHaveProperty('findings');
    expect(result).toHaveProperty('summary');
    expect(result).toHaveProperty('stats');
  });

  it('handles empty input gracefully', () => {
    const result = analyze('');
    expect(result.score).toBe(0);
    expect(result.totalMatches).toBe(0);
  });

  it('handles null/undefined input', () => {
    expect(analyze(null).score).toBe(0);
    expect(analyze(undefined).score).toBe(0);
  });

  it('scores clean human text low', () => {
    const text = loadFixture('human-sample-1.txt');
    const result = analyze(text);
    expect(result.score).toBeLessThan(25);
  });

  it('scores obvious AI text high', () => {
    const text = loadFixture('ai-sample-1.txt');
    const result = analyze(text);
    expect(result.score).toBeGreaterThan(50);
  });

  it('detects multiple categories in AI text', () => {
    const text = loadFixture('ai-sample-1.txt');
    const result = analyze(text);
    const hitCategories = Object.entries(result.categories)
      .filter(([, v]) => v.matches > 0)
      .map(([k]) => k);
    expect(hitCategories.length).toBeGreaterThanOrEqual(3);
  });

  it('includes stats in result', () => {
    const text = 'The cat sat on the mat. The dog ran fast. The bird flew away.';
    const result = analyze(text);
    expect(result.stats).not.toBeNull();
    expect(result.stats).toHaveProperty('burstiness');
    expect(result.stats).toHaveProperty('typeTokenRatio');
  });
});

// ─── Score Function ──────────────────────────────────────

describe('score', () => {
  it('returns a number between 0 and 100', () => {
    const s = score('This is a simple sentence.');
    expect(s).toBeGreaterThanOrEqual(0);
    expect(s).toBeLessThanOrEqual(100);
  });

  it('scores AI sample higher than human sample', () => {
    const aiScore = score(loadFixture('ai-sample-1.txt'));
    const humanScore = score(loadFixture('human-sample-1.txt'));
    expect(aiScore).toBeGreaterThan(humanScore);
  });
});

// ─── Pattern Filtering ──────────────────────────────────

describe('pattern filtering', () => {
  it('can check only specific patterns', () => {
    const text = 'Additionally, this serves as a testament to excellence.';
    const full = analyze(text);
    const filtered = analyze(text, { patternsToCheck: [7] }); // Only AI vocab
    expect(filtered.findings.length).toBeLessThanOrEqual(full.findings.length);
    expect(filtered.findings.every((f) => f.patternId === 7)).toBe(true);
  });
});

// ─── Formatting ──────────────────────────────────────────

describe('formatting', () => {
  it('formatReport produces a string', () => {
    const result = analyze('This is a testament to great things.');
    const report = formatReport(result);
    expect(typeof report).toBe('string');
    expect(report).toContain('AI WRITING PATTERN ANALYSIS');
    expect(report).toContain('Score:');
  });

  it('formatJSON produces valid JSON', () => {
    const result = analyze('This is a testament to great things.');
    const json = formatJSON(result);
    const parsed = JSON.parse(json);
    expect(parsed).toHaveProperty('score');
  });

  it('formatMarkdown produces markdown', () => {
    const result = analyze('This is a testament to great things.');
    const md = formatMarkdown(result);
    expect(typeof md).toBe('string');
    expect(md).toContain('# AI writing pattern analysis');
    expect(md).toContain('**Score:');
  });
});

// ─── Individual Pattern Detection ────────────────────────

describe('pattern detection', () => {
  // 1. Significance inflation
  it('detects significance inflation', () => {
    const text =
      'This moment marks a pivotal shift in the evolution of technology, setting the stage for a key turning point.';
    const result = analyze(text, { patternsToCheck: [1] });
    expect(result.findings.length).toBeGreaterThan(0);
    expect(result.findings[0].patternId).toBe(1);
  });

  // 2. Notability name-dropping
  it('detects notability name-dropping', () => {
    const text = 'She maintains an active social media presence with millions of followers.';
    const result = analyze(text, { patternsToCheck: [2] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 3. Superficial -ing analyses
  it('detects superficial -ing analyses', () => {
    const text =
      "The building uses modern materials, showcasing the architect's vision and reflecting the community's values.";
    const result = analyze(text, { patternsToCheck: [3] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 4. Promotional language
  it('detects promotional language', () => {
    const text =
      'Nestled in the heart of downtown, this stunning venue boasts breathtaking views and renowned cuisine.';
    const result = analyze(text, { patternsToCheck: [4] });
    expect(result.findings.length).toBeGreaterThan(0);
    expect(result.totalMatches).toBeGreaterThanOrEqual(3);
  });

  // 5. Vague attributions
  it('detects vague attributions', () => {
    const text =
      'Experts believe this is important. Industry reports suggest continued growth. Studies show improvement.';
    const result = analyze(text, { patternsToCheck: [5] });
    expect(result.findings.length).toBeGreaterThan(0);
    expect(result.totalMatches).toBeGreaterThanOrEqual(2);
  });

  // 6. Formulaic challenges
  it('detects formulaic challenges', () => {
    const text =
      'Despite its challenges, the city continues to thrive. Despite these obstacles, the future outlook remains positive.';
    const result = analyze(text, { patternsToCheck: [6] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 7. AI vocabulary
  it('detects AI vocabulary words', () => {
    const text =
      'Additionally, this showcases the vibrant tapestry of the evolving landscape, a testament to enduring innovation.';
    const result = analyze(text, { patternsToCheck: [7] });
    expect(result.findings.length).toBeGreaterThan(0);
    expect(result.totalMatches).toBeGreaterThanOrEqual(4);
  });

  // 8. Copula avoidance
  it('detects copula avoidance', () => {
    const text =
      'The gallery serves as a space for art. The building boasts over 3000 square feet. It functions as a hub.';
    const result = analyze(text, { patternsToCheck: [8] });
    expect(result.findings.length).toBeGreaterThan(0);
    expect(result.totalMatches).toBeGreaterThanOrEqual(2);
  });

  // 9. Negative parallelisms
  it('detects negative parallelisms', () => {
    const text =
      "It's not just a tool, it's a revolution. Not only does it save time but also transforms workflows.";
    const result = analyze(text, { patternsToCheck: [9] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 10. Rule of three
  it('detects rule of three with abstract nouns', () => {
    const text =
      'The event promotes innovation, inspiration, and collaboration for increased motivation, dedication, and education.';
    const result = analyze(text, { patternsToCheck: [10] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 13. Em dash overuse
  it('detects em dash overuse', () => {
    const text =
      'The project — which started last year — has grown significantly — reaching new heights — and the team — a dedicated group — continues to push forward.';
    const result = analyze(text, { patternsToCheck: [13] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 14. Boldface overuse
  it('detects boldface overuse', () => {
    const text =
      'The **team** worked on **three** key **projects** using **modern** tools for **better** results.';
    const result = analyze(text, { patternsToCheck: [14] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 15. Inline-header lists
  it('detects inline-header lists', () => {
    const text =
      '- **Speed:** Loading is faster now.\n- **Quality:** Output quality improved.\n- **Adoption:** More users joined.';
    const result = analyze(text, { patternsToCheck: [15] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 16. Title Case headings
  it('detects Title Case headings', () => {
    const text =
      '## Strategic Negotiations And Global Partnerships\n\nSome content here.\n\n## Building A Better Tomorrow Today';
    const result = analyze(text, { patternsToCheck: [16] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 17. Emoji overuse
  it('detects emoji overuse in professional text', () => {
    const text =
      '🚀 Launch phase complete\n💡 Key insights discovered\n✅ Next steps defined\n🎯 Goals aligned';
    const result = analyze(text, { patternsToCheck: [17] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 18. Curly quotes
  it('detects curly quotes', () => {
    const text =
      'He said \u201Cthe project is on track\u201D but she replied \u201CI\u2019m not so sure.\u201D';
    const result = analyze(text, { patternsToCheck: [18] });
    expect(result.findings.length).toBeGreaterThan(0);
    expect(result.totalMatches).toBeGreaterThanOrEqual(3);
  });

  // 19. Chatbot artifacts
  it('detects chatbot artifacts', () => {
    const text =
      'Here is an overview of the topic. I hope this helps! Let me know if you would like me to expand on any section.';
    const result = analyze(text, { patternsToCheck: [19] });
    expect(result.findings.length).toBeGreaterThan(0);
    expect(result.totalMatches).toBeGreaterThanOrEqual(2);
  });

  // 20. Cutoff disclaimers
  it('detects cutoff disclaimers', () => {
    const text =
      'While specific details are limited, based on available information the company was founded in the 1990s. As of my last training update, this was accurate.';
    const result = analyze(text, { patternsToCheck: [20] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 21. Sycophantic tone
  it('detects sycophantic tone', () => {
    const text =
      "Great question! You're absolutely right that this is complex. That's an excellent point about the economy.";
    const result = analyze(text, { patternsToCheck: [21] });
    expect(result.findings.length).toBeGreaterThan(0);
    expect(result.totalMatches).toBeGreaterThanOrEqual(2);
  });

  // 22. Filler phrases
  it('detects filler phrases', () => {
    const text =
      'In order to achieve this goal, due to the fact that resources are limited, the team has the ability to adapt.';
    const result = analyze(text, { patternsToCheck: [22] });
    expect(result.findings.length).toBeGreaterThan(0);
    expect(result.totalMatches).toBeGreaterThanOrEqual(2);
  });

  // 23. Excessive hedging
  it('detects excessive hedging', () => {
    const text =
      'It could potentially be true. One might possibly agree that things could conceivably improve.';
    const result = analyze(text, { patternsToCheck: [23] });
    expect(result.findings.length).toBeGreaterThan(0);
  });

  // 24. Generic conclusions
  it('detects generic conclusions', () => {
    const text =
      'The future looks bright for the company. Exciting times lie ahead as they continue their journey toward excellence.';
    const result = analyze(text, { patternsToCheck: [24] });
    expect(result.findings.length).toBeGreaterThan(0);
    expect(result.totalMatches).toBeGreaterThanOrEqual(2);
  });
});

// ─── AI Sample Full Analysis ─────────────────────────────

describe('full AI sample analysis', () => {
  it('detects many patterns in ai-sample-1.txt', () => {
    const text = loadFixture('ai-sample-1.txt');
    const result = analyze(text, { verbose: true });
    const categories = Object.entries(result.categories).filter(([, v]) => v.matches > 0);
    expect(categories.length).toBeGreaterThanOrEqual(4);
    expect(result.score).toBeGreaterThan(50);
    expect(result.totalMatches).toBeGreaterThan(15);
  });

  it('detects many patterns in ai-sample-2.txt', () => {
    const text = loadFixture('ai-sample-2.txt');
    const result = analyze(text);
    expect(result.score).toBeGreaterThan(30);
    expect(result.totalMatches).toBeGreaterThan(5);
  });
});
