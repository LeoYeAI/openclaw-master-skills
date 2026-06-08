# Example: Source Management Conversation

This shows how a user manages their briefing sources through natural conversation.

---

**User:** Show my sources

**Agent:**
Here are your active sources, grouped by topic:

**📌 Municipal Bonds** (5 sources)
- ✅ The Bond Buyer (newsletter) — reliability: 0.95 — last fetched: 2h ago
- ✅ MuniNet Guide (blog) — reliability: 0.85 — last fetched: 2h ago
- ✅ MuniLand Blog (blog) — reliability: 0.80 — last fetched: 2h ago
- ✅ Reuters Municipal (rss) — reliability: 0.90 — last fetched: 2h ago
- ⚠️ Muni Credit News (blog) — reliability: 0.45 — last fetched: 3 days ago (2 consecutive failures)

**📌 AI Policy** (4 sources)
- ✅ The Information (newsletter) — reliability: 0.90 — last fetched: 2h ago
- ✅ TechCrunch AI (rss) — reliability: 0.85 — last fetched: 2h ago
- ✅ Stratechery (newsletter) — reliability: 0.92 — last fetched: 2h ago
- ✅ SemiAnalysis (blog) — reliability: 0.88 — last fetched: 2h ago

⚠️ Heads up: Muni Credit News has failed 2 fetches in a row. I'll keep trying — if it hits 5 failures I'll pause it automatically.

---

**User:** Add https://www.creditriskmonitor.com/blog/feed to my municipal bonds sources

**Agent:**
Checked the feed — it's active and has recent content about credit monitoring and risk assessment. Added to your Municipal Bonds sources as "CreditRisk Monitor Blog" (RSS feed).

---

**User:** Ban cnn.com from my sources

**Agent:**
Done — banned cnn.com. No sources from that domain were active, but it won't appear in future source discovery results either.

---

**User:** Drop Muni Credit News, it's been garbage lately

**Agent:**
Deactivated Muni Credit News. It's archived — say "restore Muni Credit News" if you change your mind. You still have 4 active Municipal Bonds sources.

---

**User:** Find me more sources for AI hardware specifically

**Agent:**
Searching for AI hardware-focused sources...

Found 4 strong candidates:
- **SemiAnalysis** (already in your list ✅)
- **Tom's Hardware AI** — Hardware-focused coverage with regular chip industry analysis
- **Fabricated Knowledge** — Deep technical newsletter on semiconductor manufacturing
- **Dylan Patel's Substack** — Former SemiAnalysis writer, focused on AI chip economics

Want me to add all three new ones, or pick specific ones?

---

**User:** Add Fabricated Knowledge and Dylan Patel

**Agent:**
Added both to your AI Policy sources:
- Fabricated Knowledge (newsletter) — reliability: 0.70 (new source, will calibrate)
- Dylan Patel's Substack (newsletter) — reliability: 0.70 (new source)

These will start showing up in tomorrow's briefing.
