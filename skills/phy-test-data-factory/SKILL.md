---
name: phy-test-data-factory
description: Schema-driven test data factory generator. Reads your database schema or model definitions — Prisma schema, SQLAlchemy models, Django models, TypeORM entities, Zod schemas, Pydantic models, or raw SQL DDL — and generates ready-to-use factory functions with realistic fake data. Outputs TypeScript factory files using Faker.js, Python conftest.py using factory_boy + Faker, or raw SQL INSERT seed scripts. Respects foreign key relationships (seeds parents before children), handles enums, nullable fields, unique constraints, and generates edge-case variants (empty strings, max-length values, boundary dates). Zero external API — pure local file analysis + code generation. Triggers on "generate test data", "seed database", "test fixtures", "factory functions", "fake data from schema", "/test-data-factory".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - testing
    - test-data
    - fixtures
    - faker
    - factory-boy
    - prisma
    - sqlalchemy
    - django
    - seed-data
    - developer-tools
---

# Test Data Factory

Writing test setup is slower than writing the test itself. You have a `User` model with 12 fields, a `Post` model that requires a User, and an `Order` model that requires both. Every test file re-invents the same `createTestUser()` boilerplate — with slightly different hardcoded values that don't cover edge cases.

Paste your schema and get a complete factory module: realistic Faker-powered defaults for every field, relationship-aware ordering, and one-line overrides for specific test scenarios.

**Reads any schema format. Outputs TypeScript, Python, or SQL. Zero external APIs.**

---

## Trigger Phrases

- "generate test data", "seed my database", "test fixtures"
- "factory functions", "fake data from schema", "test data setup"
- "create test factories", "Faker from schema", "factory_boy setup"
- "generate seed data", "populate test database"
- "I need fake users/orders/products for testing"
- "/test-data-factory"

---

## How to Provide Input

```bash
# Option 1: Prisma schema
/test-data-factory schema.prisma
/test-data-factory prisma/schema.prisma

# Option 2: SQLAlchemy / Django models file
/test-data-factory models.py
/test-data-factory app/models.py

# Option 3: TypeORM entities directory
/test-data-factory src/entities/

# Option 4: Zod schemas file
/test-data-factory src/schemas/user.schema.ts

# Option 5: Raw SQL DDL
/test-data-factory --sql migrations/001_initial.sql

# Option 6: Output format override
/test-data-factory schema.prisma --output typescript
/test-data-factory models.py --output python
/test-data-factory schema.prisma --output sql

# Option 7: Include edge-case variants
/test-data-factory schema.prisma --edge-cases

# Option 8: Specific count
/test-data-factory schema.prisma --count 50
```

---

## Step 1: Detect and Parse Schema

### Prisma Schema Parser

```python
import re
from dataclasses import dataclass, field
from typing import Any

@dataclass
class PrismaField:
    name: str
    type: str
    is_optional: bool = False
    is_list: bool = False
    is_id: bool = False
    is_unique: bool = False
    is_auto: bool = False
    default: Any = None
    relation: str | None = None
    enum_values: list[str] = field(default_factory=list)

def parse_prisma_schema(schema_text: str) -> dict:
    """Parse Prisma schema into model definitions."""
    models = {}
    enums = {}

    # Parse enums first
    for enum_match in re.finditer(r'enum\s+(\w+)\s*\{([^}]+)\}', schema_text, re.DOTALL):
        enum_name = enum_match.group(1)
        values = [v.strip() for v in enum_match.group(2).split('\n')
                  if v.strip() and not v.strip().startswith('//')]
        enums[enum_name] = values

    # Parse models
    for model_match in re.finditer(r'model\s+(\w+)\s*\{([^}]+)\}', schema_text, re.DOTALL):
        model_name = model_match.group(1)
        body = model_match.group(2)
        fields = []

        for line in body.split('\n'):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('@@'):
                continue
            # Parse field: name type? modifiers
            parts = line.split()
            if len(parts) < 2:
                continue

            fname = parts[0]
            ftype_raw = parts[1]

            is_optional = ftype_raw.endswith('?')
            is_list = ftype_raw.endswith('[]')
            ftype = ftype_raw.rstrip('?').rstrip('[]')

            is_id = '@id' in line
            is_unique = '@unique' in line
            is_auto = '@default(autoincrement())' in line or '@default(auto())' in line or '@default(uuid())' in line or '@default(cuid())' in line
            is_relation = '@relation' in line

            default_match = re.search(r'@default\((.+?)\)', line)
            default_val = default_match.group(1) if default_match else None

            fields.append(PrismaField(
                name=fname,
                type=ftype,
                is_optional=is_optional,
                is_list=is_list,
                is_id=is_id,
                is_unique=is_unique,
                is_auto=is_auto,
                default=default_val,
                relation=ftype if is_relation and ftype[0].isupper() else None,
                enum_values=enums.get(ftype, []),
            ))

        models[model_name] = fields

    return {'models': models, 'enums': enums}
```

### SQL DDL Parser

```python
def parse_sql_ddl(sql_text: str) -> dict:
    """Parse CREATE TABLE statements."""
    models = {}

    for table_match in re.finditer(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?(\w+)[`"]?\s*\(([^;]+)\)',
        sql_text, re.IGNORECASE | re.DOTALL
    ):
        table_name = table_match.group(1)
        columns_text = table_match.group(2)
        fields = []

        for col_line in columns_text.split(','):
            col_line = col_line.strip()
            if not col_line or col_line.upper().startswith(('PRIMARY', 'FOREIGN', 'UNIQUE', 'INDEX', 'KEY', 'CONSTRAINT')):
                continue

            col_match = re.match(r'[`"]?(\w+)[`"]?\s+(\w+)(\(\d+\))?(.*)$', col_line, re.IGNORECASE)
            if not col_match:
                continue

            fname = col_match.group(1)
            ftype = col_match.group(2).upper()
            rest = col_match.group(4).upper()
            is_nullable = 'NOT NULL' not in rest
            is_auto = 'AUTO_INCREMENT' in rest or 'SERIAL' in ftype
            is_unique = 'UNIQUE' in rest

            fields.append(PrismaField(
                name=fname,
                type=ftype,
                is_optional=is_nullable,
                is_auto=is_auto,
                is_unique=is_unique,
            ))

        models[table_name] = fields

    return {'models': models, 'enums': {}}
```

---

## Step 2: Map Types to Faker Functions

```python
# Prisma/TypeScript type → Faker.js function
FAKER_JS_MAP = {
    # Primitives
    'String':   'faker.lorem.words(3)',
    'Int':      'faker.number.int({ min: 1, max: 10000 })',
    'Float':    'faker.number.float({ min: 0, max: 1000, fractionDigits: 2 })',
    'Boolean':  'faker.datatype.boolean()',
    'DateTime': 'faker.date.recent({ days: 30 })',
    'BigInt':   'BigInt(faker.number.int({ min: 1, max: 1000000 }))',
    'Json':     '{}',
    'Bytes':    'Buffer.from(faker.string.alphanumeric(16))',

    # Semantic overrides (based on field name)
    'email':       'faker.internet.email()',
    'name':        'faker.person.fullName()',
    'firstName':   'faker.person.firstName()',
    'lastName':    'faker.person.lastName()',
    'username':    'faker.internet.username()',
    'password':    'faker.internet.password({ length: 12 })',
    'phone':       'faker.phone.number()',
    'address':     'faker.location.streetAddress()',
    'city':        'faker.location.city()',
    'country':     'faker.location.country()',
    'zipCode':     'faker.location.zipCode()',
    'url':         'faker.internet.url()',
    'imageUrl':    'faker.image.url()',
    'avatar':      'faker.image.avatar()',
    'bio':         'faker.lorem.paragraph()',
    'description': 'faker.lorem.sentences(2)',
    'title':       'faker.lorem.sentence()',
    'slug':        'faker.helpers.slugify(faker.lorem.words(3))',
    'color':       'faker.color.human()',
    'uuid':        'faker.string.uuid()',
    'ip':          'faker.internet.ip()',
    'createdAt':   'faker.date.past({ years: 1 })',
    'updatedAt':   'new Date()',
    'deletedAt':   'null',
    'publishedAt': 'faker.date.recent({ days: 90 })',
    'price':       'faker.number.float({ min: 0.99, max: 999.99, fractionDigits: 2 })',
    'amount':      'faker.number.int({ min: 1, max: 10000 })',
    'quantity':    'faker.number.int({ min: 1, max: 100 })',
    'score':       'faker.number.float({ min: 0, max: 5, fractionDigits: 1 })',
    'rating':      'faker.number.int({ min: 1, max: 5 })',
    'status':      None,  # replaced by enum values
    'role':        None,  # replaced by enum values
    'type':        None,  # replaced by enum values
}

# Same mapping for Python Faker
FAKER_PY_MAP = {
    'String': "fake.sentence(nb_words=3)",
    'str':    "fake.sentence(nb_words=3)",
    'Int':    "fake.random_int(min=1, max=10000)",
    'int':    "fake.random_int(min=1, max=10000)",
    'Float':  "round(random.uniform(0, 1000), 2)",
    'float':  "round(random.uniform(0, 1000), 2)",
    'bool':   "fake.boolean()",
    'datetime': "fake.date_time_this_year()",
    'email':  "fake.email()",
    'name':   "fake.name()",
    'phone':  "fake.phone_number()",
    'url':    "fake.url()",
    'uuid':   "str(uuid.uuid4())",
    'price':  "round(random.uniform(0.99, 999.99), 2)",
}

def get_faker_value(field_name: str, field_type: str, enum_values: list, lang: str = 'ts') -> str:
    """Get the Faker expression for a field."""
    mapper = FAKER_JS_MAP if lang == 'ts' else FAKER_PY_MAP
    prefix = 'faker.' if lang == 'ts' else 'fake.'

    # Enum field: pick from enum values
    if enum_values:
        if lang == 'ts':
            return f'faker.helpers.arrayElement([{", ".join(repr(v) for v in enum_values)}])'
        else:
            return f'random.choice([{", ".join(repr(v) for v in enum_values)}])'

    # Check semantic field name first
    for semantic_key, expr in mapper.items():
        if field_name.lower().endswith(semantic_key.lower()) or field_name.lower() == semantic_key.lower():
            if expr:
                return expr

    # Fall back to type mapping
    return mapper.get(field_type, f'"TODO: {field_type}"')
```

---

## Step 3: Detect Relationship Order

Topologically sort models so parents are created before children:

```python
def topological_sort(models: dict) -> list[str]:
    """Return model names in dependency order (parents first)."""
    from collections import defaultdict, deque

    graph = defaultdict(list)
    in_degree = {name: 0 for name in models}

    for model_name, fields in models.items():
        for field in fields:
            if field.relation and field.relation in models and not field.is_optional:
                # model_name depends on field.relation
                graph[field.relation].append(model_name)
                in_degree[model_name] += 1

    queue = deque([m for m, d in in_degree.items() if d == 0])
    order = []

    while queue:
        model = queue.popleft()
        order.append(model)
        for dependent in graph[model]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # Append any remaining (circular deps)
    for m in models:
        if m not in order:
            order.append(m)

    return order
```

---

## Step 4: Generate Factory Code

### TypeScript Output (Faker.js)

```typescript
// Generated by phy-test-data-factory
// Install: npm install -D @faker-js/faker

import { faker } from '@faker-js/faker';
import { PrismaClient, UserRole, PostStatus } from '@prisma/client';

const prisma = new PrismaClient();

// ─── User Factory ────────────────────────────────────────────────────────────

export interface CreateUserOptions {
  id?: string;
  email?: string;
  name?: string;
  role?: UserRole;
  createdAt?: Date;
}

export function buildUser(overrides: CreateUserOptions = {}) {
  return {
    id:        faker.string.uuid(),
    email:     faker.internet.email(),
    name:      faker.person.fullName(),
    username:  faker.internet.username(),
    password:  faker.internet.password({ length: 12 }),
    bio:       faker.lorem.paragraph(),
    avatarUrl: faker.image.avatar(),
    role:      faker.helpers.arrayElement(['USER', 'ADMIN', 'MODERATOR'] as UserRole[]),
    isActive:  true,
    createdAt: faker.date.past({ years: 1 }),
    updatedAt: new Date(),
    ...overrides,
  };
}

export async function createUser(overrides: CreateUserOptions = {}) {
  return prisma.user.create({ data: buildUser(overrides) });
}

// ─── Post Factory ─────────────────────────────────────────────────────────────

export interface CreatePostOptions {
  id?: string;
  title?: string;
  content?: string;
  authorId?: string;       // Will create a User if not provided
  status?: PostStatus;
}

export async function createPost(overrides: CreatePostOptions = {}) {
  const authorId = overrides.authorId ?? (await createUser()).id;
  return prisma.post.create({
    data: {
      id:          faker.string.uuid(),
      title:       faker.lorem.sentence(),
      slug:        faker.helpers.slugify(faker.lorem.words(4)),
      content:     faker.lorem.paragraphs(3),
      excerpt:     faker.lorem.sentences(2),
      status:      faker.helpers.arrayElement(['DRAFT', 'PUBLISHED', 'ARCHIVED'] as PostStatus[]),
      publishedAt: faker.date.recent({ days: 90 }),
      authorId,
      createdAt:   faker.date.past({ years: 1 }),
      updatedAt:   new Date(),
      ...overrides,
    },
  });
}

// ─── Order Factory ────────────────────────────────────────────────────────────

export interface CreateOrderOptions {
  id?: string;
  userId?: string;
  total?: number;
  status?: 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';
}

export async function createOrder(overrides: CreateOrderOptions = {}) {
  const userId = overrides.userId ?? (await createUser()).id;
  return prisma.order.create({
    data: {
      id:      faker.string.uuid(),
      userId,
      total:   faker.number.float({ min: 9.99, max: 999.99, fractionDigits: 2 }),
      status:  faker.helpers.arrayElement(['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED']),
      address: faker.location.streetAddress(),
      city:    faker.location.city(),
      country: faker.location.country(),
      createdAt: faker.date.past({ years: 1 }),
      updatedAt: new Date(),
      ...overrides,
    },
  });
}

// ─── Bulk creation helpers ────────────────────────────────────────────────────

export async function createUsers(count: number, overrides: CreateUserOptions = {}) {
  return Promise.all(Array.from({ length: count }, () => createUser(overrides)));
}

export async function createPosts(count: number, overrides: CreatePostOptions = {}) {
  return Promise.all(Array.from({ length: count }, () => createPost(overrides)));
}

// ─── Teardown ─────────────────────────────────────────────────────────────────

export async function clearTestData() {
  // Delete in reverse dependency order (children before parents)
  await prisma.order.deleteMany();
  await prisma.post.deleteMany();
  await prisma.user.deleteMany();
}
```

### Python Output (factory_boy)

```python
# Generated by phy-test-data-factory
# Install: pip install factory_boy faker

import uuid, random
from datetime import datetime
import factory
from factory import Faker, SubFactory, LazyFunction
from factory.django import DjangoModelFactory  # or SQLAlchemyModelFactory
from myapp.models import User, Post, Order, UserRole, PostStatus

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    id           = LazyFunction(lambda: str(uuid.uuid4()))
    email        = Faker('email')
    name         = Faker('name')
    username     = Faker('user_name')
    bio          = Faker('paragraph')
    avatar_url   = Faker('image_url')
    role         = factory.Iterator([r.value for r in UserRole])
    is_active    = True
    created_at   = Faker('date_time_this_year')
    updated_at   = LazyFunction(datetime.utcnow)

class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    id           = LazyFunction(lambda: str(uuid.uuid4()))
    title        = Faker('sentence', nb_words=6)
    slug         = factory.LazyAttribute(lambda o: o.title.lower().replace(' ', '-').replace(',', ''))
    content      = Faker('paragraphs', nb=3, as_list=False)
    excerpt      = Faker('sentences', nb=2, as_list=False)
    status       = factory.Iterator([s.value for s in PostStatus])
    author       = SubFactory(UserFactory)
    published_at = Faker('date_time_this_month')
    created_at   = Faker('date_time_this_year')
    updated_at   = LazyFunction(datetime.utcnow)

class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    id       = LazyFunction(lambda: str(uuid.uuid4()))
    user     = SubFactory(UserFactory)
    total    = LazyFunction(lambda: round(random.uniform(9.99, 999.99), 2))
    status   = factory.Iterator(['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED'])
    address  = Faker('street_address')
    city     = Faker('city')
    country  = Faker('country')
    created_at = Faker('date_time_this_year')
    updated_at = LazyFunction(datetime.utcnow)


# Usage in pytest conftest.py:
#
# @pytest.fixture
# def user(db):
#     return UserFactory()
#
# @pytest.fixture
# def post_with_author(db):
#     return PostFactory()  # auto-creates a User via SubFactory
#
# @pytest.fixture
# def many_orders(db):
#     return OrderFactory.create_batch(20)
```

### SQL Seed Output

```sql
-- Generated by phy-test-data-factory
-- Seed data for: users, posts, orders
-- Insert in dependency order (parents first)

-- Users (10 rows)
INSERT INTO users (id, email, name, role, is_active, created_at) VALUES
  ('usr_001', 'alice@example.com', 'Alice Johnson', 'USER', true, '2026-01-15 09:30:00'),
  ('usr_002', 'bob@example.com', 'Bob Smith', 'ADMIN', true, '2026-01-20 14:00:00'),
  ('usr_003', 'carol@example.com', 'Carol Williams', 'USER', true, '2026-02-01 11:00:00'),
  -- ... (7 more rows)

-- Posts (20 rows, requires users above)
INSERT INTO posts (id, title, slug, status, author_id, created_at) VALUES
  ('post_001', 'Getting Started with Testing', 'getting-started-testing', 'PUBLISHED', 'usr_001', '2026-02-10 10:00:00'),
  ('post_002', 'Advanced Patterns in TypeScript', 'advanced-typescript', 'DRAFT', 'usr_002', '2026-02-15 11:30:00'),
  -- ... (18 more rows)
```

---

## Step 5: Output Report

```markdown
## Test Data Factory — Generated
Schema: prisma/schema.prisma | Models: User, Post, Comment, Order, Tag
Output: src/test/factories/index.ts

---

### Models Processed (dependency order)

| Model | Fields | Relationships | Factory Type |
|-------|--------|--------------|-------------|
| User | 14 fields | — (root) | createUser() |
| Tag | 4 fields | — (root) | createTag() |
| Post | 11 fields | → User (author) | createPost() |
| Comment | 8 fields | → User, → Post | createComment() |
| Order | 9 fields | → User | createOrder() |

---

### Generated Files

- `src/test/factories/index.ts` — all factory functions
- `src/test/factories/builders.ts` — plain object builders (no DB write)
- `src/test/setup.ts` — jest/vitest beforeAll/afterAll with clearTestData()

---

### Auto-Detected Semantic Mappings

| Field | Detected As | Faker Function Used |
|-------|------------|---------------------|
| `email` | Email address | `faker.internet.email()` |
| `avatarUrl` | Image URL | `faker.image.avatar()` |
| `publishedAt` | Recent date | `faker.date.recent({ days: 90 })` |
| `role` | Enum (USER/ADMIN/MOD) | `faker.helpers.arrayElement([...])` |
| `slug` | URL slug | `faker.helpers.slugify(faker.lorem.words(3))` |
| `price` | Currency amount | `faker.number.float({ fractionDigits: 2 })` |

---

### Quick Usage

```typescript
import { createUser, createPost, createOrder, clearTestData } from './factories';

// Single record
const user = await createUser();

// With overrides
const adminUser = await createUser({ role: 'ADMIN', email: 'admin@test.com' });

// Relationships handled automatically
const post = await createPost();       // creates a User internally
const post2 = await createPost({ authorId: user.id });  // reuse existing User

// Batch creation
const orders = await createOrders(50);

// Teardown
afterAll(clearTestData);
```
```

---

## Edge Case Variants

With `--edge-cases`, generate additional factory variants for boundary testing:

```typescript
// Generated edge-case builders for User model:

export const edgeCaseUsers = {
  withMinLengthFields: () => buildUser({
    email: 'a@b.co',
    name: 'A',
    bio: '',
  }),
  withMaxLengthFields: () => buildUser({
    email: 'a'.repeat(243) + '@b.co',  // 255 chars total
    name: 'A'.repeat(255),
    bio: 'x'.repeat(5000),
  }),
  withNullableFieldsNull: () => buildUser({
    bio: null,
    avatarUrl: null,
    phoneNumber: null,
  }),
  withSpecialCharacters: () => buildUser({
    name: "O'Brien-Smith, Jr.",
    bio: '<script>alert("xss")</script>',  // for XSS testing
  }),
  withUnicodeContent: () => buildUser({
    name: '张伟',
    bio: '日本語テキスト with emoji 🎉',
  }),
  withPastDates: () => buildUser({
    createdAt: new Date('2000-01-01'),
  }),
  withFutureDates: () => buildUser({
    createdAt: new Date('2099-12-31'),
  }),
};
```

---

## Install Dependencies

```bash
# TypeScript / JavaScript
npm install -D @faker-js/faker

# Python (Django)
pip install factory_boy faker

# Python (SQLAlchemy)
pip install factory_boy faker sqlalchemy

# Verify installation
node -e "const { faker } = require('@faker-js/faker'); console.log(faker.person.fullName())"
python3 -c "import factory; print('factory_boy ready')"
```
