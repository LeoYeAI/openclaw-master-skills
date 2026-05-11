---
name: cypress-agent-skill
description: Production-grade Cypress E2E and component testing — selectors, network stubbing, auth, CI parallelization, flake elimination, Page Object Model, and TypeScript support. The complete Cypress skill for AI agents.
user-invocable: true
metadata: {"openclaw":{"emoji":"🧪","requires":{"anyBins":["cypress","npx"]},"install":[{"id":"npm","kind":"node","package":"cypress","label":"Install Cypress (npm)"}]}}
---

# Cypress Expert Skill

## Quick Reference

**When to use this skill:**
- Writing or fixing Cypress E2E or component tests
- Setting up Cypress in a new project
- Debugging flaky tests
- Adding network stubbing / API mocking
- Configuring CI pipelines for Cypress
- Implementing auth patterns (`cy.session`)
- Building Page Object Model architecture

**Quick start:**
1. `npm install --save-dev cypress` — install
2. `npx cypress open` — interactive mode (first run generates config)
3. `npx cypress run` — headless CI mode
4. Read full references in `{baseDir}/references/` for deep patterns

---

## Core Philosophy

Cypress runs **inside the browser**. It has native access to the DOM, network requests, and application state. Every command is automatically retried until it passes or times out. This means:

- **Never use `cy.wait(3000)`** — use aliases + `cy.wait('@alias')` instead
- **Never query DOM immediately after an action** — Cypress retries automatically
- **Always assert on outcomes, not implementation** — test user-visible behavior
- **Use `data-testid` attributes** — decouple tests from styling/structure

---

## 1. Installation & Configuration

### Install

```bash
npm install --save-dev cypress
# or
yarn add -D cypress
# or
pnpm add -D cypress
```

### cypress.config.js (JavaScript)

```js
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 8000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    retries: {
      runMode: 2,
      openMode: 0,
    },
    // v15.10.0+ — enforce new cy.env() / Cypress.expose() APIs
    // set after migrating all Cypress.env() calls
    allowCypressEnv: false,
    // v15.x — faster visibility checks
    experimentalFastVisibility: true,
    // v15.9.0+ — run all specs without --parallel flag; now works for component tests too
    experimentalRunAllSpecs: true,
    setupNodeEvents(on, config) {
      return config
    },
  },
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
    experimentalRunAllSpecs: true,
  },
})
```

### cypress.config.ts (TypeScript)

```ts
import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: 'cypress/e2e/**/*.cy.ts',
    setupNodeEvents(on, config) {
      return config
    },
  },
})
```

### tsconfig for Cypress

```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["es5", "dom"],
    "types": ["cypress", "node"]
  },
  "include": ["**/*.ts"]
}
```

---

## 2. Selectors (Stability Hierarchy)

Use the most stable selector available. Prefer in this order:

```js
// ✅ BEST — semantic, decoupled from style/structure
cy.get('[data-testid="submit-button"]')
cy.get('[data-cy="login-form"]')
cy.get('[data-test="user-email"]')

// ✅ GOOD — ARIA/accessibility selectors
cy.get('[role="dialog"]')
cy.get('[aria-label="Close modal"]')
cy.get('button[type="submit"]')

// ✅ GOOD — cy.contains for text-driven queries
cy.contains('button', 'Submit')
cy.contains('[data-testid="nav"]', 'Dashboard')

// ⚠️ FRAGILE — CSS classes tied to styling
cy.get('.btn-primary')         // avoid
cy.get('.MuiButton-root')      // avoid

// ❌ WORST — absolute XPath / positional
cy.get('div > ul > li:nth-child(3) > a')  // never
```

### Scoped Queries

```js
cy.get('[data-testid="user-card"]').within(() => {
  cy.get('[data-testid="user-name"]').should('contain', 'Alice')
  cy.get('[data-testid="user-role"]').should('contain', 'Admin')
})

cy.get('table').find('tr').should('have.length', 5)
```

---

## 3. Assertions

### Should / Expect

```js
// Chainable assertions
cy.get('[data-testid="title"]').should('be.visible')
cy.get('[data-testid="title"]').should('have.text', 'Dashboard')
cy.get('[data-testid="title"]').should('contain.text', 'Dash')

// Multiple assertions (all retry together)
cy.get('[data-testid="btn"]')
  .should('be.visible')
  .and('not.be.disabled')
  .and('have.attr', 'type', 'submit')

// Value
cy.get('input[name="email"]').should('have.value', 'user@example.com')

// Length assertions
cy.get('[data-testid="item"]').should('have.length', 3)
cy.get('[data-testid="item"]').should('have.length.greaterThan', 0)

// Negative assertions (use carefully — can pass too early)
cy.get('[data-testid="error"]').should('not.exist')
cy.get('[data-testid="spinner"]').should('not.be.visible')

// BDD expect style
cy.get('[data-testid="count"]').invoke('text').then((text) => {
  expect(parseInt(text)).to.be.greaterThan(0)
})

// URL assertions
cy.url().should('include', '/dashboard')
cy.url().should('eq', 'http://localhost:3000/dashboard')

// Alias + should
cy.get('[data-testid="price"]').invoke('text').as('price')
cy.get('@price').should('match', /\$\d+\.\d{2}/)
```

### Async State Assertions

```js
// Wait for element to appear (retries automatically)
cy.get('[data-testid="success-message"]', { timeout: 10000 })
  .should('be.visible')

// Wait for element to disappear
cy.get('[data-testid="loading-spinner"]').should('not.exist')
```

---

## 4. Network Stubbing with cy.intercept

```js
// Basic stub
cy.intercept('GET', '/api/users', {
  statusCode: 200,
  body: [
    { id: 1, name: 'Alice', role: 'admin' },
    { id: 2, name: 'Bob', role: 'user' },
  ],
}).as('getUsers')

cy.visit('/users')
cy.wait('@getUsers')
cy.get('[data-testid="user-row"]').should('have.length', 2)

// Fixture file
cy.intercept('GET', '/api/users', { fixture: 'users.json' }).as('getUsers')

// Glob/regex patterns
cy.intercept('GET', '/api/users/*').as('getUser')
cy.intercept('GET', /\/api\/products\/\d+/).as('getProduct')

// Dynamic handler
cy.intercept('POST', '/api/orders', (req) => {
  req.reply({ statusCode: 201, body: { id: 999, ...req.body } })
}).as('createOrder')

// Modify real server response (spy + transform)
cy.intercept('GET', '/api/config', (req) => {
  req.reply((res) => {
    res.body.featureFlag = true
    return res
  })
}).as('getConfig')

// Error simulation
cy.intercept('GET', '/api/critical', { forceNetworkError: true }).as('networkError')
cy.intercept('GET', '/api/data', { statusCode: 500, body: { error: 'Server Error' } }).as('serverError')

// Delay (for loading state tests)
cy.intercept('GET', '/api/data', (req) => {
  req.reply({ delay: 1000, body: { data: [] } })
}).as('slowRequest')

// Assert request details
cy.wait('@createOrder').then((interception) => {
  expect(interception.request.body).to.deep.include({ quantity: 2 })
  expect(interception.response.statusCode).to.equal(201)
})
```

---

## 5. Authentication Patterns

### cy.session — Cache Auth State (Recommended)

```js
Cypress.Commands.add('loginByUI', (email, password) => {
  cy.session(
    [email, password],
    () => {
      cy.visit('/login')
      cy.get('[data-testid="email"]').type(email)
      cy.get('[data-testid="password"]').type(password)
      cy.get('[data-testid="submit"]').click()
      cy.url().should('include', '/dashboard')
    },
    {
      validate() {
        cy.getCookie('session_token').should('exist')
      },
      cacheAcrossSpecs: true,
    }
  )
})
```

### API-Based Auth (Faster)

```js
Cypress.Commands.add('loginByApi', (email, password) => {
  cy.session(
    ['api', email, password],
    () => {
      cy.request({
        method: 'POST',
        url: '/api/auth/login',
        body: { email, password },
      }).then(({ body }) => {
        window.localStorage.setItem('auth_token', body.token)
        cy.setCookie('session', body.sessionId)
      })
    },
    {
      validate() {
        cy.window().its('localStorage').invoke('getItem', 'auth_token').should('exist')
      },
    }
  )
})

// Usage — cy.env() for secrets (v15.10.0+, replaces deprecated Cypress.env())
beforeEach(() => {
  cy.env(['adminPassword']).then(({ adminPassword }) => {
    cy.loginByApi('admin@example.com', adminPassword)
    cy.visit('/dashboard')
  })
})
```

---

## 6. Custom Commands

```js
// cypress/support/commands.js
Cypress.Commands.add('getByTestId', (testId, options) => {
  return cy.get(`[data-testid="${testId}"]`, options)
})

Cypress.Commands.add('waitForToast', (message) => {
  const selector = '[data-testid="toast"], [role="status"]'
  if (message) {
    cy.get(selector, { timeout: 10000 }).should('contain', message)
  } else {
    cy.get(selector, { timeout: 10000 }).should('be.visible')
  }
})

Cypress.Commands.add('fillForm', (data) => {
  Object.entries(data).forEach(([field, value]) => {
    cy.get(`[name="${field}"]`).clear().type(String(value))
  })
})

// TypeScript — cypress/support/index.d.ts
declare global {
  namespace Cypress {
    interface Chainable {
      getByTestId(testId: string, options?: Partial<Loggable & Timeoutable>): Chainable<JQuery>
      loginByApi(email: string, password: string): Chainable<void>
      loginByUI(email: string, password: string): Chainable<void>
      waitForToast(message?: string): Chainable<void>
      fillForm(data: Record<string, string | number>): Chainable<void>
    }
  }
}
```

---

## 7. Page Object Model

```js
// cypress/pages/LoginPage.js
class LoginPage {
  visit() { cy.visit('/login'); return this }
  getEmailInput() { return cy.get('[data-testid="email-input"]') }
  getPasswordInput() { return cy.get('[data-testid="password-input"]') }
  getSubmitButton() { return cy.get('[data-testid="submit-button"]') }
  getErrorMessage() { return cy.get('[data-testid="error-message"]') }

  login(email, password) {
    this.getEmailInput().clear().type(email)
    this.getPasswordInput().clear().type(password)
    this.getSubmitButton().click()
    return this
  }

  assertLoggedIn() { cy.url().should('include', '/dashboard'); return this }
  assertError(message) { this.getErrorMessage().should('contain', message); return this }
}

export default new LoginPage()

// Usage
import loginPage from '../pages/LoginPage'

it('logs in successfully', () => {
  loginPage.visit().login('admin@example.com', 'password123').assertLoggedIn()
})
```

---

## 8. Component Testing

```js
// cypress/component/Button.cy.jsx
import { mount } from 'cypress/react'
import Button from '../../src/components/Button'

describe('Button', () => {
  it('calls onClick when clicked', () => {
    const onClick = cy.stub().as('clickHandler')
    mount(<Button label="Submit" onClick={onClick} />)
    cy.get('button').click()
    cy.get('@clickHandler').should('have.been.calledOnce')
  })

  it('is disabled when loading', () => {
    mount(<Button label="Submit" loading={true} />)
    cy.get('button').should('be.disabled')
  })
})

// Run component tests
// npx cypress open --component
// npx cypress run --component
```

---

## 9. Common Patterns

```js
// Forms
cy.get('input[name="email"]').clear().type('new@example.com')
cy.get('select[name="country"]').select('United States')
cy.get('[data-testid="agree"]').check()
cy.get('[data-testid="file-input"]').selectFile('cypress/fixtures/doc.pdf')

// File drag & drop
cy.get('[data-testid="drop-zone"]').selectFile('cypress/fixtures/image.png', {
  action: 'drag-drop',
})

// Modal handling
cy.get('[data-testid="open-modal"]').click()
cy.get('[role="dialog"]').should('be.visible')
cy.get('[role="dialog"]').within(() => {
  cy.get('[data-testid="confirm-btn"]').click()
})
cy.get('[role="dialog"]').should('not.exist')

// Window alerts
cy.on('window:alert', (text) => { expect(text).to.contain('Success') })
cy.on('window:confirm', () => true)

// LocalStorage / Cookies
cy.window().then((win) => { win.localStorage.setItem('key', 'value') })
cy.setCookie('session', 'abc123')
cy.clearAllCookies()
cy.clearAllLocalStorage()

// Date/Time control
cy.clock(new Date('2024-03-15'))
cy.tick(25 * 60 * 1000)  // advance 25 minutes

// Spy on methods
cy.visit('/checkout', {
  onBeforeLoad(win) { cy.spy(win.analytics, 'track').as('track') },
})
cy.get('@track').should('have.been.calledWith', 'Purchase Completed')
```

---

## 10. Flake Prevention

```js
// ❌ FLAKY
cy.wait(2000)
cy.get('[data-testid="result"]').should('exist')

// ✅ STABLE — wait for network alias
cy.intercept('GET', '/api/results').as('getResults')
cy.get('[data-testid="search-btn"]').click()
cy.wait('@getResults')
cy.get('[data-testid="result"]').should('have.length.greaterThan', 0)

// Test isolation — reset state between tests
beforeEach(() => {
  cy.clearAllCookies()
  cy.clearAllLocalStorage()
  cy.clearAllSessionStorage()
})

// Retries config
retries: { runMode: 2, openMode: 0 }

// Per-test retry
it('critical path', { retries: 3 }, () => { ... })
```

---

## 11. CI / Parallelization

### GitHub Actions (Parallel Matrix)

```yaml
name: Cypress Tests
on: [push, pull_request]

jobs:
  cypress-run:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        containers: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: 'npm' }
      - run: npm ci
      - run: npm start &
      - run: npx wait-on http://localhost:3000 --timeout 60000
      - uses: cypress-io/github-action@v6
        with:
          record: true
          parallel: true
          group: 'UI Tests'
          tag: ${{ github.ref_name }}
        env:
          CYPRESS_RECORD_KEY: ${{ secrets.CYPRESS_RECORD_KEY }}
          CYPRESS_ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}   # accessed via cy.env()
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: cypress-screenshots
          path: cypress/screenshots
```

### New CLI flags (v15.11.0)

```bash
# Don't fail the run when no tests are found (useful for conditional spec discovery)
npx cypress run --pass-with-no-tests

# Run component tests with experimentalRunAllSpecs (now works for component testing too, v15.9.0+)
npx cypress run --component
```

### Smoke Test Tags

```js
// Run subset of tests in CI
const isSmoke = Cypress.expose('SMOKE') === 'true'
;(isSmoke ? describe.only : describe)('Checkout', () => { ... })
// Run: CYPRESS_SMOKE=true npx cypress run
```

### Docker Compose for CI

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
  cypress:
    image: cypress/included:15.11.0   # updated from 13.x
    depends_on:
      - app
    environment:
      - CYPRESS_baseUrl=http://app:3000
      - CYPRESS_ADMIN_PASSWORD=${ADMIN_PASSWORD}   # passed via cy.env()
    volumes:
      - ./:/e2e
    working_dir: /e2e
    command: cypress run --browser chrome
```

---

## 12. Environment Variables

> ⚠️ **Breaking change in v15.10.0:** `Cypress.env()` is deprecated and will be removed in Cypress 16.  
> Migrate to `cy.env()` for secrets and `Cypress.expose()` for public config values.

### New API (v15.10.0+)

```js
// cy.env() — for SECRETS (API keys, passwords, tokens)
// Async, only exposes the values you explicitly request
// Values are NOT serialized into browser state
cy.env(['apiKey', 'adminPassword']).then(({ apiKey, adminPassword }) => {
  cy.request({
    method: 'POST',
    url: '/api/auth/login',
    body: { email: 'admin@test.com', password: adminPassword },
    headers: { Authorization: `Bearer ${apiKey}` },
  })
})

// Cypress.expose() — for NON-SENSITIVE public config
// Synchronous, safe to appear in browser state
// Use for: feature flags, API versions, env labels, base URLs
const apiUrl = Cypress.expose('apiUrl')
cy.visit(apiUrl + '/dashboard')
```

### cypress.config.js (v15.10.0+)

```js
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  // Enforce migration — disables legacy Cypress.env() API entirely
  allowCypressEnv: false,

  env: {
    apiUrl: 'http://localhost:3001',       // non-sensitive — use Cypress.expose()
    adminEmail: 'admin@test.com',          // non-sensitive — use Cypress.expose()
    // secrets (apiKey, adminPassword) come from cypress.env.json or CYPRESS_* OS vars
    // never hardcode secrets here
  },
})
```

### cypress.env.json — secrets only (gitignore this file)

```json
{
  "adminPassword": "secret123",
  "apiKey": "test-key"
}
```

### CI environment variables (prefix CYPRESS\_)

```bash
# Set secrets as CI env vars — accessed via cy.env()
CYPRESS_API_KEY=abc123 npx cypress run
CYPRESS_ADMIN_PASSWORD=secret npx cypress run
```

### Migration cheatsheet

| Old (deprecated) | New | When |
|---|---|---|
| `Cypress.env('apiKey')` | `cy.env(['apiKey']).then(...)` | Secrets, inside hooks/tests |
| `Cypress.env('apiUrl')` | `Cypress.expose('apiUrl')` | Public config, synchronous access needed |
| `Cypress.env()` (all) | Never use — intentional explicit access only | — |

### Plugin migration note

Popular plugins require updates to drop `Cypress.env()`:
- `@cypress/grep` → upgrade to latest major
- `@cypress/code-coverage` → upgrade to latest major
- Review all custom plugins for `Cypress.env()` usage before setting `allowCypressEnv: false`

---

## 13. Fixtures and Data Management

```js
// cypress/fixtures/user.json
{
  "id": 1,
  "name": "Test User",
  "email": "test@example.com",
  "role": "admin"
}

// Load fixture
cy.fixture('user.json').then((user) => {
  cy.get('[data-testid="name"]').should('contain', user.name)
})

// Use fixture as stub (shorthand)
cy.intercept('GET', '/api/user', { fixture: 'user.json' }).as('getUser')

// Dynamic data generation
const generateUser = (overrides = {}) => ({
  id: Math.random(),
  name: 'Test User',
  email: `test+${Date.now()}@example.com`,
  role: 'user',
  ...overrides,
})

cy.intercept('GET', '/api/user', generateUser({ role: 'admin' })).as('getUser')

// Seed DB via API task (faster than UI)
beforeEach(() => {
  cy.request('POST', '/api/test/reset', { scenario: 'clean-slate' })
})
```

---

## 14. Accessibility Testing

```js
// Install: npm install --save-dev cypress-axe axe-core
// Add to cypress/support/e2e.js: import 'cypress-axe'

describe('Accessibility', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.injectAxe()
  })

  it('has no detectable a11y violations on load', () => {
    cy.checkA11y()
  })

  it('has no violations in the modal', () => {
    cy.get('[data-testid="open-modal"]').click()
    cy.get('[role="dialog"]').should('be.visible')
    cy.checkA11y('[role="dialog"]', {
      rules: {
        'color-contrast': { enabled: false },  // disable specific rules
      },
    })
  })

  it('reports violations with details', () => {
    cy.checkA11y(null, null, (violations) => {
      violations.forEach((violation) => {
        cy.log(`${violation.id}: ${violation.description}`)
        violation.nodes.forEach((node) => cy.log(node.html))
      })
    })
  })
})
```

---

## 15. Best Practices Summary

| Pattern | Do | Don't |
|---|---|---|
| Selectors | `data-testid` attributes | CSS classes, XPath |
| Waiting | `cy.wait('@alias')` | `cy.wait(3000)` |
| Auth | `cy.session()` | Login via UI every test |
| Assertions | Chain `.should()` | Implicit `then()` checks |
| Data | API seeding | UI-based test data setup |
| Isolation | `beforeEach` resets | Shared state between tests |
| Network | `cy.intercept()` stubs | Real API calls in unit tests |

---

## 16. Debugging

```js
// Pause execution — opens interactive debugger in Cypress UI
cy.pause()

// Debug current subject — logs to console
cy.get('[data-testid="el"]').debug()

// Log custom messages
cy.log('Current step: submitting checkout form')

// Take screenshot at specific point
cy.screenshot('before-submit')

// Inspect DOM state
cy.get('[data-testid="form"]').then(($el) => {
  console.log('Form HTML:', $el.html())
  debugger  // opens DevTools when running in interactive mode
})

// Time travel debugging: Cypress UI → click any command in the log → DOM snapshot appears
```

### cy.prompt() — Experimental Natural Language Tests (v15.x)

```js
// cy.prompt() lets you write tests in plain English
// Cypress AI interprets intent and generates the necessary commands
// Enable: set experimentalCyPrompt: true in cypress.config.js

cy.prompt('Click the submit button and verify the success message appears')
cy.prompt('Fill in the login form with admin credentials and sign in')
cy.prompt('Verify the product list shows 3 items and the first one is selected')
```

> Enable with: `experimentalCyPrompt: true` in `cypress.config.js`. Self-healing: if a selector changes, Cypress attempts to re-locate the element by intent rather than failing immediately.

---

## References

All detailed references in `{baseDir}/references/`:

- `selectors.md` — Selector strategies and anti-patterns
- `commands.md` — Full cy.* command cheatsheet
- `network.md` — cy.intercept advanced patterns
- `assertions.md` — Complete assertion reference
- `config.md` — Full cypress.config.js options
- `ci.md` — CI/CD setup guides (GitHub Actions, GitLab, CircleCI, Jenkins)
- `component-testing.md` — React/Vue/Angular component testing
- `patterns.md` — Visual regression, API testing, multi-tab, drag/drop

## Examples

Working test files in `{baseDir}/examples/`:

- `auth-flow.cy.js` — Full auth with cy.session
- `api-intercept.cy.js` — Network stubbing patterns
- `page-objects.cy.js` — POM implementation
- `custom-commands.js` — Custom command library