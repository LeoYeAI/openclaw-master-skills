# Operation Patterns

Use these as repeatable task templates.

## Pattern: Open an app and start from known state

1. check frontmost app
2. if needed, focus target app
3. capture state
4. verify the expected app is visible
5. continue with the task

## Pattern: Find a person or object in an app

When the UI has a search box, prefer search over manual scrolling.

Before clicking a candidate row, keep the target app frontmost and use move -> mouse-position -> click -> recapture instead of blind clicking.

1. capture current state
2. if target is visibly present, click it
3. otherwise locate the app search area
4. click search field
5. type target text
6. capture again
7. verify results appeared
8. click the intended result
9. capture again to verify the correct view opened

## Pattern: Send a message

1. confirm the correct conversation is open
2. if the app window can move, prefer window-relative region targeting instead of full-screen absolute points
3. derive the bottom input region from the front window when possible
4. generate 3-5 candidate points inside the input region and avoid the attachment/tool row above the text box
5. click one candidate, then recapture to verify the real text cursor landed in the text field
6. type message text
7. if a real line break is needed, run `desktop_ops.py insert-newline`
8. capture and verify the text is visible in the actual input field
9. check whether a verified visible send control exists
10. if it exists, use that explicit send control
11. otherwise, if direct-Enter-to-send is verified for the host and app, run `desktop_ops.py press --key return`
12. capture again and verify the message appears sent

For WeChat and similar chat apps, the preferred order is explicit visible send control first, verified send key second.

If the intended payload needs multiple lines, use `desktop_ops.py insert-newline` for the line break and reserve the final send action for the verified send step.

For instant-messaging apps like WeChat, do not re-capture immediately after pressing Enter. The UI may need a short fraction of a second to commit the outgoing message bubble. Standard rule: wait briefly after send (for example ~0.3-0.8s), then capture; if still ambiguous, wait until about 1 second total and capture again before declaring failure.

## Pattern: File selection flow

1. ensure file picker is frontmost
2. use search if available
3. otherwise navigate carefully one step at a time
4. capture after every meaningful navigation change
5. confirm intended file is selected
6. click open/confirm
7. capture again to verify picker closed or target app updated

## Pattern: Region-first precise interaction

Use this when the target is small or the screen is visually dense.

1. capture full screen or target app state
2. narrow to a region capture around the area of interest
3. reason over the smaller region
4. execute one action
5. recapture the region or full state and verify

## Pattern: Recovery after a failed click

1. do not keep clicking blindly
2. capture current state again
3. verify frontmost app is still correct
4. refocus if needed
5. reduce scope to a region capture
6. retry one carefully chosen step
7. if still unstable, escalate or pause

## Pattern: Right-click context menu

1. right-click target: `click --x X --y Y --button right`
2. wait 0.3s for menu to render
3. capture and OCR the context menu
4. click the target option (left-click)
5. capture and verify action result
6. if menu disappeared without action, press `escape` and retry

Context menus use absolute screen coordinates and disappear on any stray click — do not click outside the menu accidentally.

## Pattern: Drag and drop

1. identify source position (OCR or known region)
2. identify destination position
3. use `drag --x1 SX --y1 SY --x2 DX --y2 DY --duration 0.5`
4. longer `--duration` (0.5–1.0s) for apps that need sustained hold
5. capture and verify element moved
6. if drag failed, try longer duration or click-hold first

## Pattern: Multi-field form fill

1. capture form area
2. for each field: OCR label → click input → verify cursor → type value → verify
3. use `tab` key between fields when layout is vertical and sequential
4. after all fields: locate submit button → click → verify result
5. if validation error appears, OCR the error message and correct the field

## Pattern: Dropdown selection

1. click dropdown control to open
2. wait 0.2s for options to render
3. capture and OCR option list
4. click target option
5. verify dropdown shows selected value
6. if option not visible, scroll within dropdown before clicking

## Pattern: Cross-app copy-paste

1. focus source app → select content → `hotkey --keys cmd c`
2. focus destination app → click target field → `hotkey --keys cmd v`
3. capture and verify pasted content
4. always re-focus and re-get bounds when switching apps

## Pattern: Tab switching (browser/editor)

1. use keyboard shortcuts: `hotkey --keys cmd t` (new tab), `hotkey --keys cmd w` (close tab)
2. switch tabs: `hotkey --keys cmd shift ]` (next) or `hotkey --keys cmd 1` (specific tab)
3. after switching, capture and verify tab title/content via OCR
4. tab operations do not change window bounds — no need to re-get bounds

## Pattern: System settings navigation

1. focus settings app
2. prefer search if available: click search → type setting name → select result
3. if no search: OCR sidebar → click category → verify panel changed
4. re-get window bounds after deep navigation changes
5. interact with control (toggle, slider, input) → verify state changed
