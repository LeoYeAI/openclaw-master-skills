# PDF Output Template

## Instructions

Generate a print-ready HTML document optimized for PDF conversion. The user can save it as PDF directly from the browser (Print → Save as PDF) or from Word.

## Design Principles

- Clean, professional layout
- Optimized for A4 paper printing
- Proper page breaks between universities
- Headers and footers on each page
- Color-coded sections for easy navigation

## Output Format

Generate as HTML with print-optimized CSS:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Hong Kong Universities Master's Admissions Guide</title>
<style>
  /* Print optimization */
  @page {
    size: A4;
    margin: 2cm 2.5cm;
    @top-center { content: "HK University Master's Admissions Guide"; font-size: 9pt; color: #666; }
    @bottom-center { content: "Page " counter(page) " of " counter(pages); font-size: 9pt; color: #666; }
  }

  @media print {
    .no-print { display: none; }
    .page-break { page-break-before: always; }
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }

  /* General styles */
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', Calibri, 'Microsoft YaHei', sans-serif;
    font-size: 10pt;
    line-height: 1.4;
    color: #333;
  }

  /* Cover page */
  .cover-page {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: linear-gradient(135deg, #1a237e 0%, #3f51b5 100%);
    color: white;
    page-break-after: always;
  }
  .cover-page h1 { font-size: 32pt; margin-bottom: 10px; }
  .cover-page .subtitle { font-size: 16pt; opacity: 0.9; }
  .cover-page .meta { font-size: 11pt; opacity: 0.7; margin-top: 30px; }

  /* TOC */
  .toc { page-break-after: always; }
  .toc h2 { font-size: 18pt; margin-bottom: 15px; color: #1a237e; }
  .toc-item { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dotted #ccc; }

  /* Sections */
  h2 {
    font-size: 16pt; color: #1a237e;
    border-bottom: 3px solid #3f51b5;
    padding-bottom: 5px; margin: 20px 0 10px 0;
  }
  h3 { font-size: 12pt; color: #3949ab; margin: 15px 0 8px 0; }
  h4 { font-size: 10pt; color: #5c6bc0; margin: 10px 0 5px 0; }

  /* Tables */
  table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 9pt; }
  th {
    background: #e8eaf6; color: #1a237e;
    padding: 6px 8px; border: 1px solid #9fa8da;
    text-align: left; font-weight: 600;
  }
  td { padding: 5px 8px; border: 1px solid #c5cae9; }
  tr:nth-child(even) { background: #fafafa; }

  /* Info boxes */
  .info-box {
    background: #e3f2fd; border-left: 4px solid #1976d2;
    padding: 10px 15px; margin: 10px 0; font-size: 9pt;
  }
  .warning-box {
    background: #fff3e0; border-left: 4px solid #f57c00;
    padding: 10px 15px; margin: 10px 0; font-size: 9pt;
  }

  /* Stats grid */
  .stats-grid { display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }
  .stat-card {
    flex: 1; min-width: 120px; text-align: center;
    background: #e8eaf6; border-radius: 6px; padding: 12px;
  }
  .stat-card .number { font-size: 20pt; font-weight: bold; color: #1a237e; }
  .stat-card .label { font-size: 8pt; color: #5c6bc0; text-transform: uppercase; }

  a { color: #1565c0; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
  <h1>🎓 Hong Kong Universities</h1>
  <h1>Master's Programme Admissions Guide</h1>
  <p class="subtitle">[Academic Year] Intake</p>
  <p class="meta">
    9 Universities | [X] Programmes | Official Data Only<br>
    Data Collected: [Date]
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<div class="toc">
  <h2>Table of Contents</h2>
  <!-- Auto-generate TOC entries -->
</div>

<!-- EXECUTIVE SUMMARY -->
<div class="page-break">
  <h2>Executive Summary</h2>
  <div class="stats-grid">
    <div class="stat-card"><div class="number">[X]</div><div class="label">Total Programs</div></div>
    <div class="stat-card"><div class="number">9</div><div class="label">Universities</div></div>
    <div class="stat-card"><div class="number">[X]</div><div class="label">Avg Tuition HKD</div></div>
    <div class="stat-card"><div class="number">[X]</div><div class="label">Degree Types</div></div>
  </div>
  <div class="warning-box">
    ⚠️ All data sourced exclusively from official university websites.
    Verify at provided links before making application decisions.
  </div>
</div>

<!-- UNIVERSITY SECTIONS (one per university, each starts on new page) -->
<div class="page-break">
  <h2>[University Name]</h2>
  <!-- University content with tables -->
</div>

<!-- COMPARISON SECTION -->
<div class="page-break">
  <h2>Cross-University Comparison</h2>
  <!-- Comparison tables -->
</div>

<!-- APPENDIX -->
<div class="page-break">
  <h2>Appendices</h2>
  <!-- Complete listings and links -->
</div>

</body>
</html>
```

## Delivery Instructions

Present in a code block with `html` language tag. Tell the user:

> **How to save as PDF:**
> 1. Copy the HTML content into a file named `hk_admissions_guide.html`
> 2. Open in any web browser (Chrome, Edge, Safari, Firefox)
> 3. Press `Ctrl+P` (Windows) or `Cmd+P` (Mac) to open Print dialog
> 4. Select "Save as PDF" as the printer
> 5. Click Save
>
> The document is optimized for A4 paper with proper page breaks, headers, and footers.
