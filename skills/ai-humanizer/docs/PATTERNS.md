# Pattern documentation

Detailed technical documentation for all 24 AI writing patterns detected by humanizer.

## How detection works

Each pattern has a `detect(text)` function that returns an array of matches. Detection uses:

- **Regex matching** for vocabulary words, phrases, and structural patterns
- **Density analysis** for patterns that depend on frequency (em dashes, AI vocab)
- **Heuristic checks** for structural patterns (synonym cycling, rule of three)

## Pattern weights

Patterns are weighted 1-5 based on how strongly they signal AI-generated text:

| Weight | Meaning | Patterns |
|--------|---------|----------|
| 5 | Dead giveaway | AI vocabulary (7), Chatbot artifacts (19) |
| 4 | Strong signal | Significance inflation (1), -ing analyses (3), Vague attributions (5), Cutoff disclaimers (20), Sycophantic tone (21) |
| 3 | Moderate signal | Notability (2), Promotional language (4), Formulaic challenges (6), Copula avoidance (8), Negative parallelisms (9), Inline-header lists (15), Filler phrases (22), Hedging (23), Generic conclusions (24) |
| 2 | Weak signal | Rule of three (10), Synonym cycling (11), False ranges (12), Em dash overuse (13), Boldface overuse (14), Emoji overuse (17) |
| 1 | Minor tell | Title Case headings (16), Curly quotes (18) |

## Scoring algorithm

The AI score (0-100) combines three components:

1. **Density score** (up to 65 points): Weighted matches per 100 words, on a logarithmic scale
2. **Breadth bonus** (up to 20 points): 2 points per unique pattern type detected
3. **Category bonus** (up to 15 points): 3 points per category with hits

The logarithmic curve prevents long texts from getting inflated scores just by having more words to match against.

## Adding new patterns

To add a new pattern to `src/patterns.js`:

1. Define the pattern object with `id`, `name`, `category`, `description`, `weight`, and `detect(text)` function
2. The detect function must return `{ match, index, line, column, suggestion }`
3. Use the `findMatches()` helper for regex-based detection
4. Add tests in `tests/analyzer.test.js`
5. Document in `references/patterns.md`

Example:

```javascript
{
  id: 25,
  name: 'New pattern name',
  category: 'content', // or language, style, communication, filler
  description: 'What this pattern is and why it matters.',
  weight: 3,
  detect(text) {
    const regex = /your-pattern-here/gi;
    return findMatches(text, regex, 'Suggestion for fixing this pattern.');
  },
}
```
