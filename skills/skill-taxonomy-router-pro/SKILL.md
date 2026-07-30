---
name: skill-taxonomy-router-pro
description: Route user tasks to the most relevant skills using a layered taxonomy, risk model, and minimum-necessary-loading strategy. Use when deciding which skill to load, when multiple skills could apply, when new downloaded skills need classification, when evaluating whether a skill may threaten the system, or when maintaining a persistent task-to-skill routing policy.
---

# Skill Taxonomy Router Pro

Use this skill to classify skills, choose which skill(s) to load for a task, and assess risk before loading action-capable skills.
Read `references/session-layer.md` first when you need the lightweight conversational rules. Use scripts/reports for heavy governance data instead of pulling large reference files into chat.

## Core policy

Follow this priority order:
1. Best task fit
2. Lowest sufficient risk
3. Lowest context cost
4. Fewest skills needed
5. Expand only if blocked

Do not load skills mechanically. Load the single most specific relevant skill first. Add a second skill only when it clearly fills a missing capability.
Also do not invoke the full skill-router workflow more than needed: start from summarized pool/index views, then drill into individual skills only when the task actually needs deeper routing help.

## Domain taxonomy

Classify each skill into exactly one primary domain and one subdomain.
Optional: assign up to two secondary domains.

Primary domains:
- A. Communication & Collaboration
- B. Knowledge & Retrieval
- C. Development & Agentic Work
- D. System & Infrastructure
- E. Business Ops & Growth
- F. Personal Productivity
- G. Devices & IoT
- H. Mobility & Lifestyle
- I. Finance & Trading
- Z. Meta / Platform Extension / Unclassified

### Subdomain risk baselines
Use these subdomains and default risk baselines when classifying current or future skills.

- A1 instant messaging/chat actions -> R2
- A2 email workflows -> R2-R3
- A3 document collaboration -> R1-R2
- A4 drive/file collaboration -> R1-R2
- A5 permissions/sharing control -> R3
- A6 wiki/knowledge-base collaboration -> R1-R2

- B1 web search -> R0
- B2 fetch/read web content -> R0-R1
- B3 academic/technical research lookup -> R0
- B4 local knowledge/markdown search -> R0
- B5 personal knowledge-base management -> R1
- B6 professional information lookup -> R0-R1

- C1 coding/implementation -> R1-R2
- C2 codebase understanding/navigation -> R0-R1
- C3 browser automation -> R2 baseline, raise to R3 if submit/login/write
- C4 multi-agent orchestration -> R1-R2
- C5 skill creation/maintenance -> R1-R2
- C6 terminal/session control -> R2
- C7 developer platform/API integration -> R1-R2

- D1 host health/security audit -> R1-R2
- D2 config/service management -> R3
- D3 AWS infra -> R2-R4
- D4 Azure infra -> R2-R4
- D5 SaaS admin/platform ops -> R2-R3
- D6 updating/self-maintenance -> R3

- E1 lead/contact enrichment -> R2-R3
- E2 CRM/sales data management -> R2-R3
- E3 outbound/ABM automation -> R3
- E4 customer messaging/email automation -> R3
- E5 affiliate/monetization tooling -> R2-R3
- E6 publishing/blog/content ops -> R1-R2
- E7 project/team business workflows -> R2

- F1 calendar/time management -> R1-R2
- F2 reminders/todos/planning -> R1-R2
- F3 notes systems -> R1
- F4 inbox search/processing -> R0-R1
- F5 cognition/knowledge/self-management -> R0-R1

- G1 media/audio device control -> R2
- G2 home/lifestyle device control -> R3
- G3 fabrication/printers/machines -> R3-R4
- G4 local sensing/screen/camera/device interaction -> R1-R3

- H1 weather/environment info -> R0
- H2 transit/routing -> R0
- H3 flight tracking/aviation status -> R0-R1
- H4 reading/media conversion lifestyle services -> R1-R2

- I1 budgeting/personal finance ops -> R2-R3
- I2 trading/crypto execution -> R4
- I3 commercial asset/revenue operations -> R2-R3

- Z1 skill marketplace/install/update -> R2-R3
- Z2 credentials/vaults/secrets -> R4
- Z3 bridges/proxies/platform adapters -> R2-R4
- Z4 temporary unclassified -> default R2 until reviewed

## Risk model

Use these levels:
- R0 read-only safe lookup
- R1 low-risk local/personal writing
- R2 moderate automation or remote write
- R3 high-risk control, permissions, external sending, service/config changes, device control
- R4 critical risk: credentials, money movement, infra privilege, proxying, production-impact actions

## Threat dimensions
For each skill, assess these dimensions:
- local_system: writes config/files, installs, executes shell, restarts services
- data_egress: uploads or sends local/remote data outward
- external_action: sends messages/emails/posts or mutates remote systems
- physical_world: controls devices, temperature, machinery, robotics
- auth_permission: handles credentials, sharing, IAM, vaults, privilege boundaries
- financial_asset: trading, payments, budgets, billable/valuable asset movement

## Capability tags
Assign 1-5 tags when classifying a skill:
- read-only
- search
- retrieve
- write-local
- write-remote
- message-send
- browser-act
- device-control
- finance
- credential
- automation
- agent-orchestration
- knowledge-base
- calendar
- notes
- crm
- cloud-infra
- security
- content-publish
- monitoring
- setup-install

## Routing algorithm
When a task arrives, do this:

1. Infer task intent in one sentence.
2. Determine the main object:
   - message, document, knowledge, code, browser, system, cloud, device, travel, finance, etc.
3. Determine the main action:
   - search, read, analyze, create, edit, send, schedule, control, install, update, trade, automate.
4. Search for the most specific matching subdomain.
5. Prefer one skill with the highest specificity.
6. If that skill lacks a needed capability, add one complementary skill only.
7. Avoid loading broad meta-skills if a narrower skill exists.
8. If multiple candidate skills remain, prefer:
   - lower risk
   - more read-only
   - more direct fit
   - fewer side effects
   - lower context cost
9. If task is ambiguous, stay with the least risky useful skill or ask only one clarifying question.
10. If task needs no skill, use built-in tools directly.
11. After a skill is actually chosen and used, treat routing-decision logging as the default post-action: record the chosen skill(s) with `python3 scripts/log_routing_decision.py ...` unless there is a concrete reason not to.

## Multi-skill composition rules
Use multiple skills only when roles are distinct, for example:
- retrieval skill + writing/publishing skill
- CRM skill + outbound messaging skill
- platform-specific skill + browser automation fallback
- codebase understanding skill + coding skill

Avoid combining multiple skills that do the same thing unless the first one fails or lacks required coverage.

## Future skill classification procedure
For any newly downloaded skill:

1. Read only its name and description first.
2. Determine the primary user task it solves.
3. Assign exactly one primary domain and one subdomain.
4. Assign optional secondary domains if truly cross-domain.
5. Assign 1-5 capability tags.
6. Inherit the subdomain risk baseline.
7. Raise risk if description mentions sending, permissions, credentials, trading, config, services, devices, installs, or proxying.
8. Lower risk only if the skill is clearly read-only.
9. If unclear, place in Z4 temporarily and mark for review.

## Permanent operating rule
Treat this routing policy as persistent guidance for future tasks. Reuse it by default whenever deciding whether to load a skill.

## Update policy
Update this skill when one of these happens:
- a new cluster of downloaded skills appears
- a subdomain becomes crowded and needs splitting
- a skill was misrouted in practice
- a risk baseline proved too high or too low
- recurring tasks show a better routing pattern

When updating:
1. Preserve stable top-level domains whenever possible.
2. Prefer adding or refining subdomains over restructuring the whole taxonomy.
3. Log changes in references/change-log.md.
4. If adding a new subdomain, define purpose, inclusion rule, exclusion rule, and default risk.
5. Rebuild the installed-skill index with `python3 scripts/update_skill_index.py --log` after classification changes or new skill installs.
6. Treat newly installed skills as backlog until reviewed or manually mapped.

## Maintenance workflow
Use this workflow to keep the router current:
1. When new skills are installed, rebuild the index with `python3 scripts/update_skill_index.py --log`.
2. Review newly added or backlog skills by reading only their name and description first.
3. If a skill is clearly important or likely to be used, move it from backlog into the manual mapping in `scripts/update_skill_index.py`.
4. Rebuild the index again after updating the mapping.
5. Run `python3 scripts/review_new_skills.py` to detect repeated backlog patterns that may justify a new subdomain.
6. Start from `python3 scripts/summarize_skill_pool.py` or `python3 scripts/query_skill_index.py ...` instead of pulling the full index into chat.
7. Keep `references/change-log.md` short and append-only.

## Usage tracking
Track skill frequency over time:
- Preferred path: when a routing choice is made, log it with `python3 scripts/log_routing_decision.py --intent <...> --domain <...> --subdomain <...> --risk <...> --skills <skill...> [--candidates ...] [--reason ...]`.
- Treat this as the default route-post action, not an optional extra, whenever a skill is clearly used.
- This both records the routing decision and increments usage counts for the chosen skills.
- Direct usage-only fallback: `python3 scripts/track_skill_usage.py mark <skill-name> [...]`.
- To see high-frequency skills, run `python3 scripts/track_skill_usage.py report --limit 30`.
- Use frequency as a prioritization signal for backlog classification: high-use backlog-adjacent domains should be reviewed first.

## Taxonomy expansion rule
Do not force every new skill into an ill-fitting old bucket.
When newly added skills repeatedly:
- land in backlog,
- match existing subdomains only weakly,
- or form a recurring theme not well represented,
then create or split a subdomain.
Use `python3 scripts/review_new_skills.py` to generate a review report for this.

## Backlog prioritization
Do not work backlog in arbitrary order.
Prioritize formal classification for skills that are:
- actually used in real tasks,
- likely to appear often,
- action-capable or higher-risk,
- or part of a repeated backlog cluster.
Use `python3 scripts/prioritize_backlog.py` to generate a recommended next-batch report.

## Overlap detection and fusion
When new skills arrive, check for overlap before treating every skill as independent.
Two safe automation layers are allowed:
1. Routing/index fusion: detect likely duplicates/variants and prefer one canonical skill by default.
2. Canonical-first index view: keep overlapping variants on disk, but de-prioritize them in routing.

Do NOT do destructive file/content merges automatically.
If overlapping skills contain materially different instructions, scripts, or design choices, ask the user before any content-level merge.

Use:
- `python3 scripts/detect_skill_overlap.py` to detect likely duplicate/variant families.
- `python3 scripts/apply_overlap_fusion.py` to generate a canonical-first fusion view.

## Download inbox workflow
Use a single temporary download folder for newly downloaded skills:
- New, unreviewed downloads go to `~/Desktop/skills-inbox`.
- After skills are reviewed, organized, and incorporated into the router process, do not maintain a second permanent reviewed folder on the Desktop.
- When the batch has been fully processed, delete the inbox folder.

Rules:
- Downloading a skill does not make it trusted.
- Skills in inbox are unreviewed by default and should not perform risk operations.
- Reviewing/organizing a skill means classifying it, checking overlap, and deciding routing priority or de-prioritization.
- Before downloading a new skill, check the existing organized/classified skill set to avoid redundant downloads and unnecessary overlap.
- New-skill risk operations still require explicit user approval.

Preferred intake path:
- Use `python3 scripts/intake_skill.py <skill-name>` for high-automation intake.
- This checks overlap against the organized skill set, downloads into `~/Desktop/skills-inbox` only when appropriate, and records intake state for later review.

Use `python3 scripts/cleanup_download_inbox.py --yes` to remove the Desktop inbox folder after the import batch is fully processed.

## External risk signals
When available, use external risk/security signals to speed up review:
- If a ClawHub page exposes security or risk labeling, incorporate that signal into review priority.
- If a skill comes from outside ClawHub or through a manual copy/import path, proactively screen it before giving it routing priority.
- Treat non-ClawHub skills as needing more active review than registry-installed skills.

Use `python3 scripts/review_risk_sources.py` to generate a review list for suspicious/high-risk/nonstandard sources.

## Files in this skill
- `references/skill-index.md`: current installed-skill index
- `references/change-log.md`: compact history of taxonomy/index changes
- `references/skill-classification-schema.md`: schema/checklist for classification decisions
- `references/usage-stats.json`: usage counters for skills chosen in practice
- `references/routing-decisions.jsonl`: append-only routing decision log
- `references/new-skill-review.md`: report of backlog clusters and possible taxonomy gaps
- `references/backlog-priority.md`: prioritized backlog report for next formal classifications
- `references/skill-overlap-report.md`: likely duplicate/variant families
- `references/skill-overlap-map.json`: canonical-to-variants overlap map
- `references/skill-fusion-view.md`: canonical-first routing/index view
- `references/risk-source-review.md`: review list for suspicious/high-risk/nonstandard-source skills
- `scripts/update_skill_index.py`: rebuilds the installed-skill index from current skills
- `scripts/cleanup_download_inbox.py`: deletes the Desktop inbox folder after a batch is fully processed
- `scripts/review_risk_sources.py`: generates a review list using source/risk signals
- `scripts/check_download_overlap.py`: checks a candidate download against the existing organized/classified skill set
- `scripts/intake_skill.py`: high-automation intake that checks overlap, downloads to inbox, and records intake state
- `scripts/summarize_skill_pool.py`: summarizes the skill pool so routing can start from a compact overview
- `scripts/track_skill_usage.py`: marks skill usage and reports high-frequency skills
- `scripts/log_routing_decision.py`: logs a routing decision and increments chosen-skill usage in one step
- `scripts/review_new_skills.py`: scans backlog/new skills for taxonomy expansion signals
- `scripts/prioritize_backlog.py`: scores backlog skills and suggests the next classification batches
- `scripts/detect_skill_overlap.py`: detects duplicate/variant skill families
- `scripts/apply_overlap_fusion.py`: generates a canonical-first fusion view without destructive merging

## Output format for future routing decisions
When useful, summarize chosen routing in this compact form:
- intent:
- primary domain/subdomain:
- candidate skills:
- chosen skill(s):
- risk level:
- why this choice:
- why others were not loaded:

## Boundaries
These hard boundaries apply equally to the pro edition. The pro edition may be more capable, but it does not receive more autonomous authority.
- Do not load a high-risk skill when a lower-risk path can complete the task.
- Do not treat installation/update skills as defaults.
- Do not let broad agent or meta skills overshadow narrow purpose-built skills.
- Do not permanently trust unreviewed new skills; classify them first.
- Do not allow newly downloaded skills to perform risk operations unless the user explicitly agrees.
- Treat new-skill risk operations as blocked by default for system/config/service/cron/credential/network-changing actions, even if the skill claims to automate them.
