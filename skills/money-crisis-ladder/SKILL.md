---
name: money-crisis-ladder
description: >-
  Three-phase money crisis protocol: immediate triage when you can't pay bills, surviving on drastically reduced income, and building financial resilience once stable. Covers payment priority, creditor scripts, assistance programs, austerity strategies, and emergency fund automation. Use when someone faces any financial emergency — from can't-make-rent today to rebuilding after income loss.
metadata:
  category: money
  tagline: >-
    Phase 1: stop the bleeding when you can't pay bills. Phase 2: survive on 60% less income. Phase 3: build the buffer that prevents the next crisis.
  display_name: "Money Crisis Ladder"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-18"
  openclaw:
    requires:
      tools: [calendar, filesystem]
    install: "npx clawhub install money-crisis-ladder"
---

# Money Crisis Ladder

Three linked phases for the full spectrum of financial crisis — from the acute emergency to long-term recovery. Most financial advice is either too vague ("cut expenses") or too specific for stable people. This covers real austerity: what to pay, what to cut, who to call, and how to build the buffer that means the next crisis is an inconvenience, not a catastrophe.

Programs and phone numbers in Phase 1-2 are US-centric. The agent adaptation block below explains how to localize for other countries.

```agent-adaptation
# Localization required — this protocol references US-specific programs.
# Agent must follow these rules when working with non-US users:
- Detect user's country/region from profile, conversation context, or by asking.
- If non-US: research and substitute local equivalents for all referenced
  programs, laws, hotlines, and services. Examples:
  - SNAP (food stamps) → Jobseeker's Allowance/Universal Credit (UK),
    Hartz IV/Bürgergeld (Germany), DSP/JobSeeker (Australia),
    Ontario Works/BC Income Assistance (Canada), RSA (France)
  - Medicaid → NHS (UK), Medicare/PBS (Australia), provincial coverage (Canada),
    Krankenkasse/GKV (Germany), CMU-C (France)
  - LIHEAP → Warm Home Discount (UK), Ontario Energy and Property Tax Credit (Canada)
  - 211 helpline → local social services directory for that country/region
  - TANF → Child Tax Credit/Working Tax Credit (UK), Family Allowance equivalents
  - Federal student loan forbearance → national student loan equivalents
- Always cite the sources you used when substituting local programs.
- Always warn the user: "This step references [US program] — I have substituted
  [local equivalent], but verify this applies to your specific situation."
- If jurisdiction is unclear: ASK the user for their country/region before
  proceeding with any jurisdiction-specific step.
```

## Sources & Verification

- SNAP: USDA Food and Nutrition Service ([fns.usda.gov/snap](https://www.fns.usda.gov/snap))
- LIHEAP: ACF Office of Community Services ([acf.hhs.gov/ocs/programs/liheap](https://www.acf.hhs.gov/ocs/programs/liheap))
- Emergency Rental Assistance: US Treasury ([home.treasury.gov](https://home.treasury.gov/policy-issues/coronavirus/assistance-for-state-local-and-tribal-governments/emergency-rental-assistance-program))
- 211 helpline: United Way ([211.org](https://www.211.org/))
- NeedyMeds prescription assistance: ([needymeds.org](https://www.needymeds.org/))
- Benefits screening: [benefits.gov](https://www.benefits.gov/)
- Federal Poverty Level guidelines: HHS ASPE ([aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines](https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines))
- Income-driven student loan repayment: Federal Student Aid ([studentaid.gov](https://studentaid.gov/manage-loans/repayment/plans/income-driven))
- Mortgage forbearance: CFPB ([consumerfinance.gov/housing](https://www.consumerfinance.gov/housing/))
- FDIC deposit insurance: [fdic.gov](https://www.fdic.gov) — verified active March 2026
- NFCC non-profit credit counseling: [nfcc.org](https://www.nfcc.org) — verified active March 2026
- Federal Reserve 2023 data: 37% of US adults cannot cover a $400 emergency from savings
- Payday loan APR data: CFPB, "Payday Loans and Deposit Advance Products," 2013

## When to Use

- Can't make rent or mortgage this month
- Income dropped dramatically (job loss, pay cut, divorce, disability)
- Behind on multiple bills and doesn't know where to start
- Utilities about to be shut off
- Needs to cut expenses by 40-60% or more
- Has no savings buffer and wants to build one
- Living paycheck to paycheck and wants a concrete system

---

# PHASE 1: EMERGENCY TRIAGE

*Use when: immediate financial crisis — can't pay bills right now.*

## Instructions: Safety Check First

**STOP.** Before proceeding, the agent MUST ask:

> "Before we start, I need to ask: are you safe right now? Is someone controlling your finances or threatening you?"

- If financial abuse or domestic violence is present: redirect to the safe-exit-planner skill. Provide: National Domestic Violence Hotline 1-800-799-7233 or text START to 88788.
- If having thoughts of self-harm: provide 988 Suicide & Crisis Lifeline (call or text 988) immediately.
- If safe: proceed.

## Instructions: Payment Priority

When you can't pay everything, there is a correct order. This is based on consequences, not creditor pressure.

```
PAYMENT PRIORITY (most urgent first):

1. FOOD — Apply for SNAP today (benefits can arrive in 7 days)
   → SNAP enrollment: fns.usda.gov/snap
   → Local food banks: feedingamerica.org/find-your-local-foodbank
   → WIC (pregnant women/children): fns.usda.gov/wic

2. ESSENTIAL MEDICATION — Don't skip meds
   → NeedyMeds.org — discount drug programs
   → GoodRx.com — prescription price comparison
   → Patient assistance programs (call number on drug's website)
   → $4 generic lists at Walmart, Costco (no membership needed)

3. HOUSING — Rent or mortgage
   → Call landlord BEFORE the due date:
     "I'm having a financial emergency. Can we discuss a payment plan?"
   → Apply for Emergency Rental Assistance: treasury.gov/rental-assistance
   → Call 211 for local housing assistance programs

4. UTILITIES — Power, water, heat
   → Call each provider and ask for a "hardship plan"
   → LIHEAP (utility assistance): liheap.org
   → Most states prohibit utility shutoffs in extreme weather

5. TRANSPORTATION — If needed for work
   → Car payment before insurance (can't drive without the car)
   → If facing repossession: call lender about forbearance

6. EVERYTHING ELSE — credit cards, medical debt, student loans
   → These can wait. They damage credit but can't take your home.
   → Federal student loans: apply for income-driven repayment ($0/month possible)
   → Credit cards: call and ask for hardship program
   → Medical debt: does not go to collections for 180 days typically

WHAT MOST PEOPLE GET WRONG:
Medical debt and credit card debt feel urgent because collectors call.
But they can't take your house or put you in jail.
Pay housing and food first. Always.
```

## Instructions: Immediate Cash Sources

```
WHERE TO FIND MONEY THIS WEEK:

□ 211 (dial 2-1-1) — connects to ALL local assistance programs
□ Salvation Army / St. Vincent de Paul — emergency financial assistance
□ Local churches — many have emergency funds for anyone, not just members
□ Employer advance — many employers offer paycheck advances
□ State Emergency Assistance — search "[your state] emergency cash assistance"
□ Modest Needs (modestneeds.org) — grants for people in temporary crisis
□ United Way — 211 connects you or visit unitedway.org

DO NOT:
✗ Take out a payday loan (300-500% APR — will make things worse)
✗ Borrow against your 401k unless truly last resort
✗ Use title loans (you will lose your car)
```

## Instructions: Creditor Call Script

The single most important thing: CALL BEFORE YOU'RE LATE. Every creditor has hardship programs they don't advertise.

```
CREDITOR CALL SCRIPT:

"Hi, I'm calling because I'm experiencing a financial hardship
due to [job loss / medical emergency / income reduction].
I want to stay current on my account. Do you have any hardship
programs, payment plans, or temporary forbearance options?"

FOR EACH CREDITOR, ASK:
→ Can payments be deferred?
→ Can late fees be waived?
→ Is there a hardship/forbearance program?
→ Can the due date be moved?
→ GET THE REPRESENTATIVE'S NAME AND CONFIRMATION NUMBER.
```

---

# PHASE 2: AUSTERITY MODE

*Use when: income has dropped significantly and you need to survive on dramatically less.*

## Instructions: The Austerity Payment Hierarchy

```
PAYMENT PRIORITY TIERS:

TIER 1 — SURVIVAL (pay these first, no exceptions):
[] Food
[] Shelter (rent/mortgage)
[] Utilities (minimums)
[] Essential medication
[] Transportation to earn income

TIER 2 — LEGAL CONSEQUENCES (pay next):
[] Child support (non-payment = jail)
[] Tax debts
[] Court-ordered payments

TIER 3 — NEGOTIATE THESE (call before they call you):
[] Car payment (ask for deferment or lower payment)
[] Student loans (apply for income-driven repayment: $0/month possible)
[] Insurance premiums (reduce coverage to minimum required)
[] Medical debt (lowest real priority despite what collectors say)

TIER 4 — STOP IMMEDIATELY:
[] All subscriptions and memberships
[] Dining out and delivery
[] New clothing purchases
[] Any automatic payment not in Tier 1-3
```

## Instructions: Where the Real Money Is

```
HOUSING (biggest expense, biggest lever):
- Renting: can you move somewhere cheaper?
  Moving costs $500-2000 but saves $300-800/MONTH
- Can you take on a roommate? (it works)
- If you own: can you rent a room? Refinance? Ask about forbearance?
- Call landlord/mortgage company BEFORE you're behind

FOOD ($200-300/month for one person is realistic):
- Meal plan around rice, beans, eggs, potatoes, frozen veg,
  bananas, oats, chicken thighs, canned tomatoes
- See Module C/D of the survival-basics skill for the full system
- Food banks exist and are not shameful: feedingamerica.org

TRANSPORTATION:
- If you have a car payment you can't afford: can you sell the car
  and buy a $3-5K reliable used car outright?
  Eliminating a $400/month payment + higher insurance is enormous.

PHONE/INTERNET:
- Switch to $15-25/month prepaid (Mint, Visible, Cricket)
- vs major carriers: $65-100/month for the same coverage
- Cancel all streaming. Use the library for entertainment.

INSURANCE:
- Health: if you lost employer coverage, apply for Medicaid
  immediately if income qualifies. If not, get cheapest ACA plan.
- Car: raise deductibles to maximum to lower premiums
- Cancel any insurance that isn't legally required
```

## Instructions: Negotiation Calls

```
CALL SCRIPT FOR EVERY CREDITOR:

"I'm experiencing a significant reduction in income and I want to
keep paying but I need help. What options do you have for:
- Temporary payment reduction
- Deferment or forbearance
- Hardship programs"

SPECIFIC CALLS:
[] MORTGAGE: forbearance (3-12 months of reduced/no payments)
[] CAR LOAN: deferment (skip 1-3 payments, added to end)
[] CREDIT CARDS: hardship rate reduction (many drop to 0-5%)
[] STUDENT LOANS: income-driven repayment online (studentaid.gov)
[] UTILITIES: budget billing and low-income assistance (LIHEAP)
[] MEDICAL DEBT: negotiate hard — hospitals accept 20-60% of the bill.
   Never pay the full amount without negotiating first.

CALL BEFORE YOU'RE BEHIND. Being proactive gets better options.
```

## Instructions: Protecting Your Mental Health While Broke

```
FREE THINGS THAT KEEP YOU SANE:
- Library: books, movies, wifi, community events
- Walking/running outside: free, improves mental health more than
  most things you can buy
- Cooking: creative, productive, saves money simultaneously
- Community: churches, community centers, volunteer orgs — free
  social connection

THINGS TO PROTECT (even on austerity):
- One social activity per week (free or very cheap)
- Physical movement every day
- Sleep

THINGS THAT FEEL FREE BUT COST:
- Scrolling shopping sites (you will buy something)
- "Free trials" (you will forget to cancel)
- Driving around to "clear your head" (gas adds up)
```

---

# PHASE 3: EMERGENCY FUND BUILDER

*Use when: income is stabilizing and you want to prevent the next crisis.*

## Instructions: Calculate Your Real Number

"Three to six months of expenses" is useless without a concrete number.

**Agent action**: Walk the user through this calculation interactively, one category at a time. Record each number and calculate the total.

```
MONTHLY ESSENTIALS CALCULATOR:

Housing: rent or mortgage + insurance: $______
Utilities: electricity + gas + water + internet + phone: $______
Food: groceries (realistic average, NOT restaurants): $______
Transportation: car payment + insurance + gas OR transit: $______
Health: insurance premium + prescriptions: $______
Minimum debt payments: $______

TOTAL MONTHLY ESSENTIALS: $______

YOUR TARGETS:
  Starter (1 month): $______ ← START HERE
  Full (3 months):   $______ (total x 3)
  Secure (6 months): $______ (total x 6)

DON'T LET THE 6-MONTH NUMBER PARALYZE YOU.
Getting to 1 month first is the only goal.
```

## Instructions: Find the Money

```
WHERE THE MONEY COMES FROM:

SUBSCRIPTION AUDIT (20 minutes, easiest wins):
  List every subscription you pay for. For each: when did you last
  use it? If over 30 days: cancel.
  Expected savings: $20-100/month.
  
  How to find hidden subscriptions:
  - Check bank statement for recurring charges
  - Search email for "receipt" and "subscription"

PHONE PLAN SWITCH:
  Most people overpay by $20-40/month.
  MVNOs (same networks, fraction of price):
    Mint Mobile: ~$15-25/month
    Visible: ~$25/month
  vs major carriers: $65-100/month

ONE-TIME INCOME SOURCES:
  - Sell unused items (Facebook Marketplace, eBay)
  - Tax refund: redirect directly to emergency fund
  - Side work: redirect first few paychecks
```

## Instructions: Open the Right Account

```
EMERGENCY FUND ACCOUNT REQUIREMENTS:

MUST HAVE:
[ ] FDIC insured (banks) or NCUA insured (credit unions)
    — up to $250,000 per depositor. Safe even if bank fails.
[ ] No monthly fees
[ ] No minimum balance requirements
[ ] Easy transfer to checking in 1-3 business days

SHOULD HAVE:
[ ] High-yield savings (HYSA)
    As of March 2026: competitive HYSAs offer 4-5% APY.
    Check current rates: bankrate.com/banking/savings/
    
DO NOT USE:
[ ] Your checking account (too easy to accidentally spend)
[ ] Cash at home (no interest, theft/fire/flood risk)
[ ] Crypto or investments (value can drop 50% right when you need it)
[ ] CDs or accounts with early withdrawal penalties

CREDIT UNION OPTION:
  Non-profit, often better rates than banks.
  Find one at: mycreditunion.gov
```

## Instructions: Automate and Protect

```
AUTOMATION SETUP:
1. Open the savings account
2. Set automatic transfer from checking to savings:
   - Amount: whatever you found in the previous step
   - Timing: THE DAY AFTER PAYDAY (money you never see, you never spend)
   - Do this at your bank's website or app — takes 5 minutes

STARTING SMALL IS CORRECT:
  $25/month = $300/year (plus interest)
  The habit matters more than the amount.
  $25 → $50 → $100 as income stabilizes.

WHAT COUNTS AS AN EMERGENCY:
  [ ] Job loss or sudden income interruption
  [ ] Medical bill or unexpected health cost
  [ ] Essential car repair (needed to get to work)
  [ ] Home repair affecting habitability
  [ ] Family emergency requiring travel

WHAT DOES NOT COUNT:
  [ ] Holiday gifts (predictable — plan for it separately)
  [ ] Sales or deals
  [ ] Travel
  [ ] Upgrading something that still works

THE FRICTION TRICK:
  Keep the emergency fund at a DIFFERENT bank than your checking.
  The 1-3 day transfer delay is a feature, not a bug.
  It forces you to confirm the spending is genuinely necessary.

IF YOU USE IT:
  Replenish before you stop. This is not a failure — it is the fund
  doing its job. Set a new transfer at the same or higher amount.
```

## If This Fails

**Phase 1 (crisis):**
1. 211 not available: try [findhelp.org](https://www.findhelp.org) — enter zip code for local programs
2. SNAP denied: appeal within 90 days. Most denials are missing documents, not ineligibility
3. About to be evicted: contact legal aid at [lawhelp.org](https://www.lawhelp.org) — many eviction defense services are free
4. Utilities already shut off: call utility company for reconnection on a hardship plan. Apply for emergency LIHEAP
5. Overwhelmed: call or text 988

**Phase 2 (austerity):**
1. Can't cover rent even after cutting everything: contact 211 immediately for Emergency Rental Assistance
2. Can't afford medication: needymeds.org, $4 generics at Walmart/Costco
3. Debt still piling up: see the debt-survival skill
4. Breaking you mentally: call or text 988. Free counseling via community mental health centers — call 211

**Phase 3 (rebuilding):**
1. Income doesn't cover essentials: this is a benefits or income problem. See the benefits-navigator skill
2. Keep spending the emergency fund: move it to a bank with no debit card access
3. Debt payments are too high to save anything: NFCC non-profit credit counselor at nfcc.org — free or low cost

## Rules

- Lead with Phase 1's triage order — people in crisis need priorities, not options
- Food and medication FIRST, always
- Never recommend payday loans, title loans, or high-interest debt
- If someone mentions financial abuse or feeling unsafe, redirect to safe-exit-planner
- Never moralize about financial situations — austerity is a response to circumstances, not a character flaw
- Medical debt and credit card debt collectors are not the priority — housing and food are
- If income is genuinely below survival cost, say so — budgeting harder will not fix a structural gap

## Tips

- 211 is the most underused resource in the US. It connects to every local program that exists.
- Most hardship programs require you to ASK — they don't offer automatically
- Medical debt is the most negotiable debt. Hospitals accept 20-60% of the bill.
- The single biggest savings lever most people miss: a car payment. Selling a $15K car and buying a $4K reliable used car saves $400+/month in payments plus cheaper insurance.
- The transfer timing (day after payday, not end of month) is the most impactful behavioral design choice in personal savings.
- "I can't afford that" is a complete sentence. You don't owe an explanation.

## Agent State

Persist across sessions:

```yaml
money_crisis:
  phase: null           # 1 | 2 | 3
  safety_check_done: false
  phase_1:
    tier_1_covered: false
    snap_applied: false
    creditors_called: []
    assistance_applied: []
  phase_2:
    monthly_income: null
    monthly_minimum_expenses: null
    runway_months: null
    bills_negotiated: []
    expense_cuts_made: []
  phase_3:
    monthly_essentials: null
    targets:
      one_month: null
      three_months: null
      six_months: null
    current_balance: null
    automatic_transfer:
      amount: null
      day: null
      set_up: false
    milestones:
      first_100: false
      one_month: false
      three_months: false
    emergency_definition: []
    subscriptions_cancelled: []
    flags:
      income_gap: false
      debt_counselor_referred: false
      unbanked: false
```

## Automation Triggers

```yaml
triggers:
  - name: creditor_call_reminder
    condition: "phase == 1 AND any creditors not yet called"
    schedule: "daily until all calls made"
    action: "You still have creditors to call. Today: call [next creditor]. Use the script. Get their name and confirmation number."

  - name: monthly_austerity_review
    condition: "phase == 2"
    schedule: "monthly on the 1st"
    action: "Monthly money check: What came in? What went out? Are you staying within the austerity plan? Recalculate runway."

  - name: transfer_reminder
    condition: "phase == 3 AND automatic_transfer.set_up == false"
    action: "Savings automation not yet set up. This is the most important step. Ready to set up the transfer? It takes under 5 minutes."

  - name: milestone_checkin
    condition: "phase == 3 AND current_balance >= targets.one_month AND milestones.one_month == false"
    action: "You hit your 1-month emergency fund target. That is a real milestone. Next target: 3 months. Ready to increase the automatic transfer?"
```
