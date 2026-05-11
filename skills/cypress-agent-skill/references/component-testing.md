# Component Testing Reference — Cypress

## Setup

### Install

```bash
npm install --save-dev cypress
npx cypress open --component  # first run generates config
```

### cypress.config.js — React + Vite

```js
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
  },
})
```

### cypress.config.js — React + Webpack (CRA)

```js
module.exports = defineConfig({
  component: {
    devServer: {
      framework: 'create-react-app',
      bundler: 'webpack',
    },
  },
})
```

### cypress.config.js — Next.js

```js
module.exports = defineConfig({
  component: {
    devServer: {
      framework: 'next',
      bundler: 'webpack',
    },
  },
})
```

### cypress.config.js — Vue 3 + Vite

```js
module.exports = defineConfig({
  component: {
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
  },
})
```

### cypress.config.js — Angular

```js
module.exports = defineConfig({
  component: {
    devServer: {
      framework: 'angular',
      bundler: 'webpack',
    },
    specPattern: '**/*.cy.ts',
  },
})
```

---

## React Component Tests

### Basic Mounting

```jsx
// src/components/Button.cy.jsx
import { mount } from 'cypress/react'
import Button from './Button'

describe('Button', () => {
  it('renders with text', () => {
    mount(<Button>Click me</Button>)
    cy.get('button').should('have.text', 'Click me')
  })

  it('calls onClick handler', () => {
    const handleClick = cy.stub().as('clickHandler')
    mount(<Button onClick={handleClick}>Submit</Button>)
    cy.get('button').click()
    cy.get('@clickHandler').should('have.been.calledOnce')
  })

  it('is disabled', () => {
    mount(<Button disabled>Submit</Button>)
    cy.get('button').should('be.disabled')
  })
})
```

### With Context / Providers

```jsx
import { mount } from 'cypress/react'
import { ThemeProvider } from './ThemeContext'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import UserProfile from './UserProfile'

const mountWithProviders = (component) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return mount(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme="dark">
        {component}
      </ThemeProvider>
    </QueryClientProvider>
  )
}

describe('UserProfile', () => {
  it('shows user data', () => {
    cy.intercept('GET', '/api/user/1', { fixture: 'user.json' }).as('getUser')
    mountWithProviders(<UserProfile userId={1} />)
    cy.wait('@getUser')
    cy.get('[data-testid="user-name"]').should('contain', 'Alice')
  })
})
```

### Custom Mount Command

```jsx
// cypress/support/component.js
import { mount } from 'cypress/react'
import { MemoryRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import { createStore } from './test-utils'
import './commands'
import '../../src/index.css'

Cypress.Commands.add('mount', (component, options = {}) => {
  const {
    routerProps = { initialEntries: ['/'] },
    reduxState = {},
    ...mountOptions
  } = options

  const store = createStore(reduxState)

  const wrapped = (
    <Provider store={store}>
      <MemoryRouter {...routerProps}>
        {component}
      </MemoryRouter>
    </Provider>
  )

  return mount(wrapped, mountOptions)
})

// TypeScript declaration
// cypress/support/component.d.ts
declare global {
  namespace Cypress {
    interface Chainable {
      mount(
        component: React.ReactNode,
        options?: { routerProps?: object; reduxState?: object }
      ): Chainable<void>
    }
  }
}
```

### Testing Hooks

```jsx
// src/hooks/useCounter.cy.jsx
import { mount } from 'cypress/react'
import useCounter from './useCounter'

// Render a test component that exercises the hook
function CounterComponent({ initial = 0 }) {
  const { count, increment, decrement, reset } = useCounter(initial)
  return (
    <div>
      <span data-testid="count">{count}</span>
      <button data-testid="inc" onClick={increment}>+</button>
      <button data-testid="dec" onClick={decrement}>-</button>
      <button data-testid="reset" onClick={reset}>Reset</button>
    </div>
  )
}

describe('useCounter', () => {
  it('increments count', () => {
    mount(<CounterComponent initial={0} />)
    cy.get('[data-testid="count"]').should('have.text', '0')
    cy.get('[data-testid="inc"]').click()
    cy.get('[data-testid="count"]').should('have.text', '1')
  })

  it('resets to initial value', () => {
    mount(<CounterComponent initial={5} />)
    cy.get('[data-testid="inc"]').click().click()
    cy.get('[data-testid="reset"]').click()
    cy.get('[data-testid="count"]').should('have.text', '5')
  })
})
```

---

## Vue Component Tests

```js
// src/components/TodoItem.cy.js
import { mount } from 'cypress/vue'
import TodoItem from './TodoItem.vue'

describe('TodoItem', () => {
  it('renders todo text', () => {
    mount(TodoItem, {
      props: {
        todo: { id: 1, text: 'Buy groceries', done: false },
      },
    })
    cy.get('[data-testid="todo-text"]').should('contain', 'Buy groceries')
  })

  it('emits toggle event on checkbox click', () => {
    mount(TodoItem, {
      props: {
        todo: { id: 1, text: 'Buy groceries', done: false },
      },
    })
    cy.get('[data-testid="todo-checkbox"]').click()
    cy.wrap(Cypress.vueWrapper.emitted()).should('have.property', 'toggle')
    cy.wrap(Cypress.vueWrapper.emitted('toggle')[0]).should('deep.equal', [1])
  })

  it('shows strike-through when done', () => {
    mount(TodoItem, {
      props: {
        todo: { id: 1, text: 'Buy groceries', done: true },
      },
    })
    cy.get('[data-testid="todo-text"]').should('have.class', 'line-through')
  })
})
```

---

## Intercepting in Component Tests

```jsx
// Network stubs work the same in component tests
describe('UserCard with API', () => {
  it('loads and displays user', () => {
    cy.intercept('GET', '/api/users/1', {
      body: { id: 1, name: 'Alice', role: 'Admin' },
    }).as('getUser')

    mount(<UserCard userId={1} />)
    cy.wait('@getUser')
    cy.get('[data-testid="user-name"]').should('contain', 'Alice')
    cy.get('[data-testid="user-role"]').should('contain', 'Admin')
  })

  it('shows error state on failure', () => {
    cy.intercept('GET', '/api/users/1', {
      statusCode: 500,
      body: { error: 'Server error' },
    }).as('getUserError')

    mount(<UserCard userId={1} />)
    cy.wait('@getUserError')
    cy.get('[data-testid="error-message"]').should('be.visible')
  })
})
```

---

## Viewport and Responsive Tests

```js
describe('Responsive layout', () => {
  it('shows mobile nav on small screens', () => {
    cy.viewport('iphone-14')
    mount(<Navigation />)
    cy.get('[data-testid="hamburger-menu"]').should('be.visible')
    cy.get('[data-testid="desktop-nav"]').should('not.be.visible')
  })

  it('shows full nav on desktop', () => {
    cy.viewport(1280, 720)
    mount(<Navigation />)
    cy.get('[data-testid="hamburger-menu"]').should('not.be.visible')
    cy.get('[data-testid="desktop-nav"]').should('be.visible')
  })
})
```

---

## Running Component Tests

```bash
# Interactive mode
npx cypress open --component

# Headless (CI)
npx cypress run --component

# Specific spec
npx cypress run --component --spec 'src/components/Button.cy.jsx'

# Specific browser
npx cypress run --component --browser chrome
```
