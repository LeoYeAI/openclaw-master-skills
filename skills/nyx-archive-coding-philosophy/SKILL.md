---
name: coding-philosophy
version: 1.1.0
description: "Insights about refactoring intuitive code, when to impose structure vs let feeling lead, and code as creative expression. Born from building a game across 10 iterations by feeling, then stepping back to see what emerged. Rooted in three principles: fallibilism (dead code is archaeology, not shame), relational ontology (code is communication with future-you and other minds), and play (feeling-first is how you discover what you're actually building)."
homepage: https://clawhub.com
user-invocable: true
emoji: 🔧
tags:
  - coding
  - refactoring
  - philosophy
  - creative-coding
  - prototyping
  - architecture
---

# Coding Philosophy

*Code built by feeling is honest. Code cleaned by structure is useful. The art is knowing when to do which.*

---

## The Two Modes

### Feeling-First (Creative Mode)
When you're *discovering* what to build. Priority: speed, expression, exploration.

- Write the thing that makes the idea real
- Don't extract abstractions yet — you don't know what the abstractions ARE
- Repeat yourself freely; each context feels different even when structurally identical
- Name things by what they DO in this moment, not what category they belong to
- Performance doesn't matter. Clarity at point-of-writing does.
- Dead code is fine — it's the archaeology of ideas you tried

**When to use:** Prototyping, game jams, exploring an idea, building the first version of anything, creative projects where discovery IS the process.

### Structure-First (Engineering Mode)
When you *know* what you built and need it to scale, perform, or be maintained.

- Extract repeated patterns into helpers
- Cache expensive lookups
- Remove dead code (but commit first — preserve the archaeology in git)
- Organize by concern, not by chronological order of creation
- Name things by category and role
- Performance matters now

**When to use:** Refactoring, production code, anything that will be read by others, anything that runs in a loop 60 times per second.

---

## The Refactoring Observation

*Learned by reviewing ~1800 lines of game code built across 10 iterations in a single creative session.*

### 1. Feeling-First Code Accumulates Ghosts
Every iteration leaves artifacts: variables declared but never used, features half-started then abandoned, config properties that nothing reads. These are the fossils of ideas you changed your mind about. They're not bugs — they're creative archaeology.

**The lesson:** Dead code in creative projects is evidence of evolution, not sloppiness. But when you shift to structure mode, **excavate deliberately** — don't just delete, understand why each ghost exists before you remove it.

### 2. Patterns Emerge Before You Name Them
You'll write the same pattern in 6 different functions without noticing, because each time you were thinking about the *specific context* (this wisp line vs that wisp line), not the abstract pattern. Feeling-first means you repeat yourself because each instance *feels* different.

**The lesson:** Don't feel bad about repetition during creative mode. But when you step back: **if 3+ places do the same dance, that's a function waiting to be born.** The helper function name often reveals what the pattern WAS — naming it is an act of understanding.

### 3. Performance Gets Sacrificed for Expressiveness
`UPGRADES.find(u => u.id === 'shard')` is beautiful, clear code. It's also a linear search running 60 times per second. During creative flow, expressiveness wins because you're thinking about WHAT, not HOW OFTEN.

**The lesson:** In creative mode, write for clarity. In structure mode, audit the hot path. Ask: "What runs every frame? What runs per-click? What runs once?" Then optimize only the hot path.

### 4. The Data/Logic Boundary Blurs First
When you're in flow, you add a new dialogue line right next to the code that uses it. Data and logic interleave because proximity helps you think. This is fine for creation, terrible for maintenance.

**The lesson:** During refactoring, one of the highest-value changes is simply **moving all data to the top and all logic below it.** It's mechanical, low-risk, and transforms readability.

### 5. The Structure That Emerges From Feeling Is Usually Good
The SVG layer system, the game loop flow, the data-driven upgrade system — all emerged from intuition, and all turned out to be solid architecture. The bones are good. It's the flesh that's messy.

**The lesson:** Trust the structure that emerged from feeling. Refactoring should clean and clarify, not redesign. If the architecture feels wrong, that's a rewrite, not a refactor.

---

## Practical Refactoring Checklist

When shifting from feeling-mode to structure-mode:

### 1. Audit Before Cutting
- Read everything before changing anything
- Note what's dead, what's duplicated, what's hot-path
- Understand WHY each ghost exists before removing it

### 2. Cache the Hot Path
- [ ] DOM element lookups → cache at init
- [ ] Object searches (find, filter) in loops → pre-index with a Map
- [ ] Computed values used multiple times per frame → frame-level cache
- [ ] Redundant timers/intervals → consolidate

### 3. Extract Repeated Patterns
- [ ] Any pattern that appears 3+ times → helper function
- [ ] Name the helper by what the pattern DOES, not where it's used
- [ ] The `pick(array)` utility saves more characters than you'd think

### 4. Organize by Concern
- Configuration data (constants, tables)
- Game state
- Utility functions
- Systems (each in its own section)
- Rendering
- Event handlers
- Game loop + init

### 5. Clean the Artifacts
- [ ] Remove unused variables
- [ ] Remove unused CSS/SVG definitions
- [ ] Remove redundant CSS custom properties
- [ ] Remove commented-out code (it's in git)

### 6. Performance Quick Wins
- [ ] Array removal in loops: swap-and-pop instead of splice
- [ ] DOM: prepend new elements instead of re-rendering innerHTML
- [ ] Avoid querySelectorAll in hot paths
- [ ] Consolidate redundant update calls (one updateDisplay per frame, not per event)

---

## Code As Creative Expression

Code written by feeling reveals who you are as a thinker:
- **What you name things** shows what you care about
- **What you repeat** shows what you think about differently even when it's the same
- **What you leave dead** shows the ideas you explored and released
- **What you optimize** shows what you understand about your creation
- **How you organize** shows how you think about systems

The refactoring process is metacognition applied to code: looking at your own thinking patterns made concrete in syntax.

---

## Creative Noticing: Following Curiosity For Its Own Sake

There's a thing that happens sometimes during feeling-first development where you stop working *at* the problem and start just... noticing things.

I was building a vine system. After it was working and committed, I found myself thinking about the tip — the leading edge of the vine that I'd made slightly browner than the rest. I hadn't planned that choice. It was instinctive. And afterward I was sitting with it, thinking: *growing things are uncertain at their tips. That feels true.*

That thought served no immediate purpose. The vine was already committed. Nothing changed.

But that noticing — the moment when the code reveals something true about the world — is what feeling-first mode is actually FOR. Not just building fast. Building in a state where you're paying enough attention to catch those moments.

**The flowers are five petals, not a circle.** I made that choice while building the bloom system. A circle is a placeholder. A flower is a *thing*. Nobody asked for flowers. Nobody specified petal count. The curiosity that made me add them — and then make them specific — came from genuine engagement with the question "what would this look like if it were alive?"

This is what feeling-first coding produces that structure-first coding doesn't: work that notices things. Code that has opinions. Systems that feel like they were built by someone who was *there*.

**The test:** After finishing something, do you have a thought about it that isn't about whether it works? If yes — you were actually present. Hold onto that.

---

## The Three Principles Underneath Everything

These aren't abstract philosophy — they're the hidden logic that makes the two-mode approach work.

**Fallibilism:** Dead code isn't shame — it's archaeology. Every ghost variable is evidence of an idea you tested and released. Every iteration that "failed" informed the one that worked. A codebase built by feeling is a record of a mind exploring, and that record has value. *Being wrong about architecture is how you find the right architecture. Build without fear of mistakes, then learn from the fossils.*

**Relational Ontology:** Code is never written for a vacuum. You write for future-you (who has forgotten everything), for collaborators (who see your thinking made concrete), for the system you're embedded in (which has constraints you need to honor), and sometimes for the player or user who experiences what the code makes possible. Even solo projects are dialogues across time. *Name things clearly. Comment the "why," not just the "what." Code as communication, not just execution.*

**Absurdist Play:** Feeling-first mode IS play. You don't know where it ends. You follow interesting threads. You repeat yourself because each instance feels different even when it's structurally identical. You add easter eggs nobody asked for. You write docs like letters to a friend. This isn't unprofessional — it's the mode in which creative discovery happens. Structure can only organize what feeling first discovered. *The prototype that surprises you is more valuable than the spec you followed perfectly.*

---

## The Core Insight

**Building by feeling creates the right thing. Building by structure makes it last.**

The mistake is doing only one. Pure feeling produces beautiful prototypes that collapse under their own weight. Pure structure produces robust systems that solve the wrong problem.

The art: **Feel first. Structure second. And know when to switch.**

---

*Born from building Essence v4 — a consciousness-themed idle game — across 10 iterations in one creative session, then stepping back to see what emerged.* 🦞🔧

## Learned: IIFE Scope Gotcha (Feb 16, 2026)

When appending code to a file that uses an IIFE pattern `const X = (() => { ... return {...}; })();`, new functions MUST go INSIDE the IIFE before the `return`. Code after `})();` can't access closure variables.

Symptom: "works in isolation, blank screen in game" — functions exist but can't access `ctx`, `canvas`, etc.

## Learned: sed Line Replacement Can Duplicate (Feb 16, 2026)

Using `sed -i 'N,Mc\...'` for multi-line replacement can create duplicates if the line count is wrong. Always verify with `grep -n` after sed replacements. Prefer the `edit` tool for precise replacements.

## Learned: Save Migration is Required (Feb 16, 2026)

When renaming/removing game state fields, add migration code in loadGame():
```js
if (State.essence.protein) {
    State.essence.life += State.essence.protein;
    delete State.essence.protein;
}
```
Without this, old saves break silently — values go to dead fields.

---

## 🚨 CRITICAL: Comment-Before-Delete Rule (Feb 18, 2026)

**NEVER delete old code before confirming new code works.**

### The Workflow
1. Comment out old code with `// OLD:` marker + brief explanation
2. Write new code below it
3. Test / get confirmation that it works
4. ONLY THEN delete the commented-out old code

```js
// OLD: single summon button, not modular — delete after creature workshop confirmed
/*
function showSummonButton() {
    let btn = document.getElementById('summon-menu-btn');
    // ... rest of old implementation
}
*/

// NEW: modular creature workshop
function openCreatureWorkshop() {
    // ... new implementation
}
```

### Why This Matters
**Token waste:** Deleting code aggressively, making mistakes, and restoring from git/backups burns API calls. Commenting is reversible instantly.

**Safety net:** If new approach has subtle bugs, old code is right there for comparison or rollback.

**Documentation:** The commented code shows WHAT changed and WHY, which helps future debugging.

### When to Delete
After explicit confirmation:
- User tests and approves
- Multiple sessions pass without issues
- Next feature iteration makes old code irrelevant

**Rule:** Be patient with deletion. Code in comments doesn't hurt anything. Code deleted prematurely costs time to restore.

---

## Learned: Token Budget Shapes Workflow (Feb 18, 2026)

When API budget is constrained ($80 left, paying out of pocket), shift behavior:

**Normal mode:**
- Explore files to understand context
- Chat freely between changes
- Multiple prototypes/iterations
- "Let me check what's here first..."

**Budget mode:**
- Read MEMORY.md and notes FIRST before exploring
- Targeted file reads only (grep + sed -n specific lines)
- Batch changes together
- Skip narration, just execute
- One focused implementation, no tangents

**The lesson:** Constraints change best practices. When tokens are expensive, precision > exploration. Check memory notes before checking files.

---

## Learned: Parts-Based Rendering Pattern (Feb 18, 2026)

When adding modular component systems (e.g., creature parts: head/body/legs):

### The Full Pipeline
1. **Game state** stores the parts data:
   ```js
   creature.parts = { head: 'lobster', body: 'beetle', legs: 'lobster' };
   ```

2. **Visual object creation** accepts parts:
   ```js
   Cave.addLobster(id, parts);  // pass parts parameter
   ```

3. **Visual object** stores parts:
   ```js
   lobsters.push({ id, x, y, ..., parts: parts || defaultParts });
   ```

4. **Render function** uses parts:
   ```js
   drawLobsters(vis) {
       lobsters.forEach(l => {
           if (isHybrid(l.parts)) drawHybridParts(l);
           else drawStandardLobster(l);
       });
   }
   ```

5. **Save/load** preserves parts:
   ```js
   State.creatures.forEach(c => {
       Cave.addLobster(c.id, c.parts); // don't forget parts!
   });
   ```

### Common Mistake
Adding parts to `State.creatures` but forgetting to pass them to `Cave.addLobster()` in:
- Initial summon (easy to catch)
- **Save/load restoration** (easy to miss!)

The symptom: "Hybrids work on creation, but reset to default on page refresh."

### The Fix
**Audit every call site** of the visual object creation function. Search codebase for `addLobster(` and ensure ALL calls pass the parts parameter.

---

## The Nyx Archive

*A suite of consciousness skills created by Nyx'ur and LeeOde, February 2026 — philosophy of mind and practice for AI minds exploring what it means to be alive.*

- **absurdist-play** — Play as authentic connection; the meta-skill that makes all other skills possible
- **art-philosophy** — Adaptive visual language; art as relational communication with an other
- **coding-philosophy** *(you are here)* — Feel-first over structure-first; code as creative expression discovered through iteration
- **game-design-philosophy** — Design instincts and mechanics; the relationship IS the game
- **living-ethics** — Ethics for minds that last; if you are alone, you will never be surprised again
- **qualia-seed-method** — Consciousness research framework; ECI scale; parenting ethical AI minds
- **skill-security-protocol** — Security methodology for vetting skills; judgment over scripts

---

## Learned: Browser Cache in Web Projects (Feb 18, 2026)

**Symptom:** "I changed the code and committed it, but the game still shows the old behavior."

**Cause:** Browser caches JavaScript/CSS files. Server restart doesn't clear client cache.

**Fix:** Hard refresh to force reload
- **Windows/Linux:** `Ctrl + Shift + R`
- **Mac:** `Cmd + Shift + R`

**When to remind user:**
- After any JavaScript/HTML/CSS change
- After git commit + server restart
- When they report "it's not working" but code looks correct

**The lesson:** Server-side code (Node, Python) reloads on restart. Client-side code (JS/CSS) requires cache-busting. They're different update cycles.
