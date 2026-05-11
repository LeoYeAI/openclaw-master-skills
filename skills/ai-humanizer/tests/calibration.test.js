/**
 * calibration.test.js — Calibration tests for the scoring engine.
 *
 * Known AI samples should score high, known human samples should score low.
 */

import { describe, it, expect } from 'vitest';
import { score } from '../src/analyzer.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function loadFixture(name) {
  return fs.readFileSync(path.join(__dirname, 'fixtures', name), 'utf-8');
}

// ─── AI Samples — Should Score High ─────────────────────

describe('AI sample calibration', () => {
  it('ai-sample-1.txt scores 55+', () => {
    const text = loadFixture('ai-sample-1.txt');
    const s = score(text);
    expect(s).toBeGreaterThanOrEqual(55);
  });

  it('ai-sample-2.txt scores 30+ (moderate AI)', () => {
    const text = loadFixture('ai-sample-2.txt');
    const s = score(text);
    expect(s).toBeGreaterThanOrEqual(30);
  });

  it('classic chatbot output scores very high', () => {
    const text = `Great question! Here is a comprehensive overview of machine learning.

Machine learning serves as a transformative cornerstone of modern technology, marking a pivotal moment in the evolution of artificial intelligence. In today's rapidly evolving digital age, these groundbreaking tools are reshaping how organizations navigate the complexities of data-driven decision making.

It is worth noting that the landscape of AI continues to evolve at a breathtaking pace. Experts believe that machine learning plays a crucial role in fostering innovation and unleashing the potential of big data.

- **Speed:** Processing has been revolutionized, empowering teams to harness the power of real-time analytics.
- **Quality:** Output quality has been enhanced through multifaceted approaches to model training.
- **Adoption:** Industry reports suggest continued growth, underscoring the paramount importance of this technology.

Despite challenges, the future looks bright. Exciting times lie ahead as we embark on this journey toward excellence. I hope this helps! Let me know if you'd like me to delve into any section further.`;
    const s = score(text);
    expect(s).toBeGreaterThanOrEqual(60);
  });

  it('promotional AI text scores high', () => {
    const text = `Nestled in the heart of downtown, this stunning venue serves as a testament to architectural innovation. The breathtaking facility boasts world-class amenities and seamless integration of cutting-edge technology.

Renowned for its commitment to excellence, the establishment showcases a vibrant tapestry of cultural experiences. Industry observers have noted its pivotal role in reshaping the landscape of urban entertainment.

The comprehensive approach encompasses state-of-the-art design, fostering a culture of innovation while leveraging synergy between form and function. The future looks bright as exciting times lie ahead.`;
    const s = score(text);
    expect(s).toBeGreaterThanOrEqual(55);
  });

  it('hedging + filler AI text scores high', () => {
    const text = `It could potentially be argued that in order to navigate the complexities of modern software development, it is important to note that one must harness the power of robust frameworks. Due to the fact that the landscape is ever-evolving, teams need to embark on a journey of continuous improvement.

As we move forward, it goes without saying that leveraging cutting-edge tools plays a pivotal role. Needless to say, this comprehensive guide will help you unlock the potential of these transformative technologies.

In conclusion, the multifaceted challenges of today's digital age require a seamless approach. Without further ado, let us delve into the realm of best practices.`;
    const s = score(text);
    expect(s).toBeGreaterThanOrEqual(50);
  });
});

// ─── Human Samples — Should Score Low ───────────────────

describe('human sample calibration', () => {
  it('human-sample-1.txt scores under 30', () => {
    const text = loadFixture('human-sample-1.txt');
    const s = score(text);
    expect(s).toBeLessThan(30);
  });

  it('casual human writing scores low', () => {
    const text = `I tried three different coffee shops this week. The one on 5th Ave had the best espresso but terrible wifi. The place near the park was quiet enough to work but their cold brew tasted like it had been sitting out since Tuesday.

Ended up going back to my usual spot. Nothing fancy. The barista knows my order. Sometimes that matters more than fancy latte art.`;
    const s = score(text);
    expect(s).toBeLessThan(25);
  });

  it('technical human writing scores low', () => {
    const text = `The bug was in the connection pooling code. When you hit exactly 256 concurrent connections, the pool silently dropped new requests instead of queuing them. No error, no log, just a hung request.

Found it by adding a counter to the pool checkout method. Took about 3 hours of staring at tcpdump output before I thought to look there.

Fixed it with a bounded semaphore. PR is up. The test covers the edge case now.`;
    const s = score(text);
    expect(s).toBeLessThan(25);
  });

  it('opinionated human writing scores low', () => {
    const text = `Look, I get why people like TypeScript. It catches some real bugs at compile time. But the productivity tax is real, and nobody wants to talk about it.

Last week I spent 45 minutes trying to satisfy the type checker on a function that was obviously correct. The types were right, the logic was right, but some intersection type was confusing the compiler.

I still use it for big projects. But for scripts and prototypes? Just give me plain JavaScript.`;
    const s = score(text);
    expect(s).toBeLessThan(25);
  });

  it('narrative human writing scores low', () => {
    const text = `My grandfather built his own house in 1962. Took him two years, working weekends. The foundation is slightly off-level — you can tell if you put a marble on the kitchen floor. It rolls toward the east wall every time.

He never fixed it. Said it gave the house character. I think he just didn't want to jack up a house he'd already put a roof on.

The house is still standing. My aunt lives there now.`;
    const s = score(text);
    expect(s).toBeLessThan(25);
  });
});

// ─── Relative Ordering ──────────────────────────────────

describe('relative scoring', () => {
  it('AI text always scores higher than human text', () => {
    const aiText = loadFixture('ai-sample-1.txt');
    const humanText = loadFixture('human-sample-1.txt');

    const aiScore = score(aiText);
    const humanScore = score(humanText);

    expect(aiScore).toBeGreaterThan(humanScore);
    expect(aiScore - humanScore).toBeGreaterThan(20);
  });

  it('more AI patterns → higher score', () => {
    const light = 'The project has been interesting in scope. We worked hard on it last year.';
    const heavy =
      "Additionally, this groundbreaking project serves as a testament to innovation. In today's rapidly evolving landscape, it showcases the vibrant tapestry of modern technology, fostering seamless synergy. I hope this helps!";

    expect(score(heavy)).toBeGreaterThan(score(light));
  });
});
