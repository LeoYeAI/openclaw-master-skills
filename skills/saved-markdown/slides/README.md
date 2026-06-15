# Slides (frontend-slides delegated)

This folder is intentionally structured for future slide scaffolding files
that are stored alongside the `saved-markdown` skill package.

Right now, Slides Deck generation is delegated to the external
`frontend-slides` skill (installed from):

- https://github.com/zarazhangrui/frontend-slides

### What the agent should do

When the user requests a slide deck (a page with `contentType: "slides"`):

1. Ensure `frontend-slides` is installed.
2. Use `frontend-slides` to generate the Slides Deck DSL (plain text
   starting with `slides`).
3. Publish the resulting deck via `POST /api/pages` with
   `contentType: "slides"`.

### Future work

Later, you can add slide-specific reference files here (for deck layout
constraints, naming conventions, and style rules) without changing the
delegation flow above.

