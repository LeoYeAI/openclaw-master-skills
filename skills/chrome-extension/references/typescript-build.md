# TypeScript and Build Tooling Reference

## Table of contents
1. TypeScript setup
2. Project structure
3. Build tools comparison
4. Plain Vite (no framework)
5. Webpack setup
6. esbuild / tsup setup
7. Type definitions for chrome.* APIs
8. Shared code between contexts

## 1. TypeScript setup

### Install Chrome extension types

```bash
npm install -D typescript @types/chrome
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "outDir": "dist",
    "rootDir": "src",
    "declaration": false,
    "sourceMap": true,
    "types": ["chrome"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

Note: `@types/chrome` provides types for all `chrome.*` APIs. They are automatically
available via the `types` field.

## 2. Project structure

### Recommended layout

```
my-extension/
├── src/
│   ├── background/
│   │   └── index.ts          # Service worker entry
│   ├── content/
│   │   ├── index.ts          # Content script entry
│   │   └── styles.css
│   ├── popup/
│   │   ├── index.html
│   │   ├── index.tsx          # or .ts for vanilla
│   │   └── styles.css
│   ├── options/
│   │   ├── index.html
│   │   └── index.tsx
│   ├── sidepanel/
│   │   ├── index.html
│   │   └── index.tsx
│   ├── shared/
│   │   ├── messages.ts        # Typed message definitions
│   │   ├── storage.ts         # Storage helpers
│   │   ├── rpc.ts             # RPC layer
│   │   └── constants.ts
│   └── manifest.json          # or manifest.ts with CRXJS
├── public/
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
├── dist/                      # Build output (load this in chrome://extensions)
├── tsconfig.json
├── package.json
└── vite.config.ts             # or webpack.config.js
```

### Key principle: shared code

Put message types, storage keys, constants, and utility functions in `src/shared/`.
Import from any context. The bundler handles the rest.

```typescript
// src/shared/messages.ts
export type Message =
  | { type: 'FETCH_API'; url: string }
  | { type: 'GET_SETTINGS' }
  | { type: 'SET_THEME'; theme: 'light' | 'dark' };

export type ResponseMap = {
  FETCH_API: { ok: boolean; data: string };
  GET_SETTINGS: Settings;
  SET_THEME: void;
};

export interface Settings { theme: 'light' | 'dark'; enabled: boolean; }

// src/shared/constants.ts
export const STORAGE_KEYS = {
  SETTINGS: 'settings',
  CACHE: 'cache',
  AUTH_TOKEN: 'auth_token',
} as const;
```

## 3. Build tools comparison

| Tool | DX (HMR) | Config complexity | Content script HMR | Ecosystem |
|------|----------|-------------------|---------------------|-----------|
| **CRXJS + Vite** | Excellent | Minimal | Yes (true HMR) | Vite plugins |
| **WXT** | Excellent | Convention-based | Yes | Built-in everything |
| **Plasmo** | Good | Minimal | Partial | React-focused |
| **Vite (manual)** | Manual reload | Medium | No | Vite plugins |
| **Webpack** | Manual reload | High | No | Huge ecosystem |
| **esbuild/tsup** | None | Low | No | Fast builds |

**Recommendation**:
- For Vite users wanting minimal abstraction: **CRXJS** (see crxjs skill)
- For a full framework with conventions: **WXT**
- For maximum control: **Vite manual** or **esbuild**
- For fast CI/production builds: **esbuild/tsup**

## 4. Plain Vite (no CRXJS)

When you want Vite's speed without CRXJS magic:

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'src/popup/index.html'),
        options: resolve(__dirname, 'src/options/index.html'),
        background: resolve(__dirname, 'src/background/index.ts'),
        content: resolve(__dirname, 'src/content/index.ts'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
  },
});
```

You must manually copy manifest.json and icons to dist/. Use a plugin or script:

```typescript
// vite-plugin-copy-manifest.ts
import { copyFileSync, mkdirSync } from 'fs';

export function copyManifest() {
  return {
    name: 'copy-manifest',
    writeBundle() {
      copyFileSync('src/manifest.json', 'dist/manifest.json');
      mkdirSync('dist/icons', { recursive: true });
      ['icon16.png', 'icon48.png', 'icon128.png'].forEach(f => {
        copyFileSync(`public/icons/${f}`, `dist/icons/${f}`);
      });
    },
  };
}
```

No HMR for content scripts. You must manually reload the extension after changes.

## 5. Webpack setup

```javascript
// webpack.config.js
const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
  mode: 'development',
  devtool: 'cheap-module-source-map',
  entry: {
    background: './src/background/index.ts',
    content: './src/content/index.ts',
    popup: './src/popup/index.tsx',
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js',
    clean: true,
  },
  module: {
    rules: [
      { test: /\.tsx?$/, use: 'ts-loader', exclude: /node_modules/ },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] },
    ],
  },
  resolve: { extensions: ['.ts', '.tsx', '.js'] },
  plugins: [
    new CopyPlugin({
      patterns: [
        { from: 'src/manifest.json' },
        { from: 'public', to: '.' },
        { from: 'src/popup/index.html', to: 'popup.html' },
      ],
    }),
  ],
};
```

## 6. esbuild / tsup setup

Fastest build times. Good for CI or when you don't need HMR.

```typescript
// build.ts
import * as esbuild from 'esbuild';
import { copyFileSync } from 'fs';

async function build() {
  // Service worker (single bundle, no code splitting)
  await esbuild.build({
    entryPoints: ['src/background/index.ts'],
    bundle: true,
    outfile: 'dist/background.js',
    format: 'esm',
    target: 'chrome116',
  });

  // Content script
  await esbuild.build({
    entryPoints: ['src/content/index.ts'],
    bundle: true,
    outfile: 'dist/content.js',
    format: 'iife',          // content scripts should be IIFE
    target: 'chrome116',
  });

  // Popup
  await esbuild.build({
    entryPoints: ['src/popup/index.tsx'],
    bundle: true,
    outfile: 'dist/popup.js',
    format: 'esm',
    target: 'chrome116',
    loader: { '.tsx': 'tsx' },
  });

  copyFileSync('src/manifest.json', 'dist/manifest.json');
}

build();
```

## 7. Type definitions for chrome.* APIs

`@types/chrome` covers most APIs. For newer APIs not yet typed:

```typescript
// types/chrome-extended.d.ts
declare namespace chrome.sidePanel {
  function setPanelBehavior(options: { openPanelOnActionClick: boolean }): Promise<void>;
  function setOptions(options: {
    tabId?: number;
    path?: string;
    enabled?: boolean;
  }): Promise<void>;
  function open(options: { windowId?: number; tabId?: number }): Promise<void>;
}
```

## 8. Shared code between contexts

The bundler should tree-shake unused imports per entry point. But be aware:

- Service worker: no DOM APIs (`document`, `window`, `HTMLElement`)
- Content script: has DOM but limited chrome.* APIs
- Popup/options: full DOM + full chrome.* APIs

```typescript
// shared/utils.ts
// Safe for all contexts (no DOM, no chrome.* specifics)
export function debounce<T extends (...args: any[]) => void>(fn: T, ms: number) {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}

// shared/storage.ts
// Safe for all contexts (chrome.storage available everywhere)
export async function getSetting<K extends keyof Settings>(key: K): Promise<Settings[K]> {
  const result = await chrome.storage.sync.get(key);
  return result[key];
}
```
