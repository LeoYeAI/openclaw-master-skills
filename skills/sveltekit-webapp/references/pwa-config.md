# PWA Configuration

## Installation

```bash
npm install -D vite-plugin-pwa
```

## vite.config.ts

```typescript
import { sveltekit } from '@sveltejs/kit/vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    sveltekit(),
    SvelteKitPWA({
      srcDir: 'src',
      mode: 'production',
      strategies: 'generateSW',
      registerType: 'prompt',
      manifest: {
        name: 'APP_NAME',
        short_name: 'APP_SHORT_NAME',
        description: 'APP_DESCRIPTION',
        theme_color: '#ffffff',
        background_color: '#ffffff',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/icons/icon-512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: '/icons/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,webp,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      },
      devOptions: {
        enabled: true,
        type: 'module'
      }
    })
  ]
});
```

## ReloadPrompt Component

Create `src/lib/components/ReloadPrompt.svelte`:

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  
  let needRefresh = $state(false);
  let offlineReady = $state(false);
  let updateServiceWorker: (() => Promise<void>) | undefined;

  onMount(async () => {
    const { registerSW } = await import('virtual:pwa-register');
    
    updateServiceWorker = registerSW({
      immediate: true,
      onNeedRefresh() {
        needRefresh = true;
      },
      onOfflineReady() {
        offlineReady = true;
        setTimeout(() => { offlineReady = false; }, 3000);
      },
      onRegistered(r) {
        console.log('SW registered:', r);
      },
      onRegisterError(error) {
        console.error('SW registration error:', error);
      }
    });
  });

  async function refresh() {
    await updateServiceWorker?.();
  }

  function close() {
    needRefresh = false;
    offlineReady = false;
  }
</script>

{#if needRefresh}
  <div class="fixed bottom-4 right-4 bg-blue-600 text-white p-4 rounded-lg shadow-lg z-50">
    <p class="mb-2">New version available!</p>
    <div class="flex gap-2">
      <button onclick={refresh} class="px-3 py-1 bg-white text-blue-600 rounded">
        Update
      </button>
      <button onclick={close} class="px-3 py-1 border border-white rounded">
        Dismiss
      </button>
    </div>
  </div>
{/if}

{#if offlineReady}
  <div class="fixed bottom-4 right-4 bg-green-600 text-white p-4 rounded-lg shadow-lg z-50">
    Ready for offline use ✓
  </div>
{/if}
```

## PWA Icons

Create icons at these sizes in `static/icons/`:
- `icon-192.png` (192x192)
- `icon-512.png` (512x512)

For maskable icons, ensure safe zone (center 80%) contains the main content.

## TypeScript Declaration

Add to `src/app.d.ts`:

```typescript
declare module 'virtual:pwa-register' {
  export function registerSW(options?: {
    immediate?: boolean;
    onNeedRefresh?: () => void;
    onOfflineReady?: () => void;
    onRegistered?: (registration: ServiceWorkerRegistration | undefined) => void;
    onRegisterError?: (error: Error) => void;
  }): () => Promise<void>;
}
```

## Include in Layout

Add to `src/routes/+layout.svelte`:

```svelte
<script>
  import ReloadPrompt from '$lib/components/ReloadPrompt.svelte';
</script>

<!-- ... rest of layout ... -->

<ReloadPrompt />
```
