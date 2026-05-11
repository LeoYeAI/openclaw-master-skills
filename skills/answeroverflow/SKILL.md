---
name: answeroverflow
description: Search indexed Discord community discussions via Answer Overflow. Find solutions to coding problems, library issues, and community Q&A that only exist in Discord conversations.
---

# Answer Overflow Skill

Search indexed Discord community discussions via Answer Overflow. Great for finding solutions to coding problems, library issues, and community Q&A.

## What is Answer Overflow?

Answer Overflow indexes public Discord support channels and makes them searchable via Google and direct API access. Perfect for finding answers that only exist in Discord conversations.

## Quick Search

Use web_search to find Answer Overflow results:
```bash
# Search for a topic (Answer Overflow results often appear in Google)
web_search "site:answeroverflow.com prisma connection pooling"
```

## Fetching Thread Content

### Markdown URLs
Add `/m/` prefix or `.md` suffix to get markdown-formatted content:

```
# Standard URL
https://www.answeroverflow.com/m/1234567890123456789

# With .md suffix (alternative)
https://www.answeroverflow.com/m/1234567890123456789.md
```

### Using web_fetch
```bash
# Fetch a thread in markdown format
web_fetch url="https://www.answeroverflow.com/m/<message-id>"
```

### Accept Header
When making requests, the API checks for `Accept: text/markdown` header to return markdown format.

## MCP Server (Reference)

Answer Overflow has an MCP server at `https://www.answeroverflow.com/mcp` with these tools:

| Tool | Description |
|------|-------------|
| `search_answeroverflow` | Search across all indexed Discord communities. Can filter by server or channel ID. |
| `search_servers` | Discover Discord servers indexed on Answer Overflow. Returns server IDs for filtered searching. |
| `get_thread_messages` | Get all messages from a specific thread/discussion. |
| `find_similar_threads` | Find threads similar to a given thread. |

## URL Patterns

| Pattern | Example |
|---------|---------|
| Thread | `https://www.answeroverflow.com/m/<message-id>` |
| Server | `https://www.answeroverflow.com/c/<server-slug>` |
| Channel | `https://www.answeroverflow.com/c/<server-slug>/<channel-slug>` |

## Common Searches

```bash
# Find Discord.js help
web_search "site:answeroverflow.com discord.js slash commands"

# Find Next.js solutions
web_search "site:answeroverflow.com nextjs app router error"

# Find Prisma answers
web_search "site:answeroverflow.com prisma many-to-many"
```

## Tips

- Results are real Discord conversations, so context may be informal
- Threads often have back-and-forth discussion before the solution
- Check the server/channel name to understand the context (e.g., official support vs community)
- Many open source projects index their Discord support channels here

## Links

- **Website:** https://www.answeroverflow.com
- **Docs:** https://docs.answeroverflow.com
- **MCP:** https://www.answeroverflow.com/mcp
- **Discord:** https://discord.answeroverflow.com
