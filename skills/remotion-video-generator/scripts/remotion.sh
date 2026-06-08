#!/bin/bash
# Remotion Video Helper Script

COMMAND="${1:-help}"
PROJECT_DIR="${2:-.}"

case "$COMMAND" in
  "create")
    NAME="${2:-my-video}"
    echo "Creating Remotion project: $NAME"
    cd output
    npx --yes create-video@latest "$NAME" --template blank
    cd "$NAME"
    npm install
    echo "Project created at: output/$NAME"
    ;;

  "dev")
    echo "Starting Remotion Studio..."
    cd "$PROJECT_DIR"
    npm run dev
    ;;

  "build")
    echo "Building Remotion bundle..."
    cd "$PROJECT_DIR"
    npm run build
    ;;

  "render")
    COMPOSITION="${3:-MyVideo}"
    OUTPUT="${4:-out/video.mp4}"
    echo "Rendering $COMPOSITION to $OUTPUT..."
    cd "$PROJECT_DIR"
    npx remotion render "$COMPOSITION" "$OUTPUT"
    ;;

  "preview")
    echo "Starting Remotion preview..."
    cd "$PROJECT_DIR"
    npx remotion preview
    ;;

  "studio")
    echo "Starting Remotion Studio (web interface)..."
    cd "$PROJECT_DIR"
    npx remotion studio
    ;;

  "help"|*)
    echo "Remotion Helper Script"
    echo ""
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Commands:"
    echo "  create <name>     Create new Remotion project"
    echo "  dev [dir]         Start dev server"
    echo "  build [dir]       Build bundle"
    echo "  render <comp> [output] [dir]  Render video"
    echo "  preview [dir]     Start preview"
    echo "  studio [dir]      Start Studio web interface"
    echo "  help              Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 create my-promo-video"
    echo "  $0 dev ./output/my-video"
    echo "  $0 render MyComposition out/final.mp4"
    ;;
esac
