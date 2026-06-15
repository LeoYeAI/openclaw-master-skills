# API Test Create

**Version**: 0.4.1
**Category**: Testing Tool
**Tags**: api, testing, openapi, swagger, create, automation

## Overview

API Test Create is a tool that automatically generates comprehensive API test cases from interface specifications. It accepts API documentation (supporting OpenAPI/Swagger, simplified definitions, or natural language descriptions) and outputs structured test case checklists covering parameter validation, business logic, response verification, and common pitfalls.

## Features

- 🤖 **Smart Parsing**: Supports OpenAPI/Swagger, YAML/JSON, and natural language input
- 📋 **Comprehensive Coverage**: Automatically generates 7 categories of test points (Parameter, Business Logic, Response, Security, Performance, Compatibility, and Supplementary Tests)
- 🎯 **Priority Labeling**: Test points categorized as P0/P1/P2 priority levels
- ⚠️ **High-Frequency Pitfalls**: Built-in 140 common API testing pitfalls for automatic cross-checking
- 📊 **Statistical Reports**: Automatically generates test point quantity statistics

## Directory Structure

```
api-test-checklist/
├── README.md                    # Chinese documentation
├── README_EN.md                 # English documentation (this file)
├── QUICKSTART.md               # Quick start guide
├── SKILL.md                     # Main skill file (for Claude)
├── _meta.json                   # Metadata
├── requirements.txt            # Dependencies
├── scripts/                     # Executable scripts
│   ├── generate-checklist.py    # Core generator
│   └── utils.py                 # Utility functions
├── examples/                    # Examples
│   ├── openapi-example.yaml     # OpenAPI example
│   └── simple-example.md        # Simplified definition example
├── references/                  # Reference documentation
│   ├── test-case-design.md      # Test case design methods
│   └── common-pitfalls.md       # 140 common pitfalls
└── tests/                       # Unit tests
    └── test_generator.py        # Generator tests
```

## Quick Start

### Method 1: Using Claude Skill (Recommended)

Simply tell Claude your interface definition:

```
I have the following API, please generate a test checklist:

Interface Name: User Login
Endpoint: POST /api/users/login
Parameters:
  - username: string, required, 3-20 characters
  - password: string, required, 6-20 characters
Response:
  - token: string
  - user: object
```

### Method 2: Using Script

#### Generate from OpenAPI/Swagger

```bash
python scripts/generate-checklist.py \
  --input examples/openapi-example.yaml \
  --format openapi \
  --output output/checklist.md
```

#### Generate from Simplified Definition

```bash
python scripts/generate-checklist.py \
  --input examples/simple-example.md \
  --format simple \
  --output output/checklist.md
```

#### Generate from String

```bash
python scripts/generate-checklist.py \
  --input "Interface: POST /api/login
Parameters:
  - username: string, required
  - password: string, required
Response:
  - token: string" \
  --format simple
```

### Method 3: Programmatic Usage

```python
from scripts.generate_checklist import APITestGenerator

# Initialize generator
generator = APITestGenerator()

# Generate from OpenAPI
openapi_spec = """
{
  "openapi": "3.0.0",
  "info": {"title": "Test API", "version": "1.0.0"},
  "paths": {
    "/test": {
      "post": {
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "name": {"type": "string", "minLength": 3, "maxLength": 20}
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

checklist = generator.generate_from_openapi(openapi_spec, "Test API")
print(checklist)
```

## Input Formats

### 1. OpenAPI/Swagger (Recommended)

Supports OpenAPI 3.0 and Swagger 2.0 specifications.

**Example**: `examples/openapi-example.yaml`

### 2. Simplified Interface Definition

**Format**:

```
Interface Name: [Name]
Endpoint: [METHOD] [Path]
Parameters:
  - [param_name]: [type], [required/optional], [constraints], [description]
Response Fields:
  - [field_name]: [type]
Business Rules:
  - [rule_description]
```

**Example**: `examples/simple-example.md`

### 3. Natural Language Description

Describe the interface information directly, Claude will intelligently parse it.

## Output Example

Generates structured Markdown format:

```markdown
## API: User Registration

### Basic Information
- Endpoint: POST /api/users/register
- Description: User registration endpoint

### Parameter Validation Test Points

#### username (string, required, 3-20 characters)
| Test Scenario | Test Value | Expected Result | Priority |
|---------------|------------|-----------------|----------|
| Normal value | "testuser" | Success | P0 |
| Boundary - min length | "abc" | Success | P1 |
| Boundary - max length | "a"*20 | Success | P1 |
| Empty value | null/"" | Parameter error | P0 |
| Special characters | "<script>alert(1)</script>" | Parameter error | P1 |
| SQL injection | "admin'--" | Parameter error | P1 |

### Business Logic Test Points
| Test Scenario | Precondition | Action | Expected Result | Priority |
|---------------|--------------|--------|-----------------|----------|
| Normal registration | None | Submit valid data | Registration success, return token | P0 |
| Duplicate username | User "testuser" exists | Register with same username | Return username already exists | P0 |

### Response Verification Test Points
| Item | Verification | Priority |
|------|--------------|----------|
| Response structure | Contains code, message, data | P0 |
| data.id | Returns user ID (integer) | P0 |
| data.token | Returns valid JWT token | P0 |

### Security Test Points
| Test Scenario | Test Value | Expected Result | Priority |
|---------------|------------|-----------------|----------|
| SQL injection | "' OR '1'='1" | Parameter error | P0 |
| XSS attack | "<script>alert(1)</script>" | Parameter error | P0 |

### Statistics
- Parameter validation: 25 test points
- Business logic: 6 test points
- Response verification: 6 test points
- Security tests: 2 test points
- **Total: 39 test points**
```

## Test Coverage

### 1. Parameter Validation (Auto-generated)

| Parameter Type | Test Scenarios |
|----------------|----------------|
| string | Length boundaries, special chars, SQL injection, XSS, Unicode, format validation |
| integer | Value range, boundary values, zero, negative, overflow, type conversion |
| number | Precision, scientific notation, range |
| enum | All valid values, invalid values, case sensitivity, null |
| boolean | true/false, string conversion, numeric conversion |
| array | Empty array, element count, duplicate elements, invalid elements |
| object | Complete object, missing required fields, extra fields |
| datetime | Valid dates, invalid dates, format, timezone, leap year |

### 2. Business Logic (Rule-based)

- Existence validation (data exists/not exists/deleted)
- Uniqueness validation (duplicate data)
- State transition validation (valid/invalid transitions)
- Permission validation (authorized/unauthorized/not logged in)
- Association validation (foreign key existence)
- Quantity limits (upper/lower bounds)

### 3. Response Verification

- Structure completeness (code, message, data)
- Field type correctness
- Pagination information accuracy
- Empty result handling (returns [] or null)

### 4. Security Testing

- SQL injection attacks
- XSS cross-site scripting
- Authentication bypass
- Unauthorized access
- Brute force attacks

### 5. Performance Testing Suggestions

- Response time thresholds
- Concurrent access testing
- Large page number queries
- Batch operation limits

### 6. Compatibility Testing

- Different browsers/clients
- Different environments (test/production)
- Different version coexistence

### 7. Supplementary Tests (40 items)

#### 7.1 General Information Validation (10 items)
- URL correctness/error handling
- HTTP method correctness/errors
- Request header correctness/errors
- Interface authentication (correct, missing, wrong, expired)

#### 7.2 Detailed Parameter Validation (18 items)
- Required fields (complete, missing, null, empty string)
- Optional fields (none, partial)
- Length (exceed max, below min, equal to max)
- Data types (correct, wrong)
- Validity (within range, outside range)
- Uniqueness (unique, duplicate)
- Association (mutually exclusive, dependent)

#### 7.3 Other Supplementary Items (12 items)
- Idempotency (repeat submission, lottery, order modification)
- Weak network environment (network interruption, payment scenarios)
- Distributed systems (data synchronization, consistency)
- Interface style (RESTful compliance)
- Sensitive information (transmission encryption, log desensitization, storage encryption)

## 140 Common Pitfalls

Built-in 140 common pitfalls for automatic cross-checking, covering 7 dimensions:

1. **Request Layer Specification** (15 items)
2. **Parameter Processing** (30 items)
3. **Response Results** (20 items)
4. **Business Logic** (15 items)
5. **Performance & Concurrency** (10 items)
6. **Security & Compatibility** (10 items)
7. **Supplementary Tests** (40 items) - Includes 40 detailed test items provided by users

See `references/common-pitfalls.md` for detailed list.

## Configuration

Create `config.json` for customization:

```bash
# Create config.json based on your needs
{
  "priority_rules": {
    "required_missing": "P0",
    "sql_injection": "P0"
  }
}
```

### Configuration Options

- `priority_rules`: Test priority rules
- `custom_validators`: Custom validators
- `test_data_generators`: Test data generation rules
- `security_test_cases`: Security test cases

## Advanced Features

### Batch Generation

```bash
# Batch process all YAML files in directory
for file in apis/*.yaml; do
  python scripts/generate-checklist.py \
    --input "$file" \
    --output "output/$(basename "$file" .yaml).md"
done
```

### Custom Rules

Edit `config.json`:

```json
{
  "custom_validators": {
    "phone_number": {
      "pattern": "^1[3-9]\\d{9}$",
      "error_message": "Invalid phone number format"
    }
  }
}
```

## Testing

```bash
# Run unit tests
pytest tests/

# Test coverage
pytest --cov=scripts tests/

# Integration tests
python tests/integration_test.py
```

## FAQ

### Q: How to handle non-standard interface definitions?
A: Use `--format text` parameter and provide natural language description

### Q: How to customize test priorities?
A: Edit `config.json` and modify `priority_rules`

### Q: Which OpenAPI versions are supported?
A: OpenAPI 3.0 and Swagger 2.0

### Q: What if too many test points are generated?
A: Use `--priority P0,P1` parameter to generate only high-priority test points

### Q: How to run tests?
A: `pytest tests/`

## Changelog

### v0.4.1 (2026-03-25)
- ✅ Added 40 supplementary test items
- ✅ Added general information validation tests
- ✅ Added detailed parameter validation tests
- ✅ Added idempotency, weak network, distributed system tests
- ✅ Added RESTful style and sensitive information encryption tests
- ✅ Updated all documentation to reflect 140 test points

### v0.4.0 (2026-03-25)
- ✅ Added executable workflow scripts
- ✅ Unified Chinese documentation
- ✅ Enhanced metadata
- ✅ Added README.md and QUICKSTART.md
- ✅ Added unit tests (pytest)
- ✅ Added configuration examples
- ✅ Added OpenAPI and simplified definition examples

### v0.3.0 (2026-03-25)
- Optimized document structure
- Added detailed workflow

### v0.2.0 (2026-03-25)
- Added 100 common pitfalls

### v0.1.0 (2026-03-25)
- Initial version

## Contributing

Welcome to submit Issues and PRs!

## License

MIT License
