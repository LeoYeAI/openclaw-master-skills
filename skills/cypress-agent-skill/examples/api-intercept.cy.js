// cypress/e2e/api-intercept.cy.js
// Example: Comprehensive network stubbing patterns

describe('API Intercept Patterns', () => {

  describe('Basic Stubbing', () => {
    it('stubs list endpoint and asserts rendered items', () => {
      cy.intercept('GET', '/api/products', {
        body: [
          { id: 1, name: 'Widget A', price: 29.99, inStock: true },
          { id: 2, name: 'Widget B', price: 49.99, inStock: false },
          { id: 3, name: 'Widget C', price: 19.99, inStock: true },
        ],
      }).as('getProducts')

      cy.visit('/products')
      cy.wait('@getProducts')

      cy.get('[data-testid="product-card"]').should('have.length', 3)
      cy.get('[data-testid="product-card"]').first().should('contain', 'Widget A')
      cy.get('[data-testid="product-card"]').eq(1)
        .find('[data-testid="out-of-stock-badge"]').should('be.visible')
    })

    it('stubs POST and verifies request payload', () => {
      cy.intercept('POST', '/api/cart/items', {
        statusCode: 201,
        body: { cartItemId: 42, productId: 1, quantity: 2 },
      }).as('addToCart')

      cy.visit('/products/1')
      cy.get('[data-testid="quantity-input"]').clear().type('2')
      cy.get('[data-testid="add-to-cart-btn"]').click()

      cy.wait('@addToCart').then((interception) => {
        expect(interception.request.body).to.deep.include({
          productId: 1,
          quantity: 2,
        })
        expect(interception.response.statusCode).to.equal(201)
      })

      cy.get('[data-testid="cart-count"]').should('contain', '1')
    })
  })

  describe('Error States', () => {
    it('shows empty state when API returns empty array', () => {
      cy.intercept('GET', '/api/products', { body: [] }).as('getEmpty')
      cy.visit('/products')
      cy.wait('@getEmpty')
      cy.get('[data-testid="empty-state"]').should('be.visible')
      cy.get('[data-testid="empty-state"]').should('contain', 'No products found')
    })

    it('shows error banner on 500', () => {
      cy.intercept('GET', '/api/products', {
        statusCode: 500,
        body: { message: 'Internal server error' },
      }).as('serverError')

      cy.visit('/products')
      cy.wait('@serverError')
      cy.get('[data-testid="error-banner"]').should('be.visible')
      cy.get('[data-testid="retry-button"]').should('be.visible')
    })

    it('shows offline message on network error', () => {
      cy.intercept('GET', '/api/products', { forceNetworkError: true }).as('offline')
      cy.visit('/products')
      cy.wait('@offline')
      cy.get('[data-testid="offline-message"]').should('be.visible')
    })

    it('shows auth error and redirects on 401', () => {
      cy.intercept('GET', '/api/user/profile', { statusCode: 401 }).as('unauthorized')
      cy.visit('/profile')
      cy.wait('@unauthorized')
      cy.url().should('include', '/login')
    })
  })

  describe('Loading States', () => {
    it('shows skeleton/spinner during fetch', () => {
      cy.intercept('GET', '/api/products', (req) => {
        req.reply({ delay: 800, body: [{ id: 1, name: 'Widget' }] })
      }).as('slowProducts')

      cy.visit('/products')

      // Assert loading indicator is shown while waiting
      cy.get('[data-testid="loading-skeleton"]').should('be.visible')

      cy.wait('@slowProducts')

      // Assert loading is gone and content appeared
      cy.get('[data-testid="loading-skeleton"]').should('not.exist')
      cy.get('[data-testid="product-card"]').should('have.length', 1)
    })
  })

  describe('Pagination', () => {
    it('loads next page on scroll/click', () => {
      // First page
      cy.intercept('GET', '/api/products?page=1', {
        body: {
          data: Array.from({ length: 10 }, (_, i) => ({
            id: i + 1,
            name: `Product ${i + 1}`,
          })),
          meta: { total: 25, page: 1, lastPage: 3 },
        },
      }).as('page1')

      // Second page
      cy.intercept('GET', '/api/products?page=2', {
        body: {
          data: Array.from({ length: 10 }, (_, i) => ({
            id: i + 11,
            name: `Product ${i + 11}`,
          })),
          meta: { total: 25, page: 2, lastPage: 3 },
        },
      }).as('page2')

      cy.visit('/products')
      cy.wait('@page1')
      cy.get('[data-testid="product-card"]').should('have.length', 10)

      cy.get('[data-testid="next-page-btn"]').click()
      cy.wait('@page2')
      cy.get('[data-testid="product-card"]').should('have.length', 10)
      cy.url().should('include', 'page=2')
    })
  })

  describe('Search and Filtering', () => {
    it('sends correct query params on search', () => {
      cy.intercept('GET', '/api/products*', (req) => {
        req.reply({ body: [] })
      }).as('search')

      cy.visit('/products')
      cy.get('[data-testid="search-input"]').type('widget')

      cy.wait('@search').then((interception) => {
        expect(interception.request.url).to.include('q=widget')
      })
    })

    it('combines filter params correctly', () => {
      cy.intercept('GET', '/api/products*').as('filtered')

      cy.visit('/products')
      cy.get('[data-testid="category-filter"]').select('Electronics')
      cy.get('[data-testid="min-price"]').type('10')
      cy.get('[data-testid="max-price"]').type('100')
      cy.get('[data-testid="apply-filters"]').click()

      cy.wait('@filtered').then((interception) => {
        const url = new URL(interception.request.url)
        expect(url.searchParams.get('category')).to.equal('Electronics')
        expect(url.searchParams.get('minPrice')).to.equal('10')
        expect(url.searchParams.get('maxPrice')).to.equal('100')
      })
    })
  })

  describe('Optimistic Updates', () => {
    it('immediately updates UI before server responds', () => {
      cy.intercept('PATCH', '/api/todos/1', (req) => {
        req.reply({ delay: 1000, body: { id: 1, completed: true } })
      }).as('toggleTodo')

      cy.visit('/todos')
      cy.get('[data-testid="todo-1-checkbox"]').click()

      // UI should update immediately (optimistic)
      cy.get('[data-testid="todo-1"]').should('have.class', 'completed')

      // Server eventually confirms
      cy.wait('@toggleTodo')
    })

    it('reverts optimistic update on server error', () => {
      cy.intercept('PATCH', '/api/todos/1', {
        statusCode: 500,
        body: { error: 'Failed to update' },
      }).as('failedToggle')

      cy.visit('/todos')
      cy.get('[data-testid="todo-1-checkbox"]').click()

      cy.wait('@failedToggle')

      // UI should revert after error
      cy.get('[data-testid="todo-1"]').should('not.have.class', 'completed')
      cy.get('[data-testid="error-toast"]').should('be.visible')
    })
  })

  describe('Real-Time / Polling', () => {
    it('polls for updates and reflects new data', () => {
      let callCount = 0
      cy.intercept('GET', '/api/notifications', (req) => {
        callCount++
        if (callCount === 1) {
          req.reply({ body: { count: 0 } })
        } else {
          req.reply({ body: { count: 3 } })
        }
      }).as('notifications')

      cy.clock()
      cy.visit('/dashboard')
      cy.wait('@notifications')
      cy.get('[data-testid="notification-badge"]').should('not.exist')

      // Advance clock to trigger poll
      cy.tick(30000)
      cy.wait('@notifications')
      cy.get('[data-testid="notification-badge"]').should('contain', '3')
    })
  })
})
