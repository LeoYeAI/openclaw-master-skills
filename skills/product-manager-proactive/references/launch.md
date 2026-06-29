# Launch

This file covers three things: knowing when you're ready to launch, what to watch after you do, and how to make the soft-to-hard launch call.

For the full launch decision playbook (including go/no-go with blockers and team communication), use `run GTM playbook` from `references/playbooks.md`.

---

## Launch Readiness Checklist

Run this before any public release. All items should be confirmed — not "we'll handle it post-launch."

### Product
- [ ] Feature is complete to the agreed scope (not "almost done")
- [ ] Edge cases and error states are defined and handled (not just the happy path)
- [ ] Rollback plan exists: if we need to turn this off, how do we do it and how long does it take?
- [ ] Load tested: does it hold under expected (and 2x expected) traffic?
- [ ] Monitoring is configured: the team will know within 15 minutes if something breaks

### Engineering
- [ ] No P0 or P1 bugs open against this release
- [ ] Logging is in place to diagnose issues post-launch
- [ ] Deployment process is documented and rehearsed (no first-time deploys at launch)
- [ ] Rollback has been tested, not just planned

### Communications
- [ ] Support team briefed: they know what's launching, what edge cases to expect, and who to escalate to
- [ ] Changelog written and ready to publish
- [ ] User-facing documentation updated (if applicable)
- [ ] Internal announcement drafted for the team

### GTM
- [ ] Positioning is locked: one sentence on what this does and why it matters, agreed by PM + marketing
- [ ] Sales / marketing / CS teams briefed on what's changing and what to say
- [ ] Announcement copy approved (if doing a public launch)
- [ ] Success metrics defined: we know what "this launch worked" looks like in numbers

---

## Early Signal Monitoring Framework

After launch, watch these windows. Don't wait for a weekly review — issues compound fast.

### Hour 0–24: Stability check
What to watch:
- Error rate vs. pre-launch baseline (alert threshold: >20% elevation)
- Crash rate (alert threshold: any increase)
- Activation rate for the new feature (is anyone using it?)
- Support ticket volume (spike = user confusion)

Action: if any metric is outside threshold, PM calls a triage within 4 hours. Don't wait for the next standup.

### Day 2–7: Usage signal
What to watch:
- D1 retention (are users who activated on Day 0 coming back?)
- Feature adoption rate (% of eligible users who tried it)
- Support ticket category breakdown (are tickets about bugs, confusion, or missing features?)
- Drop-off point in the new flow (if instrumented)

Action: if D1 retention drops >10% from baseline, this is a product problem, not a comms problem — investigate the flow.

### Week 2: Value confirmation
What to watch:
- D7 retention
- NPS or CSAT delta (if tracked)
- Qualitative signal from sales / support / CS on feature reception
- Any unexpected user behavior patterns (workarounds, misuse, underuse)

Action: form a clear hypothesis on whether the launch delivered intended value. If not, decide: iterate now or in the next cycle?

---

## Soft Launch → Hard Launch Decision Gate

### Soft launch definition
- Controlled audience (internal users, beta group, specific cohort)
- No public announcement
- Monitoring active, team on standby
- Rollback can happen without user impact

### Hard launch gate — all 3 must be green before going public

| Gate | Threshold | Status |
|------|-----------|--------|
| D3 retention | ≥ pre-launch baseline | [ ] |
| Error rate | < threshold agreed with engineering | [ ] |
| Value prop confirmation | At least 3 user quotes confirming core value is landing | [ ] |

### Hard launch is blocked if any of these are true
- Any P0 or P1 bug is open
- GTM teams (marketing, sales, CS) are not aligned on messaging
- Support has not been briefed
- Monitoring is not active

### Making the call
PM owns the soft → hard launch gate. When all 3 green gates are met:
1. PM sends a "go for hard launch" message to stakeholders with the gate evidence
2. PM and engineering agree on a deployment window
3. GTM teams execute the public announcement

When gates are not met after 7 days post-soft-launch:
- PM runs a triage: what specifically isn't meeting the threshold?
- Is this a fixable bug or a product/positioning problem?
- If fixable: set a clear deadline (not "soon") and re-evaluate
- If structural: pause and decide whether to proceed with caveats or pull back

---

## Launch Retrospective

Run this within 2 weeks of hard launch.

Questions to answer:
1. Did the launch meet its success metrics? If not, by how much and why?
2. What surprised us (positive or negative)?
3. What did we find out post-launch that we should have known before?
4. What would we change in the process next time?

Output: a 1-page retrospective doc added to the knowledge base under `07-versions-releases/`.
