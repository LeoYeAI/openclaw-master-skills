# Page Templates Reference

Each page type has a specific structure that performs well in search.
The skill auto-detects page type from the keyword intent, but users can override.

## Service Page

**Triggers:** "[service] in [location]", "[service] company", "[service] near me"

**Structure:**
```
H1: [Service] in [Location] - [Value Prop]
  H2: What Is [Service] / How [Service] Works
  H2: [Service] Options / Types of [Service]
    H3: [Option 1]
    H3: [Option 2]
    H3: [Option 3]
  H2: Pricing / What Does [Service] Cost
  H2: How to Choose [a/the right] [Service Provider]
  H2: Why [Company/Location] for [Service]
  H2: Frequently Asked Questions
    H3: [PAA Question 1]
    H3: [PAA Question 2]
    H3: [PAA Question 3]
```

**Schema:** LocalBusiness + FAQPage
**Word count target:** 1500-2500
**Must include:** Pricing (even ranges), specific location references, social proof

## Comparison Page

**Triggers:** "[X] vs [Y]", "best [category]", "[product] alternatives", "top [N] [category]"

**Structure:**
```
H1: [X] vs [Y]: [Differentiating Angle] ([Year])
  H2: Quick Comparison / TL;DR
    [Comparison table]
  H2: What Is [X]
    H3: Key Features
    H3: Pricing
    H3: Best For
  H2: What Is [Y]
    H3: Key Features
    H3: Pricing
    H3: Best For
  H2: [X] vs [Y]: [Criteria 1]
  H2: [X] vs [Y]: [Criteria 2]
  H2: [X] vs [Y]: [Criteria 3]
  H2: Which Should You Choose?
  H2: FAQ
```

**Schema:** FAQPage (+ Product if applicable)
**Word count target:** 2000-3500
**Must include:** Comparison table near top, specific criteria-based sections, clear recommendation

## How-To / Guide

**Triggers:** "how to [action]", "[topic] guide", "[topic] tutorial"

**Structure:**
```
H1: How to [Action]: [Qualifier] Guide ([Year])
  H2: What You'll Need / Prerequisites
  H2: Step 1: [Action]
    H3: [Sub-step if complex]
  H2: Step 2: [Action]
  H2: Step 3: [Action]
  H2: [N] more steps...
  H2: Common Mistakes / Troubleshooting
  H2: Tips from [Experts/Experience]
  H2: FAQ
```

**Schema:** HowTo + FAQPage
**Word count target:** 1500-3000
**Must include:** Numbered steps, specific examples, troubleshooting section

## Location Page

**Triggers:** "[service] [city]", "[business type] [neighborhood]", "[thing to do] in [location]"

**Structure:**
```
H1: [Service/Topic] in [City, State] - [Value Prop]
  H2: [Service] Options in [City]
    H3: [Option/Area 1]
    H3: [Option/Area 2]
  H2: [City]-Specific Information
    [Local details: regulations, seasonality, landmarks, neighborhoods]
  H2: Pricing in [City]
  H2: How to [Get Started/Book/Find] [Service] in [City]
  H2: Tips for [Service] in [City]
  H2: Nearby Alternatives
    [Adjacent cities/neighborhoods]
  H2: FAQ
```

**Schema:** LocalBusiness + FAQPage + BreadcrumbList
**Word count target:** 1200-2000
**Must include:** Specific local details (not generic), nearby alternatives for internal linking, local pricing

## Product / Feature Page

**Triggers:** "[product] features", "[product] review", "[product] pricing"

**Structure:**
```
H1: [Product Name]: [Key Benefit] ([Year])
  H2: What Is [Product]
  H2: Key Features
    H3: [Feature 1] - [Benefit]
    H3: [Feature 2] - [Benefit]
    H3: [Feature 3] - [Benefit]
  H2: Pricing
    [Plans table or breakdown]
  H2: Pros and Cons
  H2: Who Is [Product] Best For
  H2: [Product] vs Alternatives
  H2: How to Get Started
  H2: FAQ
```

**Schema:** Product + FAQPage + Review (if review angle)
**Word count target:** 1500-2500
**Must include:** Pricing specifics, honest pros/cons, clear "best for" segment

## General Quality Rules (All Templates)

1. Every H2 section should have at least 150 words of substantive content
2. FAQ sections use the exact PAA questions (or close variants) as H3s
3. Include at least one data point, stat, or specific example per major section
4. Internal links should go in contextually relevant spots, not dumped at the bottom
5. Schema markup matches the page type (see schema-patterns.md)
6. Year in title only if the content is genuinely time-sensitive
7. No filler paragraphs. If a section doesn't add value, cut it.
