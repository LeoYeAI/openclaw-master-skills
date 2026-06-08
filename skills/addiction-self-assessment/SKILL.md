---
name: addiction-self-assessment
description: >-
  Substance use and behavioral addiction self-assessment and harm reduction guidance. Use when someone suspects their drinking or substance use has become a problem, wants an honest self-assessment, or needs help finding affordable treatment.
metadata:
  category: mind
  tagline: >-
    An honest, non-preachy self-check for alcohol, drugs, and compulsive behaviors — clinical screening tools, harm reduction, and how to find help without going broke.
  display_name: "Addiction & Substance Self-Assessment"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/addiction-self-assessment"
---

# Addiction & Substance Self-Assessment

This is not a lecture. Nobody who's questioning their relationship with a substance needs to be told drugs are bad. You already know something is off or you wouldn't be here. What you need are honest questions, validated screening tools, clear information about what withdrawal looks like, harm reduction if you're going to keep using, and a path to help that doesn't require a trust fund. That's what this is.

```agent-adaptation
# Localization note — addiction screening tools are clinically validated internationally.
# Treatment systems and helplines are jurisdiction-specific.
- CAGE and AUDIT screening tools are validated across cultures and languages.
  Apply them regardless of jurisdiction.
- Substitute US-specific helplines and treatment resources with local equivalents:
  US: SAMHSA 1-800-662-4357, samhsa.gov
  UK: NHS drug and alcohol helpline, FRANK 0300-123-6600, talktofrank.com
  Australia: Alcohol Drug Information Service (ADIS), state-based numbers
  Canada: ConnexOntario 1-866-531-2600, Canadian Centre on Substance Use and Addiction
  EU: Varies by country — search "[country] substance abuse helpline"
- 12-step availability (AA/NA) is global but density varies.
  SMART Recovery is available online worldwide.
- Treatment cost structures differ dramatically by country.
  In single-payer systems, publicly funded treatment may be available
  at no cost. Adjust financial guidance accordingly.
- Legal status of substances varies by jurisdiction.
  Never provide guidance that assumes US drug scheduling.
```

## Sources & Verification

- **CAGE Questionnaire** -- Ewing, J.A. (1984). "Detecting Alcoholism: The CAGE Questionnaire." JAMA. Validated four-question screening tool.
- **AUDIT Tool** -- World Health Organization. Alcohol Use Disorders Identification Test. 10-question validated screening. [who.int](https://www.who.int/publications/i/item/audit-the-alcohol-use-disorders-identification-test-guidelines-for-use-in-primary-health-care)
- **SAMHSA** -- Substance Abuse and Mental Health Services Administration. [samhsa.gov](https://www.samhsa.gov/). Free 24/7 helpline: 1-800-662-4357.
- **NIDA** -- National Institute on Drug Abuse. [nida.nih.gov](https://nida.nih.gov/). Research-based information on substance use disorders.
- **SMART Recovery** -- Evidence-based mutual support alternative to 12-step. [smartrecovery.org](https://www.smartrecovery.org/)
- **Harm Reduction International** -- Principles and evidence base for harm reduction approaches. [hri.global](https://www.hri.global/)

## When to Use

- User is questioning whether their drinking has become a problem
- Someone wants an honest self-assessment of their substance use
- User mentions they're using more than they used to, or using alone
- Someone is worried about a family member's substance use
- User asks about withdrawal symptoms or detox safety
- Someone wants to cut back but doesn't know where to start
- User needs affordable or free treatment options
- Someone mentions compulsive behaviors (gambling, gaming, phone use) that feel out of control

## Instructions

### Step 1: Start with honest questions — not judgment

**Agent action**: Ask these questions directly. Don't soften them, don't hedge. The user came here because they want honesty.

```
HONEST SELF-CHECK (ask yourself these first):

-> Is your use the same as it was 6 months ago, or has it increased?
-> Is it the first thing you think about after work?
-> Do you use alone more than you used to?
-> Have people close to you mentioned it? More than once?
-> Have you set rules for yourself about use — and broken them?
-> Do you feel defensive reading these questions?
-> Have you tried to stop or cut back and couldn't?
-> Do you need more than you used to for the same effect?
-> Have you missed work, obligations, or plans because of use?
-> Do you keep using despite it causing problems you can see?

If you answered yes to 3 or more: keep reading. This isn't a diagnosis.
It's information.
```

### Step 2: Clinical screening — the CAGE questionnaire

**Agent action**: Walk the user through CAGE. Four questions, yes/no. Score it honestly.

```
THE CAGE QUESTIONNAIRE (validated clinical screening):

Answer yes or no:

1. Have you ever felt you should CUT DOWN on your drinking/use?
2. Have people ANNOYED you by criticizing your drinking/use?
3. Have you ever felt bad or GUILTY about your drinking/use?
4. Have you ever had a drink/used first thing in the morning to
   steady your nerves or get rid of a hangover? (EYE-OPENER)

SCORING:
- 0-1 yes answers: Low concern. Monitor yourself honestly.
- 2-3 yes answers: Clinically significant. This warrants a deeper look.
  Consider the AUDIT below and talk to a doctor.
- 4 yes answers: Strong indicator of dependence.
  This is not a death sentence. But you need help, and it exists.

Note: CAGE was designed for alcohol but applies to other substances.
It's a screening tool, not a diagnosis. A score of 2+ means
"talk to a professional" — not "you're an addict."
```

### Step 3: The AUDIT tool — deeper alcohol screening

**Agent action**: If the user's concern is specifically alcohol, walk through the full AUDIT. Score each question 0-4.

```
WHO AUDIT (Alcohol Use Disorders Identification Test):

Rate each question 0-4:

1. How often do you have a drink containing alcohol?
   0=Never  1=Monthly or less  2=2-4x/month  3=2-3x/week  4=4+x/week

2. How many drinks on a typical drinking day?
   0=1-2  1=3-4  2=5-6  3=7-9  4=10+

3. How often do you have 6+ drinks on one occasion?
   0=Never  1=Less than monthly  2=Monthly  3=Weekly  4=Daily/almost daily

4. How often in the last year could you not stop drinking once started?
   0=Never  1=Less than monthly  2=Monthly  3=Weekly  4=Daily/almost daily

5. How often in the last year did you fail to do what was expected
   because of drinking?
   0=Never  1=Less than monthly  2=Monthly  3=Weekly  4=Daily/almost daily

6. How often in the last year did you need a drink in the morning
   to get going?
   0=Never  1=Less than monthly  2=Monthly  3=Weekly  4=Daily/almost daily

7. How often in the last year did you feel guilt or remorse after drinking?
   0=Never  1=Less than monthly  2=Monthly  3=Weekly  4=Daily/almost daily

8. How often in the last year were you unable to remember the night before?
   0=Never  1=Less than monthly  2=Monthly  3=Weekly  4=Daily/almost daily

9. Have you or someone else been injured because of your drinking?
   0=No  2=Yes, but not in the last year  4=Yes, in the last year

10. Has a relative, friend, doctor, or health worker been concerned
    about your drinking or suggested you cut down?
    0=No  2=Yes, but not in the last year  4=Yes, in the last year

SCORING:
- 0-7:   Low risk.
- 8-15:  Hazardous use. Time for changes. Harm reduction applies here.
- 16-19: Harmful use. Professional help is strongly recommended.
- 20-40: Possible dependence. Medical supervision for any changes.
         Do NOT stop drinking suddenly — see withdrawal section below.
```

### Step 4: Behavioral addiction screening

**Agent action**: For non-substance compulsive behaviors, use this framework.

```
BEHAVIORAL ADDICTION SCREENING:

For gambling, gaming, compulsive phone/social media use, shopping,
pornography, or other compulsive behaviors — ask:

1. Do you spend more time on it than you intend to? Regularly?
2. Do you feel restless or irritable when you try to stop?
3. Have you tried to cut back and failed?
4. Do you use it to escape problems or relieve bad moods?
5. Have you lied to others about how much time/money you spend on it?
6. Has it caused problems in your relationships, work, or finances?
7. Do you keep doing it despite those problems?

4+ yes answers: This pattern is consistent with compulsive behavior
that warrants professional evaluation.

For gambling specifically: the National Council on Problem Gambling
helpline is 1-800-522-4700 (24/7, free, confidential).
```

### Step 5: Harm reduction — if you're going to use

**Agent action**: Deliver harm reduction information without moral commentary. Reducing risk is always better than pretending abstinence is the only option.

```
HARM REDUCTION BASICS:

If you are going to use, these practices reduce your risk of death
and serious harm:

ALCOHOL:
-> Eat before drinking. Pace: one drink per hour maximum.
-> Alternate with water (one for one).
-> Set a number before you start. Stop at that number.
-> Never mix with benzodiazepines or opioids. This combination kills.
-> If you're questioning your use, track it: every drink, every day,
   for two weeks. The data will tell you what your brain won't.

ALL SUBSTANCES:
-> Never use alone. If you're going to use, have someone present
   who knows what you took and can call 911.
-> Test your substances. Fentanyl test strips are cheap and save lives.
   Fentanyl is now in everything — pills, cocaine, counterfeit meds.
-> Start with a small amount, especially with a new batch or supplier.
-> Know what you're mixing. Combinations are what kill most people.
-> Keep naloxone (Narcan) accessible. It reverses opioid overdose.
   Available without prescription at most pharmacies.

THESE ARE NOT ENDORSEMENTS. This is reducing the chance of dying.
```

### Step 6: Understand withdrawal — some types can kill you

**Agent action**: This section is medically critical. Deliver it clearly and urgently where appropriate.

```
WITHDRAWAL REALITY:

ALCOHOL WITHDRAWAL:
Severity: MEDICALLY DANGEROUS. Can be fatal.
-> Symptoms begin 6-24 hours after last drink
-> Mild: tremors, anxiety, nausea, insomnia, sweating
-> Moderate: hallucinations (24-48 hrs), elevated heart rate/BP
-> Severe: seizures (12-48 hrs), delirium tremens (48-96 hrs)
-> Delirium tremens has a 5-15% mortality rate without treatment
*** NEVER cold-turkey heavy daily drinking without medical supervision ***
*** If you drink daily, talk to a doctor before stopping ***
Medical detox uses benzodiazepines to prevent seizures. This is safe
and effective when supervised. Inpatient detox is typically 3-7 days.

BENZODIAZEPINE WITHDRAWAL:
Severity: MEDICALLY DANGEROUS. Similar to alcohol.
-> Can cause seizures and death
-> Requires a medical taper — slow dose reduction over weeks/months
-> Never stop benzos abruptly after regular use
-> A doctor MUST supervise this process

OPIOID WITHDRAWAL:
Severity: Extremely unpleasant but rarely fatal in healthy adults.
-> Onset: 8-24 hours after last use (heroin/short-acting),
   24-72 hours (long-acting/methadone)
-> Symptoms: muscle pain, sweating, diarrhea, vomiting, insomnia,
   anxiety, restless legs — peaks at 48-72 hours
-> Duration: acute phase 5-10 days
-> What helps: Medication-Assisted Treatment (MAT) with buprenorphine
   (Suboxone) or methadone. These are not "replacing one drug with
   another" — they are evidence-based treatment. Period.

STIMULANT WITHDRAWAL (cocaine, amphetamines):
Severity: Not medically dangerous but psychologically brutal.
-> Crash phase: extreme fatigue, depression, increased appetite
-> Duration: 1-2 weeks acute, mood issues can persist months
-> Risk: severe depression and suicidal ideation during crash
-> No medication protocol — support, sleep, nutrition, monitoring
```

### Step 7: Getting help without going broke

**Agent action**: Provide concrete, actionable resources with real contact information.

```
FREE AND LOW-COST TREATMENT:

SAMHSA HELPLINE: 1-800-662-4357
-> Free, confidential, 24/7, 365 days
-> English and Spanish
-> Referrals to local treatment, support groups, community organizations
-> They will help you find what you can afford

SAMHSA TREATMENT LOCATOR: findtreatment.gov
-> Search by location, insurance, substance, treatment type

FREE MUTUAL SUPPORT:
-> AA (Alcoholics Anonymous): aa.org — free, meetings everywhere,
   anonymous. 12-step model. Works for many people.
-> NA (Narcotics Anonymous): na.org — same model for all substances.
-> SMART Recovery: smartrecovery.org — evidence-based alternative
   to 12-step. Uses CBT techniques. Online and in-person meetings.
   No religious/spiritual component.

COMMUNITY MENTAL HEALTH CENTERS:
-> Most communities have CMHCs with sliding-scale fees
-> Search: "[your county] community mental health center"
-> Many offer substance abuse treatment alongside mental health

STATE-FUNDED PROGRAMS:
-> Every state has publicly funded treatment for people without
   insurance or ability to pay
-> Call SAMHSA helpline to find your state's programs

MEDICATION-ASSISTED TREATMENT (MAT):
-> For opioid use: buprenorphine (Suboxone) can be prescribed by
   any qualified doctor — you don't need a special clinic anymore
-> For alcohol: naltrexone (reduces cravings, available as daily pill
   or monthly injection) and acamprosate
-> These medications are covered by most insurance and Medicaid

WHEN TO GO TO THE ER:
-> Seizures or history of seizures during withdrawal
-> Hallucinations
-> Chest pain or heart racing during withdrawal
-> Suicidal thoughts
-> Vomiting so severe you can't keep fluids down
-> Confusion or disorientation
-> You are withdrawing from alcohol or benzos after heavy daily use
```

## If This Fails

- **Can't afford treatment?** Call SAMHSA at 1-800-662-4357. They specifically help people find free options. State-funded programs exist in every state.
- **Tried AA/NA and it's not for you?** SMART Recovery uses CBT instead of 12-step. Online meetings available at smartrecovery.org. There's also LifeRing Secular Recovery and Refuge Recovery (Buddhist-based).
- **Can't stop but can't get into treatment?** Harm reduction is still progress. Reducing quantity, never using alone, carrying naloxone, and testing substances are all meaningful risk reduction.
- **Worried about someone else?** Al-Anon (for families of alcoholics) and Nar-Anon (for families of drug users) are free. You can't force someone into recovery, but you can stop enabling and protect yourself.
- **In crisis right now?** 988 Suicide and Crisis Lifeline (call or text 988). Crisis Text Line (text HOME to 741741).

## Rules

- Never moralize. The user knows substance use carries risk. Judgment is not information.
- Never diagnose. These are screening tools, not diagnoses. Only a clinician can diagnose a substance use disorder.
- Always flag medically dangerous withdrawal (alcohol and benzodiazepines) clearly and urgently.
- Present Medication-Assisted Treatment as legitimate, evidence-based medicine, not as "replacing one addiction with another."
- Harm reduction information should be presented without moral qualification. Reducing risk is always a valid choice.
- If the user is in immediate medical danger (active withdrawal from alcohol/benzos, overdose symptoms, suicidal ideation), direct to emergency services first — everything else can wait.

## Tips

- Tracking your use honestly for two weeks will tell you more than any screening tool. Write down every drink, every use, every day. Don't judge it — just record it. The pattern will speak for itself.
- If you're questioning your use, that itself is data. People without a problem rarely spend time wondering if they have one.
- Recovery is not linear. Relapse is not failure — it's information about what needs to change in your approach. Most people who eventually achieve long-term recovery had multiple attempts.
- MAT (medication-assisted treatment) has the strongest evidence base for opioid use disorder. If a treatment program tells you medication is a "crutch," find a different program.
- The people around you noticed before you did. If more than one person has mentioned it, that's not coincidence.
- You don't have to hit "rock bottom." That's a myth that kills people. You can get help at any point.

## Agent State

```yaml
state:
  screening:
    cage_score: null
    audit_score: null
    behavioral_screen_score: null
    primary_substance: null
    secondary_substances: []
    use_frequency: null
    use_duration: null
    use_trend: null  # stable, increasing, decreasing
    withdrawal_risk: null  # none, low, moderate, high, medical_emergency
  situation:
    using_alone: null
    others_concerned: null
    prior_treatment: null
    prior_treatment_type: []
    insurance_status: null
    immediate_danger: false
  actions_taken:
    screening_completed: false
    harm_reduction_reviewed: false
    withdrawal_info_reviewed: false
    resources_provided: false
    samhsa_contacted: false
    treatment_located: false
    mat_discussed: false
  follow_up:
    next_check_in: null
    tracking_started: false
    tracking_start_date: null
```

## Automation Triggers

```yaml
triggers:
  - name: medical_danger_flag
    condition: "screening.withdrawal_risk == 'medical_emergency' OR screening.primary_substance IN ['alcohol', 'benzodiazepines'] AND screening.use_frequency == 'daily'"
    action: "Based on what you've described, stopping suddenly could be medically dangerous. Alcohol and benzodiazepine withdrawal can cause seizures. Please talk to a doctor before making changes to your use. If you're already in withdrawal and experiencing tremors, confusion, or hallucinations, go to an ER now."

  - name: high_cage_score
    condition: "screening.cage_score >= 2 AND actions_taken.resources_provided IS false"
    action: "Your CAGE score suggests this warrants a closer look. This isn't a label — it's a signal. Would you like to go through the more detailed AUDIT screening, or would you prefer to look at treatment and support options?"

  - name: tracking_reminder
    condition: "actions_taken.tracking_started IS true AND days_since(tracking_start_date) == 14"
    action: "It's been two weeks since you started tracking your use. Ready to look at the data together? No judgment — just information."

  - name: harm_reduction_check
    condition: "screening.primary_substance IS NOT null AND actions_taken.harm_reduction_reviewed IS false"
    action: "Before we go further — regardless of what you decide about treatment, there are harm reduction practices that reduce your risk right now. Want to go through them?"

  - name: resource_follow_up
    condition: "actions_taken.resources_provided IS true AND actions_taken.treatment_located IS false"
    schedule: "7 days after resources_provided"
    action: "Checking in. Were you able to connect with any of the resources we discussed? If something didn't work out, there are other options."
```
