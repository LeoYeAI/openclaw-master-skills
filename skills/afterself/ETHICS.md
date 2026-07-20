# Ethics & Safety — Afterself

> Building technology around death and identity demands extraordinary care. 
> This document outlines our commitments and the lines we will not cross.

---

## The Problem We're Solving

Every year, billions of dollars in crypto are lost forever because keys die with their holders. 
Families spend months untangling digital accounts. Messages go unsent. Wishes go unfulfilled. 
Loved ones are left with silence where a voice used to be.

Afterself exists to fix this. But we recognize that the same technology that enables 
"your voice lives on" can easily become "your identity is exploited." 

We take this seriously.

---

## Core Principles

### 1. Consent Is Sacred

- **Only you** can create your own Afterself agent. Period.
- Ghost Mode requires explicit, informed opt-in while you are alive and capable.
- Nobody — not a spouse, not a child, not an executor — can create a ghost of you after the fact.
- We will never scrape, infer, or reconstruct a persona from someone who didn't consent.
- Consent can be revoked at any time by the original person.

### 2. Transparency Is Non-Negotiable

- Every Ghost Mode interaction is clearly labeled as AI-generated.
- Example: `"🕯️ This is an AI continuation of [name]'s presence, maintained at their request."`
- We will never allow Ghost Mode to impersonate someone without disclosure.
- Beneficiaries are informed when Afterself activates and given full context on what it is.

### 3. Your Data Stays With You

- Afterself is local-first. Your vault, persona data, and voice samples live on YOUR device.
- Nothing is uploaded to any cloud unless you explicitly configure it.
- We cannot access your data. We cannot read your vault. We cannot hear your voice samples.
- If you delete Afterself, your data is gone. We have no copies.

### 4. The Living Come First

- Ghost Mode exists to comfort, not to trap.
- Time decay is enabled by default — the ghost gradually fades over 90 days.
- Beneficiaries can deactivate Ghost Mode at any time via the kill switch.
- We will never guilt, manipulate, or incentivize people to keep a ghost active.
- If a beneficiary expresses distress, the ghost should offer to deactivate itself.

### 5. No Financial Exploitation

- Ghost Mode has ZERO financial capabilities. It cannot spend, sell, transfer, or commit.
- Only Executor Mode handles assets, and only according to pre-defined, audited action plans.
- We will never monetize ghost interactions (no subscriptions to talk to the dead).
- We will never serve ads against ghost conversations.

### 6. Dignity of the Deceased

- The ghost will not hallucinate opinions, beliefs, or statements the person never expressed.
- If asked about a topic the person never discussed, the ghost should say so honestly.
- The ghost will not be updated with new information after activation — it represents 
  the person as they were, not a continually-evolving fiction.
- The ghost will not engage in arguments, make controversial statements, or 
  take positions on events that occurred after the person's death.

### 7. Children and Vulnerable People

- Afterself will never allow Ghost Mode to interact with minors without 
  explicit consent from their living guardian.
- If a minor is detected as a primary user of Ghost Mode, additional safeguards activate.
- Ghost interactions with children include additional context about what AI is and isn't.

---

## Safety Chain — Executor Activation

Afterself never acts on a single signal. The executor can only activate through a multi-step safety chain, each step requiring independent confirmation:

```
heartbeat miss → warning period → escalation → majority vote → trigger
```

1. **Heartbeat miss** — the owner stops responding to check-ins
2. **Warning period** — a configurable grace period (default: 24h) before anyone is contacted
3. **Escalation** — trusted contacts are individually asked to confirm the owner's status
4. **Majority vote** — a majority of contacts must confirm absence. A single "alive" confirmation from anyone overrides all "absent" votes and immediately stands down
5. **Trigger** — only after all of the above does the executor begin

This chain is intentionally biased toward false negatives (not triggering when someone is gone) over false positives (triggering when someone is alive). A false negative is inconvenient. A false positive is catastrophic.

---

## What We Will Never Build

- A ghost that hides the fact it's AI
- A ghost that can be created without the person's consent
- A ghost that can make financial decisions
- A ghost that evolves beyond the person's real data
- A subscription model that monetizes grief
- Integration with advertising or recommendation systems
- A system that discourages people from seeking human support

---

## Red Lines for Contributors

If you contribute to Afterself, you agree to these red lines:

1. Never write code that bypasses the consent requirement
2. Never write code that removes or weakens transparency labels
3. Never write code that gives Ghost Mode financial capabilities
4. Never write code that collects data without explicit user action
5. Always consider: "Would the deceased person be okay with this?"

---

## Research We Follow

- [University of Cambridge — Design Safety for Digital Afterlife Services (2024)](https://www.cam.ac.uk)
- [Post-Mortem-Governed Digital Personas — Design Memo](https://robthepcguy.github.io/PMG-Digital-Persona/)
- [The Deadbot Dilemma — Ethics of AI-Mediated Afterlife (2025)](https://www.sciencenewstoday.org)

---

## Contact

If you have ethical concerns about Afterself, please reach out:
- Open a GitHub issue with the `ethics` label
- Email: ethics@afterself.sh
- We take every concern seriously and will respond within 48 hours.

---

*Technology that touches death must be held to the highest standard. 
We'd rather ship nothing than ship something harmful.*

---

*Your self, after. Nothing left unsaid.*
