---
name: clean-pytest
description: Write clean, maintainable pytest tests using Fake-based testing, contract testing, and dependency injection patterns. Use when setting up test suites for Python/MCP projects, creating Fakes for external dependencies, writing contract tests, or implementing test patterns with fixtures and parametrization.
license: MIT
metadata:
  emoji: "🧪"
  homepage: https://github.com/numinstante/skills
  os: [darwin, linux, windows]
  tags: [python, pytest, testing, tdd, mcp, contract-testing]
  requires:
    anyBins: [python3]
---

# Clean Pytest

Clean, maintainable pytest test patterns using Fake-based testing, contract testing, and dependency injection. Focuses on test isolation, reusability, and clarity through explicit AAA pattern and well-structured fixtures.

## When to Use

- Setting up test suites for Python/MCP projects
- Creating Fake implementations for external dependencies
- Writing contract tests for MCP tools/controllers
- Implementing test patterns with dependency injection
- Testing layered architectures (Controllers → Services → Repositories)
- Writing parametrized tests for multiple scenarios

## Core Principles

### 1. Fakes over Mocks

Use **Fake classes** instead of mocking with `unittest.mock`. Fakes are in-memory implementations that mimic real dependencies without external calls.

**Why Fakes?**
- More readable and maintainable
- Easier to debug
- Better test isolation
- No monkey-patching magic
- Self-documenting behavior

### 2. Explicit AAA Pattern

Structure every test into three clear phases with comments:

```python
# Arrange
# Set up test data and dependencies

# Act
# Execute the code under test

# Assert
# Verify the result
```

### 3. Dependency Injection in Fixtures

Inject dependencies between fixtures to maintain relationships and avoid duplication.

### 4. Contract Testing

Verify that components register tools/functions correctly and pass expected arguments.

## Architecture Pattern

```
Controller (MCP Tools)
    ↓
Service (Business Logic)
    ↓
Repository (Data Access)
    ↓
Fake (Test Implementation)
```

## Creating Fakes

### Basic Fake Structure

Create a Fake class that implements the same interface as the real dependency:

```python
# tests/fakes.py
from typing import Any, Dict, List, Optional

class FakeAuth:
    """Fake implementation of AuthProvider for testing."""
    def __init__(self) -> None:
        self.created: List[Dict[str, Any]] = []
        self.deleted: List[str] = []
        self._seq = 0
        self.fail_on_create: bool = False

    def create_user(self, email: str, password: str, display_name: str) -> str:
        if self.fail_on_create:
            raise RuntimeError("create_user failed (fake)")
        self._seq += 1
        uid = f"uid-{self._seq}"
        rec = {"uid": uid, "email": email, "display_name": display_name}
        self.created.append(rec)
        return uid

    def delete_user(self, uid: str) -> None:
        self.deleted.append(uid)
```

### Repository Fake

```python
class FakeUsersRepo:
    """Fake implementation of UsersRepository."""
    def __init__(self) -> None:
        self.users: Dict[str, Dict[str, Any]] = {}
        self.fail_on_upsert: bool = False

    def upsert_user_doc(self, uid: str, data: Dict[str, Any]) -> None:
        if self.fail_on_upsert:
            raise RuntimeError("upsert_user_doc failed (fake)")
        self.users[uid] = dict(data)

    def list_users(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        items = list(self.users.values())
        if limit and limit > 0:
            items = items[:limit]
        return [dict(it) for it in items]
```

### Controlled Failure Fakes

```python
class FakeAuth:
    def __init__(self) -> None:
        self.fail_on_create: bool = False  # Control failure in tests

    def create_user(self, email: str, password: str, display_name: str) -> str:
        if self.fail_on_create:
            raise RuntimeError("create_user failed (fake)")
        # ... rest of implementation
```

### Nested Repository Fakes

```python
class FakeSectorsRepo:
    def __init__(self, institutions: FakeInstitutionsRepo | None = None) -> None:
        self.institutions = institutions  # Inject dependency
        self.data: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def institution_exists(self, institution_id: str) -> bool:
        return bool(self.institutions and institution_id in self.institutions.data)

    def upsert_sector(self, institution_id: str, sector_id: str, data: Dict[str, Any]) -> None:
        self.data.setdefault(institution_id, {})[sector_id] = dict(data)
```

## Fixtures

### Basic Fixture (conftest.py)

```python
# tests/conftest.py
import pytest
from tests.fakes import FakeAuth, FakeUsersRepo

@pytest.fixture()
def fake_auth():
    """Provide a fresh FakeAuth for each test."""
    return FakeAuth()

@pytest.fixture()
def fake_users_repo():
    """Provide a fresh FakeUsersRepo for each test."""
    return FakeUsersRepo()
```

### Fixture with Dependency Injection

```python
@pytest.fixture()
def fake_sectors_repo(fake_institutions_repo):
    """FakeSectorsRepo depends on FakeInstitutionsRepo."""
    return FakeSectorsRepo(institutions=fake_institutions_repo)

@pytest.fixture()
def fake_rooms_repo(fake_sectors_repo):
    """FakeRoomsRepo depends on FakeSectorsRepo."""
    return FakeRoomsRepo(sectors=fake_sectors_repo)
```

### Environment Fixture

```python
@pytest.fixture()
def user_env(fake_auth, fake_users_repo):
    """Provide service and all dependencies for user operations."""
    from myapp.services.user_service import UserService
    svc = UserService(fake_auth, fake_users_repo)
    return svc, fake_auth, fake_users_repo
```

### Seeded Environment Fixture

```python
@pytest.fixture()
def user_env_seeded(user_env):
    """Environment with pre-seeded data."""
    svc, auth, repo = user_env
    svc.add_user(email="test@example.com", password="secret", name="Test User")
    return svc
```

### Fixture with Cleanup

```python
@pytest.fixture()
def temp_file():
    """Provide a temporary file and clean up after test."""
    import tempfile
    import os
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.unlink(path)
```

## Service Layer Testing

### Basic AAA Pattern Test

```python
# tests/test_user_service.py
import pytest
from myapp.services.user_service import UserService

def test_add_user_success(fake_auth, fake_users_repo):
    # Arrange
    svc = UserService(fake_auth, fake_users_repo)
    email = "test@example.com"
    password = "secret"
    name = "Test User"

    # Act
    result = svc.add_user(email=email, password=password, name=name)

    # Assert
    assert result["status"] == "ok"
    assert result["user"]["email"] == email
    assert result["user"]["name"] == name
    assert result["uid"] in fake_users_repo.users
```

### Parametrized Tests

```python
@pytest.mark.parametrize(
    "email,password,name,role",
    [
        ("a@example.com", "secret", "Alice", "admin"),
        ("b@example.com", "p@ss", "Bob", "user"),
    ],
)
def test_add_user_parametrized(user_env, email, password, name, role):
    svc, _auth, _repo = user_env

    # Act
    res = svc.add_user(email=email, password=password, name=name, global_role=role)

    # Assert
    assert res["status"] == "ok"
    assert res["user"]["email"] == email
    assert res["user"]["name"] == name
    assert res["user"]["globalRole"] == role
```

### Testing Error Scenarios with Fakes

```python
@pytest.mark.parametrize("email", ["c@example.com", "d@example.com"])
def test_add_user_rollback_on_firestore_failure(fake_auth, fake_users_repo, email):
    # Arrange
    fake_users_repo.fail_on_upsert = True
    svc = UserService(fake_auth, fake_users_repo)

    # Act & Assert
    with pytest.raises(RuntimeError):
        svc.add_user(email=email, password="secret", name="Bob")

    # Assert rollback
    assert fake_auth.deleted, "Expected auth user to be deleted on Firestore failure"
```

### Testing Timestamp Normalization

```python
def test_list_users_normalizes_timestamps_to_iso(user_env):
    # Arrange
    svc, _auth, repo = user_env
    from datetime import datetime
    repo.users["u1"] = {
        "id": "u1",
        "email": "x@y.z",
        "name": "X",
        "globalRole": "user",
        "createdAt": datetime(2024, 1, 1),
        "updatedAt": datetime(2024, 1, 2),
    }

    # Act
    res = svc.list_users(limit=10)

    # Assert
    assert res["status"] == "ok"
    assert res["count"] == 1
    user = res["users"][0]
    assert isinstance(user["createdAt"], str)
    assert isinstance(user["updatedAt"], str)
```

## Contract Testing

### MCP Tool Registration Contract

Test that controllers properly register tools with expected signatures:

```python
# tests/test_controllers_contract.py
from typing import Any, Callable, Dict

class FakeMCP:
    """Minimal FakeMCP for contract testing."""
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}
        self.meta: Dict[str, Dict[str, Any]] = {}

    def tool(self, name: str, description: str, tags: Optional[set] = None, meta: Optional[dict] = None):
        def decorator(fn: Callable[..., Any]):
            self.tools[name] = fn
            self.meta[name] = {
                "description": description,
                "tags": set(tags or set()),
                "meta": dict(meta or {}),
            }
            return fn
        return decorator


class FakeUserService:
    """Simple fake service that records calls."""
    def __init__(self):
        self.calls = []

    def add_user(self, **kwargs):
        self.calls.append(("add_user", kwargs))
        return {"status": "ok", "op": "add_user", "args": kwargs}


def test_users_controller_contract():
    # Arrange
    from myapp.controllers.users_controller import UsersController
    fake = FakeMCP()
    svc = FakeUserService()
    UsersController(fake, svc)

    # Assert tool registration
    assert "add_user" in fake.tools
    assert "list_users" in fake.tools

    # Act & Assert tool behavior
    res = fake.tools["add_user"](
        email="a@x.y", password="s3cr3t", name="Alice", global_role="admin"
    )
    assert res["status"] == "ok"
    assert res["op"] == "add_user"
    assert res["args"]["email"] == "a@x.y"
```

### Parametrized Contract Tests

```python
@pytest.mark.parametrize(
    "email,password,name,role",
    [
        ("a@x.y", "s3cr3t", "Alice", "admin"),
        ("b@x.y", "p@ssw0rd", "Bob", "user"),
    ],
)
def test_users_add_user_parametrized(_users_env, email, password, name, role):
    # Arrange
    fake, _ = _users_env

    # Act
    res = fake.tools["add_user"](
        email=email, password=password, name=name, global_role=role
    )

    # Assert
    assert res["status"] == "ok"
    assert res["op"] == "add_user"
    assert res["args"]["email"] == email
```

## Repository Layer Testing

### Testing Repository Operations

```python
@pytest.fixture()
def repo_env(fake_institutions_repo, fake_sectors_repo):
    # Seed data
    fake_institutions_repo.upsert("inst1", {"id": "inst1", "name": "Inst One"})
    fake_sectors_repo.upsert_sector(
        "inst1", "er", {"id": "er", "name": "ER", "slug": "er", "isActive": True}
    )
    return fake_sectors_repo
```

### Testing Multiple Data Scenarios

```python
@pytest.mark.parametrize("rooms", [
    ["101"],
    ["201", {"name": "102", "id": "room-102"}],
])
def test_add_and_list_rooms(room_env, rooms):
    svc, _ = room_env

    # Act
    res = svc.add_sector_rooms("inst1", "er", rooms)

    # Assert
    assert res["status"] == "ok"
    assert res["count"] == len(rooms)

    lst = svc.list_sector_rooms("inst1", "er", limit=10)
    assert lst["status"] == "ok"
    assert lst["count"] == len(rooms)
```

### Testing Limit Behavior

```python
@pytest.mark.parametrize("limit", [1, 3])
def test_list_rooms_limits(room_env_seeded, limit):
    svc = room_env_seeded

    # Act
    lst = svc.list_sector_rooms("inst1", "er", limit=limit)

    # Assert
    assert lst["status"] == "ok"
    assert lst["count"] == min(2, limit)  # 2 items seeded
```

### Testing Not Found Scenarios

```python
@pytest.mark.parametrize("room_id,deleted", [
    ("room-102", True),
    ("room-999", False),
])
def test_remove_rooms_parametrized(room_env_seeded, room_id, deleted):
    svc = room_env_seeded

    # Act
    res = svc.remove_sector_room("inst1", "er", room_id)

    # Assert
    assert res["deleted"] is deleted
    if not deleted:
        assert res.get("reason") == "room_not_found"
```

## Integration Testing

### Conditional Integration Tests

Skip integration tests when external dependencies are not available:

```python
# tests/test_integration_wiring.py
import os
import pytest

# Gate this integration test on presence of credentials
_ENV_KEYS = (
    "FIREBASE_SERVICE_ACCOUNT",
    "GOOGLE_APPLICATION_CREDENTIALS",
)
_has_env_creds = any(os.getenv(k) for k in _ENV_KEYS)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _has_env_creds,
        reason=(
            "Integration test requires Firebase Admin credentials via env "
            "(FIREBASE_SERVICE_ACCOUNT or GOOGLE_APPLICATION_CREDENTIALS)"
        ),
    ),
]

@pytest.mark.integration
def test_build_app_initializes_and_registers_tools():
    # Arrange
    from myapp.wiring import build_app

    # Act
    app = build_app()

    # Assert
    assert hasattr(app, "run")
```

### Test Isolation

Each test should be independent and not share state:

```python
def test_user_created_in_one_test_not_visible_in_another(fake_auth, fake_users_repo):
    # Arrange
    svc1 = UserService(fake_auth, fake_users_repo)

    # Act
    result1 = svc1.add_user(email="test1@example.com", password="secret", name="User1")

    # Assert - second test with fresh fixtures should not see this user
    svc2 = UserService(fake_auth, fake_users_repo)
    users = svc2.list_users()
    assert users["count"] == 1  # Only the user from this test
```

## Testing Anti-Patterns to Avoid

### Don't Mock What You Don't Own

❌ Bad - Mocking external library:

```python
@patch('firebase_admin.auth.create_user')
def test_add_user(mock_create_user):
    mock_create_user.return_value = Mock(uid="uid-1")
    # ... test code
```

✅ Good - Use Fake for your interface:

```python
def test_add_user(fake_auth, fake_users_repo):
    svc = UserService(fake_auth, fake_users_repo)
    # ... test code
```

### Don't Test Implementation Details

❌ Bad - Testing internal method calls:

```python
def test_add_user(fake_auth, fake_users_repo):
    svc = UserService(fake_auth, fake_users_repo)
    svc.add_user(email="test@example.com", password="secret", name="User")
    assert fake_auth.created == [{"uid": "uid-1", ...}]  # Implementation detail
```

✅ Good - Testing observable behavior:

```python
def test_add_user(fake_auth, fake_users_repo):
    svc = UserService(fake_auth, fake_users_repo)
    result = svc.add_user(email="test@example.com", password="secret", name="User")
    assert result["status"] == "ok"
    assert result["user"]["email"] == "test@example.com"
```

### Don't Skip Error Paths

❌ Bad - Only happy path:

```python
def test_add_user_success(fake_auth, fake_users_repo):
    # Only tests success case
```

✅ Good - Test all scenarios:

```python
def test_add_user_success(fake_auth, fake_users_repo):
    # Happy path

def test_add_user_rollback_on_firestore_failure(fake_auth, fake_users_repo):
    # Error path

def test_add_user_handles_duplicate_email(fake_auth, fake_users_repo):
    # Edge case
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=myapp --cov-report=term-missing

# Run specific test file
pytest tests/test_user_service.py

# Run specific test
pytest tests/test_user_service.py::test_add_user_success

# Run parametrized tests with verbose output
pytest -v tests/test_user_service.py::test_add_user_parametrized

# Skip integration tests
pytest -m "not integration"

# Run only integration tests
pytest -m integration

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run tests in parallel (with pytest-xdist)
pytest -n auto
```

## Best Practices Checklist

- [ ] Use Fake classes instead of `unittest.mock`
- [ ] Structure tests with explicit AAA comments
- [ ] Use fixtures for test setup
- [ ] Inject dependencies between fixtures
- [ ] Parametrize tests for multiple scenarios
- [ ] Test happy paths and error paths
- [ ] Test edge cases and boundaries
- [ ] Write contract tests for interfaces
- [ ] Ensure test isolation
- [ ] Use descriptive test names
- [ ] Keep tests focused on one behavior
- [ ] Avoid testing implementation details
- [ ] Test at appropriate level (unit vs integration)
- [ ] Mock external dependencies appropriately
- [ ] Maintain test coverage
