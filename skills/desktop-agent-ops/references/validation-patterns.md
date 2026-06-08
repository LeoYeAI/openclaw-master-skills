# Validation Patterns

Use this reference for any desktop task where acting on the wrong target would cause visible mistakes.

## Principle

Do not treat action success as task success.

A desktop action is only valid when both are true:
1. the target before the action is confirmed correct
2. the outcome after the action is confirmed correct

## Two-stage validation

### Stage 1: Target validation

Before clicking or typing, confirm the target object is correct.

Preferred validation signals:
- target app is frontmost
- front-window bounds are known
- target region is derived relative to the window
- expected title or header matches
- expected list row or selected state matches
- expected content context matches
- cursor-visible capture shows the pointer inside the intended target region when click precision matters

### Stage 2: Outcome validation

After the action, capture again and confirm the intended effect happened.

When click precision matters, prefer a structured verification bundle that includes:
- window bounds
- region bounds
- candidate points
- live mouse coordinates
- pre-click cursor-visible capture
- post-click cursor-visible capture

Preferred outcome signals:
- screen changed in the expected area
- title changed as expected
- text appears in the intended input field
- selected row changed
- sent message bubble appears
- popup closed or expected dialog appeared

When possible, verify outcome with region-level diff:

- capture pre-click and post-click frames
- compute a diff score in the target region
- fail the action if the region did not change as expected

Use `scripts/region_diff.py` to implement this check.

## Hard safety rule

If target validation fails, do not continue with destructive or user-visible actions.

That includes:
- sending a message
- deleting an item
- moving a file
- confirming a dialog
- clicking a primary action button

## Chat app pattern

For chat apps, validation must include all of these before send:
- app is correct
- window is correct
- active conversation title matches expected chat
- visible context looks like the intended conversation
- input text is visible in the true composer, not the toolbar or attachment row

## Browser-like pattern

For browser-like apps, validation should include:
- target tab/window is correct
- visible page title or URL-equivalent cue matches intent
- action region is correct

## Recovery order

If validation fails:
1. recapture current state
2. refocus app
3. reacquire window bounds
4. derive region again
5. retry one action only
6. escalate or stop if still ambiguous
