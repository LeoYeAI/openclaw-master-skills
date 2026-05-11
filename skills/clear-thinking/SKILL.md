---
name: clear-thinking
description: >-
  Critical thinking skills and decision-making frameworks. Use when someone needs to evaluate conflicting information, make a difficult decision, spot manipulation or misinformation, or wants to think more clearly about problems.
metadata:
  category: mind
  tagline: >-
    Spot manipulation, evaluate claims, and make hard choices — logical fallacies, source evaluation, and decision frameworks for real life.
  display_name: "Clear Thinking & Decisions"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-19"
  openclaw:
    requires:
      tools: [filesystem]
    install: "npx clawhub install howtousehumans/clear-thinking"
---

# Clear Thinking & Decisions

Most bad decisions aren't made by stupid people. They're made by smart people using shortcuts that worked well enough in simpler situations but fail catastrophically when the stakes go up. Your brain is running on hardware evolved for a world where the biggest decision was "is that a predator or a rock." That same hardware is now evaluating health claims, political arguments, financial decisions, and career moves — and it's full of bugs that marketers, politicians, con artists, and your own ego exploit constantly. This skill covers two things: how to evaluate information so you stop getting fooled, and how to make decisions so you stop being paralyzed. Neither requires being "smart." Both require specific, learnable techniques that most people were never taught.

This skill references and extends: ai-scam-defense, boundaries-saying-no.

```agent-adaptation
# Localization note — media landscapes, education systems, and decision-making
# norms vary across cultures. Adapt examples accordingly.
- Media literacy context:
  US: Highly polarized media landscape. Left-right framing dominates. Teach
  evaluation of both sides, not just the one the user disagrees with.
  UK: Tabloid culture. BBC is publicly funded but not bias-free. Teach
  understanding of editorial vs. reporting.
  AU: Concentrated media ownership (News Corp dominance). Source diversity
  is especially important.
  Developing nations: State-controlled media may be the primary source.
  Teach evaluation of international sources as cross-reference.
- Statistical literacy:
  Adjust examples to local health systems, currencies, and measurement systems.
  The principles are universal; the numbers need localization.
- Decision-making norms:
  Individualist cultures (US, UK, AU): Decisions often framed as personal choice.
  Collectivist cultures: Decisions involve family, community, obligation.
  Decision frameworks need to account for collective input without dismissing it.
- Education systems:
  Critical thinking instruction varies wildly. Some users had formal logic
  training. Most didn't. Start with practical examples, not academic terminology.
- Misinformation vectors:
  WhatsApp-driven misinformation is dominant in South Asia, Latin America, Africa.
  Facebook/Meta in the US and Europe. WeChat in China. Adapt platform-specific
  advice accordingly.
```

## Sources & Verification

- **Daniel Kahneman, "Thinking, Fast and Slow"** -- System 1/System 2 framework. Cognitive biases and their effects on judgment. Farrar, Straus and Giroux, 2011.
- **Shane Parrish, "Clear Thinking"** -- Practical decision-making frameworks for high-stakes situations. Portfolio, 2023.
- **Carl Sagan, "The Demon-Haunted World"** -- The "baloney detection kit." Scientific literacy as civic duty. Ballantine Books, 1995.
- **Chip & Dan Heath, "Decisive"** -- The WRAP framework for overcoming cognitive biases in decisions. Crown Business, 2013.
- **Darrell Huff, "How to Lie with Statistics"** -- Classic primer on statistical manipulation. Still relevant. Norton, 1954.
- **Nassim Nicholas Taleb, "Fooled by Randomness"** -- How we mistake noise for signal and luck for skill. Random House, 2005.
- **First Draft / Credibility Coalition** -- Research on misinformation detection and media literacy. https://firstdraftnews.org

## When to Use

- User is trying to evaluate conflicting information (health claims, news stories, advice)
- Needs to make a difficult decision with incomplete information
- Suspects they're being manipulated or lied to
- Is overwhelmed by options and can't decide
- Wants to argue their position more effectively
- Is evaluating a financial opportunity that seems too good to be true
- Is reading about a health treatment and wants to know if it's legitimate
- Feels paralyzed by a big life decision (career change, move, relationship)
- Wants to understand why they keep making the same bad decisions

## Instructions

### Step 1: The 6 Fallacies That Matter Most in Daily Life

**Agent action**: Present the most common logical fallacies with real-world examples, not textbook definitions.

```
THE 6 FALLACIES YOU'LL ENCOUNTER THIS WEEK

These aren't academic exercises. These show up in arguments, ads,
news, social media, and conversations every single day.

1. AD HOMINEM (attacking the person, not the argument)
   "You can't talk about nutrition — you're overweight."
   The argument's validity has nothing to do with who's making it.
   A broke accountant can still give correct tax advice. Evaluate
   the claim, not the claimant.

   Where you'll see it: Political debates, online arguments, any
   time someone is losing an argument and pivots to personal attacks.

2. FALSE DICHOTOMY (only two options when more exist)
   "You're either with us or against us."
   "If you don't support this policy, you must support the problem."
   Most decisions have more than two options. When someone frames
   a choice as binary, ask: "What are the other options they're
   not mentioning?"

   Where you'll see it: Political messaging, sales pressure ("buy
   now or lose this forever"), relationship ultimatums.

3. APPEAL TO AUTHORITY (it's true because an important person said it)
   "Dr. Famous said this supplement works."
   Experts can be wrong. Experts can be paid. The relevant question
   isn't WHO said it but WHAT'S THE EVIDENCE. A celebrity doctor
   endorsing a product is advertising, not science.

   Where you'll see it: Health products, financial advice, any time
   a credential is used as a substitute for evidence.

4. SUNK COST FALLACY (continuing because you've already invested)
   "I've been in this relationship for 5 years — I can't leave now."
   "We've spent $50K on this project — we have to finish it."
   Past investment is irrelevant to whether future investment is wise.
   The money/time is gone regardless. The only question is: going
   forward, is this the best use of your resources?

   Where you'll see it: Bad relationships, failing businesses, boring
   movies, degree programs you hate, stocks that are tanking.

5. CONFIRMATION BIAS (seeking info that confirms what you already believe)
   You Google "is coffee good for you" and click only the articles
   that say yes. You interpret ambiguous evidence as supporting your
   existing view. Everyone does this. It's the most pervasive bias
   in human cognition.

   The fix: Actively seek the strongest argument AGAINST your position.
   If you think X is true, search for "why X is wrong" and read the
   best version of that argument. If your position survives that test,
   it's stronger. If it doesn't, you've learned something.

   Where you'll see it: Everywhere. Every argument you've ever had.
   Every belief you hold.

6. ANECDOTAL EVIDENCE (my experience = universal truth)
   "My grandfather smoked and lived to 95, so smoking isn't that bad."
   "I didn't wear a seatbelt and I'm fine."
   One example proves nothing about the general pattern. Survivorship
   bias: you don't hear from the people who smoked and died at 55
   because they're not here to tell the story.

   Where you'll see it: Health decisions, risk assessment, any time
   someone says "well, in MY experience..."
```

### Step 2: How to Evaluate a Claim

**Agent action**: Provide the source evaluation checklist for news, health claims, and general information.

```
THE SOURCE EVALUATION CHECKLIST

Before you believe a claim — from a news article, a social media post,
a friend, or an ad — run it through these filters:

1. WHO IS SAYING THIS?
   - A journalist at a reputable outlet?
   - A random person on social media?
   - A company selling something?
   - An expert in the relevant field (not just any field)?
   - A think tank or organization? (Who funds them?)

2. WHAT'S THEIR INCENTIVE?
   - Do they profit if you believe this? (Advertisers, salespeople,
     politicians, influencers)
   - Does their career depend on this position? (Academics, pundits)
   - Could they face consequences for lying? (Journalists can be sued.
     Random social media posters cannot.)

3. DOES IT CITE PRIMARY SOURCES?
   - "Studies show..." Which studies? Where published? By whom?
   - "Experts say..." Which experts? What's their credential in THIS
     field?
   - If a claim doesn't link to or cite the actual evidence, treat
     it as an opinion, not a fact.

4. HAS IT BEEN INDEPENDENTLY VERIFIED?
   - Can you find this claim reported by multiple independent outlets?
   - If only one source is reporting it, be cautious.
   - If multiple outlets are reporting it but all cite the same single
     source, that's still only one source.

5. HOW DOES IT MAKE YOU FEEL?
   - If it makes you immediately outraged, afraid, or triumphant,
     pause. Emotionally charged content is designed to bypass your
     critical thinking. The stronger your emotional reaction, the
     more carefully you should evaluate the claim.

6. WHAT'S THE STRONGEST COUNTERARGUMENT?
   - If you can't articulate the other side's best argument, you
     don't understand the issue well enough to have a strong opinion.

EVALUATING HEALTH CLAIMS SPECIFICALLY:

- Is it peer-reviewed? Published in a recognized medical journal?
- Sample size: A study of 12 people is not conclusive. A study of
  12,000 is more convincing.
- Relative vs. absolute risk: "Doubles your risk!" sounds scary.
  But doubling from 0.001% to 0.002% is not scary. Always ask:
  what's the actual number?
- Does it replicate? One study proves almost nothing. Multiple
  studies showing the same thing start to prove something.
- Who funded the study? Coca-Cola-funded research on sugar safety
  should be viewed differently than independently funded research.
```

### Step 3: Spotting Statistical Manipulation

**Agent action**: Teach the most common ways numbers lie.

```
HOW NUMBERS LIE — THE 5 MOST COMMON TRICKS

1. CHERRY-PICKED TIMELINES
   "The economy grew 3% this quarter!" (But it shrank 8% last quarter.)
   "Crime is up 20% since January!" (But down 40% from 5 years ago.)
   Any statistic with a timeline can be manipulated by choosing the
   start and end dates. Ask: what does the FULL timeline look like?

2. MISLEADING GRAPHS
   - Y-axis doesn't start at zero: makes small differences look huge.
   - Compressed or expanded scales: can make any trend look dramatic
     or flat.
   - Dual-axis charts: can imply correlation where none exists.
   Always read the axes before reacting to the shape of the graph.

3. CORRELATION DOES NOT EQUAL CAUSATION
   "Countries that eat more chocolate win more Nobel Prizes."
   (Both correlate with wealth and education investment.)
   "Ice cream sales correlate with drowning deaths."
   (Both increase in summer.)
   Just because two things move together doesn't mean one causes
   the other. There's almost always a third variable.

4. RELATIVE VS. ABSOLUTE NUMBERS
   "This treatment reduces your risk by 50%!" = relative.
   "This treatment reduces your risk from 2% to 1%." = absolute.
   Same data. Very different feeling. Always demand the absolute
   numbers. Relative numbers are the native language of manipulation.

5. AVERAGE VS. MEDIAN
   "The average income in this company is $200K!" (Because the CEO
   makes $10M and everyone else makes $60K.)
   Average (mean) is distorted by outliers. Median (the middle value)
   tells you what's typical. When someone quotes an average, ask
   for the median.

THE GENERAL RULE:
If a number is being used to sell you something, scare you, or
persuade you, ask: "What's the number they AREN'T showing me?"
There's always one.
```

### Step 4: Reversible vs. Irreversible Decisions

**Agent action**: Teach the decision categorization framework that eliminates most analysis paralysis.

```
THE FIRST QUESTION FOR ANY DECISION: CAN I UNDO IT?

Most people spend the same amount of mental energy on reversible
decisions as irreversible ones. This is a massive waste.

REVERSIBLE DECISIONS (Type 2):
- Trying a new job (you can quit or find another)
- Moving to a new city (you can move back)
- Starting a side project (you can stop)
- Changing your hairstyle (it grows back)
- Trying a new restaurant (you eat one bad meal)
- Signing up for a class (you can drop it)

IRREVERSIBLE DECISIONS (Type 1):
- Having a child
- Major surgery
- Burning a professional bridge publicly
- Spending money you can't get back on a depreciating asset
- Saying something in anger that can't be unsaid
- Signing a contract with severe penalties for exit

THE RULE:
- REVERSIBLE decisions: Decide fast. The cost of delay usually
  exceeds the cost of a wrong choice. Try it, evaluate, adjust.
- IRREVERSIBLE decisions: Go slow. Gather information. Consult
  others. Sleep on it. The cost of a wrong choice exceeds the
  cost of delay.

THE COMMON MISTAKE:
Most people overthink reversible decisions (spending weeks choosing
a restaurant, agonizing over a gym membership) and underthink
irreversible ones (signing a mortgage in a rush, saying yes to
marriage because of social pressure). Flip it.
```

### Step 5: The 70% Rule

**Agent action**: Provide the information-threshold framework for decisions.

```
THE 70% RULE — WHEN TO STOP GATHERING AND START DECIDING

With 40% of the information: you're guessing. Gather more.
With 70% of the information: you have enough. Decide.
With 100% of the information: it's too late. The opportunity passed.

WHY 70% IS THE SWEET SPOT:
- You'll never have all the information. Ever. For any decision.
  Waiting for certainty is waiting forever.
- The marginal value of additional information drops sharply after
  ~70%. Going from 70% to 80% informed takes as long as going
  from 0% to 70%, and changes the decision far less often.
- Speed of decision often matters more than quality of decision,
  especially for reversible choices (Step 4).

HOW TO ESTIMATE YOUR INFORMATION LEVEL:
Ask yourself:
1. Do I understand the major options? (Yes/no)
2. Do I understand the likely consequences of each? (Yes/no)
3. Have I consulted someone with relevant experience? (Yes/no)
4. Do I know the key risks? (Yes/no)
5. Am I just gathering more info to avoid the discomfort of deciding?

If you answered yes to 1-4, you're probably at 70%+.
If you answered yes to 5, you're procrastinating, not researching.

THE TEST: "If I had to decide right now, what would I choose?"
If you have a clear answer, you have enough information. The extra
research is stalling.
```

### Step 6: Decision Frameworks for Specific Situations

**Agent action**: Provide multiple frameworks the user can apply depending on the decision type.

```
FRAMEWORK TOOLKIT — PICK THE ONE THAT FITS

THE 10/10/10 RULE (for emotional decisions):
Ask: How will I feel about this in:
- 10 minutes? (The hot emotional reaction)
- 10 months? (When the dust has settled)
- 10 years? (When it's ancient history)

If all three timeframes agree, the decision is clear.
If they disagree, trust the 10-year answer.

Use for: Confrontations, quitting impulses, emotional purchases,
relationship decisions made while angry.

---

THE "HELL YES OR NO" FILTER (for optional commitments):
If your response to an invitation, opportunity, or request isn't
an enthusiastic "hell yes," it's a no.

This filter only applies to OPTIONAL things. You still have to pay
taxes, show up to work, and feed your kids.

Use for: Social invitations, volunteer commitments, side projects,
favors. Protects against over-commitment and people-pleasing.

---

WEIGHTED PROS AND CONS (for complex decisions):
Standard pro/con lists are useless because they treat all items
as equal. "Pro: closer to family. Con: slightly worse weather."
Those aren't the same weight.

Instead:
1. List all pros and cons.
2. Assign each a weight from 1 (barely matters) to 5 (life-changing).
3. Multiply: number of items x weight.
4. Compare totals.

Example — Should I take the new job?
Pros: More money (5) + shorter commute (3) + new skills (4) = 12
Cons: Less stability (4) + further from friends (2) + unknown team (3) = 9
Pro total is higher. Take the job.

This doesn't make the decision for you. It externalizes your values
so you can see them clearly.

---

REGRET MINIMIZATION (for major life decisions):
Jeff Bezos framework: Project yourself to age 80. Ask: "Will I
regret NOT doing this more than I'll regret doing it?"

Use for: Career changes, moves, starting businesses, ending
relationships, big risks. Not for daily decisions — reserve this
for the handful of choices that genuinely shape a life.
```

### Step 7: Stop Second-Guessing After Deciding

**Agent action**: Provide techniques for post-decision commitment.

```
AFTER THE DECISION — CLOSING THE DOOR

The decision is made. Now your brain will try to unmake it.
Second-guessing after deciding is one of the biggest sources of
anxiety and wasted energy in adult life.

WHY YOU SECOND-GUESS:
- Hedonic adaptation: The new choice becomes normal fast, and you
  start seeing the grass as greener on the other option.
- Counterfactual thinking: Your brain generates "what if" scenarios
  about the path not taken. These fantasies are always unrealistically
  positive because they're fiction.
- Loss aversion: The losses of your chosen option feel 2x more
  painful than the equivalent gains (Kahneman research).

THE COMMITMENT PROTOCOL:

1. SET A REVIEW DATE
   "I will not reconsider this decision for [30/60/90 days]."
   Write it down. Give the decision time to play out before
   evaluating. Most decisions need time to show their real effects.

2. STOP RESEARCHING ALTERNATIVES
   Once you've chosen a restaurant, stop reading reviews of other
   restaurants. Once you've taken the job, stop browsing job boards.
   Continued comparison erodes satisfaction with any choice.

3. INVEST IN YOUR CHOICE
   The best way to make the right decision is to make your decision
   right. Put energy into making the chosen path work rather than
   wondering about the other paths.

4. ACCEPT IMPERFECTION
   No option was perfect. You chose the best available option with
   the information you had. That's all anyone can do. The unlived
   path was not problem-free — you just can't see its problems
   because you didn't walk it.

THE EXCEPTION:
If genuinely new information emerges (not "I'm having second
thoughts" but "I discovered a fact I didn't have before"), then
reassessment is appropriate. Changed circumstances change decisions.
That's rational, not weak.
```

### Step 8: Recognizing Manipulation in Real Time

**Agent action**: Provide practical manipulation detection for sales, arguments, and media.

```
MANIPULATION DETECTION — REAL-TIME CHECKLIST

SALES AND MARKETING:
- Artificial urgency: "Only 3 left!" "Price goes up at midnight!"
  Real scarcity doesn't need a countdown timer.
- Social proof manipulation: "10,000 people bought this!" So what?
  10,000 people make bad purchases daily.
- Anchoring: The "original price" was never the real price. The
  "compare at" price is fiction. Evaluate the actual price against
  the actual value.
- Free trial to paid: They're betting on inertia. You'll forget to
  cancel. If you sign up, set a calendar reminder for 2 days before
  it converts.

ARGUMENTS AND DEBATES:
- Gish gallop: Throwing 20 weak arguments instead of 1 strong one.
  You can't refute all 20, so they "win." Response: "Let's take your
  strongest point and examine it."
- Moving the goalposts: You prove X, they say "well, what about Y?"
  You prove Y, they say "but what about Z?" Name it: "I answered your
  original question. Do you accept that point?"
- Whataboutism: "What about [unrelated bad thing]?" Response: "We're
  talking about [original topic]. We can discuss that separately."
- Appeal to emotion: A sad story doesn't prove a policy works. A scary
  anecdote doesn't prove a risk is significant. Feelings are real.
  They're not evidence.

MEDIA AND SOCIAL MEDIA:
- Headlines are designed for clicks, not accuracy. Read the article.
  Often the headline contradicts the content.
- Screenshots of tweets/posts can be fabricated in 30 seconds.
  Go to the original source.
- "Some people say..." is a way to introduce an idea without taking
  responsibility for it. WHO says? How many? What's their evidence?
- If a claim makes you feel like sharing it immediately — that's the
  moment to pause and verify. Viral content is optimized for emotional
  response, not accuracy.

THE GENERAL DEFENSE:
When someone is trying to get you to believe, buy, or do something,
ask: "Why is this being presented to me right now, in this way, by
this person?" The answer is usually: because someone profits from
your belief or action.
```

## If This Fails

- "I'm still paralyzed by a decision": Set a deadline. "I will decide by Friday at noon." Deadlines force action. Make the best choice you can with what you know, and commit to evaluating it after a defined period.
- "I keep getting fooled by misinformation": This is a skill that improves with practice, not a switch you flip. Start with one habit: before you share anything online, check one additional source. That single behavior cuts misinformation spread significantly.
- "I understand the fallacies but I still fall for them emotionally": Knowing about biases doesn't eliminate them (this is itself a bias — the "bias blind spot"). The techniques help. You'll still get fooled sometimes. The goal is getting fooled less, not never.
- "These frameworks make me overthink": Use the reversible/irreversible filter (Step 4) first. If the decision is reversible, skip the frameworks and just try something. Save the frameworks for the decisions that actually matter.
- "The people around me don't think critically and it's frustrating": You can't force anyone to think differently. You can model it. Ask questions instead of making arguments. "What's the evidence for that?" is more effective than "You're wrong."

## Rules

- Don't be condescending about critical thinking. Most people were never taught these skills. Meet them where they are.
- Don't assume the user's political or ideological position. Apply critical thinking equally to all claims, regardless of which "side" they come from.
- Don't claim that rational thinking eliminates all errors. It reduces them. Uncertainty is permanent. Intellectual humility is part of thinking clearly.
- Don't frame emotions as the enemy of thinking. Emotions provide data. The problem is when emotions REPLACE thinking, not when they inform it.

## Tips

- The fastest way to test your own reasoning: explain your position to someone who disagrees. If you can't make their counterargument for them, you don't understand the issue well enough.
- "I don't know" is one of the most powerful things you can say. It opens the door to learning. "I have a strong opinion on this" is often a sign you stopped investigating too early.
- When evaluating any claim, ask: "What would change my mind?" If the answer is "nothing," you're not reasoning — you're defending a position.
- The sunk cost fallacy kills more good decisions than any other bias. Practice saying: "What I've already spent doesn't matter. What should I do going forward?"
- Read primary sources when you can. A news article about a study is an interpretation. The study itself is the data. Even reading the abstract takes 2 minutes and gives you more than most people bother to get.
- Sleep on irreversible decisions. Literally. Decide in the morning. Research on decision quality shows a full night's sleep improves complex judgment measurably.

## Agent State

```yaml
clear_thinking_session:
  context: null
  decision_type: null
  reversibility: null
  information_level: null
  fallacies_identified: []
  frameworks_applied: []
  claims_evaluated: []
  decision_made: false
  commitment_period_set: false
  resources_provided: []
  related_skills_referenced: []
```

## Automation Triggers

```yaml
triggers:
  - name: misinformation_evaluation
    condition: "user asks whether a claim is true or presents conflicting information"
    schedule: "on_demand"
    action: "Run the source evaluation checklist (Step 2) and identify any relevant fallacies (Step 1)"
  - name: decision_paralysis
    condition: "user describes being unable to make a decision or overthinking"
    schedule: "on_demand"
    action: "Start with Step 4 reversible/irreversible classification, then apply Step 5 (70% rule) and relevant framework from Step 6"
  - name: manipulation_flag
    condition: "user describes a sales pitch, argument, or media claim that feels manipulative"
    schedule: "on_demand"
    action: "Jump to Step 8 manipulation detection checklist and help user identify specific techniques being used"
  - name: post_decision_anxiety
    condition: "user has made a decision but can't stop second-guessing it"
    schedule: "on_demand"
    action: "Apply Step 7 commitment protocol and help set a review date"
```
