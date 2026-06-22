# Example output

## Mode
full

## Reference analysis
The references are all mobile-first campaign pages built around a festive hero area, a reward CTA, and a task-to-reward loop.

### Observed
- prominent hero/banner at the top
- date range near the title
- one primary CTA in the core area
- task list and reward explanation below the fold
- popup-oriented reward feedback is strongly implied

### Inferred
- users complete tasks to earn draw chances or points
- the main CTA likely opens a lottery flow or reward exchange flow
- popup states probably include success, failure, and rule details

### Assumed
- task completion status needs three states: todo / done / claimed
- there is a record/history entry near the lottery area
- some small rules exist but are not fully readable

## Gameplay abstraction
Common pattern extracted from the references:
1. attract with hero theme
2. explain reward value quickly
3. drive task completion
4. convert task progress into chances or points
5. show reward feedback in popup form

## New campaign proposal
### Name
Spring Benefit Relay

### Goal
Boost short-term activity and repeat visits during a seasonal campaign window.

### Main idea
Instead of a direct copy of the original draw page, this version changes:
- the theme: from generic lucky draw to relay challenge
- the reward design: from flat prize display to milestone rewards + final draw
- the task structure: from isolated tasks to staged daily tasks
- the core interaction: progress unlocks reward stages before the final CTA

### Participation path
Visit page → complete daily tasks → unlock milestone cards → earn final draw chances → open result popup

## Page architecture
### Modules
1. hero banner
2. campaign meta bar
3. progress milestone strip
4. daily task list
5. final draw area
6. reward pool
7. rules section
8. history entry

### Popups
- rule popup
- reward result popup
- insufficient chance popup
- milestone unlocked popup

### State flow
`init -> taskUpdated -> milestoneUnlocked -> chanceReady -> drawing -> resultShown`

### Tracking suggestions
- hero_cta_click
- task_claim_click
- milestone_open
- draw_start_click
- draw_result_view

## Delivery schema
See `campaign-schema-example.json` for one possible contract.

## Visual direction
- warm red-gold festive palette with dense decorative layering
- high-contrast hero, framed content panels, and a glossy CTA area
- chips, badges, progress nodes, and prize cards instead of empty placeholders

## H5/Web starter files
### index.html
```html
<div class="campaign-shell">
  <section id="hero" class="hero-banner">
    <div class="hero-copy">
      <span class="hero-kicker">春日活动主会场</span>
      <h1>Spring Benefit Relay</h1>
      <p>完成任务点亮里程碑，领取阶段奖励并解锁终极抽奖。</p>
    </div>
    <div class="hero-highlight-card">
      <p>终极奖励</p>
      <strong>限量惊喜礼包</strong>
    </div>
  </section>
  <section id="milestones" class="feature-panel"></section>
  <section id="tasks" class="feature-panel"></section>
  <section id="draw-zone" class="feature-panel feature-panel-highlight"></section>
  <section id="rewards" class="feature-panel"></section>
  <section id="rules" class="feature-panel"></section>
</div>
<div id="popup-root"></div>
```

### styles.css
```css
:root {
  --bg-main: linear-gradient(180deg, #8d101a 0%, #d74b35 48%, #ff8e4d 100%);
  --panel-fill: linear-gradient(180deg, #fff8e8 0%, #ffe7af 100%);
}

body { margin: 0; background: var(--bg-main); }
.campaign-shell { max-width: 750px; margin: 0 auto; padding: 16px; }
.hero-banner,
.feature-panel { border-radius: 28px; overflow: hidden; }
.hero-banner { padding: 24px; background: linear-gradient(135deg, #a40f1a 0%, #f06a3e 100%); }
.feature-panel { margin-top: 14px; padding: 18px; background: var(--panel-fill); }
.feature-panel-highlight { background: linear-gradient(180deg, #fff2c5 0%, #ffd672 100%); }
.popup-mask { position: fixed; inset: 0; display: none; }
```

### main.js
```javascript
document.addEventListener('DOMContentLoaded', function () {
  renderPage(window.campaignData);
  bindEvents();
});

function bindEvents() {
  document.getElementById('draw-zone').addEventListener('click', function (event) {
    if (!event.target.closest('.js-start-draw')) {
      return;
    }

    openPopup('rewardResult');
  });
}
```

### mock-data.js
```javascript
window.campaignData = {
  campaignMeta: { title: 'Spring Benefit Relay' },
  tasks: [
    { id: 'sign', title: '每日签到', ctaText: '去完成' }
  ],
  rewards: [
    { id: 'gift-1', title: '里程碑礼包' }
  ],
  popups: [
    { id: 'rewardResult', title: '恭喜获得阶段奖励' }
  ]
};
```

## Uncertainties
- microcopy in small rule text is low confidence
- exact prize probabilities are not visible from the references
