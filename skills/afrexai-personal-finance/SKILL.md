---
name: afrexai-personal-finance
description: Complete personal finance system — budgeting, debt payoff, investing, tax optimization, net worth tracking, and financial independence planning. Use when managing money, building wealth, paying off debt, planning retirement, or optimizing taxes. Zero dependencies.
---

# Personal Finance Mastery

Complete personal finance system covering budgeting, debt elimination, investing, tax optimization, insurance, estate planning, and financial independence. Works for any income level, any country.

---

## Quick Financial Health Check

Run `/finance-check` to score current financial health:

| Signal | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Emergency fund | 3-6 months expenses | 1-3 months | < 1 month |
| Savings rate | > 20% | 10-20% | < 10% |
| Debt-to-income | < 36% | 36-50% | > 50% |
| Housing cost | < 28% of gross | 28-35% | > 35% |
| Net worth trend | Growing quarterly | Flat | Declining |
| Insurance coverage | All critical covered | Gaps exist | Major gaps |
| Investment allocation | Age-appropriate | Slightly off | Way off |
| Tax optimization | Using all vehicles | Some unused | None used |

Score: /16. Below 10 = immediate action needed.

---

## Phase 1: Financial Snapshot

### Net Worth Statement

```yaml
net_worth:
  date: "YYYY-MM-DD"
  assets:
    liquid:
      checking: 0
      savings: 0
      money_market: 0
    investments:
      retirement_401k: 0
      retirement_ira: 0
      brokerage: 0
      hsa: 0
      crypto: 0
    property:
      home_value: 0
      vehicles: 0
      other: 0
  liabilities:
    mortgage: 0
    student_loans: 0
    auto_loans: 0
    credit_cards: 0
    personal_loans: 0
    other_debt: 0
  net_worth: 0  # assets - liabilities
  monthly_income_gross: 0
  monthly_income_net: 0
  monthly_expenses: 0
  savings_rate: 0  # (income_net - expenses) / income_net
  debt_to_income: 0  # total_debt_payments / gross_income
```

### Income Inventory

Document ALL income sources:

| Source | Type | Monthly Amount | Stability | Growth Potential |
|--------|------|---------------|-----------|-----------------|
| Primary job | W-2/salary | | High | Moderate |
| Side business | 1099/self-emp | | Variable | High |
| Investments | Dividends/interest | | Moderate | Moderate |
| Rental income | Passive | | Moderate | Moderate |
| Other | | | | |

### Monthly Cash Flow Map

```
INCOME (net take-home)
├── Fixed Expenses (needs) — target: ≤50%
│   ├── Housing (rent/mortgage + insurance + tax)
│   ├── Utilities (electric, water, gas, internet, phone)
│   ├── Transportation (car payment, insurance, fuel, transit)
│   ├── Insurance (health, life, disability)
│   ├── Minimum debt payments
│   └── Groceries (baseline)
├── Financial Goals (savings/investing) — target: ≥20%
│   ├── Emergency fund
│   ├── Retirement contributions
│   ├── Investment contributions
│   ├── Debt extra payments
│   └── Specific savings goals
└── Lifestyle (wants) — target: ≤30%
    ├── Dining out
    ├── Entertainment/subscriptions
    ├── Shopping/clothing
    ├── Travel
    ├── Hobbies
    └── Personal care
```

This is the **50/30/20 framework** — adjust ratios to your situation but track against these benchmarks.

---

## Phase 2: Emergency Fund

### Priority #1 — Before Investing

| Stage | Target | Timeline | Where to Keep |
|-------|--------|----------|---------------|
| Starter | $1,000 (or 1 month) | 1-3 months | High-yield savings |
| Basic | 3 months expenses | 3-6 months | High-yield savings |
| Full | 6 months expenses | 6-12 months | HYSA + money market |
| Enhanced | 12 months expenses | Optional | HYSA + I-bonds + money market |

### When to Use Emergency Fund

**YES — True emergencies:**
- Job loss
- Medical emergency
- Essential home/car repair
- Urgent family situation

**NO — Not emergencies:**
- Vacations
- Sales/deals
- Predictable expenses (insurance premiums, taxes)
- Lifestyle upgrades

### Replenishment Rules

- After any withdrawal, replenish becomes priority #1
- Redirect all non-essential spending until restored
- Set automatic transfer to rebuild over 3-6 months

---

## Phase 3: Debt Elimination

### Debt Inventory

```yaml
debt_inventory:
  - name: "Credit Card A"
    balance: 0
    interest_rate: 0
    minimum_payment: 0
    type: "revolving"
    tax_deductible: false
  - name: "Student Loan"
    balance: 0
    interest_rate: 0
    minimum_payment: 0
    type: "installment"
    tax_deductible: true
```

### Strategy Selection

| Method | How It Works | Best For | Psychology |
|--------|-------------|----------|------------|
| **Avalanche** | Pay highest interest first | Mathematically optimal, saves most money | Disciplined people |
| **Snowball** | Pay smallest balance first | Fastest "wins", builds momentum | Need motivation |
| **Hybrid** | Pay any debt < $500 first, then avalanche | Quick wins + math optimization | Most people |

### Debt Priority Order

1. **Payday loans / title loans** (300%+ APR) — eliminate immediately, even if it means selling things
2. **Credit cards** (15-30% APR) — aggressive payoff
3. **Personal loans** (8-15% APR) — steady payoff
4. **Auto loans** (4-8% APR) — pay minimum unless rate > 6%
5. **Student loans** (3-7% APR) — pay minimum, invest the difference if rate < 5%
6. **Mortgage** (3-7% APR) — usually don't accelerate, invest instead

### The Crossover Rule

**If debt interest rate > expected investment return (historically ~7-10% stocks):**
→ Pay off debt first

**If debt interest rate < expected investment return:**
→ Pay minimum on debt, invest the difference

**Grey zone (4-7%):**
→ Split extra money 50/50 between debt payoff and investing

### Debt Payoff Accelerators

1. **Balance transfer** — 0% APR cards (watch transfer fees, 3-5%)
2. **Refinance** — lower rate on student loans, mortgage, auto
3. **Consolidation** — single payment, potentially lower rate
4. **Income boost** — side income dedicated 100% to debt
5. **Expense audit** — cancel subscriptions, negotiate bills
6. **Sell assets** — unused items → debt payoff

### Credit Score Management

| Factor | Weight | How to Optimize |
|--------|--------|----------------|
| Payment history | 35% | Never miss a payment — automate minimums |
| Credit utilization | 30% | Keep below 30%, ideally below 10% |
| Length of history | 15% | Don't close old cards |
| Credit mix | 10% | Installment + revolving is good |
| New credit | 10% | Limit hard inquiries |

---

## Phase 4: Budgeting System

### Budget Template

```yaml
monthly_budget:
  month: "YYYY-MM"
  income:
    salary_net: 0
    side_income: 0
    other: 0
    total: 0
  
  fixed_expenses:  # ≤50% of income
    housing: 0
    utilities: 0
    transportation: 0
    insurance: 0
    debt_minimums: 0
    groceries: 0
    childcare: 0
    subscriptions_essential: 0
    subtotal: 0
    percent_of_income: 0
  
  financial_goals:  # ≥20% of income
    emergency_fund: 0
    retirement: 0
    investments: 0
    debt_extra: 0
    savings_goals: 0
    subtotal: 0
    percent_of_income: 0
  
  lifestyle:  # ≤30% of income
    dining_out: 0
    entertainment: 0
    shopping: 0
    travel_fund: 0
    hobbies: 0
    personal_care: 0
    gifts: 0
    subscriptions_fun: 0
    subtotal: 0
    percent_of_income: 0
  
  variance: 0  # income - all expenses (should be ≥ 0)
```

### Expense Tracking Methods

| Method | Effort | Best For |
|--------|--------|----------|
| **Envelope system** | High | Cash-heavy, needs discipline |
| **App tracking** (YNAB, Mint) | Low | Tech-savvy, automated |
| **Spreadsheet** | Medium | Control-oriented, custom |
| **Agent-tracked** | Low | Let AI categorize + alert |
| **Reverse budgeting** | Lowest | Auto-transfer savings first, spend rest |

### Reverse Budgeting (Recommended)

The simplest effective system:

1. **Day 1 of month**: Auto-transfer savings/investment target to separate accounts
2. **Day 1 of month**: Auto-pay all fixed bills
3. **Remaining**: Spend freely — guilt-free because goals are already funded
4. **Monthly**: Review if remaining amount felt tight or generous → adjust

### Subscription Audit

Run quarterly:
- List every recurring charge
- Score each 1-5 (value received)
- Cancel anything scoring ≤ 2
- Downgrade anything scoring 3
- Keep 4-5s
- **Common waste**: streaming services (how many do you actually watch?), gym memberships (do you go?), software trials, news subscriptions

### Annual Expenses Calendar

Don't let irregular expenses surprise you:

| Month | Expense | Amount | Funded? |
|-------|---------|--------|---------|
| Jan | Insurance renewal | | |
| Mar | Tax preparation | | |
| Apr | Tax payment (if owed) | | |
| Jun | Car registration | | |
| Aug | Back to school | | |
| Nov | Holiday gifts | | |
| Dec | Annual subscriptions | | |

**Sinking fund**: Divide annual expenses by 12, save monthly. No surprises.

---

## Phase 5: Investing

### Investment Priority Order

Follow this exact sequence:

1. **Employer 401(k) match** — FREE money, always max this first (typically 3-6% match)
2. **High-interest debt payoff** — anything > 7% APR
3. **Emergency fund** — 3-6 months
4. **HSA** (if eligible) — triple tax advantage ($4,150 individual / $8,300 family, 2024)
5. **Roth IRA** — $7,000/year ($8,000 if 50+), tax-free growth
6. **401(k) beyond match** — up to $23,000/year ($30,500 if 50+)
7. **Taxable brokerage** — no limits, more flexibility
8. **529 plan** (if kids) — tax-free education growth
9. **Real estate / alternatives** — only after 1-8 are solid

### Asset Allocation by Age

Simple rule: **Age in bonds, rest in stocks** (adjust for risk tolerance)

| Age Range | Stocks | Bonds | Alternatives | Risk Level |
|-----------|--------|-------|-------------|------------|
| 20-35 | 90% | 10% | 0% | Aggressive |
| 35-45 | 80% | 15% | 5% | Growth |
| 45-55 | 70% | 25% | 5% | Moderate |
| 55-65 | 60% | 35% | 5% | Conservative |
| 65+ | 40-50% | 40-50% | 0-10% | Preservation |

### Simple Portfolio Models

**3-Fund Portfolio** (Bogleheads recommended):
- US Total Stock Market (VTI/VTSAX) — 60%
- International Stock Market (VXUS/VTIAX) — 30%
- US Total Bond Market (BND/VBTLX) — 10%

**2-Fund Portfolio** (even simpler):
- Target Date Fund (e.g., Vanguard 2055) — 100%
- Adjust nothing until retirement

**Income Portfolio** (retirees):
- Dividend stocks (VYM/SCHD) — 30%
- Bonds (BND/AGG) — 40%
- REITs (VNQ) — 15%
- Cash/money market — 15%

### Investment Rules

1. **Never invest money you need within 5 years** — use HYSA/CDs for short-term
2. **Dollar-cost average** — invest consistently regardless of market conditions
3. **Don't time the market** — time IN the market beats timing THE market
4. **Keep fees below 0.2%** — index funds, not active management
5. **Rebalance annually** — sell winners, buy losers (back to target allocation)
6. **Ignore daily market news** — check portfolio quarterly at most
7. **Tax-loss harvest** in taxable accounts — offset gains with losses
8. **Never panic sell** — downturns are buying opportunities

### Compound Growth Reference

$500/month invested at 7% average return:

| Years | Contributed | Portfolio Value | Growth |
|-------|------------|-----------------|--------|
| 5 | $30,000 | $35,800 | $5,800 |
| 10 | $60,000 | $86,500 | $26,500 |
| 20 | $120,000 | $260,500 | $140,500 |
| 30 | $180,000 | $607,000 | $427,000 |
| 40 | $240,000 | $1,320,000 | $1,080,000 |

**The message**: Start early. Time is the biggest factor.

---

## Phase 6: Tax Optimization

### Tax-Advantaged Account Summary

| Account | Contribution Limit (2024) | Tax Treatment | Best For |
|---------|--------------------------|---------------|----------|
| Traditional 401(k) | $23,000 ($30,500 50+) | Pre-tax in, taxed out | High earners now |
| Roth 401(k) | $23,000 ($30,500 50+) | After-tax in, tax-free out | Expect higher tax later |
| Traditional IRA | $7,000 ($8,000 50+) | Pre-tax in, taxed out | No employer plan |
| Roth IRA | $7,000 ($8,000 50+) | After-tax in, tax-free out | Under income limits |
| HSA | $4,150/$8,300 | Pre-tax in, tax-free out | Triple tax advantage |
| 529 Plan | Varies by state | After-tax in, tax-free for education | Kids' college |
| Mega Backdoor Roth | Up to $69,000 total | After-tax → Roth conversion | High earners |

### Tax Reduction Strategies

**For employees:**
1. Max 401(k) contributions — reduces taxable income
2. Use FSA/HSA for medical expenses
3. Itemize deductions if > standard deduction ($14,600 single / $29,200 married, 2024)
4. Charitable donations — donor-advised fund for bunching
5. State/local tax (SALT) deduction — up to $10,000

**For self-employed:**
1. SEP IRA or Solo 401(k) — up to $69,000/year
2. Qualified Business Income deduction — 20% of QBI
3. Home office deduction — dedicated space required
4. Business expenses — equipment, software, travel, meals (50%)
5. Health insurance premium deduction
6. Retirement plan contributions
7. Vehicle expenses — mileage or actual costs

**For investors:**
1. Hold investments > 1 year — long-term capital gains rate (0/15/20% vs ordinary income)
2. Tax-loss harvesting — sell losers to offset gains
3. Asset location — bonds in tax-advantaged, stocks in taxable
4. Qualified dividends — taxed at capital gains rate
5. Roth conversion ladder — convert in low-income years
6. Donate appreciated stock — avoid capital gains + get deduction
7. Opportunity Zones — defer and reduce capital gains

### Tax Planning Calendar

| Month | Action |
|-------|--------|
| January | Gather W-2s, 1099s, receipts |
| February | Estimate tax liability |
| March | File or extend (April 15 deadline) |
| April | Q1 estimated tax payment (if self-employed) |
| June | Q2 estimated tax payment |
| September | Q3 estimated tax payment |
| October | Extended filing deadline |
| November | Tax-loss harvesting review |
| December | Max retirement contributions, charitable donations, Roth conversions |
| January | Q4 estimated tax payment |

---

## Phase 7: Insurance & Protection

### Essential Coverage Checklist

| Insurance | Need Level | Notes |
|-----------|-----------|-------|
| Health insurance | **Critical** | ACA marketplace if no employer plan |
| Auto insurance | **Critical** (if driving) | Liability + collision/comprehensive |
| Renters/homeowners | **Critical** | Covers belongings + liability |
| Life insurance | **Critical** (if dependents) | Term life = 10-12x annual income |
| Disability insurance | **Important** | 60-70% income replacement |
| Umbrella liability | **Important** (high net worth) | $1M+ coverage, cheap |
| Long-term care | **Consider** (age 50+) | Protect retirement assets |

### Life Insurance Decision Tree

```
Do you have dependents who rely on your income?
├── YES → Buy term life insurance
│   ├── Coverage: 10-12x annual income
│   ├── Term: until youngest child is 25 or mortgage is paid
│   └── Type: TERM (not whole life — invest the difference)
└── NO → Skip for now, reassess when situation changes
```

**Rule**: Never buy whole life insurance as an investment. Buy term, invest the difference.

### Insurance Optimization

1. **Bundle policies** — same insurer for home + auto = 10-25% discount
2. **Raise deductibles** — $500 → $1,000 deductible saves 15-30% on premiums
3. **Shop annually** — rates vary wildly between insurers
4. **Review coverage yearly** — life changes mean coverage changes
5. **Don't over-insure** — match coverage to actual risk and assets

---

## Phase 8: Major Purchase Planning

### Home Buying Readiness

| Factor | Ready | Not Ready |
|--------|-------|-----------|
| Emergency fund | 3-6 months AFTER down payment | Drained by purchase |
| Down payment | 20% (avoids PMI) | < 10% |
| Debt-to-income | < 36% with mortgage | > 43% |
| Credit score | 740+ (best rates) | < 680 |
| Job stability | 2+ years steady income | Recent job change |
| Plan to stay | 5+ years | < 3 years (rent instead) |
| Monthly cost | < 28% of gross income | > 35% |

### Rent vs Buy Decision

**Monthly cost comparison:**
- Renting: rent + renters insurance
- Buying: mortgage + property tax + insurance + HOA + maintenance (1-3% of value/year) + opportunity cost of down payment

**Buy if**: staying 5+ years AND total ownership cost < rent AND you want the stability.
**Rent if**: < 5 years OR high mobility OR local market is overpriced (price-to-rent > 20x).

### Car Buying Rules

1. **Total vehicle cost < 35% of annual income** (purchase price)
2. **Buy used** (2-4 years old) — avoid 30-40% depreciation
3. **Pay cash if possible** — if financing, keep loan < 48 months
4. **Total transportation < 15% of take-home** (payment + insurance + fuel + maintenance)
5. **Never lease** unless business write-off justifies it

---

## Phase 9: Financial Independence (FI)

### FI Number Calculation

```
FI Number = Annual Expenses × 25
```

Based on the 4% rule (Trinity Study — 4% withdrawal rate has historically survived 30-year retirements).

| Annual Expenses | FI Number | Monthly Savings Needed (25 years at 7%) |
|----------------|-----------|----------------------------------------|
| $30,000 | $750,000 | $940/month |
| $50,000 | $1,250,000 | $1,567/month |
| $75,000 | $1,875,000 | $2,350/month |
| $100,000 | $2,500,000 | $3,134/month |

### FI Stages

| Stage | Description | What Changes |
|-------|-------------|-------------|
| **Coast FI** | Enough invested that compound growth alone will fund retirement by 65 | Can take lower-paying fulfilling work |
| **Barista FI** | Investments cover most expenses, need small income | Part-time work for insurance/extras |
| **Lean FI** | 25x minimal expenses saved | Can stop working, frugal lifestyle |
| **FI** | 25x comfortable expenses saved | Full financial independence |
| **Fat FI** | 25x generous expenses saved | Independence with luxury |

### FI Tracking Dashboard

```yaml
fi_tracker:
  date: "YYYY-MM-DD"
  annual_expenses: 0
  fi_number: 0  # expenses × 25
  current_invested: 0
  fi_percentage: 0  # invested / fi_number × 100
  monthly_savings: 0
  savings_rate: 0
  years_to_fi: 0  # calculated from savings rate
  coast_fi_number: 0  # what you need now to coast to 65
  coast_fi_reached: false
```

### Savings Rate → Years to FI

| Savings Rate | Years to FI |
|-------------|-------------|
| 10% | 51 years |
| 20% | 37 years |
| 30% | 28 years |
| 40% | 22 years |
| 50% | 17 years |
| 60% | 12.5 years |
| 70% | 8.5 years |
| 80% | 5.5 years |

**The lever**: Cutting expenses is 2x as powerful as earning more (reduces FI number AND increases savings).

### Safe Withdrawal Strategies

| Strategy | Rate | Best For |
|----------|------|----------|
| **Fixed 4%** | 4% of initial portfolio, adjusted for inflation | Simple, traditional |
| **Variable %** | 3-5% based on market conditions | Adapts to market |
| **Guardrails** | 4% base, increase/decrease if portfolio deviates 20% | Balanced |
| **Bucket strategy** | 2 years cash + 5 years bonds + rest stocks | Sequence risk protection |

---

## Phase 10: Estate Planning Essentials

### Documents Everyone Needs

| Document | What It Does | Priority |
|----------|-------------|----------|
| **Will** | Distributes assets, names guardian for children | Critical |
| **Power of Attorney** | Someone manages finances if incapacitated | Critical |
| **Healthcare Directive** | Medical wishes if you can't communicate | Critical |
| **Beneficiary designations** | Override will for 401k, IRA, life insurance | Critical |
| **Trust** (optional) | Avoids probate, privacy, control | Important if assets > $500K |

### Digital Estate Checklist

- [ ] Password manager shared with trusted person
- [ ] List of all financial accounts and institutions
- [ ] Crypto wallet recovery phrases stored securely
- [ ] Social media legacy contacts set
- [ ] Email account recovery instructions
- [ ] Insurance policies documented and locatable
- [ ] Safe deposit box key location documented

---

## Phase 11: Financial Review Cadence

### Weekly (5 minutes)

- Check bank/credit card for unauthorized charges
- Log any large or unusual expenses
- Verify automated transfers went through

### Monthly (30 minutes)

```yaml
monthly_review:
  month: "YYYY-MM"
  income_actual: 0
  expenses_actual: 0
  savings_actual: 0
  savings_rate_actual: 0
  budget_variances:
    over_budget: []
    under_budget: []
  net_worth_change: 0
  debt_paid_this_month: 0
  investments_contributed: 0
  action_items: []
```

### Quarterly (1 hour)

- Update net worth statement
- Review investment allocation (rebalance if > 5% drift)
- Subscription audit
- Insurance coverage check
- Update financial goals progress

### Annually (half day)

- Full financial plan review
- Tax planning for next year
- Insurance shopping/comparison
- Beneficiary designation review
- Will/estate document review
- Set next year's financial goals
- Negotiate bills (insurance, phone, internet, subscriptions)

---

## Financial Scoring Rubric (0-100)

| Dimension | Weight | 0-25 | 50 | 75 | 100 |
|-----------|--------|------|-----|-----|------|
| Emergency fund | 15% | < 1 month | 1-3 months | 3-6 months | 6+ months |
| Debt management | 15% | High-interest debt, no plan | Plan exists | Only low-interest | Debt-free |
| Savings rate | 15% | < 5% | 10-15% | 15-25% | > 25% |
| Investment strategy | 15% | Not investing | Investing but no plan | Diversified + tax-optimized | Full optimization |
| Insurance coverage | 10% | Major gaps | Basic coverage | Solid coverage | Fully optimized |
| Tax optimization | 10% | No tax planning | Using some accounts | Maxing accounts | Full strategy |
| Net worth growth | 10% | Declining | Flat | Growing | Accelerating |
| Estate planning | 10% | Nothing | Basic will | Will + POA + directive | Complete plan |

### Scoring Guide

- **90-100**: Financial mastery — maintain and optimize
- **70-89**: Strong foundation — optimize tax and estate
- **50-69**: Building — focus on savings rate and debt
- **30-49**: Getting started — emergency fund + debt payoff
- **0-29**: Crisis mode — stabilize cash flow, minimum debt payments

---

## Common Mistakes

| Mistake | Why It Hurts | Fix |
|---------|-------------|-----|
| No emergency fund | One crisis = debt spiral | Build $1K starter, then 3 months |
| Lifestyle inflation | Raises never turn into wealth | Save 50%+ of every raise |
| Paying minimums on high-interest debt | Interest compounds against you | Avalanche or snowball method |
| Not investing early | Missing compound growth | Start with $50/month today |
| Timing the market | Miss best days = miss most gains | Dollar-cost average, always |
| Whole life insurance | Expensive, bad returns | Buy term, invest the difference |
| No tax planning | Leaving thousands on the table | Max tax-advantaged accounts |
| Ignoring insurance | One event = financial ruin | Cover the catastrophic risks |
| Emotional spending | Budget-busting | 48-hour rule for purchases > $100 |
| Keeping up with others | Comparison drives overspending | Track YOUR net worth, ignore others |

---

## Edge Cases

### Irregular Income (Freelance / Commission)

- Budget based on lowest 3-month average from past year
- In good months, build buffer to 3 months ahead
- Separate business and personal accounts
- Set aside 25-30% for taxes immediately (estimated payments quarterly)
- Variable expenses flex, fixed expenses stay locked

### Dual Income / Couples

- Decide: fully joint, fully separate, or hybrid (joint for shared + separate for personal)
- Hybrid recommended: joint account for bills/goals + personal "fun money" accounts
- Monthly money meeting — review budget, goals, upcoming expenses together
- Life insurance on BOTH incomes
- Estate planning is critical — both wills, beneficiaries aligned

### High Income ($200K+)

- Max ALL tax-advantaged accounts (401k, backdoor Roth, HSA, mega backdoor if available)
- Donor-advised fund for charitable giving
- Umbrella liability insurance ($1-2M)
- Estate planning with trusts
- Consider tax diversification: pre-tax + Roth + taxable + real estate
- Beware lifestyle creep — savings rate matters more than income

### Fresh Start (Post-Bankruptcy / Major Setback)

- Secured credit card to rebuild credit
- Budget with zero-based budgeting (every dollar assigned)
- Emergency fund is priority #1 (even $500 helps)
- No new debt until existing is managed
- Focus on income growth — skills, certifications, side income

### International / Multi-Currency

- Track in primary currency, note exchange rates for foreign accounts
- Understand tax obligations in BOTH countries (US citizens taxed on worldwide income)
- FBAR filing if foreign accounts > $10K aggregate
- FATCA reporting for foreign financial assets
- Currency hedging for large foreign holdings

---

## Agent Automation

### Daily
- Categorize new transactions
- Flag unusual spending (> 2x category average)
- Check account balances

### Weekly
- Generate spending summary by category
- Compare actual vs budget
- Alert if any category > 90% of monthly budget

### Monthly
- Generate full budget report with variances
- Update net worth tracking
- Calculate savings rate
- Debt payoff progress update
- Investment contribution tracking

### Quarterly
- Net worth trend chart
- FI percentage update
- Insurance review reminder
- Rebalancing check (portfolio drift > 5%)

### Annually
- Full financial health score (0-100)
- Year-over-year net worth comparison
- Tax optimization review
- Estate document review reminder
- Goal setting for next year

---

## File Structure

```
finance/
├── net-worth-YYYY-MM.yaml      # Monthly net worth snapshots
├── budget-YYYY-MM.yaml         # Monthly budgets
├── debt-tracker.yaml           # Debt inventory and payoff progress
├── investment-allocation.yaml  # Current portfolio allocation
├── fi-tracker.yaml             # Financial independence progress
├── annual-expenses.yaml        # Sinking fund calendar
├── insurance-coverage.yaml     # All policies
├── estate-checklist.yaml       # Documents and beneficiaries
└── reviews/
    ├── monthly-YYYY-MM.md      # Monthly review notes
    └── annual-YYYY.md          # Annual review
```

---

## Natural Language Commands

- "What's my net worth?" → Calculate from latest snapshot
- "How's my budget this month?" → Compare actual vs plan
- "When will I be debt-free?" → Calculate based on current payoff rate
- "Am I on track for FI?" → Show FI percentage and years remaining
- "Score my finances" → Run 0-100 scoring rubric
- "What should I do with an extra $500?" → Apply to priority order
- "Review my subscriptions" → List all recurring charges with value scores
- "Tax optimization check" → Review which accounts are maxed
- "How much house can I afford?" → Calculate based on income and debts
- "Compare my spending this month vs last" → Category-by-category comparison
- "Rebalance check" → Compare current allocation to target
- "Set a savings goal" → Create goal with timeline and monthly amount
