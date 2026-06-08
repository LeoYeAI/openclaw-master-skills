# Overlay Components

Overlay components present content on top of the current page — dialogs, modals, popovers, toasts, and loading indicators.

## ion-action-sheet

A dialog that slides up from the bottom, presenting a set of buttons for the user to choose from.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `animated` | `boolean` | `true` | Animate the action sheet. |
| `backdropDismiss` | `boolean` | `true` | Dismiss when backdrop is clicked. |
| `buttons` | `(string \| ActionSheetButton)[]` | `[]` | Array of buttons. |
| `cssClass` | `string \| string[]` | `undefined` | Custom CSS classes. |
| `enterAnimation` | `AnimationBuilder` | `undefined` | Custom enter animation. |
| `header` | `string` | `undefined` | Title text. |
| `htmlAttributes` | `object` | `undefined` | Additional HTML attributes. |
| `isOpen` | `boolean` | `false` | Controls presentation state. |
| `keyboardClose` | `boolean` | `true` | Auto-dismiss keyboard on present. |
| `leaveAnimation` | `AnimationBuilder` | `undefined` | Custom leave animation. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `subHeader` | `string` | `undefined` | Subtitle text. |
| `translucent` | `boolean` | `false` | Translucent background (iOS only). |
| `trigger` | `string` | `undefined` | ID of element that triggers opening. |

### Events

| Event | Description |
| --- | --- |
| `ionActionSheetDidDismiss` | Emitted after dismissed. |
| `ionActionSheetDidPresent` | Emitted after presented. |
| `ionActionSheetWillDismiss` | Emitted before dismissing. |
| `ionActionSheetWillPresent` | Emitted before presenting. |
| `didDismiss` | Shorthand for `ionActionSheetDidDismiss`. |
| `didPresent` | Shorthand for `ionActionSheetDidPresent`. |
| `willDismiss` | Shorthand for `ionActionSheetWillDismiss`. |
| `willPresent` | Shorthand for `ionActionSheetWillPresent`. |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `dismiss` | `dismiss(data?: any, role?: string) => Promise<boolean>` | Dismiss the action sheet. |
| `onDidDismiss` | `onDidDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when dismissed. |
| `onWillDismiss` | `onWillDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when about to dismiss. |
| `present` | `present() => Promise<void>` | Present the action sheet. |

### CSS Custom Properties

`--backdrop-opacity`, `--background`, `--button-background`, `--button-background-activated`, `--button-background-activated-opacity`, `--button-background-focused`, `--button-background-focused-opacity`, `--button-background-hover`, `--button-background-hover-opacity`, `--button-background-selected`, `--button-background-selected-opacity`, `--button-color`, `--button-color-activated`, `--button-color-disabled`, `--button-color-focused`, `--button-color-hover`, `--button-color-selected`, `--color`, `--height`, `--max-height`, `--max-width`, `--min-height`, `--min-width`, `--width`

---

## ion-alert

A dialog that presents a message, optional inputs, and buttons.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `animated` | `boolean` | `true` | Animate the alert. |
| `backdropDismiss` | `boolean` | `true` | Dismiss when backdrop is clicked. |
| `buttons` | `(string \| AlertButton)[]` | `[]` | Array of buttons. |
| `cssClass` | `string \| string[]` | `undefined` | Custom CSS classes. |
| `enterAnimation` | `AnimationBuilder` | `undefined` | Custom enter animation. |
| `header` | `string` | `undefined` | Main title text. |
| `htmlAttributes` | `object` | `undefined` | Additional HTML attributes. |
| `inputs` | `AlertInput[]` | `[]` | Array of inputs to show. |
| `isOpen` | `boolean` | `false` | Controls presentation state. |
| `keyboardClose` | `boolean` | `true` | Auto-dismiss keyboard on present. |
| `leaveAnimation` | `AnimationBuilder` | `undefined` | Custom leave animation. |
| `message` | `string \| IonicSafeString` | `undefined` | Main message content. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `subHeader` | `string` | `undefined` | Subtitle text. |
| `translucent` | `boolean` | `false` | Translucent background (iOS only). |
| `trigger` | `string` | `undefined` | ID of element that triggers opening. |

### Events

| Event | Description |
| --- | --- |
| `ionAlertDidDismiss` | Emitted after dismissed. |
| `ionAlertDidPresent` | Emitted after presented. |
| `ionAlertWillDismiss` | Emitted before dismissing. |
| `ionAlertWillPresent` | Emitted before presenting. |
| `didDismiss` | Shorthand for `ionAlertDidDismiss`. |
| `didPresent` | Shorthand for `ionAlertDidPresent`. |
| `willDismiss` | Shorthand for `ionAlertWillDismiss`. |
| `willPresent` | Shorthand for `ionAlertWillPresent`. |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `dismiss` | `dismiss(data?: any, role?: string) => Promise<boolean>` | Dismiss the alert. |
| `onDidDismiss` | `onDidDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when dismissed. |
| `onWillDismiss` | `onWillDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when about to dismiss. |
| `present` | `present() => Promise<void>` | Present the alert. |

### CSS Custom Properties

`--backdrop-opacity`, `--background`, `--height`, `--max-height`, `--max-width`, `--min-height`, `--min-width`, `--width`

---

## ion-loading

A loading indicator overlay that blocks user interaction while an async operation completes.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `animated` | `boolean` | `true` | Animate the loading indicator. |
| `backdropDismiss` | `boolean` | `false` | Dismiss when backdrop is clicked. |
| `cssClass` | `string \| string[]` | `undefined` | Custom CSS classes. |
| `duration` | `number` | `0` | Milliseconds before auto-dismiss. 0 = no auto-dismiss. |
| `enterAnimation` | `AnimationBuilder` | `undefined` | Custom enter animation. |
| `htmlAttributes` | `object` | `undefined` | Additional HTML attributes. |
| `isOpen` | `boolean` | `false` | Controls presentation state. |
| `keyboardClose` | `boolean` | `true` | Auto-dismiss keyboard on present. |
| `leaveAnimation` | `AnimationBuilder` | `undefined` | Custom leave animation. |
| `message` | `string \| IonicSafeString` | `undefined` | Display text content. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `showBackdrop` | `boolean` | `true` | Show a backdrop behind the indicator. |
| `spinner` | `SpinnerTypes \| null` | `undefined` | Type of loading spinner. |
| `translucent` | `boolean` | `false` | Translucent background (iOS only). |
| `trigger` | `string` | `undefined` | ID of element that triggers opening. |

### Events

| Event | Description |
| --- | --- |
| `ionLoadingDidDismiss` | Emitted after dismissed. |
| `ionLoadingDidPresent` | Emitted after presented. |
| `ionLoadingWillDismiss` | Emitted before dismissing. |
| `ionLoadingWillPresent` | Emitted before presenting. |
| `didDismiss` | Shorthand for `ionLoadingDidDismiss`. |
| `didPresent` | Shorthand for `ionLoadingDidPresent`. |
| `willDismiss` | Shorthand for `ionLoadingWillDismiss`. |
| `willPresent` | Shorthand for `ionLoadingWillPresent`. |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `dismiss` | `dismiss(data?: any, role?: string) => Promise<boolean>` | Dismiss the loading indicator. |
| `onDidDismiss` | `onDidDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when dismissed. |
| `onWillDismiss` | `onWillDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when about to dismiss. |
| `present` | `present() => Promise<void>` | Present the loading indicator. |

### CSS Custom Properties

`--backdrop-opacity`, `--background`, `--height`, `--max-height`, `--max-width`, `--min-height`, `--min-width`, `--spinner-color`, `--width`

---

## ion-modal

A dialog that slides up or appears as a card/sheet, presenting custom content.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `animated` | `boolean` | `true` | Animate the modal. |
| `backdropBreakpoint` | `number` | `0` | Breakpoint (0-1) when backdrop fades in (sheet modals). |
| `backdropDismiss` | `boolean` | `true` | Dismiss when backdrop is clicked. |
| `breakpoints` | `number[]` | `undefined` | Snap points for sheet modals (0-1). |
| `canDismiss` | `boolean \| (() => Promise<boolean>)` | `true` | Controls whether modal can be dismissed. |
| `enterAnimation` | `AnimationBuilder` | `undefined` | Custom enter animation. |
| `expandToScroll` | `boolean` | `true` | Scrolling expands sheet to next breakpoint. |
| `focusTrap` | `boolean` | `true` | Trap focus within the modal. |
| `handle` | `boolean` | `undefined` | Show drag handle for sheet modals. |
| `handleBehavior` | `"cycle" \| "none"` | `'none'` | Handle interaction behavior. |
| `htmlAttributes` | `object` | `undefined` | Additional HTML attributes. |
| `initialBreakpoint` | `number` | `undefined` | Starting breakpoint for sheet modals. |
| `isOpen` | `boolean` | `false` | Controls presentation state. |
| `keepContentsMounted` | `boolean` | `false` | Mount content on creation, persist until destruction. |
| `keyboardClose` | `boolean` | `true` | Auto-dismiss keyboard on present. |
| `leaveAnimation` | `AnimationBuilder` | `undefined` | Custom leave animation. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `presentingElement` | `HTMLElement` | `undefined` | Element for card modal stacking effect. |
| `showBackdrop` | `boolean` | `true` | Show a backdrop behind the modal. |
| `trigger` | `string` | `undefined` | ID of element that triggers opening. |

### Events

| Event | Description |
| --- | --- |
| `ionModalDidDismiss` | Emitted after dismissed. |
| `ionModalDidPresent` | Emitted after presented. |
| `ionModalWillDismiss` | Emitted before dismissing. |
| `ionModalWillPresent` | Emitted before presenting. |
| `ionBreakpointDidChange` | Emitted when sheet breakpoint changes. |
| `ionDragEnd` | Emitted when drag gesture completes. |
| `ionDragMove` | Emitted continuously during drag. |
| `ionDragStart` | Emitted when drag gesture starts. |
| `didDismiss` | Shorthand for `ionModalDidDismiss`. |
| `didPresent` | Shorthand for `ionModalDidPresent`. |
| `willDismiss` | Shorthand for `ionModalWillDismiss`. |
| `willPresent` | Shorthand for `ionModalWillPresent`. |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `dismiss` | `dismiss(data?: any, role?: string) => Promise<boolean>` | Dismiss the modal. |
| `getCurrentBreakpoint` | `getCurrentBreakpoint() => Promise<number \| undefined>` | Get current sheet breakpoint. |
| `onDidDismiss` | `onDidDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when dismissed. |
| `onWillDismiss` | `onWillDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when about to dismiss. |
| `present` | `present() => Promise<void>` | Present the modal. |
| `setCurrentBreakpoint` | `setCurrentBreakpoint(breakpoint: number) => Promise<void>` | Move sheet to a breakpoint. |

### Slots

| Slot | Description |
| --- | --- |
| (default) | Content placed in `.modal-content`. |

### CSS Shadow Parts

| Part | Description |
| --- | --- |
| `backdrop` | The backdrop overlay element. |
| `content` | Wrapper for default slot content. |
| `handle` | Draggable handle on sheet modals. |

### CSS Custom Properties

`--backdrop-opacity`, `--background`, `--border-color`, `--border-radius`, `--border-style`, `--border-width`, `--height`, `--max-height`, `--max-width`, `--min-height`, `--min-width`, `--width`

---

## ion-popover

A floating overlay positioned relative to a trigger element.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `alignment` | `"center" \| "end" \| "start"` | `undefined` | Align popover content with reference point. |
| `animated` | `boolean` | `true` | Animate the popover. |
| `arrow` | `boolean` | `true` | Display an arrow pointing at the reference. |
| `backdropDismiss` | `boolean` | `true` | Dismiss when backdrop is clicked. |
| `component` | `Function \| HTMLElement \| string` | `undefined` | Component to display inside. |
| `componentProps` | `object` | `undefined` | Data passed to the component. |
| `dismissOnSelect` | `boolean` | `false` | Auto-dismiss when content is clicked. |
| `enterAnimation` | `AnimationBuilder` | `undefined` | Custom enter animation. |
| `event` | `any` | `undefined` | Event to pass to the animation. |
| `focusTrap` | `boolean` | `true` | Trap focus within the popover. |
| `htmlAttributes` | `object` | `undefined` | Additional HTML attributes. |
| `isOpen` | `boolean` | `false` | Controls presentation state. |
| `keepContentsMounted` | `boolean` | `false` | Mount content on creation. |
| `keyboardClose` | `boolean` | `true` | Auto-dismiss keyboard on present. |
| `leaveAnimation` | `AnimationBuilder` | `undefined` | Custom leave animation. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `reference` | `"trigger" \| "event"` | `'trigger'` | Position reference point. |
| `showBackdrop` | `boolean` | `true` | Show a backdrop. |
| `side` | `"top" \| "right" \| "bottom" \| "left" \| "start" \| "end"` | `'bottom'` | Side of the reference to position on. |
| `size` | `"auto" \| "cover"` | `'auto'` | How popover width is calculated. |
| `translucent` | `boolean` | `false` | Translucent background (iOS only). |
| `trigger` | `string` | `undefined` | ID of trigger element. |
| `triggerAction` | `"click" \| "hover" \| "context-menu"` | `'click'` | Interaction type that opens the popover. |

### Events

| Event | Description |
| --- | --- |
| `ionPopoverDidDismiss` | Emitted after dismissed. |
| `ionPopoverDidPresent` | Emitted after presented. |
| `ionPopoverWillDismiss` | Emitted before dismissing. |
| `ionPopoverWillPresent` | Emitted before presenting. |
| `didDismiss` | Shorthand for `ionPopoverDidDismiss`. |
| `didPresent` | Shorthand for `ionPopoverDidPresent`. |
| `willDismiss` | Shorthand for `ionPopoverWillDismiss`. |
| `willPresent` | Shorthand for `ionPopoverWillPresent`. |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `dismiss` | `dismiss(data?: any, role?: string, dismissParentPopover?: boolean) => Promise<boolean>` | Dismiss the popover. |
| `onDidDismiss` | `onDidDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when dismissed. |
| `onWillDismiss` | `onWillDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when about to dismiss. |
| `present` | `present(event?: MouseEvent \| TouchEvent \| PointerEvent) => Promise<void>` | Present the popover. |

### Slots

| Slot | Description |
| --- | --- |
| (default) | Content placed in `.popover-content`. |

### CSS Shadow Parts

| Part | Description |
| --- | --- |
| `arrow` | Arrow pointing to reference (iOS only). |
| `backdrop` | The backdrop element. |
| `content` | Wrapper for default slot content. |

### CSS Custom Properties

`--backdrop-opacity`, `--background`, `--box-shadow`, `--height`, `--max-height`, `--max-width`, `--min-height`, `--min-width`, `--offset-x`, `--offset-y`, `--width`

---

## ion-toast

A non-blocking notification that appears temporarily at the top, bottom, or middle of the screen.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `animated` | `boolean` | `true` | Animate the toast. |
| `buttons` | `(string \| ToastButton)[]` | `undefined` | Array of buttons. |
| `color` | `string` | `undefined` | Color from palette. |
| `cssClass` | `string \| string[]` | `undefined` | Custom CSS classes. |
| `duration` | `number` | `0` | Milliseconds before auto-dismiss. 0 = no auto-dismiss. |
| `enterAnimation` | `AnimationBuilder` | `undefined` | Custom enter animation. |
| `header` | `string` | `undefined` | Header text. |
| `htmlAttributes` | `object` | `undefined` | Additional HTML attributes. |
| `icon` | `string` | `undefined` | Icon name or SVG path. |
| `isOpen` | `boolean` | `false` | Controls presentation state. |
| `keyboardClose` | `boolean` | `false` | Auto-dismiss keyboard on present. |
| `layout` | `"baseline" \| "stacked"` | `'baseline'` | Layout of message and buttons. |
| `leaveAnimation` | `AnimationBuilder` | `undefined` | Custom leave animation. |
| `message` | `string \| IonicSafeString` | `undefined` | Message content. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `position` | `"top" \| "bottom" \| "middle"` | `'bottom'` | Screen position. |
| `positionAnchor` | `HTMLElement \| string` | `undefined` | Element to anchor position to. |
| `swipeGesture` | `"vertical"` | `undefined` | Swipe direction to dismiss. |
| `translucent` | `boolean` | `false` | Translucent background (iOS only). |
| `trigger` | `string` | `undefined` | ID of trigger element. |

### Events

| Event | Description |
| --- | --- |
| `ionToastDidDismiss` | Emitted after dismissed. |
| `ionToastDidPresent` | Emitted after presented. |
| `ionToastWillDismiss` | Emitted before dismissing. |
| `ionToastWillPresent` | Emitted before presenting. |
| `didDismiss` | Shorthand for `ionToastDidDismiss`. |
| `didPresent` | Shorthand for `ionToastDidPresent`. |
| `willDismiss` | Shorthand for `ionToastWillDismiss`. |
| `willPresent` | Shorthand for `ionToastWillPresent`. |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `dismiss` | `dismiss(data?: any, role?: string) => Promise<boolean>` | Dismiss the toast. |
| `onDidDismiss` | `onDidDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when dismissed. |
| `onWillDismiss` | `onWillDismiss<T>() => Promise<OverlayEventDetail<T>>` | Resolves when about to dismiss. |
| `present` | `present() => Promise<void>` | Present the toast. |

### CSS Shadow Parts

`button`, `container`, `content`, `header`, `icon`, `message`, `wrapper`

### CSS Custom Properties

`--background`, `--border-color`, `--border-radius`, `--border-style`, `--border-width`, `--box-shadow`, `--button-color`, `--color`, `--end`, `--height`, `--max-height`, `--max-width`, `--min-height`, `--min-width`, `--start`, `--white-space`, `--width`

---

## ion-backdrop

A transparent overlay placed behind overlays to handle dismiss-on-click behavior. Typically used internally by other overlay components. Not commonly used directly.
