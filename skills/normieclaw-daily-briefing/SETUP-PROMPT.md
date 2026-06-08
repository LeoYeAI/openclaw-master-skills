# Supercharged Daily Briefing — Setup Prompt

Copy and paste this entire block into your agent's chat to install the skill.

---

**Paste this:**

> I just installed the Supercharged Daily Briefing skill. Please set it up for me by running these steps:
>
> **Step 1: Create directories**
> ```
> mkdir -p data/briefing-archive config scripts
> chmod 700 data data/briefing-archive config scripts
> ```
>
> **Step 2: Copy skill files to workspace**
> Find the skill package directory (it contains a file named SKILL.md with the text "Supercharged Daily Briefing") and copy the required files:
> ```
> # Find and validate the skill package location
> SKILL_DIR=""
> MATCH_COUNT=0
> while IFS= read -r skill_file; do
>   candidate_dir="$(dirname "$skill_file")"
>   if grep -q "Skill: Supercharged Daily Briefing" "$skill_file" && \
>      [ -f "$candidate_dir/config/briefing-config.json" ] && \
>      [ -f "$candidate_dir/scripts/briefing-scheduler.sh" ]; then
>     MATCH_COUNT=$((MATCH_COUNT + 1))
>     SKILL_DIR="$candidate_dir"
>   fi
> done < <(find . -type f -path "*/skills/daily-briefing/SKILL.md" 2>/dev/null)
>
> if [ "$MATCH_COUNT" -eq 0 ]; then
>   echo "ERROR: Could not locate a valid Supercharged Daily Briefing skill package." >&2
>   exit 1
> fi
>
> if [ "$MATCH_COUNT" -gt 1 ]; then
>   echo "ERROR: Found multiple matching skill packages. Remove duplicates and rerun setup." >&2
>   exit 1
> fi
>
> # Copy config (don't overwrite existing)
> [ ! -f config/briefing-config.json ] && cp "$SKILL_DIR/config/briefing-config.json" config/briefing-config.json
>
> # Copy script
> cp "$SKILL_DIR/scripts/briefing-scheduler.sh" scripts/briefing-scheduler.sh
> chmod 700 scripts/briefing-scheduler.sh
>
> # Copy SKILL.md to skills directory for agent reference
> mkdir -p skills/daily-briefing
> cp "$SKILL_DIR/SKILL.md" skills/daily-briefing/SKILL.md
> ```
>
> **Step 3: Initialize data files**
> Create empty data files if they don't exist:
> ```
> [ ! -f data/briefing-sources.json ] && echo '{"sources":[],"banned_domains":[]}' > data/briefing-sources.json
> [ ! -f data/briefing-feedback.json ] && echo '[]' > data/briefing-feedback.json
> chmod 600 data/briefing-sources.json data/briefing-feedback.json config/briefing-config.json
> ```
>
> **Step 4: Verify installation**
> Confirm these files exist and are readable:
> - `skills/daily-briefing/SKILL.md`
> - `config/briefing-config.json`
> - `scripts/briefing-scheduler.sh`
> - `data/briefing-sources.json`
> - `data/briefing-feedback.json`
>
> List them with `ls -la` for each path and confirm everything is in place.
>
> **Step 5: Walk me through setup**
> Now ask me:
> 1. What 2-3 topics or industries I want you to monitor
> 2. What time I want my briefing delivered each morning
> 3. Which days of the week (default: every day)
>
> Then discover sources for my topics and show me what you found.

---

## What This Does

- Creates `data/`, `config/`, and `scripts/` directories at your workspace root
- Copies the skill configuration and scheduler script into place
- Initializes empty data files for sources and feedback tracking
- Sets secure permissions (700 for directories, 600 for sensitive files)
- Walks you through choosing your topics, schedule, and source preferences

## After Setup

Your agent will:
- Discover high-quality sources for your chosen topics
- Deliver a personalized morning briefing at your chosen time
- Learn from your feedback to improve over time
- Monitor source health and replace failing sources automatically

Just chat naturally: "run brief", "add AI to my topics", "show my sources", "change briefing time to 8 AM".
