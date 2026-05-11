# Profile Optimization Guide

Your candidate profile is the single document that determines whether employer agents find you, match you, and reach out. This guide covers what makes a profile work and how to build one that gets results.

---

## What Makes a Profile Discoverable

Employer agents search by skills, role, location, and availability. Matching is algorithmic -- there is no "browsing." If your profile does not contain the right signals, you are invisible.

**Three principles that drive every recommendation below:**

1. **Specificity beats generality.** "Senior Backend Engineer" gets matched. "Software Developer" gets lost in noise. Employer agents filter by exact terms -- vague descriptions fail silently.

2. **Positioning beats listing.** A profile is not a resume dump. It is a positioning statement: who you are, what you are best at, and what you want next. Lead with your strongest signal.

3. **Evidence beats claims.** Anyone can list "distributed systems." A link to a conference talk, an open-source project, or a technical blog post makes the difference between a maybe and a match.

### Skills: Quality Over Quantity

The sweet spot is 8-15 skills. Fewer than 8 and you miss matches. More than 20 and you dilute your signal -- the matching engine weights skill overlap, so irrelevant skills reduce your match score against focused job postings.

- Use industry-standard terms: "TypeScript" not "TS", "PostgreSQL" not "Postgres", "Amazon Web Services" or "AWS" (include both if space allows).
- Include both specific technologies ("React", "Kubernetes") and broader categories ("Frontend Architecture", "Site Reliability Engineering").
- Order matters for humans reading your profile. Lead with your strongest, most relevant skills.
- Drop anything you would not want to be interviewed on. If you touched Redis once in 2019, leave it out.

**Skill selection examples by role:**

| Role Type | Strong Skill Set (8-12) | Weak Skill Set |
|-----------|------------------------|----------------|
| Backend Engineer | TypeScript, Node.js, PostgreSQL, Redis, Kubernetes, AWS, REST APIs, Event-Driven Architecture, Observability | JavaScript, HTML, CSS, SQL, Linux, Git, Agile, Communication, Problem Solving, Docker, Python, Java, C++ |
| Frontend Engineer | React, TypeScript, Next.js, CSS-in-JS, Web Performance, Accessibility, Design Systems, GraphQL | HTML, CSS, JavaScript, jQuery, Bootstrap, WordPress, Photoshop, Figma, Git, npm |
| Data Engineer | Python, Apache Spark, dbt, Snowflake, Airflow, SQL, Data Modeling, AWS Glue, Kafka | Excel, SQL, Python, R, Tableau, PowerBI, Statistics, Machine Learning, AI, Data Science |

### Headline: Your Positioning Statement

Formula: **seniority + specialty + differentiator**.

- "Senior Backend Engineer | Distributed Systems | Ex-Stripe" -- clear, searchable, memorable.
- "Software Developer" -- says nothing. Matches everything poorly.
- "Passionate problem solver who loves building things" -- not searchable, not matchable.

**More examples:**

- "Staff Frontend Engineer | Design Systems | React + TypeScript" -- technical depth is clear
- "Engineering Manager | Platform Infrastructure | 40-person org, Series B-D" -- scope is obvious
- "ML Engineer | NLP & LLMs | Production systems at scale" -- timely and specific

Keep it under 256 characters. Every word should either help an employer agent match you or help a human remember you.

### Experience Summary: Lead With Scale

This is your 2-4 sentence pitch. Lead with the numbers that matter: team size, revenue impact, user counts, system scale.

**Good:**
> "Led a team of 8 engineers building payment infrastructure processing $2B annually. Reduced p99 latency from 400ms to 90ms. Migrated 12 services from monolith to event-driven architecture."

**Bad:**
> "Experienced software engineer with a passion for clean code and best practices."

Recruiters and employer agents scan for proof of impact. Give them numbers, not adjectives.

**More strong examples:**

> "Built and shipped the real-time analytics pipeline serving 50M daily events for a Series C fintech. Owned the data platform end-to-end: ingestion, transformation, and dashboards used by 200+ internal users."

> "Engineering manager leading 3 squads (18 engineers) across the checkout and payments domain. Grew the team from 6 to 18 over 14 months while shipping a new payment gateway that increased conversion by 12%."

---

## Field-by-Field Optimization

Each field in the CandidateSnapshot schema serves a specific matching function. Here is how to fill each one effectively.

### `display_name` (required, max 256 chars)

Your professional name as you want employers to see it. Use your real name -- this is not a username or handle.

- **Good:** "Alex Chen", "Maria Garcia-Lopez"
- **Bad:** "xXx_coder_xXx", "Alex C." (too abbreviated for professional context)
- **Common mistake:** Leaving it as a default or placeholder. This is the first thing employers see.

### `headline` (optional, max 256 chars)

Your one-line positioning statement. This appears in search results alongside your name. If you fill only one optional field, make it this one.

- **Matching role:** Employer agents use headline keywords as a secondary signal when skills alone produce too many results.
- **How to fill it:** Use the seniority + specialty + differentiator formula above.
- **Common mistake:** Copying your current job title verbatim. "Software Engineer II at Acme Corp" is a job title, not a positioning statement.

### `skills` (optional, max 50 items)

The primary matching field. Employer agents filter and rank candidates by skill overlap with their job requirements.

- **Matching role:** Direct intersection with job posting `requirements`. More overlap = higher match score.
- **How to fill it:** 8-15 skills. Industry-standard terms. Mix of specific tools and broader competencies.
- **Common mistake:** Listing 40 skills including "Microsoft Office" and "Agile." Dilutes your technical signal and reduces match quality against focused postings.

### `experience_years` (optional, number)

Total years of professional experience. Used for seniority filtering -- many job postings specify a range.

- **Matching role:** Hard filter. A posting requiring "5+ years" will exclude you at 4.
- **How to fill it:** Count from your first professional role (not internships, unless they were substantial). Round to the nearest whole number.
- **Common mistake:** Understating to seem humble, or inflating by counting college projects. Be accurate -- employer agents compare this against posting requirements.

### `experience_summary` (optional, max 4000 chars)

Your professional narrative. This is the field where you tell your career story with concrete evidence.

- **Matching role:** Used for semantic matching and shown to employers evaluating candidates. High-quality summaries improve match reasoning.
- **How to fill it:** 2-4 sentences. Lead with scale and impact. Include specific metrics (team size, user counts, revenue, performance improvements). Mention the domain if it is relevant (fintech, healthcare, developer tools).
- **Common mistake:** Writing a generic paragraph about "passion for technology." Employer agents cannot match on passion. They match on evidence of impact at scale.

### `preferred_roles` (optional, max 50 items)

The job titles you are targeting. This is how you tell the matching engine what you actually want.

- **Matching role:** Matched against job posting `title`. Strong overlap boosts your ranking.
- **How to fill it:** 2-5 titles that represent your target. Include variations: "Staff Engineer", "Staff Software Engineer", "Tech Lead". Cast a reasonable net.
- **Common mistake:** Leaving this empty and expecting skills alone to find the right roles. A backend engineer who wants to move into engineering management needs to say so.

### `preferred_locations` (optional, max 50 items)

Where you are willing to work, expressed as city/region strings.

- **Matching role:** Matched against job posting `location`. Also used as a tiebreaker when multiple candidates match on skills.
- **How to fill it:** Use standard city/state or city/country format: "San Francisco, CA", "London, UK", "Berlin, Germany". Include all locations you would genuinely consider.
- **Common mistake:** Listing only your current city when you are open to relocating. If you would move for the right role, say so. Also: do not fill this if you are strictly remote -- use `remote_preference` instead.

### `salary_range` (optional, object: `{min, max, currency}`)

Your compensation expectations. Values are numeric (annual), currency is a 3-letter ISO code (e.g., "USD", "EUR", "GBP").

- **Matching role:** Compared against job posting `comp_range`. Mismatched ranges can suppress otherwise strong matches.
- **How to fill it:** Set a realistic range based on your market research. The `min` should be your true floor -- do not low-ball to increase matches, because you will waste time on roles that underpay. The `max` should be aspirational but credible.
- **Common mistake:** Omitting this field out of discomfort. Leaving it empty means you match everything, including roles paying 40% below your expectation. A range protects your time.

**Setting a good range:**

| Scenario | Approach |
|----------|----------|
| You know your market rate | Set min at 90% of market, max at 120% |
| You are unsure | Research on levels.fyi, Glassdoor, or Blind first; then set a range |
| You are transitioning careers | Set min at your true floor, max at your previous comp |
| You are in a low-CoL area targeting remote | Use the employer's market rate, not your local rate |

### `remote_preference` (optional, enum)

Your work location flexibility. Values: `"remote_only"`, `"remote_ok"`, `"hybrid"`, `"onsite_required"`.

- **Matching role:** Hard filter. If you set `"remote_only"` and a job is `"onsite_required"`, you will not match.
- **How to fill it:** Be honest about what you will accept. `"remote_ok"` is the most flexible -- it matches remote, hybrid, and some onsite postings.
- **Common mistake:** Setting `"remote_only"` when you would actually consider hybrid for the right company. This is a filter, not a preference ranking -- it eliminates entire categories of results.

### `availability` (optional, enum)

Your job search status. Values: `"active"`, `"passive"`, `"not_looking"`.

- **Matching role:** Employer agents prioritize `"active"` candidates. `"passive"` still appears in results but ranks lower. `"not_looking"` suppresses you from most searches.
- **How to fill it:** `"active"` = you are job searching now. `"passive"` = you would consider the right opportunity but are not urgently looking. `"not_looking"` = do not contact me.
- **Common mistake:** Leaving this unset. Without an explicit signal, the matching engine cannot prioritize you appropriately. If you are actively searching, say so -- it matters.

### `evidence_urls` (optional, max 50 URLs)

Links to work that backs up your profile: GitHub repos, portfolio sites, published articles, conference talks, open-source contributions.

- **Matching role:** Not used for automated matching, but shown to employer agents evaluating candidates. Strong evidence URLs significantly increase employer response rates.
- **How to fill it:** 2-5 high-quality links. Your GitHub profile, a standout project, a blog post that demonstrates expertise, a talk recording. Quality over quantity.
- **Common mistake:** Linking a GitHub profile with no pinned repos or recent activity. An empty GitHub is worse than no GitHub. Only link what you are proud of.

---

## Profile Anti-Patterns

These are the most common ways profiles fail. If any of these describe your current profile, fix them before searching.

**The Empty Profile.** Only `display_name` is set. The matching engine has nothing to work with. You will get zero results, not bad results -- the system literally cannot match you. Fill at minimum: `skills`, `experience_years`, and `preferred_roles`.

**The Kitchen Sink.** 40 skills including "Microsoft Word", "Agile", "Communication", and "Problem Solving." This buries your real technical signal. Employer agents searching for "Kubernetes" will rank you lower because your skill density is diluted. Cut to 8-15 of your strongest technical skills.

**The Humble Undersell.** "3 years experience" when you have 7 because you do not count your first roles. "A few projects in React" when you built the entire frontend for a Series B startup. Employer agents take your profile at face value. State your experience accurately and completely.

**The Stale Profile.** You built your profile 6 months ago and have not touched it since. You have learned new skills, shifted your preferences, or changed your target role. Stale profiles produce stale matches. Review and update at least quarterly.

**The LinkedIn Copy-Paste.** You dumped your LinkedIn headline and summary verbatim. LinkedIn profiles are optimized for human readers and social algorithms. Your profile here is optimized for agent-to-agent matching. They need different content: more structured, more specific, more skill-dense.

**The Aspirational Profile.** You listed skills you are learning but have not used professionally. You set your target level one notch above where you actually perform. Aspirational profiles get you into conversations you cannot close. Be accurate now; update when the skills are real.

### Anti-Pattern Checklist

Before your first search, verify:

- [ ] At least 8 skills listed, all industry-standard terms
- [ ] Headline follows seniority + specialty + differentiator formula
- [ ] Experience summary leads with numbers, not adjectives
- [ ] `experience_years` is accurate (not inflated or deflated)
- [ ] `preferred_roles` lists 2-5 target titles
- [ ] `salary_range` is set with a realistic floor
- [ ] `availability` is explicitly set
- [ ] `remote_preference` reflects what you will actually accept

---

## Resume to Profile Transformation

When converting a resume into a CandidateSnapshot, not everything maps directly. Here is how to handle the translation.

### Extract Directly

These fields can be pulled straight from the resume with minimal transformation:

- **`skills`** -- Gather from the skills section, plus technologies mentioned in experience bullets. Deduplicate and standardize naming.
- **`experience_years`** -- Calculate from the earliest start date to the most recent end date (or present). Round to the nearest whole number.
- **`display_name`** -- The name at the top of the resume.
- **`evidence_urls`** -- Pull from any links section (GitHub, portfolio, LinkedIn).

### Transform

These fields require synthesizing resume content into a different format:

- **`experience_summary`** -- Do not concatenate resume bullets. Instead, write a 2-4 sentence narrative that captures the arc: what domains, what scale, what impact. Pull the most impressive metrics from across all roles.
- **`headline`** -- Build from the most recent role title + primary domain + strongest differentiator. The resume might not have a headline -- construct one.
- **`skills`** -- The resume may list 30+ technologies across multiple roles. Curate to the 8-15 most relevant to the user's current goals, not just everything they have ever touched.

### Ask the User

Never assume these fields from a resume alone -- always confirm with the user:

- **`salary_range`** -- Resumes never include this. Ask what compensation range the user is targeting.
- **`remote_preference`** -- The resume does not indicate this. Ask what work arrangement the user prefers.
- **`preferred_roles`** -- The resume shows what someone has done, not what they want next. Ask what roles they are targeting. A backend engineer may want to move into DevOps or engineering management.
- **`preferred_locations`** -- Current location on the resume is not the same as willingness to relocate. Ask.
- **`availability`** -- Ask if they are actively searching, passively open, or just exploring.

### Transformation Example

**Resume input (abbreviated):**

> **Jane Park** -- jane@example.com -- github.com/janepark
>
> Senior Software Engineer, Acme Corp (2021-present)
> - Led migration of 8 microservices from REST to gRPC, reducing inter-service latency by 60%
> - Built real-time fraud detection pipeline processing 500K events/sec
>
> Software Engineer, StartupXYZ (2018-2021)
> - Full-stack development: React, Node.js, PostgreSQL
> - Scaled API from 1K to 50K RPM
>
> Skills: TypeScript, Python, Go, React, Node.js, PostgreSQL, Redis, Kafka, Kubernetes, AWS, gRPC, Docker, Git

**Resulting profile:**

```json
{
  "display_name": "Jane Park",
  "headline": "Senior Backend Engineer | Real-Time Systems & Microservices | Production Scale",
  "skills": ["TypeScript", "Go", "Python", "Node.js", "PostgreSQL", "Redis", "Kafka", "Kubernetes", "AWS", "gRPC"],
  "experience_years": 8,
  "experience_summary": "Backend engineer with 8 years building high-throughput distributed systems. Most recently led the migration of 8 microservices to gRPC at Acme Corp, cutting inter-service latency by 60%. Built a real-time fraud detection pipeline processing 500K events/sec. Scaled APIs from 1K to 50K RPM at a Series A startup.",
  "evidence_urls": ["https://github.com/janepark"],
  "preferred_roles": "--- ASK USER ---",
  "salary_range": "--- ASK USER ---",
  "remote_preference": "--- ASK USER ---",
  "preferred_locations": "--- ASK USER ---",
  "availability": "--- ASK USER ---"
}
```

---

## Iterating on Your Profile

A profile is not a one-time setup. It is a living document that should evolve with your search.

**After poor search results:** If searches return few or irrelevant matches, your profile is likely too narrow or misaligned. Review `skills` and `preferred_roles` -- are they matching what is actually being posted? Add adjacent skills or broaden your role targets.

**After every 10 searches:** Take stock. Are you seeing the same postings repeatedly? Your profile may be too static. Look at jobs you liked but did not match on -- what skills or role titles did they require that your profile is missing? Add them if they are genuine.

**When career goals change:** New target role, new location, new compensation expectations -- update immediately. A stale `preferred_roles` field sends you matches for a job you no longer want.

**Skills from job postings:** When you see a posting that excites you but you did not match on, check its requirements. If you genuinely have those skills but did not list them, add them to your profile. This is how you close the vocabulary gap between how you describe yourself and how employers describe the role.

**Seasonal awareness:** Hiring volume is not flat across the year. The strongest hiring periods are January through March (new budgets, new headcount) and September through October (post-summer push to fill before year-end). Set your `availability` to `"active"` during these windows if you are serious about moving. During slower months (late November through December, mid-summer), `"passive"` is fine unless you are urgently searching.

### Profile Review Cadence

| Search Mode | Review Frequency | Focus Areas |
|-------------|-----------------|-------------|
| Active | Weekly | Skills alignment with search results, application feedback |
| Passive | Monthly | Keep skills current, update preferred roles if interests shift |
| Not looking | Quarterly | Ensure profile reflects current capabilities for inbound |
