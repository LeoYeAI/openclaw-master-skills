# Mode example — architecture

## User input
The user sends a campaign reference and asks:

> 不要代码，帮我把这个新活动拆成页面模块、弹窗、状态流转和埋点方案，按 architecture mode 输出。

## Expected response shape

### Mode
architecture

### Page module plan
1. hero banner
2. campaign info bar
3. checkpoint progress strip
4. daily task section
5. reward exchange / draw zone
6. reward pool section
7. rule section
8. record entry

### Module notes
- `hero banner`: communicates theme, date, and primary CTA
- `campaign info bar`: shows time range, eligibility, and shortcut actions
- `checkpoint progress strip`: visualizes progress and unlock milestones
- `daily task section`: lists task items and task states
- `reward exchange / draw zone`: handles the main reward action
- `reward pool section`: previews available rewards
- `rule section`: contains visible summary rules and entry to full rules popup
- `record entry`: links to user history or reward records

### Popup system
- `rulePopup`
- `rewardResultPopup`
- `insufficientChancePopup`
- `checkpointUnlockPopup`

### State flow
`init -> taskUpdated -> checkpointUnlocked -> chanceReady -> actionStarted -> resultShown`

### Tracking suggestions
- `hero_cta_click`
- `task_action_click`
- `checkpoint_reward_view`
- `draw_start_click`
- `draw_result_view`
- `rules_open`

### Delivery contract hint
Suggested file layout for later delivery mode:
- `index.html`
- `styles.css`
- `main.js`
- `mock-data.js`

## What this mode should not do
- do not write large HTML/CSS/JS code blocks
- do not claim backend or API details unless the user provided them
