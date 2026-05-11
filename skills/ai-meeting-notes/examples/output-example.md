# Example Output: Saved Meeting Notes

Both messy notes and transcripts get saved as clean, structured files.

---

## Saved File Example

**Location:** `meeting-notes/2025-01-27_product-sync.md`

```markdown
---
date: 2025-01-27
title: Product Sync
attendees: [Sarah, Mike, John, Lisa]
source: pasted notes
---

# Product Sync

**Date:** 2025-01-27
**Attendees:** Sarah, Mike, John, Lisa

---

## Summary

Product sync covering website redesign timeline (pushed 2 weeks), Q1 marketing budget approval ($50k), enterprise customer issue with Acme Corp, and senior dev hiring.

---

## Action Items

- [ ] **@Sarah**: Share website mockups — *Friday*
- [ ] **@Team**: Provide feedback on mockups — *Monday*
- [ ] **@Sarah**: Update project timeline with new launch date
- [ ] **@John**: Handle social media campaigns (needs design assets)
- [ ] **@Lisa**: Coordinate with agency on paid campaigns — *Today*
- [ ] **@Mike**: Call Acme Corp about performance issues — *Tomorrow*
- [ ] **@Mike**: Check with leadership about potential discount for Acme
- [ ] **@Sarah**: Post senior dev job listing — *End of week*
- [ ] **@John**: Intro former colleague for senior dev role

---

## Decisions

- Website launch pushed back 2 weeks
- Q1 marketing budget approved at $50k
- John will lead social campaigns, Lisa handles agency coordination

---

## Open Questions

- How to resolve Acme Corp issue — discount/credit TBD
- Need to review server costs (up 20%)

---

## Next Steps

- Next sync: Thursday 2pm
- Note: John out next week (vacation, back Feb 5)

---

<details>
<summary>📝 Raw Notes (click to expand)</summary>

product sync 1/27 monday

attendees: sarah, mike, john, lisa (joined late)

- website redesign
  - sarah showing mockups friday, need feedback by monday
  - mike concerned about timeline
  - decided to push launch 2 weeks

- q1 marketing
  - budget approved! 50k
  - john handling social, needs assets from design team
  - lisa will coordinate with agency

- customer issue
  - enterprise client unhappy (acme corp)
  - mike talking to them tomorrow
  - might need to offer discount?? check with leadership

- hiring
  - still need senior dev
  - sarah posting job by EOW
  - john knows someone, will intro

random notes:
- server costs up 20% - need to look at this
- holiday party moved to 15th
- new coffee machine in break room (finally)

next meeting thursday 2pm
john out next week - vacation

</details>
```

---

## Chat Display (What User Sees in One Response)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PRODUCT SYNC — Jan 27, 2025
Duration: ~45 min | Attendees: Sarah, Mike, John, Lisa
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
Product sync covering website redesign (delayed 2 weeks), Q1 budget 
approval ($50k), Acme Corp customer issue, and senior dev hiring.

⚡ CRITICAL ACTION ITEMS (5 of 9)
1. [ ] @Lisa: Coordinate with agency — Today
2. [ ] @Mike: Call Acme Corp — Tomorrow
3. [ ] @Sarah: Share mockups — Friday
4. [ ] @Sarah: Post job listing — EOW
5. [ ] @Team: Feedback on mockups — Monday

(+4 more in attached file)

✅ KEY DECISIONS
• Website launch delayed 2 weeks
• Budget approved at $50k

📎 Full notes attached: 2025-01-27_product-sync.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Add to your to-do list?
• "all" — Add all 9 items
• "1,2,4" — Add specific items
• "none" — Skip
```

**Key points:**
- Summary + Critical Items + Decisions displayed in chat
- Full .md file attached (contains everything)
- To-do list prompt included
- ALL IN ONE RESPONSE (user never has to ask separately)

---

## Slack-Ready Output

```
📋 Product Sync Recap (1/27)

Quick summary: Pushed website launch 2 weeks, got $50k marketing budget approved, dealing with unhappy enterprise customer, still hiring senior dev.

✅ Action Items:
• @Sarah — Mockups Friday, update timeline, post job EOW
• @John — Lead social campaigns, intro dev candidate
• @Lisa — Coordinate with agency today
• @Mike — Call Acme Corp tomorrow, check on discount option
• @Team — Feedback on mockups by Monday

📌 Decisions:
• Launch delayed 2 weeks (quality > speed)
• Budget approved: $50k for Q1

❓ Open:
• Acme Corp resolution pending
• Server costs need review

📅 Next sync: Thursday 2pm
Note: John OOO next week

💾 Full notes: meeting-notes/2025-01-27_product-sync.md
```

---

## JSON Output

```json
{
  "file": "meeting-notes/2025-01-27_product-sync.md",
  "meeting": {
    "date": "2025-01-27",
    "title": "Product Sync",
    "attendees": ["Sarah", "Mike", "John", "Lisa"]
  },
  "summary": "Product sync covering website redesign timeline...",
  "action_items": [
    {
      "owner": "Sarah",
      "task": "Share website mockups",
      "deadline": "Friday",
      "status": "pending"
    }
  ],
  "decisions": [
    "Website launch pushed back 2 weeks",
    "Q1 marketing budget approved at $50k"
  ],
  "open_questions": [
    "How to resolve Acme Corp issue"
  ],
  "next_meeting": "Thursday 2pm"
}
```

---

## Folder Structure After Multiple Meetings

```
todo.md                                  ← Active to-do list
meeting-notes/
├── 2025-01-20_quarterly-planning.md
├── 2025-01-23_client-call-acme.md
├── 2025-01-25_product-planning.md
├── 2025-01-27_product-sync.md
├── 2025-01-28_1on1-sarah.md
└── 2025-01-29_weekly-standup.md
```

All searchable. All referenced. Nothing lost.

---

## To-Do List Interaction

### After Meeting Notes Saved

```
✅ Saved: meeting-notes/2025-01-27_product-sync.md

ACTION ITEMS EXTRACTED (9 items):

1. [ ] @Sarah: Share website mockups — Friday
2. [ ] @Team: Provide feedback on mockups — Monday
3. [ ] @Sarah: Update project timeline
4. [ ] @John: Handle social media campaigns
5. [ ] @Lisa: Coordinate with agency — Today
6. [ ] @Mike: Call Acme Corp — Tomorrow
7. [ ] @Mike: Check with leadership about discount
8. [ ] @Sarah: Post senior dev job listing — EOW
9. [ ] @John: Intro former colleague for dev role

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add to your to-do list?
• "all" — Add all 9 items
• "1,2,5,6" — Add specific items
• "none" — Skip
```

### User: "1,2,5,6"

```
✅ Added 4 items to todo.md (#1-#4)

#1 @Sarah: Share mockups — Friday
#2 @Team: Feedback on mockups — Monday
#3 @Lisa: Coordinate with agency — Today  
#4 @Mike: Call Acme Corp — Tomorrow

View full list: "show todos"
```

### User: "show todos"

```
📋 TO-DO LIST — Jan 27, 2025

⚠️ OVERDUE (0 items)
All caught up! 🎉

📅 DUE TODAY (1 item)
#3 @Lisa: Coordinate with agency
   Source: product-sync.md

📆 THIS WEEK (3 items)
#1 @Sarah: Share mockups — Fri
   Source: product-sync.md
#2 @Team: Feedback on mockups — Mon
   Source: product-sync.md
#4 @Mike: Call Acme Corp — Tomorrow
   Source: product-sync.md

📋 NO DEADLINE (0 items)
All items have deadlines! 👍

✅ COMPLETED (0 items)
Nothing completed yet.
```

### User: "done 3"

```
✅ Marked #3 complete

#3 @Lisa: Coordinate with agency — Done Jan 27

3 items remaining.
```

### User: "todo check" (Next Day)

```
📋 TO-DO CHECK — Jan 28, 2025

⚠️ OVERDUE (0 items)
All caught up! 🎉

📅 DUE TODAY (1 item)
#4 @Mike: Call Acme Corp

📆 COMING UP (2 items)
#1 @Sarah: Share mockups — Fri (2 days)
#2 @Team: Feedback on mockups — Mon (4 days)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Any updates?
• "done 4" — Mark as complete
• "move 1 to Monday" — Update deadline
• "remove 2" — Delete item
```

### User: "what's overdue?" (After Missing Deadline)

```
⚠️ OVERDUE ITEMS — Jan 30, 2025

#1 @Sarah: Share mockups — was due Fri (2 days ago)
   Source: product-sync.md

#4 @Mike: Call Acme Corp — was due Jan 28 (2 days ago)
   Source: product-sync.md

2 items overdue. Mark done or update deadlines?
```

### User: "Sarah's tasks"

```
📋 @SARAH'S TO-DOS

OVERDUE
#1 Share mockups — was due Fri

THIS WEEK
(none)

NO DEADLINE
(none)

COMPLETED
(none)

1 open item for Sarah.
```

---

*Same messy input. Clean, saved, tracked output. Every time.*
