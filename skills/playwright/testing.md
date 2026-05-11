# Testing Patterns

## Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/products');
  });

  test('completes purchase with valid card', async ({ page }) => {
    await page.getByTestId('product-card').first().click();
    await page.getByRole('button', { name: 'Add to Cart' }).click();
    await page.getByRole('link', { name: 'Checkout' }).click();
    
    await expect(page.getByRole('heading', { name: 'Order Summary' })).toBeVisible();
  });
});
```

## Page Object Model

```typescript
// pages/checkout.page.ts
export class CheckoutPage {
  constructor(private page: Page) {}

  readonly cartItems = this.page.getByTestId('cart-item');
  readonly checkoutButton = this.page.getByRole('button', { name: 'Checkout' });
  readonly totalPrice = this.page.getByTestId('total-price');

  async removeItem(name: string) {
    await this.cartItems
      .filter({ hasText: name })
      .getByRole('button', { name: 'Remove' })
      .click();
  }

  async expectTotal(amount: string) {
    await expect(this.totalPrice).toHaveText(amount);
  }
}

// tests/checkout.spec.ts
test('removes item from cart', async ({ page }) => {
  const checkout = new CheckoutPage(page);
  await checkout.removeItem('Product A');
  await checkout.expectTotal('$0.00');
});
```

## Fixtures

```typescript
// fixtures.ts
import { test as base } from '@playwright/test';
import { CheckoutPage } from './pages/checkout.page';

type Fixtures = {
  checkoutPage: CheckoutPage;
};

export const test = base.extend<Fixtures>({
  checkoutPage: async ({ page }, use) => {
    await page.goto('/checkout');
    await use(new CheckoutPage(page));
  },
});
```

## API Mocking

```typescript
test('shows error on API failure', async ({ page }) => {
  await page.route('**/api/checkout', route => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Payment failed' }),
    });
  });

  await page.goto('/checkout');
  await page.getByRole('button', { name: 'Pay' }).click();
  await expect(page.getByText('Payment failed')).toBeVisible();
});
```

## Visual Regression

```typescript
test('matches snapshot', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixels: 100,
  });
});

// Component snapshot
await expect(page.getByTestId('header')).toHaveScreenshot();
```

## Parallelization

```typescript
// playwright.config.ts
export default defineConfig({
  workers: process.env.CI ? 4 : undefined,
  fullyParallel: true,
});

// Per-file control
test.describe.configure({ mode: 'parallel' });
test.describe.configure({ mode: 'serial' });  // dependent tests
```

## Authentication State

```typescript
// Save auth state
await page.context().storageState({ path: 'auth.json' });

// Reuse across tests
test.use({ storageState: 'auth.json' });
```

## Assertions

```typescript
// Visibility
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();
await expect(locator).toBeAttached();

// Content
await expect(locator).toHaveText('Expected');
await expect(locator).toContainText('partial');
await expect(locator).toHaveValue('input value');

// State
await expect(locator).toBeEnabled();
await expect(locator).toBeChecked();
await expect(locator).toHaveAttribute('href', '/path');

// Polling (for async state)
await expect.poll(async () => {
  return await page.evaluate(() => window.dataLoaded);
}).toBe(true);
```
