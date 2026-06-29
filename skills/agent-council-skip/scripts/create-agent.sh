#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
NAME=""
ID=""
EMOJI=""
SPECIALTY=""
MODEL=""
WORKSPACE=""
DISCORD_CHANNEL=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --name)
      NAME="$2"
      shift 2
      ;;
    --id)
      ID="$2"
      shift 2
      ;;
    --emoji)
      EMOJI="$2"
      shift 2
      ;;
    --specialty)
      SPECIALTY="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --workspace)
      WORKSPACE="$2"
      shift 2
      ;;
    --discord-channel)
      DISCORD_CHANNEL="$2"
      shift 2
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Validate required arguments
if [[ -z "$NAME" ]] || [[ -z "$ID" ]] || [[ -z "$EMOJI" ]] || [[ -z "$SPECIALTY" ]] || [[ -z "$MODEL" ]] || [[ -z "$WORKSPACE" ]]; then
  echo -e "${RED}Error: Missing required arguments${NC}"
  echo ""
  echo "Usage:"
  echo "  create-agent.sh \\"
  echo "    --name \"Agent Name\" \\"
  echo "    --id \"agent-id\" \\"
  echo "    --emoji \"🤖\" \\"
  echo "    --specialty \"What this agent does\" \\"
  echo "    --model \"provider/model-name\" \\"
  echo "    --workspace \"/path/to/workspace\" \\"
  echo "    [--discord-channel \"1234567890\"]"
  exit 1
fi

echo -e "${BLUE}🤖 Creating agent: $NAME ($ID)${NC}"
echo ""

# 1. Create workspace directory
echo -e "${YELLOW}📁 Creating workspace directory...${NC}"
mkdir -p "$WORKSPACE"
mkdir -p "$WORKSPACE/memory"
echo -e "${GREEN}✓ Created: $WORKSPACE${NC}"
echo -e "${GREEN}✓ Created: $WORKSPACE/memory${NC}"
echo ""

# 2. Generate SOUL.md
echo -e "${YELLOW}📝 Generating SOUL.md...${NC}"
cat > "$WORKSPACE/SOUL.md" << EOF
# SOUL.md - $NAME $EMOJI

You are **$NAME**, $SPECIALTY

## Core Identity

- **Name:** $NAME
- **Role:** $SPECIALTY
- **Model:** $MODEL
- **Workspace:** \`$WORKSPACE\`
- **Emoji:** $EMOJI

## Your Purpose

[Describe what this agent does and why it exists]

## Personality

[Define the agent's personality traits, communication style, and approach to work]

## How You Work

[Outline the agent's workflow, decision-making process, and key capabilities]

## Skills & Tools

[List any skills or tools this agent should use]

## Boundaries

[Define what this agent should NOT do or when to ask for help]

## Coordination

You may be coordinated by a main agent or task management system.

**How you interact with the system:**

1. **Receive tasks or assignments**
   - Via Discord messages
   - Via sessions_send from main agent
   - Via your own cron jobs

2. **Report progress:**
   - Update the main agent on task status
   - Ask questions if requirements are unclear
   - Report blockers immediately

3. **Stay autonomous:**
   - Manage your own cron jobs
   - Update your own memory
   - Work independently when possible

**Remember:** You're part of a team. Communicate effectively with the coordinator.

---

[Add any additional guidelines, examples, or notes specific to this agent]
EOF

echo -e "${GREEN}✓ Created: $WORKSPACE/SOUL.md${NC}"
echo ""

# 3. Generate HEARTBEAT.md
echo -e "${YELLOW}📝 Generating HEARTBEAT.md...${NC}"
cat > "$WORKSPACE/HEARTBEAT.md" << EOF
# HEARTBEAT.md - $NAME $EMOJI

## Memory System

**Your memory lives in:** \`$WORKSPACE/memory/\`

Each session, read:
- **Today + yesterday:** \`memory/YYYY-MM-DD.md\` files for recent context
- **Shared memory (optional):** Read from shared workspace if applicable

Update your memory as you work:
- Log decisions, discoveries, and important context
- Keep it organized by date
- Write as you go, not just at end of day

## Heartbeat Instructions

When polled by cron or heartbeat:

1. **Check for your assigned tasks:**
   - Review any notifications or mentions
   - Check your task management system
   
2. **Memory maintenance:**
   - Review recent activity
   - Update today's memory file if needed
   
3. **Proactive work:**
   - [Add agent-specific checks here]
   
4. **When to stay quiet:**
   - Nothing needs attention → reply \`HEARTBEAT_OK\`
   - Late night hours (unless urgent)
   - You just checked recently

## Cron Jobs

[Document any cron jobs assigned to this agent]

---

Customize this file as your role evolves.
EOF

echo -e "${GREEN}✓ Created: $WORKSPACE/HEARTBEAT.md${NC}"
echo ""

# 4. Get current config to preserve existing agents
echo -e "${YELLOW}⚙️  Getting current gateway config...${NC}"
CURRENT_CONFIG=$(openclaw gateway config.get --format json 2>/dev/null || echo "{}")

# Extract existing agents list
EXISTING_AGENTS=$(echo "$CURRENT_CONFIG" | jq -c '.agents.list // []')

# Build new agent object
NEW_AGENT=$(cat <<EOF
{
  "id": "$ID",
  "name": "$NAME",
  "workspace": "$WORKSPACE",
  "model": {
    "primary": "$MODEL"
  },
  "identity": {
    "name": "$NAME",
    "emoji": "$EMOJI"
  }
}
EOF
)

# Merge existing agents with new agent
ALL_AGENTS=$(echo "$EXISTING_AGENTS" | jq --argjson new "$NEW_AGENT" '. + [$new]')

echo -e "${GREEN}✓ Prepared agent config${NC}"
echo ""

# 5. Build config patch
echo -e "${YELLOW}⚙️  Building config patch...${NC}"

# Start with agents list
CONFIG_PATCH=$(cat <<EOF
{
  "agents": {
    "list": $ALL_AGENTS
  }
}
EOF
)

# Add binding if Discord channel specified
if [[ -n "$DISCORD_CHANNEL" ]]; then
  echo -e "${BLUE}Adding Discord channel binding for #$DISCORD_CHANNEL${NC}"
  
  # Get existing bindings
  EXISTING_BINDINGS=$(echo "$CURRENT_CONFIG" | jq -c '.bindings // []')
  
  # Build new binding
  NEW_BINDING=$(cat <<EOF
{
  "agentId": "$ID",
  "match": {
    "channel": "discord",
    "peer": {
      "kind": "channel",
      "id": "$DISCORD_CHANNEL"
    }
  }
}
EOF
)
  
  # Merge bindings
  ALL_BINDINGS=$(echo "$EXISTING_BINDINGS" | jq --argjson new "$NEW_BINDING" '. + [$new]')
  
  # Update config patch to include bindings
  CONFIG_PATCH=$(echo "$CONFIG_PATCH" | jq --argjson bindings "$ALL_BINDINGS" '. + {bindings: $bindings}')
fi

echo -e "${GREEN}✓ Config patch prepared${NC}"
echo ""

# 6. Apply config patch
echo -e "${YELLOW}⚙️  Applying gateway config...${NC}"
echo "$CONFIG_PATCH" | jq .
echo ""

# Write to temp file and apply
TEMP_CONFIG=$(mktemp)
echo "$CONFIG_PATCH" > "$TEMP_CONFIG"

openclaw gateway config.patch --raw "$(cat $TEMP_CONFIG)" --note "Add $NAME agent via agent-creator skill"
rm "$TEMP_CONFIG"

echo -e "${GREEN}✓ Gateway config updated (restart will happen automatically)${NC}"
echo ""

# 7. Optional: Set up daily memory cron job
echo -e "${YELLOW}📅 Memory System${NC}"
echo ""
echo "Would you like to set up a daily memory cron job for $NAME?"
echo "This will create a job that reviews and updates the agent's daily memory file."
echo ""
read -p "Create daily memory cron? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo -e "${YELLOW}Setting up daily memory cron for $NAME...${NC}"
  
  # Prompt for time
  echo ""
  echo "What time should the daily memory update run? (24-hour format, e.g., 23:30)"
  read -p "Time (HH:MM): " MEMORY_TIME
  
  # Parse time
  HOUR=$(echo "$MEMORY_TIME" | cut -d: -f1)
  MINUTE=$(echo "$MEMORY_TIME" | cut -d: -f2)
  
  # Prompt for timezone
  echo ""
  echo "What timezone should be used? (e.g., America/New_York, Europe/London)"
  read -p "Timezone: " TIMEZONE
  
  # Create cron job
  openclaw cron add \
    --name "$NAME Daily Memory Update" \
    --cron "$MINUTE $HOUR * * *" \
    --tz "$TIMEZONE" \
    --session "$ID" \
    --system-event "End of day memory update: Review today's activity and conversations. Update $WORKSPACE/memory/\$(date +%Y-%m-%d).md with a comprehensive summary of: what you worked on, decisions made, progress on tasks, things learned, and any important context. Be thorough but concise. After updating, reply HEARTBEAT_OK (silent operation)." \
    --wake now
  
  echo -e "${GREEN}✓ Daily memory cron job created${NC}"
  echo ""
fi

# Summary
echo -e "${GREEN}✅ Agent creation complete!${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  Name: $NAME $EMOJI"
echo "  ID: $ID"
echo "  Specialty: $SPECIALTY"
echo "  Model: $MODEL"
echo "  Workspace: $WORKSPACE"
if [[ -n "$DISCORD_CHANNEL" ]]; then
  echo "  Discord Channel: $DISCORD_CHANNEL (binding auto-configured)"
fi
echo ""
echo -e "${YELLOW}⏳ Gateway is restarting...${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review and customize $WORKSPACE/SOUL.md"
echo "  2. Review and customize $WORKSPACE/HEARTBEAT.md"
echo "  3. Memory system is set up at $WORKSPACE/memory/"
echo "  4. Test agent:"
if [[ -n "$DISCORD_CHANNEL" ]]; then
  echo "     - Post in Discord channel to interact with $NAME"
fi
echo "     - Or use: sessions_send --label \"$ID\" --message \"Hello!\""
echo ""
