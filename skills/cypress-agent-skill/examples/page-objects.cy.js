// cypress/e2e/page-objects.cy.js
// Example: Full Page Object Model implementation

// ─── Page Objects ────────────────────────────────────────────────

class BasePage {
  get pageTitle() {
    return cy.get('[data-testid="page-title"]')
  }

  get loadingIndicator() {
    return cy.get('[data-testid="loading-spinner"]')
  }

  waitForLoad() {
    this.loadingIndicator.should('not.exist')
    return this
  }
}

class LoginPage extends BasePage {
  get emailInput() {
    return cy.get('[data-testid="email-input"]')
  }
  get passwordInput() {
    return cy.get('[data-testid="password-input"]')
  }
  get submitButton() {
    return cy.get('[data-testid="login-button"]')
  }
  get errorMessage() {
    return cy.get('[data-testid="login-error"]')
  }
  get forgotPasswordLink() {
    return cy.get('[data-testid="forgot-password-link"]')
  }

  visit() {
    cy.visit('/login')
    return this
  }

  fillEmail(email) {
    this.emailInput.clear().type(email)
    return this
  }

  fillPassword(password) {
    this.passwordInput.clear().type(password, { log: false })
    return this
  }

  submit() {
    this.submitButton.click()
    return this
  }

  login(email, password) {
    return this.fillEmail(email).fillPassword(password).submit()
  }

  assertLoginError(message) {
    this.errorMessage.should('be.visible').and('contain', message)
    return this
  }
}

class DashboardPage extends BasePage {
  get welcomeMessage() {
    return cy.get('[data-testid="welcome-message"]')
  }
  get userMenu() {
    return cy.get('[data-testid="user-menu"]')
  }
  get logoutButton() {
    return cy.get('[data-testid="logout-button"]')
  }
  get statsWidget() {
    return cy.get('[data-testid="stats-widget"]')
  }
  get recentActivity() {
    return cy.get('[data-testid="recent-activity"]')
  }
  get navLinks() {
    return cy.get('[data-testid="nav-link"]')
  }

  visit() {
    cy.visit('/dashboard')
    return this
  }

  openUserMenu() {
    this.userMenu.click()
    return this
  }

  logout() {
    this.openUserMenu()
    this.logoutButton.click()
    return new LoginPage()
  }

  navigateTo(linkText) {
    cy.contains('[data-testid="nav-link"]', linkText).click()
    return this
  }

  assertWelcome(name) {
    this.welcomeMessage.should('contain', name)
    return this
  }
}

class ProductsPage extends BasePage {
  get searchInput() {
    return cy.get('[data-testid="search-input"]')
  }
  get productCards() {
    return cy.get('[data-testid="product-card"]')
  }
  get emptyState() {
    return cy.get('[data-testid="empty-state"]')
  }
  get sortDropdown() {
    return cy.get('[data-testid="sort-select"]')
  }
  get filterPanel() {
    return cy.get('[data-testid="filter-panel"]')
  }

  visit() {
    cy.visit('/products')
    return this
  }

  search(query) {
    this.searchInput.clear().type(query)
    return this
  }

  sortBy(option) {
    this.sortDropdown.select(option)
    return this
  }

  getProductByName(name) {
    return cy.contains('[data-testid="product-card"]', name)
  }

  addToCart(productName) {
    this.getProductByName(productName)
      .find('[data-testid="add-to-cart-btn"]')
      .click()
    return this
  }

  assertProductCount(count) {
    this.productCards.should('have.length', count)
    return this
  }

  assertProductVisible(name) {
    this.getProductByName(name).should('be.visible')
    return this
  }

  assertEmptyState() {
    this.emptyState.should('be.visible')
    return this
  }
}

class CheckoutPage extends BasePage {
  get orderSummary() {
    return cy.get('[data-testid="order-summary"]')
  }
  get totalPrice() {
    return cy.get('[data-testid="total-price"]')
  }
  get placeOrderButton() {
    return cy.get('[data-testid="place-order-btn"]')
  }
  get cardNumberInput() {
    return cy.get('[data-testid="card-number"]')
  }
  get cardExpiryInput() {
    return cy.get('[data-testid="card-expiry"]')
  }
  get cardCvvInput() {
    return cy.get('[data-testid="card-cvv"]')
  }
  get successMessage() {
    return cy.get('[data-testid="order-success"]')
  }

  visit() {
    cy.visit('/checkout')
    return this
  }

  fillPayment({ number, expiry, cvv }) {
    this.cardNumberInput.type(number)
    this.cardExpiryInput.type(expiry)
    this.cardCvvInput.type(cvv)
    return this
  }

  placeOrder() {
    this.placeOrderButton.click()
    return this
  }

  assertSuccess() {
    this.successMessage.should('be.visible')
    return this
  }

  assertTotal(amount) {
    this.totalPrice.should('contain', amount)
    return this
  }
}

// ─── Instantiate Pages ───────────────────────────────────────────

const loginPage = new LoginPage()
const dashboardPage = new DashboardPage()
const productsPage = new ProductsPage()
const checkoutPage = new CheckoutPage()

// ─── Tests ───────────────────────────────────────────────────────

describe('E-Commerce Flows — Page Object Model', () => {
  beforeEach(() => {
    cy.clearAllCookies()
    cy.clearAllLocalStorage()
  })

  describe('Authentication', () => {
    it('logs in with valid credentials', () => {
      cy.intercept('POST', '/api/auth/login', {
        body: { token: 'test-token', user: { name: 'Alice' } },
      }).as('login')

      loginPage.visit().login('alice@example.com', 'password123')
      cy.wait('@login')
      dashboardPage.assertWelcome('Alice')
    })

    it('shows error for invalid credentials', () => {
      cy.intercept('POST', '/api/auth/login', {
        statusCode: 401,
        body: { error: 'Invalid credentials' },
      }).as('loginFailed')

      loginPage
        .visit()
        .login('wrong@example.com', 'wrongpass')
        .assertLoginError('Invalid credentials')
    })
  })

  describe('Product Browsing', () => {
    beforeEach(() => {
      cy.intercept('GET', '/api/products*', {
        body: [
          { id: 1, name: 'Laptop', price: 999, category: 'Electronics' },
          { id: 2, name: 'Phone', price: 599, category: 'Electronics' },
          { id: 3, name: 'Desk', price: 299, category: 'Furniture' },
        ],
      }).as('getProducts')

      productsPage.visit()
      cy.wait('@getProducts')
    })

    it('shows all products', () => {
      productsPage.assertProductCount(3)
    })

    it('searches and filters results', () => {
      cy.intercept('GET', '/api/products?q=Laptop', {
        body: [{ id: 1, name: 'Laptop', price: 999 }],
      }).as('searchResults')

      productsPage.search('Laptop')
      cy.wait('@searchResults')
      productsPage.assertProductCount(1).assertProductVisible('Laptop')
    })

    it('shows empty state when no results', () => {
      cy.intercept('GET', '/api/products?q=xyz', { body: [] }).as('noResults')
      productsPage.search('xyz')
      cy.wait('@noResults')
      productsPage.assertEmptyState()
    })
  })

  describe('Checkout Flow', () => {
    it('completes purchase end-to-end', () => {
      // Setup stubs
      cy.intercept('POST', '/api/cart/items', {
        statusCode: 201,
        body: { cartId: 'cart-123' },
      }).as('addToCart')

      cy.intercept('GET', '/api/cart', {
        body: {
          items: [{ id: 1, name: 'Laptop', price: 999, quantity: 1 }],
          total: 999,
        },
      }).as('getCart')

      cy.intercept('POST', '/api/orders', {
        statusCode: 201,
        body: { orderId: 'order-456', status: 'confirmed' },
      }).as('placeOrder')

      cy.intercept('GET', '/api/products*', {
        body: [{ id: 1, name: 'Laptop', price: 999 }],
      })

      // Execute flow
      productsPage.visit().addToCart('Laptop')
      cy.wait('@addToCart')

      cy.visit('/checkout')
      cy.wait('@getCart')

      checkoutPage
        .assertTotal('$999')
        .fillPayment({ number: '4111111111111111', expiry: '12/26', cvv: '123' })
        .placeOrder()

      cy.wait('@placeOrder')
      checkoutPage.assertSuccess()
    })
  })
})
