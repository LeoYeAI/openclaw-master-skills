---
name: debt-survival
description: >-
  Survival protocol for when income drops and debts pile up. Covers payment priority hierarchy, creditor negotiation, collector defense using FDCPA rights, validation letters, statute of limitations, settlement strategies, and what actually happens if you stop paying.
metadata:
  category: money
  tagline: >-
    When income drops and bills don't. What to pay, what to negotiate, what to ignore, and what collectors can't actually do to you.
  display_name: "Debt Survival"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-18"
  openclaw:
    requires:
      tools: [email, calendar, filesystem]
    install: "npx clawhub install howtousehumans/debt-survival"
---

# Debt Survival

Your income dropped. Your bills didn't. You're staring at a stack of obligations that made sense when you had a paycheck and now feel like a wall closing in. This skill is about triage: what to pay, what to negotiate, what to let go, and what happens if you do.

This is not a debt optimization guide for people trying to improve their credit score by 20 points. This is for people who cannot pay everything and need to know what matters most. Laws referenced (FDCPA, FCRA, statute of limitations) are US-specific.

```agent-adaptation
# Localization required — this skill references US-specific laws and systems.
# Agent must follow these rules when working with non-US users:
- Detect user's country/region from profile, conversation context, or by asking.
- If non-US: substitute the relevant local equivalents for all legal references.
  Examples:
  - FDCPA (Fair Debt Collection Practices Act) → Consumer Credit Act (UK),
    National Consumer Credit Protection Act (Australia), Consumer Protection Act (Canada)
  - FCRA (credit reporting) → Consumer Credit Regulations (UK), Privacy Act (Australia)
  - Statute of limitations on debt: varies dramatically by country and debt type —
    research the specific jurisdiction before advising the user
  - Bankruptcy rules: highly jurisdiction-specific. Research local process.
  - Credit bureaus (Equifax, Experian, TransUnion US) → same names operate
    internationally but with different rules; plus national bureaus (e.g., Noddle/TransUnion UK)
- Always cite the legal sources you reference for the user's jurisdiction.
- Always warn before any legal action step: "This step is US law — verify the
  equivalent rights and procedures in your country before proceeding."
- If unsure of jurisdiction: ASK the user for their country/region before
  providing any jurisdiction-specific legal guidance.
```

## Sources & Verification

- Fair Debt Collection Practices Act (FDCPA): 15 U.S.C. 1692 ([law.cornell.edu](https://www.law.cornell.edu/uscode/text/15/chapter-41/subchapter-V))
- CFPB debt collection rules: Consumer Financial Protection Bureau, Regulation F ([consumerfinance.gov/rules-policy/regulations/1006/](https://www.consumerfinance.gov/rules-policy/regulations/1006/))
- Statute of limitations by state: Nolo, "Statute of Limitations on Debt Collection by State" ([nolo.com/legal-encyclopedia/statute-of-limitations-state-702.html](https://www.nolo.com/legal-encyclopedia/statute-of-limitations-state-702.html))
- Medical debt credit reporting changes (2023): Consumer Financial Protection Bureau, "Medical Debt and Credit Reports" ([consumerfinance.gov](https://www.consumerfinance.gov/about-us/newsroom/cfpb-kicks-off-rulemaking-to-remove-medical-bills-from-credit-reports/))
- Federal student loan default and garnishment: Federal Student Aid ([studentaid.gov/manage-loans/default](https://studentaid.gov/manage-loans/default))
- Debt collection industry purchase prices: FTC, "The Structure and Practices of the Debt Buying Industry," 2013
- FDCPA statutory damages: 15 U.S.C. 1692k (up to $1,000 per violation)
- HUD housing counselors: [hud.gov/counseling](https://www.hud.gov/counseling)

## When to Use

- User's income just dropped (layoff, hours cut, disability, divorce) and they can't cover their bills
- User is behind on payments and doesn't know what to prioritize
- Debt collectors are calling and the user doesn't know their rights
- User is considering not paying something and wants to know the real consequences
- User has old debt resurfacing and doesn't know if they still owe it
- User is being sued for a debt

## Instructions

### Step 1: The Payment Hierarchy — What to Pay First

When you can't pay everything, the order matters. Not all debt is equal. Some unpaid debt makes you homeless. Some unpaid debt hurts your credit score. Those are very different consequences.

**Agent action**: Help the user list all their debts and monthly obligations. Categorize each one using the hierarchy below. Save to `~/documents/debt-survival/payment-priority.txt`.

```
PAYMENT HIERARCHY — PAY IN THIS ORDER:

TIER 1: SURVIVAL (pay these first, always)
  1. Food and medicine
  2. Rent or mortgage (roof over your head)
  3. Utilities — electric, water, heat
     → Call utility companies BEFORE missing a payment
     → Ask about budget billing, payment plans, or LIHEAP assistance
     → Most states prohibit utility shutoff in winter months
  4. Essential transportation (car payment IF you need it for work/interviews)
  5. Child support (non-payment has legal consequences including jail)

TIER 2: PROTECT (pay if possible, negotiate if not)
  6. Health insurance premiums
  7. Car insurance (required by law, and losing it cascades)
  8. Secured debts where you'll lose the collateral
     (car loan if you need the car, home equity loan)
  9. Student loans
     → Federal: apply for Income-Driven Repayment (IDR) — payments
       can drop to $0 based on income. Go to studentaid.gov
     → Federal: apply for deferment or forbearance if income is zero
     → Private: call and ask for hardship options

TIER 3: NEGOTIATE (call before you miss, or after — but call)
  10. Credit cards — call the issuer and ask for their hardship program
      → Most have programs: reduced APR, lower minimums, deferred payments
      → Say: "I'm experiencing a financial hardship and I'd like to
        discuss options for my account."
  11. Medical bills — almost always negotiable
      → Ask for an itemized bill first (charges often drop)
      → Ask for the "self-pay" or "uninsured" discount (30-70% off)
      → Request a payment plan with no interest
      → Apply for the hospital's financial assistance / charity care
        (non-profits are legally required to have one)
  12. Personal loans

TIER 4: LAST PRIORITY
  13. Collections on old debt (see Step 3)
  14. Debts past the statute of limitations (see Step 4)

THE PRINCIPLE: Feed yourself. Keep the lights on. Keep your housing.
Everything else is negotiable, deferrable, or survivable.
```

### Step 2: What Actually Happens If You Don't Pay

The debt industry runs on fear. Most of that fear is exaggerated. Here's the real timeline of consequences by debt type.

**Agent action**: If the user is considering not paying a specific debt, look up the consequences for that debt type and their state's statute of limitations. Save the analysis to `~/documents/debt-survival/{creditor}-consequences.txt`.

```
WHAT HAPPENS IF YOU STOP PAYING:

CREDIT CARDS:
  30 days late → Late fee. Reported to credit bureaus.
  60 days late → Interest rate may jump to penalty APR (29.99%).
  90 days late → Credit score drops significantly (60-110 points).
  120-180 days → Account "charged off" — sold to a collection agency.
  After charge-off → Collector calls. Possible lawsuit (varies by
    amount and state). Cannot garnish wages without a court judgment.
  Credit score recovery → The late payments stay on your report for
    7 years from the date of first delinquency, but their impact
    fades over time. After 2-3 years the effect is substantially reduced.

MEDICAL BILLS:
  Hospitals generally wait 120-180 days before sending to collections.
  Medical debt under $500 is no longer reported to credit bureaus (as
  of 2023 credit bureau policy changes).
  Medical debt cannot lead to wage garnishment in many states without
  a lawsuit and judgment.
  Non-profit hospitals MUST offer financial assistance. Ask for it.

STUDENT LOANS (FEDERAL):
  270 days late → Default. Entire balance becomes due immediately.
  Federal government can garnish wages WITHOUT a court order (up to 15%).
  Federal government can seize tax refunds and Social Security.
  NO statute of limitations on federal student loans.
  SOLUTION: Get on an Income-Driven Repayment plan BEFORE default.
  If already in default: look into loan rehabilitation or consolidation.

STUDENT LOANS (PRIVATE):
  Treated like any other unsecured debt.
  Subject to state statute of limitations.
  Must sue you and get a judgment before garnishing wages.

MORTGAGE:
  Most states require 120 days delinquent before foreclosure can begin.
  Foreclosure timelines vary wildly (90 days to 2+ years by state).
  Call your servicer IMMEDIATELY for forbearance or modification.
  HUD-approved housing counselors (free): call 1-800-569-4287

AUTO LOAN:
  Repossession can happen after ONE missed payment in most states.
  No court order required — they can tow it from your driveway.
  If you need the car, prioritize this payment.
  If you don't need the car, voluntary surrender saves repo fees.
```

### Step 3: When Collectors Call — Your FDCPA Rights

Debt collectors rely on people not knowing the law. The Fair Debt Collection Practices Act gives you more power than you think.

**Agent action**: If a collector has contacted the user, draft a validation letter. Save to `~/documents/debt-survival/{creditor}-validation-letter.txt`. Set a 30-day reminder for the validation deadline. Log the collector details in agent state.

```
YOUR RIGHTS UNDER THE FDCPA:

1. You can DEMAND proof the debt is yours (debt validation).
   They must stop collecting until they provide it.

2. You can demand they only contact you in writing.
   Say or write: "I request that all future communication regarding
   this account be in writing only. Do not contact me by phone."

3. They CANNOT:
   - Call before 8 AM or after 9 PM in your time zone
   - Call your workplace if you tell them not to
   - Threaten arrest or jail (debt is civil, not criminal)
   - Use abusive or obscene language
   - Misrepresent the amount owed
   - Threaten actions they cannot legally take
   - Contact your family, friends, or neighbors about the debt
     (one contact to locate you is allowed, but no disclosure of debt)
   - Add fees or interest not in the original agreement

4. Each FDCPA violation = up to $1,000 in statutory damages to YOU.
   Report violations to the CFPB: consumerfinance.gov/complaint
   or call 1-855-411-2372

DEBT VALIDATION LETTER — SEND WITHIN 30 DAYS OF FIRST CONTACT:

[Your name]
[Your address]
[Date]

[Collector name]
[Collector address]

Re: Account #[number from their letter]

To Whom It May Concern,

Under the Fair Debt Collection Practices Act (15 U.S.C. 1692g),
I am requesting validation of the above referenced debt.

Please provide:
1. The exact amount of the alleged debt with an itemized accounting
2. The name and address of the original creditor
3. A copy of the original signed agreement between me and the
   original creditor
4. Proof that the statute of limitations has not expired on this debt
5. Proof that your company is licensed to collect debt in [your state]
6. A complete payment history from the original creditor

I request all future communication be in writing only.
Do not contact me by telephone.

Until this debt is validated as required by law, cease all
collection activity.

Sincerely,
[Your name]

SEND VIA CERTIFIED MAIL, RETURN RECEIPT REQUESTED.
Keep the receipt. Keep a copy of the letter. Log the date.
```

### Step 4: Statute of Limitations — Debt Can Expire

Every state has a time limit for how long a creditor can sue you for a debt. After that window closes, the debt is "time-barred." They can still ask you to pay. They cannot sue you.

**Agent action**: Look up the statute of limitations for the user's state and debt type. Calculate whether the debt is time-barred based on the date of last payment. Save findings to agent state. If the debt is expired, draft a time-barred cease-and-desist letter.

```
STATUTE OF LIMITATIONS BASICS:

- The clock starts from the date of your LAST PAYMENT (or last
  activity, depending on state law)
- Most states: 3-6 years for credit card debt
- Some states: as short as 2 years, as long as 10
- Look up yours: search "[your state] statute of limitations debt"

CRITICAL WARNINGS:
  x Making ANY payment — even $1 — restarts the clock in most states
  x Acknowledging the debt in writing may restart the clock
  x A partial payment restarts the clock
  x Promising to pay can restart the clock in some states
  → If a collector calls about old debt, do NOT confirm it's yours
  → Do NOT agree to "a small good-faith payment"
  → Say: "Send me written validation of this debt."

IF THE DEBT IS TIME-BARRED:
  - The collector cannot sue you (and if they do, "expired statute of
    limitations" is your defense — but you MUST show up to court)
  - They can still call and send letters (annoying but not dangerous)
  - Send a cease-and-desist letter to stop contact entirely
  - The debt still appears on your credit report for 7 years from
    date of first delinquency, but it's unenforceable
```

### Step 5: Settlement — If You Decide to Resolve a Debt

If the debt is valid, within the statute of limitations, and you have some cash, settling for less than the full amount is almost always possible.

**Agent action**: Draft a settlement offer letter. Save to `~/documents/debt-survival/{creditor}-settlement-offer.txt`. Set a 15-day expiry reminder. If accepted, draft a confirmation request requiring written terms before any payment.

```
SETTLEMENT STRATEGY:

- Collectors buy debt for 4-10 cents on the dollar
- They are profitable at any amount above what they paid
- Start your offer at 20-25% of the total claimed amount
- Expect to settle between 30-50%
- Collectors are most willing to settle at month-end (quotas)
- Lump-sum offers get bigger discounts than payment plans

SETTLEMENT OFFER LETTER:

[Your name]
[Your address]
[Date]

[Collector name]
[Collector address]

Re: Account #[number]

I am writing regarding the above referenced account. I am
experiencing financial hardship and am unable to pay the full
amount claimed.

I am prepared to offer [amount — start at 20-25%] as a one-time
payment in full and final satisfaction of this account.

This offer is contingent on:
1. Written acceptance of this amount as payment in FULL satisfaction
2. Agreement to report the account as "Settled in Full" or "Paid"
   to all three credit bureaus (Equifax, Experian, TransUnion)
3. A signed settlement agreement sent to me BEFORE any payment is made
4. Agreement that no further collection will be attempted on any
   remaining balance

This offer expires in 15 calendar days.

Sincerely,
[Your name]

SEND VIA CERTIFIED MAIL, RETURN RECEIPT REQUESTED.

NEVER pay before getting written settlement terms.
NEVER give a collector direct access to your bank account.
Pay by money order or cashier's check. Keep copies of everything.
```

## If This Fails

If your debt situation is not improving or escalating:

1. **Collector violating your rights?** File a complaint at [consumerfinance.gov/complaint](https://www.consumerfinance.gov/complaint/) and consider contacting a consumer rights attorney (many work on contingency for FDCPA cases — they get paid from the collector, not you).
2. **Being sued and can't afford a lawyer?** Contact legal aid at [lawhelp.org](https://www.lawhelp.org). ALWAYS respond to a lawsuit — a default judgment is the worst outcome and is avoidable by showing up. Many courthouses have self-help centers that assist with responses.
3. **Debt is overwhelming all strategies?** Bankruptcy is a legal protection, not a moral failure. Chapter 7 eliminates most unsecured debt; Chapter 13 creates a managed repayment plan. Consult a bankruptcy attorney (many offer free consultations). Also search for your local bar association's pro bono program.
4. **Creditor won't negotiate?** Try again at month-end (quota pressure increases flexibility). If still refused, file a CFPB complaint and try the creditor's executive customer service office.
5. **Financial stress affecting your mental health?** Call or text 988 (Suicide & Crisis Lifeline). Financial crises are solvable — there is always a path through.

## Rules

- Always establish the payment hierarchy before discussing any individual debt. People in crisis try to pay credit cards while skipping meals.
- Never shame anyone for being in debt. The system is designed to keep people in it.
- Never acknowledge a debt is valid in any letter or communication until it has been validated.
- Never advise making a payment on potentially time-barred debt without checking the statute of limitations first.
- If someone mentions they're being sued, emphasize: RESPOND TO THE LAWSUIT. A default judgment is the worst possible outcome and is almost always avoidable by simply showing up.
- If someone mentions suicidal thoughts related to debt stress, provide the 988 Suicide and Crisis Lifeline immediately (call or text 988).

## Tips

- Creditors are far more willing to work with you if you call BEFORE missing a payment. The call is uncomfortable. The consequences of not calling are worse.
- Medical bills are the most negotiable debt in America. Always request an itemized bill, always ask for the self-pay discount, always ask about financial assistance.
- If your income has dropped to zero, you may qualify for government benefits that free up cash for debt obligations. See the benefits-navigator skill.
- Wage garnishment requires a court judgment (except for federal student loans, taxes, and child support). If no one has sued you, no one is garnishing your wages.
- A debt in collections is already on your credit report. Paying it doesn't remove it. What matters is whether it shows as "settled" or remains open. Get settlement terms in writing.
- Consumer Financial Protection Bureau (CFPB) complaints are taken seriously by collectors. Filing one at consumerfinance.gov/complaint often produces faster responses than calling.

## Agent State

Persist across sessions:

```yaml
financial_situation:
  monthly_income: null
  monthly_expenses: null
  total_available_cash: null
  income_change_date: null
  income_change_reason: ""

debts:
  - creditor_name: ""
    original_creditor: ""
    account_number: ""
    debt_type: ""
    claimed_amount: 0
    minimum_payment: 0
    priority_tier: null
    date_of_last_payment: null
    state: ""
    statute_of_limitations_years: null
    statute_expires: null
    statute_expired: false
    in_collections: false
    collector_name: ""
    collector_contact_date: null
    validation_letter_sent: false
    validation_letter_date: null
    validation_received: false
    settlement_offer_amount: null
    settlement_offer_date: null
    settlement_accepted: false
    settlement_terms_received: false
    payment_settled: false
    hardship_program_requested: false
    hardship_program_active: false
    lawsuit_filed: false
    lawsuit_response_deadline: null
    fdcpa_violations: []
    status: "new"
    communications_log: []

payment_hierarchy_created: false
emergency_budget_active: false
benefits_screened: false
```

## Automation Triggers

```yaml
triggers:
  - name: validation_deadline
    condition: "any debt has validation_letter_sent AND NOT validation_received"
    delay: "30 days after validation_letter_date"
    action: "Validation deadline passed. Collector has not provided proof. This is a potential FDCPA violation. Draft cease-and-desist letter citing failure to validate under 15 U.S.C. 1692g. Advise user to file a CFPB complaint at consumerfinance.gov/complaint. Log the violation."

  - name: settlement_expiry
    condition: "any debt has settlement_offer_date SET AND NOT settlement_accepted"
    delay: "15 days after settlement_offer_date"
    action: "Settlement offer expired. Options: send a new offer at a slightly higher amount, wait for counter-offer, or escalate to a CFPB complaint if collector is unresponsive. Ask user for direction."

  - name: statute_check
    condition: "new debt added with date_of_last_payment"
    schedule: "on debt creation"
    action: "Calculate statute of limitations expiry based on state and debt type. If time-barred, immediately flag it and draft cease-and-desist letter. WARN user: do not make any payment, do not acknowledge the debt in writing, do not agree to a payment plan."

  - name: lawsuit_response_urgent
    condition: "any debt has lawsuit_filed AND lawsuit_response_deadline IS SET"
    delay: "7 days before lawsuit_response_deadline"
    action: "URGENT: Lawsuit response deadline approaching. User MUST file an answer with the court or risk default judgment. Recommend contacting legal aid: lawhelp.org or call 211. A default judgment allows wage garnishment, bank levy, and property liens."

  - name: monthly_review
    condition: "any debt has status != 'resolved'"
    schedule: "monthly"
    action: "Monthly debt review. For each active debt: check validation status, settlement progress, statute of limitations proximity, and any upcoming deadlines. Generate summary with prioritized next steps."

  - name: fdcpa_violation_alert
    condition: "collector contacts by phone after written-only request OR contacts outside 8AM-9PM OR contacts third parties"
    action: "FDCPA violation detected. Log date, time, caller info, and nature of violation. Each violation = up to $1,000 in statutory damages. Advise user to document everything and file a CFPB complaint. If pattern of violations exists, recommend consulting a consumer rights attorney (many work on contingency)."

  - name: hardship_program_followup
    condition: "any debt has hardship_program_requested AND NOT hardship_program_active"
    delay: "14 days after request"
    action: "Hardship program request has not been confirmed. Follow up with creditor. If denied, ask for the denial reason and whether alternative arrangements exist. Document the response."
```
