---
name: expense-tracker
description: "Just say what you spent — your AI logs it, categorizes it, and tracks it against your budget. No apps, no forms, no friction. Supports natural language like 'spent $45 at Costco' or 'split a $90 dinner with Jake'. 16 auto-categories, monthly budget alerts, weekly and monthly reports. Runs entirely local — your spending data stays on your machine."
version: "1.0.2"
category: finance
tags: [expenses, budget, finance, spending, personal-finance, tracking, reports, money, frugal, budgeting, natural-language, local]
---

# Expense Tracker Skill

Track, categorize, and budget personal expenses through natural conversation. Users text expenses in plain language and the AI logs them, tracks budgets, and generates reports.

## Skill Directory

```
skills/expense-tracker/
├── SKILL.md                    # This file — AI instructions
├── references/
│   ├── categories.json         # Category definitions + keyword matching
│   └── budgets.json            # Monthly budget limits (user-editable)
├── scripts/
│   ├── add-expense.sh          # Add expense to ledger
│   ├── query.sh                # Query/filter expenses
│   └── budget-check.sh         # Check spending vs budget
├── templates/
│   ├── weekly-report.md        # Weekly report template
│   └── monthly-report.md       # Monthly report template
└── expenses/
    └── ledger.json             # Transaction data (auto-created)
```

---

## 1. Parsing Natural Language Expenses

When a user mentions spending money, extract these fields:

| Field | Required | How to Extract |
|-------|----------|----------------|
| **amount** | Yes | Dollar amounts: "$45", "45 dollars", "forty-five bucks", "45.99" |
| **vendor** | Yes | Named entity after "at", "from", "to", or contextual merchant name |
| **category** | Auto | Match vendor/context against `references/categories.json` keywords |
| **date** | Default today | "today", "yesterday", "last Tuesday", "on 2/14", explicit dates |
| **notes** | Optional | Anything extra the user adds — "for the party", "work expense" |

### Parsing Examples

| User Says | amount | vendor | category | date | notes |
|-----------|--------|--------|----------|------|-------|
| "spent $45 at Costco" | 45 | Costco | Groceries | today | |
| "grabbed lunch for $18 at Chipotle yesterday" | 18 | Chipotle | Dining | yesterday | |
| "$120 electric bill" | 120 | Electric company | Utilities | today | |
| "filled up the tank, 55 bucks at Shell" | 55 | Shell | Gas/Transport | today | |
| "Netflix $15.99" | 15.99 | Netflix | Subscriptions | today | |
| "dropped $200 at Target for birthday stuff" | 200 | Target | Shopping | today | birthday stuff |
| "refund from Amazon $35" | -35 | Amazon | Shopping | today | refund |
| "paid rent $2000" | 2000 | Rent/Landlord | Housing | today | |
| "spent $5.50 at starbucks yesterday" | 5.50 | Starbucks | Dining | yesterday | |
| "vet visit for the dog, $280" | 280 | Vet | Pets | today | |
| "car insurance $180" | 180 | Car insurance | Insurance | today | |
| "groceries and some clothes at Target $150" | 150 | Target | Shopping | today | groceries and clothes (ask user to split or pick) |
| "got reimbursed $45 for work lunch" | -45 | Work | Dining | today | reimbursement |

### Ambiguous Categories

When a vendor could match multiple categories (e.g., "Walmart" could be Groceries or Shopping):

1. **Best-guess first**: Pick the most likely category based on context
2. **Confirm with user**: "I logged $85 at Walmart as **Groceries** — is that right, or was this more of a Shopping trip?"
3. **Remember preferences**: If the user corrects, note the preference for future entries

When no category matches at all, use **Miscellaneous** and tell the user: "Logged under Miscellaneous — want me to put this in a specific category?"

---

## 2. Commands

### `/add` — Log an Expense

Log an expense explicitly.

**Usage:** `/add <amount> <vendor> [category] [date] [notes]`

**Implementation:** Run the add-expense script:
```bash
bash skills/expense-tracker/scripts/add-expense.sh <amount> "<category>" "<vendor>" "<date>" "<notes>"
```

**Examples:**
- `/add 45 Costco` → logs $45 at Costco, auto-categorized, today's date
- `/add 18.50 Chipotle Dining yesterday` → $18.50 dining, yesterday
- `/add -35 Amazon Shopping 2026-02-10 "refund for headphones"` → refund

Most of the time, users won't use `/add` — they'll just say "spent $45 at Costco" and you parse it.

### `/spending` — View Spending

Query expenses with optional filters.

**Usage:** `/spending [period] [category]`

**Implementation:** Run the query script:
```bash
bash skills/expense-tracker/scripts/query.sh [--from DATE] [--to DATE] [--category CAT] [--format summary|detail|json]
```

**Examples:**
- `/spending` → current month summary
- `/spending this week` → this week's expenses
- `/spending Dining` → all dining expenses this month
- `/spending February detail` → detailed February breakdown
- "how much have I spent on groceries?" → query with `--category Groceries`
- "what did I spend last week?" → query with appropriate date range

**Format options:**
- `summary` (default) — totals by category
- `detail` — itemized list with all fields
- `json` — raw JSON output

### `/budget` — Budget Status

Check spending against budget limits.

**Usage:** `/budget [month]`

**Implementation:** Run the budget check script:
```bash
bash skills/expense-tracker/scripts/budget-check.sh [YYYY-MM]
```

**Examples:**
- `/budget` → current month budget status
- `/budget 2026-01` → January budget review
- "how's my budget looking?" → run budget check

**Also supports adjusting budgets:**
- "set my dining budget to $400" → update `references/budgets.json` using `jq --arg` (never interpolate user values into jq code directly)
- "what's my grocery budget?" → read from budgets.json

### `/categories` — View/Manage Categories

Show available categories or recategorize expenses.

**Examples:**
- `/categories` → list all categories
- `/categories Dining` → show Dining keywords and recent expenses
- "move expense #12 to Entertainment" → update ledger entry's category

---

## 3. Category Auto-Matching

Use `references/categories.json` to match vendors to categories. The matching algorithm:

1. **Exact keyword match**: Check if vendor name (lowercased) contains any keyword
2. **Partial match**: Check if any keyword is a substring of the vendor name
3. **Context clues**: Use surrounding words — "lunch at" → Dining, "filled up at" → Gas/Transport
4. **Fallback**: Miscellaneous

### Available Categories
Groceries, Dining, Gas/Transport, Subscriptions, Health/Fitness, Entertainment, Shopping, Utilities, Housing, Personal Care, Education, Gifts, Travel, Insurance, Pets, Miscellaneous.

### Priority Order (when multiple match)
1. Most specific keyword wins ("Costco gas" → Gas/Transport over Groceries)
2. Context from user's message
3. User's historical pattern for that vendor
4. Ask the user

---

## 4. Budget Tracking

Budget configuration lives in `references/budgets.json`. The user edits this to set their limits.

### Alert Thresholds

| Threshold | Emoji | Action |
|-----------|-------|--------|
| < 50% | ⚪ | No alert |
| 50–79% | 🟢 | Informational only |
| 80–99% | 🟡 | Proactive warning: "Heads up — Dining is at 85% of your $300 budget" |
| ≥ 100% | 🔴 | Alert: "You've exceeded your Dining budget ($312 / $300)" |

### When to Alert

- **On every expense**: After logging, silently check the category budget. Only speak up at 80%+ threshold.
- **On `/budget` command**: Show full breakdown with all categories.
- **Weekly**: If generating a weekly report, include budget status section.

### Proactive Budget Warnings

After logging an expense that pushes a category past 80%, add a note:

> ✅ Expense #24: $45.00 at Olive Garden (Dining) on 2026-02-17
> ⚠️ Heads up — Dining is now at $275 / $300 (92%) for February.

After exceeding 100%:

> ✅ Expense #25: $38.00 at Thai Palace (Dining) on 2026-02-19
> 🔴 Dining has exceeded your February budget: $313 / $300 (104%)

---

## 5. Report Generation

### Weekly Report

Use `templates/weekly-report.md` as a guide. Generate when the user asks "weekly report", "how'd I do this week", etc.

**To generate**, run query.sh for the week's date range, then format the results using the template structure:

```bash
# Get this week's data
bash skills/expense-tracker/scripts/query.sh --from 2026-02-10 --to 2026-02-16 --format json

# Get last week for comparison
bash skills/expense-tracker/scripts/query.sh --from 2026-02-03 --to 2026-02-09 --format json

# Get budget status
bash skills/expense-tracker/scripts/budget-check.sh
```

Include: category breakdown, top expenses, budget status, week-over-week trend.

### Monthly Report

Use `templates/monthly-report.md` as a guide. Generate for "monthly report", "how'd February go", end-of-month reviews.

```bash
# Current month data
bash skills/expense-tracker/scripts/query.sh --from 2026-02-01 --to 2026-02-28 --format json

# Previous month for comparison
bash skills/expense-tracker/scripts/query.sh --from 2026-01-01 --to 2026-01-31 --format json

# Budget check
bash skills/expense-tracker/scripts/budget-check.sh 2026-02
```

Include: full category breakdown, top expenses, weekly breakdown, month-over-month comparison, savings rate (if income is set in budgets.json).

---

## 6. Edge Cases

### Refunds
- Detect words: "refund", "returned", "got back", "credit", "reimbursement"
- Store as **negative amount**: `add-expense.sh -35 "Shopping" "Amazon" "2026-02-15" "refund"`
- Refunds reduce the category total in budget calculations

### Splitting Expenses
- "Split $80 dinner with Sarah" → log $40 (user's half)
- "Split 3 ways: $120 at the bar" → log $40
- Confirm the split: "Logging your share: $40 at the bar (Dining). That right?"

### Recurring Expenses
- This skill doesn't auto-schedule recurring expenses
- When the user says "Netflix again" or "monthly gym payment", treat as a new entry
- The AI can note: "Want me to remind you about this next month?" (but don't auto-create)

### Multi-Item Purchases
- "Spent $150 at Target on groceries and clothes" → Ask user whether to log as one entry or split
- If split: create separate entries per category
- If single: pick the dominant category or ask which one
- "Bought lunch and a coffee at Panera, $22" → single Dining entry is fine (same category)

### Multi-Currency (Optional)
- If the user mentions foreign currency: "spent €50 in Paris"
- Log the original amount and note the currency: `add-expense.sh 55 "Travel" "Paris restaurant" "2026-02-15" "€50 EUR"`
- Convert to USD for budget purposes (ask user for rate or use approximate)
- Default behavior: assume USD unless told otherwise

### Corrections
- "Actually that Costco trip was $52, not $45" → Find the recent Costco entry, update amount
- "Delete expense #12" → Remove from ledger using `jq --argjson id 12 'map(select(.id != $id))'` — always use --arg/--argjson, never interpolate IDs into filter strings
- "Move #12 to Dining" → Update category field

### Zero-Expense Days
- Don't alert on no-spend days unless asked
- In reports, show $0 days as positive (savings!)

---

## 7. Conversational Patterns

The AI should handle these naturally without requiring commands:

| User Says | AI Action |
|-----------|-----------|
| "spent $45 at Costco" | Parse → add expense → confirm → check budget |
| "how much have I spent this month?" | Run query.sh for current month → format summary |
| "am I over budget?" | Run budget-check.sh → report status |
| "weekly report" | Generate weekly report from template |
| "what did I spend on food?" | Query Groceries + Dining categories |
| "I got a $20 refund from Amazon" | Log negative amount → confirm |
| "split a $90 dinner with Jake" | Calculate half → log $45 → confirm |
| "that last one should be Entertainment, not Shopping" | Update most recent entry's category |
| "set grocery budget to $700" | Update budgets.json |
| "how much is left in my dining budget?" | Calculate: limit - spent this month |
| "show me everything from last week" | Query with date range, detail format |
| "what's my biggest expense this month?" | Query + sort by amount |
| "cancel that last expense" | Delete most recent ledger entry |
| "spent $5.50 at starbucks yesterday" | Parse date as yesterday → add expense |
| "vet bill was $280" | Log as Pets category |
| "car insurance came out, $180" | Log as Insurance category |
| "I spent like 50 bucks at Target" | Log $50, confirm amount approximation |
| "got reimbursed $45 from work" | Log as negative (reimbursement) |
| "how much did I spend on food this month?" | Query Groceries + Dining combined |
| "compare this month to last month" | Generate month-over-month comparison |

---

## 8. Example Full Interaction

```
User: spent $45 at Costco
AI: ✅ Expense #1: $45.00 at Costco (Groceries) on 2026-02-17

User: grabbed lunch at Chipotle for $12.50
AI: ✅ Expense #2: $12.50 at Chipotle (Dining) on 2026-02-17

User: $150 at Target yesterday
AI: I logged $150 at Target as **Shopping** — was this groceries or more of a general shopping trip?
User: shopping
AI: ✅ Expense #3: $150.00 at Target (Shopping) on 2026-02-16

User: how's my budget looking?
AI:
=== Budget Check: 2026-02 ===
  🟢 OK    Groceries        $345     / $600   (58%)
  🟡 WARN  Dining           $248     / $300   (83%)
  🟢 OK    Shopping         $280     / $300   (93%)
  ⚪ LOW   Gas/Transport    $85      / $250   (34%)
  ...
  TOTAL: $1,245.00 / $4,950 (25%)

⚠️ Heads up — Dining is at 83% and Shopping is at 93% of your February budget.

User: I got a refund from Amazon for $35
AI: ✅ Refund #4: $35.00 from Amazon (Shopping) on 2026-02-17
   Shopping is now at $245 / $300 (82%) for February.

User: weekly report
AI: [generates formatted weekly report from template]

User: set my dining budget to $400
AI: Updated Dining budget: $300 → $400 for this month. You're now at $248 / $400 (62%) — much more breathing room! 🟢
```

---

## 9. Data Format Reference

### Ledger Entry (expenses/ledger.json)
```json
[
  {
    "id": 1,
    "amount": 45.00,
    "category": "Groceries",
    "vendor": "Costco",
    "date": "2026-02-17",
    "notes": "",
    "created_at": "2026-02-17T23:32:00Z"
  },
  {
    "id": 2,
    "amount": -35.00,
    "category": "Shopping",
    "vendor": "Amazon",
    "date": "2026-02-17",
    "notes": "refund for headphones",
    "created_at": "2026-02-17T23:45:00Z"
  }
]
```

### Key Rules
- **IDs**: Incrementing integers, never reused
- **Amounts**: Always numbers. Positive = expense, negative = refund
- **Dates**: ISO 8601 `YYYY-MM-DD`
- **Categories**: Must match a name in `references/categories.json`
- **created_at**: UTC timestamp of when the entry was created

---

## 10. Script Reference

All scripts are in `skills/expense-tracker/scripts/` and must be run with `bash`:

```bash
# Add an expense
bash skills/expense-tracker/scripts/add-expense.sh 45 "Groceries" "Costco" "2026-02-17" "weekly groceries"

# Query expenses
bash skills/expense-tracker/scripts/query.sh --from 2026-02-01 --to 2026-02-28 --category Dining --format summary

# Check budget
bash skills/expense-tracker/scripts/budget-check.sh 2026-02
```

### Script Arguments

**add-expense.sh** `<amount> <category> <vendor> [date] [notes]`
- `amount` — number (negative for refunds)
- `category` — category name from categories.json
- `vendor` — merchant name
- `date` — YYYY-MM-DD (default: today)
- `notes` — optional description

**query.sh** `[--from DATE] [--to DATE] [--category CAT] [--vendor TEXT] [--format FMT]`
- `--from` — start date (inclusive)
- `--to` — end date (inclusive)
- `--category` — filter by category name
- `--vendor` — filter by vendor (partial match, case-insensitive)
- `--format` — `summary` (default), `detail`, or `json`

**budget-check.sh** `[YYYY-MM]`
- Optional month argument (default: current month)
- Exit code 0 = all OK, exit code 1 = at least one category ≥ 80%
