---
name: workwork
description: Academic review writer and formatting assistant for Chinese academic papers. Use this skill when users need to format, check, and refine academic literature reviews, reference lists, or generate compliant Word documents according to Chinese academic standards.
---

# Workwork - Academic Review Writing & Formatting Assistant

## Purpose

This skill provides comprehensive tools for academic review writing and formatting, specifically optimized for Chinese academic standards. It automates reference checking, format validation, document generation, and quality control processes to help researchers produce compliant, professional academic papers efficiently.

## When to Use This Skill

Use this skill when:
- Writing or formatting academic literature reviews
- Checking reference list formats and citations
- Validating document structure according to Chinese academic standards
- Generating Word documents with proper formatting
- Filtering references by journal quality (e.g., removing non-core journals)
- Fixing reference numbering and citation consistency
- Proofreading for typos and grammar errors

## Core Capabilities

This skill provides **ten** functional modules accessible through scripts in the `scripts/` directory:

### 1. Literature Integrity Checker ⭐ NEW (CRITICAL)
- **Script**: `literature_integrity_checker.py`
- **Purpose**: Comprehensive validation of reference integrity and citation consistency
- **What it checks**:
  - Reference completeness (authors, title, journal, year, pages)
  - Citation consistency (all citations have corresponding references)
  - Reference numbering continuity
  - Duplicate references
  - Citation format compliance
  - Invalid/orphan citations
  - **Consecutive duplicate citations** 🆕 NEW: Detects when the same reference is cited in 3+ consecutive sentences
- **Critical Feature**: Returns non-zero exit code on critical errors, preventing submission with errors
- **Auto-Open Feature** 🆕 NEW: Automatically opens the final Word document (`your_review_上标版.docx`) after successful check (no critical issues)
- **Usage**:
  ```bash
  # Standard check with auto-open enabled (default)
  python scripts/literature_integrity_checker.py your_review.md

  # With deep verification
  python scripts/literature_integrity_checker.py your_review.md --deep-check

  # Disable auto-open
  python scripts/literature_integrity_checker.py your_review.md --no-auto-open
  ```
- **Output**: `your_review_literature_integrity_report.md`
- **Note**: When check passes (no critical issues), the script automatically searches for and opens `your_review_上标版.docx` or `your_review.docx`

### 2. Unified Checker (RECOMMENDED - Most Efficient)
- **Script**: `unified_checker.py`
- **Purpose**: Run all checks at once in a single operation
- **What it does**: 
  - Reference format validation
  - Citation accuracy checking
  - Typo and grammar detection
  - Document format compliance checking
- **Usage**:
  ```bash
  python scripts/unified_checker.py your_review.md
  ```
- **Output**: `your_review_unified_report.md`

### 3. Reference Formatter
- **Script**: `reference_formatter.py`
- **Purpose**: Validate and format reference citations and bibliography
- **What it checks**:
  - Citation marker positioning (before punctuation)
  - Author name formatting (adding "等" when exceeding limit)
  - Reference numbering continuity
  - Duplicate reference numbers
  - Figure/table citation markers
- **Configuration**: Edit `templates/ref_format_default.yml` for custom rules
- **Usage**:
  ```bash
  python scripts/reference_formatter.py your_review.md
  python scripts/reference_formatter.py your_review.md custom_config.yml
  ```

### 4. Typo & Grammar Checker
- **Script**: `typo_grammar_checker.py`
- **Purpose**: Detect common typos, grammar errors, punctuation issues
- **What it checks**:
  - Common Chinese typos
  - Mismatched quotes/brackets
  - Punctuation usage
  - Number formatting
- **Usage**:
  ```bash
  python scripts/typo_grammar_checker.py your_review.md
  ```

### 5. Reference Accuracy Checker
- **Script**: `reference_accuracy_checker.py`
- **Purpose**: Verify citation validity and reference integrity
- **What it checks**:
  - Invalid citations (referencing non-existent references)
  - Orphaned references (not cited in text)
  - Reference numbering continuity
  - Citation numbering in text
  - Citation marker positioning
- **Usage**:
  ```bash
  python scripts/reference_accuracy_checker.py your_review.md
  ```

### 6. Document Format Checker
- **Script**: `document_format_checker.py`
- **Purpose**: Validate document structure and formatting
- **What it checks**:
  - Main title presence and formatting
  - Abstract and keywords sections
  - Chapter structure and numbering
  - References section
  - Paragraph formatting
  - Heading hierarchy
  - List formatting
- **Usage**:
  ```bash
  python scripts/document_format_checker.py your_review.md
  ```

### 7. Reference Filter
- **Script**: `filter_references.py`
- **Purpose**: Filter references based on journal quality lists
- **What it does**: Identifies and removes references from non-core journals
- **Setup required**: Edit the script's journal lists before running
- **Usage**:
  ```bash
  python scripts/filter_references.py
  ```

### 8. Reference Number Fixer
- **Script**: `extract_and_fix_references.py`
- **Purpose**: Renumber references and update all citations in text
- **What it does**: 
  - Extracts all references
  - Renumbers them sequentially
  - Updates all citation markers in text
  - Removes invalid citations
- **Warning**: Directly modifies the source file—backup first
- **Usage**:
  ```bash
  python scripts/extract_and_fix_references.py
  ```

### 9. Word Document Generator
- **Script**: `create_word_doc_v3.js` (Node.js)
- **Purpose**: Generate Word documents with Chinese academic formatting
- **What it produces**:
  - Font: SimSun (宋体) for Chinese, Times New Roman for English
  - Font size: 小四 for body, 三号 for headings
  - Line spacing: 1.5倍
  - Margins: 2.54cm
- **Requirements**: Node.js 14+, `docx` npm package
- **Usage**:
  ```bash
  node scripts/create_word_doc_v3.js
  ```

### 10. Word Document with Superscript Citations
- **Script**: `create_word_with_superscript.js` (Node.js)
- **Purpose**: Generate Word documents with **superscript reference citations** (右上标格式)
- **Important**: Citation format is `[n]` (with brackets) in superscript - e.g., `[1]`, `[2-3]`
- **Features**:
  - **Smart Font Handling**: Chinese text uses SimSun (宋体), English/numbers/punctuation use Times New Roman
  - **Superscript Citations**: Body text citations appear as superscript: `[¹]`, `[²⁻³]`
  - **Italic Scientific Names**: Automatically detects and italicizes species Latin names (e.g., *Rhinopithecus bieti*)
  - **Font Size**: Body text and references use 小四 (12pt), headings use appropriate sizes
  - **Auto-Open**: Automatically opens the generated document after creation
- **What it produces**:
  - Body text citations appear as superscript: `[¹]`, `[²⁻³]`
  - Reference list entries remain normal format (not superscript)
  - All other formatting same as standard generator
- **Requirements**: Node.js 14+, `docx` npm package
- **Usage**:
  ```bash
  node scripts/create_word_with_superscript.js your_review.md
  ```
- **Output**: `your_review_上标版.docx` (auto-opens after generation)

### 11. Citation Pattern Analyzer ⭐ NEW
- **Script**: `analyze_citation_pattern.py`
- **Purpose**: Detect "whole-paragraph citation split into per-sentence annotations" pattern
- **What it checks**:
  - Same reference cited in 2+ consecutive sentences within a paragraph
  - "Serious" flag for 3+ consecutive sentences
  - "Warning" flag for 2 consecutive sentences
  - Distinguishes valid total-then-detail structures from unnecessary repetition
- **Academic rule**: When an entire paragraph derives from one source, cite only at the first or last sentence, not every sentence
- **Usage**:
  ```bash
  python scripts/analyze_citation_pattern.py your_review.md
  ```
- **Output**: `your_review_citation_pattern_report.md`



For most use cases, follow this 9-step workflow:

### Step 1: Write Review
Create your academic review in Markdown format: `your_review.md`

### Step 2: Run Literature Integrity Check ⭐ CRITICAL
**这是最重要的检查步骤！** 运行文献完整性检查，确保所有引用和文献都正确无误：
```bash
python scripts/literature_integrity_checker.py your_review.md
```
This takes ~2 minutes and generates `your_review_literature_integrity_report.md`

**⚠️ 重要**: 此检查会发现以下严重错误：
- 无效引用（引用编号超出参考文献范围）
- 孤立引用（正文中有引用但参考文献列表中不存在）
- 参考文献编号不连续
- 重复的参考文献
- 文献信息不完整（缺少作者、标题、期刊、年份等）

**如果发现严重问题，脚本会返回错误码，阻止继续操作！**

### Step 3: Run Unified Check
Execute unified checker to run all validations at once:
```bash
python scripts/unified_checker.py your_review.md
```
This takes ~5 minutes and generates `your_review_unified_report.md`

### Step 4: Review Report
Read the unified report:
```bash
cat your_review_unified_report.md
```
The report contains:
- Problem statistics (total/critical/warnings/info)
- Detailed issues by category
- Fix recommendations

### Step 5: Fix Issues
Edit `your_review.md` based on report findings:
- Fix critical issues (🔴 must fix) first
- Then warnings (🟡 should fix)
- Finally info items (🔵 optional)

### Step 6: Filter References (Optional)
If you need to remove non-core journals:
1. Edit `scripts/filter_references.py` to set journal lists
2. Run: `python scripts/filter_references.py`

### Step 7: Fix Reference Numbers
If you removed references, renumber them:
```bash
python scripts/extract_and_fix_references.py
```
**Warning**: This modifies the source file directly—backup first!

### Step 8: Final Verification
Quick verification:
```bash
python scripts/simple_verify.py
```

**再次运行文献完整性检查（推荐）**:
```bash
python scripts/literature_integrity_checker.py your_review.md
```

✨ **新功能**: 如果检查通过（无严重问题），脚本会自动打开 `your_review_上标版.docx` 文档！

### Step 9: Generate Word Document
Create the final formatted Word document:

**Standard format** (inline citations):
```bash
node scripts/create_word_doc_v3.js
```

**Superscript format** (右上标引用) - RECOMMENDED for Chinese academic papers:
```bash
node scripts/create_word_with_superscript.js your_review.md
```
⚠️ **Important**: 
- Superscript citations include brackets: `[1]`, `[2-3]` appear as superscript
- Automatically handles mixed Chinese/English fonts (宋体 for Chinese, Times New Roman for English/numbers)
- Auto-italicizes scientific names (e.g., *Rhinopithecus bieti*)
- Document auto-opens after generation

Output: `your_review_上标版.docx`

---

### 🚀 快速工作流（推荐）

对于新的文献综述，使用以下快速工作流：

```bash
# 1. 运行文献完整性检查（自动打开 Word 文档）
python scripts/literature_integrity_checker.py your_review.md

# 检查通过后，Word 文档会自动打开！无需手动操作
# 如果发现问题，修复后再次运行检查
```

## Alternative Workflows

### Complete Workflow (Step-by-Step)
Use when you need detailed information about each check type. Run each checker individually:
1. `reference_formatter.py`
2. `typo_grammar_checker.py`
3. `reference_accuracy_checker.py`
4. `document_format_checker.py`
View each report separately for detailed analysis.

### Quick Fix Workflow
Use when you've only made minor edits after previous checks. Run only the relevant checker:
- Fixed citations? → `reference_accuracy_checker.py`
- Fixed typos? → `typo_grammar_checker.py`
- Fixed formatting? → `document_format_checker.py`
- Fixed reference format? → `reference_formatter.py`

## Important Notes

### Avoid Redundant Checks
- ❌ **Wrong**: Run unified check → fix → run unified check again → fix again...
- ✅ **Right**: Run unified check → fix → targeted recheck → generate Word

The unified checker is designed to be run once per major editing session. After fixing issues, only run the specific checkers relevant to what you changed.

### File Backup
- Scripts that modify source files: `extract_and_fix_references.py`, `filter_references.py`
- Always backup before running:
  ```bash
  cp your_review.md your_review_backup.md
  ```

### Configuration Files
- Main config: `templates/ref_format_default.yml`
- Edit this file to customize:
  - Citation style (superscript vs inline)
  - Max authors before adding "等"
  - Journal filtering rules
  - Quality check options

### Dependencies
- Python 3.7+
- Node.js 14+
- Python packages: `pyyaml`, `python-docx` (optional)
- Node.js package: `docx`

## Example Use Cases

### Case 1: First Draft - Full Check
```bash
# Step 1: Run literature integrity check (CRITICAL)
python scripts/literature_integrity_checker.py my_review.md

# Step 2: Run unified check on new draft
python scripts/unified_checker.py my_review.md

# Review and fix issues (open editor)
# ...

# Step 3: Generate Word document
node scripts/create_word_with_superscript.js my_review.md
# Total time: ~12 minutes
```

### Case 2: Reference Numbering Fix
```bash
# Backup first
cp my_review.md my_review_backup.md

# Remove non-core journals
python scripts/filter_references.py

# Renumber and update citations
python scripts/extract_and_fix_references.py

# Verify
python scripts/simple_verify.py

# Generate Word
node scripts/create_word_doc_v3.js
```

### Case 3: Minor Edits - Quick Fix
```bash
# After fixing a few typos manually, just recheck
python scripts/typo_grammar_checker.py my_review.md

# Regenerate Word
node scripts/create_word_doc_v3.js
# Total time: ~3 minutes
```

## Troubleshooting

### Python encoding issues on Windows
If you encounter GBK vs UTF-8 encoding errors:
- Ensure scripts are saved with UTF-8 encoding
- Use `encoding='utf-8'` in file operations

### Node.js docx package not found
```bash
npm install docx
```

### Missing YAML configuration
Copy `templates/ref_format_default.yml` to your working directory and edit it.

## Additional Resources

See `references/` directory for:
- Detailed workflow guides
- Configuration examples
- Troubleshooting tips
- Feature checklists

See scripts directory for:
- All executable checkers and formatters
- Helper utilities for document analysis
- Validation and repair tools

## Version History

- **v3.3.0** (2026-03-20): **功能更新 - 新增引用模式分析器 + 深度引用审查**
  - **新增**: `analyze_citation_pattern.py` - 专项检测整段引用被拆分逐句标注的问题
    - 检测连续句子中同一引用重复出现的模式
    - 3句及以上标记为严重，2句标记为警告
    - 生成详细报告含原文句子和修复建议
  - **修复（典型案例）**: 学术文献综述中发现的严重引用错误类型：
    - 引用编号指向错误文献（如用贻贝实验引用编号标注灵长类研究）→ 核查并更正
    - 超出参考文献范围的引用编号 → 全部清理或替换为有效编号
    - 引用文献内容与正文上下文不符 → 核对并修正
    - 整段内容中间重复标注 → 合并为段首+段末引用
  - **最佳实践总结**: 引用错配比重复引用更危险，需先核验参考文献实际内容

- **v3.2.0** (2026-03-19): **功能更新 - 新增自动打开最终文档功能**
  - **新增**: 文献完整性检查器支持检查通过后自动打开 Word 文档
    - 自动查找 `_上标版.docx` 或 `.docx` 文件
    - 仅在无严重问题时自动打开
    - 跨平台支持（Windows/macOS/Linux）
    - 可通过 `--no-auto-open` 参数禁用
  - **更新**: SKILL.md 文档，添加快速工作流说明
  - **改进**: 优化用户体验，简化工作流程

- **v3.1.0** (2026-03-19): **功能更新 - 新增连续相同引用检查**
  - **新增**: 连续相同引用检测功能
    - 自动检测同一段落中连续三句话或更多句子引用同一篇文献的情况
    - 遵循学术规范：同一段落中连续引用同一篇文献时，建议只在最后一句话保留引用
    - 作为警告级别提示，不阻止文档生成
  - **改进**: 优化检测逻辑，只标记相邻句子中的重复引用，避免误报段落首尾的正常引用模式
  - **更新**: 更新文献完整性检查器功能说明和版本日志

- **v3.0.0** (2026-03-19): **重大更新 - 新增文献完整性检查系统**
  - **新增**: `literature_integrity_checker.py` - 全面的文献完整性验证
    - 检查文献信息完整性（作者、标题、期刊、年份、页码）
    - 验证引用与文献列表的一致性
    - 检测无效引用和孤立引用
    - 检查参考文献编号连续性
    - 识别重复文献
    - **关键特性**: 发现严重错误时返回非零退出码，阻止错误提交
  - **更新**: 推荐工作流程，将文献完整性检查作为关键步骤
  - **改进**: 更严格的错误检测机制，杜绝文献引用错误

- **v2.3.0** (2026-03-19): Enhanced superscript Word generator with:
  - Smart mixed font handling (Chinese SimSun + English Times New Roman)
  - Auto-italicization of scientific names (Latin species names)
  - Auto-open document after generation
  - Body text and references use 小四 (12pt) font size
- **v2.2.0** (2026-03-19): Added superscript citation Word generator (`create_word_with_superscript.js`). **Important**: Superscript citations retain brackets `[n]` format.
- **v2.1.0** (2026-03-19): Added unified checker, optimized workflows, eliminated redundant checks
- **v2.0.0** (2026-03-19): Added typo checking, reference accuracy, document format validation
- **v1.0.0** (2026-03-19): Initial version with basic reference formatting and Word generation
