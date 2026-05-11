---
name: payroll-gl-reconciliation
description: >
  Reconcile payroll processor reports (Gusto, ADP, Paychex, Rippling) to general ledger journal entries
  in QuickBooks Online, Xero, or other accounting software. Automates journal entry creation from payroll
  summaries, validates wage/tax/benefit allocations to correct GL accounts, detects variances, and flags
  discrepancies before month-end close. Produces audit-ready reconciliation workpapers.
  Use when: reconciling payroll registers to GL, mapping payroll processor exports to chart of accounts,
  creating payroll journal entries, validating employee benefit deductions, or preparing payroll workpapers.
  NOT for: payroll processing or running payroll (use your payroll platform), tax filing (W-2, 941),
  on-chain payroll (use on-chain-payroll), HR onboarding, or benefits enrollment.
version: 1.0.0
author: PrecisionLedger
tags:
  - payroll
  - reconciliation
  - accounting
  - journal-entries
  - gl
  - quickbooks
  - month-end
  - compliance
---

# Payroll GL Reconciliation Skill

Reconcile payroll processor reports to general ledger journal entries. Automate journal entry creation, validate account mappings, detect variances, and produce audit-ready workpapers — all from raw payroll exports.

---

## When to Use This Skill

**Trigger phrases:**
- "Reconcile payroll to the GL"
- "Create journal entries for payroll"
- "Payroll didn't hit the right accounts"
- "Map Gusto export to QuickBooks"
- "Check payroll entries for month-end close"
- "Payroll reconciliation workpaper"
- "Validate payroll tax liabilities"

**NOT for:**
- Running or processing payroll — use Gusto, ADP, or Paychex directly
- Filing 941/940/W-2 — use a tax compliance workflow
- On-chain payroll disbursement — use on-chain-payroll skill (PTIN-backed, not here)
- Benefits enrollment or HR workflows — out of scope
- Actual QuickBooks data entry — use `qbo-automation` for live API writes

---

## Payroll GL Reconciliation Overview

Every payroll run produces three categories of GL impact:

```
1. GROSS WAGES EXPENSE (Debit)
   ├── Regular wages
   ├── Overtime wages
   ├── Bonus / commissions
   └── PTO / sick pay

2. EMPLOYER PAYROLL TAXES EXPENSE (Debit)
   ├── Employer FICA (Social Security 6.2%)
   ├── Employer Medicare (1.45%)
   ├── Federal Unemployment (FUTA 0.6%)
   └── State Unemployment (SUTA — rate varies by state)

3. LIABILITY ACCOUNTS (Credit)
   ├── Net pay payable (cash out → employee bank accounts)
   ├── Employee FICA withheld
   ├── Employee Medicare withheld
   ├── Federal income tax withheld
   ├── State income tax withheld
   ├── Employee benefits deductions (health, dental, 401k)
   └── Employer benefits contributions (401k match, HSA)
```

**The fundamental check:**
```
Total Debits = Gross Wages + Employer Taxes + Employer Benefits
Total Credits = Net Pay + All Withholdings + All Liabilities

Debits must equal Credits. If not, there's an error.
```

---

## Standard Chart of Accounts Mapping

### Expense Accounts (Debits)

| Payroll Line Item | GL Account | Account Type |
|---|---|---|
| Regular wages | 6100 – Salaries & Wages Expense | Expense |
| Overtime pay | 6100 – Salaries & Wages Expense | Expense |
| Bonus / commissions | 6110 – Bonus Expense | Expense |
| Employer FICA | 6200 – Payroll Tax Expense | Expense |
| Employer Medicare | 6200 – Payroll Tax Expense | Expense |
| FUTA | 6210 – Federal Unemployment Tax Expense | Expense |
| SUTA | 6220 – State Unemployment Tax Expense | Expense |
| Employer 401(k) match | 6300 – Employee Benefits Expense | Expense |
| Employer health premium | 6310 – Health Insurance Expense | Expense |
| Employer HSA contribution | 6320 – HSA Contribution Expense | Expense |

### Liability Accounts (Credits)

| Payroll Line Item | GL Account | Account Type |
|---|---|---|
| Net pay to employees | 2000 – Net Payroll Payable | Current Liability |
| Employee FICA withheld | 2100 – FICA Payable | Current Liability |
| Employee Medicare withheld | 2110 – Medicare Payable | Current Liability |
| Federal income tax withheld | 2120 – Federal Withholding Payable | Current Liability |
| State income tax withheld | 2130 – State Withholding Payable | Current Liability |
| Employee 401(k) deduction | 2200 – 401(k) Payable | Current Liability |
| Employee health deduction | 2210 – Health Insurance Payable | Current Liability |
| Employer FICA (matching) | 2100 – FICA Payable | Current Liability |
| Employer Medicare (matching) | 2110 – Medicare Payable | Current Liability |

> **Note:** When taxes are remitted to the IRS/state, debit the liability account and credit cash.

---

## Department / Cost Center Allocation

For multi-department businesses, allocate wages by department:

```
6100 – Wages Expense (Engineering)    [Debit]    $45,000
6100 – Wages Expense (Sales)          [Debit]    $30,000
6100 – Wages Expense (G&A)            [Debit]    $25,000
```

**Allocation methods:**
1. **Direct mapping** — each employee assigned a department in payroll system
2. **Headcount ratio** — allocate shared costs proportionally
3. **Time tracking** — allocate based on logged hours per project/department
4. **Revenue ratio** — allocate shared overhead by revenue contribution

---

## Processor-Specific Export Formats

### Gusto

Gusto provides a "Payroll Journal" CSV export under Reports → Journal Entries.

```python
import csv
from dataclasses import dataclass
from typing import List

@dataclass
class GustoPayrollLine:
    pay_date: str
    employee_name: str
    department: str
    gross_wages: float
    employee_fica: float
    employee_medicare: float
    federal_withholding: float
    state_withholding: float
    employee_401k: float
    employee_health: float
    net_pay: float
    employer_fica: float
    employer_medicare: float
    futa: float
    suta: float
    employer_401k: float
    employer_health: float

def parse_gusto_export(filepath: str) -> List[GustoPayrollLine]:
    """
    Parse Gusto payroll journal CSV into structured records.
    
    Gusto columns (may vary by plan):
    'Check Date', 'Employee Name', 'Department', 'Gross Pay',
    'Employee OASDI', 'Employee Medicare', 'Federal WH', 'State WH',
    '401k Employee', 'Medical Employee', 'Net Pay',
    'Employer OASDI', 'Employer Medicare', 'FUTA', 'SUTA',
    '401k Employer', 'Medical Employer'
    """
    lines = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lines.append(GustoPayrollLine(
                pay_date=row.get('Check Date', ''),
                employee_name=row.get('Employee Name', ''),
                department=row.get('Department', 'General'),
                gross_wages=float(row.get('Gross Pay', 0) or 0),
                employee_fica=float(row.get('Employee OASDI', 0) or 0),
                employee_medicare=float(row.get('Employee Medicare', 0) or 0),
                federal_withholding=float(row.get('Federal WH', 0) or 0),
                state_withholding=float(row.get('State WH', 0) or 0),
                employee_401k=float(row.get('401k Employee', 0) or 0),
                employee_health=float(row.get('Medical Employee', 0) or 0),
                net_pay=float(row.get('Net Pay', 0) or 0),
                employer_fica=float(row.get('Employer OASDI', 0) or 0),
                employer_medicare=float(row.get('Employer Medicare', 0) or 0),
                futa=float(row.get('FUTA', 0) or 0),
                suta=float(row.get('SUTA', 0) or 0),
                employer_401k=float(row.get('401k Employer', 0) or 0),
                employer_health=float(row.get('Medical Employer', 0) or 0),
            ))
    return lines
```

### ADP

ADP exports vary by product (RUN, Workforce Now, TotalSource). Request the "Payroll Register" + "Tax Summary" reports.

```python
def parse_adp_register(filepath: str) -> dict:
    """
    Parse ADP payroll register. ADP uses fixed-width or pipe-delimited format.
    
    Key ADP column names:
    'Employee Name', 'Reg Hours', 'Reg Earn', 'OT Earn', 'Gross',
    'FIT', 'SIT', 'SS EE', 'MED EE', 'SS ER', 'MED ER',
    '401K EE', '401K ER', 'Medical EE', 'Medical ER',
    'Net Pay', 'FUTA', 'SUI'
    """
    # ADP format detection
    with open(filepath, 'r') as f:
        header = f.readline()
    
    delimiter = '|' if '|' in header else ','
    # ... parse with detected delimiter
    pass
```

### Paychex

```python
def parse_paychex_summary(filepath: str) -> dict:
    """
    Paychex Payroll Summary Report.
    Download from: My Paychex → Reports → Payroll Summary
    
    Key sections in Paychex report:
    - 'Earnings' block: Regular, Overtime, Bonus
    - 'Employee Deductions' block: FIT, SIT, FICA, Medicare, Benefits
    - 'Employer Taxes' block: FUTA, SUTA, FICA ER, Medicare ER
    - 'Employer Benefits': 401k Match, Health ER
    - 'Check Summary': Net Pay total
    """
    pass
```

---

## Journal Entry Builder

```python
from dataclasses import dataclass, field
from typing import List
from decimal import Decimal, ROUND_HALF_UP

@dataclass
class JournalLine:
    account_number: str
    account_name: str
    debit: Decimal = Decimal('0')
    credit: Decimal = Decimal('0')
    memo: str = ''
    department: str = ''

@dataclass
class JournalEntry:
    date: str
    reference: str
    description: str
    lines: List[JournalLine] = field(default_factory=list)
    
    @property
    def total_debits(self) -> Decimal:
        return sum(line.debit for line in self.lines)
    
    @property
    def total_credits(self) -> Decimal:
        return sum(line.credit for line in self.lines)
    
    @property
    def is_balanced(self) -> bool:
        return abs(self.total_debits - self.total_credits) < Decimal('0.01')
    
    def validate(self) -> list:
        """Return list of validation errors."""
        errors = []
        if not self.is_balanced:
            errors.append(
                f"UNBALANCED: Debits ${self.total_debits} ≠ Credits ${self.total_credits} "
                f"(difference: ${abs(self.total_debits - self.total_credits)})"
            )
        if not self.lines:
            errors.append("Journal entry has no lines")
        for i, line in enumerate(self.lines):
            if line.debit > 0 and line.credit > 0:
                errors.append(f"Line {i+1} has both debit and credit — split into two lines")
        return errors


def build_payroll_journal_entry(
    lines: List[GustoPayrollLine],
    pay_date: str,
    pay_period: str,
    account_map: dict = None,
) -> JournalEntry:
    """
    Build a complete payroll journal entry from payroll data.
    
    Args:
        lines: Parsed payroll lines (one per employee or department total)
        pay_date: Date of journal entry (e.g., "2026-03-15")
        pay_period: Human-readable period (e.g., "March 1-15, 2026")
        account_map: Optional override for default GL account numbers
    
    Returns:
        JournalEntry with all debits and credits, ready for posting
    """
    
    # Default account map (customize to client's COA)
    accounts = {
        'wages_expense': ('6100', 'Salaries & Wages Expense'),
        'bonus_expense': ('6110', 'Bonus Expense'),
        'payroll_tax_expense': ('6200', 'Payroll Tax Expense'),
        'futa_expense': ('6210', 'Federal Unemployment Tax Expense'),
        'suta_expense': ('6220', 'State Unemployment Tax Expense'),
        'benefits_expense': ('6300', 'Employee Benefits Expense'),
        'health_expense': ('6310', 'Health Insurance Expense'),
        'net_pay_payable': ('2000', 'Net Payroll Payable'),
        'fica_payable': ('2100', 'FICA / SS Payable'),
        'medicare_payable': ('2110', 'Medicare Payable'),
        'federal_wh_payable': ('2120', 'Federal Withholding Payable'),
        'state_wh_payable': ('2130', 'State Withholding Payable'),
        'retirement_payable': ('2200', '401(k) Payable'),
        'health_payable': ('2210', 'Health Insurance Payable'),
    }
    if account_map:
        accounts.update(account_map)
    
    # Aggregate totals
    totals = {
        'gross_wages': Decimal('0'),
        'employer_fica': Decimal('0'),
        'employer_medicare': Decimal('0'),
        'futa': Decimal('0'),
        'suta': Decimal('0'),
        'employer_401k': Decimal('0'),
        'employer_health': Decimal('0'),
        'net_pay': Decimal('0'),
        'employee_fica': Decimal('0'),
        'employee_medicare': Decimal('0'),
        'federal_wh': Decimal('0'),
        'state_wh': Decimal('0'),
        'employee_401k': Decimal('0'),
        'employee_health': Decimal('0'),
    }
    
    for line in lines:
        totals['gross_wages'] += Decimal(str(line.gross_wages))
        totals['employer_fica'] += Decimal(str(line.employer_fica))
        totals['employer_medicare'] += Decimal(str(line.employer_medicare))
        totals['futa'] += Decimal(str(line.futa))
        totals['suta'] += Decimal(str(line.suta))
        totals['employer_401k'] += Decimal(str(line.employer_401k))
        totals['employer_health'] += Decimal(str(line.employer_health))
        totals['net_pay'] += Decimal(str(line.net_pay))
        totals['employee_fica'] += Decimal(str(line.employee_fica))
        totals['employee_medicare'] += Decimal(str(line.employee_medicare))
        totals['federal_wh'] += Decimal(str(line.federal_withholding))
        totals['state_wh'] += Decimal(str(line.state_withholding))
        totals['employee_401k'] += Decimal(str(line.employee_401k))
        totals['employee_health'] += Decimal(str(line.employee_health))
    
    je = JournalEntry(
        date=pay_date,
        reference=f"PR-{pay_date.replace('-', '')}",
        description=f"Payroll — {pay_period}",
        lines=[]
    )
    
    def add_debit(key: str, amount: Decimal, memo: str = ''):
        if amount > 0:
            num, name = accounts[key]
            je.lines.append(JournalLine(
                account_number=num, account_name=name,
                debit=amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                memo=memo or je.description
            ))
    
    def add_credit(key: str, amount: Decimal, memo: str = ''):
        if amount > 0:
            num, name = accounts[key]
            je.lines.append(JournalLine(
                account_number=num, account_name=name,
                credit=amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                memo=memo or je.description
            ))
    
    # DEBITS (expenses)
    add_debit('wages_expense', totals['gross_wages'], 'Gross wages')
    add_debit('payroll_tax_expense', totals['employer_fica'] + totals['employer_medicare'], 'Employer FICA + Medicare')
    add_debit('futa_expense', totals['futa'], 'Federal unemployment tax')
    add_debit('suta_expense', totals['suta'], 'State unemployment tax')
    add_debit('benefits_expense', totals['employer_401k'], 'Employer 401(k) match')
    add_debit('health_expense', totals['employer_health'], 'Employer health premium')
    
    # CREDITS (liabilities)
    add_credit('net_pay_payable', totals['net_pay'], 'Net pay to employees')
    add_credit('fica_payable', totals['employee_fica'] + totals['employer_fica'], 'FICA SS payable (EE + ER)')
    add_credit('medicare_payable', totals['employee_medicare'] + totals['employer_medicare'], 'Medicare payable (EE + ER)')
    add_credit('federal_wh_payable', totals['federal_wh'], 'Federal income tax withheld')
    add_credit('state_wh_payable', totals['state_wh'], 'State income tax withheld')
    add_credit('retirement_payable', totals['employee_401k'] + totals['employer_401k'], '401(k) payable (EE + ER)')
    add_credit('health_payable', totals['employee_health'] + totals['employer_health'], 'Health ins payable (EE + ER)')
    
    return je
```

---

## Variance Detection & Reconciliation Checks

```python
def reconcile_payroll_to_gl(
    payroll_je: JournalEntry,
    gl_actual: dict,
    tolerance_usd: float = 0.10
) -> dict:
    """
    Compare expected journal entry (from payroll export) vs actual GL entries.
    
    Args:
        payroll_je: Journal entry built from payroll processor data
        gl_actual: Dict of {account_number: actual_amount} from GL export
        tolerance_usd: Acceptable rounding variance (default $0.10)
    
    Returns:
        Reconciliation result with variances and pass/fail flags
    """
    variances = []
    
    for line in payroll_je.lines:
        expected = float(line.debit or line.credit)
        actual = gl_actual.get(line.account_number, 0)
        diff = abs(expected - actual)
        
        if diff > tolerance_usd:
            variances.append({
                'account': f"{line.account_number} – {line.account_name}",
                'expected': expected,
                'actual': actual,
                'variance': actual - expected,
                'variance_pct': (actual - expected) / expected * 100 if expected else None,
                'flag': 'MATERIAL' if diff > 100 else 'MINOR'
            })
    
    return {
        'reconciled': len(variances) == 0,
        'material_variances': [v for v in variances if v['flag'] == 'MATERIAL'],
        'minor_variances': [v for v in variances if v['flag'] == 'MINOR'],
        'total_variance_usd': sum(v['variance'] for v in variances),
        'action_required': len([v for v in variances if v['flag'] == 'MATERIAL']) > 0
    }


def common_variance_causes(account: str, variance: float) -> str:
    """Suggest likely cause for common payroll variances."""
    causes = {
        'net_pay': [
            "Mid-period employee start/termination not reflected",
            "Manual check or off-cycle payment missing from register",
            "Direct deposit reversal or reissue",
        ],
        'fica': [
            "SS wage base hit ($168,600 for 2024) — employee no longer subject",
            "New hire mid-period: partial period calculation",
            "Prior-period correction posted in current period",
        ],
        'futa': [
            "FUTA wage base hit ($7,000) for one or more employees",
            "FUTA credit reduction for states with outstanding loans",
        ],
        'suta': [
            "State-specific taxable wage base reached",
            "Rate change effective mid-year",
        ],
        '401k': [
            "Employee changed contribution % mid-period",
            "Annual contribution limit reached ($23,000 for 2024)",
            "Employer match formula mismatch",
        ],
    }
    return causes.get(account, ["Review payroll register vs GL detail for this account"])
```

---

## Workpaper Output Format

### Reconciliation Workpaper (Markdown)

```python
def generate_workpaper(
    je: JournalEntry,
    recon_result: dict,
    processor: str,
    client_name: str
) -> str:
    """Generate audit-ready reconciliation workpaper in markdown."""
    
    balanced_status = "✅ BALANCED" if je.is_balanced else "❌ UNBALANCED"
    recon_status = "✅ RECONCILED" if recon_result['reconciled'] else "⚠️ VARIANCES FOUND"
    
    lines_table = "\n".join([
        f"| {l.account_number} | {l.account_name} | "
        f"${l.debit:,.2f} | ${l.credit:,.2f} | {l.memo} |"
        for l in je.lines
    ])
    
    return f"""
# Payroll GL Reconciliation Workpaper
**Client:** {client_name}
**Pay Date:** {je.date}
**Period:** {je.description}
**Payroll Processor:** {processor}
**Prepared by:** Sam Ledger / PrecisionLedger
**Date Prepared:** {datetime.today().strftime('%Y-%m-%d')}

---

## Journal Entry — {balanced_status}

| Account # | Account Name | Debit | Credit | Memo |
|-----------|-------------|-------|--------|------|
{lines_table}
| | **TOTALS** | **${je.total_debits:,.2f}** | **${je.total_credits:,.2f}** | |

---

## GL Reconciliation — {recon_status}

{'**No material variances found. All accounts reconcile within tolerance.**' 
 if recon_result['reconciled'] 
 else f"**Material Variances: {len(recon_result['material_variances'])} accounts require investigation.**"}

{_format_variances(recon_result['material_variances'], 'MATERIAL VARIANCES')}
{_format_variances(recon_result['minor_variances'], 'MINOR VARIANCES (within $100)')}

---

## Sign-Off

- [ ] Journal entry reviewed for accuracy
- [ ] GL accounts agree to payroll register totals
- [ ] All variances investigated and resolved
- [ ] Journal entry posted in accounting system
- [ ] Payroll register filed in client workpaper folder

**Reviewer:** _________________ **Date:** _________________
"""
```

---

## Step-by-Step Workflow

### Monthly Payroll Close Checklist

```
For each payroll run in the period:

□ 1. EXPORT from payroll processor
     - Gusto: Reports → Journal Entries → CSV
     - ADP: Reports → Payroll Register + Tax Summary
     - Paychex: My Paychex → Reports → Payroll Summary

□ 2. PARSE the export
     - Run through appropriate parser function above
     - Verify employee count and period match expectations

□ 3. BUILD journal entry
     - Use build_payroll_journal_entry()
     - Confirm balanced (debits = credits)
     - Map to client's specific chart of accounts

□ 4. COMPARE to GL
     - Export actual GL entries for payroll accounts
     - Run reconcile_payroll_to_gl()
     - Investigate any variance > $100

□ 5. DOCUMENT variances
     - Root-cause each material variance
     - Prepare adjusting entries if needed
     - Note minor variances with explanation

□ 6. GENERATE workpaper
     - Run generate_workpaper()
     - Save as PDF in client workpaper folder
     - Include original payroll register as support

□ 7. POST to accounting system
     - Via QBO API (use qbo-automation skill) or manual entry
     - Confirm posting with journal entry reference number

□ 8. VERIFY tax liability balances
     - FICA Payable balance = this period + any prior unpaid
     - 941 semi-weekly vs monthly deposit schedule
     - State withholding deposit due dates by state
```

---

## Tax Deposit Schedule Reference

| Tax Type | Federal Deposit Schedule | 2026 Rates |
|---|---|---|
| Federal income tax withheld | Semi-weekly or monthly* | Varies per W-4 |
| Employee FICA (SS) | Same as FIT | 6.2% (up to $176,100 wage base) |
| Employer FICA | Same as FIT | 6.2% |
| Employee Medicare | Same as FIT | 1.45% (+ 0.9% over $200k) |
| Employer Medicare | Same as FIT | 1.45% |
| FUTA | Quarterly if liability > $500 | 0.6% (up to $7,000 wage base) |
| SUTA | Varies by state | Varies (avg ~2.7%) |

*Semi-weekly: payroll Wednesday/Thursday → deposit by following Wednesday; payroll Fri/Sat/Sun/Mon/Tue → deposit by following Friday
*Monthly: deposit by 15th of following month (if prior year tax liability < $50,000)

---

## Integration Points

- **`qbo-automation`** — post journal entries via QBO API after reconciliation
- **`financial-close-checklist`** — payroll recon is a required step in monthly close
- **`compliance-monitor`** — track 941 and state tax deposit deadlines
- **`crypto-tax-agent`** — if employee equity/token compensation involved
- **`bank-reconciliation-agent`** — confirm net payroll matches bank ACH outflow

---

## Example: End-to-End Reconciliation

**Input:** Gusto export, 15 employees, pay period March 1-15, 2026

```
Sam receives: gusto_payroll_2026-03-15.csv

Step 1: parse_gusto_export('gusto_payroll_2026-03-15.csv')
  → 15 employee records parsed
  → Total gross wages: $87,450.00

Step 2: build_payroll_journal_entry(lines, '2026-03-15', 'March 1-15, 2026')
  → Journal Entry PR-20260315
  → Total debits: $101,247.83
  → Total credits: $101,247.83
  → Status: BALANCED ✅

Step 3: reconcile_payroll_to_gl(je, qbo_gl_extract)
  → Account 6100 Wages: Expected $87,450 | Actual $87,450 ✅
  → Account 2100 FICA: Expected $10,842.90 | Actual $10,842.90 ✅
  → Account 2000 Net Pay: Expected $62,114.50 | Actual $62,190.00 ⚠️
    Variance: +$75.50 → Investigate (likely off-cycle check not in register)

Step 4: generate_workpaper(...)
  → Saved: workpapers/PR-20260315-recon.md
  → 1 minor variance flagged for review
  → All major accounts reconcile within tolerance
```

---

## Common Errors & Fixes

| Error | Likely Cause | Fix |
|---|---|---|
| JE doesn't balance | Rounding on individual lines | Use Decimal, not float |
| FICA payable too low | SS wage base hit for high earners | Check individual wage bases |
| Net pay variance | Off-cycle check or reversal | Search bank feed for extra ACH |
| Benefits mismatch | Mid-period enrollment change | Compare to benefits carrier invoice |
| SUTA variance | Rate update not in system | Confirm current year SUTA rate |
| Missing department | Employee dept not set in payroll | Default to 'General', flag for setup |
