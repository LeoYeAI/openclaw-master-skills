# Action & Button Components

Components for user actions — buttons, floating action buttons, and ripple effects.

## ion-button

A clickable element for triggering actions or navigation.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `buttonType` | `string` | `'button'` | The type of button. |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `download` | `string` | `undefined` | Download URL as local file. |
| `expand` | `"block" \| "full"` | `undefined` | Full-width button style. `block` has margin; `full` has no margin or border-radius. |
| `fill` | `"clear" \| "default" \| "outline" \| "solid"` | `undefined` | Background fill style. |
| `form` | `HTMLFormElement \| string` | `undefined` | Form element or ID. |
| `href` | `string` | `undefined` | URL for hyperlink behavior. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `rel` | `string` | `undefined` | Link relationship. |
| `routerAnimation` | `AnimationBuilder` | `undefined` | Custom navigation animation. |
| `routerDirection` | `"back" \| "forward" \| "root"` | `'forward'` | Navigation transition direction. |
| `shape` | `"round"` | `undefined` | Rounded corners. |
| `size` | `"small" \| "default" \| "large"` | `undefined` | Button height and padding. |
| `strong` | `boolean` | `false` | Heavier font weight. |
| `target` | `string` | `undefined` | Where to display linked URL. |
| `type` | `"button" \| "reset" \| "submit"` | `'button'` | HTML button type. |

### Events

| Event | Description |
| --- | --- |
| `ionBlur` | Emitted when the button loses focus. |
| `ionFocus` | Emitted when the button has focus. |

### Slots

| Slot | Description |
| --- | --- |
| (default) | Content between named slots. |
| `start` | Content left of button text (LTR). |
| `end` | Content right of button text (LTR). |
| `icon-only` | For an icon in a button with no text. |

### CSS Shadow Parts

| Part | Description |
| --- | --- |
| `native` | The native HTML button or anchor element. |

### CSS Custom Properties

`--background`, `--background-activated`, `--background-activated-opacity`, `--background-focused`, `--background-focused-opacity`, `--background-hover`, `--background-hover-opacity`, `--border-color`, `--border-radius`, `--border-style`, `--border-width`, `--box-shadow`, `--color`, `--color-activated`, `--color-focused`, `--color-hover`, `--opacity`, `--padding-bottom`, `--padding-end`, `--padding-start`, `--padding-top`, `--ripple-color`, `--transition`

---

## ion-fab

A fixed-position container for a floating action button and optional speed-dial list.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `activated` | `boolean` | `false` | Activate the FAB and all child FAB lists. |
| `edge` | `boolean` | `false` | Display on the edge of a header/footer. |
| `horizontal` | `"start" \| "center" \| "end"` | `undefined` | Horizontal position. |
| `vertical` | `"top" \| "center" \| "bottom"` | `undefined` | Vertical position. |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `close` | `close() => Promise<void>` | Close an active FAB list. |

---

## ion-fab-button

The main button within an `ion-fab`. Also used as items inside `ion-fab-list`.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `activated` | `boolean` | `false` | Show close icon when active. |
| `closeIcon` | `string` | `'close'` | Icon shown when activated. |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `download` | `string` | `undefined` | Download URL as file. |
| `href` | `string` | `undefined` | URL for hyperlink. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `rel` | `string` | `undefined` | Link relationship. |
| `routerAnimation` | `AnimationBuilder` | `undefined` | Custom navigation animation. |
| `routerDirection` | `"back" \| "forward" \| "root"` | `'forward'` | Navigation direction. |
| `show` | `boolean` | `false` | Visibility within fab-list. |
| `size` | `"small"` | `undefined` | Mini button variant. |
| `target` | `string` | `undefined` | Link target. |
| `translucent` | `boolean` | `false` | Translucent background (iOS only). |
| `type` | `"button" \| "reset" \| "submit"` | `'button'` | Button type. |

### Events

| Event | Description |
| --- | --- |
| `ionBlur` | Emitted when button loses focus. |
| `ionFocus` | Emitted when button has focus. |

### CSS Shadow Parts

| Part | Description |
| --- | --- |
| `close-icon` | The close icon element. |
| `native` | The native HTML button or anchor. |

---

## ion-fab-list

A speed-dial list of `ion-fab-button` elements that expands from a parent `ion-fab`.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `activated` | `boolean` | `false` | Show or hide the list. |
| `side` | `"start" \| "end" \| "top" \| "bottom"` | `'bottom'` | Direction to expand. |

---

## ion-ripple-effect

A Material Design ripple animation applied to a parent element on click/tap. Used internally by `ion-button` and other interactive components in `md` mode.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `type` | `"bounded" \| "unbounded"` | `'bounded'` | Ripple animation type. `bounded` stays within the element; `unbounded` extends beyond. |

To use on a custom element, add `ion-activatable` class and include `<ion-ripple-effect>` as a child:

```html
<div class="ion-activatable" style="position: relative;">
  Custom content
  <ion-ripple-effect></ion-ripple-effect>
</div>
```
