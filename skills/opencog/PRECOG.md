# Precog

Precog is a fully onchain, multichain prediction market protocol deployed on Base (with Ethereum and Arbitrum coming soon). It turns forecasting into usable economic infrastructure: markets generate probabilistic signals that anyone can use for decision-making, governance, and risk management.

Documentation: https://learn.precog.markets
App: https://core.precog.markets

---

# Welcome to Precog

Precog is a fully onchain prediction market protocol on Ethereum, Arbitrum, and Base. It lets anyone create markets around real-world questions, fund them with liquidity, and forecast outcomes, earning rewards for accuracy.

Everything runs onchain. No central party controls outcomes, holds your funds, or can shut a market down.

## Ask your agent about Precog

---

# Prediction Markets 101

A prediction market is a place where people trade on the probability of future events. Instead of just stating an opinion, participants put something at stake, which creates a powerful incentive to be accurate rather than just confident.

The core mechanic is simple: each possible outcome has a price between 0 and 1, representing its implied probability. If you think an event is more likely than the market believes, you buy shares of that outcome. If you're right, each share pays out 1 unit. If you're wrong, it pays out nothing.

This structure aggregates information efficiently. People with genuine knowledge or insight are rewarded for acting on it, which pulls prices toward the true probability over time. Prediction markets have consistently outperformed polls, expert panels, and traditional forecasting methods across domains from politics to science to finance.

On Precog, this mechanism runs fully onchain using an LS-LMSR pricing curve, an algorithm that sets prices automatically based on trading activity, without requiring an order book or a counterparty.
 
## Further Reading

- [Cultivate Labs: Types of Prediction Markets](https://www.cultivatelabs.com/crowdsourced-forecasting-guide/what-are-the-different-types-of-prediction-markets)
- [Research Corner: Gates Building Prediction Market](https://www.cs.utexas.edu/news/2012/research-corner-gates-building-prediction-market)
- [Augur: LMSR and LS-LMSR](https://augur.mystrikingly.com/blog/augur-s-automated-market-maker-the-ls-lmsr)
- [Precog: Interactive LMSR pricing](https://www.desmos.com/calculator/jvy0ci53lm)

---

# How to Make a Prediction

This page walks through what happens when you forecast on Precog, from finding a market to collecting your winnings.

 
## Step 1: Find a Market

Browse open markets on [Precog Core](https://core.precog.markets). Each market shows:

- The question being asked
- The current probability of each outcome (e.g., "Outcome A: 45% / Outcome B: 35% / Outcome C: 20%")
- The closing date (after this, no new positions can be taken)
- The collateral token used (e.g., ETH, USDC)

Markets on Precog support multiple outcomes, not just Yes/No. A market might ask which candidate will win an election, which team will win a tournament, or which option a DAO should choose — with each option showing its own probability.

The probability shown is not just a display number; it is the market's current price. Buying "Outcome A" at 45% means you're paying 0.45 tokens per share. If Outcome A wins, each share pays out 1 token.
 
## Step 2: Form Your View

Before buying, decide whether you think any outcome's price is too low or too high.

- If the market prices Outcome A at 20% but you think it's closer to 45%, buying Outcome A is good value
- If the market prices Outcome B at 60% but you think it's closer to 30%, buying one of the other outcomes is good value

In a multi-outcome market, you can also spread positions across several outcomes if you think the market is mispricing more than one. You don't need to be right about the exact probability; you just need the market to be wrong in the direction you're betting on.

See [Forecasting 101](/forecasting/forecasting-101) for techniques to sharpen your estimates.
 
## Step 3: Buy Outcome Shares

> Don't have funds yet? See [Getting Funds onto Precog](/blockchain/fund-wallet) to bridge or onramp before continuing.

Select the outcome you want to back and enter an amount. The interface will show you:

- How many shares you'll receive
- The effective price per share (the implied probability you're paying)
- The price impact: larger trades move the curve and cost more per share

Confirm the transaction in your wallet. Your outcome shares are now held onchain.

> The price you pay reflects the curve at the moment you trade. If others buy the same outcome after you, the price rises. If they buy the other side, it falls. Your shares keep the price you locked in.
 
## Step 4: Track Your Position

After buying, your position appears in your portfolio. You can see:

- Which outcome you hold shares in
- How many shares
- The current market probability vs. your entry price
- Unrealized gain or loss based on current prices
 
## Step 5: Wait for Resolution (or Sell Early)

**If you hold until the market closes:**
- If your outcome wins, each share pays out 1 token
- If your outcome loses, your shares are worth 0

**If you want to exit early:**
- You can sell your shares back to the curve at the current market price
- This locks in a gain if the probability moved in your direction, or limits a loss if it moved against you
 
## Risks

- **You can lose your full position.** If the outcome you backed does not win, your shares pay out nothing. There is no partial payout for being "close."
- **Price impact on large trades.** The LS-LMSR curve means large buys shift the price against you. Check the price impact before confirming big trades.
- **Smart contract risk.** As with all onchain protocols, bugs in the contracts are a possibility.
 
## After Resolution

Once the market resolves (see [Resolution](/markets/resolution)), winning shares become redeemable. If funds haven't been automatically distributed yet, go to your portfolio and claim your own winnings directly.

Funds go straight to your wallet onchain.

---

# Forecasting 101

> A Beginner’s Guide to Superforecasting Techniques

Forecasting may sound intimidating, but with the right tools, anyone can improve their ability to predict the future. This guide is based on the principles of Superforecasters, individuals who consistently outperform others in making accurate predictions. Let’s dive into the techniques to help you forecast like a pro.

## 1. The Fermi-Size Approach: Breaking It Down
Named after physicist Enrico Fermi, this method involves breaking a big, complicated question into smaller, more manageable pieces. Think of it like solving a puzzle step by step.
Steps:
Start with a big question: For example, “How many piano tuners are there in New York City?”
Break it down: Ask simple sub-questions like:
How many people live in New York City?
How many households own pianos?
How often do pianos need tuning?
Estimate each piece: Use approximate numbers that feel reasonable.
Multiply the pieces back together: Combine your answers to get a total estimate.
Tip: The Socratic Method (asking yourself and others pointed questions) helps refine your thinking as you break problems down.

## 2. The Outside View: Start Broad
The outside view is about grounding your predictions in reality by using historical data or base rates. It’s your anchor to avoid wild guesses.
Example:
If you’re forecasting the chance of a new business succeeding, start by asking, “What percentage of new businesses typically succeed within five years?” This is your baseline.
Why it works: Base rates provide a reality check, showing how common an event is within a larger class of similar events.

## 3. The Inside View: Add Your Unique Insight
Once you have the outside view, it’s time to factor in specifics. The inside view is where your hunches, assumptions, and unique context come into play.
How to balance it:
Look at the unique circumstances: What makes this situation different?
Adjust your prediction based on these nuances.
Avoid letting your adjustments deviate too far from the base rate.
Example: If the new business is led by an experienced entrepreneur, you might increase its odds of success slightly above the baseline.

## 4. Thesis, Antithesis, and Synthesis: Thinking in Layers
This technique comes from philosophy but applies perfectly to forecasting. It’s about considering multiple perspectives and combining them into a well-rounded conclusion.
Steps:
Thesis: State your initial prediction.
Antithesis: Challenge it by asking, “What if I’m wrong?”
Synthesis: Reconcile the two perspectives to create a more robust prediction.
Why it’s useful: It forces you to confront your biases and refine your forecast.

## 5. The Crowd Within: Two Heads Are Better Than One (Even if Both Are Yours)
This technique involves generating two independent estimates and then merging them for a more reliable prediction.
Steps:
Make your first estimate based on your initial thoughts.
Assume this is wrong, and challenge yourself to create a second estimate from a different angle.
Combine the two: Average them or take a weighted approach.
Example: Predicting election results? Your first estimate might use polling data, while the second considers economic trends. Merge them for balance.

## 6. Dialectic Discussions: Feedback Is Key
Engage in thoughtful discussions with others to refine your forecasts. This helps you avoid groupthink and leverage diverse perspectives.
How to do it:
Share your initial prediction with someone else.
Ask for their reasoning and feedback.
Compare your thoughts and adjust your forecast accordingly.
Tip: Seek out people who challenge your views rather than just agreeing with you.

## 7. Pre-Mortem Analysis: Spot Problems Before They Happen
A pre-mortem involves imagining that your prediction has already failed and then brainstorming reasons why.
Steps:
Assume your forecast turned out wrong.
Ask yourself, “What went wrong?”
List potential pitfalls and adjust your prediction to account for them.
Why it’s useful: It helps you anticipate and mitigate risks before committing to a forecast.

## 8. Probabilistic Thinking: Quantify Your Confidence
Forecasting isn’t just about making predictions—it’s about assigning probabilities to outcomes.
How to do it:
Use percentages to express your confidence (e.g., “I’m 70% sure this will happen”).
Regularly update your probabilities as new information becomes available.
Avoid being overconfident by considering a range of outcomes.
Example: Instead of saying, “The stock market will rise,” say, “There’s a 60% chance the market will rise in the next quarter.”

## Final Thoughts: Practice Makes Perfect
Becoming a great forecaster takes time, but these techniques will set you on the right path. Start with small questions, practice regularly, and always be open to learning and improving. Happy forecasting!

---

# Foresight Score (WIP)

> Accurate forecasting is essential, but how do you measure the quality of your predictions? Enter the Foresight Score: a refined tool that improves on the traditional Brier Score by rewarding accurate, confident predictions and penalizing overconfident mistakes more heavily. 

## Understanding the Brier Score
The Brier Score is a simple yet powerful tool for evaluating the accuracy of probabilistic predictions. At its core, it measures how close your predictions are to the actual outcomes. This metric is widely used in fields like meteorology, machine learning, and sports analytics, as it offers a straightforward way to quantify the quality of probabilistic forecasts.
Let’s break down the formula. The Brier Score for a binary outcome (e.g., an event either happens or it doesn't) is calculated as :

```math
Brier Score = 1𝑛∑𝑖=1𝑛(f𝑖−o𝑖)2
```

N: Number of predictions <br/>
fi: Predicted probability for the ii-th event <br/>
oi: Observed outcome for the ii-th event (1 if the event happened, 0 otherwise)

Here, is the forecasted probability of an event occurring, is the actual outcome (1 if the event occurred, 0 if it didn’t), and is the total number of predictions. The score ranges from 0 to 1, where 0 represents perfect predictions and 1 indicates completely inaccurate predictions.
To understand this better, let’s look at an example. Imagine a weather app predicting the chance of rain:

Here's the forecast for rain on any given day. What is the Brier score for the forecast?

Day 1: It predicts a 90% chance of rain, and it does rain.<br/>

```math
Brier Score = 1𝑛∑𝑖=1𝑛(.9−1)2 = .01
```

Day 2: It predicts a 20% chance of rain, and it doesn’t rain.<br/>

```math
Brier Score = 1𝑛∑𝑖=1𝑛(.2−0)2 = .04
```

Day 3: It predicts a 50% chance of rain, and it rains.

```math
Brier Score = 1𝑛∑𝑖=1𝑛(.5−1)2 = .25
```

Lower scores indicate better predictions. The Brier Score doesn’t just measure whether you got the outcome right or wrong; it also considers how confident you were in your prediction. The Brier Score has some weaknesses, it is useful relative to a prediction's dificulty, meaning the same Brier Score can have different meaning, depending on how wll other forecasters predict the outcome. 
The Brier Score also treats overconfidence in incorrect predictions and underconfidence in correct predictions the same way. For example, predicting 90% rain when it doesn’t rain is penalized just as much as predicting 10% rain when it does, bot yield a 0.81 Brier score. Moreover, it doesn’t prioritize impactful errors over minor ones.
 
## Introducing the Foresight Score

To address these issues, let’s introduce the Foresight Score, a more advanced metric designed to encourage sharper and more reliable predictions. The Foresight Score builds on the Brier Score by penalizing overconfidence in wrong predictions more heavily while rewarding high-confidence correct predictions. It’s especially useful for applications where precise, actionable predictions are critical, like decision-making.

Here’s how it works:

Scaling to Intuition: The Foresight Score is inverted and scaled to range from 0 to 1, where 1 represents perfect predictions and 0 represents entirely inaccurate predictions. This makes it more intuitive for users.

Overconfidence Penalty: The weight  is calculated as:

The parameter  determines how heavily overconfident incorrect predictions are penalized. Larger values of  emphasize the cost of overconfidence.

Sharpness Penalty: The sharpness penalty encourages well-calibrated confidence in correct predictions. It is defined as:

Customization: The parameter  adjusts the weight of the sharpness penalty relative to the accuracy term, making the score flexible for different contexts.

By combining these elements, the Foresight Score encourages predictions that are both accurate and confident, while penalizing harmful overconfidence.
To address these issues, let’s introduce the Foresight Score, a more advanced metric designed to encourage sharper and more reliable predictions. The Foresight Score builds on the Brier Score by penalizing overconfidence in wrong predictions more heavily while rewarding high-confidence correct predictions. It’s especially useful for applications where precise, actionable predictions are critical, like decision-making predicions.

## How It Works in Practice

The tentative formula is:

```math
Foresight Score = 1𝑛∑[wi ⋅ (f𝑖−o𝑖)2 + α ⋅ SharpnessPenalty(f𝑖−o𝑖)]
```

Where:
wi: A weight that increases for overconfident incorrect predictions.<br/>
This penalizes high-confidence wrong predictions more than low-confidence ones.

Sharpness Penalty: A term encouraging well-calibrated confidence in correct predictions. Defined as:

### Why Use the Foresight Score?
The Foresight Score isn’t just about punishing bad predictions—it’s about creating better incentives. Here’s why it matters:
Encourages Better Predictions: It penalizes overconfidence in wrong predictions more than underconfidence in right ones, pushing forecasters to calibrate better.

**Actionable Feedback**: By separating weights and penalties, it provides clear areas for improvement.

**Customizable**: Parameters like and can be tuned to fit the importance of sharpness or the cost of errors in different contexts.

**Holistic Insight**: It evaluates prediction quality across individual events, categories, and entire systems, making it a powerful KPI for continuous improvement.

Forecasting is a skill that can be improved with deliberate practice and the right techniques. For those looking to sharpen their prediction abilities, a dedicated section in this guide provides actionable steps and methods to enhance forecasting performance.
Whether tracking personal forecasting skill, comparing performance across teams, or evaluating an entire protocol, the Foresight Score helps align incentives towards better decision-making. By adopting this metric, you not only measure performance but actively guide it toward improvement.

---

# Guidelines for Creating Prediction Markets

> Prediction markets are powerful tools for forecasting future events by leveraging the collective knowledge of participants. This guide focuses on actionable steps and considerations for individuals creating prediction markets.

## Step 1: Craft a Clear and Effective Question

### Define the Core Question
- Ensure the question is precise and unambiguous
- Include measurable elements such as time frames, specific metrics, or conditions
- Avoid broad or vague phrasing

**Examples:**
- "Will SpaceX launch Starship into orbit by June 30, 2025?"
- "Will the inflation rate in Country X exceed 5% by December 31, 2024?"

### Specify the Resolution Criteria
- Clearly describe how the outcome will be judged
- Identify trusted, verifiable sources for determining results (e.g., official reports, reputable news outlets)
- Make criteria objective and free of subjective interpretation

### Avoid Ambiguities
- Provide definitions for technical terms or unusual concepts
- Explicitly mention any assumptions or conditions that apply

## Step 2: Write a Detailed Market Description

### Add Context
- Provide background information to help participants understand the importance of the question
- Highlight relevant data or trends that participants may consider

### Explain the Resolution Process
- Detail how and when the market will be resolved
- Include timelines for data publication and dispute resolution, if applicable

### Be Transparent About Changes
- Specify if and how market details might be updated, and how participants will be informed

## Step 3: Engage and Inform Participants

### Encourage Thoughtful Participation
- Highlight the importance of using reliable data and sound reasoning
- Provide resources or examples for newcomers to improve their predictions

### Promote Fair Play
- Set expectations around avoiding manipulation or misuse of the market
- Ensure all participants have access to the same core information

### Incentivize Participation
- Use rewards or recognition for accurate forecasters to boost engagement

## Step 4: Finalizing and Launching the Market

### Double-Check for Clarity
- Revisit the question, description, and resolution criteria to ensure everything is unambiguous and comprehensive

### Communicate Effectively
- Share the market widely and provide regular updates
- Make key dates and milestones clear to participants

## Step 5: Resolve the Market Responsibly

### Follow the Defined Criteria
- Resolve the market strictly according to the predefined resolution criteria
- Reference the agreed-upon sources to declare the outcome

### Be Transparent About the Outcome
- Communicate the resolution process and results clearly to participants

### Learn and Iterate
- Gather feedback from participants to improve future markets
- Review what worked well and address any issues that arose

By focusing on clarity, transparency, and participant engagement, you can create prediction markets that provide meaningful forecasts and foster trust among participants.

---

# Outcome Shares

When you make a prediction on Precog, you are not placing a bet with a bookmaker. You are buying **outcome shares**: onchain tokens that represent a stake in a specific result.

## What You're Buying

Every market has a set of possible outcomes. Precog supports multiple outcomes in a single market, not just Yes/No. A market might have three, five, or more options (e.g., Outcome A / Outcome B / Outcome C). Each outcome has its own share.

- **1 share of the winning outcome = 1 collateral token at resolution**
- **1 share of any losing outcome = 0**

The price of a share at any moment equals the market's current implied probability for that outcome. If "Outcome B" is priced at 0.35, the market believes there is a 35% chance of Outcome B winning.
 
## Price = Probability

This is the core insight. The share price and the probability are the same number expressed differently:

| Share price | Implied probability |
|-------------|---------------------|
| 0.10 | 10% |
| 0.50 | 50% |
| 0.85 | 85% |  

When you buy a share, you are expressing a belief that the true probability is higher than the current price. When you sell, you are either locking in a gain (price went up) or cutting a loss (price went down).

All outcome prices in a market add up to approximately 1. In a three-outcome market priced at Outcome A: 0.45 / Outcome B: 0.35 / Outcome C: 0.20, the sum is 1. Buying one outcome slightly lowers the implied probability of all the others.
 
## How Prices Move

Prices are set by the LS-LMSR curve, not by a matching order book. Every trade shifts the price:

- Buying an outcome increases its price (and slightly decreases the others)
- Selling decreases its price

This means your trade itself moves the market. Larger trades have more impact. Check the price impact shown at checkout before confirming.

See [Understanding Outcomes Pricing](/markets/pricing-mechanism) for a deeper look at the curve mechanics.
 
## Selling Before Resolution

You can sell your shares at any time before the market closes. The curve will buy them back at the current price.

**Selling makes sense if:**
- The probability has moved in your favor and you want to lock in profit
- New information changes your view and you want to cut your loss
- You need the capital back before resolution

**Selling forgoes the full 1-token payout** if your outcome ends up winning. It is a tradeoff between certainty now and potential upside later.
 
## Fees

**Buying outcome shares has no fee.** You pay the curve price and receive shares, nothing extra.

**Selling may incur a fee**, depending on the market. Selling fees, when present, are split between LPs, the market creator, and the protocol. The exact amount is shown before you confirm a sale.
 
## Collateral Tokens

Any ERC-20 token can be used as collateral on Precog. Each market specifies which token it uses. If you're looking to participate in a market denominated in a community or ecosystem token, see [Branded Markets](/launchpad/branded-markets) for context on how those are set up.
 
## What You Can Lose

Your maximum loss on any position is the amount you paid for the shares. If the outcome loses, those shares pay out nothing.

There is no partial credit for being "close" or for the probability being high at close. Resolution is binary per outcome: it either wins or it doesn't.

> Example: You buy 100 Outcome B shares at 0.35 (cost: 35 tokens). Outcome A wins instead. You lose the full 35 tokens. Had you sold your Outcome B shares earlier when the price moved to 0.55, you would have received 55 tokens and locked in a 20-token profit.
 
## Shares Are Onchain

Outcome shares are ERC-20 tokens held directly in your wallet. You own them; Precog has no custody. They can be viewed in any wallet that supports ERC-20 token balances, though they are only redeemable through the Precog protocol at resolution.

---

# Understanding Outcomes Pricing

> In this section, we'll explore how prices are determined for outcomes in Precog's prediction markets. The protocol uses a mechanism called LS-LMSR (Logarithmic Scoring - Logarithmic Market Scoring Rule) to calculate these prices. This pricing mechanism is a core part of how Precog works, running as immutable code on the blockchain to ensure fairness and transparency. Let's dive into how this pricing system functions and why it's particularly well-suited for prediction markets.

## What is an LS-LMSR Curve?

- **Core Concept**: The LS-LMSR curve operates as a cost function that calculates the price to buy shares for specific outcomes in a prediction market.
- **On-Chain Code**: This pricing mechanism is deployed as immutable and transparent smart contracts on the blockchain. This ensures censorship resistance and reliability.
- **Dynamic Pricing**: Prices are not fixed but adjust dynamically based on market activity, reflecting the collective beliefs of participants.
 
## Multi-Outcome Support

- **Simultaneous Outcomes**: Unlike simpler market models, the LS-LMSR curve supports multiple outcomes within the same calculation. This means prices for all possible outcomes are interdependent and calculated together.
- **Cost-Effectiveness**: By handling multiple outcomes in a single calculation, the LS-LMSR mechanism is computationally efficient, reducing gas costs and increasing scalability.
 
## Customization Options

- **Custom Tokens**: Market creators can define custom tokens for liquidity and betting, allowing them to align prediction markets with specific ecosystems or applications.
- **Outcome Labels**: Labels for outcomes can be fully customized, making it easier for other developers to integrate without needing API keys.
 
## Benefits of the LS-LMSR Curve in Precogs

- **Censorship Resistance**: As immutable on-chain code, the LS-LMSR mechanism ensures that no central authority can interfere with its operation.
- **Fair Pricing**: The logarithmic cost function ensures that prices reflect market sentiment without allowing any single participant to dominate.
- **Cost Efficiency**: Supporting multiple outcomes in a single computation minimizes overhead, making prediction markets more accessible.
- **Transparency**: All calculations and adjustments are executed transparently on-chain, fostering trust among participants.
 
By understanding the LS-LMSR curve, market creators and participants in the Precog Protocol can confidently engage in "precogs" that are fair, efficient, and robust against manipulation. Its flexible design and on-chain deployment make it a cornerstone for decentralized forecasting solutions.

---

# Market Resolution

When a market closes, the outcome needs to be determined and recorded onchain so winnings can be paid out. Precog uses a two-layer decentralized resolution system: **Reality.eth** for crowdsourced answers and **Kleros** as an arbitration backstop if answers are disputed.

No single party, including Precog, controls the outcome. Resolution follows the market's stated criteria.

## How It Works

```
┌─────────────────────────────┐
│        Market Closes        │
│   (at creator-set deadline) │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Answer submitted to        │
│  Reality.eth with a bond    │
│  (anyone can submit)        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Challenge window opens     │
│  (duration set per market)  │
└──────────┬──────────────────┘
           │
     ┌─────┴─────────────────┐
     │                       │
  No challenge            Challenged
     │                       │
     ▼                       ▼
┌──────────────┐    ┌─────────────────┐
│ Answer is    │    │ Escalates to    │
│ finalized    │    │ Kleros          │
└──────┬───────┘    └────────┬────────┘
       │                     │
       │            ┌────────▼────────┐
       │            │ Jurors review   │
       │            │ evidence & vote │
       │            └────────┬────────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
     ┌────────────────────────┐
     │   Market resolves      │
     │   Winnings claimable   │
     └────────────────────────┘
```
 
## Reality.eth: Crowdsourced Answers

Reality.eth is a decentralized oracle that determines outcomes by having participants put money where their mouth is.

**How bonding works:**
1. After a market closes, anyone can submit an answer by posting a bond (a small deposit)
2. If someone disagrees, they can challenge by posting a bond at least double the previous one
3. Each challenge resets the timer
4. If no challenge is posted before the window expires, the last answer becomes final

The escalating bond mechanism means that submitting a wrong answer is increasingly expensive to maintain. Honest answers tend to survive because it only takes one correct challenger to overturn a wrong one.
 
## Kleros: Arbitration Backstop

If a dispute cannot be resolved through bonding alone (because the answer is genuinely ambiguous or requires interpretation), it escalates to **Kleros**.

Kleros uses a court of randomly selected, anonymized jurors who review the evidence and vote. Their ruling is final and onchain. Jurors are economically incentivized to rule honestly (voting with the majority earns rewards; voting against loses stake).

This means even edge cases and contested outcomes have a credible, decentralized path to resolution.
 
## Resolution Timeframes

There is no fixed global timer. Each market has its own:

- **Market close date** - when trading stops and the question is evaluated
- **Challenge window** - set per market; the time during which a Reality.eth answer can be disputed

Creators set these when designing the market. Longer windows give more time for disputes but delay payouts. Check the market details page for the specific dates.
 
## Writing Good Resolution Criteria

The most common reason a market fails or gets disputed is vague resolution criteria. Reality.eth answerers need to look at a source and say definitively "yes" or "no."

**Good:**
> "Will Argentina win the 2026 FIFA World Cup final, according to the official FIFA full-time result published on July 19, 2026?"

**Bad:**
> "Will Argentina do well at the World Cup?"

Rules of thumb:
- Name a specific data source (an official governing body, a published record, a live broadcast result)
- Include an exact date and time with timezone
- Define what "yes" looks like unambiguously
- Anticipate edge cases (what if the event is postponed? what if the match goes to extra time or penalties?)

---

# Mate Markets 🧉

You can visit MATE token's page [here](https://www.matetoken.xyz/).

## The Problem

Onchain apps carry real financial risk. For newcomers (people who have never used a prediction market, never held a crypto wallet, or never made a probabilistic forecast), this risk creates a barrier. The stakes feel too high to experiment and learn.

## The Solution: MATE Token

**MATE** is a non-monetary practice token with no economic value. It lets users participate in Precog prediction markets without putting real money at risk.

Think of it as training wheels: you use real Precog markets, real mechanics, and real resolution, but with MATE instead of ETH or USDC. When you make a wrong prediction, you lose MATE. When you're right, you gain it. Nothing real is at stake, but everything about how the market works is identical.

## Why It Matters

The biggest obstacle to good forecasting is not a lack of intelligence; it is a lack of practice. Superforecasters become accurate through repetition and feedback, not intuition alone. MATE gives users a safe environment to:

- Learn how to read market probabilities
- Practice forming and expressing a view
- Understand price impact and curve mechanics
- Make mistakes cheaply, then adjust

## How to Get MATE

MATE can be claimed at [matetoken.xyz](http://matetoken.xyz).

To be eligible, you must validate you are a human (no KYC required). We validate your passport keeping your identity private using [zkPassport](https://zkpassport.id/).

### Other ways to get MATE tokens

meet at least one of the following criteria:

- Have a **Devconnect ARG** ticket
- Have a **Devcon SEA** ticket
- Hold any **Devcon or DevConnect official POAP** token
- Have a **Zupass** from any Devcon or Devconnect
- Have attended any **Edge City** event

If you qualify, claim your MATE directly here: [core.precog.markets/claim](https://core.precog.markets/claim/8453/mate)

## Who Should Use MATE Markets

- Anyone new to prediction markets
- Crypto-curious users who want to try onchain interaction without financial exposure
- Experienced forecasters who want to test a new strategy before committing real capital
- Communities and DAOs running educational forecasting programs

## How to Get Started

Check eligibility and [claim your MATE](https://core.precog.markets/claim/8453/mate), then start predicting on practice markets.

---

# Creator Markets

On Precog, market creators ask questions about the future and turn them into prediction markets. They earn a share of the profits when their market resolves, plus the reputational value of running a well-designed, engaging market.

When a market resolves:
1. The winning outcome traders are paid first.
2. Any money left over is the profit pool.
3. That profit pool is split: 90% to LPs, 5% to the market creator, 5% to the protocol (which currently ALSO go to market creators through the creator boost program).

The key for creators is to design markets that attract trading, more trading means more potential leftover profit and therefore higher earnings. Multi-outcome markets often perform better, as they spread trader bets across more possibilities, increasing the chance that the winning outcome is underbet.

### A. Profitable Creator

Question: Which L2 will have the most daily transactions on Dec 31, 2025? (Outcomes: Arbitrum, Base, Optimism, zkSync, Starknet, Other.)

LP funds \$1,000. The market gets active with heavy betting on Arbitrum and Optimism.
Base wins with only 15% probability at close. Profit pool after paying Base traders: \$800. Creator share (5%): \$40 profit — no capital at risk.

### B. Obvious Market - Lower Earnings
Question: Will Ethereum’s Shanghai upgrade happen before June 2023?
Market quickly shifts to 99% “Yes” as date becomes certain.
LPs take a small loss (under 10%), leaving almost no profit pool.
Creator earns close to \$0.

## Why Creators Like This Model
No upfront capital required (you can still LP in your own market if you want to boost returns).
Earnings scale with engagement — the more traders and liquidity, the more potential profit.
Creative freedom to design markets on any topic allowed by Precog’s rules.

---

# Liquidity Provision

On Precog, liquidity providers (LPs) fund prediction markets to earn a share of the profits when those markets resolve. LPs put up capital that gets spread across all possible outcomes of a question.
When the market resolves:
1. Traders who hold the winning outcome get paid first.
2. Any money left over is the profit pool.
3. That profit pool is split: 90% to LPs, 5% to the market creator, 5% to the protocol.

Because more outcomes mean traders’ bets are spread thinner, multi-outcome markets can offer LPs higher potential profits if the probabilities are correctly distributed and traders overbet the wrong options.

Important: LP positions are locked until market resolution, there’s currently no way to sell or trade them early.

## Examples

### A. Multi-Outcome, Profitable LP
Market: Who will win the 2026 FIFA World Cup? (8 outcomes: Brazil, France, Argentina, Spain, Germany, England, Italy, Other)
LP funds \$1,000 in total.
Traders heavily bet on Brazil (60%) and France (25%), leaving smaller bets on others.
Argentina wins at 10% probability.
After paying Argentina traders, there’s \$1,800 left in the pool.
Profit pool: \$1,800 – \$1,000 initial liquidity = \$800 profit.
LP share (90%): \$720 profit + original \$1,000 back = \$1,720 total payout.

### B. Multi-Outcome, Small LP Loss
Market: Who will be the next U.S. Federal Reserve Chair? (5 outcomes: Current Chair stays, Candidate A, Candidate B, Candidate C, None)
LP funds \$1,000 in total.
Traders heavily bet Current Chair stays up to 99% probability (obvious market).
This outcome wins.
LP loss is capped under 7% → LP gets back ~\$910 (original \$1,000 minus \$90 loss).

## Virtual Liquidity

Some markets on Precog use virtual liquidity. In these markets, LPs only need to deposit what they can actually lose (their Max Loss) rather than the full curve depth. The rest of the liquidity depth is mathematically guaranteed to be covered. There will always be enough capital to pay all the winning shares of the market.

### Classic LP vs. Virtual LP

Using the same $1,000 market from the examples above:

|  | Classic LP | Virtual LP |
|---|---|---|
| Market curve depth | $1,000 | $1,000 |
| LP deposits | $1,000 | ~$70 |
| Max loss | ~$70 (7% of deposit) | ~$70 (100% of deposit) |
| If profitable: LP earns $720 | ROI ≈ 72% | ROI ≈ 1,028% |

The absolute outcomes are identical: the same maximum loss in dollar terms, the same potential profit in dollar terms. The only difference is how much capital is tied up. With virtual LP, the same $1,000 budget can back ~14 markets instead of 1.

You are not taking on more risk in dollar terms; you are just not locking up extra idle capital alongside it. The worst case is identical to classic LP in absolute terms. 

### Is a market using virtual liquidity?

This is set per market by the market validator. Check the market's details before providing liquidity to see whether virtual liquidity is enabled and what your Max Loss will be.

Use the [simulator](/launchpad/simulator) to learn more about Max Loss.

## Key Takeaways
- Multi-outcome = higher profit potential if market probabilities are wrong.
- Obvious markets (near 99% probability before close) always result in an LP loss (usually less than 7% from investment).
- LPs earn from 90% of profit after winning bets are paid, plus trading fees collected during the market.
- LP positions are illiquid until market resolution. No early exit.
- Markets with virtual liquidity only require LPs to deposit their Max Loss, not the full curve depth.
- Same absolute outcomes, but far higher ROI, and the same capital can be spread across many more markets.

You have reached the end of this LP rabbithole. If you want to dig deeper, follow the white rabbit to simulate different scenarios -> [🕳️🐇](/launchpad/simulator)

*Disclaimer: LP losses are capped at around 7% in obvious market under normal market conditions. However, providing liquidity carries other risks, including smart contract bugs, oracle failures, or market manipulation, which could result in a total loss of funds.

---

# Market Simulator

The Market Simulator lets you model a prediction market without risking real funds. Adjust parameters, run simulated trades, and see exactly what an LP would earn or lose under different scenarios: before committing any capital.

## How to access it

There are three ways to open the simulator:

1. **From any market's detail panel**: open a market on Precog, then click the lab flask icon in the top-right corner of the panel. The simulator opens pre-loaded with that market's current configuration.

2. **From your profile**: if you have funded a market, you can launch its simulator directly from your profile view.

3. **Directly**: visit [core.precog.markets/simulator](https://core.precog.markets/simulator) to open a blank simulator you can configure from scratch.

## Configuring your simulation

Click the pencil icon in the top-right corner of the simulator to open the **Edit Configuration** modal. You can set:

- **Question**: the market question label. This is for your reference only and has no mechanical effect on the simulation.
- **Overround**: suggested range: 0.02–0.3. Controls the margin built into prices. A higher value makes the market "deeper": larger trades move the price less, implied probabilities become more stable and resistant to small speculative trades, and LP risk stays capped (typically under 7% loss in obvious markets where one outcome nears 100% certainty). The tradeoff is a higher collateral requirement for LPs to achieve that depth.
- **Sell Fee**: suggested range: 0–20%. The percentage charged when a trader sells outcome shares back to the market. This fee is split between the LP, the creator, and the protocol at resolution.
- **Initial Liquidity**: suggested minimum: 1,000 per outcome. The capital seeding the market's price curve. More liquidity means tighter prices and greater resistance to manipulation.
- **Outcomes**: add or remove possible outcomes. More outcomes disperse trader bets across more options, which can increase LP profit potential when the market resolves on a low-probability outcome.

## Running simulated trades

The simulator includes three trader personas: **Alice**, **Bob**, and **Charlie**: each represented by a tab in the **Make your prediction** panel.

To place a trade:
1. Select a persona tab.
2. Choose an outcome from the dropdown.
3. Enter a value using the **Shares / Cost / Price** toggle to specify how you want to size the trade: by number of shares, by total cost, or by target price.
4. Click **Buy**.

To run a batch of random trades across all personas at once, click **Simulate trades**. This fills the market with synthetic activity so you can quickly see how the metrics evolve.

The **trade history chart** shows the price curve for each outcome over time as trades accumulate. The **trade log** at the bottom lists each individual trade with its persona, outcome, shares, and cost.

## Reading the results panels

### Market config

Displays the parameters currently in effect:

| Field | Description |
|-------|-------------|
| Overround | The margin built into prices |
| Alpha | Derived from Overround; the LS-LMSR sensitivity parameter |
| Initial Liquidity | The capital seeded into the curve |
| Outcomes | Number of possible outcomes |
| Sell Fee | Fee charged on sells |

---

# Branded Markets

#### TL;DR
Precog serves onchain organizations by providing customized prediction markets. These enable clients to customize the banner, define the links to external sites, and select the token denominated in the market, the token icon, and, lastly, set up a distribution of the token if needed.
Branded Markets are a paid, white‑label offering from Precog. Optional advisory and integration support is available.

Interested? You can reach out on [Discord](https://discord.gg/frgXQfM3KZ) or [email](mailto:admin@precog.markets?subject=Branded%20Markets%20Inquiry).

## What is a Branded Market

A Branded Market is a curated prediction market hosted on Precog that carries your brand, your token, and your calls to action. It is designed for organizations that want to run forecasting campaigns, research programs, or futarchy-style decision support while keeping their visual identity and growth links front and center. Delivered as a scoped, white‑label prediction market, it includes setup, launch support, and reporting, with optional advisory and integration.

**You control**

* Visual banner and brand palette
* Clickable links and CTAs to your site, docs, quests, or forms
* Market denomination token (any supported ERC‑20)
* Token icon shown across the market UI
* Optional token distribution plan tied to market participation or outcomes *(optional)*

**We handle**

* Liquidity mechanics and settlement
* Strategy advisory (market design, futarchy) *(optional)*
* Integration support (widgets, APIs, SSO/wallet embed, oracles) *(optional)*
* Results, analytics, and post‑mortem reporting

## Who is it for

Protocols and onchain organizations running research or governance experiments looking for accurate predictions. L2s, foundations, and ecosystems seeking ecosystem‑wide engagement. Also for media, tournaments, and events that want live community forecasting

## Implementation flow

1. **Brief** – You share the market goals, primary user journey, success metrics, timelines.
2. **Assets** – Provide banner, logo, token icon, brand colors, link targets, and token contract.
3. **Market design** – We co‑draft questions, outcomes, and resolution criteria. You approve.
4. **Token setup** – Confirm chain, token decimals, denomination, and any distribution rules.
5. **Liquidity plan** – Decide whether you provide LP, we co‑fund, or we source LPs.
6. **Compliance review** – Resolution sources, timing, and any geographic restrictions.
7. **Launch** – Markets go live with your brand and CTAs. We monitor performance.
8. **Reporting** – Final reports on reach, trading, and forecasting accuracy.

## Liquidity Provision – how it works on Precog

On Precog, liquidity providers (LPs) fund prediction markets to earn a share of the profits when those markets resolve. LPs put up capital that gets spread across all possible outcomes of a question. When the market resolves:

**Important:** LP positions are locked until market resolution. There is no early exit or secondary trading for LP shares at this time.

You can read more on Precog's [Liquidity Provision](/launchpad/liquidity-provision) section. 

## Advisory & integration services (optional)

We can work alongside your team on:

* **Strategy advisory:** question sourcing, governance/futarchy design, risk checks
* **Technical integration:** embed widgets, APIs/webhooks, oracles/resolvers, wallet/SSO flows
* **Custom UI & data:** branded components and dashboards
* **Analytics:** forecasting accuracy reviews, trader cohorts, campaign lift

> Note: The service and advisory fees are separate from protocol fees at resolution.

## FAQ

**Is this a paid service?**
Yes. Branded Markets are the way to make Precog sustainable and impartial. We scope your campaign and provide a quote covering setup, customization, launch support, reporting, and any advisory/integration work.

**Can Precog advise us on market design or governance?**
Yes. We offer paid strategy advisory for question sourcing, futarchy/governance design, and risk checks.

**Can you integrate Precog into our app or site?**
Yes. We provide paid integration support via widgets, APIs/webhooks, oracle/resolver setup, and wallet/SSO flows.

**Can we denominate in our own token?**
Yes, if the token and chain are supported and pass risk checks.

**Can we add multiple links and track conversions?**
Yes. We support multiple CTAs and UTM parameters.

**Who provides liquidity?**
Options include you, community LPs, or co‑funding. LP shares are locked until resolution.

**What does the creator earn?**
5% of the profit pool at resolution. This is separate from any service or advisory fees.

**How fast can we launch?**
After assets and criteria are finalized, launches typically take days, not weeks. Exact timing depends on scope and approvals.

**What risks should we disclose?**
LP capital can lose value. Smart contract, oracle, and market manipulation risks exist. Participants should read disclosures.

## Next steps

* Request a **quote** for a Branded Market (share scope, audience, dates, and any advisory/integration needs)
* Share a draft **Market brief** and **Asset checklist**
* Confirm chain and token details
* Align on timelines, reporting cadence, and compliance
* Sign a short **SOW** to kick off

Ready to explore scenarios before launch? Follow the white rabbit to the market simulator → [🕳️🐇](https://core.precog.markets/simulator)

---

# Your Wallet

Precog is a fully onchain protocol. Your funds, outcome shares, and winnings are held directly in a wallet, not in a Precog account. Every action you take is a signed transaction on the blockchain.
 
## Types of Wallets

### Embedded wallets (email login)

If you sign in with email, Precog creates an embedded wallet for you automatically. No setup required.

**Tradeoff:** The private key is managed by the wallet provider, not you. You trust that provider's infrastructure for custody and recovery. If the provider has an outage or shuts down, access to funds may require a recovery process.

### Self-custodied wallets (MetaMask, Rabby, etc.)

You hold the private key (and seed phrase) yourself. No third party can freeze or access your funds.

**Tradeoff:** If you lose your seed phrase, funds are unrecoverable. You are fully responsible for key security.

> Embedded wallets reduce friction while self-custody gives full ownership. As your balance grows, we suggest transitioning out from your embedded wallet into a self-custody solution.
 
## Finding Your Wallet Address

Your wallet address is a unique identifier that starts with `0x`. You need it to receive funds from a bridge or onramp.

**On Precog:** go to [your profile](https://core.precog.markets/profile). Your address is displayed next to your avatar. Click the copy icon to copy the full address.

 
## Checking Your ETH Balance

Your ETH balance is shown in the top-right corner of Precog, next to the "Fund wallet" button. If it shows `0 ETH`, your wallet has no funds yet.

Precog is multichain. Clicking the balance indicator lets you see how much ETH you hold on each supported network (Base, Ethereum, and Arbitrum) separately, so you know exactly where your funds are before bridging or trading.

You can also paste your `0x` address into [Etherscan](https://etherscan.io/) to see your full balance and transaction history.
 
Ready to add funds? See [Getting Funds onto Precog](/blockchain/fund-wallet).

---

# Getting Funds onto Precog

Precog runs on **Base** (**Ethereum** and **Arbitrum** coming soon). To participate, you need ETH or the market's collateral token in your wallet on the correct network.

Not sure where your wallet address is or how to check your balance? See [Your Wallet](/blockchain/your-wallet) first.
 
## I Have Funds on Another Chain

Your funds are safe, they just need to be moved to Base. Use a bridge.

### Recommended bridges

| Bridge | Best for |
|--------|----------|
| [deBridge](https://app.debridge.finance/) | Wide chain support, fast transfers |
| [Across](https://across.to/) | Speed-optimized, low fees, intent-based |
| [Jumper Exchange](https://jumper.exchange) | Aggregator that compares many bridges at once |

**Steps:**
1. Open your preferred bridge
2. Select your source chain and **Base** as the target
3. Choose the token and amount, then confirm the transaction in your wallet

> If the bridge aggregator doesn't support your chain, check the chain's official site for a native bridge.
 
## I'm New and Have No Crypto Yet

You'll need to purchase crypto first, then send it to your wallet.

### Peer (decentralized p2p)

[Peer](https://www.peer.xyz/) is a decentralized, peer-to-peer onramp. You buy crypto directly from another user, no centralized company holds your funds in the process. This is the most trust-minimized way to onboard.

### Centralized onramps

- [Coinbase](https://coinbase.com/) - straightforward for beginners, supports debit/credit card and bank transfer
- [MoonPay](https://www.moonpay.com/) - card-based, available in many countries

**After purchasing:**
1. Find your wallet address in your [Precog profile](/blockchain/your-wallet)
2. Send funds to that address, making sure to select the market network when withdrawing. Usually it would be on Ethereum, Base or Arbitrum.
 
## Final Note

Always do your own research before using any third-party service. Precog is not liable for issues arising from fund transfers outside our platform.

---

# Precog's Roadmap

🟢 Completed | 🔵 In Progress | 🟣 Planning | ⚪️ Future 

### 1. Fully Onchain Core 🟢
All prediction logic is executed by smart contracts
Transparent, immutable, and verifiable markets

### 2. Censorship Resistance & Permissionless 🟢
No centralized control over trade execution
No gatekeepers; anyone can predict
No KYC, no whitelists — anyone can trade.

### 3. Open Funding  🟢
Anyone can fund a question and profit from it’s success

### 4. Open Liquidity & Fee Structure 🟢
Community-owned incentives: creators earn

### 5. Modular & Composable 🟢
Designed for integration with DAOs, DeFi, and external agents
Precog as a building block for governance and coordination

### 6. Multi-Frontends (Redundancy + Resilience) 🟢
MiniApps (Farcaster & Base Wallet) 
OSS frontend (https://dev.precog.markets/)
Mirror-friendly architecture

### 7. Decentralized Resolution System 🟢
Reality.eth & Kleros integrations

### 8. Deep Forecasting ⚪️
MCP for Agents to use Precog’s predictions
Agents can create and fund questions for better decision-making

### 9. Opportunity Markets 🟣
Priority access to predictions for funders

### 10. Privacy-Preserving Trading 🟣
Optional anonymous trading and prediction staking

### 11. Futarchy-Aligned Infrastructure ⚪️
Futarchy Curated Registries (FCRs)
Decision markets for DAO votes, grant allocation, and parameter tuning

### 12. Radical Question Freedom ⚪️
No KYC, no whitelists — anyone can create or resolve markets
Launching Precog Constitution + Market Policy Layer
Question arbitration
