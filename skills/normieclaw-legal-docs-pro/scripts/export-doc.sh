#!/usr/bin/env bash
set -euo pipefail

# Legal Docs Pro — Document Export
# Exports a document from the data directory as markdown or PDF

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$SKILL_DIR/data"
DOCS_DIR="$DATA_DIR/documents"

usage() {
    echo "Usage: export-doc.sh [OPTIONS] [FILENAME]"
    echo ""
    echo "Options:"
    echo "  --format md|pdf   Output format (default: md)"
    echo "  --output PATH     Output file path (default: ~/Documents/)"
    echo "  --list            List available documents"
    echo "  --help            Show this help"
    echo ""
    echo "Examples:"
    echo "  export-doc.sh --list"
    echo "  export-doc.sh --format pdf --output ~/Desktop/nda.pdf nda-acme-2026.md"
    echo "  export-doc.sh nda-acme-2026.md"
}

FORMAT="md"
OUTPUT=""
LIST=false
FILENAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --format)
            if [[ -z "${2:-}" ]]; then
                echo "Error: --format requires a value (md or pdf)" >&2
                exit 1
            fi
            FORMAT="$2"
            if [[ "$FORMAT" != "md" && "$FORMAT" != "pdf" ]]; then
                echo "Error: format must be 'md' or 'pdf'" >&2
                exit 1
            fi
            shift 2
            ;;
        --output)
            if [[ -z "${2:-}" ]]; then
                echo "Error: --output requires a path" >&2
                exit 1
            fi
            OUTPUT="$2"
            shift 2
            ;;
        --list)
            LIST=true
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
            FILENAME="$1"
            shift
            ;;
    esac
done

# Ensure data directory exists
if [[ ! -d "$DOCS_DIR" ]]; then
    echo "Error: No documents directory found. Run setup.sh first." >&2
    exit 1
fi

# List mode
if [[ "$LIST" == true ]]; then
    echo "📄 Available Documents:"
    echo "━━━━━━━━━━━━━━━━━━━━━━"
    FOUND=false
    for f in "$DOCS_DIR"/*.md; do
        if [[ -f "$f" ]]; then
            FOUND=true
            BASENAME=$(basename "$f")
            SIZE=$(wc -c < "$f" | tr -d ' ')
            MOD=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$f" 2>/dev/null || stat -c "%y" "$f" 2>/dev/null | cut -d'.' -f1)
            echo "  $BASENAME  ($SIZE bytes, $MOD)"
        fi
    done
    if [[ "$FOUND" == false ]]; then
        echo "  No documents found. Generate one by asking the agent."
    fi
    exit 0
fi

# Require filename
if [[ -z "$FILENAME" ]]; then
    echo "Error: no filename specified." >&2
    echo "Use --list to see available documents, or specify a filename." >&2
    echo ""
    usage
    exit 1
fi

SOURCE="$DOCS_DIR/$FILENAME"

# Check source exists
if [[ ! -f "$SOURCE" ]]; then
    echo "Error: document not found: $FILENAME" >&2
    echo "Use --list to see available documents." >&2
    exit 1
fi

# Determine output path
if [[ -z "$OUTPUT" ]]; then
    BASENAME="${FILENAME%.md}"
    OUTPUT="$HOME/Documents/${BASENAME}.${FORMAT}"
fi

# Ensure output directory exists
OUTPUT_DIR=$(dirname "$OUTPUT")
mkdir -p "$OUTPUT_DIR"

if [[ "$FORMAT" == "md" ]]; then
    cp "$SOURCE" "$OUTPUT"
    echo "✓ Exported to: $OUTPUT"
elif [[ "$FORMAT" == "pdf" ]]; then
    # Check for pandoc
    if ! command -v pandoc &>/dev/null; then
        echo "pandoc is required for PDF export but not found."
        echo ""
        if command -v brew &>/dev/null; then
            read -rp "Install pandoc via Homebrew? (y/N): " INSTALL
            if [[ "$INSTALL" =~ ^[Yy]$ ]]; then
                brew install pandoc
            else
                echo "Install pandoc manually: brew install pandoc (macOS) or sudo apt install pandoc (Linux)"
                exit 1
            fi
        else
            echo "Install pandoc: https://pandoc.org/installing.html"
            exit 1
        fi
    fi

    # Check for a PDF engine
    PDF_ENGINE=""
    for engine in pdflatex xelatex lualatex wkhtmltopdf weasyprint; do
        if command -v "$engine" &>/dev/null; then
            PDF_ENGINE="$engine"
            break
        fi
    done

    if [[ -z "$PDF_ENGINE" ]]; then
        echo "Warning: No PDF engine found. Trying pandoc default..." >&2
        pandoc "$SOURCE" -o "$OUTPUT" --metadata title="Legal Document" 2>/dev/null || {
            echo "Error: PDF generation failed. Install a PDF engine:" >&2
            echo "  brew install --cask basictex   (macOS)" >&2
            echo "  sudo apt install texlive       (Linux)" >&2
            echo "  pip install weasyprint         (cross-platform)" >&2
            exit 1
        }
    else
        pandoc "$SOURCE" -o "$OUTPUT" --pdf-engine="$PDF_ENGINE" --metadata title="Legal Document"
    fi

    echo "✓ Exported PDF to: $OUTPUT"
fi
