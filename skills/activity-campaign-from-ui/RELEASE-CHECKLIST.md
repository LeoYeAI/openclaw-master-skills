# Release Checklist

This checklist is for the final review of the `activity-campaign-from-ui` skill before publishing.

## 1. Positioning and scope

- [ ] The skill is clearly described as **one skill with multiple modes**.
- [ ] The supported modes are documented consistently:
  - [ ] `analysis`
  - [ ] `proposal`
  - [ ] `architecture`
  - [ ] `delivery`
  - [ ] `full`
- [ ] The skill is explicitly limited to:
  - [ ] H5 / Web
  - [ ] HTML
  - [ ] CSS
  - [ ] JavaScript
- [ ] No document implies support for Vue, React, Uni-app, or any other framework.
- [ ] The skill description does not drift back into a generic “image-to-code” or “UI parser only” tool.

## 2. Documentation consistency

Check all of these files:

- [ ] `README.md`
- [ ] `README.zh-CN.md`
- [ ] `SKILL.md`
- [ ] `references/scope.md`
- [ ] `examples/input-example.md`
- [ ] `examples/output-example.md`
- [ ] `examples/spring-festival-case.md`
- [ ] `examples/campaign-schema-example.json`

Consistency rules:

- [ ] The skill name is the same across all files.
- [ ] The one-line definition is aligned across all files.
- [ ] The supported platforms are always H5 / Web.
- [ ] The output stack is always HTML + CSS + JavaScript.
- [ ] The mode names are spelled the same everywhere.
- [ ] The default behavior is described the same way everywhere.
- [ ] The anti-copy rule is described the same way everywhere.
- [ ] The output file structure is described the same way everywhere.

## 3. Mode behavior

### analysis mode
- [ ] Only analyzes references.
- [ ] Does not generate a new campaign by default.
- [ ] Does not generate delivery code by default.

### proposal mode
- [ ] Produces a new campaign proposal.
- [ ] Clearly separates observed facts from inferred ideas.
- [ ] Does not over-expand into full implementation unless requested.

### architecture mode
- [ ] Produces page modules, popup structure, state flow, and implementation structure.
- [ ] Keeps focus on information architecture and interaction structure.
- [ ] Does not skip directly to large code blocks.

### delivery mode
- [ ] Produces implementation-oriented output only.
- [ ] Uses the fixed file structure:
  - [ ] `index.html`
  - [ ] `styles.css`
  - [ ] `main.js`
  - [ ] `mock-data.js`
- [ ] Uses plain JavaScript in interaction logic when behavior is needed.

### full mode
- [ ] Follows the complete flow:
  - [ ] reference analysis
  - [ ] pattern abstraction
  - [ ] new campaign proposal
  - [ ] page architecture
  - [ ] implementation skeleton

## 4. Anti-copy protection

- [ ] The skill explicitly says it must not reproduce the reference page directly.
- [ ] The rule is actionable, not vague.
- [ ] The output must change at least **2 of the following 4 items**:
  - [ ] campaign theme
  - [ ] reward mechanism
  - [ ] task structure
  - [ ] major module sequence or core interaction
- [ ] The skill avoids preserving the full original loop of:
  - [ ] same hero logic
  - [ ] same reward chain
  - [ ] same task loop
- [ ] The examples demonstrate transformation, not superficial reskinning.

## 5. Output structure

- [ ] The recommended output template is fixed and stable.
- [ ] The output clearly distinguishes:
  - [ ] `Observed`
  - [ ] `Inferred`
  - [ ] `Assumed`
- [ ] The output remains concise and structured.
- [ ] The output is suitable for handoff to product, design, or front-end teams.
- [ ] The skill does not overclaim pixel-perfect recovery from screenshots.

## 6. Code delivery rules

- [ ] The delivery output is implementation-oriented, not fake-production marketing text.
- [ ] HTML structure is semantic enough for front-end handoff.
- [ ] CSS structure maps to visible modules and states.
- [ ] JavaScript logic is readable and limited to realistic demo behavior.
- [ ] DOM interaction uses plain JavaScript APIs consistently where needed.
- [ ] Mock data is separated from rendering logic when possible.
- [ ] The output does not pretend to include backend integration unless explicitly provided.

## 7. Schema quality

Check `examples/campaign-schema-example.json`:

- [ ] It includes campaign-level data.
- [ ] It includes module-level data.
- [ ] It includes popup definitions.
- [ ] It includes state-related fields where needed.
- [ ] It includes tracking or event fields if the skill claims tracking support.
- [ ] The schema matches the documented output sections.
- [ ] The schema reflects H5/Web delivery, not framework-specific component trees.

## 8. Example quality

### input example
- [ ] The input example is realistic.
- [ ] It mentions the mode clearly.
- [ ] It does not mention unsupported frameworks.
- [ ] It uses H5 / Web wording consistently.

### output example
- [ ] The output example follows the documented structure.
- [ ] The output example shows how the mode affects the response.
- [ ] The output example demonstrates non-copying transformation.
- [ ] The output example includes implementation-oriented sections when relevant.

### case example
- [ ] The case example is specific enough to be useful.
- [ ] The generated campaign is clearly different from the references.
- [ ] The module design supports the proposed campaign logic.
- [ ] The implementation suggestion matches the schema and file layout.

## 9. Language quality

- [ ] `README.md` and `README.zh-CN.md` say the same thing, not two different products.
- [ ] Chinese and English terminology match:
  - [ ] mode
  - [ ] proposal
  - [ ] architecture
  - [ ] delivery
  - [ ] anti-copy
  - [ ] implementation skeleton
- [ ] No leftover wording suggests multi-framework support.
- [ ] No outdated wording remains from the earlier “activity image parser” version.

## 10. Repository hygiene

- [ ] No `.DS_Store`
- [ ] No `__MACOSX`
- [ ] No unused temp files
- [ ] File names are stable and readable
- [ ] Example files can be opened directly
- [ ] The zip package contains only skill-related content

## 11. Final go / no-go questions

Before publishing, answer all of these with “yes”:

- [ ] Can a user understand what this skill does in under 30 seconds?
- [ ] Can a user understand what this skill does **not** do?
- [ ] Will the user clearly know that only H5 / Web + HTML/CSS/JS are supported?
- [ ] Will the mode system reduce output drift instead of increasing confusion?
- [ ] Do the examples reflect the actual intended behavior?
- [ ] Does the skill avoid overpromising code completeness?
- [ ] Is the skill useful even when the reference screenshots are incomplete?
- [ ] Is the skill still useful when the user only wants one stage of the pipeline?

## Recommended final additions

If you want one more improvement before publishing, add these:

- [ ] `examples/mode-analysis-example.md`
- [ ] `examples/mode-proposal-example.md`
- [ ] `examples/mode-architecture-example.md`
- [ ] `examples/mode-delivery-example.md`
- [ ] `examples/full-delivery-example.md`

These make the mode behavior much easier to verify and maintain.
