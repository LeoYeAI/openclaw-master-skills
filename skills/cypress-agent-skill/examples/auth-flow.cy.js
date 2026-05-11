/**
 * auth-flow.cy.js — Cypress auth patterns (v15.10.0+ compatible)
 *
 * Uses cy.env() for secrets (replaces deprecated Cypress.env())
 * Uses Cypress.expose() for non-sensitive public config
 *
 * Required cypress.env.json / CYPRESS_* env vars:
 *   testUserEmail, testUserPassword, adminEmail, adminPassword
 */

describe('Authentication Flows', () => {

  // ─── UI Login ──────────────────────────────────────────────────────────────

  context('UI Login', () => {
    it('logs in with valid credentials', () => {
      cy.env(['testUserEmail', 'testUserPassword']).then(({ testUserEmail, testUserPassword }) => {
        cy.session(
          ['ui-login', testUserEmail],
          () => {
            cy.visit('/login')
            cy.get('[data-testid="email-input"]').type(testUserEmail || 'user@example.com')
            cy.get('[data-testid="password-input"]').type(testUserPassword || 'password123')
            cy.get('[data-testid="submit-button"]').click()
            cy.url().should('include', '/dashboard')
          },
          {
            validate() {
              cy.getCookie('session_token').should('exist')
            },
            cacheAcrossSpecs: true,
          }
        )
        cy.visit('/dashboard')
        cy.get('[data-testid="user-menu"]').should('be.visible')
      })
    })

    it('shows error for invalid credentials', () => {
      cy.visit('/login')
      cy.get('[data-testid="email-input"]').type('wrong@example.com')
      cy.get('[data-testid="password-input"]').type('wrongpassword')
      cy.get('[data-testid="submit-button"]').click()
      cy.get('[data-testid="error-message"]').should('contain', 'Invalid credentials')
      cy.url().should('include', '/login')
    })
  })

  // ─── API Login (Faster) ────────────────────────────────────────────────────

  context('API Login (Faster)', () => {
    it('logs in via API and sets token', () => {
      cy.env(['adminEmail', 'adminPassword']).then(({ adminEmail, adminPassword }) => {
        cy.session(
          ['api-admin', adminEmail],
          () => {
            cy.request({
              method: 'POST',
              url: '/api/auth/login',
              body: {
                email: adminEmail || 'admin@example.com',
                password: adminPassword,
              },
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
        cy.visit('/dashboard')
        cy.get('[data-testid="admin-panel"]').should('be.visible')
      })
    })
  })

  // ─── Logout ────────────────────────────────────────────────────────────────

  context('Logout', () => {
    beforeEach(() => {
      cy.env(['testUserEmail', 'testUserPassword']).then(({ testUserEmail, testUserPassword }) => {
        cy.session(['logout-test-user', testUserEmail], () => {
          cy.request({
            method: 'POST',
            url: '/api/auth/login',
            body: { email: testUserEmail, password: testUserPassword },
          }).then(({ body }) => {
            window.localStorage.setItem('auth_token', body.token)
          })
        })
        cy.visit('/dashboard')
      })
    })

    it('logs out and redirects to login', () => {
      cy.get('[data-testid="user-menu"]').click()
      cy.get('[data-testid="logout-button"]').click()
      cy.url().should('include', '/login')
      cy.getCookie('session_token').should('not.exist')
    })
  })

  // ─── Role-Based Access ─────────────────────────────────────────────────────

  context('Role-Based Access', () => {
    it('restricts admin routes for regular users', () => {
      cy.env(['testUserEmail', 'testUserPassword']).then(({ testUserEmail, testUserPassword }) => {
        cy.session(['rbac-user', testUserEmail], () => {
          cy.request('POST', '/api/auth/login', {
            email: testUserEmail,
            password: testUserPassword,
          }).then(({ body }) => {
            window.localStorage.setItem('auth_token', body.token)
          })
        })
        cy.visit('/admin', { failOnStatusCode: false })
        cy.url().should('include', '/dashboard')
        cy.get('[data-testid="access-denied"]').should('be.visible')
      })
    })
  })
})