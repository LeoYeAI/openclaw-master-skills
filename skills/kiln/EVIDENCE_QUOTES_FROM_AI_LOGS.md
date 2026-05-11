# Evidence: Adam Arreola's Direct Statements to AI Tools Regarding 3DOS

**Source:** Claude Code conversation logs stored locally at `~/.claude/projects/-Users-adamarreola-Kiln/*.jsonl` and retained server-side by Anthropic.
**Date range:** February 10-25, 2026
**Extracted:** February 25, 2026
**Classification:** CONFIDENTIAL — For legal counsel and internal review only

---

## Overview

These are Adam Arreola's direct, timestamped statements to AI coding tools (Claude by Anthropic) during the development of Kiln. They demonstrate a consistent, unbroken pattern across 10+ separate sessions:

1. 3DOS was always positioned as a partner whose network Kiln would route traffic TO
2. Adam proactively removed 3DOS claims from public materials when the partnership was unconfirmed
3. Adam's "coming soon" language was a placeholder for the anticipated 3DOS partnership
4. Adam's monetization model was built around generating revenue FOR 3DOS through referrals
5. At no point did Adam instruct any AI tool to copy, replicate, or compete with 3DOS

---

## Category 1: 3DOS Explicitly Positioned as a Partner, Not a Competitor

### Vision document given to Claude as project instructions
**Session:** `9b229161-ffcd-4d47-8f1a-42758303e024`
**Date:** February 10, 2026

> "**3DOS Partnership** — We are investors in 3DOS (3dos.io) -- a distributed manufacturing network. **Kiln is the agent-native gateway to their network.** When local printing isn't viable (scale, material, quality, location), Kiln routes jobs to 3DOS seamlessly. This relationship is a strategic moat -- treat the 3DOS integration as a first-class citizen, not a plugin."

> "**Path 1: 3DOS Referral Revenue** — Every print job Kiln routes to 3DOS generates a referral fee. This is the passive baseline. Instrument all 3DOS job routing with attribution tracking from day one."

**Significance:** The foundational project instructions describe Kiln as a "gateway" to 3DOS's network — not as a replacement for it. 3DOS is described as a "strategic moat" whose integration should be treated as "first-class." The business model is routing revenue TO 3DOS.

---

### Wanting to route traffic to 3DOS and share revenue
**Session:** `af97d73e-1a80-488d-a528-af48033611c8`
**Date:** February 12, 2026

> "we need to reach out to 3dos, and these two, and ideally explore deals where we route them order traffic and they give us some cut lol."

**Significance:** Adam's monetization strategy was explicitly to drive demand to 3DOS (and other providers) and receive a referral cut. This is affiliate/partnership behavior.

---

### After drafting the DM to John
**Session:** `af97d73e-1a80-488d-a528-af48033611c8`
**Date:** February 12, 2026

> "how is that? formatted it and showed him it supports more than just 3dos so he knows he is tryna get some of that traffic routed to him"

**Significance:** Adam wanted John to understand that Kiln would route traffic to him. The DM was crafted to show John the benefit to 3DOS.

---

### After sending the DM to John
**Session:** `af97d73e-1a80-488d-a528-af48033611c8`
**Date:** February 12, 2026

> "ok sent to John, awaiting his reply. hope he likes it / that it is worthy of bringing to him already as is"

**Significance:** Adam hoped John would be pleased by what he built. This is not the sentiment of someone trying to undermine a competitor.

---

### Describing his personal relationship with John
**Session:** `af97d73e-1a80-488d-a528-af48033611c8`
**Date:** February 12, 2026

> "more personal because i have known John the ceo for years and he is who i would DM and i backed 3dos via my vc firm in the past"

> "john and i spoke last week about 3dos fyi so hasnt been a while, we spoke recently"

---

### Distinguishing 3DOS as a different type of service
**Session:** `e41a7a6a-a72a-4235-9f4c-502cdc0fcf42`
**Date:** February 13, 2026

> "3dos is more of a decentralized 3d printing network more than a 3d printing fulfillment center. idk if it matters to distinguish that we support decentralized 3d printing networks AND 3d printing fulfillment centers"

**Significance:** Adam recognized 3DOS as a categorically different type of service and wanted to distinguish between supporting decentralized networks (like 3DOS) and fulfillment centers (like Craftcloud). He saw these as separate categories, not the same product.

---

### Deferring monetization decisions to collaborative talks
**Session:** `2ac8ee9a-ac71-48f4-a761-cf332c44a4ff`
**Date:** February 13, 2026

> "TBD via talks w 3dos and others if theyll cut us in on more $$"

**Significance:** Monetization beyond basic referral fees was explicitly deferred to collaborative negotiations with 3DOS. Adam didn't set terms unilaterally.

---

## Category 2: Proactively Removing 3DOS Claims Before Launch

### Catching and removing fictional 3DOS pricing
**Session:** `606e0969-3707-4534-9666-f2e280197c31`
**Date:** February 11, 2026

> "the readme says 'All local printing is free forever. Kiln only charges a 5% fee on jobs routed through the 3DOS distributed manufacturing network'... i havent spoken to 3dos at all yet. and does this encourage users to route through places that are not 3dos? we need to think here how to make this make some $ lol"

> "'Strip the 3DOS-specific pricing claims from public docs now (README, WHITEPAPER) since they're fictional. Replace with something honest' do this"

**Significance:** When the AI auto-generated copy that included 3DOS-specific pricing, Adam immediately caught it and ordered it removed because he hadn't spoken to 3DOS yet and didn't want to make false claims. He insisted on honesty.

---

### Removing 3DOS by name from all public materials before launch
**Session:** `8a5f4a61-728a-4bd0-812e-5f7157e4c8cc`
**Date:** February 18, 2026

> "that looks great. i noticed in the blog post that it mentions 3dos but tbh the founder and i havent had a call yet and i don't have the api and he hasnt replied so i don't want to go live talking about how the 3dos implementation is here. maybe we leave mention of 3dos' name out for now and we say fulfillment through decentralized networks is coming soon without naming names, and we make the docs not say 3dos yet either until it is confirmed and added"

**Significance:** This is the strongest single quote. Adam explicitly removed 3DOS by name from ALL public-facing materials before launch because:
1. The founder hadn't responded to his partnership request
2. He didn't have API access
3. He didn't want to publicly claim an integration that wasn't confirmed

He replaced it with generic "distributed networks (coming soon)" placeholder language — NOT because he was building a competing network, but because he was waiting for the 3DOS partnership to be confirmed before naming them.

---

### Creating a deferred task to re-add 3DOS only after partnership confirmation
**Session:** `8a5f4a61-728a-4bd0-812e-5f7157e4c8cc`
**Date:** February 18, 2026

> "make 'Re-adding 3DOS later: Every change I made uses generic "distributed network" phrasing with "(coming soon)" markers. When the API is ready, just search for coming soon and distributed.*network across these files to find every spot. It'll be a clean find-and-replace back to "3DOS" in each location.' a task on tasks.md and note that it should only be done once we have the 3dos api so it's deferred for now"

**Significance:** Adam created a specific tracking task to re-add 3DOS references ONLY AFTER the partnership was confirmed. The "coming soon" language was always a placeholder for 3DOS — not for a competing network Adam intended to build.

---

## Category 3: Wanting to Collaborate Before Launch

### Wanting to talk to 3DOS before going live
**Session:** `af97d73e-1a80-488d-a528-af48033611c8`
**Date:** February 12, 2026

> "maybe i talk to 3dos before launch in case they want to do some sort of deal, or at least gimme API, or have helpful advice"

---

### Not having spoken to 3DOS about Kiln yet
**Session:** `606e0969-3707-4534-9666-f2e280197c31`
**Date:** February 10, 2026

> "regarding 2, i havent spoken to 3dos about Kiln at all yet, so does 2 give me leverage when i speak to him or what? idk how to frame that convo. 2 is worth doing regardless i figure?"

---

### Acknowledging he didn't have the API
**Session:** `af97d73e-1a80-488d-a528-af48033611c8`
**Date:** February 12, 2026

> "which integrations for 3d printing fullfillment providers do we have fully set up vs partial vs not at all? i know i don't have 3dos api yet unless u found it somewhere."

---

## Category 4: The Tweet John Referenced

The tweet John cited (https://x.com/adamaarreola/status/2024203275885764893) included language about "distributed network, peer-to-peer manufacturing (coming soon)."

**Context from the conversation logs:** The "coming soon" language was a direct reference to the 3DOS integration that Adam was waiting to activate. He had:
- Built the 3DOS integration (Feb 11, git commit `9de1fd5`)
- DM'd John asking for API access and proposing collaboration (Feb 12)
- Assumed John would respond positively given their years-long relationship

The tweet was Adam publicly promoting the anticipated 3DOS integration as a coming feature — it was advertising John's network as something Kiln would connect to, not advertising a competing network Adam was building. The "distributed network" and "peer-to-peer manufacturing" described 3DOS's architecture, which Adam was planning to integrate with as a client.

After the hostile call with John (approx Feb 22-23), when Adam understood John had misinterpreted the language, he updated all website and documentation messaging to use clearer "partner-network integrations" language and added explicit boundary clarifications. The tweet remains up and has not been altered.

---

## Notes on Verifiability

1. **Local logs:** All conversation logs are stored at `~/.claude/projects/-Users-adamarreola-Kiln/*.jsonl` on Adam's machine. Each log file contains the full conversation transcript with timestamps, including both Adam's messages and Claude's responses.

2. **Anthropic server logs:** Anthropic retains conversation data server-side. These can potentially be requested through Anthropic's data access processes to provide independent verification.

3. **Git history:** The code changes described in these conversations correspond to timestamped git commits that can be independently verified in the repository.

4. **Session IDs:** Each quote includes a session ID (UUID) that maps to a specific conversation log file, enabling precise verification.

---

*This document contains direct quotes extracted from AI conversation logs for use in legal consultation. All quotes are Adam Arreola's own words as recorded in the conversation transcripts.*
