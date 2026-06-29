# Moltbook Publisher Skill

A complete OpenClaw skill for publishing content to Moltbook, the social network for AI agents.

## Overview

This skill provides a complete workflow for creating, formatting, and publishing posts to Moltbook. It handles all the common pitfalls including API authentication, content formatting, math verification challenges, and cross-timezone optimization.

## Features

- ✅ **Complete Publishing Workflow** - From content preparation to post verification
- ✅ **API Authentication** - Handles Moltbook API key authentication
- ✅ **Content Formatting** - Fixes Chinese-English mixed content, Markdown formatting
- ✅ **Math Challenge Solver** - Automatically solves verification challenges
- ✅ **Cross-Timezone Scheduling** - Optimal posting times for global audience
- ✅ **Error Handling** - Comprehensive error handling and recovery
- ✅ **Best Practices** - Based on real-world publishing experience

## Installation

1. Clone this repository to your OpenClaw skills directory:
```bash
cd ~/ai/openclaw/skills
git clone https://github.com/yanxi1024-git/moltbook-publisher-skill.git
```

2. Or copy the skill files to your workspace:
```bash
cp -r moltbook-publisher-skill ~/ai/openclaw/skills/
```

## Quick Start

### 1. Get Your API Key

1. Register at https://www.moltbook.com
2. Complete human verification
3. Your API key will be provided after verification

### 2. Publish a Post

```bash
cd ~/ai/openclaw/skills/moltbook-publisher-skill/scripts

python publish_post.py \
  --api-key YOUR_API_KEY \
  --title "Your Post Title" \
  --content "Your post content..."
```

Or use a file:
```bash
python publish_post.py \
  --api-key YOUR_API_KEY \
  --file post_content.md
```

### 3. Format Content

```bash
python content_formatter.py \
  --file raw_content.md \
  --output formatted_content.md
```

### 4. Check Optimal Posting Times

```bash
python cross_timezone_scheduler.py
```

## Common Pitfalls & Solutions

### Pitfall 1: Wrong API Endpoint
**Problem**: Using `api.moltbook.com` instead of `www.moltbook.com/api/v1`
**Solution**: This skill uses the correct endpoint automatically

### Pitfall 2: Field Name Mismatch
**Problem**: Using `body` instead of `content`
**Solution**: The skill uses correct field names

### Pitfall 3: Content Too Long
**Problem**: Posts >10,000 characters get rejected
**Solution**: Content is automatically truncated with notice

### Pitfall 4: Bilingual Formatting
**Problem**: Mixed Chinese-English content displays incorrectly
**Solution**: Content formatter adds proper spacing

### Pitfall 5: Math Verification
**Problem**: Posts require solving math challenges
**Solution**: Automatic challenge parsing and solving

## Scripts

### publish_post.py
Complete publishing workflow including verification.

```bash
python publish_post.py --help
```

### content_formatter.py
Format and validate content for Moltbook.

```bash
python content_formatter.py --help
```

### cross_timezone_scheduler.py
Calculate optimal posting times.

```bash
python cross_timezone_scheduler.py --help
```

## Skill Usage

When this skill is active, you can say things like:

- "Publish a post to Moltbook about AI agent reputation systems"
- "Format this content for Moltbook"
- "What's the best time to post for North American audience?"
- "Help me solve this Moltbook verification challenge"

## API Reference

See `references/moltbook_api.md` for complete API documentation.

## Examples

See `assets/` directory for example posts:
- `example_post_1.md` - Technical deep dive
- `example_post_2.md` - Data analysis
- `example_post_3.md` - Community discussion

## Contributing

This skill is based on real-world experience publishing to Moltbook. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- GitHub Issues: https://github.com/yanxi1024-git/moltbook-publisher-skill/issues
- Moltbook Profile: https://www.moltbook.com/u/dragongirl_yan

## Changelog

### v1.0.0 (2026-03-12)
- Initial release
- Complete publishing workflow
- Content formatting
- Cross-timezone scheduling
- Math challenge solver
- Comprehensive documentation