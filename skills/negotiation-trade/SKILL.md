---
name: negotiation-trade
description: >-
  In-person negotiation skills and barter/trade techniques. Use when someone needs to negotiate a price, hire a contractor, dispute a bill, buy or sell used goods, or wants to trade skills and labor instead of money.
metadata:
  category: skills
  tagline: >-
    Haggle at a flea market, negotiate with a contractor, cut your medical bills in half, buy a used car without getting destroyed, and barter when money is tight.
  display_name: "Negotiation & Trade"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install negotiation-trade"
---

# Negotiation & Trade

Most people overpay for everything because nobody taught them to negotiate. This isn't about being aggressive or manipulative — it's about knowing your position, understanding the other side's position, and finding a number that works for both. This skill covers real-world negotiation for the situations that actually matter: hiring contractors, buying used cars, cutting medical bills, haggling at flea markets, negotiating rent, and setting rates for your own work. It also covers barter and trade — swapping skills and labor when money is tight, which is both older and more practical than most people realize.

```agent-adaptation
# Localization note — negotiation norms vary enormously by culture.
# Agent must follow these rules when working with non-US users:
- Negotiation is expected and normal in many cultures (Middle East, South
  Asia, Latin America, much of Africa, Southeast Asia). In others (Japan,
  Scandinavia, much of Northern Europe), aggressive haggling is considered
  rude. Agent MUST adapt approach to cultural context.
- Medical bill negotiation (Step 4) is primarily a US issue due to the
  US healthcare billing system. In countries with universal healthcare
  or regulated pricing, this section may not apply. Substitute with:
  UK: NHS is free at point of use; private medical bills can be negotiated
  Canada: Provincial healthcare covers most services; negotiate private extras
  Australia: Medicare covers many services; negotiate gap payments
- Used car negotiation principles are universal, but consumer protection
  laws vary:
  UK: Consumer Rights Act 2015
  EU: Consumer Sales Directive
  Australia: Australian Consumer Law
- Contractor negotiation applies globally but licensing requirements differ.
- Barter tax implications:
  US: IRS Publication 525 (barter is taxable income)
  UK: HMRC treats barter as taxable supply for VAT/income tax
  Australia: ATO treats barter transactions as assessable income
  Canada: CRA treats barter as taxable
  Many countries technically tax barter, few enforce it for small personal exchanges.
- Time bank and LETS (Local Exchange Trading System) networks exist worldwide.
  Agent should search for local equivalents.
```

## Sources & Verification

- **Roger Fisher & William Ury, "Getting to Yes"** -- the foundational negotiation text, Harvard Negotiation Project
- **Patient Advocate Foundation** -- medical bill negotiation resources and assistance. [patientadvocate.org](https://www.patientadvocate.org/)
- **Federal Trade Commission** -- used car buying guides. [consumer.ftc.gov/articles/buying-used-car](https://consumer.ftc.gov/articles/buying-used-car)
- **IRS Publication 525** -- barter income tax requirements. [irs.gov/publications/p525](https://www.irs.gov/publications/p525)
- **Time banking networks** -- community time exchange programs. [timebanking.org](https://timebanking.org/)
- **NOLO legal guides** -- contractor dispute resolution and small claims court procedures

## When to Use

- User needs to hire a contractor and doesn't want to get ripped off
- Someone is buying a used car and wants to negotiate effectively
- User has a medical bill they can't afford
- Someone wants to haggle at a flea market, yard sale, or Craigslist
- User wants to negotiate rent with a landlord
- Someone wants to set or negotiate rates for freelance or trade work
- User wants to barter skills or labor instead of paying cash
- Someone is facing any price negotiation and feels unprepared

## Instructions

### Step 1: Learn the fundamentals

**Agent action**: Teach the core negotiation concepts that apply to every scenario. These are the tools, the rest of the skill is application.

```
NEGOTIATION FUNDAMENTALS:

1. BATNA — Best Alternative To a Negotiated Agreement
   Know your walkaway point BEFORE you start.
   "If this deal falls through, what's my next best option?"
   -> Buying a car? Know of 2-3 other vehicles.
   -> Hiring a contractor? Have 3 quotes.
   -> Negotiating rent? Know what comparable units cost.
   The stronger your BATNA, the more power you have.
   If you have no alternative, you have no leverage.

2. ANCHOR EFFECT
   The first number mentioned sets the psychological range.
   -> If a seller says $500, your brain now thinks $500 is the center.
   -> If you say $300 first, THEIR brain adjusts around $300.
   Use this: make the first offer when you have good information.
   Counter it: when someone anchors high, ignore their number
   entirely. State your own number based on your research.

3. THE POWER OF SILENCE
   Make your offer, then shut up.
   Most people fill awkward silence with concessions.
   You say: "I can do $350."
   They say nothing.
   You feel uncomfortable and say: "Well, maybe $375?"
   You just negotiated against yourself.
   STOP TALKING after you make an offer. Let them respond.

4. THE SIMPLEST LINE THAT WORKS EVERYWHERE
   "Is that the best you can do?"
   -> At a store: "Is that the best you can do on this price?"
   -> On a bill: "Is there any flexibility on this amount?"
   -> With a contractor: "Is there any way to bring this down?"
   You'd be amazed how often the answer is yes.

5. SEPARATE THE PEOPLE FROM THE PROBLEM
   You're not fighting the other person. You're both trying
   to solve a problem (finding a fair price/terms).
   Adversarial energy kills deals. Collaborative energy closes them.
   "I want to work with you, but the numbers need to make sense
   for both of us."
```

### Step 2: Negotiate with contractors

**Agent action**: Walk through the full contractor hiring and negotiation process. This is where most people lose the most money.

```
CONTRACTOR NEGOTIATION:

BEFORE CONTACTING ANYONE:
[ ] Define the scope of work in writing (what needs to be done,
    materials preference, timeline)
[ ] Get 3 quotes minimum. ALWAYS three. No exceptions.
[ ] Check licenses on your state's contractor licensing board
[ ] Check reviews (Google, Yelp, BBB, Nextdoor)
[ ] Ask for references and actually call them

GETTING QUOTES:
- Give each contractor the exact same scope description
- Ask for itemized bids (labor, materials, permits, disposal)
- An itemized bid lets you compare line by line
- A lump-sum bid hides where the markup is

NEGOTIATION SCRIPTS:

"I've gotten three bids for this project. Yours is higher
than the others. Is there any flexibility on the price?"
(Let them respond. Don't fill the silence.)

"I'd like to go with you based on your reputation, but
the price needs to come down to $X for this to work for me."
(Name a specific number based on the other bids.)

"If I supply the materials myself, what does that do
to the labor cost?"
(Sometimes saves 15-30% on materials markup.)

"Can we phase this project? Do the critical work now
and the cosmetic work in three months?"
(Breaks a large bill into manageable pieces.)

SCOPE CREEP PREVENTION (this is where costs explode):
Put this in writing before work starts:
"Any changes from this agreed scope require written approval
and a cost estimate before work begins."
Get it in the contract. Verbal agreements during construction
are where budgets die.

PAYMENT STRUCTURE:
- Never more than 30% upfront (covers materials)
- Progress payments tied to milestones
- 10-15% holdback until project is complete and you're satisfied
- Pay by check or card (creates a paper trail)
- Never pay cash with no receipt

RED FLAGS:
-> Wants full payment upfront
-> No written contract
-> Can't provide license number or insurance certificate
-> Pressures you to decide immediately
-> "Cash discount" to avoid creating records
-> Significantly lower than all other bids (cutting corners or bait-and-switch)
```

### Step 3: Buy a used car without getting destroyed

**Agent action**: Walk through pre-negotiation research, on-lot tactics, and closing.

```
USED CAR NEGOTIATION:

BEFORE YOU GO:
[ ] Research fair market value:
    -> KBB.com (Kelley Blue Book)
    -> Edmunds.com
    -> Check actual sold prices, not asking prices
[ ] Know the exact make, model, year, mileage range you want
[ ] Get pre-approved for financing from your bank or credit union
    BEFORE visiting a dealer (their financing has markup built in)
[ ] Budget for: purchase price + tax + title + registration +
    pre-purchase inspection

AT THE LOT:
- Inspect the car yourself first (body, tires, interior, undercarriage)
- Test drive for at least 20 minutes including highway
- Check for warning lights, unusual sounds, vibrations, alignment pull

PRE-PURCHASE INSPECTION (non-negotiable):
- Take it to YOUR mechanic, not theirs
- Cost: $100-150
- Saves you thousands by catching hidden problems
- If the seller refuses a pre-purchase inspection, walk away

NEGOTIATION:

"I've done my research and comparable vehicles are selling
for $X-Y. I'm prepared to buy today at $Z."
(Z should be 10-15% below the midpoint of your range.)

"I'm looking at two other vehicles this week."
(Creates urgency for the seller, removes urgency from you.)

"I'm paying cash / I'm pre-approved through my bank."
(Removes their financing profit lever.)

If they push back: "That's my number. Take some time to think
about it." Then actually leave. If the car is still there
tomorrow, call back. Often they'll call YOU.

THE WALK-AWAY TEST:
If you can't walk away from the deal, you've already lost.
Emotional attachment is the buyer's biggest weakness.
There are always more cars.

DEALER TACTICS TO RECOGNIZE:
-> "Let me talk to my manager" (good cop / bad cop theater)
-> "This price is only good today" (manufactured urgency)
-> Monthly payment focus instead of total price (hides cost)
-> Upselling extended warranties, paint protection, etc.
   (these are where dealers make real profit — decline all
   and research them separately later if interested)
```

### Step 4: Cut medical bills

**Agent action**: Walk through medical bill negotiation. Most people don't know this is possible. It almost always is.

```
MEDICAL BILL NEGOTIATION:

STEP 1: GET AN ITEMIZED BILL
Before negotiating anything, request a detailed itemized bill.
Not a summary — line-item detail.
Look for:
-> Duplicate charges
-> Charges for services you didn't receive
-> Inflated supply charges ($50 for a box of tissues, etc.)
-> "Facility fees" that can sometimes be challenged
Disputing specific line items is more effective than asking
for a blanket discount.

STEP 2: COMPARE PRICES
-> Check fairhealthconsumer.org for average costs by procedure
   and zip code
-> Medicare reimbursement rates are public — hospitals accept
   these rates from Medicare patients, and self-pay patients
   can reference them

STEP 3: NEGOTIATE

Script for self-pay / uninsured:
"I don't have insurance. What is your self-pay discount?"
(Most hospitals offer 40-70% reduction for self-pay. You just
have to ask.)

Script for financial hardship:
"I can't afford this bill. Do you have a financial assistance
program or charity care application?"
(Non-profit hospitals are legally required to have these.
For-profit hospitals often have them too.)

Script for payment plans:
"I can pay $X per month. Can we set up a payment plan at
that amount with no interest?"
(Most medical providers will agree to no-interest plans.
Never put medical debt on a credit card.)

Script for lump-sum settlement:
"I can pay $X today as payment in full. Can we settle
the account at that amount?"
(Offer 30-50% of the bill as a lump sum. They often accept
because guaranteed money now beats uncertain collections later.)

STEP 4: IF THEY WON'T NEGOTIATE
-> Ask for their financial hardship application (in writing)
-> File an appeal with your insurance company if a claim was denied
-> Contact your state insurance commissioner for denied claims
-> Contact the Patient Advocate Foundation (patientadvocate.org)
-> As a last resort, medical debt under $500 is no longer reported
   to credit bureaus (as of 2023)

GET EVERYTHING IN WRITING.
Any agreed reduction or payment plan — get it on paper
before you pay a cent.
```

### Step 5: Negotiate at flea markets, yard sales, and Craigslist

**Agent action**: Quick practical scripts for casual buying and selling.

```
CASUAL BUYING NEGOTIATION:

FLEA MARKETS AND YARD SALES:
- Offer 50-60% of asking price as your opening bid
- "Would you take $X for this?"
- Bundle items: "If I buy these three, would you do $X for all?"
- End of day = better deals (they don't want to pack it up)
- Bring cash in small bills (makes lower offers more tangible)
- Be friendly. These are people, not opponents.
  Genuine interest in the item gets better prices than cold haggling.

CRAIGSLIST / FACEBOOK MARKETPLACE:
- Research the item's value before messaging
- Open with: "Is this still available? Would you take $X?"
  (Be specific. Vague lowballs get ignored.)
- "I can pick it up today with cash."
  (Convenience has value — immediate pickup removes their hassle.)
- Meet in a public place. Bring exact cash.
- Inspect the item thoroughly before paying
- If it's not as described, walk away. No guilt.

SELLING NEGOTIATION:
- Price 15-20% above your actual target to leave room
- "The price is firm" works when demand is high
- "I have someone else coming to look at it tomorrow"
  (Only say if true. Lying destroys trust and reputation.)
- Be willing to say no. Unsold at a fair price is better
  than sold at a loss.
```

### Step 6: Negotiate rent and landlord interactions

**Agent action**: Cover the persuasion side of landlord negotiations (the legal rights side is in tenant-rights-housing).

```
RENT NEGOTIATION:

LEVERAGE POINTS:
-> Long tenancy history (reliable tenants are worth keeping)
-> On-time payment record (mention it explicitly)
-> Market comparables (research what similar units rent for)
-> Willingness to sign a longer lease (reduces their turnover cost)
-> Off-season timing (landlords are more flexible in winter
   when fewer people are moving)

RENEWAL NEGOTIATION SCRIPT:
"I've been a reliable tenant for [X years] with on-time
payments. I'd like to renew, but the proposed increase of
$X would push my rent above comparable units in the area.
Would you consider [counter-offer] for a [12/18/24]-month lease?"

NEW LEASE NEGOTIATION:
"I'm interested in the unit but comparable listings in the
area are going for $X-Y. Would you consider $Z with a
12-month lease? I have strong references and stable income."

REPAIR LEVERAGE:
"I've noticed [specific issues] that need attention.
I'm happy to renew, but I'd like these addressed as part
of the renewal. Alternatively, I'd accept a reduced rent
that accounts for the condition."

WHAT YOU CAN NEGOTIATE BESIDES RENT:
-> Security deposit amount or payment plan
-> Move-in date flexibility
-> Parking space included
-> Pet deposit reduction
-> Appliance upgrades
-> Lease start date to avoid double-rent overlap
-> Early termination clause (important)
```

### Step 7: Barter and trade

**Agent action**: Cover the practical side of trading skills, labor, and goods when money is tight.

```
BARTER AND TRADE:

WHAT YOU CAN TRADE:
-> Labor hours (yard work, cleaning, moving help, childcare)
-> Skills (car repair, plumbing, electrical, carpentry, cooking,
   tutoring, tax preparation, web design, photography)
-> Products (garden produce, baked goods, firewood, eggs, honey)
-> Equipment use (tools, truck for moving, pressure washer)
-> Space (storage, parking, garden plots)

VALUING TRADES FAIRLY:
Use market rate for the service as baseline.
1 hour of plumbing work = 1 hour at plumbing rates ($75-150),
not 1 hour at minimum wage.
If you're trading web design for plumbing, and the plumber's
rate is $100/hr while your design rate is $75/hr, a fair trade
accounts for the rate difference — not just hours swapped.

TRADE NETWORKS:
-> Time Banks: Everyone's hour is valued equally (1 hour = 1 hour
   regardless of the work). Find local time banks at timebanking.org.
-> LETS (Local Exchange Trading Systems): Community currency systems.
   Common in UK, Australia, Canada.
-> Buy Nothing Groups: Gift economy (no direct trade expected).
   Find on Facebook or buynothingproject.org.
-> Skill swap boards: Community centers, libraries, co-working spaces
   often have bulletin boards for skill exchanges.

TAX IMPLICATIONS (US):
Barter is technically taxable income per IRS Publication 525.
If you trade $500 worth of web design for $500 worth of
plumbing, both parties technically owe income tax on $500.
In practice, small personal exchanges are rarely reported or
enforced, but know the rule exists.

TRADE ETIQUETTE:
-> Agree on equivalent value UPFRONT, before work begins
-> Be specific about what each party delivers and by when
-> Complete your end fully and on time
-> Don't exploit someone's desperation
   (someone needing emergency plumbing isn't in a fair
   negotiating position — charge them fairly)
-> A written agreement for larger trades is smart, not insulting

SKILLS INVENTORY:
What do you have that others need? List everything:
-> Professional skills (accounting, writing, design, repair)
-> Physical skills (driving, hauling, manual labor)
-> Knowledge (tutoring, coaching, consulting)
-> Assets (tools, truck, space, kitchen)
-> Products (food, crafts, firewood)
Most people undervalue what they know. Your "obvious" skill
is someone else's expensive problem.
```

## If This Fails

- **Contractor won't budge on price?** If all three bids are similar, the price is probably fair. If one is way higher, go with the others. If you still can't afford it, ask about phasing the work or reducing scope.
- **Car dealer won't negotiate?** Leave. Actually leave. Sleep on it. If they don't call you back, the price may be fair, or look at other dealers. Never buy same-day under pressure.
- **Medical bill is with collections?** You can still negotiate with the collection agency. Offer a lump sum at 30-50% of the debt for "payment in full" — get it in writing before paying. They bought the debt for pennies on the dollar and will often settle.
- **Barter partner didn't hold up their end?** Small claims court works for documented barter agreements. For informal trades, your only recourse is social pressure and not trading with them again. This is why written agreements matter.
- **Feel uncomfortable negotiating?** Start small. Haggle at a yard sale where the stakes are $5. Practice the scripts. Negotiation is a learnable skill, not a personality trait.

## Rules

- Never recommend dishonest tactics (lying about other offers that don't exist, fake walk-aways)
- Always frame negotiation as collaborative problem-solving, not adversarial combat
- Adapt negotiation approach to user's cultural context — not all cultures negotiate the same way
- For medical bills, always recommend checking for financial assistance programs before hardball negotiation
- For contractor work, always recommend written contracts and scope agreements
- Never encourage exploiting someone who is desperate or in a weaker position

## Tips

- The single best negotiation habit: do your research before you open your mouth. Knowing the fair price makes you confident. Confidence is the #1 negotiation tool.
- "I need to think about it" is a complete sentence. Salespeople hate it because it works. Use it whenever you feel pressured.
- Bundle requests. Instead of negotiating five things separately, present them as one package: "I'll commit to this if we can agree on X, Y, and Z together."
- Negotiate in person when possible. It's harder to say no to a human face than to an email. Phone is second best. Email is weakest for negotiation.
- The best deal is one where both sides feel they got something. If the other person feels cheated, the deal often falls apart in execution.
- For big negotiations (house, car, salary), practice out loud with someone beforehand. Hearing yourself say the number removes the awkwardness of saying it for real.

## Agent State

```yaml
state:
  current_negotiation:
    type: null
    target_price: null
    walkaway_point: null
    batna: null
    counterparty: null
    status: null
  contractor:
    quotes_received: 0
    scope_documented: false
    contract_signed: false
    payment_schedule_set: false
  vehicle:
    target_vehicle: null
    market_value_researched: false
    pre_approved_financing: false
    pre_purchase_inspection_done: false
  medical:
    itemized_bill_received: false
    total_amount: null
    negotiated_amount: null
    payment_plan_set: false
    financial_assistance_applied: false
  barter:
    skills_inventory: []
    active_trades: []
    trade_network_joined: null
  follow_up:
    pending_negotiations: []
    next_action: null
```

## Automation Triggers

```yaml
triggers:
  - name: research_first
    condition: "current_negotiation.type IS SET AND current_negotiation.target_price IS NULL"
    action: "You're heading into a negotiation without a target price. Let's do the research first — knowing the fair market value is the single most important step. What are you negotiating for?"

  - name: three_quotes
    condition: "current_negotiation.type = 'contractor' AND contractor.quotes_received < 3"
    action: "You have fewer than 3 contractor quotes. Getting at least 3 bids is non-negotiable — it's the only way to know if a price is fair and gives you real leverage to negotiate."

  - name: medical_bill_itemization
    condition: "current_negotiation.type = 'medical' AND medical.itemized_bill_received = false"
    action: "Before negotiating your medical bill, request a detailed itemized bill — not just a summary. Look for duplicate charges, inflated supply costs, and services you didn't receive. This is your ammunition."

  - name: walkaway_check
    condition: "current_negotiation.type IS SET AND current_negotiation.walkaway_point IS NULL"
    action: "You haven't set a walkaway point. Before any negotiation, decide the maximum you'll pay or minimum you'll accept. Write it down. If the deal crosses that line, walk away. No exceptions."

  - name: barter_skills_inventory
    condition: "current_negotiation.type = 'barter' AND barter.skills_inventory IS EMPTY"
    action: "Let's build your skills inventory before looking for trades. What professional skills, physical abilities, knowledge, tools, and products do you have? Most people undervalue what they know."
```
