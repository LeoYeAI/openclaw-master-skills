# Debugging Guide

## Playwright Inspector

```bash
# Run in debug mode
npx playwright test --debug

# Debug specific test
npx playwright test my-test.spec.ts --debug

# Headed mode (see browser)
npx playwright test --headed
```

```typescript
// Pause in test
await page.pause();
```

## Trace Viewer

```bash
# Record trace
npx playwright test --trace on

# View trace file
npx playwright show-trace trace.zip
```

```typescript
// Config for traces
use: {
  trace: 'on-first-retry',  // Only on failures
  trace: 'retain-on-failure',  // Keep failed traces
}
```

## Common Errors

### Element Not Found

```
Error: Timeout 30000ms exceeded waiting for selector
```

**Causes:**
- Element doesn't exist in DOM
- Element is inside iframe
- Element is in shadow DOM
- Page hasn't loaded

**Fixes:**
```typescript
// Wait for element
await page.waitForSelector('.element');

// Check frame context
const frame = page.frameLocator('iframe');
await frame.locator('.element').click();

// Increase timeout
await page.click('.element', { timeout: 60000 });
```

### Flaky Click

```
Error: Element is not visible
Error: Element is outside viewport
```

**Fixes:**
```typescript
// Ensure visible
await page.locator('.btn').waitFor({ state: 'visible' });
await page.locator('.btn').click();

// Scroll into view
await page.locator('.btn').scrollIntoViewIfNeeded();

// Force click (bypass checks)
await page.locator('.btn').click({ force: true });
```

### Timeout in CI

**Causes:**
- Slower CI environment
- Network latency
- Resource constraints

**Fixes:**
```typescript
// Increase global timeout
export default defineConfig({
  timeout: 60000,
  expect: { timeout: 10000 },
});

// Use polling assertions
await expect.poll(async () => {
  return await page.locator('.items').count();
}, { timeout: 30000 }).toBeGreaterThan(5);
```

### Stale Element

```
Error: Element is no longer attached to DOM
```

**Fix:**
```typescript
// Don't store element references
const button = page.locator('.submit');  // This is fine (locator)

// Re-query when needed
await button.click();  // Playwright re-queries automatically
```

### Network Issues

```typescript
// Log all requests
page.on('request', request => {
  console.log('>>', request.method(), request.url());
});

page.on('response', response => {
  console.log('<<', response.status(), response.url());
});

// Wait for specific request
const responsePromise = page.waitForResponse('**/api/data');
await page.click('.load-data');
const response = await responsePromise;
```

## Screenshot Debugging

```typescript
// Take screenshot on failure
test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status !== 'passed') {
    await page.screenshot({
      path: `screenshots/${testInfo.title}.png`,
      fullPage: true,
    });
  }
});
```

## Console Logs

```typescript
// Capture console messages
page.on('console', msg => {
  console.log('PAGE LOG:', msg.text());
});

page.on('pageerror', error => {
  console.log('PAGE ERROR:', error.message);
});
```

## Slow Motion

```typescript
// playwright.config.ts
use: {
  launchOptions: {
    slowMo: 500,  // 500ms delay between actions
  },
}
```

## Compare Local vs CI

| Check | Command |
|-------|---------|
| Viewport | `await page.viewportSize()` |
| User agent | `await page.evaluate(() => navigator.userAgent)` |
| Timezone | `await page.evaluate(() => Intl.DateTimeFormat().resolvedOptions().timeZone)` |
| Network | `page.on('request', ...)` to log all requests |

## Debugging Checklist

1. [ ] Run with `--debug` or `--headed`
2. [ ] Add `await page.pause()` before failure point
3. [ ] Check for iframes/shadow DOM
4. [ ] Verify element exists with `page.locator().count()`
5. [ ] Review trace file in Trace Viewer
6. [ ] Compare screenshots between local and CI
7. [ ] Check console for JS errors
8. [ ] Verify network requests completed
