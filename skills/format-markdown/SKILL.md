---
name: format-markdown
description: Summarize and format markdown files, then apply mkdocs/material-compatible structural spacing fixes for math, list, and table blocks. Outputs to {filename}_formatted.md by default.
metadata: { "version": 1.0.0 }
---

# Markdown Formatter

Markdown formatting skill with two layers of processing:

1. **Content formatting**: analyze content, improve readability, and add metadata or structural aids when needed.
2. **Structural compatibility fixing**: apply mkdocs/material-safe spacing fixes for math, list, and table blocks without rewriting text content.

You MUST follow the workflow in the `Workflow` section below and must not skip required steps.

## Core Principles

- Preserve original meaning and wording as much as possible.
- In **content-formatting mode** (Steps 2-5), metadata and structural aids may be added, such as title, summary, headings, emphasis, lists, tables, and admonitions.
- In **Step 6 structural-fix mode**, the script performs whitespace-only changes and never rewrites text content.

| Principle                  | Requirement                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------------- |
| **Meaning Preservation**   | Preserve the author's meaning, tone, and wording as much as possible.                    |
| **Structural Additions**   | In formatting mode, only add metadata or formatting structures that improve readability. |
| **Whitespace-Only Script** | Step 6 may only modify whitespace, empty lines, and structural spacing.                  |
| **Rendering Safety**       | Ensure all changes improve markdown rendering stability in mkdocs/material style.        |
| **Traceability**           | Every meaningful change must be summarized in the final report.                          |

---

## Usage

The workflow has two phases:

1. **Analyze and format content** (Steps 1-5)
2. **Apply structural compatibility fixes** for mkdocs/material rendering (Step 6)

Claude performs content analysis and formatting first, then runs the structural compatibility script as the final cleanup step.

## Workflow

### Step 1: Read & Detect Content Type

Read the user-specified file, then detect content type:

| Indicator                                                   | Classification |
| ----------------------------------------------------------- | -------------- |
| Has `---` YAML frontmatter                                  | Markdown       |
| Has `#`, `##`, `###` headings                               | Markdown       |
| Has `**bold**`, `*italic*`, lists, code blocks, blockquotes | Markdown       |
| None of above                                               | Plain text     |

**If Markdown is detected, ask the user:**

```text
Detected existing markdown formatting. What would you like to do?

1. Optimize formatting (Recommended)
   - Analyze content, improve headings, bold, lists, tables, and readability
   - Run structural compatibility script afterward
   - Output: {filename}_formatted.md

2. Keep original formatting
   - Preserve existing markdown structure
   - Run structural compatibility script only on the copied file
   - Output: {filename}_formatted.md

3. Structural fixes only
   - Run the structural compatibility script on the original file in-place
   - No copy created; modifies the original file directly
```

**Based on user choice:**

- **Optimize**: Continue to Step 2 (full workflow)
- **Keep original**: Skip to Step 5, copy file, then run Step 6
- **Structural fixes only**: Skip to Step 6 and run on the original file directly

---

### Step 2: Analyze Content (Reader's Perspective)

Read the entire content carefully. Think from a reader's perspective: what would help them quickly understand and remember the key information?

Produce an analysis covering these dimensions:

#### 2.1 Highlights & Key Insights

- Core arguments or conclusions the author makes
- Surprising facts, data points, or counterintuitive claims
- Memorable quotes or well-phrased sentences (golden quotes)

#### 2.2 Structure Assessment

- Does the content have a clear logical flow? What is it?
- Are there natural section boundaries that lack headings?
- Are there long walls of text that could benefit from visual breaks?

#### 2.3 Reader-Important Information

- Actionable advice or takeaways
- Definitions and explanations of key concepts
- Lists or enumerations buried in prose
- Comparisons or contrasts that would be clearer as tables

#### 2.4 Formatting Issues

- Missing or inconsistent heading hierarchy
- Paragraphs that mix multiple topics
- Parallel items written as prose instead of lists
- Code, commands, or technical terms not marked as code
- Obvious typos or formatting errors

**Save analysis to file**: `{original-filename}-analysis.md`

The analysis file serves as the blueprint for Step 3. Use this format:

```markdown
# Content Analysis: {filename}

## Highlights & Key Insights

- [list findings]

## Structure Assessment

- Current flow: [describe]
- Suggested sections: [list heading candidates with brief rationale]

## Reader-Important Information

- [list actionable items, key concepts, buried lists, potential tables]

## Formatting Issues

- [list specific issues with location references]

## Typos Found

- [list any obvious typos with corrections, or "None found"]
```

---

### Step 3: Check/Create Frontmatter, Title & Summary

Check for YAML frontmatter (`---` block). Create it if missing.

| Field        | Processing                                                                       |
| ------------ | -------------------------------------------------------------------------------- |
| `title`      | See **Title Generation** below                                                   |
| `slug`       | Infer from file path or generate from title                                      |
| `summary`    | See **Summary Generation** below                                                 |
| `coverImage` | Check if `imgs/cover.png` exists in the same directory; if so, use relative path |

#### Title Generation

Whether or not a title already exists, always run the title optimization flow unless `auto_select_title` is set.

**Preparation** — read the full text and extract:

- Core argument (one sentence: "what is this article about?")
- Most impactful opinion or conclusion
- Reader pain point or curiosity trigger
- Most memorable metaphor or golden quote

**Generate 3-4 style-differentiated candidates:**

| Style           | Characteristics                         | Example                                                 |
| --------------- | --------------------------------------- | ------------------------------------------------------- |
| Subversive      | Deny common practice, create conflict   | "All de-AI-flavor prompts are wrong"                    |
| Solution        | Give the answer directly, promise value | "One recipe to make AI write in your voice"             |
| Suspense        | Reveal half, spark curiosity            | "It took me six months to find how to remove AI flavor" |
| Concrete number | Use numbers for credibility             | "150 lines of docs taught AI my writing style"          |

Present to the user:

```text
Pick a title:

1. [Title A] — (recommended)
2. [Title B] — [style note]
3. [Title C] — [style note]

Enter number, or type a custom title:
```

Put the strongest hook first and mark it as recommended.

**Title principles:**

- **Hook in the first 5 chars**: create an information gap or cognitive conflict
- **Specific > abstract**: "150 lines" beats "a document"
- **Negation > affirmation**: "you're doing it wrong" beats "the right way"
- **Conversational**: like chatting with a friend, not a paper title
- **Max ~25 chars**: longer titles get truncated in feeds
- **Accurate, not clickbait**: the article must deliver what the title promises

**Prohibited patterns:**

- "浅谈 XX"、"关于 XX 的思考"、"XX 的探索与实践"
- "震惊！"、"万字长文"、"建议收藏"
- Pure questions without direction: "AI 写作的未来在哪里？"

If `title` exists in frontmatter and there is no H1 in the body content, **YOU MUST insert the title as the first H1 (`# {{title}}`)**. Do not remove it. If frontmatter already has `title`, include it as context but still generate fresh candidates unless skipped by configuration.

#### Summary Generation

Generate 3 candidate summaries with different angles. Present to the user:

```text
Pick a summary:

1. [Summary A] — [focus note]
2. [Summary B] — [focus note]
3. [Summary C] — [focus note]

Enter number, or type a custom summary:
```

**Summary principles:**

- 80-150 characters, precise and information-rich
- Convey the **core value** to the reader, not just the topic
- Vary angles: problem-driven, result-driven, insight-driven
- **Hook the reader**: make them want to read the full article
- Use concrete details (numbers, outcomes, specific methods) over vague descriptions

**Prohibited patterns:**

- "本文介绍了..."、"本文探讨了..."
- Pure topic description without value proposition
- Repeating the title in different words

If frontmatter already has `summary`, skip selection and use it.

To make the summary appear visibly, generate it following the **Admonition Syntax Rules**. Place it after the H1 title:

```markdown
!!! example "Summary"

    Here is the summary you generated.
```

**EXTEND.md skip behavior:** If `auto_select: true` is set in `EXTEND.md`, skip title and summary selection and generate the best candidate directly without asking. The user may also set `auto_select_title: true` or `auto_select_summary: true` independently.

---

### Step 4: Format Content

Apply formatting guided by the Step 2 analysis. The goal is to make the content scannable and the key points easy to grasp.

#### Formatting toolkit

| Element         | When to use                                                 | Format                                                 |
| --------------- | ----------------------------------------------------------- | ------------------------------------------------------ |
| Headings        | Natural topic boundaries, section breaks                    | `##`, `###` hierarchy                                  |
| Bold            | Key conclusions, important terms, core takeaways            | `**bold**`                                             |
| Unordered lists | Parallel items, feature lists, examples                     | `- item`                                               |
| Ordered lists   | Sequential steps, ranked items, procedures                  | `1. item`                                              |
| Highlights      | Critical details, important comparisons for quick attention | `==text==`                                             |
| Color highlight | Colored emphasis where standard bold is insufficient        | `<span style="color:red;font-weight:bold">text</span>` |
| Tables          | Comparisons, structured data, option matrices               | Markdown table                                         |
| Code            | Commands, file paths, technical terms, variable names       | `` `inline` `` or fenced blocks                        |
| Blockquotes     | Notable quotes, important warnings, cited text              | `> blockquote`                                         |
| Admonition      | Definitions, examples, notable warnings, conclusions        | Follow **Admonition Syntax Rules** below               |
| Separators      | Major topic transitions                                     | `---`                                                  |

#### Admonition Syntax Rules

Strict enforcement. When using MkDocs-style admonitions (e.g. `!!! note`, `!!! example`, `!!! warning`), you must follow these indentation rules strictly. Markdown parsers require content inside the block to be indented.

**Correct format:**

```markdown
!!! note "Title Text"

    This is the content. It must start with 4 spaces, and the above line is empty.

    This is a second paragraph. It also needs **4** spaces indentation.

    - List items also follow. The end line should have an empty line with no indent below.

This is the line outside admonition (correct).
```

**Incorrect format (DO NOT DO THIS):**

```markdown
!!! note "Title Text"
This content has no indent. (Wrong - breaks indentation rule)

!!! note "Title Text"

    First paragraph ok.

Second paragraph has no indent. (Wrong - breaks the block)
```

**Syntax rules:**

1. **Indentation**: All content belonging to the admonition must be indented **4 spaces** relative to the `!!!` line.
2. **Paragraph breaks**: Blank lines inside the block must also preserve block structure; ensure the next paragraph starts with 4 spaces.
3. **Nested lists/code**: If using lists or code inside an admonition, indent them **8 spaces** total.
4. **Consistency**: Do not mix tabs and spaces. Use 4 spaces consistently.

#### Formatting principles — what NOT to do

- Do NOT add invented facts, explanations, or commentary
- Do NOT delete or shorten valid original content without user intent
- Do NOT rephrase or rewrite the author's wording unless the task explicitly requires it
- Do NOT add headings that editorialize (e.g. "Amazing Discovery"); use neutral descriptive headings
- Do NOT over-format: not every sentence needs bold, and not every paragraph needs a heading

#### Formatting principles — what TO do

- Preserve the author's voice, tone, and wording as much as possible
- **Bold key conclusions and core takeaways** — the sentences a reader would likely highlight
- Extract parallel items from prose into lists when the structure is clearly present
- Add headings where the topic genuinely shifts
- Use tables for comparisons or structured data buried in prose
- Use blockquotes for golden quotes, memorable statements, or important warnings
- Fix obvious typos **only when the correction is unambiguous**

---

### Step 5: Save Formatted File

Save the formatted content as a new file. The output filename is built from the original filename plus a suffix defined in `EXTEND.md`.

- **Default suffix**: `_formatted` → `{original-filename}_formatted.md`
- **Override via `EXTEND.md`**: set `output_suffix: _formatted` → `{original-filename}_formatted.md`

**Backup existing file before overwrite:**

```bash
if [ -f "{filename}_formatted.md" ]; then
  mv "{filename}_formatted.md" "{filename}_formatted.backup-$(date +%Y%m%d-%H%M%S).md"
fi
```

After Step 5 saves the formatted file, Step 6 must run on that saved output file **in-place**.

---

### Step 6: Execute Structural Rendering Compatibility Script

Scripts are stored in the `scripts/` subdirectory. `${SKILL_DIR}` is the root directory containing this `SKILL.md`.

This script is designed for **MkDocs + Material** rendering compatibility. It fixes structural spacing around math, list, and table blocks while preserving document content.

#### Runtime Requirements

- **Node.js 18+**
- Local npm dependencies installed once in `${SKILL_DIR}`

If dependencies are not installed yet:

```bash
cd ${SKILL_DIR}
npm install
```

If `package-lock.json` already exists, prefer:

```bash
cd ${SKILL_DIR}
npm ci
```

#### Script

| Script                         | Purpose                                                               |
| ------------------------------ | --------------------------------------------------------------------- |
| `scripts/format-structure.mjs` | Fixes mkdocs/material-sensitive spacing around math/list/table blocks |

#### Command

```bash
node ${SKILL_DIR}/scripts/format-structure.mjs <file.md> [options]
```

#### CLI Options

| Option        | Short | Description                         | Default  |
| ------------- | ----- | ----------------------------------- | -------- |
| `--output`    | `-o`  | Specify output file path            | In-place |
| `--dry-run`   | `-n`  | Preview changes without writing     | false    |
| `--no-backup` |       | Skip backup of existing output file | false    |

#### What the script fixes

1. **Math block spacing**
   - Ensures block math has blank lines before and after
   - Handles standalone single-line block math such as `$$E = mc^2$$`
   - Removes illegal inner blank lines immediately after opening `$$` or before closing `$$`

2. **List block spacing**
   - Ensures blank lines before and after markdown lists

3. **Table block spacing**
   - Ensures blank lines before and after markdown tables

4. **Safety**
   - Uses Markdown AST to detect structural blocks
   - Applies minimal text patches instead of re-stringifying the full document
   - Preserves text content and existing writing style as much as possible

#### EXTEND.md Rule Toggles

The script reads simple `key: value` settings from `EXTEND.md`.

Supported keys:

```md
output_suffix: \_formatted
fix_math_blocks: true
fix_list_blocks: true
fix_table_blocks: true
trim_math_inner_blank_lines: true
```

#### Usage in Workflow

- **Full workflow**: after Step 5 saves the formatted file, run the script **in-place** on that output file.
- **Structural-fixes-only mode**: run the script directly on the original file in-place.

Examples:

```bash
# In-place fix on already formatted output
node ${SKILL_DIR}/scripts/format-structure.mjs "{output-file-path}"

# Write to a custom file
node ${SKILL_DIR}/scripts/format-structure.mjs article.md -o article_fixed.md

# Preview only
node ${SKILL_DIR}/scripts/format-structure.mjs article.md --dry-run

# Skip backup
node ${SKILL_DIR}/scripts/format-structure.mjs article.md --no-backup
```

#### Output and Backup Behavior

| Condition                                     | Output Path                    |
| --------------------------------------------- | ------------------------------ |
| Default                                       | Input file modified in-place   |
| With `--output custom.md`                     | `custom.md`                    |
| Step 5 + default suffix                       | `{original-name}_formatted.md` |
| With `output_suffix: _formatted` in EXTEND.md | `{original-name}_formatted.md` |

If the target output file already exists and `--no-backup` is **not** set, the script creates a timestamped backup before writing.

---

## 📋 Step 7: Completion Report

```text
**Formatting Complete**

**Files:**
- Analysis: {filename}-analysis.md
- Formatted: {filename}_formatted.md

**Content Analysis Summary:**
- Highlights found: X key insights
- Golden quotes: X memorable sentences
- Formatting issues fixed: X items

**Changes Applied:**
- Frontmatter: [added/updated] (title, slug, summary)
- Headings added: X (##: N, ###: N)
- Bold markers added: X
- Lists created: X (from prose → list conversion)
- Tables created: X
- Admonitions added: X
- Typos fixed: X [list each: "original" → "corrected"]

**Structural Compatibility Script:**
- Math blocks processed: X
- List blocks processed: X
- Table blocks processed: X
- Empty lines added: X
- Math inner blank lines removed: X
- Backup created: [yes/no]
```
