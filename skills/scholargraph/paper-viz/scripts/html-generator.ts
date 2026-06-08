/**
 * @module paper-viz/html-generator
 * @description 生成自包含的论文演示 HTML 文件
 *
 * 特性：
 * - 学术深色主题，CSS 变量，clamp() 响应式排版
 * - 100vh/100dvh 全屏幻灯片，overflow:hidden
 * - 键盘(←→/空格)、触摸滑动、鼠标滚轮导航
 * - contenteditable + localStorage 自动保存 + E 键切换
 * - Intersection Observer + reveal 动画
 * - 论文原文可点击链接
 * - 嵌入图表（base64 或相对路径）
 */

import type { PresentationData, PresentationSlide, ContentBlock, PresentationTheme } from './types';

/**
 * 生成论文演示 HTML
 * @param data - 演示文稿数据
 * @returns 完整的 HTML 字符串
 */
export function generatePaperHtml(data: PresentationData): string {
  const { theme } = data;
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(data.title)}</title>
<style>
${generateCSS(theme)}
</style>
</head>
<body>
<div class="presentation" id="presentation">
${data.slides.map((s, i) => renderSlide(s, i, data)).join('\n')}
</div>
<nav class="nav-dots" id="navDots" aria-label="Slide navigation">
${data.slides.map((s, i) => `<button class="dot${i === 0 ? ' active' : ''}" data-index="${i}" aria-label="Slide ${i + 1}">${i + 1}</button>`).join('\n')}
</nav>
<div class="slide-counter" id="slideCounter">1 / ${data.slides.length}</div>
<div class="edit-indicator" id="editIndicator">EDIT MODE</div>
<div class="controls-hint" id="controlsHint">
  <span>← → Space</span> Navigate
  <span>E</span> Edit mode
  <span>Scroll</span> Next/Prev
</div>
<script>
${generateJS(data)}
</script>
</body>
</html>`;
}

/** 生成完整 CSS */
function generateCSS(t: PresentationTheme): string {
  return `
:root {
  --primary: ${t.primaryColor};
  --accent: ${t.accentColor};
  --bg: ${t.backgroundColor};
  --surface: ${t.surfaceColor};
  --text: ${t.textColor};
  --text-secondary: ${t.textSecondaryColor};
  --code-bg: ${t.codeBackground};
  --font: ${t.fontFamily};
  --font-heading: ${t.headingFontFamily};
  --radius: 12px;
  --slide-gap: 0px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html {
  scroll-snap-type: y mandatory;
  overflow-y: scroll;
  scroll-behavior: smooth;
  scrollbar-width: none;
}
html::-webkit-scrollbar { display: none; }

body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

/* === Slide === */
.slide {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: clamp(2rem, 5vw, 4rem) clamp(2rem, 8vw, 8rem);
  scroll-snap-align: start;
  position: relative;
  overflow: hidden;
}

.slide.layout-center {
  align-items: center;
  text-align: center;
}

.slide.layout-two-column .slide-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  width: 100%;
}

.slide.layout-full-image {
  padding: 2rem;
}
.slide.layout-full-image .block-image {
  max-height: 70vh;
}

/* === Slide Title === */
.slide-title {
  font-family: var(--font-heading);
  font-size: clamp(1.5rem, 3.5vw, 2.8rem);
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 1.5rem;
  line-height: 1.2;
}

.slide.layout-center .slide-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
}

/* === Content Blocks === */
.slide-content {
  max-width: 1100px;
  width: 100%;
}

.block { margin-bottom: 1.2rem; }

.block-heading {
  font-family: var(--font-heading);
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  color: var(--text);
  line-height: 1.15;
  margin-bottom: 0.5rem;
}

.block-text {
  font-size: clamp(1rem, 1.8vw, 1.25rem);
  color: var(--text-secondary);
  line-height: 1.8;
}
.block-text.authors {
  font-size: clamp(1rem, 2vw, 1.35rem);
  color: var(--accent);
  margin-top: 1rem;
}
.block-text.meta {
  font-size: clamp(0.85rem, 1.4vw, 1.05rem);
  color: var(--text-secondary);
  margin-top: 0.5rem;
}
.block-text.summary {
  font-size: clamp(1.05rem, 1.9vw, 1.3rem);
  color: var(--text);
  border-left: 3px solid var(--primary);
  padding-left: 1rem;
}

.block-quote {
  border-left: 4px solid var(--accent);
  padding: 1rem 1.5rem;
  background: var(--surface);
  border-radius: 0 var(--radius) var(--radius) 0;
  font-style: italic;
  color: var(--text-secondary);
  font-size: clamp(0.9rem, 1.5vw, 1.1rem);
  line-height: 1.7;
}

.block-list-title {
  font-weight: 600;
  font-size: clamp(0.95rem, 1.6vw, 1.15rem);
  color: var(--primary);
  margin-bottom: 0.4rem;
}

.block-list {
  list-style: none;
  padding: 0;
}
.block-list li {
  position: relative;
  padding: 0.5rem 0 0.5rem 1.5rem;
  font-size: clamp(0.9rem, 1.5vw, 1.1rem);
  color: var(--text-secondary);
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.block-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary);
}
.block-list li.sub-item {
  padding-left: 2.5rem;
  font-size: clamp(0.8rem, 1.3vw, 0.95rem);
  color: var(--text-secondary);
  opacity: 0.85;
}
.block-list li.sub-item::before {
  left: 1rem;
  width: 4px;
  height: 4px;
  background: var(--accent);
}

/* Importance badges */
.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-right: 0.5rem;
  vertical-align: middle;
}
.badge-critical, .badge-major, .badge-high { background: #EF4444; color: #fff; }
.badge-important, .badge-moderate, .badge-medium { background: #F59E0B; color: #1a1a1a; }
.badge-supporting, .badge-minor, .badge-low { background: #6B7280; color: #fff; }

/* Keywords tags */
.keywords-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 0.75rem;
}
.keyword-tag {
  padding: 0.25rem 0.75rem;
  background: var(--surface);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

/* === Images === */
.block-image {
  max-width: 100%;
  max-height: 55vh;
  object-fit: contain;
  border-radius: var(--radius);
  margin: 0.5rem auto;
  display: block;
}
.block-image-caption {
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  font-style: italic;
}

/* === Navigation Dots === */
.nav-dots {
  position: fixed;
  right: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 100;
}
.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--text-secondary);
  background: transparent;
  cursor: pointer;
  font-size: 0;
  transition: all 0.3s;
  padding: 0;
}
.dot.active {
  background: var(--primary);
  border-color: var(--primary);
  transform: scale(1.3);
}
.dot:hover {
  border-color: var(--primary);
}

/* === Slide Counter === */
.slide-counter {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  opacity: 0.6;
  z-index: 100;
  font-variant-numeric: tabular-nums;
}

/* === Edit Mode === */
.edit-indicator {
  position: fixed;
  top: 1rem;
  right: 1rem;
  padding: 0.3rem 0.8rem;
  background: var(--accent);
  color: #1a1a1a;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 100;
  pointer-events: none;
}
body.editing .edit-indicator { opacity: 1; }
body.editing [contenteditable="true"] {
  outline: 1px dashed var(--accent);
  outline-offset: 4px;
}

/* === Controls Hint === */
.controls-hint {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 1.5rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
  opacity: 0.5;
  z-index: 100;
  transition: opacity 0.5s;
}
.controls-hint span {
  background: var(--surface);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-family: monospace;
  margin-right: 0.3rem;
}

/* === Paper Link === */
.paper-link {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.4rem 1rem;
  background: var(--surface);
  color: var(--primary);
  text-decoration: none;
  border-radius: var(--radius);
  border: 1px solid rgba(96,165,250,0.3);
  font-size: 0.9rem;
  transition: all 0.2s;
}
.paper-link:hover {
  background: var(--primary);
  color: var(--bg);
}

/* === Reveal Animations === */
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
.reveal.scale {
  transform: scale(0.95);
}
.reveal.scale.visible {
  transform: scale(1);
}

/* === Responsive === */
@media (max-width: 768px) {
  .slide { padding: 1.5rem; }
  .slide.layout-two-column .slide-content {
    grid-template-columns: 1fr;
  }
  .nav-dots { right: 0.5rem; }
  .controls-hint { display: none; }
}

@media print {
  html { scroll-snap-type: none; }
  .slide { min-height: auto; page-break-after: always; padding: 2rem; }
  .nav-dots, .slide-counter, .edit-indicator, .controls-hint { display: none; }
}
`;
}

/** 渲染单张幻灯片 */
function renderSlide(slide: PresentationSlide, index: number, data: PresentationData): string {
  const layoutClass = slide.layout ? ` layout-${slide.layout}` : ' layout-default';
  const isTitle = slide.type === 'title';

  let html = `<section class="slide${layoutClass}" id="slide-${index}" data-type="${slide.type}">`;

  if (!isTitle) {
    html += `<h2 class="slide-title reveal">${escapeHtml(slide.title)}</h2>`;
  }

  html += `<div class="slide-content">`;

  for (const block of slide.blocks) {
    html += renderBlock(block);
  }

  // 标题页添加论文链接
  if (isTitle && data.url) {
    html += `<a class="paper-link reveal" href="${escapeHtml(data.url)}" target="_blank" rel="noopener">View Original Paper ↗</a>`;
  }

  html += `</div>`;
  html += `</section>`;

  return html;
}

/** 渲染内容块 */
function renderBlock(block: ContentBlock): string {
  const cls = block.className ? ` ${block.className}` : '';

  switch (block.type) {
    case 'heading':
      return `<div class="block reveal"><h1 class="block-heading${cls}" contenteditable="false">${escapeHtml(block.content)}</h1></div>`;

    case 'text': {
      // 支持简单的 **bold** 标记
      const content = escapeHtml(block.content).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      return `<div class="block reveal"><p class="block-text${cls}" contenteditable="false">${content}</p></div>`;
    }

    case 'quote':
      return `<div class="block reveal"><blockquote class="block-quote${cls}" contenteditable="false">${escapeHtml(block.content)}</blockquote></div>`;

    case 'list': {
      const variant = block.variant;
      const badgeHtml = variant
        ? `<span class="badge badge-${variant}">${variant}</span>`
        : '';
      let html = `<div class="block reveal">`;
      if (block.content) {
        html += `<div class="block-list-title">${badgeHtml}${escapeHtml(block.content)}</div>`;
      }
      if (block.className === 'keywords') {
        // Keywords 使用标签样式
        html += `<div class="keywords-container">`;
        for (const item of block.items ?? []) {
          html += `<span class="keyword-tag">${escapeHtml(item)}</span>`;
        }
        html += `</div>`;
      } else {
        html += `<ul class="block-list" contenteditable="false">`;
        if (block.items) {
          for (const item of block.items) {
            html += `<li class="sub-item">${escapeHtml(item)}</li>`;
          }
        }
        html += `</ul>`;
      }
      html += `</div>`;
      return html;
    }

    case 'image':
      return `<div class="block reveal scale">
<img class="block-image" src="${escapeHtml(block.src ?? '')}" alt="${escapeHtml(block.content)}" loading="lazy">
${block.caption ? `<p class="block-image-caption">${escapeHtml(block.caption)}</p>` : ''}
</div>`;

    case 'badge':
      return `<div class="block reveal"><span class="badge badge-${block.variant ?? 'supporting'}">${escapeHtml(block.content)}</span></div>`;

    default:
      return `<div class="block reveal"><p class="block-text">${escapeHtml(block.content)}</p></div>`;
  }
}

/** 生成交互 JS */
function generateJS(data: PresentationData): string {
  return `
(function() {
  'use strict';

  const TOTAL = ${data.slides.length};
  const STORAGE_KEY = 'paper-viz-edits-' + ${escapeJsString(data.title.slice(0, 40))};
  let current = 0;
  let editing = false;
  let touchStartY = 0;
  let scrollLock = false;

  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.dot');
  const counter = document.getElementById('slideCounter');
  const hint = document.getElementById('controlsHint');

  // === Navigation ===
  function goTo(index) {
    if (index < 0 || index >= TOTAL) return;
    current = index;
    slides[current].scrollIntoView({ behavior: 'smooth' });
    updateUI();
  }

  function next() { goTo(current + 1); }
  function prev() { goTo(current - 1); }

  function updateUI() {
    dots.forEach(function(d, i) {
      d.classList.toggle('active', i === current);
    });
    counter.textContent = (current + 1) + ' / ' + TOTAL;
  }

  // Keyboard
  document.addEventListener('keydown', function(e) {
    if (editing) return;
    switch (e.key) {
      case 'ArrowRight': case 'ArrowDown': case ' ':
        e.preventDefault(); next(); break;
      case 'ArrowLeft': case 'ArrowUp':
        e.preventDefault(); prev(); break;
      case 'Home': e.preventDefault(); goTo(0); break;
      case 'End': e.preventDefault(); goTo(TOTAL - 1); break;
      case 'e': case 'E':
        toggleEdit(); break;
    }
  });

  // Scroll / Wheel
  document.addEventListener('wheel', function(e) {
    if (editing || scrollLock) return;
    scrollLock = true;
    if (e.deltaY > 30) next();
    else if (e.deltaY < -30) prev();
    setTimeout(function() { scrollLock = false; }, 800);
  }, { passive: true });

  // Touch
  document.addEventListener('touchstart', function(e) {
    touchStartY = e.touches[0].clientY;
  }, { passive: true });
  document.addEventListener('touchend', function(e) {
    if (editing) return;
    var diff = touchStartY - e.changedTouches[0].clientY;
    if (Math.abs(diff) > 50) {
      if (diff > 0) next(); else prev();
    }
  }, { passive: true });

  // Navigation dots
  dots.forEach(function(dot) {
    dot.addEventListener('click', function() {
      goTo(parseInt(this.dataset.index));
    });
  });

  // Intersection Observer for current slide tracking and reveal
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        var idx = Array.from(slides).indexOf(entry.target);
        if (idx !== -1) {
          current = idx;
          updateUI();
        }
        // Reveal animations
        entry.target.querySelectorAll('.reveal').forEach(function(el) {
          el.classList.add('visible');
        });
      }
    });
  }, { threshold: 0.5 });

  slides.forEach(function(s) { observer.observe(s); });

  // === Edit Mode ===
  function toggleEdit() {
    editing = !editing;
    document.body.classList.toggle('editing', editing);
    var editableEls = document.querySelectorAll('[contenteditable]');
    editableEls.forEach(function(el) {
      el.contentEditable = editing ? 'true' : 'false';
    });
    if (!editing) saveEdits();
  }

  function saveEdits() {
    try {
      var edits = {};
      slides.forEach(function(slide, i) {
        var editableEls = slide.querySelectorAll('[contenteditable]');
        editableEls.forEach(function(el, j) {
          var key = i + '-' + j;
          edits[key] = el.innerHTML;
        });
      });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(edits));
    } catch(e) {}
  }

  function loadEdits() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (!saved) return;
      var edits = JSON.parse(saved);
      slides.forEach(function(slide, i) {
        var editableEls = slide.querySelectorAll('[contenteditable]');
        editableEls.forEach(function(el, j) {
          var key = i + '-' + j;
          if (edits[key]) el.innerHTML = edits[key];
        });
      });
    } catch(e) {}
  }

  loadEdits();

  // Auto-save while editing
  document.addEventListener('input', function() {
    if (editing) {
      clearTimeout(window._saveTimer);
      window._saveTimer = setTimeout(saveEdits, 1000);
    }
  });

  // Hide controls hint after 5s
  setTimeout(function() {
    if (hint) hint.style.opacity = '0';
  }, 5000);

  // Initial reveal for first slide
  slides[0].querySelectorAll('.reveal').forEach(function(el) {
    el.classList.add('visible');
  });
})();
`;
}

/** HTML 转义 */
function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/** JS 字符串转义（用于 <script> 块内嵌字符串，防止脚本注入） */
function escapeJsString(str: string): string {
  return JSON.stringify(str).replace(/</g, '\\u003c');
}
