---
name: capacitor-expert
description: "A comprehensive starting point for AI agents to work with Capacitor. Covers core concepts, CLI, app creation, plugins, framework integration, best practices, storage, security, testing, troubleshooting, upgrading, and Capawesome Cloud (live updates, native builds, app store publishing). Pair with the other Capacitor skills in this collection for deeper topic-specific guidance."
metadata:
  author: capawesome-team
  source: https://github.com/capawesome-team/skills/tree/main/skills/capacitor-expert
---

# Capacitor Expert

Comprehensive reference for building cross-platform apps with Capacitor. Covers architecture, CLI, plugins, framework integration, best practices, and Capawesome Cloud.

## Core Concepts

Capacitor is a cross-platform native runtime for building web apps that run natively on iOS, Android, and the web. The web app runs in a native WebView, and Capacitor provides a bridge to native APIs via plugins.

### Architecture

A Capacitor app has three layers:

1. **Web layer** -- HTML/CSS/JS app running inside a native WebView (WKWebView on iOS, Android System WebView on Android).
2. **Native bridge** -- Serializes JS plugin calls, routes them to native code, and returns results as Promises.
3. **Native layer** -- Swift/ObjC (iOS) and Kotlin/Java (Android) code implementing native functionality.

Data passed across the bridge must be JSON-serializable. Pass files as paths, not base64.

### Project Structure

```
my-app/
  android/                  # Native Android project (committed to VCS)
  ios/                      # Native iOS project (committed to VCS)
    App/
      App/                  # iOS app source files
      App.xcodeproj/
  src/                      # Web app source code
  dist/ or www/ or build/   # Built web assets
  capacitor.config.ts       # Capacitor configuration
  package.json
```

The `android/` and `ios/` directories are full native projects -- they are committed to version control and can be modified directly.

### Capacitor Config

`capacitor.config.ts` (preferred) or `capacitor.config.json` controls app behavior:

```typescript
import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.example.app',
  appName: 'My App',
  webDir: 'dist',
  server: {
    // androidScheme: 'https', // default in Cap 6+
  },
};

export default config;
```

For details, see [App Configuration](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/references/app-configuration.md).

## Creating a New App

### Quick Start

```bash
# 1. Create a web app (React example with Vite)
npm create vite@latest my-app -- --template react-ts
cd my-app && npm install

# 2. Install Capacitor
npm install @capacitor/core
npm install -D @capacitor/cli

# 3. Initialize Capacitor
npx cap init "My App" com.example.myapp --web-dir dist

# 4. Build web assets
npm run build

# 5. Add platforms
npm install @capacitor/android @capacitor/ios
npx cap add android
npx cap add ios

# 6. Sync and run
npx cap sync
npx cap run android
npx cap run ios
```

**Web asset directories by framework:**
- Angular: `dist/<project-name>/browser` (Angular 17+ with application builder)
- React (Vite): `dist`
- Vue (Vite): `dist`
- Vanilla: `www`

For the full guided creation flow, see [capacitor-app-creation](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-creation/SKILL.md).

## Capacitor CLI

All commands: `npx cap <command>`. Most important commands:

| Command | Purpose |
| ------- | ------- |
| `npx cap init <name> <id>` | Initialize Capacitor in a project |
| `npx cap add <platform>` | Add Android or iOS platform |
| `npx cap sync` | Copy web assets + update native dependencies (run after every plugin install, config change, or web build) |
| `npx cap copy` | Copy web assets only (faster, no native dependency update) |
| `npx cap run <platform>` | Build, sync, and deploy to device/emulator |
| `npx cap run <platform> -l --external` | Run with live reload |
| `npx cap open <platform>` | Open native project in IDE |
| `npx cap build <platform>` | Build native project |
| `npx cap doctor` | Diagnose configuration issues |
| `npx cap ls` | List installed plugins |
| `npx cap migrate` | Automated upgrade to newer Capacitor version |

For the full CLI reference, see [CLI Reference](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/references/cli.md).

## Framework Integration

Capacitor works with any web framework. Framework-specific patterns:

### Angular

- Wrap Capacitor plugins in Angular services for DI and testability.
- Plugin event listeners run outside NgZone -- always wrap callbacks in `NgZone.run()`.
- Register listeners in `ngOnInit`, remove in `ngOnDestroy`.

For details, see [capacitor-angular](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-angular/SKILL.md).

### React

- Create custom hooks (`useCamera`, `useNetwork`) that wrap Capacitor plugins.
- Use `useEffect` for listener registration with cleanup to prevent memory leaks.
- React 18 strict mode double-mounts -- ensure cleanup functions work correctly.

For details, see [capacitor-react](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-react/SKILL.md).

### Vue

- Create composables (`useCamera`, `useNetwork`) using Vue 3 Composition API.
- Register listeners in `onMounted`, remove in `onUnmounted`.
- Vue reactivity picks up `ref` changes automatically (no NgZone equivalent needed).

For details, see [capacitor-vue](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-vue/SKILL.md).

## Plugins

Plugins are Capacitor's extension mechanism. Each plugin exposes a JS API backed by native implementations.

### Plugin Sources

- **Official** (`@capacitor/*`) -- Camera, Filesystem, Geolocation, Preferences, etc.
- **Capawesome** (`@capawesome/*`, `@capawesome-team/*`) -- SQLite, NFC, Biometrics, Live Update, etc.
- **Community** (`@capacitor-community/*`) -- AdMob, BLE, SQLite, Stripe, etc.
- **Firebase** (`@capacitor-firebase/*`) -- Analytics, Auth, Messaging, Firestore, etc.
- **MLKit** (`@capacitor-mlkit/*`) -- Barcode scanning, face detection, translation.
- **RevenueCat** (`@revenuecat/purchases-capacitor`) -- In-app purchases.

### Installing a Plugin

```bash
npm install @capacitor/camera
npx cap sync
```

After installation, apply any required platform configuration (permissions in `AndroidManifest.xml`, `Info.plist` entries, etc.) as documented by the plugin.

### Using a Plugin

```typescript
import { Camera, CameraResultType } from '@capacitor/camera';

const photo = await Camera.getPhoto({
  quality: 90,
  resultType: CameraResultType.Uri,
});
```

For the full plugin index (160+ plugins) and setup guides, see [capacitor-plugins](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-plugins/SKILL.md).

## Plugin Development

Create custom Capacitor plugins with native iOS (Swift) and Android (Java/Kotlin) implementations:

1. Scaffold with `npm init @capacitor/plugin@latest`.
2. Define the TypeScript API in `src/definitions.ts`.
3. Implement the web layer in `src/web.ts`.
4. Implement iOS plugin in `ios/Sources/`.
5. Implement Android plugin in `android/src/main/java/`.
6. Verify with `npm run verify`.

Key rules:
- The `registerPlugin()` name in `src/index.ts` must match `jsName` on iOS and `@CapacitorPlugin(name = "...")` on Android.
- iOS methods need `@objc` and must be listed in `pluginMethods` (CAPBridgedPlugin).
- Android methods need `@PluginMethod()` annotation and must be `public`.

For full details, see [capacitor-plugin-development](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-plugin-development/SKILL.md).

## Cross-Platform Best Practices

### Platform Detection

```typescript
import { Capacitor } from '@capacitor/core';

const platform = Capacitor.getPlatform(); // 'android' | 'ios' | 'web'
if (Capacitor.isNativePlatform()) { /* native-only code */ }
if (Capacitor.isPluginAvailable('Camera')) { /* plugin available */ }
```

### Permissions

Follow the check-then-request pattern:

```typescript
const status = await Camera.checkPermissions();
if (status.camera !== 'granted') {
  const requested = await Camera.requestPermissions();
  if (requested.camera === 'denied') {
    // Guide user to app settings -- cannot re-request on iOS
    return;
  }
}
const photo = await Camera.getPhoto({ ... });
```

### Performance

- **Minimize bridge calls** -- batch operations instead of many individual calls.
- **Use file paths** over base64 for binary data.
- **Lazy-load plugins** with dynamic imports for code splitting.

### Error Handling

Always wrap plugin calls in try-catch:

```typescript
try {
  const photo = await Camera.getPhoto({ resultType: CameraResultType.Uri });
} catch (error) {
  if (error.message === 'User cancelled photos app') {
    // Not an error
  } else {
    console.error('Camera error:', error);
  }
}
```

For full details, see [Cross-Platform Best Practices](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/references/cross-platform-best-practices.md).

## Deep Links

Deep links open specific content in the app from external URLs.

- **iOS**: Universal Links via `apple-app-site-association` hosted at `https://<domain>/.well-known/`.
- **Android**: App Links via `assetlinks.json` hosted at `https://<domain>/.well-known/`.

### Listener Setup

```typescript
import { App } from '@capacitor/app';

App.addListener('appUrlOpen', (event) => {
  const path = new URL(event.url).pathname;
  // Route to the appropriate page
});
```

### Platform Configuration

- **iOS**: Add `applinks:<domain>` to Associated Domains capability in `ios/App/App/App.entitlements`.
- **Android**: Add `<intent-filter android:autoVerify="true">` to `android/app/src/main/AndroidManifest.xml`.

For full setup, see [Deep Links](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/references/deep-links.md).

## Storage

| Requirement | Solution |
| ----------- | -------- |
| App settings, preferences | `@capacitor/preferences` (native key-value, persists reliably) |
| Sensitive data (tokens, credentials) | `@capawesome-team/capacitor-secure-preferences` (Keychain/Keystore) |
| Relational data, offline-first | SQLite (`@capawesome-team/capacitor-sqlite` or `@capacitor-community/sqlite`) |
| Files, images, documents | `@capacitor/filesystem` |

**Do NOT use** `localStorage`, `IndexedDB`, or cookies for persistent data -- the OS can evict them (especially on iOS).

For details, see [Storage](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/references/storage.md).

## Security

- **Never embed secrets** (API keys with write access, OAuth secrets, DB credentials) in client code -- move to a server API.
- **Use secure storage** (`@capawesome-team/capacitor-secure-preferences`) for tokens and credentials, not `localStorage` or `@capacitor/preferences`.
- **HTTPS only** -- never allow cleartext HTTP in production.
- **Content Security Policy** -- add a `<meta>` CSP tag in `index.html`.
- **Disable WebView debugging** in production: set `webContentsDebuggingEnabled: false` in `capacitor.config.ts`.
- **Prefer Universal/App Links** over custom URL schemes (verified via HTTPS).
- **iOS Privacy Manifest** (`PrivacyInfo.xcprivacy`) -- required for iOS 17+ when using privacy-sensitive APIs.

For details, see [Security](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/references/security.md).

## Testing

### Unit Testing

Mock Capacitor plugins in Jest/Vitest since tests run in Node.js, not a WebView:

```typescript
vi.mock('@capacitor/camera', () => ({
  Camera: {
    getPhoto: vi.fn().mockResolvedValue({
      webPath: 'https://example.com/photo.jpg',
    }),
  },
}));
```

### E2E Testing

- **Web E2E**: Cypress or Playwright (tests web layer, plugins must be mocked).
- **Native E2E**: Appium (cross-platform) or Detox (iOS-focused).

### Debugging

- **Android**: Enable `webContentsDebuggingEnabled: true`, open `chrome://inspect` in Chrome.
- **iOS**: Enable `webContentsDebuggingEnabled: true`, use Safari > Develop menu > select device.

For details, see [Testing](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/references/testing.md).

## Troubleshooting

### Android

- **`npx cap sync` fails**: Verify `@capacitor/core` and `@capacitor/cli` versions match. Run `cd android && ./gradlew clean`.
- **Build fails after config changes**: Clean with `cd android && ./gradlew clean`, then rebuild.
- **Plugin not found at runtime**: Run `npx cap sync` after plugin installation. Verify Gradle sync completed.
- **SDK errors**: Verify `ANDROID_HOME` is set. Install missing SDK versions via Android Studio SDK Manager.
- **White square notification icon**: Push notification icons must be white pixels on transparent background.

### iOS

- **Build fails with "no such module"**: Run `npx cap sync ios`. For CocoaPods: `cd ios/App && pod install --repo-update`.
- **Build fails after config changes**: Clean build folder (Xcode Product > Clean Build Folder) or delete `ios/App/Pods` and re-run `pod install`.
- **Simulator cannot receive push notifications**: Use a physical device for push notification testing.
- **Permission denied permanently**: Cannot re-request on iOS. Guide user to Settings > App > Permissions.
- **WebView not loading**: Verify `webDir` in `capacitor.config.ts` matches the actual build output directory.

### General

- **Live reload not connecting**: Ensure device and dev machine are on the same network. Use `--external` flag.
- **Plugin not found**: Run `npx cap sync`. Verify plugin is in `package.json` dependencies.
- **`Capacitor is not defined`**: Install `@capacitor/core` (`npm install @capacitor/core`).

For full troubleshooting, see [Android Troubleshooting](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/references/troubleshooting-android.md) and [iOS Troubleshooting](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/references/troubleshooting-ios.md).

## Upgrading

Capacitor supports upgrades across major versions (4 through 8). Apply each major version jump sequentially -- do not skip intermediate versions.

| Current to Target | Node.js | Xcode | Android Studio |
| ----------------- | ------- | ----- | -------------- |
| to 5 | 16+ | 14.1+ | Flamingo 2022.2.1+ |
| to 6 | 18+ | 15.0+ | Hedgehog 2023.1.1+ |
| to 7 | 20+ | 16.0+ | Ladybug 2024.2.1+ |
| to 8 | 22+ | 26.0+ | Otter 2025.2.1+ |

Quick automated upgrade:

```bash
npx cap migrate
npx cap sync
```

If `npx cap migrate` fails partially, apply manual steps from the upgrade guides.

For app upgrades, see [capacitor-app-upgrades](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-upgrades/SKILL.md).
For plugin upgrades, see [capacitor-plugin-upgrades](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-plugin-upgrades/SKILL.md).

## Capawesome Cloud

[Capawesome Cloud](https://cloud.capawesome.io) provides cloud infrastructure for Capacitor apps: native builds, live updates, and automated app store publishing.

Website: [capawesome.io](https://capawesome.io) | Cloud Services: [cloud.capawesome.io](https://cloud.capawesome.io)

### Getting Started

```bash
# Install and authenticate
npx @capawesome/cli login

# Create an app
npx @capawesome/cli apps:create
```

### Live Updates

Deploy over-the-air (OTA) web updates to Capacitor apps without going through the app stores. Users receive updates immediately on next app launch.

**Setup:**

```bash
# Install the live update plugin
npm install @capawesome/capacitor-live-update
npx cap sync
```

Configure in `capacitor.config.ts`:

```typescript
const config: CapacitorConfig = {
  plugins: {
    LiveUpdate: {
      appId: '<APP_ID>',
      autoUpdate: true,
    },
  },
};
```

**Deploy an update:**

```bash
npm run build
npx @capawesome/cli apps:liveupdates:upload --app-id <APP_ID>
```

### Native Builds

Build iOS and Android apps in the cloud without local build environments. Supports signing certificates, environments, and build configuration.

```bash
# Trigger a build
npx @capawesome/cli apps:builds:create --app-id <APP_ID> --platform android

# Download the artifact
npx @capawesome/cli apps:builds:download --app-id <APP_ID> --build-id <BUILD_ID>
```

### App Store Publishing

Automate submissions to Apple App Store (TestFlight) and Google Play Store.

```bash
# Create a deployment destination
npx @capawesome/cli apps:destinations:create --app-id <APP_ID>

# Deploy a build
npx @capawesome/cli apps:deployments:create --app-id <APP_ID> --build-id <BUILD_ID>
```

### CI/CD Integration

Use token-based auth for CI/CD pipelines:

```bash
npx @capawesome/cli login --token <TOKEN>
npx @capawesome/cli apps:builds:create --app-id <APP_ID> --platform ios --detached
```

For full Capawesome Cloud setup, see [capawesome-cloud](https://github.com/capawesome-team/skills/blob/main/skills/capawesome-cloud/SKILL.md).
For the Capawesome CLI reference, see [capawesome-cli](https://github.com/capawesome-team/skills/blob/main/skills/capawesome-cli/SKILL.md).

## Push Notifications

Set up push notifications using Firebase Cloud Messaging (FCM) via `@capacitor-firebase/messaging`:

```bash
npm install @capacitor-firebase/messaging firebase
npx cap sync
```

Requires Firebase project setup, platform-specific configuration (APNs for iOS, `google-services.json` for Android), and permission handling.

For the full setup guide, see [capacitor-push-notifications](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-push-notifications/SKILL.md).

## In-App Purchases

Set up in-app purchases and subscriptions with either:

- **Capawesome Purchases** (`@capawesome-team/capacitor-purchases`) -- lightweight, no third-party backend, requires Capawesome Insiders license.
- **RevenueCat** (`@revenuecat/purchases-capacitor`) -- full managed backend with receipt validation, analytics, and integrations.

Both require App Store Connect (iOS) and/or Google Play Console (Android) product configuration.

For the full setup guide, see [capacitor-in-app-purchases](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-in-app-purchases/SKILL.md).

## Related Skills

- [capacitor-app-creation](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-creation/SKILL.md) -- Create a new Capacitor app from scratch.
- [capacitor-app-development](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-development/SKILL.md) -- General Capacitor development topics, configuration, and troubleshooting.
- [capacitor-angular](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-angular/SKILL.md) -- Angular-specific Capacitor patterns.
- [capacitor-react](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-react/SKILL.md) -- React-specific Capacitor patterns.
- [capacitor-vue](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-vue/SKILL.md) -- Vue-specific Capacitor patterns.
- [capacitor-plugins](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-plugins/SKILL.md) -- Install and configure 160+ Capacitor plugins.
- [capacitor-plugin-development](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-plugin-development/SKILL.md) -- Create custom Capacitor plugins.
- [capacitor-app-upgrades](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-app-upgrades/SKILL.md) -- Upgrade Capacitor apps across major versions.
- [capacitor-plugin-upgrades](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-plugin-upgrades/SKILL.md) -- Upgrade Capacitor plugins across major versions.
- [capacitor-push-notifications](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-push-notifications/SKILL.md) -- Push notifications with FCM.
- [capacitor-in-app-purchases](https://github.com/capawesome-team/skills/blob/main/skills/capacitor-in-app-purchases/SKILL.md) -- In-app purchases and subscriptions.
- [capawesome-cloud](https://github.com/capawesome-team/skills/blob/main/skills/capawesome-cloud/SKILL.md) -- Live updates, native builds, app store publishing.
- [capawesome-cli](https://github.com/capawesome-team/skills/blob/main/skills/capawesome-cli/SKILL.md) -- Capawesome CLI reference.
