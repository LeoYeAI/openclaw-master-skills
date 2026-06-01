<table width="100%">
  <tr>
    <td width="80px">
      <img src="https://cdn.jsdelivr.net/gh/opsat-btc/agent_proxy@main/eng.svg" width="80" alt="Logo" style="filter: invert(1);">
    </td>
    <td align="left">
      <h1 style="border:none; margin:0;">{Project Name} — Research Report</h1>
      <p style="margin:0; color:gray;">Crab Catch — Research Assistant</p>
    </td>
    <td align="right" valign="bottom">
      <p style="margin:0; font-size:0.85em; color:gray;">Generated at: <code>{YYYY-MM-DD HH:mm}</code></p>
    </td>
  </tr>
</table>

> **Research Entry:** [{user-provided URL}]({url})

---

## 📌 Basic Information

<!--
  This table is FLEXIBLE — add/remove rows based on available data.
  Only include rows where data was actually collected.
  Do NOT pad with "N/A" or placeholder rows.
  Examples of additional rows: Audit Firm, Launch Date, TVL, DEX Listings, etc.
-->

| Item | Content |
| :--- | :--- |
| **Project Name** | **{Project Name}** |
| **Official Site** | [{url}]({url}) |
| **Social Media** | Twitter: [@{username}]({url}) `(Followers: {N})` |
| **Smart Contract** | `{Chain}` : `{address}` |
| ... | *agent adds/removes rows based on collected data* |

---

## 🧠 Core Findings

> **Executive Summary:** `{one-sentence verdict}`

| Level | Signal | Impact & Reasoning |
| :---: | :--- | :--- |
| 🟢 | **Bullish:** {positive signal} [[1]]({url}) | {why it matters} |
| 🔴 | **Critical:** {risk signal} [[2]]({url}) | {high-priority risk} |
| 🟡 | **Unknown:** {unverified factor} | {what's missing for confirmation} |

---

## 🛡️ Verification & Cross-Reference

### Claim Verification
*Verify key project claims against code and on-chain reality. Prioritize claims that affect user funds.*

| Claimed Fact | Source | How Verified | Verdict |
| :--- | :--- | :--- | :---: |
| {e.g. "Audited by CertiK"} | Website [[N]]({url}) | {Audit link valid + deployed code matches audited version} [[N]]({url}) | ✅ / ⚠️ / ❌ |
| {e.g. "Max supply 100M"} | Docs [[N]]({url}) | {Contract has no mint() or mint is capped} [[N]]({url}) | ✅ / ⚠️ / ❌ |
| {e.g. "Decentralized"} | Website [[N]]({url}) | {Owner is multisig, no pause/blacklist} [[N]]({url}) | ✅ / ⚠️ / ❌ |
| {e.g. "Liquidity locked"} | Twitter [[N]]({url}) | {LP lock contract verified, N months} [[N]]({url}) | ✅ / ⚠️ / ❌ |

### Contradictions & Anomalies
*The most valuable signals — where different data sources tell different stories.*

| Dimension | Source A says | Source B says | Severity |
| :--- | :--- | :--- | :---: |
| {e.g. TVL} | Website: "$10M TVL" [[N]]({url}) | On-chain: $500K actual [[N]]({url}) | 🔴 |
| {e.g. Team location} | Twitter: "Based in US" [[N]]({url}) | GitHub: commits all UTC+8 [[N]]({url}) | 🟡 |
| {e.g. Token supply} | Docs: "100M fixed" [[N]]({url}) | Contract: mintable, no cap [[N]]({url}) | 🔴 |

> *If no contradictions found, state: "No cross-source contradictions detected."*

#### Key Dispute Analysis
*For each 🔴 contradiction or community accusation, provide detailed evidence chain.*

**{Dispute title, e.g. "Token supply mismatch"}**

| Step | Evidence | Source |
| :--- | :--- | :--- |
| Project claims | {"Max supply 100M, deflationary"} | Docs page [[N]]({url}) |
| On-chain reality | {Contract has `mint()` with no cap, owner can mint unlimited} | Contract code [[N]]({url}) |
| Technical analysis | {Community analyst @sec_researcher: "this mint function bypasses the cap check via proxy delegate call, same pattern as $SCAM_TOKEN rug in 2024"} | Analysis thread [[N]]({url}) |
| On-chain forensics | {Deployer wallet 0xABC sent 500 ETH to Tornado Cash 3 days after launch, then received tokens from 5 fresh wallets — circular flow pattern} | Tx [[N]]({explorer_url}) |
| Community reaction | {"@user_a: classic rug setup" — 245 likes, 89 replies} | Tweet reply [[N]]({url}) |
| KOL stance | {"@kol_b quoted: 'team needs to explain this immediately'"} | Quote tweet [[N]]({url}) |
| Counter-argument | {Team: "mint is for staking rewards only, will renounce after launch"} | Team tweet [[N]]({url}) |
| **Verdict** | {**Unresolved** — mint function exists, team promise is unenforceable on-chain. Community analysis corroborates the risk.} | — |

> *Repeat this block for each major dispute. Only disputes with 🔴 severity or active community accusations require detailed analysis. Include community technical analysis (code reviews, on-chain forensics, tokenomics breakdowns) whenever available.*

### Information Gaps
*What could not be verified and why — absence of data is also a signal.*

| Missing Data | Why Unavailable | Risk Implication |
| :--- | :--- | :--- |
| {e.g. Team identity} | {No LinkedIn, anonymous GitHub} | {Cannot assess accountability} |
| {e.g. Audit report} | {Claimed but link 404} | {Security unverified} |

---

## 📊 Deep Dive (Optional)

### 👤 Team & Key Figures
*Identified from website, tweets, comments, GitHub commits, or community mentions.*

| Person | Role | Source | Background Check | Flag |
| :--- | :--- | :--- | :--- | :---: |
| {name/@handle} | {Founder} | {Website + Twitter} | {account age, past projects, KOL followers} | ✅ / ⚠️ / 🔴 |
| {name/@handle} | {CTO} | {GitHub commits} | {commit history matches claimed expertise} | ✅ / ⚠️ / 🔴 |

### 💻 GitHub Analysis
* **Tech Stack:** `{languages, frameworks}`
* **Activity:** Last commit `{date}`, `{N}` contributors
* **Completeness:** `{functional / skeleton / abandoned}`

### ⛓️ On-chain Security
| Check | Result | Risk |
| :--- | :--- | :---: |
| **Honeypot** | {result} | 🟢/🟡/🔴 |
| **Buy/Sell Tax** | {N% / N%} | 🟢/🟡/🔴 |
| **Ownership** | {Renounced / Multisig / EOA} | 🟢/🟡/🔴 |
| **Liquidity Lock** | {result} | 🟢/🟡/🔴 |

### 📈 Social Signals
* **KOL Followers:** `{notable names from kol-followers API}`
* **Anomalies:** `{e.g. bot-like follower spikes, deleted tweets}`
* **Community Sentiment:** `{from search/tweet analysis}`

### 📅 Project Timeline
*Cross-source chronological reconstruction — abnormal timing patterns are high-value signals.*

| Date | Event | Source | Flag |
| :--- | :--- | :--- | :---: |
| {YYYY-MM-DD} | {Domain registered} | Website [[N]]({url}) | — |
| {YYYY-MM-DD} | {Contract deployed} | On-chain [[N]]({url}) | — |
| {YYYY-MM-DD} | {Twitter account created} | Twitter [[N]]({url}) | ⚠️ {same day as deploy} |
| {YYYY-MM-DD} | {Liquidity added: $N} | On-chain [[N]]({url}) | — |
| {YYYY-MM-DD} | {First GitHub commit} | GitHub [[N]]({url}) | — |
| {YYYY-MM-DD} | {KOL @xxx followed} | Twitter [[N]]({url}) | — |
| {YYYY-MM-DD} | {N tweets deleted} | Twitter [[N]]({url}) | 🔴 |
| {YYYY-MM-DD} | {Ownership transferred / renounced} | On-chain [[N]]({url}) | — |

> **Timeline Analysis:** `{1-2 sentence interpretation — e.g. "All infrastructure created within 24h suggests a speed-launched project. KOL engagement preceded any real on-chain activity, indicating possible paid promotion."}`

---

## 📝 Conclusion & Verdict

| Dimension | Assessment |
| :--- | :--- |
| **Overall Rating** | **{Summary}** |
| **Confidence** | `[ ██████░░░░ ] {N}%` |
| **Recommendation** | **{Clear recommendation}** |
| **Primary Risk** | {The single biggest threat} |

---

## ⚠️ Risk Warning

| # | Risk | Severity | Detail |
| :---: | :--- | :---: | :--- |
| 1 | {e.g. Contract ownership not renounced} | 🔴 | {owner can mint/pause/blacklist} |
| 2 | {e.g. Team fully anonymous} | 🟡 | {no verifiable identity across any source} |
| 3 | {e.g. Low liquidity} | 🟡 | {$N locked, easy to drain} |

> *If no risks identified, state: "No critical risks identified."*

---

## 📂 References
<!--
  Citation rules (like academic papers):
  - Every factual claim, data point, or quote in the report MUST have a [[N]] inline citation
  - Every [[N]] in the report body MUST have a matching entry in this list
  - Every entry in this list MUST be cited at least once in the report body
  - Number sequentially from 1, in order of first appearance
  - One source may be cited multiple times with the same [[N]]
-->
| # | Source | Type | URL |
| :---: | :--- | :--- | :--- |
| 1 | {source title} | {Twitter / Website / On-chain / GitHub / Docs} | [{url}]({url}) |
| 2 | {source title} | {type} | [{url}]({url}) |
| 3 | ... | ... | ... |

---
<p align="center">
  <sub>⚠️ <b>DYOR:</b> This report is generated by AI for informational purposes only. No investment advice.</sub>
</p>
