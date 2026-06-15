# Resume / CV — HTML Reference

## When to Use This Template

- User asks for an HTML resume, CV, personal profile, or professional landing page
- User explicitly requests HTML format for a resume
- User wants richer visual styling (two-column layout, color accents, styled skill tags)

---

## Structure Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Full Name} — {Role}</title>
  <style>
    :root {
      --accent: #2563eb;
      --accent-light: #dbeafe;
      --text: #1e293b;
      --text-muted: #64748b;
      --bg: #ffffff;
      --bg-alt: #f8fafc;
      --border: #e2e8f0;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: var(--text);
      background: var(--bg-alt);
      line-height: 1.6;
    }

    .container {
      max-width: 860px;
      margin: 2rem auto;
      background: var(--bg);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    header {
      display: grid;
      grid-template-columns: 150px 1fr;
      gap: 2rem;
      padding: 2.5rem;
      background: var(--accent);
      color: #fff;
      align-items: center;
    }

    header img {
      width: 130px;
      height: 130px;
      border-radius: 50%;
      border: 4px solid rgba(255,255,255,0.3);
      object-fit: cover;
    }

    header h1 { font-size: 1.8rem; margin-bottom: 0.25rem; }
    header .tagline { opacity: 0.9; font-size: 1.05rem; }

    header .contact-row {
      margin-top: 0.75rem;
      font-size: 0.9rem;
      opacity: 0.85;
    }

    header .contact-row a { color: #fff; }

    main {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 2rem;
      padding: 2.5rem;
    }

    .left-col section, .right-col section { margin-bottom: 2rem; }

    h2 {
      font-size: 1.1rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--accent);
      border-bottom: 2px solid var(--accent);
      padding-bottom: 0.4rem;
      margin-bottom: 1rem;
    }

    .job { margin-bottom: 1.25rem; }
    .job h3 { font-size: 1rem; margin-bottom: 0.15rem; }
    .job .meta { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem; }
    .job ul { padding-left: 1.2rem; font-size: 0.92rem; }
    .job li { margin-bottom: 0.3rem; }

    .skill-tag {
      display: inline-block;
      background: var(--accent-light);
      color: var(--accent);
      padding: 0.2rem 0.65rem;
      border-radius: 999px;
      font-size: 0.82rem;
      margin: 0.2rem 0.15rem;
      font-weight: 500;
    }

    .edu-item, .cert-item { margin-bottom: 0.75rem; font-size: 0.92rem; }
    .edu-item strong, .cert-item strong { display: block; }
    .edu-item .meta, .cert-item .meta { font-size: 0.82rem; color: var(--text-muted); }

    footer {
      text-align: center;
      padding: 1.5rem;
      background: var(--bg-alt);
      font-size: 0.9rem;
      color: var(--text-muted);
    }

    footer a { color: var(--accent); text-decoration: none; }

    @media print {
      body { background: #fff; }
      .container { box-shadow: none; margin: 0; border-radius: 0; }
    }

    @media (max-width: 640px) {
      header { grid-template-columns: 1fr; text-align: center; }
      header img { margin: 0 auto; }
      main { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <img src="{photo_url}" alt="{Name}">
      <div>
        <h1>{Full Name}</h1>
        <div class="tagline">{Professional tagline — role + specialty}</div>
        <div class="contact-row">
          {email} · {phone} · {location}<br>
          <a href="{linkedin_url}">LinkedIn</a> · <a href="{portfolio_url}">Portfolio</a>
        </div>
      </div>
    </header>

    <main>
      <div class="left-col">
        <section>
          <h2>About</h2>
          <p>{2-3 sentence professional summary.}</p>
        </section>

        <section>
          <h2>Experience</h2>

          <div class="job">
            <h3>{Job Title} — {Company}</h3>
            <div class="meta">{MMM YYYY} – {MMM YYYY | Present}</div>
            <ul>
              <li>{Achievement with quantified result}</li>
              <li>{Achievement with scope}</li>
            </ul>
          </div>

          <!-- Repeat .job blocks -->
        </section>
      </div>

      <div class="right-col">
        <section>
          <h2>Skills</h2>
          <span class="skill-tag">{Skill 1}</span>
          <span class="skill-tag">{Skill 2}</span>
          <span class="skill-tag">{Skill 3}</span>
          <!-- More tags -->
        </section>

        <section>
          <h2>Education</h2>
          <div class="edu-item">
            <strong>{Degree}</strong>
            <span class="meta">{Institution}, {Year}</span>
          </div>
        </section>

        <section>
          <h2>Certifications</h2>
          <div class="cert-item">
            <strong>{Certification}</strong>
            <span class="meta">{Issuer}, {Year}</span>
          </div>
        </section>
      </div>
    </main>

    <footer>
      Interested in working together? Reach out at <a href="mailto:{email}">{email}</a>
    </footer>
  </div>
</body>
</html>
```

---

## Styling Guidelines

- **Two-column grid**: Left column for experience/about (wider), right column for skills/education/certs
- **Colored accent header**: Full-width `header` with `var(--accent)` background, white text, circular photo
- **Skill tags**: Styled `<span class="skill-tag">` with pill shape and accent colors — more visual than a table
- **CSS custom properties**: All colors in `:root` for easy theming — change `--accent` to rebrand instantly
- **Print media query**: Clean output with no shadows/background for PDF generation
- **Responsive**: Falls back to single-column on mobile via `@media (max-width: 640px)`

---

## Professional Tips

1. **Lead with achievements, not responsibilities** — same as markdown; HTML just makes them more visually prominent
2. **Skill tags over tables** — In HTML, pill-shaped tags are more scannable and visually engaging than tables
3. **Color theming** — Change `--accent` to match the user's personal brand or target company
4. **Photo sizing** — Keep `width`/`height` at 130px with `object-fit: cover` to avoid distortion
5. **Print-friendly** — The `@media print` block ensures the resume prints cleanly without background/shadows
6. **Omit empty sections** — If no certifications, remove the entire `<section>` — don't leave empty headers

---

## Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Maria Chen — Senior Product Designer</title>
  <style>
    :root {
      --accent: #7c3aed;
      --accent-light: #ede9fe;
      --text: #1e293b;
      --text-muted: #64748b;
      --bg: #ffffff;
      --bg-alt: #f8fafc;
      --border: #e2e8f0;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: var(--text); background: var(--bg-alt); line-height: 1.6;
    }
    .container {
      max-width: 860px; margin: 2rem auto; background: var(--bg);
      border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    header {
      display: grid; grid-template-columns: 150px 1fr; gap: 2rem;
      padding: 2.5rem; background: var(--accent); color: #fff; align-items: center;
    }
    header img {
      width: 130px; height: 130px; border-radius: 50%;
      border: 4px solid rgba(255,255,255,0.3); object-fit: cover;
    }
    header h1 { font-size: 1.8rem; margin-bottom: 0.25rem; }
    header .tagline { opacity: 0.9; font-size: 1.05rem; }
    header .contact-row { margin-top: 0.75rem; font-size: 0.9rem; opacity: 0.85; }
    header .contact-row a { color: #fff; }
    main { display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; padding: 2.5rem; }
    .left-col section, .right-col section { margin-bottom: 2rem; }
    h2 {
      font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.05em;
      color: var(--accent); border-bottom: 2px solid var(--accent);
      padding-bottom: 0.4rem; margin-bottom: 1rem;
    }
    .job { margin-bottom: 1.25rem; }
    .job h3 { font-size: 1rem; margin-bottom: 0.15rem; }
    .job .meta { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem; }
    .job ul { padding-left: 1.2rem; font-size: 0.92rem; }
    .job li { margin-bottom: 0.3rem; }
    .skill-tag {
      display: inline-block; background: var(--accent-light); color: var(--accent);
      padding: 0.2rem 0.65rem; border-radius: 999px; font-size: 0.82rem;
      margin: 0.2rem 0.15rem; font-weight: 500;
    }
    .edu-item { margin-bottom: 0.75rem; font-size: 0.92rem; }
    .edu-item strong { display: block; }
    .edu-item .meta { font-size: 0.82rem; color: var(--text-muted); }
    footer {
      text-align: center; padding: 1.5rem; background: var(--bg-alt);
      font-size: 0.9rem; color: var(--text-muted);
    }
    footer a { color: var(--accent); text-decoration: none; }
    @media print { body { background: #fff; } .container { box-shadow: none; margin: 0; border-radius: 0; } }
    @media (max-width: 640px) { header { grid-template-columns: 1fr; text-align: center; } header img { margin: 0 auto; } main { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <img src="https://example.com/photos/maria-chen.jpg" alt="Maria Chen">
      <div>
        <h1>Maria Chen</h1>
        <div class="tagline">Senior Product Designer — Crafting B2B tools that users actually love</div>
        <div class="contact-row">
          maria@designstudio.io · Berlin, Germany<br>
          <a href="https://linkedin.com/in/mariachen">LinkedIn</a> ·
          <a href="https://mariachen.design">Portfolio</a> ·
          <a href="https://dribbble.com/mariachen">Dribbble</a>
        </div>
      </div>
    </header>

    <main>
      <div class="left-col">
        <section>
          <h2>About</h2>
          <p>Product designer with 8 years of experience building enterprise SaaS interfaces. Specialized in turning complex workflows into intuitive experiences. Previously at Stripe and Figma, now freelancing with early-stage B2B startups.</p>
        </section>

        <section>
          <h2>Experience</h2>
          <div class="job">
            <h3>Lead Product Designer — Stripe</h3>
            <div class="meta">Mar 2022 – Present</div>
            <ul>
              <li>Redesigned merchant onboarding flow, reducing drop-off by 34% across 12 markets</li>
              <li>Led 5-person design team shipping Stripe Tax's first self-serve configuration UI</li>
              <li>Established component audit process that cut design-to-dev handoff time by 40%</li>
            </ul>
          </div>
          <div class="job">
            <h3>Product Designer — Figma</h3>
            <div class="meta">Jan 2019 – Feb 2022</div>
            <ul>
              <li>Designed collaborative commenting system used by 4M+ users daily</li>
              <li>Shipped accessibility improvements bringing WCAG AA compliance to 96% of components</li>
              <li>Mentored 3 junior designers through Figma's design guild program</li>
            </ul>
          </div>
        </section>
      </div>

      <div class="right-col">
        <section>
          <h2>Skills</h2>
          <span class="skill-tag">Figma</span>
          <span class="skill-tag">Sketch</span>
          <span class="skill-tag">Principle</span>
          <span class="skill-tag">User Research</span>
          <span class="skill-tag">A/B Testing</span>
          <span class="skill-tag">HTML/CSS</span>
          <span class="skill-tag">React</span>
          <span class="skill-tag">Design Systems</span>
          <span class="skill-tag">Accessibility</span>
        </section>

        <section>
          <h2>Education</h2>
          <div class="edu-item">
            <strong>B.A. Interaction Design</strong>
            <span class="meta">University of the Arts, Berlin — 2016</span>
          </div>
        </section>

        <section>
          <h2>Awards</h2>
          <div class="edu-item">
            <strong>Webby Award, Best UX</strong>
            <span class="meta">Stripe Tax Dashboard, 2023</span>
          </div>
          <div class="edu-item">
            <strong>Featured Creator</strong>
            <span class="meta">Figma Community, 2021</span>
          </div>
        </section>
      </div>
    </main>

    <footer>
      Interested in working together? Reach out at <a href="mailto:maria@designstudio.io">maria@designstudio.io</a>
    </footer>
  </div>
</body>
</html>
```
