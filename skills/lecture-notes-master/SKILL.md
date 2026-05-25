---
name: lecture-notes-master
description: "Obsidian lecture notes with recursive atomic decomposition. Generates main note (hub), atomic notes (3+ layers deep, rich structure each), and unlimited glossary entries. Inputs: lectures, articles, videos, URLs, transcripts, PDFs. Outputs: Obsidian markdown with Mermaid diagrams, comparison tables, bilingual terms, wikilinks."
---

# Lecture Notes Master

Generate structured Obsidian lecture notes with **recursive atomic decomposition**:

- **主笔记 (Main Note)**: Hub note with overview, core sections, summary, review questions
- **原子笔记 (Atomic Notes)**: Deep concept notes in ≥3 layers, each layer with rich structure
- **原子概念 (Glossary)**: Unlimited bilingual term definitions

## When to Apply

**Triggers**:
- User provides: URL, video link, PDF, transcript, PPT, slides, article
- User says: "总结", "summarize", "create notes", "lecture notes", "笔记", "做笔记"
- User mentions: Obsidian, atomic notes, wikilinks, PARA, MOC
- User provides content for note-taking or analysis
- Exam prep / study materials

**Example prompts**:
- "总结一下这个视频 https://youtu.be/xxx"
- "Create lecture notes for this article"
- "帮我做笔记 https://www.example.com/article"
- "Summarize this into Obsidian notes"

---

## User Profile

Configured in `config.json`:

- **Name**: Schaefer (Zonghan Jia)
- **University**: Heidelberg University (ZITI), Computer Engineering
- **Obsidian Vault**: See `config.json` → `obsidian.vault_path`
- **Output Directory**: `00-Inbox/{Topic}/` (main note + glossary + numbered L1 subdirectories)
- **Language**: Bilingual — English primary, Chinese secondary
- **Term format**: `English Term（中文术语）`

---

## Core Principles

### Recursive Atomic Decomposition

Every source material is decomposed into a tree of notes, organized into **numbered subdirectories by L1 topic**:

```
{Topic}/
├── 主笔记: {Topic}-Notes.md
│   Hub note linking to all L1 atomic notes
│
├── 01-{L1-Concept-A}/
│   ├── {L1-Concept-A}.md              (L1 顶层概念)
│   ├── {L2-Sub-Concept-A1}.md         (L2 子概念)
│   ├── {L2-Sub-Concept-A2}.md         (L2 子概念)
│   ├── {L3-Detail-A1a}.md             (L3 细分解)
│   └── {L3-Detail-A1b}.md             (L3 细分解)
│
├── 02-{L1-Concept-B}/
│   ├── {L1-Concept-B}.md              (L1 顶层概念)
│   ├── {L2-Sub-Concept-B1}.md         (L2 子概念)
│   └── {L3-Detail-B1a}.md             (L3 细分解)
│
├── 03-{L1-Concept-C}/
│   └── {L1-Concept-C}.md              (L1 顶层概念)
│
├── glossary/（原子概念 — 术语定义，不限量）
│   ├── English Term（中文术语）.md
│   └── ... 每个术语一个文件
│
└── assets/（图表资源）
    └── *.png
```

### Directory Organization Rules

| Location | Contains | Example |
|----------|----------|---------|
| `{Topic}/` root | Main note only | `Lazygit-Notes.md` |
| `NN-{L1-Concept}/` | L1 note + its L2 children + their L3 children | `01-Installation-and-Setup/` |
| `glossary/` | All glossary entries | `glossary/TUI（终端用户界面）.md` |
| `assets/` | Generated charts/images | `assets/performance-chart.png` |

**Numbering Rules**:
1. L1 subdirectories use two-digit prefix: `01-`, `02-`, `03-`, ...
2. **No atomic notes in the topic root** — only the main hub note lives there
3. Within each L1 folder, all notes are flat (L1 + L2 + L3 together, no further nesting)
4. Numbering follows the order of L1 concepts as they appear in the main note
5. Wiki-links use filename only (no path prefix) — Obsidian resolves them automatically

### Decomposition Rules

**Layer 1 (顶层概念)**:
- Source material's major themes, sections, or arguments
- Each L1 note covers ONE major concept branch
- Number: determined by content (typically 3-7, NOT fixed)

**Layer 2 (子概念)**:
- Sub-concepts, mechanisms, or components within each L1 concept
- Each L2 explains a specific aspect of its parent L1
- Number: typically 2-4 per L1 parent

**Layer 3+ (细分解)**:
- Specific mechanisms, case studies, comparisons, or evidence
- Finest granularity of analysis
- Number: as many as the content demands

**Stop Decomposing When**:
- A concept can be fully explained in ≤500 words with one diagram
- Further splitting would break logical coherence
- The concept is better served as a glossary entry (pure definition)

**Glossary vs Atomic Note**:
| Use Glossary | Use Atomic Note |
|--------------|-----------------|
| Term needing a bilingual definition (1-3 sentences) | Concept requiring explanation, examples, diagrams |
| No deep analysis needed | Has sub-components worth exploring |
| Pure noun/term | Has "why", "how", comparison dimensions |

### Minimum Requirement

Every set of notes **MUST** produce:
- 1 main note (主笔记)
- ≥3 layers of atomic notes (L1 → L2 → L3 minimum)
- Glossary entries for ALL technical terms mentioned

### Every Atomic Note Must Be Rich

**ALL atomic notes (L1, L2, L3)** use the **same rich template** structure:

1. **定义** — One-paragraph definition with inline wikilinks
2. **Why Do We Need This?** — Motivation with concrete scenario
3. **Core Concept** — Idea + example + Mermaid diagram + step-by-step breakdown
4. **Comparison** — Table comparing with/without, or vs alternatives
5. **Common Pitfalls** — 2-3 mistakes and fixes (omit only if truly not applicable)
6. **Key Takeaway** — One flashcard-worthy sentence
7. **Review Questions** — 3 levels: recall, understanding, application
8. **Related Notes** — Parent (UP), children (DOWN), siblings (ACROSS)

> See `templates/atomic-note.md` for the full template.

### Writing Style: Runoob Tutorial（菜鸟教程风格）

| Rule | Description |
|------|-------------|
| **Step-by-step** | "Why do we need this?" → "What is it?" → "How does it work?" → "Watch out for..." |
| **Example-driven** | Example FIRST, then explain the principle. Never start with pure theory |
| **Visual-rich** | Every concept gets at least one Mermaid diagram OR table |
| **Table comparison** | Similar concepts → comparison table |
| **Bilingual terms** | `English Term（中文）`, English is primary |
| **Atomic** | Each note covers exactly ONE concept |
| **Review questions** | 3 per note: recall, understanding, application |

---

## Prerequisites

```bash
python3 --version || python --version
pip3 install matplotlib numpy  # For visualization scripts (optional)
```

Optional: `summarize` CLI for URL/video content extraction.

---

## Workflow

### Step 1: Analyze User Input

Identify: input type (URL, video, PDF, transcript, raw text), topic name, key themes.

#### URL & Video Content Extraction

When user provides a URL or video link, use `summarize` CLI:

```bash
# Extract text from URL
summarize "<URL>" --extract-only --model google/gemini-3-flash-preview

# Extract YouTube transcript
summarize "<YouTube-URL>" --youtube auto --extract-only

# Pre-summary for screening
summarize "<URL>" --length medium --model google/gemini-3-flash-preview
```

**Useful flags**: `--extract-only` (raw text), `--youtube auto`, `--firecrawl auto` (JS-heavy sites), `--json`

**If `summarize` is not available**: Use the agent's built-in web fetching tools as fallback.

### Step 2: Plan Decomposition Tree

> **⚠️ MANDATORY: You MUST complete this step BEFORE writing ANY content.**
> **⚠️ MANDATORY: You MUST create ALL directories with `mkdir -p` BEFORE writing ANY files.**
> **⚠️ ZERO TOLERANCE: No atomic notes are allowed in the topic root directory. ONLY the main hub note lives there.**

**Plan the COMPLETE file tree with numbered directories, then create them immediately.**

#### 2a. Plan the tree (output to user for confirmation)

```
Topic: 2028 Global Intelligence Crisis

主笔记: 2028-Global-Intelligence-Crisis-Notes.md  (in topic root)

01-Intelligence-Displacement-Spiral/
  L1: Intelligence-Displacement-Spiral.md
  L2: OpEx-Substitution-Mechanism.md
  L2: Ghost-GDP-Phenomenon.md
  L3: OpEx-vs-CapEx-AI-Spending.md               ← parent: OpEx-Substitution
  L3: Why-No-Natural-Brake.md                     ← parent: OpEx-Substitution

02-SaaS-Collapse-and-Intermediation-Death/
  L1: SaaS-Collapse-and-Intermediation-Death.md
  L2: Agentic-Coding-Disruption.md
  L2: Habitual-Intermediation-Collapse.md
  L3: Friction-Zero-Disruption.md                 ← parent: Habitual-Intermediation

03-White-Collar-Displacement-Asymmetry/
  L1: White-Collar-Displacement-Asymmetry.md
  L2: Downshifting-Effect.md
  L2: Labor-Share-Decline.md

04-Financial-Contagion-Chain/
  L1: Financial-Contagion-Chain.md
  L2: Private-Credit-SaaS-Crisis.md
  L2: Permanent-Capital-Trap.md
  L2: Mortgage-Market-Structural-Threat.md
  L3: Zendesk-Case-Study.md                       ← parent: Private-Credit
  L3: Insurance-Asset-Impairment.md               ← parent: Permanent-Capital

glossary/ (42 entries):
  glossary/Ghost GDP（幽灵GDP）.md
  glossary/Intelligence Displacement Spiral（智能替代螺旋）.md
  glossary/Private Credit（私募信贷）.md
  ... (one file per term)
```

#### 2b. Create ALL directories FIRST (before writing any files)

```bash
# MANDATORY: Run this BEFORE writing any notes
TOPIC_DIR="<vault>/00-Inbox/{Topic}"
mkdir -p "$TOPIC_DIR"
mkdir -p "$TOPIC_DIR/01-{L1-Concept-A}"
mkdir -p "$TOPIC_DIR/02-{L1-Concept-B}"
mkdir -p "$TOPIC_DIR/03-{L1-Concept-C}"
# ... one mkdir per L1 concept
mkdir -p "$TOPIC_DIR/glossary"
mkdir -p "$TOPIC_DIR/assets"
```

#### 2c. Verify directory structure before proceeding

```bash
# Verify: must show numbered subdirectories + glossary + assets
find "$TOPIC_DIR" -type d | sort
```

**Only proceed to Step 3 after directories exist.**

### Step 3: Search Existing Resources

```bash
# Search glossary for existing bilingual terms
python3 <SKILL_DIR>/scripts/search.py "<topic keywords>" --domain glossary

# Search Mermaid templates for diagram ideas
python3 <SKILL_DIR>/scripts/search.py "<concept type>" --domain mermaid

# Search writing rules for style guidance
python3 <SKILL_DIR>/scripts/search.py "<content type>" --domain writing
```

### Step 4: Generate Notes (in order)

> **⚠️ CRITICAL: Every file MUST be written to its correct subdirectory. Double-check the output path before every Write/Edit call.**

| Order | Note Type | Write To | Example Path |
|-------|-----------|----------|-------------|
| 1 | Main note (hub) | `{Topic}/` root — **ONLY file here** | `Lazygit/Lazygit-Notes.md` |
| 2 | L1 atomic notes | `{Topic}/NN-{L1-Concept}/` | `Lazygit/01-Installation-and-Setup/Installation-and-Setup.md` |
| 3 | L2 atomic notes | Same dir as parent L1 | `Lazygit/03-Basic-Git-Operations/Staging-and-Committing.md` |
| 4 | L3 atomic notes | Same dir as parent L1 | `Lazygit/03-Basic-Git-Operations/Staging-Modes.md` |
| 5 | Glossary entries | `{Topic}/glossary/` | `Lazygit/glossary/Stage（暂存）.md` |
| 6 | Visualizations | `{Topic}/assets/` | `Lazygit/assets/workflow-chart.png` |

**Self-check before each file write:**
- Is this the main hub note? → Write to `{Topic}/` root
- Is this an atomic note (L1/L2/L3)? → Write to `{Topic}/NN-{L1-Parent}/`
- Is this a glossary entry? → Write to `{Topic}/glossary/`
- **NEVER write atomic notes directly to `{Topic}/` root**

#### Script Usage

```bash
# Main note (in topic root)
python3 <SKILL_DIR>/scripts/generate.py \
  --type lecture --title "<title>" \
  --concepts "C1,C2,C3,C4" \
  --output "<vault>/00-Inbox/{Topic}/"

# Atomic note (any layer — output to its L1 parent subdirectory)
python3 <SKILL_DIR>/scripts/generate.py \
  --type atomic --concept "<name>" \
  --parent "<parent-note-stem>" \
  --children "Child1,Child2" \
  --siblings "Sibling1,Sibling2" \
  --output "<vault>/00-Inbox/{Topic}/NN-{L1-Concept}/"

# Glossary entry
python3 <SKILL_DIR>/scripts/generate.py \
  --type glossary --term-en "<English Term>" --term-cn "<中文术语>" \
  --definition "<one-line definition>" \
  --output "<vault>/00-Inbox/{Topic}/glossary/"

# Course MOC
python3 <SKILL_DIR>/scripts/generate.py \
  --type moc --course "<course>" --semester "<semester>"
```

> **Note**: `<SKILL_DIR>` = the directory where this skill is installed. `NN` = two-digit L1 index (01, 02, ...).

### Step 5: Generate Visualizations (as needed)

For data-driven charts that Mermaid cannot handle:

```bash
python3 <SKILL_DIR>/scripts/visualize.py \
  --type "<chart_type>" \
  --data "<data_json>" \
  --output "<output_path>" \
  --title "<chart title>"
```

Available chart types: `bar`, `line`, `scatter`, `timeline`, `heatmap`, `comparison`, `pie`, `radar`

---

## Output Format Templates

All templates are in the `templates/` directory:

| Type | Template File | Description |
|------|--------------|-------------|
| Main Note (主笔记) | `templates/lecture-note.md` | Hub note with overview, N sections, summary, review questions |
| Atomic Note (原子笔记) | `templates/atomic-note.md` | Rich concept note — used for ALL layers (L1, L2, L3) |
| Glossary Entry (原子概念) | `templates/glossary-entry.md` | Short bilingual term definition |
| Course MOC | `templates/course-moc.md` | Map of Content with lecture index, concept clusters |

### Main Note (主笔记) Key Requirements

- YAML frontmatter: title, date, course/topic, tags, source_files, status, aliases
- Core Idea（核心思想）blockquote with inline `[[glossary-wikilinks]]`
- Source links
- Overview section (with image embed if available)
- **N numbered sections** (one per L1 concept, NOT limited to 3), each with:
  - `→ 详见 [[L1-Atomic-Note]]` link
  - Sub-sections: Why → What → How
  - Mermaid diagrams, comparison tables, key insight blockquotes
- Summary section: concept map (Mermaid) + data summary table + key quote
- Review Questions: recall + understanding + application + critical thinking
- Related Notes linking to all L1 atomic notes

### Atomic Note (原子笔记) Key Requirements

**Same rich structure for ALL layers (L1, L2, L3):**

- YAML frontmatter: title (bilingual), date, tags, aliases
- One-paragraph **定义** with inline wikilinks
- **Why Do We Need This?** — motivation + concrete example
- **Core Concept** — idea + example/code + Mermaid diagram + step-by-step
- **Comparison** — table comparing alternatives or with/without
- **Common Pitfalls** — mistakes and how to avoid
- **Key Takeaway** — one flashcard-worthy sentence
- **Review Questions** — recall, understanding, application
- **Related Notes** — parent (UP) + children (DOWN) + siblings (ACROSS)

### Glossary Entry (原子概念) Key Requirements

- YAML frontmatter: title (bilingual), date, tags: [glossary, {topic-tag}], aliases
- One blockquote **定义** (1-3 sentences, bilingual)
- Related Notes linking to relevant atomic notes + main note

### Cross-Reference Rules (CRITICAL)

**All notes link in THREE directions:**

| Note Type | Links UP to | Links DOWN to | Links ACROSS to |
|-----------|-------------|---------------|-----------------|
| Main Note | — | All L1 notes | — |
| L1 Atomic | Main Note | Its L2 children | Sibling L1 notes |
| L2 Atomic | Parent L1 | Its L3 children | Sibling L2 notes |
| L3 Atomic | Parent L2 | — | Sibling L3 notes |
| Glossary | Related atomic notes | — | Related glossary terms |

**Inline wikilinks**: All glossary terms MUST be linked inline on first mention in every note using `[[Term（术语）]]` syntax.

---

## Wiki-Link Naming Convention (CRITICAL)

**Wiki-link targets MUST match filenames (without `.md`).** Spaces → hyphens in atomic notes, but glossary keeps parenthetical Chinese.

| Note Type | File Name Pattern | Wiki-Link |
|-----------|------------------|-----------|
| Main Note | `{Topic}-Notes.md` | `[[{Topic}-Notes]]` |
| Atomic Note | `{Concept-Name}.md` | `[[{Concept-Name}]]` |
| Glossary Entry | `{English Term（中文术语）}.md` | `[[{English Term（中文术语）}]]` |

**Rules:**
1. **Before generating any notes**, list ALL file names AND their target directories
2. **NEVER leave wiki-links empty** (`[[]]`) or with placeholder text (`[[TODO]]`)
3. If a target note doesn't exist yet, use the correct future filename — Obsidian creates it on click
4. Glossary filenames include both English and Chinese: `English Term（中文术语）.md`
5. Wiki-links use **filename only** (no path) — Obsidian resolves across subdirectories automatically

---

## Mermaid Diagram Guidelines

| Diagram Type | Use For | Example |
|-------------|---------|---------|
| `graph TB/LR` | Hierarchies, flows, architectures | Concept trees, process chains |
| `sequenceDiagram` | Time-ordered interactions | Data transfers, API calls |
| `stateDiagram-v2` | State transitions | Lifecycle, mode changes |
| `classDiagram` | Object relationships | Class hierarchy |
| `gantt` | Timelines, parallel tasks | Project phases, pipeline |
| `pie` | Proportions | Distribution breakdown |
| `xychart-beta` | Data trends | Performance scaling |
| `mindmap` | Topic overview | Concept clustering |

**Rules**:
1. NEVER use ASCII art — always Mermaid
2. Every diagram must have a title and labeled edges
3. Max 15-20 nodes per diagram
4. Use `classDef` for consistent colors
5. Use subgraphs for grouping

**Color theme**:
```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4CAF50', 'primaryTextColor': '#fff', 'primaryBorderColor': '#388E3C', 'lineColor': '#666', 'secondaryColor': '#FF9800', 'tertiaryColor': '#2196F3'}}}%%
```

---

## Matplotlib Visualization

Use when Mermaid cannot express the data: performance bars, scaling curves, heatmaps, radar charts.

**Rules**: PNG at `dpi=150`, consistent colors (`#4CAF50`, `#FF9800`, `#2196F3`, `#F44336`), always include axis labels and title, reference as `![[filename.png]]`.

---

## Search Reference

| Domain | Use For | Example Keywords |
|--------|---------|-----------------|
| `glossary` | Find existing bilingual terms | cuda, memory, 内存, 术语 |
| `mermaid` | Find diagram templates | flow, sequence, hierarchy, 图表 |
| `writing` | Get writing style rules | introduction, comparison, 规则 |
| `questions` | Get review question templates | recall, application, 考试 |

---

## Quality Checklist

### Content
- [ ] WHY → WHAT → HOW structure for every concept (all layers)
- [ ] Example appears BEFORE theory in every concept note
- [ ] All terms bilingual: `English（中文）`
- [ ] Each atomic note covers exactly ONE concept

### Decomposition
- [ ] Decomposition tree planned BEFORE writing
- [ ] ALL file names AND target directories listed before generation
- [ ] ≥3 layers of atomic notes produced (L1 → L2 → L3 minimum)
- [ ] L1 covers major themes, L2 breaks down sub-concepts, L3 provides finest analysis
- [ ] Glossary entries for ALL technical terms mentioned

### Visualization
- [ ] NO ASCII art — use Mermaid
- [ ] Every concept has at least one diagram or table
- [ ] Similar concepts have comparison tables
- [ ] Diagrams have titles and labeled edges

### Structure
- [ ] YAML frontmatter complete (title, date, tags, aliases)
- [ ] `[[wiki-links]]` for all cross-references (inline + Related Notes)
- [ ] 3 review questions per atomic note: recall, understanding, application
- [ ] Related Notes with UP / DOWN / ACROSS links
- [ ] File naming: `Concept-Name.md` (hyphens for atomic notes)

### Directory Organization
- [ ] Main note in topic root (`00-Inbox/{Topic}/`)
- [ ] Atomic notes organized into numbered L1 subdirectories (`01-xxx/`, `02-xxx/`)
- [ ] L2 and L3 notes placed inside their parent L1 subdirectory (flat, no further nesting)
- [ ] Glossary entries in `glossary/` subdirectory
- [ ] No atomic notes left loose in topic root

### Obsidian Compatibility
- [ ] `[[wiki-links]]` syntax (not markdown links)
- [ ] Standard ` ```mermaid ` fencing
- [ ] Images: `![[image.png]]`
- [ ] Tags: lowercase with hyphens

---

## Tips

1. **Provide source material**: URL, video link, PDF, transcript → better notes
2. **Video links**: Paste YouTube/Bilibili URLs directly; transcript auto-extracted
3. **Be specific about topic**: "这个视频的AI经济分析" > "总结一下"
4. **Search glossary first**: Reuse existing terms for cross-course consistency
5. **Iterate**: Generate base notes, then ask for deeper decomposition on specific branches
6. **Cross-reference**: Link related concepts across different note sets
