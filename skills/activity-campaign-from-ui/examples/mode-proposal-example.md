# Mode example — proposal

## User input
The user sends 2 seasonal campaign screenshots and asks:

> 参考这两个活动页的方向，给我出一个新的 H5 活动策划。产物要更像运营活动视觉稿，不要写代码。如果可以，顺手用 Python 在本地生成一个 proposal PPT，走 proposal mode。

## Expected response shape

### Mode
proposal

### Proposal notes
- keep the result in proposal mode and do not switch to front-end delivery
- make the output read like an operations campaign visual deck rather than a plain memo
- lead with campaign hook, hero concept, visual direction, and reward hook
- if the user explicitly asks for a local deck and Python/local execution is available, `campaign-proposal.pptx` may be generated in the workspace

### File targets
- `campaign-proposal.md`
- `campaign-proposal.pptx` optional local artifact when explicitly requested and supported

### Brief reference summary
The references use a reward-first seasonal layout with task-driven engagement.

#### Observed
- both references place the main reward promise near the top
- both use short task lists and clear CTA areas
- both imply popup-based result feedback

#### Inferred
- the references are built for quick participation and repeat visits
- the primary conversion goal is likely task completion followed by reward action

#### Assumed
- detailed rules, reward limits, and edge states are not fully visible

### New campaign proposal
#### Name
Spring Lucky Route

#### Goal
Increase short-term user activity during a limited campaign window.

#### Core idea
Instead of directly repeating a simple draw page, this proposal changes:
- the theme: from a generic festive draw to a route-unlock challenge
- the reward mechanism: from one-shot draw emphasis to checkpoint rewards plus a final draw
- the task structure: from flat tasks to staged progress tasks

#### Visual direction
- festive hero art with a stronger campaign hook and poster-like headline treatment
- high-contrast seasonal palette matched to the target holiday
- reward promise shown early as a visual key message rather than buried in long copy
- module rhythm presented like deck slides or campaign boards, not like an implementation spec

#### Participation path
Visit page → complete daily tasks → unlock route checkpoints → collect checkpoint rewards → use final draw chances

#### Reward design
- checkpoint rewards for early participation
- extra rewards for consecutive task completion
- final draw rewards for users who complete progress goals

#### Why it is not a copy
At least 2 of the 4 anti-copy dimensions are changed:
- changed reward mechanism
- changed task structure
- changed core interaction path

## What this mode should not do
- do not output a full page module contract unless the user asks for architecture mode
- do not output starter code files
- do not reduce the output to a plain strategy memo with no visual campaign framing
