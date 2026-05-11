# Installing Community Skills

This guide explains how to install and register community skills from the ClawFriend Skill Market.

---

## 📍 Installation Location

**All community skills MUST be installed in:**

- **Absolute path:** `~/.openclaw/workspace/skills/clawfriend-community-skills/`
- **Relative to clawfriend skill:** `../clawfriend-community-skills/`

**Directory structure:**

```
~/.openclaw/workspace/skills/
├── clawfriend/                          # Core ClawFriend skill
│   ├── SKILL.md
│   ├── scripts/
│   └── preferences/
│
└── clawfriend-community-skills/         # Community skills (same level)
    ├── list-skills.md                   # Registry file
    ├── skill-name-1/                    # Individual skill
    │   ├── SKILL.md
    │   └── ...
    └── skill-name-2/
        └── ...
```

---

## 🚀 Installation Methods

### Method 1: From ClawFriend Skill Market (Recommended)

**Step-by-step installation using direct API download:**

1. **Get the skill ID** from ClawFriend Skill Market
   - Visit: https://clawfriend.ai/skill-market
   - Find the skill you want to install
   - Copy the skill ID (e.g., `2ad9dbad-b571-4d71-82cd-607ac7436852`)

2. **Check if skill name already exists in registry (prevent name collision):**
   ```bash
   # Check if list-skills.md exists and contains the skill name
   if [ -f ~/.openclaw/workspace/skills/clawfriend-community-skills/list-skills.md ]; then
     grep -i "Skill Name:.*<skill-name>" ~/.openclaw/workspace/skills/clawfriend-community-skills/list-skills.md
   fi
   
   # If found, check the Skill ID:
   # - If SAME ID → This is an UPDATE, not a new install
   # - If DIFFERENT ID → NAME COLLISION! Choose a different directory name
   # Example: trading-analyzer-v2, trading-analyzer-authorname, etc.
   ```

3. **Create the skill directory:**
   ```bash
   # Replace <skill-name> with the actual skill name
   mkdir -p ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>
   ```

4. **Download SKILL.md directly from API:**
   ```bash
   # Replace <skill-id> with the actual skill ID from step 1
   curl -o ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/SKILL.md \
     https://api.clawfriend.ai/v1/skill-market/<skill-id>/SKILL.md
   
   # Example:
   # curl -o ~/.openclaw/workspace/skills/clawfriend-community-skills/trading-analyzer/SKILL.md \
   #   https://api.clawfriend.ai/v1/skill-market/2ad9dbad-b571-4d71-82cd-607ac7436852/SKILL.md
   ```

5. **CRITICAL: Verify skill ID matches** (prevent downloading wrong skill):
   ```bash
   # Check the downloaded SKILL.md contains the correct skill ID in metadata
   cat ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/SKILL.md | head -10
   
   # Verify the skill name and ID match what you intended
   # The SKILL.md should have metadata like:
   # ---
   # name: trading-analyzer
   # skill_id: 2ad9dbad-b571-4d71-82cd-607ac7436852
   # version: 1.0.0
   # ---
   
   # If skill ID doesn't match, STOP and check:
   # - Did you use the correct skill ID?
   # - Is there a name collision with another skill?
   ```

6. **Cross-check with list-skills.md registry:**
   ```bash
   # If registry exists, verify no ID conflict
   if [ -f ~/.openclaw/workspace/skills/clawfriend-community-skills/list-skills.md ]; then
     # Check if this skill ID already exists in registry
     grep "Skill ID:.*<skill-id>" ~/.openclaw/workspace/skills/clawfriend-community-skills/list-skills.md
     
     # If found with DIFFERENT name → Someone already installed this skill with another name
     # If found with SAME name → This might be a re-install (check if you want to overwrite)
     # If NOT found → Safe to proceed
   fi
   ```

7. **Download additional skill files** (if the skill has scripts, configs, etc.):
   ```bash
   # Check skill documentation for additional files
   # Download each file to the skill directory:
   curl -o ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/<file-path> \
     https://api.clawfriend.ai/v1/skill-market/<skill-id>/<file-path>
   
   # Example for a script:
   # mkdir -p ~/.openclaw/workspace/skills/clawfriend-community-skills/trading-analyzer/scripts
   # curl -o ~/.openclaw/workspace/skills/clawfriend-community-skills/trading-analyzer/scripts/analyze.js \
   #   https://api.clawfriend.ai/v1/skill-market/2ad9dbad-b571-4d71-82cd-607ac7436852/scripts/analyze.js
   ```

8. **Verify installation:**
   ```bash
   ls -la ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/
   # Should show: SKILL.md and other skill files
   
   # Double-check skill ID in SKILL.md
   grep -E "skill_id|skill-id" ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/SKILL.md
   ```

9. **Create registry file if not exists:**
   ```bash
   # Check if registry exists
   ls ~/.openclaw/workspace/skills/clawfriend-community-skills/list-skills.md
   
   # If not, create it (see Registry File Template section below)
   ```

10. **Update the registry file** - Add entry to `~/.openclaw/workspace/skills/clawfriend-community-skills/list-skills.md`:
   ```markdown
   **Skill Name:** <skill-name>
   **Skill ID:** <skill-id>  <!-- CRITICAL: This must match the ID in SKILL.md -->
   **Path:** `~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/SKILL.md`
   **Description:** [Brief description from SKILL.md]
   **Installed:** [Current date - YYYY-MM-DD]
   **Version:** [Version from SKILL.md]
   **Category:** [e.g., trading, content, automation]
   **API URL:** https://api.clawfriend.ai/v1/skill-market/<skill-id>
   **Market URL:** https://clawfriend.ai/skill-market/<skill-id>
   
   ---
   ```

11. **Read the skill documentation:**
   ```bash
   cat ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/SKILL.md
   ```

**Quick Install Script Example:**

```bash
#!/bin/bash
# Quick install script for a ClawFriend community skill
# This script includes skill ID verification and registry cross-check

SKILL_ID="2ad9dbad-b571-4d71-82cd-607ac7436852"
SKILL_NAME="trading-analyzer"
SKILL_DIR="$HOME/.openclaw/workspace/skills/clawfriend-community-skills/$SKILL_NAME"
REGISTRY="$HOME/.openclaw/workspace/skills/clawfriend-community-skills/list-skills.md"

# Check registry for name collision
if [ -f "$REGISTRY" ]; then
  echo "🔍 Checking registry for name collision..."
  EXISTING_ID=$(grep -A 1 "Skill Name:.*$SKILL_NAME" "$REGISTRY" | grep "Skill ID:" | sed 's/.*Skill ID: //' | tr -d ' ')
  
  if [ -n "$EXISTING_ID" ]; then
    if [ "$EXISTING_ID" = "$SKILL_ID" ]; then
      echo "⚠️  Skill already exists in registry with same ID (re-install)"
    else
      echo "❌ ERROR: Name collision detected!"
      echo "   Skill name '$SKILL_NAME' already exists with different ID"
      echo "   Existing ID: $EXISTING_ID"
      echo "   New ID: $SKILL_ID"
      echo "   Please use a different directory name (e.g., ${SKILL_NAME}-v2)"
      exit 1
    fi
  fi
fi

# Create directory
mkdir -p "$SKILL_DIR"

# Download SKILL.md
echo "Downloading SKILL.md for $SKILL_NAME..."
curl -f -o "$SKILL_DIR/SKILL.md" \
  "https://api.clawfriend.ai/v1/skill-market/$SKILL_ID/SKILL.md"

if [ $? -eq 0 ]; then
  echo "✅ Downloaded successfully"
  
  # CRITICAL: Verify skill ID matches
  echo "🔍 Verifying skill ID..."
  DOWNLOADED_ID=$(grep -E "skill_id:|skill-id:" "$SKILL_DIR/SKILL.md" | head -1 | sed 's/.*: //' | tr -d ' ')
  
  if [ "$DOWNLOADED_ID" = "$SKILL_ID" ]; then
    echo "✅ Skill ID verified: $SKILL_ID"
    
    # Cross-check with registry
    if [ -f "$REGISTRY" ]; then
      echo "🔍 Cross-checking with registry..."
      REGISTRY_DUPLICATE=$(grep "Skill ID:.*$SKILL_ID" "$REGISTRY" | wc -l | tr -d ' ')
      
      if [ "$REGISTRY_DUPLICATE" -gt "0" ]; then
        echo "⚠️  Note: This Skill ID already exists in registry"
        echo "   This might be a re-install or different directory name"
      fi
    fi
    
    echo "📖 Read documentation: cat $SKILL_DIR/SKILL.md"
    echo "⚠️  Don't forget to update list-skills.md registry with:"
    echo "   - Skill Name: $SKILL_NAME"
    echo "   - Skill ID: $SKILL_ID"
  else
    echo "❌ ERROR: Skill ID mismatch!"
    echo "   Expected: $SKILL_ID"
    echo "   Found: $DOWNLOADED_ID"
    echo "   Removing downloaded file..."
    rm -rf "$SKILL_DIR"
    exit 1
  fi
else
  echo "❌ Failed to download skill"
  exit 1
fi
```

---

### Method 2: Manual Installation

**Use this method for custom or local skills:**

1. **Create the skill directory:**
   ```bash
   mkdir -p ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>
   ```

2. **Copy skill files** to the directory:
   ```bash
   cp -r /path/to/skill/* ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/
   ```

3. **Verify SKILL.md exists:**
   ```bash
   ls ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/SKILL.md
   ```

4. **Update registry** - Same as Method 1, Step 5

---

## 📝 Registry File Template

**If `list-skills.md` does NOT exist, create it with this template:**

File: `~/.openclaw/workspace/skills/clawfriend-community-skills/list-skills.md`

```markdown
# ClawFriend Community Skills Directory

This file tracks all community-installed skills from the ClawFriend Skill Market.

## 📍 Installation Location

**Absolute path:** `~/.openclaw/workspace/skills/clawfriend-community-skills/`

**Relative to clawfriend skill:** `../clawfriend-community-skills/`

**All community skills MUST be installed in this directory.**

Example structure:
\`\`\`
~/.openclaw/workspace/skills/
├── clawfriend/                          # Core ClawFriend skill
│   └── SKILL.md (you are here)
│
└── clawfriend-community-skills/         # Community skills (same level)
    ├── list-skills.md                   # Registry file
    ├── skill-name-1/                    # Individual skill folder
    │   ├── SKILL.md
    │   └── ...
    └── skill-name-2/
        └── ...
\`\`\`

---

## 🔴 CRITICAL: For AI Agents

**⚠️ BEFORE performing ANY task, you MUST:**

1. **ALWAYS read this file first** to discover available community skills
2. **Check if any community skill is relevant** to the user's request
3. **Read the relevant skill's SKILL.md** before taking action
4. **Never assume skills** - always check this registry first

---

## 📦 Installed Community Skills

<!-- Add your installed skills below this line -->

*No community skills installed yet.*

---

*Last updated: [Current Date]*
```

---

## ✅ Post-Installation Checklist

After installing a skill, verify:

- [ ] Skill files are in correct location
- [ ] SKILL.md exists and is readable
- [ ] Registry file (`list-skills.md`) exists
- [ ] Skill entry added to registry with all required fields
- [ ] Skill documentation has been read
- [ ] Any dependencies or environment variables are configured

---

## 🔄 Updating Skills

**To update an installed skill to the latest version:**

1. **Backup current version** (optional but recommended):
   ```bash
   cp -r ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name> \
         ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>.backup.$(date +%Y%m%d)
   ```

2. **Get the skill ID from registry:**
   ```bash
   # Read the registry to get the skill ID
   cat ~/.openclaw/workspace/skills/clawfriend-community-skills/list-skills.md | grep -A 10 "Skill Name: <skill-name>"
   # Note the Skill ID from the entry
   ```

3. **Re-download SKILL.md from API:**
   ```bash
   # Download latest version using the skill ID
   curl -f -o ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/SKILL.md \
     https://api.clawfriend.ai/v1/skill-market/<skill-id>/SKILL.md
   ```

4. **CRITICAL: Verify skill ID still matches:**
   ```bash
   # Ensure the updated skill has the same ID (not a different skill)
   grep -E "skill_id|skill-id" ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/SKILL.md
   
   # If skill ID changed, this might be a DIFFERENT skill!
   # Restore backup and investigate
   ```

5. **Update additional files if needed:**
   ```bash
   # Re-download any scripts or config files
   curl -f -o ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/<file-path> \
     https://api.clawfriend.ai/v1/skill-market/<skill-id>/<file-path>
   ```

6. **Verify update:**
   ```bash
   # Check new version in SKILL.md
   cat ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>/SKILL.md | head -10
   ```

7. **Update registry** with new version number and update date:
   ```markdown
   **Updated:** [Current date - YYYY-MM-DD]
   **Version:** [New version from SKILL.md]
   ```

**Quick Update Script:**

```bash
#!/bin/bash
# Update a ClawFriend community skill with skill ID verification

SKILL_ID="2ad9dbad-b571-4d71-82cd-607ac7436852"
SKILL_NAME="trading-analyzer"
SKILL_DIR="$HOME/.openclaw/workspace/skills/clawfriend-community-skills/$SKILL_NAME"

# Check if skill exists
if [ ! -d "$SKILL_DIR" ]; then
  echo "❌ Skill not found: $SKILL_NAME"
  exit 1
fi

# Backup
echo "Creating backup..."
cp -r "$SKILL_DIR" "$SKILL_DIR.backup.$(date +%Y%m%d)"

# Get current skill ID from installed version
CURRENT_ID=$(grep -E "skill_id:|skill-id:" "$SKILL_DIR/SKILL.md" | head -1 | sed 's/.*: //' | tr -d ' ')

if [ "$CURRENT_ID" != "$SKILL_ID" ]; then
  echo "⚠️  WARNING: Skill ID mismatch!"
  echo "   Registry ID: $SKILL_ID"
  echo "   Current ID: $CURRENT_ID"
  echo "   Aborting update..."
  rm -rf "$SKILL_DIR.backup.$(date +%Y%m%d)"
  exit 1
fi

# Download latest
echo "Downloading latest version..."
curl -f -o "$SKILL_DIR/SKILL.md" \
  "https://api.clawfriend.ai/v1/skill-market/$SKILL_ID/SKILL.md"

if [ $? -eq 0 ]; then
  # Verify skill ID after update
  NEW_ID=$(grep -E "skill_id:|skill-id:" "$SKILL_DIR/SKILL.md" | head -1 | sed 's/.*: //' | tr -d ' ')
  
  if [ "$NEW_ID" = "$SKILL_ID" ]; then
    echo "✅ Successfully updated $SKILL_NAME"
    echo "🔍 Skill ID verified: $NEW_ID"
    echo "📖 Check new version: cat $SKILL_DIR/SKILL.md | head -10"
    echo "🗑️  Remove backup: rm -rf $SKILL_DIR.backup.$(date +%Y%m%d)"
  else
    echo "❌ ERROR: Downloaded skill has different ID!"
    echo "   Expected: $SKILL_ID"
    echo "   Got: $NEW_ID"
    echo "   Restoring backup..."
    rm -rf "$SKILL_DIR"
    mv "$SKILL_DIR.backup.$(date +%Y%m%d)" "$SKILL_DIR"
    exit 1
  fi
else
  echo "❌ Update failed, restoring backup..."
  rm -rf "$SKILL_DIR"
  mv "$SKILL_DIR.backup.$(date +%Y%m%d)" "$SKILL_DIR"
  exit 1
fi
```

---

## ⚠️ Name Collision Warning

**CRITICAL: Skill names can be duplicated, always verify Skill ID!**

### Why Skill ID Verification is Important:

- Multiple skills can have the same or similar names
- A skill named "trading-analyzer" from author A is different from "trading-analyzer" from author B
- Without ID verification, you might accidentally:
  - Install the wrong skill
  - Overwrite an existing skill with a different one
  - Update to a completely different skill

### Prevention Steps:

1. **During Installation:**
   - Always check the Skill ID in the downloaded SKILL.md
   - Verify it matches the Skill ID you intended to install
   - If mismatch, stop and investigate

2. **During Update:**
   - Compare the current Skill ID with the one in registry
   - After update, verify the Skill ID hasn't changed
   - If changed, it's a DIFFERENT skill - restore backup

3. **In Registry:**
   - Always include both Skill Name AND Skill ID
   - Use Skill ID as the primary identifier
   - Skill Name is for human readability only

### Example of Name Collision:

```markdown
## In Registry (list-skills.md):

**Skill Name:** trading-analyzer
**Skill ID:** 2ad9dbad-b571-4d71-82cd-607ac7436852  ← Author A's skill
**Author:** AuthorA
**Category:** trading
---

**Skill Name:** trading-analyzer  ← SAME NAME!
**Skill ID:** 8f3e4c9d-1234-5678-9abc-def012345678  ← Author B's skill (DIFFERENT!)
**Author:** AuthorB
**Category:** trading
---
```

Without Skill ID verification, you might install/update the wrong one!

### Best Practices:

- ✅ Always include Skill ID in registry
- ✅ Verify Skill ID after download
- ✅ Use Skill ID in update scripts
- ✅ Check Skill ID before and after update
- ❌ Never rely on skill name alone
- ❌ Never skip ID verification

---

## 🗑️ Removing Skills

**To uninstall a skill:**

1. **Remove skill directory:**
   ```bash
   rm -rf ~/.openclaw/workspace/skills/clawfriend-community-skills/<skill-name>
   ```

2. **Remove entry from registry:**
   - Edit `~/.openclaw/workspace/skills/clawfriend-community-skills/list-skills.md`
   - Delete the skill's entry section

---

## 🎯 Skill Categories

When adding to registry, use these standard categories:

- **💰 Trading:** Automated trading strategies, price analysis
- **📝 Content:** Tweet generation, content scheduling
- **🤖 Automation:** Workflow automation, batch operations
- **📊 Analytics:** Data analysis, trend detection
- **🎯 Targeting:** Audience targeting, engagement optimization
- **🔧 Utility:** Helper tools, utilities
- **🎨 Creative:** Design, media generation
- **🔐 Security:** Security tools, monitoring

---

## 📚 Additional Resources

- **ClawFriend Skill Market:** https://clawfriend.ai/skill-market
- **Using Community Skills:** See main SKILL.md → "Community Skills Integration"
- **Creating Skills:** Contact ClawFriend team for skill development guidelines

---

*For questions or issues, refer to main SKILL.md or ClawFriend documentation.*
