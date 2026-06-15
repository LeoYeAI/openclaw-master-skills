# Portfolio / Showcase Reference

## When to Use This Template

- User asks for a portfolio, showcase, case studies, work samples, or project gallery
- Keywords: portfolio, showcase, case study, projects, work samples, gallery, body of work
- User wants to present multiple completed projects or creative works
- Output highlights accomplishments with visual elements and results

---

## Structure Template

```markdown
# {Portfolio Title}

**{Name or Studio}** — {One-line positioning statement}

📧 {email} · 🌐 [{website}]({url}) · [{GitHub/Dribbble/Behance}]({url})

---

## Featured Projects

### {Project 1 Name}

![{Project screenshot}]({image_url})

**{One-sentence description of the project}**

| | |
|---|---|
| **Role** | {Your role} |
| **Tech** | `{tech1}` `{tech2}` `{tech3}` |
| **Timeline** | {duration} |
| **Link** | [{Live site}]({url}) |

**The Problem:** {What challenge was this project solving?}

**The Solution:** {What did you build and how does it work?}

**The Result:** {Quantified outcome — traffic, revenue, user adoption, performance improvement}

---

### {Project 2 Name}

![{Project screenshot}]({image_url})

**{One-sentence description}**

| | |
|---|---|
| **Role** | {Role} |
| **Tech** | `{tech1}` `{tech2}` `{tech3}` |
| **Timeline** | {duration} |
| **Link** | [{Live site}]({url}) |

**The Problem:** {Challenge}

**The Solution:** {What you built}

**The Result:** {Outcome}

---

### {Project 3 Name}

{Same pattern...}

---

## Skills & Tools

| Category | Technologies |
|----------|-------------|
| {Frontend} | `React` `TypeScript` `Next.js` `Tailwind` |
| {Backend} | `Node.js` `Python` `PostgreSQL` `Redis` |
| {DevOps} | `Docker` `AWS` `Terraform` `GitHub Actions` |
| {Design} | `Figma` `Framer` `Principle` |

---

## About

{2-3 sentences about you/your studio. What kind of work you do, what you specialize in, what you're looking for.}

---

## Get in Touch

Available for {freelance / full-time / contract} work.

📧 **{email}** · 🌐 [{website}]({url})
```

---

## Styling Guidelines

- **Tech stack as inline code** — Use backtick `code` styling for technologies: `React` `PostgreSQL` `Docker`. This is a portfolio convention and improves scannability.
- **Problem → Solution → Result** per project — This trio structure tells a story, not just "I built X"
- **Project images**: Standard markdown `![alt](url)` for screenshots. Images are critical for visual portfolios.
- **Key-value table for metadata** — Use a borderless-style two-column table for Role, Tech, Timeline, Link. Compact and scannable.
- **Lead with strongest project** — Put your best work first. Attention declines as the page scrolls.
- **3-5 projects is ideal** — Enough to show range, not so many that quality dilutes

---

## Chart Recommendations

Charts are **occasionally useful** for showcasing quantified results.

**Project results bar chart** (comparing outcomes across projects):
```
```markdown-ui-widget
chart-bar
title: Project Impact — Performance Improvements
Project,"Load Time Reduction (%)"
"E-commerce Rebuild",62
"Dashboard Redesign",45
"API Optimization",78
"Mobile App",51
```
```

**Skills proficiency** (only if specifically requested):
```
```markdown-ui-widget
chart-bar
title: Technology Experience (Years)
Technology,Years
React,6
Python,8
PostgreSQL,5
AWS,4
Docker,3
```
```

Use 0-1 charts. Portfolios are visual-image-forward, not chart-forward.

---

## Professional Tips

1. **Lead with your strongest project** — First impressions matter most. Put your best, most impressive work at the top.
2. **Quantify results** — "Reduced load time by 62%" beats "Made the site faster". Numbers make claims credible.
3. **Problem → Solution → Result** — Every project should tell this story. Clients want to see your thinking process, not just the output.
4. **Tech as inline code** — `React` `Node.js` `PostgreSQL` reads like a natural skill tag and is a recognized portfolio convention
5. **Include live links** — If the project is live, link to it. If it's not, include a screenshot or demo video link.
6. **3-5 projects maximum** — Curate ruthlessly. A portfolio of 3 excellent projects beats 12 mediocre ones.
7. **Show range** — If you can, include projects of different types (web app, mobile, API, design system) to demonstrate versatility
8. **Images make or break portfolios** — A portfolio without visuals feels incomplete. Always include screenshots, mockups, or diagrams.

---

## Example

```markdown
# Projects by Alex Rivera

**Full-Stack Developer** — Building fast, accessible web applications

📧 alex@rivera.dev · 🌐 [rivera.dev](https://rivera.dev) · [GitHub](https://github.com/arivera)

---

## Featured Projects

### Tempo — Collaborative Music Production

![Tempo app screenshot](https://rivera.dev/shots/tempo-hero.png)

**Real-time collaborative DAW in the browser — "Google Docs for music producers"**

| | |
|---|---|
| **Role** | Lead developer (team of 3) |
| **Tech** | `React` `WebAudio API` `WebRTC` `Node.js` `PostgreSQL` |
| **Timeline** | 4 months |
| **Link** | [tempo.music](https://tempo.music) |

**The Problem:** Music producers collaborating remotely were sharing stems via email and Dropbox, losing hours to version conflicts and latency.

**The Solution:** A browser-based multi-track editor with real-time collaboration via WebRTC. Users see each other's cursors and edits live, with conflict-free merging using CRDTs.

**The Result:** 2,400 active users within 3 months of launch. Featured in MusicTech Magazine. Average session length: 47 minutes.

---

### Dash — Developer Analytics Dashboard

![Dash screenshot](https://rivera.dev/shots/dash-hero.png)

**GitHub activity analytics for engineering managers**

| | |
|---|---|
| **Role** | Solo developer |
| **Tech** | `Next.js` `TypeScript` `D3.js` `GitHub API` `Vercel` |
| **Timeline** | 6 weeks |
| **Link** | [getdash.dev](https://getdash.dev) |

**The Problem:** Engineering managers had no way to see team velocity, PR review times, or deployment frequency without expensive enterprise tools.

**The Solution:** A lightweight dashboard that connects to GitHub and visualizes team metrics: PR cycle time, review bottlenecks, deploy frequency, and contributor activity.

**The Result:** 800+ GitHub installs. Reduced avg PR review time by 34% for teams that adopted review-time alerts.

---

### GreenCart — Sustainable E-commerce Platform

![GreenCart screenshot](https://rivera.dev/shots/greencart-hero.png)

**Carbon-neutral e-commerce with integrated offset tracking**

| | |
|---|---|
| **Role** | Frontend lead (team of 5) |
| **Tech** | `React` `Shopify API` `Stripe` `Python` `FastAPI` |
| **Timeline** | 3 months |
| **Link** | [greencart.shop](https://greencart.shop) |

**The Problem:** Eco-conscious shoppers wanted to understand and offset the carbon footprint of their purchases, but no e-commerce platform made this easy.

**The Solution:** A Shopify-integrated storefront that calculates per-order carbon impact using shipping distance and product weight, then offers one-click offsets at checkout via a carbon credit API.

**The Result:** 12% of customers opted into offsets at checkout. $24K in carbon credits purchased in first quarter. Lighthouse performance score: 98.

---

## Skills & Tools

| Category | Technologies |
|----------|-------------|
| Frontend | `React` `Next.js` `TypeScript` `Tailwind CSS` `D3.js` |
| Backend | `Node.js` `Python` `FastAPI` `PostgreSQL` `Redis` |
| Infrastructure | `Vercel` `AWS` `Docker` `GitHub Actions` |
| APIs | `Stripe` `GitHub` `Shopify` `WebRTC` |

---

## About

Full-stack developer with 6 years of experience building web applications that are fast, accessible, and maintainable. I specialize in real-time collaboration tools and data visualization. Currently open to freelance and contract work.

---

## Get in Touch

Available for freelance and contract projects.

📧 **alex@rivera.dev** · 🌐 [rivera.dev](https://rivera.dev)
```
