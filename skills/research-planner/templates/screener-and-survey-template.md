# Recruitment Screener and Survey Template

Use this template to design:

- A **recruitment screener** for qualitative or usability sessions
- A **short survey** that may be used standalone or alongside qualitative work

Fill in all `[...]` placeholders with study‑specific content.

---

## Part A – Recruitment Screener

### A.1 Header (internal)

```markdown
Study title: [...]
Version: v[...]
Date: [...]
Owner: [...]
Target audience: [...]
Recruitment channel(s): [...]
```

---

### A.2 Introduction (participant‑facing)

Use clear, concise language.

```markdown
We’re conducting a short screening questionnaire to find people who are a good fit for a research study about [...]. Your answers will help us determine whether this study is relevant for you.

The screener should take about [X] minutes. Your responses will be kept confidential and used only for research recruiting.
```

---

### A.3 Eligibility and Disqualification Questions

Align these with the **inclusion / exclusion criteria** from the research plan.

For each key criterion:

```markdown
Q1. Which of the following best describes your role? (Select one)
- [ ] [...]
- [ ] [...]
- [ ] [...]
- [ ] None of the above  *(disqualify)*

Recruitment logic:
- **Include** if respondent selects: [...]
- **Exclude** if respondent selects: "None of the above"
```

Add further questions as needed, for example:

- Usage frequency (e.g., “How often do you [do activity]?”)
- Product familiarity (e.g., current users vs. non‑users)
- Industry / company size (for B2B)

Clearly mark disqualifying options.

---

### A.4 Demographic / Firmographic Questions (as needed)

Include only what is necessary for quotas or analysis.

```markdown
QX. Which of the following best describes your organization’s size?
- [ ] 1–10 employees
- [ ] 11–50 employees
- [ ] 51–250 employees
- [ ] 251–1,000 employees
- [ ] 1,001+ employees

QY. In which country do you currently live?
[Open text or country dropdown]
```

Document any quota rules:

```markdown
Quota plan:
- Aim for: [e.g., 50% small orgs, 50% large orgs]
- At least [N] participants from [region / segment]
```

---

### A.5 Screener Summary and Selection Rules

Summarize how to decide whether a respondent qualifies:

```markdown
Qualification rules:
- Must meet: [list key criteria]
- Must not: [list disqualifiers]

Notes for recruiters:
- Prioritize respondents who: [...]
- Avoid recruiting: [...]
```

---

## Part B – Survey Questionnaire

If the study includes a survey, use this section to define **survey items and scales**.

### B.1 Survey Overview

```markdown
Survey goal: [...]
Target population: [...]
Estimated length: [...] minutes
Distribution channel: [...]
```

---

### B.2 Sections and Question Types

Organize the survey into sections aligned to constructs (e.g., usage, satisfaction, attitudes).

#### Section 1 – Usage and Behavior

```markdown
Q1. In the past [time period], how often have you [done activity]?
- [ ] Never
- [ ] Less than once a month
- [ ] 1–3 times a month
- [ ] 1–2 times a week
- [ ] 3+ times a week

Q2. Which tools or services do you currently use to [achieve goal]? (Select all that apply)
- [ ] Tool A
- [ ] Tool B
- [ ] Tool C
- [ ] Other (please specify): ________
```

#### Section 2 – Satisfaction and Experience

```markdown
Q3. Overall, how satisfied are you with how you currently [do activity]?
(5‑point Likert scale)
- [ ] Very dissatisfied
- [ ] Dissatisfied
- [ ] Neither satisfied nor dissatisfied
- [ ] Satisfied
- [ ] Very satisfied

Q4. How strongly do you agree or disagree with the following statement?
"[Statement about ease, trust, usefulness, etc.]"
(5‑point agreement scale)
- [ ] Strongly disagree
- [ ] Disagree
- [ ] Neither agree nor disagree
- [ ] Agree
- [ ] Strongly agree
```

#### Section 3 – Concept / Feature Interest (optional)

```markdown
Q5. How interested would you be in using a solution that helps you [value proposition]?
(5‑point interest scale)
- [ ] Not at all interested
- [ ] Slightly interested
- [ ] Moderately interested
- [ ] Very interested
- [ ] Extremely interested

Q6. (Optional open‑ended)
What, if anything, would make you more likely to use such a solution?
[Open text]
```

---

### B.3 Skip Logic and Flow (If Applicable)

Describe any branching logic in plain language.

```markdown
Skip logic:
- If Q1 = "Never", skip to Q5 and show concept questions only.
- If Q2 includes "Tool A", show additional questions about Tool A.
```

---

### B.4 Closing and Thank You

Provide closing text that participants will see after submitting.

```markdown
Thank you for completing this survey. Your responses will help us better understand how people [do activity] and how we can improve our products and services.
```

