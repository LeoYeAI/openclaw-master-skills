# humanizer

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Tests](https://img.shields.io/badge/tests-128%20passing-brightgreen)
![Node >= 18](https://img.shields.io/badge/node-%3E%3D18-brightgreen)

Detect and remove signs of AI-generated writing. Makes text sound natural and human.

An [OpenClaw](https://github.com/nichochar/openclaw) skill and standalone CLI tool that scans text for **24 AI writing patterns** using **500+ vocabulary terms** and **statistical text analysis** (burstiness, type-token ratio, readability metrics) — then provides actionable suggestions to fix them.

Based on [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), [Copyleaks stylistic fingerprint research](https://arxiv.org/abs/2503.01659), and [blader/humanizer](https://github.com/blader/humanizer).

## Install

### As an OpenClaw skill

```bash
git clone https://github.com/brandonwise/humanizer.git
cp humanizer/SKILL.md ~/.config/openclaw/skills/humanizer.md
```

### As a standalone CLI tool

```bash
git clone https://github.com/brandonwise/humanizer.git
cd humanizer
npm install

# Score some text
echo "This serves as a testament to innovation." | node src/cli.js score

# Full analysis
node src/cli.js analyze -f your-draft.md

# Humanize with auto-fixes
node src/cli.js humanize --autofix -f article.txt
```

### Global install

```bash
npm install -g .
humanizer score < draft.txt
humanizer analyze -f essay.md
humanizer humanize --autofix < article.txt
```

## Architecture

The scoring engine combines three signal types:

```
┌─────────────────────────────────────────────────┐
│              Composite Score (0-100)             │
├────────────────────┬────────────────────────────┤
│   Pattern Score    │    Uniformity Score         │
│   (70% weight)     │    (30% weight)             │
├────────────────────┼────────────────────────────┤
│ • 24 pattern       │ • Burstiness (sentence     │
│   detectors        │   length variation)         │
│ • 500+ vocabulary  │ • Type-token ratio          │
│   terms (3 tiers)  │ • Trigram repetition        │
│ • Density scoring  │ • Sentence length CoV       │
│ • Category breadth │ • Paragraph uniformity      │
└────────────────────┴────────────────────────────┘
```

**Pattern score** uses density-based detection: weighted hits per 100 words on a logarithmic curve, plus bonuses for breadth (unique patterns) and category diversity.

**Uniformity score** uses statistical analysis: human text has high burstiness (varied sentence lengths), diverse vocabulary, and low n-gram repetition. AI text is mechanically uniform.

## Statistical analysis

The stats engine computes metrics that differentiate AI from human writing:

| Metric | Human Writing | AI Writing | Why It Matters |
|--------|--------------|------------|----------------|
| **Burstiness** | 0.5–1.0 | 0.1–0.3 | Humans write in bursts — short sentences, then long ones. AI is metronomic. |
| **Type-token ratio** | 0.5–0.7 | 0.3–0.5 | Humans use more varied vocabulary. AI cycles through the same words. |
| **Sentence CoV** | 0.4–0.8 | 0.15–0.35 | Coefficient of variation in sentence length. Low = robotic uniformity. |
| **Trigram repetition** | < 0.05 | > 0.10 | AI reuses the same 3-word phrases more often. |
| **Readability (FK)** | Varies | 8–12 | AI tends to write at a consistent grade level. Humans vary. |

## CLI reference

### Commands

```bash
# Quick score (0-100, higher = more AI-like)
echo "text" | humanizer score

# Full analysis with pattern matches
humanizer analyze essay.txt

# Full markdown report (pipe to file)
humanizer report article.txt > report.md

# Suggestions grouped by priority
humanizer suggest draft.md

# Statistical analysis only
humanizer stats essay.txt

# Humanization suggestions with guidance
humanizer humanize -f article.txt

# Apply safe auto-fixes
humanizer humanize --autofix -f article.txt
```

### Options

```bash
-f, --file <path>       Read text from file
--json                  Output as JSON
--verbose, -v           Show all matches
--autofix               Apply safe fixes (humanize only)
--patterns <ids>        Check specific pattern IDs (comma-separated)
--threshold <n>         Only show patterns with weight above n
--config <file>         Custom config file (JSON)
--help, -h              Show help
```

### Score badges

```
🟢 0-25    Mostly human-sounding
🟡 26-50   Lightly AI-touched
🟠 51-75   Moderately AI-influenced
🔴 76-100  Heavily AI-generated
```

## API (programmatic use)

```javascript
const { analyze, score } = require('humanizer');

// Quick score
const s = score('Your text here...');
console.log(s); // 0-100

// Full analysis
const result = analyze(text, {
  verbose: true,          // Show all matches
  patternsToCheck: [7, 19, 22], // Only specific patterns
  includeStats: true,     // Include statistical analysis
});

console.log(result.score);           // 0-100 composite
console.log(result.patternScore);    // Pattern-only score
console.log(result.uniformityScore); // Stats-based uniformity score
console.log(result.stats);           // { burstiness, typeTokenRatio, ... }
console.log(result.findings);        // Detailed pattern matches
console.log(result.categories);      // Per-category breakdown

// Humanize
const { humanize, autoFix } = require('humanizer/src/humanizer');

const suggestions = humanize(text, { autofix: true });
console.log(suggestions.critical);   // Dead giveaway issues
console.log(suggestions.important);  // Noticeable patterns
console.log(suggestions.guidance);   // Writing tips
console.log(suggestions.styleTips);  // Statistical style advice
console.log(suggestions.autofix.text); // Auto-fixed text

// Stats only
const { computeStats } = require('humanizer/src/stats');
const stats = computeStats(text);
console.log(stats.burstiness);       // Sentence variation
console.log(stats.typeTokenRatio);   // Vocabulary diversity
```

## The 24 patterns

| # | Pattern | Category | Weight | Example |
|---|---------|----------|--------|---------|
| 1 | Significance inflation | Content | 4 | "marking a pivotal moment in the evolution of..." |
| 2 | Notability name-dropping | Content | 3 | "featured in NYT, BBC, CNN, and Forbes" |
| 3 | Superficial -ing analyses | Content | 4 | "...showcasing... reflecting... highlighting..." |
| 4 | Promotional language | Content | 3 | "nestled", "breathtaking", "stunning" |
| 5 | Vague attributions | Content | 4 | "Experts believe", "Studies show" |
| 6 | Formulaic challenges | Content | 3 | "Despite challenges... continues to thrive" |
| 7 | AI vocabulary | Language | 5 | "Additionally", "delve", "tapestry" (500+ words) |
| 8 | Copula avoidance | Language | 3 | "serves as" instead of "is" |
| 9 | Negative parallelisms | Language | 3 | "It's not just X, it's Y" |
| 10 | Rule of three | Language | 2 | "innovation, inspiration, and insights" |
| 11 | Synonym cycling | Language | 2 | "protagonist... main character... central figure" |
| 12 | False ranges | Language | 2 | "from the Big Bang to dark matter" |
| 13 | Em dash overuse | Style | 2 | Too many — em dashes — in one — piece |
| 14 | Boldface overuse | Style | 2 | **Every** **other** **word** bolded |
| 15 | Inline-header lists | Style | 3 | "- **Topic:** Topic is..." |
| 16 | Title Case headings | Style | 1 | "## Every Word Capitalized Here" |
| 17 | Emoji overuse | Style | 2 | 🚀💡✅ in professional text |
| 18 | Curly quotes | Style | 1 | \u201Csmart quotes\u201D instead of "straight" |
| 19 | Chatbot artifacts | Comms | 5 | "I hope this helps!", "Let me know if..." |
| 20 | Cutoff disclaimers | Comms | 4 | "As of my last training update..." |
| 21 | Sycophantic tone | Comms | 4 | "Great question!", "You're absolutely right!" |
| 22 | Filler phrases | Filler | 3 | "In order to", "Due to the fact that" |
| 23 | Excessive hedging | Filler | 3 | "could potentially possibly" |
| 24 | Generic conclusions | Filler | 3 | "The future looks bright" |

## Vocabulary tiers

- **Tier 1** (Dead giveaways): 50+ words that appear 5-20x more in AI text. Always flagged. Examples: *delve, tapestry, vibrant, crucial, meticulous, seamless, groundbreaking*
- **Tier 2** (Suspicious in density): 80+ words flagged when 2+ appear. Examples: *furthermore, paradigm, holistic, utilize, facilitate, nuanced*
- **Tier 3** (Context-dependent): 60+ words flagged only at >3% density. Examples: *significant, effective, unique, compelling, exceptional*
- **Phrases**: 80+ multi-word patterns. Examples: *"In today's digital age"*, *"plays a crucial role"*, *"serves as a testament"*

## How scoring works

1. **Pattern detection** — Each of 24 detectors scans for regex matches. Matches are weighted 1-5.
2. **Density calculation** — Weighted matches per 100 words, on a logarithmic curve (prevents runaway scores).
3. **Breadth bonus** — More unique pattern types = higher score (up to +20).
4. **Category diversity** — Hits across content/language/style/communication/filler = higher score (up to +15).
5. **Statistical uniformity** — Low burstiness, low vocabulary diversity, high repetition add up to 100 uniformity points.
6. **Composite blend** — Pattern score (70%) + uniformity score (30%) = final score.

This transparent methodology means you can see exactly why text scored the way it did.

## What makes this different

| Feature | humanizer | GPTZero | Copyleaks | ZeroGPT |
|---------|-----------|---------|-----------|---------|
| Open source | ✅ | ❌ | ❌ | ❌ |
| Transparent scoring | ✅ Fully explainable | ❌ Black box | ❌ Black box | ❌ Black box |
| Actionable suggestions | ✅ Per-pattern guidance | ❌ Score only | ❌ Score only | ❌ Score only |
| Auto-fix | ✅ Safe mechanical fixes | ❌ | ❌ | ❌ |
| Statistical analysis | ✅ Burstiness, TTR, FK | ✅ Perplexity | ✅ Stylometric | ❌ |
| No API key needed | ✅ | ❌ | ❌ | ❌ |
| Works offline | ✅ | ❌ | ❌ | ❌ |
| Zero dependencies | ✅ | N/A | N/A | N/A |

## Before/after

**Before (AI score: 78):**
> Great question! Here is an overview of AI-assisted coding. AI-assisted coding serves as an enduring testament to the transformative potential of large language models, marking a pivotal moment in the evolution of software development. In today's rapidly evolving technological landscape, these groundbreaking tools are reshaping how engineers ideate, iterate, and deliver, underscoring their vital role in modern workflows. The future looks bright. I hope this helps!

**After (AI score: 4):**
> AI coding tools speed up boilerplate. In a 2024 Google study, developers using Codex finished simple functions 55% faster, but showed no improvement on debugging or architecture. I've used Copilot for a year. It's good at config files and test scaffolding. It's bad at knowing when it's wrong.

## Always-On Mode: Bake Into Your Agent's Personality

The skill works great on-demand, but the real power is making your AI **always** write like a human. Here's how to bake the humanizer principles into your agent's system prompt or personality file.

### For OpenClaw (SOUL.md)

Add this to your `SOUL.md` (or equivalent personality file):

```markdown
## Writing Like a Human (Anti-AI Patterns)

Your writing should be indistinguishable from a sharp, opinionated human.
These rules are always on — not just when asked to "humanize."

### Never Use These Words
Dead giveaways of AI output — ban them from your vocabulary:

**Words:** delve, tapestry, vibrant, crucial, comprehensive, meticulous, embark,
robust, seamless, groundbreaking, leverage, synergy, transformative, paramount,
multifaceted, myriad, cornerstone, reimagine, empower, catalyst, bolster,
spearhead, invaluable, bustling, nestled, realm, showcase, foster, garner,
interplay, enduring, pivotal, intricate, harness, unleash, revolutionize,
elucidate, encompass, holistic, utilize, facilitate, nuanced, paradigm, poised

**Phrases:** "In today's [anything]", "It is worth noting", "plays a crucial role",
"serves as a testament", "in the realm of", "delve into", "harness the power of",
"embark on a journey", "the landscape of", "without further ado"

**Filler to cut:** "In order to" → "to". "Due to the fact that" → "because".
"It is important to note that" → just say it.

### Kill These Patterns
1. No significance inflation — state facts, skip "pivotal moment" claims
2. No vague attributions — name the source or drop the claim
3. No -ing tails — "highlighting the importance of..." gets its own sentence
4. No copula avoidance — use "is" and "has", not "serves as" or "boasts"
5. No sycophancy — skip "Great question!" and just answer
6. No chatbot artifacts — no "I hope this helps" or "Let me know if..."
7. No generic conclusions — end with specifics, not "the future looks bright"

### Write With Human Texture
- Vary sentence length (short, then long, then short)
- Have opinions and take stances
- Use concrete specifics (numbers, names, dates)
- Allow imperfection (contractions, fragments, "And" or "But" starters)
- Use simple verbs ("is", "has", "does" are fine)
- Read it aloud — if you wouldn't say it, don't write it
```

### For Claude (system prompt)

Add to your system prompt or `CLAUDE.md`:

```
You write like a human, not an AI. Never use words like "delve", "tapestry",
"crucial", "comprehensive", "robust", "seamless", or "groundbreaking". Never
write "In today's...", "It is worth noting...", or "Great question!". Use "is"
not "serves as". Vary your sentence lengths. Have opinions. Use specific numbers
and names instead of vague claims. End with specifics, not "the future looks
bright". If you'd never say it in conversation, don't write it.
```

### For ChatGPT (Custom Instructions)

Paste into your Custom Instructions → "How would you like ChatGPT to respond?":

```
Write like a specific human, not a generic AI. Rules:
- Never use: delve, tapestry, vibrant, crucial, robust, seamless, groundbreaking,
  transformative, leverage, synergy, paramount, multifaceted, myriad
- Never start with "In today's..." or end with "the future looks bright"
- Never write "Great question!" or "I hope this helps!"
- Use "is" not "serves as". Use "to" not "in order to"
- Vary sentence length. Short. Then longer. Have opinions.
- Use real numbers and names, not "experts say" or "studies show"
```

### Verification

After baking in, test your agent by asking it to write about any topic. Then scan it:

```bash
echo "Your agent's response here" | node src/cli.js score
```

Target: consistently **under 25** on the humanizer score.

## Project structure

```
humanizer/
├── SKILL.md          # OpenClaw skill definition
├── src/
│   ├── patterns.js   # 24 pattern detectors + pattern registry
│   ├── vocabulary.js  # 500+ AI words/phrases (3 tiers)
│   ├── stats.js       # Statistical analysis engine
│   ├── analyzer.js    # Composite scoring engine
│   ├── humanizer.js   # Suggestion engine + auto-fix
│   └── cli.js         # CLI with colored output
├── tests/             # Vitest test suite (128 tests)
│   ├── analyzer.test.js
│   ├── humanizer.test.js
│   ├── statistics.test.js
│   ├── calibration.test.js
│   ├── performance.test.js
│   └── edge-cases.test.js
├── references/        # Pattern catalogs, vocabulary lists
└── docs/              # Detailed documentation
```

## Contributing

1. Fork and create a branch
2. Add/improve pattern detection (see `src/patterns.js`)
3. Write tests for your changes
4. Run `npm test` — all tests must pass
5. Open a PR

## License

[MIT](LICENSE)
