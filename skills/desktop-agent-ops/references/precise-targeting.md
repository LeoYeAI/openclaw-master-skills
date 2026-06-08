# Precise Targeting

Use this file when rough full-screen clicking is no longer good enough.

## Goal

Turn "I think the target is somewhere here" into a repeatable targeting process that can be reused across apps.

## Core idea

Targeting should happen in layers:

1. get the front window bounds
2. reduce the problem to a region inside that window
3. generate candidate points inside the region
4. move first, then verify live cursor position
5. click only after the pointer is where expected
6. recapture and verify the UI changed as intended

## Preferred targeting stack

### Layer 1: Window bounds

Use a front-window bounds query whenever the platform supports it.

Reason:
- screen coordinates are too global
- windows move
- app layouts are usually stable relative to the app window, not to the monitor origin

### Layer 2: Region contract

Represent a target area as:

- x
- y
- width
- height
- semantic label (optional)

Example regions:
- left sidebar list row area
- top search box area
- bottom input box area
- primary action button area

### Layer 3: Candidate points

For a region, generate a small set of candidate points instead of trusting one absolute point.

Recommended candidates:
- center
- upper-middle
- lower-middle
- left-middle inset
- right-middle inset

Use insets so the point lands inside the hit area instead of on borders.

### Layer 4: Move verification

Every candidate click should use:

1. move to point
2. read `mouse-position`
3. capture a cursor-visible screenshot when precision matters
4. compare intended point vs live mouse position vs visible cursor placement
5. only then click

### Layer 5: Post-click verification

A click is only successful if the next screenshot proves a UI change.

## Hybrid targeting extension

When precision and reliability matter, add higher-level target providers before falling back to geometry:

1. accessibility or selector provider
2. OCR or text anchor provider
3. template or image match provider
4. heuristic region provider

Each provider should output:

- target type
- confidence
- bounding box
- candidate click points
- validation hints

Use `scripts/target_resolver.py` to orchestrate this stack and return a ranked candidate.

## WeChat-specific lesson

For WeChat-like apps:

- first confirm the chat page is already open
- treat the bottom composer as a dedicated target region
- avoid the attachment/tool row above the input area
- first check for a verified visible send control
- if no verified visible send control exists, use a verified send key path only after text is visibly in the actual text input field

## Recommended reusable flow

1. focus target app
2. get front window bounds
3. define semantic region inside the window
4. capture that region
5. generate candidate points
6. move and verify one candidate
7. click
8. recapture region
9. if wrong, try the next candidate
10. once target field is confirmed, type text
11. verify text is visible where expected
12. trigger send action
13. verify sent state in the next screenshot

## What to avoid

- blind repeated clicking
- clicking near borders without inset
- using full-screen absolute coordinates when window-relative coordinates are available
- assuming focus stayed in the intended field after popups or dialogs
