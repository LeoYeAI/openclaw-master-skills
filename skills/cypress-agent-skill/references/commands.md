# cy.* Commands Reference — Cheatsheet

## Navigation

```js
cy.visit('/path')
cy.visit('http://example.com', { timeout: 30000 })
cy.visit('/page', { onBeforeLoad: (win) => { /* stub things */ } })
cy.go('back')
cy.go('forward')
cy.reload()
cy.reload(true)  // force reload (bypass cache)
cy.url()
cy.location()
cy.location('pathname')
cy.hash()
cy.title()
```

## DOM Queries

```js
cy.get(selector)
cy.get(selector, { timeout: 10000 })
cy.contains(text)
cy.contains(selector, text)
cy.find(selector)          // child command
cy.children()              // direct children
cy.parent()
cy.parents(selector)
cy.closest(selector)
cy.next(selector)
cy.prev(selector)
cy.siblings(selector)
cy.first()
cy.last()
cy.eq(index)
cy.filter(selector)
cy.not(selector)
cy.within(fn)
cy.wrap(subject)
```

## Actions

```js
cy.click()
cy.click({ force: true })  // click even if obscured
cy.click(50, 100)          // click at specific coords
cy.dblclick()
cy.rightclick()
cy.type('text')
cy.type('text{enter}')     // special keys
cy.type('{ctrl}a{del}')
cy.clear()                 // clear input
cy.check()                 // check checkbox
cy.uncheck()
cy.check(['value1', 'value2'])
cy.select('Option Text')   // select dropdown by text
cy.select('value')         // select by value
cy.selectFile(path)        // file upload (v9.3+)
cy.selectFile([path1, path2])
cy.selectFile(path, { action: 'drag-drop' })
cy.submit()                // submit form
cy.focus()
cy.blur()
cy.hover()                 // requires cypress-real-events plugin
cy.scrollTo('bottom')
cy.scrollTo(x, y)
cy.scrollIntoView()
cy.trigger('mouseover')
cy.trigger('change', { force: true })
```

## Keyboard Shortcuts (in .type())

```js
cy.get('input').type('{enter}')
cy.get('input').type('{esc}')
cy.get('input').type('{backspace}')
cy.get('input').type('{del}')
cy.get('input').type('{tab}')
cy.get('input').type('{uparrow}')
cy.get('input').type('{downarrow}')
cy.get('input').type('{leftarrow}')
cy.get('input').type('{rightarrow}')
cy.get('input').type('{home}')
cy.get('input').type('{end}')
cy.get('input').type('{ctrl}a')
cy.get('input').type('{cmd}k')
cy.get('input').type('{shift}{enter}')
```

## Assertions

```js
cy.should('be.visible')
cy.should('not.be.visible')
cy.should('exist')
cy.should('not.exist')
cy.should('have.text', 'exact text')
cy.should('contain', 'partial')
cy.should('have.value', 'input value')
cy.should('have.attr', 'href', '/path')
cy.should('have.class', 'active')
cy.should('not.have.class', 'error')
cy.should('have.css', 'color', 'rgb(0,0,0)')
cy.should('be.checked')
cy.should('be.disabled')
cy.should('have.length', 5)
cy.should('be.empty')
cy.and(...)  // chain additional should
```

## Network

```js
cy.intercept(method, url)
cy.intercept(method, url, response)
cy.intercept(method, url, handler)
cy.intercept({ method, url, headers, query })
cy.request(method, url)
cy.request(method, url, body)
cy.request({ method, url, body, headers, failOnStatusCode: false })
cy.wait('@alias')
cy.wait(['@alias1', '@alias2'])
cy.wait('@alias', { timeout: 15000 })
```

## Cookies / Storage

```js
cy.getCookie(name)
cy.getCookies()
cy.getAllCookies()
cy.setCookie(name, value)
cy.clearCookie(name)
cy.clearCookies()
cy.clearAllCookies()
cy.clearAllLocalStorage()
cy.clearAllSessionStorage()
cy.window()
cy.document()
cy.readFile(path)
cy.writeFile(path, content)
```

## Time Control

```js
cy.clock()                          // freeze time at current moment
cy.clock(timestamp)                 // set specific time
cy.clock(new Date(2024, 0, 1))     // January 1, 2024
cy.tick(milliseconds)              // advance clock
cy.clock().invoke('restore')        // restore real clock
```

## Tasks and Exec

```js
cy.task('myTask')
cy.task('myTask', { arg: 'value' })
cy.exec('bash command')
cy.exec('npm run seed', { timeout: 30000, failOnNonZeroExit: false })
```

## Screenshots and Videos

```js
cy.screenshot()
cy.screenshot('name')
cy.screenshot({ capture: 'fullPage' })
cy.screenshot({ clip: { x: 0, y: 0, width: 400, height: 300 } })
```

## Debugging

```js
cy.pause()                         // pause test execution
cy.debug()                         // log subject to console
cy.log('message')                  // log in Cypress runner
cy.get(selector).debug()
cy.get(selector).then(($el) => { debugger })
```

## Fixtures

```js
cy.fixture('filename.json')
cy.fixture('filename.json').as('alias')
cy.fixture('images/logo.png', 'base64')
```

## Session

```js
cy.session(id, setup)
cy.session(id, setup, { validate, cacheAcrossSpecs: true })
cy.clearAllSavedSessions()
```

## Viewport

```js
cy.viewport(1280, 720)
cy.viewport('iphone-14')
cy.viewport('ipad-2')
cy.viewport('macbook-16')
cy.viewport('samsung-s10')
```

## Other

```js
cy.focused()                        // get focused element
cy.root()                           // get root element
cy.spy(object, 'method')
cy.stub(object, 'method')
cy.stub().as('myStub')
cy.as('alias')                      // alias current subject
cy.invoke('methodName')             // invoke method on subject
cy.its('propertyName')              // get property of subject
cy.spread(fn)                       // spread array as args
cy.each(fn)                         // iterate array
cy.then(fn)                         // callback with subject
cy.pipe(fn)                         // transform subject
cy.end()                            // end chain (return undefined)
```
