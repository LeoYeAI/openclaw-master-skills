# PLANNING.md Template

Use this structure when generating `PLANNING.md` during `--plan` mode.

---

## Template

```markdown
**Task**: [One-sentence description of the deck to generate]
**Slide count**: [N] ± [tolerance]
**Language**: [Chinese / English / bilingual]
**Audience**: [Target audience description]
**Goals**:
- [Goal 1]
- [Goal 2]
**Style**: [Tone and style keywords, e.g., bold, minimal, editorial, futuristic]
**Preset**: [Style preset name from the available list, or "guided discovery"]

---

## Visual & Layout Guidelines

- **Overall tone**: [e.g., warm, minimal, high-contrast dark]
- **Background**: [hex color + description]
- **Primary text**: [hex color]
- **Accent (primary)**: [hex color + usage]
- **Typography**: [Font pairing, e.g., Clash Display + Satoshi]
- **Per-slide rule**: 1 key point + up to 5 supporting bullets; no text walls
- **Animations**: [e.g., fade + slide-up, staggered 0.1s delay]

---

## Slide-by-Slide Outline

**Slide 1 | Cover**
- Title: [title]
- Subtitle: [subtitle]
- Visual: [background treatment, logo placement]

**Slide 2 | Agenda / Overview**
- [Topic 1]
- [Topic 2]
- [Topic 3]

**Slide 3 | [Section Title]**
- Key point: [one sentence]
- Supporting: [2-4 bullets]
- Visual element: [icon set / grid / chart / diagram / screenshot]
- Speaker note: [what to say on this slide]

[...continue for each slide...]

**Slide N | Closing**
- Summary statement
- Call to action or contact info

---

## Resources Used

- [List files from resources/ and how they map to slides]
- Example: `resources/report.pdf` → Slide 3 data, Slide 5 quote

---

## Images

- [List image files if provided and which slide they go on]
- Example: `assets/screenshot.png` → Slide 4 (feature demo)

---

## Deliverables

- Output: [filename].html (single-file, zero dependencies)
- Optional: PRESENTATION_SCRIPT.md (speaker notes)
- Inline editing: [Yes / No]
```

## Guidelines for Writing the Plan

1. **Be specific** — Write actual key points and bullets per slide, not just "content about X"
2. **Map resources** — Reference which source file informs which slide
3. **Specify visuals** — Note what visual element each slide should have
4. **Speaker notes** — Note emphasis points for the presenter per slide
5. **Match audience** — Technical audience = more data; executive = more impact
