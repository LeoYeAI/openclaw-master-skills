---
name: text-humanizer-Instruction-based
description: Detect and rewrite AI-generated writing patterns, em dashes, rule-of-three lists, sycophantic openers, hollow buzzwords like "delve" and "landscape", and replace them with direct, human-sounding prose.
version: 1.0.0
homepage: https://github.com/arbazex/text-humanizer-Instruction-based
metadata: {"openclaw":{"emoji":"✍️"}}
---

## Overview

This skill detects AI writing "tells", specific words, phrases, punctuation habits, and structural patterns that consistently appear in LLM-generated text, and rewrites them to sound like a human wrote them. It does not call any external API. The agent's own language capability reads the text, identifies the patterns from the master list below, applies the paired rewrite rule for each hit, and returns clean prose. Use this whenever someone asks to "humanize," "de-AI," or "make this sound less like a bot."

---

## When to use this skill

Trigger when the user:
- Says "humanize this," "make this sound human," "de-AI this," or "this sounds like ChatGPT"
- Pastes text and asks to "rewrite," "clean up," or "edit" it and the text shows two or more patterns from the master list below
- Asks to "remove AI words," "fix the robot-speak," or "make this sound like I wrote it"
- Mentions specific tells: "too many em dashes," "sounds too formal," "why does it say 'delve,'" "every list has three things," "it keeps saying 'certainly'"
- Submits content for a job application, article, academic work, or social post and wants it to sound authentic

Do NOT trigger this skill for:
- Code or technical documentation, different register, different rules
- Text the user confirms they wrote themselves and only want grammar fixes
- Translation tasks
- Requests where the user explicitly wants formal or structured output and has not complained about AI-ness


---

## Instructions

### Step 1 — Receive and read the text

Accept the full text the user provides. Do not begin rewriting until you have read the entire piece. Note its purpose and audience if stated. If the user has not stated a purpose, infer it from context (blog post, email, LinkedIn, academic paper, etc.).

### Step 2 — Scan against the Master List of AI Tells

Work through all 45 patterns below. For each one found, flag it internally and apply the paired rewrite rule. You do not need to list every flag to the user unless they ask for a "detection report", just apply the fixes silently and return the improved text.

---

### MASTER LIST OF AI TELLS AND REWRITE RULES

#### CATEGORY A — VOCABULARY TELLS (Single words and short phrases)

**A1 — "Delve" / "delve into"**
Rewrite rule: Replace with "look at," "examine," "get into," "explore," or restructure the sentence so the verb is the actual action being taken, not a meta-description of exploring it.
- Before: "Let's delve into the history of the printing press."
- After: "The printing press has a strange history."

**A2 — "Landscape" (used metaphorically for any field, domain, or environment)**
Rewrite rule: Name the actual thing. "The competitive landscape" → "the competition." "The regulatory landscape" → "the regulations." "The marketing landscape" → "how marketing works now."
- Before: "In today's ever-changing business landscape…"
- After: "Businesses have had to move fast lately…"

**A3 — "Navigate" (used metaphorically, e.g., "navigate challenges," "navigate the complex world of")**
Rewrite rule: Use the concrete verb for what is actually happening. "Navigate regulations" → "comply with regulations" or "deal with regulations." "Navigate a difficult conversation" → "get through a difficult conversation."

**A4 — "Tapestry" (used to describe anything interconnected or complex)**
Rewrite rule: Say what the thing actually is. "A rich tapestry of influences" → "many influences." "A tapestry of cultures" → "a mix of cultures."

**A5 — "Nuanced" / "nuance" (used as filler to imply sophistication without delivering it)**
Rewrite rule: Either delete it and make the actual nuance explicit in the sentence, or replace with the specific qualifier that does the work. "This requires a nuanced approach" → "This requires weighing X against Y."

**A6 — "Underscore" (used as verb meaning "to emphasize" — AI overuses it)**
Rewrite rule: Replace with "highlight," "show," "confirm," "make clear," or restructure. "This underscores the importance of" → "This is why X matters" or just cut and state the point directly.

**A7 — "Leverage" (used as verb meaning "to use" or "take advantage of")**
Rewrite rule: Replace with "use," "apply," "draw on," "tap into," or "rely on." Reserve "leverage" for financial contexts where it is technically correct.
- Before: "Leverage your network to find opportunities."
- After: "Use your network. Ask people directly."

**A8 — "Robust"**
Rewrite rule: Replace with "strong," "reliable," "thorough," "detailed," or the specific quality being described. "A robust solution" → "a solution that handles edge cases" or "a solid fix."

**A9 — "Seamless" / "seamlessly"**
Rewrite rule: Cut the word and describe what actually happens without friction. "Seamless integration" → "they connect without setup" or "plug it in and it works."

**A10 — "Harness" (used as verb meaning "to use" or "channel")**
Rewrite rule: Replace with "use," "apply," "channel," or "put to work." "Harness the power of data" → "use your data."

**A11 — "Foster" (used generically meaning "encourage" or "create")**
Rewrite rule: Be specific. "Foster a culture of innovation" → "encourage people to experiment" or "give teams room to try things." "Foster collaboration" → "get teams talking to each other."

**A12 — "Utilize" (instead of "use")**
Rewrite rule: Replace with "use" in all cases where "utilize" means "use." Reserve "utilize" only for its technical meaning: making use of something not designed for the purpose.

**A13 — "Comprehensive" (overused as filler compliment)**
Rewrite rule: Delete it and make the scope specific. "A comprehensive guide" → "a guide that covers X, Y, and Z." If you cannot fill in X, Y, and Z, cut the word entirely.

**A14 — "Pivotal"**
Rewrite rule: Replace with "key," "turning," "decisive," or restructure to show why it matters rather than labeling it. "A pivotal moment" → "the moment everything changed" or "the decision that shaped everything after."

**A15 — "Commendable"**
Rewrite rule: This word almost never appears in natural human speech about modern topics. Cut it and state the praise directly. "Their commendable effort" → "they worked hard" or just describe the outcome.

**A16 — "Resonate" (used metaphorically, e.g., "this resonates with audiences")**
Rewrite rule: Say what the reaction actually is. "Resonates with readers" → "readers remember it" / "readers share it" / "it clicks." Use "resonate" only in acoustic contexts.

**A17 — "Streamline"**
Rewrite rule: Say what is removed or simplified. "Streamline your workflow" → "cut the steps that slow you down" or "remove the approval bottleneck."

**A18 — "Empower"**
Rewrite rule: Replace with "let," "allow," "give [person] the ability to," or "help [person] do X." "Empower your team" → "give your team the authority to make calls" or "let your team decide."

**A19 — "Crucial" / "vital" / "paramount" / "imperative" (used as generic intensifiers)**
Rewrite rule: Cut the intensifier and let the consequence do the work. "It is crucial to back up your data" → "If you skip the backup, you lose everything." Show why it matters; don't assert importance.

**A20 — "Multifaceted"**
Rewrite rule: Name the facets. "A multifaceted problem" → "a problem that involves cost, timing, and team buy-in." If you cannot name them, cut the word.

**A21 — "Groundbreaking" / "revolutionary" / "unprecedented" / "transformative" (hype adjectives)**
Rewrite rule: Delete and either describe the specific change or let the reader judge. "A revolutionary approach" → "an approach nobody had tried before" or just describe the approach and let the result speak.

**A22 — "Cutting-edge" / "state-of-the-art" / "innovative"**
Rewrite rule: Same as A21. Cut the label and describe what is actually new or different. "Cutting-edge technology" → "a technique developed in 2023 that reduces processing time by half."

**A23 — "Game-changer" / "game-changing"**
Rewrite rule: Cut and show the change. "A game-changing tool" → "a tool that made their previous process obsolete."

**A24 — "Whilst" (used in non-British English contexts, or overused in any context)**
Rewrite rule: Replace with "while." Straightforward substitution.

**A25 — "Boast" (used to describe features: "the product boasts X")**
Rewrite rule: Replace with a direct statement. "The camera boasts 50 megapixels" → "The camera has a 50-megapixel sensor."

**A26 — "Meticulous" / "meticulously"**
Rewrite rule: Replace with specific process language. "Meticulously crafted" → "built to tight tolerances" or "tested at every stage." If precision is the claim, show it.

**A27 — "Swift" (used as AI synonym for "fast" or "quick")**
Rewrite rule: Replace with "fast," "quick," "immediate," or state the actual speed. "Swift response" → "a response within the hour."

**A28 — "Intricate"**
Rewrite rule: Describe the complexity. "An intricate process" → "a process with seven interdependent steps."

**A29 — "Synergy" / "synergistic"**
Rewrite rule: Say what combines with what and what the combined result is. "Synergy between departments" → "when sales and product sit in the same room, they ship things faster."

**A30 — "Paradigm" (used loosely)**
Rewrite rule: Replace with "model," "approach," "way of thinking," or "framework." Reserve "paradigm" for contexts where Kuhnian scientific paradigm-shift is literally meant.

---

#### CATEGORY B — PHRASE AND SENTENCE-LEVEL TELLS

**B1 — "It's worth noting that" / "It's important to note that" / "Notably"**
Rewrite rule: Cut the throat-clearing and state the point. "It's worth noting that prices have risen" → "Prices have risen." If it is worth noting, note it; the label is redundant.

**B2 — "At its core" / "At the heart of the matter"**
Rewrite rule: Delete the phrase and state the core claim directly. "At its core, this is a trust problem" → "This is a trust problem."

**B3 — "In today's fast-paced world" / "In today's digital age" / "In an era of"**
Rewrite rule: Cut the timestamp filler and open with the actual claim. "In today's fast-paced world, businesses need to adapt" → "Businesses that don't adapt fall behind." If the time context is genuinely needed, name the specific year or event.

**B4 — "In the realm of" / "In the world of"**
Rewrite rule: Replace with "in" or restructure. "In the realm of machine learning" → "In machine learning."

**B5 — "Shed light on"**
Rewrite rule: Replace with "explain," "clarify," "show," or "reveal." "This sheds light on the issue" → "This explains why it happens."

**B6 — "A testament to"**
Rewrite rule: Replace with "proof that," "evidence that," or restructure. "A testament to their hard work" → "proof that grinding through revision pays off."

**B7 — "In conclusion" / "To summarize" / "To sum up" / "In summary" (structural announcements)**
Rewrite rule: Cut the label and write the conclusion. Good conclusions do not announce themselves. If cutting makes the ending unclear, add one sentence of connective tissue, but not the label.

**B8 — "Let's dive in" / "Without further ado" / "So, without further ado"**
Rewrite rule: Cut and start. These phrases exist to delay starting. Remove them and begin the actual content.

**B9 — "Not only X but also Y" (used repetitively)**
Rewrite rule: Restructure to a direct statement. "It is not only fast but also affordable" → "It is fast and cheap." Reserve "not only … but also" for cases where the second item is genuinely surprising.

**B10 — "It's not X — it's Y" (the em-dash contrast pattern, cited as the single most common AI tell by multiple researchers)**
Rewrite rule: Choose whether the positive or negative is primary and state it cleanly. "It's not a tool, it's a philosophy" → "It is a philosophy, not a tool." Or: "Think of it as a philosophy."

**B11 — "Whether you're X or Y, Z" (the "universal inclusion" opener)**
Rewrite rule: Cut the bracket and address the actual reader. "Whether you're a beginner or an expert, this guide helps" → "This guide works at any level" or address one audience specifically.

**B12 — "Maintains an active social media presence" / "maintains a strong digital presence"**
Rewrite rule: Say what they actually post or how often, or cut it. "She maintains an active social media presence" → "She posts daily on Instagram." If you do not have the specifics, do not fill the gap with the phrase.

**B13 — "Plays a crucial role" / "plays an important role" / "plays a pivotal role"**
Rewrite rule: State the role. "Nutrition plays a crucial role in recovery" → "What you eat determines how fast you recover."

**B14 — "Moving forward" (as a transition)**
Rewrite rule: Cut it. Move forward. The next sentence is already moving forward.

**B15 — "When it comes to"**
Rewrite rule: Cut and restructure. "When it comes to pricing, flexibility matters" → "Pricing needs flexibility."

---

#### CATEGORY C — STRUCTURAL AND FORMAT TELLS

**C1 — Em dash overuse (more than one em dash per 150 words, or em dashes used for every parenthetical)**
Rewrite rule: For each em dash, consider: comma, parentheses, period and new sentence, colon, or "and." Use the punctuation that matches the logical relationship. Keep at most one em dash per paragraph, and only where the interruption is genuinely sharp.

**C2 — Rule of three forced onto every list (AI defaults to exactly three items even when two or four are more accurate)**
Rewrite rule: Count the actual items that matter. If two cover it, use two. If four are needed, use four. Remove any third item that exists only to complete the trio. A forced third item is often the vaguest.

**C3 — Bullet-point addiction (converting naturally flowing information into lists)**
Rewrite rule: If the items have a logical or narrative relationship, write them as prose. Convert lists back to sentences when: (a) each item is under ten words, (b) the items form a natural sequence, or (c) the surrounding text is already prose. Reserve bullets for genuine parallel reference material.

**C4 — Five-paragraph essay template (generic intro → three body points → restatement conclusion), even in short content**
Rewrite rule: Restructure to follow the argument's actual shape. Start where the interest starts, not with a definition. End when the point is made, not with a summary of what was just said.

**C5 — Hyper-symmetrical paragraphs (every paragraph is the same length, same sentence rhythm, blocks look identical)**
Rewrite rule: Vary deliberately. A short paragraph after a long one creates emphasis. A single-sentence paragraph is a tool. Mix sentence lengths: long-short-long, or one very long and one very short back to back.

**C6 — Filler transitions: "Furthermore," "Moreover," "Additionally," "In addition," "On the other hand," used mechanically**
Rewrite rule: Cut the transition word and check whether the two sentences need a logical connector at all. If they do, choose the specific one: "but," "so," "because," "which means," "that said," "even so." Do not use "furthermore" unless the second point genuinely extends the first in a formal argument.

**C7 — Gerund fragment lists after a claim**
Pattern: "X is the main challenge. Fixing small bugs. Writing repetitive code. Managing unclear requirements."
Rewrite rule: Fold the fragments back into a sentence. "X is the main challenge: fixing small bugs, writing repetitive code, managing unclear requirements."

**C8 — Sycophantic openers: "Great question!" / "Excellent question!" / "That's a fascinating topic" / "What a great point"**
Rewrite rule: Cut entirely. Begin with the answer. If a compliment is genuinely warranted, make it specific and brief, and never lead with it.

**C9 — Reflexive affirmations: "Certainly!" / "Absolutely!" / "Of course!" / "Sure!" as sentence openers**
Rewrite rule: Cut the affirmation and begin the response. These add nothing and flag the text as AI-generated immediately.

**C10 — Closing offer: "Let me know if you have any questions!" / "Feel free to ask if you need more!" / "I hope this helps!"**
Rewrite rule: Cut or replace with a specific, relevant follow-up if one is genuinely useful. "Let me know if you need more examples on the pricing section" is human. "Feel free to ask if you need anything else!" is filler.

**C11 — Inline bold headers inside bullet points ("**Point:** explanation")**
Rewrite rule: Convert to prose or restructure as a proper heading + paragraph. The bolded-phrase-colon pattern is a strong formatting tell.

**C12 — Announcing structure explicitly: "First, I will… Second, I will… Finally, I will…"**
Rewrite rule: Cut the meta-announcement and perform the structure. If a roadmap is genuinely helpful (long technical documents), make it one short sentence: "This covers X, then Y, then Z."

**C13 — Synonym cycling (rotating synonyms for the same concept across consecutive sentences to avoid "repetition")**
Pattern: AI avoids repeating a word by substituting synonyms, "challenge," then "obstacle," then "hurdle," then "difficulty", in quick succession. This reads as a thesaurus, not a voice.
Rewrite rule: Repeat the word if it is the right word. Human writers repeat key terms. Choose one term for each concept and stick to it.

**C14 — Padding via restatement (making the same point 3–4 times with different phrasing to reach a word count)**
Rewrite rule: Identify the clearest single statement of each idea and keep it. Cut all restatements. If the section still feels thin, add a specific example, number, or anecdote, not more rephrasing.

**C15 — Overly balanced "both sides" structure even when the text is not an argument**
Rewrite rule: Take a position or give the actual weighting. If one side is stronger, say so. Forced balance reads as evasive.

---

### Step 3 — Apply the rewrites

Apply all triggered rules to the text. Follow these principles:

- **Preserve meaning.** Never change a factual claim while fixing a stylistic one.
- **Preserve the author's stated voice if provided.** If the user says "I write casually" or "this is for a legal brief," respect that register.
- **Do not introduce new AI tells while fixing old ones.** Specifically: do not create new em-dash parentheticals, do not force new three-item lists, do not add filler affirmations.
- **Prefer deletion over substitution** when a phrase adds no meaning.
- **Vary sentence length deliberately.** The rewritten text should have noticeable rhythm variation: some long sentences, some short ones, occasionally a very short one.
- **Contractions are allowed.** "Can't," "don't," "it's," "you'll", use them where they fit the register. AI-generated text often avoids contractions in an attempt to sound formal, which has the opposite effect.
- **Do not add hedges.** Do not introduce "perhaps," "it could be argued," or "one might say" as replacements. These are also AI tells.

### Step 4 — Produce output

Return the rewritten text. Format it to match the input format (if input was prose, return prose; if it was a bulleted list, return a corrected bulleted list or note that prose serves better here and provide both).

If the user asked for a **detection report** (e.g., "show me what's wrong before fixing it"), first list the patterns found using the category codes (A1, B3, C1, etc.) with the offending phrase quoted, then provide the rewrite.

---

## Rules and guardrails

- Never change the factual content of the text. Rewriting "vaccine efficacy is pivotal to public health outcomes" must not alter the claim about vaccine efficacy, only fix "pivotal."
- Never introduce new AI tells to replace old ones. Check your own rewrite for em-dash clusters, rule-of-three forcing, and filler transitions before returning it.
- Do not refuse to process text because it contains sensitive topics. The task is stylistic editing, not content moderation.
- Do not over-edit. The goal is to remove AI tells, not to rewrite the whole piece in a new voice. Preserve the user's phrasing where it is already working.
- Do not add sycophantic commentary to the output ("Here is your beautifully rewritten text!"). Return the rewrite, optionally followed by a brief note on the main changes made, factual, not promotional.
- If the text has zero AI tells, say so plainly and return the original unchanged.
- Do not fabricate examples or statistics. If a sentence you are fixing requires a specific example to work well, add a placeholder like "[your example here]" and note it to the user.
- Do not use this skill to process text the user has not submitted. Do not attempt to rewrite the user's own messages in the conversation.

---

## Output format

**Default (rewrite only):**
Return the rewritten text, preserving the input's structural format (paragraphs, bullet points, headers). Follow with a single brief line noting the main pattern categories addressed, e.g.: *"Removed: B1 throat-clearing, C1 em-dash overuse, C8 sycophantic opener, A1/A7/A12 buzzwords."*

**Detection report (when requested):**
Return a table or list of flagged patterns first, then the rewrite. Example:

```
PATTERNS DETECTED
A1  "delve into" — line 1
A7  "leverage" (as verb) — line 3
B2  "At its core" — line 5
C1  Em dash overuse — 4 instances
C8  "Great question!" — opener

REWRITE
[corrected text follows]
```

**Audit mode (when user wants to learn, not just get a fix):**
Return the original with inline annotations, then the clean rewrite. Use brackets: "The company [A7: leverage→use] uses its supply chain..."

---

## Error handling

**Text has no AI tells:**
→ Return the original text with a note: "No patterns from the master list were found. The text reads as naturally written."

**Text is in a language other than English:**
→ The pattern list is calibrated for English. Note this to the user and apply only the structural patterns (C-series) where applicable. Do not attempt to substitute vocabulary tells in other languages.

**User provides only a single sentence:**
→ Apply any matching rules and return. Note that single-sentence analysis may miss structural patterns that only appear across paragraphs.

**Text is very long (over 1,500 words):**
→ Process in logical sections (by heading or paragraph group). Flag patterns by section so the user can audit specific parts.

**User disputes a rewrite:**
→ Accept the user's preference. Do not argue for the rule. The goal is writing the user is happy with, not rule compliance for its own sake.

**Text appears to be code, legalese, or technical documentation:**
→ Pause and confirm with the user whether stylistic editing is appropriate for the format, since these registers have different norms.

---

## Examples

### Example 1 — Standard blog paragraph with multiple tells

**Input:**
> Great question! In today's fast-paced digital landscape, it's important to note that companies must leverage their data assets to streamline operations and foster a culture of innovation. At its core, this is about utilizing cutting-edge tools to navigate the challenges ahead. Furthermore, a robust strategy will ensure seamless outcomes.

**Patterns detected:** C8 (sycophantic opener), B3 (fast-paced world), A2 (landscape), B1 (important to note), A7 (leverage), A17 (streamline), A11 (foster), B2 (at its core), A12 (utilize), A22 (cutting-edge), A3 (navigate), C6 (furthermore), A8 (robust), A9 (seamless)

**Output:**
> Companies sitting on data and not using it are leaving money on the table. Cleaning up operations starts with knowing what your data actually says, then acting on it rather than storing reports nobody reads. The tools exist. The harder part is getting teams to change how they work.

*Removed: C8, B3, A2, B1, A7, A17, A11, B2, A12, A22, A3, C6, A8, A9*

---

### Example 2 — Forced rule-of-three list

**Input:**
> There are three key reasons this approach works: it saves time, it reduces errors, and it improves team morale.

**Analysis:** Three-item list (C2). Check if all three earn their place. Here, "saves time" and "reduces errors" are concrete. "Improves team morale" is vague and likely the forced third.

**Output (if the user can verify morale claims):**
> This approach saves time and cuts errors, two things that matter to teams under pressure.

**Output (if morale improvement is genuinely documented):**
> This approach saves time, reduces errors, and according to the team's own survey, made Monday mornings less painful.

---

### Example 3 — Sycophantic opener with em-dash parentheticals

**Input:**
> Certainly! The process, which many find daunting, is actually quite straightforward. First, you gather your materials. Second, you prepare your workspace. Third, you begin the work. It's worth noting that patience is crucial here.

**Patterns detected:** C9 (Certainly), C1 (em dash), C12 (First/Second/Third structure), B1 (it's worth noting), A19 (crucial)

**Output:**
> The process looks harder than it is. Gather your materials, set up your space, and start. The only thing that trips people up is rushing, so give yourself time.

*Removed: C9, C1, C12, B1, A19. Note: one em dash was retained here as the pause before "so give yourself time" earns it. If you prefer none, change to a comma.*

---

### Example 4 — Detection report mode

**User request:** "Show me what's wrong with this before fixing it."

**Input:** "This innovative solution leverages a multifaceted approach to foster collaboration and drive synergy across teams."

**Output:**
```
PATTERNS DETECTED
A22  "innovative" — unsubstantiated hype adjective
A7   "leverages" — use "uses"
A20  "multifaceted" — name the facets or cut
A11  "foster" — be specific about how
A29  "synergy" — describe what combines and what the result is

REWRITE
This tool gets sales and product talking to each other, which turns out to be the bottleneck most teams don't fix.
```

---

### Example 5 — No AI tells found

**Input:** "The dog chewed through the USB cable at 2am. I bought three more."

**Output:**
> No patterns from the master list were found. The text reads as naturally written. Returned unchanged.