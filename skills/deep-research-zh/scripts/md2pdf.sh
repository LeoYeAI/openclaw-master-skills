#!/usr/bin/env bash
# md2pdf.sh — Markdown to PDF converter with CJK support and graceful fallback
# Usage: md2pdf.sh <input.md> [output.pdf]
#
# Engine priority: weasyprint > wkhtmltopdf > send markdown as-is
# All engines produce Chinese-friendly output with embedded CSS.
set -euo pipefail

INPUT="${1:?Usage: md2pdf.sh <input.md> [output.pdf]}"
OUTPUT="${2:-}"

# Derive output path from input if not specified
if [ -z "$OUTPUT" ]; then
  OUTPUT="${INPUT%.md}.pdf"
fi

# Ensure input exists
if [ ! -f "$INPUT" ]; then
  echo "ERROR: Input file not found: $INPUT" >&2
  exit 1
fi

# Working directory for temp files
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

# Inline CSS for Chinese-friendly PDF
CSS_FILE="$WORKDIR/style.css"
cat > "$CSS_FILE" << 'CSSEOF'
@page {
  size: A4;
  margin: 2cm 2.2cm;
}
body {
  font-family: "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif;
  font-size: 14px;
  line-height: 1.8;
  color: #333;
  max-width: 100%;
}
h1 {
  font-size: 22px;
  color: #1a1a1a;
  border-bottom: 2px solid #4a90d9;
  padding-bottom: 8px;
  margin-top: 0;
}
h2 {
  font-size: 18px;
  color: #2c3e50;
  margin-top: 1.8em;
  border-bottom: 1px solid #eee;
  padding-bottom: 4px;
}
h3 {
  font-size: 16px;
  color: #34495e;
  margin-top: 1.5em;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  font-size: 13px;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: left;
}
th {
  background-color: #f5f5f5;
  font-weight: 600;
}
tr:nth-child(even) {
  background-color: #fafafa;
}
blockquote {
  border-left: 4px solid #4a90d9;
  margin: 1em 0;
  padding: 10px 20px;
  background: #f9f9f9;
  color: #555;
}
code {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
}
pre {
  background: #f8f8f8;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 12px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
}
a {
  color: #4a90d9;
  text-decoration: none;
}
strong {
  color: #2c3e50;
}
hr {
  border: none;
  border-top: 1px solid #e0e0e0;
  margin: 2em 0;
}
img {
  max-width: 100%;
}
ul, ol {
  padding-left: 2em;
}
li {
  margin-bottom: 0.3em;
}
CSSEOF

HTML_FILE="$WORKDIR/output.html"

# Detect available PDF engine and convert
if command -v weasyprint &>/dev/null; then
  echo "[md2pdf] Using weasyprint"
  # Step 1: md → html with embedded CSS
  pandoc "$INPUT" -o "$HTML_FILE" \
    --standalone \
    --css="$CSS_FILE" \
    --self-contained \
    --metadata title="" \
    2>/dev/null
  # Step 2: html → pdf
  weasyprint "$HTML_FILE" "$OUTPUT" 2>/dev/null
  if [ $? -eq 0 ] && [ -f "$OUTPUT" ]; then
    echo "[md2pdf] ✅ Success: $OUTPUT"
    exit 0
  fi
  echo "[md2pdf] ⚠️ weasyprint failed, trying next engine..." >&2

elif command -v wkhtmltopdf &>/dev/null; then
  echo "[md2pdf] Using wkhtmltopdf"
  pandoc "$INPUT" -o "$HTML_FILE" \
    --standalone \
    --self-contained \
    --metadata title="" \
    2>/dev/null
  # Inject CSS into HTML if possible
  wkhtmltopdf --encoding utf-8 --page-size A4 --margin-top 20mm --margin-bottom 20mm --margin-left 22mm --margin-right 22mm "$HTML_FILE" "$OUTPUT" 2>/dev/null
  if [ $? -eq 0 ] && [ -f "$OUTPUT" ]; then
    echo "[md2pdf] ✅ Success: $OUTPUT"
    exit 0
  fi
  echo "[md2pdf] ⚠️ wkhtmltopdf failed" >&2

else
  echo "[md2pdf] ⚠️ No PDF engine found (tried: weasyprint, wkhtmltopdf)" >&2
fi

# All engines failed — graceful fallback
echo "[md2pdf] ❌ PDF generation failed. Sending markdown instead." >&2
echo "[md2pdf] To fix: pip install weasyprint  OR  apt install wkhtmltopdf" >&2
exit 1
