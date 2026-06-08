# Navigation Components

Components for app navigation — breadcrumbs, menus, nav stacks, routers, and tabs.

## ion-breadcrumbs / ion-breadcrumb

A navigation trail showing the user's location in the app hierarchy.

### ion-breadcrumbs Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `itemsAfterCollapse` | `number` | `1` | Breadcrumbs shown after the collapsed indicator. |
| `itemsBeforeCollapse` | `number` | `1` | Breadcrumbs shown before the collapsed indicator. |
| `maxItems` | `number` | `undefined` | Threshold for collapsing breadcrumbs. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |

### ion-breadcrumbs Events

`ionCollapsedClick` — Emitted when the collapsed indicator is clicked.

### ion-breadcrumb Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `active` | `boolean` | `false` | Mark as the current/active breadcrumb. |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `download` | `string` | `undefined` | Download URL as file. |
| `href` | `string` | `undefined` | URL for navigation. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `rel` | `string` | `undefined` | Link relationship. |
| `routerAnimation` | `AnimationBuilder` | `undefined` | Navigation animation. |
| `routerDirection` | `"back" \| "forward" \| "root"` | `'forward'` | Navigation direction. |
| `separator` | `boolean` | `true` | Show separator. |
| `target` | `string` | `undefined` | Link target. |

### ion-breadcrumb Slots

(default), `separator`.

### ion-breadcrumb CSS Shadow Parts

`native`, `separator`

---

## ion-menu

A side menu (drawer) that slides in from the edge of the screen.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `contentId` | `string` | `undefined` | ID of the main content element. |
| `disabled` | `boolean` | `false` | Disable the menu. |
| `maxEdgeStart` | `number` | `50` | Edge drag threshold in pixels. |
| `menuId` | `string` | `undefined` | Menu identifier. |
| `side` | `"start" \| "end"` | `'start'` | Side to slide in from. |
| `swipeGesture` | `boolean` | `true` | Enable swipe to open/close. |
| `type` | `"overlay" \| "push" \| "reveal"` | `undefined` | Menu display mode. |

### Events

| Event | Description |
| --- | --- |
| `ionDidClose` | Menu closed. |
| `ionDidOpen` | Menu opened. |
| `ionWillClose` | Menu about to close. |
| `ionWillOpen` | Menu about to open. |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `close` | `close(animated?: boolean, role?: string) => Promise<boolean>` | Close the menu. |
| `isActive` | `isActive() => Promise<boolean>` | Check if active. |
| `isOpen` | `isOpen() => Promise<boolean>` | Check if open. |
| `open` | `open(animated?: boolean) => Promise<boolean>` | Open the menu. |
| `setOpen` | `setOpen(shouldOpen: boolean, animated?: boolean, role?: string) => Promise<boolean>` | Set open state. |
| `toggle` | `toggle(animated?: boolean) => Promise<boolean>` | Toggle open/closed. |

### CSS Shadow Parts

`backdrop`, `container`

### CSS Custom Properties

`--background`, `--height`, `--max-height`, `--max-width`, `--min-height`, `--min-width`, `--width`

---

## ion-menu-button

A button that toggles a menu open/closed. Automatically shows/hides based on menu state.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `autoHide` | `boolean` | `true` | Auto-hide when menu is disabled or not found. |
| `color` | `string` | `undefined` | Color from palette. |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `menu` | `string` | `undefined` | Target menu ID. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `type` | `"button" \| "reset" \| "submit"` | `'button'` | Button type. |

### CSS Shadow Parts

`native`, `icon`

---

## ion-menu-toggle

A component that toggles a menu when clicked. Unlike `ion-menu-button`, it does not automatically hide.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `autoHide` | `boolean` | `true` | Auto-hide when menu is not active. |
| `menu` | `string` | `undefined` | Target menu ID. |

---

## ion-nav

A standalone navigation stack component. Manages a stack of views with push/pop transitions.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `animated` | `boolean` | `true` | Animate transitions. |
| `animation` | `AnimationBuilder` | `undefined` | Custom animation. |
| `root` | `Function \| HTMLElement \| string` | `undefined` | Initial component. |
| `rootParams` | `object` | `undefined` | Parameters for root component. |
| `swipeGesture` | `boolean` | `undefined` | Swipe-to-go-back (iOS). |

### Events

| Event | Description |
| --- | --- |
| `ionNavDidChange` | Navigation completed. |
| `ionNavWillChange` | Navigation about to change. |

### Methods

| Method | Signature | Description |
| --- | --- | --- |
| `canGoBack` | `canGoBack() => Promise<boolean>` | Check if back navigation is possible. |
| `getActive` | `getActive() => Promise<ViewController \| undefined>` | Get active view. |
| `getByIndex` | `getByIndex(index: number) => Promise<ViewController \| undefined>` | Get view at index. |
| `getLength` | `getLength() => Promise<number>` | Get total views in stack. |
| `getPrevious` | `getPrevious(view?: ViewController) => Promise<ViewController \| undefined>` | Get previous view. |
| `insert` | `insert(insertIndex: number, component: any, params?: object, opts?: object) => Promise<boolean>` | Insert at index. |
| `insertPages` | `insertPages(insertIndex: number, insertComponents: any[], opts?: object) => Promise<boolean>` | Insert multiple. |
| `pop` | `pop(opts?: object) => Promise<boolean>` | Remove top view. |
| `popTo` | `popTo(indexOrViewCtrl: number \| ViewController, opts?: object) => Promise<boolean>` | Pop to index. |
| `popToRoot` | `popToRoot(opts?: object) => Promise<boolean>` | Pop to root. |
| `push` | `push(component: any, params?: object, opts?: object) => Promise<boolean>` | Push new view. |
| `removeIndex` | `removeIndex(startIndex: number, removeCount?: number, opts?: object) => Promise<boolean>` | Remove at index. |
| `setPages` | `setPages(views: any[], opts?: object) => Promise<boolean>` | Replace entire stack. |
| `setRoot` | `setRoot(component: any, params?: object, opts?: object) => Promise<boolean>` | Set root component. |

---

## ion-nav-link

A link element that pushes, pops, or sets the root of an `ion-nav`.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `component` | `Function \| HTMLElement \| string` | `undefined` | Component to navigate to. |
| `componentProps` | `object` | `undefined` | Data for the component. |
| `routerDirection` | `"back" \| "forward" \| "root"` | `'forward'` | Navigation action. |

---

## ion-router / ion-route / ion-route-redirect / ion-router-link / ion-router-outlet

Client-side routing components for vanilla JavaScript (non-framework) Ionic apps.

**Note:** When using Angular, React, or Vue, use the framework's own router instead. These components are for vanilla JS apps only.

### ion-router

Manages URL-based routing by mapping paths to components.

### ion-route Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `component` | `string` | `undefined` | Component name to render. |
| `url` | `string` | `''` | URL path pattern. |

### ion-route Events

`ionRouteDataChanged` — Emitted when route data changes.

### ion-route-redirect Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `from` | `string` | `undefined` | Source URL to redirect from. |
| `to` | `string` | `undefined` | Target URL to redirect to. |

### ion-router-outlet

The container where routed views are rendered. Provides animations and caching for page transitions.

### ion-router-link Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `href` | `string` | `undefined` | URL to navigate to. |
| `rel` | `string` | `undefined` | Link relationship. |
| `routerAnimation` | `AnimationBuilder` | `undefined` | Custom animation. |
| `routerDirection` | `"back" \| "forward" \| "root"` | `'forward'` | Navigation direction. |
| `target` | `string` | `undefined` | Link target. |

---

## ion-tabs / ion-tab / ion-tab-bar / ion-tab-button

Tab-based navigation layout.

### ion-tabs Events

| Event | Description |
| --- | --- |
| `ionTabsDidChange` | Tab transition completed. |
| `ionTabsWillChange` | Tab transition about to start. |

### ion-tabs Methods

| Method | Signature | Description |
| --- | --- | --- |
| `getSelected` | `getSelected() => Promise<string \| undefined>` | Get selected tab. |
| `getTab` | `getTab(tab: string \| HTMLIonTabElement) => Promise<HTMLIonTabElement \| undefined>` | Get tab element. |
| `select` | `select(tab: string \| HTMLIonTabElement) => Promise<boolean>` | Select a tab. |

### ion-tabs Slots

| Slot | Description |
| --- | --- |
| (default) | Content between named slots. |
| `top` | Tab bar at the top. |
| `bottom` | Tab bar at the bottom. |

### ion-tab Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `component` | `string` | `undefined` | Component to render. |
| `tab` | `string` | `undefined` | Tab identifier. |

### ion-tab-bar Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `selectedTab` | `string` | `undefined` | Selected tab. |
| `translucent` | `boolean` | `false` | Translucent background (iOS). |

### ion-tab-bar CSS Custom Properties

`--background`, `--border`, `--color`

### ion-tab-button Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `disabled` | `boolean` | `false` | Prevent interaction. |
| `download` | `string` | `undefined` | Download URL. |
| `href` | `string` | `undefined` | URL for navigation. |
| `layout` | `"icon-bottom" \| "icon-end" \| "icon-hide" \| "icon-start" \| "icon-top" \| "label-hide"` | `'icon-top'` | Icon/label layout. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `rel` | `string` | `undefined` | Link relationship. |
| `selected` | `boolean` | `false` | Whether selected. |
| `tab` | `string` | `undefined` | Tab identifier (must match `ion-tab` tab). |
| `target` | `string` | `undefined` | Link target. |

### ion-tab-button CSS Custom Properties

`--background`, `--background-focused`, `--background-focused-opacity`, `--color`, `--color-focused`, `--color-selected`, `--padding-bottom`, `--padding-end`, `--padding-start`, `--padding-top`, `--ripple-color`
