# Word Document Output Template

## Instructions

Generate a structured document formatted for Microsoft Word. Since we cannot generate .docx binary files directly, output as **well-structured HTML that Word can open**, or as formatted Markdown that can be pasted into Word.

## Document Structure

### Page Setup
- Paper size: A4
- Margins: 2.54cm all sides
- Font: Calibri / SimSun for Chinese
- Line spacing: 1.15

### Document Outline

```
COVER PAGE
├── Title: Hong Kong Universities Master's Programme Admissions Guide
├── Subtitle: [Academic Year]
├── Date: [Collection Date]
└── Disclaimer

TABLE OF CONTENTS

SECTION 1: EXECUTIVE SUMMARY
├── Overview
├── Key Statistics
└── Summary Table

SECTION 2: UNIVERSITY PROFILES (one per university)
├── 2.1 The University of Hong Kong (HKU)
│   ├── University Overview
│   ├── General Requirements
│   ├── Programs Table
│   └── Official Links
├── 2.2 The Chinese University of Hong Kong (CUHK)
│   └── [Same structure]
├── ... [2.3 - 2.9]
└── 2.9 Hong Kong Metropolitan University (HKMU)

SECTION 3: COMPARISON TABLES
├── 3.1 Tuition Fee Comparison
├── 3.2 Deadline Comparison
├── 3.3 English Requirements Comparison
└── 3.4 Program Availability Matrix

SECTION 4: APPENDICES
├── Appendix A: Complete Program List
├── Appendix B: Application Checklist
└── Appendix C: Useful Links

DISCLAIMER & DATA SOURCES
```

## Output Format

Generate as HTML with Word-compatible styling:

```html
<html xmlns:o="urn:schemas-microsoft-com:office:office"
      xmlns:w="urn:schemas-microsoft-com:office:word"
      xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta charset="utf-8">
<style>
  body { font-family: Calibri, SimSun, sans-serif; margin: 2.54cm; line-height: 1.15; }
  h1 { font-size: 28pt; color: #1a237e; text-align: center; page-break-before: always; }
  h2 { font-size: 20pt; color: #283593; border-bottom: 2px solid #283593; padding-bottom: 5px; }
  h3 { font-size: 14pt; color: #3949ab; }
  table { width: 100%; border-collapse: collapse; margin: 10px 0; }
  th { background: #e8eaf6; color: #1a237e; padding: 8px; border: 1px solid #9fa8da; text-align: left; }
  td { padding: 6px 8px; border: 1px solid #c5cae9; }
  tr:nth-child(even) { background: #f5f5f5; }
  .cover { text-align: center; padding-top: 200px; }
  .cover h1 { font-size: 36pt; border: none; }
  .cover .subtitle { font-size: 18pt; color: #5c6bc0; }
  .cover .date { font-size: 14pt; color: #7986cb; margin-top: 20px; }
  .disclaimer { background: #fff3e0; padding: 15px; border-left: 4px solid #ff9800; margin: 20px 0; }
  .stat-box { display: inline-block; width: 22%; text-align: center; padding: 15px; margin: 5px; background: #e8eaf6; border-radius: 8px; }
  .stat-number { font-size: 24pt; font-weight: bold; color: #1a237e; }
  .stat-label { font-size: 10pt; color: #5c6bc0; }
  a { color: #1565c0; }
  @page { size: A4; margin: 2.54cm; }
</style>
</head>
<body>
<!-- Document content follows the outline above -->
</body>
</html>
```

## Section Templates

### Cover Page Template
```html
<div class="cover">
  <h1>🎓 Hong Kong Universities<br>Master's Programme Admissions Guide</h1>
  <p class="subtitle">Comprehensive Collection from Official Sources</p>
  <p class="subtitle">[Academic Year] Intake</p>
  <p class="date">Data Collected: [Date]</p>
  <p class="date">Total Programs: [Count] | Universities: 9</p>
  <div class="disclaimer">
    ⚠️ All information sourced from official university websites only.
    Please verify details at the official links provided. Data may change without notice.
  </div>
</div>
```

### University Section Template
```html
<h2>2.X [University Full Name] ([Abbreviation])</h2>
<p><strong>Official Admissions:</strong> <a href="[URL]">[URL]</a></p>

<h3>General Requirements</h3>
<table>
  <tr><th>IELTS</th><th>TOEFL</th><th>Other</th></tr>
  <tr><td>[Score]</td><td>[Score]</td><td>[Other]</td></tr>
</table>

<h3>Taught Master's Programmes</h3>
<table>
  <tr>
    <th>Programme</th><th>Degree</th><th>Mode</th><th>Duration</th>
    <th>Tuition (HKD)</th><th>Deadline</th><th>Link</th>
  </tr>
  <!-- One row per program -->
  <tr>
    <td>[Program Name]</td><td>[Type]</td><td>[Mode]</td><td>[Duration]</td>
    <td>[Fee]</td><td>[Deadline]</td><td><a href="[URL]">View</a></td>
  </tr>
</table>
```

### Comparison Table Template
```html
<h2>3. Comparison Tables</h2>
<h3>3.1 Tuition Fee Comparison</h3>
<table>
  <tr><th>University</th><th>Min Fee</th><th>Max Fee</th><th>Average Fee</th></tr>
  <!-- One row per university -->
</table>
```

## Delivery Instructions

Present in a code block with `html` language tag. Tell the user:

> **How to open in Microsoft Word:**
> 1. Copy the HTML content into a text file
> 2. Save as `hk_admissions_guide.html`
> 3. Open with Microsoft Word (Right-click → Open With → Word)
> 4. Word will convert it to a proper .docx document
> 5. Save As → Word Document (.docx) to keep the Word format
