#!/usr/bin/env bash
set -euo pipefail

# Legal Docs Pro — Contract Risk Scan
# Reads a contract file and prepares it for agent review

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$SKILL_DIR/data"
REVIEWS_DIR="$DATA_DIR/reviews"

usage() {
    echo "Usage: contract-scan.sh [OPTIONS] <contract-file>"
    echo ""
    echo "Reads a contract file and outputs it for agent review."
    echo "Supports: .txt, .md, .pdf (text extraction), .docx (text extraction)"
    echo ""
    echo "Options:"
    echo "  --save          Save a copy to the reviews directory"
    echo "  --help          Show this help"
    echo ""
    echo "Examples:"
    echo "  contract-scan.sh ~/Documents/office-lease.txt"
    echo "  contract-scan.sh --save vendor-agreement.md"
}

SAVE=false
INPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --save)
            SAVE=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        -*)
            echo "Error: unknown option '$1'" >&2
            usage
            exit 1
            ;;
        *)
            INPUT_FILE="$1"
            shift
            ;;
    esac
done

# Validate input
if [[ -z "$INPUT_FILE" ]]; then
    echo "Error: no contract file specified." >&2
    echo ""
    usage
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: file not found: $INPUT_FILE" >&2
    exit 1
fi

# Get file info
FILE_SIZE=$(wc -c < "$INPUT_FILE" | tr -d ' ')
FILE_EXT="${INPUT_FILE##*.}"
FILE_NAME=$(basename "$INPUT_FILE")

# Size check (warn over 500KB)
if [[ "$FILE_SIZE" -gt 512000 ]]; then
    echo "Warning: Large file ($FILE_SIZE bytes). Processing may take longer." >&2
fi

# Extract text based on file type
CONTENT=""
case "$FILE_EXT" in
    txt|md|text)
        CONTENT=$(cat "$INPUT_FILE")
        ;;
    pdf)
        if command -v pdftotext &>/dev/null; then
            CONTENT=$(pdftotext "$INPUT_FILE" - 2>/dev/null)
        elif command -v python3 &>/dev/null; then
            CONTENT=$(python3 -c "
import subprocess, sys
try:
    result = subprocess.run(['textutil', '-convert', 'txt', '-stdout', '$INPUT_FILE'],
                          capture_output=True, text=True)
    print(result.stdout)
except Exception:
    print('Error: Cannot extract text from PDF. Install poppler: brew install poppler', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null) || {
                echo "Error: Cannot extract text from PDF." >&2
                echo "Install poppler: brew install poppler (macOS) or sudo apt install poppler-utils (Linux)" >&2
                exit 1
            }
        else
            echo "Error: Cannot extract text from PDF. Install poppler-utils." >&2
            exit 1
        fi
        ;;
    docx)
        if command -v textutil &>/dev/null; then
            CONTENT=$(textutil -convert txt -stdout "$INPUT_FILE" 2>/dev/null)
        elif command -v pandoc &>/dev/null; then
            CONTENT=$(pandoc "$INPUT_FILE" -t plain 2>/dev/null)
        else
            echo "Error: Cannot extract text from .docx. Install pandoc: brew install pandoc" >&2
            exit 1
        fi
        ;;
    *)
        echo "Warning: Unrecognized file type '.$FILE_EXT'. Attempting to read as plain text." >&2
        CONTENT=$(cat "$INPUT_FILE")
        ;;
esac

if [[ -z "$CONTENT" ]]; then
    echo "Error: No text content could be extracted from $FILE_NAME" >&2
    exit 1
fi

# Count some basics
LINE_COUNT=$(echo "$CONTENT" | wc -l | tr -d ' ')
WORD_COUNT=$(echo "$CONTENT" | wc -w | tr -d ' ')

# Save a copy if requested
if [[ "$SAVE" == true ]]; then
    mkdir -p "$REVIEWS_DIR"
    TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
    SAVE_PATH="$REVIEWS_DIR/${TIMESTAMP}-${FILE_NAME%.${FILE_EXT}}.md"
    {
        echo "# Contract Scan: $FILE_NAME"
        echo "**Scanned:** $(date '+%Y-%m-%d %H:%M')"
        echo "**Source:** $INPUT_FILE"
        echo "**Size:** $FILE_SIZE bytes | $WORD_COUNT words | $LINE_COUNT lines"
        echo ""
        echo "---"
        echo ""
        echo "$CONTENT"
    } > "$SAVE_PATH"
    echo "✓ Copy saved to: $SAVE_PATH" >&2
fi

# Output for agent review
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 CONTRACT SCAN: $FILE_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Source: $INPUT_FILE"
echo "Size: $FILE_SIZE bytes | $WORD_COUNT words | $LINE_COUNT lines"
echo "Format: .$FILE_EXT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Please review the following contract using the Legal Docs Pro"
echo "multi-pass review process (identify → flag risks → check missing"
echo "protections → summarize):"
echo ""
echo "--- BEGIN CONTRACT TEXT ---"
echo ""
echo "$CONTENT"
echo ""
echo "--- END CONTRACT TEXT ---"
