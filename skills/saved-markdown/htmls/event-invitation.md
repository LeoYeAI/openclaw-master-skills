# Event / Invitation — HTML Reference

## When to Use This Template

- User asks for an HTML event page, invitation, or meetup landing page
- User explicitly requests HTML format for conference, workshop, or RSVP pages
- User wants styled hero banner, schedule timeline, speaker cards, or registration CTA

---

## Structure Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Event Name}</title>
  <style>
    :root {
      --accent: #7c3aed;
      --accent-dark: #6d28d9;
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
      color: var(--text);
      background: var(--bg);
      line-height: 1.6;
    }

    .hero {
      background: linear-gradient(135deg, var(--accent), var(--accent-dark));
      color: #fff;
      text-align: center;
      padding: 4rem 1.5rem 3rem;
    }

    .hero .event-date {
      display: inline-block;
      background: rgba(255,255,255,0.2);
      padding: 0.4rem 1.2rem;
      border-radius: 999px;
      font-size: 0.9rem;
      margin-bottom: 1rem;
    }

    .hero h1 { font-size: 2.4rem; margin-bottom: 0.5rem; }
    .hero .subtitle { font-size: 1.1rem; opacity: 0.9; max-width: 550px; margin: 0 auto 1.5rem; }

    .hero .btn {
      display: inline-block;
      background: #fff;
      color: var(--accent);
      padding: 0.75rem 2rem;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 700;
      font-size: 1rem;
    }

    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 0 1.5rem;
    }

    section { padding: 3rem 0; }
    section + section { border-top: 1px solid var(--border); }

    h2 {
      font-size: 1.4rem;
      margin-bottom: 1.5rem;
      text-align: center;
    }

    .details-card {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      background: var(--bg-alt);
      border-radius: 12px;
      padding: 1.5rem 2rem;
      margin-bottom: 2rem;
    }

    .detail-item .label {
      font-size: 0.78rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .detail-item .value { font-size: 1rem; font-weight: 600; }

    .schedule-item {
      display: grid;
      grid-template-columns: 100px 1fr;
      gap: 1rem;
      padding: 1rem 0;
      border-bottom: 1px solid var(--border);
    }

    .schedule-item:last-child { border-bottom: none; }

    .schedule-time {
      font-weight: 700;
      color: var(--accent);
      font-size: 0.95rem;
    }

    .schedule-title { font-weight: 600; }
    .schedule-desc { font-size: 0.88rem; color: var(--text-muted); }

    .speakers-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1.5rem;
      text-align: center;
    }

    .speaker-card img {
      width: 90px; height: 90px;
      border-radius: 50%;
      object-fit: cover;
      margin-bottom: 0.5rem;
    }

    .speaker-card h4 { font-size: 0.95rem; margin-bottom: 0.1rem; }
    .speaker-card .role { font-size: 0.82rem; color: var(--text-muted); }

    .cta-section {
      text-align: center;
      background: var(--accent-light);
      border-radius: 12px;
      padding: 2.5rem;
      margin: 2rem 0;
    }

    .cta-section h2 { margin-bottom: 0.5rem; }
    .cta-section p { color: var(--text-muted); margin-bottom: 1.5rem; }

    .cta-section .btn {
      display: inline-block;
      background: var(--accent);
      color: #fff;
      padding: 0.75rem 2.5rem;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 700;
      font-size: 1.05rem;
    }

    footer {
      text-align: center;
      padding: 2rem;
      font-size: 0.85rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border);
    }

    footer a { color: var(--accent); text-decoration: none; }

    @media (max-width: 640px) {
      .hero h1 { font-size: 1.6rem; }
      .hero { padding: 2.5rem 1rem 2rem; }
      .schedule-item { grid-template-columns: 80px 1fr; }
    }
  </style>
</head>
<body>
  <div class="hero">
    <div class="event-date">{Date} · {Location}</div>
    <h1>{Event Name}</h1>
    <div class="subtitle">{Brief event description}</div>
    <a href="{registration_url}" class="btn">Register Now</a>
  </div>

  <div class="container">
    <section>
      <h2>Event Details</h2>
      <div class="details-card">
        <div class="detail-item">
          <div class="label">Date</div>
          <div class="value">{Full date}</div>
        </div>
        <div class="detail-item">
          <div class="label">Time</div>
          <div class="value">{Start} – {End}</div>
        </div>
        <div class="detail-item">
          <div class="label">Location</div>
          <div class="value">{Venue, City}</div>
        </div>
        <div class="detail-item">
          <div class="label">Price</div>
          <div class="value">{Free / Price}</div>
        </div>
      </div>
    </section>

    <section>
      <h2>Schedule</h2>
      <div class="schedule-item">
        <div class="schedule-time">{HH:MM}</div>
        <div>
          <div class="schedule-title">{Session Title}</div>
          <div class="schedule-desc">{Speaker or description}</div>
        </div>
      </div>
      <!-- More schedule items -->
    </section>

    <section>
      <h2>Speakers</h2>
      <div class="speakers-grid">
        <div class="speaker-card">
          <img src="{photo_url}" alt="{Name}">
          <h4>{Name}</h4>
          <div class="role">{Title, Company}</div>
        </div>
        <!-- More speaker cards -->
      </div>
    </section>

    <div class="cta-section">
      <h2>Don't Miss Out</h2>
      <p>{Urgency text — limited spots, early bird, etc.}</p>
      <a href="{registration_url}" class="btn">Register Now</a>
    </div>

    <footer>
      Organized by <a href="{organizer_url}">{Organizer}</a> · Questions? <a href="mailto:{email}">{email}</a>
    </footer>
  </div>
</body>
</html>
```

---

## Styling Guidelines

- **Gradient hero**: Use `linear-gradient(135deg, ...)` for a polished hero — more dynamic than a flat color
- **Event date pill**: Rounded pill badge in the hero with semi-transparent background
- **Details card**: Grid layout with label/value pairs — quick at-a-glance event info
- **Schedule timeline**: Two-column grid (time | content) with bottom borders — clean and scannable
- **Speaker cards**: Circular photos with name/role — same pattern as team cards
- **Dual CTAs**: Registration button in hero AND at the bottom — users shouldn't have to scroll back

---

## Professional Tips

1. **Date and location first** — These are the two most important pieces of info. Make them unmissable.
2. **CTA above and below the fold** — Registration button in the hero and at the bottom
3. **Schedule is key** — Even a rough schedule adds credibility. Include times, titles, and speakers.
4. **Speakers section optional** — Only include with real photos/bios. Skip if the event doesn't have named speakers.
5. **Urgency drives action** — "Limited to 50 spots" or "Early bird ends March 25" in the bottom CTA section
6. **Omit empty sections** — No speakers? Skip it. No schedule yet? Use just the details card.

---

## Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DevNights Bucharest #12 — AI in Production</title>
  <style>
    :root {
      --accent: #7c3aed; --accent-dark: #6d28d9; --accent-light: #ede9fe;
      --text: #1e293b; --text-muted: #64748b;
      --bg: #ffffff; --bg-alt: #f8fafc; --border: #e2e8f0;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: var(--text); background: var(--bg); line-height: 1.6; }
    .hero { background: linear-gradient(135deg, var(--accent), var(--accent-dark)); color: #fff; text-align: center; padding: 4rem 1.5rem 3rem; }
    .hero .event-date { display: inline-block; background: rgba(255,255,255,0.2); padding: 0.4rem 1.2rem; border-radius: 999px; font-size: 0.9rem; margin-bottom: 1rem; }
    .hero h1 { font-size: 2.2rem; margin-bottom: 0.5rem; }
    .hero .subtitle { font-size: 1.1rem; opacity: 0.9; max-width: 550px; margin: 0 auto 1.5rem; }
    .hero .btn { display: inline-block; background: #fff; color: var(--accent); padding: 0.75rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 700; }
    .container { max-width: 800px; margin: 0 auto; padding: 0 1.5rem; }
    section { padding: 3rem 0; }
    section + section { border-top: 1px solid var(--border); }
    h2 { font-size: 1.4rem; margin-bottom: 1.5rem; text-align: center; }
    .details-card { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; background: var(--bg-alt); border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 2rem; }
    .detail-item .label { font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
    .detail-item .value { font-size: 1rem; font-weight: 600; }
    .schedule-item { display: grid; grid-template-columns: 100px 1fr; gap: 1rem; padding: 1rem 0; border-bottom: 1px solid var(--border); }
    .schedule-item:last-child { border-bottom: none; }
    .schedule-time { font-weight: 700; color: var(--accent); font-size: 0.95rem; }
    .schedule-title { font-weight: 600; }
    .schedule-desc { font-size: 0.88rem; color: var(--text-muted); }
    .cta-section { text-align: center; background: var(--accent-light); border-radius: 12px; padding: 2.5rem; margin: 2rem 0; }
    .cta-section h2 { margin-bottom: 0.5rem; }
    .cta-section p { color: var(--text-muted); margin-bottom: 1.5rem; }
    .cta-section .btn { display: inline-block; background: var(--accent); color: #fff; padding: 0.75rem 2.5rem; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 1.05rem; }
    footer { text-align: center; padding: 2rem; font-size: 0.85rem; color: var(--text-muted); border-top: 1px solid var(--border); }
    footer a { color: var(--accent); text-decoration: none; }
    @media (max-width: 640px) { .hero h1 { font-size: 1.6rem; } .schedule-item { grid-template-columns: 80px 1fr; } }
  </style>
</head>
<body>
  <div class="hero">
    <div class="event-date">March 27, 2026 · Bucharest</div>
    <h1>DevNights #12 — AI in Production</h1>
    <div class="subtitle">An evening of talks, demos, and networking around deploying AI systems at scale</div>
    <a href="https://meetup.com/devnights/events/12" class="btn">Register Free</a>
  </div>

  <div class="container">
    <section>
      <h2>Event Details</h2>
      <div class="details-card">
        <div class="detail-item">
          <div class="label">Date</div>
          <div class="value">Thursday, March 27, 2026</div>
        </div>
        <div class="detail-item">
          <div class="label">Time</div>
          <div class="value">18:30 – 21:00 EET</div>
        </div>
        <div class="detail-item">
          <div class="label">Location</div>
          <div class="value">TechHub Bucharest, Calea Victoriei 12</div>
        </div>
        <div class="detail-item">
          <div class="label">Price</div>
          <div class="value">Free</div>
        </div>
      </div>
    </section>

    <section>
      <h2>Schedule</h2>
      <div class="schedule-item">
        <div class="schedule-time">18:30</div>
        <div>
          <div class="schedule-title">Doors Open & Networking</div>
          <div class="schedule-desc">Grab a drink and meet fellow developers</div>
        </div>
      </div>
      <div class="schedule-item">
        <div class="schedule-time">19:00</div>
        <div>
          <div class="schedule-title">From Notebook to Production: Lessons Learned</div>
          <div class="schedule-desc">Ana Popescu — ML Engineer, UiPath</div>
        </div>
      </div>
      <div class="schedule-item">
        <div class="schedule-time">19:40</div>
        <div>
          <div class="schedule-title">Running LLMs on a Budget</div>
          <div class="schedule-desc">Mihai Dragomir — CTO, LocalAI.ro</div>
        </div>
      </div>
      <div class="schedule-item">
        <div class="schedule-time">20:20</div>
        <div>
          <div class="schedule-title">Live Demo: Building an AI Agent with OpenClaw</div>
          <div class="schedule-desc">Bogdan I. — Developer, OpenClaw</div>
        </div>
      </div>
      <div class="schedule-item">
        <div class="schedule-time">20:50</div>
        <div>
          <div class="schedule-title">Open Networking & Drinks</div>
          <div class="schedule-desc">Continue the conversation</div>
        </div>
      </div>
    </section>

    <div class="cta-section">
      <h2>Join Us</h2>
      <p>Limited to 60 spots. Last 3 events sold out.</p>
      <a href="https://meetup.com/devnights/events/12" class="btn">Register Now</a>
    </div>

    <footer>
      Organized by <a href="https://devnights.ro">DevNights Bucharest</a> · Questions? <a href="mailto:hello@devnights.ro">hello@devnights.ro</a>
    </footer>
  </div>
</body>
</html>
```
