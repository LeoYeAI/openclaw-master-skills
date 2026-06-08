# Scroll & Virtual Components

Components for infinite scrolling, pull-to-refresh, and reordering.

## ion-infinite-scroll / ion-infinite-scroll-content

Loads additional data when the user scrolls near the end of the content.

### ion-infinite-scroll Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `disabled` | `boolean` | `false` | Hide and disable the infinite scroll. |
| `position` | `"bottom" \| "top"` | `'bottom'` | Trigger from top or bottom. |
| `threshold` | `string` | `'15%'` | Distance from edge to trigger. Accepts percentages (`'10%'`) or pixels (`'100px'`). |

### ion-infinite-scroll Events

| Event | Description |
| --- | --- |
| `ionInfinite` | Emitted when scroll reaches threshold. Call `complete()` when async operation finishes. |

### ion-infinite-scroll Methods

| Method | Signature | Description |
| --- | --- | --- |
| `complete` | `complete() => Promise<void>` | Signal that async loading is done. |

### ion-infinite-scroll-content Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `loadingSpinner` | `SpinnerTypes \| null` | `undefined` | Spinner type during loading. |
| `loadingText` | `string \| IonicSafeString` | `undefined` | Text during loading. |

Usage pattern:

```html
<ion-content>
  <!-- List items here -->

  <ion-infinite-scroll threshold="100px" (ionInfinite)="loadMore($event)">
    <ion-infinite-scroll-content
      loadingSpinner="bubbles"
      loadingText="Loading more data...">
    </ion-infinite-scroll-content>
  </ion-infinite-scroll>
</ion-content>
```

When there is no more data to load, set `disabled` to `true` to remove the infinite scroll.

---

## ion-refresher / ion-refresher-content

A pull-to-refresh component that triggers a refresh when the user pulls down on the content.

### ion-refresher Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `closeDuration` | `string` | `'280ms'` | Time to close the refresher. |
| `disabled` | `boolean` | `false` | Hide the refresher. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `pullFactor` | `number` | `1` | Pull speed multiplier. |
| `pullMax` | `number` | `pullMin + 60` | Maximum pull distance. |
| `pullMin` | `number` | `60` | Minimum pull distance to trigger refresh. |
| `snapbackDuration` | `string` | `'280ms'` | Time to snap back to refreshing state. |

### ion-refresher Events

| Event | Description |
| --- | --- |
| `ionPull` | Emitted while the user is pulling. |
| `ionPullStart` | Emitted when pulling starts. |
| `ionPullEnd` | Emitted when refresher returns to inactive state. |
| `ionRefresh` | Emitted when pull exceeds threshold. Call `complete()` when done. |

### ion-refresher Methods

| Method | Signature | Description |
| --- | --- | --- |
| `cancel` | `cancel() => Promise<void>` | Cancel the refresh. |
| `complete` | `complete() => Promise<void>` | Signal that refresh is done. |
| `getProgress` | `getProgress() => Promise<number>` | Get pull progress (0 = no pull, 1+ = ready). |

### ion-refresher-content Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `pullingIcon` | `SpinnerTypes \| string \| null` | `undefined` | Icon/spinner while pulling. |
| `pullingText` | `string \| IonicSafeString` | `undefined` | Text while pulling. |
| `refreshingSpinner` | `SpinnerTypes \| null` | `undefined` | Spinner while refreshing. |
| `refreshingText` | `string \| IonicSafeString` | `undefined` | Text while refreshing. |

Usage pattern:

```html
<ion-content>
  <ion-refresher slot="fixed" (ionRefresh)="doRefresh($event)">
    <ion-refresher-content></ion-refresher-content>
  </ion-refresher>

  <!-- Page content here -->
</ion-content>
```

The refresher must be placed inside `ion-content` with `slot="fixed"`.

---

## ion-reorder / ion-reorder-group

A drag handle and container for reordering list items.

### ion-reorder-group Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `disabled` | `boolean` | `true` | Disable reorder functionality. Set to `false` to enable. |

### ion-reorder-group Events

| Event | Description |
| --- | --- |
| `ionReorderStart` | Emitted when user starts dragging. |
| `ionReorderEnd` | Emitted when user releases. Includes `from`/`to` indices and `complete` method. |
| `ionReorderMove` | Emitted continuously during drag. |

### ion-reorder-group Methods

| Method | Signature | Description |
| --- | --- | --- |
| `complete` | `complete(listOrReorder?: boolean \| any[]) => Promise<any>` | Finalize the reorder. Pass `true` to let Ionic reorder the DOM, or pass the array to have it reorder the data. |

### ion-reorder

The drag handle element. Place inside an `ion-item` within an `ion-reorder-group`.

### ion-reorder CSS Shadow Parts

| Part | Description |
| --- | --- |
| `icon` | The reorder handle icon. |

Usage pattern:

```html
<ion-list>
  <ion-reorder-group [disabled]="false" (ionItemReorder)="handleReorder($event)">
    <ion-item>
      <ion-label>Item 1</ion-label>
      <ion-reorder slot="end"></ion-reorder>
    </ion-item>
    <ion-item>
      <ion-label>Item 2</ion-label>
      <ion-reorder slot="end"></ion-reorder>
    </ion-item>
  </ion-reorder-group>
</ion-list>
```
