# Anthropic Official Skill Best Practices

> Source: https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices
> Last Updated: 2025-01

This document contains official best practices from Anthropic for creating effective Claude Agent Skills.

---

## Table of Contents

- [Core Principles](#core-principles)
  - [Conciseness is Key](#conciseness-is-key)
  - [Set Appropriate Freedom Levels](#set-appropriate-freedom-levels)
  - [Test with All Target Models](#test-with-all-target-models)
- [Skill Structure](#skill-structure)
  - [YAML Frontmatter Requirements](#yaml-frontmatter-requirements)
  - [Naming Conventions](#naming-conventions)
  - [Writing Effective Descriptions](#writing-effective-descriptions)
  - [Progressive Disclosure Patterns](#progressive-disclosure-patterns)
- [Workflows and Feedback Loops](#workflows-and-feedback-loops)
- [Content Guidelines](#content-guidelines)
- [Common Patterns](#common-patterns)
- [Evaluation and Iteration](#evaluation-and-iteration)
- [Anti-patterns to Avoid](#anti-patterns-to-avoid)
- [Advanced: Skills with Executable Code](#advanced-skills-with-executable-code)
- [Checklist for Effective Skills](#checklist-for-effective-skills)

---

## Core Principles

### Conciseness is Key

The context window is a shared resource. Your skill shares it with:
- System prompts
- Conversation history
- Other skill metadata
- Actual requests

**Default Assumption**: Claude is already highly intelligent.

Only add context Claude doesn't have. Question every piece of information:
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Is this paragraph worth its token cost?"

**Good Example: Concise** (~50 tokens):
```markdown
## Extract PDF Text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

**Bad Example: Too Verbose** (~150 tokens):
```markdown
## Extract PDF Text

PDF (Portable Document Format) files are a common file format containing
text, images, and other content. To extract text from PDFs, you need
a library. There are many libraries for PDF processing, but we
recommend pdfplumber because it's easy to use and handles most cases.
First, you need to install it using pip. Then you can use the code below...
```

### Set Appropriate Freedom Levels

Match specificity to task fragility and variability.

| Freedom Level | When to Use | Example |
|--------------|-------------|---------|
| **High** (text instructions) | Multiple approaches work; decisions depend on context | Code review process |
| **Medium** (pseudocode/parameterized scripts) | Preferred patterns exist; some variation acceptable | Report generation template |
| **Low** (specific scripts, few/no params) | Operations are fragile; consistency is critical | Database migration |

**Analogy**: Think of Claude as a robot exploring paths:
- **Narrow bridge with cliffs on both sides**: Only one safe way forward. Provide specific guardrails (low freedom).
- **Open field with no dangers**: Many paths lead to success. Give general direction and trust Claude (high freedom).

### Test with All Target Models

Skills function as add-ons to models, so effectiveness depends on the underlying model.

| Model | Testing Focus |
|-------|---------------|
| **Claude Haiku** (fast, economical) | Does skill provide enough guidance? |
| **Claude Sonnet** (balanced) | Is skill clear and efficient? |
| **Claude Opus** (powerful reasoning) | Does skill avoid over-explaining? |

What works perfectly for Opus may need more detail for Haiku.

---

## Skill Structure

### YAML Frontmatter Requirements

| Field | Requirements |
|-------|-------------|
| `name` | Max 64 chars; lowercase letters, numbers, hyphens only; no XML tags; no reserved words ("anthropic", "claude") |
| `description` | Non-empty; max 1024 chars; no XML tags; describes what skill does AND when to use it |

### Naming Conventions

Use **gerund form** (verb + -ing) for skill names as it clearly describes the activity or capability.

**Good Examples (Gerund Form)**:
- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`
- `testing-code`
- `writing-documentation`

**Acceptable Alternatives**:
- Noun phrases: `pdf-processing`, `spreadsheet-analysis`
- Action-oriented: `process-pdfs`, `analyze-spreadsheets`

**Avoid**:
- Vague names: `helper`, `utils`, `tools`
- Too generic: `documents`, `data`, `files`
- Reserved words: `anthropic-helper`, `claude-tools`

### Writing Effective Descriptions

> **CRITICAL: Always write in third person.**
>
> Descriptions are injected into system prompts. Inconsistent perspectives cause discovery issues.
>
> - **Good**: "Processes Excel files and generates reports"
> - **Avoid**: "I can help you process Excel files"
> - **Avoid**: "You can use this to process Excel files"

**Be Specific and Include Key Terms**:

```yaml
# Good - PDF Processing
description: Extracts text and tables from PDF files, fills forms, merges documents. Use when processing PDF files or when user mentions PDF, forms, or document extraction.

# Good - Excel Analysis
description: Analyzes Excel spreadsheets, creates pivot tables, generates charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.

# Good - Git Commit Helper
description: Generates descriptive commit messages by analyzing git diffs. Use when user asks for help writing commit messages or reviewing staged changes.
```

**Avoid Vague Descriptions**:
```yaml
# Bad
description: Helps with documents
description: Processes data
description: Does various operations on files
```

### Progressive Disclosure Patterns

SKILL.md serves as an overview, pointing to detailed materials Claude reads on-demand.

**Practical Guidelines**:
- Keep SKILL.md body under 500 lines for optimal performance
- Split content into separate files when approaching this limit
- Use patterns below to organize instructions, code, and resources effectively

#### Directory Structure Example

```
skill-name/
├── SKILL.md              # Main instructions (loaded on trigger)
├── FORMS.md              # Form filling guide (loaded on demand)
├── reference.md          # API reference (loaded on demand)
├── examples.md           # Usage examples (loaded on demand)
└── scripts/
    ├── analyze.py        # Utility script (executed, not loaded)
    ├── validate.py       # Validation script
    └── process.py        # Processing script
```

#### Pattern 1: High-Level Guide with References

```markdown
# PDF Processing

## Quick Start
[Basic usage code]

## Advanced Features
**Form Filling**: See [FORMS.md](FORMS.md) for complete guide
**API Reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

#### Pattern 2: Domain-Specific Organization

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

#### Pattern 3: Conditional Details

```markdown
## Document Modification

**Creating new content?** → Follow "Create Workflow"
**Editing existing content?** → Follow "Edit Workflow"

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

### Avoid Deep Nested References

> **Keep references one level from SKILL.md.**

All reference files should link directly from SKILL.md to ensure Claude reads complete files when needed.

**Bad: Too Deep**:
```
SKILL.md → advanced.md → details.md → actual info
```

**Good: One Level Deep**:
```
SKILL.md → advanced.md
         → reference.md
         → examples.md
```

### Structure Longer Reference Files

For reference files over 100 lines, include a table of contents at the top.

```markdown
# API Reference

## Contents
- Authentication and Setup
- Core Methods (Create, Read, Update, Delete)
- Advanced Features (Batch Operations, Webhooks)
- Error Handling Patterns
- Code Examples

## Authentication and Setup
...
```

---

## Workflows and Feedback Loops

### Use Workflows for Complex Tasks

Break complex operations into clear sequential steps. For particularly complex workflows, provide a checklist.

**Example: Research Synthesis Workflow**:
```markdown
## Research Synthesis Workflow

Copy this checklist and track progress:

```
Progress:
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
- [ ] Step 3: Cross-reference claims
- [ ] Step 4: Create structured summary
- [ ] Step 5: Validate citations
```

**Step 1: Read all source documents**
[Detailed instructions...]
```

### Implement Feedback Loops

**Common Pattern**: Run validator → Fix errors → Repeat

This pattern greatly improves output quality.

```markdown
## Document Editing Process

1. Make edits to document
2. **Validate immediately**: `python scripts/validate.py`
3. If validation fails:
   - Review error messages carefully
   - Fix issues
   - Run validation again
4. **Only proceed when validation passes**
5. Build output
6. Test output
```

---

## Content Guidelines

### Avoid Time-Sensitive Information

**Bad (will become wrong)**:
```markdown
If executing before August 2025, use old API.
After August 2025, use new API.
```

**Good (use "Legacy Patterns" section)**:
```markdown
## Current Method
Use v2 API endpoint: `api.example.com/v2/messages`

## Legacy Patterns
<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>
v1 API used: `api.example.com/v1/messages`
This endpoint is no longer supported.
</details>
```

### Use Consistent Terminology

Choose one term and use it throughout the skill:

| Good (Consistent) | Bad (Inconsistent) |
|-------------------|-------------------|
| Always "API endpoint" | Mix of "API endpoint", "URL", "API route", "path" |
| Always "field" | Mix of "field", "box", "element", "control" |
| Always "extract" | Mix of "extract", "pull", "get", "retrieve" |

---

## Common Patterns

### Template Pattern

Provide templates for output formats. Match strictness to requirements.

**For Strict Requirements**:
```markdown
## Report Structure

Always use this exact template structure:

```markdown
# [Analysis Title]

## Executive Summary
[One paragraph overview of key findings]

## Key Findings
- Finding 1 with supporting data
- Finding 2 with supporting data
```
```

**For Flexible Guidance**:
```markdown
## Report Structure

This is a reasonable default format, but use your best judgment:

[Template with note: Adjust sections as needed based on analysis type]
```

### Example Pattern

For skills where output quality depends on seeing examples:

```markdown
## Commit Message Format

**Example 1:**
Input: Add user authentication using JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fix bug where dates display incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion
```

Follow this style: type(scope): short description, then details.
```

### Conditional Workflow Pattern

```markdown
## Document Modification Workflow

1. Determine modification type:

   **Creating new content?** → Follow "Create Workflow" below
   **Editing existing content?** → Follow "Edit Workflow" below
```

---

## Evaluation and Iteration

### Build Evaluation First

**Create evaluations BEFORE writing extensive documentation.**

**Evaluation-Driven Development**:
1. **Identify gaps**: Run Claude on representative tasks without skill. Document specific failures
2. **Create evaluations**: Build 3 scenarios to test those gaps
3. **Establish baseline**: Measure Claude's performance without skill
4. **Write minimal instructions**: Create enough content to address gaps and pass evaluations
5. **Iterate**: Execute evaluation, compare to baseline, improve

### Iterate with Claude

Work with one Claude instance ("Claude A") to create skills that will be used by other instances ("Claude B").

**Creating New Skills**:
1. Complete task without skill with Claude A
2. Identify reusable patterns from context you provided
3. Ask Claude A to create skill: "Create a skill to capture the patterns we just used"
4. Review for conciseness
5. Test with Claude B on similar tasks
6. Iterate based on observations

**Iterating Existing Skills**:
1. Use skill in real workflows with Claude B
2. Observe where Claude B struggles or succeeds
3. Return to Claude A for improvements
4. Apply and test changes
5. Repeat as needed

---

## Anti-patterns to Avoid

### Avoid Windows-Style Paths

Always use forward slashes, even on Windows:
- **Good**: `scripts/helper.py`, `reference/guide.md`
- **Bad**: `scripts\helper.py`, `reference\guide.md`

### Avoid Too Many Options

Don't present multiple approaches unless necessary:

**Bad (confusing)**:
```markdown
You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or...
```

**Good (provide default with escape hatch)**:
```markdown
Use pdfplumber for text extraction:
```python
import pdfplumber
```

For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
```

### Avoid Assuming Tools Are Installed

**Bad**:
```markdown
Use the pdf library to process files.
```

**Good**:
```markdown
Install required packages: `pip install pypdf`

Then use it:
```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```
```

---

## Advanced: Skills with Executable Code

### Solve, Don't Punt

Handle error conditions instead of punting to Claude.

**Good: Handle Errors Explicitly**:
```python
def process_file(path):
    """Process file, create if doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default")
        with open(path, 'w') as f:
            f.write('')
        return ''
```

**Bad: Punt to Claude**:
```python
def process_file(path):
    # Just fail and let Claude figure it out
    return open(path).read()
```

### Document Configuration Values

Avoid "voodoo constants" (Ousterhout's Law).

**Good: Self-Documenting**:
```python
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections
REQUEST_TIMEOUT = 30

# Three retries balance reliability with speed
MAX_RETRIES = 3
```

**Bad: Magic Numbers**:
```python
TIMEOUT = 47  # Why 47?
RETRIES = 5   # Why 5?
```

### Provide Utility Scripts

Pre-made scripts are more reliable than generated code, save tokens and time, and ensure consistency.

**Example**:
```markdown
## Utility Scripts

**analyze_form.py**: Extract all form fields from PDF
```bash
python scripts/analyze_form.py input.pdf > fields.json
```

**validate.py**: Check for errors
```bash
python scripts/validate.py fields.json
```
```

### MCP Tool References

Always use fully qualified tool names: `ServerName:tool_name`

```markdown
Use the BigQuery:bigquery_schema tool to retrieve table schema.
Use the GitHub:create_issue tool to create issues.
```

---

## Checklist for Effective Skills

### Core Quality
- [ ] Description is specific and includes key terms
- [ ] Description includes what skill does AND when to use it
- [ ] **Description uses third person**
- [ ] SKILL.md body is under 500 lines
- [ ] Additional details in separate files (if needed)
- [ ] No time-sensitive information (or in "Legacy Patterns" section)
- [ ] Terminology consistent throughout skill
- [ ] Examples are specific, not abstract
- [ ] File references one level deep
- [ ] Progressive disclosure used appropriately
- [ ] Workflows have clear steps

### Code and Scripts
- [ ] Scripts solve problems rather than punt to Claude
- [ ] Error handling is explicit and helpful
- [ ] No "voodoo constants" (all values justified)
- [ ] Required packages listed and verified available
- [ ] Scripts have clear documentation
- [ ] No Windows-style paths (all forward slashes)
- [ ] Validation/verification steps for critical operations
- [ ] Feedback loops included for quality-critical tasks

### Testing
- [ ] At least 3 evaluations created
- [ ] Tested with Haiku, Sonnet, and Opus
- [ ] Tested with real-world use cases
- [ ] Team feedback incorporated (if applicable)

---

## Key Takeaways

| Principle | Guideline |
|-----------|-----------|
| **Conciseness** | Only add what Claude doesn't know. Question every token. |
| **Third Person** | Always write descriptions in third person. |
| **Progressive Disclosure** | SKILL.md is navigation, not encyclopedia. |
| **One Level Deep** | Keep file references one level from SKILL.md. |
| **500 Lines Max** | SKILL.md body should stay under 500 lines. |
| **Test All Models** | What works for Opus may need more detail for Haiku. |
| **Evaluation First** | Build evaluations before extensive documentation. |
| **Solve, Don't Punt** | Handle errors explicitly in scripts. |
