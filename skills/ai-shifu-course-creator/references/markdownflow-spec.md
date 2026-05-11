# MarkdownFlow Quick Spec

## Variables

- Reference syntax: `{{var_name}}`
- No spaces in variable names
- Undefined variables resolve to `"UNKNOWN"`

## Interactions

- Single-select: `?[%{{var}} Option A | Option B | Option C]`
- Multi-select: `?[%{{var}} Option A || Option B || Option C]`
- Input: `?[%{{var}} ... enter your answer]`
- Button + input: `?[%{{var}} Option A | Option B | ...Other, please specify]`

## Structure

- Use `---` between instructional segments.
- Keep one objective per segment.

## Deterministic Output

- Single-line fixed text: `===fixed text===`
- Multi-line fixed text:

```md
!===
Line 1
Line 2
!===
```
