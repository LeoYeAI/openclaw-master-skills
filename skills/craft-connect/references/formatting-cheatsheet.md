# Craft Formatting Cheatsheet

All formats verified working via API testing on 2026-03-12.

## Block Types

| Type | Description | Insert Method |
|------|-------------|---------------|
| `text` | Text, headings, lists, tasks, callouts | Both |
| `code` | Code blocks, math formulas | JSON (needs `rawCode`) or Markdown |
| `line` | Dividers / horizontal rules | Both |
| `table` | Tables | Both |
| `image` | Images (re-hosted by Craft) | JSON |
| `richUrl` | Link previews (YouTube etc.) | JSON |
| `page` | Sub-pages / Cards | JSON |

## Markdown Mode Syntax

```
# H1    ## H2    ### H3    #### H4

**bold** *italic* ~strikethrough~ `inline code`
[link](url)
$(equation)$

- bullet
1. numbered
- [ ] todo
- [x] done
+ toggle parent
  - toggle child (2-space indent!)

> blockquote
---  (divider)

| A | B |
| --- | --- |
| 1 | 2 |

```python
code
```

<highlight color="yellow">text</highlight>
==also highlighted==
```

## Highlight Colors

**Solid:** yellow, blue, red, green, purple, pink, mint, cyan, gray
**Gradient:** gradient-blue, gradient-purple, gradient-red, gradient-yellow, gradient-brown

## Callout Colors (hex)

| Color | Hex | Use |
|-------|-----|-----|
| Blue | #00A3CB | Info |
| Red | #FF3B30 | Warning |
| Green | #34C759 | Success |
| Orange | #FF9500 | Caution |
| Purple | #9862E8 | Creative |
| Deep blue | #003382 | Formal |
| Deep green | #006744 | Nature |
| Brown | #864d00 | Warm |
| Bright red | #ef052a | Alert |
| Gray | #9ea4aa | Muted |

## Line Styles

| Style | JSON `lineStyle` |
|-------|-----------------|
| Extra light | `extraLight` |
| Light | `light` |
| Regular | `regular` |
| Strong | `strong` |

## Font Values

(omit) = system, `serif`, `mono`, `rounded`

## textStyle Values

(omit) = body, `h1`, `h2`, `h3`, `h4`, `caption`, `page`, `card`

## listStyle Values

`bullet`, `numbered`, `task`, `toggle`

## taskInfo.state Values

`todo`, `done`, `canceled` — NOT "completed"!

## Task Location Types

`inbox`, `dailyNote` (+ date), `document` (+ documentId)

## Task Scopes

`inbox`, `active`, `upcoming`, `logbook`, `document` (+ documentId)
