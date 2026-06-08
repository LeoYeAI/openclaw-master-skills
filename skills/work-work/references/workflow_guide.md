# Workwork Workflow Guide

## Complete Workflow Comparison

| Workflow | Steps | Time | Best For | Rating |
|----------|--------|------|-----------|---------|
| 🎯 Unified Check (Recommended) | 8 steps | ~10 min | First draft, comprehensive check | ⭐⭐⭐⭐⭐ |
| 📝 Step-by-Step | 11 steps | ~20 min | Detailed problem analysis | ⭐⭐⭐ |
| 🔄 Quick Fix | 3 steps | ~3 min | Minor edits | ⭐⭐⭐⭐⭐ |

## Workflow 1: Unified Check (Recommended)

**Best for:** First draft completion, full validation needed

### Process Flow

```
Step 1: Write Review
  Format: Markdown
  Output: your_review.md
    ↓
Step 2: Run Unified Check
  Command: python scripts/unified_checker.py your_review.md
  Automatically executes:
  ✓ Reference format check
  ✓ Citation accuracy check
  ✓ Typo and grammar check
  ✓ Document format compliance
  Output: your_review_unified_report.md
  Time: ~5 minutes
    ↓
Step 3: Review Unified Report
  Command: cat your_review_unified_report.md
  Report includes:
  • Problem statistics (total/critical/warnings/info)
  • Reference format issues details
  • Citation accuracy issues details
  • Typo and grammar issues details
  • Document format issues details
  • Fix recommendations
  Time: ~2 minutes
    ↓
Step 4: Fix Issues
  Fix order:
  1. Critical issues (🔴 must fix)
  2. Warning issues (🟡 should fix)
  3. Info issues (🔵 optional)
  Time: Depends on issue count
    ↓
Step 5: Filter References (Optional)
  If removing non-core journals needed:
  1. Edit scripts/filter_references.py journal list
  2. Run: python scripts/filter_references.py
  Time: ~3 minutes
    ↓
Step 6: Fix Reference Numbers
  If references removed:
  Command: python scripts/extract_and_fix_references.py
  Note: Directly modifies source file—backup first
  Time: ~2 minutes
    ↓
Step 7: Final Verification
  Command: python scripts/simple_verify.py
  Quick validation of fixes:
  • Reference numbering continuity
  • Reference completeness
  Time: ~1 minute
    ↓
Step 8: Generate Word Document
  Command: node scripts/create_word_doc_v3.js
  Generates Word with academic formatting:
  • Font: 宋体/Times New Roman
  • Size: Body 小四, Headings 三号
  • Line spacing: 1.5x
  • Margins: 2.54cm
  Input: your_review.md
  Output: your_review.docx
  Time: ~2 minutes
    ↓
✅ Complete!
Document ready for submission
```

### Command Example

```bash
# Enter workwork directory
cd ~/.workbuddy/skills/workwork

# Steps 1-2: Run unified check
python scripts/unified_checker.py your_review.md

# Step 3: Review report
cat your_review_unified_report.md

# Step 4: Manually fix issues (in text editor)

# Step 5: Filter references (optional)
# Edit scripts/filter_references.py then run
python scripts/filter_references.py

# Step 6: Fix numbering
python scripts/extract_and_fix_references.py

# Step 7: Final verification
python scripts/simple_verify.py

# Step 8: Generate Word document
node scripts/create_word_doc_v3.js

# Complete!
```

## Workflow 2: Step-by-Step

**Best for:** Detailed analysis of each specific issue type

### Process Flow

```
Step 1: Write Review
  Format: Markdown
  Input: Manual writing
  Output: your_review.md
    ↓
Step 2: Check Reference Format
  Command: python scripts/reference_formatter.py your_review.md
  Output: your_review_format_report.md
  Checks: Citation position, author format, numbering, duplicates
  Time: ~3 minutes
    ↓
Step 3: Typo and Grammar Check
  Command: python scripts/typo_grammar_checker.py your_review.md
  Output: your_review_typo_grammar_report.md
  Checks: Typos, grammar, punctuation, number format
  Time: ~3 minutes
    ↓
Step 4: Reference Accuracy Check
  Command: python scripts/reference_accuracy_checker.py your_review.md
  Output: your_review_reference_accuracy_report.md
  Checks: Reference format, citation validity, numbering
  Time: ~3 minutes
    ↓
Step 5: Document Format Check
  Command: python scripts/document_format_checker.py your_review.md
  Output: your_review_document_format_report.md
  Checks: Title, abstract, chapters, references, paragraphs
  Time: ~3 minutes
    ↓
Step 6: Review All Check Reports
  cat your_review_format_report.md
  cat your_review_typo_grammar_report.md
  cat your_review_reference_accuracy_report.md
  cat your_review_document_format_report.md
  Time: ~5 minutes
    ↓
Step 7: Confirm Fixes
  Identify issues to fix based on reports
  Time: Depends on issue count
    ↓
Step 8: Filter References (Optional)
  Edit scripts/filter_references.py journal list
  Run: python scripts/filter_references.py
  Time: ~3 minutes
    ↓
Step 9: Fix Reference Numbers
  Command: python scripts/extract_and_fix_references.py
  Time: ~2 minutes
    ↓
Step 10: Comprehensive Quality Check
  Command: python scripts/verify_review_comprehensive.py
  Time: ~2 minutes
    ↓
Step 11: Generate Word Document
  Command: node scripts/create_word_doc_v3.js
  Time: ~2 minutes
    ↓
✅ Complete!
```

### Command Example

```bash
# Enter workwork directory
cd ~/.workbuddy/skills/workwork

# Step 2: Check reference format
python scripts/reference_formatter.py your_review.md
cat your_review_format_report.md

# Step 3: Typo and grammar check
python scripts/typo_grammar_checker.py your_review.md
cat your_review_typo_grammar_report.md

# Step 4: Reference accuracy check
python scripts/reference_accuracy_checker.py your_review.md
cat your_review_reference_accuracy_report.md

# Step 5: Document format check
python scripts/document_format_checker.py your_review.md
cat your_review_document_format_report.md

# Steps 6-7: Review reports and fix issues

# Step 8: Filter references (optional)
# Edit scripts/filter_references.py then run
python scripts/filter_references.py

# Step 9: Fix numbering
python scripts/extract_and_fix_references.py

# Step 10: Comprehensive check
python scripts/verify_review_comprehensive.py

# Step 11: Generate Word document
node scripts/create_word_doc_v3.js

# Complete!
```

## Workflow 3: Quick Fix

**Best for:** Minor edits, previous comprehensive check already done

### Process Flow

```
Step 1: Fix Issues
  Based on previous errors
    ↓
    ├─ Fixed citation numbers
    │   ↓
    │   Run: python scripts/reference_accuracy_checker.py your_review.md
    │   Time: ~2 minutes
    │
    ├─ Fixed typos
    │   ↓
    │   Run: python scripts/typo_grammar_checker.py your_review.md
    │   Time: ~2 minutes
    │
    ├─ Fixed formatting
    │   ↓
    │   Run: python scripts/document_format_checker.py your_review.md
    │   Time: ~2 minutes
    │
    └─ Fixed reference format
        ↓
        Run: python scripts/reference_formatter.py your_review.md
        Time: ~2 minutes
    ↓
Step 2: Review Check Report
  Confirm fixes successful
    ↓
Step 3: Generate Word Document
  Command: node scripts/create_word_doc_v3.js
  Time: ~2 minutes
    ↓
✅ Complete!
```

### Command Examples

```bash
# Enter workwork directory
cd ~/.workbuddy/skills/workwork

# Case 1: Only fixed citation numbers
python scripts/reference_accuracy_checker.py your_review.md
node scripts/create_word_doc_v3.js

# Case 2: Only fixed typos
python scripts/typo_grammar_checker.py your_review.md
node scripts/create_word_doc_v3.js

# Case 3: Only fixed document format
python scripts/document_format_checker.py your_review.md
node scripts/create_word_doc_v3.js

# Case 4: Only fixed reference format
python scripts/reference_formatter.py your_review.md
node scripts/create_word_doc_v3.js
```

## Workflow Comparison

### Time Comparison

| Workflow | Steps | Check Time | Fix Time | Total Time |
|-----------|--------|-----------|-----------|------------|
| Unified Check | 8 steps | ~5 min | Variable | ~10 min |
| Step-by-Step | 11 steps | ~15 min | Variable | ~20 min |
| Quick Fix | 3 steps | ~2 min | Variable | ~3 min |

### Feature Comparison

| Feature | Unified | Step-by-Step | Quick Fix |
|---------|----------|--------------|-----------|
| One-pass check | ✅ | ❌ | ❌ |
| Detailed reports | ✅ | ✅ | ✅ |
| Flexibility | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Efficiency | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Avoids redundancy | ✅ | ❌ | N/A |

### Scenario Comparison

| Scenario | Unified | Step-by-Step | Quick Fix |
|----------|----------|--------------|-----------|
| First draft | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ |
| Detailed analysis | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ |
| Minor edits | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Time-critical | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## Workflow Selection Guidance

### Choose Unified Check When:
- ✅ First draft just completed
- ✅ Need comprehensive validation
- ✅ Want efficient completion
- ✅ First time using the skill

### Choose Step-by-Step When:
- ✅ Need detailed information on each specific issue
- ✅ Want to understand document condition step by step
- ✅ Learning each checker's functionality

### Choose Quick Fix When:
- ✅ Only made minor edits
- ✅ Already ran comprehensive check
- ✅ Time is limited
- ✅ Only need to verify specific sections

## Important Warnings

### Avoid Redundant Checks

```
❌ Wrong approach:
Run unified check → fix issues → run unified check again → fix again...

✅ Correct approach:
Run unified check → fix issues → targeted recheck → generate Word
```

### File Backup

```
⚠️ Caution:
- extract_and_fix_references.py directly modifies source file
- filter_references.py may modify source file

✅ Backup command:
cp your_review.md your_review_backup.md
```

## Check Frequency Recommendations

- **First draft complete:** Use Unified Check workflow
- **After fixes:** Use Quick Fix workflow
- **Before submission:** Use Unified Check workflow

## Example Use Case: First Draft, Full Check

```bash
# 1. Run unified check
python scripts/unified_checker.py my_review.md

# 2. Review report
cat my_review_unified_report.md

# Report shows:
# - Total issues: 5
# - Critical: 2 (must fix)
# - Warnings: 2 (should fix)

# 3. Fix issues
# Manually fix all issues in text editor

# 4. Filter references (optional)
python scripts/filter_references.py

# 5. Fix numbering
python scripts/extract_and_fix_references.py

# 6. Final verification
python scripts/simple_verify.py

# 7. Generate Word document
node scripts/create_word_doc_v3.js

# Complete! Time: ~10 minutes
```

## Example Use Case: Fixed Citation Numbers

```bash
# 1. Run targeted check
python scripts/reference_accuracy_checker.py my_review.md

# 2. Review report
cat my_review_reference_accuracy_report.md

# Report shows: Citation numbers correct ✅

# 3. Generate Word document
node scripts/create_word_doc_v3.js

# Complete! Time: ~3 minutes
```

---

**Document Version**: v1.0
**Last Updated**: 2026-03-19
**Skill Version**: v2.1.0
**Status**: ✅ Complete and ready to use
