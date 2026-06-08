# Data Display Components

Components for presenting data — accordions, badges, cards, chips, items, lists, and text.

## ion-accordion / ion-accordion-group

Expandable/collapsible content sections.

### ion-accordion Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `readonly` | `boolean` | `false` | Prevent interaction without changing opacity. |
| `toggleIcon` | `string` | `'chevronDown'` | Toggle icon (rotates on expand/collapse). |
| `toggleIconSlot` | `"end" \| "start"` | `'end'` | Position of toggle icon in the header item. |
| `value` | `string` | auto-generated | Accordion value identifier. |

### ion-accordion Slots

| Slot | Description |
| --- | --- |
| `header` | Content at the top; used to expand/collapse. |
| `content` | Content shown/hidden based on expanded state. |

### ion-accordion CSS Shadow Parts

| Part | Description |
| --- | --- |
| `content` | Wrapper for the content slot. |
| `expanded` | Can combine with `header`/`content` for expanded state targeting. |
| `header` | Wrapper for the header slot. |

### ion-accordion-group Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `animated` | `boolean` | `true` | Animate expand/collapse. |
| `disabled` | `boolean` | `false` | Disable all accordions. |
| `expand` | `"compact" \| "inset"` | `undefined` | Display mode. |
| `multiple` | `boolean` | `false` | Allow multiple open. |
| `readonly` | `boolean` | `false` | Prevent interaction. |
| `value` | `string \| string[] \| null` | `undefined` | Currently open accordion value(s). |

### ion-accordion-group Events

`ionChange` — Emitted when the expanded accordion changes.

---

## ion-badge

A small status indicator placed near another element.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |

### CSS Custom Properties

`--background`, `--color`, `--padding-bottom`, `--padding-end`, `--padding-start`, `--padding-top`

---

## ion-card / ion-card-header / ion-card-content / ion-card-title / ion-card-subtitle

A container for presenting grouped content.

### ion-card Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `button` | `boolean` | `false` | Render as a button. |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `download` | `string` | `undefined` | Download URL as file. |
| `href` | `string` | `undefined` | URL for hyperlink. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `rel` | `string` | `undefined` | Link relationship. |
| `routerAnimation` | `AnimationBuilder` | `undefined` | Navigation animation. |
| `routerDirection` | `"back" \| "forward" \| "root"` | `'forward'` | Navigation direction. |
| `target` | `string` | `undefined` | Link target. |
| `type` | `"button" \| "reset" \| "submit"` | `'button'` | Button type. |

### ion-card CSS Shadow Parts

| Part | Description |
| --- | --- |
| `native` | The native HTML element wrapper. |

### ion-card CSS Custom Properties

`--background`, `--color`

### ion-card-header Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `translucent` | `boolean` | `false` | Translucent background (iOS). |

### ion-card-title / ion-card-subtitle Properties

Both accept `color` and `mode`.

### ion-card-content

No specific properties. Provides padding for card body content.

---

## ion-chip

A compact element for displaying attributes, actions, or filters.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `outline` | `boolean` | `false` | Outline style. |

### CSS Custom Properties

`--background`, `--color`

---

## ion-item

A row element that can contain text, icons, inputs, and other content. The building block of lists.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `button` | `boolean` | `false` | Render as a button. |
| `color` | `string` | `undefined` | Color from palette. |
| `detail` | `boolean` | varies | Show detail arrow. |
| `detailIcon` | `string` | `'chevronForward'` | Detail arrow icon. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `download` | `string` | `undefined` | Download URL as file. |
| `href` | `string` | `undefined` | URL for hyperlink. |
| `lines` | `"full" \| "inset" \| "none"` | `undefined` | Bottom border style. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `rel` | `string` | `undefined` | Link relationship. |
| `routerAnimation` | `AnimationBuilder` | `undefined` | Navigation animation. |
| `routerDirection` | `"back" \| "forward" \| "root"` | `undefined` | Navigation direction. |
| `target` | `string` | `undefined` | Link target. |
| `type` | `"button" \| "reset" \| "submit"` | `'button'` | Button type. |

### Slots

| Slot | Description |
| --- | --- |
| (default) | Content between named slots. |
| `start` | Content at the leading edge. |
| `end` | Content at the trailing edge. |

### CSS Shadow Parts

| Part | Description |
| --- | --- |
| `container` | Wrapper for the default slot. |
| `detail-icon` | The chevron icon. |
| `inner` | Inner wrapper for item content. |
| `native` | The native HTML element wrapper. |

### CSS Custom Properties

`--background`, `--background-activated`, `--background-activated-opacity`, `--background-focused`, `--background-focused-opacity`, `--background-hover`, `--background-hover-opacity`, `--border-color`, `--border-radius`, `--border-style`, `--border-width`, `--color`, `--color-activated`, `--color-focused`, `--color-hover`, `--detail-icon-color`, `--detail-icon-font-size`, `--detail-icon-opacity`, `--inner-border-width`, `--inner-box-shadow`, `--inner-padding-bottom`, `--inner-padding-end`, `--inner-padding-start`, `--inner-padding-top`, `--min-height`, `--padding-bottom`, `--padding-end`, `--padding-start`, `--padding-top`, `--transition`

---

## ion-item-sliding / ion-item-options / ion-item-option

A list item that reveals option buttons when swiped.

### ion-item-sliding Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `disabled` | `boolean` | `false` | Prevent interaction. |

### ion-item-sliding Events

`ionDrag` — Emitted when sliding position changes.

### ion-item-sliding Methods

| Method | Signature | Description |
| --- | --- | --- |
| `close` | `close() => Promise<void>` | Close the sliding item. |
| `closeOpened` | `closeOpened() => Promise<void>` | Close all sliding items in the list. |
| `getOpenAmount` | `getOpenAmount() => Promise<number>` | Get open amount in pixels. |
| `getSlidingRatio` | `getSlidingRatio() => Promise<number>` | Get ratio of open amount to width. |
| `open` | `open(side?: Side) => Promise<void>` | Open to a specific side. |

### ion-item-options Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `side` | `"start" \| "end"` | `'end'` | Side to reveal on. |

### ion-item-option Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `download` | `string` | `undefined` | Download URL. |
| `expandable` | `boolean` | `false` | Expand to fill on full swipe. |
| `href` | `string` | `undefined` | URL for hyperlink. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `rel` | `string` | `undefined` | Link relationship. |
| `target` | `string` | `undefined` | Link target. |
| `type` | `"button" \| "reset" \| "submit"` | `'button'` | Button type. |

---

## ion-item-divider

A heading row within a list that groups items.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `sticky` | `boolean` | `false` | Stick to top on scroll. |

### Slots

(default), `start`, `end`.

---

## ion-item-group

A container that groups related items and item dividers within a list.

---

## ion-label

A text label placed inside `ion-item`. In modern Ionic, prefer using the `label` property on form components or placing text directly in the default slot of `ion-item`.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `position` | `"fixed" \| "floating" \| "stacked"` | `undefined` | Label position relative to input. |

---

## ion-note

A small text annotation placed inside `ion-item`.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |

---

## ion-list

A container for items that provides consistent styling and optional inset mode.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `inset` | `boolean` | `false` | Add margin and rounded corners. |
| `lines` | `"full" \| "inset" \| "none"` | `undefined` | Border style for child items. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |

### Methods

`closeSlidingItems() => Promise<boolean>` — Close all sliding items in the list.

---

## ion-list-header

A header row at the top of a list.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `lines` | `"full" \| "inset" \| "none"` | `undefined` | Border style. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |

---

## ion-text

A wrapper that applies a color to inline text content.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |

Usage:

```html
<ion-text color="danger">
  <p>This text is red.</p>
</ion-text>
```
