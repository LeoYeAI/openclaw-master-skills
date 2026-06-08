# Media Components

Components for displaying images, icons, and avatars.

## ion-avatar

A circular container for images, typically used in list items or cards to display user photos or icons.

### Properties

None.

### CSS Custom Properties

`--border-radius`

Usage:

```html
<ion-item>
  <ion-avatar slot="start">
    <img alt="User avatar" src="https://example.com/avatar.jpg" />
  </ion-avatar>
  <ion-label>User Name</ion-label>
</ion-item>
```

---

## ion-icon

Displays an icon from the Ionicons library or a custom SVG.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `string` | `undefined` | Color from palette. |
| `icon` | `string` | `undefined` | Icon name or SVG path. |
| `ios` | `string` | `undefined` | Icon for iOS mode. |
| `md` | `string` | `undefined` | Icon for MD mode. |
| `mode` | `"ios" \| "md"` | `undefined` | Platform styles. |
| `name` | `string` | `undefined` | Icon name from Ionicons. |
| `size` | `"small" \| "large"` | `undefined` | Icon size. |
| `src` | `string` | `undefined` | Custom SVG source URL. |

### CSS Custom Properties

`--ionicon-stroke-width`

Usage:

```html
<!-- By name (requires ionicons package) -->
<ion-icon name="heart"></ion-icon>
<ion-icon name="heart-outline"></ion-icon>

<!-- Platform-specific -->
<ion-icon ios="heart-outline" md="heart-sharp"></ion-icon>

<!-- Custom SVG -->
<ion-icon src="/assets/my-icon.svg"></ion-icon>
```

Ionicons are automatically included with Ionic Framework. Browse available icons at [ionicons.com](https://ionicons.com/).

---

## ion-img

A lazy-loading image component. Only loads the image when it scrolls into the viewport.

### Properties

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `alt` | `string` | `undefined` | Alternative text for the image. |
| `src` | `string` | `undefined` | Image URL. |

### Events

| Event | Description |
| --- | --- |
| `ionError` | Image failed to load. |
| `ionImgDidLoad` | Image finished loading. |
| `ionImgWillLoad` | Image src was set, loading started. |

Usage:

```html
<ion-img alt="Product photo" src="https://example.com/photo.jpg"></ion-img>
```

Use `ion-img` instead of a plain `<img>` tag when the image is in a scrollable list to benefit from lazy loading. For images that are always visible (e.g., in a header), a standard `<img>` tag is sufficient.

---

## ion-thumbnail

A square container for images, typically used in list items to display previews.

### Properties

None.

### CSS Custom Properties

`--border-radius`, `--size`

Usage:

```html
<ion-item>
  <ion-thumbnail slot="start">
    <img alt="Product thumbnail" src="https://example.com/thumb.jpg" />
  </ion-thumbnail>
  <ion-label>Product Name</ion-label>
</ion-item>
```
