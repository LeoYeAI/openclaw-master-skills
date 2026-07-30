#!/bin/bash
#
# Unihiker K10 Skill - Arduino Upload
# Compiles and uploads Arduino sketches to K10
#

set -e

SKETCH="$1"
PORT="$2"
FQBN="${3:-unihiker:k10:k10}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# Validate inputs
if [[ -z "$SKETCH" ]]; then
    log_error "No sketch file specified"
    exit 1
fi

if [[ ! -f "$SKETCH" ]]; then
    log_error "Sketch file not found: $SKETCH"
    exit 1
fi

if [[ -z "$PORT" ]]; then
    log_error "No port specified"
    exit 1
fi

# Get sketch directory and name
SKETCH_DIR=$(dirname "$SKETCH")
SKETCH_NAME=$(basename "$SKETCH")
SKETCH_BASE="${SKETCH_NAME%.*}"

# Create build directory
BUILD_DIR="${SKETCH_DIR}/build"
mkdir -p "$BUILD_DIR"

log_info "Compiling $SKETCH_NAME for $FQBN..."
log_info "Build directory: $BUILD_DIR"

# Compile
if ! arduino-cli compile --fqbn "$FQBN" --build-path "$BUILD_DIR" "$SKETCH"; then
    log_error "Compilation failed"
    exit 1
fi

log_success "Compilation successful"

# Upload
log_info "Uploading to $PORT..."

if ! arduino-cli upload -p "$PORT" --fqbn "$FQBN" --input-dir "$BUILD_DIR" "$SKETCH"; then
    log_error "Upload failed"
    log_info "Tips:"
    log_info "  - Make sure K10 is in bootloader mode (hold BOOT, press RST)"
    log_info "  - Check that the port is correct: $PORT"
    log_info "  - Try running with sudo on Linux"
    exit 1
fi

log_success "Upload successful!"
log_info "Sketch is now running on K10"

# Cleanup build directory (optional)
# rm -rf "$BUILD_DIR"
