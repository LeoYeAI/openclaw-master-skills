# Crisis Communications

Adapted from a contribution by @fyscleaning-jpg (PR #381).

Reactive PR for when something has gone wrong: a breach, an outage, a viral complaint, an executive controversy. Proactive PR runs on your timeline. In a crisis, the story is already running, and your job is to respond quickly, honestly, and without making it worse.

## Contents
- Get the facts first
- Legal, regulatory, and safety exposure
- Principles
- Severity tiers
- The first 60 minutes
- Channel order
- Playbooks by crisis type
- What not to do
- After the crisis
- Review checklist

## Get the Facts First

Before drafting anything, establish:

1. **What actually happened.** The confirmed fact, separate from the rumor. If it's unconfirmed, the statement says so.
2. **Who is affected.** Customers, employees, the public, a specific group, regulators.
3. **The exposure.** Contained, still unfolding, or likely to get worse (more data exposed, more people harmed, outage ongoing).
4. **What's already public.** Breaking on social, covered by press, or known only internally.
5. **What legal, security, or engineering can confirm right now** versus what's still under investigation.

Never draft a statement that asserts something not yet confirmed. A statement you walk back 24 hours later does more damage than a slower, accurate one.

## Legal, Regulatory, and Safety Exposure

If the incident involves a data breach, physical injury or safety risk, a lawsuit, or a regulator, loop in legal counsel before you admit fault, describe cause, or publish anything beyond a holding statement.

Data breaches can carry mandatory notification deadlines and required content, and these vary by jurisdiction and by the type of data involved. Counsel determines which apply. Don't state a specific deadline unless counsel has confirmed it.

Keep the legal posture and the public statement as separate documents. Counsel decides what you can say. The public statement says it in plain human language.

## Principles

- **Speed matters, accuracy matters more.** Silence in the first hours reads as incompetence or concealment. A wrong statement reads as dishonesty.
- **One source of truth.** Designate a single spokesperson and a single channel of record. Mixed messages from different staff become their own crisis.
- **Acknowledge before you explain.** Open with what happened and who it affects. Readers scan for "am I affected and what do I do."
- **Apologize without a "but."** "We're sorry this happened, but our systems generally..." is a defense with an apology in front. Once counsel has cleared accepting responsibility, say sorry, say what you're doing, and stop.
- **Keep updating.** A crisis is a sequence of updates. Commit to a cadence ("next update by 6pm ET") and keep it, even when the update is "still investigating."

## Severity Tiers

Match the response to the actual severity. When unsure, tier up: under-responding to a Tier 3 looks worse than over-responding to a Tier 2.

| Tier | Examples | Response |
|------|----------|----------|
| **1. Contained** | Single feature bug, isolated complaint thread, minor copy mistake | Support or community team replies directly. No public statement. |
| **2. Visible** | Service degradation, a complaint gaining traction, a marketing claim called out | Public acknowledgment on status page or social, owned by the support or marketing lead |
| **3. Significant** | Full outage, billing error across many customers, a widely shared customer-harm story | Formal exec-reviewed statement on status page, email, and social. Spokesperson designated. |
| **4. Severe** | Data breach, security incident, executive misconduct, safety issue, regulatory inquiry | Counsel-reviewed statement, exec-level spokesperson, dedicated incident page. Notification obligations may apply. |

## The First 60 Minutes

1. **Confirm the facts** with the people who have direct knowledge (engineering, security, legal, support lead), not secondhand summaries.
2. **Assess the tier.** For Tier 4, bring in legal counsel now.
3. **Designate the spokesperson** and the channel of record (status page, pinned post, or both).
4. **Publish a holding statement.** It says you know about the issue and are working on it, with zero unconfirmed claims about cause or scope. See [statement-templates.md](statement-templates.md).
5. **Notify staff before or alongside going public.** A short internal note covers what's happening, what to say if asked, and where to route press and customer questions.
6. **Set the next update time** and state it publicly.

## Channel Order

Getting the order wrong, such as posting publicly before telling affected customers, creates a second crisis.

1. **Directly affected parties first.** Individual email or in-app notice to the people actually impacted, especially for breaches and billing errors.
2. **Internal note**, in parallel with step 1.
3. **Status page or incident page.** The linkable source of truth you control and update.
4. **Owned social channels.** A short post linking to the full statement. Character limits force omissions that read as evasive.
5. **Press.** If reporters are already asking, respond directly instead of waiting. Press should never get the news before affected customers.

## Playbooks by Crisis Type

| Type | First move | Watch for |
|------|-----------|-----------|
| **Data breach / security incident** | Confirm scope with security and bring in counsel before any public claim about what was or wasn't exposed. Counsel checks notification obligations. | "No sensitive data was affected" is the statement most often walked back. Don't say it until security confirms it. |
| **Product outage** | Status page update within minutes, even if it only says "investigating." | Don't commit to an ETA you can't keep. "Next update by [time]" is safer than a guessed fix time. |
| **Executive misconduct** | Legal and board involvement before any statement. Here, getting it right outranks speed. | A statement that reads as protecting the executive over the people affected. |
| **Customer-harm story going viral** | Contact the customer privately before replying publicly. | Arguing facts in public reply threads. Resolve privately, then post a brief update if appropriate. |
| **Billing / pricing error** | Confirm scope (how many customers, how much money) before announcing the fix. | Waiting to be asked. Refund or credit proactively; refunds after public pressure read as conceding under fire. |
| **Layoffs leak early** | Move the internal announcement up so employees hear it from the company. | Letting the leak stand without an official statement. |
| **Misleading marketing claim called out** | Name the specific claim, correct it, and explain the fix. | Defending intent. The audience cares about the correction. |

## What Not to Do

- **Go silent.** "No new information yet, next update at [time]" beats nothing.
- **Delete criticism.** Deleted threads get screenshotted and become a second story about a cover-up.
- **Issue a non-apology.** "We're sorry if anyone was affected" puts the burden on the reader's reaction instead of owning the action.
- **Speculate.** "We believe this may have also affected..." starts a correction cycle. State what's confirmed and name what's still under investigation.
- **Admit fault or cause before the facts and counsel allow it.** You can acknowledge the issue and the impact without assigning blame you can't yet support.
- **Let legal language into the human statement.** "The Company denies any wrongdoing" inside a customer apology reads as insincere.
- **Bury the lede.** Don't open with paragraphs of context before saying what happened and who's affected.

## After the Crisis

1. **Public postmortem** for Tier 3 and 4: what happened, root cause, and what's changing. Specific, checkable commitments build trust; "we take this seriously" doesn't.
2. **Internal retro**, separate from the postmortem, on what should change in the response process itself.
3. **Track every promise.** If the statement promised a fix, credit, or policy change, see it through and post a follow-up when it ships.
4. **Watch sentiment for 1-2 weeks.** Crises often get a second wave when a new detail surfaces.

## Review Checklist

- Does the response match the tier?
- Have directly affected parties been notified before any public statement?
- Does the draft claim only what's confirmed?
- For breaches, injuries, lawsuits, or regulators: has counsel reviewed it?
- Is there one spokesperson and one channel of record?
- What's the next update commitment, and who owns it?
