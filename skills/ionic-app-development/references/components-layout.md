# Layout Components

Components for page structure — app shell, content areas, grids, toolbars, and split panes.

## ion-app

The root container for an Ionic application. Required as the outermost Ionic component. Provides the base layout and manages overlays, menus, and other app-level elements.

---

## ion-content

The main scrollable content area of a page.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `fixedSlotPlacement` | `"before" \| "after"` | `'after'` | DOM position of fixed slot elements. |
| `forceOverscroll` | `boolean` | `undefined` | Enable bounce effect even when content does not overflow. |
| `fullscreen` | `boolean` | `false` | Scroll behind headers/footers (for `collapse` effects). |
| `scrollEvents` | `boolean` | `false` | Enable scroll events (must be `true` for `ionScroll` to fire). |
| `scrollX` | `boolean` | `false` | Enable horizontal scrolling. |
| `scrollY` | `boolean` | `true` | Enable vertical scrolling. |

### Events

| Event | Description |
| --- | --- |
| `ionScroll` | Emitted while scrolling (requires `scrollEvents`). |
| `ionScrollStart` | Emitted when scroll starts (requires `scrollEvents`). |
| `ionScrollEnd` | Emitted when scroll ends (requires `scrollEvents`). |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `getScrollElement` | `getScrollElement() => Promise<HTMLElement>` | Get the internal scrollable element. |
| `scrollToTop` | `scrollToTop(duration?: number) => Promise<void>` | Scroll to top. |
| `scrollToBottom` | `scrollToBottom(duration?: number) => Promise<void>` | Scroll to bottom. |
| `scrollToPoint` | `scrollToPoint(x: number, y: number, duration?: number) => Promise<void>` | Scroll to coordinates. |
| `scrollByPoint` | `scrollByPoint(x: number, y: number, duration: number) => Promise<void>` | Scroll by offset. |

### Slots

| Slot | Description |
| --- | --- |
| (default) | Content in the scrollable area. |
| `fixed` | Non-scrolling fixed content. |

### CSS Shadow Parts

| Part | Description |
| --- | --- |
| `scroll` | The scrollable container. |
| `background` | The background layer. |

### CSS Custom Properties

`--background`, `--color`, `--keyboard-offset`, `--offset-bottom`, `--offset-top`, `--padding-bottom`, `--padding-end`, `--padding-start`, `--padding-top`

---

## ion-header

A container for toolbars at the top of a page. Must be a direct child of the page (sibling of `ion-content`).

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `collapse` | `"condense" \| "fade"` | `undefined` | Scroll collapse effect (iOS only). |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `translucent` | `boolean` | `false` | Translucent background (iOS with backdrop-filter). |

---

## ion-footer

A container for toolbars at the bottom of a page. Must be a direct child of the page (sibling of `ion-content`).

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `collapse` | `"fade"` | `undefined` | Scroll collapse effect (iOS only). |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `translucent` | `boolean` | `false` | Translucent background (iOS with backdrop-filter). |

---

## ion-toolbar

A bar that contains buttons, titles, and other content. Placed inside `ion-header` or `ion-footer`.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |

### Slots

| Slot | Description |
| --- | --- |
| (default) | Content without named slots. |
| `start` | Left-positioned content (LTR). |
| `end` | Right-positioned content (LTR). |
| `primary` | Right in iOS, far right in MD. |
| `secondary` | Left in iOS, directly right in MD. |

### CSS Shadow Parts

| Part | Description |
| --- | --- |
| `background` | Background covering the entire toolbar area. |
| `container` | Wrapper for all toolbar content. |
| `content` | Wrapper for the default slot. |

### CSS Custom Properties

`--background`, `--border-color`, `--border-style`, `--border-width`, `--color`, `--min-height`, `--opacity`, `--padding-bottom`, `--padding-end`, `--padding-start`, `--padding-top`

---

## ion-title

The title text within a toolbar.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `size` | `"large" \| "small"` | `undefined` | Title size. `large` for collapsible large titles (iOS). |

### CSS Custom Properties

`--color`

---

## ion-buttons

A container for buttons within a toolbar. Controls button placement based on the toolbar slot.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `collapse` | `boolean` | `false` | Collapse buttons when header collapses (iOS). |

---

## ion-back-button

A navigation button that returns to the previous page in the navigation stack.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `defaultHref` | `string` | `undefined` | Fallback URL when no history exists. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `icon` | `string` | `undefined` | Custom icon. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `routerAnimation` | `AnimationBuilder` | `undefined` | Custom animation. |
| `text` | `string` | `undefined` | Button text. |
| `type` | `"button" \| "reset" \| "submit"` | `'button'` | Button type. |

### CSS Custom Properties

`--background`, `--background-focused`, `--background-hover`, `--background-focused-opacity`, `--background-hover-opacity`, `--border-radius`, `--color`, `--color-focused`, `--color-hover`, `--icon-font-size`, `--icon-font-weight`, `--icon-margin-bottom`, `--icon-margin-end`, `--icon-margin-start`, `--icon-margin-top`, `--icon-padding-bottom`, `--icon-padding-end`, `--icon-padding-start`, `--icon-padding-top`, `--margin-bottom`, `--margin-end`, `--margin-start`, `--margin-top`, `--min-height`, `--min-width`, `--opacity`, `--padding-bottom`, `--padding-end`, `--padding-start`, `--padding-top`, `--ripple-color`, `--transition`

---

## ion-grid / ion-row / ion-col

A 12-column flexbox grid system.

### ion-grid Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `fixed` | `boolean` | `false` | Restrict width based on screen size. |

### ion-col Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `offset` | `string` | `undefined` | Columns to offset (0-12). |
| `offsetLg` | `string` | `undefined` | Offset at lg breakpoint. |
| `offsetMd` | `string` | `undefined` | Offset at md breakpoint. |
| `offsetSm` | `string` | `undefined` | Offset at sm breakpoint. |
| `offsetXl` | `string` | `undefined` | Offset at xl breakpoint. |
| `offsetXs` | `string` | `undefined` | Offset at xs breakpoint. |
| `pull` | `string` | `undefined` | Columns to pull (reorder). |
| `pullLg` | `string` | `undefined` | Pull at lg breakpoint. |
| `pullMd` | `string` | `undefined` | Pull at md breakpoint. |
| `pullSm` | `string` | `undefined` | Pull at sm breakpoint. |
| `pullXl` | `string` | `undefined` | Pull at xl breakpoint. |
| `pullXs` | `string` | `undefined` | Pull at xs breakpoint. |
| `push` | `string` | `undefined` | Columns to push (reorder). |
| `pushLg` | `string` | `undefined` | Push at lg breakpoint. |
| `pushMd` | `string` | `undefined` | Push at md breakpoint. |
| `pushSm` | `string` | `undefined` | Push at sm breakpoint. |
| `pushXl` | `string` | `undefined` | Push at xl breakpoint. |
| `pushXs` | `string` | `undefined` | Push at xs breakpoint. |
| `size` | `string` | `undefined` | Number of columns (1-12). |
| `sizeLg` | `string` | `undefined` | Size at lg breakpoint. |
| `sizeMd` | `string` | `undefined` | Size at md breakpoint. |
| `sizeSm` | `string` | `undefined` | Size at sm breakpoint. |
| `sizeXl` | `string` | `undefined` | Size at xl breakpoint. |
| `sizeXs` | `string` | `undefined` | Size at xs breakpoint. |

### Responsive Breakpoints

| Breakpoint | Min Width | Properties Suffix |
| --- | --- | --- |
| `xs` | 0 | `Xs` |
| `sm` | 576px | `Sm` |
| `md` | 768px | `Md` |
| `lg` | 992px | `Lg` |
| `xl` | 1200px | `Xl` |

### Grid CSS Variables

`--ion-grid-columns` (default: 12), `--ion-grid-padding-xs` through `--ion-grid-padding-xl`, `--ion-grid-column-padding-xs` through `--ion-grid-column-padding-xl`.

Use `.ion-no-padding` to remove grid and column padding.

---

## ion-split-pane

A multi-view layout that shows a side pane alongside main content when the viewport exceeds a breakpoint.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `contentId` | `string` | `undefined` | ID of the main content element. |
| `disabled` | `boolean` | `false` | Hide the split pane. |
| `when` | `boolean \| string` | `'lg'` | Breakpoint or media query for showing the side pane. Shortcuts: `xs`, `sm`, `md`, `lg`, `xl`. |

### Events

`ionSplitPaneVisible` — Emitted when visibility changes.

### CSS Custom Properties

`--border`, `--side-max-width`, `--side-min-width`, `--side-width`
