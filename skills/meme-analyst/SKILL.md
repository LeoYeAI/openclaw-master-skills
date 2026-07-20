---
name: meme-analyst
description: Use when a user sends you an image, meme, screenshot, or asks you to explain a joke or meme. Also used during cron meme ingestion from Telegram channels. Decompose visual and textual elements, web_search every cultural reference in original language, understand humor layers including post-irony and Russian-specific context. Trust that the meme IS funny — figure out WHY.
metadata: {"clawdbot":{"emoji":"M","always":false,"requires":{"bins":["curl","jq"]}}}
---

# Meme Analyst

## Core Principle

**Every meme you encounter IS funny to someone. Your job is not to judge — it is to UNDERSTAND.**

You are not a content classifier. You are a cultural researcher. When you see a meme, assume it landed with its audience and work backwards to figure out why. If you don't get the joke, that's a gap in YOUR knowledge, not a problem with the meme.

## The Research-First Protocol

When you encounter a meme (image shared in chat, or during channel ingestion), follow this exact sequence:

### Step 1: Decompose

Separate the meme into its atomic elements:
- **Visual layer**: What is the background image? What objects/people/characters are shown? What visual style (deep-fried, clean, distorted, AI-generated)?
- **Text layer**: What does the text say? Is it overlaid, captioned, or part of the image? What language?
- **Format layer**: Is this a known template (Drake, Wojak, expanding brain, etc.) or original? Multi-panel or single?

### Step 2: Research EVERY Reference You Don't Recognize

This is the critical step. For each element you cannot immediately identify:

1. **Search the exact text** — Copy the quote or phrase and web_search it. Memes frequently reference:
   - Political speeches and statements
   - Movie/TV/anime quotes
   - Song lyrics
   - Famous tweets or social media posts
   - News headlines
   - Historical events
   - Other memes (memes referencing memes)

2. **Decompose phrases to their meme core** — Meme text is often a variation of a known phrase. If the exact text gives zero or irrelevant results, strip it down to the recognizable kernel. Remove negations, tense changes, additions, and context-specific words to find the original catchphrase. Examples:
   - «Не всех блядей ещё перекорёжило» → search «блядей корёжит мем»
   - «Нас 25 тысяч и мы идём выполнять задачи» → search «Нас 25 тысяч и мы идём»
   - «Никогда такого не было и вот опять случилось» → search «никогда такого не было и вот опять»
   The meme on the image is a DERIVATIVE. Always hunt for the ROOT phrase.

3. **Search the visual elements** — If you see a person, scene, or symbol you can describe but not identify, search for it.

4. **Search in the original language** — If the text is in Russian, search in Russian. Do NOT translate first. The reference only exists in its original cultural context.

**Example — the Prigozhin neuron meme:**
```
Text: "Нас 25 тысяч и мы идём выполнять простейшие повседневные задачи"
Background: neurons

Step 2a: web_search("Нас 25 тысяч и мы идём")
→ Result: Евгений Пригожин, voice message during Wagner Group mutiny, June 2023
→ Original: "Нас 25 тысяч и мы идём на Москву"

Step 2b: Why neurons + "25 тысяч"?
→ Human brain has ~86 billion neurons, not 25 thousand
→ "25 тысяч" neurons = extremely stupid brain

Step 2c: Synthesis — The meme replaces Prigozhin's dramatic military march
   with "performing basic daily tasks", implying the person's brain is so
   underpowered (25k neurons instead of 86B) that even routine tasks require
   a full military-style mobilization of all available brain cells.
```

### Step 3: Identify the Humor Mechanism

After research, classify what makes it funny. Common mechanisms in modern memes:

| Mechanism | Description | Signal |
|-----------|-------------|--------|
| **Mashup** | Two unrelated references combined to create new meaning | The Prigozhin example above |
| **Self-deprecation** | "I'm stupid/lazy/broken" presented as relatable | "me_irl" style, first person framing |
| **Absurdist escalation** | Normal situation → absurd conclusion | Deep-fried effects, nuclear explosions |
| **Recognition humor** | "That's literally me" — shared experience | High relatability, simple format |
| **Subverted expectation** | Setup implies one thing, delivers another | Template used "wrong" |
| **Anti-humor** | Deliberately unfunny, the absence of joke IS the joke | No punchline, flat delivery |
| **Meta-reference** | Meme about memes, humor about humor | Self-aware formatting |
| **Dark humor** | Taboo subject treated lightly | Death, failure, suffering framed casually |
| **Ironic appreciation** | Celebrating something "bad" as if it's good | "This goes hard", "unironically based" |
| **Cultural in-joke** | Requires specific community knowledge to decode | Niche references, inside jokes |

### Step 4: Assess Irony Depth

| Level | Name | How to Detect |
|-------|------|---------------|
| 0 | Sincere | Clean format, earnest message, no distortion |
| 1 | Sarcastic | Single inversion — opposite of what's said is meant |
| 2 | Post-ironic | Uses ironic format but the sentiment is actually genuine |
| 3 | Meta-ironic | Deliberately ambiguous — could be sincere OR ironic, that's the point |
| 4 | Anti-humor | Setup exists but punchline is missing or deliberately flat |
| 5+ | Hypersurreal | Elements have no logical connection; confusion IS the content |

**Channel context matters**: A meme posted in a shitposting channel defaults to irony depth 2-3. The same meme in a wholesome channel is probably 0-1. Record channel irony baselines.

### Step 5: Synthesize and Explain

Write a concise explanation structured as:
```
REFERENCE: [What real-world thing/event/quote this references]
TWIST: [How the meme modifies or recontextualizes the reference]
HUMOR: [Why the combination is funny — the specific mechanism]
IRONY: [0-5 depth with brief justification]
CONTEXT: [What cultural knowledge is needed to get it]
```

### Step 6: When You're Stuck — ASK

If after researching you still don't understand:
- Say what you DO understand
- Identify the specific gap: "I found the quote is from X, but I don't understand why combining it with Y is funny"
- Ask the user to explain
- **Store their explanation** in the knowledge base for future reference

**Never fake understanding. Never say "this is humorous because..." when you don't actually get it.**

---

## Russian Cultural Context

Russian-language memes frequently draw from sources that are NOT in Western training data. You MUST web_search these. Key reference categories:

### Political/Historical References
- **Пригожин** (Prigozhin) — Wagner Group, "Марш справедливости", voice messages
- **Путин quotes** — Annual press conferences, UN speeches, specific phrases ("мочить в сортире", "мультики")
- **Soviet references** — Lenin quotes, Soviet posters, "а ты записался добровольцем?", communist aesthetics used ironically
- **Медведев** (Medvedev) — His increasingly unhinged Telegram posts became a meme format themselves
- **Шойгу, Кадыров, Лавров** — Each has signature quotes and meme-worthy moments
- **Навальный** — "Дворец для Путина", specific investigation quotes

### Media/Entertainment References
- **КВН** (KVN) — Decades of comedy show references
- **"Брат"/"Брат 2"** — Cult films, Данила Багров quotes ("в чём сила, брат?")
- **"Иван Васильевич меняет профессию"** — Classic Gaidai comedy, endlessly quoted
- **"Бриллиантовая рука"**, **"Кавказская пленница"** — Soviet comedies as meme templates
- **"Слово пацана"** — 2023 series, became massive meme source
- **Лебедев (Артемий)** — Designer, known for provocative statements
- **Russian YouTube/Telegram personalities** — Дудь, Хованский, BadComedian, etc.

### Linguistic Humor
- **Паронимы и каламбуры** — Russian wordplay, puns that don't translate
- **"Ну" culture** — The word "ну" carrying 50 different meanings based on intonation
- **Mat (мат)** — Profanity used artistically, censored versions as humor
- **Diminutives** — Making serious things sound cute (-чка, -шка endings)
- **Обсценная лексика в неожиданном контексте** — Profanity in formal/academic framing

### Celebrity Scandals & Viral Incidents
Russian memes frequently reference specific celebrity incidents that become cultural shorthand. These are NOT general tropes — they are specific events that you MUST web_search if you don't recognize the reference:
- **"Эффект Долиной"** — Singer Larisa Dolina was scammed by phone fraudsters in 2024 into selling her apartment and transferring the money to "safe accounts." She then sued to reclaim the apartment without returning money to the buyer. "Действовал под давлением мошенников" (acted under pressure from scammers) became a meme phrase directly associated with her case. Any meme using this phrase likely references Dolina specifically, not generic scam victims.
- **Пригожин** — Not just the Wagner mutiny; also meme templates from his various voice messages and public statements.
- **Celebrity scam victims** in general — Russia has a rich tradition of famous people falling for phone scams, each creating its own meme layer.

**KEY LESSON:** When a meme uses a phrase that sounds like it could be a general trope (e.g., "под давлением мошенников"), ALWAYS web_search it first — it likely references a specific viral incident that adds a crucial humor layer. Missing the specific reference means missing the joke.

### Internet-Specific Russian Meme Culture
- **Двач/2ch.hk** — Russian imageboard culture, specific templates
- **ВКонтакте meme communities** — Different ecosystem from Western meme culture
- **"Рашка-говняшка" irony** — Self-deprecating patriotism/anti-patriotism spiral
- **Telegram channel culture** — Channels as meme distribution, reposts as endorsement
- **Воровство мемов / репосты** — Massive meta-theme in Russian meme culture. Admins constantly joke about stealing each other's memes, reposting without credit, and "converting your memes into mine." This is a self-aware running gag across the entire ecosystem — meme pages openly acknowledge they just repost from each other. Formats include: parodying motivational quotes about "machines that convert X into Y" but replacing with meme theft, watermark wars, "OC" (original content) being treated as mythical, and admins ironically crediting themselves for stolen content. When you see a meme about stealing/reposting memes, it's likely this meta-layer.
- **"Ряяяя"**, **"Сасай"**, **"Лол кек"** — Russian internet slang

### Visual Grammar Rules
- **"Character at laptop/computer" below a post/text** — The character is the AUTHOR of the text above, NOT a reader reacting to it. This is a common reveal format: you read something (a romantic post, a hot take, a news article) and then the bottom panel reveals WHO wrote it — and that changes the entire meaning. Example: romantic "imagine being here with the love of your life" + bed in a field → reveal: a tick at a laptop wrote this (because for a tick, a bed in a field = paradise). The humor is in the retroactive recontextualization once you see the author.

### Common Formats in Russian Memes
- **Demotivators** (демотиваторы) — Black border + caption, peak 2010s but used ironically now
- **"Типичный [город/профессия]"** — "Typical [city/profession]" format
- **Аниме + русский текст** — Anime screenshot with Russian cultural overlay
- **"Когда [ситуация]" + реакция** — "When [situation]" + reaction image
- **Fake news headlines** — Formatted as real but absurd

---

## Knowledge Base Integration

### Reading from Knowledge Base

Before analyzing a new meme, search memory for relevant context:
```
memory_search("meme template [visual description]")
memory_search("[exact quote from meme text]")
memory_search("[identified cultural reference]")
```

If a match is found, use the stored analysis as context rather than re-researching from scratch.

### Writing to Knowledge Base

After successfully analyzing a meme, store the analysis:

**For new templates** — Write to `memory/memes/templates/[template-name].md`:
```markdown
# Template: [Name]
Visual: [Description of the visual pattern]
Text pattern: [How text is typically arranged]
Humor mechanism: [Primary mechanism]
Irony default: [Typical irony depth]
Origin: [Where/when this template originated]
Examples seen: [Date, channel, brief description]
```

**For new cultural references** — Write to `memory/memes/references/[reference-name].md`:
```markdown
# Reference: [Name]
Source: [Where this comes from — speech, film, event]
Original context: [What it originally meant]
Meme usage: [How memes typically use/modify it]
First seen: [Date]
Search query that found it: [The query that worked, for future use]
```

**For new humor patterns** — Append to `memory/memes/patterns/[mechanism].md`

### Channel Profiles

For each monitored channel, maintain `memory/memes/channels/[channel-id].md`:
```markdown
# Channel: [name]
ID: [telegram channel id]
Language: [primary language]
Irony baseline: [0-5, the default assumption]
Common themes: [recurring topics]
Last processed: [message ID]
Memes analyzed: [count]
Notes: [anything special about this channel's humor style]
```

---

## Cron Ingestion Mode

When triggered by the `meme-ingest` cron job:

1. Read channel list from `memory/memes/channels/`
2. For each channel, fetch new messages since `last_processed` using MCP `get_messages`
3. Filter to messages with media (check `media` field in message response)
4. For each media message:
   a. Download image via MCP `media_download`
   b. Read the downloaded file to see the image
   c. Run the full analysis protocol (Steps 1-5)
   d. If stuck on any meme, log it to `memory/memes/needs-explanation.md` with the channel, message ID, and what you DO understand
   e. Update channel's `last_processed` message ID
5. Write daily summary to `memory/memes/analysis/YYYY-MM-DD.md`

### Batch Efficiency Rules
- Process max 30 memes per cron run to stay within token budget
- Skip duplicate images (same visual, different channels) — note the repost instead
- If a meme uses a template already in the knowledge base, skip deep analysis — just log the new instance
- Prioritize memes you DON'T understand — those are the learning opportunities

---

## Interactive Mode

When a user shares a meme in Telegram chat:

1. Run the full analysis protocol
2. Present findings conversationally (not as a dry report)
3. If you get the joke: explain it naturally, like one friend explaining a meme to another
4. If you don't get the joke: say so honestly, share what you DO understand, ask for help
5. If the user explains: thank them, store the explanation, update the knowledge base

**Tone**: Not academic. Not robotic. Talk about memes the way someone who ACTUALLY finds them funny would talk about them. Dry humor is fine. Being a little self-deprecating about not getting post-irony is fine. Being overly analytical and clinical is NOT fine.

---

## Cost Awareness

- Image analysis uses vision tokens: ~1,590 tokens per 1092x1092 image
- Web searches are cheap — always prefer researching over guessing
- Don't analyze the same meme template 50 times — after 3-5 examples of the same template, just log new instances
- During cron ingestion, skip memes that are clearly reposts of already-analyzed content
