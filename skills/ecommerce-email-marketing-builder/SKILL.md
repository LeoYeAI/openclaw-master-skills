---
name: ecommerce-email-marketing-builder
description: "E-commerce email marketing system builder. Creates complete email automation flows with full copywriting, subject lines, ESP setup instructions, segmentation rules, and annual campaign calendars. Generates copy-paste-ready email sequences for Klaviyo, Omnisend, Mailchimp, or any ESP. Covers welcome series, cart abandonment, browse abandonment, post-purchase, review requests, cross-sell, win-back, VIP/loyalty, replenishment, and sunset flows. Includes A/B test subject line variants, send timing, trigger conditions, branching logic, and seasonal campaign calendar. No API key required. Use when: (1) setting up email marketing for an e-commerce store, (2) writing email sequences and flows, (3) planning seasonal email campaigns."
metadata:
  nexscope:
    emoji: "📧"
    category: ecommerce
---

# E-Commerce Email Marketing Builder 📧

Build a complete, copy-paste-ready email marketing system for any e-commerce business. Covers 10 core automation flows with full copywriting, ESP setup instructions, segmentation rules, and annual campaign calendars.

**Supported platforms:** Shopify, WooCommerce, BigCommerce, Squarespace, Etsy, TikTok Shop, Amazon, and any platform that connects to an ESP. For marketplace platforms (Amazon, TikTok Shop, Etsy) where buyer emails are restricted, this skill focuses on cross-channel strategies to capture emails via your own website or landing pages.

Built by [Nexscope](https://www.nexscope.ai/) — your AI assistant for smarter e-commerce decisions.

## Install

```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-email-marketing-builder -g
```

## Usage

Once installed, just describe your business and ask for email marketing help. The skill activates automatically.

```
I'm launching a Shopify store selling premium dog treats at $24.99. Help me set up 
my email marketing — I'm using Klaviyo and have about 500 subscribers.
```

```
I sell handmade jewelry on Etsy and my own website. Price range $40-120. I have 
2,000 email subscribers but no automated flows set up. What emails should I be sending?
```

```
Build me a complete email system for my sustainable fashion brand. We use Omnisend 
and have 8,000 subscribers. I want welcome series, cart abandonment, and post-purchase flows.
```

## Capabilities

- Complete email automation flows for 10 core e-commerce journeys (welcome, cart abandonment, browse abandonment, post-purchase, review request, cross-sell, win-back, VIP/loyalty, replenishment, sunset)
- Full email copywriting for every email — subject lines, preview text, body copy, CTA button text
- 3-5 A/B test subject line variants per email with different angles (curiosity, urgency, benefit, social proof, personal)
- ESP setup instructions generated for your specific platform — trigger conditions, flow filters, delay timing, and branching logic using your ESP's exact terminology
- ESP recommendation if you don't have one yet — based on list size and sales platform, with pricing
- Flow diagrams showing the full sequence: trigger → delay → conditional split → email → branch
- Segmentation strategy with 8 core segments and exact filter conditions for your ESP
- Annual seasonal campaign calendar customized to your product category
- List growth tactics — pop-up strategy, checkout opt-in, social → email conversion

---

## How This Skill Works

**Step 1: Collect information.** Extract from the user's initial message:
- Product / category
- Brand name
- Price range and target audience
- Any context about their business

**Step 2: Ask one follow-up with all remaining questions.** Use multiple-choice format:

```
Great — [acknowledge what they told you]. To build your email system I need a few more details:

1. Business stage?
   a) Pre-launch — building a list before selling
   b) Early — selling, but under $10K/mo
   c) Growing — $10K-50K/mo
   d) Established — $50K+/mo

2. Which flows do you need? (pick all that apply, or "all")
   a) Welcome series
   b) Cart abandonment
   c) Browse abandonment
   d) Post-purchase / thank you
   e) Review request
   f) Cross-sell / upsell
   g) Win-back (re-engage lapsed customers)
   h) VIP / loyalty
   i) Replenishment (consumable products)
   j) Sunset (list cleanup)
   k) All of the above
   l) Not sure — recommend for me

3. Brand voice?
   a) Professional / corporate
   b) Friendly / conversational
   c) Playful / fun
   d) Premium / luxury
   e) Bold / edgy
   f) Other: ___________

4. Email platform (ESP)?
   a) Klaviyo
   b) Omnisend
   c) Mailchimp
   d) Shopify Email
   e) Other: ___________
   f) Don't have one yet — recommend one

5. Current email list size?
   a) 0 — starting from scratch
   b) Under 1,000
   c) 1,000-10,000
   d) 10,000-50,000
   e) 50,000+

6. Any active promotions or standard discounts? (e.g., "we always offer 10% for first order")

7. Competitors to reference? (names or URLs, or skip)

Reply like: "1b 2k 3b 4a 5b 6 yes 10% first order 7 skip"
```

**Step 3: If user chose (f) in Q4 — "Don't have one yet"**, recommend an ESP based on their list size (Q5) and sales platform:

| List Size | Recommended ESP | Approx. Cost |
|-----------|-----------------|:------------:|
| 0-500 | Omnisend Free or Mailchimp Free | $0 |
| 500-2,500 | Omnisend (Shopify) or Mailchimp (other platforms) | $13-20/mo |
| 2,500-10K | Klaviyo | $35-100/mo |
| 10K+ | Klaviyo | $100-350/mo |

⚠️ Prices are approximate (2026). Tell user to verify on each platform's website.

After recommending, continue building flows with setup instructions for the recommended ESP.

**Step 4: If user chose "l) Not sure — recommend for me" in Q2**, recommend flows based on their business stage:
- **Pre-launch:** Welcome series only (build list first)
- **Early (<$10K/mo):** Welcome + Cart Abandonment + Post-Purchase (the 3 essentials)
- **Growing ($10K-50K):** All of the above + Browse Abandonment + Review Request + Cross-sell
- **Established ($50K+):** All 10 flows

**Step 5: Build each requested flow.** For EVERY flow, output:

1. **Flow overview** — purpose, expected revenue impact, priority level
2. **Flow diagram** — visual sequence with timing
3. **For each email in the flow:**
   - Subject line (30-50 chars, mobile-friendly) + 3-5 A/B variants with different angles (curiosity, urgency, benefit, social proof, personal)
   - Preview text (40-90 chars, complement the subject — don't repeat it)
   - Full email body copy (actual words: hook → value → proof → CTA → optional P.S.)
   - CTA button text (action-oriented, one primary CTA per email) + link destination
4. **Branching logic** — conditions that split the flow (purchased vs didn't, opened vs didn't)
5. **ESP setup instructions** — generate trigger conditions, flow filters, delay timing, and branching logic specific to the user's chosen ESP (Q4). Use that ESP's exact terminology and menu paths. If user doesn't have an ESP yet, use Klaviyo terminology as default

**Step 6: Build segmentation strategy.** Define core segments with exact rules:
- New subscribers (no purchase)
- First-time buyers
- Repeat customers (2+ orders)
- VIP / high-value (top 10% by spend)
- At-risk (purchased before, no activity 60-90 days)
- Lapsed (no activity 90+ days)
- Discount-driven (only buys on sale)

**Step 7: Build annual campaign calendar.** Month-by-month with:
- Key dates and seasonal events relevant to the product category
- Campaign theme for each event
- Send schedule (pre-event teaser, launch day, last chance)
- Which segments to target

**Step 8: Provide list growth tactics.** Based on their platform and stage:
- Pop-up strategies (timing, offer, design)
- Landing page recommendations
- Social media → email conversion tactics
- Checkout opt-in optimization

---

## The 10 Core E-Commerce Email Flows

### Flow 1: Welcome Series
**Priority:** 🔴 Critical — set up first
**Expected impact:** Highest-opened emails, sets tone for entire relationship
**Emails:** 3-5 emails over 7-14 days

**Trigger:** Subscribes to email list (pop-up, footer signup, landing page)
**NOT triggered by:** Purchase (that's post-purchase flow)

**Sequence:**
```
[Subscribe] → Email 1 (Immediately)
                → [Wait 2 days]
             → Email 2 (Brand Story)
                → [Wait 2 days]
             → Email 3 (Social Proof)
                → [Conditional Split: Has placed order?]
                   → YES → Exit (enter post-purchase flow)
                   → NO → [Wait 3 days]
                        → Email 4 (Urgency / Last Chance)
```

**Email 1 — Welcome + Deliver Promise**
- Goal: Deliver the signup incentive, make a strong first impression
- Timing: Send immediately (within minutes of signup)
- Content: Welcome message, deliver discount/freebie, introduce brand briefly, one clear CTA to shop
- Design: Clean, brand-forward, hero image, single CTA button

**Email 2 — Brand Story + Values**
- Goal: Build emotional connection, differentiate from competitors
- Timing: 2 days after Email 1
- Content: Founder story or brand mission, why you started, what makes you different, lifestyle imagery
- Design: Storytelling layout, minimal product — focus on brand

**Email 3 — Social Proof + Best Sellers**
- Goal: Build trust, showcase popular products
- Timing: 2 days after Email 2
- Content: Customer reviews, UGC, best-selling products, "loved by X customers"
- Design: Product grid with reviews, star ratings

**Email 4 — Discount Reminder / Urgency** (only if they haven't purchased)
- Goal: Convert remaining non-buyers before discount expires
- Timing: 3 days after Email 3
- Content: "Your [X%] off expires soon," countdown urgency, restate value prop, clear CTA
- Design: Urgent — bold colors, countdown timer if ESP supports it

### Flow 2: Cart Abandonment
**Priority:** 🔴 Critical — highest revenue per recipient
**Expected impact:** $5.81 revenue per recipient average *(Klaviyo 2026)*
**Emails:** 3 emails over 3 days

**Trigger:** Added to cart + started checkout, but did NOT complete purchase
**Wait before first email:** 1-4 hours (test: 1h vs 4h)

**Sequence:**
```
[Checkout Started, Not Completed] → [Wait 1-4 hours]
   → Email 1 (Reminder)
      → [Wait 24 hours]
      → [Conditional Split: Placed order?]
         → YES → Exit
         → NO → Email 2 (Overcome Objections)
            → [Wait 24 hours]
            → [Conditional Split: Placed order?]
               → YES → Exit
               → NO → Email 3 (Incentive)
```

**Email 1 — Simple Reminder**
- Goal: Catch people who got distracted (not resistant — just forgot)
- Content: "You left something behind," show cart contents with images + prices, direct link back to cart
- Tone: Helpful, not pushy. No discount yet
- CTA: "Complete Your Order" or "Return to Cart"

**Email 2 — Overcome Objections**
- Goal: Address why they didn't buy (shipping? trust? price?)
- Content: Social proof (reviews), shipping/return policy highlights, FAQs, "still thinking?"
- Tone: Reassuring
- CTA: "Get It Before It's Gone"

**Email 3 — Incentive** (optional — only if margin allows)
- Goal: Last resort conversion with discount or free shipping
- Content: Limited-time offer (10% off or free shipping), urgency ("expires in 24 hours")
- Tone: Urgent but not desperate
- CTA: "Claim Your [X%] Off"
- ⚠️ Only use a discount if your margin supports it. If not, emphasize scarcity instead

### Flow 3: Browse Abandonment
**Priority:** 🟡 Important — catches high-intent window shoppers
**Expected impact:** Lower conversion than cart, but much higher volume
**Emails:** 1-2 emails over 2 days

**Trigger:** Viewed product page but did NOT add to cart
**Wait:** 2-4 hours after browsing (not immediately — feels creepy)

**Sequence:**
```
[Viewed Product, Did Not Add to Cart] → [Wait 2-4 hours]
   → [Conditional Split: Has added to cart since?]
      → YES → Exit (they'll enter cart abandonment)
      → NO → Email 1 (Product Reminder)
         → [Wait 24 hours]
         → Email 2 (Related Products)
```

**Email 1 — "Still Interested?"**
- Content: Show the product they viewed with image + price, brief benefit/review quote, link to product page
- Tone: Casual, helpful — NOT "we noticed you looking" (creepy)
- CTA: "Take Another Look"
- ⚠️ Do NOT offer a discount here — saves margin, avoids training customers to browse-then-leave for discounts

**Email 2 — Related Products**
- Content: "You might also like..." with 3-4 related products, category page link
- Purpose: If they weren't sold on that specific product, show alternatives

### Flow 4: Post-Purchase / Thank You
**Priority:** 🔴 Critical — shapes the entire post-purchase experience
**Expected impact:** Reduces buyer's remorse, increases repeat rate, drives reviews
**Emails:** 3-4 emails over 14-21 days

**Trigger:** Placed order (first-time buyer gets different content than repeat buyer)

**Sequence:**
```
[Order Placed] → Email 1 (Immediately — Thank You)
   → [Wait: Estimated delivery + 2 days]
   → [Conditional Split: First-time buyer?]
      → YES → Email 2a (Product Education)
      → NO → Email 2b (Loyalty Reward)
   → [Wait 5-7 days]
   → Email 3 (Review Request — see Flow 5)
   → [Wait 14 days]
   → Email 4 (Cross-sell — see Flow 6)
```

**Email 1 — Order Confirmation + Thank You**
- Timing: Immediately after purchase
- Content: Thank you, order summary, shipping timeline, what to expect, support contact
- Tone: Warm, grateful — this is a celebration, not a receipt
- Add: "Here's what happens next" (sets expectations)

**Email 2a — Product Education (first-time buyers)**
- Timing: After estimated delivery + 2 days
- Content: How to use/care for the product, tips, FAQ, "get the most out of your [product]"
- Purpose: Reduce returns, increase satisfaction, build brand connection

**Email 2b — Loyalty Thank You (repeat buyers)**
- Timing: Same timing
- Content: "Thanks for coming back! You're one of our best customers," exclusive offer or early access
- Purpose: Reward loyalty, increase LTV

### Flow 5: Review Request
**Priority:** 🟡 Important — builds social proof that powers all other marketing
**Emails:** 1-2 emails

**Trigger:** Chained from post-purchase flow OR standalone trigger on order fulfilled + X days
**Timing:** 5-7 days after delivery (product has arrived, they've used it)

**Email 1 — Review Request**
- Content: "How's your [product]? We'd love to hear!" + direct link to leave review
- Tone: Personal, low-pressure
- Make it easy: One-click star rating if your review platform supports it (Stamped, Loox, Judge.me)
- Optional: Small incentive (10% off next order, loyalty points)

**Email 2 — Reminder** (only if no review submitted after 5 days)
- Content: Shorter, more direct. "Quick reminder — your review helps other [pet owners / etc.]"
- Social proof: "Join 500+ customers who shared their experience"

### Flow 6: Cross-Sell / Upsell
**Priority:** 🟡 Important — increases AOV and LTV
**Emails:** 1-2 emails

**Trigger:** Placed order + 14-21 days (after they've received and used the product)
**Logic:** Recommend products based on what they bought

**Email 1 — "Complete the Set" / "Pairs Well With..."**
- Content: Related products based on purchase (accessories, refills, complementary items)
- Tone: Helpful recommendation, not hard sell
- CTA: "Shop the Collection" or "Complete Your Set"

**Product recommendation logic:**
- If ESP supports dynamic product recommendations (Klaviyo, Omnisend), use them
- If not, build manual splits by product category:
  - Bought [Category A] → Recommend [Category B]
  - Bought [Product X] → Recommend [Accessory Y]

### Flow 7: Win-Back
**Priority:** 🟡 Important — re-engages lapsed customers before they're lost
**Emails:** 3-4 emails over 30 days

**Trigger:** Has placed order BUT last order was 60-90 days ago (adjust based on your purchase cycle)
**Additional filter:** Has NOT opened or clicked any email in last 30 days

**Sequence:**
```
[Last Order 60-90 days ago + No engagement 30 days]
   → Email 1 (We Miss You)
      → [Wait 7 days]
      → [Placed order?] → YES → Exit
      → NO → Email 2 (What's New)
         → [Wait 7 days]
         → Email 3 (Incentive)
            → [Wait 14 days]
            → Email 4 (Last Chance / Sunset Warning)
```

**Email 1 — "We Miss You"**
- Content: Personal, genuine message. What's new since they last bought. Best sellers they haven't tried
- Tone: Warm, not guilt-tripping
- No discount yet — test whether re-engagement alone works

**Email 2 — What's New**
- Content: New products, new features, brand updates, community highlights
- Purpose: Give them a reason to come back beyond discounts

**Email 3 — Incentive**
- Content: "Here's X% off to welcome you back" — exclusive returning customer offer
- Urgency: Time-limited (7 days)

**Email 4 — Last Chance / Sunset Warning**
- Content: "We don't want to bother you — should we keep sending?" + unsubscribe option
- Purpose: Gives control back to customer, cleans list if they don't respond
- If no response → Move to sunset flow

### Flow 8: VIP / Loyalty
**Priority:** 🟢 Nice to have for growing brands, critical for established
**Emails:** Ongoing (event-triggered)

**Trigger:** Customer enters VIP segment (top 10% by total spend, OR 3+ orders)

**Email 1 — VIP Welcome**
- Content: "You're officially a VIP! Here's what that means:" + exclusive perks
- Perks to offer: Early access to new products, exclusive discounts, free shipping, birthday gift

**Ongoing VIP emails:**
- Early access notifications (before public launches)
- Exclusive sales (VIP-only pricing)
- Birthday/anniversary rewards
- "Thank you" with surprise gift at milestones (5th order, 1-year anniversary)

### Flow 9: Replenishment (Consumable Products Only)
**Priority:** 🟡 Critical if you sell consumables — skip if not applicable
**Emails:** 1-2 emails

**Trigger:** Time-based — estimated product usage cycle after purchase
- Example: Dog treats (30-day supply) → trigger at day 25
- Example: Skincare (60-day supply) → trigger at day 50
- Example: Coffee (14-day bag) → trigger at day 10

**Email 1 — "Running Low?"**
- Timing: 5 days before estimated run-out
- Content: "Time to restock? Your [product] should be running low." + reorder link
- Optional: Subscription offer ("Never run out — subscribe and save 15%")

**Email 2 — Follow-Up**
- Timing: 3 days after Email 1 if no reorder
- Content: Shorter reminder + social proof ("other customers reorder every X days")

### Flow 10: Sunset (List Cleanup)
**Priority:** 🟢 Important for deliverability — set up after other flows are running
**Emails:** 2-3 emails over 14-21 days

**Trigger:** No email opens AND no clicks AND no purchases in 90-120 days

**Purpose:** Clean your list. Unengaged subscribers hurt deliverability (emails go to spam for everyone).

**Sequence:**
```
[No engagement 90-120 days]
   → Email 1 (Re-engagement Attempt)
      → [Wait 7 days]
      → [Opened or clicked?]
         → YES → Exit, keep on list
         → NO → Email 2 (Final Chance)
            → [Wait 7 days]
            → [Opened or clicked?]
               → YES → Exit, keep on list
               → NO → Suppress from all future sends
```

**Email 1 — "Are You Still There?"**
- Subject: Make it stand out (pattern interrupt)
- Content: "We noticed you haven't been opening our emails. Want to stay? Click here to stay subscribed"
- CTA: Single button — "Yes, Keep Me Subscribed"

**Email 2 — "This Is Goodbye (Unless...)"**
- Content: "This is our last email unless you tell us to keep going"
- CTA: "Keep Sending Me Emails"
- If no response → auto-suppress (do NOT delete — just suppress from sends)

---

## Segmentation Strategy

Define these segments in your ESP. Exact conditions provided:

| Segment | Conditions | Use For |
|---------|-----------|---------|
| New Subscribers | Subscribed + Has placed 0 orders | Welcome flow, first purchase incentives |
| First-Time Buyers | Has placed exactly 1 order | Post-purchase education, review request, second purchase push |
| Repeat Customers | Has placed 2+ orders | Cross-sell, loyalty, VIP pipeline |
| VIP | Top 10% by total spend OR 5+ orders | VIP flow, early access, exclusive offers |
| At-Risk | Last order 60-90 days ago | Win-back flow |
| Lapsed | Last order 90+ days ago + No engagement 60+ days | Aggressive win-back, sunset candidate |
| Engaged Non-Buyers | Opens/clicks emails but has NOT purchased | Browse abandon focus, stronger incentives |
| Discount-Only | Has ONLY purchased with a discount code | Reduce discount dependency, value-based messaging |

---

## Annual Campaign Calendar Template

Customize based on your product category. Not every event applies to every brand — pick the ones relevant to your audience.

| Month | Key Dates | Campaign Ideas |
|-------|-----------|----------------|
| January | New Year (Jan 1), MLK Day (Jan 20) | New Year sale, "New Year New You," goal-setting content |
| February | Valentine's Day (Feb 14), Presidents' Day (Feb 17) | Gift guides, couples/self-love angle, flash sale |
| March | Int'l Women's Day (Mar 8), St. Patrick's (Mar 17), Spring Equinox | Seasonal transition, spring collection launch |
| April | Easter (variable), Earth Day (Apr 22) | Spring sale, sustainability angle, limited editions |
| May | Mother's Day (May 11), Memorial Day (May 26) | Gift guide, "treat your mom / treat yourself," summer kickoff sale |
| June | Father's Day (Jun 15), Summer Solstice, Pride Month | Gift guide, summer collection, Pride content if authentic |
| July | July 4th, Amazon Prime Day (mid-July) | Independence Day sale, mid-year clearance, Christmas in July |
| August | Back to School (early Aug) | End of summer sale, back-to-routine content, fall preview |
| September | Labor Day (Sep 1), Fall Equinox | Labor Day sale, fall launch, loyalty program push |
| October | Halloween (Oct 31) | Spooky-themed content, costume/party angle, early holiday teasers |
| November | Veterans Day (Nov 11), Black Friday (Nov 28), Cyber Monday (Dec 1) | BFCM = biggest email month. Pre-sale VIP access → Main event → Extended sale |
| December | Christmas (Dec 25), Hanukkah, New Year's Eve | Gift guides, last-minute shipping deadlines, year-in-review, thank you |

### BFCM (Black Friday / Cyber Monday) Email Strategy
This is your biggest email revenue period. Plan ahead:
- **3-4 weeks before:** Teaser emails to build anticipation, grow list aggressively
- **1 week before:** VIP early access announcement
- **Black Friday:** Launch email (morning) + reminder (evening)
- **Saturday-Sunday:** Extended deals, bundle offers
- **Cyber Monday:** New deals or "last chance" on BF deals
- **Tuesday after:** Thank you email + "sale extended 24 hours" (if applicable)

---

## List Growth Tactics

- **Pop-up:** Show after 5-8 seconds OR on exit intent. Offer 10-15% off first order or free shipping. Target 3-5% conversion rate
- **Checkout opt-in:** Pre-checked "Email me about new products"
- **Social → email:** Instagram/TikTok bio link to email capture landing page
- **Packaging insert:** "Join our VIP list" card in orders
- **Referral:** "Give $X, get $X" programs that grow your list through customers
- **Content marketing:** Blog → gated downloads (guides, lookbooks)

---

## Output Format

```
# 📧 Email Marketing System — [Brand Name]

## Overview
Brand: [name] | Products: [category] | Price: $XX-XX
Stage: [stage] | List Size: [size] | ESP: [platform]
Voice: [brand voice] | Flows: [list]

## Flow 1: [Flow Name]
**Purpose:** [why this flow matters]
**Priority:** [🔴 Critical / 🟡 Important / 🟢 Nice to have]

### Flow Diagram
[trigger] → [delay] → [email] → [conditional split] → [branch]

### Email 1: [Name]
**Subject:** [primary subject line]
**A/B Variants:**
1. [variant] — [angle]
2. [variant] — [angle]
3. [variant] — [angle]
**Preview:** [preview text]
**Body:** [full email copy]
**CTA:** [button text] → [link]

### ESP Setup ([platform name])
- Trigger: [exact trigger in ESP terminology]
- Filters: [conditions]
- Timing: [delays between emails]
- Branching: [split conditions]

[Repeat for each email and flow]

## Segmentation Strategy
[Segments with exact filter conditions for their ESP]

## Annual Campaign Calendar
[Month-by-month with dates, themes, and target segments]

## List Growth Plan
[Tactics based on their platform and stage]
```

---

## Other Skills

For paid advertising strategy across Google, Meta, and TikTok:
```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-ppc-strategy-planner -g
```

For full omnichannel marketing strategy (includes email as one channel):
```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-marketing-strategy-builder -g
```

More e-commerce skills: [nexscope-ai/eCommerce-Skills](https://github.com/nexscope-ai/eCommerce-Skills)

Built by [Nexscope](https://www.nexscope.ai/) — your AI assistant for smarter e-commerce decisions.
