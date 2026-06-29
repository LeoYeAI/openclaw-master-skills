# JavaScript Style Guide Skill

A **Prompt-based** AI skill that provides comprehensive JavaScript coding conventions, with additional best-practice rules for modern JavaScript development.

## Overview

This skill automatically activates when you mention or imply **JavaScript** in conversation. It will:

- 🎯 Generate clean, idiomatic JavaScript that follows industry best practices
- 📏 Enforce consistent code style across variables, functions, objects, arrays, classes, modules, and more
- ⚡ Provide guidance on modern JavaScript features like async/await, optional chaining, and nullish coalescing
- 🛡️ Include proper error handling patterns and type safety conventions
- 📝 Follow JSDoc commenting standards

## Skill Type

**Natural Language — Prompt-based Skill**

No special commands or syntax required. The skill is activated through natural language conversation.

## Quick Start

Simply ask a JavaScript-related question or request:

```
"Write a JavaScript function to fetch and cache API data"
"Review my JavaScript code for style issues"
"What's the best way to handle errors in async JavaScript?"
```

The skill will respond with code and explanations that conform to the style guide documented in [SKILL.md](./SKILL.md).

## What's Covered

| Category | Key Rules |
|---|---|
| **References** | `const` > `let` > never `var` |
| **Objects** | Literal syntax, shorthand, spread operator |
| **Arrays** | Literal syntax, higher-order functions, spread |
| **Destructuring** | Object & array destructuring, multiple return values |
| **Strings** | Single quotes, template literals |
| **Functions** | Named expressions, default params, rest params |
| **Arrow Functions** | Implicit return, always use parentheses |
| **Classes** | `class` syntax, `extends`, no prototype manipulation |
| **Modules** | ES modules (`import`/`export`), no wildcard imports |
| **Variables** | One declaration per variable, group `const` then `let` |
| **Comparison** | `===`/`!==`, no nested ternaries |
| **Naming** | camelCase (vars/fns), PascalCase (classes), UPPER_SNAKE (constants) |
| **Async** | `async`/`await` over `.then()`, `Promise.all` for concurrency |
| **Error Handling** | Only throw `Error` objects, custom error classes |
| **Modern JS** | Optional chaining (`?.`), nullish coalescing (`??`) |
| **Formatting** | 2-space indent, trailing commas, always semicolons |

## File Structure

```
.
├── SKILL.md        # Complete style guide rules, activation details, and usage
├── README.md       # This file — overview and quick reference
└── LICENSE         # MIT License
```

## References

- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [MDN JavaScript Reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [ECMAScript Specification](https://tc39.es/ecma262/)

## License

MIT
