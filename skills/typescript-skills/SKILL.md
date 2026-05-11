---
name: typescript
slug: typescript
license: MIT
description: >
  Provide best-practice coding conventions and generate standards-compliant
  TypeScript code.
---

# TypeScript Style Guide Skill

> **Activation**: This skill activates whenever the user says or implies **TypeScript**. It responds
> with standards-compliant TypeScript code and can explain any rule on demand.

---

## Table of Contents

1. [General Principles](#1-general-principles)
2. [Naming Conventions](#2-naming-conventions)
3. [Types & Interfaces](#3-types--interfaces)
4. [Enums](#4-enums)
5. [Variables & Constants](#5-variables--constants)
6. [Functions](#6-functions)
7. [Classes](#7-classes)
8. [Modules & Imports](#8-modules--imports)
9. [Generics](#9-generics)
10. [Error Handling](#10-error-handling)
11. [Async / Await & Promises](#11-async--await--promises)
12. [Comments & Documentation](#12-comments--documentation)
13. [Formatting & Style](#13-formatting--style)
14. [Null & Undefined Handling](#14-null--undefined-handling)
15. [Type Assertions & Guards](#15-type-assertions--guards)
16. [React & JSX (when applicable)](#16-react--jsx-when-applicable)
17. [Testing Conventions](#17-testing-conventions)
18. [Tooling & Configuration](#18-tooling--configuration)

---

## 1. General Principles

- **Strict mode always**: Enable `"strict": true` in `tsconfig.json`. This turns on `noImplicitAny`,
  `strictNullChecks`, `strictFunctionTypes`, and more.
- **Prefer readability over cleverness**: Code is read far more often than written. Favour explicit,
  self-documenting code.
- **Minimise `any`**: Treat every use of `any` as tech debt. Prefer `unknown` when the type is
  truly not known, or use generics.
- **Immutability by default**: Use `const` over `let`; prefer `readonly` properties and
  `ReadonlyArray<T>` / `Readonly<T>` utility types.
- **Single responsibility**: Each file, class, and function should have one clear purpose.
- **Keep files small**: A file should ideally stay under 400 lines. If it grows larger, consider
  splitting it.

---

## 2. Naming Conventions

| Construct               | Convention              | Example                          |
| ----------------------- | ----------------------- | -------------------------------- |
| **Variable / Function** | `camelCase`             | `getUserName`, `isActive`        |
| **Boolean variable**    | `camelCase` with prefix | `isLoading`, `hasAccess`, `canEdit` |
| **Constant (module)**   | `UPPER_SNAKE_CASE`      | `MAX_RETRY_COUNT`, `API_BASE_URL`|
| **Constant (local)**    | `camelCase`             | `const defaultTimeout = 3000`    |
| **Class**               | `PascalCase`            | `UserService`, `HttpClient`      |
| **Interface**           | `PascalCase`            | `UserProfile`, `ApiResponse`     |
| **Type alias**          | `PascalCase`            | `UserId`, `Theme`                |
| **Enum**                | `PascalCase`            | `Direction`, `HttpStatus`        |
| **Enum member**         | `PascalCase`            | `Direction.Up`, `HttpStatus.Ok`  |
| **Generic parameter**   | Single uppercase letter or descriptive `PascalCase` | `T`, `TKey`, `TValue` |
| **File name**           | `kebab-case.ts`         | `user-service.ts`, `api-client.ts`|
| **Test file name**      | `kebab-case.test.ts` or `kebab-case.spec.ts` | `user-service.test.ts` |
| **React component file**| `PascalCase.tsx`        | `UserProfile.tsx`                |
| **Private field**       | `camelCase` (no `_` prefix) | `private count: number`      |

### Additional Naming Rules

- **Do NOT** prefix interfaces with `I` (e.g., ~~`IUser`~~ → `User`).
- **Do NOT** suffix types/interfaces with `Type` or `Interface`.
- Use descriptive names. Avoid single-letter variables except for conventional usages like loop
  indices (`i`, `j`) or generic type parameters (`T`, `K`, `V`).
- Acronyms of 2 characters stay uppercase (`IO`, `ID`); 3+ characters use PascalCase
  (`Http`, `Xml`, `Api`).

---

## 3. Types & Interfaces

### Prefer `interface` for Object Shapes

```typescript
// ✅ Good — use interface for object shapes
interface User {
  readonly id: string;
  name: string;
  email: string;
}

// ✅ Good — use type for unions, intersections, mapped types
type Status = 'active' | 'inactive' | 'suspended';
type Result<T> = Success<T> | Failure;
```

### When to Use `type` vs `interface`

| Use `interface` when …                        | Use `type` when …                          |
| ---------------------------------------------- | ------------------------------------------ |
| Defining the shape of an object or class       | Creating union or intersection types       |
| You want declaration merging                   | Using mapped / conditional types           |
| Extending other interfaces                     | Aliasing primitive or tuple types          |

### Rules

- Always annotate function return types explicitly for public APIs.
- Let TypeScript infer types for local variables when the type is obvious.
- Prefer `type` over `interface` for function signatures:
  ```typescript
  type Comparator<T> = (a: T, b: T) => number;
  ```
- Avoid empty interfaces. If extending, include at least a comment explaining intent.
- Use `Record<K, V>` instead of `{ [key: string]: V }`.
- Use utility types (`Partial<T>`, `Pick<T, K>`, `Omit<T, K>`, `Required<T>`) to derive types
  rather than duplicating.

---

## 4. Enums

### Prefer String Enums

```typescript
// ✅ Good — string enum for readability and debuggability
enum Direction {
  Up = 'UP',
  Down = 'DOWN',
  Left = 'LEFT',
  Right = 'RIGHT',
}
```

### When to Use `const` Enum or Union Types

```typescript
// ✅ Good — const enum for zero-runtime-cost enums (no reverse mapping needed)
const enum HttpMethod {
  Get = 'GET',
  Post = 'POST',
  Put = 'PUT',
  Delete = 'DELETE',
}

// ✅ Also good — string literal union (simpler, tree-shakeable)
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
```

### Rules

- **Do NOT** use numeric enums without explicit values (auto-increment is fragile).
- Prefer **string literal union types** over enums when the set is small and no namespace features
  are needed.
- Never mix string and numeric members in the same enum.

---

## 5. Variables & Constants

```typescript
// ✅ Good
const maxRetries = 3;
const baseUrl = 'https://api.example.com';
let currentAttempt = 0;

// ❌ Bad — using var
var legacyValue = 'old';

// ❌ Bad — using let when value never changes
let neverReassigned = 42;
```

### Rules

- **Always use `const`** unless the variable needs reassignment; then use `let`.
- **Never use `var`**.
- Declare variables as close to their first usage as possible.
- One variable declaration per statement.
- Prefer destructuring for extracting properties:
  ```typescript
  // ✅ Good
  const { name, age } = user;

  // ❌ Bad
  const name = user.name;
  const age = user.age;
  ```
- Use `as const` for immutable literal objects / arrays:
  ```typescript
  const ROUTES = {
    home: '/',
    about: '/about',
    contact: '/contact',
  } as const;
  ```

---

## 6. Functions

### Function Declarations

```typescript
// ✅ Good — explicit return type for public functions
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

// ✅ Good — arrow function for callbacks / short lambdas
const double = (n: number): number => n * 2;

// ✅ Good — use default parameters instead of optional + fallback
function createUser(name: string, role: Role = Role.Viewer): User {
  // ...
}
```

### Rules

- **Annotate return types** for all exported / public functions.
- Prefer **arrow functions** for callbacks and inline functions.
- Prefer **function declarations** for top-level named functions (they are hoisted and more
  readable in stack traces).
- **Maximum parameters**: 3. If more are needed, group them into an options object:
  ```typescript
  // ✅ Good
  interface CreateUserOptions {
    name: string;
    email: string;
    role?: Role;
    department?: string;
  }
  function createUser(options: CreateUserOptions): User { ... }

  // ❌ Bad — too many positional parameters
  function createUser(name: string, email: string, role: Role, dept: string): User { ... }
  ```
- Do **not** use `arguments`; use rest parameters (`...args`) instead.
- Avoid `Function` type. Use specific function signatures.
- Keep functions small — ideally under 30 lines of logic.
- Functions should **do one thing**.
- Prefer **early returns** to reduce nesting:
  ```typescript
  // ✅ Good
  function getDiscount(user: User): number {
    if (!user.isPremium) return 0;
    if (user.yearsActive < 2) return 5;
    return 10;
  }
  ```

---

## 7. Classes

```typescript
// ✅ Good
class UserService {
  private readonly repository: UserRepository;

  constructor(repository: UserRepository) {
    this.repository = repository;
  }

  async findById(id: string): Promise<User | undefined> {
    return this.repository.get(id);
  }
}
```

### Rules

- Prefer **composition over inheritance**.
- Use `readonly` for properties that should not change after construction.
- Member ordering:
  1. Static fields
  2. Instance fields
  3. Constructor
  4. Static methods
  5. Public methods
  6. Protected methods
  7. Private methods
- Use **explicit access modifiers** (`public`, `protected`, `private`) on every member.
- **Do NOT** prefix private members with `_`. TypeScript's `private` keyword is sufficient.
- Use `#` (ES private fields) when true runtime privacy is required.
- Prefer **parameter properties** for simple constructor-only assignments:
  ```typescript
  class Logger {
    constructor(private readonly prefix: string) {}
  }
  ```
- Avoid classes with only static methods — use plain functions in a module instead.
- Implement interfaces explicitly:
  ```typescript
  class UserRepositoryImpl implements UserRepository { ... }
  ```

---

## 8. Modules & Imports

```typescript
// ✅ Good — named exports
export function parseConfig(raw: string): Config { ... }
export interface Config { ... }

// ✅ Good — re-export barrel file (index.ts)
export { parseConfig } from './parse-config';
export type { Config } from './parse-config';
```

### Rules

- **Prefer named exports** over default exports (better refactoring, auto-import support).
- Use default exports only for React components if the project convention requires it.
- Use `import type` / `export type` for type-only imports to help bundlers tree-shake:
  ```typescript
  import type { User } from './user';
  ```
- Group and order imports:
  1. Node built-ins (`node:fs`, `node:path`)
  2. External packages (`react`, `lodash`)
  3. Internal aliases (`@/utils`, `@/components`)
  4. Relative parent (`../`)
  5. Relative sibling (`./`)
- Separate each group with a blank line.
- **Do NOT** use wildcard imports (`import * as`) unless re-exporting a module namespace.
- Keep barrel files (`index.ts`) thin — do not add logic.

---

## 9. Generics

```typescript
// ✅ Good — descriptive when intent is ambiguous
function merge<TTarget, TSource>(target: TTarget, source: TSource): TTarget & TSource {
  return { ...target, ...source };
}

// ✅ Good — single-letter when intent is obvious
function identity<T>(value: T): T {
  return value;
}

// ✅ Good — constrained generics
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

### Rules

- Use a **single uppercase letter** (`T`, `U`, `K`, `V`) for simple generics.
- Use **descriptive PascalCase prefixed with `T`** (`TKey`, `TValue`, `TResult`) when there are
  multiple type parameters or the purpose is not obvious.
- Always add constraints when possible (`<T extends SomeType>`).
- Avoid unnecessary generics — if a type parameter is used only once, it's likely not needed.
- Prefer generic utility types (`Array<T>`, `Promise<T>`, `Map<K, V>`) over their shorthand where
  readability benefits.

---

## 10. Error Handling

```typescript
// ✅ Good — custom error class
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
  ) {
    super(message);
    this.name = 'AppError';
  }
}

// ✅ Good — typed error handling
function parseJson<T>(raw: string): T {
  try {
    return JSON.parse(raw) as T;
  } catch (error) {
    throw new AppError(
      `Failed to parse JSON: ${error instanceof Error ? error.message : String(error)}`,
      'PARSE_ERROR',
      400,
    );
  }
}
```

### Rules

- **Never** swallow errors silently (empty `catch` blocks).
- Use **custom error classes** that extend `Error` for domain-specific errors.
- Type the `catch` variable as `unknown` (default in TS 4.4+) and narrow before use.
- Prefer **Result / Either patterns** for expected failures in libraries:
  ```typescript
  type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };
  ```
- Always clean up resources in `finally` blocks or use disposable patterns.
- Log errors with sufficient context (operation name, input summary, stack trace).

---

## 11. Async / Await & Promises

```typescript
// ✅ Good — async/await
async function fetchUser(id: string): Promise<User> {
  const response = await httpClient.get<User>(`/users/${id}`);
  return response.data;
}

// ✅ Good — parallel execution
async function fetchDashboard(userId: string): Promise<Dashboard> {
  const [user, posts, notifications] = await Promise.all([
    fetchUser(userId),
    fetchPosts(userId),
    fetchNotifications(userId),
  ]);
  return { user, posts, notifications };
}
```

### Rules

- **Prefer `async/await`** over `.then()` chains for readability.
- Always annotate return types as `Promise<T>`.
- Use `Promise.all()` for independent concurrent operations.
- Use `Promise.allSettled()` when failures should not abort sibling operations.
- **Never** use `new Promise()` when an async function suffices (avoid the explicit-construction
  antipattern).
- Avoid `async void` functions — they cannot be `await`-ed and swallow errors.
  Exception: event handlers where the framework requires `void`.
- Prefer `for...of` with `await` for sequential async iteration, not `forEach`.

---

## 12. Comments & Documentation

```typescript
/**
 * Calculate the compound interest for a principal amount.
 *
 * @param principal - The initial amount of money.
 * @param rate - The annual interest rate (decimal, e.g. 0.05 for 5%).
 * @param times - Number of times interest is compounded per year.
 * @param years - Number of years the money is invested.
 * @returns The total amount after compound interest.
 *
 * @example
 * ```typescript
 * const total = compoundInterest(1000, 0.05, 12, 10);
 * // total ≈ 1647.01
 * ```
 */
function compoundInterest(
  principal: number,
  rate: number,
  times: number,
  years: number,
): number {
  return principal * Math.pow(1 + rate / times, times * years);
}
```

### Rules

- Use **TSDoc** (`/** */`) for all public APIs, exported functions, classes, interfaces, and types.
- Include `@param`, `@returns`, `@throws`, and `@example` tags where applicable.
- **Do NOT** comment obvious code. The code should be self-documenting.
- Use `// TODO:` with a ticket number for planned improvements.
- Use `// FIXME:` for known issues that need resolution.
- Use `// HACK:` for workarounds that should be revisited.
- Never leave commented-out code in the main branch.
- Place file-level comments at the top if the module's purpose is not obvious from its name.
- Keep comments up-to-date with code changes.

---

## 13. Formatting & Style

### General

- **Indentation**: 2 spaces (no tabs).
- **Semicolons**: Required at the end of every statement.
- **Quotes**: Single quotes (`'`) for strings; backticks (`` ` ``) for template literals.
- **Trailing commas**: Always use in multi-line constructs (arrays, objects, parameters, generics).
- **Max line length**: 100 characters (soft limit), 120 characters (hard limit).
- **Braces**: Required for all control structures, even single-line bodies.
- **Blank lines**: One blank line between top-level declarations; no multiple consecutive blank lines.

### Specific Patterns

```typescript
// ✅ Good — braces always, even for single-line if
if (isValid) {
  process();
}

// ❌ Bad
if (isValid) process();

// ✅ Good — trailing comma
const config = {
  host: 'localhost',
  port: 3000,
  debug: true,
};

// ✅ Good — consistent object shorthand
const name = 'Alice';
const user = { name, age: 30 };
```

### Tooling

- Use **Prettier** for auto-formatting with the following baseline config:
  ```json
  {
    "semi": true,
    "singleQuote": true,
    "trailingComma": "all",
    "printWidth": 100,
    "tabWidth": 2,
    "arrowParens": "always"
  }
  ```
- Use **ESLint** with `@typescript-eslint/eslint-plugin` and
  `@typescript-eslint/parser` for linting.

---

## 14. Null & Undefined Handling

```typescript
// ✅ Good — optional chaining
const city = user?.address?.city;

// ✅ Good — nullish coalescing
const displayName = user.nickname ?? user.name ?? 'Anonymous';

// ✅ Good — explicit null checks for critical paths
function getUser(id: string): User {
  const user = repository.findById(id);
  if (user === undefined) {
    throw new AppError(`User not found: ${id}`, 'USER_NOT_FOUND', 404);
  }
  return user;
}
```

### Rules

- **Enable `strictNullChecks`** (included in `strict` mode).
- Prefer `undefined` over `null` as the "absence of value" indicator, unless interacting with
  external APIs that use `null`.
- Use **optional chaining** (`?.`) and **nullish coalescing** (`??`) instead of manual checks.
- **Do NOT** use non-null assertion (`!`) unless you can prove the value is always defined (add a
  comment explaining why).
- Prefer the `satisfies` operator (TS 5.0+) to validate types without widening.

---

## 15. Type Assertions & Guards

```typescript
// ✅ Good — type guard function
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value
  );
}

// ✅ Good — discriminated union
interface Success<T> {
  kind: 'success';
  data: T;
}
interface Failure {
  kind: 'failure';
  error: Error;
}
type Result<T> = Success<T> | Failure;

function handleResult<T>(result: Result<T>): T {
  switch (result.kind) {
    case 'success':
      return result.data;
    case 'failure':
      throw result.error;
  }
}
```

### Rules

- **Prefer type guards** (`is` keyword) over type assertions (`as`).
- Use `as const` for literal narrowing, not `as SpecificType`.
- Use **discriminated unions** with a `kind` / `type` field for state machines and result types.
- Avoid `as unknown as T` double assertions — they are almost always a design smell.
- When assertions are necessary, add a comment justifying them.
- Use `satisfies` for type validation without assertion:
  ```typescript
  const palette = {
    red: [255, 0, 0],
    green: '#00ff00',
  } satisfies Record<string, string | number[]>;
  ```

---

## 16. React & JSX (when applicable)

```tsx
// ✅ Good — functional component with explicit props type
interface UserCardProps {
  readonly user: User;
  readonly onSelect?: (userId: string) => void;
}

export function UserCard({ user, onSelect }: UserCardProps): React.ReactElement {
  const handleClick = useCallback(() => {
    onSelect?.(user.id);
  }, [onSelect, user.id]);

  return (
    <div className="user-card" onClick={handleClick} role="button" tabIndex={0}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
}
```

### Rules

- Use **function declarations** or **named function expressions** for components (not anonymous).
- Define props as an `interface` (e.g., `UserCardProps`), not inline.
- Mark all props as `readonly`.
- **Do NOT** use `React.FC` — it is discouraged since React 18.
- Use `React.ReactElement` or `React.ReactNode` as return type annotation.
- Colocate styles, tests, and types with the component when practical.
- Prefer **controlled components** over uncontrolled.
- Memoize expensive computations with `useMemo`, stable callbacks with `useCallback`.
- Extract custom hooks when logic is reused across components.
- Component file structure:
  1. Imports
  2. Types / Interfaces
  3. Constants
  4. Component function
  5. Helper functions (private to the module)

---

## 17. Testing Conventions

```typescript
// ✅ Good — descriptive test structure
describe('UserService', () => {
  describe('findById', () => {
    it('should return the user when the id exists', async () => {
      const user = await service.findById('user-1');
      expect(user).toEqual(expect.objectContaining({ id: 'user-1' }));
    });

    it('should return undefined when the id does not exist', async () => {
      const user = await service.findById('non-existent');
      expect(user).toBeUndefined();
    });
  });
});
```

### Rules

- Test files are colocated or in a `__tests__` directory.
- Name test files `*.test.ts` or `*.spec.ts`.
- Follow the **Arrange → Act → Assert** pattern.
- One assertion concept per test (multiple `expect` calls are okay if they test one logical
  assertion).
- Use **descriptive test names** that read like a sentence.
- Mock external dependencies; do NOT mock the module under test.
- Prefer **dependency injection** to make code testable.
- Aim for high test coverage on business logic; don't chase 100% on boilerplate.
- Use `jest.fn()` or equivalent for spies/mocks; type them properly:
  ```typescript
  const mockFetch = jest.fn<Promise<User>, [string]>();
  ```

---

## 18. Tooling & Configuration

### Recommended `tsconfig.json` (Baseline)

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### Recommended ESLint Rules

| Rule                                     | Setting   |
| ---------------------------------------- | --------- |
| `@typescript-eslint/no-explicit-any`     | `error`   |
| `@typescript-eslint/explicit-function-return-type` | `warn` (for exported functions) |
| `@typescript-eslint/no-unused-vars`      | `error`   |
| `@typescript-eslint/consistent-type-imports` | `error` |
| `@typescript-eslint/no-non-null-assertion` | `warn`  |
| `@typescript-eslint/prefer-nullish-coalescing` | `error` |
| `@typescript-eslint/prefer-optional-chain` | `error` |
| `@typescript-eslint/strict-boolean-expressions` | `warn` |
| `@typescript-eslint/naming-convention`   | `error` (configured per construct) |

---

## Usage

### Natural Language Activation

Simply mention **TypeScript** in your conversation — the skill activates automatically.

**Example prompts:**

| Prompt | Skill Response |
|---|---|
| "Write a TypeScript function to merge two objects deeply" | Generates a fully typed, standards-compliant `deepMerge<T, U>()` function following all rules above. |
| "Review my TypeScript code for style issues" | Analyses the provided code against this guide and suggests improvements. |
| "Convert this JavaScript to TypeScript" | Converts code, adds strict types, interfaces, and follows all naming / formatting conventions. |
| "What's the TypeScript best practice for error handling?" | Explains the Result pattern, custom error classes, and typed catch blocks per §10. |
| "Create a TypeScript React component for a data table" | Generates a well-typed functional component following §16 React rules with proper props interface. |
| "Set up a new TypeScript project" | Provides `tsconfig.json`, ESLint config, Prettier config, and project structure following §18. |

### Inline Rule References

You can ask about any specific section:

- *"Explain TypeScript naming conventions"* → References §2
- *"How should I handle null in TypeScript?"* → References §14
- *"Show me TypeScript generic best practices"* → References §9
