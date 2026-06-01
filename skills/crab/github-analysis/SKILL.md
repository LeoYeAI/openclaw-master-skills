---
name: github-analysis
description: |
  GitHub repository code analysis. Uses local script
  `skills/scripts/github_analyze.js` to convert a repo into an AI-friendly
  Markdown snapshot. No external API required.
metadata:
  author: NotevenDe
  version: 1.2.0
---

# GitHub Analysis — Repository Inspection

## Local Script

Script path: `skills/scripts/github_analyze.js`

### Functions

| Function | Description |
|----------|-------------|
| `analyzeRepository(url, options?)` | Metadata, structure, README, languages, architecture, recent commits |
| `convertToMarkdown(url, options?)` | Convert repo to a single AI-friendly Markdown document with file contents |
| `parseGitHubUrl(url)` | Parse GitHub URL or `owner/repo` into `{ owner, repo }` |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `depth` | 2 | Directory depth limit (analyzeRepository only) |
| `maxFiles` | 75 | Max files to include (convertToMarkdown only) |
| `maxSize` | 30000 | Max size per file in bytes (convertToMarkdown only) |

## Fallback Behavior

| Scenario                     | Behavior                                  |
|-----------------------------|-------------------------------------------|
| Repo not found or private   | Skip, record a warning                    |
