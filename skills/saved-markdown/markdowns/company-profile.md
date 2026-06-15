# Company Profile Reference

## When to Use This Template

- User asks for a company page, business profile, service listing, or about page
- Keywords: company profile, business page, about us, services page, landing page, company overview
- User provides business information: services, team, mission, products
- Output is a public-facing business presence page

---

## Structure Template

```markdown
<img
  src="{logo_url}"
  alt="{Company Name} logo"
  style="display:block; margin:0 auto; max-width:200px; background: transparent;"
/>

# {Company Name}

**{Tagline — one sentence that captures what the company does and for whom}**

📍 {Location} · 📧 {email} · 🌐 [{website}]({url})

---

## About

{2-3 paragraphs covering: what the company does, who it serves, what makes it different. Lead with customer value, not company history. Founding story only if it adds credibility or emotional connection.}

---

## Services

| Service | Description | Benefit |
|---------|-------------|---------|
| {Service 1} | {What it is — 1 sentence} | {What the customer gets} |
| {Service 2} | {What it is} | {Customer benefit} |
| {Service 3} | {What it is} | {Customer benefit} |

---

## Why {Company Name}

- ✅ {Value proposition 1 — specific, not generic}
- ✅ {Value proposition 2 — backed by evidence if possible}
- ✅ {Value proposition 3}
- ✅ {Value proposition 4}

---

## Our Work

{Brief case studies, notable clients, or portfolio highlights}

| Client / Project | What We Did | Result |
|-----------------|-------------|--------|
| {Client} | {Scope} | {Outcome} |
| {Client} | {Scope} | {Outcome} |

---

## Team

### {Name} — {Title}
{1-2 sentence bio focusing on relevant expertise}

### {Name} — {Title}
{1-2 sentence bio}

---

## Contact

Ready to get started? Reach out:

- 📧 **{email}**
- 📞 **{phone}**
- 🌐 [{website}]({url})
- 📍 {Full address if physical location}
```

---

## Styling Guidelines

- **Logo**: Use `<img>` with `max-width:200px`, centered. Only include if user provides URL.
- **Tagline under H1**: Bold, one sentence. Should communicate what + for whom.
- **Services as a table**: Three columns — Service, Description, Benefit. Tables are scannable; paragraphs are not.
- **Value propositions**: Use ✅ emoji bullets for "Why Us" to make them feel like checkmarks/guarantees.
- **Contact CTA**: End with a clear call to action, not just listed contact info.
- **Omit sections freely**: Team, Our Work, and other sections are optional. Never include them with placeholder content.

---

## Chart Recommendations

Charts are **occasionally useful** in company profiles, typically for demonstrating traction or market position.

**Growth/traction bar chart** (for startups or growth-stage companies):
```
```markdown-ui-widget
chart-bar
title: Clients Served by Year
Year,Clients
2022,24
2023,58
2024,112
2025,185
```
```

**Service distribution pie chart** (to show service mix):
```
```markdown-ui-widget
chart-pie
title: Revenue by Service Line
Service,Share
Consulting,40
Development,35
"Managed Services",15
Training,10
```
```

Limit to 1-2 charts maximum. Company profiles should be text-forward.

---

## Professional Tips

1. **Lead with customer value, not company history** — "We help X do Y" beats "Founded in 2019 by..."
2. **Services table > services paragraphs** — Nobody reads 5 paragraphs about your services. A table with Description + Benefit columns is 10x more effective.
3. **Specific value props** — "99.9% uptime SLA" beats "Reliable service". "Avg response time: 2 hours" beats "Fast support".
4. **Social proof matters** — Client names, case study results, or testimonial quotes add instant credibility
5. **One clear CTA** — End with exactly one thing you want the visitor to do: email, call, book a demo
6. **Keep team bios short** — 1-2 sentences per person. Focus on relevant expertise, not life story
7. **Mobile-friendly structure** — Short paragraphs, tables, bullet points. No walls of text.

---

## Example

```markdown
# Meridian Labs

**Product engineering for climate-tech startups — from prototype to Series A**

📍 Amsterdam, NL · 📧 hello@meridianlabs.dev · 🌐 [meridianlabs.dev](https://meridianlabs.dev)

---

## About

Meridian Labs builds MVPs and production systems for climate technology companies. We work with seed-to-Series-A startups that need to ship fast without accumulating tech debt. Our team has delivered 40+ products across carbon accounting, energy optimization, and supply chain transparency.

We're a team of 12 engineers and designers who've previously built at Stripe, Vercel, and Tomorrow.io.

---

## Services

| Service | Description | Benefit |
|---------|-------------|---------|
| MVP Development | Full-stack build from Figma to production in 8-12 weeks | Launch faster, validate sooner |
| Technical Due Diligence | Code audit + architecture review for investors | De-risk your funding round |
| Team Augmentation | Embed senior engineers into your existing team | Scale without hiring overhead |
| Design Sprints | 5-day rapid prototyping with user testing | Validate ideas before building |

---

## Why Meridian Labs

- ✅ **Climate-tech specialists** — We understand carbon data, energy APIs, and ESG reporting
- ✅ **40+ products shipped** — From idea to production, we've done this before
- ✅ **Avg. MVP in 10 weeks** — Fixed-scope, fixed-price engagement model
- ✅ **Post-launch support** — 3 months of maintenance included with every build

---

## Our Work

| Client | What We Built | Result |
|--------|---------------|--------|
| CarbonTrack | Real-time emissions dashboard for logistics companies | Secured $4.2M Series A |
| GridFlow | Energy load balancing optimizer for commercial buildings | 18% avg. energy cost reduction |
| EcoChain | Supply chain transparency platform for fashion brands | 200+ brands onboarded in 6 months |

---

## Team

### Lena Voss — CEO & Co-founder
Former engineering lead at Stripe Climate. 12 years building developer tools and data platforms.

### Marco Reyes — CTO & Co-founder
Previously at Tomorrow.io building weather prediction APIs. Systems architecture specialist.

---

## Contact

Building something in climate tech? Let's talk.

- 📧 **hello@meridianlabs.dev**
- 📞 **+31 20 555 0123**
- 🌐 [meridianlabs.dev](https://meridianlabs.dev)
- 📍 Keizersgracht 520, Amsterdam
```
