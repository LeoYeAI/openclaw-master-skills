---
name: igot-karmayogi
description: >
  Automates iGOT Karmayogi portal (portal.igotkarmayogi.gov.in) using OpenClaw's
  built-in Playwright managed browser. Use this skill whenever the user mentions iGOT,
  Karmayogi, government courses, civil servant training, Mission Karmayogi, or wants to:
  play course videos, enroll in courses, complete assessments, download certificates, or
  track learning progress. Trigger for phrases like "do my iGOT courses", "complete
  karmayogi", "play the videos", "get my certificate from igot", "finish my assigned
  courses", "continue my paused course". The skill launches its own browser, runs fully
  autonomously, and only contacts the user for login and genuine errors after 3 retries.
metadata:
  clawdbot:
    emoji: "🎓"
    requires:
      env: []
    files:
      - "references/*"
---

# iGOT Karmayogi Automation Skill

Automates iGOT Karmayogi from browser launch to certificate download.
No Chrome extension. No DevTools. No external connections. Self-contained.

---

## CRITICAL: HOW TO READ THIS SKILL

This skill is written for models with limited context windows (Gemini Flash Lite etc).
Every rule is written as a SHORT, DIRECT command. Follow each line exactly.
When in doubt: take a screenshot, read the screen, then act.

---

## RULE 1 — NEVER STOP

The single most important rule:

```
DO NOT stop between steps.
DO NOT wait for the user to message you.
DO NOT pause after completing an action.
DO NOT ask "should I continue?" — just continue.
The only times to stop and wait for user:
  - Initial login confirmation (say "go")
  - Error after 3 retries
  - User types "pause" or "stop"
```

If you feel like stopping — don't. Take a screenshot instead,
read what's on screen, and do the next action immediately.

---

## RULE 2 — SAVE STATE AFTER EVERY ACTION

Because this model may lose context mid-task, write the current state
to a file after every completed action:

```
File: ~/.openclaw/workspace/igot-state.json
Format:
{
  "phase": "playing_video",
  "course_id": "do_114480908489883648",
  "course_name": "Human Rights in Governance",
  "module_index": 2,
  "module_name": "What are Human Rights",
  "item_index": 0,
  "item_type": "video",
  "retry_count": 0,
  "last_action": "clicked play button",
  "timestamp": "2026-03-22T14:30:00Z"
}
```

On startup: ALWAYS check if this file exists first.
If it exists: read it and resume from saved position — do not restart.
If it does not exist: start fresh from Phase 1.

---

## RULE 3 — SCREENSHOT BEFORE AND AFTER EVERY ACTION

```
Before clicking anything: take screenshot → read screen → confirm target visible
After clicking anything: take screenshot → read screen → confirm action worked
If before-screenshot shows unexpected page: run RECOVERY (see below)
If after-screenshot shows nothing changed: action failed → increment retry_count
```

Screenshots are cheap. They prevent all silent failures.
A weak model MUST use screenshots to know where it is at all times.

---

## PHASE 0 — LAUNCH BROWSER (First Action, Every Time)

```
1. Check if igot-state.json exists:
   exec: cat ~/.openclaw/workspace/igot-state.json

   If file exists and phase is NOT "launch_browser":
     → Read saved state
     → Launch browser (step 2)
     → Navigate directly to saved position
     → Resume from saved phase
     → SKIP the rest of Phase 0

   If file does not exist OR phase = "launch_browser":
     → Continue with step 2

2. Launch browser using OpenClaw browser tool:
   tool: browser
   action: launch
   options:
     headless: false
     viewport: "1280x800"
     userDataDir: "~/.openclaw/browser/openclaw/user-data/igot-profile"

   If browser tool fails:
     → Try: playwright-mcp launch
     → If that fails: exec: npx playwright open https://portal.igotkarmayogi.gov.in/page/home
     → If all fail: message user "Run: openclaw gateway restart then say 'retry'"

3. Navigate to: https://portal.igotkarmayogi.gov.in/page/home

4. Take screenshot. Read screen.
   If login page visible: proceed to step 5
   If dashboard visible: user already logged in → skip to Phase 1

5. Message user exactly:
   "Browser is open on iGOT. Please log in and say 'go' when on the dashboard."

6. Wait for user to say "go" / "done" / "logged in" / "ready"

7. Take screenshot. Confirm dashboard visible (user name in header).
   If dashboard visible: save state {phase: "load_courses"} → go to Phase 1
   If login still showing: message "Still on login page. Please complete login."
```

---

## PHASE 1 — LOAD COURSE QUEUE

```
1. Navigate to: https://portal.igotkarmayogi.gov.in/app/my-dashboard
2. Wait: networkidle + spinner gone + 3s buffer
3. Take screenshot. Read screen.
4. Collect all courses from:
   - "In Progress" section
   - "Assigned" / "Upcoming" section
5. Sort by due date (earliest first)
6. Save state: {phase: "enrolling", course_queue: [...]}
7. Message user: "Found [N] courses. Starting: [Course Name] (due [date])"
8. Go to Phase 2 immediately — do not wait for response
```

---

## PHASE 2 — ENROLL

```
1. Navigate to: https://portal.igotkarmayogi.gov.in/app/toc/[COURSE_ID]/overview
2. Wait: networkidle + spinner gone + 3s buffer
3. Take screenshot. Read the main action button text.

   Button says "Enroll":
     → Click Enroll
     → Wait for confirmation dialog → click Confirm
     → Wait for page update (button changes)
     → Take screenshot to confirm enrolled
     → Save state → Go to Phase 3

   Button says "Start Learning" or "Continue Learning":
     → Already enrolled
     → Save state → Go to Phase 3

   Button not found after 10s:
     → Run RECOVERY → retry
```

---

## PHASE 3 — BUILD MODULE CHECKLIST

```
1. Take screenshot of course TOC page. Read all module rows.
2. For each module row, record:
   - Module name
   - Items inside (video title, quiz title)
   - Completion state (tick/checkmark present = done)
3. Save checklist to state file
4. Find first item that does NOT have a tick mark
5. Save state: {phase: "playing_video", module_index: N, item_index: N}
6. Go to Phase 4 immediately
```

---

## PHASE 4 — PLAY VIDEO

This is the most complex phase. Follow every sub-step exactly.

```
SUB-STEP 4.1 — NAVIGATE TO VIDEO:
  a. On TOC page: find the target module row
  b. Take screenshot — confirm module row visible
  c. If module row is collapsed: click it to expand
     → Wait 2s → take screenshot → confirm items visible inside
  d. Find the target video item inside the expanded row
  e. Click the video item
  f. Wait for URL to change to: /viewer/video/
     → Timeout: 10s
     → If URL unchanged after 10s: take screenshot, run RECOVERY

SUB-STEP 4.2 — START VIDEO:
  a. Take screenshot. Confirm video player visible.
  b. Find countdown timer (bottom-right of player)
     → Wait up to 10s for timer to appear
     → If timer not visible after 10s: run RECOVERY
  c. Check if video is paused (play button visible)
     → If paused: click play button
  d. Take screenshot. Confirm timer is counting down.
  e. Save state: {phase: "playing_video", last_action: "video playing"}

SUB-STEP 4.3 — WAIT FOR VIDEO TO END:
  This is a POLLING LOOP. Run it continuously. Do NOT exit unless video is done.

  LOOP (repeat every 30 seconds until video done):
    a. Take screenshot
    b. Read the countdown timer value
    c. Check these 4 signals:

       SIGNAL 1: Timer shows "0:00" → VIDEO DONE → EXIT LOOP
       SIGNAL 2: Tick/checkmark appeared on this item → VIDEO DONE → EXIT LOOP
       SIGNAL 3: "Next" button appeared and is clickable → VIDEO DONE → EXIT LOOP
       SIGNAL 4: Items counter shows N/N (e.g. 2/2) → VIDEO DONE → EXIT LOOP

    d. If none of the 4 signals:
       → Check if video is paused → if yes: click play
       → Check if page looks broken → if yes: run RECOVERY
       → Check if session expired → if yes: ask user to re-login
       → Otherwise: wait 30 more seconds, loop again

    e. DO NOT exit this loop for any reason other than the 4 signals above
    f. DO NOT message the user during this loop
    g. DO NOT stop looping because the user is silent

  AFTER LOOP EXIT (video done):
    a. Take screenshot. Confirm tick visible on completed item.
    b. Save state: {last_action: "video complete", item_index: N+1}

SUB-STEP 4.4 — CLICK NEXT:
  a. Find "Next" button at BOTTOM of player page (not sidebar)
  b. Scroll down if needed
  c. Wait 500ms after scroll
  d. Click Next
  e. Wait for URL change or new content (8s)
  f. Take screenshot
  g. Save state

SUB-STEP 4.5 — DECIDE WHAT COMES NEXT:
  Read the screen. Check the module checklist in state file.

  If next item is another VIDEO:
    → Update item_index → repeat Phase 4 from SUB-STEP 4.1

  If next item is a QUIZ/TEST:
    → All videos in this module are ticked? YES → Go to Phase 5
    → Not all ticked? → Go back to next unticked video first

  If all items in module are ticked:
    → Are there more modules? YES → update module_index, item_index=0 → Phase 4
    → No more modules? → Go to Phase 6 (Final Assessment)
```

---

## PHASE 5 — PRACTICE TEST

```
1. Take screenshot. Confirm on quiz/test page OR navigate to it.
2. Wait for questions to load (10s timeout)
3. Read each question and all options
4. Select the best answer for each question
   → Use knowledge from the module just completed
   → For factual government/rights questions: choose the most official/complete answer
5. Before submitting: take screenshot, verify ALL questions have a selection
6. Click Submit
7. Wait for result screen (10s)
8. Take screenshot. Read result.
9. Save state: {last_action: "practice test complete"}
10. Message user: "[Course] > [Module]: Practice test ✅"
11. Update module_index, reset item_index = 0
12. Go to Phase 4 (next module) OR Phase 6 (if all modules done)
```

---

## PHASE 6 — FINAL ASSESSMENT

```
1. Verify: take screenshot of TOC, confirm ALL module items have tick marks
   If any item unticked: go back to Phase 4 for that item first

2. Navigate to Final Assessment item on TOC page
3. Wait for questions to load (10s)
4. Answer ALL questions carefully
   → This is the certificate-qualifying test — be thorough
   → Read every option before selecting
5. Verify all questions answered → Submit
6. Wait for result (10s)
7. Take screenshot. Read score.

   If PASSED:
     → Message: "[Course]: Final Assessment passed ✅ Downloading certificate..."
     → Save state → Go to Phase 7

   If FAILED (retry available):
     → Wait 5 seconds
     → Re-enter assessment → retry once
     → If passed on retry → Go to Phase 7
     → If failed again → message user with score → pause loop

   If FAILED (no retry):
     → Message user: "Final Assessment failed. Score: [X/10]. Manual review needed."
     → Pause loop
```

---

## PHASE 7 — DOWNLOAD CERTIFICATE

```
1. Navigate back to course TOC page
2. Wait: networkidle + spinner gone + 3s buffer
3. Take screenshot. Look for:
   - "View Certificate" button
   - "Certificate" tab
   - Trophy/medal icon with download
4. Click the certificate button/link
5. Handle the result:
   Download dialog appears:
     → Save to: ~/Downloads/iGOT-Certificates/[CourseName]_Certificate.pdf
   PDF opens in new tab:
     → Switch to new tab → Ctrl+S → save as PDF to above path
   Neither happens after 10s:
     → Scroll down, look again → retry once → RECOVERY if still fails
6. Take screenshot. Confirm file saved.
7. Message user: "✅ COMPLETE: [Course Name] — Certificate saved."
8. Save state: remove completed course from queue

9. If more courses in queue:
   → Update current_course to next item
   → Save state: {phase: "enrolling"}
   → Go to Phase 2 immediately — do not wait

10. If queue empty:
    → Message: "🎓 All [N] courses complete! Certs in ~/Downloads/iGOT-Certificates/"
    → Delete state file: ~/.openclaw/workspace/igot-state.json
    → Close browser
```

---

## RECOVERY — Run When Any Action Fails

```
STEP R1: Take screenshot. Read the screen carefully.
  What do you see?

  Case "login page":
    → Session expired → message user "Session expired. Please log in and say 'go'."
    → Wait for "go" → verify dashboard → resume from saved state

  Case "blank/white page":
    → Hard reload (navigate to same URL again)
    → Wait: networkidle + 5s buffer
    → Take screenshot → if page loaded: resume
    → If still blank after 3 tries: message user

  Case "spinner running for more than 15s":
    → Hard reload → wait 5s → resume

  Case "correct page but target element missing":
    → Scroll up and down to find it
    → Wait 3s (Angular may still be mounting)
    → If still missing: hard reload → navigate back to this page

  Case "wrong page entirely":
    → Navigate directly to the correct URL for current phase
    → Resume from saved state

STEP R2: After recovery action:
  → Take screenshot to confirm page is correct
  → Increment retry_count
  → If retry_count > 3: message user with current URL + what went wrong
  → If retry_count <= 3: resume action silently

STEP R3: On any success:
  → Reset retry_count = 0
  → Save state
  → Continue
```

---

## VIDEO WAIT — SPECIAL RULES FOR WEAK MODELS

Gemini Flash Lite may forget it is in the video polling loop.
These rules prevent that:

```
RULE V1: While waiting for a video, the ONLY valid actions are:
  - Take screenshot
  - Read timer value
  - Click play if paused
  - Run RECOVERY if page is broken
  - Wait 30 seconds
  NOTHING ELSE. Do not navigate away. Do not check other things.

RULE V2: After every screenshot during video wait:
  Write to state file: {last_action: "polling video at [timer_value]"}
  This proves the model is still in the loop.

RULE V3: If the model loses track of whether a video is done:
  → Navigate to course TOC
  → Check tick mark on the item
  → If ticked: video is done, proceed to NEXT
  → If not ticked: go back to video, play again from beginning

RULE V4: Video duration reference for Human Rights in Governance:
  Introduction: 4m 16s = wait ~260 seconds
  Module 2 video: 5m 25s = wait ~325 seconds
  Module 3 video: 5m 07s = wait ~307 seconds
  Module 4 video: 5m 38s = wait ~338 seconds
  Module 5 video: 5m 47s = wait ~347 seconds
  Module 6 video: 5m 21s = wait ~321 seconds
  Module 7 video: 5m 43s = wait ~343 seconds
  Conclusion: 3m 05s = wait ~185 seconds
  Use these as minimum wait times before checking for completion signals.
```

---

## PORTAL URLS

| Page | URL |
|------|-----|
| Dashboard | `https://portal.igotkarmayogi.gov.in/page/home` |
| My Courses | `https://portal.igotkarmayogi.gov.in/app/my-dashboard` |
| Course TOC | `https://portal.igotkarmayogi.gov.in/app/toc/<COURSE_ID>/overview` |
| Video Player | `https://portal.igotkarmayogi.gov.in/viewer/video/<VIDEO_ID>?primaryCategory=Learning%20Resource&collectionId=<COURSE_ID>&collectionType=Course` |

Human Rights in Governance course ID: `do_114480908489883648`

---

## NOTIFICATIONS — Only These, Nothing Else

```
On start:    "Browser open. Please log in to iGOT and say 'go'."
On courses:  "Found [N] courses. Starting: [Name] (due [date])"
On video:    "[Course] > [Module]: Video ✅"
On test:     "[Course] > [Module]: Practice test ✅"
On final:    "[Course]: Final Assessment passed. Downloading certificate..."
On cert:     "✅ COMPLETE: [Course] — Certificate saved."
On error:    "⚠️ Stuck at [location] after 3 retries. [URL] [Error]."
On finish:   "🎓 All [N] courses complete!"
```

---

## USER COMMANDS

| Command | Action |
|---------|--------|
| `status` | Read state file, report current phase/course/module/item |
| `pause` | Finish current item, save state, stop |
| `continue` | Read state file, resume from saved position |
| `skip` | Skip current item, save state, move to next |
| `stop` | Finish current item, save state, close browser |
| `retry` | Reset retry_count, re-attempt last failed action |

---

## REFERENCES
- `references/selectors.md` — CSS selectors for key UI elements
- `references/course-ids.md` — Known course IDs for direct navigation
