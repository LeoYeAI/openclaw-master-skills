# Coral Dawn — Style Reference
# Coral Dawn — 风格参考文档

Warm, optimistic, and human. Inspired by early morning light over terracotta rooftops — the feeling of a fresh start. Cream backgrounds with coral accents and generous whitespace. Approachable yet professional.

温暖、乐观、有人情味。灵感来自清晨阳光打在赭红屋顶上的光感——新的开始。奶油底色配珊瑚橘强调色，大量留白，亲切而不失专业。

---

## Colors / 配色

```css
/* Light variant / 亮色方案 */
:root {
    --bg:           #FDFAF6;   /* warm cream / 暖奶油色 */
    --bg-secondary: #F5EFE6;   /* slightly deeper cream for cards / 卡片用稍深奶油色 */
    --text:         #2C1A0E;   /* warm dark brown, not pure black / 暖深棕，非纯黑 */
    --text-muted:   #8C6F5A;   /* mid-tone warm brown / 中调暖棕，用于次要文字 */
    --accent:       #E8541A;   /* coral — use ONCE per slide / 珊瑚橘——每张幻灯片只用一次 */
    --accent-soft:  #FDEEE7;   /* coral tint for backgrounds / 珊瑚浅色，用于背景色块 */
    --rule:         rgba(44,26,14,0.12); /* subtle divider / 细分割线 */
}
```

**Forbidden / 禁止使用：** cool grays（冷灰）, blue-tinted whites（偏蓝的白）, neon colors（霓虹色）, drop shadows（投影）, decorative borders（装饰边框）.

---

## Typography / 字体

```css
/* Display — expressive serif for titles
   标题字体——表现力强的衬线体 */
.cd-title {
    font-family: "Playfair Display", "Georgia", serif;
    font-weight: 700;
    font-size: clamp(2rem, 5vw, 4.5rem);
    line-height: 1.15;
    letter-spacing: -0.02em;
    color: var(--text);
}

/* Body — clean humanist sans
   正文字体——干净的人文无衬线体 */
.cd-body {
    font-family: "Source Sans 3", "Helvetica Neue", sans-serif;
    font-weight: 400;
    font-size: clamp(0.95rem, 1.6vw, 1.15rem);
    line-height: 1.8;
    color: var(--text);
}

/* Label / eyebrow — small caps above heading
   眉标——标题上方的小型大写标签 */
.cd-label {
    font-family: "Source Sans 3", sans-serif;
    font-size: clamp(0.65rem, 1vw, 0.75rem);
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);  /* always coral / 永远使用珊瑚橘 */
}

/* Stat / number — large metric display
   数据展示——大号指标数字 */
.cd-stat {
    font-family: "Playfair Display", serif;
    font-size: clamp(2.5rem, 6vw, 5rem);
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
```

---

## Layout / 布局

```css
/* Base slide — all slides inherit this
   基础幻灯片样式——所有幻灯片继承 */
.cd-slide {
    background: var(--bg);
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: clamp(2.5rem, 7vw, 7rem) clamp(2rem, 8vw, 10rem);
    position: relative;
    overflow: hidden;
}

/* Left accent bar — SIGNATURE ELEMENT, use on content slides only, not title/closing
   左侧强调竖条——签名元素，只用于内容页，不用于封面和结尾页 */
.cd-slide.accented::before {
    content: '';
    position: absolute;
    left: 0; top: 15%; bottom: 15%;
    width: 4px;
    background: var(--accent);
    border-radius: 0 2px 2px 0;
}

/* Card / 卡片 */
.cd-card {
    background: var(--bg-secondary);
    border-radius: 16px;
    padding: clamp(1.25rem, 2.5vw, 2rem);
}

/* 2-column grid / 双栏网格 */
.cd-cols2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(1rem, 2vw, 2rem);
}

/* 3-column grid / 三栏网格 */
.cd-cols3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: clamp(0.75rem, 1.5vw, 1.5rem);
}

/* Horizontal rule with coral centre dot
   带珊瑚圆点的水平分隔线 */
.cd-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: clamp(1rem, 2.5vh, 2rem) 0;
    color: var(--rule);
}
.cd-divider::before, .cd-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: currentColor;
}
.cd-divider-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
}
```

---

## Animation / 动画

```css
/* Warm fade-up — relaxed 0.7s, not snappy
   温和上浮淡入——0.7s 宽松节奏，不要弹跳 */
.cd-reveal {
    opacity: 0;
    transform: translateY(18px);
    transition: opacity 0.7s ease, transform 0.7s ease;
}
.slide.visible .cd-reveal              { opacity: 1; transform: translateY(0); }
.slide.visible .cd-reveal:nth-child(1) { transition-delay: 0.05s; }
.slide.visible .cd-reveal:nth-child(2) { transition-delay: 0.18s; }
.slide.visible .cd-reveal:nth-child(3) { transition-delay: 0.31s; }
.slide.visible .cd-reveal:nth-child(4) { transition-delay: 0.44s; }

/* Respect reduced-motion preference / 尊重系统减少动画设置 */
@media (prefers-reduced-motion: reduce) {
    .cd-reveal { transition: none; opacity: 1; transform: none; }
}
```

---

## Font Loading / 字体加载

```html
<!-- Preconnect for faster font load / 预连接加速字体加载 -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<!-- Playfair Display: titles / 标题 | Source Sans 3: body / 正文 -->
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
```

---

## Signature Elements / 签名视觉元素

1. **Left accent bar / 左侧竖条** — 4px coral line on the left edge of content slides. Class: `.cd-slide.accented`
2. **Eyebrow label / 眉标** — Small uppercase coral text above headings. Class: `.cd-label`
3. **Type pairing / 字体搭配** — Playfair Display (serif) for headings + Source Sans 3 (sans) for body
4. **Coral stat numbers / 珊瑚数据数字** — Large Playfair Display figures. Class: `.cd-stat`
5. **Warm card / 暖色卡片** — Slightly deeper cream background. Class: `.cd-card`

---

## Checklist / 生成前检查

- [ ] Warm cream `#FDFAF6` background — no white, no cool grays / 暖奶油色背景，不用白色或冷灰
- [ ] Coral accent on ONE element per slide / 每张幻灯片珊瑚橘只出现在一处
- [ ] Playfair Display for headings, Source Sans 3 for body / 标题用 Playfair，正文用 Source Sans 3
- [ ] Left accent bar on content slides, NOT on title or closing / 左竖条只在内容页使用
- [ ] Content never fills full width — generous horizontal padding / 内容不铺满全宽，水平留白要大

---

## Best For / 适用场景

Founder storytelling · Consumer brand launches · Education & EdTech · Health & wellness · Human-centered product decks · Any talk where warmth matters

创始人故事叙述 · 消费品牌发布 · 教育与 EdTech · 健康与生活方式 · 以人为本的产品 deck · 任何需要温暖感和亲切感的演讲
