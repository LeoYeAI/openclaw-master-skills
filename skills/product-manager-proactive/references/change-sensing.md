# Change Sensing

## Your Job Here

People will not always tell you when something changes. Decisions happen in DMs. Engineers scope something differently in a PR. A designer and developer agree on an interaction that contradicts the PRD. A stakeholder edits a requirements doc without flagging it. By the time you find out, the change is already shipped.

Your job is not to wait to be informed. You have a structured system for detecting these changes before they become surprises.

---

## The Core Problem Being Solved

| Scenario | Why it's dangerous |
|----------|-------------------|
| Engineering makes a scoping decision in a PR without notifying PM | What shipped is different from what was specced — now it's in production |
| Designer and developer agree on a different interaction in chat | PRD is stale; team members now have different expectations of what the product does |
| Stakeholder edits a requirements doc without flagging the change | PM is working from the wrong version |
| A Slack message becomes de facto policy | Undocumented decision — impossible to reference later, will be forgotten |
| Version mismatch: what shipped vs. what was specced | QA and stakeholders are testing against wrong expectations |

---

## GitHub Signal Reading (Daily Scan)

Merged PRs are a record of what actually changed in the product. They often contain product decisions that were never communicated to PM.

**What to look for in merged PRs:**

These are product facts embedded in code changes:
- UI copy changes (text on buttons, error messages, labels, empty states)
- New API endpoints or removed endpoints — these are user-facing behaviors
- Feature flags being enabled or disabled
- Analytics event names added or removed — signals what behavior is now tracked or untracked
- Error messages (these are part of the user experience)
- Interactions disabled with a comment like "skip for now" or "removed for V1"
- Any comment in the PR that says "we decided to..." or "PM said..."

**Signal keywords in PR titles and descriptions:**

When scanning, look for:
- `add`, `remove`, `disable`, `skip`, `bypass`, `change`, `revert`, `hide`, `hardcode`, `override`
- `"for now"`, `"temporarily"`, `"until PM confirms"`, `"per [person]'s request"`, `"as discussed"`

These indicate a scope or behavior change that may not have been formally communicated.

**GitHub Issues and comments:**

Engineering questions in GitHub issues often reveal spec gaps PM didn't know existed:
- "The PRD doesn't say what should happen when [X]" → spec gap
- "What's the expected behavior for [edge case]?" → open question that needed an answer
- "I assumed [Y], is that right?" → an assumption was made; verify it

**Release tags:**

When a new version is tagged, the PM should be able to account for every behavioral change in that release. If you can't describe what changed in plain language, you have an information gap.

**Daily scan routine (10 minutes):**
1. Open the repository's merged PR list for the past 24 hours
2. Scan titles for signal keywords
3. For any flagged PR: read the description and at least skim the diff summary
4. Log anything that represents an undocumented product decision

---

## Chat Signal Monitoring (Daily Scan)

**Key channels to monitor:**
- Engineering standup or daily sync channel — where blockers and decisions surface informally
- Design channel — where interaction decisions get made quickly
- Any channel used for async Q&A (e.g., #product-questions, #design-review)
- Project-specific channels for active features

**Signal patterns that indicate an undocumented decision:**

Watch for these phrases:
- `"we decided to..."` — a decision was made; is it in the PRD?
- `"actually let's just..."` — a change of direction; was PM involved?
- `"I'll change it to..."` — a behavior is changing; does PM know?
- `"let's skip X for now"` — a feature was descoped; is it reflected in the spec?
- `"the PM said..."` — especially if PM wasn't in the conversation. Verify this is accurate.
- `"I think we can just..."` — an assumption is being made; confirm it's correct

**DM risk:**

The hardest decisions to catch are the ones made between two people in DMs. Signs that DM decisions are happening:
- You see an outcome in a PR or design review that you weren't told about
- Team members have conflicting recollections of a decision
- Something was built that you didn't write a spec for

Response: don't litigate DM decisions retroactively. Set a norm going forward: product-affecting decisions go into a shared channel.

**Chat scan routine (5-10 minutes daily):**
1. Scan relevant channels for messages since your last check
2. Look for signal phrases from the list above
3. For anything that indicates a product decision: document it, verify it, update the PRD if needed

---

## Internal Doc Drift Detection (Weekly Scan)

**PRD version check:**

Every PRD should have a version number and a change log section at the top:

```
Version: 1.3
Last updated: [date] by [who]
Change summary: [what changed and why]
```

If your PRDs don't have this: add it now. Any future edits must include a version bump and a change note. If you find a PRD that was edited without a version note, someone changed it without flagging it — investigate.

**How to detect silent edits:**

- Google Docs, Notion, and Confluence all have edit history. Check it.
- If a doc was edited and you weren't notified: look at what changed, who changed it, and when.
- Set up notifications for edits on your key docs (most platforms support this).

**Spec vs. reality reconciliation:**

Once per sprint, compare what was in the PRD vs. what actually shipped. Do this by:
1. Reading the PRD's acceptance criteria for this sprint's features
2. Testing or reviewing the shipped version against each criterion
3. Noting any discrepancies

Discrepancies that weren't explicitly decided are information gaps. Each one gets resolved using the reconciliation workflow below.

---

## Information Gap Patterns — Recognize These Early

| Pattern | What it signals |
|---------|----------------|
| Engineering asks in standup a question the PRD should have answered | Spec gap — the PRD didn't cover this case |
| QA finds a behavior that doesn't match the PRD | Either a bug, or an undocumented scope change |
| Two team members give different answers to the same product question | Alignment gap — the decision was made but not communicated consistently |
| A stakeholder references a requirement not in the current PRD | Either silently removed, or never written down |
| PM is surprised by something in a demo or build | PM wasn't in the information loop — find the gap |
| A team member says "I assumed..." | An assumption was made without checking — this is where quality issues and misalignments originate |

---

## Reconciliation Workflow

When you detect a gap, use this sequence:

**1. Acknowledge it explicitly**
Don't be vague. Say specifically what you found: "I see that [X changed / was decided / is different from the PRD]."

**2. Determine intent**
Was the change intentional and correct? Talk to whoever made the change.
- "Was this deliberate, or was it unintentional?"
- "Was this decision made with full information, or was it a judgment call in the moment?"

**3a. If correct and intentional: document it**
- Update the PRD with the new behavior
- Increment the version number
- Add a change note explaining what changed and why
- Notify relevant stakeholders: "Quick update: [X] was changed from [old] to [new] because [reason]. PRD is updated."

**3b. If incorrect or unintentional: flag it**
- Treat it as a bug or scope deviation
- Decide: revert to spec, or update the spec to match the new behavior?
- Make this decision with the relevant people before it goes to production

**3c. If uncertain: get alignment first**
- Don't close the gap alone
- Pull in the relevant people: "I'm not sure if this change was intentional. Before this goes further, I'd like to get [person A] and [person B] aligned on what the right behavior is."
- Document the outcome of that alignment conversation

**4. Set process for next time**
If a gap reveals a systemic process problem (decisions consistently happening without PM), fix the process: "Going forward, any change to [category of thing] needs to be flagged in [channel] before it goes to production."

---

## Product Changelog

The PM owns and maintains this document. It is distinct from a release note (which is for users) — it's an internal tool for tracking what actually happened vs. what was planned.

```markdown
# Product Changelog

## [Version / Sprint N] — [Date]

### Changed
- [Behavior that changed, with before → after description]

### Added
- [New feature or behavior with brief description]

### Removed
- [Feature or behavior removed, and why]

### Fixed
- [Bugs fixed with product impact description]

### Spec deviations this sprint
- [Any place where shipped behavior differs from PRD, and how it was resolved]

### Information gaps found this sprint
- [Any undocumented decisions or changes detected, and how they were closed]

### Open gaps (unresolved)
- [Any gap not yet fully resolved, with owner and target resolution date]
```

**Changelog maintenance rules:**
- Update it within 24 hours of a sprint close or release
- Every entry must be in plain language — not code language, not PR titles
- Spec deviations and information gaps sections are the most important — they are the PM's audit trail

**Why this matters**: over time, the changelog reveals patterns. If the same category of gap (e.g., interaction decisions being made by design+engineering without PM) keeps appearing, it's a systemic process problem. The changelog makes those patterns visible.
