#!/bin/bash
# NPM Package Automated Audit Script
# Usage: ./audit-npm-package.sh package-name version

set -e

PACKAGE=$1
VERSION=$2

if [ -z "$PACKAGE" ] || [ -z "$VERSION" ]; then
    echo "Usage: $0 <package-name> <version>"
    echo "Example: $0 @catalyst-team/poly-sdk 0.5.0"
    exit 1
fi

PACKAGE_SAFE=$(echo $PACKAGE | tr '/' '-')
OUTPUT_DIR="audit-${PACKAGE_SAFE}-${VERSION}"

echo "=== NPM Package Audit: $PACKAGE@$VERSION ==="
echo "Output directory: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

# 1. Get NPM metadata
echo "[1/6] Fetching NPM metadata..."
npm view $PACKAGE@$VERSION --json > npm-metadata.json
echo "✅ Saved to npm-metadata.json"

# 2. Download NPM package
echo ""
echo "[2/6] Downloading NPM package..."
npm pack $PACKAGE@$VERSION
TARBALL=$(ls *.tgz | head -1)
echo "✅ Downloaded: $TARBALL"

# 3. Extract package
echo ""
echo "[3/6] Extracting package..."
mkdir -p npm-extract
tar -xzf $TARBALL -C npm-extract
FILE_COUNT=$(find npm-extract -type f | wc -l)
echo "✅ Extracted $FILE_COUNT files"

# 4. Clone GitHub repository (if available)
echo ""
echo "[4/6] Checking GitHub repository..."
REPO_URL=$(cat npm-metadata.json | jq -r '.repository.url // empty')

if [ -n "$REPO_URL" ]; then
    # Convert git+https to https
    REPO_URL=$(echo $REPO_URL | sed 's/git+https/https/' | sed 's/\.git$//')
    echo "Found repository: $REPO_URL"

    git clone --depth 50 $REPO_URL github-repo 2>&1 | grep -E "Cloning|Receiving" || echo "Repository clone failed or not needed"
else
    echo "⚠️  No GitHub repository found in package metadata"
fi

# 5. Compare NPM vs GitHub (if available)
echo ""
echo "[5/6] Comparing NPM package with GitHub source..."
if [ -d "github-repo" ]; then
    # Compare package.json
    echo "Comparing package.json scripts..."
    NPM_SCRIPTS=$(cat npm-extract/package/package.json | jq -S '.scripts')
    GITHUB_SCRIPTS=$(cat github-repo/package.json | jq -S '.scripts')

    if [ "$NPM_SCRIPTS" == "$GITHUB_SCRIPTS" ]; then
        echo "✅ Scripts match"
    else
        echo "❌ Scripts MISMATCH:"
        diff <(echo "$NPM_SCRIPTS") <(echo "$GITHUB_SCRIPTS")
    fi

    # Count differences
    DIFF_COUNT=$(diff -r npm-extract/package github-repo 2>/dev/null | grep -c "^diff" || echo "0")
    echo "Found $DIFF_COUNT differences"
else
    echo "⚠️  Skipping comparison (no GitHub repo)"
fi

# 6. Verify integrity
echo ""
echo "[6/6] Verifying integrity..."
EXPECTED_HASH=$(cat npm-metadata.json | jq -r '.dist.integrity')
echo "Expected integrity: $EXPECTED_HASH"

# Calculate actual hash
if command -v shasum &> /dev/null; then
    ACTUAL_HASH=$(shasum -a 512 $TARBALL | awk '{print $1}')
    ACTUAL_HASH_ALGO="sha512"

    if echo "$EXPECTED_HASH" | grep -q "$ACTUAL_HASH"; then
        echo "✅ Integrity verified"
    else
        echo "⚠️  Integrity hash mismatch"
        echo "Expected: $EXPECTED_HASH"
        echo "Actual:   $ACTUAL_HASH_ALGO-$ACTUAL_HASH"
    fi
else
    echo "⚠️  shasum not available, skipping integrity check"
fi

# Summary
echo ""
echo "=== Audit Summary ==="
echo "Package: $PACKAGE@$VERSION"
echo "Files: $FILE_COUNT"
echo "Size: $(du -sh npm-extract | cut -f1)"
echo ""
echo "Next steps:"
echo "1. Review npm-metadata.json"
echo "2. Inspect files in npm-extract/"
echo "3. Run source code analysis tools"
echo "4. Check Git history (if GitHub repo available)"
echo ""
echo "Output saved to: $OUTPUT_DIR/"
