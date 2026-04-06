# Practical Implementation Examples

## File: core/errors.py
```python
"""Application error hierarchy and handlers."""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error with user-friendly messaging."""
    
    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN",
        status: int = 500,
        details: Optional[dict] = None
    ):
        self.message = message
        self.code = code
        self.status = status
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Serialize error for API/UI consumption."""
        return {
            "message": self.message,
            "code": self.code,
            "details": self.details
        }
    
    def log(self, user_id: Optional[str] = None):
        """Log error with context."""
        logger.error(
            f"AppError: {self.code} - {self.message}",
            extra={
                "user_id": user_id,
                "code": self.code,
                "details": self.details
            }
        )


class ValidationError(AppError):
    """Input validation failed."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status=400,
            details=details
        )


class NotFoundError(AppError):
    """Resource not found."""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} '{resource_id}' not found",
            code="NOT_FOUND",
            status=404,
            details={"resource": resource, "resource_id": resource_id}
        )


class DuplicateError(AppError):
    """Resource already exists (e.g., duplicate email)."""
    def __init__(self, field: str, value: str):
        super().__init__(
            message=f"{field} '{value}' already exists",
            code="DUPLICATE_ERROR",
            status=409,
            details={"field": field, "value": value}
        )


class AuthorizationError(AppError):
    """User not authorized for this action."""
    def __init__(self, message: str = "You do not have permission for this action"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status=403
        )


class InternalError(AppError):
    """Unexpected internal error."""
    def __init__(self, message: str = "An unexpected error occurred"):
        super().__init__(
            message=message,
            code="INTERNAL_ERROR",
            status=500
        )


def handle_app_error(error: AppError, user_id: Optional[str] = None) -> tuple[str, str]:
    """
    Convert AppError to Streamlit UI components.
    
    Returns: (message, streamlit_severity)
    """
    error.log(user_id)
    
    if error.status == 400:
        return error.message, "error"
    elif error.status == 403:
        return "⛔ " + error.message, "warning"
    elif error.status == 404:
        return "🔍 " + error.message, "info"
    elif error.status == 409:
        return "⚠️ " + error.message, "warning"
    else:
        return "❌ An unexpected error occurred. Please contact support.", "error"
```

---

## File: core/validation.py
```python
"""Pydantic models for input validation."""

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class ClientCreate(BaseModel):
    """Request to create a new client."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v) > 255:
            raise ValueError('Name must be less than 255 characters')
        return v.strip()
    
    @field_validator('phone')
    @classmethod
    def phone_valid_format(cls, v: str) -> str:
        # Remove spaces, dashes, parentheses
        clean = ''.join(c for c in v if c.isdigit())
        if len(clean) < 7:
            raise ValueError('Phone must have at least 7 digits')
        return v


class ClientUpdate(BaseModel):
    """Request to update a client."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ClientDTO(BaseModel):
    """Client data transfer object (response)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    email: str
    phone: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ClientDetailDTO(ClientDTO):
    """Detailed client DTO with extra fields."""
    address: Optional[str] = None
    notes: Optional[str] = None


class PayrollCreate(BaseModel):
    """Request to create payroll entry."""
    
    employee_id: str
    pay_period_start: datetime
    pay_period_end: datetime
    gross_salary: float
    
    @field_validator('gross_salary')
    @classmethod
    def salary_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Salary must be positive')
        return v


class PayrollDTO(BaseModel):
    """Payroll data transfer object."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    employee_id: str
    pay_period_start: datetime
    pay_period_end: datetime
    gross_salary: float
    net_salary: float
    created_at: datetime
```

---

## File: core/result.py
```python
"""Result type for explicit error handling."""

from typing import Generic, TypeVar, Optional, Union, Callable
from dataclasses import dataclass

T = TypeVar('T')  # Success type
E = TypeVar('E')  # Error type


@dataclass
class Result(Generic[T, E]):
    """
    Encapsulate success or failure result.
    
    Usage:
        result = service.create_client(data)
        if result.is_ok():
            client = result.value
        else:
            error = result.error
    """
    
    success: bool
    value: Optional[T] = None
    error: Optional[E] = None
    
    @staticmethod
    def ok(value: T) -> 'Result[T, None]':
        """Create success result."""
        return Result(success=True, value=value, error=None)
    
    @staticmethod
    def err(error: E) -> 'Result[None, E]':
        """Create error result."""
        return Result(success=False, value=None, error=error)
    
    def is_ok(self) -> bool:
        """Check if result is success."""
        return self.success
    
    def is_err(self) -> bool:
        """Check if result is error."""
        return not self.success
    
    def map(self, func: Callable[[T], 'Result[T, E]']) -> 'Result[T, E]':
        """Transform success value; pass through error."""
        if self.is_ok():
            return func(self.value)
        return self
    
    def map_err(self, func: Callable[[E], E]) -> 'Result[T, E]':
        """Transform error; pass through success."""
        if self.is_err():
            return Result.err(func(self.error))
        return self
    
    def unwrap(self) -> T:
        """Get value or raise exception."""
        if self.is_ok():
            return self.value
        raise ValueError(f"Called unwrap on error result: {self.error}")
    
    def unwrap_or(self, default: T) -> T:
        """Get value or return default."""
        return self.value if self.is_ok() else default


# Example usage in services:
"""
def get_client(self, client_id: str) -> Result[ClientDTO, AppError]:
    try:
        client = self.repo.find_by_id(client_id)
        if not client:
            return Result.err(NotFoundError("Client", client_id))
        return Result.ok(ClientDTO.from_orm(client))
    except Exception as e:
        return Result.err(InternalError(str(e)))

# In pages:
result = service.get_client(client_id)
if result.is_ok():
    st.success(f"Found client: {result.value.name}")
else:
    st.error(result.error.message)
"""
```

---

## File: core/di.py
```python
"""Dependency injection container."""

from typing import Optional
import logging
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config, load_config
from db.repositories.client_repository import ClientRepository
from services.client_service import ClientService


logger = logging.getLogger(__name__)


class Container:
    """Service and dependency container."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        self._mongo_client: Optional[MongoClient] = None
        self._sql_engine = None
        self._sql_session_factory = None
        self._client_repo: Optional[ClientRepository] = None
        self._client_service: Optional[ClientService] = None
    
    @property
    def mongo_client(self) -> MongoClient:
        """Lazily initialize MongoDB client."""
        if self._mongo_client is None:
            logger.info(f"Initializing MongoDB: {self.config.MONGO_URI}")
            self._mongo_client = MongoClient(self.config.MONGO_URI)
            # Verify connection
            self._mongo_client.admin.command('ping')
            logger.info("MongoDB connected")
        return self._mongo_client
    
    @property
    def mongo_db(self):
        """Get MongoDB database."""
        return self.mongo_client[self.config.MONGO_DB_NAME]
    
    @property
    def sql_engine(self):
        """Lazily initialize SQLAlchemy engine."""
        if self._sql_engine is None:
            logger.info(f"Initializing SQLite: {self.config.DB_PATH}")
            self._sql_engine = create_engine(
                f"sqlite:///{self.config.DB_PATH}",
                echo=self.config.DEBUG
            )
            logger.info("SQLite connected")
        return self._sql_engine
    
    @property
    def sql_session_factory(self):
        """Get SQLAlchemy session factory."""
        if self._sql_session_factory is None:
            self._sql_session_factory = sessionmaker(bind=self.sql_engine)
        return self._sql_session_factory
    
    def sql_session(self):
        """Create new SQLAlchemy session (context manager)."""
        return self.sql_session_factory()
    
    @property
    def client_repository(self) -> ClientRepository:
        """Get or create ClientRepository."""
        if self._client_repo is None:
            self._client_repo = ClientRepository(self.mongo_db)
        return self._client_repo
    
    @property
    def client_service(self) -> ClientService:
        """Get or create ClientService."""
        if self._client_service is None:
            self._client_service = ClientService(
                repo=self.client_repository,
                config=self.config
            )
        return self._client_service
    
    def close(self):
        """Close all connections."""
        if self._mongo_client:
            self._mongo_client.close()
            logger.info("MongoDB connection closed")
        if self._sql_engine:
            self._sql_engine.dispose()
            logger.info("SQLite connection closed")


# Global singleton
_container: Optional[Container] = None


def get_container(config: Optional[Config] = None) -> Container:
    """Get or create global container."""
    global _container
    if _container is None:
        _container = Container(config)
    return _container


def reset_container():
    """Reset container (for testing)."""
    global _container
    if _container:
        _container.close()
    _container = None
```

---

## File: core/logging.py
```python
"""Logging configuration and utilities."""

import logging
import json
from datetime import datetime
from typing import Optional, Any
import sys


def setup_logging(level: str = "INFO"):
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )


def log_audit(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Optional[dict] = None,
    status: str = "SUCCESS"
):
    """Log user action for audit trail."""
    logger = logging.getLogger("audit")
    
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "status": status,
        "details": details or {}
    }
    
    logger.info(json.dumps(entry))


def log_performance(
    function_name: str,
    duration_ms: float,
    user_id: Optional[str] = None
):
    """Log function performance."""
    logger = logging.getLogger("performance")
    
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "function": function_name,
        "duration_ms": duration_ms,
        "user_id": user_id
    }
    
    if duration_ms > 1000:  # Warn if > 1 second
        logger.warning(json.dumps(entry))
    else:
        logger.debug(json.dumps(entry))


def get_logger(name: str) -> logging.Logger:
    """Get logger for module."""
    return logging.getLogger(name)
```

---

## File: db/repositories/base.py
```python
"""Base repository interface."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any

T = TypeVar('T')  # Entity type


class Repository(ABC, Generic[T]):
    """Abstract repository for CRUD operations."""
    
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[T]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def find_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """Find all entities matching filters."""
        pass
    
    @abstractmethod
    def save(self, entity: T) -> str:
        """Save entity and return ID."""
        pass
    
    @abstractmethod
    def update(self, id: str, updates: Dict[str, Any]) -> Optional[T]:
        """Update entity and return updated entity."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete entity."""
        pass
    
    @abstractmethod
    def exists(self, id: str) -> bool:
        """Check if entity exists."""
        pass
    
    @abstractmethod
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching filters."""
        pass
```

---

## File: db/repositories/client_repository.py
```python
"""MongoDB repository for clients."""

from typing import Optional, List, Dict, Any
from bson import ObjectId
from db.repositories.base import Repository
from models import Client
from core.errors import NotFoundError


class ClientRepository(Repository[Client]):
    """MongoDB repository for client documents."""
    
    def __init__(self, db):
        """Initialize with MongoDB database instance."""
        self.collection = db.clients
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for performance."""
        self.collection.create_index("email", unique=True)
        self.collection.create_index([("name", "text")])  # Full-text search
        self.collection.create_index("created_at")
    
    def find_by_id(self, id: str) -> Optional[Client]:
        """Find client by ID."""
        doc = self.collection.find_one({"_id": ObjectId(id)})
        return Client(**doc) if doc else None
    
    def find_by_email(self, email: str) -> Optional[Client]:
        """Find client by email (unique)."""
        doc = self.collection.find_one({"email": email.lower()})
        return Client(**doc) if doc else None
    
    def find_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Client]:
        """Find all clients matching filters."""
        docs = self.collection.find(filters or {})
        return [Client(**doc) for doc in docs]
    
    def find_by_name(self, name: str, limit: int = 50) -> List[Client]:
        """Search clients by name (case-insensitive, partial match)."""
        docs = self.collection.find(
            {"name": {"$regex": name, "$options": "i"}}
        ).limit(limit)
        return [Client(**doc) for doc in docs]
    
    def save(self, entity: Client) -> str:
        """Save new client and return ID."""
        result = self.collection.insert_one(entity.to_dict())
        return str(result.inserted_id)
    
    def update(self, id: str, updates: Dict[str, Any]) -> Optional[Client]:
        """Update client and return updated entity."""
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": updates},
            return_document=True
        )
        return Client(**result) if result else None
    
    def delete(self, id: str) -> bool:
        """Delete client by ID."""
        result = self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    def exists(self, id: str) -> bool:
        """Check if client exists."""
        return self.collection.find_one({"_id": ObjectId(id)}) is not None
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count clients matching filters."""
        return self.collection.count_documents(filters or {})
```

---

## File: services/client_service.py
```python
"""Client business logic service."""

import logging
from typing import List, Optional
from core.validation import ClientCreate, ClientUpdate, ClientDTO
from core.result import Result
from core.errors import AppError, ValidationError, NotFoundError, DuplicateError
from core.logging import log_audit
from db.repositories.client_repository import ClientRepository
from config import Config

logger = logging.getLogger(__name__)


class ClientService:
    """Business logic for client management."""
    
    def __init__(self, repo: ClientRepository, config: Config):
        self.repo = repo
        self.config = config
    
    def create_client(
        self,
        user_id: str,
        payload: ClientCreate
    ) -> Result[ClientDTO, AppError]:
        """Create new client."""
        try:
            # Check for duplicate email
            existing = self.repo.find_by_email(payload.email)
            if existing:
                error = DuplicateError("email", payload.email)
                log_audit(
                    user_id=user_id,
                    action="create_client",
                    resource_type="client",
                    resource_id="N/A",
                    status="FAILED",
                    details={"error": error.code}
                )
                return Result.err(error)
            
            # Create and save
            from models import Client
            client = Client(
                name=payload.name,
                email=payload.email.lower(),
                phone=payload.phone,
                address=payload.address
            )
            client_id = self.repo.save(client)
            client.id = client_id
            
            # Log action
            log_audit(
                user_id=user_id,
                action="create_client",
                resource_type="client",
                resource_id=client_id
            )
            
            logger.info(f"Created client {client_id}")
            return Result.ok(ClientDTO.from_orm(client))
        
        except Exception as e:
            logger.exception(f"Error creating client: {e}")
            error = AppError(str(e), "INTERNAL_ERROR", 500)
            return Result.err(error)
    
    def get_client(
        self,
        user_id: str,
        client_id: str
    ) -> Result[ClientDTO, AppError]:
        """Get single client by ID."""
        try:
            client = self.repo.find_by_id(client_id)
            if not client:
                error = NotFoundError("Client", client_id)
                log_audit(
                    user_id=user_id,
                    action="get_client",
                    resource_type="client",
                    resource_id=client_id,
                    status="FAILED",
                    details={"error": "NOT_FOUND"}
                )
                return Result.err(error)
            
            return Result.ok(ClientDTO.from_orm(client))
        
        except Exception as e:
            logger.exception(f"Error getting client {client_id}: {e}")
            return Result.err(AppError(str(e), "INTERNAL_ERROR"))
    
    def list_clients(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Result[List[ClientDTO], AppError]:
        """List all clients."""
        try:
            clients = self.repo.find_all()
            # Apply pagination
            clients = clients[skip:skip + limit]
            dtos = [ClientDTO.from_orm(c) for c in clients]
            return Result.ok(dtos)
        
        except Exception as e:
            logger.exception(f"Error listing clients: {e}")
            return Result.err(AppError(str(e), "INTERNAL_ERROR"))
    
    def search_clients(
        self,
        user_id: str,
        search_term: str
    ) -> Result[List[ClientDTO], AppError]:
        """Search clients by name."""
        try:
            if not search_term or len(search_term) < 2:
                error = ValidationError(
                    "Search term must be at least 2 characters",
                    details={"search_term": search_term}
                )
                return Result.err(error)
            
            clients = self.repo.find_by_name(search_term)
            dtos = [ClientDTO.from_orm(c) for c in clients]
            return Result.ok(dtos)
        
        except Exception as e:
            logger.exception(f"Error searching clients: {e}")
            return Result.err(AppError(str(e), "INTERNAL_ERROR"))
    
    def update_client(
        self,
        user_id: str,
        client_id: str,
        payload: ClientUpdate
    ) -> Result[ClientDTO, AppError]:
        """Update existing client."""
        try:
            # Verify exists
            client = self.repo.find_by_id(client_id)
            if not client:
                return Result.err(NotFoundError("Client", client_id))
            
            # Update
            updates = payload.model_dump(exclude_unset=True)
            updated_client = self.repo.update(client_id, updates)
            
            log_audit(
                user_id=user_id,
                action="update_client",
                resource_type="client",
                resource_id=client_id,
                details={"updates": updates}
            )
            
            logger.info(f"Updated client {client_id}")
            return Result.ok(ClientDTO.from_orm(updated_client))
        
        except Exception as e:
            logger.exception(f"Error updating client {client_id}: {e}")
            return Result.err(AppError(str(e), "INTERNAL_ERROR"))
    
    def delete_client(
        self,
        user_id: str,
        client_id: str
    ) -> Result[bool, AppError]:
        """Delete client."""
        try:
            # Verify exists
            if not self.repo.exists(client_id):
                return Result.err(NotFoundError("Client", client_id))
            
            # Delete
            self.repo.delete(client_id)
            
            log_audit(
                user_id=user_id,
                action="delete_client",
                resource_type="client",
                resource_id=client_id
            )
            
            logger.info(f"Deleted client {client_id}")
            return Result.ok(True)
        
        except Exception as e:
            logger.exception(f"Error deleting client {client_id}: {e}")
            return Result.err(AppError(str(e), "INTERNAL_ERROR"))
```

---

## File: ui/pages/clients.py (Refactored)
```python
"""Clients management page."""

import streamlit as st
from typing import Optional
from core.di import get_container
from core.errors import AppError
from core.validation import ClientCreate, ClientUpdate
from core.logging import log_audit

st.set_page_config(page_title="Clients", layout="wide")


def page_clients(user: dict) -> None:
    """Main clients page."""
    st.title("👥 Clients Management")
    
    # Get service from DI container
    container = get_container()
    client_service = container.client_service
    user_id = user.get("id")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["List", "Create", "Search"])
    
    with tab1:
        _render_clients_list(client_service, user_id)
    
    with tab2:
        _render_create_client(client_service, user_id)
    
    with tab3:
        _render_search_clients(client_service, user_id)


def _render_clients_list(client_service, user_id: str) -> None:
    """Render clients list."""
    st.subheader("All Clients")
    
    result = client_service.list_clients(user_id)
    
    if result.is_err():
        _handle_error(result.error, user_id)
        return
    
    clients = result.value
    
    if not clients:
        st.info("No clients found. Create one to get started!")
        return
    
    # Create table
    cols = ["Name", "Email", "Phone", "Created", "Actions"]
    col_widths = [1.5, 2, 1.5, 1.5, 1.5]
    
    st.write("---")
    with st.columns(col_widths):
        for i, col_name in enumerate(cols):
            st.subheader(col_name)
    
    st.write("---")
    
    for client in clients:
        cols = st.columns(col_widths)
        with cols[0]:
            st.text(client.name)
        with cols[1]:
            st.text(client.email)
        with cols[2]:
            st.text(client.phone)
        with cols[3]:
            st.text(str(client.created_at.date()))
        with cols[4]:
            if st.button("🔍 View", key=f"view_{client.id}"):
                st.session_state.selected_client_id = client.id
                st.rerun()


def _render_create_client(client_service, user_id: str) -> None:
    """Render create client form."""
    st.subheader("Create New Client")
    
    with st.form("create_client_form"):
        name = st.text_input("Client Name *", placeholder="Acme Corp")
        email = st.text_input("Email *", placeholder="contact@acme.com")
        phone = st.text_input("Phone *", placeholder="555-1234")
        address = st.text_area("Address", placeholder="123 Main St, City, State")
        
        submitted = st.form_submit_button("✅ Create Client")
    
    if submitted:
        # Validate with Pydantic
        try:
            payload = ClientCreate(
                name=name,
                email=email,
                phone=phone,
                address=address
            )
        except Exception as e:
            st.error(f"❌ Validation Error: {str(e)}")
            return
        
        # Call service
        result = client_service.create_client(user_id, payload)
        
        if result.is_ok():
            st.success(f"✅ Client '{result.value.name}' created successfully!")
            st.balloons()
        else:
            _handle_error(result.error, user_id)


def _render_search_clients(client_service, user_id: str) -> None:
    """Render search clients."""
    st.subheader("Search Clients")
    
    search_term = st.text_input(
        "Search by name",
        placeholder="Enter client name (min 2 characters)"
    )
    
    if search_term and len(search_term) >= 2:
        result = client_service.search_clients(user_id, search_term)
        
        if result.is_err():
            _handle_error(result.error, user_id)
            return
        
        clients = result.value
        
        if not clients:
            st.info(f"No clients found matching '{search_term}'")
        else:
            st.success(f"Found {len(clients)} client(s)")
            for client in clients:
                with st.expander(f"{client.name} ({client.email})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Email:** {client.email}")
                        st.write(f"**Phone:** {client.phone}")
                    with col2:
                        st.write(f"**Created:** {client.created_at}")


def _handle_error(error: AppError, user_id: str) -> None:
    """Display error to user."""
    error.log(user_id)
    
    if error.status == 400:
        st.error(f"❌ {error.message}")
    elif error.status == 403:
        st.warning(f"⛔ {error.message}")
    elif error.status == 404:
        st.info(f"🔍 {error.message}")
    elif error.status == 409:
        st.warning(f"⚠️ {error.message}")
    else:
        st.error("❌ An unexpected error occurred. Please contact support.")
```

---

## Summary of Improvements

✅ **Error handling** - Custom exception hierarchy
✅ **Validation** - Pydantic models as single source of truth
✅ **Dependency injection** - Loose coupling, easier testing
✅ **Repository pattern** - DB abstraction
✅ **Result type** - Explicit success/error handling
✅ **Logging** - Audit trail for compliance
✅ **DTOs** - Clear API contracts
✅ **Service layer** - Business logic separated from UI

**Next Steps:**
1. Copy these files to your project
2. Update `app.py` to use `get_container()`
3. Update existing pages to use the refactored services
4. Add tests using the DI container for mocking
