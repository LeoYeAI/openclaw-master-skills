#!/usr/bin/env bash

# promote-review.sh
# Scans memory/core/ for learnings tagged as "ready_for_promotion" and builds a unified review document.

MEMORY_DIR="$HOME/.openclaw/workspace/memory/core"
REVIEW_DOC="$HOME/.openclaw/workspace/memory/core/promotion_review.md"

echo "Scanning $MEMORY_DIR for items ready for promotion..."

if [ ! -d "$MEMORY_DIR" ]; then
  echo "Error: Memory directory not found at $MEMORY_DIR"
  exit 1
fi

# Find files containing ready_for_promotion
FILES_TO_REVIEW=$(grep -l "\*\*Status\*\*: ready_for_promotion" "$MEMORY_DIR"/*.md 2>/dev/null)

if [ -z "$FILES_TO_REVIEW" ]; then
  echo "No items are currently marked as 'ready_for_promotion'."
  echo "Status check complete."
  exit 0
fi

# Create or overwrite the review document
cat << 'EOF' > "$REVIEW_DOC"
# Weekly Promotion Review

The following items have triggered the Rule of 3 (accumulated 3+ See Also links) and are ready for promotion.

Please review the list below. Reply to OpenClaw with: "Approve [Item-ID] for [Target]" (e.g., "Approve LRN-20260302-001 for TOOLS.md").

---
EOF

for file in $FILES_TO_REVIEW; do
  echo "Found pending promotion in $(basename "$file")"
  echo "## From File: $(basename "$file")" >> "$REVIEW_DOC"
  # Extract the item block (Header until the next --- separator or EOF)
  awk '/^\#\# \[/{flag=1; print; next} /^---/{if(flag) {print; flag=0; next}} flag' "$file" >> "$REVIEW_DOC"
  echo -e "\n\n" >> "$REVIEW_DOC"
done

echo "Review document generated at: $REVIEW_DOC"
echo "OpenClaw: Please prompt the user to review this document."
