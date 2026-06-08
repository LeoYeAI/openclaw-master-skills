# Workwork Skill Changelog

## v3.0.0 (2026-03-19) - MAJOR UPDATE

### 🛡️ Literature Integrity Checker - CRITICAL NEW FEATURE

**全新文献完整性验证系统** - 杜绝文献引用错误的终极解决方案

#### Core Features

**Comprehensive Reference Validation**
- Parses and validates each reference's completeness
- Checks for: authors, title, journal, year, volume, pages, DOI
- Identifies missing or incomplete bibliographic information
- Validates year format and reasonableness (1900-current year)

**Citation Consistency Verification**
- Ensures all citations in text have corresponding references
- Detects invalid citations (numbers exceeding reference range)
- Identifies orphan citations (cited but not in reference list)
- Finds unused references (in list but never cited)

**Reference Number Management**
- Validates sequential numbering (1, 2, 3...)
- Detects missing numbers in sequence
- Identifies duplicate reference numbers
- Reports gaps in citation numbering

**Duplicate Detection**
- Identifies duplicate references by title and first author
- Prevents accidental inclusion of same source multiple times
- Suggests merging or removing duplicates

**Citation Format Compliance**
- Checks citation position (should be before punctuation)
- Identifies consecutive citation formatting issues
- Validates bracket usage and spacing

#### Critical Error Prevention

**Exit Code Behavior**
- Returns non-zero exit code on critical errors
- Prevents proceeding with document generation if issues found
- Forces user to fix problems before submission
- Integrates with CI/CD pipelines for automated checks

**Error Categories**
- 🔴 **Critical**: Invalid citations, missing references, numbering gaps
- 🟡 **Warning**: Incomplete information, formatting issues
- 🔵 **Info**: Unused references, style suggestions

#### Usage

```bash
# Basic check
python scripts/literature_integrity_checker.py your_review.md

# With deep verification (requires network)
python scripts/literature_integrity_checker.py your_review.md --deep-check
```

#### Output

Generates detailed markdown report with:
- Summary statistics
- Categorized issues list
- Reference-by-reference breakdown
- Fix recommendations
- Pre-submission checklist

### 📋 Updated Workflow

**New Recommended 9-Step Process:**
1. Write review
2. **Run Literature Integrity Check** ⭐ NEW CRITICAL STEP
3. Run unified check
4. Review reports
5. Fix issues
6. Filter references (optional)
7. Fix numbering
8. Final verification
9. Generate Word document

### 🔧 Improvements

- Enhanced error detection and reporting
- Stricter validation rules
- Better integration with existing tools
- Comprehensive documentation updates

---

## v2.3.0 (2026-03-19)

### ✨ New Features

#### Enhanced Superscript Word Generator (`create_word_with_superscript.js`)

**Smart Font Handling**
- Chinese characters use **SimSun (宋体)**
- English letters, numbers, and punctuation use **Times New Roman**
- Ensures proper academic formatting for mixed-language documents

**Auto-Italicization of Scientific Names**
- Automatically detects species Latin names (e.g., `Rhinopithecus bieti`, `Cetorhinus maximus`)
- Applies italic formatting to scientific names
- Pattern: Capitalized genus + lowercase species epithet

**Font Size Standardization**
- Body text: **小四 (12pt)**
- References: **小四 (12pt)**
- Level 1 headings: **小三 (16pt)** 黑体
- Level 2 headings: **四号 (14pt)** 黑体
- Citation superscripts: Slightly smaller for visual distinction

**Auto-Open Feature**
- Automatically opens the generated Word document after creation
- Cross-platform support (Windows, macOS, Linux)
- Provides clear console feedback

### 🔧 Improvements

- Better handling of mixed Chinese/English text
- Improved citation superscript formatting with brackets `[n]`
- Enhanced console output with formatting summary

### 📚 Documentation Updates

- Updated `SKILL.md` with detailed feature descriptions
- Added usage examples for superscript format
- Updated version history

---

## v2.2.0 (2026-03-19)

### ✨ New Features

- Added `create_word_with_superscript.js` for superscript citation format
- Superscript citations retain brackets: `[1]`, `[2-3]` appear as superscript

---

## v2.1.0 (2026-03-19)

### ✨ New Features

- Added unified checker (`unified_checker.py`) for comprehensive validation
- Optimized workflows to eliminate redundant checks
- Improved reporting format

---

## v2.0.0 (2026-03-19)

### ✨ New Features

- Added typo and grammar checker
- Added reference accuracy checker
- Added document format validation

---

## v1.0.0 (2026-03-19)

### 🎉 Initial Release

- Basic reference formatting
- Word document generation
- Reference filtering capabilities
