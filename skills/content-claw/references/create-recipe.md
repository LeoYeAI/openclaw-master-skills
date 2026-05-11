# Create Recipe Wizard

Walk the user through 7 questions. Confirm each answer before proceeding.

## Questions

1. **Name**: "What should this recipe do?" Derive slug (lowercase, hyphenated).
2. **Source type**: research-paper, podcast, blog, case-study, github-repo, event-news, social-post. Can pick multiple.
3. **Platforms**: linkedin, reddit, x, email. Can pick multiple.
4. **Brand graph**: Required? Which layers? (identity, audience, strategy, visual)
5. **Prerequisites**: Suggest defaults by source type, ask to add/remove.
   - research-paper/blog: extract-text, summarize, generate-title, research-context
   - podcast: extract-text, extract-key-points, generate-title, research-context
   - case-study/github-repo: extract-text, extract-key-points, generate-title, research-context
   - event-news: extract-text, summarize, generate-title
   - social-post: extract-text, summarize
6. **Content blocks**: For each: name, format (text/image), rules, agent (existing or new), dependencies. Show existing agents. Ask "Any more blocks?"
7. **Review**: Show full YAML. Ask for changes. Save to `BASE_DIR/recipes/<slug>.yaml`.

## Creating a new agent

If user needs a new agent for a block:
1. Ask how the content should be structured
2. Create at `BASE_DIR/agents/<name>.md` with:
   - Phase 1: JSON spec schema (must include platform, source, text_fallback)
   - Phase 2: how to render spec to final text
   - Rules section
   - Platform adaptation section
3. Show user for approval before saving
