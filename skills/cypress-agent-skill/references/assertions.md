# Assertions Reference — Cypress

## Core Assertion Patterns

```js
// Visibility
cy.get('[data-testid="el"]').should('be.visible')
cy.get('[data-testid="el"]').should('not.be.visible')
cy.get('[data-testid="el"]').should('exist')
cy.get('[data-testid="el"]').should('not.exist')

// Text content
cy.get('[data-testid="el"]').should('have.text', 'Exact text')
cy.get('[data-testid="el"]').should('contain.text', 'partial text')
cy.get('[data-testid="el"]').should('contain', 'partial text')  // shorthand
cy.get('[data-testid="el"]').invoke('text').should('match', /pattern/)
cy.get('[data-testid="el"]').invoke('text').should('not.be.empty')

// Input values
cy.get('input').should('have.value', 'expected')
cy.get('input').should('not.have.value', '')
cy.get('select').should('have.value', 'option-value')
cy.get('textarea').invoke('val').should('include', 'partial')

// Attributes
cy.get('a').should('have.attr', 'href', '/expected-path')
cy.get('a').should('have.attr', 'href').and('include', '/path')
cy.get('button').should('have.attr', 'type', 'submit')
cy.get('img').should('have.attr', 'alt').and('not.be.empty')
cy.get('[data-testid="el"]').should('have.attr', 'data-state', 'active')
cy.get('[data-testid="el"]').should('not.have.attr', 'disabled')

// CSS classes
cy.get('[data-testid="el"]').should('have.class', 'active')
cy.get('[data-testid="el"]').should('not.have.class', 'error')
cy.get('[data-testid="el"]').invoke('attr', 'class').should('include', 'btn')

// CSS properties
cy.get('[data-testid="el"]').should('have.css', 'display', 'flex')
cy.get('[data-testid="el"]').should('have.css', 'color', 'rgb(255, 0, 0)')

// Disabled / Enabled
cy.get('button').should('be.disabled')
cy.get('button').should('not.be.disabled')
cy.get('button').should('be.enabled')

// Checked state (checkbox/radio)
cy.get('input[type="checkbox"]').should('be.checked')
cy.get('input[type="checkbox"]').should('not.be.checked')

// Focus
cy.get('input').should('have.focus')
cy.get('input').should('not.have.focus')

// Length
cy.get('[data-testid="item"]').should('have.length', 5)
cy.get('[data-testid="item"]').should('have.length.greaterThan', 0)
cy.get('[data-testid="item"]').should('have.length.lessThan', 10)
cy.get('[data-testid="item"]').should('have.length.at.least', 3)
cy.get('[data-testid="item"]').should('have.length.at.most', 10)
```

## URL Assertions

```js
cy.url().should('eq', 'http://localhost:3000/dashboard')
cy.url().should('include', '/dashboard')
cy.url().should('not.include', '/login')
cy.url().should('match', /\/user\/\d+/)

cy.location('pathname').should('eq', '/dashboard')
cy.location('search').should('include', 'page=2')
cy.location('hash').should('eq', '#section-1')
```

## Multiple Chained Assertions

```js
// All assertions retry together — preferred over separate .should() calls
cy.get('[data-testid="submit-btn"]')
  .should('be.visible')
  .and('not.be.disabled')
  .and('have.attr', 'type', 'submit')
  .and('contain.text', 'Save')
```

## Async Value Assertions

```js
// Resolve via .then()
cy.get('[data-testid="price"]').invoke('text').then((text) => {
  const price = parseFloat(text.replace('$', ''))
  expect(price).to.be.greaterThan(0)
  expect(price).to.be.lessThan(1000)
})

// Alias and assert
cy.get('[data-testid="count"]').invoke('text').as('count')
cy.get('@count').should('match', /^\d+$/)
```

## Network / Request Assertions

```js
cy.wait('@myRequest').then(({ request, response }) => {
  // Request
  expect(request.method).to.equal('POST')
  expect(request.body).to.deep.include({ name: 'Alice' })
  expect(request.headers).to.have.property('authorization')

  // Response
  expect(response.statusCode).to.equal(201)
  expect(response.body.id).to.be.a('number')
  expect(response.body).to.have.keys(['id', 'name', 'email'])
})

// Chainable with .its()
cy.wait('@search')
  .its('request.url')
  .should('include', 'q=cypress')

cy.wait('@getUser')
  .its('response.body.email')
  .should('contain', '@example.com')
```

## Cookie Assertions

```js
cy.getCookie('session').should('exist')
cy.getCookie('session').should('have.property', 'value').and('not.be.empty')
cy.getCookie('session').its('httpOnly').should('be.true')
cy.getCookies().should('have.length.greaterThan', 0)
```

## localStorage Assertions

```js
cy.window().its('localStorage').invoke('getItem', 'auth_token').should('exist')
cy.window().its('localStorage').invoke('getItem', 'user').then(JSON.parse).should('have.property', 'id')
```

## Spy / Stub Assertions

```js
cy.get('@myStub').should('have.been.called')
cy.get('@myStub').should('have.been.calledOnce')
cy.get('@myStub').should('have.been.calledTwice')
cy.get('@myStub').should('have.been.calledWith', 'expected-arg')
cy.get('@myStub').should('have.been.calledWithMatch', { key: 'value' })
cy.get('@myStub').should('not.have.been.called')
```

## Viewport Assertions

```js
cy.viewport('iphone-14')
cy.viewport(375, 812)

// Assert responsive behavior
cy.get('[data-testid="mobile-nav"]').should('be.visible')
cy.get('[data-testid="desktop-nav"]').should('not.be.visible')
```

## Custom Assertion Helpers

```js
// Assert element is "ready" (visible + enabled + not loading)
const shouldBeReady = (selector) => {
  cy.get(selector)
    .should('be.visible')
    .and('not.be.disabled')
    .and('not.have.attr', 'aria-busy', 'true')
}

// Assert form validation error
const shouldHaveValidationError = (fieldName, errorText) => {
  cy.get(`[data-testid="${fieldName}-error"]`)
    .should('be.visible')
    .and('contain', errorText)
}
```
