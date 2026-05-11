---
name: ai-shifu-course-creator
description: Convert raw course material into optimized, runnable MarkdownFlow
  teaching scripts and deploy them as live courses through a five-phase pipeline
  covering segmentation, orchestration, generation, optimization, and deployment.
---

# Course Creator

Convert raw course material into runnable, optimized MarkdownFlow lesson scripts and deploy them as live AI-Shifu courses.

## Execution Modes

- Standard mode (default): Input quality is sufficient; run requested phases in full.
- Fallback mode: Input is incomplete or low quality; produce coarse outputs, mark uncertainty, and provide focused rerun hints.

## Language Resolution Policy

See `references/language-resolution.md` for the full policy.

Resolve target language with this strict priority:
1. `explicit_output_language_request`
2. `target_language_parameter`
3. `session_language_preference`
4. `prompt_language_detection`
5. `source_material_dominant_language`
6. `default_fallback_language` (`en-US`)

## Authoring Control Inputs

Use these optional controls across all phases:

- `course_profile` (json): audience level, prerequisite level, lesson duration target, lesson count target, and assessment mode.
- `delivery_constraints` (json): interaction density, platform limits, must-cover topics, avoid topics, and non-negotiable source fragments.

See `references/input-contract.md` for recommended object shapes.

## Output Boundary

- Final outputs are learner-facing teaching content only.
- Authoring rules, pipeline notes, and process instructions stay in skill docs and references, not in lesson outputs.
- Internal design notes may appear only in HTML comments when needed.

## Pipeline Overview

```
Phase 1: Segmentation → Phase 2: Orchestration → Phase 3: Generation → Phase 4: Optimization → Phase 5: Deployment
```

## Usage Paths

### Path A: End-to-End

Run all five phases from raw material to a live deployed course.

1. Phase 1: Segment raw material into semantic units.
2. Phase 2: Orchestrate lesson boundaries and generate scripts.
3. Phase 3: Generate per-lesson MarkdownFlow scripts (called internally by Phase 2).
4. Phase 4: Audit and optimize final scripts.
5. Phase 5: Build, import, and publish to the AI-Shifu platform.

### Path B: Author Only

Run Phase 1–4 to produce optimized MDF scripts without deploying. Sub-paths:
- **Segment only**: Phase 1 alone for structured segments and manual review.
- **Generate only**: Phase 3 alone on pre-existing segments to produce lesson scripts.
- **Optimize only**: Phase 4 alone to audit and improve existing MarkdownFlow scripts.

### Path C: Deploy Only

Run Phase 5 alone to deploy pre-existing MDF files to the AI-Shifu platform.

### Path D: Manage Existing

Use Phase 5 management commands (list, show, update, rename, reorder, delete, publish, archive) on courses already on the platform.

---

## Phase 1: Segmentation

Turn messy course source material into a reliable intermediate structure for downstream lesson generation.

### Workflow

1. Remove filler language and duplicated phrasing without changing meaning.
2. Mark immutable blocks: code, images, and tables.
3. Segment by semantic continuity instead of headings alone.
4. Propose lesson boundaries with one core question per lesson.
5. Return source-linked structured segments.

### Segment Schema

Each segment includes:
- `segment_id`
- `segment_type` (`concept`, `example`, `code`, `image`, `exercise`, `transition`)
- `core_point`
- `preserve_block` (`yes` or `no`)
- `source_span`

### Transfer Signals

Capture these fields for downstream teaching quality:
- `learner_hook`: statements that can trigger learner reflection.
- `evidence_type`: one of history, phenomenon, data, mechanism, or conclusion.
- `visual_cue`: fragments suited for SVG/HTML visual support.
- `concept_conflict`: candidate idea conflicts for cognitive contrast.
- `boundary_cue`: clues for validity boundaries.
- `action_cue`: clues that can become immediate or staged actions.
- `density_cue`: high-information chunks that should not be diluted.
- `quote_cue`: original wording worth preserving.
- `visual_text_pair_cue`: clues for "visual first, explanation second" blocks.
- `interaction_intent_cue`: intent labels such as diagnose, branch, calibrate, compare.
- `compare_cue`: candidate prompts for before/after comparison.

### Phase 1 Outputs

- Ordered segment list.
- Lesson boundary candidates.
- One core question per lesson.
- Preservation block index.
- Full transfer-signal package.

See `references/segmentation-rules.md`.

### Phase 1 Validation

- Segment output covers all valid source spans in traceable order.
- Code/image/table blocks keep original placement and format.
- Every lesson candidate resolves to one core question.
- Transfer-signal fields are complete and usable downstream.
- Cleanup does not alter key facts or terminology.

---

## Phase 2: Orchestration

Convert raw course material into runnable lesson-level MarkdownFlow scripts by coordinating segmentation and generation.

### Workflow

1. Normalize source ordering and merge input material.
2. Run Phase 1 for cleanup and semantic segmentation.
3. Generate lesson-cut candidates with one core question each.
4. Run Phase 3 for lesson-level MarkdownFlow scripts.
5. Build course index and global variable table.
6. Recompute only failed lessons through strict gating.

### Mandatory Gates

All gates must pass:
- Code blocks are preserved character-by-character.
- Image links and relative placement are preserved.
- Each lesson resolves one core question.
- Each lesson contains at least one valid MarkdownFlow interaction, max five interactions total.
- Each lesson includes a minimum teaching loop: setup, explanation, interaction, close.
- Lesson language is learner-facing, not pipeline narration.
- Each lesson includes at least one deepening interaction (calibration, boundary check, or counterintuitive prompt).
- Action tasks are either immediately executable or explicitly linked to later modules.
- Variable naming is consistent and traceable.
- No unresolved placeholder variables in learner-facing text.
- Do not wrap full lessons in deterministic blocks (`=== ===` or `!=== !===`).
- Deterministic blocks are reserved for legally or operationally fixed statements only.
- If an image must remain unchanged, use single-line deterministic syntax per image.
- Use `---` between instructional blocks to keep pacing readable.
- Every variable collection step must produce immediate feedback and downstream effect.
- Core knowledge points require visual + textual explanation together.
- Consecutive variable collection cannot exceed three variables.
- Do not recollect the same variable unless explicitly marked as staged comparison.
- Never reference uncollected variables.
- Interaction prompts must be concrete and directly answerable.
- Avoid repetitive interaction semantics across lessons unless comparison intent is explicit.
- `*_viewpoint_check` interactions must branch by option and drive different next steps.
- Every interaction variable must create visible downstream impact.

### Rerun Rules

- Recompute only impacted lessons.
- Recompute dependency-linked lessons when shared variables change.
- Recompute full course only when global source order changes.

### Failure Handling

When source quality is weak:
- Deliver coarse lesson drafts first.
- Mark uncertain spans explicitly.
- Continue with best-effort generation instead of stopping.

### Phase 2 Outputs

- Lesson MarkdownFlow scripts (one file per lesson).
- Course index (lesson id, title, core question, source mapping).
- Global variable table (definition, use, cross-lesson references).

See `references/output-contract.md` and `references/preservation-rules.md`.

### Phase 2 Validation

- Lesson scripts, course index, and variable table are all present.
- Code/image preservation is exact and position-safe.
- One-core-question and interaction cap rules are satisfied per lesson.
- No unresolved variables or no-op interactions remain.
- Fallback outputs include explicit uncertainty markers and rerun hints.

---

## Phase 3: Generation

Generate runnable MarkdownFlow scripts for each lesson.

### Teaching Pattern Baseline

Use these defaults unless lesson content requires a justified variation:

1. Learner-facing language only.
2. Variable collection is distributed, not front-loaded.
3. Build evidence chain from observation to mechanism to conclusion.
4. Use visual-first explanation for abstract concepts, then textual interpretation.
5. Every collected variable must immediately affect downstream content.
6. Include at least one deepening interaction (calibration, boundary check, or misconception correction).
7. Include at least one reusable deliverable.
8. Action steps must be immediately executable or explicitly staged for downstream lessons.
9. Use carryover statements only if cross-lesson dependency is allowed.
10. Avoid exposing internal authoring terms in learner-facing text.
11. Keep interaction prompts concrete and answerable.
12. `*_viewpoint_check` prompts must branch with distinct feedback paths.
13. Repeated interaction patterns are allowed only when framed as staged comparison.

See `references/teaching-patterns.md` and `references/cognitive-techniques.md`.

### Single-Lesson Generation Strategy

Required anchors:
1. Opening objective plus visual cover.
2. Evidence-chain explanation.
3. At least one effective interaction with visible downstream effect.
4. At least one reusable deliverable.
5. Lesson close with summary or decision checkpoint.

Optional modules:
- Viewpoint calibration.
- Misconception correction.
- Dual deliverables (understanding + action).
- Cross-lesson bridge sentence.
- Additional visual-text reinforcement blocks.

### Variable Strategy

- Prefer at most one variable collection per module.
- Max five interactions per lesson (recommended three to four).
- No more than three consecutive variable collections before feedback.
- Reuse global variables when possible; add lesson-local variables only when required.
- Every variable must have downstream utility (branching, depth control, or deliverable variation).
- No unresolved placeholders in learner-facing text.
- Do not recollect the same variable unless explicitly marked as staged comparison.
- Prevent semantic duplicates even when variable names differ.

### Visual-Text Coordination

- Include an SVG cover in each lesson by default.
- Every core concept must include at least one visual-plus-explanation pair.
- Visuals compress structure; text explains mechanism, limits, and pitfalls.
- Replace unstable source images with generated SVG/HTML visuals when needed.

### Interaction Design

- Use no more than one `viewpoint_check` in a lesson unless justified.
- Each `viewpoint_check` must trigger a concrete next action.
- If using a "restate-boundary-counterintuitive" pattern, branch by option with distinct content.

### Phase 3 Outputs

Return per lesson:
- `lesson_id`
- `lesson_title`
- `mdf_script`
- `used_variables`
- `depends_on_lessons`

See `references/lesson-template.md`.

### Phase 3 Validation

- Minimum teaching loop exists (setup, explanation, interaction, close).
- Interaction outcomes visibly alter downstream content.
- Variable safety rules pass (collect before reference, no duplicate recollection).
- Core concepts satisfy visual-plus-text coordination.
- Script remains valid and runnable MarkdownFlow.

---

## Phase 4: Optimization

Audit and improve existing MarkdownFlow teaching prompts. This phase is not for writing from scratch.

### When to Use

- Gap analysis against source material.
- Script quality upgrades without full rewrites.
- Consistent chapter style with lower runtime failure risk.

### Core Method

1. Start with a low-friction entry point (cover visual + one light interaction).
2. Ensure interactions change downstream logic.
3. Keep structure content-driven, not template-driven.
4. Build evidence chain: observation/history -> mechanism/data -> conclusion.
5. Use visuals for abstract structure and text for mechanism + boundaries.
6. Add viewpoint calibration with branching feedback.
7. Include concrete correction actions for major misconceptions.
8. Keep deliverables executable and reusable.
9. Stabilize syntax and variable usage.

See `references/optimization-methodology.md`.

### High-Standard Constraints

- Separate knowledge blocks with `---`.
- Include a lesson cover visual by default.
- Keep max interactions per lesson at five (recommended three to four).
- Place interactions at decision points, not only at lesson start.
- Every interaction must trigger immediate feedback plus downstream effect.
- Limit consecutive variable collection to three.
- No uncollected variables in learner-facing text.
- Spread global variable collection across lessons.
- Do not recollect the same variable unless marked as staged comparison.
- Treat semantic duplicates as duplicates even if variable names differ.
- Use stable input syntax: `?[%{{var}}...prompt]`.
- Keep ending structure lesson-appropriate; interactive endings are optional.
- Every core concept needs visual-plus-text explanation.
- Avoid internal authoring terms in learner-facing copy.
- Keep prompts concrete and answerable.
- `*_viewpoint_check` interactions must branch by option.
- Preserve source information density; do not trade substance for fluency.

### Optimization Workflow

1. Define scope (single lesson vs full course).
2. Build coverage matrix: source points -> script coverage.
3. Label issue classes:
   - `coverage_gap`
   - `meaning_shift`
   - `explanation_clarity`
   - `interaction_no_branching`
   - `visual_constraints_missing`
   - `variable_or_syntax_risk`
4. Apply smallest safe edits first.
5. Run checklist validation before final output.
6. Re-check visual-text pairing for every core concept.
7. Re-check variable lifecycle (collection, reference timing, reuse).
8. Re-check semantic duplication in interaction prompts.
9. Re-check viewpoint branching and downstream action coupling.

See `references/review-checklist.md`.

### Required Output Style

- Present conclusion and risk level first.
- Then provide grouped change list by issue class.
- Use file-level references for traceability.
- If duplicate script versions exist, declare the authoritative one.
- If cross-lesson dependency is disallowed, remove dependency text and unbound carryover variables.

### Common Failure Patterns

- Structural edits without content-depth recovery.
- Over-abstraction that drifts from source meaning.
- Hidden cross-lesson variables causing runtime failures.
- Vague prompts that models cannot execute reliably.
- Viewpoint options that still return identical feedback.
- Repeated semantic questions with different variable names.
- Visual tasks without explanatory text.
- Rigid template consistency at the cost of lesson specificity.

### Phase 4 Validation

- Conclusion and risk level are presented first.
- All issue classes are fully audited.
- `viewpoint_check` interactions branch and trigger distinct next actions.
- Uncollected variable references and semantic duplicate interactions are removed.
- Output remains runnable with no loss of source information density.

---

## Phase 5: Deployment

Deploy optimized MDF lesson scripts to the AI-Shifu platform as live courses.

### Prerequisites

- Python 3 with `requests` and `python-dotenv` packages installed.
- CLI script: `{skillDir}/scripts/shifu-cli.py`

### Authentication

See `references/cli-reference.md` for the full login flow.

When no valid token is available, guide the user through the login process:
1. Ask the user to choose their region (China mainland / non-China-mainland).
2. For China mainland: use the SMS login flow via `shifu-cli.py login`.
3. For non-China-mainland: instruct the user to log in manually and set `SHIFU_TOKEN` in `{skillDir}/.env`.

Always use CLI commands. Never make raw HTTP/API calls directly.

### Course Directory

MDF lesson scripts must be organized in a course directory before deployment. See `references/course-directory-spec.md` for the full specification.

When continuing from Phase 4 (Path A), write optimized scripts into the course directory structure automatically.

### CLI Quick Reference

Core deployment commands:

```bash
build --course-dir ./course-a/                          # Build shifu-import.json (offline)
import --new --json-file ./course-a/shifu-import.json   # Import as new course
publish <shifu_bid>                                      # Make course live
show <shifu_bid>                                         # Verify course structure
```

See `references/cli-reference.md` for the complete command reference and `references/import-json-format.md` for the JSON schema.

### Deployment Workflow

**From pipeline (Path A continuation):**
1. Write Phase 4 outputs into the course directory (`lessons/`, `README.md`, `system-prompt.md`, optional `structure.json`).
2. Run `build --course-dir <dir>` to generate `shifu-import.json`.
3. Run `import --new --json-file <dir>/shifu-import.json` to create the course.
4. Run `publish <shifu_bid>` to make it live.
5. Verify via platform URL.

**Standalone deployment (Path C):**
1. Ensure course directory is ready with MDF files.
2. Run `build`, `import`, `publish` as above.

### Common Management

Use these commands for ongoing course operations (Path D):

```bash
list                                                   # List all courses
show <shifu_bid>                                       # Show course outline
update-meta <shifu_bid> --name "..." --description "..."
update-lesson <shifu_bid> <outline_bid> --mdf-file updated.md
rename-lesson <shifu_bid> <outline_bid> --name "New Name"
reorder <shifu_bid> --order bid1,bid2,bid3
delete-lesson <shifu_bid> <outline_bid>
publish <shifu_bid>
archive <shifu_bid>
```

### Verification

After any deployment or management operation, verify the result:
1. Admin console: `https://app.ai-shifu.cn/shifu/<shifu_bid>` (cn) or `https://app.ai-shifu.com/shifu/<shifu_bid>` (global)
2. Preview: `https://app.ai-shifu.cn/c/<shifu_bid>?preview=true`
3. Check each lesson's MDF content, variable collection, and interaction logic.

### Phase 5 Validation

- Import completes without errors.
- Course is accessible via platform URL.
- Lesson count and structure match the source directory.
- Published course is reachable in preview mode.

---

## MarkdownFlow Syntax (Required)

See `references/markdownflow-spec.md` for the quick reference.

1. Variables:
   - Use `{{var_name}}` for references.
   - Variable names cannot contain spaces.
   - Undefined variables default to `"UNKNOWN"`.

2. Interactions:
   - Single-select: `?[%{{var}} Option A | Option B | Option C]`
   - Multi-select: `?[%{{var}} Option A || Option B || Option C]`
   - Input: `?[%{{var}} ... enter your answer]`
   - Button + input: `?[%{{var}} Option A | Option B | ...Other, please specify]`

3. Segments:
   - Use `---` between segments.
   - Each segment should serve one clear instructional objective.

4. Deterministic output:
   - Single-line fixed text: `===fixed text===`
   - Multi-line fixed text:
   ```md
   !===
   Line 1
   Line 2
   !===
   ```

5. Authoring principle:
   - Script text should guide generation behavior.
   - Do not output full polished learner prose as fixed text.
   - Never lock full lesson bodies inside deterministic blocks.
   - For fixed images, use one deterministic line per image.
   - After each interaction, restate learner selection and reflect it in downstream content.
   - For input prompts, include example phrasing to reduce blank responses.
   - Use stable input syntax: `?[%{{var}}...prompt]`.

## Shared Constraints

### Preservation Rules

See `references/preservation-rules.md`.

Must preserve:
- Code content and fence language.
- Image URLs, alt text, and relative placement.
- Domain terms and factual statements.

Can normalize:
- Speech filler.
- Sentence breaks and punctuation.
- Redundant transitions.

### Variable Rules

- Collect before reference; never use uncollected variables.
- No more than three consecutive variable collections before feedback.
- Max five interactions per lesson (recommended three to four).
- Every variable must produce downstream utility.
- No unresolved placeholders in learner-facing text.
- Do not recollect the same variable unless explicitly marked as staged comparison.
- Prevent semantic duplicates even when variable names differ.
- Reuse global variables when possible.

### Interaction Rules

- Each lesson includes at least one deepening interaction (calibration, boundary check, or misconception correction).
- Interaction prompts must be concrete and directly answerable.
- `*_viewpoint_check` interactions must branch by option and drive different next steps.
- Avoid repetitive interaction semantics across lessons unless comparison intent is explicit.
- Every interaction variable must create visible downstream impact.

## Validation Checkpoints

### Phase 1 (Segmentation)
- Source span traceability and immutable block preservation.
- One core question per lesson candidate.

### Phase 2 (Orchestration)
- All mandatory gates pass.
- Course index, variable table, and lesson scripts are complete.

### Phase 3 (Generation)
- Teaching loop, variable safety, visual-text coordination.
- Script is valid runnable MarkdownFlow.

### Phase 4 (Optimization)
- All issue classes audited.
- Interaction branching and variable lifecycle validated.
- No loss of source information density.

### Phase 5 (Deployment)
- Import completes without errors.
- Course is accessible and lesson structure matches source.
- Published course is reachable in preview mode.

## Report Template

See `references/report-template.md`.

## Examples

- `examples/pipeline-full.md`
- `examples/segmentation-only.md`
- `examples/generation-only.md`
- `examples/optimization-only.md`
- `examples/fallback-mode.md`
- `examples/end-to-end-deploy.md`
- `examples/deploy-only.md`
