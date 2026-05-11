# CI/CD Reference — Cypress

## GitHub Actions

### Basic (Sequential)

```yaml
name: Cypress E2E

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  cypress:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Setup Node
        uses: actions/setup-node@v6
        with:
          node-version: 22
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build app
        run: npm run build

      - name: Start server
        run: npm run start:ci &
        
      - name: Wait for server
        run: npx wait-on http://localhost:3000 --timeout 60000

      - name: Run Cypress
        uses: cypress-io/github-action@v6
        with:
          browser: chrome
          headed: false
        env:
          CYPRESS_API_URL: ${{ secrets.CYPRESS_API_URL }}
          
      - name: Upload screenshots
        uses: actions/upload-artifact@v6
        if: failure()
        with:
          name: cypress-screenshots
          path: cypress/screenshots
          
      - name: Upload videos
        uses: actions/upload-artifact@v6
        if: always()
        with:
          name: cypress-videos
          path: cypress/videos
```

### Parallel with Cypress Cloud

```yaml
name: Cypress Parallel

on: [push, pull_request]

jobs:
  cypress-run:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        containers: [1, 2, 3, 4]

    steps:
      - uses: actions/checkout@v6

      - name: Run Cypress
        uses: cypress-io/github-action@v6
        with:
          start: npm start
          wait-on: 'http://localhost:3000'
          wait-on-timeout: 120
          browser: chrome
          record: true
          parallel: true
          group: 'UI - Chrome'
        env:
          CYPRESS_RECORD_KEY: ${{ secrets.CYPRESS_RECORD_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Matrix — Multiple Browsers

```yaml
jobs:
  cypress-cross-browser:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        browser: [chrome, firefox, edge]
    steps:
      - uses: actions/checkout@v6
      - uses: cypress-io/github-action@v6
        with:
          start: npm start
          wait-on: 'http://localhost:3000'
          browser: ${{ matrix.browser }}
          record: true
          group: ${{ matrix.browser }}
        env:
          CYPRESS_RECORD_KEY: ${{ secrets.CYPRESS_RECORD_KEY }}
```

### Smoke Tests Only on PR

```yaml
jobs:
  smoke:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v6
      - uses: cypress-io/github-action@v6
        with:
          start: npm start
          wait-on: 'http://localhost:3000'
          spec: 'cypress/e2e/smoke/**/*.cy.js'

  full-suite:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v6
      - uses: cypress-io/github-action@v6
        with:
          start: npm start
          wait-on: 'http://localhost:3000'
```

---

## GitLab CI

```yaml
# .gitlab-ci.yml
image: cypress/browsers:node20-chrome-120

stages:
  - test

cypress:e2e:
  stage: test
  script:
    - npm ci
    - npm start &
    - npx wait-on http://localhost:3000
    - npx cypress run --browser chrome --record --parallel
  parallel: 4
  variables:
    CYPRESS_RECORD_KEY: $CYPRESS_RECORD_KEY
  artifacts:
    when: always
    paths:
      - cypress/videos/
      - cypress/screenshots/
    expire_in: 7 days
    reports:
      junit: cypress/results/junit.xml
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
      - ~/.cache/Cypress

cypress:component:
  stage: test
  script:
    - npm ci
    - npx cypress run --component
  artifacts:
    when: on_failure
    paths:
      - cypress/screenshots/
```

---

## CircleCI

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  cypress: cypress-io/cypress@3

workflows:
  build-and-test:
    jobs:
      - cypress/run:
          name: 'Cypress E2E'
          start-command: 'npm start'
          wait-on: 'http://localhost:3000'
          cypress-command: 'npx cypress run --record --parallel'
          parallelism: 4
          executor:
            name: 'cypress/default'
            node-version: '22'
          environment:
            CYPRESS_RECORD_KEY: $CYPRESS_RECORD_KEY
          post-steps:
            - store_artifacts:
                path: cypress/screenshots
            - store_artifacts:
                path: cypress/videos
```

---

## Jenkins

```groovy
// Jenkinsfile
pipeline {
  agent {
    docker {
      image 'cypress/browsers:node20-chrome-120'
    }
  }

  environment {
    CYPRESS_RECORD_KEY = credentials('cypress-record-key')
    HOME = '/root'
  }

  stages {
    stage('Install') {
      steps {
        sh 'npm ci'
      }
    }

    stage('E2E Tests') {
      steps {
        sh 'npm start &'
        sh 'npx wait-on http://localhost:3000 --timeout 60000'
        sh 'npx cypress run --record --browser chrome'
      }
      post {
        always {
          archiveArtifacts artifacts: 'cypress/videos/**', allowEmptyArchive: true
          archiveArtifacts artifacts: 'cypress/screenshots/**', allowEmptyArchive: true
          junit allowEmptyResults: true, testResults: 'cypress/results/*.xml'
        }
      }
    }
  }
}
```

---

## JUnit XML Reports (CI Integration)

```js
// cypress.config.js
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  reporter: 'cypress-multi-reporters',
  reporterOptions: {
    reporterEnabled: 'spec, mocha-junit-reporter',
    mochaJunitReporterReporterOptions: {
      mochaFile: 'cypress/results/junit.[hash].xml',
      toConsole: false,
    },
  },
  e2e: {
    setupNodeEvents(on, config) {},
  },
})
```

```bash
# Install reporters
npm install --save-dev cypress-multi-reporters mocha-junit-reporter
```

---

## Docker Images

```bash
# Official Cypress images
cypress/base:20           # Node 20, no browsers
cypress/browsers:node20-chrome-120-ff-121   # with browsers
cypress/included:15.11.0   # Cypress pre-installed

# Full Docker run
docker run -it \
  -v $PWD:/e2e \
  -w /e2e \
  -e CYPRESS_baseUrl=http://host.docker.internal:3000 \
  cypress/included:15.11.0
```

---

## Performance Tips

1. **Reuse node_modules cache** using lock file hash as cache key
2. **Run component tests in parallel** with `--parallel` flag
3. **Split specs by file** — avoid huge spec files (1 spec ≤ 50 tests)
4. **Use `--spec` flag** to run subset: `cypress run --spec 'cypress/e2e/auth/**'`
5. **Disable video in CI** unless needed: `video: false` in config
6. **Enable `experimentalMemoryManagement`** for long test runs
7. **Set `numTestsKeptInMemory: 0`** for memory-constrained environments