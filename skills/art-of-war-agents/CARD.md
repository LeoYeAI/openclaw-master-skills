# 📇 Art of War Agent Decision Card

Print this or keep it open while deploying agents.

---

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           📜 ART OF WAR AGENT DECISION CARD                  ┃
┃                                                              ┃
┃   知彼知己，百战不殆                                          ┃
┃   "Know enemy and yourself; 100 battles, 100 victories"      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────────────────────────────────────────────────────┐
│ 1️⃣  始计篇 — WORTH DOING? (五事七计)                         │
├─────────────────────────────────────────────────────────────┤
│  道 → Aligns with goals?         □  □  □                    │
│  天 → Right timing?              □  □  □                    │
│  地 → Context/data ready?        □  □  □                    │
│  将 → Right agent available?     □  □  □                    │
│  法 → Process defined?           □  □  □                    │
│                                                             │
│  Score: ___/5   Seven Metrics: ___/7   Total: ___/12       │
│                                                             │
│  ≥10 (80%+): ✅ DEPLOY                                       │
│  7-9 (60-79%): ⚠ FIX WEAKNESSES FIRST                       │
│  <7 (<60%):  ❌ DON'T DEPLOY — PLAN FIRST                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2️⃣  谋攻篇 — CAN WE SKIP IT? (上兵伐谋)                      │
├─────────────────────────────────────────────────────────────┤
│  □ Can this be automated entirely?                          │
│  □ Can this be eliminated (not needed)?                     │
│  □ Can a human do it faster (<5 min)?                       │
│  □ Can a single agent handle it?                            │
│                                                             │
│  If any □ is checked → Don't use multi-agent               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3️⃣  作战篇 — BUDGET? (速战速决)                               │
├─────────────────────────────────────────────────────────────┤
│  Token Budget:  □ Low (<10k)   □ Medium (10-50k)   □ High   │
│                                                             │
│  Iteration Limit: _____ (default: 3-5)                      │
│                                                             │
│  □ Reusing existing outputs (因粮于敌)                        │
│  □ Tracking cost as we go                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 4️⃣  军形篇 — RISK? (先胜后战)                                 │
├─────────────────────────────────────────────────────────────┤
│  Risk Level:  □ Low   □ Medium   □ High                     │
│                                                             │
│  If Medium/High, confirm:                                   │
│  □ Version control / backup in place                        │
│  □ Rollback plan defined                                    │
│  □ Validation mechanism ready                               │
│  □ Guardrails set (what agent CANNOT do)                    │
│  □ Human review before critical actions                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 5️⃣  部署 — MONITOR SIGNALS (行军篇)                           │
├─────────────────────────────────────────────────────────────┤
│  Watch for these danger signals:                            │
│                                                             │
│  ⚠️  Repeated questions → Missing context                    │
│  ⚠️  Output getting longer → Filling, not thinking          │
│  ⚠️  Overly confident → Possible hallucination              │
│  ⚠️  Avoiding questions → Capability limit                  │
│  ⚠️  Circular reasoning → Stuck, needs redirect             │
│                                                             │
│  Action: Intervene EARLY. Don't wait for iteration 5.       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 6️⃣  验证 — CROSS-CHECK (用间篇)                               │
├─────────────────────────────────────────────────────────────┤
│  三反原则 — Triple Verification:                             │
│                                                             │
│  Source 1 (Agent knowledge):  □ Verified                    │
│  Source 2 (External search):  □ Verified                    │
│  Source 3 (User context):     □ Verified                    │
│                                                             │
│  All 3 align → High confidence                              │
│  Diverge → Investigate why before trusting                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 🐛 TROUBLESHOOTING QUICK REF                                │
├─────────────────────────────────────────────────────────────┤
│  Problem              →  Solution                           │
│  ─────────────────────────────────────────────────────────  │
│  Stuck in loops       →  Provide context, set limit        │
│  Quality degrades     →  Force conclusion, restart         │
│  Hallucinations       →  Require sources, cross-verify     │
│  Argues with user     →  Restate goal calmly               │
│  Never completes      →  Set deadline, accept good enough  │
│  Wastes on details    →  Redirect: you handle nuance       │
│  Multi-agent chaos    →  Restructure: output→input chain   │
│  Wrong direction      →  Stop, reassess with 五事七计        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 🎯 FIVE CORE PRINCIPLES                                     │
├─────────────────────────────────────────────────────────────┤
│  • 知彼知己 — Know task + know agent limits                 │
│  • 上兵伐谋 — Plan first, execute second                    │
│  • 奇正相生 — Standard flow + creative突破                   │
│  • 速战速决 — Speed is essential, limit iterations          │
│  • 先胜后战 — Ensure victory conditions before deploying    │
└─────────────────────────────────────────────────────────────┘
```

---

**Print tip**: This card fits on one page. Keep it next to your keyboard.

**Digital tip**: Bookmark this file or add to your agent workspace.
