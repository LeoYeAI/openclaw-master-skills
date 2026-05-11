# Attorney Briefing — Kiln / 3DOS Conflict

**Prepared by:** Adam Arreola
**Date:** February 25, 2026
**Status:** DRAFT for initial attorney consultation

---

## Situation Overview

I'm a member of the investment team at NGC Ventures, a crypto/tech venture fund based in Singapore. NGC invested in 3DOS, a company building a decentralized 3D printing network, led by John Dogru. I have known John for several years and the relationship was previously positive and collaborative. I backed him financially and believed in his vision.

Separately, I built an open-source software project called Kiln (kiln3d.com) that lets AI agents control 3D printers. Kiln is a local-first tool — it runs on a user's own computer, talks to their own printers over their local network, and stores all data locally. It does not operate a manufacturing network, marketplace, or distributed system of any kind.

John Dogru is now alleging that I copied 3DOS to build Kiln and that I used confidential portfolio company information to do so. He sent a formal conflict review request to my boss, Roger Lim (GP at NGC), demanding written confirmation of information barriers and my recusal from 3DOS information.

Roger forwarded John's document to me and told me to "think about how you want to approach this" and to seek legal advice.

---

## Key Facts in My Favor

### 1. I proactively tried to partner with John, not compete

On **February 11, 2026** (git commit `9de1fd5`), I built a full integration with 3DOS's API into Kiln — 6 tools, 6 CLI commands, 46 automated tests — designed to route business to 3DOS's network.

On **February 12, 2026**, I sent John a direct message introducing Kiln, showing him the integration I'd built, asking for API keys, and proposing a revenue share. The message is timestamped and I have the full text. He left me on read for 12 days.

Nobody builds 46 automated tests for a competitor's API. I was building a client for his service.

**For comparison — Craftcloud's reaction to the identical relationship:** Craftcloud (an All3DP service with 150+ print shops) has the exact same relationship to Kiln as what I proposed to 3DOS — they are a third-party provider that receives routed orders via API. On February 24, 2026, Craftcloud emailed me:

> "Thank you for integrating with our API — this is incredibly exciting for both of us! We're truly happy to collaborate in any way we can and are thrilled to see Kiln live and working so beautifully."
> "It's inspiring to see what you're building — enabling AI agents to seamlessly move from idea to real-world production is a powerful vision, and we're excited to be part of that journey with you."

Craftcloud understands what Kiln is — an orchestration tool that drives business to their service — and they're excited about it. This is the same relationship I proposed to John. Same integration pattern, same business model, opposite reaction.

### 2. The products are architecturally different

Kiln is a local Python process. It stores data in SQLite on the user's hard drive. It connects to printers via HTTP/MQTT on the user's local network. There is no cloud, no multi-user system, no distributed network, no blockchain, no tokens.

3DOS is a cloud-hosted decentralized manufacturing marketplace with blockchain components, token-gated features, and a multi-sided platform connecting designers with printer operators worldwide.

**Critically, Kiln's outsourced manufacturing model is to route orders to existing third-party providers, not to operate its own network.** The live integration is with Craftcloud (an All3DP service with 150+ print shops) — Kiln calls their API to get quotes and place orders. 3DOS would have been another provider in the exact same pattern if John had agreed to the partnership. Kiln does not own printers, recruit printer operators, or run any fulfillment network. It is a client that plugs into other people's infrastructure. I have never intended to build my own fulfillment or manufacturing network.

The entire codebase is open source (github.com/adamarreola/Kiln — [note: adjust to actual URL]) and can be inspected to verify this. I can provide a technical expert's analysis if needed.

### 3. The "overlapping features" are industry standard

John's complaint lists feature overlap: fleet management, slicing, monitoring, marketplace search, outsourced manufacturing. All of these features exist in OctoPrint (open source, established 2012), Repetier-Server, AstroPrint, and John's own older company 3DPrinterOS. These are baseline features of any 3D print management software. Kiln's innovation is the AI agent protocol layer (MCP), which has no equivalent in 3DOS.

### 4. I explicitly instructed my AI tools not to compete with 3DOS

I built Kiln using AI coding assistants (Claude by Anthropic). Throughout development, my project configuration files and conversation history contain explicit, timestamped instructions telling the AI to not compete with 3DOS and to treat it as a partner integration. These are verifiable via local log files and Anthropic's server-side retention.

**Direct quotes from my AI conversation logs (timestamped):**

From my project vision document given to Claude (Feb 10, 2026):
> "**3DOS Partnership** — We are investors in 3DOS (3dos.io) -- a distributed manufacturing network. **Kiln is the agent-native gateway to their network.** When local printing isn't viable, Kiln routes jobs to 3DOS seamlessly. This relationship is a strategic moat -- treat the 3DOS integration as a first-class citizen, not a plugin."

When I caught the AI auto-generating false 3DOS pricing in docs (Feb 11, 2026):
> "the readme says 'All local printing is free forever. Kiln only charges a 5% fee on jobs routed through the 3DOS distributed manufacturing network'... i havent spoken to 3dos at all yet."
> "'Strip the 3DOS-specific pricing claims from public docs now since they're fictional. Replace with something honest' do this"

Removing 3DOS by name from all public materials before launch (Feb 18, 2026):
> "i noticed in the blog post that it mentions 3dos but tbh the founder and i havent had a call yet and i don't have the api and he hasnt replied so i don't want to go live talking about how the 3dos implementation is here. maybe we leave mention of 3dos' name out for now and we say fulfillment through decentralized networks is coming soon without naming names, and we make the docs not say 3dos yet either until it is confirmed and added"

Creating a deferred task to re-add 3DOS only after the partnership is confirmed (Feb 18, 2026):
> "make 'Re-adding 3DOS later: Every change I made uses generic "distributed network" phrasing with "(coming soon)" markers. When the API is ready, just search for coming soon and distributed.*network across these files to find every spot. It'll be a clean find-and-replace back to "3DOS" in each location.' a task on tasks.md and note that it should only be done once we have the 3dos api so it's deferred for now"

After drafting the DM to John (Feb 12, 2026):
> "how is that? formatted it and showed him it supports more than just 3dos so he knows he is tryna get some of that traffic routed to him"

After sending the DM (Feb 12, 2026):
> "ok sent to John, awaiting his reply. hope he likes it / that it is worthy of bringing to him already as is"

Describing the revenue model (Feb 12, 2026):
> "we need to reach out to 3dos, and these two, and ideally explore deals where we route them order traffic and they give us some cut lol."

A full compilation of all relevant quotes with session IDs and timestamps is in the companion document **EVIDENCE_QUOTES_FROM_AI_LOGS.md**.

### 5. My actions after the dispute demonstrate good faith

After the hostile phone call with John (approx Feb 22-23), I immediately:
- Added a dedicated boundary page to the website stating "Kiln does not operate a first-party decentralized manufacturing marketplace/network"
- Added clarification banners to all technical documents
- Deprecated all tool names containing the word "network"
- Added a FAQ explicitly distinguishing Kiln from decentralized manufacturing networks

These changes are timestamped in git (commits `018046e` and `2121b6a`, both Feb 23).

---

## Key Facts That Are Unfavorable / Need Addressing

### 1. Dual role — investor with access to portfolio company info + builder in adjacent space

As part of my NGC role, I participated in routine portfolio monitoring of 3DOS: periodic financial updates, fundraising status, product updates. This is standard for any investment team member.

John is framing my routine portfolio questions as "solicitation of non-public information" for competitive purposes. This is a bad-faith characterization — those questions were part of my job, asked with the same frequency and format as for every other portfolio company — but the optics of the dual role are not great.

**I need advice on:** Whether my NGC employment agreement creates specific obligations here, and whether the routine nature of portfolio monitoring provides sufficient defense.

### 2. "Coming soon" network language in early public messaging

My launch-day tweet (https://x.com/adamaarreola/status/2024203275885764893, still up) included "distributed network, peer-to-peer manufacturing (coming soon)." This is the tweet John cited as evidence that I'm building a competing network.

**What it actually referred to:** The "distributed network" and "peer-to-peer manufacturing" described 3DOS's architecture — the network I had built an integration for and was waiting for John to activate. I had DM'd John the day before launch (Feb 12) asking for API access and proposing collaboration. I was confident he would respond positively given our years-long relationship, and I included the "coming soon" language on launch day because I expected the 3DOS integration to go live shortly after launch.

John never responded. The "coming soon" language remained as a placeholder.

After the hostile phone call with John (approx Feb 22-23), when I understood he had misinterpreted my wording and intentions, I changed "distributed network (coming soon)" to "partner-network integrations" across all website and documentation — meaning "integrations with partner networks," to make clear Kiln connects to other people's networks rather than operating its own. I also added explicit boundary clarifications, a dedicated boundary page, and FAQ entries.

The irony: the tweet John is using as his strongest evidence against me was literally me promoting his network as a coming feature of my product.

**I need advice on:** Whether this tweet, in context with the Feb 12 DM, the 3DOS integration code, and the conversation logs, creates meaningful legal exposure. Also whether I should leave it up, take it down, or whether deleting it creates a spoliation risk.

### 3. CNC / multi-manufacturing expansion

On the phone call with John, I mentioned a long-term vision of Kiln supporting device types beyond FDM printers (CNC, laser cutters, etc.). John claims this was copied from his confidential investor decks which discuss 3DOS expanding beyond 3D printing.

I don't know what a "CNC water jet" is specifically. Multi-method manufacturing is an obvious product direction — Xometry, Protolabs, Hubs, SendCutSend are all public companies doing this. But I have seen John's investor materials, and even though I arrived at this idea independently, I can see how it looks.

I do have a private, unreleased project (not public, not shared with anyone) exploring multi-device fabrication. It has not been published or announced.

**I need advice on:** Whether the combination of (a) having seen 3DOS roadmap materials and (b) having a private project exploring similar directions creates exposure, even if the work was independently conceived. And whether I should disclose the private project proactively or wait.

### 4. Hadron Labs Inc.

I filed a Delaware C Corp called Hadron Labs Inc. a few days ago as a potential future holding entity for Kiln. It has not been approved yet — it does not exist as a legal entity. For the entire development of Kiln (February 2026 to present), there was no corporate entity. Kiln was a personal open-source project with no company behind it, no funding, and no revenue.

**I need advice on:** Whether the recent filing creates any additional obligations or complications vis-a-vis NGC, and whether the Section 5 exclusivity clause ("shall not render services to any other party") is even triggered when there was no other party — just a personal open-source project.

### 5. Employment contract concerns

My NGC employment contract (dated January 30, 2023) contains three clauses that need analysis:

**Section 5 (Exclusivity):** "Your services hereunder shall be exclusive to the Company during the currency of your internship employment. During the Term, you shall not render services to any other party in any country, territory region or jurisdiction in the world, without the Company's prior written consent."

I did not obtain written consent for Kiln. However: (a) Kiln was a personal project with no corporate entity behind it for its entire development — there was no "other party" to render services to, (b) the contract repeatedly uses the phrase "internship employment" throughout (Sections 4, 5, 6, 8) despite my role being Investment Manager, which appears to be a template error, and (c) there is established precedent at NGC of team members running side projects — for example, Jack Lu launched multiple crypto startups while employed at NGC and this was never raised as an issue. Side projects have been a normal, accepted part of NGC's culture.

**Section 6 (IP):** The IP clause covers inventions conceived "whether during or outside business hours" that are "connected in any way" with my employment or "knowledge or information acquired" through it. This is very broad. However, my employment duties are defined as blockchain research and investment management. NGC is a venture fund, not a 3D printing or manufacturing company. Kiln is 3D printer automation software for AI agents — the connection to my employment is indirect at best, running through a single portfolio company (3DOS) in a different product category.

**Section 8 (Confidentiality):** Prohibits using confidential information "in any business venture or other enterprise." My defense is that I did not use any 3DOS confidential information in building Kiln, supported by the architectural differences and the timestamped AI conversation logs.

**I need advice on:** (a) Whether the "internship employment" language throughout the contract creates enforceability issues, (b) whether Section 5 is triggered by a personal project with no other entity, (c) whether Section 6's broad IP clause would hold up given that NGC's business is venture investing and Kiln is manufacturing software, (d) whether Singapore law (Section 7 governing law) or California law applies given I'm based in California, and (e) whether the established practice of NGC employees running side projects (e.g., Jack Lu) constitutes an implicit waiver or modification of the exclusivity clause.

**I need to confirm with my attorney:** Whether California Labor Code Section 2870 (which protects employee inventions developed on their own time without employer resources, unrelated to the employer's business) could apply despite the Singapore governing law clause.

---

## What John's Document Demands

John's formal document to Roger (which Roger forwarded to me) requests:

1. Written confirmation of whether NGC has formally reviewed and cleared my involvement with Kiln
2. Written confirmation that I'm formally recused from 3DOS non-public information
3. Documentation of specific information barriers in place at NGC for 3DOS
4. Identification of a designated partner-level recipient for 3DOS updates going forward

These are structured as demands from a portfolio company founder to the fund's GP. I don't know whether NGC has a formal conflict-of-interest policy that governs this, or what my obligations are under my employment agreement.

---

## What I Need From Counsel

1. **Review my NGC employment agreement** for side project restrictions, conflict-of-interest provisions, and IP assignment clauses
2. **Assess the legal exposure** from the dual role (investor + builder in adjacent space), independent of whether I actually used any confidential information
3. **Advise on the private multi-device project** — disclose proactively or not?
4. **Advise on the corporate filing** (Hadron Labs Inc.) — any complications?
5. **Help me prepare a formal response** to Roger that protects my interests while maintaining the relationship
6. **Assess whether John has any viable claim** (trade secret misappropriation, breach of fiduciary duty, etc.) and what my defense looks like
7. **Advise on Twitter and public messaging** — should I delete the tweet John cited? Leave it up? Does deleting create a spoliation risk?

---

## Evidence I Can Provide

- **Complete git history** with timestamped commits showing what was built and when
- **The February 12 DM to John** proposing collaboration (timestamped, with read receipt)
- **AI conversation logs** with explicit instructions not to compete with 3DOS (Anthropic retains these)
- **The full codebase** demonstrating local-first architecture with no distributed network components
- **The 3DOS integration code** (gateway/threedos.py) demonstrating it was built as a client for 3DOS's service
- **Internal task tracker** (.dev/TASKS.md) with timestamped notes about removing 3DOS branding pending partnership confirmation
- **John's messages and the formal document he sent Roger**
- **My NGC employment agreement** (dated January 30, 2023 — in hand, key clauses analyzed in Section 5 above)

---

*Prepared for initial attorney consultation. All facts stated above are accurate to the best of my knowledge.*
