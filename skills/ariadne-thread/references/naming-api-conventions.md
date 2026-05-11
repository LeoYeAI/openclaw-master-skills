# Naming & API Conventions

Detailed rules for intent-oriented naming and API design. Universal principles first, language-specific conventions below.

> **Tier note**: This file is project configuration — read by AI agents during development but rarely updated. Treat as Tier A (always available to AI) but update only when conventions actually change.

## Universal Principles

These apply regardless of programming language:

1. **Names describe intent** — what something does or represents, not how
2. **Consistency within a project** — pick one style and stick to it
3. **Avoid ambiguous names** — `utils`, `helpers`, `misc`, `data`, `manager` indicate unclear responsibility
4. **One concept per file** — a file should be nameable by its single purpose
5. **Max 300 lines per file** (500 for verbose languages like Java/C++)
6. **Group by domain/feature**, not by technical layer (prefer `billing/` over `controllers/`)

## File & Directory Naming by Language

| Language | File Convention | Dir Convention | Example |
|----------|---------------|----------------|---------|
| C++ | `snake_case.h` / `.cpp` (or `.hpp`/`.cc`) | `snake_case/` | `invoice_calculator.cpp` |
| TypeScript | `kebab-case.ts` | `kebab-case/` | `calculate-invoice.ts` |
| Python | `snake_case.py` | `snake_case/` | `invoice_calculator.py` |
| Go | `snake_case.go` | lowercase | `invoice_calculator.go` |
| Rust | `snake_case.rs` | `snake_case/` | `invoice_calculator.rs` |
| Java | `PascalCase.java` | lowercase | `InvoiceCalculator.java` |
| C# | `PascalCase.cs` | `PascalCase/` | `InvoiceCalculator.cs` |

### Voice Coding Considerations

When identifiers may be spoken (e.g. "open user-profile-view", "go to authenticate dot ts"):

- **Prefer kebab-case** for files and directories: `user-profile-view` — each word pronounced separately; easier than `userProfileView` or `user_profile_view`.
- **Avoid similar-sounding neighbors**: `auth_guard` vs `oath_guard`, `rate` vs `wait`, `add` vs `ad` — can confuse speech-to-text.
- **Keep path segments short**: `auth` better than `authentication` at the end of a path; prefer pronounceable, spellable names.
- **Avoid long unbroken identifiers**: `calculate_invoice_total_with_discount` — consider `calc_invoice_total` or splitting into shorter names for verbal reference.

### Forbidden Names (All Languages)

These names indicate unclear responsibility — split into specific files:

- `utils.*` / `helpers.*` / `misc.*` / `common.*`
- `Manager` classes that do everything — split by operation
- Project-wide `types.*` / `constants.*` dumps — co-locate with domain
- Barrel/index files over 20 lines (thin re-exports only)

## Function & Method Naming

### Pattern: Verb + Object + Context

```
[action][Target][Qualifier]

C++:    calculate_invoice_total(), send_welcome_email()
TS/JS:  calculateInvoiceTotal(), sendWelcomeEmail()
Python: calculate_invoice_total(), send_welcome_email()
Go:     CalculateInvoiceTotal(), SendWelcomeEmail()  (exported)
Java:   calculateInvoiceTotal(), sendWelcomeEmail()
```

### Verb Vocabulary (Use Consistently)

| Action | Preferred Verb | Avoid |
|--------|---------------|-------|
| Create | `create` | `make`, `build`, `generate` (unless generating output) |
| Read | `get`, `find`, `fetch` | `read` (ambiguous with file I/O) |
| Update | `update` | `modify`, `change`, `set` (unless setting a single field) |
| Delete | `delete`, `remove` | `destroy`, `kill`, `purge` |
| Validate | `validate` | `check`, `verify` (unless security verification) |
| Transform | `format`, `parse`, `convert` | `process` (too vague) |
| Query | `find`, `search`, `list` | `query` (too low-level) |
| Boolean check | `is`, `has`, `should`, `can` | `check` (not boolean-obvious) |

### Return Type Hints in Names

```
get_user()            → single entity (User)
find_users()          → search result (vector/list, may be empty)
list_active_orders()  → enumeration (list of all matching)
has_permission()      → boolean
count_invoices()      → number/integer
create_session()      → new entity (Session)
```

## Variable & Constant Naming

### Variables

| Type | C++ / Python / Rust | TypeScript / Java / Go |
|------|--------------------|-----------------------|
| Local | `invoice_total` | `invoiceTotal` |
| Boolean | `is_valid`, `has_access` | `isValid`, `hasAccess` |
| Collection | `users`, `line_items` | `users`, `lineItems` |
| Single item | `user`, `line_item` | `user`, `lineItem` |
| Callback | `on_user_created` | `onUserCreated` |

### Constants

| Language | Convention | Example |
|----------|-----------|---------|
| C++ | `constexpr` + SCREAMING_SNAKE or `k` prefix | `constexpr int MAX_RETRY_COUNT = 3;` or `kMaxRetryCount` |
| TypeScript | `const` + SCREAMING_SNAKE | `const MAX_RETRY_COUNT = 3;` |
| Python | Module-level SCREAMING_SNAKE | `MAX_RETRY_COUNT = 3` |
| Go | Exported PascalCase or unexported camelCase | `MaxRetryCount = 3` |
| Rust | `const` + SCREAMING_SNAKE | `const MAX_RETRY_COUNT: u32 = 3;` |
| Java | `static final` + SCREAMING_SNAKE | `static final int MAX_RETRY_COUNT = 3;` |

## Type / Class / Interface Naming

| Language | Class | Interface/Trait | Enum | Type alias |
|----------|-------|----------------|------|------------|
| C++ | `PascalCase` | N/A (abstract class) | `PascalCase` or `SCREAMING` | `using PascalCase = ...` |
| TypeScript | `PascalCase` | `PascalCase` (no I- prefix) | `PascalCase` | `type PascalCase` |
| Python | `PascalCase` | `PascalCase` (ABC/Protocol) | `PascalCase` | `TypeAlias` |
| Go | `PascalCase` | `PascalCase` + `-er` suffix | N/A (const iota) | `PascalCase` |
| Rust | `PascalCase` | `PascalCase` (trait) | `PascalCase` | `type PascalCase` |
| Java | `PascalCase` | `PascalCase` (no I- prefix) | `PascalCase` | N/A |

## Error Type Naming

Error types should be domain-specific and self-descriptive. Avoid generic names like `AppError` or `CustomError`.

| Pattern | Example | When |
|---------|---------|------|
| `[Domain]Error` | `AuthError`, `ValidationError`, `PaymentError` | Domain-specific errors |
| `[Cause]Error` | `TimeoutError`, `RateLimitError`, `NotFoundError` | Technical/infrastructure errors |
| `Invalid[Thing]Error` | `InvalidTokenError`, `InvalidEmailError` | Input validation errors |

```
C++:    class AuthError : public std::runtime_error { ... };
TS:     class AuthError extends Error { ... }
Python: class AuthError(Exception): ...
Go:     var ErrAuth = errors.New("auth: ...")  // or type AuthError struct{}
Rust:   enum AuthError { InvalidCredentials, Expired, ... }
Java:   class AuthError extends RuntimeException { ... }
```

## Event / Message Naming (if applicable)

For event-driven systems, name events as past-tense facts:

| Pattern | Example | Anti-pattern |
|---------|---------|-------------|
| `[Entity][PastVerb]` | `UserCreated`, `OrderShipped`, `PaymentFailed` | `CreateUser`, `HandleOrder` |
| `[Entity][PastVerb]Event` | `UserCreatedEvent` (if suffix needed for clarity) | `UserEvent` (too vague) |

Commands (requests to do something) use imperative form: `CreateUser`, `ShipOrder`, `ProcessPayment`.

## API Design

### REST API (Web Services)

```
[method] /api/v[N]/[resource]/[id]/[sub-resource]

GET    /api/v1/users                    # List
POST   /api/v1/users                    # Create
GET    /api/v1/users/:id                # Read
PATCH  /api/v1/users/:id                # Update
DELETE /api/v1/users/:id                # Delete
GET    /api/v1/users/:id/orders         # Sub-resource
```

Rules:
- Resources: **plural nouns** (`/users`, `/invoices`)
- Actions via **HTTP verbs**, not URL: `POST /invoices` not `POST /createInvoice`
- Max 2 levels nesting
- Version in URL: `/api/v1/...`
- Consistent response shape: `{ data, error, meta }`

### Library / Header API (C++, Rust, Go)

```cpp
// Public header: include/imgproc/filters/gaussian_blur.h
namespace imgproc::filters {

/**
 * @brief Apply Gaussian blur to an image.
 * @param image Input image (not modified)
 * @param sigma Standard deviation of the Gaussian kernel
 * @return Blurred image
 * @throws InvalidImageError if image is empty
 */
Image gaussian_blur(const Image& image, double sigma);

} // namespace imgproc::filters
```

Rules:
- One concept per header
- Namespace mirrors directory structure
- Document preconditions, postconditions, and exceptions/errors
- Use `const&` for input, value/move for output
- Version via namespace or directory (e.g., `imgproc::v2::`)

### gRPC / Protobuf API

```protobuf
service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
}
```

Rules:
- Service name: `PascalCase` + `Service` suffix
- RPC name: `VerbNoun` pattern
- Request/Response: `[RpcName]Request` / `[RpcName]Response`
- Version in package name: `package myapp.v1;`

### CLI API

```
myapp <command> [flags] [args]

myapp user list [--format json|table] [--limit N]
myapp user create --name "..." --email "..."
myapp invoice generate --from 2024-01-01 --to 2024-12-31
```

Rules:
- Commands: `verb` or `noun verb` pattern
- Flags: `--kebab-case`, with short forms for common flags (`-n`, `-v`)
- Consistent output formats: `--format json|table|csv`

## Include / Import Organization

### C++ Include Order

```cpp
// 1. Corresponding header (for .cpp files)
#include "auth/authenticate.h"

// 2. C system headers
#include <cstdlib>
#include <cstring>

// 3. C++ standard library
#include <memory>
#include <string>
#include <vector>

// 4. Third-party libraries
#include <fmt/format.h>
#include <spdlog/spdlog.h>

// 5. Project headers
#include "infra/db/user_store.h"
#include "shared/crypto/hash.h"
```

Separate groups with blank lines. Use `#pragma once` for header guards.

### TypeScript / JavaScript Import Order

```typescript
// 1. Node/runtime built-ins
import { readFile } from "node:fs/promises";

// 2. External packages
import { z } from "zod";
import express from "express";

// 3. Internal absolute imports (from other modules)
import { UserStore } from "@/infra/db/user-store";

// 4. Relative imports (same module)
import { validateInput } from "./validate-input";
import type { AuthConfig } from "./auth.types";
```

### Python Import Order

```python
# 1. Standard library
import os
from pathlib import Path

# 2. Third-party packages
import numpy as np
from sqlalchemy import create_engine

# 3. Local imports
from .validate_input import validate_email
from ..infra.db import UserStore
```

### Go Import Order

```go
import (
    // 1. Standard library
    "context"
    "fmt"

    // 2. Third-party
    "github.com/gin-gonic/gin"

    // 3. Internal
    "myapp/internal/auth"
    "myapp/internal/db"
)
```

Separate groups with blank lines. Each language's standard formatter/linter enforces the convention.
