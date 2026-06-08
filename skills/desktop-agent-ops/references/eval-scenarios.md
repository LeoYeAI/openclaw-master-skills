# Eval Scenarios

Use this file to keep the skill public, testable, and improvable.

## Rule

Only include public-safe scenarios here.

Do not include:
- private contacts
- real account data
- sensitive conversations
- political or otherwise sensitive payloads
- machine-specific secrets

## Why this matters

Competitor systems improve because they do not stop at raw actions.
They also define repeatable scenarios, known initial states, and pass/fail checks.

## Scenario design format

Each scenario should define:

1. name
2. platform
3. target app class
4. preconditions
5. initial-state instructions
6. allowed actions
7. success criteria
8. failure hints

## Recommended public starter scenarios for macOS

### Scenario A: Focus and inspect app
- focus a target app
- capture screenshot
- confirm frontmost app and front-window bounds

### Scenario B: Search then open result
- focus app
- target top search region
- click verified candidate point
- type known safe query
- verify results change
- open first intended result

### Scenario C: Type into bottom composer
- open a safe conversation or scratch chat
- derive bottom input region from front window
- test candidate points until cursor is confirmed in text field
- type public-safe text
- verify text appears in input box

### Scenario D: Send a safe test message
- precondition: a send path is verified for the app under test
- message text must be generic and non-sensitive
- verify text appears in input box first
- if a verified visible send control exists, use it
- otherwise, if direct-Enter-to-send is verified, run `desktop_ops.py press --key return`
- wait a short fraction of a second for UI commit
- verify message bubble appears in transcript
- if the first capture is inconclusive, wait until about 1 second total and capture again

If the scenario needs a multi-line draft before sending, insert the line break with `desktop_ops.py insert-newline` instead of using a send key.

## Learning scenes to embed

The skill should include learning scenes in increasing difficulty:

1. focus-only
2. bounds-only
3. region capture
4. candidate-point click
5. text entry
6. send action
7. recovery from popup/dialog
8. multi-step app workflow

## Public-safe macOS WeChat test

For a public skill, define the WeChat example generically:
- use a clearly safe contact in a test account
- use a neutral payload such as `hello from desktop agent`
- never hardcode private names or IDs into the skill itself

## Evaluation style borrowed from strong competitors

From benchmark-style systems, keep these ideas:
- reproducible initial state
- execution-based verification
- task-specific success checks
- explicit exclusions for tasks that require private accounts or unstable network state
