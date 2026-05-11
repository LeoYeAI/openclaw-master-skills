# TypeScript

A prompt-based skill that provides a comprehensive **TypeScript style guide**. When the user mentions or implies TypeScript, this skill activates to generate standards-compliant TypeScript code and offer best-practice guidance.

## Overview

This skill synthesizes and extends TypeScript coding conventions from multiple industry-leading style guides:

- [clawhub.ai — TypeScript Guide](https://clawhub.ai/ivangdavila/typescript)
- [mkosir — TypeScript Style Guide](https://mkosir.github.io/typescript-style-guide)
- [Platypi — TypeScript Style Guide](https://github.com/Platypi/style_typescript)

It covers **18 topic areas** including naming conventions, types & interfaces, generics, error handling, async patterns, React/JSX, testing, and tooling configuration.

## Activation

This is a **natural language (prompt-based) skill**. It activates automatically whenever the user says or implies **TypeScript** in conversation.

No special commands or syntax are required — just talk about TypeScript.

## What It Does

| Capability | Description |
|---|---|
| **Code Generation** | Generates TypeScript code that follows all style guide rules |
| **Code Review** | Analyses existing TypeScript code against the guide and suggests improvements |
| **JS → TS Conversion** | Converts JavaScript to idiomatic TypeScript with strict types |
| **Best Practice Q&A** | Answers questions about TypeScript conventions and patterns |
| **Project Setup** | Provides recommended `tsconfig.json`, ESLint, and Prettier configurations |

## Quick Start

Just ask a question or make a request involving TypeScript:

```
"Write a TypeScript function to validate email addresses"
"Review my TypeScript code for style issues"
"What's the best practice for TypeScript error handling?"
"Set up a new TypeScript project with strict mode"
"Convert this JavaScript class to TypeScript"
```

## Style Guide Summary

The full guide is in [`SKILL.md`](./SKILL.md). Here's a quick overview of the 18 sections:

| # | Section | Key Points |
|---|---------|------------|
| 1 | General Principles | Strict mode, minimize `any`, immutability by default |
| 2 | Naming Conventions | `camelCase` for variables/functions, `PascalCase` for types/classes, no `I` prefix |
| 3 | Types & Interfaces | `interface` for objects, `type` for unions/intersections, use utility types |
| 4 | Enums | Prefer string enums or string literal unions, avoid numeric auto-increment |
| 5 | Variables & Constants | `const` by default, no `var`, prefer destructuring |
| 6 | Functions | Max 3 parameters, explicit return types, early returns, small functions |
| 7 | Classes | Composition over inheritance, explicit access modifiers, `readonly` properties |
| 8 | Modules & Imports | Named exports preferred, `import type` for types, grouped import order |
| 9 | Generics | Constrained generics, descriptive `T`-prefixed names for complex cases |
| 10 | Error Handling | Custom error classes, typed catch, Result pattern |
| 11 | Async / Await | `async/await` over `.then()`, `Promise.all()` for concurrency |
| 12 | Comments & Documentation | TSDoc for public APIs, no commented-out code |
| 13 | Formatting & Style | 2-space indent, semicolons, single quotes, trailing commas |
| 14 | Null & Undefined | Optional chaining, nullish coalescing, strict null checks |
| 15 | Type Assertions & Guards | Type guards over assertions, discriminated unions |
| 16 | React & JSX | Functional components, `interface` for props, no `React.FC` |
| 17 | Testing | Arrange-Act-Assert, descriptive names, dependency injection |
| 18 | Tooling & Configuration | Recommended `tsconfig.json`, ESLint rules, Prettier config |

## File Structure

```
typescript-skills/
├── SKILL.md          # Full style guide and skill definition
├── README.md         # This file — overview and usage instructions
└── LICENSE           # MIT License
```

## License

MIT — see [LICENSE](./LICENSE) for details.
