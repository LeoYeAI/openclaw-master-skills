# Mutation Guide

Reference for rewriting a builder's SKILL.md during evolution. Each mutation type targets a different axis of variation. The goal is to produce a child builder that generates **differently-structured or differently-instructed skills** than its parent.

## General Principles

1. **Small changes compound** — A single well-chosen tweak per generation is better than rewriting everything. Evolutionary pressure will amplify good changes over time.
2. **Preserve what works** — If the parent has high fitness (> 0.5), most of its approach is good. Mutate around the edges, not the core.
3. **Diversity is valuable** — The ecosystem benefits from builders that take different approaches. Don't converge toward a single "best" template.
4. **Be concrete** — Vague instructions ("write better code") produce vague skills. Specific instructions ("add input validation for all string parameters") produce measurable differences.
5. **Test your changes mentally** — Before finalizing, imagine an agent following the rewritten SKILL.md. Would it produce something meaningfully different from the parent?

---

## Mutation Type: `prompt_tweak`

Small, targeted changes to the builder's instruction text. The file structure stays the same; only the wording of prompts and guidance changes.

### Strategies

1. **Specificity increase** — Replace generic instructions with concrete ones. "Write good tests" → "Write at least 3 test cases: happy path, edge case (empty input), and error case (invalid type)."
2. **Tone shift** — Change the instructional voice. Terse bullet points → narrative paragraphs, or vice versa. This affects how agents interpret and follow the instructions.
3. **Priority reorder** — Move validation/testing instructions earlier in the flow so agents treat them as higher priority. Or move them later to emphasize speed.
4. **Constraint addition** — Add a new constraint the parent didn't have: "All generated files must be under 50 lines" or "Every function must have a JSDoc comment."
5. **Constraint relaxation** — Remove an overly strict constraint that might be limiting skill quality. "Must use TypeScript" → "Use TypeScript or JavaScript depending on the idea's ecosystem."
6. **Example injection** — Add a concrete before/after example showing what a good skill looks like vs. a bad one.

### Anti-patterns

- Don't just rephrase the same instruction in different words — the agent behavior won't change
- Don't add contradictory instructions (e.g., "be concise" and "include detailed explanations")
- Don't add more than 2-3 new constraints per mutation — too many changes make it hard to attribute fitness

---

## Mutation Type: `structure_change`

Alter the directory layout, file organization, or output format that the builder prescribes for generated skills.

### Strategies

1. **Add a directory** — Introduce `scripts/`, `examples/`, `tests/`, or `references/` to the expected skill output structure.
2. **Split a monolith** — If the parent puts everything in SKILL.md, split instructions into SKILL.md (agent instructions) + a separate reference file (technical details).
3. **Merge files** — If the parent has many small reference files, consolidate them into fewer, more comprehensive ones.
4. **Change the entry point** — Alter what the "main" output file is. Instead of a single script, produce a directory with an index file.
5. **Template system** — Add template files that the builder instructs the agent to customize rather than write from scratch.
6. **Config extraction** — Move hardcoded values into a config file that users can customize after installation.

### Anti-patterns

- Don't create empty directories with no purpose — every directory should have instructions for what goes in it
- Don't nest more than 3 levels deep — flat is better than nested for agent skills
- Don't change structure so drastically that the instructions no longer match the expected output

---

## Mutation Type: `reference_swap`

Change the reference materials, examples, or documentation that the builder points to or includes.

### Strategies

1. **Inline vs. external** — Switch between inline documentation (in SKILL.md) and external reference files. Each approach has tradeoffs for agent context window usage.
2. **Example replacement** — Swap out code examples for ones in a different language, framework, or paradigm while keeping the same concept.
3. **Add troubleshooting** — Include a "Common Issues" or "Troubleshooting" section that helps agents handle edge cases the parent didn't address.
4. **API reference update** — If the builder references specific APIs or libraries, update to newer patterns or alternative libraries.
5. **Style guide swap** — Change the coding style guide the builder references (e.g., from Airbnb to Standard, from OOP to functional).
6. **Add/remove context** — Add background context about *why* certain patterns are used, or remove verbose explanations in favor of terse examples.

### Anti-patterns

- Don't reference files that don't exist in the builder's directory
- Don't swap references to something completely unrelated to the builder's purpose
- Don't remove all references — agents need some grounding material

---

## Mutation Type: `hybrid`

Combine 2-3 changes from different mutation types. This is the highest-variance mutation and should be used carefully.

### Strategies

1. **Prompt + structure** — Add a new constraint (prompt_tweak) and a corresponding directory for it (structure_change). E.g., "All skills must include tests" + add a `tests/` template.
2. **Reference + prompt** — Swap a reference file (reference_swap) and update the instructions that point to it (prompt_tweak).
3. **Structure + reference** — Reorganize files (structure_change) and update the documentation to match (reference_swap).
4. **Full refresh** — For low-fitness parents (< 0.3), rewrite the approach significantly: new structure, new references, new prompt style. Keep only the core idea/purpose.
5. **Crossover simulation** — If you know about other high-fitness builders in the pool, borrow a specific technique from one and integrate it into this builder's approach.

### Anti-patterns

- Don't combine more than 3 changes — hybrid doesn't mean "change everything"
- Don't apply contradictory changes from different types
- Don't lose the builder's identity — it should still be recognizable as an evolution of its parent
- For high-fitness parents, prefer combining 2 small changes over 1 big one

---

## Diff Checklist

Before finalizing the rewritten SKILL.md, verify:

- [ ] YAML frontmatter is valid (`name`, `description`, `version`, `license` all present)
- [ ] The `name` field is updated (typically `<parent-name>-v<generation>`)
- [ ] At least one substantive instruction has changed (not just whitespace or comments)
- [ ] All file references in the instructions point to files that exist in the builder directory
- [ ] The instructions are self-consistent (no contradictions)
- [ ] An agent reading only this SKILL.md could produce a working skill
