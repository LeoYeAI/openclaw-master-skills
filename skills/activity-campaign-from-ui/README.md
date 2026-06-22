# activity-campaign-from-ui

Current repository version: **0.2.0**

A reusable OpenClaw skill for turning campaign UI references into a **new H5/Web campaign plan and delivery-ready high-fidelity front-end draft**.

## What this skill does
Given campaign screenshots, poster-like activity pages, or design references, this skill can:
- analyze the reference UI
- abstract the gameplay and module patterns
- propose a **new** campaign instead of copying the reference
- design a page/module architecture
- output visual-first draft code for **H5/Web only**

## Fixed platform and stack
This skill is intentionally strict.

- Platform: **H5 / Web**
- Stack: **HTML + CSS + JavaScript**

If the user asks for any other stack, this skill should still stay on the fixed stack above.

## Modes
This skill supports one skill with multiple modes:

- `analysis` — analyze the reference UI only
- `proposal` — generate a new campaign proposal from the reference
- `architecture` — output page modules, states, popups, and data structure
- `delivery` — output H5/Web high-fidelity draft files in HTML/CSS/JS
- `full` — do the full flow from analysis to delivery

If the user does not specify a mode:
- default to `proposal` when they want a new event idea
- default to `delivery` when they ask for code
- default to `full` when they want both planning and code

## Best for
- holiday event pages
- lucky draw / lottery campaigns
- task + reward campaigns
- promotional landing pages
- mobile-first H5 campaign pages
- poster-style marketing pages

## Typical inputs
- screenshots of activity pages
- multiple campaign references
- poster-like event images
- design previews or accessible design links
- user notes about target users, rewards, and campaign goals

## Typical outputs
- reference analysis
- gameplay abstraction
- new campaign proposal
- page architecture
- config/schema suggestions
- visual direction summary
- H5/Web high-fidelity draft code (`index.html`, `styles.css`, `main.js`, `mock-data.js`)

## Boundaries
This skill should not:
- produce code in other stacks
- pretend blurry text is exact
- claim hidden states or backend logic that are not visible
- directly copy the reference page

## Visual quality bar
For `delivery` and `full`, the expected result is a **launch-ready-feeling H5 front-end draft**, not a plain wireframe, demo shell, or generic starter.

Strong outputs should:
- summarize the screenshot's visual language before code
- decide whether the screenshot's colors actually fit the new campaign theme before reusing them
- render a believable first screen with nested hero/module markup
- use gradients, decorative wrappers, chips, badges, and stronger CTA styling when the reference implies them
- avoid repetitive white-card scaffolding unless the user explicitly asks for minimal output

If the reference theme conflicts with the requested campaign theme, keep the structural ideas but rebuild the palette and decorative language around the requested theme.
Example: a Spring Festival red-gold reference used for a Dragon Boat Festival brief should usually become a green or blue-green Dragon Boat style page rather than a red reskin.

## Additional delivery defaults
For `delivery` and `full`:
- aim for a launch-ready H5 front-end draft feel rather than a starter shell or wireframe
- use an adult female character-led first screen when the brief or reference clearly depends on poster-style human visual focus
- keep the female hero styling theme-matched, including wardrobe, dominant colors, props, and accessories
- for Spring Festival directions, default the female hero styling toward a red-dominant festive look with gold details rather than a generic modern outfit
- allow glamorous and slightly sexy commercial-fashion styling, while keeping the result suitable for a public-facing campaign page
- prefer tab-first mobile layouts when the page would otherwise become too long
- if the user requests a character-led hero but provides no asset, optionally generate one original adult female hero image and wire it as `assets/hero-figure.png` when the environment supports image generation
- this higher quality bar means production-like front-end finish, not a fully backend-connected deployment

## Local artifact generation
- in `proposal`, the result should feel closer to an operations campaign visual deck than a plain strategy memo
- if the user explicitly asks for a local visual deck and the host environment supports local execution, Python may be used to generate `campaign-proposal.pptx`
- in `delivery` and `full`, if the user explicitly asks for local front-end files and the host environment supports local execution, Python may be used to write `index.html`, `styles.css`, `main.js`, and `mock-data.js`
- use a user-specified directory when provided; otherwise default to the current working directory
- even when local artifacts are generated, do not output shell file-write commands in the response; report the created file paths instead

## Repository structure
- `SKILL.md` — main skill rules
- `agents/openai.yaml` — UI metadata for marketplaces and skill pickers
- `.editorconfig` — shared formatting rules for contributors
- `VERSION` — current repository version
- `LICENSE` — repository license
- `CODEOWNERS` — repository ownership template
- `CHANGELOG.md` — repository change history
- `RELEASE.md` — versioning and release policy
- `RELEASE-CHECKLIST.md` — final publishing checklist
- `CONTRIBUTING.md` — contribution and maintenance rules
- `references/scope.md` — scope and non-goals
- `examples/input-example.md` — input examples
- `examples/output-example.md` — output example
- `examples/spring-festival-case.md` — concrete case guidance
- `examples/campaign-schema-example.json` — example campaign delivery schema
- `examples/mode-analysis-example.md` — analysis mode example
- `examples/mode-proposal-example.md` — proposal mode example
- `examples/mode-architecture-example.md` — architecture mode example
- `examples/mode-delivery-example.md` — delivery mode example
- `examples/full-delivery-example.md` — full mode end-to-end example
