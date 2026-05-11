# Configuration Reference — cypress.config.js

## Complete Example

```js
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  // ─── Project / Paths ──────────────────────────────────────────
  projectId: 'abc123',                    // Cypress Cloud project ID
  fixturesFolder: 'cypress/fixtures',
  screenshotsFolder: 'cypress/screenshots',
  videosFolder: 'cypress/videos',
  downloadsFolder: 'cypress/downloads',

  // ─── Timeouts ─────────────────────────────────────────────────
  defaultCommandTimeout: 8000,   // cy.get, cy.contains, etc.
  execTimeout: 60000,            // cy.exec
  taskTimeout: 60000,            // cy.task
  pageLoadTimeout: 60000,        // cy.visit
  requestTimeout: 10000,         // cy.request, cy.intercept waits
  responseTimeout: 30000,        // cy.request, cy.intercept response

  // ─── Viewport ─────────────────────────────────────────────────
  viewportWidth: 1280,
  viewportHeight: 720,

  // ─── Video / Screenshot ───────────────────────────────────────
  video: true,
  videoCompression: 32,          // quality 0-51 (lower = better)
  videosFolder: 'cypress/videos',
  screenshotOnRunFailure: true,
  trashAssetsBeforeRuns: true,   // clean screenshots/videos before each run

  // ─── Test Isolation ───────────────────────────────────────────
  testIsolation: true,           // clear cookies/localStorage between tests (default: true)

  // ─── Retries ──────────────────────────────────────────────────
  retries: {
    runMode: 2,     // CI retries
    openMode: 0,    // interactive mode retries
  },

  // ─── Reporter ─────────────────────────────────────────────────
  reporter: 'spec',              // or 'dot', 'tap', 'json', 'junit'
  reporterOptions: {
    mochaFile: 'cypress/results/junit.[hash].xml',
  },

  // ─── Network / Proxy ──────────────────────────────────────────
  chromeWebSecurity: true,       // set false to allow cross-origin iframes
  blockHosts: [
    'analytics.google.com',
    '*.hotjar.com',
    'cdn.segment.com',
  ],

  // ─── Environment Variables ────────────────────────────────────
  env: {
    apiUrl: 'http://localhost:3001',
    adminEmail: 'admin@test.com',
    // secrets via cypress.env.json (gitignored) or CYPRESS_ prefix env vars
  },

  // ─── E2E Config ───────────────────────────────────────────────
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.js',
    excludeSpecPattern: ['**/node_modules/**', '**/__snapshots__/**'],
    experimentalRunAllSpecs: true,         // v15.9.0+: works for e2e AND component tests
    experimentalMemoryManagement: false,    // enable for long test suites
    experimentalFastVisibility: true,       // v15.x: faster visibility assertions
    numTestsKeptInMemory: 50,               // reduce for memory savings

    // v15.10.0+: enforce migration from deprecated Cypress.env()
    // set to false after migrating all Cypress.env() → cy.env() / Cypress.expose()
    allowCypressEnv: false,

    setupNodeEvents(on, config) {
      // Plugin registration
      require('@cypress/code-coverage/task')(on, config)

      on('task', {
        log(message) {
          console.log(message)
          return null
        },
        table(message) {
          console.table(message)
          return null
        },
      })

      on('before:browser:launch', (browser, launchOptions) => {
        if (browser.name === 'chrome') {
          launchOptions.args.push('--disable-gpu')
          launchOptions.args.push('--no-sandbox')
          launchOptions.args.push('--disable-dev-shm-usage')
        }
        return launchOptions
      })

      return config
    },
  },

  // ─── Component Testing Config ─────────────────────────────────
  component: {
    devServer: {
      framework: 'react',   // react | vue | angular | svelte | next | nuxt | solid
      bundler: 'vite',       // vite | webpack
    },
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/component.js',
    viewportWidth: 500,
    viewportHeight: 500,
    setupNodeEvents(on, config) {
      return config
    },
  },
})
```

## TypeScript Configuration

```ts
// cypress.config.ts
import { defineConfig } from 'cypress'
import codeCoverageTask from '@cypress/code-coverage/task'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    setupNodeEvents(on, config) {
      codeCoverageTask(on, config)
      return config
    },
  },
})
```

## Per-Environment Configuration

```js
// cypress.config.js
module.exports = defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL || 'http://localhost:3000',
    setupNodeEvents(on, config) {
      // Load env-specific config
      const envConfig = require(`./cypress/config/${config.env.ENV || 'local'}.json`)
      return { ...config, ...envConfig }
    },
  },
})

// cypress/config/local.json
{
  "baseUrl": "http://localhost:3000",
  "env": { "apiUrl": "http://localhost:3001" }
}

// cypress/config/staging.json
{
  "baseUrl": "https://staging.example.com",
  "env": { "apiUrl": "https://api-staging.example.com" }
}

// Run with env: npx cypress run --env ENV=staging
```

## Common CLI Flags

```bash
# Run all tests headless
npx cypress run

# Run with specific browser
npx cypress run --browser chrome
npx cypress run --browser firefox
npx cypress run --browser edge
npx cypress run --browser electron

# Run specific spec(s)
npx cypress run --spec 'cypress/e2e/auth/**/*.cy.js'
npx cypress run --spec 'cypress/e2e/auth/login.cy.js,cypress/e2e/checkout.cy.js'

# Run with env override
npx cypress run --env baseUrl=http://staging.example.com,apiKey=abc123

# Set config override
npx cypress run --config viewportWidth=1920,viewportHeight=1080

# Run component tests
npx cypress run --component

# Record to Cypress Cloud
npx cypress run --record --key your-record-key

# Parallel (with Cypress Cloud)
npx cypress run --record --parallel --ci-build-id $CI_BUILD_ID

# Open interactive
npx cypress open
npx cypress open --browser chrome
npx cypress open --component
```