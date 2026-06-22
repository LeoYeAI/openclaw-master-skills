# Mode example — delivery

## User input
The user sends one campaign reference and asks:

> 我只要更像可上线成品的前端 H5 页面，固定 H5 / Web，技术栈 HTML + CSS + JS。首屏要有美女人物主视觉，如果我没给人物图就生成一张，整体不要拉得太长，走 delivery mode。

## Expected response shape

### Mode
delivery

### Delivery notes
- keep the implementation H5/Web only
- use HTML + CSS + JavaScript only
- output a launch-ready-feeling high-fidelity draft, not a bare wireframe or starter shell
- do not claim pixel-perfect recovery from the screenshot
- summarize the likely visual language before code
- use one adult female hero figure as the dominant first-screen visual focus
- keep the female wardrobe and styling aligned with the campaign theme
- allow glamorous and slightly sexy commercial-fashion styling, while staying suitable for a public campaign page
- prefer sticky tabs when the H5 would otherwise become too long
- if the user explicitly asks for local files and Python/local execution is available, the generated front-end files may be written directly to the workspace

### File structure
- `index.html`
- `styles.css`
- `main.js`
- `mock-data.js`
- `assets/hero-figure.png` optional

### Visual extraction summary
- warm festive palette with red, gold, and cream contrast
- adult female hero in a red-dominant festive outfit with gold details and lantern accents
- first screen is anchored by the woman, title art, and a loud draw-machine device instead of a text-only layout
- content below the hero is compressed into sticky tabs rather than a long vertical stack
- modules feel like decorated panels, not plain white cards
- CTA area is loud and centered, with glow and badge support
- popup style should feel celebratory and branded

### index.html
```html
<div class="page-shell">
  <div class="page-bg-glow page-bg-glow-left"></div>
  <div class="page-bg-glow page-bg-glow-right"></div>

  <main class="festival-page">
    <section id="hero" class="hero-banner">
      <div class="hero-copy">
        <p class="hero-badge">春节限定</p>
        <h1 class="hero-title">吃瓜网春游活动</h1>
        <p class="hero-subtitle">完成每日任务赢抽奖机会，解锁限定好礼与终极红包大奖。</p>
        <div class="hero-meta">
          <span class="meta-pill">12.26 - 01.01</span>
          <span class="meta-pill">美女主理人助阵</span>
        </div>
        <div class="hero-actions">
          <button class="hero-main-cta js-open-popup" data-popup="rewardResultPopup">立即开抽</button>
          <button class="hero-secondary-cta js-switch-tab" data-tab="tasks">先做任务</button>
        </div>
      </div>

      <div class="hero-figure-wrap">
        <div class="hero-figure-glow"></div>
        <img class="hero-figure-image" src="assets/hero-figure.png" alt="春节活动美女主视觉" />
      </div>

      <aside class="hero-machine-card">
        <span class="hero-card-kicker">今日主奖</span>
        <strong class="hero-card-value">888 元新春礼盒</strong>
        <p class="hero-card-copy">完成任务可得抽奖次数，晚 20:00 额外掉落红包雨。</p>
      </aside>
    </section>

    <section class="hero-summary-panel">
      <div class="summary-chip">
        <span>当前抽奖机会</span>
        <strong>3 次</strong>
      </div>
      <div class="summary-chip">
        <span>已完成任务</span>
        <strong>2 / 5</strong>
      </div>
      <div class="summary-chip summary-chip-hot">
        <span>下一档奖励</span>
        <strong>再做 1 个任务</strong>
      </div>
    </section>

    <nav class="sticky-tabs" aria-label="活动内容导航">
      <button class="sticky-tab is-active js-switch-tab" data-tab="tasks">任务</button>
      <button class="sticky-tab js-switch-tab" data-tab="prizes">奖池</button>
      <button class="sticky-tab js-switch-tab" data-tab="rules">规则/记录</button>
    </nav>

    <section id="tab-tasks" class="tab-panel is-active"></section>
    <section id="tab-prizes" class="tab-panel"></section>
    <section id="tab-rules" class="tab-panel"></section>
  </main>
</div>

<div id="popup-root"></div>
```

### styles.css
```css
:root {
  --bg-top: #7d1018;
  --bg-bottom: #c63a2d;
  --panel-fill: linear-gradient(180deg, #fff7df 0%, #ffe8bb 100%);
  --panel-stroke: rgba(255, 245, 205, 0.84);
  --text-strong: #72140d;
  --text-soft: #9a3d22;
  --gold: #ffd46a;
  --gold-deep: #ffad2e;
  --shadow-panel: 0 18px 40px rgba(102, 12, 8, 0.22);
  --shadow-cta: 0 10px 24px rgba(171, 42, 0, 0.35);
  --radius-xl: 28px;
  --radius-lg: 22px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  color: var(--text-strong);
  background:
    radial-gradient(circle at top, rgba(255, 226, 135, 0.28), transparent 28%),
    linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bottom) 42%, #f25c38 100%);
}

.festival-page {
  max-width: 750px;
  margin: 0 auto;
  padding: 20px 16px 36px;
}

.hero-banner,
.hero-summary-panel,
.tab-panel {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-xl);
  border: 1px solid var(--panel-stroke);
  box-shadow: var(--shadow-panel);
}

.hero-banner {
  display: grid;
  grid-template-columns: 0.95fr 0.9fr 0.75fr;
  gap: 16px;
  padding: 26px 22px 22px;
  margin-bottom: 14px;
  background:
    radial-gradient(circle at top, rgba(255, 235, 159, 0.78), transparent 34%),
    linear-gradient(145deg, #a91516 0%, #d73e2f 46%, #ff874f 100%);
  color: #fff8ea;
}

.hero-figure-wrap {
  position: relative;
  min-height: 320px;
}

.hero-figure-image {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: bottom center;
}

.hero-figure-glow {
  position: absolute;
  inset: auto 12% 4% 12%;
  height: 74%;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(255, 229, 160, 0.72), rgba(255, 229, 160, 0));
}

.hero-summary-panel {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 14px;
  margin-bottom: 14px;
  background: var(--panel-fill);
}

.sticky-tabs {
  position: sticky;
  top: 0;
  z-index: 5;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 10px 0 14px;
  background: linear-gradient(180deg, rgba(125, 16, 24, 0.98), rgba(125, 16, 24, 0));
}

.sticky-tab {
  height: 44px;
  border: 0;
  border-radius: 999px;
  font-weight: 700;
  color: #ffe9b0;
  background: rgba(255, 241, 195, 0.14);
}

.sticky-tab.is-active {
  color: #7a180a;
  background: linear-gradient(180deg, #ffe59a 0%, #ffbc46 100%);
  box-shadow: var(--shadow-cta);
}

.tab-panel {
  display: none;
  padding: 18px;
  margin-bottom: 14px;
  background: var(--panel-fill);
}

.tab-panel.is-active {
  display: block;
}
```

### main.js
```javascript
document.addEventListener('DOMContentLoaded', function () {
  renderPage(window.campaignData);
  bindEvents();
  setActiveTab('tasks');
});

function renderPage(data) {
  document.getElementById('tab-tasks').innerHTML = renderTasks(data.tasks);
  document.getElementById('tab-prizes').innerHTML = renderPrizePanel(data.prizePool);
  document.getElementById('tab-rules').innerHTML = renderRulesPanel(data.rules, data.records);
}

function renderTasks(tasks) {
  return tasks.map(function (task) {
    return '<article class="task-card">' +
      '<div><p class="task-tag">' + task.tag + '</p><h3>' + task.title + '</h3><p>' + task.desc + '</p></div>' +
      '<button class="task-cta">' + task.ctaText + '</button>' +
    '</article>';
  }).join('');
}

function renderPrizePanel(prizePool) {
  return '<div class="panel-head"><h2>奖池一览</h2><span>' + prizePool.tip + '</span></div>' +
    '<div class="prize-grid">' + prizePool.items.map(function (item) {
      return '<div class="prize-chip"><span>' + item.name + '</span><b>' + item.stock + '</b></div>';
    }).join('') + '</div>';
}

function renderRulesPanel(rules, records) {
  return '<div class="panel-head"><h2>活动说明</h2><button class="text-link js-open-popup" data-popup="recordPopup">查看中奖记录</button></div>' +
    '<ol class="rules-list">' + rules.map(function (rule) {
      return '<li>' + rule + '</li>';
    }).join('') + '</ol>' +
    '<div class="record-strip">' + records.map(function (item) {
      return '<span>' + item + '</span>';
    }).join('') + '</div>';
}

function bindEvents() {
  document.querySelector('.festival-page').addEventListener('click', function (event) {
    var tabTrigger = event.target.closest('.js-switch-tab');
    if (tabTrigger) {
      setActiveTab(tabTrigger.getAttribute('data-tab'));
      return;
    }

    var popupTrigger = event.target.closest('.js-open-popup');
    if (popupTrigger) {
      openPopup(popupTrigger.getAttribute('data-popup'));
    }
  });
}

function setActiveTab(tabKey) {
  document.querySelectorAll('.sticky-tab').forEach(function (tab) {
    tab.classList.toggle('is-active', tab.getAttribute('data-tab') === tabKey);
  });

  document.querySelectorAll('.tab-panel').forEach(function (panel) {
    panel.classList.toggle('is-active', panel.id === 'tab-' + tabKey);
  });
}

function openPopup(id) {
  var popup = window.campaignData.popups.filter(function (item) {
    return item.id === id;
  })[0];

  document.getElementById('popup-root').innerHTML =
    '<div class="popup-mask is-open">' +
      '<div class="reward-popup">' +
        '<p class="popup-kicker">' + popup.kicker + '</p>' +
        '<h3>' + popup.title + '</h3>' +
        '<p>' + popup.desc + '</p>' +
      '</div>' +
    '</div>';
}
```

### mock-data.js
```javascript
window.campaignData = {
  tasks: [
    { tag: '每日任务', title: '浏览主会场 30 秒', desc: '完成后可获得 1 次抽奖机会', ctaText: '去完成' },
    { tag: '加速任务', title: '邀请好友助力 1 次', desc: '完成后额外获得 2 次抽奖机会', ctaText: '去邀请' }
  ],
  prizePool: {
    tip: '每晚 20:00 更新剩余库存',
    items: [
      { name: '888 元礼盒', stock: 'x3' },
      { name: '免单券', stock: 'x48' },
      { name: '红包雨加码卡', stock: 'x188' }
    ]
  },
  rules: [
    '活动期间每日任务可重复完成一次，奖励次日刷新。',
    '中奖结果以系统发放为准，过期不补发。'
  ],
  records: ['用户 138****8821 抽中红包', '用户 159****1688 抽中礼盒'],
  popups: [
    {
      id: 'rewardResultPopup',
      kicker: '恭喜中奖',
      title: '你获得 1 次红包雨加码机会',
      desc: '继续完成任务可解锁更高档位奖池。'
    },
    {
      id: 'recordPopup',
      kicker: '实时滚动',
      title: '中奖记录',
      desc: '最近 10 分钟已有 18 人抽中实物奖励。'
    }
  ]
};
```

## What this mode should not do
- do not switch to Vue, React, or Uni-app
- do not add backend integration claims
- do not collapse into neutral white-card scaffolding
- do not replace the requested adult female hero with a male figure by default
- do not stack every module vertically until the H5 becomes excessively long
- do not generate a full new campaign strategy unless requested elsewhere
