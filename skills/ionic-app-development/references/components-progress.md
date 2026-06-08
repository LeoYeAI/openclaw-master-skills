# Progress Components

Components for indicating loading and progress states.

## ion-progress-bar

A horizontal bar that indicates progress or an indeterminate loading state.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `buffer` | `number` | `1` | Buffer bar progress (0-1). Shows animated circles for unbuffered range. |
| `color` | `string` | `undefined` | Color from palette. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `reversed` | `boolean` | `false` | Reverse the progress direction. |
| `type` | `"determinate" \| "indeterminate"` | `'determinate'` | `determinate` shows a progress value; `indeterminate` shows a continuous animation. |
| `value` | `number` | `0` | Progress value (0-1). |

### CSS Custom Properties

| Property | Description |
| --- | --- |
| `--background` | Track background (or buffer bar fill). |
| `--progress-background` | Active progress bar background. |

Usage:

```html
<!-- Determinate -->
<ion-progress-bar value="0.5"></ion-progress-bar>

<!-- Indeterminate (loading) -->
<ion-progress-bar type="indeterminate"></ion-progress-bar>

<!-- With buffer -->
<ion-progress-bar value="0.25" buffer="0.5"></ion-progress-bar>
```

---

## ion-skeleton-text

A placeholder element that mimics content shape while data is loading.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `animated` | `boolean` | `false` | Enable shimmer animation. |

### CSS Custom Properties

| Property | Description |
| --- | --- |
| `--background` | Background color. |
| `--background-rgb` | Background color in RGB format. |
| `--border-radius` | Border radius. |

Usage:

```html
<!-- Text placeholder -->
<ion-skeleton-text animated style="width: 60%"></ion-skeleton-text>

<!-- Avatar placeholder -->
<ion-skeleton-text animated style="width: 40px; height: 40px; border-radius: 50%"></ion-skeleton-text>

<!-- Full card placeholder -->
<ion-card>
  <ion-card-header>
    <ion-skeleton-text animated style="width: 80%"></ion-skeleton-text>
  </ion-card-header>
  <ion-card-content>
    <ion-skeleton-text animated style="width: 100%"></ion-skeleton-text>
    <ion-skeleton-text animated style="width: 70%"></ion-skeleton-text>
  </ion-card-content>
</ion-card>
```

---

## ion-spinner

An animated SVG spinner for indicating loading.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `duration` | `number` | `undefined` | Animation duration in milliseconds. |
| `name` | `"bubbles" \| "circles" \| "circular" \| "crescent" \| "dots" \| "lines" \| "lines-sharp" \| "lines-sharp-small" \| "lines-small"` | `undefined` | Spinner style. Defaults to platform-specific spinner. |
| `paused` | `boolean` | `false` | Pause the animation. |

### CSS Custom Properties

| Property | Description |
| --- | --- |
| `--color` | Spinner color. |

Available spinner names:
- `bubbles` — Scaling circles
- `circles` — Fading circles
- `circular` — Material Design circular spinner
- `crescent` — Crescent/arc spinner
- `dots` — Scaling dots
- `lines` — Fading lines
- `lines-sharp` — Sharp fading lines
- `lines-sharp-small` — Small sharp fading lines
- `lines-small` — Small fading lines

Usage:

```html
<ion-spinner></ion-spinner>
<ion-spinner name="crescent"></ion-spinner>
<ion-spinner name="dots" color="primary"></ion-spinner>
```
