---
name: time-capsule
version: 1.0.0
description: >
  Write messages to your future self — or your future team — that unlock
  when specific code conditions are met. "Dear future me: if you're reading
  this, someone finally tried to refactor the billing module. Here's what
  you need to know..." Encodes institutional knowledge into the codebase
  itself, triggered exactly when it's needed.
author: J. DeVere Cooley
category: fun-tools
tags:
  - knowledge-transfer
  - time-delayed
  - institutional-memory
  - fun
metadata:
  openclaw:
    emoji: "⏳"
    os: ["darwin", "linux", "win32"]
    cost: free
    requires_api: false
    tags:
      - zero-dependency
      - fun
      - knowledge
---

# Time Capsule

> "The best time to document your decisions was when you made them. The second best time is to leave a message for whoever has to deal with them later."

## What It Does

You know things right now that will be desperately needed later — but you don't know *when* later. Time Capsule lets you **bury messages in the codebase** that surface automatically when specific conditions are triggered:

- When someone finally touches that file nobody's touched in 2 years
- When the TODO count in a module exceeds a threshold
- When a specific dependency gets upgraded
- When test coverage drops below a certain percentage
- When a new developer makes their first commit
- On a specific date ("Hey team, the API license expires next month")

The message arrives exactly when it's relevant — not before (when it would be noise) and not after (when it would be too late).

## Capsule Types

### The Welcome Capsule
*Triggered when a new contributor makes their first commit*

```
╔══════════════════════════════════════════════════════════════╗
║  ⏳ TIME CAPSULE OPENED!                                     ║
║  Buried by: @jcooley on 2025-06-15                          ║
║  Trigger: New contributor detected                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Dear new team member,                                       ║
║                                                              ║
║  Welcome! Here's what I wish someone told me on day one:     ║
║                                                              ║
║  1. The "legacy" folder isn't legacy — it's the billing      ║
║     engine and it handles $2M/day. Don't rename anything.    ║
║                                                              ║
║  2. Tests in /integration are slow (40 min). Run /unit       ║
║     first. Only run integration before pushing to main.      ║
║                                                              ║
║  3. If you see a function called `doTheThing()` in           ║
║     auth.ts — yes, we know. No, don't fix it yet. There's   ║
║     a Time Capsule on it. You'll understand when it opens.   ║
║                                                              ║
║  4. The real architecture diagram is in /docs/actual.png,    ║
║     not /docs/architecture.png (which is from 2023).         ║
║                                                              ║
║  Good luck. You're going to love it here.                    ║
║  — The team, June 2025                                       ║
╚══════════════════════════════════════════════════════════════╝
```

### The Warning Capsule
*Triggered when someone modifies a specific dangerous file*

```
╔══════════════════════════════════════════════════════════════╗
║  ⏳ TIME CAPSULE OPENED!                                     ║
║  Buried by: @sarah on 2025-09-22                            ║
║  Trigger: src/payments/reconciliation.ts was modified        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  STOP. Read this before you change anything.                 ║
║                                                              ║
║  This file handles payment reconciliation with Stripe.       ║
║  It looks simple. It is NOT simple. Here's what you need     ║
║  to know:                                                    ║
║                                                              ║
║  - The 3-second delay on line 47 is NOT arbitrary.           ║
║    Stripe's webhook delivery has a race condition.            ║
║    Without the delay, 1 in ~500 payments double-charges.     ║
║    We learned this the hard way. Ticket: INC-2847.           ║
║                                                              ║
║  - The `Math.round()` on line 63 MUST stay.                  ║
║    Floating point + currency = disaster. We lost $12,847     ║
║    over 3 weeks before we found this. Ticket: INC-3012.      ║
║                                                              ║
║  - If you need to test this, use the Stripe sandbox with     ║
║    the webhook replay tool. Do NOT test with real charges.    ║
║    (Yes, someone did. No, we don't talk about it.)           ║
║                                                              ║
║  If you're refactoring: keep all three invariants above.     ║
║  If you're fixing a bug: check INC-2847 and INC-3012 first. ║
║                                                              ║
║  — Sarah, the last person who touched this file              ║
╚══════════════════════════════════════════════════════════════╝
```

### The Date Capsule
*Triggered on a specific calendar date*

```
╔══════════════════════════════════════════════════════════════╗
║  ⏳ TIME CAPSULE OPENED!                                     ║
║  Buried by: @mike on 2025-11-01                             ║
║  Trigger: Date reached: March 1, 2026                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Hey team,                                                   ║
║                                                              ║
║  The GeoLocation API license expires on March 31, 2026.     ║
║  Renewal costs $4,800/year. The free alternative (OpenCage)  ║
║  exists but doesn't support batch queries.                   ║
║                                                              ║
║  Decision needed:                                            ║
║  1. Renew the license ($4,800)                               ║
║  2. Migrate to OpenCage (est. 3 dev-days)                    ║
║  3. Build our own geocoding cache (est. 2 dev-weeks)         ║
║                                                              ║
║  I buried this 4 months early so you have time to decide.    ║
║  Don't let it expire accidentally like the SSL cert in 2024. ║
║                                                              ║
║  — Mike                                                      ║
╚══════════════════════════════════════════════════════════════╝
```

### The Threshold Capsule
*Triggered when a code metric crosses a threshold*

```
╔══════════════════════════════════════════════════════════════╗
║  ⏳ TIME CAPSULE OPENED!                                     ║
║  Buried by: @jcooley on 2025-08-10                          ║
║  Trigger: src/checkout/ test coverage dropped below 80%      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Coverage dropped below 80%. I knew this day would come.     ║
║                                                              ║
║  When I wrote the checkout tests in August 2025, coverage    ║
║  was 94%. I'm writing this capsule because I know that       ║
║  deadline pressure will slowly erode it. Here's the deal:    ║
║                                                              ║
║  The untested code paths are where the money bugs hide.      ║
║  Specifically: multi-currency, discount stacking, and        ║
║  partial refunds. If coverage dropped, it's probably         ║
║  because someone added a feature without adding tests.       ║
║                                                              ║
║  Recovery plan:                                              ║
║  1. Run: npm test -- --coverage checkout/                    ║
║  2. The red lines are the new code without tests             ║
║  3. Priority: anything touching money gets tests FIRST       ║
║  4. Don't let this drop below 70%. Below 70%, the           ║
║     checkout module becomes unfixable without fear.          ║
║                                                              ║
║  I've buried another capsule at 70%. You don't want to       ║
║  read that one.                                              ║
║                                                              ║
║  — Past You (who had more test coverage and more optimism)   ║
╚══════════════════════════════════════════════════════════════╝
```

### The Dependency Capsule
*Triggered when a specific dependency is updated*

```
╔══════════════════════════════════════════════════════════════╗
║  ⏳ TIME CAPSULE OPENED!                                     ║
║  Buried by: @dev_b on 2025-07-20                            ║
║  Trigger: react upgraded past v19                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  You're upgrading React. Brave. Here's the map:             ║
║                                                              ║
║  Known pain points from our codebase:                        ║
║  1. UserDashboard uses a class component with               ║
║     componentWillMount (deprecated). Convert to useEffect.   ║
║  2. We have a custom useRouter hook that wraps React Router. ║
║     Check if the new React version broke the Router API.     ║
║  3. The theme provider in src/ui/theme.tsx uses              ║
║     legacy context API. Must migrate to createContext.       ║
║  4. Our test setup mocks ReactDOM.render(). If React 19+    ║
║     changes the render API, ALL test mocks need updating.    ║
║                                                              ║
║  Estimated effort: 2-3 days if you know about these.        ║
║  Estimated effort: 2-3 WEEKS if you don't.                  ║
║                                                              ║
║  You're welcome.                                             ║
╚══════════════════════════════════════════════════════════════╝
```

### The Achievement Capsule
*Triggered when a milestone is reached*

```
╔══════════════════════════════════════════════════════════════╗
║  ⏳ TIME CAPSULE OPENED!                                     ║
║  Buried by: @jcooley on 2025-03-15                          ║
║  Trigger: Repository reached 1,000 commits                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🎉 1,000 COMMITS! 🎉                                        ║
║                                                              ║
║  When I buried this capsule, we had 247 commits and          ║
║  2 developers. I wasn't sure we'd make it here.              ║
║                                                              ║
║  Whoever opened this: look how far we've come.               ║
║  The early commits were messy. The architecture was wrong.   ║
║  We rewrote auth twice and the database three times.         ║
║  But here we are — 1,000 commits of learning, building,     ║
║  breaking, and fixing.                                       ║
║                                                              ║
║  Take a moment. Then get back to work. There's a capsule    ║
║  at 10,000 and it's going to be even better.                 ║
║                                                              ║
║  — Commit #247                                               ║
╚══════════════════════════════════════════════════════════════╝
```

## Trigger Types

| Trigger | Condition | Use Case |
|---|---|---|
| **File Touch** | Specific file is modified | Warn about landmines, explain non-obvious code |
| **Date** | Calendar date is reached | License expiry, scheduled reviews, reminders |
| **Threshold** | Metric crosses a value | Coverage drop, bug count spike, dependency age |
| **Dependency** | Package is updated/removed | Migration guides, known gotchas |
| **New Contributor** | First commit from unknown author | Onboarding tips, welcome messages |
| **Milestone** | Commit count, tag, release | Celebrations, retrospective notes |
| **Pattern** | Specific code pattern appears | "If you're writing another retry loop, see utils/retry.ts" |
| **Absence** | No commits for N days | "If nobody's touched this in 6 months, here's what to know..." |

## Burying a Capsule

```
╔══════════════════════════════════════════════════════════════╗
║                  ⏳ BURY A TIME CAPSULE                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  TRIGGER: When does this capsule open?                       ║
║  > When someone modifies src/payments/reconciliation.ts      ║
║                                                              ║
║  MESSAGE: What should future developers know?                ║
║  > [Your message here...]                                    ║
║                                                              ║
║  AUTHOR: Who buried this?                                    ║
║  > @sarah                                                    ║
║                                                              ║
║  EXPIRY: When should this capsule be destroyed if not opened?║
║  > Never (default) / After 1 year / After specific date     ║
║                                                              ║
║  ✅ Capsule buried.                                           ║
║  It will open the next time someone modifies                 ║
║  src/payments/reconciliation.ts.                             ║
╚══════════════════════════════════════════════════════════════╝
```

## When to Invoke

- **After making a non-obvious decision** — bury a capsule explaining WHY for the next person who touches it
- **Before leaving a team or project** — leave capsules with everything the next person needs to know
- **When you discover a landmine** — mark it so the next person doesn't step on it
- **For scheduled events** — license renewals, deprecation deadlines, review dates
- **For celebrations** — commit milestones, release targets, team achievements
- **When writing code you know will be confusing** — leave a map for the future explorer

## Why It Matters

Comments go stale. Documentation goes unread. Slack messages get buried. Wiki pages get forgotten. But a Time Capsule that **opens exactly when someone needs it** — triggered by the very action that makes the knowledge relevant — that's institutional memory with a pulse.

It's fun to bury them. It's even more fun to discover them. And the knowledge they carry can save hours, days, or (in the case of the Stripe reconciliation capsule) thousands of dollars.

Zero external dependencies. Zero API calls. Pure event-triggered knowledge delivery.
