# Brand Graphs

## Create a brand

Guide through 6 questions:
1. "What's the brand name?" (creates directory)
2. "What does it do? 1-2 sentences." (identity: positioning, description)
3. "Who do you create content for?" (audience: roles, interests, pain points)
4. "Content goals?" (strategy: goals)
5. "Brand colors?" (visual: hex codes, optional)
6. "Niche keywords?" (strategy: niche_keywords)

Save YAML files to `BASE_DIR/brand-graphs/<name>/`:
- identity.yaml, audience.yaml, strategy.yaml, visual.yaml, feedback.yaml (empty insights list)

After saving, automatically run topic discovery (see references/topics.md).

## Create from template

Available templates in `BASE_DIR/brand-graphs/templates/`: saas-b2b, dev-tools, ai-ml

1. Copy template to `BASE_DIR/brand-graphs/<name>/`
2. Walk through each file, show placeholders, ask user to customize
3. Auto-run topic discovery after customization

## Show brand

Read all YAML files from `BASE_DIR/brand-graphs/<name>/` and display formatted summary.

## Brand graph diff

When user asks what the feedback loop learned:
1. Read `BASE_DIR/brand-graphs/<name>/feedback.yaml`
2. Compare latest insights to previous (by checked_at timestamp)
3. Summarize patterns: which platforms/recipes/topics perform best
4. Suggest adjustments
