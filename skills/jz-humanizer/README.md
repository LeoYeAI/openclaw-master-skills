# Humanizer Skill

Remove signs of AI-generated writing to make text sound more natural and human.

## Features

- **Pattern Detection**: Based on Wikipedia's comprehensive "Signs of AI writing" guide
- **50+ AI Vocabulary Words**: Identifies and replaces overused AI words
- **Content Patterns**: Detects inflated symbolism, promotional language, vague attributions
- **Style Patterns**: Fixes em dash overuse, rule of three, negative parallelisms
- **Soul Injection**: Not just removing bad patterns, but adding actual personality

## Installation

```bash
npx clawhub@latest install humanizer
```

## Usage

Simply ask your agent to "humanize" any text:

```
Humanize this text: [paste your AI-generated text]
```

Or when editing content:

```
Review this draft for AI patterns and fix them: [your draft]
```

## What It Catches

- Inflated significance ("pivotal moment", "testament to")
- AI vocabulary ("delve", "tapestry", "multifaceted")
- Structural patterns (rule of three, excessive em dashes)
- Soulless writing (no personality, no opinions)

## Version

v2.2.0

## License

MIT
