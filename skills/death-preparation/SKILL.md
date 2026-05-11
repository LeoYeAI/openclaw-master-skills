---
name: death-preparation
description: >-
  Practical end-of-life preparation and philosophical mortality awareness. Use when someone needs to create a will or advance directive, wants to have the death conversation with family, is processing mortality after a health scare, or wants to get their affairs in order.
metadata:
  category: life
  tagline: >-
    Advance directives, wills, digital legacy, funeral preferences, and the conversation nobody wants to have — practical and philosophical preparation for the one certainty.
  display_name: "Death Preparation & Mortality Awareness"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/death-preparation"
---

# Death Preparation & Mortality Awareness

You are going to die. Not eventually, not in theory, not as a metaphor. You, specifically, will stop being alive, and everything you haven't prepared for will become someone else's emergency. Half of this skill is paperwork — wills, advance directives, digital legacy, the death file. The other half is the part nobody talks about: what it means to live with the knowledge that this ends, how to have the conversation with the people you love, and why doing this work actually makes you less afraid, not more. The practical and the philosophical are the same project.

```agent-adaptation
# Localization note — death is universal. The paperwork is jurisdiction-specific.
- Advance directive forms, will requirements, and estate law vary by country AND
  by state/province within countries.
  US: State-specific advance directive forms (varies by state), probate law varies
  UK: Lasting Power of Attorney (health and welfare), Wills Act 1837
  Australia: Advance Care Directive (varies by state/territory)
  Canada: Provincial advance directive forms, provincial probate law
  EU: Varies dramatically by country
- Substitute local legal resources:
  US: State bar association free forms, FiveWishes.org
  UK: NHS advance care planning, gov.uk/make-will
  Australia: Advance Care Planning Australia advancecareplanning.org.au
  Canada: Speak Up Canada advancecareplanning.ca
- Organ donation registration processes are country-specific.
  US: organdonor.gov / registerme.org
  UK: NHS Organ Donor Register organdonation.nhs.uk
  Australia: donatelife.gov.au
  Canada: Provincial registries
- Funeral costs and norms vary significantly by culture and country.
  The cost ranges in this skill are US-centric. Adjust for local market.
- Cultural attitudes toward death preparation vary enormously. Some cultures
  consider it unlucky or inappropriate to discuss death planning. The agent
  should acknowledge cultural context while still encouraging practical preparation.
```

## Sources & Verification

- **Five Wishes** -- Advance directive document valid in most US states. [fivewishes.org](https://www.fivewishes.org/)
- **American Bar Association** -- Will and estate planning resources. [americanbar.org/groups/real_property_trust_estate](https://www.americanbar.org/groups/real_property_trust_estate/)
- **AARP** -- End-of-life planning guides. [aarp.org/caregiving/financial-legal/](https://www.aarp.org/caregiving/financial-legal/)
- **National Hospice and Palliative Care Organization** -- Advance care planning resources. [nhpco.org](https://www.nhpco.org/)
- **Atul Gawande** -- "Being Mortal: Medicine and What Matters in the End" (2014). Metropolitan Books.
- **National Funeral Directors Association** -- Cost survey and consumer resources. [nfda.org](https://www.nfda.org/)

## When to Use

- User needs to create a will or advance directive and doesn't know where to start
- Someone has had a health scare and wants to get their affairs in order
- User wants to have the death conversation with family members but doesn't know how
- Someone is processing mortality — their own or a loved one's
- User asks about funeral planning, estate planning, or digital legacy
- Someone wants to do the practical work of being a responsible adult about this
- User is interested in memento mori or mortality awareness as a daily practice

## Instructions

### Step 1: The advance directive — do this today

**Agent action**: Walk the user through creating an advance directive. This is the single highest-priority item.

```
ADVANCE DIRECTIVE (also called a Living Will):

This document tells doctors what you want when you can't speak
for yourself. Without it, your family has to guess — and that
guessing can tear families apart during the worst moment of
their lives.

WHAT IT COVERS:
-> Do you want CPR if your heart stops?
-> Do you want mechanical ventilation (breathing machine)?
-> Do you want artificial nutrition and hydration (feeding tube)?
-> Do you want dialysis?
-> Do you want palliative/comfort care only?
-> Under what conditions do you want treatment stopped?

HEALTHCARE PROXY (also called Healthcare Power of Attorney):
-> This is the person who makes medical decisions for you when
   you can't. Pick ONE person. Not your whole family.
-> Choose someone who: (a) will honor YOUR wishes, not their own,
   (b) can handle pressure from other family members,
   (c) can make hard decisions under stress.
-> Tell this person your wishes IN DETAIL. The document alone
   isn't enough. They need to hear it from you.

HOW TO GET THE FORMS:
-> FiveWishes.org: $5, plain-language form valid in most states
   (widely recognized, written for non-lawyers)
-> Your state's free form: search "[your state] advance directive
   form" — most state bar associations offer free downloads
-> Your doctor's office usually has forms available

REQUIREMENTS (most states):
-> Must be witnessed by 2 adults (restrictions vary by state —
   usually witnesses can't be your healthcare proxy or heirs)
-> Some states require notarization
-> Give copies to: your healthcare proxy, your doctor, your
   hospital, and keep one in your death file (Step 6)

THIS TAKES 30 MINUTES AND COULD SPARE YOUR FAMILY THE WORST
ARGUMENT OF THEIR LIVES. DO IT TODAY.
```

### Step 2: The will — when you need a lawyer and when you don't

**Agent action**: Help the user assess their situation and take the appropriate path.

```
SIMPLE WILL ASSESSMENT:

YOU PROBABLY DON'T NEED A LAWYER IF:
-> Small estate (under your state's threshold — often $100-150K
   excluding home in some states)
-> Straightforward beneficiaries (everything to spouse, then kids)
-> No business ownership
-> No blended family complications
-> No complex tax situations

ONLINE WILL OPTIONS ($100-200, simple estates):
-> LegalZoom, Nolo, Trust & Will, FreeWill
-> These generate legally valid wills for simple situations
-> They walk you through the decisions step by step

YOU NEED A LAWYER IF:
-> Blended family (children from different marriages)
-> Business ownership (succession planning)
-> Significant assets (estate tax threshold: $13.61M federal 2024,
   but some states tax much lower)
-> Special needs beneficiary (requires a special needs trust)
-> Property in multiple states
-> Complex debts or obligations
-> You want to disinherit someone (requirements are strict)

WHAT YOUR WILL MUST INCLUDE:
-> Executor (the person who carries out your wishes — pick someone
   organized, honest, and willing. This is a real job.)
-> Beneficiaries (who gets what)
-> Guardian for minor children (THIS IS CRITICAL if you have kids —
   without it, a court decides)
-> Specific bequests if any (grandma's ring goes to Sarah, etc.)

WHAT A WILL DOESN'T COVER:
-> Retirement accounts (401k, IRA) — these pass by beneficiary
   designation, not by will. CHECK YOUR BENEFICIARY DESIGNATIONS.
   After a divorce, many people forget to update these.
-> Life insurance — same. Beneficiary designation controls.
-> Joint accounts — pass to the surviving owner automatically.
-> Transfer-on-death accounts — pass by designation.

DO NOT skip beneficiary designation review. Many people have
meticulously crafted wills while their 401k still lists
an ex-spouse from 15 years ago.
```

### Step 3: Life insurance — what you actually need

**Agent action**: Cut through the industry confusion. Most people need term life and nothing else.

```
LIFE INSURANCE REALITY:

TERM LIFE INSURANCE:
-> You pay a monthly premium. If you die during the term,
   your beneficiary gets the payout. If you don't die, you
   "lose" the premiums. That's how insurance works.
-> Typical: 20-30 year term, coverage of 10-12x annual income
-> Cost: A healthy 30-year-old can get $500K for $20-30/month
-> THIS IS ALMOST ALWAYS THE RIGHT CHOICE for working people
   with dependents.

WHOLE LIFE INSURANCE:
-> Combines insurance with a savings/investment component
-> Much more expensive (5-15x the cost of equivalent term)
-> The investment returns are mediocre
-> Insurance agents push it because the commissions are enormous
-> For 95% of people, buying term life + investing the difference
   in an index fund is a better financial decision

WHO ACTUALLY NEEDS WHOLE LIFE:
-> Very high net worth individuals (estate tax planning)
-> Business succession situations
-> People who have already maxed out all other tax-advantaged
   investment options
-> Almost nobody else

WHEN YOU DON'T NEED LIFE INSURANCE AT ALL:
-> No dependents (no spouse, no kids, no one relies on your income)
-> Retired with sufficient assets
-> Kids are grown and financially independent

RULE OF THUMB:
If someone depends on your income, you need term life insurance
for 10-12x your annual income. If nobody depends on your income,
you probably don't need it at all.
```

### Step 4: Digital legacy

**Agent action**: Walk through the modern reality of what happens to your digital life.

```
DIGITAL LEGACY CHECKLIST:

PASSWORD MANAGEMENT:
-> Use a password manager (1Password, Bitwarden, etc.)
-> Share vault access with ONE trusted person (emergency kit,
   shared vault, or written master password in a sealed envelope
   in a secure location)
-> Without this, your family cannot access your accounts, photos,
   email, or financial services after you die

ACCOUNT SUCCESSION SETTINGS (set these now):
-> Google: Inactive Account Manager
   (settings > data & privacy > make a plan for your digital legacy)
   Set a trusted contact who gets access after inactivity period
-> Apple: Legacy Contact
   (Settings > [Your Name] > Password & Security > Legacy Contact)
-> Facebook: Memorialization settings or Legacy Contact
   (Settings > General > Memorialization Settings)
-> Instagram: Can be memorialized by family with proof of death

WHAT HAPPENS TO YOUR:
-> Photos: Without access, they're gone. Cloud storage accounts
   close after extended inactivity. Back up locally AND ensure
   someone can access the cloud.
-> Email: Contains keys to your entire digital life. Ensure
   your trusted person can access it.
-> Social media: Each platform has different policies. Set
   preferences now rather than leaving it to grieving family.
-> Subscriptions: Someone needs to cancel these. A list in your
   death file prevents charges from running for months.
-> Cryptocurrency: Without wallet keys, it's gone permanently.
   If you hold crypto, document access thoroughly.

DIGITAL LEGACY DOCUMENT (include in your death file):
-> List of all accounts with the service, username, and
   reference to password manager entry
-> Devices and their passcodes
-> Email accounts (primary key to everything else)
-> Financial accounts accessible only online
-> Subscriptions to cancel
-> Social media preferences (delete, memorialize, or transfer)
-> Any cryptocurrency wallet locations and access methods
```

### Step 5: Funeral preferences

**Agent action**: Present costs and options honestly. This industry profits from grief and confusion.

```
FUNERAL PLANNING:

COST REALITY:
-> Cremation: $1,000-3,000 (direct cremation, no service)
-> Cremation with service: $2,000-5,000
-> Traditional burial: $7,000-12,000 (national median ~$8,300)
-> This includes casket, embalming, funeral home services,
   burial plot, headstone, vault
-> The funeral industry is one of the least transparent on pricing.
   The FTC Funeral Rule REQUIRES funeral homes to give you an
   itemized price list. Ask for it.

PREPAYING FOR FUNERALS:
-> Often a bad deal. Prepayment plans frequently have fine print
   that benefits the funeral home, not you.
-> Better approach: document your preferences and set aside money
   in a payable-on-death savings account earmarked for funeral costs.
-> If you do prepay, make sure the plan is transferable (you might
   move) and that the funds are held in trust (protected if the
   funeral home goes bankrupt).

WHAT TO DOCUMENT (in your death file):
-> Cremation or burial preference
-> Service preference (formal, informal, celebration of life, none)
-> Religious or cultural requirements
-> Music, readings, or specific requests
-> Who you want to officiate
-> Where you want remains (scattered, buried, kept, specific location)
-> Organ donation registration (registerme.org — takes 2 minutes)

ORGAN DONATION:
-> Register at registerme.org or your state's DMV
-> Tell your family your wishes (in some states, family can
   override registration)
-> One organ donor can save 8 lives and enhance 75 more
-> There is no medical condition that automatically disqualifies
   you — doctors make that determination at the time
-> Organ donation does not affect open-casket funeral options
```

### Step 6: The death file

**Agent action**: This is the single most practical thing someone can create for their survivors.

```
THE DEATH FILE:

One folder. Physical or digital (ideally both). Contains everything
someone would need to handle your affairs after you die. One trusted
person knows where it is.

CONTENTS:

LEGAL DOCUMENTS:
-> Will (original or location of original)
-> Advance directive / living will
-> Healthcare proxy designation
-> Power of attorney (financial)
-> Trust documents if applicable
-> Birth certificate, marriage certificate, military discharge papers

FINANCIAL:
-> List of all bank accounts (institution, account type, approximate balance)
-> List of all investment/retirement accounts
-> List of all debts (mortgage, car loan, student loans, credit cards)
-> Life insurance policies (company, policy number, benefit amount)
-> Property deeds
-> Vehicle titles
-> Tax returns (last 3 years)
-> Safe deposit box location and key

INSURANCE:
-> Health insurance
-> Life insurance
-> Home/renters insurance
-> Auto insurance
-> Any other policies

DIGITAL (see Step 4):
-> Password manager access
-> Account list
-> Device passcodes

CONTACTS:
-> Attorney
-> Financial advisor (if any)
-> Insurance agent
-> Accountant/tax preparer
-> Employer HR department
-> Close friends/family to notify

FUNERAL PREFERENCES (see Step 5)

LOCATION:
-> Fireproof safe at home, OR
-> Safe deposit box (but note: these can be sealed at death —
   keep a copy at home too), OR
-> Secure digital location with trusted person access
-> TELL YOUR TRUSTED PERSON WHERE IT IS
```

### Step 7: Having the conversation

**Agent action**: Provide specific scripts. This is the hardest part and people need exact words to start.

```
THE DEATH CONVERSATION:

Nobody wants to have this talk. Have it anyway. Here's how.

OPENING SCRIPTS (pick the one that fits):

With a spouse/partner:
"I want to talk about what happens when one of us dies. Not
because something is wrong — because I love you enough to
make it easier when that day comes. Can we set aside 30 minutes
this weekend?"

With aging parents:
"Mom/Dad, I need to know what your wishes are for medical care
if you can't speak for yourself. I'm not trying to be morbid —
I'm trying to make sure I honor what you actually want instead
of guessing under pressure."

With adult children:
"I've put together a file with everything you'd need if something
happened to me. I want to walk you through where things are.
This isn't a crisis — it's just being organized."

THE CONVERSATION ITSELF:
-> Start with the practical: "Here's where the important
   documents are. Here's who to call."
-> Move to medical wishes: "If I can't speak for myself,
   here's what I want."
-> Address the emotional: "Here's what I want you to know
   now, so I don't run out of time to say it."
-> End with questions: "What do you need to know from me
   that I haven't covered?"

IF THEY RESIST:
-> "I understand this is uncomfortable. It's uncomfortable
   for me too. But the alternative is you making these
   decisions alone, in crisis, with no guidance. I'd rather
   be uncomfortable for an hour now."
-> Don't force it. Plant the seed. Come back to it.
-> Sometimes writing a letter is easier than talking.
```

### Step 8: Memento mori — living with mortality

**Agent action**: Present the philosophical dimension as a daily practice, not an existential crisis.

```
MEMENTO MORI — REMEMBER YOU WILL DIE:

This is not morbid. It's clarifying.

THE PRACTICE:
Periodically — daily if you can manage it — remind yourself
that you will die. Not in a panic. As a fact. Like reminding
yourself that gravity exists.

WHAT THIS DOES:
-> It clarifies priorities. "Would I still be doing this if
   I had one year left?" If the answer is no, ask why you're
   doing it at all.
-> It dissolves pettiness. Most arguments, grudges, and
   resentments become absurd when held up against mortality.
-> It generates urgency for the right things. Tell the people
   you love that you love them. Today. Not when it's convenient.
-> It reduces the fear. Paradoxically, people who think about
   death regularly are less afraid of it than people who avoid
   the subject. Avoidance amplifies fear.

THE EPICUREAN ARGUMENT:
"Where I am, death is not. Where death is, I am not.
Therefore, death is nothing to me."
You will never experience your own death. You'll experience
dying, perhaps, but not death itself. The thing you're afraid
of is something you will, by definition, never encounter.

THE STOIC ARGUMENT:
Death is not in your control. Fearing it is spending energy
on the second list. What IS in your control: how you live
today, what you build, how you treat people, what you leave
behind.

THE PRACTICAL ARGUMENT:
The paperwork from this skill — the will, the advance directive,
the death file — is itself an act of love. You're saying to the
people in your life: "I cared enough about you to make this
easier." That's not morbid. That's the most practical expression
of love there is.

WHAT WOULD YOU STOP DOING IF YOU HAD ONE YEAR LEFT?
Make a list. Then ask yourself why you haven't stopped already.

WHAT WOULD YOU START DOING?
Make that list too. Then start.
```

## If This Fails

- **Family refuses to discuss it?** Write a letter. Put it in the death file. You've done your part even if they won't engage. Come back to the conversation later — sometimes it takes multiple attempts.
- **Overwhelmed by the paperwork?** Do ONE thing today: the advance directive. It takes 30 minutes and it's the highest-impact item. Everything else can wait. Start with Five Wishes if you want a guided format.
- **Can't afford a lawyer for the will?** For simple estates, online will services ($100-200) produce legally valid documents. FreeWill.com is free for basic wills. Your state bar association may offer free legal clinics.
- **Existential spiral instead of productive reflection?** Mortality awareness is supposed to clarify, not paralyze. If thinking about death triggers persistent anxiety, panic, or depression, talk to a therapist. This skill is practical preparation, not exposure therapy for death anxiety. 988 Suicide and Crisis Lifeline if you're in crisis.
- **Don't know where to start on digital legacy?** Start with one thing: set up a password manager if you don't have one. Then add your trusted contact. Everything else follows from having centralized access.

## Rules

- Treat this topic with directness, not delicacy. The user came here for practical help, not euphemisms.
- Never use "passed away," "crossed over," or other softening language unless the user requests it. Use "die," "death," "dead." Clarity matters.
- If the user is in acute grief, this is not the time for paperwork. Acknowledge the loss and offer to come back to the practical items when they're ready.
- Always recommend professional legal help for complex estates, blended families, or significant assets.
- Flag jurisdiction-specific requirements (witnesses, notarization, state forms) rather than giving blanket advice.
- The philosophical and the practical reinforce each other. Don't skip the philosophical sections — they're what motivate people to actually do the paperwork.

## Tips

- The advance directive is the single most important document in this skill. If you do nothing else, do that.
- Update your will and beneficiary designations after every major life event: marriage, divorce, birth, death, major asset change.
- Your death file doesn't help anyone if nobody knows it exists. Tell your trusted person where it is. Today.
- Organ donation registration takes 2 minutes at registerme.org. Do it now while you're thinking about it.
- The conversation gets easier the second time. The first time is the hardest. Every time after that, it's just an update.
- Prepaying for a funeral is almost never the best financial move. Document your wishes and set aside money in a POD account instead.

## Agent State

```yaml
state:
  preparation:
    advance_directive_completed: false
    healthcare_proxy_designated: false
    will_completed: false
    will_type: null  # online, attorney, none
    life_insurance_reviewed: false
    beneficiary_designations_checked: false
    digital_legacy_configured: false
    funeral_preferences_documented: false
    organ_donation_registered: false
    death_file_created: false
    death_file_location: null
    trusted_person_informed: false
  conversations:
    spouse_conversation_had: false
    parents_conversation_had: false
    children_conversation_had: false
  context:
    trigger: null  # health_scare, responsible_planning, loss_of_loved_one, curiosity
    urgency: null  # immediate, near_term, long_term
    estate_complexity: null  # simple, moderate, complex
  follow_up:
    next_review_date: null
    items_remaining: []
```

## Automation Triggers

```yaml
triggers:
  - name: advance_directive_priority
    condition: "preparation.advance_directive_completed IS false"
    action: "The advance directive is the single most important item here. Without it, your family has to guess what you'd want while they're in crisis. It takes 30 minutes. Want to start with that?"

  - name: beneficiary_check
    condition: "preparation.will_completed IS true AND preparation.beneficiary_designations_checked IS false"
    action: "Your will is done, but have you checked your beneficiary designations on retirement accounts, life insurance, and bank accounts? These override your will. Many people have wills that say one thing while their 401k beneficiary form still lists an ex-spouse."

  - name: death_file_reminder
    condition: "preparation.death_file_created IS true AND preparation.trusted_person_informed IS false"
    action: "You've created your death file, but does anyone know where it is? A death file that nobody can find is the same as no death file. Tell your trusted person where it is this week."

  - name: conversation_prompt
    condition: "preparation.advance_directive_completed IS true AND preparation.will_completed IS true AND conversations.spouse_conversation_had IS false"
    action: "The paperwork is done. Now the harder part: have you talked to your family about your wishes? The documents help, but the conversation is what really prepares them. Want to go through the conversation scripts?"

  - name: annual_review
    condition: "preparation.death_file_created IS true"
    schedule: "annually"
    action: "Annual death file review: any major life changes this year (marriage, divorce, birth, death, job change, move, major asset change)? If yes, your will, beneficiary designations, and advance directive may need updates."
```
