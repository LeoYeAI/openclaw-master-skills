---
name: emergency-fund-builder
description: >-
  Step-by-step protocol for building an emergency fund from zero. Use when someone has no savings buffer, lives paycheck to paycheck, or wants a concrete system to build financial resilience starting with whatever they have.
metadata:
  category: money
  tagline: >-
    Build your first financial buffer from zero — calculate your real number, find the money, automate it, and protect it from yourself
  display_name: "Emergency Fund Builder"
  openclaw:
    requires:
      tools: [calendar, filesystem]
    install: "npx clawhub install howtousehumans/emergency-fund-builder"
---

# Emergency Fund Builder

An emergency fund is not a luxury. It is the single piece of financial infrastructure that prevents one crisis from becoming a spiral. Without it, every car repair, medical bill, or job gap goes on a credit card — and debt compounds faster than savings. With it, most ordinary emergencies are inconveniences, not catastrophes. This skill provides a concrete protocol to build a buffer from zero, even on a tight income, without pretending it's easy or that it just takes "cutting out lattes."

**DISCLAIMER**: This skill provides general financial guidance, not financial advice. Tax situations, benefit eligibility, debt payoff vs saving trade-offs, and investment decisions vary by individual circumstances. For complex situations, a non-profit credit counselor (NFCC member agencies offer free or low-cost counseling) is a better resource than this skill alone.

## Sources & Verification

- Federal Deposit Insurance Corporation (FDIC) — deposit insurance limits, bank account safety verification. fdic.gov — verified active March 2026
- Consumer Financial Protection Bureau (CFPB) — savings account guidance, bank comparison tools, and financial education resources. consumerfinance.gov — verified active March 2026
- National Foundation for Credit Counseling (NFCC) — non-profit credit counseling network, free or low-cost. nfcc.org — verified active March 2026
- Board of Governors of the Federal Reserve System, "Report on the Economic Well-Being of US Households," 2023 — 37% of US adults cannot cover a $400 emergency from savings
- HighYieldSavings.net and Bankrate (bankrate.com) — HYSA rate comparison tools. Bankrate verified active March 2026
- NCUA (National Credit Union Administration) — credit union deposit insurance parallel to FDIC. mycreditunion.gov — verified active March 2026

## When to Use

- User has no savings buffer and lives paycheck to paycheck
- A recent emergency wiped out whatever savings they had
- Knows they "should" save but can't figure out how to start
- Has money going out the same day it comes in
- Wants to stop relying on credit cards for emergencies
- Has some savings but no intentional system or target

## Instructions

### Step 1: Calculate your real number

"Three to six months of expenses" is the standard advice. It is useless without a concrete dollar figure.

**Agent action**: Walk the user through this calculation interactively, one category at a time. Record each number and calculate the total. Store as "monthly_essentials" in state.

```
MONTHLY ESSENTIALS CALCULATOR:
(essentials only — not nice-to-haves)

Housing:
  Rent or mortgage: $______
  Renter's/homeowner's insurance: $______

Utilities:
  Electricity: $______
  Gas/heat: $______
  Water: $______
  Internet (if needed for work or job search): $______
  Phone (basic plan): $______

Food:
  Groceries (realistic average): $______
  (NOT restaurants or delivery — that's discretionary)

Transportation:
  Car payment: $______
  Car insurance: $______
  Gas or public transit: $______

Health:
  Health insurance premium (your share): $______
  Prescription medications: $______

Minimum debt payments (credit cards, student loans, etc.):
  These are non-negotiable minimums only: $______

TOTAL MONTHLY ESSENTIALS: $______

YOUR EMERGENCY FUND TARGETS:
  Starter target (1 month):    $______ (your total x 1)
  Full target (3 months):      $______ (your total x 3)
  Secure target (6 months):    $______ (your total x 6)

START WITH THE STARTER TARGET.
Getting to 1 month first is the most important step.
Don't let the 6-month number paralyze you.
```

### Step 2: Find the money

This step requires honesty, not judgment. The goal is to find $20-200/month without destroying quality of life.

**Agent action**: Run the user through each category and ask about current spending. Do not moralize. Record identified savings in state. Calculate total available monthly savings.

```
WHERE THE MONEY COMES FROM:

SUBSCRIPTION AUDIT (easiest wins — takes 20 minutes):
  List every subscription you pay for:
  [ ] Streaming services (Netflix, Hulu, Disney+, etc.)
  [ ] Gym membership (are you using it?)
  [ ] Subscription boxes
  [ ] Software subscriptions
  [ ] News paywalls
  [ ] Any "free trials" that became charges

  For each: when did you last use it? If over 30 days: cancel.
  Expected savings: $20-100/month for most people.

  How to find hidden subscriptions:
  - Check your bank statement/credit card for recurring charges
  - Search your email for "receipt" and "subscription"
  - Apps: your bank app often has a subscription detection feature

FOOD SPENDING:
  What are you spending on food per week, honestly?
  If over $70/week for one person: the budget-meal-prep skill
  shows how to get to $40-50/week. That's $80-120/month freed up.

PHONE PLAN:
  Most people overpay by $20-40/month.
  MVNOs (low-cost carriers that use the same networks):
    Mint Mobile: ~$15-25/month
    Visible: ~$25/month
    Cricket: ~$30/month
  vs major carriers: $65-100/month for the same coverage.

ONE-TIME INCOME SOURCES:
  [ ] Unused items on Facebook Marketplace, eBay, or Craigslist
  [ ] Overtime, side work, or gig work for the launch sprint
  [ ] Tax refund: redirect it directly to emergency fund

  Note: Do NOT build your emergency fund plan on income
  you don't reliably have. Use reliable income for
  the recurring deposit; use windfalls for acceleration.
```

### Step 3: Choose and open the right account

The emergency fund needs to be accessible, safe, and earning interest. It should NOT be in your checking account — that money will disappear.

**Agent action**: Help the user evaluate account options. Do not recommend specific banks. Provide the comparison framework and red-flag checklist.

```
EMERGENCY FUND ACCOUNT REQUIREMENTS:

MUST HAVE:
[ ] FDIC insured (banks) or NCUA insured (credit unions)
    — up to $250,000 per depositor. This means your
    money is safe even if the bank fails.
[ ] No monthly fees (common at online banks and credit unions)
[ ] No minimum balance requirements (or one you can meet)
[ ] Easy transfer to checking in 1-3 business days
    (not instant — but accessible when you need it)

SHOULD HAVE:
[ ] High-yield interest rate (HYSA)
    As of March 2026: competitive HYSAs offer 4-5% APY.
    Traditional savings accounts at big banks: 0.01-0.5%.
    On a $2,000 emergency fund: that's $80-100/year vs $2.
    Check current rates at: bankrate.com/banking/savings/best-high-yield-interests-savings-accounts/

DO NOT USE:
[ ] Your checking account (too easy to accidentally spend)
[ ] Cash at home (no interest, theft/fire/flood risk)
[ ] Crypto or investments (value can drop 30-50% right when
    you need the money — that's the opposite of a buffer)
[ ] CDs or accounts with early withdrawal penalties

CREDIT UNION OPTION:
  Credit unions are non-profit and often offer better rates
  and lower fees than banks. Membership requirements are
  usually easy to meet (employer, geography, association).
  Find one at: mycreditunion.gov

RED FLAGS IN ACCOUNT TERMS:
[ ] Monthly maintenance fee (skip it)
[ ] "Introductory rate" that drops after 3-12 months
    (fine — just note when it changes and compare again)
[ ] Limits on withdrawals per month that would prevent
    emergency access
```

### Step 4: Automate the transfer

Saving by willpower fails. Automation succeeds because the decision is made once, not monthly.

**Agent action**: After the user selects an account, set up the automation reminder and record the transfer amount and date in state.

```
AUTOMATION SETUP:

1. Open the new savings account.
2. Set up an automatic transfer from checking to savings:
   - Amount: whatever you identified in Step 2
   - Timing: THE DAY AFTER PAYDAY (not end of month)
     Why: money you never see in checking, you never spend.
     "Pay yourself first" is not motivational nonsense --
     it's a behavioral design choice.
   - Do this at your bank's website or app.
     Most let you schedule recurring transfers in under
     5 minutes.

STARTING SMALL IS CORRECT:
  $25/month is not nothing. It is $300/year.
  It is also a habit. The amount can increase.
  The habit is what matters first.

  $25/month: $300/year
  $50/month: $600/year
  $100/month: $1,200/year
  $150/month: $1,800/year — for many people, this is
    a full 1-month starter emergency fund in one year.

INCREASE ANNUALLY:
  Set a calendar reminder for 12 months from now to
  increase the transfer by $25. This is called the
  "set it and forget it increase" and it compounds.
```

### Step 5: Protect it from yourself

The emergency fund only works if it stays there until a real emergency.

**Agent action**: Help the user define what counts as an emergency and what doesn't. Save the definition in state.

```
WHAT COUNTS AS AN EMERGENCY:
  [ ] Job loss or sudden income interruption
  [ ] Medical bill or unexpected health cost
  [ ] Essential car repair (needed to get to work)
  [ ] Home repair that affects habitability (heat, water,
      structural safety)
  [ ] Family emergency requiring travel

WHAT DOES NOT COUNT:
  [ ] Holiday gifts (predictable — plan for it separately)
  [ ] Annual bills like car registration (predictable --
      divide by 12 and save separately each month)
  [ ] Sales, deals, or things you "might need soon"
  [ ] Wanting to upgrade something that still works
  [ ] Travel (save separately for this)

THE FRICTION TRICK:
  Keep the emergency fund at a different bank than your
  checking account. The 1-3 day transfer delay is not
  a bug — it's a feature. It gives you time to confirm
  the spending is genuinely necessary.
  "I need it now" is rarely true for things that aren't
  actual emergencies.

IF YOU USE IT:
  Replenish before you stop. Set a new automatic transfer
  at the same or higher amount until it's rebuilt.
  This is not a failure — it's the fund doing its job.
```

### Step 6: Build to three months

Once the starter fund (1 month) is established, the protocol continues.

**Agent action**: When the user hits their 1-month target, recalculate the 3-month target, increase the automatic transfer if possible, and set a check-in date.

```
BUILDING FROM 1 TO 3 MONTHS:

1. Increase the automatic transfer by whatever is
   realistic without straining your budget.

2. Direct any windfalls to the fund:
   Tax refund, bonus, birthday money, side income.
   Even 50% of a windfall to savings is better than 0%.

3. Track progress.
   Most HYSAs show your balance in the app.
   Set a quarterly check-in to see progress and
   adjust the transfer amount if your income has changed.

WHEN CARRYING HIGH-INTEREST DEBT:
  This is the real question: should you pay off debt
  or build savings?

  RECOMMENDED APPROACH (from CFPB):
  1. Get to $500-1,000 starter buffer first.
     This prevents you from adding new debt during
     the payoff phase.
  2. Then focus extra money on high-interest debt
     (anything above 10% APR — credit cards, payday loans).
  3. Once high-interest debt is cleared, build the
     full 3-month fund.

  Reason: a $500 buffer prevents a $500 emergency
  from becoming a $600 credit card charge at 25% APR.
  The math favors the buffer first.
```

## If This Fails

1. **Income genuinely does not cover essentials**: This is not a savings problem — it is an income or benefits problem. See the benefits-navigator skill to check for programs you may qualify for. See the austerity-living skill for immediate expense reduction. See the debt-survival skill if debt is consuming available income.
2. **You keep spending the emergency fund on non-emergencies**: Move the account to a bank with no app or debit card access. The added friction is the point.
3. **A financial crisis has wiped out your savings**: See the emergency-financial-triage skill for the immediate stabilization protocol. This skill is for building, not recovering.
4. **Debt payments are too high to save anything**: A non-profit credit counselor (NFCC member agencies at nfcc.org) can negotiate debt repayment plans and consolidation options at no or low cost. Do not use for-profit debt settlement companies — they damage your credit and often make things worse.
5. **No bank account**: Many people experiencing financial hardship are unbanked. Credit unions have the lowest barrier to entry. Bank On-certified accounts (finra.org/investors/have-problem/bank-account-problems) offer no-fee accounts specifically designed for people rebuilding banking relationships.

## Rules

- Never recommend specific financial products or banks by name — provide the framework and comparison criteria instead
- Never suggest stopping minimum debt payments in favor of saving — that triggers fees and credit damage that cost more than the savings gain
- Always acknowledge when the income/expense gap is structural — don't imply that budgeting harder will fix a situation where income is genuinely below survival cost
- Crypto, stocks, and investments are not emergency funds — never suggest them as substitutes

## Tips

- The Federal Reserve data is not shaming material — it is evidence that the lack of a buffer is a structural economic reality for most people, not a personal failure.
- The transfer timing (day after payday, not end of month) is the single most impactful behavioral design choice in personal savings. Test it.
- Interest rate chasing on savings accounts is not worth more than 30 minutes of effort per year. Pick a competitive HYSA and move on.
- The most common emergency fund mistake is making the target feel impossible by leading with the 6-month number. One month first. Always.

## Agent State

Persist across sessions:

```yaml
emergency_fund:
  monthly_essentials: null
  targets:
    one_month: null
    three_months: null
    six_months: null
  current_balance: null
  current_account_type: null
  automatic_transfer:
    amount: null
    frequency: null
    day: null
    set_up: false
  emergency_definition: []
  milestones_reached:
    first_100: false
    one_month: false
    three_months: false
    six_months: false
  savings_found_monthly: null
  subscriptions_cancelled: []
  fund_used:
    - date: null
      reason: null
      amount: null
      replenished: false
  flags:
    income_gap: false
    high_interest_debt: false
    debt_counselor_referred: false
    unbanked: false
```

## Automation Triggers

```yaml
triggers:
  - name: transfer_day_reminder
    condition: "automatic_transfer.set_up == false"
    action: "Savings automation not yet set up. This is the most important step — money moved automatically before you see it is money that gets saved. Ready to set up the transfer now? It takes under 5 minutes."

  - name: monthly_balance_checkin
    condition: "current_balance IS SET"
    schedule: "monthly on the 1st"
    action: "Monthly savings check-in. What's your emergency fund balance right now? Let's update your progress and see how close you are to your next milestone."

  - name: milestone_celebration
    condition: "milestones_reached.one_month == false AND current_balance >= targets.one_month"
    action: "You hit your 1-month emergency fund target. That is a real thing — 37% of Americans cannot cover a $400 emergency. You now can. Next target: 3 months. Ready to increase the automatic transfer?"

  - name: annual_transfer_increase
    condition: "automatic_transfer.set_up == true"
    schedule: "annually"
    action: "Annual savings review. Your income or expenses may have changed. Can you increase your automatic transfer by $25-50/month? Even a small increase compounds significantly over time."

  - name: replenishment_prompt
    condition: "fund_used[-1].replenished == false"
    action: "You used your emergency fund. Good — that's what it's for. Time to rebuild it. What can you put toward replenishment this month? Let's reset the automatic transfer."
```
