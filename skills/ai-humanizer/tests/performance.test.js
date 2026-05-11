/**
 * performance.test.js — Benchmark tests.
 *
 * Analyze 10K words in under 1 second.
 */

import { describe, it, expect } from 'vitest';
import { analyze } from '../src/analyzer.js';
import { computeStats } from '../src/stats.js';

/**
 * Generate a large text block of approximately the target word count.
 */
function generateLargeText(targetWords) {
  const paragraphs = [
    "The project serves as a testament to innovation and transformative technology. In today's rapidly evolving landscape, these groundbreaking tools are reshaping how organizations navigate complexities.",
    'I tried three different approaches last week. The first one worked but was slow. The second broke in production. Third time was the charm — simple solution, no fancy tricks.',
    'Additionally, the comprehensive framework showcases seamless integration with cutting-edge platforms. Experts believe this plays a crucial role in fostering synergy across multifaceted teams.',
    'Found the bug at 2am. It was a race condition in the connection pool. Added a mutex, wrote a test, went to bed. PR got merged the next morning.',
    'It is worth noting that the landscape of modern software continues to evolve at a breathtaking pace. Despite challenges, the future looks bright as exciting times lie ahead.',
    "The API returns JSON. You POST to /users with a name and email. It gives you back an ID. That's it. No magic, just a REST endpoint.",
  ];

  let text = '';
  let words = 0;
  let i = 0;
  while (words < targetWords) {
    text += paragraphs[i % paragraphs.length] + '\n\n';
    words += paragraphs[i % paragraphs.length].split(/\s+/).length;
    i++;
  }
  return text;
}

describe('performance', () => {
  it('analyzes 10K words in under 1 second', () => {
    const text = generateLargeText(10000);
    const wordCount = text.split(/\s+/).filter(Boolean).length;
    expect(wordCount).toBeGreaterThanOrEqual(9000);

    const start = performance.now();
    const result = analyze(text);
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(1000);
    expect(result.score).toBeGreaterThanOrEqual(0);
    expect(result.score).toBeLessThanOrEqual(100);
  });

  it('computes statistics on 10K words in under 500ms', () => {
    const text = generateLargeText(10000);

    const start = performance.now();
    const stats = computeStats(text);
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(500);
    expect(stats.wordCount).toBeGreaterThan(5000);
  });

  it('handles 50K words without crashing', () => {
    const text = generateLargeText(50000);

    const start = performance.now();
    const result = analyze(text);
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(5000);
    expect(result.score).toBeGreaterThanOrEqual(0);
  });

  it('many short analyses complete quickly (batch)', () => {
    const texts = Array.from(
      { length: 100 },
      (_, i) => `This is test text number ${i}. It has a few sentences. Nothing special here.`,
    );

    const start = performance.now();
    for (const text of texts) {
      analyze(text);
    }
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(2000);
  });
});
