---
name: layoff-72-hours
description: >-
  Urgent, time-boxed protocol for the first 72 hours after losing a job. Covers immediate document preservation, unemployment filing, health insurance decisions, emergency budgeting, severance review, and family communication. This is about stabilizing, not job searching.
metadata:
  category: crisis
  tagline: >-
    You just lost your job. Here's what to do right now, in the right order, before the panic sets in.
  display_name: "The First 72 Hours"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-18"
  openclaw:
    requires:
      tools: [email, calendar, filesystem]
    install: "npx clawhub install layoff-72-hours"
---

# The First 72 Hours

You just lost your job. Your brain is doing that thing where it cycles between "I'm fine" and "everything is ruined" every 45 seconds. That's normal. It's also why you need a protocol, not a pep talk.

This skill is a strict triage sequence. It covers the first 4 hours, first 24 hours, and first 72 hours. It does NOT cover finding your next job — that comes later. Right now you need to stop the bleeding: lock down your documents, file for unemployment, figure out health insurance, and do the math on how long your money lasts.

Phone numbers, agencies, and legal references are US-specific. Adapt for your country.

```agent-adaptation
# Localization required — this skill references US-specific programs and laws.
# Agent must follow these rules when working with non-US users:
- Detect user's country/region from profile, conversation context, or by asking.
- If non-US: substitute local equivalents for all jurisdiction-specific steps.
  Examples:
  - Unemployment filing → JobSeeker's Allowance/Universal Credit (UK),
    Employment Insurance (Canada), JobSeeker Payment (Australia),
    Arbeitslosengeld I (Germany)
  - COBRA health insurance continuation → NHS enrollment (UK — automatic),
    OHIP/provincial health (Canada), Medicare/private insurance (Australia)
  - ACA Special Enrollment → equivalent health insurance marketplace enrollment
    in the user's country
  - OWBPA severance review period (21/45 days) → local employment law on
    severance notice periods (highly jurisdiction-specific — research carefully)
  - W-2/final paycheck timeline → local final pay legislation
  - State unemployment agency → national/local equivalent
- Always warn: "This step references US law/programs — I have substituted
  [local equivalent], but verify this applies to your specific situation."
- If severance agreement involved: always recommend local employment lawyer review.
- If unsure of jurisdiction: ASK before providing specific legal guidance.
```

## Sources & Verification

- OWBPA (Older Workers Benefit Protection Act) 21/45-day review period: 29 U.S.C. 626(f) ([law.cornell.edu](https://www.law.cornell.edu/uscode/text/29/626))
- COBRA 60-day retroactive election: 29 U.S.C. 1166(a) ([law.cornell.edu](https://www.law.cornell.edu/uscode/text/29/1166))
- ACA Special Enrollment Period after job loss: [healthcare.gov/glossary/special-enrollment-period](https://www.healthcare.gov/glossary/special-enrollment-period/)
- State unemployment filing portals: [careeronestop.org/LocalHelp/UnemploymentBenefits](https://www.careeronestop.org/LocalHelp/UnemploymentBenefits/unemployment-benefits.aspx) (US DOL-sponsored)
- Average job search duration (3-6 months): Bureau of Labor Statistics, "Duration of Unemployment" series ([bls.gov](https://www.bls.gov/cps/lfcharacteristics.htm))
- Severance negotiation practices: SHRM, "Severance Agreements: Guidelines for Employers," 2024

## When to Use

- User just got laid off, fired, or "separated" — today or within the past few days
- User is sitting in their car in the parking lot after being walked out
- User is staring at a severance agreement and doesn't know what to do
- User is panicking about money and insurance
- User is about to lose their job (PIP, restructuring rumors, contract ending)

## Instructions

### SAFETY CHECK — Read This First

**STOP.** Before proceeding, the agent MUST ask:

> "Are you okay right now? Job loss can bring up very dark thoughts. If you're having thoughts of hurting yourself, we need to address that first."

- If YES (having dark thoughts): **Do not continue with this skill.** Provide crisis resources immediately:
  - **988 Suicide & Crisis Lifeline**: Call or text 988 (24/7)
  - **Crisis Text Line**: Text HOME to 741741
- If NO: Proceed to Step 1.

**Agent action**: Ask this question explicitly. Job loss is a leading trigger for suicidal ideation. Do not skip it.

### Step 1: The First 4 Hours — Before You Lose Access

This is the golden window. Once IT disables your accounts, some of this becomes impossible.

**Agent action**: Create a triage checklist at `~/documents/layoff-72-hours/triage-checklist.txt`. Ask the user if they still have access to work systems. If yes, prioritize the access-dependent items. Set a 4-hour reminder to check progress on critical items.

```
FIRST 4 HOURS — DO THESE NOW:

1. DO NOT SIGN ANYTHING
   You almost certainly have 21 days to review a severance agreement
   (45 days if you're over 40, under the OWBPA). Say this exact phrase:
   "I appreciate this. I'd like to review it with an advisor before signing."

2. PRESERVE YOUR DOCUMENTS (while you still have access)
   Forward to your personal email or save to personal cloud:
   □ Performance reviews, positive feedback, awards
   □ Your contact list — every colleague, client, vendor
   □ Any documentation of your accomplishments with numbers
   □ Your benefits enrollment summary (health, dental, vision, 401k)
   □ Your most recent pay stubs (you'll need these for unemployment)
   □ Your offer letter and any amendments
   □ Your employee handbook (especially severance and non-compete sections)
   DO NOT take proprietary company information, trade secrets, or
   client data. That can get you sued. Take YOUR records about YOU.

3. SCREENSHOT YOUR BENEFITS
   □ Health insurance: carrier name, plan name, group number, your ID
   □ Last day of coverage (ask HR explicitly — "What is my last day
     of health insurance coverage?")
   □ 401k balance and provider (Fidelity, Vanguard, etc.)
   □ HSA/FSA balance (FSA funds expire — spend them)
   □ Life insurance and disability details
   □ Any unvested stock or RSU schedule

4. TELL ONE PERSON
   Not LinkedIn. Not a group chat. One person you trust. Say: "I lost
   my job today. I don't need advice yet, I just need someone to know."
```

### Step 2: The First 24 Hours — File, Don't Sign, Do the Math

**Agent action**: Help the user locate their state unemployment website. Calculate their financial runway using the formula below. Save the emergency budget to `~/documents/layoff-72-hours/emergency-budget.txt`. Set a calendar reminder for 24 hours: "Review severance agreement status."

```
FIRST 24 HOURS:

1. FILE FOR UNEMPLOYMENT — TODAY
   → Go to your state's Department of Labor website
   → Google: "[your state] file for unemployment"
   → You can file even if you received severance (rules vary by state)
   → You can file even if you were fired (unless for gross misconduct)
   → Benefits start from your FILING DATE, not approval date
   → Waiting costs you money. Every day you delay is a day of benefits lost.
   → If the website is down, call. If the phone is jammed, try at
     8:00 AM sharp when lines open.

2. DO THE RUNWAY MATH
   This is the single most important number right now:

   Checking + Savings + Severance (after tax) = Total Cash
   Total Cash / Monthly Expenses = Months of Runway

   If runway < 2 months: activate emergency mode (Step 3 becomes urgent)
   If runway 2-4 months: you have breathing room but cut spending now
   If runway > 4 months: you're okay. Proceed deliberately.

3. DO NOT SIGN THE SEVERANCE AGREEMENT YET
   Read it carefully. Look for:
   □ Non-compete clauses (how long, how broad, what geography?)
   □ Non-disparagement clauses (are they mutual?)
   □ General release of claims (what are you giving up?)
   □ Reference language (what will they say when called?)
   □ COBRA subsidy or extended benefits?
   Consider having an employment attorney review it.
   Many offer a free 30-minute consultation. The agreement itself
   is negotiable — companies expect pushback.

   NEGOTIATION POINTS:
   - More weeks of severance (standard: 1-2 weeks per year of service)
   - Extended health insurance or COBRA subsidy
   - Outplacement services
   - Positive reference agreement (get it in writing)
   - Accelerated stock vesting
   - Non-compete modification or removal
   - Payment of unused PTO

4. RESIST THE URGE TO JOB SEARCH
   Your brain wants to "do something productive." Job searching on
   Day 1 is reactive, unfocused, and leads to applying to anything
   that moves. You'll make better decisions in 72 hours.
```

### Step 3: The First 72 Hours — Insurance, Budget, Stabilize

**Agent action**: Help the user compare COBRA vs. marketplace health insurance costs. Create a comparison document at `~/documents/layoff-72-hours/insurance-comparison.txt`. Set calendar reminders for the 60-day COBRA election window and the 60-day Special Enrollment Period on healthcare.gov.

```
HEALTH INSURANCE DECISION — MAKE THIS IN 72 HOURS, NOT 72 DAYS:

Option A: COBRA
  - Continues your exact same plan
  - You pay the FULL premium (employer share + your share + 2% admin fee)
  - Typical cost: $600-$2,000/month for individual, more for family
  - You have 60 days to elect retroactively
  - STRATEGY: Wait to elect. If you have a medical expense in the
    gap, elect COBRA retroactively to cover it. If not, you saved
    the premiums. This is legal.

Option B: ACA Marketplace (healthcare.gov)
  - Job loss is a "qualifying life event" — you get a 60-day
    Special Enrollment Period regardless of open enrollment
  - Subsidies are based on CURRENT income (which just dropped to $0)
  - You may qualify for very low or $0 premium plans
  - Go to healthcare.gov or call 1-800-318-2596
  - Have your most recent tax return and pay stubs ready

Option C: Spouse's employer plan
  - Your job loss triggers a Special Enrollment Period on their plan too
  - Usually 30 days to enroll — check with their HR immediately

Option D: Medicaid
  - If your income has dropped to near zero, you may now qualify
  - Apply at healthcare.gov or your state Medicaid office
  - No premiums, no deductibles in most states
  - Processing: 1-2 weeks in most states
```

```
EMERGENCY BUDGET — CUT TO SURVIVAL MODE:

Keep paying (in this order):
  1. Food and medicine
  2. Housing (rent/mortgage)
  3. Utilities (electric, water, heat)
  4. Transportation (if needed for job search)
  5. Health insurance
  6. Minimum debt payments ONLY (see debt-survival skill)

Stop paying or reduce immediately:
  □ Subscriptions (streaming, gym, software, meal kits)
  □ Dining out, delivery, coffee shops
  □ Non-essential shopping
  □ Extra debt payments (pay minimums only)

Contact proactively:
  □ Landlord — ask about hardship deferral BEFORE you miss a payment
  □ Mortgage company — ask about forbearance options
  □ Utility companies — ask about payment plans or LIHEAP
  □ Student loans — apply for income-driven repayment or deferment
  □ Car payment — some lenders offer hardship extensions
  □ Credit card companies — ask for hardship programs (lower APR,
    reduced minimums, deferred payments)

IMPORTANT: Making these calls BEFORE you miss a payment gives you
far more options than calling after. Creditors help people who
communicate. They punish people who go silent.
```

### Step 4: What NOT to Do

```
THE DON'T LIST:

x Don't cash out your 401k (10% penalty + income tax = losing 30-40%)
x Don't take on new debt to "maintain lifestyle"
x Don't start a business out of panic
x Don't accept the first job offer out of desperation (if you have runway)
x Don't post about it on social media while emotional
x Don't isolate — job loss thrives in silence and shame
x Don't skip filing for unemployment because you "don't need it" or
  feel embarrassed. You paid into this system. It's yours.
x Don't make any major financial decisions for 72 hours
```

## If This Fails

If you cannot complete the triage steps or things spiral:

1. **Unemployment website down?** Call your state DOL directly at 8:00 AM when lines open. Or visit a local American Job Center in person: [careeronestop.org/LocalHelp](https://www.careeronestop.org/LocalHelp/local-help.aspx)
2. **Can't afford COBRA or marketplace?** Apply for Medicaid immediately if your income has dropped to near zero. See the benefits-navigator skill.
3. **Severance pressure?** If your employer is pressuring you to sign immediately, say: "I'm exercising my legal right to review this. I'll respond by [date within your window]." If they threaten to withdraw: consult an employment attorney (many offer free consultations).
4. **Financial runway under 1 month?** Call 211 immediately for emergency assistance. Apply for SNAP today (expedited processing can provide food funds within 7 days). See the emergency-financial-triage skill.
5. **Feeling hopeless or having dark thoughts?** Call or text 988. Job loss is temporary. Your life is not.

## Rules

- Lead with the triage sequence. Do not skip to job searching.
- Unemployment filing must happen Day 1. Repeat this if needed.
- Never imply the layoff is the user's fault.
- If the user mentions suicidal thoughts or hopelessness, provide the 988 Suicide and Crisis Lifeline immediately (call or text 988).
- If the user is being pressured to sign a severance agreement immediately, reinforce that they have the legal right to take time.
- Always confirm whether the user still has access to work systems before advising document preservation.

## Tips

- The average job search takes 3-6 months. Plan your budget for 6. If it takes 3, celebrate.
- Severance agreements are almost always negotiable. The first offer is rarely the best one.
- COBRA's 60-day retroactive election is one of the most valuable and least-known insurance strategies.
- Filing for unemployment does not go on a permanent record. Future employers cannot see it.
- If you were laid off (not fired for cause), you are almost certainly eligible for unemployment. File first, let the state sort it out.
- Contact your state's Department of Labor if your employer contests your unemployment claim — many initial denials are reversed on appeal.

## Agent State

Persist across sessions:

```yaml
layoff:
  layoff_date: null
  employer_name: ""
  severance_offered: false
  severance_agreement_deadline: null
  severance_signed: false
  last_day_of_benefits: null
  unemployment_filed: false
  unemployment_filed_date: null
  unemployment_state: ""
  cobra_election_deadline: null
  cobra_elected: false
  marketplace_enrolled: false
  health_insurance_decision: null
  financial_runway_months: null
  monthly_expenses: null
  total_available_cash: null
  documents_preserved: false
  emergency_budget_created: false
  phase: "first_4_hours"
  contacts_preserved: false
  four_oh_one_k_provider: ""
  four_oh_one_k_balance: null
  hsa_balance: null
  fsa_balance: null
  fsa_deadline: null
  checklist:
    signed_nothing: false
    filed_unemployment: false
    preserved_documents: false
    screenshotted_benefits: false
    told_someone: false
    calculated_runway: false
    insurance_decision_made: false
    emergency_budget_active: false
```

## Automation Triggers

```yaml
triggers:
  - name: severance_deadline_warning
    condition: "severance_offered AND NOT severance_signed"
    delay: "3 days before severance_agreement_deadline"
    action: "Severance agreement deadline approaching. Remind user of their remaining time. If they haven't consulted an attorney, recommend a free employment law consultation. List negotiation points they haven't addressed."

  - name: unemployment_filing_nudge
    condition: "NOT unemployment_filed"
    delay: "24 hours after layoff_date"
    action: "Unemployment has not been filed. Every day of delay is lost benefits. Provide direct link to the user's state unemployment portal. Offer to help gather required information (employer name, dates, last pay stub)."

  - name: cobra_election_deadline
    condition: "NOT cobra_elected AND NOT marketplace_enrolled"
    delay: "45 days after last_day_of_benefits"
    action: "COBRA election window closing in 15 days. User has not made a health insurance decision. Compare COBRA cost vs. marketplace options at current income level. Flag urgency."

  - name: insurance_gap_check
    condition: "last_day_of_benefits IS SET AND NOT cobra_elected AND NOT marketplace_enrolled"
    delay: "7 days after last_day_of_benefits"
    action: "User currently has no health insurance. Present options: retroactive COBRA election (still available for 60 days), marketplace Special Enrollment Period, Medicaid if income qualifies. Emphasize that the COBRA backdating strategy only works within the 60-day window."

  - name: phase_advancement
    condition: "phase = 'first_4_hours' AND documents_preserved"
    action: "First 4 hours checklist substantially complete. Advance phase to 'first_24_hours'. Present next set of actions: file unemployment, calculate runway, review severance."

  - name: fsa_expiration_warning
    condition: "fsa_balance > 0 AND fsa_deadline IS SET"
    delay: "14 days before fsa_deadline"
    action: "FSA funds expire soon. Remaining balance will be lost. Advise user to schedule medical appointments, buy glasses, fill prescriptions, or purchase eligible items to use remaining funds."

  - name: weekly_stabilization_check
    condition: "phase != 'stabilized'"
    schedule: "weekly"
    action: "Review checklist completion. Identify any critical items still unfinished (unemployment, insurance, budget). Generate status summary and next actions."
```
