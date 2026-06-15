# Resume / CV Reference

## When to Use This Template

- User asks for a resume, CV, personal profile, or professional landing page
- Keywords: resume, CV, curriculum vitae, professional profile, personal page, career page, bio page
- User provides work experience, skills, education, or career information
- User wants a shareable professional link

---

## Structure Template

```markdown
<img
  src="{photo_url}"
  alt="{Name}"
  style="display:block; margin:0 auto; width:150px; height:150px; border-radius:50%; background: transparent;"
/>

# {Full Name}

**{Professional tagline — role + specialty or value proposition}**

📧 {email} · 📱 {phone} · 📍 {location}
🔗 [{LinkedIn}]({url}) · [{Portfolio/Website}]({url}) · [{GitHub}]({url})

---

## About

{2-3 sentence professional summary. Lead with years of experience, core expertise, and what makes this person distinctive. End with what they're looking for or passionate about.}

---

## 💼 Experience

### {Job Title} — {Company}
*{MMM YYYY} – {MMM YYYY | Present}*

- {Achievement with quantified result: "Increased X by Y% through Z"}
- {Achievement with scope: "Led team of N to deliver..."}
- {Achievement with impact: "Reduced costs by $X through..."}

### {Job Title} — {Company}
*{MMM YYYY} – {MMM YYYY}*

- {Achievement 1}
- {Achievement 2}

---

## 🛠 Skills

| Category | Skills |
|----------|--------|
| {Languages} | {Python, TypeScript, Go, ...} |
| {Frameworks} | {React, FastAPI, Django, ...} |
| {Tools} | {Docker, AWS, Terraform, ...} |
| {Soft Skills} | {Leadership, Communication, ...} |

---

## 🎓 Education

**{Degree}** — {Institution}
*{Year}*
{Optional: honors, GPA, relevant coursework}

---

## 🏆 Certifications & Awards

- {Certification/Award} — {Issuer}, {Year}
- {Certification/Award} — {Issuer}, {Year}

---

## 📬 Contact

Interested in working together? Reach out at **{email}** or connect on [{LinkedIn}]({url}).
```

---

## Styling Guidelines

- **Profile photo**: Always use the circular `<img>` tag with `border-radius:50%` when user provides a photo URL. Center it above the name.
- **Contact row**: Keep all contact info on 1-2 lines using `·` as separators. Use emoji prefixes (📧, 📱, 📍, 🔗).
- **Section headers**: Use emoji-prefixed H2s (💼, 🛠, 🎓, 🏆, 📬) for visual scanning.
- **Skills table**: Always use a table, never a comma-separated list — tables scan faster.
- **Horizontal rules** (`---`): Use between major sections for visual breathing room.
- **Bold company names and dates**: Makes the career timeline scannable.

---

## Chart Recommendations

Charts are **rarely used** in resumes. Exceptions:

- **Skills proficiency bar chart** (only if user specifically requests a visual skills rating):
```
```markdown-ui-widget
chart-bar
title: Technical Skills Proficiency
Skill,Proficiency
Python,95
TypeScript,88
React,82
Docker,78
AWS,85
```
```

- **Career timeline** (only for visual portfolios, not standard resumes)

In general, prefer tables over charts for resumes — they're more professional and information-dense.

---

## Professional Tips

1. **Lead with achievements, not responsibilities** — "Increased revenue by 40%" beats "Responsible for revenue growth"
2. **Quantify everything** — Numbers, percentages, dollar amounts, team sizes, timelines make claims credible
3. **Action verbs first** — Start every bullet with: Led, Built, Designed, Reduced, Increased, Launched, Automated, Delivered
4. **One-page equivalent** — Keep total content to what would fit on 1-2 printed pages. Ruthlessly cut filler.
5. **Omit empty sections** — No education? Skip it. No certifications? Skip it. Never include placeholder text.
6. **Tailor the tagline** — The line under the name should communicate role + unique value, not just a job title
7. **Most recent first** — Always reverse chronological order for experience and education
8. **Contact CTA at the end** — Close with a warm, actionable invitation to connect

---

## Example

```markdown
<img
  src="https://example.com/photos/maria-chen.jpg"
  alt="Maria Chen"
  style="display:block; margin:0 auto; width:150px; height:150px; border-radius:50%; background: transparent;"
/>

# Maria Chen

**Senior Product Designer — Crafting B2B tools that users actually love**

📧 maria@designstudio.io · 📍 Berlin, Germany
🔗 [LinkedIn](https://linkedin.com/in/mariachen) · [Portfolio](https://mariachen.design) · [Dribbble](https://dribbble.com/mariachen)

---

## About

Product designer with 8 years of experience building enterprise SaaS interfaces. Specialized in turning complex workflows into intuitive experiences. Previously at Stripe and Figma, now freelancing with early-stage B2B startups.

---

## 💼 Experience

### Lead Product Designer — Stripe
*Mar 2022 – Present*

- Redesigned the merchant onboarding flow, reducing drop-off by 34% across 12 markets
- Led a 5-person design team shipping Stripe Tax's first self-serve configuration UI
- Established a component audit process that cut design-to-dev handoff time by 40%

### Product Designer — Figma
*Jan 2019 – Feb 2022*

- Designed the collaborative commenting system used by 4M+ users daily
- Shipped accessibility improvements that brought WCAG AA compliance to 96% of components
- Mentored 3 junior designers through Figma's design guild program

### UI/UX Designer — Freelance
*Jun 2016 – Dec 2018*

- Delivered 20+ client projects across fintech, healthtech, and e-commerce
- Built a reusable design system template adopted by 500+ Figma community members

---

## 🛠 Skills

| Category | Skills |
|----------|--------|
| Design | Figma, Sketch, Principle, Framer |
| Research | User interviews, A/B testing, heuristic evaluation |
| Development | HTML/CSS, React (prototyping), Storybook |
| Methods | Design systems, accessibility, design sprints |

---

## 🎓 Education

**B.A. Interaction Design** — University of the Arts, Berlin
*2016*

---

## 🏆 Awards

- Webby Award, Best UX — Stripe Tax Dashboard, 2023
- Figma Community Featured Creator, 2021

---

## 📬 Contact

Open to full-time and contract opportunities. Reach out at **maria@designstudio.io** or connect on [LinkedIn](https://linkedin.com/in/mariachen).
```
