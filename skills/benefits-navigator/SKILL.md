---
name: benefits-navigator
description: >-
  Comprehensive guide to every major US government assistance program: SNAP, Medicaid, unemployment, LIHEAP, TANF, WIC, Section 8, Lifeline, SSDI, SSI, and more. Covers eligibility, application process, processing times, and approval tips for each program.
metadata:
  category: money
  tagline: >-
    Every government program you might qualify for and how to actually get approved. SNAP, Medicaid, unemployment, LIHEAP, TANF, and more.
  display_name: "Benefits Navigator"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-18"
  openclaw:
    requires:
      tools: [browser, calendar, filesystem]
    install: "npx clawhub install howtousehumans/benefits-navigator"
---

# Benefits Navigator

These programs exist for exactly your situation. You paid into this system through taxes. Using it is not failure — it is what the safety net is for. Billions of dollars in government benefits go unclaimed every year because people don't know they qualify, feel too proud to apply, or get discouraged by the paperwork. This skill walks through every major US assistance program: who qualifies, how to apply, how long it takes, and how to avoid the common reasons applications get denied.

Start at benefits.gov — it has a screening tool that checks eligibility across all federal programs at once. Then use this guide to understand each program and navigate the application process.

```agent-adaptation
# Localization required — this skill is entirely US-specific.
# Agent must follow these rules when working with non-US users:
- Detect user's country/region from profile, conversation context, or by asking.
- If non-US: this skill cannot be used as-is. Research and substitute the
  country's equivalent programs before proceeding. Examples:
  - SNAP → Universal Credit/food bank referrals (UK), SNAP has no direct equivalent
    in most countries — research local food assistance programs
  - Medicaid → NHS (UK), Medicare/Centrelink (Australia), provincial health (Canada),
    GKV/Krankenkasse (Germany), Sécurité Sociale (France)
  - Unemployment insurance → JobSeeker's Allowance (UK), Arbeitslosengeld I (Germany),
    Employment Insurance (Canada), JobSeeker Payment (Australia)
  - LIHEAP → Warm Home Discount/Winter Fuel Payment (UK), provincial energy programs (Canada)
  - TANF → Child Benefit/Tax Credits (UK), Kindergeld + Bürgergeld (Germany)
  - Section 8 / HCV → social housing waiting lists (most countries have different systems)
  - SSDI/SSI → Personal Independence Payment/DLA (UK), NDIS (Australia), CPP Disability (Canada)
  - EITC → Working Tax Credit (UK), WFTC equivalents by country
- Always cite the local program sources you use.
- Always warn the user: "This step references [US program] — I have substituted
  [local equivalent], but verify eligibility and application process for your situation."
- If unsure of jurisdiction: ASK the user for their country/region before proceeding.
```

## Sources & Verification

- Federal Poverty Level guidelines: HHS ASPE, "Poverty Guidelines" ([aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines](https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines))
- SNAP program: USDA FNS ([fns.usda.gov/snap](https://www.fns.usda.gov/snap/supplemental-nutrition-assistance-program))
- Medicaid eligibility by state: Kaiser Family Foundation ([kff.org/medicaid/](https://www.kff.org/medicaid/))
- ACA marketplace: [healthcare.gov](https://www.healthcare.gov/) — verified active as of March 2026
- Unemployment insurance by state: CareerOneStop (DOL-sponsored) ([careeronestop.org](https://www.careeronestop.org/LocalHelp/UnemploymentBenefits/unemployment-benefits.aspx))
- LIHEAP: ACF Office of Community Services ([acf.hhs.gov/ocs/programs/liheap](https://www.acf.hhs.gov/ocs/programs/liheap))
- TANF program: ACF Office of Family Assistance ([acf.hhs.gov/ofa/programs/tanf](https://www.acf.hhs.gov/ofa/programs/tanf))
- WIC program: USDA FNS ([fns.usda.gov/wic](https://www.fns.usda.gov/wic))
- Section 8 / HCV: HUD ([hud.gov/topics/housing_choice_voucher_program_section_8](https://www.hud.gov/topics/housing_choice_voucher_program_section_8))
- SSDI/SSI: Social Security Administration ([ssa.gov/benefits/disability](https://www.ssa.gov/benefits/disability/))
- Lifeline program: FCC ([lifelinesupport.org](https://www.lifelinesupport.org/))
- EITC: IRS ([irs.gov/credits-deductions/individuals/earned-income-tax-credit-eitc](https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit-eitc))
- Benefits screening tool: [benefits.gov](https://www.benefits.gov/)

## When to Use

- User lost income and needs help covering food, housing, utilities, or healthcare
- User doesn't know what government programs exist or assumes they don't qualify
- User has been told they "make too much" but is still struggling
- User had a life change: job loss, disability, divorce, new baby, death of a provider
- User is already receiving one benefit and may qualify for others
- User applied for benefits and was denied

## Instructions

### Step 1: Eligibility Screening

**Agent action**: Ask the user for their household size, monthly gross income, state, and any special circumstances. Use the Federal Poverty Level table below to estimate eligibility across programs. Save the screening results to `~/documents/benefits-navigator/eligibility-screening.txt`.

```
2024 FEDERAL POVERTY LEVEL (FPL) — CONTIGUOUS US:
(Alaska and Hawaii are higher)

Household Size | 100% FPL  | 130% FPL  | 138% FPL  | 185% FPL  | 200% FPL  | 400% FPL
       1       |  $15,060  |  $19,578  |  $20,783  |  $27,861  |  $30,120  |  $60,240
       2       |  $20,440  |  $26,572  |  $28,207  |  $37,814  |  $40,880  |  $81,760
       3       |  $25,820  |  $33,566  |  $35,632  |  $47,767  |  $51,640  | $103,280
       4       |  $31,200  |  $40,560  |  $43,056  |  $57,720  |  $62,400  | $124,800
       5       |  $36,580  |  $47,554  |  $50,480  |  $67,673  |  $73,160  | $146,320
       6       |  $41,960  |  $54,548  |  $57,905  |  $77,626  |  $83,920  | $167,840

These numbers are updated annually (usually in January).
FPL thresholds determine eligibility for most programs below.
```

```
QUICK QUALIFIER CHECKLIST:

□ Income recently dropped? → Unemployment, SNAP, Medicaid
□ Have children under 5? → WIC
□ Have school-age children? → Free/Reduced Lunch
□ Pregnant? → WIC, Medicaid (higher income limits)
□ Disabled? → SSDI, SSI, Medicaid
□ Over 60? → SNAP (higher limits), Medicare Savings Programs
□ Veteran? → VA benefits (separate system, see va.gov)
□ Struggling with utility bills? → LIHEAP
□ Need phone/internet? → Lifeline
□ Need housing help? → Section 8, Emergency Rental Assistance
□ Filing taxes? → EITC, Child Tax Credit
```

### Step 2: Program-by-Program Guide

**Agent action**: For each program the user likely qualifies for, provide the details below. Help them gather documents and start applications. Save a tracking list to `~/documents/benefits-navigator/applications-tracker.txt`. Set calendar reminders for follow-up dates and recertification deadlines.

---

**SNAP (Supplemental Nutrition Assistance Program / Food Stamps)**

```
WHAT IT IS: Monthly funds loaded onto an EBT card for buying groceries.

WHO QUALIFIES:
  - Gross income below 130% FPL ($2,266/month for a family of 4)
  - Some states use "broad-based categorical eligibility" with higher
    limits (up to 200% FPL)
  - Assets limits have been eliminated in most states
  - If you receive TANF or SSI, you automatically qualify

HOW TO APPLY:
  - Online: search "[your state] SNAP application" or go to
    fns.usda.gov/snap/state-directory
  - In person: your county Department of Social Services / Human Services
  - By phone: call 211 and ask for SNAP application assistance

WHAT YOU NEED:
  - Photo ID
  - Proof of income (pay stubs, unemployment letter, or statement of
    no income)
  - Proof of residency (utility bill, lease)
  - Social Security numbers for household members
  - Bank statements (in states that still check assets)

PROCESSING TIME:
  - Standard: 30 days
  - Expedited (if income is extremely low or you have less than $100
    in liquid assets): 7 days
  - If you qualify for expedited, say so explicitly when applying

MONTHLY BENEFIT AMOUNTS (approximate, varies by state and income):
  - 1 person: up to $291/month
  - 2 people: up to $535/month
  - 4 people: up to $973/month

TIPS:
  - Report ALL deductions: rent, utilities, child care, medical expenses
    over $35/month for elderly/disabled. Deductions increase your benefit.
  - If denied, appeal within 90 days. Many denials are due to missing
    documents, not actual ineligibility.
  - Recertification is required every 6-12 months. Mark the date.
  - Students aged 18-49 enrolled in college at least half-time are
    generally ineligible unless they work 20+ hours/week or qualify
    for an exemption (work-study, TANF, etc.)
```

---

**MEDICAID**

```
WHAT IT IS: Free or very low-cost health insurance from your state.

WHO QUALIFIES:
  - In Medicaid expansion states (40 states + DC): income under 138% FPL
    ($20,783/year for an individual)
  - In non-expansion states: varies, often limited to very low-income
    parents, pregnant women, children, disabled, and elderly
  - Children qualify at higher income levels (often up to 200-300% FPL)
  - Pregnant women qualify at higher income levels (often up to 200% FPL)

HOW TO APPLY:
  - Online: healthcare.gov (your application will be routed to your
    state Medicaid office if you qualify)
  - Or apply directly at your state Medicaid office
  - By phone: 1-800-318-2596 (healthcare.gov helpline)

PROCESSING TIME: Usually 1-2 weeks. Can be faster for pregnant women
and children.

WHAT IT COVERS: Doctor visits, hospital, prescriptions, mental health,
substance abuse treatment, preventive care. Specifics vary by state.

TIPS:
  - If your income just dropped (job loss), apply based on your
    CURRENT monthly income, not last year's tax return
  - Medicaid can be retroactive up to 3 months before your application
    date if you would have been eligible
  - If denied, appeal. Denials are often due to income being calculated
    incorrectly or missing documentation.
  - In many states, if you qualify for SNAP you'll be fast-tracked
    for Medicaid
```

---

**UNEMPLOYMENT INSURANCE**

```
WHAT IT IS: Weekly cash payments (typically 40-50% of your previous
weekly wage, up to a state maximum) while you look for work.

WHO QUALIFIES:
  - Lost your job through no fault of your own (layoff, company closure,
    reduction in force)
  - Worked enough weeks and earned enough wages in the "base period"
    (usually the first 4 of the last 5 completed calendar quarters)
  - Able to work, available to work, and actively searching for work
  - In many states, you can qualify even if fired (unless for gross
    misconduct like theft or violence)

HOW TO APPLY:
  - Online: your state Department of Labor website
  - Google: "[your state] file unemployment claim"
  - File the WEEK you lose your job. Benefits are calculated from
    the filing date, not the approval date.

WHAT YOU NEED:
  - Social Security number
  - Driver's license or state ID
  - Employer name, address, phone number, dates of employment
  - Reason for separation
  - Most recent pay stubs

PROCESSING TIME: 2-4 weeks for first payment. Some states are faster,
some much slower.

DURATION: Typically 26 weeks (6 months). Some states offer less.
Extended benefits may be available during high unemployment periods.

WEEKLY BENEFIT AMOUNTS (varies dramatically by state):
  - Lowest: Mississippi ($235/week max)
  - Highest: Massachusetts ($1,015/week max)
  - Most states: $300-$600/week max

TIPS:
  - File immediately. Every week you wait is a week of lost benefits.
  - You can collect unemployment AND severance simultaneously in many
    states (some states offset, but still file)
  - Keep records of your job search activities (applications, interviews,
    networking contacts) — you may be audited
  - If your employer contests your claim, you will get a hearing.
    Show up. Bring documentation. Most contested claims that go to
    hearing are decided in the worker's favor.
  - If denied, appeal within the deadline (usually 10-30 days).
    Many initial denials are reversed.
```

---

**LIHEAP (Low Income Home Energy Assistance Program)**

```
WHAT IT IS: Help paying heating and cooling bills. Can also help with
weatherization and emergency utility situations.

WHO QUALIFIES:
  - Income at or below 150% FPL (varies by state, some go up to 200%)
  - Priority given to elderly, disabled, and households with children
    under 6
  - If you receive SNAP, SSI, or TANF, you typically auto-qualify

HOW TO APPLY:
  - Contact your state LIHEAP office: liheapch.acf.hhs.gov/profiles
  - Call 211 and ask for energy assistance
  - Contact your local Community Action Agency

WHAT IT PROVIDES:
  - One-time payment toward your utility bill (typically $200-$1,000
    depending on state and need)
  - Emergency crisis assistance if utilities are about to be shut off
    or you're using unsafe heating
  - Weatherization (insulation, sealing, furnace repair)

PROCESSING TIME: 2-4 weeks, faster for emergencies.

TIPS:
  - Apply as early in the heating/cooling season as possible --
    funds run out
  - If your utilities are about to be shut off, ask for EMERGENCY
    LIHEAP, which is processed faster
  - Many states prohibit utility shutoff during winter months if you
    have a pending LIHEAP application
```

---

**TANF (Temporary Assistance for Needy Families)**

```
WHAT IT IS: Monthly cash assistance for families with children.

WHO QUALIFIES:
  - Very low income (thresholds vary widely by state, often well
    below the poverty line)
  - Must have a dependent child under 18 (or under 19 if in school)
  - Must be a US citizen or qualified non-citizen
  - Asset limits apply in most states

HOW TO APPLY:
  - Through your state or county Department of Social Services
  - Often through the same office/application as SNAP
  - Call 211 for your local office

WHAT IT PROVIDES:
  - Monthly cash payment (amounts vary dramatically by state)
  - Examples: Mississippi ~$170/month for a family of 3,
    New Hampshire ~$1,066/month for a family of 3
  - May also include job training, child care assistance, transportation

TIME LIMITS: Federal limit of 60 months lifetime. Some states have
shorter limits. Extensions may be available for hardship.

TIPS:
  - TANF has work requirements — you must participate in work
    activities (job search, training, community service)
  - If you receive TANF, you automatically qualify for SNAP
  - Apply even if you think you might not qualify — the income limits
    vary so much by state that general advice is unreliable
```

---

**WIC (Women, Infants, and Children)**

```
WHAT IT IS: Nutrition assistance for pregnant and postpartum women,
infants, and children under 5. Provides specific foods (milk, eggs,
cereal, baby formula, fruits, vegetables) via vouchers or EBT card.

WHO QUALIFIES:
  - Pregnant, breastfeeding, or postpartum (up to 6 months, or 12
    months if breastfeeding)
  - Infants and children under age 5
  - Income at or below 185% FPL
  - If you receive SNAP, Medicaid, or TANF, you automatically qualify
  - Fathers and guardians can apply on behalf of the child

HOW TO APPLY:
  - Find your local WIC office: fns.usda.gov/wic/wic-how-apply
  - Call your state WIC agency
  - You'll need to attend an appointment (some states allow virtual)

WHAT IT PROVIDES:
  - Monthly food package worth approximately $35-$75/person
  - Nutrition education and breastfeeding support
  - Referrals to other health and social services

TIPS:
  - WIC and SNAP are different programs — you can receive both
  - WIC participation does not affect immigration status
  - Apply as soon as you're pregnant — don't wait until the baby arrives
```

---

**SECTION 8 / HOUSING CHOICE VOUCHER**

```
WHAT IT IS: Government pays a portion of your rent directly to your
landlord. You pay the rest (typically 30% of your adjusted income).

WHO QUALIFIES:
  - Income at or below 50% of area median income (varies by location)
  - Priority given to extremely low income (30% of area median),
    elderly, disabled, and families with children

HOW TO APPLY:
  - Through your local Public Housing Authority (PHA)
  - Find yours: hud.gov/program_offices/public_indian_housing/pha/contacts

REALITY CHECK: Waitlists are long. Often 1-5 years. Many waitlists
are closed. Apply anyway and get on the list.

TIPS:
  - Apply to multiple PHAs if you're willing to live in different areas
  - Check if your PHA has preference categories you fall into
    (homeless, veteran, domestic violence survivor, etc.)
  - When the waitlist opens, apply immediately — windows may be
    short (sometimes just a few days)
  - While waiting: check for Emergency Rental Assistance in your area,
    contact 211, and look for local housing nonprofits
```

---

**LIFELINE (Phone/Internet Discount)**

```
WHAT IT IS: $9.25/month discount on phone or internet service.

WHO QUALIFIES:
  - Income at or below 135% FPL
  - OR participation in: SNAP, Medicaid, SSI, Federal Public Housing
    Assistance, Veterans Pension, Tribal programs

HOW TO APPLY:
  - Online: lifelinesupport.org
  - Or through participating phone/internet carriers

TIPS:
  - Only one Lifeline benefit per household
  - You must recertify annually or you lose the benefit
  - Some carriers offer free phones through Lifeline
```

---

**SSDI and SSI (Social Security Disability)**

```
SSDI (Social Security Disability Insurance):
  - For people who worked and paid Social Security taxes
  - Must have a medical condition expected to last 12+ months or
    result in death
  - Benefit amount based on your work history
  - Apply: ssa.gov or call 1-800-772-1213
  - Processing: 3-6 months initial decision. Approval rate on
    initial application is about 30%.
  - If denied (most people are), appeal. Approval rate at hearing
    with a judge is about 50%.
  - Consider a disability attorney (they work on contingency,
    capped at 25% of back pay up to $7,200)

SSI (Supplemental Security Income):
  - For disabled, blind, or elderly (65+) people with very limited
    income and resources
  - Does NOT require work history
  - Maximum federal payment: $943/month individual, $1,415/month couple
    (2024). Many states add a supplement.
  - Asset limit: $2,000 individual, $3,000 couple
  - Apply: ssa.gov or call 1-800-772-1213

TIPS:
  - SSDI applications are almost always denied on the first try.
    This is not a reflection of your case. Appeal.
  - Document EVERYTHING: doctor visits, medications, how your
    condition affects daily activities
  - A disability attorney significantly increases approval odds
    and costs you nothing upfront
  - If approved for SSI, you automatically get Medicaid in most states
  - If approved for SSDI, you get Medicare after a 24-month waiting period
```

### Step 3: Application Support and Follow-Up

**Agent action**: For each program the user is applying to, help gather required documents, set calendar reminders for processing windows, and track application status. Create a master tracking document at `~/documents/benefits-navigator/applications-tracker.txt`.

```
DOCUMENTS TO GATHER (most programs need these):
  □ Government-issued photo ID
  □ Social Security card or number for all household members
  □ Proof of income: pay stubs, unemployment determination letter,
    self-employment records, or written statement of no income
  □ Proof of residency: utility bill, lease agreement, or mail
    with your address
  □ Bank statements (last 30-60 days)
  □ Rent or mortgage payment documentation
  □ Utility bills
  □ Medical expenses documentation (if applicable)
  □ Birth certificates for children (for WIC, TANF, CHIP)
  □ Pregnancy verification (for WIC, Medicaid)
  □ Disability documentation (for SSDI, SSI)

PRO TIPS FOR ALL APPLICATIONS:
  - Apply for SNAP first. Approval often fast-tracks you for other
    programs (called "categorical eligibility").
  - Include ALL documentation upfront. The number one reason for
    delays and denials is missing paperwork.
  - If you're denied, ALWAYS appeal. Many initial denials are
    reversed — especially for SNAP, Medicaid, and unemployment.
  - Call 211 for free help with any application. They can connect you
    to local organizations that provide application assistance.
  - Many public libraries have social workers or navigators who help
    with benefits applications for free.
  - Save copies of everything you submit. Screenshot confirmation
    pages. Note the date, time, and confirmation number of every
    submission.
  - If applying based on a recent income drop, make sure the
    application reflects your CURRENT income, not your annual income
    from last year's tax return.
```

## If This Fails

If applications are denied or you cannot access programs:

1. **SNAP denied?** Appeal within 90 days. Contact your local legal aid ([lawhelp.org](https://www.lawhelp.org)) or call 211 for free application assistance. Many denials are due to missing documents, not actual ineligibility.
2. **Medicaid denied in a non-expansion state?** Check if you qualify for ACA marketplace subsidies at [healthcare.gov](https://www.healthcare.gov/) — with low income, your premium may be $0. Also check if your children qualify (higher income limits for children's Medicaid/CHIP).
3. **Unemployment denied?** Appeal within the deadline (usually 10-30 days). Most contested claims that go to hearing are decided in the worker's favor. Bring documentation.
4. **SSDI/SSI denied?** This is expected — most initial applications are denied. Appeal immediately (within 60 days). Consider a disability attorney (they work on contingency, capped at 25% of back pay up to $7,200).
5. **Cannot navigate the paperwork?** Call 211 to connect with local organizations that provide free application assistance. Many public libraries have social workers or navigators on staff.
6. **Need food today, can't wait for SNAP?** Find your nearest food bank: [feedingamerica.org/find-your-local-foodbank](https://www.feedingamerica.org/find-your-local-foodbank). Call 211 for emergency food resources.

## Rules

- Never make anyone feel ashamed for applying for assistance. Frame it clearly: these programs are funded by taxpayer dollars for exactly this purpose.
- Always check state-specific programs in addition to federal ones. Many states have additional programs not listed here.
- If income recently dropped, help the user apply based on current monthly income, not annual income.
- Mention 211 as a universal resource — it's a free hotline that connects to local services in every US community.
- If a user is denied, always recommend appealing. Include the appeal deadline and process for that specific program.
- If a user mentions food insecurity (not having enough to eat right now), prioritize SNAP expedited processing and local food banks (feedingamerica.org/find-your-local-foodbank or call 211).

## Tips

- Applying for one program often qualifies you for others automatically. SNAP approval can fast-track Medicaid. SSI approval triggers Medicaid in most states. This is called "categorical eligibility" and it's the most efficient path through the system.
- EITC (Earned Income Tax Credit) is the largest anti-poverty program in America. If you worked at all this year, check if you qualify — the credit can be several thousand dollars. File taxes even if your income was very low. Use IRS Free File at irs.gov/freefile.
- The benefits.gov screening tool checks all federal programs at once. It takes about 15 minutes and gives you a personalized list of programs to apply for.
- If you have children, the Child Tax Credit ($2,000 per child) is available even at moderate incomes. It's partially refundable, meaning you get money back even if you don't owe taxes.
- Many people just above the income limits qualify during transitional periods (job loss, divorce, medical event). Apply based on current circumstances, not your best-case income from last year.
- Local Community Action Agencies (find yours at communityactionpartnership.com) often have additional resources: food pantries, utility assistance, holiday help, school supplies, and emergency funds that don't show up in federal databases.

## Agent State

Persist across sessions:

```yaml
household:
  size: null
  monthly_gross_income: null
  state: ""
  special_circumstances: []
  dependents:
    - name: ""
      age: null
      relationship: ""

screening:
  screening_completed: false
  screening_date: null
  fpl_percentage: null

programs:
  - program_name: ""
    likely_eligible: null
    application_started: false
    application_date: null
    application_method: ""
    confirmation_number: ""
    documents_submitted: []
    documents_needed: []
    status: "not_started"
    expected_processing_days: null
    follow_up_date: null
    decision_date: null
    approved: null
    denial_reason: ""
    appeal_filed: false
    appeal_deadline: null
    monthly_benefit_amount: null
    recertification_date: null
    notes: ""

documents_gathered:
  photo_id: false
  ssn_cards: false
  income_proof: false
  residency_proof: false
  bank_statements: false
  rent_mortgage_proof: false
  utility_bills: false
  birth_certificates: false
  medical_records: false
```

## Automation Triggers

```yaml
triggers:
  - name: application_followup
    condition: "any program has application_started AND status = 'pending'"
    delay: "expected_processing_days + 7 days after application_date"
    action: "Application processing window has passed. Advise user to check status: call the program office, check online portal, or visit in person. If no decision, ask for a timeline and escalate if needed."

  - name: recertification_warning
    condition: "any program has approved = true AND recertification_date IS SET"
    delay: "30 days before recertification_date"
    action: "Recertification deadline approaching for [program]. User must recertify to keep benefits. Gather updated income documentation and submit recertification. Missing this deadline means benefits stop and you have to reapply from scratch."

  - name: denial_appeal_deadline
    condition: "any program has approved = false AND appeal_deadline IS SET AND NOT appeal_filed"
    delay: "7 days before appeal_deadline"
    action: "URGENT: Appeal deadline approaching for [program] denial. Denials are frequently reversed on appeal. Help user draft appeal, gather supporting documentation, and submit before deadline. Contact 211 or local legal aid (lawhelp.org) for free appeal assistance."

  - name: snap_expedited_check
    condition: "screening_completed AND monthly_gross_income < 500 AND NOT snap application started"
    action: "User likely qualifies for EXPEDITED SNAP processing (7 days instead of 30). Flag this on the application. Mention it explicitly to the caseworker. Prioritize SNAP application immediately."

  - name: categorical_eligibility_check
    condition: "any program has approved = true"
    action: "User was approved for [program]. Check for categorical eligibility: SNAP approval may fast-track Medicaid. SSI approval triggers Medicaid in most states. TANF approval qualifies for SNAP. Update screening and recommend additional applications."

  - name: income_change_rescan
    condition: "monthly_gross_income changes"
    action: "Income has changed. Re-run eligibility screening against all programs. User may now qualify for programs they were previously ineligible for, or may need to report the change to programs they're currently receiving."

  - name: monthly_benefits_review
    condition: "any program has status != 'not_started'"
    schedule: "monthly"
    action: "Monthly benefits review. Check: pending applications status, upcoming recertification dates, any income changes that affect eligibility, and whether new programs should be explored. Generate summary with action items."
```
