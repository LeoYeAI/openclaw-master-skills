---
name: Event Planner Pro
description: Plan, execute, and measure business events — conferences, webinars, workshops, product launches, networking events, trade shows, and corporate gatherings. Complete event lifecycle from concept to post-event ROI analysis.
metadata: {"clawdbot":{"emoji":"🎪","os":["linux","darwin","win32"]}}
---

# Event Planner Pro 🎪

Complete event planning and execution system. Covers every event type from intimate workshops to 5,000+ person conferences. Business-grade methodology with templates, budgets, timelines, and ROI measurement.

---

## Phase 1: Event Strategy & Concept

### Quick Event Assessment

When asked to plan an event, gather:

```yaml
event_brief:
  name: ""
  type: ""  # conference | webinar | workshop | networking | trade_show | product_launch | corporate | fundraiser | retreat
  purpose: ""  # lead_gen | brand_awareness | education | community | sales | internal_alignment | celebration
  target_audience: ""
  expected_attendees: 0
  date_range: ""  # preferred dates or flexibility
  budget_range: ""  # total budget or per-attendee target
  format: ""  # in_person | virtual | hybrid
  success_metrics: []  # what does success look like?
  constraints: []  # venue locked, date fixed, sponsor requirements, etc.
```

### Event Type Decision Matrix

| Type | Best For | Typical Size | Lead Time | Budget/Person |
|------|----------|-------------|-----------|--------------|
| Webinar | Lead gen, thought leadership | 50-500 | 2-4 weeks | $5-20 |
| Workshop | Deep skill transfer, premium positioning | 10-50 | 4-8 weeks | $100-500 |
| Networking | Relationship building, community | 30-200 | 3-6 weeks | $30-100 |
| Conference | Brand authority, multi-track content | 200-5000+ | 3-12 months | $200-800 |
| Product Launch | Buzz, press, sales pipeline | 50-500 | 6-12 weeks | $150-1000 |
| Trade Show (booth) | Industry visibility, leads | N/A | 8-16 weeks | $5K-50K total |
| Corporate/Internal | Alignment, culture, training | 20-500 | 4-8 weeks | $100-400 |
| Fundraiser | Donations, donor cultivation | 50-500 | 8-16 weeks | $150-500 |
| Retreat | Team bonding, strategy | 10-50 | 6-12 weeks | $500-2000 |

### Purpose → Format Mapping

- **Lead generation** → Webinar (top funnel) + Workshop (bottom funnel)
- **Brand authority** → Conference or speaking at others' events
- **Sales acceleration** → Intimate dinner/roundtable for 10-20 prospects
- **Community building** → Monthly meetup series + annual summit
- **Education** → Workshop series with certification
- **Internal alignment** → Offsite retreat + quarterly town halls

---

## Phase 2: Budget Planning

### Budget Template

```yaml
event_budget:
  name: ""
  total_budget: 0
  contingency_pct: 15  # always include 15% buffer
  
  venue:
    rental: 0
    insurance: 0
    security: 0
    permits: 0
    subtotal: 0
  
  food_beverage:
    catering: 0
    beverages: 0
    special_dietary: 0
    service_staff: 0
    subtotal: 0
  
  technology:
    av_equipment: 0
    streaming_platform: 0  # for virtual/hybrid
    event_app: 0
    wifi_upgrade: 0
    recording: 0
    subtotal: 0
  
  marketing:
    design_branding: 0
    paid_ads: 0
    email_platform: 0
    printed_materials: 0
    signage: 0
    photography_video: 0
    subtotal: 0
  
  speakers:
    fees: 0
    travel: 0
    accommodation: 0
    gifts: 0
    subtotal: 0
  
  logistics:
    staff_travel: 0
    shipping: 0
    swag_gifts: 0
    badges_lanyards: 0
    decorations: 0
    transportation: 0
    subtotal: 0
  
  contingency: 0  # 15% of total
  grand_total: 0

  revenue:
    ticket_sales: 0
    sponsorships: 0
    exhibitor_fees: 0
    merchandise: 0
    total_revenue: 0
  
  net_cost: 0  # grand_total - total_revenue
  cost_per_attendee: 0
```

### Budget Allocation Rules by Event Type

| Type | Venue | F&B | Tech | Marketing | Speakers | Logistics |
|------|-------|-----|------|-----------|----------|-----------|
| Conference | 25% | 20% | 15% | 20% | 10% | 10% |
| Webinar | 0% | 0% | 40% | 35% | 15% | 10% |
| Workshop | 20% | 15% | 10% | 25% | 20% | 10% |
| Networking | 30% | 30% | 5% | 20% | 5% | 10% |
| Product Launch | 20% | 15% | 20% | 25% | 5% | 15% |
| Trade Show | 40% | 10% | 15% | 20% | 0% | 15% |

### Cost-Cutting Strategies (When Budget is Tight)

1. **Venue** → Use co-working spaces, university halls, partner offices
2. **Speakers** → Offer exposure/content swap instead of fees for smaller events
3. **F&B** → Breakfast/lunch only (no dinner), drink tickets instead of open bar
4. **Marketing** → Leverage speakers' audiences, partner cross-promotion
5. **Tech** → Use free tiers (StreamYard, Zoom, Luma) for <100 attendees
6. **Swag** → Digital swag bags (ebooks, templates, discount codes) instead of physical

---

## Phase 3: Timeline & Project Plan

### Master Timeline Template

Adapt lead time to event type. Conference = 6-12 months. Webinar = 2-4 weeks.

```yaml
timeline:
  t_minus_6_months:
    - Define event concept, goals, success metrics
    - Set budget and get approval
    - Book venue (in-person) or select platform (virtual)
    - Identify keynote speakers, begin outreach
    - Create event brand (name, logo, color scheme, tagline)
    
  t_minus_4_months:
    - Confirm speakers and session topics
    - Launch event website/landing page
    - Open early-bird registration
    - Begin sponsor outreach (sponsorship deck ready)
    - Book AV, catering, photographer
    
  t_minus_2_months:
    - Finalize agenda and schedule
    - Launch marketing campaign (email, social, ads)
    - Send speaker prep kits (guidelines, templates, deadlines)
    - Confirm all vendor contracts
    - Set up registration/ticketing system
    - Plan networking activities
    
  t_minus_1_month:
    - Close early-bird pricing
    - Send attendee pre-event survey
    - Finalize run-of-show document
    - Brief all staff on roles and responsibilities
    - Test all technology (streaming, mics, slides)
    - Prepare attendee welcome materials
    
  t_minus_1_week:
    - Final headcount to caterer
    - Print badges, signage, materials
    - Load all presentations into master deck
    - Run full tech rehearsal
    - Send attendee reminder with logistics
    - Prepare emergency kit (adapters, tape, markers, batteries, meds)
    
  t_minus_1_day:
    - Venue walkthrough with team
    - Set up registration desk, signage, AV
    - Test wifi under load
    - Charge all devices
    - Pre-position water, snacks in speaker rooms
    - Team dinner / final briefing
    
  event_day:
    - Arrive 2 hours early
    - Registration desk open 1 hour before
    - Run-of-show doc in every staff member's hands
    - Photographer capturing key moments
    - Live social media coverage
    - Monitor and fix issues in real time
    - Collect feedback (paper cards or app)
    
  post_event:
    - day_1: Thank you emails to attendees, speakers, sponsors
    - day_2: Share photos and recording links
    - day_3: Send feedback survey
    - week_1: Analyze survey results, calculate ROI
    - week_2: Debrief with team, document lessons learned
    - week_3: Follow up on leads generated
    - month_1: Publish recap content (blog, video, social)
```

### Webinar-Specific Fast Timeline (2-4 Weeks)

```yaml
webinar_timeline:
  week_1:
    - Define topic, title, speaker(s)
    - Create landing page with registration form
    - Write 3-email invite sequence
    - Schedule social posts (5-8 posts)
    - Set up streaming platform (test audio/video)
    
  week_2:
    - Send invite email #1 (announcement)
    - Speaker prep call (align on content, Q&A format)
    - Create slide deck template
    - Send invite email #2 (value hook)
    - Partner cross-promotion (ask speakers to share)
    
  week_3:
    - Slides finalized
    - Full dry run with speaker(s)
    - Send invite email #3 (urgency/last chance)
    - Prepare follow-up email sequence (recording, CTA)
    - Set up polls/Q&A in platform
    
  webinar_day:
    - Test 30 min before go-live
    - Start recording
    - Moderator manages Q&A
    - Drop CTA in chat at midpoint and end
    - Thank everyone, announce next event
    
  post_webinar:
    - Send recording within 24 hours
    - Send follow-up #1 (recording + resource) — day 1
    - Send follow-up #2 (CTA/offer) — day 3
    - Send follow-up #3 (case study/social proof) — day 7
    - Add registrants to nurture sequence
```

---

## Phase 4: Venue & Vendor Management

### Venue Selection Scorecard (In-Person)

Rate each venue 1-5:

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Capacity fits (with 20% buffer) | 5 | /5 | /25 |
| Location accessibility (transit, parking, airport) | 4 | /5 | /20 |
| AV capabilities built-in | 4 | /5 | /20 |
| Wifi capacity (ask: max concurrent devices) | 4 | /5 | /20 |
| Catering options (in-house or flexible) | 3 | /5 | /15 |
| Breakout rooms available | 3 | /5 | /15 |
| Natural lighting | 2 | /5 | /10 |
| Brand alignment (vibe matches event) | 2 | /5 | /10 |
| Cancellation/rescheduling policy | 3 | /5 | /15 |
| **Total** | | | **/150** |

**Threshold:** 110+ = book it. 80-109 = negotiate improvements. <80 = keep looking.

### Venue Contract Checklist

- [ ] Confirm capacity (seated vs standing vs classroom)
- [ ] Wifi specs: bandwidth, max devices, password distribution
- [ ] AV: projector, screens, mics (how many wireless?), sound system
- [ ] Power: outlet locations, extension cord policy, generator backup
- [ ] Setup/teardown time included (typically need 2-4 hours each)
- [ ] Cancellation terms and force majeure clause
- [ ] Catering exclusivity or BYO allowed
- [ ] Parking: how many spots, validation, shuttle
- [ ] Insurance requirements (usually need event liability)
- [ ] Noise restrictions and time curfews
- [ ] Accessibility: wheelchair, elevators, restrooms

### Vendor Management Template

```yaml
vendors:
  - name: ""
    type: ""  # catering | av | photography | streaming | decor | transport | security
    contact: ""
    phone: ""
    email: ""
    contract_signed: false
    deposit_paid: false
    deposit_amount: 0
    total_cost: 0
    payment_schedule: ""
    cancellation_policy: ""
    insurance_verified: false
    delivery_date: ""
    setup_time_needed: ""
    notes: ""
```

---

## Phase 5: Speaker & Content Management

### Speaker Outreach Template

```
Subject: Speaking at [Event Name] — [Date]

Hi [Name],

We're organizing [Event Name], a [type] event for [audience] on [date] in [location/virtual].

Your work on [specific topic/achievement] is exactly what our attendees need. We'd love you to deliver a [length]-minute [keynote/talk/workshop/panel] on [proposed topic].

What we offer:
- [Fee / travel + accommodation / exposure to X audience]
- Professional recording of your session
- Promotion to our [X]-person audience across [channels]

[X] attendees from companies like [notable names].

Interested? Happy to jump on a quick call this week.

Best,
[Name]
```

### Speaker Prep Kit

Send 4 weeks before event:

```yaml
speaker_kit:
  event_overview:
    name: ""
    date: ""
    venue: ""
    audience_profile: ""
    expected_attendance: 0
    
  session_details:
    title: ""
    format: ""  # keynote | breakout | workshop | panel | fireside
    duration_minutes: 0
    q_and_a_minutes: 0
    time_slot: ""
    room: ""
    
  content_guidelines:
    slide_template_url: ""  # branded template
    slide_deadline: ""  # 1 week before event
    max_slides: 0
    no_sales_pitch: true
    actionable_takeaways: 3  # minimum
    audience_level: ""  # beginner | intermediate | advanced | mixed
    
  logistics:
    arrival_time: ""
    tech_check_time: ""
    green_room_location: ""
    av_setup: ""  # what's provided (clicker, mic type, monitor)
    laptop_compatibility: ""  # HDMI, USB-C, bring own adapter
    recording_consent: true
    
  promotion:
    headshot_needed: true
    bio_word_limit: 100
    social_handles: ""
    promotional_posts_requested: 2  # minimum shares
```

### Agenda Design Principles

1. **Energy management** — high-energy sessions after breaks, reflective sessions after lunch
2. **The 18-minute rule** — no single talk >18 min without interaction (TED model)
3. **Breakout ratio** — for conferences, 60% main stage / 40% breakouts
4. **Networking slots** — schedule 3 structured networking moments (not just "breaks")
5. **Start strong, end strong** — best speakers open and close the day
6. **Buffer time** — add 10 min between sessions (transitions always take longer)
7. **No back-to-back panels** — audience fatigue kills engagement

### Agenda Template (Full-Day Conference)

```
08:00 - 08:45  Registration & Coffee ☕
08:45 - 09:00  Welcome & Housekeeping
09:00 - 09:30  Opening Keynote: [Big Name / Big Idea]
09:30 - 09:45  Transition + Networking Activity #1
09:45 - 10:15  Talk: [Topic A]
10:15 - 10:45  Talk: [Topic B]
10:45 - 11:15  Break + Expo / Sponsor Booths ☕
11:15 - 12:00  Workshop Track A | Workshop Track B | Workshop Track C
12:00 - 13:00  Lunch + Networking Activity #2 🍽️
13:00 - 13:30  Fireside Chat: [Industry Leader]
13:30 - 14:00  Talk: [Topic C]
14:00 - 14:30  Talk: [Topic D]
14:30 - 15:00  Break + Expo ☕
15:00 - 15:45  Panel: [Hot Topic]
15:45 - 16:15  Lightning Talks (5 min x 5 speakers)
16:15 - 16:45  Closing Keynote
16:45 - 17:00  Wrap-up & Announcements
17:00 - 19:00  Happy Hour / After-Party 🎉
```

---

## Phase 6: Registration & Marketing

### Registration Pricing Strategy

```yaml
pricing_tiers:
  super_early_bird:
    discount: 40%
    deadline: "T-3 months"
    purpose: "Validate demand, seed initial registrations"
    
  early_bird:
    discount: 20%
    deadline: "T-6 weeks"
    purpose: "Build momentum, create urgency"
    
  regular:
    discount: 0%
    deadline: "T-1 week"
    purpose: "Standard pricing"
    
  last_minute:
    premium: 10%  # optional
    deadline: "Day of"
    purpose: "Captures procrastinators"
    
  group_discount:
    threshold: 3  # tickets
    discount: 15%
    purpose: "Encourage team attendance"
    
  student_nonprofit:
    discount: 50%
    verification: "edu email or org verification"
```

### Marketing Campaign Timeline

```yaml
marketing_phases:
  awareness:  # T-8 to T-6 weeks
    - Launch event website/landing page
    - Announce on social media (3-5 posts)
    - Email blast to existing list
    - Speaker announcements (1 per week)
    - Partner cross-promotion begins
    
  consideration:  # T-6 to T-3 weeks
    - Share agenda/session details
    - Speaker spotlight posts (interviews, quotes)
    - Early testimonials from past events
    - Retargeting ads on registrants who didn't complete
    - Blog post: "X Reasons to Attend [Event]"
    
  urgency:  # T-3 weeks to T-1 week
    - "Early bird ending" campaign
    - Countdown posts
    - "Only X spots left" (if true)
    - Direct outreach to high-value prospects
    - Reminder email to registered (build excitement)
    
  final_push:  # T-1 week
    - "Last chance" email
    - Social proof: "X people already registered"
    - DM outreach to key targets
    - Logistics email to confirmed attendees
```

### Email Sequence (6 Emails)

1. **Announcement** (T-8 weeks): What, when, why. Early-bird CTA
2. **Speaker reveal** (T-6 weeks): Highlight 2-3 speakers. Social proof
3. **Agenda drop** (T-4 weeks): Full schedule. "Which sessions excite you?"
4. **Early bird ending** (T-3 weeks): Price goes up in X days. Urgency
5. **Final details** (T-1 week): Logistics, what to bring, excitement builder
6. **Day-before** (T-1 day): Reminder, schedule link, parking/wifi info

### Landing Page Must-Haves

- [ ] Clear event name, date, location above the fold
- [ ] 1-sentence value prop: "What you'll walk away with"
- [ ] Speaker headshots + 1-line bios
- [ ] Agenda overview (expandable)
- [ ] Social proof (past attendee quotes, logos of companies attending)
- [ ] Pricing tiers with clear CTA
- [ ] FAQ section (parking, refunds, dress code, recording)
- [ ] Mobile-responsive
- [ ] Countdown timer
- [ ] Video from past event (if applicable)

---

## Phase 7: Sponsorship

### Sponsorship Tier Structure

```yaml
sponsorship_tiers:
  title_sponsor:
    price: ""  # typically 40-60% of total sponsorship goal
    benefits:
      - Logo on all materials (event name: "Powered by [Sponsor]")
      - Keynote slot or fireside chat (10-15 min)
      - Premium booth location
      - Full attendee list (with consent)
      - 10 complimentary tickets
      - Logo on recording/replay
      - Social media mentions (10+)
      - Email feature
    limit: 1
    
  gold:
    price: ""
    benefits:
      - Logo on website and printed materials
      - Breakout session or workshop slot
      - Booth in expo area
      - 5 complimentary tickets
      - Social media mentions (5)
      - Logo on attendee email
    limit: 3
    
  silver:
    price: ""
    benefits:
      - Logo on website
      - Table in expo area
      - 3 complimentary tickets
      - Social media mention (2)
    limit: 5
    
  community:
    price: ""  # or in-kind
    benefits:
      - Logo on website
      - 2 complimentary tickets
      - Social mention (1)
    limit: 10
```

### Sponsor Outreach Email

```
Subject: Sponsorship Opportunity — [Event Name] ([Date])

Hi [Name],

[Event Name] brings together [X] [audience type] on [date] in [location].

Last year: [X attendees], [X% decision-makers], [notable companies].

We have [tier] sponsorship packages from $[low] to $[high], including:
- [Top 3 benefits of relevant tier]

Our attendees match your ICP: [specific overlap].

Happy to send the full sponsorship deck. Quick 15 min this week?

Best,
[Name]
```

### Sponsor ROI Package (Post-Event)

Send within 2 weeks:
- Total attendee count and demographics
- Booth traffic / session attendance numbers
- Social media impressions and mentions
- Photos featuring sponsor branding
- Lead list (with consent) or scan data
- Attendee satisfaction scores
- "Thank you" and early-bird offer for next event

---

## Phase 8: Day-Of Execution

### Run of Show Document

The single most important document. Every staff member gets a copy.

```yaml
run_of_show:
  event: ""
  date: ""
  venue: ""
  
  team_contacts:
    event_lead: {name: "", phone: ""}
    av_tech: {name: "", phone: ""}
    registration: {name: "", phone: ""}
    catering: {name: "", phone: ""}
    venue_contact: {name: "", phone: ""}
    
  schedule:
    - time: "06:00"
      activity: "Team arrives, begin setup"
      owner: ""
      notes: ""
    - time: "07:00"
      activity: "AV check, mic test all rooms"
      owner: ""
      notes: ""
    # ... full schedule with owner and notes for every slot
    
  contingency:
    speaker_no_show: "Backup: [name] on standby. Extend Q&A. Panel becomes fireside."
    av_failure: "Backup laptop loaded. Mobile hotspot ready. Portable speaker in kit."
    low_attendance: "Close off sections. Rearrange to fill front. More interactive format."
    wifi_down: "Mobile hotspots x3. Offline slide copies. Apologize + offer recording."
    medical_emergency: "First aid kit at [location]. Nearest hospital: [name, address]. Call [emergency#]."
    weather_disruption: "Indoor backup plan. Communication plan for attendees."
```

### Emergency Kit Checklist

- [ ] Power strips and extension cords (5+)
- [ ] HDMI, USB-C, DisplayPort adapters (all types)
- [ ] Backup laptop with all presentations
- [ ] Mobile wifi hotspots (2-3)
- [ ] Gaffer tape, duct tape, double-sided tape
- [ ] Markers (whiteboard + permanent)
- [ ] Scissors, box cutter
- [ ] Batteries (AA, AAA)
- [ ] Phone chargers (Lightning, USB-C)
- [ ] First aid kit
- [ ] Breath mints, pain relievers, hand sanitizer
- [ ] Printed attendee list (backup for registration)
- [ ] Cash for tips/emergencies
- [ ] Spare badges and lanyards
- [ ] Bluetooth speaker (backup audio)

### Networking Facilitation Activities

Don't just say "network" — structure it:

1. **Speed networking** — 3 min rounds with prompt cards ("What's your biggest challenge this quarter?")
2. **Birds of a feather** — tables labeled by topic, self-select
3. **Buddy match** — pre-match 2 attendees with complementary profiles, email intro before event
4. **Ask the expert** — speakers available at labeled tables during breaks
5. **Scavenger hunt** — find people matching descriptions on a bingo card (icebreaker)

---

## Phase 9: Virtual & Hybrid Events

### Platform Selection Guide

| Platform | Best For | Max Attendees | Price Range |
|----------|----------|---------------|-------------|
| Zoom Webinar | Simple webinars | 10,000 | $79-6,490/yr |
| StreamYard | Multi-speaker, branded | 1,000 | Free-$99/mo |
| Hopin | Full conferences | 100,000 | Custom |
| Luma | Community events, ticketing | Unlimited | Free-$59/mo |
| Airmeet | Networking-focused | 10,000 | $167+/mo |
| Riverside | High-quality recording | 8 speakers | $24/mo |
| YouTube Live | Broadcast, no interaction | Unlimited | Free |

### Hybrid Event Rules

1. **Virtual is NOT second-class** — dedicated camera angles, chat moderator, virtual MC
2. **Separate virtual agenda** — don't just stream the in-person event; add virtual-only Q&A, breakouts
3. **Tech check doubles** — test in-room AND streaming simultaneously
4. **Chat moderator mandatory** — someone monitoring virtual chat and surfacing questions
5. **On-demand within 24 hours** — virtual attendees expect recordings fast
6. **Pricing** — virtual tickets = 30-50% of in-person (lower, but not free)

### Virtual Engagement Techniques

- **Polls every 10 minutes** — keep attention
- **Chat prompts** — "Drop your city in chat!" at the start
- **Breakout rooms** — 4-6 people, 10 min, specific prompt
- **Live Q&A** — dedicate last 1/3 of session
- **Gamification** — points for participation, prize at end
- **Camera-on culture** — encourage (don't mandate) cameras for workshops

---

## Phase 10: Post-Event Analysis & ROI

### Feedback Survey (Send Within 24 Hours)

Keep it short (5 min max):

1. Overall satisfaction (1-10)
2. Which session was most valuable? (dropdown)
3. Which session was least valuable? (dropdown)
4. How likely to recommend to a colleague? (1-10 NPS)
5. What one thing would you improve?
6. What topics do you want next time?
7. Would you attend again? (Yes / Maybe / No)

### ROI Calculation Framework

```yaml
event_roi:
  costs:
    total_spend: 0
    staff_time_hours: 0
    staff_time_cost: 0  # hours × blended rate
    total_cost: 0  # spend + staff time
    
  direct_revenue:
    ticket_sales: 0
    sponsorship_revenue: 0
    merchandise: 0
    total_direct: 0
    
  pipeline_value:
    leads_generated: 0
    qualified_leads: 0
    average_deal_size: 0
    expected_close_rate: 0
    pipeline_value: 0  # qualified × deal_size
    expected_revenue: 0  # pipeline × close_rate
    
  brand_value:
    social_impressions: 0
    media_mentions: 0
    new_email_subscribers: 0
    content_assets_created: 0  # recordings, blogs, clips
    estimated_content_value: 0  # cost to create equivalent
    
  calculations:
    direct_roi_pct: 0  # (direct_revenue - total_cost) / total_cost × 100
    pipeline_roi_pct: 0  # (expected_revenue - total_cost) / total_cost × 100
    cost_per_lead: 0  # total_cost / leads_generated
    cost_per_attendee: 0  # total_cost / attendees
    nps_score: 0
    
  verdict: ""  # repeat | modify | kill
  # Repeat: ROI > 200% or NPS > 50
  # Modify: ROI 50-200% or NPS 20-50
  # Kill: ROI < 50% AND NPS < 20
```

### Post-Event Content Strategy

Maximize the long tail value of your event:

1. **Day 1-2**: Thank you email + survey + photos
2. **Day 3-5**: Recording links (gated = lead gen)
3. **Week 1**: Blog recap ("Top 5 Takeaways from [Event]")
4. **Week 2**: Speaker highlight clips (30-60 sec for social)
5. **Week 3**: Full session recordings released (drip, not all at once)
6. **Month 1**: Ebook/report compiled from session content
7. **Month 2**: Case study from attendee success story
8. **Ongoing**: Repurpose quotes, stats, clips for 3-6 months

### Lessons Learned Template

```yaml
post_mortem:
  event: ""
  date: ""
  attendees: 0
  nps: 0
  
  what_worked:
    - ""
    
  what_didnt:
    - ""
    
  surprises:
    - ""
    
  vendor_feedback:
    - vendor: ""
      rating: "/5"
      rebook: true  # would use again?
      notes: ""
      
  budget_vs_actual:
    budgeted: 0
    actual: 0
    variance_pct: 0
    biggest_overruns: []
    biggest_savings: []
    
  next_time:
    keep: []
    change: []
    add: []
    remove: []
```

---

## Phase 11: Event Series & Scaling

### Building a Recurring Event Brand

1. **Consistent naming** — "[Brand] Summit 2026", "[Brand] Meetup #14"
2. **Monthly cadence for meetups** — same day/time (e.g., "First Thursday")
3. **Annual flagship** — one big event per year, smaller events feed into it
4. **Content flywheel** — each event produces content that markets the next
5. **Community** — create a year-round community (Slack/Discord) between events
6. **Alumni pricing** — past attendees get early access and discounts

### Scaling Checklist

- [ ] Documented SOPs for every role
- [ ] Vendor relationships established (repeat = discounts)
- [ ] Registration system handles volume
- [ ] Volunteer/staff training program
- [ ] Sponsor renewal process (12 months ahead)
- [ ] Content library from past events
- [ ] Budget template refined from actuals
- [ ] NPS trending upward event over event

---

## Phase 12: Industry-Specific Guides

### Tech/SaaS Events
- Focus: Product demos, developer workshops, API hackathons
- Unique: Offer wifi and power at every seat. Developer swag (stickers, tees). Live coding demos.
- Sponsorship angle: "Reach X developers building with [technology]"

### Professional Services (Legal, Consulting, Finance)
- Focus: CLE/CPE credits, roundtable discussions, case study presentations
- Unique: Formal networking (no icebreaker games). Name badges with titles. Printed agendas.
- Sponsorship angle: "Position your firm in front of X decision-makers"

### Healthcare
- Focus: CME credits, compliance workshops, patient outcome data
- Unique: Strict pharma sponsorship rules (Sunshine Act). No gifts >$100. Disclosure requirements.
- Sponsorship angle: Work through compliance-approved channels only

### Construction / Manufacturing
- Focus: Site visits, equipment demos, safety workshops, trade certifications
- Unique: PPE requirements for site visits. Outdoor contingency plans. Hands-on format preferred.
- Sponsorship angle: "Demo your equipment to X contractors/engineers"

### Real Estate
- Focus: Market outlook panels, deal-making networking, property tours
- Unique: Evening cocktail format works best. Bring listings/deal sheets. Intimate roundtables (20-30).
- Sponsorship angle: "Connect with X active investors/developers"

---

## Scoring & Quality Check

### Event Readiness Score (Pre-Event)

Rate 1-5 before proceeding:

| Dimension | Score |
|-----------|-------|
| Venue/platform confirmed and tested | /5 |
| Speakers confirmed with content submitted | /5 |
| Registration open with marketing active | /5 |
| Budget tracked with <10% unknowns | /5 |
| Run-of-show document complete | /5 |
| Team briefed on roles | /5 |
| Contingency plans documented | /5 |
| Tech rehearsal completed | /5 |
| **Total** | **/40** |

**35+** = Go. **25-34** = Fix gaps this week. **<25** = Postpone or simplify.

---

## Natural Language Commands

- "Plan a [type] event for [audience] on [date]"
- "Create a budget for a [size]-person [type] event"
- "Build an event timeline for [date]"
- "Design the agenda for a [duration] [type] event"
- "Write a speaker outreach email for [name] about [topic]"
- "Create a sponsorship deck for [event]"
- "Build a marketing campaign for [event]"
- "Calculate ROI for [event] — [costs] spent, [results] achieved"
- "Create a run-of-show for [event]"
- "Write a post-event survey for [event]"
- "Compare venues: [venue A] vs [venue B]"
- "Plan a webinar on [topic] in [timeframe]"
