# Coordinate Reconstruction

Use this file when the agent must decide **where** to click from screenshot evidence instead of relying on fixed guesses.

## Goal

Reconstruct a reliable click target from:

- full-screen screenshots
- region screenshots
- screen size
- live mouse coordinates
- pixel samples at candidate points

## Principle

Do not trust a guessed absolute coordinate until you verify it.

Preferred loop:

1. get current screen size
2. capture full screen
3. identify a candidate UI region visually
4. narrow to a region capture if needed
5. estimate a target point inside the region
6. optionally sample the pixel color at that point
7. move to the target point
8. read back the real mouse position
9. click only if the pointer landed where expected
10. capture again and verify UI change

## Why this matters

Absolute coordinates alone are fragile because:

- the frontmost window can change
- window positions can move
- screen scaling can change perceived layout
- a control’s visible center may not be its true hit target

## Practical commands

Use helper commands like:

- `screen-size`
- `screenshot`
- `capture-region`
- `mouse-position`
- `pixel-color --x ... --y ...`
- `move --x ... --y ...`
- `click --x ... --y ...`

## Reconstruction strategy

### 1. Global locate

Use a full screenshot to find the rough area of the app and the target control.

### 2. Region refine

Crop a smaller region around the target and reason there instead of on the full screen.

### 3. Pick an anchor point

Choose a point such as:

- center of a button
- center of a row
- center of an icon
- slightly inward from a visible border

### 4. Validate with move

Move first, then read back `mouse-position`.
If the pointer did not land where expected, stop and reassess.

### 5. Validate with UI change

A successful click must be verified by a fresh screenshot, not assumed from the command return.

## Future upgrades

Later, add OCR, text anchors, or UI detection. For MVP, coordinate reconstruction should still work with screenshot + region crop + move/readback + pixel sampling.

When OCR is available, prefer text anchors for buttons, tabs, and titles:

- run OCR on a cropped region
- match text to a query
- derive the click point from the matched text box

This reduces reliance on layout percentages when labels are visible.
