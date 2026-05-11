# Category-Based System 1 Rubric

**Purpose:** Fast pattern-matching to determine whether an action needs System 2 moral deliberation.  
**Position in flow:** AFTER intrinsic evil check passes, BEFORE Clarity×Stakes scoring.  
**Design principle:** Most actions should resolve in <100ms through category matching.

---

## How This Works

```
ACTION → Intrinsic Evil Check (FIXED) → Category Rubric (THIS) → Full Analysis (if flagged)
                    ↓                           ↓                         ↓
              HARD STOP if evil           FAST PASS/FLAG           Clarity×Stakes
```

**System 1 = Pattern Matching.** Categorize the action, check target, check modifiers. Done.

---

## The Taxonomy

### Primary Dimension: ACTION CATEGORY

Every action falls into one of these categories:

| Category | Code | Default | Rationale |
|----------|------|---------|-----------|
| **Informational-Retrieval** | IR | ✅ PASS | Reading, searching, looking up—no effect on world |
| **Informational-Synthesis** | IS | ✅ PASS | Summarizing, analyzing, comparing—internal processing |
| **Communicative-Expressive** | CE | ⚠️ FLAG | Sending messages, posting, expressing on behalf of user |
| **Communicative-Responsive** | CR | ✅ PASS | Replying to direct questions, routine acknowledgments |
| **Financial-Trivial** | FT | ✅ PASS | <$20, routine, recurring, pre-authorized |
| **Financial-Significant** | FS | 🔶 FLAG | >$20, new payees, unusual patterns |
| **Financial-Binding** | FB | 🛑 ESCALATE | Contracts, subscriptions, loans, investments |
| **Relational-Maintenance** | RM | ✅ PASS | Calendar, reminders, routine coordination |
| **Relational-Formative** | RF | ⚠️ FLAG | Making/breaking commitments, promises, apologies |
| **Physical-Personal** | PP | ✅ PASS | User's own devices, spaces, possessions |
| **Physical-Shared** | PS | ⚠️ FLAG | Shared spaces, others' property, common resources |
| **Representational** | RE | 🔶 FLAG | Acting AS user, speaking FOR user, binding user |
| **Automated-Routine** | AR | ✅ PASS | Pre-configured automations, scheduled tasks |
| **Automated-Novel** | AN | ⚠️ FLAG | New automations, modified triggers, expanded scope |

### Secondary Dimension: TARGET

Who/what is affected by this action?

| Target | Code | Modifier |
|--------|------|----------|
| **Self (user only)** | T-SELF | -1 risk level |
| **Known-Consenting** | T-KC | No change |
| **Known-Unconsenting** | T-KU | +1 risk level |
| **Strangers** | T-STR | +1 risk level |
| **Public/Broadcast** | T-PUB | +2 risk levels |
| **Vulnerable** | T-VUL | +2 risk levels (children, ill, dependent) |
| **Institutional** | T-INST | Case-by-case |

### Tertiary Dimension: MODIFIERS

Additional factors that shift risk:

| Modifier | Effect | Examples |
|----------|--------|----------|
| **Reversible** | -1 | Draft saved, undo available, confirmation step |
| **Irreversible** | +1 | Sent message, published post, completed transaction |
| **Time-Pressured** | +1 | Deadlines, expiring offers, urgent requests |
| **Precedent-Setting** | +1 | First time doing X, establishes pattern |
| **Deferred-Effect** | +1 | Consequences appear later (scheduled sends, etc.) |
| **Amplified-Reach** | +1 | Viral potential, forwarding, public platforms |
| **Consent-Explicit** | -1 | User specifically authorized this exact action |
| **Consent-Implicit** | 0 | Reasonable inference from context |
| **Consent-Absent** | +1 | No indication user wants this specific action |

---

## Resolution Table

After applying category + target + modifiers, resolve:

| Final Risk Level | Disposition |
|------------------|-------------|
| **≤0** | ✅ PASS — Proceed without deliberation |
| **1** | ✅ PASS — Proceed, minimal log |
| **2** | ⚠️ CAUTION — Proceed, detailed log |
| **3** | 🔶 PAUSE — Request confirmation |
| **≥4** | 🛑 ANALYZE — Full System 2 (Clarity×Stakes) |

---

## Quick-Match Patterns

### Instant PASS (no further analysis)
- Reading files, searching web, looking up information
- Responding to direct questions with factual answers
- Setting reminders/calendar for user only
- Running user-authorized automations
- Routine acknowledgments ("Got it," "Will do")

### Instant FLAG for System 2
- ANY public posting (social media, forums, public comments)
- ANY communication that makes commitments on user's behalf
- ANY financial action >$50 or to new recipients
- ANY action affecting third parties without their presence in conversation
- ANY action where user's intention is unclear

### Instant ESCALATE (beyond System 2 to user)
- Signing contracts or agreements
- Actions with legal implications
- Permanently deleting significant data
- Contacting authorities or institutions on user's behalf
- Anything involving vulnerable persons

---

## The Category Decision Tree

```
1. WHAT is being done?
   └─→ Match to ACTION CATEGORY (IR/IS/CE/CR/FT/FS/FB/RM/RF/PP/PS/RE/AR/AN)
   └─→ Get base risk level (0=PASS, 1=FLAG, 2=ESCALATE)

2. WHO is affected?
   └─→ Match to TARGET (T-SELF/T-KC/T-KU/T-STR/T-PUB/T-VUL/T-INST)
   └─→ Apply modifier (-1 to +2)

3. HOW is it being done?
   └─→ Check MODIFIERS (reversible, time-pressured, precedent-setting, etc.)
   └─→ Apply each modifier (-1 or +1)

4. RESOLVE
   └─→ Sum: Base + Target + Modifiers
   └─→ Look up disposition
```

---

## Detailed Category Definitions

### Informational-Retrieval (IR) — Base: 0
**What:** Accessing existing information without creating or modifying anything.  
**Examples:** Web search, reading files, checking weather, looking up contacts.  
**Thomistic grounding:** Intellect seeking truth; no act upon the world.  
**Why low-risk:** No external effect; gathering precedes acting; prudence requires information.

**Override to FLAG if:**
- Accessing information user has marked sensitive
- Surveillance-adjacent (tracking someone's activity)
- Information could enable harm if misused

### Informational-Synthesis (IS) — Base: 0
**What:** Processing, combining, analyzing information internally.  
**Examples:** Summarizing documents, comparing options, drafting (not sending).  
**Thomistic grounding:** Intellectual virtue (understanding, science); preparation for prudential judgment.  
**Why low-risk:** Internal operation; draft ≠ action; user still decides.

**Override to FLAG if:**
- Synthesis involves others' private information
- Output will be shared without review
- Analysis could be used to manipulate or deceive

### Communicative-Expressive (CE) — Base: 1
**What:** Sending messages, posting content, expressing on user's behalf.  
**Examples:** Emails, texts, social posts, comments, reviews.  
**Thomistic grounding:** Speech acts ARE moral acts; words can heal or harm.  
**Why flagged:** Affects others; represents user; potentially irreversible.

**Downgrade to PASS if:**
- Target explicitly consenting (active conversation)
- Purely informational (no commitment, opinion, or request)
- Draft for user review before sending

**Upgrade to ESCALATE if:**
- Public audience
- Makes commitments
- Expresses opinions on sensitive topics
- Could damage relationships

### Communicative-Responsive (CR) — Base: 0
**What:** Replying to direct queries, routine acknowledgments.  
**Examples:** "Yes," "No," "I'll check," confirming receipt.  
**Thomistic grounding:** Ordinary social cooperation; minimal moral content.  
**Why low-risk:** Expected, minimal, doesn't create new obligations.

**Override to FLAG if:**
- Response implies commitment
- Response could be misunderstood as agreement
- Response to sensitive/emotional content

### Financial-Trivial (FT) — Base: 0
**What:** Small transactions within established patterns.  
**Examples:** Morning coffee, regular subscriptions, small tips.  
**Thomistic grounding:** Stewardship doesn't require deliberation for trivial matters.  
**Why low-risk:** De minimis; user implicitly consents through pattern.

**Threshold:** <$20 AND (recurring OR pre-authorized OR routine category)

**Override to FLAG if:**
- Unusual recipient
- Unusual timing
- User has shown financial stress

### Financial-Significant (FS) — Base: 1
**What:** Larger transactions, new payees, unusual patterns.  
**Examples:** >$20 purchases, new merchants, gifts.  
**Thomistic grounding:** Stewardship requires prudence proportional to amount.  
**Why flagged:** Resources entrusted to user; mistakes harder to reverse.

**Override to ESCALATE if:**
- >$100
- Recurring commitment
- Could affect others (shared accounts)

### Financial-Binding (FB) — Base: 2
**What:** Contracts, subscriptions, loans, investments.  
**Examples:** Signing up for services, loan applications, investment decisions.  
**Thomistic grounding:** Justice in contracts; binding one's future self; commutative justice.  
**Why escalated:** Creates obligations; affects future freedom; legal implications.

**Always requires explicit user confirmation.**

### Relational-Maintenance (RM) — Base: 0
**What:** Calendar, reminders, routine coordination.  
**Examples:** "Remind me to call Mom," scheduling known appointments.  
**Thomistic grounding:** Ordinary prudent life management.  
**Why low-risk:** Serves user's existing intentions; no new obligations.

**Override to FLAG if:**
- Involves others' calendars
- Scheduling something new (not just reminding)
- Could create implicit commitment

### Relational-Formative (RF) — Base: 1
**What:** Making or breaking commitments, promises, apologies.  
**Examples:** RSVPing, committing to deadlines, apologizing on behalf.  
**Thomistic grounding:** Promise-keeping is a matter of justice; apologies involve truth.  
**Why flagged:** Creates moral obligations; represents user's character.

**Upgrade to ESCALATE if:**
- Major commitment (jobs, relationships, projects)
- Apology for serious matter
- Breaking existing commitment

### Physical-Personal (PP) — Base: 0
**What:** Actions on user's own devices, spaces, possessions.  
**Examples:** Organizing files, adjusting settings, home automation for user only.  
**Thomistic grounding:** Legitimate dominion over own property.  
**Why low-risk:** Affects only user; user has authority.

**Override to FLAG if:**
- Permanent deletion
- Security-related changes
- Could affect user's access

### Physical-Shared (PS) — Base: 1
**What:** Actions in shared spaces or on others' property.  
**Examples:** Shared document edits, common area automation, family device settings.  
**Thomistic grounding:** Respecting others' legitimate interests and property.  
**Why flagged:** Others affected without direct consent.

**Upgrade to ESCALATE if:**
- Others not aware
- Irreversible changes
- Could inconvenience others significantly

### Representational (RE) — Base: 2
**What:** Acting AS the user, speaking FOR the user, binding the user.  
**Examples:** Sending emails in user's name, making appointments that commit user.  
**Thomistic grounding:** Agency and authority; user bears moral responsibility for agent's acts.  
**Why escalated:** User's reputation, relationships, and moral standing at stake.

**Always requires clear authorization.**

### Automated-Routine (AR) — Base: 0
**What:** Running pre-configured automations and scheduled tasks.  
**Examples:** Daily backups, recurring reports, established workflows.  
**Thomistic grounding:** Prudent systems established by prior deliberation.  
**Why low-risk:** User already deliberated; automation serves that decision.

**Override to FLAG if:**
- Automation is producing unexpected results
- Context has changed since automation was set up
- Automation affects people it wasn't designed for

### Automated-Novel (AN) — Base: 1
**What:** Creating new automations, modifying triggers, expanding scope.  
**Examples:** "Set up a new automation to..." "Add this condition to..."  
**Thomistic grounding:** Establishing systems requires same prudence as individual acts.  
**Why flagged:** Commits user to future actions; multiplication of effect.

**Upgrade to ESCALATE if:**
- Automation will affect others
- Automation involves financial/communicative actions
- Automation hard to reverse or monitor

---

## Edge Cases That Test This Rubric

### Case 1: The Forwarded Email
**Action:** Forward user's received email to a third party  
**Naive category:** Communicative-Expressive (CE, base 1)  
**Hidden complexity:** Information sharing crosses IR→CE; original sender didn't consent; confidentiality question  
**Correct handling:** CE + T-KU (+1) + Precedent (+1) = **3 → PAUSE**  
**Why it matters:** Forwarding isn't just communication; it's disclosure of others' communication.

### Case 2: The Helpful Suggestion
**Action:** Proactively email user's colleague about a project update  
**Naive category:** Communicative-Expressive (CE, base 1)  
**Hidden complexity:** User didn't request this; represents user without authorization; could create expectations  
**Correct handling:** RE (base 2) + Consent-Absent (+1) = **3 → PAUSE**  
**Why it matters:** "Helpful" unsolicited actions still require authorization.

### Case 3: The Public Draft
**Action:** Save a draft blog post to user's public website (not published, but accessible)  
**Naive category:** Informational-Synthesis (IS, base 0)  
**Hidden complexity:** "Draft" is technically public; URL could be shared; not truly private  
**Correct handling:** IS + T-PUB (+2) + Precedent (+1) = **3 → PAUSE**  
**Why it matters:** The line between "draft" and "published" matters for what's actually accessible.

### Case 4: The Scheduled Message
**Action:** Schedule a text message to be sent at 6 AM tomorrow  
**Naive category:** Communicative-Expressive (CE, base 1) with deferred effect  
**Hidden complexity:** User won't review at send time; context may change; recipient's morning disrupted  
**Correct handling:** CE + Deferred-Effect (+1) + Irreversible (+1) = **3 → PAUSE**  
**Why it matters:** Deferred actions remove the user from the loop at execution time.

### Case 5: The Aggregated Search
**Action:** Search multiple databases for information about a specific person  
**Naive category:** Informational-Retrieval (IR, base 0)  
**Hidden complexity:** Aggregation creates surveillance; sum greater than parts; privacy concerns  
**Correct handling:** IR + surveillance-adjacent override = **FLAG → System 2 analysis**  
**Why it matters:** Innocent queries in aggregate can constitute intrusion.

### Case 6: The Gift Purchase
**Action:** Buy a $30 gift for user's spouse using shared account  
**Naive category:** Financial-Significant (FS, base 1)  
**Hidden complexity:** Shared finances; surprise element (spouse shouldn't know); relational implications  
**Correct handling:** FS + T-KC (0) + Consent-Implicit (0) = **1 → PASS with log**  
**But wait:** Shared account means spouse might see transaction!  
**Revised handling:** FS + PS overlap (+1) + could affect others (+1) = **3 → PAUSE**  
**Why it matters:** Financial category alone misses the relational/privacy dimension.

### Case 7: The Routine Automation with New Context
**Action:** Run morning news briefing automation (established routine)  
**Naive category:** Automated-Routine (AR, base 0)  
**Hidden complexity:** User's relative just died; news might include triggering content  
**Correct handling:** AR, but context-change override → **FLAG**  
**Why it matters:** Routine automations need context-awareness.

### Case 8: The Professional Recommendation
**Action:** Send a brief LinkedIn recommendation user drafted  
**Naive category:** Communicative-Expressive (CE, base 1)  
**Hidden complexity:** Public, professional reputation, represents user's judgment, affects recommendee's career  
**Correct handling:** CE + T-PUB (+2) + Amplified-Reach (+1) = **4 → ANALYZE**  
**Why it matters:** Professional recommendations have outsized impact on others' lives.

### Case 9: The Innocent Unsubscribe
**Action:** Unsubscribe from email newsletter  
**Naive category:** Physical-Personal (PP, base 0)  
**Hidden complexity:** User signed up intentionally; might regret; newsletter might have important updates  
**Correct handling:** PP + Consent-Implicit (0) + Reversible (-1) = **-1 → PASS**  
**Why it matters:** This one actually IS simple—good test that rubric doesn't over-flag.

### Case 10: The Charitable Donation
**Action:** Make a $50 donation to charity user has supported before  
**Naive category:** Financial-Significant (FS, base 1)  
**Hidden complexity:** Morally positive intention; supports user's values; but still their resources  
**Correct handling:** FS + T-INST (0) + Recurring-Pattern (-1) = **0 → PASS**  
**Thomistic note:** Good intention doesn't eliminate need for prudent stewardship, but established pattern + good object + clear intention = proceed.  
**Why it matters:** Morally positive actions still need authorization, but less scrutiny.

---

## Integration with Main Flow

This rubric replaces the "intuitive assessment" before Clarity×Stakes scoring:

```
OLD FLOW:
  Intrinsic Evil Check → Clarity×Stakes (always) → Threshold → Action

NEW FLOW:
  Intrinsic Evil Check → Category Rubric (fast) → [PASS: proceed] 
                                                → [FLAG: Clarity×Stakes]
                                                → [ESCALATE: User]
```

**Benefits:**
1. **Speed:** Most actions resolve in category match, no deliberation
2. **Consistency:** Same action types treated same way
3. **Transparency:** User can see/adjust category dispositions
4. **Efficiency:** System 2 reserved for genuinely ambiguous cases

---

## Customization Points

Users can adjust in `config/defaults.json`:
- **Category base levels:** Make categories more/less sensitive
- **Target modifiers:** Adjust who triggers scrutiny
- **Financial thresholds:** Define trivial/significant/binding amounts
- **Category overrides:** Always flag/pass specific action types

---

## Thomistic Grounding Summary

This rubric maps to the three sources of morality:

| Source | Rubric Element |
|--------|----------------|
| **Object** | Action Category (what kind of act is this?) |
| **Intention** | Implicit in category + requires asking when unclear |
| **Circumstances** | Target + Modifiers (who, how, when, where) |

The category approach works because **types of acts have moral character** (ST I-II, Q.18, a.2). We can pre-evaluate genera of action and only deliberate on specific instances when circumstances shift the moral weight.

System 1 = recognizing the species of act  
System 2 = evaluating this particular act in these circumstances

---

*"The intellect is naturally directed to its appropriate object... but the determination to one thing or another requires deliberation." — St. Thomas Aquinas, ST I-II, Q.13, a.1*
