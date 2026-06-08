# Example Cases

Use this reference for public-safe, repeatable desktop operation examples.

## Rule

All examples here must be:
- public-safe
- generic
- reproducible
- free of private identities, secrets, or sensitive content

Each case should be read as a reusable pattern, not a one-off script.

## Case format

Each example includes:
1. goal
2. target app type
3. preconditions
4. workflow
5. validation points
6. failure recovery

---

## Case 1: Focus an app and confirm the correct window

### Goal
Bring a target app to the foreground and confirm the active window is correct.

### Target app type
Any desktop app.

### Preconditions
- app is installed
- the app can be activated normally

### Workflow
1. focus target app
2. obtain front-window bounds
3. capture current screen
4. confirm the frontmost app matches expectation
5. confirm the visible window matches expectation

### Validation points
- app is frontmost
- window bounds are available
- screenshot matches the intended app
- when precision matters, the report should include window bounds, region bounds, candidate points, and live mouse coordinates

### Failure recovery
- refocus app
- recapture
- if still ambiguous, resize/reposition window and try again

---

## Case 2: Select a conversation in a chat app and verify target correctness

### Goal
Switch into the intended conversation before typing or sending.

### Target app type
Chat app on desktop.

### Preconditions
- target app is frontmost
- left conversation list is visible

### Workflow
1. obtain front-window bounds
2. derive the conversation list region
3. click the intended conversation row
4. capture again
5. confirm conversation title/header matches the intended target
6. confirm visible transcript context is compatible with the intended target

### Validation points
- title/header is correct
- transcript context is correct
- selected state appears consistent with the chosen conversation

### Failure recovery
- do not send anything
- recapture and retry selection
- use search instead of manual list scanning if available

---

## Case 3: Type into the true input field instead of the toolbar

### Goal
Ensure text goes into the actual composer or input field.

### Target app type
Chat app, editor, browser form, or search UI.

### Preconditions
- active window has been verified
- input region can be derived from the window

### Workflow
1. derive the input region relative to the window
2. generate candidate points in the region
3. click candidate point
4. type sample text
5. capture again
6. confirm the text is in the true input field

### Validation points
- typed text is visible where expected
- no attachment, toolbar, or popup UI was triggered accidentally

### Failure recovery
- clear misfocused UI if needed
- derive input region again
- click a lower or more central candidate point and retry

---

## Case 4: Send a safe test message in a chat app

### Goal
Send a public-safe test message only after the correct conversation and input field are verified.

### Target app type
Desktop chat app.

### Preconditions
- correct conversation already verified
- typed text is visible in the true composer
- at least one send path is verified: visible send button or verified send key behavior

### Workflow
1. type neutral safe text
2. if a literal line break is needed, use `desktop_ops.py insert-newline`
3. verify text is visible in the composer
4. check whether a verified visible send control exists
5. if it exists, use that explicit send control
6. otherwise, if direct-Enter-to-send is verified, run `desktop_ops.py press --key return`
7. wait briefly for UI commit
8. capture again
9. if needed, capture once more after about 1 second total
10. confirm the outgoing message bubble appears

### Validation points
- typed text existed before send
- outgoing bubble appears after send
- message appears in the correct conversation

### Failure recovery
- do not assume success from keypress return values alone
- recapture and verify active conversation again
- confirm the visible send control or verified send key path before retrying

If the message body needs multiple lines, insert the line break with `desktop_ops.py insert-newline` before the final send action.

---

## Case 5: Search inside an app instead of manually scanning

### Goal
Use in-app search to reduce random clicks and unstable scrolling.

### Target app type
Any app with a search UI.

### Preconditions
- app is focused
- search region is visible or reachable

### Workflow
1. derive top search region
2. click inside the search field
3. verify text cursor or active field state
4. type query
5. capture again
6. confirm search results changed
7. select intended result and verify target correctness

### Validation points
- search field accepted input
- result list changed as expected
- selected result matches intended target

### Failure recovery
- clear the field and retry once
- if search UI is ambiguous, recapture only the top region

---

## Case 6: Open a file in a file manager

### Goal
Find and open a target file using visible GUI state.

### Target app type
Finder or other file manager.

### Preconditions
- file manager window is active
- search field or list view is visible

### Workflow
1. focus file manager
2. verify front window
3. use search if available
4. verify result row or filename
5. double-click or open the file
6. capture again
7. verify the expected file or app opened

### Validation points
- selected row matches file name expectation
- resulting window or app matches intended file open action

### Failure recovery
- return to the file manager
- narrow search scope
- verify file row again before opening

---

## Case 7: Handle a popup or permission dialog safely

### Goal
Recover from unexpected dialogs without causing side effects.

### Target app type
Any desktop app.

### Preconditions
- a popup or dialog is visible

### Workflow
1. capture the dialog
2. identify whether it is expected or unexpected
3. derive the dialog button region
4. choose the safest valid action
5. click once
6. capture again
7. verify the dialog closed or the intended next state appeared

### Validation points
- dialog type understood well enough
- chosen button matches the intended recovery action
- post-dialog state is correct

### Failure recovery
- prefer cancel, close, or deny when intent is unclear
- stop rather than guessing on destructive dialogs

---

## Case 8: Browser-like navigation with verification

### Goal
Operate a browser or browser-like desktop app via visible GUI patterns.

### Target app type
Desktop browser or embedded browser shell.

### Preconditions
- browser window active
- page content visible

### Workflow
1. verify app and window
2. validate page title or visible page context
3. derive action region
4. click link/button/input
5. capture again
6. confirm intended page or state transition occurred

### Validation points
- visible page context is correct before action
- visible page context changed correctly after action

### Failure recovery
- avoid repeated blind clicks
- refresh the visible context by recapturing before retrying

---

## Case 9: Closed software with no usable API

### Goal
Operate software entirely through visible GUI state.

### Target app type
Closed desktop app with no integration path.

### Preconditions
- app can be focused
- window bounds can be obtained

### Workflow
1. focus app
2. obtain window bounds
3. derive region from visible layout
4. move and verify pointer position
5. click or type one step
6. capture again
7. validate outcome
8. continue one step at a time

### Validation points
- each action is locally verified
- no blind global-coordinate sequences are used

### Failure recovery
- rebuild the region from the window
- reduce scope to smaller captures
- do not chain unverified actions

---

## Case 10: End-to-end chat reply with context compatibility

### Goal
Read visible context from a chat, compose a compatible reply, and send only after full validation.

### Target app type
Desktop chat app.

### Preconditions
- app focused
- target conversation verified
- visible transcript readable enough for context

### Workflow
1. select and verify conversation
2. read recent visible context
3. draft a compatible public-safe reply
4. click verified composer region
5. type reply
6. verify text in composer
7. send
8. wait briefly
9. capture again
10. verify outgoing bubble in the same conversation

### Validation points
- reply is context-compatible
- conversation remained correct throughout
- outgoing message appears in the verified conversation

### Failure recovery
- if conversation correctness is lost, stop and revalidate before retrying
- if send verification is ambiguous, use delayed second capture

---

## Case 11: Launch a desktop controller app and batch-start all tasks

### Goal
Open a launcher/controller app, verify the correct window, and start all listed tasks or tunnels.

### Target app type
Desktop launcher, controller, proxy manager, tunnel manager, or similar utility app.

### Preconditions
- the app is installed and launchable
- the app window can be focused
- the task list or tunnel list is visible after opening

### Workflow
1. focus or launch the target app
2. obtain front-window bounds
3. verify the active window title matches the intended app
4. derive the list region and the primary action region relative to the window
5. inspect whether tasks are already running or stopped
6. locate the global start-all action if present; otherwise iterate over visible stopped items one by one
7. after each start action, wait briefly and capture again
8. verify status indicators changed to running/active
9. if scrolling is needed, scroll the list and continue with validation at each step

### Validation points
- active app and window are correct
- the list belongs to the intended launcher/controller app
- each started task shows a running/active state
- no unexpected error dialog remains open

### Failure recovery
- if the wrong utility window is active, refocus and revalidate before any click
- if start-all is not obvious, prefer verified per-item start over guessing a toolbar button
- if an error dialog appears, capture it and choose the safest recovery path before continuing

---

## Case 12: Right-click context menu operation

### Goal
Right-click an element to open a context menu and select an option.

### Target app type
Any desktop app with context menus (file manager, browser, editor, etc.).

### Preconditions
- target element is visible
- window bounds are known

### Workflow
1. focus target app
2. locate target element via OCR or coordinates
3. right-click: `desktop_ops.py click --x X --y Y --button right`
4. wait 0.3s for menu to appear
5. capture screenshot
6. OCR the context menu to find the target option
7. click the menu option (left-click)
8. capture again and verify the action took effect

### Validation points
- context menu appeared after right-click
- correct menu option was identified
- action result is visible (e.g., file renamed, item deleted, etc.)

### Failure recovery
- if menu didn't appear, re-right-click
- if wrong menu appeared, press Escape to dismiss and retry
- context menu coordinates are absolute — do NOT reuse old coordinates after menu dismiss

---

## Case 13: Drag and drop between locations

### Goal
Drag a file, UI element, or selection from one position to another.

### Target app type
File manager, editor, kanban board, or any drag-enabled UI.

### Preconditions
- source and destination positions are known
- window bounds are current

### Workflow
1. focus target app
2. locate source element (OCR or known position)
3. locate destination area
4. execute: `desktop_ops.py drag --x1 SX --y1 SY --x2 DX --y2 DY --duration 0.5`
5. use longer `--duration` (0.5–1.0s) for apps that need sustained hold to register drag
6. capture again
7. verify the element moved to the destination

### Validation points
- source element is no longer at original position
- element appears at destination
- no error dialog appeared

### Failure recovery
- if drag failed, try longer `--duration`
- ensure source was correctly identified before retrying
- some apps require clicking source first, holding briefly, then dragging — add a separate click+hold step

---

## Case 14: Navigate system settings (multi-panel)

### Goal
Open system settings, navigate to a specific panel, and change a setting.

### Target app type
System Settings (macOS), Settings (Windows), or similar preferences app.

### Preconditions
- settings app can be focused

### Workflow
1. focus settings app: `focus-app --name "System Settings"` (macOS) or `focus-app --name "Settings"` (Windows)
2. capture and verify the correct settings window
3. if search is available, use it: click search field → type setting name → select result
4. if no search, navigate sidebar: OCR sidebar → click target category
5. after each navigation, capture and verify the panel changed
6. locate the target control (toggle, dropdown, input field)
7. interact with the control
8. capture and verify the change

### Validation points
- correct settings panel is visible
- control state changed as expected
- no unsaved-changes dialog blocks exit

### Failure recovery
- settings panels can be deep — always re-get window bounds after navigation
- if lost in navigation, use search or go back to main settings list
- some settings require admin/password — handle the auth dialog if it appears

---

## Case 15: Fill a multi-field form

### Goal
Fill out multiple fields in a form (registration, login, data entry).

### Target app type
Browser form, desktop app form, or dialog with multiple inputs.

### Preconditions
- form is visible
- field labels are readable

### Workflow
1. capture the form area
2. for each field:
   a. OCR to find the field label
   b. click the input area next to/below the label
   c. verify cursor is in the correct field (capture)
   d. clear existing content if needed: `hotkey --keys cmd a` then `press --key delete`
   e. type the value: `type --text "value"`
   f. capture and verify text is in the right field
3. after all fields are filled, locate the submit button
4. click submit
5. capture and verify form submitted successfully

### Validation points
- each field contains the correct value
- no field was accidentally skipped or double-filled
- submit action triggered the expected result

### Failure recovery
- if text goes to wrong field, clear it, re-locate the correct field
- Tab key can navigate between fields: `press --key tab`
- if form validation fails, capture error messages and correct the fields

---

## Case 16: Select from a dropdown or combo box

### Goal
Open a dropdown menu and select a specific option.

### Target app type
Any app with dropdown/select controls.

### Preconditions
- dropdown control is visible

### Workflow
1. locate the dropdown control via OCR or region
2. click to open the dropdown
3. wait 0.2s for options to appear
4. capture the dropdown list
5. OCR to find the target option
6. click the target option
7. capture and verify the dropdown now shows the selected value

### Validation points
- dropdown opened and showed options
- correct option was selected
- dropdown closed and displays the new value

### Failure recovery
- if dropdown didn't open, click again
- if target option is not visible, scroll within the dropdown: `scroll --amount -3 --x X --y Y`
- if wrong option selected, re-open and re-select

---

## Case 17: Toggle a switch or adjust a slider

### Goal
Toggle an on/off switch or drag a slider to a target value.

### Target app type
Settings panel, preferences dialog, audio/video controls.

### Preconditions
- control is visible

### Workflow (toggle):
1. locate the toggle via OCR (look for label text near it)
2. click the toggle control
3. capture and verify state changed (color change, position change, label change)

### Workflow (slider):
1. locate the slider track and current handle position
2. calculate target position on the track
3. drag from current handle to target: `drag --x1 HX --y1 HY --x2 TX --y2 HY --duration 0.3`
4. capture and verify slider moved to expected position

### Validation points
- toggle: visual state changed (on↔off)
- slider: handle position changed, associated value updated

### Failure recovery
- toggles may need double-click on some platforms
- sliders may need precise coordinates — use capture-region to narrow down

---

## Case 18: Switch between multiple apps (cross-app workflow)

### Goal
Copy content from one app and paste it into another.

### Target app type
Any two desktop apps.

### Preconditions
- both apps are running

### Workflow
1. focus source app: `focus-app --name "SourceApp"`
2. get window bounds
3. locate and select source content (click, or Cmd+A)
4. copy: `hotkey --keys cmd c`
5. focus destination app: `focus-app --name "DestApp"`
6. get window bounds
7. click target input field
8. paste: `hotkey --keys cmd v`
9. capture and verify content was pasted

### Validation points
- source content was selected before copy
- destination field received the content
- content matches expected value

### Failure recovery
- if paste shows nothing, re-copy from source
- verify focus is correct before each hotkey
- clipboard content can be checked via `pbpaste` (macOS) or PowerShell `Get-Clipboard` (Windows)

---

## Case 19: Browser tab management

### Goal
Open, switch between, or close browser tabs.

### Target app type
Desktop browser (Chrome, Safari, Firefox, Edge).

### Preconditions
- browser is focused

### Workflow (open new tab):
1. `hotkey --keys cmd t` (macOS) or `hotkey --keys ctrl t` (Windows/Linux)
2. type URL: `type --text "https://example.com"`
3. `press --key return`
4. capture and verify page loaded

### Workflow (switch tab):
1. to go to next tab: `hotkey --keys cmd shift ]` (macOS) or `hotkey --keys ctrl tab`
2. to go to specific tab: `hotkey --keys cmd 1` (first tab), `cmd 2` (second), etc.
3. capture and verify correct tab is active

### Workflow (close tab):
1. `hotkey --keys cmd w` (macOS) or `hotkey --keys ctrl w`
2. capture and verify tab closed

### Validation points
- correct tab is active (verify title or URL content via OCR)
- page content matches expected state

### Failure recovery
- if wrong tab, use Cmd+Z/Ctrl+Z to reopen closed tab
- capture tab bar area to count/identify open tabs
