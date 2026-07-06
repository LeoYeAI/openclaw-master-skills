---
name: blue-collar-mental-health
description: >-
  Mental health support designed for workers in trades, service, and physical occupations. Use when someone in a physical job is struggling with stress, substance use, anger, isolation, or burnout and traditional mental health resources feel inaccessible.
metadata:
  category: mind
  tagline: >-
    Mental health tools built for people in physical jobs — where "talk to a therapist" is culturally and financially unrealistic as a first step.
  display_name: "Blue-Collar Mental Health Toolkit"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/blue-collar-mental-health"
---

# Blue-Collar Mental Health Toolkit

"Just talk to a therapist" is great advice if you have insurance that covers it, a schedule that allows it, and a workplace culture that doesn't treat it as weakness. Most people in trades, service, and physical jobs have none of those three things. Construction has the second-highest suicide rate of any industry. Food service workers have depression rates double the national average. This skill doesn't pretend those barriers don't exist. It starts where you actually are — on the job, on the clock, dealing with it — and works from there.

This skill references and extends: burnout-recovery, anxiety-emergency, someone-is-struggling.

```agent-adaptation
# Localization note — mental health stigma, access, and crisis resources vary by jurisdiction.
- Crisis lines:
  US: 988 Suicide & Crisis Lifeline (call or text 988), Crisis Text Line (text HOME to 741741)
  UK: Samaritans (116 123, free 24/7), SHOUT (text SHOUT to 85258)
  AU: Lifeline (13 11 14), Beyond Blue (1300 22 4636)
  CA: 988 (national), Crisis Services Canada (1-833-456-4566)
  NZ: Need to Talk? (1737)
- EAP equivalents:
  UK: Often provided through employer or union. NHS also provides IAPT (free therapy).
  AU: EAP common in larger employers. Beyond Blue has workplace programs.
  CA: Most employers with 50+ workers offer EAP.
- In countries with universal healthcare (UK, AU, CA), therapy access is broader but
  wait times can be long. Provide both public and private pathways.
- Industry-specific programs:
  US: Construction Industry Alliance for Suicide Prevention
  AU: MATES in Construction (mates.org.au) — peer support model
  UK: Lighthouse Construction Industry Charity
  CA: Construction Safety Nova Scotia mental health resources
- Substance use resources: Swap AA/NA with local equivalents. SMART Recovery is
  international. In UK, NHS drug/alcohol services via FRANK helpline.
```

## Sources & Verification

- **CDC Workplace Mental Health** -- Surveillance data on mental health by industry and occupation. https://www.cdc.gov/workplacehealthpromotion/
- **Construction Industry Alliance for Suicide Prevention** -- Industry-specific prevention tools and training. https://preventconstructionsuicide.com
- **SAMHSA** -- Substance Abuse and Mental Health Services Administration. National helpline and treatment locator. https://www.samhsa.gov
- **988 Suicide & Crisis Lifeline** -- 24/7 crisis support via call or text. https://988lifeline.org
- **Journal of Occupational Health Psychology** -- Research on mental health outcomes in blue-collar and service occupations.
- **MATES in Construction (AU)** -- Peer support model for construction industry mental health. https://mates.org.au
- **Anthropic, "Labor market impacts of AI"** -- March 2026 research showing this occupation/skill area has near-zero AI exposure. https://www.anthropic.com/research/labor-market-impacts

## When to Use

- Someone in a physical job says they're "fine" but their behavior has changed
- User mentions increased drinking, anger, sleep problems, or withdrawal from people
- Explicitly asks for mental health help but dismisses therapy as an option
- Burnout symptoms in a trades/service/physical job context
- Coworker seems to be struggling and user wants to know how to approach them
- Mentions suicidal thoughts or self-harm — trigger immediate crisis protocol
- Has tried generic mental health advice and found it useless for their situation

## Instructions

### Step 1: Recognize the Warning Signs in Yourself

**Agent action**: Present the self-check list without clinical jargon. Direct language.

Most people in physical jobs don't wake up one day and think "I need mental health support." It's a slow slide. Here's what it actually looks like:

```
HONEST SELF-CHECK
Check anything that's been true for the last 2+ weeks:

[ ] Sleep is off — can't fall asleep, can't stay asleep, or sleeping way more than usual
[ ] Drinking more than 6 months ago — more often, more volume, or drinking alone
[ ] Shorter temper — snapping at coworkers, family, or over things that didn't used to bother you
[ ] Pulling away from people — turning down plans, not answering texts, eating alone
[ ] Body symptoms you can't explain — constant headaches, stomach problems,
    chest tightness, jaw clenching
[ ] Dreading work not because of the work, but because of everything
[ ] Lost interest in stuff you used to enjoy — hobbies, sex, food, hanging out
[ ] Thoughts like "what's the point" or "everyone would be better off without me"
[ ] Using anything to numb out — substances, screens, food, gambling
[ ] More risk-taking on the job — not caring about safety the way you used to

0-2 checked: Normal stress range. Monitor it.
3-5 checked: Yellow flag. Use the tools in this skill. Tell one person.
6+ checked: Red flag. You need support beyond self-help. See Step 7.

If you checked the "what's the point" or "better off without me" box:
Stop here. Text or call 988 now. Or text HOME to 741741. This is the step.
```

### Step 2: The 5-Minute Reset

**Agent action**: Walk the user through the physiological reset technique they can use on a break.

This is for the moment when you're about to lose it — rage, panic, shutdown. You have 5 minutes on break. Here's what actually works, based on neuroscience, not motivational posters.

```
5-MINUTE RESET (do these in order)

1. PHYSIOLOGICAL SIGH (30 seconds)
   - Double inhale through nose: one big breath in, then one more small sip of air
     on top of it.
   - Long, slow exhale through mouth. Twice as long as the inhale.
   - Repeat 3 times.
   - This activates your parasympathetic nervous system faster than any other
     breathing technique. Discovered by Stanford researchers (Huberman Lab).

2. COLD WATER ON FACE (30 seconds)
   - Splash cold water on your face, especially forehead and cheeks.
   - Or hold a cold can/bottle against your face and wrists.
   - This triggers the mammalian dive reflex — involuntary heart rate reduction.
   - Works even when "breathing exercises feel stupid."

3. 2-MINUTE WALK (2 minutes)
   - Walk away from the situation. Doesn't matter where.
   - Bilateral movement (walking) helps the brain process stress.
   - Don't talk to anyone. Don't check your phone. Just walk.

4. NAME IT (1 minute)
   - Mentally say: "I am feeling [angry/anxious/overwhelmed/hopeless]. This is a
     feeling, not a fact. It will change."
   - Naming the emotion reduces amygdala activation by up to 50%.
     (UCLA research, Lieberman et al.)

Total time: ~5 minutes. No one needs to know you did it.
```

### Step 3: Substance Use Self-Assessment

**Agent action**: Present a non-judgmental self-assessment. No moralizing.

```
HONEST QUESTIONS — NOT A LECTURE
Read these. Answer in your head. Nobody's checking.

1. Is your after-work drinking the same as it was 6 months ago? 12 months ago?
   If it's trending up, that's information.

2. Do you drink (or use) to feel normal, or to feel good? "I need a beer to unwind"
   is different from "I want a beer because today was good."

3. Have you tried to cut back and failed? Even once?

4. Are you hiding how much you're using from anyone? Partner, coworker, doctor?

5. Has anyone said something? Even casually — "you've been drinking a lot lately"?

6. Are mornings harder than they should be? Not just tired — shaky, nauseous, anxious
   until the first drink?

If 2+ of these are hitting differently than you'd like, something is shifting.
This isn't about being an "alcoholic" or not. That binary isn't useful.
It's about whether your use is still working for you or starting to work against you.

WHAT TO DO WITH THAT INFORMATION:
- Option 1: Try 30 days without. Not forever. Just 30 days. See how you feel.
- Option 2: Call SAMHSA helpline (1-800-662-4357). Free, confidential, 24/7.
  They don't show up at your job. They help you figure out options.
- Option 3: SMART Recovery (smartrecovery.org). Evidence-based, not 12-step.
  Online meetings. No religious component. Free.
```

### Step 4: Check on a Coworker Without Being Weird

**Agent action**: Provide specific conversation scripts for peer support.

```
HOW TO ASK IF SOMEONE'S OKAY — SCRIPTS THAT ACTUALLY WORK

The goal: Open a door. Not kick it down.

OPENING LINES:
- "Hey, you don't seem like yourself lately. Everything good?"
- "I noticed you've been quiet. Just checking in."
- "You seem stressed. Want to grab a coffee and talk about whatever?"

DON'T SAY: "You need a therapist" (wall goes up), "Just think positive"
(insulting), "At least you have a job" (minimizing), "Man up" (the problem).

IF THEY OPEN UP: Listen. Don't fix, compare, or one-up. "That sounds really
hard" is a complete sentence. If they mention self-harm: "I'm taking that
seriously. Can we call 988 together?" Don't promise secrecy.

IF THEY BRUSH IT OFF: "Alright. I'm here if that changes." Check in again
in a week. Consistency matters more than one conversation.
```

### Step 5: The 90-Second Rule for Anger

**Agent action**: Explain the physiological anger cycle and how to use it.

```
ANGER — THE 90-SECOND REALITY

When rage hits, your body dumps adrenaline and cortisol: hot face, tight chest,
clenched jaw, tunnel vision. That chemical surge peaks and DISSIPATES in 90
seconds. Anything after that is you re-engaging the anger by replaying the
situation. The physiology is done. The story keeps it alive.

THE PROTOCOL:
1. Feel the surge. Acknowledge it: "I'm furious right now."
2. DO NOTHING for 90 seconds. Don't speak. Don't text. Don't punch anything.
   If you're in a conversation, say "I need a minute" and walk away.
3. After 90 seconds, the heat drops. Now you can think.
4. Decide: Is this worth responding to? If yes, respond from the cool state,
   not the hot state.

This isn't about suppressing anger. Anger is useful information — it tells you a
boundary was crossed. The 90-second rule is about not making a decision during
the worst possible moment to make one.

WHERE THIS MATTERS MOST:
- Responding to a boss who disrespected you in front of the crew
- Handling a conflict with a coworker
- Reacting to a partner after a bad shift
- Dealing with a customer who's wrong and won't stop talking
```

### Step 6: Access Help Without Stigma

**Agent action**: Present concrete, low-barrier options for professional support.

```
RESOURCES YOU PROBABLY DON'T KNOW YOU HAVE

EAP (Employee Assistance Program):
- Most employers with 50+ workers offer this. 3-8 free sessions. Confidential.
- Also covers: financial counseling, legal consultation, substance use.
- Ask HR "Do we have an EAP?" or check your benefits paperwork.

UNION: Check your union's member assistance program (MAP). Many unions (IBEW,
UA, Laborers, SEIU) have mental health and peer support programs.

CRISIS (immediate, free):
- 988 Suicide & Crisis Lifeline: Call or text 988. 24/7.
- Crisis Text Line: Text HOME to 741741.
- SAMHSA Helpline: 1-800-662-4357.

LOW-COST THERAPY:
- Open Path Collective (openpathcollective.org): $30-80/session.
- Sliding scale: Search "sliding scale therapy [your city]."
- Community mental health centers: Federally funded, fee based on income.
- psychologytoday.com: Filter by sliding scale.
```

### Step 7: Relationship Strain from Job Stress

**Agent action**: Provide communication templates for partners dealing with a physically/emotionally exhausted worker.

```
Common pattern: 10-12 hours of physical labor, come home with nothing left.
Partner feels ignored. Fights happen.

TEMPLATE: "I know I've been [distant/short/checked out]. It's not about you.
My job is draining me more than I'm recovering. Here's what I need: [specific
request]. What do you need from me?"

THE 20-MINUTE TRANSITION: When you get home, take 20 minutes before engaging.
Shower, change, sit. This is the reset between work mode and home mode. Tell
your partner why. Most will respect a defined transition. They won't respect
indefinite withdrawal.

IF IT'S BEYOND A CONVERSATION: EAP often covers couples sessions. On a budget:
"Hold Me Tight" by Sue Johnson — most evidence-based couples book. $15.
```

### Step 8: When It's Beyond Self-Help

**Agent action**: If user's responses indicate clinical severity, provide direct guidance. No euphemisms.

```
WHEN TO GET PROFESSIONAL HELP — NO SUGARCOATING

NOW (call 988, text 741741, or go to an ER):
- Thinking about suicide or self-harm
- Can't stop using substances despite wanting to
- Less than 3-4 hours sleep for 2+ weeks straight
- Panic attacks at work or driving
- Thoughts of hurting someone else

SOON (within 2 weeks):
- Self-check scored 6+. Hopeless/empty for a month+. Work performance slipping.
- Unexplained physical symptoms. Substance use increasing for 3+ months.

DEPRESSION QUICK SCREEN (PHQ-2):
Over 2 weeks, how often bothered by: (1) Little interest or pleasure in things?
(2) Feeling down, depressed, or hopeless? Score 0-3 each. Total 3+ = see a provider.
```

## If This Fails

- "Breathing thing didn't work": Practice it 5 times when NOT stressed first. It's a skill, not magic.
- "EAP therapist doesn't get my life": Request someone experienced with blue-collar or first responder populations. You can switch.
- "Can't talk about this at work": Crisis text line is texting. Online therapists (BetterHelp) run $60-80/month.
- "Nothing helps": After 3+ months of genuine effort, this may be a medication conversation. Primary care can prescribe SSRIs. You don't need a psychiatrist to start.

## Rules

- Never tell someone to "just be positive" or "things could be worse." Those aren't support. They're dismissals.
- If someone mentions suicide or self-harm, respond with crisis resources immediately. Don't try to be their therapist. Connect them to trained crisis responders.
- Don't diagnose. This skill helps people recognize patterns and find resources. Diagnosis is for licensed professionals.
- Confidentiality matters. If a coworker opens up to you, don't tell the crew. The exception: if they're in danger of harming themselves or others.
- Substances aren't the enemy — unaddressed pain is. Approach substance use with curiosity, not judgment.

## Tips

- The 5-minute reset works better than you think. Most people never try it because it seems too simple. Do it for a week before you judge it.
- Writing down what's bothering you — even on a scrap of paper you throw away — reduces the mental load measurably. Research calls it "expressive writing." You can call it getting it out of your head.
- Physical labor provides some mental health benefits on its own (movement, social connection, tangible results). If those have stopped working, that's significant information.
- The biggest barrier to getting help is the first phone call. Many crisis lines now offer text. Use text if calling feels like too much.
- If your employer offers mental health days, use them. They exist for this. If they don't offer them, call in sick. A day of actual rest prevents a week of declining performance.
- Men in trades are at especially high risk and especially unlikely to seek help. If you're reading this as a supervisor or business owner: making it okay to not be okay is the most impactful safety measure you can implement.

## Agent State

```yaml
mental_health_session:
  self_check_score: null
  primary_concerns: []
  substance_use_flagged: false
  crisis_risk_level: "not_assessed"
  eap_available: null
  resources_provided: []
  referral_made: false
  related_skills_referenced: []
```

## Automation Triggers

```yaml
triggers:
  - name: crisis_detection
    condition: "user mentions suicidal thoughts, self-harm, or hopelessness"
    schedule: "immediate"
    action: "Provide crisis resources (988, Crisis Text Line) immediately before any other response"
  - name: substance_escalation_check
    condition: "user mentions increased substance use over 3+ months"
    schedule: "on_demand"
    action: "Run substance use self-assessment and provide SAMHSA helpline and SMART Recovery resources"
  - name: burnout_crossref
    condition: "user scores 6+ on self-check or describes burnout symptoms"
    schedule: "on_demand"
    action: "Reference burnout-recovery skill and recommend professional evaluation"
```
