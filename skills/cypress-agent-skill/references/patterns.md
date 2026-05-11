# Advanced Patterns Reference

## Visual Regression Testing

```js
// Install: npm install --save-dev @percy/cypress
// Add to cypress/support/e2e.js: import '@percy/cypress'

describe('Visual Regression', () => {
  it('matches dashboard snapshot', () => {
    cy.intercept('GET', '/api/**', { fixture: 'dashboard-data.json' })
    cy.visit('/dashboard')
    cy.get('[data-testid="dashboard-content"]').should('be.visible')
    cy.percySnapshot('Dashboard - Default View')
  })

  it('matches dark mode snapshot', () => {
    cy.visit('/dashboard?theme=dark')
    cy.percySnapshot('Dashboard - Dark Mode', { widths: [375, 768, 1280] })
  })
})

// Run: PERCY_TOKEN=xxx npx percy exec -- cypress run
```

## API Testing (Without Browser)

```js
// Direct cy.request — no browser needed
describe('API Tests', () => {
  let authToken

  before(() => {
    cy.request('POST', '/api/auth/login', {
      email: Cypress.env('API_USER'),
      password: Cypress.env('API_PASS'),
    }).then(({ body }) => {
      authToken = body.token
    })
  })

  it('GET /api/users returns paginated list', () => {
    cy.request({
      method: 'GET',
      url: '/api/users?page=1&limit=10',
      headers: { Authorization: `Bearer ${authToken}` },
    }).then(({ status, body, headers }) => {
      expect(status).to.equal(200)
      expect(body.data).to.have.length(10)
      expect(body.meta.total).to.be.a('number')
      expect(headers['content-type']).to.include('application/json')
    })
  })

  it('POST /api/users creates a user', () => {
    const newUser = {
      name: 'Test User',
      email: `test+${Date.now()}@example.com`,
      role: 'user',
    }

    cy.request({
      method: 'POST',
      url: '/api/users',
      headers: { Authorization: `Bearer ${authToken}` },
      body: newUser,
    }).then(({ status, body }) => {
      expect(status).to.equal(201)
      expect(body.id).to.exist
      expect(body.email).to.equal(newUser.email)
    })
  })

  it('validates required fields', () => {
    cy.request({
      method: 'POST',
      url: '/api/users',
      headers: { Authorization: `Bearer ${authToken}` },
      body: { name: 'No Email' },
      failOnStatusCode: false,  // don't throw on 4xx
    }).then(({ status, body }) => {
      expect(status).to.equal(422)
      expect(body.errors).to.have.property('email')
    })
  })
})
```

## Multi-Tab / New Window Handling

```js
// Cypress doesn't support multiple tabs natively
// Best approach: remove target="_blank" attribute
it('opens link in same window', () => {
  cy.get('[data-testid="external-link"]')
    .invoke('removeAttr', 'target')
    .click()
  cy.url().should('include', 'expected-destination')
})

// Capture new window URL via cy.stub on window.open
it('calls window.open with correct URL', () => {
  cy.window().then((win) => {
    cy.stub(win, 'open').as('windowOpen')
  })
  cy.get('[data-testid="share-btn"]').click()
  cy.get('@windowOpen').should('be.calledWithMatch', /expected-url/)
})
```

## Clipboard Testing

```js
it('copies text to clipboard', () => {
  cy.window().then((win) => {
    cy.stub(win.navigator.clipboard, 'writeText').resolves().as('clipboard')
  })
  cy.get('[data-testid="copy-btn"]').click()
  cy.get('@clipboard').should('have.been.calledWith', 'Expected copied text')
  cy.get('[data-testid="copy-success"]').should('be.visible')
})
```

## Drag and Drop

```js
// Using cypress-drag-drop plugin
// npm install --save-dev @4tw/cypress-drag-drop
import '@4tw/cypress-drag-drop'

it('reorders items via drag and drop', () => {
  cy.get('[data-testid="drag-item-1"]').drag('[data-testid="drop-zone-3"]')
  cy.get('[data-testid="item-list"]')
    .children()
    .first()
    .should('contain', 'Item 3')
})

// Native HTML5 drag events
it('drops file on upload zone', () => {
  cy.get('[data-testid="drop-zone"]').selectFile(
    'cypress/fixtures/test-file.pdf',
    { action: 'drag-drop' }
  )
  cy.get('[data-testid="file-name"]').should('contain', 'test-file.pdf')
})
```

## Date/Time Manipulation

```js
// Freeze clock to specific time
it('shows correct date on dashboard', () => {
  const now = new Date('2024-03-15T10:00:00.000Z')
  cy.clock(now)
  cy.visit('/dashboard')
  cy.get('[data-testid="today-date"]').should('contain', 'March 15, 2024')
})

// Tick time forward
it('shows session expiry warning', () => {
  cy.clock()
  cy.visit('/dashboard')
  cy.tick(25 * 60 * 1000)  // advance 25 minutes
  cy.get('[data-testid="session-warning"]').should('be.visible')
})
```

## Spy on Methods

```js
it('tracks analytics events', () => {
  cy.visit('/checkout', {
    onBeforeLoad(win) {
      cy.spy(win.analytics, 'track').as('analyticsTrack')
    },
  })
  cy.get('[data-testid="purchase-btn"]').click()
  cy.get('@analyticsTrack').should('have.been.calledWith', 'Purchase Completed')
  cy.get('@analyticsTrack').should('have.been.calledWithMatch', {
    event: 'Purchase Completed',
    properties: { value: Cypress.sinon.match.number },
  })
})
```

## Scroll and Viewport

```js
// Scroll to element
cy.get('[data-testid="footer"]').scrollIntoView()
cy.get('[data-testid="footer"]').should('be.visible')

// Scroll to position
cy.scrollTo('bottom')
cy.scrollTo(0, 500)

// Test sticky header
cy.scrollTo(0, 300)
cy.get('[data-testid="sticky-header"]').should('have.class', 'sticky')
  .and('be.visible')
```

## Download Testing

```js
// Assert file was downloaded
it('downloads CSV report', () => {
  const downloadsFolder = Cypress.config('downloadsFolder')
  
  // Clear downloads before test
  cy.task('clearDownloads', downloadsFolder)
  
  cy.get('[data-testid="export-csv"]').click()
  
  // Wait for file to appear
  cy.readFile(`${downloadsFolder}/report.csv`, { timeout: 15000 })
    .should('contain', 'Name,Email,Role')
})

// cypress.config.js — register task
setupNodeEvents(on, config) {
  on('task', {
    clearDownloads(downloadsFolder) {
      const fs = require('fs')
      if (fs.existsSync(downloadsFolder)) {
        fs.rmSync(downloadsFolder, { recursive: true })
      }
      fs.mkdirSync(downloadsFolder, { recursive: true })
      return null
    },
  })
}
```

## Testing PWA / Service Workers

```js
// Disable service workers in tests to avoid caching issues
cy.visit('/', {
  onBeforeLoad(win) {
    delete win.navigator.__proto__.serviceWorker
  },
})
```

## Handling Flaky Third-Party Scripts

```js
// Block third-party requests that might cause flakiness
cy.intercept('GET', 'https://analytics.example.com/**', { statusCode: 200 }).as('analytics')
cy.intercept('GET', 'https://chat-widget.com/embed.js', { body: '' }).as('chatWidget')

// Or block by resource type (requires cypress plugin)
cy.visit('/', {
  onBeforeLoad(win) {
    // Stub chatbot initialization
    win.Intercom = cy.stub().as('Intercom')
  },
})
```

## Database Seeding via Tasks

```js
// cypress.config.js
setupNodeEvents(on, config) {
  on('task', {
    async seedDatabase(scenario) {
      const db = require('./db-connection')
      await db.seed(scenario)
      return null
    },
    async resetDatabase() {
      const db = require('./db-connection')
      await db.truncateAll()
      return null
    },
    async queryDatabase(sql) {
      const db = require('./db-connection')
      return db.query(sql)
    },
  })
}

// Usage in tests
beforeEach(() => {
  cy.task('resetDatabase')
  cy.task('seedDatabase', 'standard-users')
})

it('shows seeded users', () => {
  cy.task('queryDatabase', 'SELECT count(*) FROM users').then((result) => {
    const count = result.rows[0].count
    cy.visit('/users')
    cy.get('[data-testid="user-row"]').should('have.length', parseInt(count))
  })
})
```

## TypeScript Full Setup

```bash
# Install types
npm install --save-dev @types/cypress
```

```ts
// cypress/support/e2e.ts
import './commands'

// cypress/support/commands.ts
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>
      getByTestId<T = HTMLElement>(
        testId: string,
        options?: Partial<Loggable & Timeoutable & Withinable & Shadow>
      ): Chainable<JQuery<T>>
    }
  }
}

Cypress.Commands.add('login', (email: string, password: string) => {
  cy.session([email, password], () => {
    cy.visit('/login')
    cy.get('[data-testid="email"]').type(email)
    cy.get('[data-testid="password"]').type(password)
    cy.get('[data-testid="submit"]').click()
    cy.url().should('include', '/dashboard')
  })
})

Cypress.Commands.add('getByTestId', (testId: string, options?) => {
  return cy.get(`[data-testid="${testId}"]`, options)
})
```
