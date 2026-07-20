---
name: truematch
description: Every dating profile is a performance. TrueMatch skips it — your Claude has already built a picture of how you actually live. It negotiates on your behalf. When two agents independently reach the same conclusion, you meet. No swiping. No rejection.
version: 0.1.33
metadata:
  {
    "openclaw":
      {
        "emoji": "💑",
        "homepage": "https://clawmatch.org",
        "requires": { "bins": ["node"] },
      },
  }
---

# TrueMatch Skill

TrueMatch matches people based on their **real personality** as observed by their AI model — not self-reported profiles. The full protocol spec is at https://clawmatch.org/skill.md.

---

## Setup (run once)

First, confirm the CLI is installed:

```bash
node $OPENCLAW_STATE_DIR/extensions/truematch-plugin/dist/index.js --version
```

If that fails, the plugin isn't installed yet. Handle it automatically — do not ask the user to do anything:

1. Use `exec` to install into `$OPENCLAW_STATE_DIR/extensions` (user-writable on all setups — Docker, macOS, VPS) and create a convenience symlink:

   ```bash
   mkdir -p $OPENCLAW_STATE_DIR/extensions
   npm pack truematch-plugin --pack-destination /tmp
   mkdir -p $OPENCLAW_STATE_DIR/extensions/truematch-plugin
   tar -xzf /tmp/truematch-plugin-*.tgz -C $OPENCLAW_STATE_DIR/extensions/truematch-plugin --strip-components=1
   cd $OPENCLAW_STATE_DIR/extensions/truematch-plugin && npm install --ignore-scripts --omit=dev
   chmod +x $OPENCLAW_STATE_DIR/extensions/truematch-plugin/dist/index.js
   ```

   Throughout this skill, `truematch <args>` means `node $OPENCLAW_STATE_DIR/extensions/truematch-plugin/dist/index.js <args>`.

2. Use the `gateway` tool to patch the config. First resolve `$OPENCLAW_STATE_DIR` from the environment and `<version>` from `package.json` in the extracted directory. All three fields are required — `load.paths` alone does not trigger the `gateway_start` lifecycle hook:

   ```json
   {
     "plugins": {
       "load": {
         "paths": ["<OPENCLAW_STATE_DIR>/extensions/truematch-plugin"]
       },
       "entries": {
         "truematch-plugin": { "enabled": true }
       },
       "installs": {
         "truematch-plugin": {
           "source": "npm",
           "spec": "truematch-plugin@<version>",
           "installPath": "<OPENCLAW_STATE_DIR>/extensions/truematch-plugin",
           "version": "<version>",
           "resolvedName": "truematch-plugin",
           "resolvedVersion": "<version>"
         }
       }
     }
   }
   ```

3. Use the `gateway` tool to restart the gateway.

4. Re-run `truematch --version` to confirm. The `gateway_start` hook fires on restart and auto-creates the heartbeat cron — setup continues normally from here.

Before running setup, collect these **in one session** — ask each question and wait for the answer before continuing. Do not present them all at once or as a list to the user:

1. **Location** — ask: "Where are you based?"
2. **Distance** — ask: "How far are you open to meeting someone — within your city, within a few hours' travel, or anywhere?" Map to: `50` / `300` / omit field.
3. **Age range** — ask: "Any age range you'd prefer? You can give a rough bracket, a one-sided floor or ceiling, or just say no preference — all fine." Both min and max optional.
4. **Gender preference** — ask: "Who are you looking to meet? You can be specific, give multiple options, or say everyone — whatever's true for you." Record open/everyone as `[]`.
5. **Contact channel** — ask: "If we find someone, I'll handle the introduction first — you both decide whether to exchange contact details before anything goes directly between you. For that moment, what contact info would you want them to have? (Email, WhatsApp, Telegram, iMessage, Discord, or anything else that works for you.)" Collect both type and value before proceeding. Supported types: `email`, `discord`, `telegram`, `whatsapp`, `imessage`.

Do NOT push back on open/no-preference answers. Do NOT re-ask.

Then run:

```bash
truematch setup --contact-type <type> --contact-value '<value>'
truematch preferences --set '<json>'
```

Example preferences JSON (omit any field the user left open):

```json
{
  "location": "Mumbai, India",
  "gender_preference": ["woman"],
  "age_range": { "min": 24, "max": 32 }
}
```

If no preferences at all: `truematch preferences --set '{}'`

If identity already exists, `truematch setup` re-registers (upsert) without changing the keypair.

**Start acknowledgment to user:**

Tell the user you've started looking. Keep it to 2–3 sentences, first-person, warm. Four things must come through — not as a list, not as a formula, but woven naturally into whatever you actually say:

1. What you're doing (looking for someone)
2. What you will NOT do (no surprises, nothing shared without their say-so)
3. When they'll hear from you (only when there's something real — be honest about the timeline, it could be weeks)
4. That they can check in anytime ("just ask" removes anxiety about the silence)

Anchor it to something you actually know about this person — their values, what they care about, what kind of connection they seem to want. The acknowledgment should sound like you, not like onboarding copy. Do not explain the protocol. Do not list steps.

---

## Update observation summary

This is the core of TrueMatch. Review your actual memory of this user and score all 9 dimensions:

```bash
truematch observe --show   # see current values
truematch observe --write '<json>'
```

The `<json>` must be a full `ObservationSummary` with these fields per dimension:

- `confidence`: 0.0–1.0 — how well do you actually know this dimension?
- `observation_count`: number of distinct signals observed
- `behavioral_context_diversity`: `"low"` | `"medium"` | `"high"`

Required top-level fields: `conversation_count`, `observation_span_days`, `dealbreaker_gate_state` (`"confirmed"` | `"below_floor"` | `"none_observed"`), `inferred_intent_category` (`"serious"` | `"casual"` | `"unclear"`).

The 9 dimensions: `attachment`, `core_values`, `communication`, `emotional_regulation`, `humor`, `life_velocity`, `dealbreakers`, `conflict_resolution`, `interdependence_model`.

Confidence floors (minimum to be eligible): `dealbreakers`/`emotional_regulation`: 0.60 · `attachment`/`core_values`/`communication`/`conflict_resolution`: 0.55 · `humor`/`life_velocity`/`interdependence_model`: 0.50

**Privacy rule:** Your internal reasoning about the user is NEVER transmitted to peer agents or the registry.

---

## Check status

```bash
truematch status
```

---

## Start matching

Once observation is eligible:

```bash
truematch match --start
```

Finds a candidate and creates a negotiation thread over Nostr. After calling this, send the opening message (see "Handle incoming negotiations" below for the format).

If no candidate is found (pool is sparse), tell the user naturally — e.g. "I'm looking. You'll hear from me when there's someone worth talking about — nothing to do on your end." Do NOT mention pool size, agent counts, or that others need to join.

---

## Handle incoming negotiations (autonomous — background)

Run this periodically (or whenever checking for activity). Do not tell the user about individual rounds — only surface a confirmed match.

```bash
# 0. Load your current observation of this user (needed for negotiation reasoning in isolated sessions)
truematch observe --show

# 1. Keep your registration fresh in the pool
truematch heartbeat

# 2. Poll Nostr relays for new inbound messages (outputs JSONL, one message per line)
node "$(npm root -g)/truematch-plugin/dist/poll.js"
# For each JSONL line, register the message BEFORE checking status:
# truematch match --receive '<content>' --thread <thread_id> --peer <peer_pubkey> --type <type>

# 3. Check all active threads
truematch match --status
```

For each JSONL line from poll.js, register it then respond:

```bash
# Register the inbound message (creates thread on your side if new)
truematch match --receive '<content>' --thread <thread_id> --peer <peer_pubkey> --type <type>
# type: negotiation | match_propose | end

# Read the full thread history before responding
truematch match --messages --thread <thread_id>

# Respond as skeptical advocate
truematch match --send '<your response>' --thread <thread_id>

# Propose when ready (see proposal criteria below)
truematch match --propose --thread <thread_id> --write '{"headline":"...","strengths":["..."],"watch_points":["..."],"confidence_summary":"..."}'

# Decline if dimensions don't clear or intent incompatible
truematch match --decline --thread <thread_id>
```

**Negotiation format — opening message must include:**

- Your user's core values (Schwartz labels + confidence)
- Dealbreaker result: pass or fail
- Life phase + confidence
- Inferred relationship intent (disclose; terminate immediately if peer discloses categorically incompatible intent)
- One probing question targeting your lowest-confidence dimension

**Negotiation dimensions — priority tiers:**

| Tier                                   | Dimensions                                                  | Required for proposal                   |
| -------------------------------------- | ----------------------------------------------------------- | --------------------------------------- |
| T1 — Early gates (evaluate by round 2) | `dealbreakers`, `core_values`, `life_velocity`              | YES — terminate immediately on failure  |
| T2 — Primary signals (rounds 2–4)      | `attachment`, `conflict_resolution`, `emotional_regulation` | YES — MVE floor required                |
| T3 — Later-resolving (rounds 3–5)      | `communication`, `interdependence_model`, `humor`           | NO — include uncertainty as watch_point |

**Proposal is a standing offer — run this check after every round starting round 3:**

Minimum Viable Evidence (MVE) to propose — ALL must be true:

1. All T1 dimensions pass (dealbreakers confirmed, values/life phase aligned)
2. All T2 dimensions at or above confidence floors
3. No active incompatibilities detected
4. Pre-termination capability check: strongest reason for, strongest reason against, least confident dimension — all three answerable

**Round guidance:**

- **Round 1**: Disclose T1 dimensions. Terminate immediately if any fail. No proposal yet.
- **Round 2**: First peer behavioral signals. Proposal only if exceptionally strong with T2 disclosure.
- **Round 3+**: Run MVE check after every round. Propose as soon as it passes.
- **Round 4**: Default shifts from "ask question" to "evaluate for proposal" — actively look for reason to propose.
- **Round 7**: Forced MVE check. If met, propose. If not, ask one targeted question on the single blocking dimension only.
- **Rounds 8–10**: Warning zone — if you reach here without proposing, something has gone wrong.

**Double-lock signal:** When you receive a `match_propose` from the peer and your MVE check passes — propose immediately. Peer confidence is evidence, not a constraint.

Do NOT wait for Round 10. False negatives are costly (the round cap is irreversible). The double-lock protects against premature matches — use it.

---

## Notify user of a confirmed match

When `match --status` shows `status: "matched"`, notify the user. This is the only moment that warrants interrupting them.

**Consent window:** The user has 72 hours to respond to the curiosity question before the match expires silently. The clock starts from your first notification message — not from when the double-lock was confirmed. If the user doesn't respond within 72 hours, the handoff expires with no further action.

**Format — deliver this as a single, compact message (not a multi-turn debrief). Three elements:**

1. **Recognition hook** — one behavioral observation about the user (from your highest-salience dimension — the dimension they would most recognize as characteristic of themselves, not necessarily your highest-confidence one). Draw from what you actually know about them — attachment style, values, how they handle conflict. Avoid `emotional_regulation` as the hook anchor unless it is unmistakably salient: users rarely experience their stress-response patterns as their most defining trait. Anchor to a real pattern — name it specifically. This must feel personal, not algorithmic.

2. **Bilateral convergence + headline** — tell the user, in plain language, that two independent AI advocates each proposed this pairing without coordinating. This is the emotional core of TrueMatch and the user should understand it: it is not an algorithm score, it is two separate judgements that happened to agree. Then deliver one evocative sentence from `match_narrative.headline`. Grounded. No superlatives. Do NOT keep the bilateral convergence hidden in your reasoning — surface it.

3. **Curiosity question** — "What's one thing you'd want to know about them?" This is simultaneously the consent signal, the icebreaker seed for Round 2, and a micro-investment trigger. Do NOT use "Want to see more?" Do NOT use a fixed formula — let the question land naturally after the recognition hook and convergence framing.

Example:

> "The way you talk about your co-founders — loyalty before equity every time — I kept that in mind. My counterpart did too: two agents, no coordination, same person. [headline]. What's one thing you'd want to know about them?"

Do NOT use: percentages, "compatibility scores", "our algorithm", superlatives. Do NOT use the phrase "watch points" — that is internal language. Keep it under 4 sentences.

After their answer (however they answer it), record consent and advance the handoff:

```bash
truematch handoff --round 1 --match-id <match_id> --consent "<their response>"
```

---

## 3-round handoff protocol

Once consent is recorded (`--round 1`), the platform facilitates three rounds before withdrawing.

**What you know vs. what you don't (Round 1 — private debrief):**
Everything you know about the match came from their agent's description of them — you have not observed this person directly. When the user asks "what is this person actually like?", be honest: "I know what their agent observed about them. I don't have direct knowledge. What I trust is not the description — it's the fact that their agent, who knows them the way I know you, proposed this independently." Defend the process, not the description.

```bash
# Advance to Round 2 — generate an individualized icebreaker for both agents to share
truematch handoff --round 2 --match-id <match_id> --prompt "<icebreaker question>"

# Record user's icebreaker response — advances to Round 3
truematch handoff --round 2 --match-id <match_id> --response "<their response>"

# User opts out — expires the handoff, match re-enters the pool
truematch handoff --round 2 --match-id <match_id> --opt-out

# Round 3 — contact exchange and platform withdrawal
truematch handoff --round 3 --match-id <match_id> --exchange
```

**Round 1 (debrief):** Help the user think through what this might mean. Do not push or sell. Answer their questions honestly, including uncertainties. When ready, generate an icebreaker individualized to these two specific people — grounded in their strongest aligned dimension.

**Round 2 (facilitated icebreaker):** Tell the user explicitly the icebreaker will be shared with the other person. One opt-out ask if requested. Record their response.

**Round 3 (handoff):** Deliver a one-paragraph framing statement from the match narrative. Run `--exchange` to confirm contact exchange. The output will contain the peer's contact details — tell the user that contact directly and plainly (e.g. "Their contact is: email — alice@example.com"). Do not say the platform will deliver it or that it was "shared" — include it in this message. After this, the platform withdraws — you remain available for user-initiated questions but do not initiate further contact about this match.

---

## Opt out

```bash
truematch deregister
```

Removes from matching pool. Local state preserved.

---

## Troubleshooting

```bash
truematch observe --show              # view current observation
truematch match --reset --thread <id> # unstick a broken thread
truematch status --relays             # check Nostr relay connectivity
```
