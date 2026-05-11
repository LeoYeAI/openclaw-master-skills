# Web Style Extraction Checklist

## A. Meta
- [ ] Source URL
- [ ] Page title
- [ ] Viewport
- [ ] Extraction mode: live render / static source / screenshot-assisted
- [ ] Dark mode present?
- [ ] Reduced motion present?
- [ ] Shadow DOM/custom elements present?
- [ ] Canvas/WebGL/video-heavy?

## B. Typography
- [ ] Sans font stack
- [ ] Mono font stack
- [ ] Font weights
- [ ] Type scale
- [ ] Line heights
- [ ] Letter spacing
- [ ] Heading/body/link/button/input styles

## C. Color
- [ ] Page background
- [ ] Surface layers
- [ ] Text primary/secondary/muted/inverse
- [ ] Border/divider
- [ ] Brand/accent
- [ ] State colors
- [ ] Code colors
- [ ] Gradients/overlays

## D. Layout
- [ ] Max content width
- [ ] Grid/gutter
- [ ] Section spacing
- [ ] Component padding
- [ ] Gap rhythm
- [ ] Mobile/tablet/desktop differences

## E. Surface / Shape / Elevation
- [ ] Radius scale
- [ ] Border patterns
- [ ] Shadow scale
- [ ] Blur/backdrop
- [ ] Focus ring
- [ ] Overlay layering

## F. Motion
- [ ] Fast/normal/slow durations
- [ ] Easing curves
- [ ] Hover motion
- [ ] Enter/exit motion
- [ ] Loading motion
- [ ] Reduced motion fallback

## G. Components
- [ ] Buttons
- [ ] Cards
- [ ] Forms
- [ ] Tags/badges
- [ ] Navigation
- [ ] Tables
- [ ] Alerts/callouts
- [ ] Modals/popovers/tooltips
- [ ] Code blocks
- [ ] Empty states
- [ ] Toasts/skeletons

## H. States
- [ ] Default
- [ ] Hover
- [ ] Focus-visible
- [ ] Active
- [ ] Selected
- [ ] Disabled
- [ ] Loading
- [ ] Open/expanded

## I. Themes / Responsiveness
- [ ] Light
- [ ] Dark
- [ ] Breakpoints
- [ ] Type/spacing adaptation
- [ ] Print behavior if relevant

## J. Atmosphere / Background
- [ ] html/body/main 的最终背景色
- [ ] 是否有 background-image
- [ ] 是否有 linear-gradient / radial-gradient / conic-gradient
- [ ] 是否有 repeating-linear-gradient / repeating-radial-gradient
- [ ] 是否存在背景图片 / SVG / data URI
- [ ] 是否有 noise / grain / texture overlay
- [ ] 是否有 pseudo-element 背景层
- [ ] 是否有 section 之间的背景切换
- [ ] 是否有 hero 专属背景处理
- [ ] 是否有 blur / glow / vignette / spotlight
- [ ] 是否有 scanline / grid / stripe / dotted pattern
- [ ] 是否有 blend-mode / mask-image / filter
- [ ] 是否有装饰性绝对定位元素
- [ ] 是否有滚动时出现的背景动效
- [ ] 是否可以抽象为 site motif

## K. Motifs
- [ ] 是否存在条纹母题
- [ ] 是否存在网格母题
- [ ] 是否存在点阵母题
- [ ] 是否存在 editorial line / rule
- [ ] 是否存在终端/工业风扫描线
- [ ] 是否存在反复出现的 glow / blur 造型
- [ ] 是否存在 signature hover pattern
- [ ] 是否存在 recurring pseudo-element ornaments
- [ ] 是否存在 recurring mask / clip treatment
- [ ] 是否存在应该上升为品牌视觉 DNA 的局部装饰

## L. Output quality
- [ ] Semantic tokens present
- [ ] Component archetypes present
- [ ] Background system present
- [ ] Motif system present
- [ ] Manifest present
- [ ] Specimen HTML present
- [ ] Limitations explained
- [ ] Reusable for future AI page generation