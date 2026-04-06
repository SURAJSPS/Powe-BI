# Testing guide (RNK Civil / Streamlit)

## RNK quick reference

- **Where tests live:** `tests/` at the repo root, mirroring packages (`tests/services/`, `tests/core/`, …). Shared fixtures in `tests/conftest.py` (Mongo mocks, sample users).
- **What to test first:** (1) `services/` — logic without Streamlit; (2) `core/` — roles, session/cookie helpers; (3) `db/` — optional integration; (4) `ui/pages/` — smoke only, keep pages thin.
- **Tools:** `pytest` (+ `pytest-cov` for coverage). Mock Mongo with `mongomock` or `unittest.mock`. Avoid calling `st` in service tests.
- **Checklist per feature:** happy path + one failure path for services; type hints on public helpers; no secrets in tests.

The sections below are the **full testing strategy** from the improvement doc pack (examples use generic `Client` / `Payroll` / `models` — adapt types and paths to this repo as you adopt repositories and DTOs). See **`Implementation-roadmap.md`** Phase 1 for bootstrapping `tests/`.

---

## 1. Testing Pyramid

```
        △  UI Tests (10%)
       ╱ ╲
      ╱   ╲  Integration Tests (30%)
     ╱─────╲
    ╱       ╲ Unit Tests (60%)
   ╱─────────╲
```

- **Unit Tests** (60%): Test services, validators, helpers in isolation
- **Integration Tests** (30%): Test services with real/mock DB
- **UI Tests** (10%): Smoke tests for critical paths; avoid testing Streamlit UI directly

---

## 2. Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── fixtures.py                    # Factories for test data
│
├── unit/
│   ├── test_validation.py         # Pydantic validators
│   ├── test_errors.py             # Error handling
│   └── test_result.py             # Result type
│
├── services/
│   ├── test_client_service.py     # Service logic (mocked DB)
│   ├── test_payroll_service.py
│   └── test_queries.py
│
├── repositories/
│   ├── test_client_repository.py  # Repo logic (real/mock DB)
│   └── test_payroll_repository.py
│
└── integration/
    ├── conftest.py                # Integration test fixtures
    ├── test_client_workflow.py    # End-to-end flows
    └── test_payroll_workflow.py
```

---

## 3. Setup & Dependencies

### `requirements-dev.txt`
```
# Testing
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1
factory-boy==3.2.1
faker==19.3.0

# Mocking
unittest-xml-reporting==3.2.0
responses==0.23.3

# Quality
black==23.7.0
flake8==6.0.0
mypy==1.4.1
```

### `pytest.ini`
```ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=.
    --cov-report=html
    --cov-report=term-missing:skip-covered
    -v
markers =
    unit: Unit tests (fast)
    integration: Integration tests (slower)
    slow: Slow tests
```

---

## 4. Fixtures & Factories

### File: `tests/conftest.py`
```python
"""Shared test configuration and fixtures."""

import pytest
import os
from unittest.mock import Mock, MagicMock
from core.di import Container, reset_container
from config import Config, Environment


@pytest.fixture(autouse=True)
def reset_di():
    """Reset DI container before each test."""
    reset_container()
    yield
    reset_container()


@pytest.fixture
def test_config() -> Config:
    """Test configuration."""
    config = Mock(spec=Config)
    config.ENV = Environment.TEST
    config.MONGO_URI = "mongodb://localhost:27017/test_db"
    config.MONGO_DB_NAME = "test_db"
    config.DB_PATH = ":memory:"
    config.DEBUG = True
    config.LOG_LEVEL = "DEBUG"
    return config


@pytest.fixture
def mock_container(test_config):
    """Mock DI container."""
    container = Mock(spec=Container)
    container.config = test_config
    container.mongo_db = Mock()
    container.sql_session_factory = Mock()
    return container


@pytest.fixture
def mock_mongo_db():
    """Mock MongoDB database."""
    db = MagicMock()
    db.clients = MagicMock()
    db.payroll = MagicMock()
    return db


@pytest.fixture
def mock_sql_session():
    """Mock SQLAlchemy session."""
    session = MagicMock()
    return session
```

### File: `tests/fixtures.py`
```python
"""Test data factories."""

from factory import Factory, Faker, LazyFunction
from datetime import datetime
from models import Client, Payroll


class ClientFactory(Factory):
    """Factory for creating test Client objects."""
    
    class Meta:
        model = Client
    
    id = Faker('uuid4')
    name = Faker('company')
    email = Faker('email')
    phone = Faker('phone_number')
    address = Faker('address')
    created_at = LazyFunction(datetime.utcnow)
    updated_at = None
    
    @classmethod
    def to_dict(cls):
        """Create dict representation."""
        instance = cls()
        return {
            'id': str(instance.id),
            'name': instance.name,
            'email': instance.email,
            'phone': instance.phone,
            'address': instance.address,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }


class PayrollFactory(Factory):
    """Factory for creating test Payroll objects."""
    
    class Meta:
        model = Payroll
    
    id = Faker('uuid4')
    employee_id = Faker('uuid4')
    pay_period_start = Faker('date_object')
    pay_period_end = Faker('date_object')
    gross_salary = Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    deductions = 0.0
    net_salary = LazyFunction(lambda: Faker('pydecimal', positive=True).evaluate(None, None, {}))
    created_at = LazyFunction(datetime.utcnow)


@pytest.fixture
def client_dto():
    """Create sample ClientDTO."""
    from core.validation import ClientDTO
    return ClientDTO(
        id="test_id_123",
        name="Test Client",
        email="test@example.com",
        phone="555-1234",
        created_at=datetime.utcnow()
    )


@pytest.fixture
def create_client_payload():
    """Create sample ClientCreate payload."""
    from core.validation import ClientCreate
    return ClientCreate(
        name="New Client",
        email="new@example.com",
        phone="555-5678",
        address="123 Test St"
    )
```

---

## 5. Unit Tests

### File: `tests/unit/test_validation.py`
```python
"""Test input validation."""

import pytest
from pydantic import ValidationError
from core.validation import ClientCreate, ClientUpdate


class TestClientCreate:
    """Test ClientCreate validation."""
    
    def test_valid_client_creation(self):
        """Valid data should create client."""
        client = ClientCreate(
            name="Acme Corp",
            email="contact@acme.com",
            phone="555-1234"
        )
        assert client.name == "Acme Corp"
        assert client.email == "contact@acme.com"
    
    def test_name_stripped(self):
        """Whitespace should be stripped."""
        client = ClientCreate(
            name="  Test  ",
            email="test@example.com",
            phone="555-1234"
        )
        assert client.name == "Test"
    
    def test_name_required(self):
        """Name is required."""
        with pytest.raises(ValidationError) as exc_info:
            ClientCreate(
                name="",
                email="test@example.com",
                phone="555-1234"
            )
        errors = exc_info.value.errors()
        assert any(e['msg'] for e in errors if 'Name cannot be empty' in str(e))
    
    def test_invalid_email(self):
        """Invalid email should fail."""
        with pytest.raises(ValidationError):
            ClientCreate(
                name="Test",
                email="not-an-email",
                phone="555-1234"
            )
    
    def test_phone_minimum_digits(self):
        """Phone must have minimum digits."""
        with pytest.raises(ValidationError) as exc_info:
            ClientCreate(
                name="Test",
                email="test@example.com",
                phone="123"
            )
        errors = exc_info.value.errors()
        assert any('7 digits' in str(e) for e in errors)


class TestClientUpdate:
    """Test ClientUpdate validation."""
    
    def test_all_fields_optional(self):
        """All fields should be optional."""
        update = ClientUpdate()
        assert update.model_dump(exclude_unset=True) == {}
    
    def test_partial_update(self):
        """Can update individual fields."""
        update = ClientUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.phone is None
```

### File: `tests/unit/test_errors.py`
```python
"""Test error handling."""

import pytest
from core.errors import AppError, ValidationError, NotFoundError, DuplicateError


class TestErrorHierarchy:
    """Test error types and conversion."""
    
    def test_validation_error_status(self):
        """ValidationError should have 400 status."""
        error = ValidationError("Invalid input")
        assert error.status == 400
        assert error.code == "VALIDATION_ERROR"
    
    def test_not_found_error_details(self):
        """NotFoundError should include resource info."""
        error = NotFoundError("Client", "123")
        assert error.status == 404
        assert error.details["resource"] == "Client"
        assert error.details["resource_id"] == "123"
    
    def test_duplicate_error_serialization(self):
        """Error should serialize to dict."""
        error = DuplicateError("email", "test@example.com")
        error_dict = error.to_dict()
        assert error_dict["code"] == "DUPLICATE_ERROR"
        assert error_dict["message"]
    
    def test_error_logging(self, caplog):
        """Error should log with context."""
        error = AppError("Test error", code="TEST")
        error.log(user_id="user123")
        assert "Test error" in caplog.text


class TestResultType:
    """Test Result wrapper."""
    
    def test_ok_result(self):
        """OK result should contain value."""
        from core.result import Result
        result = Result.ok("success")
        assert result.is_ok()
        assert result.value == "success"
    
    def test_err_result(self):
        """Err result should contain error."""
        from core.result import Result
        error = AppError("Failed")
        result = Result.err(error)
        assert result.is_err()
        assert result.error == error
    
    def test_result_mapping(self):
        """Result should support mapping."""
        from core.result import Result
        result = Result.ok(5)
        mapped = result.map(lambda x: Result.ok(x * 2))
        assert mapped.value == 10
```

### File: `tests/services/test_client_service.py`
```python
"""Test ClientService business logic."""

import pytest
from unittest.mock import Mock, MagicMock
from core.validation import ClientCreate, ClientUpdate
from core.errors import NotFoundError, DuplicateError
from services.client_service import ClientService
from tests.fixtures import ClientFactory, client_dto, create_client_payload


class TestClientService:
    """Test client service methods."""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock client repository."""
        repo = Mock()
        return repo
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock()
        config.DEBUG = True
        return config
    
    @pytest.fixture
    def service(self, mock_repo, mock_config):
        """Create service with mocked dependencies."""
        return ClientService(repo=mock_repo, config=mock_config)
    
    def test_get_client_success(self, service, mock_repo):
        """Get existing client."""
        client = ClientFactory()
        mock_repo.find_by_id.return_value = client
        
        result = service.get_client("user123", str(client.id))
        
        assert result.is_ok()
        assert result.value.name == client.name
        mock_repo.find_by_id.assert_called_once_with(str(client.id))
    
    def test_get_client_not_found(self, service, mock_repo):
        """Get non-existent client."""
        mock_repo.find_by_id.return_value = None
        
        result = service.get_client("user123", "nonexistent")
        
        assert result.is_err()
        assert isinstance(result.error, NotFoundError)
        assert result.error.status == 404
    
    def test_create_client_success(self, service, mock_repo, create_client_payload):
        """Create new client."""
        mock_repo.find_by_email.return_value = None
        mock_repo.save.return_value = "new_client_id"
        
        result = service.create_client("user123", create_client_payload)
        
        assert result.is_ok()
        assert result.value.id == "new_client_id"
        mock_repo.save.assert_called_once()
    
    def test_create_client_duplicate_email(self, service, mock_repo, create_client_payload):
        """Create client with duplicate email."""
        existing_client = ClientFactory(email=create_client_payload.email)
        mock_repo.find_by_email.return_value = existing_client
        
        result = service.create_client("user123", create_client_payload)
        
        assert result.is_err()
        assert isinstance(result.error, DuplicateError)
        assert result.error.status == 409
    
    def test_list_clients(self, service, mock_repo):
        """List all clients."""
        clients = [ClientFactory() for _ in range(3)]
        mock_repo.find_all.return_value = clients
        
        result = service.list_clients("user123")
        
        assert result.is_ok()
        assert len(result.value) == 3
    
    def test_search_clients(self, service, mock_repo):
        """Search clients by name."""
        clients = [ClientFactory(name="Acme Corp")]
        mock_repo.find_by_name.return_value = clients
        
        result = service.search_clients("user123", "Acme")
        
        assert result.is_ok()
        assert len(result.value) == 1
    
    def test_search_clients_minimum_length(self, service, mock_repo):
        """Search term must be minimum length."""
        result = service.search_clients("user123", "A")
        
        assert result.is_err()
        assert "2 characters" in result.error.message
    
    def test_update_client(self, service, mock_repo):
        """Update existing client."""
        client = ClientFactory()
        mock_repo.find_by_id.return_value = client
        
        updated_client = ClientFactory(name="Updated Name")
        mock_repo.update.return_value = updated_client
        
        payload = ClientUpdate(name="Updated Name")
        result = service.update_client("user123", str(client.id), payload)
        
        assert result.is_ok()
        assert result.value.name == "Updated Name"
    
    def test_delete_client(self, service, mock_repo):
        """Delete existing client."""
        mock_repo.exists.return_value = True
        mock_repo.delete.return_value = True
        
        result = service.delete_client("user123", "client_id")
        
        assert result.is_ok()
        mock_repo.delete.assert_called_once_with("client_id")
```

---

## 6. Integration Tests

### File: `tests/integration/conftest.py`
```python
"""Integration test fixtures."""

import pytest
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.mongodb import MongoDbContainer


@pytest.fixture(scope="session")
def mongo_container():
    """MongoDB test container (session-scoped)."""
    container = MongoDbContainer()
    container.start()
    yield container
    container.stop()


@pytest.fixture
def mongo_db(mongo_container):
    """MongoDB test database."""
    client = MongoClient(mongo_container.get_connection_string())
    db = client.test_db
    yield db
    # Cleanup
    client.drop_database("test_db")
    client.close()


@pytest.fixture
def sql_session_factory():
    """SQLAlchemy test session factory."""
    engine = create_engine("sqlite:///:memory:")
    
    # Create tables
    from models import Base
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    yield SessionLocal
    
    engine.dispose()


@pytest.fixture
def sql_session(sql_session_factory):
    """SQLAlchemy test session."""
    session = sql_session_factory()
    yield session
    session.close()
```

### File: `tests/integration/test_client_repository.py`
```python
"""Test ClientRepository with real MongoDB."""

import pytest
from db.repositories.client_repository import ClientRepository
from tests.fixtures import ClientFactory


class TestClientRepository:
    """Integration tests for ClientRepository."""
    
    @pytest.fixture
    def repository(self, mongo_db):
        """Create repository with test MongoDB."""
        return ClientRepository(mongo_db)
    
    def test_create_and_retrieve(self, repository):
        """Create and retrieve client."""
        from models import Client
        client = Client(
            name="Test Corp",
            email="test@example.com",
            phone="555-1234"
        )
        
        client_id = repository.save(client)
        retrieved = repository.find_by_id(client_id)
        
        assert retrieved is not None
        assert retrieved.name == "Test Corp"
        assert retrieved.email == "test@example.com"
    
    def test_unique_email_constraint(self, repository):
        """Email should be unique."""
        from models import Client
        from pymongo.errors import DuplicateKeyError
        
        client1 = Client(
            name="Corp A",
            email="duplicate@example.com",
            phone="555-1111"
        )
        client2 = Client(
            name="Corp B",
            email="duplicate@example.com",
            phone="555-2222"
        )
        
        repository.save(client1)
        
        # Saving duplicate email should raise error
        with pytest.raises(DuplicateKeyError):
            repository.save(client2)
    
    def test_search_by_name(self, repository):
        """Search clients by name."""
        from models import Client
        
        # Create test data
        repository.save(Client(
            name="Acme Corporation",
            email="acme@example.com",
            phone="555-1111"
        ))
        repository.save(Client(
            name="Widget Company",
            email="widget@example.com",
            phone="555-2222"
        ))
        
        results = repository.find_by_name("Acme")
        
        assert len(results) == 1
        assert results[0].name == "Acme Corporation"
    
    def test_update_client(self, repository):
        """Update client fields."""
        from models import Client
        
        client = Client(
            name="Original Name",
            email="test@example.com",
            phone="555-1111"
        )
        client_id = repository.save(client)
        
        updated = repository.update(client_id, {
            "name": "Updated Name",
            "phone": "555-2222"
        })
        
        assert updated.name == "Updated Name"
        assert updated.phone == "555-2222"
        
        # Verify persistence
        retrieved = repository.find_by_id(client_id)
        assert retrieved.name == "Updated Name"
    
    def test_delete_client(self, repository):
        """Delete client."""
        from models import Client
        
        client = Client(
            name="To Delete",
            email="delete@example.com",
            phone="555-1111"
        )
        client_id = repository.save(client)
        
        # Should exist
        assert repository.exists(client_id)
        
        # Delete
        success = repository.delete(client_id)
        assert success
        
        # Should not exist
        assert not repository.exists(client_id)
```

### File: `tests/integration/test_client_workflow.py`
```python
"""Test complete client workflow (E2E-like)."""

import pytest
from core.di import Container
from core.validation import ClientCreate
from config import Config


class TestClientWorkflow:
    """Test complete client management workflows."""
    
    @pytest.fixture
    def container(self, mongo_db, test_config):
        """DI container with test databases."""
        container = Container(test_config)
        container._mongo_client = mongo_db.client
        return container
    
    def test_create_and_retrieve_workflow(self, container):
        """User creates client and retrieves it."""
        service = container.client_service
        user_id = "test_user_123"
        
        # Create client
        payload = ClientCreate(
            name="New Client",
            email="new@example.com",
            phone="555-1234"
        )
        create_result = service.create_client(user_id, payload)
        
        assert create_result.is_ok()
        created_client = create_result.value
        
        # Retrieve created client
        get_result = service.get_client(user_id, created_client.id)
        
        assert get_result.is_ok()
        retrieved = get_result.value
        assert retrieved.name == "New Client"
        assert retrieved.email == "new@example.com"
    
    def test_search_and_update_workflow(self, container):
        """User searches and updates client."""
        service = container.client_service
        user_id = "test_user_456"
        
        # Create initial client
        payload = ClientCreate(
            name="Acme Corporation",
            email="acme@example.com",
            phone="555-5555"
        )
        create_result = service.create_client(user_id, payload)
        assert create_result.is_ok()
        
        # Search for client
        search_result = service.search_clients(user_id, "Acme")
        assert search_result.is_ok()
        assert len(search_result.value) == 1
        
        # Update client
        from core.validation import ClientUpdate
        client_id = search_result.value[0].id
        update_payload = ClientUpdate(name="Acme Corp Updated")
        update_result = service.update_client(user_id, client_id, update_payload)
        
        assert update_result.is_ok()
        assert update_result.value.name == "Acme Corp Updated"
```

---

## 7. Running Tests

### Run all tests
```bash
pytest
```

### Run specific test class
```bash
pytest tests/services/test_client_service.py::TestClientService
```

### Run with coverage
```bash
pytest --cov --cov-report=html
```

### Run only unit tests
```bash
pytest -m unit
```

### Run only integration tests
```bash
pytest -m integration
```

### Run with verbose output
```bash
pytest -v
```

---

## 8. CI/CD Integration

### `.github/workflows/test.yml`
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest --cov
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 9. Quality Metrics

### Code Coverage Goals
- **Overall:** 80%+ coverage
- **Services:** 90%+ coverage (critical business logic)
- **UI pages:** 20%+ coverage (smoke tests only)

### Run coverage report
```bash
pytest --cov --cov-report=html
# Open htmlcov/index.html to view
```

---

## 10. Best Practices

✅ **Do:**
- Test service layer thoroughly
- Mock external dependencies (DB, API)
- Use factories for test data
- Test both success and failure paths
- Use descriptive test names
- Organize tests by layer

❌ **Don't:**
- Test Streamlit UI directly (hard, fragile)
- Skip error path testing
- Use real external services in tests
- Have circular test dependencies
- Mix unit and integration tests

---

## Summary

| Test Type | Speed | Cost | Coverage |
|-----------|-------|------|----------|
| **Unit** | Fast | Low | High |
| **Integration** | Medium | Medium | Medium |
| **UI Smoke** | Slow | High | Low |

**Recommended ratio:** 70% unit, 25% integration, 5% UI smoke.
