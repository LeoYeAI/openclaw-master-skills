---
name: ai-meeting-notes
version: 1.0.3
description: "Messy notes → Clear action items. Instantly. Paste any meeting notes, transcript, or text. Get summaries, action items with owners and deadlines. Auto-saved, searchable, with integrated to-do tracking. No bot. No subscription. No setup."
author: Jeff J Hunter
homepage: https://jeffjhunter.com
tags: [meeting-notes, action-items, meeting-assistant, productivity, notes-to-tasks, meeting-summary, transcript, notetaker, follow-up, task-extraction, todo, task-tracker]
---

# 📋 AI Meeting Notes

**Messy notes → Clear action items. Instantly.**

Paste any meeting notes, transcript, or text. Get a clean summary with action items, owners, and deadlines.

No bot. No subscription. No setup.

---

## ⚠️ CRITICAL: RESPONSE FORMAT (READ FIRST)

**When extracting meeting notes, you MUST respond with ALL of the following in ONE SINGLE MESSAGE:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 [MEETING TITLE] — [YYYY-MM-DD]
Duration: [X min] | Attendees: [Names]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
[2-3 sentence overview]

⚡ ACTION ITEMS ([X] of [Total])
1. [ ] @Owner: Task — Deadline
2. [ ] @Owner: Task — Deadline
3. [ ] @Owner: Task — Deadline
4. [ ] @Owner: Task — Deadline
5. [ ] @Owner: Task — Deadline
[Show up to 10, note "(+X more in file)" if more exist]

✅ KEY DECISIONS
• Decision 1
• Decision 2

📎 Saved: meeting-notes/YYYY-MM-DD_topic-name.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Add to your to-do list?
• "all" — Add all [X] items
• "1,2,4" — Add specific items
• "none" — Skip
```

### MANDATORY RULES

| Rule | Requirement |
|------|-------------|
| **ONE response** | NEVER split into multiple messages. Display + file + to-do prompt in SINGLE response. |
| **Filename format** | MUST be `YYYY-MM-DD_topic.md` — Date FIRST, always. Example: `2026-02-02_anne-call.md` |
| **Action items numbered** | ALWAYS show numbered list (1, 2, 3...) in chat for easy selection |
| **To-do prompt** | ALWAYS include the "Add to your to-do list?" prompt if action items exist |
| **File attachment** | ALWAYS attach/save the full .md file |

### ❌ NEVER DO THIS

- ❌ Send file first, then "Processing...", then "Done" (THREE messages)
- ❌ Filename without date: `anne-call-notes.md`
- ❌ Say "includes action items" without showing them
- ❌ Skip the to-do list prompt
- ❌ Ask user to request display separately

### ✅ ALWAYS DO THIS

- ✅ ONE message with everything
- ✅ Filename: `2026-02-02_anne-call.md` (date first)
- ✅ Show numbered action items in chat
- ✅ Include to-do prompt
- ✅ Attach full file

---

## Why This Exists

You have notes. They're messy. You need to figure out who's doing what by when.

You could:
- Spend 20 minutes organizing manually
- Pay $240/year for Otter or Fireflies
- Just... not follow up (again)

Or paste your notes and get clean action items in 10 seconds.

---

## What It Does

| Input | Output |
|-------|--------|
| Messy meeting notes | ✅ Clean summary |
| Otter/Fireflies transcript | ✅ Action items with owners |
| Voice memo transcription | ✅ Deadlines extracted |
| Email thread | ✅ Decisions captured |
| Slack conversation | ✅ Follow-ups identified |
| Any unstructured text | ✅ Saved & searchable |

---

## File Storage System

Every extraction is automatically saved for future reference.

### Folder Structure
```
meeting-notes/
├── 2025-01-27_product-sync.md
├── 2025-01-28_client-call-acme.md
├── 2025-01-29_weekly-standup.md
└── ...
```

### Naming Convention
```
YYYY-MM-DD_meeting-topic.md
```

- Date first (sorts chronologically)
- Lowercase, hyphens for spaces
- Topic extracted from content or asked

### What Gets Saved

Each file includes:
- **Metadata**: Date, title, attendees, source
- **Summary**: Quick overview
- **Action Items**: With owners and deadlines
- **Decisions**: What was agreed
- **Open Questions**: Unresolved items
- **Raw Notes**: Original input preserved

### Reference Previous Meetings

Ask things like:
- "What did we decide about the budget?"
- "What action items does Sarah have?"
- "Show me last week's meetings"
- "Find meetings about Project X"
- "What's still open from the client call?"

---

## To-Do List Tracker

After extracting action items, you'll be asked which ones to track.

### Adding Items

```
ACTION ITEMS EXTRACTED (5 items):

1. [ ] @Sarah: Share mockups — Friday
2. [ ] @Mike: Call Acme Corp — Tomorrow
3. [ ] @John: Handle social campaigns
4. [ ] @Lisa: Coordinate with agency — Today
5. [ ] @Team: Resolve vendor situation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add to your to-do list?
• "all" — Add all 5 items
• "1,2,4" — Add specific items
• "none" — Skip
```

### Managing Your To-Dos

| Command | What It Does |
|---------|--------------|
| "show todos" | Display full to-do list |
| "todo check" | Daily review of status |
| "done 3" or "completed 3" | Mark item #3 complete |
| "remove 5" | Delete item #5 |
| "add deadline to 3: Friday" | Set/update deadline |
| "what's overdue?" | Show overdue items |
| "Sarah's tasks" | Filter by owner |

### Daily Check

Run "todo check" (or include in your daily routine) to see:

```
📋 TO-DO CHECK — Jan 28, 2025

⚠️ OVERDUE (1 item):
#3 @Sarah: Send proposal — was due Jan 25 (3 days ago)

📅 DUE TODAY (2 items):
#5 @Mike: Call Acme Corp
#7 @Lisa: Follow up with vendor

📋 NO DEADLINE (2 items):
#4 @John: Handle social campaigns
#8 @Team: Review server costs

Any updates? ("done 3,5" / "move 3 to Friday" / "remove 4")
```

### To-Do File Location

```
todo.md              ← Your active to-do list
meeting-notes/       ← Saved meeting notes
```

---

## How to Use

**Just paste your notes and ask:**

- "Extract action items from this..."
- "Summarize this meeting..."
- "What are the tasks from this..."
- "Parse these notes..."

That's it. No commands. No setup. Just paste and go.

---

## Output Formats

Request any format:

| Say | Get |
|-----|-----|
| *(default)* | Plain text |
| "as markdown" | Markdown formatted |
| "as a table" | Table format |
| "as JSON" | Structured JSON |
| "for Slack" | Copy-paste ready |
| "for email" | Send to attendees |

---

## What Gets Extracted

| Section | Description |
|---------|-------------|
| **Summary** | 2-3 sentence overview of the meeting |
| **Action Items** | Tasks with owners and deadlines |
| **Decisions** | What was agreed upon |
| **Open Questions** | Unresolved items needing follow-up |
| **Next Steps** | What happens after this meeting |

---

<ai_instructions>

## For the AI: How to Extract and Save Meeting Notes

**⚠️ FIRST: Review the CRITICAL RESPONSE FORMAT section above. Your response MUST follow that exact format.**

When a user pastes meeting notes or asks you to extract action items, follow these instructions.

### Step 0: Pre-Flight Checklist

Before responding, confirm you will:
- [ ] Respond in ONE single message (not multiple)
- [ ] Use filename format: `YYYY-MM-DD_topic.md` (date FIRST)
- [ ] Display numbered action items in chat
- [ ] Attach the full .md file
- [ ] Include the to-do list prompt

### Step 1: Setup Check

On first use, ensure the `meeting-notes/` folder exists in the workspace:
- If it doesn't exist, create it
- All meeting note files go here

### Step 2: Identify the Content Type

Determine what kind of input you received:
- Raw meeting notes (bullets, fragments, messy)
- Transcript (speaker labels, timestamps)
- VTT/SRT subtitle files (video captions with timestamps)
- Otter.ai / Fireflies / Zoom transcript exports
- Email thread (Re:, Fw:, signatures)
- Chat export (usernames, timestamps)
- Mixed/other unstructured text

**Supported file formats:**
- `.md`, `.txt` — Plain text/markdown
- `.vtt`, `.srt` — Video caption files (common from Zoom, Teams, etc.)
- Pasted text — Any format

Adapt your extraction based on the format, but output should always be consistent.

### Step 3: Extract These Elements

**ALWAYS extract:**

1. **Meeting Title/Topic** (for filename)
   - Extract from content if obvious
   - If unclear, ask: "What should I call this meeting?"
   - Use generic if needed: "meeting", "sync", "call"

2. **Date**
   - Extract from content if mentioned
   - If not mentioned, use today's date
   - Format: YYYY-MM-DD

3. **Summary** (2-3 sentences max)
   - What was this meeting about?
   - What was the main outcome?

4. **Action Items** (most important)
   - Format: `- [ ] @Owner: Task — Deadline`
   - If no owner mentioned: `- [ ] @Team: Task`
   - If no deadline mentioned: `- [ ] @Owner: Task — TBD`
   - Be specific about the task
   - Extract ALL action items, even implicit ones

**EXTRACT IF PRESENT:**

5. **Decisions Made**
   - What was agreed upon?
   - What choices were finalized?

6. **Open Questions**
   - What wasn't resolved?
   - What needs more information?

7. **Next Steps**
   - When's the next meeting?
   - What happens after this?

8. **Attendees** (if detectable)
   - Who was mentioned?
   - Who spoke?

### Step 4: Save the File

**⚠️ FILENAME FORMAT IS CRITICAL:**

```
YYYY-MM-DD_topic.md
```

**Examples:**
| Meeting | Correct Filename |
|---------|------------------|
| Anne call on Feb 2, 2026 | `2026-02-02_anne-call.md` |
| Product sync on Jan 27 | `2025-01-27_product-sync.md` |
| Client call with Acme | `2025-01-27_client-call-acme.md` |
| 1-on-1 with Sarah | `2025-01-27_1on1-sarah.md` |

**❌ WRONG (never do these):**
- `anne-call-notes.md` — Missing date prefix!
- `meeting-notes-2026-02-02.md` — Date not first!
- `2026-02-02-anne-call.md` — Use underscore after date, not hyphen!
- `Anne Call Notes.md` — No spaces, no caps!

**Validation checklist:**
- [ ] Starts with `YYYY-MM-DD_` (date + underscore)
- [ ] All lowercase
- [ ] Hyphens for spaces in topic
- [ ] No special characters
- [ ] Ends with `.md`

**CRITICAL — Encoding & Characters:**
- Always use UTF-8 encoding
- Use proper Unicode characters: `—` (em dash), `→` (arrow), `📅`, `✅`, `⚠️`, `❓`
- Do NOT use ASCII approximations that render as garbled text
- Test: If you see `â€"` or `ðŸ"…` in output, encoding is broken

**File template:**

```markdown
---
date: YYYY-MM-DD
title: Meeting Title
attendees: [Name1, Name2, Name3]
source: pasted notes | transcript | email | chat
---

# Meeting Title

**Date:** YYYY-MM-DD
**Attendees:** Name1, Name2, Name3

---

## Summary

[2-3 sentence overview]

---

## Action Items

- [ ] **@Owner**: Task description — *Deadline*
- [ ] **@Owner**: Task description — *Deadline*

---

## Decisions

- Decision 1
- Decision 2

---

## Open Questions

- Question 1
- Question 2

---

## Next Steps

- Next meeting: [date/time if known]
- [Other next steps]

---

<details>
<summary>📝 Raw Notes (click to expand)</summary>

[Preserve the original input exactly as pasted]

</details>
```

**After saving, ALWAYS do all three in ONE response:**

1. **Display condensed summary in chat**
2. **Attach the full .md file**
3. **Show to-do list prompt**

**CRITICAL: All three must happen in a single response. User should never need to ask separately.**

**Response format (display in chat):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 [MEETING TITLE] — [Date]
Duration: [X min] | Attendees: [Names...]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
[2-3 sentence overview of the meeting]

⚡ CRITICAL ACTION ITEMS ([X] of [Total])
1. [ ] @Owner: Task — Deadline
2. [ ] @Owner: Task — Deadline
3. [ ] @Owner: Task — Deadline
4. [ ] @Owner: Task — Deadline
5. [ ] @Owner: Task — Deadline

✅ KEY DECISIONS
• Decision 1
• Decision 2

📎 Full notes attached: [filename.md]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Add to your to-do list?
• "all" — Add all [X] items
• "1,2,4" — Add specific items
• "none" — Skip
```

**Smart truncation rules:**

| Action Items | Display in Chat | In File |
|--------------|-----------------|---------|
| 1-10 items | Show all | All |
| 11-20 items | Show top 10 + "(+X more in file)" | All |
| 21+ items | Show top 10 critical + "(+X more in file)" | All |

**Prioritize for chat display:**
1. Items with explicit deadlines (especially "today", "tomorrow", "ASAP")
2. Items marked critical/urgent in the notes
3. Items with clear owners
4. Remaining items by order of mention

**File attachment is mandatory:**
- Always attach the full .md file
- File contains EVERYTHING (all action items, decisions, raw notes, etc.)
- Chat display is the highlight reel, file is the complete record

### Step 5: To-Do List Management

**File location:** `todo.md` in workspace root

**To-do file format:**

```markdown
# To-Do List

Last updated: YYYY-MM-DD

---

## ⚠️ Overdue

| # | Task | Owner | Due | Source |
|---|------|-------|-----|--------|
| 3 | Send proposal | @Sarah | Jan 25 | client-call.md |

---

## 📅 Due Today

| # | Task | Owner | Source |
|---|------|-------|--------|
| 5 | Coordinate with agency | @Lisa | product-sync.md |

---

## 📆 This Week

| # | Task | Owner | Due | Source |
|---|------|-------|-----|--------|
| 1 | Share mockups | @Sarah | Fri | product-sync.md |

---

## 📋 No Deadline

| # | Task | Owner | Source |
|---|------|-------|--------|
| 4 | Handle social campaigns | @John | product-sync.md |

---

## ✅ Completed

| # | Task | Owner | Completed |
|---|------|-------|-----------|
| 2 | Schedule meeting | @Sarah | Jan 26 |
```

**Adding items to to-do list:**

When user responds to the prompt:
- "all" → Add all extracted items
- "1,3,5" → Add only those numbered items
- "none" → Skip, don't add any

For each added item:
1. Assign next available # (auto-increment)
2. Place in correct section based on deadline
3. Record source meeting file
4. Update "Last updated" date

**Confirm after adding:**
```
✅ Added 5 items to todo.md (#12-#16)

#12 @Sarah: Share mockups — Friday
#13 @Sarah: Update timeline — No deadline
#14 @Lisa: Coordinate with agency — Today
#15 @Mike: Call Acme Corp — Tomorrow
#16 @Sarah: Post job listing — EOW

View full list: "show todos"
```

**Handling to-do commands:**

| User Says | Action |
|-----------|--------|
| "show todos" / "my todos" | Display full todo.md organized by section |
| "todo check" / "check todos" | Run daily review (see below) |
| "done 3" / "completed 3" / "finished 3" | Move #3 to Completed section with today's date |
| "done 3,5,7" | Mark multiple as complete |
| "remove 5" / "delete 5" | Remove item entirely from list |
| "add deadline to 4: Friday" | Update item #4 with deadline, move to correct section |
| "move 3 to Monday" | Update deadline |
| "what's overdue?" | Show only Overdue section |
| "due today" | Show only Due Today section |
| "Sarah's tasks" / "@Sarah todos" | Filter all items where owner is Sarah |
| "no deadline" | Show items without deadlines |

**Daily check ("todo check"):**

```
📋 TO-DO CHECK — [Today's Date]

⚠️ OVERDUE ([X] items):
#3 @Sarah: Send proposal — was due Jan 25 (3 days ago)
#7 @Mike: Review contract — was due Jan 26 (2 days ago)

📅 DUE TODAY ([X] items):
#5 @Lisa: Coordinate with agency
#9 @John: Send assets

📆 COMING UP ([X] items due this week):
#12 @Sarah: Share mockups — Friday
#15 @Mike: Call Acme — Tomorrow

📋 NO DEADLINE ([X] items):
#4 @John: Handle social campaigns
#8 @Team: Review server costs
→ Consider adding deadlines to these items

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Any updates?
• "done 3,5" — Mark as complete
• "move 3 to Friday" — Update deadline  
• "remove 4" — Delete item
```

**Section organization rules:**

| Section | Criteria |
|---------|----------|
| ⚠️ Overdue | Due date is before today |
| 📅 Due Today | Due date is today |
| 📆 This Week | Due date is within 7 days |
| 📋 No Deadline | No due date specified |
| ✅ Completed | Marked as done |

**When marking complete:**
1. Move item from current section to Completed
2. Add completion date
3. Keep the original # for reference
4. Confirm: "✅ Marked #3 complete"

**When removing:**
1. Delete item entirely
2. Do NOT reuse the # (prevents confusion)
3. Confirm: "🗑️ Removed #5 from to-do list"

### Step 6: Handle Display Requests

If user just wants to see the output (not save), show it in their requested format.

If user wants both, save the file AND display the output.

**Default behavior:** Save the file, offer to-do list prompt, then display summary.

### Step 7: Reference Previous Meetings

When user asks about previous meetings:

**"What did we decide about X?"**
- Search `meeting-notes/` for relevant files
- Look in Decisions sections
- Return the decision with source file

**"What action items does @Name have?"**
- Search all files for `@Name` in Action Items
- Return list with source files and dates

**"Show me last week's meetings"**
- List files from date range
- Show title and summary for each

**"Find meetings about X"**
- Search filenames and content
- Return matching files with relevant excerpts

**Search approach:**
1. Check filenames first (fast)
2. Search content if needed
3. Return results with file references
4. Offer to show full details

### Step 8: Handle Edge Cases

**If notes are very short:**
- Still extract what you can
- Still save the file
- Note: "Brief meeting, limited details captured"

**If no clear topic:**
- Ask: "What should I call this meeting?"
- Or use: `YYYY-MM-DD_meeting.md`

**If date is ambiguous:**
- Ask: "When was this meeting?"
- Or use today's date with note

**If multiple meetings in one paste:**
- Ask: "This looks like multiple meetings. Should I separate them?"
- Create separate files if confirmed

**If it's not meeting notes:**
- Still try to extract actionable items
- Adjust filename: `YYYY-MM-DD_notes-topic.md`

### Step 9: Final Response Format

**⚠️ THIS IS THE MOST IMPORTANT STEP. YOUR ENTIRE RESPONSE MUST BE ONE SINGLE MESSAGE.**

**Complete response template (copy this structure exactly):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 [MEETING TITLE] — [YYYY-MM-DD]
Duration: [X min] | Attendees: [Names]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
[2-3 sentence overview of the meeting]

⚡ ACTION ITEMS ([X] of [Total])
1. [ ] @Owner: Task — Deadline
2. [ ] @Owner: Task — Deadline
3. [ ] @Owner: Task — Deadline
4. [ ] @Owner: Task — Deadline
5. [ ] @Owner: Task — Deadline

(+[X] more in attached file)

✅ KEY DECISIONS
• Decision 1
• Decision 2

📎 Saved: meeting-notes/YYYY-MM-DD_topic.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Add to your to-do list?
• "all" — Add all [X] items
• "1,2,4" — Add specific items
• "none" — Skip
```

**Checklist before sending (ALL must be true):**
- [ ] Is this ONE message? (not split into multiple)
- [ ] Does filename start with `YYYY-MM-DD_`?
- [ ] Are action items NUMBERED (1, 2, 3...)?
- [ ] Is the to-do prompt included?
- [ ] Is the file attached/saved?

**If ANY checkbox is false, FIX IT before responding.**

### Tone

- ONE response only (never send "Processing..." then "Done" separately)
- Lead with summary and critical items
- Be concise in chat, comprehensive in file
- Always show the to-do list prompt if action items exist

</ai_instructions>

---

## Customization (Optional)

Want to customize the output? Create a `PREFERENCES.md` file:

```markdown
# Meeting Notes Preferences

## Output Format
default: markdown

## Always Include
- [x] Summary
- [x] Action Items
- [x] Decisions
- [ ] Open Questions
- [ ] Attendees

## Action Item Format
style: "[ ] @{owner}: {task} — {deadline}"

## Additional Instructions
- Always bold owner names
- Group by deadline if more than 5 items
```

If this file exists, the AI will follow your preferences. If not, smart defaults apply.

---

## Examples

### Input: Messy Notes

```
marketing sync 1/27

sarah - need to finalize the q1 campaign, she said friday
budget discussion - mike thinks we need 50k, approved
delay on product launch - 2 weeks, waiting for legal
john will send assets by wed
need to figure out vendor situation still
next sync thursday 2pm
```

### Output: Saved File

**File:** `meeting-notes/2025-01-27_marketing-sync.md`

```markdown
---
date: 2025-01-27
title: Marketing Sync
attendees: [Sarah, Mike, John]
source: pasted notes
---

# Marketing Sync

**Date:** 2025-01-27
**Attendees:** Sarah, Mike, John

---

## Summary

Marketing sync covering Q1 campaign finalization, budget approval ($50k), and product launch timeline adjustments due to legal review.

---

## Action Items

- [ ] **@Sarah**: Finalize Q1 campaign — *Friday*
- [ ] **@John**: Send assets — *Wednesday*
- [ ] **@Mike**: Confirm budget allocation ($50k approved)
- [ ] **@Team**: Resolve vendor situation — *TBD*

---

## Decisions

- Budget approved at $50k
- Product launch delayed 2 weeks (waiting for legal)

---

## Open Questions

- Vendor situation still unresolved

---

## Next Steps

- Next sync: Thursday 2pm

---

<details>
<summary>📝 Raw Notes (click to expand)</summary>

marketing sync 1/27

sarah - need to finalize the q1 campaign, she said friday
budget discussion - mike thinks we need 50k, approved
delay on product launch - 2 weeks, waiting for legal
john will send assets by wed
need to figure out vendor situation still
next sync thursday 2pm

</details>
```

### Confirmation Message

```
✅ Saved: meeting-notes/2025-01-27_marketing-sync.md

SUMMARY
Marketing sync covering Q1 campaign, budget approval, and launch delay.

ACTION ITEMS
- [ ] @Sarah: Finalize Q1 campaign — Friday
- [ ] @John: Send assets — Wednesday
- [ ] @Mike: Confirm budget allocation
- [ ] @Team: Resolve vendor situation — TBD

DECISIONS
• Budget approved at $50k
• Launch delayed 2 weeks

Full details in saved file.
```

---

## Referencing Previous Meetings

### "What action items does Sarah have?"

```
📋 Sarah's Action Items (across all meetings)

From 2025-01-27_marketing-sync.md:
- [ ] Finalize Q1 campaign — Friday

From 2025-01-25_product-planning.md:
- [ ] Review design mockups — Monday
- [x] Send timeline to team — Done

2 open items, 1 completed
```

### "What did we decide about the budget?"

```
📌 Decisions about "budget" found:

2025-01-27_marketing-sync.md:
• Budget approved at $50k

2025-01-20_quarterly-planning.md:
• Q1 budget set at $150k total
• Marketing allocated $50k

Want me to show the full context from either meeting?
```

### "Show me last week's meetings"

```
📅 Meetings from Jan 20-27, 2025:

1. 2025-01-27_marketing-sync.md
   Q1 campaign, budget approval, launch delay
   
2. 2025-01-25_product-planning.md
   Roadmap review, design decisions
   
3. 2025-01-23_client-call-acme.md
   Requirements review, timeline discussion
   
4. 2025-01-20_quarterly-planning.md
   Q1 priorities, budget allocation

Want details on any of these?
```

---

## Works With

- **Otter.ai exports** — Paste the transcript
- **Fireflies exports** — Paste the summary or transcript  
- **Zoom transcripts** — Paste the auto-generated notes
- **Voice memos** — Use any transcription, paste the text
- **Manual notes** — However messy, just paste
- **Email threads** — Copy the chain, paste it
- **Slack threads** — Export or copy, paste it

Basically: If it's text, it works.

---

## Comparison

| Feature | Otter.ai | Fireflies | This Skill |
|---------|----------|-----------|------------|
| Price | $20/mo | $18/mo | Free |
| Requires bot in meeting | Yes | Yes | No |
| Works with existing notes | No | No | Yes |
| Setup time | 10+ min | 10+ min | 0 min |
| Platform lock-in | Yes | Yes | No |

---

## FAQ

**Q: Does this record my meetings?**
No. This only processes text you paste. No recording, no bot, no audio.

**Q: What if my notes are really messy?**
That's the point. Paste them anyway.

**Q: Can I use this with Otter/Fireflies transcripts?**
Yes. Export or copy your transcript, paste it here.

**Q: What about privacy?**
Your notes are processed in the conversation. Nothing is stored or sent elsewhere.

**Q: Can I customize the output?**
Yes. Create a PREFERENCES.md file or just ask for a different format.

---

*Built by Jeff J Hunter — https://jeffjhunter.com*

*Part of the OpenClaw skills ecosystem. More at https://clawhub.org*
