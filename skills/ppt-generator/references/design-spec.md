# 设计规范详细文档

## 背景效果

### 主背景
- 主色：#000000 或 #0a0a0a
- 深色渐变底色

### 动态光斑（必须包含）
每页必须包含 1~3 个模糊光斑：

```css
.light-spot {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
  animation: float 20s ease-in-out infinite;
}

.light-spot-1 { background: #3b82f6; }  /* 蓝色 */
.light-spot-2 { background: #8b5cf6; }  /* 紫色 */
.light-spot-3 { background: #06b6d4; }  /* 青色 */

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(50px, -30px); }
  50% { transform: translate(-30px, 50px); }
  75% { transform: translate(-50px, -20px); }
}
```

## 字体加载（国内CDN）

```html
<!-- HarmonyOS Sans SC -->
<link href="https://s1.hdslb.com/bfs/static/jinkela/long/font/regular.css" rel="stylesheet">

<!-- 思源黑体备选 -->
<link href="https://fonts.loli.net/css2?family=Noto+Sans+SC:wght@300;400;700;900&display=swap" rel="stylesheet">

<!-- Inter 英文字体 -->
<link href="https://fonts.loli.net/css2?family=Inter:wght@300;400;700;900&display=swap" rel="stylesheet">
```

## 排版层级

```css
/* H1 超大标题 */
.slide-title {
  font-size: 3rem;      /* 48px */
  font-weight: 900;     /* font-black */
  line-height: 1.2;
  color: #ffffff;
}

/* H2 副标题 */
.slide-subtitle {
  font-size: 1.5rem;    /* 24px */
  font-weight: 700;     /* font-bold */
  color: #ffffff;
}

/* P 说明文字 */
.slide-text {
  font-size: 1.125rem;  /* 18px */
  font-weight: 300;     /* font-light */
  color: #9ca3af;
}
```

## 间距规范

- 元素间距：space-y-8 以上（32px+）
- 页面内边距：p-8 或 p-12
- 内容居中：flex items-center justify-center

## 页面容器

```css
.slide {
  width: 100%;
  height: 100vh;
  aspect-ratio: 9/16;
  max-width: 450px;      /* 竖屏限制 */
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
```

## 切换动画

```css
.slide {
  opacity: 0;
  transform: translateX(100%);
  transition: all 0.5s ease-out;
}

.slide.active {
  opacity: 1;
  transform: translateX(0);
}

.slide.prev {
  transform: translateX(-100%);
}
```
