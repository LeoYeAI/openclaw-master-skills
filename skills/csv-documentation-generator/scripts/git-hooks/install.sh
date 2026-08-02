#!/bin/bash
# Install git hooks for CSV Documentation Generator
# Usage: ./install.sh [--global|--local]

set -e

GLOBAL=false
HOOK_NAME="post-commit"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK_SOURCE="$SCRIPT_DIR/git-hooks/post-commit"

install_local() {
    echo "Installing local git hooks..."

    # Create .git/hooks directory if it doesn't exist
    mkdir -p "$REPO_ROOT/.git/hooks"

    # Install post-commit hook
    if [ -f "$HOOK_SOURCE" ]; then
        chmod +x "$HOOK_SOURCE"
        cp "$HOOK_SOURCE" "$REPO_ROOT/.git/hooks/$HOOK_NAME"
        echo "Installed $HOOK_NAME hook to .git/hooks/"
    else
        echo "Error: Hook source not found at $HOOK_SOURCE"
        exit 1
    fi
}

install_global() {
    echo "Installing global git hooks template..."

    # Get the global git hooks directory
    HOOKS_DIR=$(git config --global core.hooksPath 2>/dev/null || echo "")

    if [ -z "$HOOKS_DIR" ]; then
        # Use default template directory
        TEMPLATE_DIR=$(git config --global init.templateDir 2>/dev/null || echo "$HOME/.git-template")
        HOOKS_DIR="$TEMPLATE_DIR/hooks"
        mkdir -p "$HOOKS_DIR"
    fi

    # Install post-commit hook to global location
    if [ -f "$HOOK_SOURCE" ]; then
        chmod +x "$HOOK_SOURCE"
        cp "$HOOK_SOURCE" "$HOOKS_DIR/$HOOK_NAME"
        echo "Installed $HOOK_NAME hook globally to $HOOKS_DIR/"
    else
        echo "Error: Hook source not found at $HOOK_SOURCE"
        exit 1
    fi
}

uninstall() {
    echo "Removing local git hooks..."

    if [ -f "$REPO_ROOT/.git/hooks/$HOOK_NAME" ]; then
        rm "$REPO_ROOT/.git/hooks/$HOOK_NAME"
        echo "Removed $HOOK_NAME hook"
    else
        echo "No local hook found"
    fi
}

# Parse arguments
case "${1:-local}" in
    --global|-g)
        install_global
        ;;
    --local|-l)
        install_local
        ;;
    --uninstall|-u)
        uninstall
        ;;
    *)
        echo "Usage: $0 [--global|--local|--uninstall]"
        echo "  --local (default): Install hooks in .git/hooks/"
        echo "  --global: Install hooks to global git template"
        echo "  --uninstall: Remove local hooks"
        exit 1
        ;;
esac

echo "Done!"
