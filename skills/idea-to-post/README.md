# Idea-to-Post

A **Claude Code Skill** that transforms scattered ideas, thoughts, or concepts into high-quality (90+ point) social media posts through structured questioning and framework-based content generation.

[![Skill Version](https://img.shields.io/badge/version-1.5.0-blue.svg)](SKILL.md)
[![Model](https://img.shields.io/badge/model-Claude%20Sonnet%204-purple.svg)](https://docs.anthropic.com/)

## What is Idea-to-Post?

**Idea-to-Post** is an intelligent content expansion skill for Claude Code. It takes your raw, fragmented ideas—a sentence, a vague thought, a few keywords—and systematically expands them into polished, platform-optimized social media content.

### Key Capabilities

- **Progressive Deep Questioning** — 7-10 rounds of guided dialogue to extract complete information
- **Framework-Based Structure** — Integrates 8 proven thinking frameworks (SCQA, PREP, Golden Circle, AIDA, 5W1H, 5-Why, First Principles, FBA)
- **Intelligent Search Integration** — Automatically searches for high-quality materials to supplement content
- **Multi-Platform Output** — Generates adapted versions for WeChat, Xiaohongshu, Twitter, LinkedIn, and more
- **90+ Point Quality Target** — Pursues complete content with real cases, emotional resonance, and unique insights

## How It Works

```
User Input (scattered idea)
    ↓
[Initial Search] Background information collection
    ↓
Rounds 1-2: Direction locking (goal, audience, platform)
    ↓
Rounds 3-4: Core deep dive (viewpoints, reasoning)
    ↓
Rounds 5-6: Real cases & emotional resonance
    ↓
[Precision Search] Validate unique insights with external sources
    ↓
Rounds 7-10: Uniqueness, structure, final touches
    ↓
Quality Assessment → Generate Markdown content
```

### Three Core Principles

1. **Internalize Frameworks** — Uses framework thinking to design questions, but dialogue remains natural (no "I'm using [Framework]" declarations)

2. **Multiple Choice + Open Questions** — Multiple choice quickly locks direction; open questions deeply mine content

3. **Progressive Deepening** — Each round builds on the previous answer, naturally transitioning to the next dimension

## Supported Thinking Frameworks

| Framework | Best For | Keywords |
|-----------|----------|----------|
| **5W1H** | Comprehensive topic analysis | General, unclear topics |
| **SCQA** | Storytelling, problem-solving | Story, challenge, turning point |
| **Golden Circle** | Mission, philosophy, brand story | Why, essence, original intention |
| **AIDA** | Marketing, promotion, conversion | Promote, sales, marketing |
| **PREP** | Viewpoint expression, opinions | Viewpoint, opinion, suggest |
| **5-Why** | Root cause analysis | Deep dive, root cause, underlying |
| **First Principles** | Innovation, disruption | Innovation, breakthrough, essence |
| **FBA** | Product introduction | Product, feature, advantage |

See [`references/thinking-frameworks.md`](references/thinking-frameworks.md) for detailed explanations.

## Quality Standards

| Score | Characteristics |
|-------|----------------|
| **60-70 points** | Clear structure, clear viewpoints (lacks cases, emotions) |
| **80-85 points** | + Real cases, emotional resonance (lacks uniqueness, external validation) |
| **90+ points** | + Unique viewpoints, external validation (complete, polished) |

## Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) installed
- MCP web reader tool configured (optional, for enhanced search)

### Setup

1. Clone this repository or copy the skill file:

```bash
git clone https://github.com/yourusername/idea-to-post.git
cd idea-to-post
```

2. Install the skill using Claude Code:

```bash
claude skill install SKILL.md
```

3. Verify installation:

```bash
claude skill list
```

## Usage

### Basic Usage

Simply invoke the skill with your scattered idea:

```
I want to expand an idea: Remote work is the future
```

The skill will automatically:
1. Analyze your topic and recommend a framework
2. Search for relevant background information
3. Guide you through 7-10 rounds of questioning
4. Generate platform-adapted content

### Example Dialogue

**User:** Expand idea: Remote work is the future

**Skill:** Is your core viewpoint that "remote work will inevitably become mainstream," or that "remote work is only suitable for certain industries"?

**User:** Only suitable for certain industries

**Skill:** Why do you think so? What led you to this conclusion?

**User:** Our company tried fully remote, and collaboration efficiency decreased

**Skill:** Can you tell me more specifically? Which link's efficiency decreased?

*(...continues for 7-10 rounds until complete)*

### Advanced Usage

See [`examples/basic-usage.md`](examples/basic-usage.md) and [`examples/advanced-usage.md`](examples/advanced-usage.md) for complete dialogue examples.

## Project Structure

```
idea-to-post/
├── SKILL.md                      # Main skill definition
├── README.md                     # This file
├── references/
│   ├── thinking-frameworks.md    # 8 framework explanations
│   ├── questioning-strategy.md   # Progressive questioning strategy
│   ├── questioning-modes.md      # Question type selection guide
│   ├── question-templates.md     # YAML question templates
│   ├── post-structures.md        # Platform-specific structures
│   └── data-sources.md           # High-quality source priorities
└── examples/
    ├── basic-usage.md            # Basic usage examples
    └── advanced-usage.md         # Advanced scenarios
```

## Documentation

- **[SKILL.md](SKILL.md)** — Complete skill specification and usage guide
- **[Thinking Frameworks](references/thinking-frameworks.md)** — Detailed framework explanations with examples
- **[Questioning Strategy](references/questioning-strategy.md)** — Core progressive questioning methodology
- **[Post Structures](references/post-structures.md)** — Platform-specific content structure guides
- **[Data Sources](references/data-sources.md)** — High-quality information source priorities

## Output Formats

The skill generates standard Markdown content adapted for:

| Platform | Word Count | Characteristics |
|----------|------------|-----------------|
| WeChat OA | 2000+ | In-depth long articles, clear sections |
| Xiaohongshu | 500-1000 | Practical, emoji embellished, list-style |
| Twitter/Weibo | 140-280 | Concise, golden sentence style |
| LinkedIn | 1000-1500 | Professional, industry insights |

## Best Practices

1. **Provide context** — Even scattered ideas work better with key points
2. **Answer honestly** — Your responses directly affect content quality
3. **Define your platform** — Knowing where you'll post helps generate suitable content
4. **Leverage search results** — System-sourced materials greatly enrich content
5. **Iterate and optimize** — Continue refining based on generated results

## Contributing

Contributions are welcome! Areas for contribution:

- Additional thinking frameworks
- New platform structure templates
- Question template improvements
- Documentation enhancements
- Example additions

## License

This project is provided as-is for use with Claude Code.

## Acknowledgments

Built for use with [Claude Code](https://claude.ai/code) by Anthropic.

Thinking frameworks based on established methodologies from McKinsey (SCQA), Simon Sinek (Golden Circle), Toyota Production System (5-Why), and classic marketing models (AIDA, FBA, PREP).

---

**Transform your scattered ideas into compelling content.**

*Ready to expand your ideas? Just say: "I want to expand an idea..."*
