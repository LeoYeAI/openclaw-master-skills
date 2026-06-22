# Mode example — analysis

## User input
The user sends 3 campaign screenshots and asks:

> 只做参考分析，不要出新活动，也不要出代码。请按 analysis mode 输出。

## Expected response shape

### Mode
analysis

### Reference analysis
Summarize what is visible across the references.

#### Observed
- mobile-first layout with a large hero section
- one dominant CTA in the upper half of the page
- reward-oriented cards below the hero area
- task or progress elements in the mid-page area
- popup-style interaction is likely part of the flow

#### Inferred
- the page is designed to convert visits into repeated task actions
- the CTA probably starts either a draw, reward claim, or exchange action
- the campaign likely relies on short feedback loops rather than long forms

#### Assumed
- detailed rules and edge-case states are hidden in popups or lower sections
- some task states exist even if the screenshot does not fully show them

### Shared pattern summary
1. hero section creates theme and urgency
2. reward value is exposed early
3. task or progress loop drives repeat action
4. popup feedback closes the reward loop

### Design and interaction notes
- visual hierarchy is top-heavy and CTA-led
- the references favor short, direct conversion paths
- module spacing suggests card-based H5 design

## What this mode should not do
- do not invent a new campaign proposal
- do not output module contracts as if implementation is already decided
- do not output HTML, CSS, or JavaScript starter files
