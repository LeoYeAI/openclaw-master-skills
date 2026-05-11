#!/bin/bash
# Bundle a Vite React project into a single HTML file
# Usage: bash scripts/bundle-artifact.sh
# Run from project root (where package.json is)

set -e

echo "📦 Bundling to single HTML file..."

# Check if we're in a project directory
if [ ! -f "package.json" ]; then
  echo "❌ Error: No package.json found. Run this from your project root."
  exit 1
fi

# Check if index.html exists
if [ ! -f "index.html" ]; then
  echo "❌ Error: No index.html found in project root."
  exit 1
fi

# Install bundling dependencies if needed
if ! npm ls parcel > /dev/null 2>&1; then
  echo "📦 Installing bundling dependencies..."
  npm install -D parcel @parcel/config-default parcel-resolver-tspaths html-inline
fi

# Create .parcelrc if it doesn't exist
if [ ! -f ".parcelrc" ]; then
  echo "⚙️ Creating Parcel config..."
  cat > .parcelrc << 'EOF'
{
  "extends": "@parcel/config-default",
  "resolvers": ["parcel-resolver-tspaths", "..."]
}
EOF
fi

# Build with Parcel
echo "🔨 Building with Parcel..."
npx parcel build index.html --no-source-maps --dist-dir dist-parcel

# Inline all assets
echo "📄 Inlining assets into single HTML..."
npx html-inline -i dist-parcel/index.html -o bundle.html -b dist-parcel

# Clean up
rm -rf dist-parcel .parcel-cache

# Get file size
SIZE=$(ls -lh bundle.html | awk '{print $5}')

echo ""
echo "✅ Bundle created: bundle.html ($SIZE)"
echo ""
echo "You can now share this file or use it as a Claude artifact."
echo ""
