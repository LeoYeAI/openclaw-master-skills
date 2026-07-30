# I Fed a Viral Quant Thread to My AI Agent. It Built 7 Working Tools in One Shot.

A post by [@gemchange_ltd](https://x.com/gemchange_ltd) called "How to Simulate Like a Quant Desk" hit 2.7 million views last week. 21,000 people bookmarked it. I was one of them.

Then I actually did something with it.

## The post that started it

If you haven't seen it - it's a 28,000-character deep dive into quantitative simulation. Monte Carlo methods, importance sampling, particle filters, copulas, agent-based models. Every section has formulas, explanations, and Python code.

It's the kind of post you bookmark, tell yourself you'll read later, and never do. I know because I've done that hundreds of times.

But this time I had a different idea.

## One prompt

I run [Claude Code](https://docs.anthropic.com/en/docs/claude-code) as my daily driver for development. It's an AI coding agent that lives in the terminal. I pointed it at the article and said something like:

> Read this article. Extract every piece of code. Build standalone, runnable tools from each section. Make sure they actually work.

That's it. No architecture diagram. No spec document. No careful extraction of code blocks by hand. Just - here's a massive quant article, turn it into tools.

The agent read 28K characters of quant math, identified 6 distinct simulation techniques, extracted the code from each section, filled in the gaps (the article had some pseudocode and implied imports), built 7 standalone Python scripts, and verified each one ran correctly.

Took maybe 10 minutes.

## What it built

Seven tools. Each one a self-contained Python script that you can run right now. Here's what they do and what they output.

### 1. Binary Contract Pricer (`binary_pricer.py`)

Prices binary options using both Black-Scholes analytical solution and Monte Carlo simulation. Think: "Will AAPL close above $200 by March 15?" - this gives you the probability and shows how Monte Carlo converges to the analytical answer.

```
Black-Scholes analytical price [N(d2)]: 0.411781
   n_paths     MC Prob    CI Width       Error
     1,000    0.416000    0.061100    0.004219
   100,000    0.408990    0.006095    0.002791
Brier score (MC[100k] vs analytical): 0.00000779
```

The Brier score of 0.0000078 means the Monte Carlo estimate at 100K paths is essentially identical to the closed-form solution. That's a nice sanity check that the simulation engine works.

### 2. Tail Risk Simulator (`tail_risk.py`)

This one's clever. When you're trying to estimate the probability of rare events - like "S&P drops 20% in a week" - crude Monte Carlo fails. You might get zero hits in 100,000 samples.

Importance sampling solves this by deliberately oversampling the crash region, then correcting the bias mathematically.

```
Crude Monte Carlo    P=0.010480  SE=3.22e-04
Importance Sampling  P=0.010115  SE=5.20e-05
Variance Reduction Factor: 38.3x
IS oversamples crash region by ~48x
```

38x variance reduction. That means you get the same precision with 38 times fewer samples. Or way better precision with the same compute budget. In production, this is the difference between "we can't price this contract" and "we're trading it."

### 3. Particle Filter (`particle_filter.py`)

Real-time probability updating. Feed it observations - market prices, poll results, vote counts - and it maintains a swarm of particles representing hypotheses about the true probability. As data arrives, particles that match reality survive, others die off.

The example simulates election night tracking:

```
Election Night Tracker:
 Step  Observed  Filtered  95% CI
    1     0.500     0.466  (0.247, 0.697)
   50     0.650     0.541  (0.335, 0.734)
Mean Absolute Error: 0.0949
```

Wide confidence interval at the start (we don't know much), narrowing as data comes in. The filter smooths noise - when a market price spikes on a single trade, the filter recognizes the true probability might not have moved that much. This is what election forecasting desks actually use.

### 4. Variance Reduction Toolkit (`variance_reduction.py`)

Three techniques that stack multiplicatively: antithetic variates, control variates, and stratified sampling. Each one squeezes more precision out of the same number of samples.

```
Crude MC           10.420541  VR: 1.00x
Antithetic         10.467314  VR: 2.00x
Control Variate    10.466844  VR: 6.85x
Combined           10.450475  VR: 28.87x
```

Combined: nearly 29x variance reduction. Free performance. The original article calls this "table stakes in production" and I believe it. You'd be leaving money on the table running crude Monte Carlo when these techniques exist.

### 5. Copula Simulator (`copula_sim.py`)

This is where it gets interesting. Copulas model how multiple events correlate - especially in the tails. The Gaussian copula (the one that contributed to the 2008 financial crisis) assumes extreme co-movements have zero probability. That's catastrophically wrong.

The tool compares independent, Gaussian, Student-t, and Clayton copulas for a portfolio of correlated events:

```
Independent P(sweep): 0.05033 (1.0x)
Gaussian:             0.17151 (3.4x)
Student-t:            0.17197 (3.4x)
Clayton:              0.28317 (5.6x) -- crash contagion
```

Clayton copula shows 5.6x higher probability of a joint crash compared to the independence assumption. If you're trading correlated prediction market contracts without modeling tail dependence, you're running a portfolio that will blow up in exactly the scenarios that matter most.

### 6. Market Agent-Based Model (`market_abm.py`)

Simulates a prediction market populated by three types of agents: informed traders (who know something), noise traders (who don't), and market makers (who provide liquidity). Emergent price discovery from pure agent interaction.

```
Informed traders: +157.20
Noise traders:    -21.45
Market maker:     -0.25
Kyle lambda configured: 0.0500, estimated: 0.0487
```

Informed traders profit. Noise traders lose. The market maker barely breaks even. And the price converges toward truth. The estimated Kyle lambda (price impact parameter) matches the configured value almost perfectly - which validates that the microstructure model is working correctly.

### 7. Pipeline Runner (`pipeline.py`)

Runs all 6 tools end-to-end. One command, full quant simulation stack.

## What actually happened behind the scenes

I want to be honest about this because "AI did everything perfectly" stories are usually lies.

The agent did about 90% of the work cleanly on the first pass. The original article had some code that was more pseudocode than runnable Python - missing imports, implied helper functions, parameters referenced but not defined. The agent filled those gaps intelligently.

A few things needed tweaking. Some of the output formatting didn't match what I wanted. One of the random seeds gave confusing results on the first run. Small stuff.

But the core simulation logic - the math, the algorithms, the statistical methods - was correct. The Brier scores check out. The variance reduction factors are in the expected ranges. The copula tail dependencies match the theoretical predictions from the original article.

I didn't have to understand the Radon-Nikodym derivative to get a working importance sampler. I didn't need to implement systematic resampling from scratch. The agent read the article, understood what each section was trying to do, and built it.

## The actual point

There's a pattern here that I think matters.

Every week, someone publishes an incredible technical thread. Quant finance, ML pipelines, distributed systems, whatever. Millions of views. Thousands of bookmarks. And maybe 0.1% of those people actually implement anything from it.

The gap between "I bookmarked a great article about quant simulation" and "I have 7 working quant simulation tools on my machine" used to be weeks of work. Understanding the math, debugging the code, filling in the gaps between theory and implementation.

Now it's one prompt.

I'm not saying you don't need to understand the math eventually. If you're going to trade real money using these models, you better understand what a copula does and why Clayton captures crash contagion differently than Gaussian. But the barrier to getting started - to having something runnable, something you can experiment with, something that demystifies the theory - that barrier is basically gone.

You don't need a quant PhD. You don't need a Bloomberg terminal. You need a good article and a good agent.

## Get the tools

I packaged all 7 tools as a skill on ClawHub: {{CLAWHUB_LINK}}

Install it, run `pipeline.py`, and you've got a quant simulation stack on your laptop. Poke at the code. Change the parameters. Break things. That's how you learn this stuff.

The original article by [@gemchange_ltd](https://x.com/gemchange_ltd) is genuinely excellent - probably the best single overview of quant simulation techniques I've seen in a social media post. Go read it. Or do what I did and let your agent read it for you.
