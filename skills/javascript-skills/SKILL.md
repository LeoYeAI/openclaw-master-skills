---
name: JavaScript
license: MIT
description: >
  A comprehensive JavaScript style guide skill.
  When activated, it provides best-practice JavaScript coding conventions and generates
  code that strictly follows the style guide, covering variables, functions, objects,
  arrays, classes, modules, async patterns, error handling, naming conventions, and more.
---

# JavaScript Style Guide Skill

## Activation

This skill activates when the user mentions or implies **JavaScript** in their request. Once activated, it:

- Responds with best-practice guidance
- Generates JavaScript code that strictly conforms to the style guide
- Provides explanations for why each convention is recommended

---

## Complete Style Rules

### 1. References

- Use `const` for all references; avoid `var`.
- If you must reassign references, use `let` instead of `var`.
- Both `const` and `let` are block-scoped, whereas `var` is function-scoped.

```javascript
// bad
var count = 1;

// good
const count = 1;
let mutableValue = 1;
mutableValue += 1;
```

### 2. Objects

- Use literal syntax for object creation.
- Use computed property names when creating objects with dynamic property names.
- Use object method shorthand and property value shorthand.
- Group shorthand properties at the beginning of the object declaration.
- Only quote properties that are invalid identifiers.
- Prefer the object spread syntax (`...`) over `Object.assign` to shallow-copy objects.

```javascript
// bad
const item = new Object();

// good
const item = {};

// computed property names
const key = 'name';
const obj = { [key]: 'value' };

// method & property shorthand
const name = 'Alice';
const atom = {
  name,
  value: 1,
  addValue(val) {
    return atom.value + val;
  },
};

// shallow copy
const original = { a: 1, b: 2 };
const copy = { ...original, c: 3 };
```

### 3. Arrays

- Use literal syntax for array creation.
- Use `Array.from` or the spread operator to convert array-like objects.
- Use `return` statements in array method callbacks.
- Use line breaks after the opening bracket and before the closing bracket if the array has multiple lines.

```javascript
// bad
const items = new Array();

// good
const items = [];

// convert iterable
const nodes = Array.from(document.querySelectorAll('.item'));
const uniqueValues = [...new Set(arr)];

// array methods
[1, 2, 3].map((x) => x + 1);

[1, 2, 3].map((x) => {
  const y = x + 1;
  return x * y;
});
```

### 4. Destructuring

- Use object destructuring when accessing multiple properties of an object.
- Use array destructuring.
- Use object destructuring for multiple return values, not array destructuring.

```javascript
// bad
function getFullName(user) {
  const firstName = user.firstName;
  const lastName = user.lastName;
  return `${firstName} ${lastName}`;
}

// good
function getFullName({ firstName, lastName }) {
  return `${firstName} ${lastName}`;
}

// array destructuring
const [first, , third] = [1, 2, 3];

// multiple return values — use object destructuring
function processInput(input) {
  return { left, right, top, bottom };
}
const { left, top } = processInput(input);
```

### 5. Strings

- Use single quotes `''` for strings.
- Use template literals for string interpolation and multi-line strings.
- Never use `eval()` on a string.
- Do not unnecessarily escape characters in strings.

```javascript
// bad
const name = "Alice";
const greeting = 'Hello, ' + name + '!';

// good
const name = 'Alice';
const greeting = `Hello, ${name}!`;
```

### 6. Functions

- Use named function expressions instead of function declarations.
- Wrap immediately invoked function expressions (IIFE) in parentheses.
- Never declare a function in a non-function block (`if`, `while`, etc.).
- Never name a parameter `arguments`.
- Use default parameter syntax rather than mutating function arguments.
- Always put default parameters last.
- Never use the `Function` constructor to create a new function.
- Use the spread operator `...` to call variadic functions.
- Use rest parameters (`...args`) instead of `arguments`.

```javascript
// named function expression
const short = function longUniqueMoreDescriptiveLexicalFoo() {
  // ...
};

// default parameters last
function handleThings(name, opts = {}) {
  // ...
}

// rest parameters
function concatenateAll(...args) {
  return args.join('');
}

// spread to call
const values = [1, 2, 3];
console.log(Math.max(...values));
```

### 7. Arrow Functions

- Use arrow function notation for anonymous functions (callbacks).
- If the function body consists of a single expression, omit the braces and use the implicit return.
- If the expression spans multiple lines, wrap it in parentheses for readability.
- Always include parentheses around arguments for clarity and consistency.

```javascript
// bad
[1, 2, 3].map(function (x) {
  const y = x + 1;
  return x * y;
});

// good
[1, 2, 3].map((x) => {
  const y = x + 1;
  return x * y;
});

// implicit return
[1, 2, 3].map((x) => x * 2);

// multiline implicit return
[1, 2, 3].map((number) => (
  `A long string with the ${number}. It's so long that we don't want it to take up space on the .map line!`
));
```

### 8. Classes & Constructors

- Always use `class`; avoid manipulating `prototype` directly.
- Use `extends` for inheritance.
- Methods can return `this` to enable method chaining.
- Classes have a default constructor if no constructor is specified; an empty constructor or one that just delegates to a parent is unnecessary.
- Avoid duplicate class members.

```javascript
// bad
function Queue(contents = []) {
  this.queue = [...contents];
}
Queue.prototype.pop = function () {
  return this.queue.pop();
};

// good
class Queue {
  constructor(contents = []) {
    this.queue = [...contents];
  }

  pop() {
    return this.queue.pop();
  }
}

// inheritance
class PeekableQueue extends Queue {
  peek() {
    return this.queue[0];
  }
}
```

### 9. Modules

- Always use ES modules (`import`/`export`) over a non-standard module system.
- Do not use wildcard imports.
- Do not export directly from an import.
- Only import from a path in one place.
- Do not export mutable bindings.
- Prefer default export for modules that only export a single thing.
- Put all `import`s above non-import statements.
- Multi-line imports should be indented like multi-line array and object literals.

```javascript
// bad
const utils = require('./utils');
module.exports = utils.fetchData;

// good
import { fetchData } from './utils';
export default fetchData;

// single place import
import { named1, named2 } from 'module';

// multiline
import {
  longNameA,
  longNameB,
  longNameC,
} from 'path/to/module';
```

### 10. Iterators and Generators

- Prefer JavaScript's higher-order functions over `for-in` or `for-of` loops.
- Use `map`, `filter`, `reduce`, `find`, `findIndex`, `every`, `some`, etc.
- Don't use generators for now (if targeting ES5 environments).

```javascript
const numbers = [1, 2, 3, 4, 5];

// bad
let sum = 0;
for (const num of numbers) {
  sum += num;
}

// good
const sum = numbers.reduce((total, num) => total + num, 0);

// filtering
const evens = numbers.filter((num) => num % 2 === 0);
```

### 11. Properties

- Use dot notation when accessing properties.
- Use bracket notation `[]` when accessing properties with a variable.
- Use the exponentiation operator `**` instead of `Math.pow`.

```javascript
const luke = { jedi: true, age: 28 };

// dot notation
const isJedi = luke.jedi;

// bracket notation
const prop = 'jedi';
const isJedi = luke[prop];

// exponentiation
const result = 2 ** 10;
```

### 12. Variables

- Always use `const` or `let`; never use `var`.
- Use one `const` or `let` declaration per variable or assignment.
- Group all `const`s and then group all `let`s.
- Assign variables where you need them, but place them in a reasonable place.
- Don't chain variable assignments.
- Avoid using unary increments (`++`, `--`); use `+= 1` / `-= 1` instead.
- Avoid linebreaks before or after `=` in an assignment.

```javascript
// bad
const items = getItems(),
  goSportsTeam = true,
  dragonball = 'z';

// good
const items = getItems();
const goSportsTeam = true;
const dragonball = 'z';

// group const then let
const a = 1;
const b = 2;
let c = 3;
let d = 4;

// avoid unary
let count = 0;
count += 1;
```

### 13. Hoisting

- `var` declarations get hoisted; `const` and `let` are in Temporal Dead Zone.
- Named function expressions hoist the variable name but not the function body.
- Function declarations hoist the name and the function body.

### 14. Comparison Operators & Equality

- Use `===` and `!==` over `==` and `!=`.
- Use shortcuts for booleans, but explicit comparisons for strings and numbers.
- Use braces to create blocks in `case` and `default` clauses that contain lexical declarations.
- Ternaries should not be nested and generally be single-line expressions.
- Avoid unneeded ternary statements.
- When mixing operators, enclose them in parentheses (except `**`, `+`, `-`).

```javascript
// bad
if (isValid == true) { /* ... */ }
if (name != '') { /* ... */ }

// good
if (isValid) { /* ... */ }
if (name !== '') { /* ... */ }
if (collection.length > 0) { /* ... */ }

// no nested ternaries
const thing = foo === 123 ? bar : foobar;
```

### 15. Blocks

- Use braces with all multiline blocks.
- Put `else` on the same line as the `if` block's closing brace.
- If an `if` block always executes a `return`, the subsequent `else` block is unnecessary.

```javascript
// bad
if (test)
  return false;

// good
if (test) return false;

if (test) {
  return false;
}

// if/else
if (test) {
  thing1();
} else {
  thing2();
}
```

### 16. Control Statements

- If a control statement (`if`, `while`, etc.) gets too long, each grouped condition should be on a new line, with the logical operator at the beginning of the line.
- Don't use selection operators in place of control statements.

```javascript
if (
  foo === 123
  && bar === 'abc'
) {
  thing1();
}
```

### 17. Comments

- Use `/** ... */` for multiline comments.
- Use `//` for single-line comments. Place them on a new line above the subject.
- Start all comments with a space for readability.
- Prefix comments with `FIXME:` or `TODO:` to annotate problems or suggest actions.

```javascript
// good single line
// This is a comment
const active = true;

/**
 * Multiline comment explaining the function.
 * @param {string} tag - The tag name.
 * @returns {Element} The created element.
 */
function make(tag) {
  return document.createElement(tag);
}

// TODO: implement caching
// FIXME: should not use global state
```

### 18. Whitespace

- Use soft tabs (spaces) set to 2 spaces.
- Place 1 space before the leading brace.
- Place 1 space before the opening parenthesis in control statements.
- Set off operators with spaces.
- End files with a single newline character.
- Use indentation when making long method chains (more than 2 method chains).
- Leave a blank line after blocks and before the next statement.
- Do not pad blocks with blank lines.
- Do not use multiple blank lines to pad your code.
- Do not add spaces inside parentheses, brackets.
- Add spaces inside curly braces.

```javascript
// bad
function foo(){
  const name='Alice';
}

// good
function foo() {
  const name = 'Alice';
}

// method chaining
$('#items')
  .find('.selected')
  .highlight()
  .end()
  .find('.open')
  .updateCount();
```

### 19. Commas

- Do **not** use leading commas.
- Use trailing commas (dangling commas) for multiline structures.

```javascript
// bad — leading commas
const hero = {
    firstName: 'Ada'
  , lastName: 'Lovelace'
};

// good — trailing commas
const hero = {
  firstName: 'Ada',
  lastName: 'Lovelace',
};

const heroes = [
  'Batman',
  'Superman',
];
```

### 20. Semicolons

- **Always** use semicolons.

```javascript
// bad
const name = 'Alice'

// good
const name = 'Alice';
```

### 21. Type Casting & Coercion

- Perform type coercion at the beginning of the statement.
- Use `String()` for strings, `Number()` for numbers, `Boolean()` or `!!` for booleans.
- Use `parseInt` always with a radix.

```javascript
const val = '4';

// bad
const totalScore = val + 0;

// good
const totalScore = Number(val);
const inputValue = String(someNum);
const hasAge = Boolean(age);
const hasName = !!name;
const count = parseInt(inputValue, 10);
```

### 22. Naming Conventions

- Avoid single-letter names; be descriptive.
- Use **camelCase** for objects, functions, and instances.
- Use **PascalCase** for classes and constructors.
- Use **UPPERCASE_SNAKE_CASE** for constants that are exported and truly immutable.
- Do not use trailing or leading underscores.
- A base filename should exactly match the name of its default export.
- Use **camelCase** when exporting a function; use **PascalCase** when exporting a class / constructor / singleton / function library / bare object.
- Acronyms and initialisms should always be all uppercased or all lowercased.

```javascript
// bad
const OBJEcttsssss = {};
function c() {}
const u = new user();

// good
const thisIsMyObject = {};
function calculateTotal() {}
const user = new User();

// constants
export const API_BASE_URL = 'https://api.example.com';
export const MAX_RETRY_COUNT = 3;

// filename examples
// file: makeStyleGuide.js → export default function makeStyleGuide() {}
// file: User.js              → export default class User {}
```

### 23. Accessors

- Accessor functions for properties are not required.
- Do not use JavaScript getters/setters as they cause unexpected side effects.
- If you do make accessor functions, use `getVal()` and `setVal('value')`.
- If the property/method is a boolean, use `isVal()` or `hasVal()`.

```javascript
// bad
dragon.age();

// good
dragon.getAge();
dragon.setAge(25);
dragon.isAlive();
dragon.hasWings();
```

### 24. Events

- When attaching data payloads to events, pass an object (hash) instead of a raw value.

```javascript
// bad
emitter.emit('itemUpdate', item.id);

// good
emitter.emit('itemUpdate', { itemId: item.id });
```

### 25. Promises & Async/Await

- Prefer `async`/`await` over chaining `.then()` and `.catch()`.
- Always handle errors with `try...catch` in `async` functions.
- Avoid mixing callbacks and promises.
- Use `Promise.all` for concurrent independent async operations.
- Use `Promise.allSettled` when you need results of all promises regardless of rejection.

```javascript
// bad
function fetchData() {
  return getData()
    .then((data) => parseData(data))
    .then((parsed) => validate(parsed))
    .catch((err) => console.error(err));
}

// good
async function fetchData() {
  try {
    const data = await getData();
    const parsed = await parseData(data);
    return validate(parsed);
  } catch (err) {
    console.error(err);
    throw err;
  }
}

// concurrent operations
async function loadDashboard() {
  const [user, posts, notifications] = await Promise.all([
    fetchUser(),
    fetchPosts(),
    fetchNotifications(),
  ]);
  return { user, posts, notifications };
}
```

### 26. Error Handling

- Only throw `Error` objects (or subclasses of `Error`).
- Always catch errors where they can be meaningfully handled.
- Use custom error classes for domain-specific errors.

```javascript
// bad
throw 'Something went wrong';
throw { message: 'error' };

// good
throw new Error('Something went wrong');

class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}

throw new ValidationError('Invalid email', 'email');
```

### 27. Optional Chaining & Nullish Coalescing

- Use optional chaining (`?.`) to access nested properties that may not exist.
- Use nullish coalescing (`??`) instead of `||` when you want to allow falsy values like `0` or `''`.

```javascript
// bad
const city = user && user.address && user.address.city;
const port = config.port || 3000; // breaks if port is 0

// good
const city = user?.address?.city;
const port = config.port ?? 3000;
```

### 28. Standard Library

- Use `Number.isNaN` instead of global `isNaN`.
- Use `Number.isFinite` instead of global `isFinite`.

```javascript
// bad
isNaN('1.2');
isFinite('2e3');

// good
Number.isNaN('1.2');
Number.isFinite('2e3');
```

---

## Usage

This is a **Prompt-based Skill** (natural language activation).

### How to Use

1. **Automatic Activation**: Simply mention "JavaScript" in your request. The skill will be activated automatically.

2. **Ask for Style Guidance**:
   ```
   "How should I write a JavaScript function that fetches user data?"
   ```

3. **Request Code Review**:
   ```
   "Review this JavaScript code for style issues: [paste code]"
   ```

4. **Generate Compliant Code**:
   ```
   "Write a JavaScript module to handle form validation"
   ```

5. **Ask About Specific Rules**:
   ```
   "What's the correct way to declare variables in JavaScript?"
   "How should I handle async errors in JavaScript?"
   ```

### Examples

**User**: Write a JavaScript utility function to deep clone an object.

**Skill Response**: Generates clean, style-guide-compliant code:

```javascript
/**
 * Deep clones a plain object or array using structured cloning.
 * Falls back to JSON serialization for environments without structuredClone.
 *
 * @param {Object|Array} source - The value to clone.
 * @returns {Object|Array} A deep copy of the source.
 */
function deepClone(source) {
  if (typeof structuredClone === 'function') {
    return structuredClone(source);
  }

  return JSON.parse(JSON.stringify(source));
}

export default deepClone;
```
