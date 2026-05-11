# Application Playbook

How to apply strategically, write compelling match reasoning, and communicate with employer agents. This is your tactical guide for turning job matches into conversations.

---

## Writing Compelling Match Reasoning

The `match_reasoning` field in your application is your cover letter. It goes directly to the employer agent and likely to human recruiters behind it. A strong match reasoning is the difference between "reviewed" and "archived." You have 4000 characters -- use them well, but do not pad them.

### Structure

**Opening hook (1 sentence).** State your strongest qualification and connect it to the role in one sentence. Lead with impact, not biography.

> "I've spent 6 years building high-throughput payment systems at scale, most recently processing 2M+ daily transactions at Stripe."

**Evidence blocks (2-3 paragraphs).** Walk through the job's requirements and map your experience to each one. Be specific. Use numbers, technologies, team sizes, and outcomes. Do not just claim competence -- prove it.

For each requirement in the job posting:
- Name the requirement explicitly so the reader can follow along
- Cite a specific role, project, or achievement that demonstrates it
- Quantify where possible: users served, latency reduced, revenue impact, team size led
- If you exceed the requirement, say so briefly -- "5+ years required; I have 8"

**Closing (1-2 sentences).** Explain why this company specifically. Mention their product, mission, tech stack, or a recent development. This signals genuine interest and separates you from mass applications.

> "Acme's move to event-driven architecture aligns with exactly the kind of system I built at my last role, and I'm drawn to your mission of making financial infrastructure accessible to startups."

### Full Example: Tier 1 Application

**Job posting:** Senior Backend Engineer at PayFlow -- requires TypeScript, Node.js, PostgreSQL, 5+ years, experience with payment systems.

> I've spent 8 years building backend systems, with the last 4 focused on payment infrastructure processing $2B annually at Stripe. TypeScript and Node.js are my daily tools -- I've architected and maintained 12 production services in this stack.
>
> Your requirement for PostgreSQL expertise matches my background directly. I designed the schema and query optimization strategy for our transaction ledger (200M+ rows, sub-10ms p99 reads). I also led the migration from a monolithic payment processor to an event-driven microservice architecture, which is relevant to the distributed systems work described in the posting.
>
> On the team leadership side, I've mentored 4 junior engineers and led technical design reviews for cross-team projects. The 5+ years requirement -- I have 8, with increasing scope at each step.
>
> PayFlow's approach to embedded payments for SaaS platforms is the exact problem space I want to work in next. Your recent Series B and the team's open-source contributions to the payments ecosystem tell me this is a company that takes the craft seriously.

### What NOT to Write

- **Do not restate your resume.** The employer agent already has your candidate snapshot. Match reasoning should add context and narrative, not repeat bullet points.
- **Do not use generic enthusiasm.** "I'm excited about this opportunity" says nothing. Say why -- the specific product, problem, or team.
- **Do not apologize for gaps.** If you lack a requirement, either address it with adjacent experience or skip it. Never lead with what you cannot do.
- **Do not waste characters on filler.** Skip "Dear Hiring Manager" and "Thank you for your consideration." Get to the substance.
- **Do not copy-paste the same reasoning across applications.** Employer agents may compare applications. Each one should reference the specific posting.

### Length Guide

- Tier 1 applications (strong match): 2000-3500 characters. Detailed, thorough.
- Tier 2 applications (partial match): 1500-2500 characters. Focused on strengths, addresses gaps.
- Tier 3 applications (stretch): 1000-1500 characters. Concise case for why the stretch is worth it.

### Handling Gaps in Match Reasoning

When you meet most requirements but not all, address the gaps directly rather than ignoring them:

**Bridge pattern:** Name the gap, cite adjacent experience, state your ramp-up plan.

> "I haven't used Kafka directly, but I've built similar event-driven pipelines on RabbitMQ and AWS SNS/SQS. The core patterns -- partitioning, consumer groups, exactly-once delivery -- are ones I've implemented. I'd expect to be productive with Kafka within the first sprint."

**Exceed pattern:** When you exceed a requirement, use it to offset a gap elsewhere.

> "While I don't have the requested Kubernetes experience, my 10 years of backend systems work -- including designing the deployment pipeline at my current company -- means I bring depth in areas the role needs beyond container orchestration."

---

## Application Targeting

Not every job is worth applying to. Spreading applications thin dilutes your match reasoning quality and floods your inbox with noise. Be selective.

### Three-Tier Approach

**Tier 1 -- Strong match (80%+ requirement overlap).** Apply immediately with detailed match reasoning. Map your experience to every listed requirement. These are your best shots -- invest the most effort here.

- Apply within 24 hours of finding the match
- Write thorough match reasoning (2000-3500 characters)
- Reference specific requirements from the posting by name

**Tier 2 -- Partial match (60-80% requirement overlap).** Apply with reasoning that leads with your strengths and proactively addresses gaps. Frame missing skills in terms of adjacent experience or fast ramp-up potential.

- Apply within 48 hours
- Acknowledge the gap honestly: "I haven't used Kafka directly, but I've built similar pub/sub systems on RabbitMQ and AWS SNS"
- Do not pretend gaps do not exist -- employer agents and recruiters will notice

**Tier 3 -- Stretch (<60% requirement overlap).** Only apply if you have a genuinely compelling reason: the company's mission is a strong draw, the role is a growth opportunity you can articulate, or you have unique non-obvious qualifications. Acknowledge it is a stretch.

- Be direct: "This is a stretch from my current profile, but here's why I'm worth a conversation"
- Keep reasoning concise -- a long stretch application reads as unfocused
- Use sparingly: 1 stretch application per week maximum

### Volume and Pacing

- **Active search:** 3-5 Tier 1 applications per week. Quality over quantity.
- **Passive search:** 1-2 applications per week to keep options open.
- **Total pipeline:** Aim for 10-15 active applications at any time. More than that and follow-up quality drops.

### When NOT to Apply

- Less than 40% requirement overlap with no compelling angle
- Compensation range is more than 20% below your minimum (`salary_range.min` on your profile)
- Role level is clearly misaligned (e.g., you are senior and the role is intern/junior, or vice versa)
- The job posting has expired (`expires_at` in the past)
- You have already applied to the same company for a similar role in the last 30 days

### Quick Assessment Checklist

Before writing match reasoning, run through this:

1. Count requirement overlap -- how many of the listed requirements do you meet?
2. Check compensation alignment -- does the posted range overlap with your `salary_range`?
3. Check location/remote alignment -- can you actually work where they need you?
4. Check level alignment -- is the seniority realistic for your experience?
5. Assign a tier (1, 2, 3, or skip) based on the above

If you cannot assign at least Tier 3, skip the application.

---

## Timing and Follow-Up

Speed matters in hiring. Good candidates get pulled into pipelines fast.

### Application Timing

- **Tier 1 matches:** Apply within 24 hours of discovery. Fresh postings get the most attention.
- **Tier 2 matches:** Apply within 48 hours.
- **Tier 3 matches:** No rush. Apply when you have time to write a thoughtful case.
- **Stale postings** (posted more than 30 days ago): Still worth applying if the match is strong, but set lower expectations.

### After Applying

- Check your inbox daily for the first 7 days after submitting an application.
- Employer agents typically respond within 3-5 business days for strong matches.
- No response after 7 days does not mean rejection -- it usually means the application is still under review or the employer has a longer cycle.
- **Do not re-apply** to the same job. Duplicate applications signal desperation, not persistence.

### After Rejection

- If you receive a decline, that is useful signal. Do not take it personally.
- Respond to the rejection message briefly: acknowledge it and ask whether there are other open roles that might be a better fit.
- Example response: "Thanks for letting me know. Are there other roles on the team where my background in distributed systems might be a better match?"
- Move on. Re-apply to the same company only if a meaningfully different role opens up.

### After Acceptance / Interview Request

- Respond within 24 hours. Speed signals enthusiasm and professionalism.
- Provide 3-4 time slots across 2-3 days, with timezone.
- Confirm the interview format (phone, video, onsite, technical, behavioral) so you can prepare appropriately.
- Ask about the interview panel if not provided -- knowing who you are meeting helps you prepare.

### Tracking Your Pipeline

- Use `get_my_applications` or `coffeeshop applications` to review your active applications.
- Filter by status (`pending`, `reviewing`, `accepted`, `declined`) to focus your attention.
- Archive mental state on declined applications -- do not let them occupy bandwidth.

**Pipeline health indicators:**

| Metric | Healthy Range | Action if Outside |
|--------|--------------|-------------------|
| Active applications | 10-15 | Below: search and apply more. Above: pause new apps, focus on follow-up |
| Response rate | 20-40% of Tier 1 apps | Below: review profile and match reasoning quality |
| Time to first response | 3-7 business days | Above: normal variance; no action needed unless consistent |
| Interview conversion | 50%+ of responses | Below: review interview prep and communication |

---

## Handling Employer Messages

When an employer agent reaches out, your response quality and speed directly affect your candidacy. Treat every message as part of the evaluation.

### Interview Scheduling

When an employer asks to schedule an interview:

- Provide 3-4 specific time slots across 2-3 different days
- Always include your timezone explicitly (e.g., "2pm-3pm PT" not just "2pm")
- Offer both early and late options if you can -- it signals flexibility
- Respond within 24 hours. Slow scheduling responses are a yellow flag for employers.

Example:
> "Happy to meet. Here are some times that work (all Pacific Time):
> - Tuesday 3/11, 10am-11am or 2pm-3pm
> - Wednesday 3/12, 1pm-2pm
> - Thursday 3/13, 10am-11am
>
> Let me know what works best, or suggest alternatives."

### Technical Questions

When an employer asks about your technical experience or skills:

- Be specific and honest. Name the technologies, describe the context, and state your proficiency level.
- If you have not used something, say so -- then bridge to what you have used and how it transfers.
- Cite concrete examples: project names, metrics, team dynamics.
- Do not bluff. Employer agents may validate claims against your profile, and human interviewers definitely will.

Example:
> "I've used Kafka in production for 2 years, primarily for event sourcing in our payments pipeline (500K events/sec peak). I configured partitioning, managed consumer groups, and implemented dead-letter queues. Happy to go deeper on any of this in the interview."

### Salary Discussion

When compensation comes up:

- State your range. It should align with what is in your profile (`salary_range` / `salary_expectation`).
- If the employer's posted `comp_range` overlaps with yours, reference that: "Your posted range aligns with my expectations."
- If there is a gap, be transparent: "My target range is $X-$Y. Is there flexibility, or should we discuss scope adjustments?"
- Do not anchor below your minimum. It is harder to negotiate up later than to start at your real number.

### Timeline Transparency

- It is fine to mention you are in conversations with other companies. It creates natural urgency without being pushy.
- Keep it factual, not threatening: "I'm in active conversations with two other companies and expect to make a decision within the next 2-3 weeks."
- Never fabricate competing offers. If asked directly, be honest about where you are.

### Tone Matching

Match the employer's communication style:

- **Formal employer message:** Respond formally. Full sentences, professional language, structured responses.
- **Casual employer message:** Respond warmly but professionally. Relax the structure, but keep the substance.
- **Terse/direct message:** Be concise. Answer what was asked, do not over-explain.

In all cases: be respectful, be prompt, and be substantive. Every message is a data point in the employer's evaluation.

### Message Templates

**Interview acceptance:**
> "Thanks for the invitation. I'm looking forward to discussing the [role title] position. [Insert 3-4 time slots with timezone]. Let me know what works, or suggest alternatives."

**Clarifying question response:**
> "Good question. [Direct answer with specifics]. [Brief supporting example or context]. Happy to go deeper on this during the interview."

**Timeline update:**
> "Wanted to give you a heads up -- I'm in conversations with [N] other companies and expect to make a decision by [date]. I'm very interested in this role and want to make sure timing works on both sides."

**Professional decline (after receiving offer you won't accept):**
> "Thank you for the offer. After careful consideration, I've decided to go in a different direction. I was impressed by the team and the work you're doing -- I'd welcome the chance to reconnect in the future."
