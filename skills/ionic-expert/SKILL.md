---
name: ionic-expert
description: "A comprehensive starting point for AI agents to work with the Ionic Framework. Covers core concepts, components, CLI, theming, layout, lifecycle, navigation, and framework-specific patterns for Angular, React, and Vue. Pair with the other Ionic skills in this collection for deeper topic-specific guidance like app creation, framework integration, and upgrades."
metadata:
  author: capawesome-team
  source: https://github.com/capawesome-team/skills/tree/main/skills/ionic-expert
---

# Ionic Expert

Comprehensive reference for Ionic Framework development — core concepts, components, theming, lifecycle, navigation, framework-specific patterns (Angular, React, Vue), upgrading, and Capawesome Cloud integration.

## Core Concepts

Ionic Framework is a UI toolkit for building cross-platform apps with web technologies. It provides 80+ pre-built UI components as Web Components prefixed with `ion-` (e.g., `<ion-button>`, `<ion-content>`).

- **Platform modes**: Components adapt styling to the platform. iOS devices use `ios` mode; Android and all other platforms use `md` (Material Design). The `<html>` element receives a class (`ios` or `md`).
- **Capacitor integration**: Ionic handles the UI; Capacitor handles native device APIs. See the `capacitor-app-development` skill for Capacitor guidance.
- **Framework support**: Ionic integrates with Angular (`@ionic/angular`), React (`@ionic/react`), and Vue (`@ionic/vue`).

## Creating a New App

```bash
npm install -g @ionic/cli
ionic start <name> <template> --type=<framework> --capacitor --package-id=<id>
```

| `--type` value       | Framework                       |
| -------------------- | ------------------------------- |
| `angular`            | Angular (NgModules)             |
| `angular-standalone` | Angular (Standalone Components) |
| `react`              | React                           |
| `vue`                | Vue                             |

| Template   | Description                 |
| ---------- | --------------------------- |
| `blank`    | Empty project, single page  |
| `tabs`     | Tab-based layout            |
| `sidemenu` | Side menu layout            |

For details, see [ionic-app-creation](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-creation/SKILL.md).

## Ionic CLI

Run `ionic --help` for the full and always up-to-date command list.

| Command              | Description                                             |
| -------------------- | ------------------------------------------------------- |
| `ionic start`        | Scaffold a new Ionic project.                           |
| `ionic serve`        | Start a local dev server with live reload (port 8100).  |
| `ionic build`        | Build the web app for production.                       |
| `ionic generate`     | Generate pages, components, services (framework-dependent). |
| `ionic info`         | Print system/environment info.                          |
| `ionic repair`       | Remove and recreate dependencies and platform files.    |

Useful `ionic serve` flags: `--external` (all network interfaces), `--port=<port>`, `--prod`, `--no-open`.

## Components Overview

Ionic provides 80+ UI components organized by category. For full API reference (properties, events, methods, slots, CSS custom properties), see the linked reference files.

### Layout

`ion-app` (root container), `ion-content` (scrollable area), `ion-header`, `ion-footer`, `ion-toolbar`, `ion-title`, `ion-buttons`, `ion-back-button`, `ion-grid`/`ion-row`/`ion-col`, `ion-split-pane`.

Key usage:

```html
<ion-header>
  <ion-toolbar>
    <ion-buttons slot="start">
      <ion-back-button defaultHref="/home"></ion-back-button>
    </ion-buttons>
    <ion-title>Page Title</ion-title>
  </ion-toolbar>
</ion-header>
<ion-content>
  <!-- Scrollable content -->
</ion-content>
```

For details, see [components-layout.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-development/references/components-layout.md).

### Navigation

`ion-tabs`, `ion-tab-bar`, `ion-tab-button`, `ion-menu`, `ion-menu-button`, `ion-menu-toggle`, `ion-router-outlet`, `ion-nav`, `ion-breadcrumbs`.

For details, see [components-navigation.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-development/references/components-navigation.md).

### Form

`ion-input`, `ion-textarea`, `ion-select`/`ion-select-option`, `ion-checkbox`, `ion-toggle`, `ion-radio`/`ion-radio-group`, `ion-range`, `ion-datetime`/`ion-datetime-button`, `ion-searchbar`, `ion-segment`/`ion-segment-button`, `ion-input-otp`.

Key properties shared by most form components: `label`, `labelPlacement` (`floating`, `stacked`, `fixed`, `start`), `fill` (`outline`, `solid`), `errorText`, `helperText`, `disabled`, `value`, `placeholder`.

Key events:
- `ionInput` — fires on each keystroke (use for `ion-input`/`ion-textarea`).
- `ionChange` — fires when value is committed (use for `ion-select`, `ion-toggle`, `ion-checkbox`, `ion-range`).

```html
<ion-input label="Email" labelPlacement="floating" fill="outline"
           type="email" placeholder="you@example.com"
           errorText="Invalid email" helperText="Enter your email">
</ion-input>

<ion-select label="Country" labelPlacement="floating" fill="outline" interface="popover">
  <ion-select-option value="us">United States</ion-select-option>
  <ion-select-option value="de">Germany</ion-select-option>
</ion-select>
```

For details, see [components-form.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-development/references/components-form.md).

### Overlays

`ion-modal`, `ion-alert`, `ion-toast`, `ion-action-sheet`, `ion-loading`, `ion-popover`.

All overlays share: `isOpen` prop for declarative control, `trigger` prop to open from a button ID, `backdropDismiss`, `animated`, and lifecycle events (`didPresent`, `didDismiss`, `willPresent`, `willDismiss`).

**Sheet modal** (bottom sheet):

```html
<ion-modal [isOpen]="isOpen" [breakpoints]="[0, 0.5, 1]" [initialBreakpoint]="0.5" [handle]="true">
  <ion-content>Sheet content</ion-content>
</ion-modal>
```

For details, see [components-overlay.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-development/references/components-overlay.md).

### Data Display

`ion-list`, `ion-item`, `ion-item-sliding`/`ion-item-options`/`ion-item-option`, `ion-card`/`ion-card-header`/`ion-card-content`, `ion-accordion`/`ion-accordion-group`, `ion-chip`, `ion-badge`, `ion-label`, `ion-note`.

For details, see [components-data-display.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-development/references/components-data-display.md).

### Scroll

`ion-refresher`/`ion-refresher-content` (pull-to-refresh), `ion-infinite-scroll`/`ion-infinite-scroll-content`, `ion-reorder-group`/`ion-reorder`.

For details, see [components-scroll.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-development/references/components-scroll.md).

### Actions & Media

`ion-button`, `ion-fab`/`ion-fab-button`, `ion-icon`, `ion-avatar`, `ion-thumbnail`, `ion-spinner`, `ion-skeleton-text`, `ion-progress-bar`.

For details, see [components-action.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-development/references/components-action.md) and [components-media.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-development/references/components-media.md).

## Theming

### Colors

Nine default colors: `primary`, `secondary`, `tertiary`, `success`, `warning`, `danger`, `light`, `medium`, `dark`. Apply via the `color` attribute:

```html
<ion-button color="primary">Save</ion-button>
<ion-button color="danger">Delete</ion-button>
```

Customize a color by overriding all six CSS variables in `:root`:

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

### Global CSS Variables

Key variables: `--ion-background-color`, `--ion-text-color`, `--ion-font-family`, `--ion-safe-area-top/right/bottom/left`, `--ion-margin`, `--ion-padding`.

### Dark Mode

Three approaches (import from `@ionic/angular/css/`, `@ionic/react/css/`, or `@ionic/vue/css/`):

1. **System preference** (default): `@import '@ionic/<framework>/css/palettes/dark.system.css';`
2. **Always dark**: `@import '@ionic/<framework>/css/palettes/dark.always.css';`
3. **CSS class toggle**: `@import '@ionic/<framework>/css/palettes/dark.class.css';` then add `.ion-palette-dark` to `<html>`.

### Platform Styles

Target platform-specific styles in CSS using the mode class on `<html>`:

```css
.ios ion-toolbar { --background: #f8f8f8; }
.md ion-toolbar { --background: #ffffff; }
```

Preview a specific mode in the browser: `http://localhost:8100/?ionic:mode=ios`

## Layout

### Grid System

12-column flexbox grid: `ion-grid`, `ion-row`, `ion-col`. Columns expand evenly unless `size` (1-12) is specified.

| Breakpoint | Min Width | Property Suffix |
| ---------- | --------- | --------------- |
| `xs`       | 0         | `Xs`            |
| `sm`       | 576px     | `Sm`            |
| `md`       | 768px     | `Md`            |
| `lg`       | 992px     | `Lg`            |
| `xl`       | 1200px    | `Xl`            |

### CSS Utility Classes

- **Padding**: `.ion-padding`, `.ion-padding-top/bottom/start/end`, `.ion-no-padding`
- **Margin**: `.ion-margin`, `.ion-margin-top/bottom/start/end`, `.ion-no-margin`
- **Text**: `.ion-text-center`, `.ion-text-start`, `.ion-text-end`, `.ion-text-wrap`, `.ion-text-nowrap`
- **Display**: `.ion-display-none`, `.ion-display-block`, `.ion-display-flex`
- **Flex**: `.ion-justify-content-center`, `.ion-align-items-center`, `.ion-flex-row`, `.ion-flex-column`

All utility classes support responsive suffixes: `.ion-text-md-center` (applies at 768px+).

## Page Lifecycle

Ionic provides four lifecycle hooks that fire during page transitions. These exist because `ion-router-outlet` **caches pages in the DOM** — framework-native lifecycle hooks (`ngOnInit`, `useEffect`, `onMounted`) only fire once on first creation, not on every page visit.

| Hook                 | Fires When                       | Use For                                |
| -------------------- | -------------------------------- | -------------------------------------- |
| `ionViewWillEnter`   | Page about to enter (pre-animation)  | Refresh data on every visit            |
| `ionViewDidEnter`    | Page fully entered (post-animation)  | Start animations, focus inputs         |
| `ionViewWillLeave`   | Page about to leave (pre-animation)  | Save state, pause subscriptions        |
| `ionViewDidLeave`    | Page fully left (post-animation)     | Clean up off-screen resources          |

**Critical rules**:
- Only fire on components directly mapped to a route via `ion-router-outlet`.
- Child components do not receive these events.
- The component must use the framework-specific page wrapper (see framework sections below).

## Framework-Specific Patterns

### Angular

For full details, see [ionic-angular](https://github.com/capawesome-team/skills/blob/main/skills/ionic-angular/SKILL.md).

**Detect architecture**: Check `src/main.ts` for `bootstrapApplication` (standalone) vs `platformBrowserDynamic().bootstrapModule` (NgModule).

| Aspect            | Standalone                                     | NgModule                                   |
| ----------------- | ---------------------------------------------- | ------------------------------------------ |
| Ionic setup       | `provideIonicAngular({})` in `app.config.ts`   | `IonicModule.forRoot()` in `app.module.ts` |
| Component imports | Each from `@ionic/angular/standalone`           | `IonicModule` provides all globally        |
| Lazy loading      | `loadComponent` in routes                      | `loadChildren` in routes                   |
| Icons             | `addIcons()` from `ionicons` required           | Automatic                                  |

**Navigation**: Use `NavController` from `@ionic/angular` for animated navigation (`navigateForward`, `navigateBack`, `navigateRoot`, `back`). Use `routerLink` with `routerDirection` in templates.

**Lifecycle**: Implement interfaces `ViewWillEnter`, `ViewDidEnter`, `ViewWillLeave`, `ViewDidLeave` from `@ionic/angular`:

```typescript
import { ViewWillEnter } from '@ionic/angular';

@Component({ /* ... */ })
export class HomePage implements ViewWillEnter {
  ionViewWillEnter() {
    this.loadData(); // Runs on every page visit
  }
}
```

For navigation details, see [angular/navigation.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-angular/references/navigation.md). For lifecycle details, see [angular/lifecycle.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-angular/references/lifecycle.md).

### React

For full details, see [ionic-react](https://github.com/capawesome-team/skills/blob/main/skills/ionic-react/SKILL.md).

**Key setup differences**:
- Call `setupIonicReact()` before rendering in `src/main.tsx`.
- Use `IonReactRouter` (from `@ionic/react-router`) instead of `BrowserRouter`.
- Use `IonRouterOutlet` to contain routes with the `component` prop (not `render` or `children`).
- **Every page must render `IonPage` as root** — required for transitions and lifecycle hooks.

**Navigation**: Use `useIonRouter` hook for programmatic navigation:

```typescript
import { useIonRouter } from '@ionic/react';

const router = useIonRouter();
router.push('/detail/123', 'forward', 'push');
router.goBack();
```

**Lifecycle hooks** (from `@ionic/react`):

```typescript
import { useIonViewWillEnter } from '@ionic/react';

useIonViewWillEnter(() => {
  fetchData(); // Runs on every page visit
});
```

**Overlay hooks**: `useIonAlert`, `useIonToast`, `useIonActionSheet`, `useIonLoading`, `useIonModal`, `useIonPopover`, `useIonPicker`.

**Form events**: Use `onIonInput` for `IonInput`/`IonTextarea`, `onIonChange` for `IonSelect`/`IonToggle`/`IonCheckbox`/`IonRange`. Access values via `e.detail.value`.

For routing details, see [react/routing.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-react/references/routing.md). For hooks, see [react/hooks.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-react/references/hooks.md).

### Vue

For full details, see [ionic-vue](https://github.com/capawesome-team/skills/blob/main/skills/ionic-vue/SKILL.md).

**Key setup differences**:
- Install `IonicVue` plugin in `src/main.ts`: `createApp(App).use(IonicVue).use(router)`.
- Import `createRouter` from `@ionic/vue-router` (not from `vue-router`).
- **Every page must use `IonPage` as root template element** — without it, transitions and lifecycle hooks silently fail.
- Import all Ionic components from `@ionic/vue`.
- Use kebab-case for event names in templates (`@ion-change`, `@ion-input`).
- Import icons as SVG references from `ionicons/icons` — never as strings.

**Navigation**: Use `useIonRouter` composable:

```vue
<script setup lang="ts">
import { useIonRouter } from '@ionic/vue';

const ionRouter = useIonRouter();
ionRouter.push('/detail/123');
ionRouter.back();
</script>
```

Declarative: `<ion-button router-link="/detail" router-direction="forward">Go</ion-button>`

**Lifecycle hooks** (from `@ionic/vue`):

```vue
<script setup lang="ts">
import { onIonViewWillEnter } from '@ionic/vue';

onIonViewWillEnter(() => {
  fetchData(); // Runs on every page visit
});
</script>
```

**Composables**: `useIonRouter()`, `useBackButton(priority, handler)`, `useKeyboard()`, `isPlatform(name)`, `getPlatforms()`.

**Access Web Component methods via `$el`**: `contentRef.value.$el.scrollToBottom(300)`.

For navigation details, see [vue/navigation.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-vue/references/navigation.md). For composables, see [vue/composables.md](https://github.com/capawesome-team/skills/blob/main/skills/ionic-vue/references/composables.md).

## Navigation Patterns

### Tab Navigation

Each framework uses `ion-tabs` with `ion-tab-bar` and child routes per tab. Each tab maintains its own navigation stack.

**Rules**:
- The `tab` attribute on `ion-tab-button` must match the child route path.
- Never navigate between tabs programmatically — only the tab bar buttons should switch tabs.
- For shared views across tabs, use `ion-modal` instead of cross-tab routing.

### Side Menu

Use `ion-menu` with `contentId` matching the `id` on `ion-router-outlet`. Wrap menu items in `ion-menu-toggle` to auto-close after selection. Use `routerDirection="root"` for top-level menu navigation.

### Linear vs. Non-Linear Routing

- **Linear**: Sequential forward/back navigation (list -> detail -> edit). Back button returns to the previous page.
- **Non-linear**: Multiple independent stacks (tabs). Back navigation stays within the current tab's stack.

Use non-linear routing for tabs or split-pane layouts. Use linear routing for simple page flows.

## Upgrading

Ionic supports upgrades from version 4 through 8. Each major version jump must be applied sequentially — do not skip intermediate versions.

For full upgrade guides, see [ionic-app-upgrades](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-upgrades/SKILL.md).

## Capacitor Integration

Ionic apps use Capacitor for native device features (camera, filesystem, push notifications, etc.). The standard workflow:

```bash
npm run build
npx cap sync
npx cap run android
npx cap run ios
```

For live reload on a device:

```bash
ionic cap run android --livereload --external
ionic cap run ios --livereload --external
```

For Capacitor guidance, see the `capacitor-app-development` skill.

## Capawesome Cloud

[Capawesome Cloud](https://cloud.capawesome.io) provides CI/CD services for Ionic/Capacitor apps:

- **Live Updates** — Deploy OTA updates to Ionic/Capacitor apps instantly, without app store review.
- **Native Builds** — Build iOS and Android binaries in the cloud without local Xcode or Android Studio.
- **App Store Publishing** — Automate submissions to the Apple App Store and Google Play Store.

Visit [capawesome.io](https://capawesome.io) for the full Capawesome ecosystem. For setup, see the `capawesome-cloud` skill.

## Common Troubleshooting

- **`ionic: command not found`**: Run `npm install -g @ionic/cli`.
- **Components not rendering**: Verify Ionic CSS files are imported in the global stylesheet. For standalone Angular, verify each component is imported from `@ionic/angular/standalone`.
- **`ionViewWillEnter` not firing**: The component must be directly routed via `ion-router-outlet`. Child components do not receive lifecycle events. For React/Vue, verify `IonPage` is the root element.
- **Page data not refreshing on back navigation**: Use Ionic lifecycle hooks (`ionViewWillEnter`) instead of framework-native lifecycle hooks (`ngOnInit`, `useEffect`, `onMounted`). Ionic caches pages in the DOM.
- **Page transitions not animating**: Use the framework's Ionic router integration (`NavController` for Angular, `IonReactRouter` for React, `createRouter` from `@ionic/vue-router` for Vue). Standard framework routers do not trigger Ionic animations.
- **CSS custom properties not applying**: Ionic components use Shadow DOM. Use documented CSS custom properties (`--background`, `--color`) instead of targeting internal elements.
- **Icons not showing (Angular standalone)**: Call `addIcons()` from `ionicons` with the required icons and import `IonIcon` from `@ionic/angular/standalone`.
- **`Failed to resolve component: ion-*` (Vue)**: The Ionic component is not imported. Add the import from `@ionic/vue`.
- **Tab bar disappears on sub-page (React)**: All routes (including detail routes) must be inside the `IonRouterOutlet` within `IonTabs`.
- **Form input values not updating (React)**: Use `onIonInput` for `IonInput`/`IonTextarea`, not `onChange`. Access values via `e.detail.value`.
- **Slot attribute deprecation warning (Vue)**: Ionic uses Web Component slots. Disable the ESLint rule: `'vue/no-deprecated-slot-attribute': 'off'`.

## Related Skills

- **[`ionic-app-creation`](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-creation/SKILL.md)** — Create a new Ionic app from scratch.
- **[`ionic-app-development`](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-development/SKILL.md)** — General Ionic development, full component API reference.
- **[`ionic-angular`](https://github.com/capawesome-team/skills/blob/main/skills/ionic-angular/SKILL.md)** — Angular-specific patterns (standalone vs NgModule, navigation, forms, testing).
- **[`ionic-react`](https://github.com/capawesome-team/skills/blob/main/skills/ionic-react/SKILL.md)** — React-specific patterns (IonReactRouter, hooks, state management).
- **[`ionic-vue`](https://github.com/capawesome-team/skills/blob/main/skills/ionic-vue/SKILL.md)** — Vue-specific patterns (composables, navigation, IonPage requirement).
- **[`ionic-app-upgrades`](https://github.com/capawesome-team/skills/blob/main/skills/ionic-app-upgrades/SKILL.md)** — Upgrade Ionic to a newer major version.
- **[`capacitor-app-development`](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/SKILL.md)** — General Capacitor development.
- **[`capawesome-cloud`](https://github.com/capawesome-team/skills/blob/main/skills/capawesome-cloud/SKILL.md)** — Live updates, native builds, and app store publishing.
