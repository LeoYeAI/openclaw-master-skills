# Frontend Common Issues & Fix Methods (Bug Fixing Catalog)

Goal: Provide a "high-frequency pattern library" for troubleshooting and fixing. Each entry includes: symptom, quick identification, common root causes, fix strategy, verification.

Principles:
- Don't guess; use minimal evidence (logs/breakpoints/network panel/repro cases) to identify root cause.
- Fix should be minimal but complete; avoid only fixing the surface.

## 1) React/Hooks High-Frequency Issues

### 1.1 useEffect Missing Dependencies (or Wrong Dependencies)

- Symptom: Side effects don't update after props/state change; requests use old params; page shows stale data.
- Quick identification:
  - Check if `useEffect(..., [])` reads props/state inside.
  - Check for `eslint-disable-next-line react-hooks/exhaustive-deps` suppression.
- Common root cause: Effect dependency array doesn't match actually read "reactive values", causing closures to capture old values (stale closure).
- Fix strategy:
  - Add real dependencies to the dependency array; or split logic: events use handlers, side effects use effects (avoid mixing).
  - Avoid suppressing the linter to "silence warnings" — this usually buries bugs.
- Verification:
  - Change dependency values (e.g. switch filter conditions/roomId/serverUrl), confirm side effect re-executes as expected.
  - Reproduce old bug scenario + regression on new scenarios.

Official key point (React docs): Don't suppress exhaustive-deps; missing dependencies cause effects to not re-sync when values change.

### 1.2 setInterval / setTimeout Captures Old Values

- Symptom: Timer callback always uses initial value; modifying config has no effect.
- Quick identification: Print relevant variables in interval callback, check if always initial value.
- Common root cause: Timer registered at mount time, closure captures old variables; effect dependencies empty or incomplete.
- Fix strategy:
  - Use functional setState (e.g. `setCount(c => c + delta)`) and ensure dependencies are correct.
  - Or put mutable values in a ref and read current ref value in callback (use cautiously, avoid bypassing reactivity).
- Verification: Dynamically adjust parameters (increment/frequency), behavior changes immediately with no duplicate timers.

### 1.3 StrictMode Dev Environment Double-Invoke Appears as "Duplicate Execution"

- Symptom: Dev environment effect/ref callbacks execute twice; connections/subscriptions duplicated; duplicate requests or resource leaks.
- Quick identification: Only happens in dev + StrictMode; doesn't reproduce in production.
- Common root cause: Side effects lack proper cleanup; old subscriptions/requests not cancelled on dependency change.
- Fix strategy:
  - Disconnect/unsubscribe/clear timers in effect cleanup.
  - Make "create-once side effects" idempotent + cleanup capable.
- Verification: Under StrictMode, resource count doesn't grow after repeated mount/unmount, no duplicate subscriptions.

### 1.4 setState After Component Unmount (Async Callback Writes to Unmounted Component)

- Symptom: Console warning (or potential memory leak); abnormal state after quickly switching pages.
- Quick identification: setState called in async request/subscription callback; component already unmounted.
- Common root cause: Request not cancelled; subscription not unbound; race condition causes late response to overwrite new page state.
- Fix strategy:
  - Use AbortController for fetch; unsubscribe in cleanup; for concurrent requests, "keep only latest".
  - Introduce requestId/sequence: only process the last request's response.
- Verification: Rapidly switching routes/filter conditions no longer produces warnings; data not overwritten by old requests.

### 1.5 Controlled/Uncontrolled Input Switch

- Symptom: Input value jumps unexpectedly; console warns about controlled/uncontrolled switch.
- Quick identification: value changes from undefined to string (or vice versa).
- Root cause: Initial value not set; async fill causes type change.
- Fix strategy: Ensure input is always controlled (value always string), e.g. default empty string; or always uncontrolled (don't pass value).
- Verification: First render/async load/reset form flows all without warnings.

### 1.6 Unstable Key Causes List Reuse Errors

- Symptom: List item input misaligned; expand/collapse state mixed up; animation/focus abnormal.
- Quick identification: Key uses index or random number; sort/insert/delete changes index.
- Root cause: React relies on stable keys for node reuse; unstable keys misassign state.
- Fix strategy: Use stable business ID as key; avoid index as key (unless list never reorders/inserts).
- Verification: After sort/filter/insert/delete, each item's state is still correct.

## 2) Frontend Data Flow/Cache/Race Conditions

### 2.1 Race Condition: Late Response Overwrites

- Symptom: Rapidly switching filter conditions causes results to flash back to old data; loading state abnormal.
- Quick identification: Multiple incomplete requests exist simultaneously; response arrival order differs from initiation order.
- Fix strategy:
  - Cancel old requests (AbortController).
  - Or "only apply latest response" (sequence guard).
- Verification: Rapidly operating UI, final display always corresponds to last input.

### 2.2 Cache Not Invalidated (List/Detail Out of Sync After Mutation)

- Symptom: Add/edit succeeds but list doesn't refresh; detail page and list page state inconsistent.
- Quick identification: Check if mutation success callback triggers refresh/invalidate.
- Fix strategy: Uniformly do invalidation after writes; or have server return latest object and update local cache.
- Verification: After write, all consumer surfaces (list/detail/selector/statistics) are consistent.

### 2.3 Cross-Origin/CORS or Preflight (OPTIONS) Failure

- Symptom: Browser reports CORS error; request blocked in Network; only occurs in online/different-domain environments.
- Quick identification:
  - Check if Network shows OPTIONS sent first; check if response lacks `Access-Control-Allow-*`.
  - Check if custom headers / cookies are sent (triggers preflight or stricter rules).
- Common root cause: Backend doesn't allow origin/method/headers; preflight route not handled; credentials + allow-origin combination incorrect.
- Fix strategy:
  - Have backend properly handle OPTIONS and return allowed headers/methods/origin.
  - If cookies needed: frontend `credentials` pairs with backend `Access-Control-Allow-Credentials`, and allow-origin cannot use `*`.
- Verification: In cross-origin environment, GET/POST both succeed; preflight OPTIONS returns 200/204 with correct headers.

### 2.4 Cookie/SameSite Causes Login Session Loss (Cross-Site/Third-Party Scenarios)

- Symptom: Login lost after refresh; cross-subdomain/cross-site requests don't carry cookie; only reproduces in certain browsers.
- Quick identification: Check if requests carry Cookie in Network; check if response Set-Cookie is rejected by browser (DevTools shows hint).
- Common root cause: SameSite/Domain/Secure config mismatch; cross-site scenario doesn't enable Secure; frontend doesn't use credentials.
- Fix strategy: Set Domain/SameSite/Secure based on deployment topology; cross-site needs SameSite=None + Secure; frontend requests carry credentials.
- Verification: Same-domain/cross-subdomain/cross-site (if applicable) all three paths maintain session consistency.

## 3) UI Rendering & Visibility

### 3.1 Conditional Rendering Omission (Backend Has Field, Frontend Doesn't Display / Wrong Field)

- Symptom: API returns data but UI doesn't display; or different methods/scenarios have wrong display logic.
- Quick identification: Compare API response fields vs UI render components; check if destructured but unused.
- Fix strategy: Add missing render components; use field priority based on scenario (e.g. HTTP method).
- Verification: Do snapshot or minimal manual test matrix for all relevant method/state combinations.

### 3.2 SSR/Hydration Mismatch

- Symptom: Console warns hydration mismatch; first screen flickers; only in SSR scenarios.
- Quick identification: Check if render output depends on `window`/random numbers/local timezone; check if conditional rendering differs between server/client.
- Common root cause: Server and client render results differ; browser-only data read during render phase.
- Fix strategy: Put browser-only logic in effects/client boundary; stabilize or defer rendering for time/random values.
- Verification: SSR page first screen has no hydration warnings; refresh/navigation consistent.

## 4) Minimal Verification Checklist (Frontend)

- Original scenario reproducible → no longer reproduced after fix.
- Rapid consecutive operations (switch routes/filters/popups) have no race condition overwrites.
- No new console error/warn.
- Key use cases: list/detail/selector/form consistency check passes.
