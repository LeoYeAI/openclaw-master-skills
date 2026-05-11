# Minimal Host Template

Use this as the default shape for host-app integration.

## Goal

Keep host code small and explicit:

- one bootstrap location
- direct SDK calls in feature code
- no large translation layer
- canonical onboarding/paywall/purchase event names at touched call sites

## Dashboard Credentials

Before bootstrap code is added:

- Open [dash.analyticscli.com](https://dash.analyticscli.com) and select the target project.
- In **API Keys**, copy the publishable ingest API key for SDK init.
- If CLI validation is in scope, create/copy a CLI `readonly_token` in the same **API Keys** area.
- Optional for CLI verification: set a default project once with `analyticscli projects select` (arrow-key picker), or pass `--project <project_id>` per command.

## Bootstrap Template (Web)

```ts
import { init } from '@analyticscli/sdk';

export const analytics = init({
  apiKey: process.env.NEXT_PUBLIC_ANALYTICSCLI_PUBLISHABLE_API_KEY ?? '',
  platform: 'web',
  identityTrackingMode: 'consent_gated', // default
});
```

## Bootstrap Template (React Native / Expo)

```ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Application from 'expo-application';
import { Platform } from 'react-native';
import { init } from '@analyticscli/sdk';

export const analytics = init({
  apiKey: process.env.EXPO_PUBLIC_ANALYTICSCLI_PUBLISHABLE_API_KEY,
  debug: __DEV__,
  platform: Platform.OS,
  appVersion: Application.nativeApplicationVersion,
  identityTrackingMode: 'consent_gated', // default
  storage: AsyncStorage, // optional for persistent IDs after consent
});
```

`ready()` does not start tracking. It is only for blocking flow transitions until async storage hydration finishes.

## React Native Non-Onboarding Screen Tracking

For React Native / Expo screens outside onboarding, track screen views on focus:

```ts
import { useFocusEffect } from '@react-navigation/native';
import { useCallback } from 'react';
import { analytics } from '@/utils/analytics';

export function ResultsScreen() {
  useFocusEffect(
    useCallback(() => {
      analytics.screen('results', {
        screen_class: 'ResultsScreen',
        source: 'tabs',
      });
    }, []),
  );

  return null;
}
```

Rules:

- Use one screen-tracking owner per route transition (parent layout or child screen, not both).
- Keep SDK screen dedupe defaults enabled (`dedupeScreenViewsPerSession: true`) as a safety net for accidental double-fired hooks.
- Keep onboarding overlap dedupe enabled (`dedupeOnboardingScreenStepViewOverlapsPerSession: true`) so onboarding `screen:*` and `onboarding:step_view` are not double-counted for the same step.
- Adjust `screenViewDedupeWindowMs` only when navigation behavior requires it (default `1200` ms, also used for onboarding screen/step overlap dedupe).
- Keep onboarding milestones on dedicated onboarding APIs; do not replace them with screen-only events.

## Full-Tracking Consent

```ts
// user accepts full tracking
analytics.setFullTrackingConsent(true);

// user declines full tracking but strict analytics can continue
analytics.setFullTrackingConsent(false);
```

## Call-Site Template

```ts
import { analytics } from '@/utils/analytics';

const paywall = analytics.createPaywallTracker({
  source: 'onboarding',
  paywallId: 'default_paywall',
  offering: 'rc_main',
});

analytics.screen('onboarding_region');

paywall.shown({
  fromScreen: 'onboarding_offer',
});

paywall.purchaseSuccess({
  packageId: 'annual',
});
```

For onboarding/survey in touched flows, prefer dedicated APIs:

```ts
const onboarding = analytics.createOnboardingTracker({
  onboardingFlowId: 'onboarding_v4',
  onboardingFlowVersion: '4.0.0',
  isNewUser: true,
  stepCount: 5,
});

const step = onboarding.step('welcome', 0);
step.view();
step.complete();
step.surveyResponse({
  // shared flow fields come from tracker defaults
  surveyKey: 'onboarding_main',
  questionKey: 'primary_goal',
  answerType: 'single_choice',
  responseKey: 'growth',
});
```

For repeated survey steps, keep payloads minimal by reusing tracker defaults instead of passing
`onboardingFlowId`/`onboardingFlowVersion`/`stepCount`/`isNewUser` on every call.

For RevenueCat flows, keep identity aligned:

```ts
analytics.setUser(appUserId); // same id passed to Purchases.logIn(appUserId)
// ...
analytics.clearUser(); // on sign-out
```

Create one paywall tracker per stable paywall flow context. Do not recreate a new
`createPaywallTracker(...)` instance for every callback/event.
If your provider exposes it, always pass an `offering` identifier in tracker defaults
(RevenueCat offering, Adapty paywall/placement, Superwall placement/paywall id).

## Hosted Paywall Screen Template

When the paywall UI is hosted by a provider SDK, wire lifecycle callbacks to one screen-level tracker:

```ts
const paywall = analytics.createPaywallTracker({
  source: screenOrigin,
  paywallId: routeName,
  offering: providerOfferingId,
});

paywall.shown({ fromScreen: routeName, packageId: selectedPackageId });
paywall.purchaseStarted({ packageId: selectedPackageId });
paywall.purchaseSuccess({ packageId: selectedPackageId });
paywall.purchaseFailed({ packageId: selectedPackageId, error_message: message });
paywall.purchaseCancel({ packageId: selectedPackageId });
paywall.skip({ packageId: selectedPackageId });
```

Rules:

- Do not emit paywall/purchase milestones via generic `track(...)`/`trackEvent(...)` in hosted paywall screens.
- Do not treat `screen(...)` as replacement for `paywall:shown`.
- If multiple paywall screens exist, each screen/context needs its own stable tracker defaults.

## Anti-Patterns

Do not generate by default:

- `mapEventToCanonical(...)` with many branches
- giant generic `trackEvent(...)` indirection for all product events
- per-call `try/catch` wrappers around every SDK call
- `Promise<AnalyticsClient | null>` bootstrap patterns
- `platform: 'react-native'` (use canonical `ios`/`android`/`mac`/`windows`/`web` or omit)
- explicit `endpoint` in host app code
- creating `createPaywallTracker(...)` inside every paywall callback/event helper
- `apiKey` fallback chains using `*WRITE_KEY*` env vars in host-app code
- duplicate screen tracking from both parent layout and child screen for the same route change
- touching onboarding/paywall/purchase instrumentation while keeping legacy alias/custom event names
- hosted paywall screens that only emit `screen(...)`/`trackScreenView(...)` and never emit `paywall:shown`
- purchase lifecycle emitted via generic `track(...)` instead of tracker callbacks when stable paywall context is available
- onboarding step/survey milestones emitted via generic `track(...)`/`trackEvent(...)` instead of dedicated onboarding APIs
- dual-write to legacy providers or legacy milestone names
