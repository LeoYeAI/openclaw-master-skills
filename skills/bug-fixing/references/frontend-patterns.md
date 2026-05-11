# Frontend Common Issues & Fix Patterns

High-frequency pattern library for troubleshooting and fixing frontend bugs.

**Principles**:
- Don't guess; use minimal evidence (logs/breakpoints/network panel/repro cases)
- Fix should be minimal but complete; avoid only fixing the surface

---

## 1. React/Hooks High-Frequency Issues

### 1.1 useEffect Missing Dependencies

- **Symptom**: Side effects don't update after props/state change; requests use old params; stale data
- **Detection**: Check if `useEffect(..., [])` reads props/state inside. Look for `eslint-disable-next-line react-hooks/exhaustive-deps`
- **Root cause**: Dependency array doesn't match reactive values, causing stale closures
- **Fix**: Add real dependencies; split logic (events use handlers, side effects use effects). Don't suppress linter
- **Verify**: Change dependency values, confirm effect re-executes

### 1.2 setInterval/setTimeout Captures Old Values

- **Symptom**: Timer callback always uses initial value; config changes have no effect
- **Detection**: Print variables in interval callback, check if stuck at initial value
- **Fix**: Use functional setState (`setCount(c => c + delta)`) with correct dependencies. Or use ref for mutable values
- **Verify**: Dynamically adjust parameters, behavior changes immediately

### 1.3 StrictMode Double-Invoke

- **Symptom**: Dev environment effects execute twice; duplicate connections/requests
- **Detection**: Only happens in dev + StrictMode, not in production
- **Fix**: Add proper cleanup in effects (disconnect/unsubscribe/clear timers). Make side effects idempotent
- **Verify**: Under StrictMode, resource count doesn't grow after mount/unmount cycles

### 1.4 setState After Unmount

- **Symptom**: Console warning about setState on unmounted component; state issues on route change
- **Detection**: setState called in async callback after component unmounts
- **Fix**: Use AbortController for fetch; unsubscribe in cleanup; keep-only-latest pattern with requestId
- **Verify**: Rapidly switching routes produces no warnings; data not overwritten

### 1.5 Controlled/Uncontrolled Input Switch

- **Symptom**: Input value jumps; console warns about controlled/uncontrolled switch
- **Detection**: value changes from undefined to string (or vice versa)
- **Fix**: Ensure input is always controlled (default empty string) or always uncontrolled
- **Verify**: First render/async load/reset flows without warnings

### 1.6 Unstable Key Causes List Reuse Errors

- **Symptom**: List item state misaligned; expand/collapse mixed up
- **Detection**: Key uses index or random number; sort/insert/delete changes index
- **Fix**: Use stable business ID as key
- **Verify**: After sort/filter/insert/delete, each item's state is correct

---

## 2. Data Flow / Cache / Race Conditions

### 2.1 Race Condition: Late Response Overwrites

- **Symptom**: Rapidly switching filters causes results to flash back to old data
- **Detection**: Multiple incomplete requests simultaneously; response order differs from initiation
- **Fix**: Cancel old requests (AbortController) or "only apply latest response" (sequence guard)
- **Verify**: Rapidly operating UI, final display matches last input

### 2.2 Cache Not Invalidated

- **Symptom**: Add/edit succeeds but list doesn't refresh; detail and list inconsistent
- **Detection**: Check if mutation callback triggers refresh/invalidate
- **Fix**: Invalidate after writes; or update local cache from server response
- **Verify**: After write, all surfaces (list/detail/selector) are consistent

### 2.3 CORS / Preflight Failure

- **Symptom**: Browser CORS error; request blocked; only in cross-domain environments
- **Detection**: Check if OPTIONS is sent; check response for `Access-Control-Allow-*`
- **Fix**: Backend: handle OPTIONS, return correct headers. Frontend: pair credentials with Allow-Credentials
- **Verify**: Cross-origin GET/POST succeed; OPTIONS returns 200/204

### 2.4 Cookie/SameSite Session Loss

- **Symptom**: Login lost after refresh; cookies not sent cross-site
- **Detection**: Check if requests carry Cookie in Network panel; check Set-Cookie rejection
- **Fix**: Set Domain/SameSite/Secure based on deployment. Cross-site: SameSite=None + Secure
- **Verify**: Same-domain/cross-subdomain/cross-site all maintain session

---

## 3. UI Rendering & Visibility

### 3.1 Conditional Rendering Omission

- **Symptom**: API returns data but UI doesn't display; wrong display for different scenarios
- **Detection**: Compare API response fields vs UI render components
- **Fix**: Add missing render components; use context-aware display logic
- **Verify**: Snapshot or manual test matrix for all method/state combinations

### 3.2 SSR/Hydration Mismatch

- **Symptom**: Console warns hydration mismatch; first screen flickers; SSR only
- **Detection**: Render output depends on window/random/timezone; server/client differ
- **Fix**: Put browser-only logic in effects/client boundary; stabilize time/random
- **Verify**: SSR page has no hydration warnings; refresh consistent

---

## Minimal Verification Checklist (Frontend)

- [ ] Original scenario reproducible, no longer reproduces after fix
- [ ] Rapid consecutive operations (switch routes/filters) have no race condition
- [ ] No new console error/warn
- [ ] Key use cases: list/detail/selector/form consistency check passes
