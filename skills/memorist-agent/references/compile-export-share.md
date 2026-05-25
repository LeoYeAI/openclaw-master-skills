# Compile, Export & Share

## /memorist_agent compile

**Purpose:** Compile all story fragments into polished memoir chapters. The Openclaw user can review and edit each chapter before finalizing.

**Usage:**
- `/memorist_agent compile --narrator "Dad"` — compile all complete domains

**Steps:**

1. Load all fragments for the narrator, grouped by domain.
2. For each domain that has >=1 fragment:

   a. Merge all fragments from that domain into a single narrative arc.
   b. Write a chapter in the narrator's language using the following structure:
      - **Chapter title**: evocative, personal (e.g. "The Courtyard Where I Grew Up")
      - **Opening**: 2-3 sentences setting the scene
      - **Body**: synthesized narrative from all fragments, preserving the narrator's voice, in chronological order within the domain
      - **Closing**: a reflection or a quote from the narrator's own words
   c. Save to `chapters/chapter-{NN}-{domain}.md`.

3. Generate a master memoir file:
   `exports/memoir-{narrator-slug}-{date}.md`

   Structure:
   ```markdown
   # {Narrator Name}'s Story
   ## As told to {user name} | {year}

   ---

   ## Foreword
   {Brief context: who narrated, who compiled, how many sessions}

   ---

   ## Chapter 1: {title}
   {chapter content}

   ---
   ## Chapter 2: {title}
   ...

   ---

   ## Appendix: People & Places
   {entity map as a reference}
   ```

4. Display compilation summary:
   ```
   Memoir Compiled — {narrator name}

   Chapters created : {N}
   Total words      : {approx count}
   Domains covered  : {list}
   Domains pending  : {list of not-started}

   Preview (Chapter 1):
   ───────────────────────────────
   {first 10 lines of Chapter 1}
   ───────────────────────────────

   To read the full memoir:
     /memorist_agent export --narrator "{name}" --format md

   To continue adding stories:
     /memorist_agent interview --narrator "{name}"
   ```

### Co-editing Mode

During compilation, show each chapter draft and ask:
```
Chapter 1 draft ready. Would you like to:
[1] Accept as-is
[2] Edit — tell me what to change
[3] Add a note or annotation
[4] Skip this chapter for now
```

If the user chooses to edit, apply their changes and re-save the chapter file, marking it with `editedBy: "{user}"` and `editedAt: "{ISO}"`.

---

## /memorist_agent export

**Purpose:** Export the compiled memoir to a file.

**Usage:**
- `/memorist_agent export --narrator "Dad" --format md` (default)
- `/memorist_agent export --narrator "Dad" --format json`
- `/memorist_agent export --narrator "Dad" --format txt`

**Steps:**

1. Check that `exports/memoir-{slug}-{date}.md` exists. If not: run compile first.
2. For `--format md`: export is already in markdown — confirm the file path.
3. For `--format json`: export the full structured data (all fragments + entity map + chapter metadata).
4. For `--format txt`: strip all markdown formatting, output plain text.
5. Report:
   ```
   Memoir exported

   File    : ~/.openclaw/memorist_agent/narrators/{id}/exports/memoir-{date}.{ext}
   Format  : {format}
   Size    : {file size}
   Words   : {approx word count}

   This file stays on your local machine.
   To share with family: /memorist_agent share --narrator "{name}"
   ```

---

## /memorist_agent share

**Purpose:** Share the memoir or a chapter with a family co-editor via a generated file or message.

**Steps:**

1. Load the compiled memoir.
2. Ask:
   ```
   How would you like to share?
   [1] Copy the memoir text here (paste into email/WeChat yourself)
   [2] Send a WhatsApp message to a family member with the memoir text
   [3] Show a shareable summary (first chapter + table of contents)
   ```
3. For option 1: display the full text in the conversation.
4. For option 2: ask for the recipient's WhatsApp number, then send via `whatsapp_send_message`:
   ```
   [Family Memoir from {user name}]

   I've been recording {narrator name}'s life stories with the help of AI.
   Here's a chapter to read:

   ─────────────
   {chapter 1 content, max 2000 chars}
   ─────────────

   There are {N} chapters total. Reply to let me know what you think!
   ```
5. For option 3: display first chapter + a table of contents listing all chapter titles and word counts.
6. Mark `sharesHistory` in `profile.json` with `{ sharedAt, format, recipient }`.
