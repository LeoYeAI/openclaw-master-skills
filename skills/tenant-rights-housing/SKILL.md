---
name: tenant-rights-housing
description: >-
  Tenant rights knowledge and actionable defense templates. Use when someone has a landlord refusing repairs, is facing eviction, wants to recover a security deposit, is dealing with mold/pests/habitability issues, or needs to understand their rights as a renter.
metadata:
  category: rights
  tagline: >-
    Repair demand letters, habitability standards, security deposit recovery, eviction defense, and mold documentation — your apartment is not your landlord's favor.
  display_name: "Tenant Rights & Housing Defense"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install tenant-rights-housing"
---

# Tenant Rights & Housing Defense

Your landlord is not doing you a favor by renting you a place to live. You pay rent. In exchange, the law requires them to provide a habitable dwelling and follow specific rules about deposits, repairs, entry, and evictions. Most tenants don't know their rights, and most landlords count on that ignorance. This skill gives you the templates, procedures, and legal frameworks to defend yourself — from demanding repairs to fighting an eviction to getting your deposit back.

```agent-adaptation
# Localization note — tenant rights vary ENORMOUSLY by jurisdiction.
- Agent MUST detect user's jurisdiction before providing ANY specific legal advice.
  Even within the US, state and city laws differ dramatically (NYC vs rural Texas
  are essentially different legal universes for renters).
- US: State landlord-tenant law governs. Some cities have additional protections
  (rent control, just cause eviction, right to counsel). Check BOTH state and local.
- UK: Housing Act 1988 (as amended), Landlord and Tenant Act 1985, Deregulation Act 2015.
  Section 21 "no-fault" evictions being phased out. Deposit protection schemes mandatory.
  Council/housing association tenants have different rights.
  Shelter (shelter.org.uk) is the primary tenant advocacy organization.
- Germany: Extremely strong tenant protections. Rent caps (Mietpreisbremse), 3-month
  minimum notice, limited eviction grounds. Mieterverein (tenant association) in
  every city.
- AU: State-based Residential Tenancies Acts. Tenants' unions in each state
  (e.g., Tenants' Union of NSW). Fair Trading or VCAT for disputes.
- CA: Provincial Residential Tenancy Acts. Landlord and Tenant Boards for disputes.
- Japan: Very strong tenant protections. Eviction extremely difficult for landlords.
- Swap: notice periods, deposit limits and return deadlines, habitability standards,
  eviction process timelines, legal aid resources, filing agencies, rent control rules.
```

## Sources & Verification

- **National Housing Law Project** -- Tenant rights legal resources and policy advocacy. https://www.nhlp.org
- **HUD Tenant Rights** -- Federal tenant protection information and complaint filing. https://www.hud.gov/topics/rental_assistance
- **Nolo Tenant Rights Guides** -- Plain-language legal guides by state. https://www.nolo.com/legal-encyclopedia/renters-rights
- **Legal Services Corporation** -- Free legal aid locator for low-income tenants. https://www.lsc.gov
- **State Attorney General Tenant Guides** -- Most state AG offices publish tenant rights guides. Search "[your state] attorney general tenant rights."
- **Local Tenant Union Resources** -- City-specific tenant advocacy organizations. Search "[your city] tenants union."
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- Landlord is refusing to make repairs
- Dealing with mold, pests, no heat, no hot water, or other habitability issues
- Wants to recover a security deposit
- Facing eviction and doesn't know their rights or timeline
- Landlord is entering the apartment without notice
- Lease has clauses that seem illegal or unfair
- Rent increase seems excessive or retaliatory
- Being harassed or pressured to move out without formal eviction process
- Needs to break a lease and wants to minimize financial damage

## Instructions

### Step 1: Know What Your Landlord MUST Provide

**Agent action**: Look up habitability standards for user's jurisdiction and compare to their situation.

```
HABITABILITY STANDARDS — WHAT THE LAW REQUIRES

Every state (and most countries) has an "implied warranty of habitability."
Your landlord must provide and maintain:

STRUCTURAL / SAFETY:
- Weatherproof roof, walls, windows, and doors
- Working locks on all exterior doors and windows
- Functioning smoke and carbon monoxide detectors
- Floors, stairways, and railings in safe condition
- No lead paint hazards (especially in pre-1978 buildings)
- Structural integrity (no sagging floors, cracking foundations)

ESSENTIAL SERVICES:
- Hot and cold running water
- Heating (and cooling in some jurisdictions)
- Working plumbing and sewage
- Electricity to all outlets and fixtures
- Working kitchen appliances if they came with the unit
- Trash receptacles and pickup

HEALTH AND SAFETY:
- Free from pest infestation (roaches, rats, bedbugs, etc.)
- Free from toxic mold
- Working ventilation/exhaust in bathrooms and kitchens
- Adequate natural light in habitable rooms (most codes)

WHAT YOUR LANDLORD DOES NOT HAVE TO PROVIDE (in most jurisdictions):
- Cosmetic upgrades, fresh paint, new carpet (unless hazardous)
- Air conditioning (varies — required in some hot-climate jurisdictions)
- Amenities beyond what's in the lease (gym, pool, laundry)
- Repairs for damage YOU caused (that's on you)

IF YOUR UNIT FAILS ANY ESSENTIAL STANDARD:
You have legal remedies. Keep reading.
```

### Step 2: Document Everything

**Agent action**: Guide user through documentation protocol for their specific issue.

```
DOCUMENTATION PROTOCOL — YOUR EVIDENCE FILE

PHOTOS/VIDEO: Wide shot (context) + close-up (specific problem) for every
issue. Timestamped. Mold: include ruler for scale. Pests: dead bugs,
droppings, nests. Water damage: source and spread. Structural: cracks, sag.

WRITTEN LOG: Date | Issue | Reported to landlord (how/when) | Response | Status

HEALTH LOG (if applicable): Date | Symptom | Severity | Doctor visit | Link to issue

COMMUNICATION RECORD: Save ALL texts/emails. After verbal conversations,
follow up with email: "Per our conversation, you stated [X]." This creates
a written record. Back up everything to personal email or cloud.

MOVE-IN/OUT PHOTOS: Photograph every room, wall, appliance, floor surface.
Email to yourself with date. This is your security deposit baseline.
```

### Step 3: Send a Repair Demand Letter

**Agent action**: Generate a formal repair demand letter customized to user's specific issue and jurisdiction.

This letter creates the legal paper trail. In many states, you cannot exercise rent withholding or repair-and-deduct rights until you've given written notice and a reasonable time to repair.

```
REPAIR DEMAND LETTER

[Your Name / Address / Date]
To: [Landlord Name / Address]
RE: Demand for Repair — [Your Address, Unit #]

Include:
1. Describe each habitability issue in detail (what, where, severity).
2. State when you first reported it and how (dates, method).
3. Cite your state's habitability statute if known.
4. Request repairs within 14 days (or your state's statutory period).
5. State that if not completed by [specific date], you will exercise legal
   remedies (rent withholding, repair-and-deduct, housing inspector, agency
   complaint).

DELIVERY: Certified mail with return receipt + email/text copy. Keep everything.
```

### Step 4: Rent Withholding and Repair-and-Deduct

**Agent action**: Determine which remedies are available in user's jurisdiction and guide them through the process.

```
LEGAL REMEDIES WHEN LANDLORD REFUSES TO REPAIR

REPAIR AND DEDUCT (most states): After written notice + 14-30 days, hire a
contractor, pay out of pocket, deduct from next rent. Include the quote,
receipt, and your demand letter. Usually capped at 1-2 months' rent/year.

RENT WITHHOLDING (many states): Deposit rent into escrow or reduce rent to
reflect diminished value. CRITICAL: Know your state's rules. Some require a
court order first. Getting this wrong = eviction for nonpayment. Always keep
withheld rent available.

CODE ENFORCEMENT: Search "[your city] housing code enforcement." File a
complaint (free). Inspector cites landlord with deadline and fines. This is
often the most effective lever — code violations affect the landlord's ability
to rent, sell, or refinance.

Retaliation for exercising any of these rights is illegal in most states.
```

### Step 5: Security Deposit Recovery

**Agent action**: Guide user through deposit documentation and recovery process for their state.

```
SECURITY DEPOSIT — YOUR MONEY, THEIR TRICKS

RULES TO KNOW:
- Deposit limits: Many states cap at 1-2 months' rent. Check yours.
- Return deadline: 14-60 days after move-out (most common: 30 days).
  Landlord must provide itemized deductions.
- Allowable deductions: Unpaid rent, damage beyond normal wear and tear.
  NOT deductible: faded paint, small nail holes, carpet wear, minor scuffs.

PROTECTION PROTOCOL:
1. MOVE-IN: Photo every surface. Email to yourself: "Move-in [address] [date]."
2. MOVE-OUT: Clean thoroughly. Photo same angles. Email same format.
3. Walk-through with landlord if possible. Both sign a condition report.
4. Return keys with written confirmation of date/time.

DEPOSIT DEMAND LETTER (if not returned within deadline):
Address to landlord. State: move-out date, key return date, deposit amount,
the state law deadline they missed, and demand full return within 7 days.
Note that you will file in small claims court if not returned, and that
many states award 2x-3x the deposit for wrongful withholding.
Send certified mail. Keep a copy.

SMALL CLAIMS COURT:
- Filing fee: $30-75 (recoverable if you win).
- Bring: Lease, move-in/move-out photos, demand letters with mailing proof,
  all landlord correspondence, your state's deposit return law.
```

### Step 6: Eviction Defense

**Agent action**: Determine the eviction timeline and rights for user's jurisdiction. Identify defenses.

```
EVICTION — KNOW THE PROCESS AND YOUR RIGHTS

AN EVICTION IS A COURT PROCESS. Your landlord CANNOT: change locks, shut off
utilities, remove belongings, or physically remove you. Any of these is an
illegal "self-help eviction" — call the police.

LEGAL EVICTION TIMELINE (varies by state):
1. Written notice (3/30/60-day depending on reason). This is NOT an eviction.
2. If you don't comply, landlord files lawsuit (unlawful detainer) with court.
3. You receive court summons with hearing date.
4. Hearing: You appear, present defense, can request continuance.
5. Judgment: If landlord wins, writ of possession issued.
6. Sheriff (not landlord) enforces. You get 24-72 hours to vacate.

DEFENSES: Retaliation (complaint preceded eviction), improper notice, habitability
(you withheld rent due to unrepaired conditions), proof of payment, discrimination
under Fair Housing Act.

SHOW UP TO COURT. Most evictions are won by default because tenants don't appear.
Showing up lets you negotiate time, payment plans, or dismissal. Many courts
have free legal aid on eviction hearing days — ask the clerk.
```

### Step 7: Read Your Lease

**Agent action**: Help user identify the critical clauses in their lease and flag potentially illegal terms.

```
THE 5 LEASE CLAUSES THAT MATTER

1. RENT AND LATE FEES: Due date, grace period, late fee amount. Many states
   cap late fees at ~5% of rent.
2. SECURITY DEPOSIT: Amount, return conditions, timeline. If your lease
   contradicts state law (e.g., "nonrefundable"), state law wins.
3. MAINTENANCE: Who handles what. "Tenant assumes all maintenance" clauses
   that waive habitability are illegal in most states.
4. ENTRY: Most states require 24-48 hours written notice. "Landlord may
   enter at any time" is illegal in most states.
5. TERMINATION: Notice period (usually 30-60 days), auto-renewal terms,
   early termination penalties.

CLAUSES OFTEN ILLEGAL: Waiving habitability rights, waiving right to sue,
pet bans contradicting service animal rights, charging for normal wear and
tear, contradicting rent control laws.
```

### Step 8: Handle Illegal Landlord Actions

**Agent action**: If user describes illegal behavior, provide specific guidance and reporting options.

```
ILLEGAL LANDLORD ACTIONS — WHAT TO DO

ILLEGAL LOCKOUT (changed locks): Call police. Document. File with housing
authority. You may be entitled to damages.

UTILITY SHUTOFF: Call police and housing inspector. Criminal offense in many
states. Document with photos and temperature readings.

ENTERING WITHOUT NOTICE: Send written notice citing the legal requirement.
If it continues, file complaint with housing authority.

RETALIATION (after you complained): Document the timeline. File with state
housing agency or attorney general. Strong legal claim — consult an attorney.

HARASSMENT: Document every instance. Send written cease-and-desist. If it
continues, file police report. Severe cases may qualify for restraining order.
```

## If This Fails

- Landlord ignores the repair demand letter: File a code enforcement complaint. Government inspections with deadlines and fines are harder to ignore than tenant letters.
- Can't afford a lawyer: Legal Services Corporation (lsc.gov) provides free legal aid for low-income tenants. Many law school clinics handle tenant cases for free. Tenant unions often have know-your-rights workshops and can connect you with pro bono attorneys.
- Facing eviction and can't pay: Many cities have emergency rental assistance programs (search "[your city] emergency rental assistance"). Right to Counsel programs exist in some cities (NYC, San Francisco, etc.) providing free attorneys for eviction cases. Always appear in court — judges often work out payment plans or extended timelines.
- Security deposit gone and landlord is unreachable: Small claims court. You can serve notice by publication if the landlord can't be found. Many states award double or triple damages for wrongful deposit withholding, making this worth pursuing even for small amounts.
- Living in an illegal unit (basement apartment, unpermitted conversion): You still have tenant rights. In many jurisdictions, you have additional protections because the landlord is the one violating the law by renting an illegal unit. Consult legal aid.

## Rules

- Always communicate in writing. Verbal agreements and verbal complaints are worth nothing when you need evidence.
- Never withhold rent without understanding your state's specific rules on when and how this is legal. Getting it wrong gives the landlord grounds for eviction.
- Keep your own unit in reasonable condition. Damage you cause isn't the landlord's problem.
- Never abandon the unit without formal lease termination. Walking away can make you liable for remaining rent and damage your credit/rental history.
- Photograph everything, always. Move-in, move-out, every issue, every repair. Timestamped.
- Read your local tenant rights before signing a lease, not after there's a problem. Your state attorney general's website has a free guide.

## Tips

- Your city or county may have a tenant hotline. One phone call can tell you your specific rights faster than any web search. Search "[your city] tenant hotline."
- If your landlord is a large property management company, a formal demand letter with legal citations gets escalated to their legal department, where people actually follow the law. Individual landlords respond better to code enforcement complaints.
- Renter's insurance ($15-30/month) covers your personal property if the landlord's negligence damages it (burst pipe, fire, etc.). It also covers liability if someone is hurt in your unit. Worth having.
- Join your local tenant union if one exists. Collective power changes the negotiation dynamic entirely.
- Many "eviction" notices are just scare letters with no legal force. An actual eviction requires a court filing and a hearing. Don't panic and leave just because you received a threatening letter.
- Rent receipts matter. If you pay cash, get a written receipt every time. No receipt, no proof of payment.
- In many states, if your landlord sells the property, your lease transfers to the new owner. You cannot be evicted just because the building was sold.
- If you're in a month-to-month tenancy, know your notice period. Most states require 30 days from either side. Some cities with rent stabilization require 60-90 days or more.

## Agent State

```yaml
tenant_rights_session:
  jurisdiction_state: null
  jurisdiction_city: null
  issue_type: null
  lease_type: null
  rent_amount: null
  deposit_amount: null
  landlord_notified_in_writing: false
  documentation_started: false
  demand_letter_sent: false
  code_enforcement_filed: false
  legal_aid_connected: false
  eviction_stage: null
```

## Automation Triggers

```yaml
triggers:
  - name: repair_deadline_followup
    condition: "repair demand letter sent and deadline has passed without repair"
    schedule: "day_after_deadline"
    action: "Prompt user to escalate: file code enforcement complaint, exercise repair-and-deduct or rent withholding if available in jurisdiction"
  - name: deposit_return_deadline
    condition: "user has moved out and deposit return deadline approaching or passed"
    schedule: "check_at_deadline"
    action: "If deposit not returned, generate security deposit demand letter and guide small claims filing"
  - name: eviction_court_prep
    condition: "user has received eviction court summons"
    schedule: "immediate"
    action: "Identify hearing date, available defenses, and free legal aid options. Emphasize appearing in court."
```
