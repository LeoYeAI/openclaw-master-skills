# Form Components

Components for user input — text fields, checkboxes, toggles, selects, date pickers, and more.

## ion-input

A text input field with support for labels, validation states, and various input types.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `autocapitalize` | `string` | `'off'` | Text capitalization behavior. |
| `autocomplete` | `string` | `'off'` | Browser autocomplete hint. |
| `autocorrect` | `"off" \| "on"` | `'off'` | Auto correction. |
| `autofocus` | `boolean` | `false` | Focus on page load. |
| `clearInput` | `boolean` | `false` | Show clear icon when there is a value. |
| `clearInputIcon` | `string` | `undefined` | Custom clear button icon. |
| `clearOnEdit` | `boolean` | `undefined` | Clear value after focus upon edit. |
| `color` | `string` | `undefined` | Color from palette. |
| `counter` | `boolean` | `false` | Show character counter. |
| `counterFormatter` | `(inputLength: number, maxLength: number) => string` | `undefined` | Custom counter text. |
| `debounce` | `number` | `undefined` | Delay in ms before `ionInput` fires. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `enterkeyhint` | `"done" \| "enter" \| "go" \| "next" \| "previous" \| "search" \| "send"` | `undefined` | Enter key display hint. |
| `errorText` | `string` | `undefined` | Error text shown when invalid. |
| `fill` | `"outline" \| "solid"` | `undefined` | Background fill style. |
| `helperText` | `string` | `undefined` | Helper text shown when valid. |
| `inputmode` | `"decimal" \| "email" \| "none" \| "numeric" \| "search" \| "tel" \| "text" \| "url"` | `undefined` | Keyboard type hint. |
| `label` | `string` | `undefined` | Label text. |
| `labelPlacement` | `"end" \| "fixed" \| "floating" \| "stacked" \| "start"` | `'start'` | Label position. |
| `max` | `number \| string` | `undefined` | Maximum value. |
| `maxlength` | `number` | `undefined` | Maximum character count. |
| `min` | `number \| string` | `undefined` | Minimum value. |
| `minlength` | `number` | `undefined` | Minimum character count. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `multiple` | `boolean` | `undefined` | Allow multiple values. |
| `name` | `string` | auto-generated | Form control name. |
| `pattern` | `string` | `undefined` | Regex validation pattern. |
| `placeholder` | `string` | `undefined` | Placeholder text. |
| `readonly` | `boolean` | `false` | Prevent value modification. |
| `required` | `boolean` | `false` | Required field. |
| `shape` | `"round"` | `undefined` | Rounded border radius. |
| `spellcheck` | `boolean` | `false` | Enable spellcheck. |
| `step` | `string` | `undefined` | Value increment step. |
| `type` | `"date" \| "datetime-local" \| "email" \| "month" \| "number" \| "password" \| "search" \| "tel" \| "text" \| "time" \| "url" \| "week"` | `'text'` | Input type. |
| `value` | `string \| number \| null` | `''` | Input value. |

### Events

| Event | Description |
| --- | --- |
| `ionBlur` | Input loses focus. |
| `ionChange` | Value committed (blur or enter, not on each keystroke). |
| `ionFocus` | Input receives focus. |
| `ionInput` | Value modified (fires on each keystroke). |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `getInputElement` | `getInputElement() => Promise<HTMLInputElement>` | Get the native input element. |
| `setFocus` | `setFocus() => Promise<void>` | Set focus on the input. |

### Slots

| Slot | Description |
| --- | --- |
| `start` | Content at the leading edge. |
| `end` | Content at the trailing edge. |
| `label` | Custom label content. |

### CSS Custom Properties

`--background`, `--border-color`, `--border-radius`, `--border-style`, `--border-width`, `--color`, `--highlight-color-focused`, `--highlight-color-invalid`, `--highlight-color-valid`, `--highlight-height`, `--padding-bottom`, `--padding-end`, `--padding-start`, `--padding-top`, `--placeholder-color`, `--placeholder-font-style`, `--placeholder-font-weight`, `--placeholder-opacity`

---

## ion-textarea

A multi-line text input field.

### Properties

Same pattern as `ion-input` with these differences/additions:

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `autoGrow` | `boolean` | `false` | Expand height based on content. |
| `cols` | `number` | `undefined` | Visible character width. |
| `rows` | `number` | `undefined` | Visible text lines. |
| `wrap` | `"hard" \| "off" \| "soft"` | `undefined` | Text wrapping behavior. |

Also supports: `autocapitalize`, `autofocus`, `clearOnEdit`, `color`, `counter`, `counterFormatter`, `debounce`, `disabled`, `enterkeyhint`, `errorText`, `fill`, `helperText`, `inputmode`, `label`, `labelPlacement`, `maxlength`, `minlength`, `mode`, `name`, `placeholder`, `readonly`, `required`, `shape`, `spellcheck`, `value`.

### Events

`ionBlur`, `ionChange`, `ionFocus`, `ionInput` (same as `ion-input`).

### Methods

`getInputElement() => Promise<HTMLTextAreaElement>`, `setFocus() => Promise<void>`.

### Slots

`start`, `end`, `label`.

### CSS Custom Properties

Same as `ion-input`.

---

## ion-input-otp

A one-time password input with individual character boxes.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `autocapitalize` | `string` | `'off'` | Text capitalization. |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `fill` | `"outline" \| "solid"` | `'outline'` | Fill style. |
| `inputmode` | `"numeric" \| "text"` | `undefined` | Keyboard type. |
| `length` | `number` | `4` | Number of input boxes. |
| `pattern` | `string` | based on type | Allowed character regex. |
| `readonly` | `boolean` | `false` | Prevent modification. |
| `separators` | `string \| number[] \| "all"` | `undefined` | Divider positions between boxes. |
| `shape` | `"rectangular" \| "soft" \| "round"` | `'round'` | Border radius style. |
| `size` | `"small" \| "medium" \| "large"` | `'medium'` | Input box size. |
| `type` | `"number" \| "text"` | `'number'` | Input format. |
| `value` | `string` | `''` | Current value. |

### Events

`ionBlur`, `ionChange`, `ionComplete` (all boxes filled), `ionFocus`, `ionInput`.

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `setFocus` | `setFocus(index?: number) => Promise<void>` | Focus a specific box or first empty box. |

### CSS Custom Properties

`--background`, `--border-color`, `--border-radius`, `--border-width`, `--color`, `--height`, `--highlight-color-focused`, `--highlight-color-invalid`, `--highlight-color-valid`, `--margin-bottom`, `--margin-end`, `--margin-start`, `--margin-top`, `--min-width`, `--padding-bottom`, `--padding-end`, `--padding-start`, `--padding-top`, `--separator-border-radius`, `--separator-color`, `--separator-height`, `--separator-width`, `--width`

---

## ion-input-password-toggle

A toggle button used inside `ion-input` to show/hide password text. Place inside an `ion-input` with `type="password"` using the `end` slot.

---

## ion-checkbox

A boolean input that can be checked, unchecked, or indeterminate.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `alignment` | `"center" \| "start"` | `undefined` | Cross-axis alignment. |
| `checked` | `boolean` | `false` | Whether checked. |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `errorText` | `string` | `undefined` | Error text when invalid. |
| `helperText` | `string` | `undefined` | Helper text when valid. |
| `indeterminate` | `boolean` | `false` | Indeterminate visual state. |
| `justify` | `"start" \| "end" \| "space-between"` | `undefined` | Label/checkbox packing. |
| `labelPlacement` | `"start" \| "end" \| "fixed" \| "stacked"` | `'start'` | Label position. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `name` | `string` | auto-generated | Form control name. |
| `required` | `boolean` | `false` | Required for accessibility. |
| `value` | `any` | `'on'` | Form value. |

### Events

`ionBlur`, `ionChange`, `ionFocus`.

### Slots

| Slot | Description |
| --- | --- |
| (default) | Label text. |

### CSS Custom Properties

`--border-color`, `--border-color-checked`, `--border-radius`, `--border-style`, `--border-width`, `--checkbox-background`, `--checkbox-background-checked`, `--checkmark-color`, `--checkmark-width`, `--size`, `--transition`

---

## ion-toggle

A switch that toggles between on and off states.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `alignment` | `"center" \| "start"` | `undefined` | Cross-axis alignment. |
| `checked` | `boolean` | `false` | Whether on. |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `enableOnOffLabels` | `boolean` | `undefined` | Accessibility labels. |
| `errorText` | `string` | `undefined` | Error text. |
| `helperText` | `string` | `undefined` | Helper text. |
| `justify` | `"start" \| "end" \| "space-between"` | `undefined` | Label/toggle packing. |
| `labelPlacement` | `"start" \| "end" \| "fixed" \| "stacked"` | `undefined` | Label position. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `name` | `string` | auto-generated | Form control name. |
| `required` | `boolean` | `false` | Required for accessibility. |
| `value` | `string` | `'on'` | Form value. |

### Events

`ionBlur`, `ionChange`, `ionFocus`.

### Slots

| Slot | Description |
| --- | --- |
| (default) | Label text. |

### CSS Shadow Parts

`handle`, `track`, `label`, `helper-text`, `error-text`, `supporting-text`

### CSS Custom Properties

`--border-radius`, `--handle-background`, `--handle-background-checked`, `--handle-border-radius`, `--handle-box-shadow`, `--handle-height`, `--handle-max-height`, `--handle-spacing`, `--handle-transition`, `--handle-width`, `--track-background`, `--track-background-checked`

---

## ion-radio / ion-radio-group

A radio button for single-selection within a group.

### ion-radio Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `alignment` | `"center" \| "start"` | `undefined` | Cross-axis alignment. |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `justify` | `"start" \| "end" \| "space-between"` | `undefined` | Label/radio packing. |
| `labelPlacement` | `"start" \| "end" \| "fixed" \| "stacked"` | `undefined` | Label position. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `name` | `string` | auto-generated | Form control name. |
| `value` | `any` | `undefined` | Radio value. |

### ion-radio Events

`ionBlur`, `ionFocus`.

### ion-radio Slots

| Slot | Description |
| --- | --- |
| (default) | Label text. |

### ion-radio CSS Shadow Parts

`container`, `label`, `mark`

### ion-radio CSS Custom Properties

`--border-radius`, `--color`, `--color-checked`, `--inner-border-radius`

### ion-radio-group Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `allowEmptySelection` | `boolean` | `false` | Allow deselecting. |
| `compareWith` | `string \| Function` | `undefined` | Custom comparison. |
| `name` | `string` | auto-generated | Form control name. |
| `value` | `any` | `undefined` | Selected value. |

### ion-radio-group Events

`ionChange` — Emitted when the selected value changes.

---

## ion-range

A slider for selecting a value within a range.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `activeBarStart` | `number` | `undefined` | Start position of active bar. |
| `color` | `string` | `undefined` | Color from palette. |
| `debounce` | `number` | `undefined` | Delay before `ionInput` fires. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `dualKnobs` | `boolean` | `false` | Two knob controls. |
| `label` | `string` | `undefined` | Label text. |
| `labelPlacement` | `"start" \| "end" \| "fixed" \| "stacked"` | `'start'` | Label position. |
| `max` | `number` | `100` | Maximum value. |
| `min` | `number` | `0` | Minimum value. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `name` | `string` | auto-generated | Form control name. |
| `pin` | `boolean` | `false` | Show value on knob press. |
| `pinFormatter` | `(value: number) => string \| number` | `undefined` | Custom pin text. |
| `snaps` | `boolean` | `false` | Snap to tick marks. |
| `step` | `number` | `1` | Value granularity. |
| `ticks` | `boolean` | `true` | Show tick marks. |
| `value` | `number \| { lower: number; upper: number }` | `0` | Current value. |

### Events

`ionBlur`, `ionChange`, `ionFocus`, `ionInput`, `ionKnobMoveStart`, `ionKnobMoveEnd`.

### Slots

`label`, `start`, `end`.

### CSS Custom Properties

`--bar-background`, `--bar-background-active`, `--bar-border-radius`, `--bar-height`, `--height`, `--knob-background`, `--knob-border-radius`, `--knob-box-shadow`, `--knob-size`, `--pin-background`, `--pin-color`

---

## ion-searchbar

A search input with icons and optional cancel button.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `animated` | `boolean` | `false` | Enable animation. |
| `autocapitalize` | `string` | `'off'` | Text capitalization. |
| `autocomplete` | `string` | `'off'` | Browser autocomplete. |
| `autocorrect` | `"off" \| "on"` | `'off'` | Auto correction. |
| `cancelButtonIcon` | `string` | platform default | Cancel icon (MD). |
| `cancelButtonText` | `string` | `'Cancel'` | Cancel text (iOS). |
| `clearIcon` | `string` | `undefined` | Custom clear icon. |
| `color` | `string` | `undefined` | Color from palette. |
| `debounce` | `number` | `undefined` | Delay before `ionInput`. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `enterkeyhint` | `string` | `undefined` | Enter key hint. |
| `inputmode` | `string` | `undefined` | Keyboard type. |
| `maxlength` | `number` | `undefined` | Max characters. |
| `minlength` | `number` | `undefined` | Min characters. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `name` | `string` | auto-generated | Form control name. |
| `placeholder` | `string` | `'Search'` | Placeholder text. |
| `searchIcon` | `string` | `undefined` | Custom search icon. |
| `showCancelButton` | `"always" \| "focus" \| "never"` | `'never'` | Cancel button visibility. |
| `showClearButton` | `"always" \| "focus" \| "never"` | `'always'` | Clear button visibility. |
| `spellcheck` | `boolean` | `false` | Enable spellcheck. |
| `type` | `"email" \| "number" \| "password" \| "search" \| "tel" \| "text" \| "url"` | `'search'` | Input type. |
| `value` | `string \| null` | `''` | Search value. |

### Events

`ionBlur`, `ionCancel`, `ionChange`, `ionClear`, `ionFocus`, `ionInput`.

### Methods

`getInputElement() => Promise<HTMLInputElement>`, `setFocus() => Promise<void>`.

### CSS Custom Properties

`--background`, `--border-radius`, `--box-shadow`, `--cancel-button-color`, `--clear-button-color`, `--color`, `--icon-color`, `--placeholder-color`, `--placeholder-font-style`, `--placeholder-font-weight`, `--placeholder-opacity`

---

## ion-select / ion-select-option

A dropdown select control.

### ion-select Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `cancelText` | `string` | `'Cancel'` | Cancel button text. |
| `color` | `string` | `undefined` | Color from palette. |
| `compareWith` | `string \| Function` | `undefined` | Custom value comparison. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `errorText` | `string` | `undefined` | Error text. |
| `expandedIcon` | `string` | `undefined` | Icon when open. |
| `fill` | `"outline" \| "solid"` | `undefined` | Fill style. |
| `helperText` | `string` | `undefined` | Helper text. |
| `interface` | `"action-sheet" \| "alert" \| "modal" \| "popover"` | `'alert'` | Overlay type for options. |
| `interfaceOptions` | `object` | `{}` | Options passed to the overlay. |
| `justify` | `"start" \| "end" \| "space-between"` | `undefined` | Label/control alignment. |
| `label` | `string` | `undefined` | Label text. |
| `labelPlacement` | `"start" \| "end" \| "fixed" \| "floating" \| "stacked"` | `'start'` | Label position. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `multiple` | `boolean` | `false` | Allow multiple selection. |
| `name` | `string` | auto-generated | Form control name. |
| `okText` | `string` | `'OK'` | OK button text. |
| `placeholder` | `string` | `undefined` | Placeholder text. |
| `required` | `boolean` | `false` | Required for accessibility. |
| `selectedText` | `string \| null` | `undefined` | Custom display for selected value. |
| `shape` | `"round"` | `undefined` | Rounded style. |
| `toggleIcon` | `string` | `undefined` | Custom toggle icon. |
| `value` | `any` | `undefined` | Selected value(s). |

### ion-select Events

`ionBlur`, `ionCancel`, `ionChange`, `ionDismiss`, `ionFocus`.

### ion-select Methods

`open(event?: UIEvent) => Promise<any>` — Open the select overlay.

### ion-select Slots

`start`, `end`, `label`.

### ion-select CSS Shadow Parts

`bottom`, `container`, `error-text`, `helper-text`, `icon`, `inner`, `label`, `placeholder`, `supporting-text`, `text`, `wrapper`

### ion-select CSS Custom Properties

`--background`, `--border-color`, `--border-radius`, `--border-style`, `--border-width`, `--highlight-color-focused`, `--highlight-color-invalid`, `--highlight-color-valid`, `--highlight-height`, `--padding-bottom`, `--padding-end`, `--padding-start`, `--padding-top`, `--placeholder-color`, `--placeholder-opacity`, `--ripple-color`

### ion-select-option Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `disabled` | `boolean` | `false` | Disable option. |
| `value` | `any` | `undefined` | Option value. |

---

## ion-datetime / ion-datetime-button

An inline date and/or time picker.

### ion-datetime Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `cancelText` | `string` | `'Cancel'` | Cancel button text. |
| `clearText` | `string` | `'Clear'` | Clear button text. |
| `color` | `string` | `'primary'` | Color from palette. |
| `dayValues` | `number \| number[] \| string` | `undefined` | Selectable days. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `doneText` | `string` | `'Done'` | Done button text. |
| `firstDayOfWeek` | `number` | `0` | Week start (0 = Sunday). |
| `formatOptions` | `object` | `undefined` | Intl.DateTimeFormatOptions. |
| `highlightedDates` | `array \| Function` | `undefined` | Custom date highlighting. |
| `hourCycle` | `"h11" \| "h12" \| "h23" \| "h24"` | `undefined` | 12/24 hour format. |
| `hourValues` | `number \| number[] \| string` | `undefined` | Selectable hours. |
| `isDateEnabled` | `(dateIsoString: string) => boolean` | `undefined` | Enable/disable individual dates. |
| `locale` | `string` | `'default'` | Locale for formatting. |
| `max` | `string` | `undefined` | Maximum date (ISO 8601). |
| `min` | `string` | `undefined` | Minimum date (ISO 8601). |
| `minuteValues` | `number \| number[] \| string` | `undefined` | Selectable minutes. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `monthValues` | `number \| number[] \| string` | `undefined` | Selectable months (1-12). |
| `multiple` | `boolean` | `false` | Allow multiple date selection. |
| `name` | `string` | auto-generated | Form control name. |
| `preferWheel` | `boolean` | `false` | Use wheel picker instead of calendar. |
| `presentation` | `"date" \| "date-time" \| "month" \| "month-year" \| "time" \| "time-date" \| "year"` | `'date-time'` | Which picker(s) to show. |
| `readonly` | `boolean` | `false` | Prevent modification. |
| `showAdjacentDays` | `boolean` | `false` | Show previous/next month days. |
| `showClearButton` | `boolean` | `false` | Show Clear button. |
| `showDefaultButtons` | `boolean` | `false` | Show Cancel/OK buttons. |
| `showDefaultTimeLabel` | `boolean` | `true` | Show "Time" label. |
| `showDefaultTitle` | `boolean` | `false` | Show header title. |
| `size` | `"cover" \| "fixed"` | `'fixed'` | Fixed or fill container. |
| `titleSelectedDatesFormatter` | `Function` | `undefined` | Format header for multiple dates. |
| `value` | `string \| string[] \| null` | `undefined` | Selected date (ISO 8601). |
| `yearValues` | `number \| number[] \| string` | `undefined` | Selectable years. |

### ion-datetime Events

`ionBlur`, `ionCancel`, `ionChange`, `ionFocus`.

### ion-datetime Methods

| Method | Signature | Description |
| --- | --- | --- |
| `cancel` | `cancel(closeOverlay?: boolean) => Promise<void>` | Cancel selection. |
| `confirm` | `confirm(closeOverlay?: boolean) => Promise<void>` | Confirm selection. |
| `reset` | `reset(startDate?: string) => Promise<void>` | Reset to a date. |

### ion-datetime Slots

`buttons`, `time-label`, `title`.

### ion-datetime CSS Custom Properties

`--background`, `--background-rgb`, `--title-color`, `--wheel-fade-background-rgb`, `--wheel-highlight-background`, `--wheel-highlight-border-radius`

### ion-datetime-button

A button that opens an `ion-datetime` in a popover or modal. Set the `datetime` property to the ID of the `ion-datetime` element.

---

## ion-picker

An inline wheel picker for custom value selection.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |

### CSS Custom Properties

`--fade-background-rgb`, `--highlight-background`, `--highlight-border-radius`

---

## ion-segment / ion-segment-button / ion-segment-view / ion-segment-content

A group of toggle buttons where only one can be active at a time.

### ion-segment Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `scrollable` | `boolean` | `false` | Enable horizontal scrolling. |
| `selectOnFocus` | `boolean` | `false` | Select on keyboard focus. |
| `swipeGesture` | `boolean` | `false` | Enable swipe between buttons. |
| `value` | `string` | `undefined` | Selected segment value. |

### ion-segment Events

`ionChange` — Emitted when value changes via user interaction.

### ion-segment CSS Custom Properties

`--background`

### ion-segment-button Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `contentId` | `string` | `undefined` | ID of associated content panel. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `layout` | `"icon-bottom" \| "icon-end" \| "icon-hide" \| "icon-start" \| "icon-top" \| "label-hide"` | `'icon-top'` | Icon and label layout. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `value` | `string` | `'ion-sb-{ids++}'` | Button value. |

### ion-segment-view / ion-segment-content

`ion-segment-view` contains `ion-segment-content` panels that show/hide based on the selected segment. Each `ion-segment-content` has an `id` matching a segment button's `contentId`.
