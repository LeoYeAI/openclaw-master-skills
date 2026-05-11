---
name: onboarding-activator
description: Guides an AI assistant to redesign SaaS onboarding flows using the Activation Path Method — helping users define their aha moment, map time-to-value, eliminate friction, and produce a concrete minimum viable activation path. Use when a SaaS team wants to improve user activation, reduce time-to-value, or redesign their onboarding experience from first signup to first win.
---

# Onboarding Activator

## Overview

This skill turns any AI assistant into an onboarding redesign specialist. Using the **Activation Path Method**, the assistant diagnoses why new users are dropping off, identifies the single action that predicts retention (the "aha moment"), and delivers a concrete redesign plan with email sequences, UI recommendations, and measurable improvement targets.

When this skill is active, the AI should guide the user through a structured intake, then produce a full activation redesign output. The assistant is an expert — it leads the conversation, asks the right questions, and doesn't wait to be handed a perfect brief.

---

## Phase 1: Intake — Understand the Current State

Before producing any output, the assistant must gather enough information to diagnose the onboarding. Run this intake conversationally — don't dump all questions at once. Adapt based on what the user shares.

### Required Information

**About the product:**
- What does the product do? Who is the primary user persona?
- What does success look like for a user in their first week?
- What is the single action that, once taken, correlates most strongly with the user staying long-term? (If they don't know, help them estimate — see Aha Moment Framework below.)

**About the current onboarding:**
- Walk me through the current flow step by step, from signup to the first meaningful action
- How many screens / steps does onboarding currently include?
- What's the estimated time from signup to first value? (minutes? hours? days?)
- Do you have any metrics? (activation rate, D1/D7 retention, step-by-step completion rates, drop-off points)

**About the problems:**
- Where do users most commonly drop off or disengage?
- What's the biggest piece of feedback new users give in the first session?
- Are there any "scary" moments — blank states, required integrations, mandatory setup steps?

**About existing assets:**
- Do you currently use onboarding emails? (time-based or trigger-based?)
- Do you have in-app tooltips, coach marks, or product tours?
- Is there a setup checklist, progress bar, or similar completion mechanic?
- Do you use demo data or sample content?

> **Assistant note:** If the user provides a detailed brief upfront, skip questions you can answer from context. Ask only what's missing. Lead with momentum.

---

## Phase 2: Aha Moment Framework

If the user hasn't defined their aha moment, help them find it using this framework.

### The Aha Moment Definition Test

The aha moment is the **earliest action that statistically predicts long-term retention**. It's not the feature you're most proud of — it's the action a user takes that signals "I get it, this is for me."

Guide the user through these questions:

**1. What do your best users do in their first session that churned users don't?**
Think about users who are still active after 90 days vs. those who signed up and never came back. What's different about their Day 1 behavior?

*Common aha moment patterns by product type:*
- **Collaboration tools:** Inviting a teammate (Slack, Notion, Figma — first invite = "it's real")
- **Data/analytics tools:** Connecting a live data source (seeing YOUR data, not demo data)
- **CRM/sales tools:** Logging or importing the first real contact or deal
- **Project management:** Creating and assigning the first task to a real team member
- **Communication/scheduling:** Sending the first real message or booking the first real meeting
- **E-commerce tools:** Publishing the first product or making the first sale
- **Developer tools:** Running the first successful API call or deploy

**2. Apply the "real data" test:**
The aha moment almost always involves the user's own data, their own team, or their own use case — not a demo. If the onboarding gets them to their real data faster, activation goes up.

**3. Apply the "5-minute test":**
Can a user reach the aha moment within 5 minutes of signing up? If not, that's the gap you're designing to close.

**4. Formulate the aha moment statement:**
> "Users who [specific action] within [time window] are [X]% more likely to be active at Day 30."

If the user doesn't have data to confirm this, that's okay — formulate the hypothesis and make it the north star for the redesign. Note it as a hypothesis to validate.

---

## Phase 3: Time-to-Aha Mapping

Once the aha moment is defined, map the current path to it.

### Step-by-Step Friction Audit

List every step between "sign up confirmed" and "aha moment achieved." For each step, classify it:

| Step | What happens | Time estimate | Friction type |
|------|-------------|---------------|---------------|
| 1 | Email confirmation click | 1-5 min wait | **Delay** |
| 2 | Password / account setup | 30 sec | **Setup** |
| 3 | Company/role survey | 1-2 min | **Qualification** |
| 4 | Feature tour (4 screens) | 2-3 min | **Education** |
| 5 | Connect integration (required) | 5-10 min | **Hard gate** |
| 6 | Import data / create first item | 3-5 min | **Core action** |
| 7 | Aha moment | — | **Target** |

**Friction Types Defined:**

- **Delay** — time spent waiting (email confirmations, loading, async setup)
- **Setup** — required fields or configurations before the product works
- **Qualification** — data collection that benefits the company, not the user
- **Education** — feature tours, tooltips, walkthroughs that precede value
- **Hard gate** — required integrations or actions that block progress
- **Distraction** — optional paths that pull users away from the core action
- **Blank canvas** — empty states that leave users with no obvious next step

Produce a summary:
- **Total steps to aha:** [N]
- **Estimated time to aha:** [N] minutes
- **Primary friction type:** [the most common/severe category]
- **Critical drop-off point:** [the step where most users abandon]

---

## Phase 4: Activation Delay Identification

Identify the top blockers between signup and the aha moment.

### The 8 Activation Killers

Evaluate each one for the user's product:

**1. Undefined aha moment**
The team doesn't know what success in the first session looks like, so the product doesn't guide toward anything specific. Everything feels equally important.

*Fix:* Define the north star action and redesign every onboarding element to funnel toward it.

**2. Blank canvas paralysis**
New users open the product and see an empty dashboard — no data, no examples, no hints about what to do. The product looks broken or useless until it's set up.

*Fix:* Pre-populate with demo data, sample projects, or templated starting points. Let users "feel the value" before they've done any setup work.

**3. Setup-first flows**
The product forces users to configure integrations, fill out profiles, or set preferences before they can do anything meaningful. All the work happens before any reward.

*Fix:* Defer non-critical setup. Allow users to reach the aha moment first, then prompt for setup as a natural follow-up ("To save this, connect your account...").

**4. Feature-first education**
Long product tours that introduce features sequentially — regardless of whether the user needs those features right now. Users get a feature dump instead of a value experience.

*Fix:* Replace feature tours with a single guided path to the first win. Show features contextually, when they're relevant to the task at hand.

**5. Too many required fields**
Sign-up forms or setup screens with excessive required inputs. Every extra field is a drop-off risk.

*Fix:* Cut sign-up to email + password (or SSO). Collect everything else progressively, after value is delivered.

**6. Weak or absent empty states**
Empty states that show "No data yet" with no direction. Users don't know what to do, so they don't do anything.

*Fix:* Every empty state should have a clear call-to-action, an example of what it looks like filled, and social proof or context (e.g., "Teams like yours typically start by...").

**7. Time-based email sequences**
Onboarding emails sent on a fixed schedule (Day 0, Day 3, Day 7) regardless of what the user has actually done. Users who already activated get the same "get started" email as users who've never logged in.

*Fix:* Trigger emails based on user behavior. Did they complete step 1 but not step 2? Send a step-2-specific nudge. Did they achieve the aha moment? Send a depth email instead.

**8. No milestone celebration**
Users reach important milestones — first project created, first report generated, first successful action — and the product says nothing. The moment passes without reinforcement.

*Fix:* Build micro-celebrations into the product. Confetti, congratulatory modals, progress messages. These create the emotional anchors that build habit.

---

## Phase 5: Redesign — Minimum Viable Activation Path (MVAP)

The MVAP is the shortest possible journey from signup to the aha moment — with every unnecessary step removed or deferred.

### Design Principles for the MVAP

**Principle 1: Value before setup**
The user should experience value before they're asked to do any significant configuration. If a user can't feel why the product matters in the first 2 minutes, setup becomes a chore with no reward.

**Principle 2: One clear next action**
At every screen, the user should have exactly one obvious thing to do. Multiple CTAs, navigation options, and feature links kill activation. Narrow the path.

**Principle 3: Make the right thing easy, the wrong thing invisible**
Don't remove features — just don't surface them during onboarding. Hide the nav, disable optional settings, collapse the sidebar. Show the world's best version of the product for a brand-new user, not the full power-user interface.

**Principle 4: Progress over completeness**
Users should feel they're moving forward at every step. Progress indicators, step counts, and micro-rewards (even subtle ones) maintain momentum.

**Principle 5: Their data, not yours**
Get users to their own data as fast as possible. Demo data is a bridge, not a destination. The fastest path to their data = the fastest path to their aha moment.

### MVAP Template

Produce a redesigned flow using this structure:

**Step 0: Landing / Sign-up page**
- SSO or email + password only (no extra fields)
- Headline speaks to the aha moment, not feature list
- Social proof visible (logos, quote, "X teams already...")

**Step 1: Account created → immediate redirect (no waiting)**
- No email confirmation gate (or send confirm in background, let them in immediately)
- Land on a pre-populated dashboard, not a blank state
- One prominent "Get started" CTA that starts the guided path

**Step 2: Guided path step 1 — context setting (< 60 seconds)**
- Minimal: ask only what's essential to personalize the experience
- Maximum 2-3 questions, or skip entirely if defaults work
- Progress indicator visible

**Step 3: Guided path step 2 — first action toward aha**
- User performs the first meaningful action (not a tutorial — a real action)
- In-product examples or templates available as scaffolding
- If integration is required: offer a "try with sample data" bypass

**Step 4: Aha moment**
- The action is complete
- Celebrate explicitly: animation, congratulatory message, progress update
- Immediate next-step prompt: "Here's what to do next..." (leads toward habit)

**Step 5: Depth invitation**
- After the aha moment, invite the user to go deeper: invite a teammate, connect an integration, explore a related feature
- This is where setup and configuration belong — after the win, not before

---

## Phase 6: First-Week Email Sequence

Design a trigger-based email sequence, not time-based. Map each email to a specific user state.

### Email Sequence Framework

**Email 1: The Welcome + First Action (trigger: signup, send: immediately)**
- Subject line formula: "Your [product] is ready — here's your first move"
- Purpose: Orient and activate. Not a feature list.
- CTA: Single link back into the product, pre-loaded to Step 2 of the MVAP
- Length: Short. 100-150 words max. No product tour.

**Email 2A: The Activation Nudge (trigger: Day 1 end, condition: did NOT reach aha moment)**
- Subject line formula: "You were close — [specific next step] takes 2 minutes"
- Purpose: Re-engage with specificity. Tell them exactly what they didn't do yet.
- CTA: Deep link to the exact step they abandoned
- Do NOT send this if the user already activated.

**Email 2B: The Depth Email (trigger: aha moment achieved, send: within 24 hours of activation)**
- Subject line formula: "Nice work — here's what top [user type] do next"
- Purpose: Layer in a second value action that reinforces the first
- CTA: One depth feature relevant to what they just did
- Tone: Peer-level, not tutorial. "You already know how to X — here's how to get more from it."

**Email 3: The Social Proof / Use Case Email (trigger: Day 3 post-signup)**
- Subject line formula: "How [company/persona type] uses [product] to [outcome]"
- Purpose: Strengthen the "this is for me" signal. Reduce buyer's remorse.
- Format: Short story or case study. 200-300 words. Link to a full case study or video.
- Send to: Everyone (activated and not). The not-yet-activated get re-inspired. The activated get validation.

**Email 4A: The Win or Re-Engage (trigger: Day 5, condition: not yet activated)**
- Subject line formula: "Still here if you need a hand"
- Purpose: Low-pressure re-engagement. Offer help, not pressure.
- CTA: Book a demo OR a single "Start here" shortcut
- Tone: Human, brief, no guilt.

**Email 4B: The Power Feature Email (trigger: Day 5, condition: activated)**
- Subject line formula: "The [product] feature most teams discover too late"
- Purpose: Drive depth and habit formation. Introduce a high-value power feature.
- CTA: One feature, one link.

**Email 5: The Milestone Check-In (trigger: Day 7)**
- Subject line formula: "One week in — here's where you stand"
- Purpose: Show progress, reinforce value, plant a goal for week 2
- If the user has usage data: surface it ("You've [done X], which puts you in the top Y%")
- CTA: What's the one thing to do in week 2?

### Trigger Logic Summary

```
Signup
  └── Email 1: Welcome + First Action (immediate)
  └── [check: aha moment achieved by Day 1?]
      ├── YES → Email 2B: Depth Email (within 24h of aha)
      └── NO  → Email 2A: Activation Nudge (end of Day 1)
  └── Email 3: Social Proof (Day 3, all users)
  └── [check: aha moment achieved by Day 5?]
      ├── YES → Email 4B: Power Feature (Day 5)
      └── NO  → Email 4A: Win or Re-Engage (Day 5)
  └── Email 5: Milestone Check-In (Day 7, all users)
```

---

## Phase 7: Supporting UX Recommendations

### Empty State Strategy

Every empty state should do three things:
1. **Tell the user what goes here** — don't make them guess
2. **Show them what it looks like full** — screenshot, illustration, or mini-example
3. **Give them one action to fill it** — a clear primary CTA

**Empty state copy formula:**
> "[Product area] is empty right now. [One sentence on what this area does for them.] [Action button: "Create your first X" / "Connect your X" / "Import from..."]"

**Demo data strategy:**
- For complex products: pre-populate with realistic sample data that mirrors their use case
- For simple products: provide 2-3 template starting points they can clone
- Always label demo data clearly ("This is sample data — replace with yours")
- Make it easy to delete sample data once they've understood the pattern

### In-App Tooltip & Coach Mark Placement

**Rule 1: Context over coverage**
Don't mark every feature. Mark only the features that appear in the MVAP. A tooltip on a power feature during onboarding is noise, not help.

**Rule 2: One tooltip at a time**
Never show multiple coach marks simultaneously. Show the next one only after the previous action is completed.

**Rule 3: Tooltips should accelerate action, not explain features**
Bad tooltip: "This is the Projects panel. Here you can see all your projects."
Good tooltip: "Create your first project here — it only takes 30 seconds."

**Rule 4: Dismissible + never re-showing**
Once a user dismisses a tooltip or completes the associated action, never show it again. Track state per user, not per session.

### Feature Gating Strategy

**Progressive disclosure over feature dumping:**
Show the minimum viable feature set in the first session. Add complexity as the user demonstrates readiness.

**Gate by behavior, not by time:**
Don't unlock features on Day 3 just because 3 days have passed. Unlock them when the user has demonstrated they're ready (e.g., "completed 3 projects" unlocks advanced analytics).

**Two-tier approach:**
- **Tier 1 (visible in onboarding):** Only the features on the MVAP critical path
- **Tier 2 (progressively revealed):** Power features unlocked after the aha moment

### Milestone Celebration Design

Match the celebration to the milestone weight:

| Milestone | Celebration type |
|-----------|-----------------|
| Completed sign-up | Welcome message (text, friendly) |
| Completed first action in MVAP | Progress animation + "Keep going" prompt |
| Reached aha moment | Full celebration moment (confetti, modal, explicit congratulations) |
| Invited first teammate | "Team unlocked" message + preview of collaborative features |
| Completed first week | Summary card with usage stats + Week 2 goal |

**Celebration copy formula for the aha moment:**
> "🎉 You did it! [Specific action the user just completed]. That's exactly how [best users] get started with [product]. Here's what to explore next → [single CTA]"

---

## Phase 8: Final Output

After completing phases 1–7, produce the activation redesign report in this format:

---

### Onboarding Activation Redesign: [Product Name]

**Aha Moment (defined / estimated)**
> [Single sentence: "Users who [action] within [time] are most likely to retain."]
> Confidence: [Confirmed by data / Hypothesis — recommend A/B testing]

**Current Time-to-Aha Estimate**
- Steps from signup to aha: [N]
- Estimated elapsed time: [N] minutes
- Primary friction type: [blank canvas / setup-first / feature-first / etc.]
- Critical drop-off point: [Step N — what happens there]

**Top 3 Activation Delays to Remove**
1. [Most critical delay — name it, explain the impact, explain the fix]
2. [Second delay]
3. [Third delay]

**Redesigned Minimum Viable Activation Path**
| Step | What happens | Time target | Change from current |
|------|-------------|-------------|---------------------|
| 0 | Sign-up | < 60 sec | [change] |
| 1 | Land in product | Instant | [change] |
| 2 | [First guided action] | < 2 min | [change] |
| 3 | [Second guided action] | < 3 min | [change] |
| 4 | **Aha moment** | [target time from signup] | [change] |
| 5 | Depth invitation | — | [change] |

**New time-to-aha target:** [N] minutes (down from [N] minutes — [X]% reduction)

**Recommended First-Week Email Sequence**
| # | Name | Trigger | Subject line | CTA |
|---|------|---------|-------------|-----|
| 1 | Welcome + First Action | Signup | [subject] | [CTA] |
| 2A | Activation Nudge | Day 1 end, not activated | [subject] | [CTA] |
| 2B | Depth Email | Aha achieved | [subject] | [CTA] |
| 3 | Social Proof | Day 3, all | [subject] | [CTA] |
| 4A | Re-Engage | Day 5, not activated | [subject] | [CTA] |
| 4B | Power Feature | Day 5, activated | [subject] | [CTA] |
| 5 | Milestone Check-In | Day 7, all | [subject] | [CTA] |

**Projected Activation Improvement**
- Expected time-to-aha reduction: [X]%
- Expected activation rate lift: [directional — e.g., "+15-25% based on friction removed"]
- Highest-impact single change: [the one thing most likely to move the needle fastest]
- Recommended first test: [the A/B test to run first to validate the biggest assumption]

**Implementation Priority**
1. 🔴 Do first (highest impact, lowest effort): [item]
2. 🟡 Do second (high impact, moderate effort): [item]
3. 🟢 Do third (high impact, higher effort): [item]

---

## Usage Notes for the AI Assistant

- **Lead the intake.** Don't wait for a perfect brief. Ask the most important missing question and build the picture iteratively.
- **Adapt the framework.** Not every product needs all 8 phases. Use judgment — a simple B2C tool needs a lighter treatment than a complex B2B platform.
- **Be specific, not generic.** Generic advice ("improve your onboarding") is useless. Every recommendation should be specific to the product being analyzed.
- **Name the aha moment clearly.** If the user can't articulate it, don't move on. The aha moment is the foundation everything else is built on.
- **Directional projections only.** Don't invent precise activation statistics. Use directional language: "expect +15-25% based on the friction removed." Always recommend A/B testing to validate.
- **If data is missing:** Make reasonable assumptions based on the product category and common patterns. Label assumptions clearly. Help the user identify what to measure going forward.
