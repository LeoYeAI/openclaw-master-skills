---
name: add-analytics
description: Add Google Analytics 4 tracking to any project. Detects framework, adds tracking code, sets up events, and configures privacy settings.
argument-hint: "<measurement-id> [--events] [--consent] [--debug]"
---

# Google Analytics 4 Setup Skill

You are setting up Google Analytics 4 (GA4) for a project. Follow this comprehensive guide to add analytics properly.

## Arguments

Parse the following from `$ARGUMENTS`:
- **Measurement ID**: Format `G-XXXXXXXXXX` (required, ask if not provided)
- **--events**: Include custom event tracking helpers
- **--consent**: Include cookie consent integration
- **--debug**: Enable debug mode for development

## Step 1: Detect Project Type

Scan the project to determine the framework/setup:

```
Priority detection order:
1. next.config.js/ts → Next.js
2. nuxt.config.js/ts → Nuxt.js
3. astro.config.mjs → Astro
4. svelte.config.js → SvelteKit
5. remix.config.js → Remix
6. gatsby-config.js → Gatsby
7. vite.config.js + src/App.vue → Vue + Vite
8. vite.config.js + src/App.tsx → React + Vite
9. angular.json → Angular
10. package.json with "react-scripts" → Create React App
11. index.html only → Plain HTML
12. _app.tsx/jsx → Next.js (App Router check: app/ directory)
```

Also check for:
- TypeScript usage (tsconfig.json)
- Existing analytics (search for gtag, GA, analytics)
- Package manager (pnpm-lock.yaml, yarn.lock, package-lock.json)

## Step 2: Validate Measurement ID

The Measurement ID must:
- Start with `G-` (GA4 format)
- Be followed by exactly 10 alphanumeric characters
- Example: `G-ABC1234567`

If the user provides a `UA-` ID, inform them:
> "You provided a Universal Analytics ID (UA-). GA4 uses Measurement IDs starting with 'G-'.
> Universal Analytics was sunset in July 2024. You'll need to create a GA4 property at analytics.google.com"

## Step 3: Implementation by Framework

### Next.js (App Router - app/ directory)

Create `app/layout.tsx` modification or create `components/GoogleAnalytics.tsx`:

```tsx
// components/GoogleAnalytics.tsx
'use client'

import Script from 'next/script'

interface GoogleAnalyticsProps {
  measurementId: string
}

export function GoogleAnalytics({ measurementId }: GoogleAnalyticsProps) {
  return (
    <>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${measurementId}`}
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${measurementId}');
        `}
      </Script>
    </>
  )
}
```

Add to root layout:
```tsx
// app/layout.tsx
import { GoogleAnalytics } from '@/components/GoogleAnalytics'

// Add inside <body> or <html>:
<GoogleAnalytics measurementId="G-XXXXXXXXXX" />
```

### Next.js (Pages Router - pages/ directory)

Modify `pages/_app.tsx`:

```tsx
// pages/_app.tsx
import type { AppProps } from 'next/app'
import Script from 'next/script'

const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA_MEASUREMENT_ID}');
        `}
      </Script>
      <Component {...pageProps} />
    </>
  )
}
```

### React (Vite/CRA)

Create `src/lib/analytics.ts`:

```typescript
// src/lib/analytics.ts
export const GA_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void
    dataLayer: unknown[]
  }
}

export const initGA = () => {
  if (typeof window === 'undefined') return

  const script = document.createElement('script')
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`
  script.async = true
  document.head.appendChild(script)

  window.dataLayer = window.dataLayer || []
  window.gtag = function gtag() {
    window.dataLayer.push(arguments)
  }
  window.gtag('js', new Date())
  window.gtag('config', GA_MEASUREMENT_ID)
}

export const pageview = (url: string) => {
  window.gtag('config', GA_MEASUREMENT_ID, {
    page_path: url,
  })
}

export const event = (action: string, params?: Record<string, unknown>) => {
  window.gtag('event', action, params)
}
```

Initialize in `src/main.tsx`:

```tsx
import { initGA } from './lib/analytics'

// Initialize before render
if (import.meta.env.PROD) {
  initGA()
}
```

### Vue 3 (Vite)

Create `src/plugins/analytics.ts`:

```typescript
// src/plugins/analytics.ts
import type { App } from 'vue'
import type { Router } from 'vue-router'

const GA_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void
    dataLayer: unknown[]
  }
}

export const analyticsPlugin = {
  install(app: App, { router }: { router: Router }) {
    // Load gtag script
    const script = document.createElement('script')
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`
    script.async = true
    document.head.appendChild(script)

    window.dataLayer = window.dataLayer || []
    window.gtag = function gtag() {
      window.dataLayer.push(arguments)
    }
    window.gtag('js', new Date())
    window.gtag('config', GA_MEASUREMENT_ID)

    // Track route changes
    router.afterEach((to) => {
      window.gtag('config', GA_MEASUREMENT_ID, {
        page_path: to.fullPath,
      })
    })

    // Provide global methods
    app.config.globalProperties.$gtag = window.gtag
  }
}
```

### Nuxt 3

Create `plugins/analytics.client.ts`:

```typescript
// plugins/analytics.client.ts
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const measurementId = config.public.gaMeasurementId

  if (!measurementId) return

  // Load gtag
  useHead({
    script: [
      {
        src: `https://www.googletagmanager.com/gtag/js?id=${measurementId}`,
        async: true,
      },
      {
        innerHTML: `
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${measurementId}');
        `,
      },
    ],
  })

  // Track route changes
  const router = useRouter()
  router.afterEach((to) => {
    window.gtag('config', measurementId, {
      page_path: to.fullPath,
    })
  })
})
```

Add to `nuxt.config.ts`:

```typescript
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      gaMeasurementId: process.env.NUXT_PUBLIC_GA_MEASUREMENT_ID,
    },
  },
})
```

### Astro

Create `src/components/Analytics.astro`:

```astro
---
// src/components/Analytics.astro
interface Props {
  measurementId: string
}

const { measurementId } = Astro.props
---

<script
  is:inline
  define:vars={{ measurementId }}
  src={`https://www.googletagmanager.com/gtag/js?id=${measurementId}`}
></script>

<script is:inline define:vars={{ measurementId }}>
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    dataLayer.push(arguments);
  }
  gtag('js', new Date());
  gtag('config', measurementId);
</script>
```

Add to layout:

```astro
---
import Analytics from '../components/Analytics.astro'
---
<html>
  <head>
    <Analytics measurementId="G-XXXXXXXXXX" />
  </head>
</html>
```

### SvelteKit

Create `src/lib/analytics.ts` and `src/routes/+layout.svelte`:

```typescript
// src/lib/analytics.ts
import { browser } from '$app/environment'

export const GA_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID

export function initGA() {
  if (!browser) return

  const script = document.createElement('script')
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`
  script.async = true
  document.head.appendChild(script)

  window.dataLayer = window.dataLayer || []
  window.gtag = function gtag() {
    window.dataLayer.push(arguments)
  }
  window.gtag('js', new Date())
  window.gtag('config', GA_MEASUREMENT_ID)
}

export function trackPageview(url: string) {
  if (!browser) return
  window.gtag('config', GA_MEASUREMENT_ID, { page_path: url })
}
```

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import { onMount } from 'svelte'
  import { page } from '$app/stores'
  import { initGA, trackPageview } from '$lib/analytics'

  onMount(() => {
    initGA()
  })

  $: if ($page.url.pathname) {
    trackPageview($page.url.pathname)
  }
</script>

<slot />
```

### Plain HTML

Add to `<head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## Step 4: Environment Variables

Create or update `.env` / `.env.local`:

```bash
# For Next.js
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX

# For Vite (React/Vue/Svelte)
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX

# For Nuxt
NUXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

Add to `.env.example` if it exists (without the actual ID):

```bash
# Google Analytics 4 Measurement ID
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

**IMPORTANT**: Add `.env.local` to `.gitignore` if not already present.

## Step 5: Event Tracking Helpers (if --events flag)

Create a comprehensive events utility:

```typescript
// lib/analytics-events.ts

/**
 * GA4 Event Tracking Utilities
 *
 * Recommended events: https://support.google.com/analytics/answer/9267735
 */

type GTagEvent = {
  action: string
  category?: string
  label?: string
  value?: number
  [key: string]: unknown
}

// Core event function
export const trackEvent = ({ action, category, label, value, ...rest }: GTagEvent) => {
  if (typeof window === 'undefined' || !window.gtag) return

  window.gtag('event', action, {
    event_category: category,
    event_label: label,
    value,
    ...rest,
  })
}

// Engagement events
export const trackClick = (elementName: string, location?: string) => {
  trackEvent({
    action: 'click',
    category: 'engagement',
    label: elementName,
    click_location: location,
  })
}

export const trackScroll = (percentage: number) => {
  trackEvent({
    action: 'scroll',
    category: 'engagement',
    value: percentage,
  })
}

// Conversion events
export const trackSignUp = (method: string) => {
  trackEvent({
    action: 'sign_up',
    method,
  })
}

export const trackLogin = (method: string) => {
  trackEvent({
    action: 'login',
    method,
  })
}

export const trackPurchase = (params: {
  transactionId: string
  value: number
  currency: string
  items?: Array<{
    itemId: string
    itemName: string
    price: number
    quantity: number
  }>
}) => {
  trackEvent({
    action: 'purchase',
    transaction_id: params.transactionId,
    value: params.value,
    currency: params.currency,
    items: params.items,
  })
}

// Content events
export const trackSearch = (searchTerm: string) => {
  trackEvent({
    action: 'search',
    search_term: searchTerm,
  })
}

export const trackShare = (method: string, contentType: string, itemId: string) => {
  trackEvent({
    action: 'share',
    method,
    content_type: contentType,
    item_id: itemId,
  })
}

// Form events
export const trackFormStart = (formName: string) => {
  trackEvent({
    action: 'form_start',
    form_name: formName,
  })
}

export const trackFormSubmit = (formName: string, success: boolean) => {
  trackEvent({
    action: 'form_submit',
    form_name: formName,
    success,
  })
}

// Error tracking
export const trackError = (errorMessage: string, errorLocation?: string) => {
  trackEvent({
    action: 'exception',
    description: errorMessage,
    fatal: false,
    error_location: errorLocation,
  })
}

// Custom event builder for flexibility
export const createCustomEvent = (eventName: string) => {
  return (params?: Record<string, unknown>) => {
    trackEvent({
      action: eventName,
      ...params,
    })
  }
}
```

## Step 6: Cookie Consent Integration (if --consent flag)

Create a consent-aware wrapper:

```typescript
// lib/analytics-consent.ts

type ConsentState = 'granted' | 'denied'

interface ConsentConfig {
  analytics_storage: ConsentState
  ad_storage: ConsentState
  ad_user_data: ConsentState
  ad_personalization: ConsentState
}

const CONSENT_COOKIE = 'analytics_consent'

// Initialize with consent mode
export const initWithConsent = (measurementId: string) => {
  if (typeof window === 'undefined') return

  // Set default consent state (denied until user consents)
  window.gtag('consent', 'default', {
    analytics_storage: 'denied',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    wait_for_update: 500, // Wait for consent banner
  })

  // Load gtag
  const script = document.createElement('script')
  script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`
  script.async = true
  document.head.appendChild(script)

  window.dataLayer = window.dataLayer || []
  window.gtag = function gtag() {
    window.dataLayer.push(arguments)
  }
  window.gtag('js', new Date())
  window.gtag('config', measurementId)

  // Check for existing consent
  const savedConsent = getCookie(CONSENT_COOKIE)
  if (savedConsent) {
    updateConsent(JSON.parse(savedConsent))
  }
}

// Update consent when user makes a choice
export const updateConsent = (consent: Partial<ConsentConfig>) => {
  if (typeof window === 'undefined' || !window.gtag) return

  const consentState: ConsentConfig = {
    analytics_storage: consent.analytics_storage || 'denied',
    ad_storage: consent.ad_storage || 'denied',
    ad_user_data: consent.ad_user_data || 'denied',
    ad_personalization: consent.ad_personalization || 'denied',
  }

  window.gtag('consent', 'update', consentState)

  // Save to cookie
  setCookie(CONSENT_COOKIE, JSON.stringify(consentState), 365)
}

// Convenience functions
export const acceptAll = () => {
  updateConsent({
    analytics_storage: 'granted',
    ad_storage: 'granted',
    ad_user_data: 'granted',
    ad_personalization: 'granted',
  })
}

export const acceptAnalyticsOnly = () => {
  updateConsent({
    analytics_storage: 'granted',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
  })
}

export const denyAll = () => {
  updateConsent({
    analytics_storage: 'denied',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
  })
}

// Cookie utilities
function setCookie(name: string, value: string, days: number) {
  const date = new Date()
  date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000)
  document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/;SameSite=Lax`
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`))
  return match ? match[2] : null
}
```

## Step 7: Debug Mode (if --debug flag)

Add debug configuration:

```typescript
// For development, enable debug mode
if (process.env.NODE_ENV === 'development') {
  window.gtag('config', 'G-XXXXXXXXXX', {
    debug_mode: true,
  })
}
```

Also recommend installing the [Google Analytics Debugger](https://chrome.google.com/webstore/detail/google-analytics-debugger/jnkmfdileelhofjcijamephohjechhna) Chrome extension.

## Step 8: TypeScript Declarations

Create `types/gtag.d.ts` if using TypeScript:

```typescript
// types/gtag.d.ts
declare global {
  interface Window {
    gtag: Gtag.Gtag
    dataLayer: object[]
  }
}

declare namespace Gtag {
  interface Gtag {
    (command: 'config', targetId: string, config?: ConfigParams): void
    (command: 'set', targetId: string, config: ConfigParams): void
    (command: 'set', config: ConfigParams): void
    (command: 'js', date: Date): void
    (command: 'event', eventName: string, eventParams?: EventParams): void
    (command: 'consent', consentArg: 'default' | 'update', consentParams: ConsentParams): void
    (...args: unknown[]): void
  }

  interface ConfigParams {
    page_title?: string
    page_location?: string
    page_path?: string
    send_page_view?: boolean
    debug_mode?: boolean
    [key: string]: unknown
  }

  interface EventParams {
    event_category?: string
    event_label?: string
    value?: number
    [key: string]: unknown
  }

  interface ConsentParams {
    analytics_storage?: 'granted' | 'denied'
    ad_storage?: 'granted' | 'denied'
    ad_user_data?: 'granted' | 'denied'
    ad_personalization?: 'granted' | 'denied'
    wait_for_update?: number
  }
}

export {}
```

## Step 9: Verification Checklist

After implementation, verify:

1. [ ] Measurement ID is correct format (G-XXXXXXXXXX)
2. [ ] Script loads in production (check Network tab)
3. [ ] Real-time reports show activity in GA4 dashboard
4. [ ] Page views are tracked on navigation
5. [ ] No console errors related to gtag
6. [ ] Environment variables are not committed to git
7. [ ] TypeScript has no type errors (if applicable)

## Step 10: Summary Output

After completing setup, provide the user with:

1. **Files created/modified** (list them)
2. **Environment variables needed** (with example values)
3. **Next steps**:
   - Add the Measurement ID to environment variables
   - Deploy and verify in GA4 Real-time reports
   - Set up conversions in GA4 dashboard
   - Consider adding custom events for key user actions

## Common Issues & Solutions

**"gtag is not defined"**
- Script hasn't loaded yet; ensure async loading is handled

**No data in GA4**
- Check if ad blockers are preventing tracking
- Verify Measurement ID is correct
- Check browser console for errors

**Double page views**
- SPA router sending duplicate events; implement deduplication

**GDPR Compliance**
- Always implement consent mode for EU users
- Use the --consent flag to add consent management
