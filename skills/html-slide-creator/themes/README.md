# Custom Themes

Drop a folder here to add your own design preset to slide-creator.

## Structure

```
themes/
  your-theme-name/
    reference.md      ← required: style description Claude reads
    starter.html      ← optional: pre-built boilerplate (like blue-sky-starter.html)
```

## reference.md format

Follow the same format as the built-in references (e.g. `references/chinese-chan.md`):

```markdown
# Your Theme Name — Style Reference

One-sentence description. Inspired by / aesthetic / mood.

---

## Colors

```css
:root {
    --bg:      #...;
    --text:    #...;
    --accent:  #...;
}
```

## Typography
...

## Layout
...

## Best For
Use cases, audience, occasion.
```

## starter.html (optional)

If your theme has complex visual elements (animated backgrounds, special layout systems),
provide a starter HTML file. Claude will read it and use it as the base instead of
building from scratch. See `references/blue-sky-starter.html` for an example.

## Example

`_example-coral-dawn/` — a complete sample theme you can copy and adapt.
Directories starting with `_` are ignored by slide-creator and will not appear in the preset picker.

Also see:
- `references/chinese-chan.md` — a built-in reference in the same format
- `references/blue-sky-starter.html` — a full starter template

## Sharing themes

To share a theme with others, publish the folder as a git repo. Users clone it into their
`themes/` directory:

```bash
git clone https://github.com/yourname/slide-creator-theme-yourtheme \
  ~/.claude/skills/slide-creator/themes/yourtheme
```
