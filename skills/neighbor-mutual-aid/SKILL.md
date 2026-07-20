---
name: neighbor-mutual-aid
description: >-
  Setting up a hyperlocal mutual aid network with neighbors. Use when someone wants to build community resilience, organize neighbors for mutual support, share resources, or create emergency preparedness networks on their block or in their building.
metadata:
  category: life
  tagline: >-
    Build a practical support network on your block -- tool sharing, emergency contacts, group purchasing, and babysitting exchanges in one afternoon.
  display_name: "Neighbor Mutual Aid Setup"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install neighbor-mutual-aid"
---

# Neighbor Mutual Aid Setup

Most people live within 50 feet of others and know almost none of them. A mutual aid network is not a political project or a commune -- it's a practical arrangement where nearby humans agree to share resources, watch out for each other, and coordinate during emergencies. The setup takes one afternoon of door-knocking and one sheet of paper. The payoff is knowing who has a truck when you need to move something, who's a nurse when someone falls, and who can grab your kid from school if you're stuck at work.

```agent-adaptation
# Localization note
- Community structures, housing types, and cultural norms around neighbor contact vary hugely
- Apartment building (buzz intercom, leave flyer under doors, talk to building manager first)
  vs. suburban block (walk up to front doors) vs. rural (longer distances, fewer neighbors, more self-reliance)
- Cultural directness norms differ: in some cultures, knocking unannounced is normal;
  in others, a written note first is more appropriate
- Adjust for local emergency numbers (911 in US, 999 in UK, 112 in EU, 000 in Australia)
- Swap local disaster types (earthquake, hurricane, tornado, bushfire, flooding)
- Group purchasing sources and co-op structures vary by country
```

## Sources & Verification

- **Mutual Aid Hub** -- directory of mutual aid networks and organizing resources. https://www.mutualaidhub.org
- **FEMA CERT Program** -- Community Emergency Response Team training and neighborhood preparedness frameworks. https://www.ready.gov/cert
- **Big Door Brigade** -- mutual aid organizing resources and practical guides. https://bigdoorbrigade.com
- **Neighborhood tool library models** -- Little Free Library concept applied to tools, operating in 50+ US cities
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- User wants to know their neighbors but doesn't know how to start
- Someone just moved to a new neighborhood and wants to build connections
- User is worried about emergency preparedness and wants a local support system
- Someone wants to share tools, childcare, or bulk purchasing with neighbors
- User lives alone and wants a check-in system with nearby people
- A disaster or emergency just happened and the user realizes they have no local network
- User wants to reduce expenses through resource sharing

## Instructions

### Step 1: Map Your Block

**Agent action**: Help the user create a simple map of their immediate neighborhood -- who lives where and what they already know about them.

```
BLOCK MAPPING EXERCISE (15 minutes)

Draw a rough sketch of your block or building floor. For each unit/house:

1. Write the address or unit number
2. Write names if you know them (first name is fine)
3. Note anything you already know:
   - Approximate age range (young family, retired, etc.)
   - Pets (you'll see them outside)
   - Vehicles (truck owners are gold for mutual aid)
   - Visible skills (someone always doing yard work = gardening knowledge)

DON'T OVERTHINK THIS. You're not surveilling anyone.
You're just writing down what you already passively know.

Target: 8-15 households for a suburban block, 6-10 for an apartment floor
```

### Step 2: The Door-Knock Script

**Agent action**: Provide the user with a tested door-knocking script and coach them on the approach. This is the hardest part -- most people are nervous about it. Normalize that.

```
DOOR-KNOCK PROTOCOL

When to go: Saturday or Sunday, 10am-12pm or 4-6pm
What to bring: A one-page flyer (template below) and a pen
What to wear: Normal clothes. Not a clipboard-and-lanyard vibe.

OPENING SCRIPT (adjust to your personality):

"Hi, I'm [name], I live at [address/unit]. I'm putting together a
neighborhood contact list -- just so we know each other and can help
out in emergencies or share resources. Takes about 2 minutes. Would
you be interested?"

IF THEY SAY YES:
Walk through the 5-question survey (Step 3).
Leave them the flyer. Ask for their preferred contact method.

IF THEY SAY NO OR SEEM UNCOMFORTABLE:
"No problem at all. Here's my number if you ever need anything."
Hand them the flyer and move on. No pressure. Ever.

IF NOBODY'S HOME:
Leave the flyer with a handwritten note:
"Hi neighbor -- I'm [name] at [address]. Putting together a block
contact list for emergencies and resource sharing. Text me if
you're interested: [phone number]"

EXPECT: About 60-70% positive response rate. Some people will be
thrilled someone finally did this. Some won't be interested. Both
are fine.
```

### Step 3: The 5-Question Neighbor Survey

**Agent action**: Generate a simple survey the user can fill out during each conversation. This is the core data-gathering step.

```
NEIGHBOR RESOURCE SURVEY

(Fill out during the door-knock conversation. Keep it casual.)

Name: _______________    Address/Unit: _______________
Phone: _______________   Email (optional): _______________
Preferred contact method:  Text / Call / Email / Signal / WhatsApp

1. SKILLS: Do you have any medical training, mechanical skills,
   trade skills, or other expertise? (nurse, electrician, plumber,
   EMT, teacher, IT, etc.)
   _______________________________________________

2. EQUIPMENT: Do you have any of these you'd be willing to lend
   occasionally? (Check all that apply)
   [ ] Truck/van/trailer    [ ] Ladder (what height? ___)
   [ ] Power tools           [ ] Generator
   [ ] Chainsaw              [ ] First aid kit
   [ ] Jumper cables         [ ] Snow blower
   [ ] Lawn mower            [ ] Other: _______________

3. EMERGENCY: Is there anyone in your household who might need
   extra help in an emergency? (Elderly person, infant, someone
   with mobility issues, medication-dependent, etc.)
   _______________________________________________

4. AVAILABILITY: Would you be open to any of these?
   [ ] Emergency contact exchange (call me if something's wrong)
   [ ] Key exchange (I can check on your place when you travel)
   [ ] Tool/equipment lending
   [ ] Group purchasing (bulk food, supplies)
   [ ] Babysitting/childcare swap
   [ ] Pet care coverage (feed cat, walk dog when you're away)
   [ ] Seasonal help (snow removal, storm prep, yard work)

5. OTHER: Anything else you'd want from a neighborhood network?
   _______________________________________________
```

### Step 4: Build the Neighborhood Resource Sheet

**Agent action**: Compile survey results into a one-page resource sheet. Generate it as a formatted document the user can print and distribute.

```
NEIGHBORHOOD RESOURCE SHEET (template)

[YOUR BLOCK/BUILDING NAME] -- Emergency & Resource Contacts
Last updated: [DATE]

EMERGENCY CONTACTS:
- Fire/Police/Ambulance: 911
- Poison Control: 1-800-222-1222
- Non-emergency police: [local number]

NEIGHBOR CONTACT LIST:
Name          | Address | Phone        | Key Skills/Resources
______________|_________|______________|____________________
              |         |              |
              |         |              |
              |         |              |
(continue for all participating neighbors)

SHARED RESOURCES AVAILABLE:
- Truck/trailer: [Name, phone]
- Generator: [Name, phone]
- Ladder (extension): [Name, phone]
- Medical training: [Name, phone]
- Mechanical/trade skills: [Name, phone]

SEASONAL COORDINATION:
- Snow removal rotation: [names]
- Storm prep lead: [name]
- Yard waste coordination: [name]

EMERGENCY PLAN:
- Meeting point (if evacuation needed): [location]
- Who checks on who:
  [Name] checks on [Name] (elderly/needs assistance)
  [Name] checks on [Name]

PRINT THIS. Put it on your fridge. Give a copy to every
participating household.
```

### Step 5: Set Up Specific Exchange Systems

**Agent action**: Based on survey responses, help the user set up whichever exchange systems neighbors expressed interest in.

```
TOOL/EQUIPMENT LENDING LIBRARY

Simple system -- no apps needed:
1. Create a shared note (Google Doc, group text, or physical binder)
2. List every item available for lending and who owns it
3. Rules:
   - Text the owner to borrow, return within 48 hours
   - Return clean and in working order
   - If you break it, you replace it or pay for repair
   - No lending to non-network people without owner's OK

GROUP PURCHASING

Best items for bulk buying:
- Paper products (toilet paper, paper towels) -- 30-40% savings
- Cleaning supplies -- 25-35% savings
- Non-perishable food (rice, beans, canned goods) -- 20-30% savings
- Seasonal supplies (salt, firewood, garden soil) -- 20-40% savings

How to run it:
1. One person places the Costco/warehouse order
2. Split cost proportionally
3. Distribute from one location (garage, lobby)
4. Rotate who places the order each month
5. Use Splitwise or Venmo to settle up

BABYSITTING/CHILDCARE EXCHANGE

Credit system works best:
1. Track hours with a shared spreadsheet
2. 1 hour of watching = 1 credit
3. Use credits to get coverage from another parent
4. Maximum "debt" of 5 hours before you need to give back
5. Emergency coverage (sick kid, stuck at work) doesn't cost credits
6. All participating parents meet first so kids know every adult

PET CARE COVERAGE

1. Exchange house keys or provide lockbox codes
2. Each pet owner writes a one-page care sheet:
   - Feeding schedule, amounts, brand
   - Medication if any
   - Vet name and number
   - Behavioral notes (leash reactive, hides under bed, etc.)
3. Do a practice run while you're home so the pet knows the neighbor
```

### Step 6: Apartment Building Variation

**Agent action**: If the user lives in an apartment building, adapt the approach for that context.

```
APARTMENT BUILDING ADAPTATION

Different challenges, same concept.

GETTING STARTED:
- Talk to building manager first. Some buildings have rules about
  door-to-door contact. Get permission or at least a heads-up.
- Use the mailroom, lobby, or laundry room as your "town square"
- Post a flyer on the community board before knocking
- Start with your floor only, then expand

WHAT CHANGES:
- No tool lending library (storage is the issue -- keep it small)
- Package watching is the #1 easy win (accept packages for each other)
- Noise coordination matters (text before a party, agree on quiet hours)
- Emergency check-ins are more critical (people can be isolated for days
  in apartments without anyone noticing)
- Shared laundry scheduling can reduce conflict
- Group purchasing works great (one delivery split across units)

WHAT STAYS THE SAME:
- Emergency contact exchange
- Skills inventory
- Key exchange for emergencies
- Pet care and childcare swaps
- The fundamental pitch: "We live 10 feet apart. We should at least
  know each other's names."
```

### Step 7: Maintain the Network

**Agent action**: Help the user set up lightweight maintenance so the network doesn't die after the first month.

```
KEEPING IT ALIVE (minimal effort version)

QUARTERLY:
- Update the contact sheet (new neighbors, moves, changed numbers)
- One casual gathering per season (doesn't have to be fancy --
  front yard hangout, building lobby coffee, block party)

ANNUALLY:
- Refresh the resource survey (people get new tools, learn new skills)
- Review and update emergency plans
- Restock shared emergency supplies if applicable

ONGOING:
- Group text/chat for time-sensitive things (storm warning, suspicious
  activity, lost pet, "does anyone have a Phillips head screwdriver")
- Use the network. Borrow the ladder. Ask for help moving the couch.
  The more people use it, the stronger it gets.
- Welcome new neighbors. Knock on their door within the first month.
  Give them the resource sheet. This is how the network grows.

WHO COORDINATES:
- You started it, so you're the coordinator for now
- After 6 months, ask if someone else wants to share or take over
- It doesn't need a leader. It needs someone willing to send
  the occasional group text.
```

## If This Fails

- If door-knocking feels impossible, start with just one neighbor you already wave to. Build from there.
- If your building management blocks organizing, frame it as "emergency preparedness" -- harder to object to.
- If nobody responds to flyers, try the "I just baked too many cookies" approach -- show up with food and introduce yourself.
- If the network fizzles after a month, it's not dead. Send one group text next time there's a storm warning. Activity revives networks.
- If one neighbor is difficult or creates drama, you can have a network that doesn't include everyone. It's voluntary.

## Rules

- Never pressure anyone to participate. Voluntary only, always.
- Don't collect more personal information than people are comfortable sharing
- The contact sheet stays within the network -- never share it with outside parties, landlords, or on social media
- Start small (your immediate 5-8 neighbors) before trying to organize the whole block
- This is about practical mutual support, not political organizing or activism
- Respect that some people have good reasons for wanting privacy. Don't take "no" personally.

## Tips

- Food is the universal icebreaker. Bring cookies, banana bread, or whatever you make when you knock on doors. It changes the whole dynamic.
- The group text is the most-used feature of any neighborhood network. Start there if nothing else.
- Tool lending alone saves most households $200-500 per year. Lead with that if people need a practical reason.
- Parents with young kids are almost always the most enthusiastic participants. Start with them.
- Holiday coordination (trick-or-treating routes, block yard sales, shared decorating) builds social glue without requiring deep trust.
- Elderly neighbors are often the most isolated and the most grateful for inclusion. Make sure they're on the list.
- Keep the group text to one platform. Don't split across SMS, WhatsApp, Signal, and Nextdoor. Pick one and commit.

## Agent State

```yaml
mutual_aid:
  network_status: null
  block_mapped: false
  households_contacted: 0
  households_participating: 0
  contact_sheet_created: false
  exchanges_active:
    tool_lending: false
    group_purchasing: false
    childcare_swap: false
    pet_care: false
    emergency_contacts: false
    key_exchange: false
  housing_type: null
  last_updated: null
  next_gathering: null
  coordinator: null
```

## Automation Triggers

```yaml
triggers:
  - name: seasonal_coordination
    condition: "network_status IS 'active'"
    schedule: "quarterly"
    action: "Time for a seasonal check-in with your neighborhood network. Update the contact sheet, plan a casual gathering, and coordinate any seasonal needs (storm prep, snow removal rotation, yard waste, etc.)."

  - name: new_neighbor_welcome
    condition: "network_status IS 'active' AND user_reports_new_neighbor"
    action: "A new neighbor moved in. Within the first two weeks, knock on their door with the resource sheet and introduce the network. First impressions set the tone -- keep it casual and low-pressure."

  - name: network_revival
    condition: "network_status IS 'active' AND last_updated > 90 days"
    action: "Your neighborhood network hasn't had any activity in 3 months. Send a group text with something simple -- a weather warning, a question, or an invite to a front-yard hangout. Networks stay alive through use."

  - name: emergency_prep_check
    condition: "network_status IS 'active'"
    schedule: "annually"
    action: "Annual emergency preparedness review for your neighborhood network. Refresh the resource survey, update emergency contacts, review who checks on who during emergencies, and verify everyone still has the current contact sheet."
```
