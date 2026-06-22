# Complete Workflow Reference

## Channel and Target

`--channel` and `--target` are extracted by the Agent from conversation context; this skill does not implement channel-specific logic.

## Quick Reference

All channels use `create` uniformly (sync mode: create task + poll for result + download result).

```
Scenario A (Topic infographic):       create(--mode article) → get local image → deliver
Scenario B (Long-form infographic):   create(--mode article) → get local image → deliver
Scenario C (Sketch to infographic):   transfer → create(--mode reference --reference-type sketch) → deliver
Scenario D (Style transfer):          transfer → create(--mode reference --reference-type style_transfer) → deliver
Scenario E (Product embed):           transfer → create(--mode reference --reference-type product_embed) → deliver
Scenario F (Content rewrite):         transfer → create(--mode reference --reference-type content_rewrite) → deliver
Scenario G (Batch infographics):      create(--mode article --count 3) → get local images → deliver
Scenario H (Retry):                   cat action_log → create(--action switch_style --last-task-id xxx) → deliver
Scenario I (Modify previous):         cat action_log → create(--mode reference --reference-type content_rewrite --reference-image-urls <url>) → deliver
```

---

## Detailed Examples

### Scenario A: Topic Infographic

When the user provides only a one-line topic, proactively suggest content structure first, then create using `article` mode with the enriched content.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/check_config.py

python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --mode article \
  --article "Einstein's Life: Childhood and education, the development of special and general relativity, impact on modern physics and public science communication." \
  --style-hint "minimalist" \
  --aspect-ratio "3:4" \
  --locale "en-US"
# Returns {"success": true, "task_id": "xxx", "images": ["/abs/path/result_xxx.png"], ...}
```

### Scenario B: Long-form Text to Infographic

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --mode article \
  --article "A long article about AI development..." \
  --style-hint "tech"
```

### Scenario C: Sketch to Infographic

```bash
# 1. Upload sketch
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py transfer \
  --file "/path/to/sketch.jpg"
# Get image_url, width, height

# 2. Create task (sync wait for result)
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --mode reference \
  --reference-type sketch \
  --reference-image-urls "<image_url>" \
  --reference-image-width <width> \
  --reference-image-height <height>
```

### Scenario D: Style Transfer Infographic

```bash
# 1. Upload reference infographic
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py transfer \
  --file "/path/to/reference.png"
# Get image_url, width, height

# 2. Create task
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --mode reference \
  --reference-type style_transfer \
  --reference-image-urls "<image_url>" \
  --reference-image-width <width> \
  --reference-image-height <height> \
  --reference-topic "The Origin and History of Gold"
```

### Scenario E: Product Embed Infographic

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py transfer \
  --file "/path/to/product.png"
# Get image_url, width, height

python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --mode reference \
  --reference-type product_embed \
  --reference-image-urls "<image_url>" \
  --reference-image-width <width> \
  --reference-image-height <height> \
  --reference-article "Product selling points copy..."
```

### Scenario F: Content Rewrite Infographic

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py transfer \
  --file "/path/to/existing_infographic.png"
# Get image_url, width, height

python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --mode reference \
  --reference-type content_rewrite \
  --reference-image-urls "<image_url>" \
  --reference-image-width <width> \
  --reference-image-height <height> \
  --reference-article "New replacement content..."
```

### Scenario G: Batch Infographics

**Simple batch (user has specified count + topic)**:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --mode article \
  --article "The Origin and History of Gold: Part one covers gold's cosmic origins and natural formation; part two covers currency, power, and religious symbolism in ancient civilizations; part three covers modern financial reserves, jewelry, and industrial applications." \
  --style-hint "classical hand-drawn" \
  --count 3
```

**Planned batch (Agent plans content → passes via article mode)**:

User says "generate a series of infographics about the history of gold", Agent plans content:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --mode article \
  --article "History of Gold

Chapter 1: The Cosmic Origins of Gold
Gold was born from supernova explosions and neutron star collisions. About 4.5 billion years ago when Earth formed, large amounts of gold sank into the core with meteorites...

Chapter 2: Gold in Ancient Civilizations
Around 3000 BCE, Egyptian pharaohs regarded gold as the embodiment of the sun god. Tutankhamun's gold mask weighs 11 kilograms...

Chapter 3: Evolution of Gold Smelting Technology
From the earliest river panning, to the Roman amalgamation method, to the cyanide process invented in 1887...

Chapter 4: Gold and Monetary Systems
Around 700 BCE, Lydia minted humanity's first gold coin. In 1816, Britain established the gold standard...

Chapter 5: Modern Gold
In 2024, global gold reserves total approximately 36,000 tonnes. Gold is used in the electronics industry for chip bonding wires..." \
  --count 5 \
  --style-hint "classical hand-drawn" \
  --child-reference-type content_rewrite
```

```bash
# Batch generate 4 coherent infographic pages (content_rewrite, user provided long text)
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --mode article \
  --article "A long article about AI development..." \
  --count 4 \
  --child-reference-type content_rewrite
```

### Scenario H: Retry (for existing results)

> Applicable when: User references a previously generated infographic and requests regeneration, style change, or content change.
> Note: When retrying, use the previous task's `last_task_id`; no need to re-upload reference images (reference image URLs are recorded in task history).
> Note: `content_rewrite` / `style_transfer` type results using `action=switch_style` will be downgraded to `switch_all`.

**First, read the action log:**

```bash
cat ~/.openclaw/media/plume/action_log_{channel}.json
# If empty, fallback: cat ~/.openclaw/media/plume/last_result_{channel}.json
```

**"Try again" (replay last operation):**

```bash
# Read the last entry from action_log
# If action is null (first creation) → repeat_last_task
# If action is not null → replay with same action and params, last_task_id from the last entry's last_task_id

python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --action <same action as last entry> \
  --last-task-id <last_task_id from last entry>
```

**Regenerate (same content and style):**

```bash
# Get task_id from the most recent entry with status=success
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --action repeat_last_task \
  --last-task-id <task_id from success entry>
```

**Switch style (same content, different style):**

```bash
# Get params.article from the base record in action_log
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --action switch_style \
  --last-task-id <task_id from success entry> \
  --article "<params.article from base record>"
```

**Switch content (same style, different topic/content):**

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --action switch_content \
  --last-task-id <task_id from success entry> \
  --article "<new complete content>"
```

### Scenario I: Generate New Content Using Previous Infographic as Reference

Use the previously generated infographic as a reference image (style_transfer), fill in new content to regenerate. Note: This is a new task, not a retry. The executor will extract the reference image's style and regenerate; it will not preserve the original layout details.

```bash
# 1. Read image URL from previous result (prefer action_log, fallback to last_result)
cat ~/.openclaw/media/plume/action_log_{channel}.json
# Get result_url from the most recent entry with status=success
# If empty: cat ~/.openclaw/media/plume/last_result_{channel}.json, get result_url

# 2. Create task with reference style + new content (content_rewrite flow)
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> \
  --mode reference \
  --reference-type content_rewrite \
  --reference-image-urls "<result_url>" \
  --reference-article "New content text..."
```

---

## Image Source Priority

1. Current message has attached image → `transfer --file`
2. No image, user refers to "the last one" → read `action_log_{channel}.json` for most recent success `result_url`, fallback to `last_result_{channel}.json`
3. Neither available → prompt user to send an image
