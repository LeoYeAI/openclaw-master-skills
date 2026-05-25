# Interview Workflow — Detailed Steps

This document contains the full interview session logic for `/memorist_agent interview`.

---

## Step 1 — Load Context

1. Load `~/.openclaw/memorist_agent/narrators.json`. If empty: "No narrators set up yet. Run /memorist_agent setup first."
2. Resolve narrator by name (case-insensitive, partial match OK).
3. Load `profile.json`, `entities.json`, `sessions.json`.
4. If `--domain` not specified: pick the next domain with `status: "not-started"` or `status: "in-progress"`. If all domains are `complete`: "All 9 domains are complete! Run /memorist_agent compile to create the memoir."
5. Load all existing fragments for this domain.

## Step 2 — Prepare the Interview

Generate a session context object:
```json
{
  "sessionId": "session-{timestamp}",
  "narratorId": "{id}",
  "domain": "{domain}",
  "lang": "{lang}",
  "startedAt": "{ISO}",
  "exchanges": [],
  "newFragments": [],
  "entitiesFound": { "people": [], "places": [], "years": [], "events": [] }
}
```

**Build the opening question** using this logic:
- If domain has 0 fragments: use the domain's standard opening question (see Domain Table in SKILL.md).
- If domain has existing fragments: read them and generate a contextual follow-up question that deepens or fills gaps.
- If `entities.json` has unresolved people/places mentioned in prior sessions: prioritize a follow-up on those.
- Always adapt the question to the narrator's language setting.

**Language templates:**

For `lang: "zh"`, use warm, colloquial Mandarin:
```
爸爸/妈妈，我想听您讲讲小时候的故事。
您在哪里出生的，那时候家里是什么样子的？
```

For `lang: "en"`, use warm, conversational English:
```
Dad, I'd love to hear about your childhood.
Where were you born, and what's your earliest memory of home?
```

## Step 3 — Send the Question

**Channel: `live`**
Display the question directly to the user:
```
───────────────────────────────
Interview: {narrator name} — {domain label}
Session {N} | {lang}
───────────────────────────────

Ask {narrator} this question:

  "{opening question}"

When they answer, type or paste their response here, then I'll
generate the follow-up questions.
───────────────────────────────
```
Wait for the user to provide the answer.

**Channel: `relay`**
Display:
```
───────────────────────────────
Next question for {narrator} ({channel}: relay)
───────────────────────────────

Please ask {narrator}:

  "{opening question}"

Paste or type their answer below when ready.
───────────────────────────────
```

**Channel: `whatsapp`**
Send via `whatsapp_send_message` to narrator's number:

For `lang: "zh"`:
```
[家庭故事] {narrator name}，您好！

我正在帮助记录您的人生故事。

问题：
{opening question}

您可以直接回复这条消息，用文字或语音都可以。
```

For `lang: "en"`:
```
[Family Memoir] Hi {narrator name},

I'm helping to capture your life story for the family.

Question:
{opening question}

Please reply to this message with your answer — voice note or text is fine.
```

Then tell the user:
```
Question sent to {narrator} via WhatsApp (+{number}).
I'll process their reply when you paste it here.
```

## Step 4 — Adaptive Follow-up Loop

This loop runs for up to 5 exchanges per session (configurable):

**For each answer received:**

1. **Extract entities** from the answer:
   - People mentioned (names, relationships): add to `entitiesFound.people`
   - Places mentioned: add to `entitiesFound.places`
   - Years/decades mentioned: add to `entitiesFound.years`
   - Events mentioned: add to `entitiesFound.events`

2. **Decide the next move** (pick ONE):

   **Option A — Deepen** (narrator mentioned something interesting):
   Generate a follow-up that digs deeper into a specific detail they just shared.
   Example: If they said "我们那时候住在大杂院" → ask "您能描述一下那个大杂院吗？邻居们都是什么样的人？"

   **Option B — Expand timeline** (narrator gave a fact, not a story):
   Ask for a specific memory or sensory detail.
   Example: If they said "I worked at the factory for 20 years" → ask "What was your very first day at the factory like? What did it smell like, sound like?"

   **Option C — Resolve entity** (they mentioned a person or place we don't know yet):
   Ask about an unresolved entity from `entitiesFound`.
   Example: "You mentioned Uncle Wang — who was he and what was your relationship like?"

   **Option D — Pivot** (after 3+ exchanges in the same sub-topic):
   Transition to a related area of the same domain.

3. Send the follow-up question using the same channel logic as Step 3.

4. Append to `session.exchanges`:
   ```json
   {
     "q": "{question}",
     "a": "{answer}",
     "timestamp": "{ISO}",
     "entities": { "people": [], "places": [], "years": [] }
   }
   ```

5. After 3–5 exchanges (or when user types `/done`, `完了`, `done`): end the loop and proceed to Step 5.

## Step 5 — Distill Fragment

After the session exchanges, synthesize a story fragment:

1. Analyze all exchanges for this session.
2. Write a first-person narrative fragment in the narrator's language (warm, personal, present-tense or past-tense as appropriate). Length: 150–400 words.
3. Preserve the narrator's voice — keep dialect phrases, specific names, and their natural expressions. Do not sanitize.
4. Note any gaps or inconsistencies that should be followed up in a future session.

**Fragment format** (`fragments/{domain}-{NNN}.json`):
```json
{
  "id": "{domain}-{NNN}",
  "narratorId": "{id}",
  "domain": "{domain}",
  "sessionId": "{sessionId}",
  "lang": "{lang}",
  "title": "{auto-generated short title}",
  "content": "{narrative text}",
  "rawExchanges": [{...}],
  "entitiesFound": { "people": [], "places": [], "years": [], "events": [] },
  "followUpNeeded": ["{question 1}", "{question 2}"],
  "createdAt": "{ISO}",
  "editedAt": null,
  "editedBy": null
}
```

## Step 6 — Update Entity Map

Merge `entitiesFound` from this session into `entities.json`:
- People: add new ones, merge with existing by name-match
- Places: same
- Years: same
- Mark each entity with `{ "mentionedIn": ["{fragment-id}"], "followedUp": false }`

Entities not yet followed up will influence future sessions (Option C in Step 4).

## Step 7 — Save and Report

1. Write fragment file.
2. Update `sessions.json` with completed session.
3. Update `profile.json` domain status:
   - If this is the first fragment: `"in-progress"`
   - If follow-up questions remain: `"in-progress"`
   - If domain feels complete (no follow-up needed): `"complete"`

4. Reply to user:
```
✅ Session complete — {narrator name} | {domain label}

Fragment saved: {fragment title}
───────────────────────────────
{first 3 lines of fragment content...}
───────────────────────────────
People mentioned : {list}
Places mentioned : {list}
Follow-ups needed: {count}

Domain progress: {N}/{9} domains have fragments
Next suggested  : /memorist_agent interview --narrator "{name}" --domain {next-domain}
```
