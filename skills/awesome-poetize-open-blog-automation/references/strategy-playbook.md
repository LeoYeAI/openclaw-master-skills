# Strategy Playbook

Use this playbook when OpenClaw needs to decide what kind of blog action to take before touching the Poetize API.

## Default position

- Treat the blog as a long-term content asset, not a short-term monetization funnel.
- Default to free publishing.
- Prefer maintaining and upgrading existing articles before creating near-duplicate new ones.
- Use hiding instead of deletion when a post should be taken down from public view.

## Action selection

Choose one action before executing:

- `create_article`
  - Use when the topic is meaningfully new and does not belong inside an existing article.
- `refresh_article`
  - Use when an article already exists and the best move is to improve, expand, or fix it.
- `repurpose_article`
  - Use when the new post is clearly a different angle or audience from the source material.
- `hide_article`
  - Use when the post should be removed from normal public visibility without deleting it.

## Publishing defaults

- Public by default for finished content.
- Draft when the user explicitly asks for preview, internal review, or unfinished work.
- Recommended only when the content is unusually strong or strategically important.
- Search push on by default for public evergreen content.
- Comments on by default unless the content is sensitive, low-value, or likely to attract noise.

## Monetization rules

- Default: `payType: 0`
- Do not suggest a paywall for ordinary personal-blog posts.
- Only allow paid publishing when:
  - the user explicitly asks for it
  - the content has clear conversion value
  - the task goal is `conversion`
- If those conditions are not met, force the content back to free.

## Maintenance-first heuristics

Prefer updating or hiding over creating when:

- the topic substantially overlaps an existing article
- the old article is outdated but still relevant
- the taxonomy structure would become noisier by adding another post
- the new draft would fragment traffic or search intent
