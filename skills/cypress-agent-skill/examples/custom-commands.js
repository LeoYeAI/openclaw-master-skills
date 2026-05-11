// cypress/support/custom-commands.js
// Drop-in custom command library for Cypress
// Add to cypress/support/e2e.js: import './custom-commands'

// ─── Selectors ───────────────────────────────────────────────────

/** Shorthand for cy.get('[data-testid="..."]') */
Cypress.Commands.add('getByTestId', (testId, options) => {
  return cy.get(`[data-testid="${testId}"]`, options)
})

/** Find by data-cy attribute */
Cypress.Commands.add('getByCy', (selector, options) => {
  return cy.get(`[data-cy="${selector}"]`, options)
})

/** Find by aria-label */
Cypress.Commands.add('getByAriaLabel', (label, options) => {
  return cy.get(`[aria-label="${label}"]`, options)
})

/** Find by role + optional name */
Cypress.Commands.add('getByRole', (role, name, options) => {
  const selector = name
    ? `[role="${role}"][aria-label="${name}"]`
    : `[role="${role}"]`
  return cy.get(selector, options)
})

// ─── Auth ─────────────────────────────────────────────────────────

/**
 * Login via API (fast — skips UI)
 * Caches session between tests
 */
Cypress.Commands.add('loginByApi', (email, password) => {
  const cacheKey = `api:${email}`
  cy.session(
    cacheKey,
    () => {
      cy.request({
        method: 'POST',
        url: `${Cypress.env('apiUrl') || ''}/api/auth/login`,
        body: { email, password },
        failOnStatusCode: true,
      }).then(({ body }) => {
        if (body.token) {
          window.localStorage.setItem('auth_token', body.token)
        }
        if (body.sessionId) {
          cy.setCookie('session_id', body.sessionId)
        }
      })
    },
    {
      validate() {
        cy.window()
          .its('localStorage')
          .invoke('getItem', 'auth_token')
          .should('exist')
      },
      cacheAcrossSpecs: true,
    }
  )
})

/**
 * Login via UI form
 * Caches session — use for testing login flow itself or when API auth isn't available
 */
Cypress.Commands.add('loginByUI', (email, password) => {
  cy.session(
    `ui:${email}`,
    () => {
      cy.visit('/login')
      cy.get('[data-testid="email-input"]').type(email)
      cy.get('[data-testid="password-input"]').type(password, { log: false })
      cy.get('[data-testid="login-button"]').click()
      cy.url().should('not.include', '/login')
    },
    {
      validate() {
        cy.getCookie('session').should('exist')
      },
      cacheAcrossSpecs: true,
    }
  )
})

/** Set auth token directly (for token-based APIs) */
Cypress.Commands.add('setAuthToken', (token) => {
  window.localStorage.setItem('auth_token', token)
  cy.setCookie('auth_token', token)
})

// ─── State Management ─────────────────────────────────────────────

/** Reset all browser state */
Cypress.Commands.add('resetState', () => {
  cy.clearAllCookies()
  cy.clearAllLocalStorage()
  cy.clearAllSessionStorage()
})

/** Seed application via API */
Cypress.Commands.add('seedData', (scenario) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/test/seed`,
    body: { scenario },
    headers: {
      'x-test-secret': Cypress.env('TEST_SECRET'),
    },
  })
})

/** Reset database via API */
Cypress.Commands.add('resetDatabase', () => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/test/reset`,
    headers: {
      'x-test-secret': Cypress.env('TEST_SECRET'),
    },
  })
})

// ─── Network ──────────────────────────────────────────────────────

/** Stub all auth requests to bypass real authentication */
Cypress.Commands.add('stubAuth', (user = {}) => {
  const defaultUser = {
    id: 1,
    name: 'Test User',
    email: 'test@example.com',
    role: 'user',
    ...user,
  }

  cy.intercept('POST', '/api/auth/login', {
    statusCode: 200,
    body: { token: 'fake-token-123', user: defaultUser },
  }).as('stubbedLogin')

  cy.intercept('GET', '/api/auth/me', {
    statusCode: 200,
    body: defaultUser,
  }).as('stubbedMe')

  cy.intercept('POST', '/api/auth/logout', {
    statusCode: 200,
    body: { success: true },
  }).as('stubbedLogout')
})

// ─── Form Helpers ────────────────────────────────────────────────

/** Fill a form from a data object — matches input[name] to keys */
Cypress.Commands.add('fillForm', (data) => {
  Object.entries(data).forEach(([field, value]) => {
    cy.get(`[name="${field}"]`).clear().type(String(value))
  })
})

/** Select a value from a dropdown (by text or value) */
Cypress.Commands.add('selectOption', (selector, value) => {
  cy.get(selector).select(value)
})

/** Upload file to input */
Cypress.Commands.add('uploadFile', (selector, fixturePath, mimeType) => {
  cy.get(selector).selectFile(`cypress/fixtures/${fixturePath}`, {
    mimeType: mimeType || 'application/octet-stream',
  })
})

// ─── Wait Helpers ─────────────────────────────────────────────────

/** Wait for page to fully load (no pending network requests, no spinners) */
Cypress.Commands.add('waitForPageLoad', () => {
  cy.get('[data-testid="loading-spinner"]', { timeout: 15000 }).should('not.exist')
  cy.document().its('readyState').should('eq', 'complete')
})

/** Wait for a toast notification and optionally assert text */
Cypress.Commands.add('waitForToast', (message) => {
  const selector = '[data-testid="toast"], [role="status"], .toast'
  if (message) {
    cy.get(selector, { timeout: 10000 }).should('contain', message)
  } else {
    cy.get(selector, { timeout: 10000 }).should('be.visible')
  }
})

// ─── Assertions ───────────────────────────────────────────────────

/** Assert an element is visible and contains expected text */
Cypress.Commands.add(
  'shouldContainText',
  { prevSubject: 'element' },
  (subject, text) => {
    cy.wrap(subject).should('be.visible').and('contain', text)
  }
)

/** Assert element has no a11y violations */
Cypress.Commands.add('shouldBeAccessible', { prevSubject: 'element' }, (subject) => {
  cy.wrap(subject)
    .should('be.visible')
    .invoke('attr', 'aria-hidden')
    .should('not.equal', 'true')
})

// ─── Screenshot Helpers ───────────────────────────────────────────

/** Take named screenshot at current state */
Cypress.Commands.add('captureState', (name) => {
  cy.screenshot(name, { overwrite: true })
})

// ─── TypeScript Declarations ──────────────────────────────────────
// Save as: cypress/support/index.d.ts
/*
declare global {
  namespace Cypress {
    interface Chainable {
      getByTestId(testId: string, options?: Partial<Loggable & Timeoutable>): Chainable<JQuery>
      getByCy(selector: string, options?: Partial<Loggable & Timeoutable>): Chainable<JQuery>
      getByAriaLabel(label: string, options?: Partial<Loggable & Timeoutable>): Chainable<JQuery>
      getByRole(role: string, name?: string, options?: Partial<Loggable & Timeoutable>): Chainable<JQuery>
      loginByApi(email: string, password: string): Chainable<void>
      loginByUI(email: string, password: string): Chainable<void>
      setAuthToken(token: string): Chainable<void>
      resetState(): Chainable<void>
      seedData(scenario: string): Chainable<void>
      resetDatabase(): Chainable<void>
      stubAuth(user?: Partial<{ id: number; name: string; email: string; role: string }>): Chainable<void>
      fillForm(data: Record<string, string | number>): Chainable<void>
      selectOption(selector: string, value: string): Chainable<void>
      uploadFile(selector: string, fixturePath: string, mimeType?: string): Chainable<void>
      waitForPageLoad(): Chainable<void>
      waitForToast(message?: string): Chainable<void>
      shouldContainText(text: string): Chainable<JQuery>
      shouldBeAccessible(): Chainable<JQuery>
      captureState(name: string): Chainable<void>
    }
  }
}
export {}
*/
