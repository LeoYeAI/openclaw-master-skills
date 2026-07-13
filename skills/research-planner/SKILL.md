---
name: research-planner
description: >
  Designs market and user research plans focused on methodology selection and research material authoring (screeners, surveys, interview guides, usability task scripts, etc.). Use this skill whenever the user wants to plan or structure research activities, choose between qualitative and quantitative methods, or draft research artifacts, but not to analyze collected data.
---

# Installation
**Via Clawdhub:**
```bash
clawdhub install research-planner
```
**Manual Installation:**
```bash
npx skills add https://github.com/NKZ55/research-planner/tree/main/skills/research-planner
```

# Research Planner

Market and user research planning skill focused on **research design and documentation**, not on data analysis.

This skill is inspired by systematic frameworks from:

- **User/UX research books**
  - Erika Hall, *Just Enough Research* (research strategy, scoping, stakeholder alignment)
  - Steve Portigal, *Interviewing Users* (study design and interview materials)
  - C. J. Hoefflich & Jeff Sauro, *Quantifying the User Experience* (quantitative UX measures and study design – used here for planning, not analysis)
- **Market research and consulting**
  - Naresh Malhotra, *Marketing Research* (problem definition → research design → data collection plan)
  - McKinsey-style **hypothesis-driven, MECE research framing** (issue trees, key questions, assumptions)
- **Online frameworks**
  - Nielsen Norman Group research-planning guidance ([research plans](https://www.nngroup.com/articles/pm-research-plan/), [research methods overview](https://www.nngroup.com/articles/guide-ux-research-methods/))
  - Practice-oriented UX research strategy guides such as [The Ultimate Guide to Research Strategy](https://www.userinterviews.com/blog/the-ultimate-guide-to-ux-research-strategy)

This skill helps the agent:
- Select appropriate research methods given the user's goal, constraints, and audience
- Turn a chosen method into concrete research artifacts (screeners, questionnaires, discussion guides, task lists, etc.)
- Structure research projects into clear phases and deliverables

Data analysis (qualitative coding, statistical analysis, report writing) is **explicitly out of scope** and should be delegated to analysis-focused skills (for example, interview-analysis skills such as [Interview Analyst](https://github.com/nealcaren/social-data-analysis/tree/main/plugins/interview-analyst/skills/interview-analyst)).

## Scope

- **In scope**
  - Clarifying research objectives and hypotheses
  - Choosing suitable research methods (e.g., in-depth interviews, usability tests, surveys, diary studies, field research, concept tests)
  - Designing multi-method research plans (mixed methods)
  - Drafting all research materials needed to run the study:
    - Recruitment screeners and eligibility criteria
    - Participant invitation text and consent wording
    - Interview and discussion guides
    - Usability test task scripts and success criteria
    - Survey questionnaires and question wording
    - Moderator notes and observation templates
  - Structuring timelines, milestones, and required roles for execution

- **Out of scope**
  - Cleaning, transforming, or aggregating collected data
  - Coding qualitative data or running statistical tests
  - Creating insights decks, final research reports, or recommendations
  - Any task that belongs to the separate analysis/reporting skills

## Phase Model

Use this phase model for every project. This skill covers only the **planning and documentation** phases.

```text
Problem framing
   ↓
Research strategy & method selection
   ↓
Study plan & logistics
   ↓
Research materials (screeners, guides, surveys, scripts)
   ↓
Fieldwork / data collection  [OUT OF SCOPE]
   ↓
Analysis & reporting         [OUT OF SCOPE – use analysis skills]
```

## How to Use This Skill

For each user request:

1. **Clarify the research need**
2. **Choose appropriate research approach(es)**
3. **Turn the approach into a concrete study plan**
4. **Generate the necessary research materials**
5. **Package everything into an execution-ready bundle**

Always keep analysis out of scope and gently point users to analysis skills once data is collected.

---

## Step 1: Clarify the Research Need

Before suggesting methods, derive a clear, consulting-style problem framing.

- **Clarify business and research goals**
  - What decision will this research inform?
  - What would success look like for stakeholders?
  - What hypotheses or assumptions are we testing?
- **Define target users and context**
  - Which segment(s), roles, geographies, or usage patterns matter?
  - In what context does the behavior occur (device, channel, environment)?
- **Map constraints**
  - Timeframe, budget, required sample size or coverage
  - Access to participants (existing users, prospects, internal staff)

Output for this step:

- A short **Problem Statement**
- 3–7 **Key Questions** (MECE where possible)
- A list of **Assumptions / Hypotheses** to probe

---

## Step 2: Choose Research Approach(es)

Use a small set of canonical user and market research methods. Combine methods when appropriate (mixed methods).

### Method-Selection Matrix

| Primary goal                           | Typical method(s)                                       | Notes |
|----------------------------------------|---------------------------------------------------------|-------|
| Explore unknown problem space          | 1:1 in-depth interviews, contextual inquiry, diary     | Discovery / generative research |
| Evaluate usability of an experience    | Moderated usability tests, unmoderated remote tests    | Task-based, scenario-driven |
| Measure attitudes or behaviors at scale| Structured survey, poll, simple experiment             | Requires clear constructs and metrics |
| Compare concepts or ideas              | Concept testing sessions, preference tests, card sorts | May combine with interview or survey |
| Understand real-world context          | Field visits, observation, shadowing, diary study      | Higher logistics cost |

Method choice should balance:

- **Stage** (discovery vs validation vs evaluation)
- **Decision type** (go/no-go, prioritization, design iteration, positioning)
- **Practical constraints** (timeline, recruiting, tools already in use)

When recommending methods:

- Propose **1–2 primary methods** plus any lightweight secondary methods
- Briefly justify each method in terms of the user’s goals and constraints

---

## Step 3: Turn the Approach into a Study Plan

Following both classic marketing-research texts and NN/g research-plan guidance, every study plan should cover at least:

- **Background & Objectives**
  - Context, problem statement, business goals
  - Research objectives and key questions
- **Methodology Overview**
  - Chosen methods and rationale
  - Study type (exploratory, descriptive, causal; formative vs summative)
- **Participants**
  - Target population and segments
  - Inclusion / exclusion criteria
  - Planned sample size and justification
- **Procedure**
  - Study phases (pilot, main fieldwork)
  - Session format (remote vs in-person, moderated vs unmoderated)
  - High-level flow or timeline
- **Roles and Responsibilities**
  - Researcher, moderator, note-taker, stakeholders
- **Risks and Ethical Considerations**
  - Consent, privacy, incentives, sensitive topics

When the user asks for a plan, structure your answer in these sections and keep wording concise enough that it can be copy-pasted into a research plan document.

---

## Step 4: Generate Research Materials

For each chosen method, generate concrete artifacts. Keep templates modular so they can be reused across projects.

### 4.1 Recruitment Screener

Structure:

- Study title and short purpose (participant-facing)
- Eligibility questions
  - Must-have criteria (knock-out logic)
  - Nice-to-have criteria (for quota balancing)
- Disqualification rules (e.g., professional researchers, competitors)
- Demographic / firmographic questions only as necessary

Make the screener:

- Simple enough for non-researchers to administer
- Explicit about inclusion/exclusion logic

### 4.2 Participant Invitation & Consent Wording

Include:

- Plain-language description of the study’s purpose
- What participation involves (time, activities, recording)
- Incentive and payment process
- Privacy and confidentiality statement
- Contact for questions or withdrawal

Ensure consent text is **non-legalistic** but clear; defer to the user’s legal or compliance team for final approval.

### 4.3 Interview / Discussion Guide

For qualitative interviews, base structure on best practices from interview-focused texts:

- Introduction and warm-up
- Core sections aligned to key questions or themes
- Probing prompts and follow-ups (avoid leading questions)
- Wrap-up, closing questions, and thanks

Organize the guide as:

- Section headings (themes)
- Bullet-point questions and probes
- Optional timing guidance per section

### 4.4 Usability Test Script

Components:

- Study intro (purpose, disclaimers, think-aloud instructions)
- Task list
  - Realistic scenarios framed in user language
  - Clear success criteria per task
  - Space for observers to note observations
- Closing questions (short interview or satisfaction questions)

Include simple **moderator cues** (what to read verbatim, when to stay silent, when to probe).

### 4.5 Survey Questionnaire

When planning surveys, follow quantitative UX and survey-design guidance:

- Map each **construct** (e.g., satisfaction, trust, task success) to specific items
- Prefer simple, unambiguous wording
- Choose scale types consistently (e.g., 5- or 7-point Likert, yes/no, NPS)
- Keep survey as short as possible while still answering key questions

Output:

- Ordered list of questions
- Response options and scale labels
- Any skip logic or branching described in plain language

---

## Step 5: Package an Execution-Ready Output

Default response format for this skill:

```markdown
# Research Plan Overview

## 1. Background & Objectives
[Problem statement, context, objectives]

## 2. Research Approach
- Primary method(s): [...]
- Secondary method(s): [...]
- Rationale: [...]

## 3. Participants
- Target: [...]
- Inclusion / exclusion: [...]
- Sample size and rationale: [...]

## 4. Procedure & Timeline
[Study phases, session format, key milestones]

## 5. Risks & Ethics
[Key ethical considerations, data handling notes]

## 6. Research Materials
- Recruitment screener
- Invitation & consent text
- Interview / test script / survey questions
```

Populate each section with concrete, copy-paste-ready content tailored to the user’s situation.

---

## Phases Overview

For more detailed step-by-step guidance, this skill includes phase files under `phases/`:

- `phases/01-clarify-need.md`
  - Use when you need to deeply clarify the **research need**, decisions, target users, and constraints.
  - Expands **Step 1** into a full workflow for:
    - Business context and decisions.
    - Research objectives and key questions.
    - Target users and context.
    - Constraints and a one-page Phase 1 summary.

- `phases/02-method-selection-and-plan.md`
  - Use when moving from clarified need to **method selection and a full research plan**.
  - Expands **Steps 2–3** into:
    - Mapping objectives to research types (exploratory, descriptive, evaluative, causal).
    - Selecting single or mixed methods.
    - Drafting a structured research plan (background, methodology, participants, procedure, risks).

- `phases/03-materials-and-logistics.md`
  - Use when turning the approved plan into **research materials and an operational schedule**.
  - Expands **Steps 4–5** into:
    - Mapping plan components to required artifacts (screener, guide, script, survey, etc.).
    - Drafting and refining materials using the templates.
    - Creating timelines, roles, and operational checklists.

When a user task is complex (e.g., multi-method study, multiple stakeholders, long timeline), prefer:

1. Following the relevant `phases/` file(s) for process and structure.
2. Using the `templates/` files for concrete artifact formats.

---

## Templates Overview

This skill is bundled with detailed templates under `templates/`. Use them as follows:

- **Research planning and alignment**
  - When the user asks for a **research plan** or **study proposal**, read:
    - `templates/research-plan-template.md`
  - When the user needs **stakeholder alignment** or a kickoff agenda, read:
    - `templates/stakeholder-kickoff-template.md`
    - `templates/stakeholder-walkthrough-template.md`
  - When scoping what is **out of scope** and defining future research needs, read:
    - `templates/out-of-scope-and-research-needs-template.md`
  - When grounding a study in existing knowledge with a **desk/literature review**, read:
    - `templates/literature-review-template.md`

- **Consent and ethics**
  - For any study involving human participants (interviews, usability tests, diary studies, etc.), read:
    - `templates/uxr-consent-form-template.md`

- **Interview- and workshop-based methods**
  - For **qualitative interviews or discussions**, read:
    - `templates/interview-guide-template.md`
  - For **focus groups**, read:
    - `templates/focus-group-template.md`
  - For **persona workshops** and persona documentation, read:
    - `templates/persona-workshop-and-template.md`
  - For **stakeholder discovery sessions**, read:
    - `templates/stakeholder-walkthrough-template.md`
  - For **brainstorming/ideation sessions**, read:
    - `templates/brainstorming-template.md`

- **Usability and UX evaluation**
  - For **moderated usability testing**, read:
    - `templates/usability-test-script-template.md`
  - For **expert reviews** of flows or UI, read:
    - `templates/expert-review-template.md`
  - For **heuristic evaluations**, read:
    - `templates/heuristic-evaluation-template.md`
  - For **rapid iterative testing (RITE)**, read:
    - `templates/rapid-iterative-testing-rite-template.md`
  - For **eye-tracking studies**, read:
    - `templates/eye-tracking-template.md`
  - For **A/B tests / online experiments**, read:
    - `templates/ab-test-template.md`

- **Information architecture and navigation**
  - For **card sorting** (mental models, IA exploration), read:
    - `templates/card-sorting-template.md`
  - For **tree testing** (validating IA structure), read:
    - `templates/tree-testing-template.md`

- **Surveys and satisfaction measurement**
  - For **customer satisfaction surveys (CSAT, NPS + drivers)**, read:
    - `templates/customer-satisfaction-surveys-template.md`
  - For **recruitment screeners and survey structures**, read:
    - `templates/screener-and-survey-template.md`

- **Contextual and longitudinal methods**
  - For **contextual inquiry / field visits**, read:
    - `templates/contextual-inquiry-template.md`
  - For **diary studies**, read:
    - `templates/diary-study-template.md`
  - For **shadowing** and associated note-taking, read:
    - `templates/shadowing-template.md`
    - `templates/shadowing-notes-template.md`
  - For **ethnographic** or deep contextual work, read:
    - `templates/ethnography-template.md`

- **Strategy, jobs, and journeys**
  - For **Jobs to Be Done (JTBD)** framing, read:
    - `templates/jobs-to-be-done-template.md`
  - For **gap analyses** (current vs desired experience or capability), read:
    - `templates/gap-analysis-template.md`
  - For **user journeys / experience maps**, read:
    - `templates/journey-map-template.md`
  - For **competitive or comparative analysis**, read:
    - `templates/competitive-analysis-template.md`
  - For **Kano analysis** of feature satisfaction, read:
    - `templates/kano-analysis-template.md`

- **Visualization and empathy tools**
  - For **empathy maps**, read:
    - `templates/empathy-map-template.md`
  - For **storyboards** to visualize key moments, read:
    - `templates/storyboard-template.md`

When generating any concrete artifact (plan, screener, guide, script, survey, etc.), first:

1. Identify the relevant method(s) based on the user’s goal.
2. Read the corresponding template file(s) from `templates/`.
3. Adapt the structure and fill in project-specific details.

---

## Future Extensions

To keep `SKILL.md` concise, move heavier content into separate files when needed:

- `phases/` directory for more detailed, phase-by-phase instructions (similar to interview-analysis skills)
- `templates/` for long-form templates and examples

Link to those files from this skill when they exist, and keep this core document focused on the high-level framework and standard response structures.

