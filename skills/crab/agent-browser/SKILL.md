---
name: agent-browser
description: |
  Browser automation tool. Used to capture project websites, DApp pages and
  other JS-rendered content, extract page text and interactive elements, and
  assist with research-oriented data collection.
metadata:
  author: NotevenDe
  version: 1.1.0
  requires:
    bins: [node, npm, agent-browser]
---

# Agent Browser — Page Crawling and Data Extraction

## Installation

CLAWBOT must ensure agent-browser is available before any browsing task:

```bash
which agent-browser || npm install -g agent-browser
agent-browser install
```

## Purpose

CLAWBOT uses this in Research Step 2 (explore & collect) when it encounters
pages that require JS rendering.
Suitable for: project official websites, DApp pages, and dynamic pages on
aggregator platforms.

## Core Workflow

```bash
# 1. Open & wait
agent-browser open <url>
agent-browser wait --load networkidle

# 2. Snapshot — get interactive elements with @refs
agent-browser snapshot -i

# 3. Extract content
agent-browser get text @e1         # element text
agent-browser get html @e1         # innerHTML
agent-browser get attr @e1 href    # attribute
agent-browser get title            # page title
agent-browser get url              # current URL
agent-browser get count ".item"    # count matching elements

# 4. Interact
agent-browser click @e1            # click
agent-browser fill @e2 "keyword"   # fill input (clears first)
agent-browser scroll down 500      # scroll
agent-browser scrollintoview @e1   # scroll element into view
agent-browser press Enter          # press key

# 5. Capture evidence
agent-browser screenshot --full    # full-page screenshot
agent-browser pdf output.pdf       # save as PDF

# 6. Close
agent-browser close
```

## Wait Strategies

```bash
agent-browser wait @e1                  # wait for element
agent-browser wait 2000                 # wait milliseconds
agent-browser wait --text "Success"     # wait for text
agent-browser wait --url "/dashboard"   # wait for URL pattern
agent-browser wait --load networkidle   # wait for network idle
```

## Semantic Locators (alternative to @refs)

```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
```

## Output Format

Add `--json` for structured output:

```bash
agent-browser snapshot -i --json
agent-browser get text @e1 --json
```

## Notes

- `@ref` changes after page navigation; always re-snapshot
- Use `fill` for inputs (clears old value), not `type`
- For dynamic pages, `wait --load networkidle` before `snapshot`
- Use `--headed` to see the browser window for debugging
