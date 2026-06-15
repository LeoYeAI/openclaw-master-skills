# Company Profile — HTML Reference

## When to Use This Template

- User asks for an HTML company page, business profile, or landing page
- User explicitly requests HTML format for an about-us or services page
- User wants styled hero section, service cards, team layout, or CTA buttons

---

## Structure Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Company Name} — {Tagline}</title>
  <style>
    :root {
      --accent: #2563eb;
      --accent-dark: #1d4ed8;
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
      background: var(--bg);
      line-height: 1.6;
    }

    .hero {
      background: var(--accent);
      color: #fff;
      text-align: center;
      padding: 4rem 1.5rem;
    }

    .hero h1 { font-size: 2.2rem; margin-bottom: 0.5rem; }
    .hero .tagline { font-size: 1.15rem; opacity: 0.9; max-width: 600px; margin: 0 auto; }

    .container {
      max-width: 900px;
      margin: 0 auto;
      padding: 0 1.5rem;
    }

    section { padding: 3rem 0; }
    section + section { border-top: 1px solid var(--border); }

    h2 {
      font-size: 1.4rem;
      margin-bottom: 1rem;
      text-align: center;
    }

    .section-subtitle {
      text-align: center;
      color: var(--text-muted);
      max-width: 600px;
      margin: -0.5rem auto 2rem;
      font-size: 0.95rem;
    }

    .services-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
    }

    .service-card {
      background: var(--bg-alt);
      border-radius: 10px;
      padding: 1.5rem;
      border: 1px solid var(--border);
    }

    .service-card h3 { font-size: 1.05rem; margin-bottom: 0.5rem; color: var(--accent); }
    .service-card p { font-size: 0.92rem; color: var(--text-muted); }

    .value-props {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 2rem;
      text-align: center;
    }

    .value-prop .number { font-size: 2rem; font-weight: 700; color: var(--accent); }
    .value-prop .label { font-size: 0.9rem; color: var(--text-muted); }

    .team-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1.5rem;
      text-align: center;
    }

    .team-card img {
      width: 100px; height: 100px;
      border-radius: 50%;
      object-fit: cover;
      margin-bottom: 0.75rem;
    }

    .team-card h4 { font-size: 0.95rem; margin-bottom: 0.15rem; }
    .team-card .role { font-size: 0.82rem; color: var(--text-muted); }

    .cta-section {
      text-align: center;
      background: var(--bg-alt);
      border-radius: 12px;
      padding: 2.5rem;
      margin: 2rem 0;
    }

    .cta-section h2 { margin-bottom: 0.5rem; }
    .cta-section p { color: var(--text-muted); margin-bottom: 1.5rem; }

    .btn {
      display: inline-block;
      background: var(--accent);
      color: #fff;
      padding: 0.75rem 2rem;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 600;
      font-size: 1rem;
    }

    .btn:hover { background: var(--accent-dark); }

    footer {
      text-align: center;
      padding: 2rem;
      font-size: 0.85rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border);
    }

    @media (max-width: 640px) {
      .value-props { grid-template-columns: 1fr; }
      .hero { padding: 2.5rem 1rem; }
      .hero h1 { font-size: 1.6rem; }
    }
  </style>
</head>
<body>
  <div class="hero">
    <h1>{Company Name}</h1>
    <div class="tagline">{One-line value proposition}</div>
  </div>

  <div class="container">
    <section>
      <h2>About Us</h2>
      <p>{2-3 paragraphs about the company — mission, history, what makes it unique.}</p>
    </section>

    <section>
      <h2>Our Services</h2>
      <p class="section-subtitle">{Brief intro to services offered}</p>
      <div class="services-grid">
        <div class="service-card">
          <h3>{Service Name}</h3>
          <p>{Brief description of the service.}</p>
        </div>
        <!-- More service cards -->
      </div>
    </section>

    <section>
      <h2>By the Numbers</h2>
      <div class="value-props">
        <div class="value-prop">
          <div class="number">{N}+</div>
          <div class="label">{Metric label}</div>
        </div>
        <!-- More value props -->
      </div>
    </section>

    <section>
      <h2>Our Team</h2>
      <div class="team-grid">
        <div class="team-card">
          <img src="{photo_url}" alt="{Name}">
          <h4>{Name}</h4>
          <div class="role">{Role}</div>
        </div>
        <!-- More team cards -->
      </div>
    </section>

    <div class="cta-section">
      <h2>Ready to Get Started?</h2>
      <p>{Call to action text}</p>
      <a href="mailto:{email}" class="btn">Contact Us</a>
    </div>

    <footer>
      &copy; {Year} {Company Name} · {Location}<br>
      {email} · {phone}
    </footer>
  </div>
</body>
</html>
```

---

## Styling Guidelines

- **Hero section**: Full-width colored banner at top with company name and tagline — sets the brand tone
- **Service cards grid**: Responsive grid with subtle border and background — easy to scan
- **Value props**: Large numbers with label below — impactful "by the numbers" section
- **Team cards**: Circular photos centered with name/role below — humanizes the brand
- **CTA section**: Standout box with rounded corners, distinct background, prominent button
- **CSS custom properties**: Change `--accent` to match brand colors instantly

---

## Professional Tips

1. **Hero sets the tone** — The hero section is the first impression. Keep the tagline to one sentence.
2. **Services over features** — Frame offerings as services the customer gets, not features you built
3. **Social proof** — Numbers (clients, projects, years) build credibility. Use the value-props section.
4. **Team section is optional** — Only include if photos/bios are provided. Never use placeholder photos.
5. **Single CTA** — One clear call to action. Don't overwhelm with multiple buttons.
6. **Omit empty sections** — No team info? Skip the team grid. No numbers? Skip value props.

---

## Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Meridian Labs — AI Solutions for Healthcare</title>
  <style>
    :root {
      --accent: #0891b2; --accent-dark: #0e7490; --accent-light: #cffafe;
      --text: #1e293b; --text-muted: #64748b;
      --bg: #ffffff; --bg-alt: #f8fafc; --border: #e2e8f0;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: var(--text); background: var(--bg); line-height: 1.6; }
    .hero { background: var(--accent); color: #fff; text-align: center; padding: 4rem 1.5rem; }
    .hero h1 { font-size: 2.2rem; margin-bottom: 0.5rem; }
    .hero .tagline { font-size: 1.15rem; opacity: 0.9; max-width: 600px; margin: 0 auto; }
    .container { max-width: 900px; margin: 0 auto; padding: 0 1.5rem; }
    section { padding: 3rem 0; }
    section + section { border-top: 1px solid var(--border); }
    h2 { font-size: 1.4rem; margin-bottom: 1rem; text-align: center; }
    .section-subtitle { text-align: center; color: var(--text-muted); max-width: 600px; margin: -0.5rem auto 2rem; font-size: 0.95rem; }
    .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
    .service-card { background: var(--bg-alt); border-radius: 10px; padding: 1.5rem; border: 1px solid var(--border); }
    .service-card h3 { font-size: 1.05rem; margin-bottom: 0.5rem; color: var(--accent); }
    .service-card p { font-size: 0.92rem; color: var(--text-muted); }
    .value-props { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; text-align: center; }
    .value-prop .number { font-size: 2rem; font-weight: 700; color: var(--accent); }
    .value-prop .label { font-size: 0.9rem; color: var(--text-muted); }
    .cta-section { text-align: center; background: var(--bg-alt); border-radius: 12px; padding: 2.5rem; margin: 2rem 0; }
    .cta-section h2 { margin-bottom: 0.5rem; }
    .cta-section p { color: var(--text-muted); margin-bottom: 1.5rem; }
    .btn { display: inline-block; background: var(--accent); color: #fff; padding: 0.75rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; }
    footer { text-align: center; padding: 2rem; font-size: 0.85rem; color: var(--text-muted); border-top: 1px solid var(--border); }
    @media (max-width: 640px) { .value-props { grid-template-columns: 1fr; } .hero { padding: 2.5rem 1rem; } .hero h1 { font-size: 1.6rem; } }
  </style>
</head>
<body>
  <div class="hero">
    <h1>Meridian Labs</h1>
    <div class="tagline">AI-powered diagnostic tools that help clinicians make faster, more accurate decisions</div>
  </div>

  <div class="container">
    <section>
      <h2>About Us</h2>
      <p>Founded in 2021 in Zurich, Meridian Labs builds AI diagnostic assistants for hospitals and clinics across Europe. Our models analyze medical imaging, lab results, and patient histories to surface actionable insights in real time.</p>
      <p style="margin-top:1rem;">We partner with 40+ healthcare institutions and are certified for clinical use under the EU AI Act.</p>
    </section>

    <section>
      <h2>Our Services</h2>
      <p class="section-subtitle">End-to-end AI integration for healthcare providers</p>
      <div class="services-grid">
        <div class="service-card">
          <h3>Diagnostic AI</h3>
          <p>Real-time imaging analysis for radiology, pathology, and dermatology with 97.3% accuracy.</p>
        </div>
        <div class="service-card">
          <h3>Clinical Decision Support</h3>
          <p>Evidence-based treatment recommendations integrated directly into your EHR workflow.</p>
        </div>
        <div class="service-card">
          <h3>Data Platform</h3>
          <p>HIPAA/GDPR-compliant data pipeline for training custom models on your institution's data.</p>
        </div>
      </div>
    </section>

    <section>
      <h2>By the Numbers</h2>
      <div class="value-props">
        <div class="value-prop">
          <div class="number">40+</div>
          <div class="label">Hospital Partners</div>
        </div>
        <div class="value-prop">
          <div class="number">2.1M</div>
          <div class="label">Scans Analyzed</div>
        </div>
        <div class="value-prop">
          <div class="number">97.3%</div>
          <div class="label">Diagnostic Accuracy</div>
        </div>
      </div>
    </section>

    <div class="cta-section">
      <h2>Ready to Transform Your Diagnostics?</h2>
      <p>Schedule a demo to see Meridian AI in action with your own imaging data.</p>
      <a href="mailto:sales@meridianlabs.ai" class="btn">Request a Demo</a>
    </div>

    <footer>
      &copy; 2026 Meridian Labs AG · Zurich, Switzerland<br>
      sales@meridianlabs.ai · +41 44 123 4567
    </footer>
  </div>
</body>
</html>
```
