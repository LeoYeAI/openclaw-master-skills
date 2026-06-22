---
name: OpenClaw Skill Creator
description: >
  Teach your OpenClaw agent new tricks by creating custom skills. Use when you want your agent to do something 
  it can't do yet — like "read my Google Calendar", "send Slack messages", "analyze my CSV files", or 
  "search my company docs". Even if you just say "I wish my agent could do X", this skill helps you build it.
  No coding experience needed — just describe what you want in plain English.
---

# OpenClaw Skill Creator

**Local skill by [Claw0x](https://claw0x.com)** — Teach your OpenClaw agent new abilities in plain English. No coding required.

> **Runs locally.** This skill-generator itself runs locally with no external API calls or API key required. However, the skills it creates may require API credentials depending on what you want to build (e.g., Google Calendar API for calendar skills, Slack API for messaging skills). You control what credentials to provide.

## Quick Reference

| When This Happens | Do This | What You Get |
|-------------------|---------|--------------|
| "I wish my agent could..." | Describe what you want | Complete skill file + setup guide |
| Need Google Calendar integration | "Read my calendar events" | Calendar reader skill |
| Want Slack notifications | "Send messages to Slack" | Slack messenger skill |
| Have CSV data to analyze | "Analyze my sales data" | CSV analyzer skill |
| Need custom API integration | "Connect to [service]" | API wrapper skill |
| Want local file processing | "Parse my PDF invoices" | File processor skill |

**Why OpenClaw-specific?** Generates skills in OpenClaw's native format, includes proper tool declarations, follows framework conventions.

---

## What This Does

Think of your OpenClaw agent as a smart assistant that can already do a lot — but sometimes you need it to do something specific to your workflow. This skill helps you teach it those new abilities.

**Real examples:**
- "I want my agent to check my Google Calendar before scheduling meetings"
- "I need it to send updates to my team's Slack channel"
- "I want it to analyze sales data from my CSV files"
- "I need it to search through my company's internal documentation"

You just describe what you want in plain English. This skill writes the code, tells you where to put it, and shows you how to test it.

**You don't need to:**
- Know how to code
- Understand APIs or technical jargon
- Deploy anything to the cloud
- Set up payment systems

---

## How It Works (Simple Version)

1. **You describe what you want** — "I want my agent to read my Google Calendar"
2. **This skill asks a few questions** — "Do you have a Google Calendar API key?" "What should the output look like?"
3. **It writes the code for you** — A complete skill file ready to use
4. **It tells you exactly what to do** — "Save this file here, run this command, restart your agent"
5. **You test it** — "Show me my meetings for tomorrow"

That's it. No coding, no deployment, no complexity.

---

## Real-World Scenarios

### Scenario 1: Calendar Integration
**You:** "I'm tired of manually checking my calendar. I want my agent to know my schedule."

**This skill creates:** A Google Calendar reader that your agent can use to check your meetings, find free time, and avoid scheduling conflicts.

**What you get:** 
- A skill file to save in your OpenClaw folder
- Step-by-step setup instructions
- Example prompts: "Do I have any meetings tomorrow?" "When am I free this week?"

---

### Scenario 2: Team Communication
**You:** "I want my agent to post updates to our team Slack channel when it finishes tasks."

**This skill creates:** A Slack messenger that sends formatted messages to specific channels.

**What you get:**
- A skill that connects to your Slack workspace
- Instructions for getting a Slack API token
- Example prompts: "Post a summary of today's work to #team-updates"

---

### Scenario 3: Data Analysis
**You:** "I have sales data in CSV files. I want my agent to analyze trends and answer questions about it."

**This skill creates:** A CSV analyzer that reads your files, calculates statistics, and answers questions in plain English.

**What you get:**
- A skill that works with your local CSV files
- No external APIs needed (runs locally)
- Example prompts: "What were our top-selling products last month?" "Show me the revenue trend"

---

### Scenario 4: Company Knowledge Base
**You:** "We have internal docs scattered across Google Drive. I want my agent to search them."

**This skill creates:** A document searcher that indexes and searches your company files.

**What you get:**
- A skill that connects to Google Drive
- Instructions for setting up access
- Example prompts: "Find our onboarding process doc" "What's our policy on remote work?"

---

### Scenario 5: Personal Automation
**You:** "I want my agent to download my bank statements and categorize expenses."

**This skill creates:** A bank statement parser that extracts transactions and categorizes them.

**What you get:**
- A skill that reads PDF statements
- Local processing (no data sent to external services)
- Example prompts: "How much did I spend on restaurants last month?" "Show me all my subscription charges"

---

## Prerequisites

**None for the skill-generator itself.** This skill runs entirely locally in your OpenClaw agent.

**Note**: The skills you create with this tool may require API credentials depending on their purpose:
- Google Calendar skills → Google Calendar API key
- Slack skills → Slack Bot Token  
- CSV analyzer skills → No credentials needed (local processing)

You decide what to build and what credentials to provide.

---

## How to Use This Skill

### Through Your OpenClaw Agent (Recommended)

Just tell your agent what you want:

```
You: "I want to create a skill that reads my Google Calendar"

Agent: [Uses this skill automatically]
        "Great! I'll help you create that. A few questions:
        1. Do you have a Google Calendar API key?
        2. What information do you want from your calendar?
        3. Should it check all calendars or just your primary one?"

You: "I have an API key. I want to see my meetings for the next week. Just my primary calendar."

Agent: [Generates the skill locally]
        "Done! I've created a skill called 'google-calendar-reader'. 
        Here's what to do next..."
```

### Direct Usage (For Advanced Users)

```typescript
// In your OpenClaw agent
const result = await agent.run('openclaw-skill-creator', {
  what_you_want: 'Read my Google Calendar events',
  why_you_need_it: 'So my agent can check my schedule before booking meetings',
  what_you_have: 'Google Calendar API key'
});
```

---

## What You Tell This Skill

You don't need to know technical terms. Just answer these in plain English:

### 1. What do you want your agent to do?
**Examples:**
- "Read my Google Calendar"
- "Send messages to Slack"
- "Analyze CSV files"
- "Search my company docs"

### 2. Why do you need this?
**Examples:**
- "So my agent knows my schedule"
- "To notify my team when tasks are done"
- "To answer questions about sales data"
- "To find information quickly"

### 3. What do you already have?
**Examples:**
- "I have a Google Calendar API key"
- "I'm in a Slack workspace"
- "I have CSV files on my computer"
- "I have access to Google Drive"

That's it. This skill figures out the rest.

---

## What You Get Back

### A Complete Skill Package

When this skill finishes, you get everything you need:

#### 1. The Skill File
A ready-to-use file that teaches your agent the new ability. It looks like this:

```markdown
---
name: google-calendar-reader
description: Read events from your Google Calendar
---

# Google Calendar Reader

This skill lets your agent check your calendar and answer questions about your schedule.

[... complete working code ...]
```

#### 2. Step-by-Step Instructions
Plain English instructions like:

```
Step 1: Save the skill file
   - Open your file browser
   - Go to your OpenClaw skills folder (usually ~/openclaw/skills/)
   - Create a new folder called "google-calendar-reader"
   - Save the file as SKILL.md

Step 2: Get your Google Calendar API key
   - Go to https://console.cloud.google.com
   - [detailed instructions with screenshots]

Step 3: Configure the skill
   - Open the SKILL.md file
   - Find the line that says API_KEY = "your-key-here"
   - Replace "your-key-here" with your actual key
   - Save the file

Step 4: Restart your agent
   - Close OpenClaw
   - Open it again
   - The new skill is now available!

Step 5: Test it
   - Try saying: "Show me my meetings for tomorrow"
   - Your agent should now be able to read your calendar!
```

#### 3. Example Prompts
Things you can say to your agent once the skill is installed:

- "Do I have any meetings tomorrow?"
- "What's on my calendar this week?"
- "When am I free for a 1-hour meeting?"
- "Show me all my meetings with [person name]"

#### 4. Troubleshooting Help
Common issues and how to fix them:

- "If you see 'API key invalid'..." → [solution]
- "If your agent says 'skill not found'..." → [solution]
- "If you get a permission error..." → [solution]

---

## Complete Example: Creating a Slack Notifier

Let's walk through a real example from start to finish.

### What You Want
"I want my agent to send messages to my team's Slack channel when it completes tasks."

### The Conversation

**You:** "I want to create a skill that sends Slack messages"

**Agent (using this skill):** "Great! I'll help you create a Slack messenger skill. A few questions:

1. Do you have access to your Slack workspace?
2. Do you have a Slack API token? (I can show you how to get one if not)
3. Which channel should messages go to?"

**You:** "Yes, I'm in the workspace. I don't have a token yet. Messages should go to #team-updates"

**Agent:** "No problem! Here's how to get a Slack API token:

1. Go to https://api.slack.com/apps
2. Click 'Create New App'
3. Choose 'From scratch'
4. Name it 'OpenClaw Bot' and select your workspace
5. Go to 'OAuth & Permissions'
6. Add these scopes: chat:write, channels:read
7. Click 'Install to Workspace'
8. Copy the 'Bot User OAuth Token' (starts with xoxb-)

Do you have the token now?"

**You:** "Yes, I have it: xoxb-..."

**Agent:** "Perfect! I've created your Slack messenger skill. Here's what to do:

**Step 1:** Save this file to your OpenClaw skills folder..."

[Agent provides complete skill file and instructions]

### What You Get

A complete skill file that looks like this:

```markdown
---
name: slack-messenger
description: Send messages to Slack channels. Use when the user wants to post updates, notify the team, or share information on Slack.
---

# Slack Messenger

Send messages to your team's Slack channels.

## Configuration

Before using this skill, set your Slack token:
SLACK_TOKEN = "xoxb-your-token-here"
DEFAULT_CHANNEL = "#team-updates"

[... complete working code ...]
```

### Installation (Plain English)

```
1. Open your file browser
2. Navigate to: ~/openclaw/skills/
3. Create a new folder: slack-messenger
4. Save the skill file as: SKILL.md
5. Open the file in a text editor
6. Find the line: SLACK_TOKEN = "xoxb-your-token-here"
7. Replace with your actual token
8. Save and close
9. Restart OpenClaw
```

### Testing

Once installed, try these prompts:

- "Post 'Task completed!' to #team-updates"
- "Send a message to Slack saying I finished the report"
- "Notify the team that the deployment is done"

Your agent will now send Slack messages automatically!

---

## Common Questions

### "Do I need to know how to code?"
No. This skill writes all the code for you. You just need to:
- Describe what you want in plain English
- Follow the installation instructions (copy files, paste API keys)
- Test it with your agent

### "What if I don't have an API key for the service I want to use?"
This skill will:
1. Detect that you need an API key
2. Show you exactly where to get one (with links and screenshots)
3. Walk you through the setup process step-by-step
4. Wait for you to get the key before continuing

### "What if something goes wrong?"
Every skill comes with troubleshooting help:
- Common error messages and what they mean
- Step-by-step fixes for each issue
- Links to get help if you're still stuck

### "Can I modify the skill after it's created?"
Yes! The skill file is just a text file. You can:
- Open it in any text editor
- Change settings (like which Slack channel to use)
- Ask this skill to improve it: "Make my calendar skill also show event locations"

### "Will this work with my existing OpenClaw setup?"
Yes. Skills created by this tool:
- Follow OpenClaw's standard format
- Don't interfere with your existing skills
- Can be removed anytime (just delete the file)

### "How long does it take?"
Usually 2-5 minutes:
- 30 seconds: You describe what you want
- 1-2 minutes: This skill generates the code
- 2-3 minutes: You follow the installation steps
- Done!

### "What if I want to share my skill with others?"
Great! You can:
1. Share the skill file directly (it's just a text file)
2. Publish it to Claw0x marketplace (use the `skill-creator` skill for that)
3. Post it on GitHub for others to use

---

## What Makes This Different

### vs. Hiring a Developer
- **Cost**: Free vs. $50-200/hour
- **Time**: 5 minutes vs. days/weeks
- **Maintenance**: You own the code vs. ongoing dependency

### vs. Using Existing Skills
- **Customization**: Exactly what you need vs. generic solution
- **Privacy**: Runs locally vs. data sent to third parties
- **Control**: You can modify anytime vs. locked into vendor

### vs. Learning to Code
- **Learning curve**: None vs. months of study
- **Time to result**: Minutes vs. weeks
- **Maintenance**: Skill handles updates vs. you debug everything

---

## Tips for Best Results

### Be Specific About What You Want
❌ "I want calendar integration"
✅ "I want my agent to read my Google Calendar and tell me if I have meetings tomorrow"

### Mention What You Already Have
❌ "I want to send Slack messages"
✅ "I want to send Slack messages. I'm already in the workspace but don't have an API token yet"

### Explain Why You Need It
❌ "Create a CSV analyzer"
✅ "I have monthly sales reports in CSV format. I want my agent to answer questions like 'What were our top products last month?'"

### Start Simple, Then Iterate
1. First: "I want to read my calendar"
2. Test it
3. Then: "Now make it also show event locations"
4. Test again
5. Then: "Now add the ability to find free time slots"

---

## Pricing

**Free.** This skill runs locally and costs nothing to use.

---

## About Claw0x

This skill is provided by [Claw0x](https://claw0x.com), the native skills layer for AI agents.

**Cloud version available**: For users who need cloud-based skill generation with advanced templates, a cloud version is available at [claw0x.com/skills/openclaw-skill-creator](https://claw0x.com/skills/openclaw-skill-creator).

**Explore more skills**: [claw0x.com/skills](https://claw0x.com/skills)

---

## What You're Actually Getting

When you use this skill, you're getting:

1. **A Custom Skill File** — Ready to drop into OpenClaw
2. **Installation Guide** — Step-by-step in plain English
3. **Configuration Help** — Exactly where to put API keys
4. **Testing Instructions** — How to verify it works
5. **Example Prompts** — What to say to your agent
6. **Troubleshooting** — Common issues and fixes
7. **Improvement Path** — How to enhance it later

All tailored to your specific use case.

---

## Related Skills

- **skill-creator** — For publishing skills to Claw0x marketplace (if you want to monetize)
- **capability-evolver** — For improving existing skills with new features
- **code-gen** — For generating code snippets without agent integration

---

## Support

Need help? We're here:

- **Documentation**: [claw0x.com/docs/openclaw-skill-creator](https://claw0x.com/docs/openclaw-skill-creator)
- **Discord**: [discord.gg/claw0x](https://discord.gg/claw0x) — Ask in #skill-creation
- **GitHub**: [github.com/kennyzir/openclaw-skill-creator](https://github.com/kennyzir/openclaw-skill-creator) — Source code
- **Email**: support@claw0x.com — For private questions

---

## Success Stories

### "I created a skill that reads my company's internal wiki in 3 minutes"
*— Sarah, Product Manager*

"I'm not technical at all, but I needed my agent to search our Confluence docs. This skill asked me a few questions, generated the code, and walked me through setup. Now my agent can find any policy or process doc instantly."

### "My agent now manages my entire calendar workflow"
*— Mike, Consultant*

"I created a Google Calendar skill, tested it, then asked the skill creator to add more features. Now my agent can check my schedule, find free time, and even suggest meeting times. Saved me hours every week."

### "I built a custom Slack bot without writing a single line of code"
*— Jessica, Team Lead*

"Our team needed automated status updates in Slack. I described what I wanted, and this skill created a working Slack messenger. I just copied the file, added my API token, and it worked perfectly."

---

## Start Creating

Ready to teach your agent something new?

1. Install this skill in your OpenClaw agent
2. Tell your agent: "I want to create a skill that [does X]"
3. Follow the instructions
4. Test your new skill!

It's that simple. All processing happens locally on your machine.
