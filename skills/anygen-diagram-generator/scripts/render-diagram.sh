#!/usr/bin/env bash
# render-diagram.sh — Convert Excalidraw/DrawIO diagrams to PNG
#
# Usage: render-diagram.sh <type> <input> <output> [options]
#
# Arguments:
#   type    Diagram type: excalidraw | drawio
#   input   Input file path (use "-" for stdin)
#   output  Output PNG file path
#
# Options:
#   --scale <n>        PNG scale factor (default: 2)
#   --background <hex> Background color (default: #ffffff)
#   --padding <n>      Export padding in px (default: 20)
#
# Dependencies (playwright, tsx) are auto-installed on first run.

set -euo pipefail

# ---- Colors ----

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ---- Paths ----

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---- Usage ----

usage() {
  cat <<EOF
Usage: $(basename "$0") <type> <input> <output> [options]

Arguments:
  type    Diagram type: excalidraw | drawio
  input   Input file path (use "-" for stdin)
  output  Output PNG file path

Options:
  --scale <n>        PNG scale factor (default: 2)
  --background <hex> Background color (default: #ffffff)
  --padding <n>      Export padding in px (default: 20)

Examples:
  $(basename "$0") excalidraw diagram.json output.png
  $(basename "$0") drawio diagram.xml output.png
  $(basename "$0") excalidraw diagram.json output.png --scale 3
  cat diagram.json | $(basename "$0") excalidraw - output.png
EOF
}

# ---- Show usage if no arguments or --help ----

if [[ $# -eq 0 ]] || [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

# ---- Parse positional arguments ----

TYPE="${1:-}"
INPUT_FILE="${2:-}"
OUTPUT_FILE="${3:-}"

if [[ -z "$TYPE" ]] || [[ -z "$INPUT_FILE" ]] || [[ -z "$OUTPUT_FILE" ]]; then
  echo -e "${RED}✗ Missing required arguments${NC}" >&2
  echo "" >&2
  usage >&2
  exit 1
fi

# ---- Validate diagram type ----

if [[ "$TYPE" != "excalidraw" ]] && [[ "$TYPE" != "drawio" ]]; then
  echo -e "${RED}✗ Unsupported diagram type: $TYPE${NC}" >&2
  echo -e "${YELLOW}  Supported types: excalidraw, drawio${NC}" >&2
  exit 1
fi

# ---- Validate input file ----

if [[ "$INPUT_FILE" != "-" ]] && [[ ! -f "$INPUT_FILE" ]]; then
  echo -e "${RED}✗ Input file not found: $INPUT_FILE${NC}" >&2
  exit 1
fi

# ---- Check Node.js ----

if ! command -v node &> /dev/null; then
  echo -e "${RED}✗ Node.js not found${NC}" >&2
  echo -e "${YELLOW}  Please install Node.js (v18+): https://nodejs.org${NC}" >&2
  exit 1
fi

if ! command -v npm &> /dev/null; then
  echo -e "${RED}✗ npm not found${NC}" >&2
  echo -e "${YELLOW}  Please install npm${NC}" >&2
  exit 1
fi

# ---- Auto-install npm dependencies ----

if [[ ! -d "$SCRIPT_DIR/node_modules/playwright" ]] || [[ ! -d "$SCRIPT_DIR/node_modules/tsx" ]]; then
  echo -e "${BLUE}⚙ First run, installing dependencies...${NC}"
  if (cd "$SCRIPT_DIR" && npm install --no-audit --no-fund --loglevel=error); then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
  else
    echo -e "${RED}✗ Failed to install dependencies${NC}" >&2
    echo -e "${YELLOW}  Please run manually: cd $SCRIPT_DIR && npm install${NC}" >&2
    exit 1
  fi
fi

# ---- Auto-install Playwright Chromium ----

PLAYWRIGHT_BIN="$SCRIPT_DIR/node_modules/.bin/playwright"
if [[ -x "$PLAYWRIGHT_BIN" ]]; then
  # Check if chromium browser is available
  if ! "$PLAYWRIGHT_BIN" install --dry-run chromium &> /dev/null; then
    echo -e "${BLUE}⚙ Installing Chromium browser...${NC}"
    if "$PLAYWRIGHT_BIN" install chromium; then
      echo -e "${GREEN}✓ Chromium installed${NC}"
    else
      echo -e "${YELLOW}⚠ Chromium installation may have issues, will try system browser${NC}"
    fi
  fi
fi

# ---- Create output directory ----

OUTPUT_DIR="$(dirname "$OUTPUT_FILE")"
if [[ "$OUTPUT_DIR" != "." ]] && [[ ! -d "$OUTPUT_DIR" ]]; then
  mkdir -p "$OUTPUT_DIR"
fi

# ---- Render ----

echo -e "${BLUE}▶ Rendering $TYPE diagram -> PNG${NC}"
echo -e "${BLUE}  Input:  $INPUT_FILE${NC}"
echo -e "${BLUE}  Output: $OUTPUT_FILE${NC}"

TSX_BIN="$SCRIPT_DIR/node_modules/.bin/tsx"

if "$TSX_BIN" "$SCRIPT_DIR/diagram-to-image.ts" "$@"; then
  echo -e "${GREEN}✓ Render complete: $OUTPUT_FILE${NC}"
  exit 0
else
  echo -e "${RED}✗ Render failed${NC}" >&2
  exit 1
fi
