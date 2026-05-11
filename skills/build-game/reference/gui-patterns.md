# GUI / HUD Design Patterns

Premium-quality UI patterns for browser games. Every game should have polished, readable, responsive UI. These patterns use CSS-only effects (no images) for crisp rendering at any resolution.

## Design Principles

1. **Glassmorphism over solid backgrounds** — use `backdrop-filter: blur()` with semi-transparent backgrounds
2. **Consistent spacing** — use a 4px/8px grid system
3. **Readable at a glance** — large numbers, high contrast, clear hierarchy
4. **Animated transitions** — never snap, always ease
5. **Layered information** — primary info always visible, secondary on hover/press
6. **Responsive** — percent/vw/vh units, not fixed pixels for layout
7. **Pointer-events: none** on HUD container, **pointer-events: auto** only on interactive elements

## Base HUD Container

```html
<style>
    #hud {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; z-index: 10;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }
    #hud * { pointer-events: none; }
    .hud-panel {
        background: rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px 16px;
        color: #fff;
    }
    .hud-panel-dark {
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px 16px;
        color: #fff;
    }
    .hud-label {
        font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px;
        color: rgba(255,255,255,0.5); margin-bottom: 4px;
    }
    .hud-value {
        font-size: 28px; font-weight: 700; line-height: 1;
        font-variant-numeric: tabular-nums;
    }
    .hud-value-sm { font-size: 18px; font-weight: 600; }
    .hud-accent { color: #60a5fa; }
    .hud-warn { color: #fbbf24; }
    .hud-danger { color: #ef4444; }
    .hud-success { color: #4ade80; }
</style>
```

## Health Bar (Premium)

```html
<div id="health-container" style="position:absolute; bottom:24px; left:24px;">
    <div class="hud-label">HEALTH</div>
    <div style="position:relative; width:220px; height:14px; background:rgba(0,0,0,0.5); border-radius:7px; overflow:hidden; border:1px solid rgba(255,255,255,0.08);">
        <!-- Background damage flash (shows briefly when hit) -->
        <div id="health-damage" style="position:absolute; width:100%; height:100%; background:#ef4444; border-radius:7px; transition:width 0.5s ease-out;"></div>
        <!-- Actual health -->
        <div id="health-fill" style="position:absolute; width:100%; height:100%; border-radius:7px; transition:width 0.25s ease-out;
            background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%);
            box-shadow: 0 0 8px rgba(74,222,128,0.3);"></div>
        <!-- Shine overlay -->
        <div style="position:absolute; top:0; left:0; width:100%; height:50%; border-radius:7px 7px 0 0;
            background: linear-gradient(180deg, rgba(255,255,255,0.15) 0%, transparent 100%);"></div>
    </div>
    <div id="health-text" style="font-size:13px; color:rgba(255,255,255,0.7); margin-top:3px; font-variant-numeric:tabular-nums;">100 / 100</div>
</div>
```

```javascript
// Health bar with damage flash effect
function updateHealthBar(current, max) {
    const pct = (current / max) * 100;
    document.getElementById('health-fill').style.width = pct + '%';
    document.getElementById('health-text').textContent = `${current} / ${max}`;
    // Color shifts based on health level
    const fill = document.getElementById('health-fill');
    if (pct > 60) {
        fill.style.background = 'linear-gradient(90deg, #22c55e, #4ade80)';
        fill.style.boxShadow = '0 0 8px rgba(74,222,128,0.3)';
    } else if (pct > 30) {
        fill.style.background = 'linear-gradient(90deg, #eab308, #fbbf24)';
        fill.style.boxShadow = '0 0 8px rgba(251,191,36,0.3)';
    } else {
        fill.style.background = 'linear-gradient(90deg, #dc2626, #ef4444)';
        fill.style.boxShadow = '0 0 8px rgba(239,68,68,0.4)';
    }
}
// On damage: briefly show the damage flash bar lagging behind
function flashDamage(prevPct) {
    const dmgBar = document.getElementById('health-damage');
    dmgBar.style.width = prevPct + '%';
    dmgBar.style.transition = 'none';
    requestAnimationFrame(() => {
        dmgBar.style.transition = 'width 0.5s ease-out';
        dmgBar.style.width = document.getElementById('health-fill').style.width;
    });
}
```

## Score Display

```html
<div id="score-panel" class="hud-panel" style="position:absolute; top:20px; right:20px; text-align:right; min-width:120px;">
    <div class="hud-label">SCORE</div>
    <div class="hud-value" id="score-value" style="color:#ffd700;">0</div>
</div>
```

```javascript
// Animated score counter (counts up smoothly)
let displayedScore = 0;
function updateScore(targetScore, delta) {
    if (displayedScore < targetScore) {
        displayedScore += Math.ceil((targetScore - displayedScore) * 8 * delta);
        if (displayedScore > targetScore) displayedScore = targetScore;
    }
    document.getElementById('score-value').textContent = displayedScore.toLocaleString();
}
// Score pop on increase
function scorePopEffect() {
    const el = document.getElementById('score-value');
    el.style.transform = 'scale(1.3)';
    el.style.transition = 'transform 0.1s ease-out';
    setTimeout(() => {
        el.style.transition = 'transform 0.3s ease-out';
        el.style.transform = 'scale(1)';
    }, 100);
}
```

## Timer (Racing / Speedrun)

```html
<div id="timer-panel" class="hud-panel" style="position:absolute; top:20px; left:50%; transform:translateX(-50%); text-align:center;">
    <div id="timer-value" style="font-size:38px; font-weight:800; font-variant-numeric:tabular-nums; letter-spacing:1px; color:#fff; text-shadow: 0 0 12px rgba(100,180,255,0.3);">0:00.000</div>
    <div id="timer-penalty" style="font-size:14px; color:#ef4444; height:18px;"></div>
</div>
```

## Speedometer (Racing)

```html
<div id="speed-panel" style="position:absolute; bottom:24px; left:24px;">
    <div class="hud-panel" style="text-align:center; min-width:130px;">
        <div class="hud-value" id="speed-num" style="font-size:42px;">0</div>
        <div style="font-size:12px; color:rgba(255,255,255,0.4); letter-spacing:2px; margin-top:-2px;">KM/H</div>
    </div>
    <!-- Speed bar underneath -->
    <div style="width:130px; height:4px; background:rgba(255,255,255,0.1); border-radius:2px; margin-top:8px; overflow:hidden;">
        <div id="speed-fill" style="height:100%; width:0%; border-radius:2px; transition:width 0.15s;
            background: linear-gradient(90deg, #60a5fa, #f472b6);"></div>
    </div>
</div>
```

## Crosshair (FPS)

```html
<!-- Minimal dot + lines crosshair that spreads on firing -->
<div id="crosshair" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:0; height:0;">
    <!-- Center dot -->
    <div style="position:absolute; top:-2px; left:-2px; width:4px; height:4px; background:#fff; border-radius:50%; box-shadow:0 0 4px rgba(255,255,255,0.5);"></div>
    <!-- Lines (gap controlled by CSS variable) -->
    <div class="ch-line" style="position:absolute; left:-1px; bottom:6px; width:2px; height:12px; background:rgba(255,255,255,0.8); border-radius:1px;
        transform:translateY(calc(-1 * var(--ch-spread, 0px)));"></div>
    <div class="ch-line" style="position:absolute; left:-1px; top:6px; width:2px; height:12px; background:rgba(255,255,255,0.8); border-radius:1px;
        transform:translateY(var(--ch-spread, 0px));"></div>
    <div class="ch-line" style="position:absolute; top:-1px; right:6px; width:12px; height:2px; background:rgba(255,255,255,0.8); border-radius:1px;
        transform:translateX(calc(-1 * var(--ch-spread, 0px)));"></div>
    <div class="ch-line" style="position:absolute; top:-1px; left:6px; width:12px; height:2px; background:rgba(255,255,255,0.8); border-radius:1px;
        transform:translateX(var(--ch-spread, 0px));"></div>
</div>
<style>
    #crosshair { --ch-spread: 0px; transition: --ch-spread 0.1s ease-out; }
</style>
```

```javascript
// Spread crosshair on fire, recover over time
function crosshairFire() {
    document.getElementById('crosshair').style.setProperty('--ch-spread', '8px');
    setTimeout(() => document.getElementById('crosshair').style.setProperty('--ch-spread', '0px'), 80);
}
```

## Hit Marker

```html
<style>
    #hit-marker {
        position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
        width:24px; height:24px; opacity:0; transition: opacity 0.05s;
    }
    #hit-marker.active { opacity:1; }
    #hit-marker::before, #hit-marker::after {
        content:''; position:absolute; background:#fff;
    }
    #hit-marker::before {
        width:2px; height:10px; top:0; left:11px; transform:rotate(45deg);
    }
    #hit-marker::after {
        width:2px; height:10px; bottom:0; left:11px; transform:rotate(-45deg);
    }
    /* Kill confirmed variant (red X) */
    #hit-marker.kill::before, #hit-marker.kill::after { background:#ef4444; height:14px; }
</style>
```

## Kill Feed

```html
<div id="kill-feed" style="position:absolute; top:70px; right:20px; display:flex; flex-direction:column; gap:4px; max-width:280px;"></div>
<style>
    .kill-entry {
        background: rgba(0,0,0,0.4); backdrop-filter:blur(6px);
        padding:6px 12px; border-radius:8px; font-size:13px; color:#fff;
        border-left:3px solid #ffd700;
        animation: killSlideIn 0.3s ease-out, killFadeOut 0.5s ease-in 2.5s forwards;
    }
    @keyframes killSlideIn { from { opacity:0; transform:translateX(30px); } to { opacity:1; transform:translateX(0); } }
    @keyframes killFadeOut { to { opacity:0; transform:translateX(20px); } }
</style>
```

```javascript
function addKillFeed(text) {
    const el = document.createElement('div');
    el.className = 'kill-entry';
    el.textContent = text;
    const feed = document.getElementById('kill-feed');
    feed.prepend(el);
    setTimeout(() => el.remove(), 3000);
    while (feed.children.length > 5) feed.lastChild.remove();
}
```

## Combo Counter

```html
<div id="combo" style="position:absolute; top:50%; left:50%; transform:translate(-50%, 50px);
    font-size:0; font-weight:900; color:#ffd700; text-align:center;
    text-shadow: 0 0 20px rgba(255,215,0,0.6), 0 2px 4px rgba(0,0,0,0.5);
    transition: font-size 0.12s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.4s ease-out;">
</div>
```

```javascript
function updateCombo(count) {
    const el = document.getElementById('combo');
    if (count >= 2) {
        el.textContent = `${count}x COMBO`;
        el.style.fontSize = Math.min(40, 18 + count * 3) + 'px';
        el.style.opacity = '1';
        // Punch scale effect
        el.style.transform = 'translate(-50%, 50px) scale(1.3)';
        setTimeout(() => el.style.transform = 'translate(-50%, 50px) scale(1)', 100);
    } else {
        el.style.opacity = '0';
        el.style.fontSize = '0';
    }
}
```

## Wave / Level Announcement

```html
<div id="announcement" style="position:absolute; top:30%; left:50%; transform:translate(-50%,-50%);
    text-align:center; opacity:0; pointer-events:none;">
    <div id="announce-text" style="font-size:56px; font-weight:900; color:#fff;
        text-shadow: 0 0 30px rgba(100,180,255,0.6), 0 4px 8px rgba(0,0,0,0.5);
        letter-spacing:4px;"></div>
    <div id="announce-sub" style="font-size:18px; color:rgba(255,255,255,0.6); margin-top:8px;"></div>
</div>
<style>
    #announcement {
        transition: opacity 0.4s ease-out;
    }
    #announcement.show {
        opacity: 1;
        animation: announceIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    @keyframes announceIn {
        from { transform: translate(-50%,-50%) scale(0.5); opacity:0; }
        to { transform: translate(-50%,-50%) scale(1); opacity:1; }
    }
</style>
```

```javascript
function showAnnouncement(text, sub = '', duration = 2500) {
    const el = document.getElementById('announcement');
    document.getElementById('announce-text').textContent = text;
    document.getElementById('announce-sub').textContent = sub;
    el.classList.add('show');
    el.style.opacity = '1';
    setTimeout(() => { el.style.opacity = '0'; el.classList.remove('show'); }, duration);
}
// Usage: showAnnouncement('WAVE 3', '8 enemies incoming');
```

## Damage Vignette

```html
<div id="damage-vignette" style="position:fixed; top:0; left:0; width:100%; height:100%;
    pointer-events:none; opacity:0; z-index:9;
    background: radial-gradient(ellipse at center, transparent 40%, rgba(200,0,0,0.5) 100%);
    transition: opacity 0.08s ease-out;"></div>
```

```javascript
let vignetteOpacity = 0;
function flashDamageVignette(intensity = 0.6) { vignetteOpacity = intensity; }
function updateVignette(delta) {
    if (vignetteOpacity > 0) {
        vignetteOpacity = Math.max(0, vignetteOpacity - delta * 2);
        document.getElementById('damage-vignette').style.opacity = vignetteOpacity;
    }
}
```

## Title Screen (Premium)

```html
<div id="title-screen" style="position:fixed; inset:0; display:flex; flex-direction:column;
    align-items:center; justify-content:center; z-index:20; cursor:pointer;">
    <!-- Gradient overlay over 3D background -->
    <div style="position:absolute; inset:0; background: linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.5) 60%, rgba(0,0,0,0.8) 100%);"></div>
    <div style="position:relative; text-align:center;">
        <h1 style="font-size:clamp(36px, 7vw, 72px); font-weight:900; color:#fff;
            text-shadow: 0 0 40px rgba(100,160,255,0.4), 0 4px 12px rgba(0,0,0,0.6);
            letter-spacing:3px; margin-bottom:8px;">GAME TITLE</h1>
        <div style="font-size:clamp(14px, 2vw, 20px); color:rgba(255,255,255,0.5);
            margin-bottom:40px; font-weight:300;">Subtitle or tagline</div>
        <div style="font-size:clamp(16px, 2.5vw, 22px); color:#fff;
            animation: pulse 2s ease-in-out infinite;">Click to Play</div>
        <div style="color:rgba(255,255,255,0.3); font-size:13px; margin-top:30px; line-height:2.2;">
            <!-- Control hints with key icons -->
            <span class="key-hint">W A S D</span> Move &nbsp;&bull;&nbsp;
            <span class="key-hint">MOUSE</span> Look &nbsp;&bull;&nbsp;
            <span class="key-hint">CLICK</span> Shoot
        </div>
    </div>
</div>
<style>
    @keyframes pulse { 0%,100% { opacity:0.4; } 50% { opacity:1; } }
    .key-hint {
        display:inline-block; padding:2px 8px; margin:0 2px;
        background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.15);
        border-radius:4px; font-size:11px; letter-spacing:1px; font-weight:600;
        vertical-align:middle;
    }
</style>
```

## Game Over Screen (Premium)

```html
<div id="gameover-screen" style="position:fixed; inset:0; display:none; flex-direction:column;
    align-items:center; justify-content:center; z-index:20; cursor:pointer;
    background:rgba(0,0,0,0.75); backdrop-filter:blur(8px);">
    <div style="text-align:center;">
        <div id="go-icon" style="font-size:64px; margin-bottom:12px;"><!-- emoji or icon --></div>
        <h1 id="go-title" style="font-size:52px; font-weight:900; color:#ef4444;
            text-shadow: 0 0 20px rgba(239,68,68,0.4); margin-bottom:20px;
            letter-spacing:2px;">GAME OVER</h1>
        <div class="hud-panel-dark" style="display:inline-block; padding:20px 32px; margin-bottom:20px;">
            <div id="go-stats" style="font-size:18px; line-height:2; color:#ccc;"></div>
        </div>
        <div id="go-best" style="font-size:16px; color:#4ade80; margin-bottom:24px;"></div>
        <div style="font-size:18px; color:rgba(255,255,255,0.6); animation:pulse 2s ease-in-out infinite;">
            Click to Restart
        </div>
    </div>
</div>
```

## Victory / Finish Screen

```html
<div id="victory-screen" style="position:fixed; inset:0; display:none; flex-direction:column;
    align-items:center; justify-content:center; z-index:20; cursor:pointer;
    background:rgba(0,0,0,0.7); backdrop-filter:blur(8px);">
    <div style="text-align:center;">
        <div id="v-icon" style="font-size:72px; margin-bottom:8px;
            animation: victoryBounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);"></div>
        <h1 style="font-size:48px; font-weight:900; color:#ffd700;
            text-shadow: 0 0 30px rgba(255,215,0,0.4); margin-bottom:20px;">VICTORY!</h1>
        <div class="hud-panel-dark" style="display:inline-block; padding:20px 36px;">
            <div id="v-stats" style="font-size:18px; line-height:2.2; color:#ddd;"></div>
        </div>
        <div style="margin-top:24px; font-size:18px; color:rgba(255,255,255,0.5);
            animation:pulse 2s ease-in-out infinite;">Click to Continue</div>
    </div>
</div>
<style>
    @keyframes victoryBounce {
        0% { transform: scale(0) rotate(-20deg); }
        60% { transform: scale(1.2) rotate(5deg); }
        100% { transform: scale(1) rotate(0deg); }
    }
</style>
```

## Minimap (Canvas-based)

```html
<div id="minimap-container" style="position:absolute; top:20px; right:20px;">
    <div class="hud-panel" style="padding:8px; border-radius:50%; overflow:hidden;">
        <canvas id="minimap" width="130" height="130" style="border-radius:50%; display:block;"></canvas>
    </div>
</div>
```

## Notification Toast

```html
<div id="toast-container" style="position:absolute; bottom:80px; left:50%; transform:translateX(-50%);
    display:flex; flex-direction:column; align-items:center; gap:8px;"></div>
<style>
    .toast {
        background: rgba(0,0,0,0.7); backdrop-filter:blur(12px);
        padding:10px 20px; border-radius:8px; color:#fff; font-size:15px;
        border:1px solid rgba(255,255,255,0.08);
        animation: toastIn 0.3s ease-out, toastOut 0.4s ease-in 2.6s forwards;
        white-space:nowrap;
    }
    .toast-success { border-left:3px solid #4ade80; }
    .toast-warn { border-left:3px solid #fbbf24; }
    .toast-error { border-left:3px solid #ef4444; }
    .toast-info { border-left:3px solid #60a5fa; }
    @keyframes toastIn { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
    @keyframes toastOut { to { opacity:0; transform:translateY(-10px); } }
</style>
```

```javascript
function showToast(text, type = 'info', duration = 3000) {
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = text;
    document.getElementById('toast-container').appendChild(el);
    setTimeout(() => el.remove(), duration);
}
// Usage: showToast('Gate cleared!', 'success');
// Usage: showToast('+2s Penalty', 'error');
```

## Countdown (3-2-1-GO)

```html
<div id="countdown" style="position:absolute; top:40%; left:50%; transform:translate(-50%,-50%);
    font-size:0; font-weight:900; color:#fff; text-align:center;
    text-shadow: 0 0 40px rgba(100,180,255,0.5);
    transition: font-size 0.15s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s;
    opacity:0;"></div>
```

```javascript
function showCountdown(value) {
    const el = document.getElementById('countdown');
    el.textContent = value;
    el.style.opacity = '1';
    el.style.fontSize = '0px';
    el.style.color = value === 'GO!' ? '#4ade80' : '#fff';
    requestAnimationFrame(() => {
        el.style.fontSize = value === 'GO!' ? '100px' : '120px';
    });
}
function hideCountdown() {
    document.getElementById('countdown').style.opacity = '0';
}
```

## Ammo Display (FPS)

```html
<div class="hud-panel" style="position:absolute; bottom:24px; right:24px; text-align:center; min-width:100px;">
    <div style="display:flex; align-items:baseline; justify-content:center; gap:4px;">
        <span id="ammo-current" style="font-size:36px; font-weight:800; font-variant-numeric:tabular-nums;">30</span>
        <span style="font-size:16px; color:rgba(255,255,255,0.3);">/</span>
        <span id="ammo-max" style="font-size:18px; color:rgba(255,255,255,0.5); font-variant-numeric:tabular-nums;">30</span>
    </div>
    <div id="ammo-reload" style="font-size:11px; color:#fbbf24; text-transform:uppercase;
        letter-spacing:1.5px; height:16px; opacity:0; transition:opacity 0.2s;">RELOADING</div>
</div>
```

## Inventory Panel (RPG)

```html
<style>
    #inventory-panel {
        position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);
        width:min(540px, 90vw); max-height:80vh;
        background:rgba(10,10,20,0.92); backdrop-filter:blur(20px);
        border:1px solid rgba(255,255,255,0.08); border-radius:16px;
        padding:24px; z-index:30; pointer-events:auto;
        display:none;
    }
    .inv-grid {
        display:grid; grid-template-columns:repeat(6, 1fr); gap:8px;
        margin-top:16px;
    }
    .inv-slot {
        aspect-ratio:1; background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.06); border-radius:8px;
        display:flex; align-items:center; justify-content:center;
        cursor:pointer; position:relative; transition: all 0.15s;
    }
    .inv-slot:hover {
        background:rgba(255,255,255,0.08); border-color:rgba(100,180,255,0.3);
        transform:scale(1.05);
    }
    .inv-slot.selected { border-color:#60a5fa; box-shadow:0 0 12px rgba(96,165,250,0.2); }
    .inv-slot .count {
        position:absolute; bottom:2px; right:4px; font-size:11px;
        color:rgba(255,255,255,0.7); font-weight:600;
    }
    .inv-header { color:#fff; font-size:20px; font-weight:700; margin-bottom:4px; }
    .inv-detail {
        margin-top:16px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.06);
        min-height:60px;
    }
    .inv-detail-name { color:#fff; font-size:16px; font-weight:600; }
    .inv-detail-desc { color:rgba(255,255,255,0.5); font-size:13px; margin-top:4px; }
    .inv-gold { color:#ffd700; font-size:14px; font-weight:600; margin-top:12px; }
</style>
```

## Dialogue Box (RPG)

```html
<style>
    #dialogue-box {
        position:fixed; bottom:24px; left:50%; transform:translateX(-50%);
        width:min(680px, 92vw); pointer-events:auto;
        background:rgba(5,5,15,0.92); backdrop-filter:blur(20px);
        border:1px solid rgba(255,255,255,0.06); border-radius:16px;
        padding:20px 24px; z-index:25; display:none;
    }
    #dlg-speaker {
        font-size:15px; font-weight:700; color:#60a5fa;
        margin-bottom:8px; letter-spacing:0.5px;
    }
    #dlg-text {
        font-size:16px; color:rgba(255,255,255,0.9);
        line-height:1.7; min-height:48px;
    }
    #dlg-choices { margin-top:14px; display:flex; flex-direction:column; gap:6px; }
    .dlg-choice {
        padding:10px 16px; background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.08); border-radius:8px;
        color:#fff; font-size:14px; cursor:pointer; transition:all 0.15s;
    }
    .dlg-choice:hover {
        background:rgba(96,165,250,0.12); border-color:rgba(96,165,250,0.3);
        padding-left:24px;
    }
    #dlg-continue {
        text-align:right; margin-top:10px; font-size:12px;
        color:rgba(255,255,255,0.3); animation:pulse 1.5s ease-in-out infinite;
    }
</style>
```

## Battle UI (RPG / Pokemon-style)

```html
<style>
    .battle-creature-info {
        background:rgba(0,0,0,0.45); backdrop-filter:blur(10px);
        border:1px solid rgba(255,255,255,0.06); border-radius:12px;
        padding:12px 16px; min-width:200px;
    }
    .battle-name { font-size:16px; font-weight:700; color:#fff; }
    .battle-level { font-size:12px; color:rgba(255,255,255,0.4); margin-left:8px; }
    .battle-hp-bar {
        width:100%; height:8px; background:rgba(255,255,255,0.08);
        border-radius:4px; overflow:hidden; margin-top:8px;
    }
    .battle-hp-fill {
        height:100%; border-radius:4px; transition:width 0.4s ease-out;
        background: linear-gradient(90deg, #22c55e, #4ade80);
    }
    .battle-hp-fill.warn { background: linear-gradient(90deg, #eab308, #fbbf24); }
    .battle-hp-fill.danger { background: linear-gradient(90deg, #dc2626, #ef4444); }
    .battle-hp-text { font-size:12px; color:rgba(255,255,255,0.5); margin-top:4px; font-variant-numeric:tabular-nums; }

    .battle-menu {
        position:absolute; bottom:20px; left:50%; transform:translateX(-50%);
        display:grid; grid-template-columns:1fr 1fr; gap:8px;
        pointer-events:auto; min-width:320px;
    }
    .battle-btn {
        padding:12px 20px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);
        background:rgba(0,0,0,0.5); backdrop-filter:blur(8px);
        color:#fff; font-size:15px; font-weight:600; cursor:pointer;
        transition:all 0.15s; text-align:center;
    }
    .battle-btn:hover {
        background:rgba(96,165,250,0.15); border-color:rgba(96,165,250,0.3);
        transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,0,0,0.3);
    }
    .battle-log {
        position:absolute; bottom:100px; left:24px; max-width:380px;
        background:rgba(0,0,0,0.4); backdrop-filter:blur(6px);
        border-radius:10px; padding:12px 16px;
        font-size:14px; color:rgba(255,255,255,0.8); line-height:1.6;
    }
</style>
```

## Speed Lines / Motion Effect

```html
<div id="speed-lines" style="position:fixed; inset:0; pointer-events:none; z-index:5; opacity:0;
    background: radial-gradient(ellipse at center, transparent 50%, rgba(200,220,255,0.12) 100%);
    transition: opacity 0.3s;"></div>
```

```javascript
// Scale opacity with speed: 0 at low speed, 1 at max
function updateSpeedLines(speedRatio) {
    document.getElementById('speed-lines').style.opacity = Math.min(1, speedRatio * 1.2);
}
```

## General CSS Utilities

```css
/* Tabular numbers for counters/timers */
.mono { font-variant-numeric: tabular-nums; }

/* Responsive text that scales with viewport */
.text-responsive { font-size: clamp(14px, 2.5vw, 24px); }

/* Smooth show/hide */
.fade-in { animation: fadeIn 0.3s ease-out; }
.fade-out { animation: fadeOut 0.3s ease-in forwards; }
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
@keyframes fadeOut { from { opacity:1; } to { opacity:0; } }

/* Slide up entrance */
.slide-up { animation: slideUp 0.4s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes slideUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }

/* Prevent text selection on HUD */
#hud, #title-screen, #gameover-screen, #finish-screen { user-select: none; -webkit-user-select: none; }
```

## Tips

- **Always use `font-variant-numeric: tabular-nums`** on numbers that change — prevents layout jumping
- **Use `clamp()` for responsive font sizes** — `clamp(min, preferred, max)`
- **Backdrop-filter has a performance cost** — use sparingly (2-3 panels max), avoid on full-screen overlays
- **Transitions vs animations**: Use CSS `transition` for state changes (hover, active), CSS `@keyframes` for entrances/exits
- **Z-index layering**: Game canvas (0) → HUD (10) → Modals/Inventory (25-30) → Title/Gameover (20) → Damage vignette (9) → Speed lines (5)
- **Color system**: Pick 4-5 colors and reuse them: primary (#60a5fa), success (#4ade80), warning (#fbbf24), danger (#ef4444), gold (#ffd700)
- **Test with `pointer-events`**: HUD container is `none`, only interactive elements (buttons, menus) are `auto`
- **Animate score changes**: Count up smoothly rather than snapping — much more satisfying
- **Key hint styling**: Use the `.key-hint` class (bordered inline pill) for control references in title/pause screens
