# Selectors Reference — Cypress

## Stability Hierarchy (Best → Worst)

### Tier 1 — Stable (Recommended)

```js
// data-testid (purpose-built for testing)
cy.get('[data-testid="submit-button"]')
cy.get('[data-testid="user-card-123"]')

// data-cy (alternative attribute)
cy.get('[data-cy="login-form"]')

// data-test (another common convention)
cy.get('[data-test="header-nav"]')

// ARIA roles (accessible AND stable)
cy.get('[role="dialog"]')
cy.get('[role="alert"]')
cy.get('[role="navigation"]')
cy.get('[role="main"]')
cy.get('[role="button"]')

// ARIA labels
cy.get('[aria-label="Close modal"]')
cy.get('[aria-label="Search products"]')

// Semantic form attributes
cy.get('button[type="submit"]')
cy.get('input[type="email"]')
cy.get('input[name="username"]')
cy.get('label[for="email"]')

// cy.contains — text-based, often stable
cy.contains('Submit')
cy.contains('button', 'Submit')    // scoped to element type
cy.contains('[data-testid="nav"]', 'Dashboard')  // scoped to parent

// ID (stable if IDs are static, not auto-generated)
cy.get('#login-form')
cy.get('#main-content')
```

### Tier 2 — Acceptable (Use With Care)

```js
// Semantic HTML elements when structure is stable
cy.get('nav')
cy.get('header')
cy.get('main')
cy.get('footer')
cy.get('form')
cy.get('table')

// HTML attributes that don't change often
cy.get('a[href="/about"]')
cy.get('img[alt="Logo"]')
cy.get('input[placeholder="Search..."]')

// Text content (breaks if copy changes)
cy.contains('Sign in')
cy.contains('h1', 'Dashboard')
```

### Tier 3 — Avoid

```js
// CSS utility classes (Tailwind, Bootstrap, etc.) — change with styling
cy.get('.btn-primary')        // ❌
cy.get('.MuiButton-root')     // ❌ (MUI generated classes change)
cy.get('.text-blue-500')      // ❌ (Tailwind class)

// Complex CSS selectors — breaks on restructuring
cy.get('.sidebar > ul > li:first-child > a')  // ❌
cy.get('.card .card-body .card-title')        // ❌

// Positional (extremely fragile)
cy.get('button').eq(2)        // ❌ (except for known stable lists)
cy.get('li:nth-child(3)')     // ❌
cy.get('.items > *:last-child')  // ❌

// XPath (never — Cypress is CSS-first)
cy.xpath('//div[@class="container"]//button')  // ❌ (avoid cypress-xpath)
```

## Scoping and Chaining

```js
// within() — scope all queries to a parent
cy.get('[data-testid="user-profile"]').within(() => {
  cy.get('[data-testid="name"]').should('contain', 'Alice')
  cy.get('[data-testid="email"]').should('contain', '@example.com')
  cy.get('[data-testid="edit-btn"]').click()
})

// find() — search within a subject
cy.get('table').find('tbody tr').should('have.length', 5)
cy.get('[data-testid="product-card"]').first().find('[data-testid="price"]')

// parent() / parents()
cy.get('[data-testid="error-icon"]').parent().should('have.class', 'field-error')
cy.get('[data-testid="tag"]').parents('[data-testid="post-card"]').first()

// siblings()
cy.get('[data-testid="active-tab"]').siblings().should('not.have.class', 'active')

// next() / prev()
cy.get('[data-testid="step-2"]').prev().should('have.class', 'completed')
cy.get('[data-testid="step-1"]').next().should('have.text', 'Step 2')

// closest() — nearest ancestor matching selector
cy.get('[data-testid="delete-icon"]').closest('[data-testid="list-item"]').should('exist')
```

## Querying Multiple Elements

```js
// Get all matches
cy.get('[data-testid="item"]')           // all items
cy.get('[data-testid="item"]').first()   // first
cy.get('[data-testid="item"]').last()    // last
cy.get('[data-testid="item"]').eq(2)     // 3rd (0-indexed)

// Iterate (only when necessary)
cy.get('[data-testid="item"]').each(($item, index) => {
  cy.wrap($item).should('be.visible')
})

// Filter
cy.get('[data-testid="item"]').filter('[data-status="active"]')
cy.get('[data-testid="item"]').not('[data-disabled="true"]')
cy.get('[data-testid="item"]').contains('Featured')
```

## Adding data-testid to Your App

```html
<!-- React -->
<button data-testid="submit-button" type="submit">Submit</button>
<input data-testid="email-input" type="email" />
<div data-testid="user-card-{id}">...</div>

<!-- Vue -->
<button data-testid="submit-button">Submit</button>
<template v-for="user in users">
  <div :data-testid="`user-card-${user.id}`">...</div>
</template>

<!-- Angular -->
<button data-testid="submit-button">Submit</button>
```

```js
// Strip test IDs from production build (optional but recommended)
// babel-plugin-react-remove-properties
{
  "plugins": [
    ["babel-plugin-react-remove-properties", {
      "properties": ["data-testid"],
      "env": "production"
    }]
  ]
}
```

## Debugging Selectors

```js
// Inspect what Cypress found
cy.get('[data-testid="btn"]').then(($el) => {
  console.log('Element:', $el[0])
  console.log('Text:', $el.text())
  console.log('Classes:', $el.attr('class'))
})

// Check if selector finds unique element
cy.get('[data-testid="submit"]').should('have.length', 1)

// Use cy.pause() and Cypress runner's selector playground
cy.pause()
```
