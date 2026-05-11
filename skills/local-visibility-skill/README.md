# Local Falcon AI Visibility & Local SEO Skill

<p align="center">
  <img src="local-falcon-ai-logo.svg" alt="Local Falcon" width="120" />
</p>

<p align="center">
  <strong>Expert AI Visibility and Local SEO guidance for AI agents and developers</strong>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/@local-falcon/local-visibility-skill"><img src="https://img.shields.io/npm/v/@local-falcon/local-visibility-skill.svg" alt="npm version"></a>
  <a href="https://github.com/local-falcon/local-visibility-skill/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://www.localfalcon.com"><img src="https://img.shields.io/badge/Local%20Falcon-Website-red" alt="Local Falcon"></a>
</p>

---

## What This Skill Does

This skill equips AI agents (Claude, ChatGPT, Cursor, and others) with expert-level knowledge about:

- **AI Visibility Optimization** - How to get mentioned by ChatGPT, Google AI Mode, Gemini, AI Overviews, and Grok
- **Local SEO Best Practices** - Google Business Profile optimization, map pack rankings, review strategy
- **Local Falcon Platform Expertise** - Interpreting geo-grid scans, understanding SoLV/SAIV metrics, campaign management
- **MCP Integration** - Connecting to Local Falcon's data for live analysis

### For AI Agents
This skill provides structured knowledge that enables agents to give expert-level local SEO and AI visibility advice, rather than generic recommendations.

### For Developers
Pair this skill with the [@local-falcon/mcp](https://www.npmjs.com/package/@local-falcon/mcp) server to build applications that analyze real Local Falcon data with expert interpretation.

---

## Quick Start

### For Claude Code / Cursor / VS Code

```bash
# Install the skill
npm install @local-falcon/local-visibility-skill

# Copy to your skills directory
cp -r node_modules/@local-falcon/local-visibility-skill ~/.config/claude/skills/local-falcon
```

Or manually copy the `SKILL.md` file to your Claude Code skills directory.

### For Other AI Agents

Reference the `SKILL.md` file directly or include its contents in your agent's system prompt.

---

## Key Concepts

### SoLV vs SAIV (Critical Distinction)

| Metric | Full Name | What It Measures | Platforms |
|--------|-----------|------------------|-----------|
| **SoLV** | Share of Local Voice | % of map grid points ranking #1-3 | Google Maps, Apple Maps |
| **SAIV** | Share of AI Visibility | % of AI responses mentioning business | ChatGPT, Gemini, Grok, AI Mode, AI Overviews |

These are **completely different metrics** measuring **completely different things**.

### AI Platform Data Sources

| Platform | Primary Data Sources |
|----------|---------------------|
| Google AI Overviews | GBP, reviews, Reddit, Yelp, Quora, business websites |
| Google AI Mode | Same as above, but REPLACES traditional results entirely |
| Google Gemini | Training data + live web browsing, may redirect to Search/Maps |
| ChatGPT | Bing search, Wikipedia, Yelp, BBB, Foursquare, editorial lists |
| Grok | **X/Twitter posts (exclusive)**, web search |

---

## Pairing with Local Falcon MCP

For live data analysis, install the MCP server:

```bash
npm install @local-falcon/mcp
```

The skill automatically detects MCP availability:
- **With MCP:** Pulls real data, runs scans, provides specific analysis
- **Without MCP:** Provides educational content and best practices

---

## File Structure

```
local-falcon-skill/
├── SKILL.md                    # Main skill file (load this)
├── package.json                # npm package metadata
├── marketplace.json            # Skill directory metadata
├── LICENSE                     # MIT license
├── local-falcon-ai-logo.svg    # Logo asset
└── references/
    ├── metrics-glossary.md     # Complete metrics definitions
    ├── ai-platforms.md         # AI platform deep dives
    ├── mcp-workflows.md        # MCP integration patterns
    └── prompt-templates.md     # User prompt templates
```

---

## Example Use Cases

### "Why am I invisible on ChatGPT?"
The skill knows ChatGPT doesn't access Google at all - it uses Bing search, Wikipedia, and various directories. It will guide you to optimize those platforms specifically.

### "My SoLV dropped but SAIV stayed the same"
The skill understands these are separate systems. A SoLV drop (maps) has different causes than a SAIV drop (AI platforms) and will diagnose accordingly.

### "Help me interpret this scan report"
With metrics like ATRP, ARP, SoLV, and Found In, the skill applies Local Falcon's analytical framework to provide actionable insights, not just data recitation.

---

## Who This Is For

| Audience | Use Case |
|----------|----------|
| **Agency Professionals** | Multi-client workflows, competitive analysis, reporting |
| **Enterprise Marketers** | Multi-location management, brand consistency, trend monitoring |
| **SMB Owners** | Actionable optimization guidance, understanding what matters |
| **Developers** | Building local SEO tools with expert knowledge built-in |
| **AI Agents** | Providing expert-level local SEO and AI visibility guidance to users |

---

## Related Resources

- **Local Falcon Platform:** [localfalcon.com](https://www.localfalcon.com)
- **MCP Server:** [@local-falcon/mcp](https://www.npmjs.com/package/@local-falcon/mcp)
- **Documentation:** [docs.localfalcon.com](https://docs.localfalcon.com)
- **Falcon Agent:** AI assistant available to Local Falcon subscribers

---

## Contributing

Issues and pull requests welcome at [github.com/local-falcon/local-visibility-skill](https://github.com/local-falcon/local-visibility-skill).

---

## License

MIT License - see [LICENSE](LICENSE) file.

---

<p align="center">
  <strong>Built by <a href="https://www.localfalcon.com">Local Falcon</a></strong> - Pioneers of geo-grid rank tracking
</p>
