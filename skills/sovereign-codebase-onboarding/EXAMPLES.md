# Sovereign Codebase Onboarding -- Examples

## Example 1: "Onboard me to this Express.js API"

### User Prompt

```
I just joined a team that builds a REST API for a food delivery service.
The repo is called "munchies-api". Can you onboard me?
```

### Expected Output

```markdown
## Project Summary

Munchies API is a Node.js REST API built with Express.js that powers a food delivery
platform. It handles restaurant management, menu items, orders, payments (Stripe),
and delivery tracking. The codebase is approximately 18,000 lines across 120 files,
organized in a layered architecture with clear separation between HTTP handling,
business logic, and data access.

## Tech Stack

- Language: TypeScript 5.2
- Framework: Express.js 4.18
- Database: PostgreSQL 15 (via Prisma ORM)
- Cache: Redis 7 (ioredis client)
- Queue: BullMQ (Redis-backed job queue)
- Auth: JWT (jsonwebtoken + passport-jwt)
- Payments: Stripe SDK
- Testing: Jest + Supertest
- CI/CD: GitHub Actions -> AWS ECS (Fargate)

## Architecture Diagram

                         +------------------+
                         |   CloudFront     |
                         |   (CDN + WAF)    |
                         +--------+---------+
                                  |
                         +--------v---------+
                         |   ALB            |
                         +--------+---------+
                                  |
                    +-------------+-------------+
                    |                           |
           +--------v--------+        +--------v--------+
           |  API Server (1) |        |  API Server (2) |
           |  Express + TS   |        |  Express + TS   |
           +--------+--------+        +--------+--------+
                    |                           |
          +---------+---------+---------+-------+
          |                   |                 |
   +------v------+    +------v------+   +------v------+
   | PostgreSQL  |    |   Redis     |   |   Stripe    |
   | (Prisma)    |    | (cache +    |   |   (payment  |
   | 14 tables   |    |  BullMQ)    |   |   gateway)  |
   +-------------+    +------+------+   +-------------+
                             |
                    +--------v---------+
                    |  Worker Process   |
                    |  (BullMQ)         |
                    |  - email sender   |
                    |  - delivery track |
                    |  - analytics sync |
                    +------------------+

## Directory Guide

  munchies-api/
    src/
      api/                      # HTTP layer
        routes/                 # Route definitions (one file per resource)
          auth.routes.ts        # POST /auth/login, /auth/register, /auth/refresh
          restaurants.routes.ts # CRUD /restaurants, /restaurants/:id/menu
          orders.routes.ts      # POST /orders, GET /orders/:id, PATCH /orders/:id/status
          payments.routes.ts    # POST /payments/checkout, webhooks
          users.routes.ts       # GET /users/me, PATCH /users/me
        middleware/              # Express middleware chain
          auth.middleware.ts    # JWT validation, role checking
          validation.ts        # Zod schema validation
          rateLimit.ts         # Rate limiting per endpoint group
          errorHandler.ts      # Central error handler (catches all thrown errors)
        controllers/            # Request handlers (thin -- delegate to services)
      core/                     # Business logic (framework-agnostic)
        services/               # Service classes (one per domain)
          OrderService.ts       # Order creation, status management, cancellation
          PaymentService.ts     # Stripe integration, refunds, invoice generation
          DeliveryService.ts    # Driver assignment, ETA calculation, tracking
          RestaurantService.ts  # Restaurant CRUD, menu management, hours
          AuthService.ts        # Login, registration, token management
        models/                 # Prisma schema + generated types
        errors/                 # Custom error classes (AppError, NotFoundError, etc.)
      workers/                  # Background jobs
        email.worker.ts         # Sends transactional emails via SendGrid
        delivery.worker.ts      # Polls delivery partner API for status updates
        analytics.worker.ts     # Syncs order data to analytics warehouse
      config/                   # Configuration (env vars, feature flags)
        index.ts                # Zod-validated config object
        database.ts             # Prisma client singleton
        redis.ts                # Redis/ioredis client singleton
    prisma/
      schema.prisma             # Database schema (14 tables)
      migrations/               # SQL migration files
      seed.ts                   # Test data seeder
    tests/
      unit/                     # Unit tests (mock dependencies)
      integration/              # API tests (real DB via test containers)
      fixtures/                 # Shared test data factories
    .github/
      workflows/
        ci.yml                  # Lint, test, build on every PR
        deploy.yml              # Deploy to ECS on push to main

## Key Files

| File | Why It Matters |
|------|----------------|
| src/api/routes/orders.routes.ts | The primary revenue path -- order creation |
| src/core/services/PaymentService.ts | 400 lines, handles Stripe + refund logic |
| src/api/middleware/auth.middleware.ts | Every authenticated request passes through here |
| prisma/schema.prisma | The entire data model in one file |
| src/config/index.ts | All env var validation -- check here if startup fails |
| src/api/middleware/errorHandler.ts | How all errors become HTTP responses |

## Data Flow: Placing an Order

  1. Client sends POST /api/orders with { restaurantId, items[], deliveryAddress }
  2. auth.middleware.ts validates JWT, attaches user to request
  3. validation.ts validates body against OrderCreateSchema (Zod)
  4. orders.controller.ts calls OrderService.createOrder(userId, orderData)
  5. OrderService validates restaurant is open (RestaurantService.isOpen)
  6. OrderService calculates total (item prices + delivery fee + tax)
  7. OrderService calls PaymentService.createPaymentIntent(total, userId)
  8. Stripe returns payment intent with client_secret
  9. Order saved to DB with status "pending_payment"
  10. Response: 201 { orderId, clientSecret } -- client completes payment in frontend
  11. Stripe webhook hits POST /api/payments/webhook
  12. PaymentService verifies webhook signature, updates order to "confirmed"
  13. BullMQ job queued: assign delivery driver
  14. BullMQ job queued: send confirmation email

## Patterns and Conventions

- **Architecture:** Layered (routes -> controllers -> services -> models)
- **Naming:** camelCase for variables/functions, PascalCase for classes, kebab-case for files
- **Error handling:** Custom AppError classes thrown in services, caught by errorHandler middleware
- **Validation:** Zod schemas co-located with routes
- **Testing:** Integration tests use Testcontainers for real PostgreSQL
- **Logging:** Pino with request ID correlation

## Day 1 Checklist

- [ ] Install Node 18+, Docker Desktop
- [ ] Clone repo, run `npm install`
- [ ] Copy `.env.example` to `.env`, ask team lead for Stripe test keys
- [ ] Run `docker compose up -d` (starts PostgreSQL + Redis)
- [ ] Run `npx prisma migrate dev` to set up DB
- [ ] Run `npx prisma db seed` to populate test data
- [ ] Run `npm run dev` -- should see "Server running on port 3000"
- [ ] Open http://localhost:3000/health and verify JSON response
- [ ] Run `npm test` -- all 147 tests should pass
- [ ] Trace the order creation flow end-to-end in the code

## Gotchas

1. **Stripe webhooks need ngrok locally.** Run `ngrok http 3000` and set the
   webhook URL in your Stripe dashboard to the ngrok URL + `/api/payments/webhook`.
2. **The seed script creates a test user** with email `test@munchies.dev` and
   password `password123`. Use this for local testing.
3. **Redis must be running** for rate limiting and BullMQ. If Redis is down,
   the API still starts but rate limiting is disabled (silent fail -- this is
   a known tech debt item).
4. **Prisma migrations are not auto-applied.** After pulling new code, always
   run `npx prisma migrate dev`.
```

---

## Example 2: "Map the architecture of this Python monorepo"

### User Prompt

```
We have a Python monorepo with multiple services -- an API, a CLI tool, shared
libraries, and data pipelines. It has grown organically over 3 years and nobody
really understands the full picture anymore. Can you map it out?
```

### Expected Output

```markdown
## Project Summary

DataForge is a Python monorepo containing 4 interconnected components: a FastAPI
web service, a Typer CLI tool, a shared library of data processing utilities, and
an Airflow-based data pipeline. The monorepo uses Poetry workspaces with 3 years
of accumulated code (~42,000 lines). There are significant areas of tech debt,
particularly around inconsistent error handling and duplicated utility code across
services.

## Tech Stack

- Language: Python 3.11
- API: FastAPI 0.104 + Uvicorn
- CLI: Typer 0.9
- Pipeline: Apache Airflow 2.7
- Database: PostgreSQL 15 (SQLAlchemy 2.0 + Alembic)
- Cache: Redis (via redis-py)
- Task Queue: Celery (Redis broker)
- Testing: pytest + pytest-asyncio + factory_boy
- Packaging: Poetry workspaces (monorepo)
- CI/CD: GitLab CI -> AWS ECS + Airflow on MWAA

## Architecture Diagram

  +------------------+     +-------------------+     +-----------------+
  |   Web Frontend   |     |   CLI Users       |     |   Cron/Airflow  |
  |   (React SPA)    |     |   (data team)     |     |   (scheduled)   |
  +--------+---------+     +--------+----------+     +--------+--------+
           |                        |                          |
  +--------v---------+     +--------v----------+     +--------v--------+
  |   FastAPI         |     |   Typer CLI       |     |   Airflow DAGs  |
  |   packages/api/   |     |   packages/cli/   |     |   packages/     |
  |   12 routers      |     |   8 commands      |     |   pipeline/     |
  +--------+----------+     +--------+----------+     |   14 DAGs       |
           |                        |                 +--------+--------+
           +----------+-------------+----------+              |
                      |                        |              |
             +--------v--------+      +--------v--------+    |
             |  Shared Library |      |   Celery Workers |    |
             |  packages/core/ |      |   packages/api/  |    |
             |  - models       |      |   workers/       |    |
             |  - schemas      |      +--------+--------+    |
             |  - utils        |               |              |
             +--------+--------+               |              |
                      |                        |              |
           +----------+----------+-------------+--------------+
           |                     |                    |
    +------v------+       +------v------+      +------v------+
    | PostgreSQL  |       |   Redis     |      |   S3        |
    | 28 tables   |       | (cache +    |      | (raw data + |
    | (Alembic)   |       |  Celery)    |      |  artifacts) |
    +-------------+       +-------------+      +-------------+

## Dependency Map

  packages/core/  (FOUNDATION -- nothing depends on external packages)
    |
    +-- packages/api/ depends on core (models, schemas, utils)
    |     |
    |     +-- packages/api/workers/ depends on api + core
    |
    +-- packages/cli/ depends on core (models, utils)
    |
    +-- packages/pipeline/ depends on core (models, utils)

  WARNING: packages/api/utils/data_helpers.py duplicates 60% of
  packages/core/utils/data.py. This should be consolidated.

## Complexity Hotspots

  [5/5] packages/api/services/etl_service.py -- 1,200 lines. Handles ingestion
        from 6 different data sources with different schemas. Needs refactoring
        into a strategy pattern with one adapter per source.

  [4/5] packages/pipeline/dags/daily_aggregate.py -- 400 lines of SQL string
        templates with complex Jinja logic. Hard to test, hard to debug.

  [4/5] packages/core/models/ -- 28 SQLAlchemy models. Some have 15+ columns
        and complex relationships. The User model alone has 8 relationships.

  [3/5] packages/api/routers/reports.py -- Generates CSV/PDF reports inline
        in the request handler. Should be offloaded to Celery.

  [2/5] packages/cli/ -- Well-structured, each command is a clean function.

## Tech Debt Report

### Critical
- packages/api/config.py loads secrets from env vars with no validation.
  If DATABASE_URL is missing, you get a cryptic SQLAlchemy error 30 seconds
  after startup instead of a clear message at boot.
- No type hints in packages/pipeline/ (all 14 DAG files). Makes refactoring
  dangerous.

### High
- Duplicated utility code between api and core (data_helpers.py vs data.py)
- etl_service.py at 1,200 lines needs to be split
- 23 TODO comments older than 1 year
- Test coverage: api=72%, cli=85%, core=90%, pipeline=31%

### Medium
- Alembic migrations are not tested (no CI step to verify up/down)
- Python 3.11 but still using `typing.Optional` instead of `X | None`
- Mixed use of `print()` and `logging` in CLI and pipeline packages
```

---

## Example 3: "What are the gotchas in this codebase?"

### User Prompt

```
I keep running into weird issues in this Django project. Can you analyze the
codebase and tell me all the gotchas, non-obvious behaviors, and things that
will trip up a new developer?
```

### Expected Output

```markdown
## Gotchas and Pitfalls in Marketplace

### Critical -- Will Cause Bugs If You Don't Know

1. **The User model is NOT Django's default User.**
   `accounts/models.py` defines a custom `User` that extends `AbstractBaseUser`,
   not `AbstractUser`. This means `username` does not exist -- auth is email-only.
   If you write `user.username`, it will raise `AttributeError` at runtime with
   no lint warning.

2. **Soft deletes are invisible.**
   The `Product` and `Order` models use soft deletes (`deleted_at` timestamp).
   The default manager filters these out: `Product.objects.all()` silently
   excludes deleted products. To see deleted records, use
   `Product.all_objects.all()`. This has caused 3 bugs in the last 6 months
   where developers wrote queries that missed deleted records they expected
   to find.

3. **Celery tasks have a 30-second timeout in production but not locally.**
   `settings/production.py` sets `CELERY_TASK_TIME_LIMIT = 30` but
   `settings/local.py` does not set it at all (defaults to no limit). If your
   task works locally but times out in staging, this is why.

4. **Django signals fire on bulk operations inconsistently.**
   `post_save` signals on `Order` trigger payment processing, but
   `Order.objects.bulk_create()` does NOT fire signals. There is a comment
   in `orders/signals.py` that says "DO NOT USE bulk_create FOR ORDERS"
   but it is easy to miss.

### High -- Will Waste Hours If You Don't Know

5. **Two different serializer libraries in use.**
   Half the API uses Django REST Framework serializers (`api/v1/`), the other
   half uses Pydantic models (`api/v2/`). There was a migration that was never
   completed. When adding a new endpoint, check which version directory you
   are in and use the matching approach.

6. **The test database is not migrated automatically.**
   Unlike standard Django, this project uses a custom test runner that loads
   a SQL dump instead of running migrations. The dump is at
   `tests/fixtures/test_db.sql` and must be regenerated after schema changes:
   `python manage.py dump_test_db`. If tests fail with "relation does not
   exist," this is usually why.

7. **Environment variables have different names in different environments.**
   Local uses `DATABASE_URL`, staging uses `DB_CONNECTION_STRING`, production
   uses `RDS_DATABASE_URL`. This is mapped in `settings/__init__.py` but it
   is confusing. There is an open issue (#234) to standardize this.

8. **The `/api/v1/search/` endpoint hits Elasticsearch, not the database.**
   This is not obvious from the code because the Elasticsearch client is
   initialized in a middleware, not imported in the view. If Elasticsearch
   is down, search returns 503 but the rest of the API works fine. Locally,
   you need to run `docker compose --profile search up` to start ES.

### Medium -- Good To Know

9. **Django admin has custom actions that modify production data.**
   The `OrderAdmin` class has a "Force Refund" action that calls the Stripe
   API directly. This is not behind a confirmation dialog. Be very careful
   in the admin panel.

10. **Static files are served by WhiteNoise in production, not Django.**
    `collectstatic` must be run before deploying. If CSS changes are not
    showing up in staging, run `python manage.py collectstatic --noinput`
    and redeploy.

11. **The `utils/` directory is a junk drawer.**
    It has 34 files with no clear organization. Some are imported everywhere
    (`utils/helpers.py` -- 600 lines), others are dead code. Grep before
    adding new utilities to avoid duplication.

12. **Migrations are not squashed.** There are 247 migration files across
    12 apps. Running `migrate` from scratch takes 4 minutes. This is a
    known issue but nobody has squashed them because it is risky.

### Tip

Before making any change, search for the model/function name across the
entire codebase. Django's magic (signals, middleware, template tags, custom
managers) means behavior is often defined far from where you expect it.
```

---

## Example 4: "Generate a Day 1 checklist for this Rust project"

### User Prompt

```
I'm starting on a Rust CLI tool for database migrations. Give me a Day 1 checklist.
```

### Expected Output

```markdown
## Day 1 Checklist for migrate-rs

### Environment Setup (20 min)
- [ ] Install Rust via rustup: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- [ ] Verify: `rustc --version` should show 1.75+
- [ ] Install Docker (needed for integration tests against real databases)
- [ ] Clone: `git clone git@github.com:team/migrate-rs.git && cd migrate-rs`
- [ ] Build: `cargo build` (first build downloads ~180 crates, takes 2-3 min)
- [ ] Run tests: `cargo test` (unit tests only, no Docker needed)
- [ ] Run integration tests: `docker compose up -d && cargo test --features integration`
- [ ] Try it: `cargo run -- --help` to see the CLI interface

### Codebase Orientation (45 min)
- [ ] Read `src/main.rs` -- entry point, uses clap for argument parsing
- [ ] Read `src/lib.rs` -- public API, this is what `main.rs` calls
- [ ] Read `src/migration.rs` -- the core Migration struct and its methods
- [ ] Read `src/drivers/` -- one file per database (postgres.rs, mysql.rs, sqlite.rs)
- [ ] Read `src/errors.rs` -- custom error types using thiserror
- [ ] Run `cargo doc --open` to browse the generated API documentation
- [ ] Read the 5 most recent PRs to understand current development focus

### First Contribution (1-2 hours)
- [ ] Pick an issue labeled "good first issue"
- [ ] Create a branch: `git checkout -b feat/your-change`
- [ ] Make the change
- [ ] Run `cargo fmt` (formatting) and `cargo clippy` (linting)
- [ ] Run `cargo test` and verify all tests pass
- [ ] Push and open a PR -- CI will run clippy, tests, and coverage
```

---

## Example 5: "Explain the data model of this e-commerce app"

### User Prompt

```
I need to understand the database schema of this Rails e-commerce app before
I start building the reporting feature. Can you map it out?
```

### Expected Output

```markdown
## Data Model: ShopEngine (Rails 7 + PostgreSQL)

### Entity Relationship Diagram (ASCII)

  +------------+     +----------------+     +-------------+
  |   users    |<--->| addresses      |     |  categories |
  |------------|  1:N|----------------|     |-------------|
  | id         |     | id             |     | id          |
  | email      |     | user_id (FK)   |     | name        |
  | name       |     | street         |     | slug        |
  | role       |     | city, state    |     | parent_id   |
  | created_at |     | zip, country   |     | position    |
  +-----+------+     | is_default     |     +------+------+
        |             +----------------+            |
        | 1:N                                       | N:M
  +-----v------+                            +-------v-------+
  |   orders   |                            | product_      |
  |------------|     +----------------+     | categories    |
  | id         |  1:N| order_items    |     +-------+-------+
  | user_id    |<--->|----------------|             |
  | status     |     | id             |     +-------v-------+
  | total      |     | order_id (FK)  |     |   products    |
  | address_id |     | product_id(FK) |     |---------------|
  | paid_at    |     | variant_id(FK) |     | id            |
  | shipped_at |     | quantity       |     | name, slug    |
  | created_at |     | unit_price     |     | description   |
  +-----+------+     +----------------+     | price         |
        |                                   | stock_count   |
        | 1:N                               | active        |
  +-----v------+     +----------------+     +-------+-------+
  |  payments  |     |   variants     |             |
  |------------|     |----------------|       1:N   |
  | id         |     | id             |<------------+
  | order_id   |     | product_id(FK) |
  | stripe_id  |     | size           |
  | amount     |     | color          |
  | status     |     | sku            |
  | method     |     | price_override |
  +------------+     | stock_count    |
                     +----------------+

### Key Relationships

- **users -> orders**: One-to-many. A user can have many orders.
- **orders -> order_items**: One-to-many. An order contains multiple line items.
- **products -> variants**: One-to-many. A product can have size/color variants.
- **products <-> categories**: Many-to-many via `product_categories` join table.
- **order_items -> variants**: Each line item references a specific variant.
- **orders -> payments**: One-to-many. An order can have multiple payment attempts.

### Non-Obvious Schema Details

1. **`products.price` is the BASE price.** Variants can override it via
   `variants.price_override`. The actual price logic is in
   `app/models/variant.rb#effective_price` -- it returns `price_override || product.price`.

2. **`orders.total` is denormalized.** It is calculated at order creation time
   and stored. It does NOT auto-update if you change order_items after creation.
   There is a `recalculate_total!` method but it must be called explicitly.

3. **`orders.status` is a state machine** defined in `app/models/concerns/orderable.rb`
   using the `aasm` gem. Valid transitions:
   `pending -> paid -> processing -> shipped -> delivered`
   `pending -> cancelled` and `paid -> refunded` are also valid.

4. **Categories are self-referential** (tree structure via `parent_id`). The
   `ancestry` gem is NOT used -- it is a simple adjacency list. Querying all
   descendants requires recursive CTE or multiple queries.

5. **Soft deletes on products.** `products.active = false` hides them from the
   storefront but preserves them for order history. The default scope in
   `Product` filters to `active: true`.

### For Your Reporting Feature

You will primarily need:
- `orders` (with status filter for completed orders)
- `order_items` (for per-product revenue)
- `products` and `categories` (for grouping)
- `payments` (for payment method breakdown)
- `users` (for customer cohort analysis)

Watch out for: the denormalized `orders.total` may drift from the sum of
`order_items`. For accurate reporting, calculate from line items.
```
