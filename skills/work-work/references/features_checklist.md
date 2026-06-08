# Workwork Features Checklist

## Core Features (8 Modules)

### Module 1: Reference Format Checker ✅
**Script:** `reference_formatter.py`

**Capabilities:**
- ✅ Check citation marker positioning
- ✅ Detect author list formatting (add "等" when exceeding limit)
- ✅ Validate reference numbering continuity
- ✅ Check duplicate reference numbers
- ✅ Verify figure/table citation markers
- ✅ Generate detailed format check reports
- ✅ Support user-defined format configuration

**Configuration:** `templates/ref_format_default.yml`

**Usage:**
```bash
python scripts/reference_formatter.py your_review.md
python scripts/reference_formatter.py your_review.md custom_config.yml
```

**Output:** `your_review_format_report.md`

---

### Module 2: Reference Manager & Filter ✅
**Script:** `filter_references.py`

**Capabilities:**
- ✅ Identify Chinese core journals
- ✅ Automatically remove non-core journal references
- ✅ Support custom journal blacklists/whitelists
- ✅ Check reference format completeness

**Usage:**
```bash
# Edit filter_references.py journal list first
python scripts/filter_references.py
```

**Note:** Requires editing journal lists before use

---

### Module 3: Reference Numbering System ✅
**Scripts:**
- `extract_and_fix_references.py` (main)
- `fix_references_precise.py` (precise fix)

**Capabilities:**
- ✅ Automatically renumber references
- ✅ Update citation numbers in text
- ✅ Detect and delete invalid citations
- ✅ Validate citation-reference correspondence

**Usage:**
```bash
python scripts/extract_and_fix_references.py
```

**Warning:** Directly modifies source file—backup first!

---

### Module 4: Format Normalization ✅
**Script:** `create_word_doc_v3.js`

**Capabilities:**
- ✅ Generate Word documents compliant with Chinese academic standards
- ✅ Set fonts (宋体/Times New Roman)
- ✅ Set font sizes (小四 for body, 三号 for headings)
- ✅ Set line spacing (1.5x)
- ✅ Set margins (2.54cm)
- ✅ Add headers/footers (optional)

**Dependencies:** Node.js 14+, `docx` npm package

**Usage:**
```bash
node scripts/create_word_doc_v3.js
```

**Output:** `your_review.docx`

---

### Module 5: Quality Control & Validation ✅
**Scripts:**
- `verify_review_comprehensive.py` (comprehensive validation)
- `simple_verify.py` (quick validation)

**Capabilities:**
- ✅ Check chapter structure completeness
- ✅ Validate citation numbering continuity
- ✅ Detect duplicate numbering
- ✅ Generate validation reports

**Usage:**
```bash
# Comprehensive validation
python scripts/verify_review_comprehensive.py

# Quick validation
python scripts/simple_verify.py
```

---

### Module 6: Typo & Grammar Checker ✅
**Script:** `typo_grammar_checker.py`

**Capabilities:**
- ✅ Check common typos
- ✅ Check grammar errors (mismatched quotes, brackets, etc.)
- ✅ Check punctuation usage
- ✅ Check number formatting
- ✅ Generate detailed check reports

**Usage:**
```bash
python scripts/typo_grammar_checker.py your_review.md
```

**Output:** `your_review_typo_grammar_report.md`

---

### Module 7: Reference Format & Citation Accuracy Checker ✅
**Script:** `reference_accuracy_checker.py`

**Capabilities:**
- ✅ Validate reference list format compliance
- ✅ Check citation accuracy (invalid citations, orphaned references)
- ✅ Validate reference numbering continuity
- ✅ Check citation numbering in text
- ✅ Check citation marker positioning
- ✅ Generate detailed check reports

**Usage:**
```bash
python scripts/reference_accuracy_checker.py your_review.md
```

**Output:** `your_review_reference_accuracy_report.md`

---

### Module 8: Document Format Checker ✅
**Script:** `document_format_checker.py`

**Capabilities:**
- ✅ Check main title
- ✅ Check abstract and keywords
- ✅ Check chapter structure and numbering
- ✅ Check references section
- ✅ Check paragraph formatting
- ✅ Check heading hierarchy
- ✅ Check list formatting
- ✅ Generate detailed check reports

**Usage:**
```bash
python scripts/document_format_checker.py your_review.md
```

**Output:** `your_review_document_format_report.md`

---

### Module 9: Unified Checker ✅ (v2.1.0 NEW)

**Script:** `unified_checker.py`

**Capabilities:**
- ✅ Integrate all check functions into single script
- ✅ Complete all checks in one operation
- ✅ Generate unified report
- ✅ Avoid redundant checks
- ✅ Improve efficiency

**Usage:**
```bash
python scripts/unified_checker.py your_review.md
```

**Output:** `your_review_unified_report.md`

---

## Configuration Templates

### Reference Format Configuration

**File:** `templates/ref_format_default.yml`

**Configuration Options:**

#### Citation Marker Style
```yaml
citation:
  style: "superscript"  # superscript or inline
  position_rules:
    before_punctuation: true
    after_quote_in_sentence: true
    before_period: true
```

#### Same Source Multi-Page Citation
```yaml
same_source_format: "[{ref}:{pages}]"  # Example: [1:12-15]
```

#### Figure/Table References
```yaml
figure_table:
  move_to_caption: true
  inline_notes_format: "superscript_number"  # ①② / dagger
```

#### Reference List
```yaml
reference_list:
  sort_order: "order_of_appearance"
  authors:
    max_authors: 3
    beyond_limit_suffix: "等"
```

#### Quality Check
```yaml
quality_check:
  check_continuity: true
  check_duplicates: true
  check_invalid_refs: true
  check_position: true
```

#### Processing Mode
```yaml
processing:
  mode: "semi_auto"  # semi_auto or auto
  generate_report: true
  backup_original: true
```

---

## File Structure

```
workwork/
├── SKILL.md                              # Main skill definition
├── scripts/                              # Executable scripts
│   ├── unified_checker.py                  # Unified checker ✨ NEW
│   ├── reference_formatter.py              # Reference format check ✅
│   ├── typo_grammar_checker.py           # Typo & grammar check ✅
│   ├── reference_accuracy_checker.py       # Reference accuracy check ✅
│   ├── document_format_checker.py          # Document format check ✅
│   ├── filter_references.py              # Reference filter ✅
│   ├── extract_and_fix_references.py     # Reference numbering fix ✅
│   ├── fix_references_precise.py         # Precise fix ✅
│   ├── create_word_doc_v3.js           # Word generation ✅
│   └── ... (other utility scripts)
├── templates/                            # Configuration templates
│   └── ref_format_default.yml           # Default format config ✅
└── references/                           # Reference documentation
    ├── workflow_guide.md                  # Workflow guide ✅
    └── features_checklist.md            # This file ✅
```

---

## Usage Scenarios

### Scenario 1: First Draft - Comprehensive Check
1. Run unified checker: `python scripts/unified_checker.py your_review.md`
2. Review report
3. Fix all issues
4. Filter references (optional)
5. Fix numbering
6. Final verification
7. Generate Word document

### Scenario 2: Reference Numbering Fix
1. Backup file
2. Filter references: `python scripts/filter_references.py`
3. Fix numbering: `python scripts/extract_and_fix_references.py`
4. Verify: `python scripts/simple_verify.py`
5. Generate Word: `node scripts/create_word_doc_v3.js`

### Scenario 3: Minor Edits - Quick Fix
1. Run targeted checker based on what changed
2. Review report
3. Generate Word document

---

## Output Format

### Unified Report Structure

```markdown
# Unified Check Report for [filename]

## Document Statistics
- Character count: [total]
- Reference count: [total]
- Citation count: [total]

## Problem Statistics
- Total issues: [total]
- Critical issues: [count] (must fix)
- Warning issues: [count] (should fix)
- Info issues: [count] (optional)

## Check Results

### 1. Reference Format Check
Status: ✅ / 🟡 / 🔴
Issues found: [count]
[Detailed issues...]

### 2. Citation Accuracy Check
Status: ✅ / 🟡 / 🔴
Issues found: [count]
[Detailed issues...]

### 3. Typo & Grammar Check
Status: ✅ / 🟡 / 🔴
Issues found: [count]
[Detailed issues...]

### 4. Document Format Check
Status: ✅ / 🟡 / 🔴
Issues found: [count]
[Detailed issues...]

## Recommendations
[Fix suggestions...]
```

---

## Best Practices

1. **Always Backup**: Backup important files before running scripts that modify them
2. **Stepwise Checking**: Follow check → review → fix workflow
3. **Customize Configuration**: Adjust config files for specific journal/school requirements
4. **Verify Results**: Run validation after each modification
5. **Version Control**: Use Git or similar for document version management

---

## Common Issues & Solutions

### Issue: Encoding Problems (GBK vs UTF-8)
**Solution:** Ensure scripts use `encoding='utf-8'` in file operations

### Issue: Node.js docx Package Not Found
**Solution:** Run `npm install docx`

### Issue: Missing Configuration File
**Solution:** Copy `templates/ref_format_default.yml` to working directory

---

## Dependencies

### Python
- Python 3.7+
- PyYAML (for config parsing)
- python-docx (optional, for Word processing)

### Node.js
- Node.js 12+
- docx (npm package)

### Optional Tools
- pandoc (for document conversion)

---

## Actual Use Case: Yunnan Snub-Nosed Monkey Review

| Item | Result |
|-------|--------|
| Original references | 98 |
| After filtering | 94 |
| Citation markers | 160 (all correct) |
| Numbering status | Continuous (1-94), no duplicates |
| Document length | 32,486 characters |
| Word document | 33KB, academic standard compliant |
| Quality score | ⭐⭐⭐⭐⭐ (5/5) |
| Check time | ~10 minutes (unified check) |

---

## Feature Version History

### v2.1.0 (2026-03-19) - Current Version
**New Features:**
- ✨ Added **unified checker function** (`unified_checker.py`)
- ✨ Optimized workflows with three workflow options
- ✨ Added usage guidelines and warnings
- ✨ Improved efficiency, eliminated redundant checks

**Improvements:**
- 🔧 Optimized document structure
- 🔧 Added loop check analysis report
- 🔧 Improved usage guide

**Bug Fixes:**
- 🐛 Fixed encoding issues (GBK vs UTF-8)
- 🐛 Fixed special character display issues

### v2.0.0 (2026-03-19)
**New Features:**
- ✨ Added typo and grammar checking
- ✨ Added reference format and citation accuracy checking
- ✨ Added document format compliance checking
- ✨ Enhanced all check report detail levels
- ✨ Optimized typo dictionary, reduced false positives
- ✨ Added comprehensive quality check summary report

### v1.0.0 (2026-03-19)
**Initial Version:**
- ✅ Implemented reference format checking
- ✅ Implemented reference filtering
- ✅ Implemented reference numbering repair
- ✅ Implemented Word document generation
- ✅ Implemented quality control checking
- ✅ Supported user-defined format configuration

---

## Skill Target Audience

- Academic researchers
- Graduate students, PhD candidates
- Paper writers
- Scientific researchers

## Skill Use Cases

- Writing academic review papers
- Standardizing reference formats
- Filtering and optimizing reference quality
- Checking paper formatting compliance
- Generating Word documents compliant with academic standards

---

**Document Version**: v2.1.0
**Last Updated**: 2026-03-19
**Skill Version**: v2.1.0
**Status**: ✅ Complete and ready to use
**Total Files**: 30+
**Total Code Lines**: 5000+

**Author**: WorkBuddy AI
**License**: MIT
