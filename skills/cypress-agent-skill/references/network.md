# Network Control Reference — cy.intercept

## Request Matching

```js
// Match by method + URL string
cy.intercept('GET', '/api/users')
cy.intercept('POST', '/api/users')
cy.intercept('PUT', '/api/users/1')
cy.intercept('DELETE', '/api/users/1')
cy.intercept('PATCH', '/api/users/1')

// Match any method
cy.intercept('/api/users')

// Glob patterns (* = any segment, ** = any path)
cy.intercept('GET', '/api/users/*')          // /api/users/1, /api/users/abc
cy.intercept('GET', '/api/**')               // any nested path under /api
cy.intercept('GET', '/api/users/*/posts')    // /api/users/1/posts

// RegExp
cy.intercept('GET', /\/api\/users\/\d+/)
cy.intercept(/\/api\/(users|posts)/)

// URL object (most precise)
cy.intercept({
  method: 'GET',
  url: '/api/search',
  query: { q: 'cypress', page: '1' },
  headers: { 'x-api-version': '2' },
})
```

## Static Responses

```js
// Full response object
cy.intercept('GET', '/api/users', {
  statusCode: 200,
  headers: {
    'content-type': 'application/json',
    'x-total-count': '42',
  },
  body: [{ id: 1, name: 'Alice' }],
  delay: 500,          // artificial delay in ms
  throttleKbps: 100,   // throttle response bandwidth
}).as('getUsers')

// Shorthand (body only)
cy.intercept('GET', '/api/users', [{ id: 1 }]).as('getUsers')

// Fixture file
cy.intercept('GET', '/api/users', { fixture: 'users.json' }).as('getUsers')

// Fixture with headers
cy.intercept('GET', '/api/users', {
  fixture: 'users.json',
  headers: { 'cache-control': 'no-cache' },
}).as('getUsers')

// Empty response
cy.intercept('DELETE', '/api/users/1', { statusCode: 204, body: '' }).as('deleteUser')

// Force network error (no response — simulates offline)
cy.intercept('GET', '/api/data', { forceNetworkError: true }).as('networkFail')
```

## Dynamic Handler Functions

```js
// Full control via handler function
cy.intercept('POST', '/api/orders', (req) => {
  // Inspect request
  console.log(req.body)
  console.log(req.headers)
  console.log(req.url)
  console.log(req.method)

  // Reply with static response
  req.reply({
    statusCode: 201,
    body: { id: 999, ...req.body },
  })
}).as('createOrder')

// Modify and forward to real server
cy.intercept('GET', '/api/config', (req) => {
  req.headers['x-test-flag'] = 'true'
  req.continue()  // forward modified request
}).as('getConfig')

// Modify response from real server
cy.intercept('GET', '/api/config', (req) => {
  req.reply((res) => {
    res.body.betaFeature = true   // inject flag
    res.headers['x-modified'] = 'true'
    // res.statusCode = 200  // optionally change status
    return res  // send modified response
  })
}).as('getConfig')

// Conditional responses
cy.intercept('GET', '/api/users/*', (req) => {
  const userId = req.url.split('/').pop()
  if (userId === '999') {
    req.reply({ statusCode: 404, body: { error: 'Not found' } })
  } else {
    req.reply({ fixture: `user-${userId}.json` })
  }
})
```

## Request Inspection and Assertions

```js
// Wait for one call
cy.wait('@createOrder')

// Wait for multiple calls
cy.wait(['@getUsers', '@getProducts'])

// Assert request details
cy.wait('@createOrder').then((interception) => {
  const { request, response } = interception

  // Request assertions
  expect(request.method).to.equal('POST')
  expect(request.url).to.include('/api/orders')
  expect(request.body).to.deep.include({ quantity: 2 })
  expect(request.headers).to.have.property('authorization')
  expect(request.headers['content-type']).to.include('application/json')

  // Response assertions
  expect(response.statusCode).to.equal(201)
  expect(response.body.id).to.be.a('number')
})

// Wait for Nth call (0-indexed)
cy.wait('@search')  // first call
cy.wait('@search')  // second call (Cypress tracks call count)

// Get all calls after the fact
cy.get('@search.all').then((interceptions) => {
  expect(interceptions).to.have.length(3)
})

// Get specific call
cy.get('@search.2').then((interception) => {
  expect(interception.request.query.q).to.equal('advanced')
})
```

## Aliases and Ordering

```js
// Multiple intercepts for same URL (last registered wins for stub)
cy.intercept('GET', '/api/items', { fixture: 'items-empty.json' }).as('getItemsEmpty')

// Override for specific scenario
describe('when items exist', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/items', { fixture: 'items-full.json' }).as('getItemsFull')
  })
  // The later registration takes precedence
})
```

## GraphQL Intercepting

```js
// Intercept GraphQL by operationName in body
cy.intercept('POST', '/graphql', (req) => {
  if (req.body.operationName === 'GetUsers') {
    req.reply({ fixture: 'graphql/get-users.json' })
  } else if (req.body.operationName === 'CreateUser') {
    req.reply({ fixture: 'graphql/create-user.json' })
  } else {
    req.continue()  // pass other queries through
  }
}).as('graphql')

// Wait for specific operation
cy.wait('@graphql').its('request.body.operationName').should('eq', 'GetUsers')
```

## WebSocket Stubs (Experimental)

```js
// Intercept WebSocket connection
cy.intercept('GET', '/ws').as('wsConnection')
```

## Tips

1. **Register intercepts BEFORE the action that triggers the request**
2. **Always use `.as()` to name intercepts you plan to `cy.wait()` on**
3. **Use `req.continue()` to pass requests to real server (spy mode)**
4. **Delay + throttle simulate slow networks for loading state tests**
5. **`forceNetworkError` tests offline/error recovery paths**
6. **Multiple `cy.wait('@alias')` calls advance through sequential requests**
