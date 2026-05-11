# Onboarding And Paywall Contract

AnalyticsCLI has strong support for onboarding and paywall funnel analytics, but that only works reliably if instrumentation follows a strict event contract.

Credential source reminder:
- Get publishable ingest API key and optional CLI `readonly_token` from project **API Keys** in [dash.analyticscli.com](https://dash.analyticscli.com).
- Optional for CLI verification: set a default project once with `analyticscli projects select` (arrow-key picker), or pass `--project <project_id>` per command.

## Use The SDK Wrappers

Prefer these helpers over ad-hoc strings:

- `trackOnboardingEvent(...)`
- `createOnboardingTracker(...)`
- `createPaywallTracker(...)`
- `trackPaywallEvent(...)`
- `trackOnboardingSurveyResponse(...)`

Available constants:

- `ONBOARDING_EVENTS`
- `PAYWALL_EVENTS`
- `PURCHASE_EVENTS`
- `ONBOARDING_SURVEY_EVENTS`

## Host App Shape

Use a thin host integration:

- one SDK bootstrap (`init({ ... })`)
- direct tracker/event calls in feature code
- minimal shared helpers only when multiple call sites truly reuse the same payload shape

Avoid:

- giant event translation files
- keeping old event aliases forever
- generic `trackEvent(...)` proxies that hide canonical SDK APIs

Onboarding/survey rule for touched flows:

- Use dedicated onboarding APIs (`createOnboardingTracker(...)`, `trackOnboardingEvent(...)`, `trackOnboardingSurveyResponse(...)`) instead of generic `track(...)` / `trackEvent(...)`.
- For step milestones, prefer tracker step helpers (`step(...).view()`, `step(...).complete()`, `step(...).surveyResponse(...)`).
- For survey responses in repeated flows, prefer one tracker with shared defaults and call `step(...).surveyResponse(...)` with only survey-specific fields.

## No-Legacy Policy

For pre-production integrations:

- use canonical AnalyticsCLI events only for touched onboarding/paywall/purchase flows
- do not keep legacy aliases or fallback event names
- do not dual-write to old names/providers

## Core Onboarding Events

| Event | When to send | Required properties |
| --- | --- | --- |
| `onboarding:start` | User starts onboarding flow | `onboardingFlowId`, `onboardingFlowVersion`, `isNewUser` |
| `onboarding:step_view` | A distinct onboarding step becomes visible | flow props plus `stepKey`, `stepIndex`, `stepCount` |
| `onboarding:step_complete` | Optional: user completes a step action | flow props plus `stepKey`, `stepIndex`, `stepCount` |
| `onboarding:complete` | Onboarding ends successfully | flow props |
| `onboarding:skip` | User exits or skips onboarding | flow props |
| `onboarding:survey_response` | Survey answer captured | `surveyKey`, `questionKey`, `answerType`, `responseKey`, plus flow props |

For low-noise onboarding funnels, you can keep `onboarding:step_view` and omit
`onboarding:step_complete` where completion semantics are weak.
For survey steps, a lean default is `onboarding:step_view` + `onboarding:survey_response`;
add `onboarding:step_complete` only when there is a real completion boundary (explicit submit/continue confirmation or async success).

## Required Paywall And Purchase Events

| Event | When to send | Required properties |
| --- | --- | --- |
| `paywall:shown` | Paywall is visible | `source`, `paywallId`, `fromScreen` |
| `paywall:skip` | User dismisses or skips paywall | `source`, `paywallId` |
| `purchase:started` | Purchase flow started | `source`, `paywallId`, `packageId` |
| `purchase:success` | Purchase succeeded | `source`, `paywallId`, `packageId` |
| `purchase:failed` | Purchase failed | `source`, `paywallId`, `packageId` |
| `purchase:cancel` | In-app purchase cancel intent detected | `source`, `paywallId`, `packageId` |

If exposed by your paywall provider, include `offering` in tracker defaults:
- RevenueCat: offering identifier
- Adapty: paywall/placement identifier
- Superwall: placement/paywall identifier

## Duplicate Tracking Prevention

- SDK built-in dedupe includes `onboarding:step_view` (`dedupeOnboardingStepViewsPerSession: true`, default).
- Emitting a new `onboarding:start` in the same session resets onboarding step-view dedupe state.
- SDK also dedupes immediate duplicate `screen:*` events (`dedupeScreenViewsPerSession: true`, default).
- SDK additionally dedupes immediate overlap between onboarding `screen:*` and `onboarding:step_view` for the same step (`dedupeOnboardingScreenStepViewOverlapsPerSession: true`, default).
- `screenViewDedupeWindowMs` controls both screen dedupe and onboarding screen/step overlap dedupe (default `1200` ms).
- SDK does not automatically dedupe paywall or purchase events.
- Assign a single owner for each funnel boundary (route-level or component-level, not both).
- Do not track the same screen transition from both parent layout and child screen hooks.
- For each paywall attempt, emit one `paywall:shown`.
- For each purchase attempt, emit one `purchase:started` and exactly one terminal event:
  - `purchase:cancel`
  - `purchase:failed`
  - `purchase:success`
- Use `createPaywallTracker(...)` so events share one `paywallEntryId`; this improves correlation and duplicate detection in analysis, but it does not dedupe automatically.
- Reuse a single `createPaywallTracker(...)` instance for one stable paywall flow context. Do not recreate a tracker for every event callback.
- Include provider offering/paywall identifier as `offering` in tracker defaults when available.
- If multiple callbacks can fire during re-render/re-mount, gate emissions with a session-local idempotency key.

## Hosted Paywall Screens (Mandatory Mapping)

For hosted paywall providers (RevenueCat UI, Adapty UI, Superwall UI) and custom host wrappers:

- Do not rely on `screen(...)`/`trackScreenView(...)` as replacement for paywall milestones.
- Create one `createPaywallTracker(...)` instance per stable screen/context (`source`, `paywallId`, optional `offering`).
- Route lifecycle callbacks to canonical tracker calls:
  - shown/visible callback -> `paywallTracker.shown(...)`
  - purchase started callback -> `paywallTracker.purchaseStarted(...)`
  - purchase success callback -> `paywallTracker.purchaseSuccess(...)`
  - purchase cancelled callback -> `paywallTracker.purchaseCancel(...)`
  - purchase failure callback -> `paywallTracker.purchaseFailed(...)`
  - close/back/dismiss callback -> `paywallTracker.skip(...)`
- If the app has multiple paywall screens, each screen needs its own stable tracker defaults.
- Avoid generic `trackEvent('purchase_*')` / `track('paywall:*')` wrappers for hosted paywall lifecycle when tracker context is available.
- In RevenueCat callbacks, prefer provider-native identifiers for correlation:
  - `packageId` from `packageBeingPurchased.identifier`
  - `productId` from `packageBeingPurchased.product.identifier`
  - `offering` from RevenueCat offering identifier in tracker defaults

## Screen View Coverage

Track screen views for all funnel-relevant screens:

- onboarding steps and onboarding completion/skip screens
- paywall screen
- purchase result and restore result screens
- core feature entry screens (where value creation starts)

Recommended approach:

- Prefer `analytics.screen('<screen_name>', props)` for new integrations.
- In React Native / Expo non-onboarding screens, prefer `useFocusEffect(...)` to call `analytics.screen(...)` on focus.
- Include stable fields: `screen_name`, `screen_class`, `source`, `platform`.
- Prefer app-level `init({ appVersion })` once; avoid sending `appVersion` repeatedly in event properties.
- Prefer direct canonical calls (`trackPaywallEvent`, tracker methods) at call sites over generic `trackEvent(...)` proxy layers.

Example (React Native / Expo non-onboarding screen):

```ts
import { useFocusEffect } from '@react-navigation/native';
import { useCallback } from 'react';
import { analytics } from '@/utils/analytics';

export function SettingsScreen() {
  useFocusEffect(
    useCallback(() => {
      analytics.screen('settings', {
        screen_class: 'SettingsScreen',
        source: 'tabs',
      });
    }, []),
  );
}
```

## Important Product Action Events

Beyond funnel milestones, add events for high-value functionality that signals activation or retained usage.

| Event | When to send | Suggested properties |
| --- | --- | --- |
| `activation:first_value` | First successful core value action | `source`, `appVersion`, `platform` |
| `calibration:completed` | Calibration finished successfully | `method`, `referenceWidthMm`, `appVersion` |
| `result:generated` | Ring size result computed | `inputMode`, `region`, `appVersion` |
| `result:shared` | Result shared/exported | `channel`, `source`, `appVersion` |
| `restore:started` | Restore purchases initiated | `source`, `appVersion` |
| `restore:completed` | Restore flow completed | `source`, `restoredEntitlements`, `appVersion` |
| `restore:failed` | Restore flow failed | `source`, `errorCode`, `appVersion` |

## RevenueCat Lifecycle Correlation

For RevenueCat-powered apps, split analytics into two complementary layers:

1. **Client journey events** via SDK tracker methods (`paywall:*`, `purchase:*`) for in-app intent.
2. **Server lifecycle events** from RevenueCat webhooks for subscription truth (trial start/cancel, renewal, churn).

Identity and correlation rules:

- Use one stable user id across both systems (`RevenueCat appUserID` == AnalyticsCLI `setUser(...)` id).
- Keep `offering`, `paywallId`, `packageId`, and `entitlementKey` on paywall/purchase events.
- For webhook-derived events, include RevenueCat payload identifiers (event id/type + transaction/subscription identifiers) so retries can be deduped and timelines can be joined.

Suggested webhook-derived event names:

- `billing:trial_started`
- `billing:trial_cancelled`
- `billing:trial_converted`
- `billing:subscription_renewed`
- `billing:subscription_cancelled`
- `billing:subscription_expired`
- `billing:billing_issue`

Important limitation:

- "Perfect real-time sync" is not guaranteed (store delays, offline clients, webhook retries).
- Design for eventual consistency and idempotent ingestion to get reliable analytics.

## Order Rules

Onboarding:

1. `onboarding:start`
2. `onboarding:complete` or `onboarding:skip`

Paywall journey:

1. `paywall:shown`
2. `purchase:started` optionally
3. `paywall:skip` or `purchase:success` or `purchase:failed`

## Example

```ts
const onboarding = analytics.createOnboardingTracker({
  isNewUser: true,
  onboardingFlowId: 'onboarding_v4',
  onboardingFlowVersion: '4.0.0',
  stepCount: 5,
  surveyKey: 'onboarding_v4',
});
const paywall = analytics.createPaywallTracker({
  source: 'onboarding',
  paywallId: 'default_paywall',
  offering: 'rc_main', // RevenueCat example
});
const welcomeStep = onboarding.step('welcome', 0);

onboarding.start();
welcomeStep.view();
welcomeStep.surveyResponse({
  questionKey: 'primary_goal',
  answerType: 'single_choice',
  responseKey: 'increase_revenue',
});

paywall.shown({
  fromScreen: 'onboarding_offer',
});

paywall.purchaseSuccess({
  packageId: 'annual',
});
```

## Common Mistakes

- non-canonical names for core paywall or purchase milestones
- legacy aliases/custom names left in touched onboarding/paywall/purchase milestones
- onboarding step/survey milestones emitted via generic `track(...)` / `trackEvent(...)` while dedicated onboarding APIs are available
- missing `onboardingFlowId` or `onboardingFlowVersion`
- missing `paywallId` or `source`
- omitting `offering` although the paywall provider exposes an offering/paywall id
- creating a new `createPaywallTracker(...)` instance for every paywall event call
- mixing screen-view semantics with funnel milestones
- instrumenting only onboarding/paywall while skipping core product value events
- dual-write to old analytics providers/events
