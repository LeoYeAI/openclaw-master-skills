# Content Claw - TODOS

## P1 - Must build (Phase 1)

### Define recipe YAML schema
- **What:** Formalize the recipe YAML format: required fields, content block structure, prerequisite format, KPI strategy format, schema version field.
- **Why:** Everything validates against this. Recipes, the engine, and the post-synthesis validator all depend on a stable schema.
- **Effort:** S
- **Blocked by:** Nothing. This is the first task.

### Convert 13 recipes from CSV to YAML
- **What:** Take the existing Notion CSV export (13 recipes) and convert each row to a validated recipe YAML file.
- **Why:** Seeds the system with real recipes. The CSV has: name, platform, priority, prerequisites, references, schema version, brand graph requirements.
- **Effort:** S
- **Blocked by:** Recipe YAML schema.

### Write SKILL.md (core skill definition)
- **What:** Write the OpenClaw SKILL.md that teaches the agent the full Content Claw pipeline: recipe execution, brand graph wizard, recipe listing, error handling, all user commands.
- **Why:** This IS the product. The SKILL.md is the instruction set that makes the OpenClaw agent a content engine.
- **Effort:** M
- **Blocked by:** Recipe YAML schema, at least 1 recipe YAML file.

### Build source extractor registry
- **What:** Modular Python extractors dispatched by URL pattern: web, PDF, YouTube, Twitter/X, Reddit, GitHub, podcast. Start with web + PDF.
- **Why:** Recipes can't run without source extraction. The existing recipes reference papers, podcasts, Reddit posts, GitHub repos.
- **Effort:** M (web + PDF first, then add others incrementally)
- **Blocked by:** Nothing (can build in parallel with SKILL.md).

### Post-synthesis content validator
- **What:** Python validation layer that checks each generated content block: non-empty, no LLM refusal markers, matches expected format. Retry once on failure, then placeholder + warning.
- **Why:** Catches the 3 most dangerous silent failures in the pipeline (empty, refusal, malformed output).
- **Effort:** S
- **Blocked by:** Recipe YAML schema (needs to know expected formats).

## P2 - Should build (Phase 2)

### Specialized agent prompts
- **What:** Write per-format synthesis prompts (agents/*.md): insight post, infographic, thread, case study, UGC video script. Start with the 3 formats used by p0 recipes.
- **Why:** Generic prompts produce generic content. Specialized prompts are the quality differentiator.
- **Effort:** M
- **Blocked by:** SKILL.md + at least 1 working recipe.

### Recipe preview / dry-run mode
- **What:** Before running a full recipe, show the user what will happen: blocks to generate, prerequisites to run, estimated time, brand graph requirements.
- **Why:** Users feel in control. Builds trust.
- **Effort:** S

### Brand graph health check (soft prompts)
- **What:** When running a recipe, detect missing optional brand graph fields and offer to fill them. "This recipe works better with brand colors set. Want to add them now?"
- **Why:** Contextual onboarding instead of hard-fail. Delightful.
- **Effort:** S

### Recipe suggestion by source type
- **What:** When user provides a URL without specifying a recipe, analyze the source and suggest matching recipes.
- **Why:** Reduces friction. Users don't need to memorize recipe names.
- **Effort:** S

### Remix command (cross-platform adaptation)
- **What:** After generating content, user says "remix this for Reddit" and the skill re-dispatches with same prereq data but a different platform recipe.
- **Why:** Zero-friction cross-posting. Multi-platform feels effortless.
- **Effort:** S
- **Blocked by:** Run artifact system (cached prereq data).

### Run artifact storage
- **What:** Save each run's context: input recipe, topic, brand snapshot, prereq outputs, generated blocks, timing, model used, errors. Stored in content/<date>_<recipe>_<brand>/.
- **Why:** Debugging and reproducibility. If output is off-brand, you can reconstruct exactly what happened.
- **Effort:** S

## P3 - Phase 3 (after generation pipeline is solid)

### Platform publishers
- **What:** Build publishing scripts for LinkedIn, Reddit, X. Handle auth, rate limits, content formatting per platform.
- **Why:** Close the loop: generate + publish from one chat command.
- **Effort:** L
- **Blocked by:** Working generation pipeline, platform API credentials.

### Content calendar view
- **What:** "Show me this week's content" command: summary of generated content, scheduled posts, recipe runs by day/platform.
- **Why:** Turns Content Claw from a tool into a content ops dashboard in chat.
- **Effort:** M
- **Blocked by:** Publishers + run artifact storage.

### KPI tracking + feedback loop
- **What:** Collect performance data from platform APIs (impressions, engagement, clicks). Feed insights back into brand graph feedback layer.
- **Why:** Recipes learn what works. Content improves over time.
- **Effort:** L
- **Blocked by:** Publishers.

## P4 - Phase 4 (platform / marketplace)

### ClawHub publication
- **What:** Package Content Claw for ClawHub. Write docs, test clean install, submit PR.
- **Why:** Distribution. Other content teams can install Content Claw.
- **Effort:** M
- **Blocked by:** Stable recipe schema (can't change after publication).

### Recipe marketplace / sharing
- **What:** Community-contributed recipes, brand graph templates by industry, agent prompt sharing.
- **Why:** Network effects. More recipes = more value = more users.
- **Effort:** XL
- **Blocked by:** ClawHub publication + stable schema.
