---
name: ionic-app-development
description: "Guides the agent through general Ionic Framework development including core concepts, component reference, CLI usage, layout, theming, animations, gestures, development workflow, and troubleshooting. Covers all Ionic UI components grouped by category with properties, events, methods, slots, and CSS custom properties. Do not use for creating a new Ionic app (use ionic-app-creation), framework-specific patterns (use ionic-angular, ionic-react, ionic-vue), or upgrading Ionic versions (use ionic-app-upgrades)."
metadata:
  author: capawesome-team
  source: https://github.com/capawesome-team/skills/tree/main/skills/ionic-app-development
---

# Ionic App Development

General Ionic Framework development — core concepts, component reference, CLI usage, layout, theming, utilities, development workflow, and troubleshooting.

## Prerequisites

1. **Node.js** (latest LTS) installed.
2. **Ionic CLI** installed globally (`npm install -g @ionic/cli`).
3. An existing Ionic project. For creating a new Ionic app, use the **`ionic-app-creation`** skill.

## Agent Behavior

- **Auto-detect the framework.** Check `package.json` for `@ionic/angular`, `@ionic/react`, or `@ionic/vue` to determine the framework in use. Adapt code examples accordingly.
- **Route to reference files.** This skill is an overview that routes agents to specific reference files for detailed component APIs and topic-specific guidance.
- **Do not duplicate framework-specific skills.** For Angular, React, or Vue specific patterns, refer to the respective framework skill.

## Core Concepts

### How Ionic Works

Ionic Framework is a UI toolkit for building cross-platform apps using web technologies (HTML, CSS, JavaScript/TypeScript). It provides a library of pre-built UI components that adapt their styling to the platform (`ios` or `md` mode).

- **Components** are custom HTML elements (Web Components) prefixed with `ion-` (e.g., `<ion-button>`, `<ion-content>`).
- **Platform modes**: Ionic renders components differently based on the platform. iOS devices use the `ios` mode; Android and all other platforms use the `md` (Material Design) mode. The `<html>` element receives a class (`ios` or `md`) that enables platform-specific styles.
- **Capacitor integration**: Ionic apps use Capacitor to access native device features. Ionic handles the UI; Capacitor handles native APIs. See the **`capacitor-app-development`** skill for Capacitor-specific guidance.

### Page Lifecycle

Ionic provides lifecycle events on top of the framework's own lifecycle hooks. These fire when a page is navigated to or from:

| Event                 | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| `ionViewWillEnter`    | Fires when the page is about to enter and become active.   |
| `ionViewDidEnter`     | Fires when the page has fully entered and is now active.   |
| `ionViewWillLeave`    | Fires when the page is about to leave and become inactive. |
| `ionViewDidLeave`     | Fires when the page has fully left and is now inactive.    |

These are in addition to the framework-specific lifecycle hooks (e.g., Angular's `ngOnInit`, React's `useEffect`, Vue's `onMounted`). Use Ionic lifecycle events for tasks that should run each time a page becomes visible (e.g., refreshing data), since some navigation strategies cache pages.

## Component Reference

Ionic provides 80+ UI components. Detailed API documentation for each component is organized into reference files by category. Each reference file covers properties, events, methods, slots, CSS shadow parts, and CSS custom properties.

When the user needs help with a specific component, read the corresponding reference file.

| Category         | Reference File                            | Components Covered                                                                                              |
| ---------------- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Action & Buttons | `references/components-action.md`         | action-sheet, button, fab, fab-button, fab-list, ripple-effect                                                  |
| Data Display     | `references/components-data-display.md`   | accordion, accordion-group, badge, card, card-content, card-header, card-subtitle, card-title, chip, item, item-divider, item-group, item-sliding, item-options, item-option, label, list, list-header, note, text |
| Form             | `references/components-form.md`           | checkbox, datetime, datetime-button, input, input-otp, input-password-toggle, picker, radio, radio-group, range, searchbar, select, select-option, segment, segment-button, segment-content, segment-view, textarea, toggle |
| Layout           | `references/components-layout.md`         | app, content, grid, col, row, header, footer, toolbar, title, buttons, back-button, split-pane                  |
| Media            | `references/components-media.md`          | avatar, icon, img, thumbnail                                                                                    |
| Navigation       | `references/components-navigation.md`     | breadcrumb, breadcrumbs, menu, menu-button, menu-toggle, nav, nav-link, router, router-link, router-outlet, route, route-redirect, tabs, tab, tab-bar, tab-button |
| Overlay          | `references/components-overlay.md`        | alert, loading, modal, popover, toast, backdrop                                                                 |
| Scroll & Virtual | `references/components-scroll.md`         | infinite-scroll, infinite-scroll-content, refresher, refresher-content, reorder, reorder-group                  |
| Progress         | `references/components-progress.md`       | progress-bar, skeleton-text, spinner                                                                            |

## Ionic CLI

The Ionic CLI is the primary tool for developing Ionic apps. Below are the most commonly used commands. Run `ionic --help` for the full and always up-to-date command list.

### Installation

```bash
npm install -g @ionic/cli
```

If upgrading from the legacy `ionic` package:

```bash
npm uninstall -g ionic
npm install -g @ionic/cli
```

### Key Commands

| Command                      | Description                                                       |
| ---------------------------- | ----------------------------------------------------------------- |
| `ionic serve`                | Start a local dev server with live reload.                        |
| `ionic serve --external`     | Serve on all network interfaces (for testing on devices).         |
| `ionic serve --port=<port>`  | Serve on a custom port (default: 8100).                           |
| `ionic serve --prod`         | Serve with production build configuration.                        |
| `ionic build`                | Build the web app for production.                                 |
| `ionic generate`             | Generate pages, components, services (framework-dependent).       |
| `ionic doctor check`         | Check the project for common issues.                              |
| `ionic info`                 | Print system/environment info for bug reports.                    |
| `ionic repair`               | Remove and recreate dependencies and platform files.              |

### `ionic serve` Options

| Option                       | Description                                                       |
| ---------------------------- | ----------------------------------------------------------------- |
| `--ssl`                      | Enable HTTPS (experimental).                                      |
| `--no-livereload`            | Serve without automatic reloading.                                |
| `--no-open`                  | Do not open a browser window automatically.                       |
| `--consolelogs`              | Print app console output in terminal.                             |
| `--browser=<browser>`        | Open in a specific browser (safari, firefox, google chrome).      |
| `--browseroption=<path>`     | Open a specific URL path (e.g., `/#/tab/dash`).                  |

For framework-specific CLI options, pass them after `--`:

```bash
ionic serve -- --proxy-config proxy.conf.json
```

## Layout

Read `references/components-layout.md` for the full API reference for layout components.

### Grid System

Ionic uses a 12-column flexbox grid system (`ion-grid`, `ion-row`, `ion-col`). Columns expand to fill the row evenly unless a `size` attribute is specified (1-12).

Responsive breakpoints:

| Breakpoint | Min Width | CSS Class Prefix |
| ---------- | --------- | ---------------- |
| `xs`       | 0         | (default)        |
| `sm`       | 576px     | `sizeSm`         |
| `md`       | 768px     | `sizeMd`         |
| `lg`       | 992px     | `sizeLg`         |
| `xl`       | 1200px    | `sizeXl`         |

### CSS Utility Classes

Ionic provides responsive CSS utility classes for common styling needs:

- **Text**: `.ion-text-center`, `.ion-text-start`, `.ion-text-end`, `.ion-text-wrap`, `.ion-text-nowrap`, `.ion-text-uppercase`, `.ion-text-lowercase`, `.ion-text-capitalize`
- **Padding**: `.ion-padding`, `.ion-padding-top`, `.ion-padding-bottom`, `.ion-padding-start`, `.ion-padding-end`, `.ion-padding-vertical`, `.ion-padding-horizontal`, `.ion-no-padding`
- **Margin**: `.ion-margin`, `.ion-margin-top`, `.ion-margin-bottom`, `.ion-margin-start`, `.ion-margin-end`, `.ion-margin-vertical`, `.ion-margin-horizontal`, `.ion-no-margin`
- **Display**: `.ion-display-none`, `.ion-display-block`, `.ion-display-flex`, `.ion-display-inline`, `.ion-display-grid`
- **Float**: `.ion-float-left`, `.ion-float-right`, `.ion-float-start`, `.ion-float-end`
- **Flex**: `.ion-justify-content-center`, `.ion-align-items-center`, `.ion-flex-row`, `.ion-flex-column`, `.ion-flex-wrap`, `.ion-flex-nowrap`
- **Border**: `.ion-no-border`

All utility classes support responsive breakpoint suffixes: `ion-text-{breakpoint}-center` (e.g., `.ion-text-md-center` applies at 768px+).

## Theming

### Colors

Ionic provides nine default colors: `primary`, `secondary`, `tertiary`, `success`, `warning`, `danger`, `light`, `medium`, `dark`. Apply via the `color` attribute on components:

```html
<ion-button color="primary">Primary</ion-button>
<ion-button color="danger">Danger</ion-button>
```

Each color has six CSS custom properties:

- `--ion-color-{name}` — Base color value
- `--ion-color-{name}-rgb` — Base color in RGB format
- `--ion-color-{name}-contrast` — Text color for readability
- `--ion-color-{name}-contrast-rgb` — Contrast color in RGB format
- `--ion-color-{name}-shade` — Darker variant (active/pressed states)
- `--ion-color-{name}-tint` — Lighter variant (hover states)

To customize a color, override all six variables in `:root`:

```css
:root {
  --ion-color-primary: #3880ff;
  --ion-color-primary-rgb: 56, 128, 255;
  --ion-color-primary-contrast: #ffffff;
  --ion-color-primary-contrast-rgb: 255, 255, 255;
  --ion-color-primary-shade: #3171e0;
  --ion-color-primary-tint: #4c8dff;
}
```

To add a custom color, define the CSS variables and create a class:

```css
:root {
  --ion-color-favorite: #69bb7b;
  --ion-color-favorite-rgb: 105, 187, 123;
  --ion-color-favorite-contrast: #ffffff;
  --ion-color-favorite-contrast-rgb: 255, 255, 255;
  --ion-color-favorite-shade: #5ca56c;
  --ion-color-favorite-tint: #78c288;
}

.ion-color-favorite {
  --ion-color-base: var(--ion-color-favorite);
  --ion-color-base-rgb: var(--ion-color-favorite-rgb);
  --ion-color-contrast: var(--ion-color-favorite-contrast);
  --ion-color-contrast-rgb: var(--ion-color-favorite-contrast-rgb);
  --ion-color-shade: var(--ion-color-favorite-shade);
  --ion-color-tint: var(--ion-color-favorite-tint);
}
```

### Global CSS Variables

| Variable                        | Description                                           |
| ------------------------------- | ----------------------------------------------------- |
| `--ion-background-color`        | Background color of the app                           |
| `--ion-text-color`              | Text color of the app                                 |
| `--ion-font-family`             | Font family of the app                                |
| `--ion-statusbar-padding`       | Statusbar padding top of the app                      |
| `--ion-safe-area-top`           | Adjust safe area inset top                            |
| `--ion-safe-area-right`         | Adjust safe area inset right                          |
| `--ion-safe-area-bottom`        | Adjust safe area inset bottom                         |
| `--ion-safe-area-left`          | Adjust safe area inset left                           |
| `--ion-margin`                  | Default margin for margin utility classes             |
| `--ion-padding`                 | Default padding for padding utility classes           |
| `--ion-placeholder-opacity`     | Opacity of placeholder text in inputs                 |

### Dark Mode

Ionic supports three dark mode approaches:

#### 1. System Preference (Default)

Automatically applies dark palette based on the user's OS setting:

```css
@import '@ionic/angular/css/palettes/dark.system.css';
/* or @ionic/react, @ionic/vue */
```

#### 2. Always Dark

Forces dark mode regardless of system settings:

```css
@import '@ionic/angular/css/palettes/dark.always.css';
```

#### 3. CSS Class Toggle

Enables manual dark mode control via a CSS class:

```css
@import '@ionic/angular/css/palettes/dark.class.css';
```

Add `.ion-palette-dark` to the `<html>` element to activate:

```html
<html class="ion-palette-dark">
```

Add this meta tag to adjust system UI elements (scrollbars, etc.):

```html
<meta name="color-scheme" content="light dark" />
```

### Platform Styles

Ionic uses two modes for platform-specific styling:

| Platform    | Default Mode | Style            |
| ----------- | ------------ | ---------------- |
| iOS         | `ios`        | Apple iOS design |
| Android     | `md`         | Material Design  |
| Other / Web | `md`         | Material Design  |

To preview a specific mode in the browser, add `?ionic:mode=ios` or `?ionic:mode=md` to the URL:

```
http://localhost:8100/?ionic:mode=ios
```

Target mode-specific styles in CSS:

```css
.ios ion-toolbar {
  --background: #f8f8f8;
}

.md ion-toolbar {
  --background: #ffffff;
}
```

## Developing

### Previewing in the Browser

The primary development workflow is browser-based:

```bash
ionic serve
```

This starts a development server at `http://localhost:8100` with live reload.

Use browser DevTools to simulate mobile devices:
- **Chrome**: `Cmd+Opt+I` (Mac) / `Ctrl+Shift+I` (Windows/Linux), then toggle device toolbar
- **Safari**: `Cmd+Opt+R` for Responsive Design Mode
- **Firefox**: `Cmd+Opt+M` (Mac) / `Ctrl+Shift+M` (Windows/Linux)

### Testing on Devices

For native functionality that requires a real device:

```bash
npx cap run android
npx cap run ios
```

For live reload on a device:

```bash
npx cap run android --livereload --external
npx cap run ios --livereload --external
```

### Debugging Tips

- Use the `debugger` keyword to set breakpoints in code.
- Add `?ionic:mode=ios` to the URL to preview iOS styles in the browser.
- Use `ionic info` to collect environment info for troubleshooting.

## Utilities

### Animations

Ionic provides a framework-agnostic animation utility built on the Web Animations API. Import:

- **JavaScript/TypeScript**: `import { createAnimation } from '@ionic/core';`
- **Angular**: Inject `AnimationController` from `@ionic/angular`
- **React**: Use `CreateAnimation` component from `@ionic/react`
- **Vue**: `import { createAnimation } from '@ionic/vue';`

Key methods: `addElement()`, `duration()`, `easing()`, `fromTo()`, `keyframes()`, `play()`, `pause()`, `stop()`, `onFinish()`.

Animations support grouping (parent-child), chaining (via `play()` promises), and integration with gestures.

For performance, prefer animating `transform` and `opacity` over `height` and `width`.

### Gestures

Ionic provides a framework-agnostic gesture utility. Import:

- **JavaScript/TypeScript**: `import { createGesture } from '@ionic/core';`
- **Angular**: Inject `GestureController` from `@ionic/angular`
- **React**: `import { createGesture } from '@ionic/react';`
- **Vue**: `import { createGesture } from '@ionic/vue';`

Configuration options: `el`, `gestureName`, `threshold`, `direction` (`x`/`y`), `maxAngle`, `gesturePriority`, `disableScroll`, `passive`.

Callbacks: `canStart`, `onWillStart`, `onStart`, `onMove`, `onEnd`, `notCaptured`.

The `GestureDetail` object provides `startX`/`startY`, `currentX`/`currentY`, `deltaX`/`deltaY`, and `velocityX`/`velocityY`.

### Hardware Back Button (Android)

Ionic emits an `ionBackButton` event when the Android hardware back button is pressed. Handlers are priority-based:

| Priority | Handler    |
| -------- | ---------- |
| 100      | Overlays   |
| 99       | Menu       |
| 0        | Navigation |

For Capacitor apps, install `@capacitor/app` to enable hardware back button support. See the framework-specific skills for implementation patterns.

## Error Handling

- **`ionic: command not found`**: The Ionic CLI is not installed. Run `npm install -g @ionic/cli`.
- **Port 8100 in use**: Another process is using the default port. Run `ionic serve --port=<other-port>`.
- **Components not rendering**: Verify the Ionic CSS files are imported in the global stylesheet. For Angular: `@import '@ionic/angular/css/core.css';`. For React/Vue: check the framework-specific import.
- **Platform styles not applied**: Ensure `@ionic/angular`, `@ionic/react`, or `@ionic/vue` is installed and configured. The `<html>` element should have an `ios` or `md` class.
- **Dark mode not working**: Verify the correct dark palette CSS import is present. For the class method, ensure `.ion-palette-dark` is applied to the `<html>` element.
- **CSS custom properties not applying**: Ionic components use Shadow DOM. Use the component's documented CSS custom properties (e.g., `--background`, `--color`) rather than targeting internal elements directly. Check the component reference file for available properties.
- **Live reload not working on device**: Ensure the device and development machine are on the same network. Use the `--external` flag with `npx cap run`.
- **`ionViewWillEnter` not firing**: This lifecycle event only fires with Ionic's routing components (`ion-router-outlet`). It does not fire with standard framework routers unless Ionic's routing integration is used.

## Related Skills

- **`ionic-app-creation`** — Create a new Ionic app.
- **`ionic-angular`** — Ionic with Angular (framework-specific patterns).
- **`ionic-react`** — Ionic with React (framework-specific patterns).
- **`ionic-vue`** — Ionic with Vue (framework-specific patterns).
- **`ionic-app-upgrades`** — Upgrade Ionic to a newer major version.
- **`capacitor-app-development`** — General Capacitor development.
- **`capacitor-plugins`** — Capacitor plugins installation and configuration.
