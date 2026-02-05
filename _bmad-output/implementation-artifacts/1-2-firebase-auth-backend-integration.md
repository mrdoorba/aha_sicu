# Story 1.2: Firebase Auth Backend Integration

Status: done

## Story

As a **system**,
I want **to validate Firebase JWT tokens on API requests**,
So that **only authenticated users can access protected endpoints**.

## Acceptance Criteria

1. **Given** a request to any `/api/v1/*` endpoint **When** the request has no `Authorization` header **Then** return 401 Unauthorized with `{"code": "AUTH_TOKEN_MISSING", "detail": "Authorization header required"}`

2. **Given** a request with `Authorization: Bearer <invalid_token>` **When** the backend validates the token via Firebase Admin SDK **Then** return 401 Unauthorized with `{"code": "AUTH_TOKEN_INVALID", "detail": "Token validation failed"}`

3. **Given** a request with a valid Firebase JWT token **When** the backend validates the token **Then**:
   - Extract user info (uid, email) from the token
   - Check if user exists in `users` table by `firebase_uid`
   - If user doesn't exist, create record with role `member`
   - Update `last_login` timestamp
   - Attach user context to request for downstream handlers

4. **Database Migration:** Create `users` table with the following schema:
   - `id` SERIAL PRIMARY KEY
   - `firebase_uid` VARCHAR(128) UNIQUE NOT NULL
   - `email` VARCHAR(255) NOT NULL
   - `role` VARCHAR(20) DEFAULT 'member' (values: member, leader, admin)
   - `created_at` TIMESTAMPTZ DEFAULT NOW()
   - `last_login` TIMESTAMPTZ

## Tasks / Subtasks

- [x] Task 1: Add Firebase Admin SDK and Database Dependencies (AC: #1, #2, #3)
  - [x] Add `firebase-admin>=6.0.0` to pyproject.toml
  - [x] Add `asyncpg>=0.30.0` to pyproject.toml for Neon PostgreSQL connection
  - [x] Update `.env.example` with Firebase and database configuration
  - [x] Run `uv sync` to install dependencies

- [x] Task 2: Create Database Migration for Users Table (AC: #4)
  - [x] Set up Alembic in raw SQL mode (no ORM)
  - [x] Create initial migration file: `001_create_users_table.py`
  - [x] Include all required columns with correct types and constraints
  - [x] Add index on `firebase_uid` for fast lookups
  - [x] Test migration runs successfully

- [x] Task 3: Implement Database Connection Pool (AC: #3)
  - [x] Implement `backend/app/db/connection.py` with asyncpg pool
  - [x] Add connection pool lifecycle to FastAPI lifespan events
  - [x] Create `get_db` dependency for request-scoped connections
  - [x] Add connection pool configuration to `config.py`

- [x] Task 4: Implement User Queries (AC: #3)
  - [x] Create `backend/app/db/queries/users.py`
  - [x] Implement `get_user_by_firebase_uid(conn, firebase_uid)` query
  - [x] Implement `create_user(conn, firebase_uid, email)` query
  - [x] Implement `update_last_login(conn, user_id)` query
  - [x] Use parameterized SQL (`$1, $2`) to prevent SQL injection

- [x] Task 5: Implement Firebase Token Validation (AC: #1, #2, #3)
  - [x] Implement `backend/app/core/security.py` with `verify_firebase_token(token)` function
  - [x] Initialize Firebase Admin SDK from credentials (env var or secret)
  - [x] Handle token verification errors with proper error codes
  - [x] Extract `uid` and `email` from decoded token

- [x] Task 6: Create Auth Middleware/Dependency (AC: #1, #2, #3)
  - [x] Implement `get_current_user` dependency in `backend/app/core/dependencies.py`
  - [x] Extract Bearer token from Authorization header
  - [x] Return 401 with `AUTH_TOKEN_MISSING` if no header
  - [x] Validate token and return 401 with `AUTH_TOKEN_INVALID` if invalid
  - [x] Create/update user in database (upsert pattern)
  - [x] Return user context (id, email, role) for downstream handlers

- [x] Task 7: Update Exception Handling (AC: #1, #2)
  - [x] Add `AuthException` class to `backend/app/core/exceptions.py`
  - [x] Define error codes: `AUTH_TOKEN_MISSING`, `AUTH_TOKEN_INVALID`, `AUTH_TOKEN_EXPIRED`
  - [x] Create exception handler in middleware that returns structured JSON

- [x] Task 8: Create Protected Test Endpoint (AC: #1, #2, #3)
  - [x] Add `/api/v1/me` endpoint that requires authentication
  - [x] Returns current user info (id, email, role, last_login)
  - [x] Wire authentication dependency to endpoint

- [x] Task 9: Write Tests (AC: #1, #2, #3)
  - [x] Unit test: `verify_firebase_token` with mocked Firebase SDK
  - [x] Integration test: `/api/v1/me` returns 401 without token
  - [x] Integration test: `/api/v1/me` returns 401 with invalid token
  - [x] Integration test: `/api/v1/me` returns user with valid token (mocked)
  - [x] Test user creation on first login
  - [x] Test `last_login` timestamp update

## Dev Notes

### Technical Stack Requirements

| Component | Technology | Version | Notes |
|-----------|------------|---------|-------|
| Firebase Admin SDK | firebase-admin | 6.x | Token verification |
| Database Driver | asyncpg | 0.30+ | Async PostgreSQL |
| Migration Tool | Alembic | 1.x | Raw SQL mode |
| Database | Neon PostgreSQL | - | Via asyncpg |

### Firebase Admin SDK Setup

**Initialization Pattern (config.py):**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Firebase
    firebase_credentials_path: str | None = None  # Path to service account JSON
    firebase_credentials_json: str | None = None  # Raw JSON for production (Secret Manager)

    # Database
    database_url: str  # Neon connection string
    database_pool_min: int = 5
    database_pool_max: int = 20
```

**Firebase Init Pattern (security.py):**
```python
import firebase_admin
from firebase_admin import credentials, auth

def init_firebase(settings: Settings):
    """Initialize Firebase Admin SDK."""
    if firebase_admin._apps:
        return  # Already initialized

    if settings.firebase_credentials_json:
        # Production: credentials from Secret Manager
        import json
        cred_dict = json.loads(settings.firebase_credentials_json)
        cred = credentials.Certificate(cred_dict)
    elif settings.firebase_credentials_path:
        # Development: credentials from file
        cred = credentials.Certificate(settings.firebase_credentials_path)
    else:
        raise ValueError("Firebase credentials not configured")

    firebase_admin.initialize_app(cred)

async def verify_firebase_token(token: str) -> dict:
    """Verify Firebase ID token and return decoded claims."""
    try:
        decoded = auth.verify_id_token(token)
        return {
            "uid": decoded["uid"],
            "email": decoded.get("email"),
        }
    except auth.ExpiredIdTokenError:
        raise AuthException(code="AUTH_TOKEN_EXPIRED", detail="Token has expired")
    except auth.InvalidIdTokenError:
        raise AuthException(code="AUTH_TOKEN_INVALID", detail="Token validation failed")
    except Exception:
        raise AuthException(code="AUTH_TOKEN_INVALID", detail="Token validation failed")
```

### Database Connection Pattern

**Connection Pool (connection.py):**
```python
import asyncpg
from contextlib import asynccontextmanager

class DatabasePool:
    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def init(self, dsn: str, min_size: int = 5, max_size: int = 20):
        self.pool = await asyncpg.create_pool(dsn, min_size=min_size, max_size=max_size)

    async def close(self):
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def connection(self):
        async with self.pool.acquire() as conn:
            yield conn

db = DatabasePool()
```

**FastAPI Lifespan (main.py):**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.connection import db
from app.core.security import init_firebase
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_firebase(settings)
    await db.init(settings.database_url, settings.database_pool_min, settings.database_pool_max)
    yield
    # Shutdown
    await db.close()

app = FastAPI(title="Store ICU API", version="0.1.0", lifespan=lifespan)
```

### User Queries Pattern

**Parameterized SQL (queries/users.py):**
```python
from asyncpg import Connection

async def get_user_by_firebase_uid(conn: Connection, firebase_uid: str) -> dict | None:
    """Get user by Firebase UID."""
    row = await conn.fetchrow(
        "SELECT id, firebase_uid, email, role, created_at, last_login FROM users WHERE firebase_uid = $1",
        firebase_uid
    )
    return dict(row) if row else None

async def create_user(conn: Connection, firebase_uid: str, email: str) -> dict:
    """Create new user with default role."""
    row = await conn.fetchrow(
        """
        INSERT INTO users (firebase_uid, email, role, last_login)
        VALUES ($1, $2, 'member', NOW())
        RETURNING id, firebase_uid, email, role, created_at, last_login
        """,
        firebase_uid, email
    )
    return dict(row)

async def update_last_login(conn: Connection, user_id: int) -> None:
    """Update user's last login timestamp."""
    await conn.execute(
        "UPDATE users SET last_login = NOW() WHERE id = $1",
        user_id
    )
```

### Authentication Dependency Pattern

**Get Current User (dependencies.py):**
```python
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_firebase_token
from app.core.exceptions import AuthException
from app.db.connection import db
from app.db.queries import users as user_queries

security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Validate token and return current user context."""
    # Check for Authorization header
    if not credentials:
        raise AuthException(code="AUTH_TOKEN_MISSING", detail="Authorization header required")

    # Verify Firebase token
    token_data = await verify_firebase_token(credentials.credentials)

    # Get or create user in database
    async with db.connection() as conn:
        user = await user_queries.get_user_by_firebase_uid(conn, token_data["uid"])

        if not user:
            # First login - create user
            user = await user_queries.create_user(conn, token_data["uid"], token_data["email"])
        else:
            # Update last login
            await user_queries.update_last_login(conn, user["id"])

    return user
```

### Exception Handling Pattern

**Custom Exceptions (exceptions.py):**
```python
class AppException(Exception):
    """Base application exception."""
    def __init__(self, code: str, detail: str, status_code: int = 400):
        self.code = code
        self.detail = detail
        self.status_code = status_code

class AuthException(AppException):
    """Authentication related exceptions."""
    def __init__(self, code: str, detail: str):
        super().__init__(code=code, detail=detail, status_code=401)
```

**Exception Handler (middleware.py):**
```python
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException
from datetime import datetime, timezone

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "detail": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
```

### Database Migration Pattern

**Alembic Setup:**
```
backend/app/db/migrations/
├── alembic.ini
├── env.py
└── versions/
    └── 001_create_users_table.py
```

**Migration File (001_create_users_table.py):**
```python
"""Create users table

Revision ID: 001
Create Date: 2026-02-05
"""
from alembic import op

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            firebase_uid VARCHAR(128) UNIQUE NOT NULL,
            email VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'member' CHECK (role IN ('member', 'leader', 'admin')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            last_login TIMESTAMPTZ
        );

        CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);
    """)

def downgrade():
    op.execute("""
        DROP INDEX IF EXISTS idx_users_firebase_uid;
        DROP TABLE IF EXISTS users;
    """)
```

### API Endpoint Pattern

**Protected Endpoint Example:**
```python
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["auth"])

@router.get("/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current authenticated user info."""
    return {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "last_login": user["last_login"].isoformat() if user["last_login"] else None,
    }
```

### Project Structure Notes

**Files to Create/Modify:**

| File | Action | Purpose |
|------|--------|---------|
| `backend/pyproject.toml` | Modify | Add firebase-admin, asyncpg |
| `backend/app/config.py` | Modify | Add Firebase and DB settings |
| `backend/app/main.py` | Modify | Add lifespan events, exception handlers |
| `backend/app/db/connection.py` | Modify | Implement connection pool |
| `backend/app/db/queries/users.py` | Create | User database queries |
| `backend/app/db/migrations/` | Create | Alembic setup and migrations |
| `backend/app/core/security.py` | Modify | Firebase token verification |
| `backend/app/core/dependencies.py` | Modify | Auth dependency |
| `backend/app/core/exceptions.py` | Modify | Custom exceptions |
| `backend/app/core/middleware.py` | Modify | Exception handlers |
| `backend/app/modules/auth/` | Create | Auth module (router, schemas) |
| `backend/.env.example` | Modify | Add new env vars |
| `backend/tests/unit/test_security.py` | Create | Security unit tests |
| `backend/tests/integration/api/test_auth.py` | Create | Auth integration tests |

### Environment Variables

**Add to `.env.example`:**
```env
# Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
# For production, use FIREBASE_CREDENTIALS_JSON with raw JSON from Secret Manager

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname
DATABASE_POOL_MIN=5
DATABASE_POOL_MAX=20
```

### Error Code Reference

| Code | HTTP Status | When |
|------|-------------|------|
| `AUTH_TOKEN_MISSING` | 401 | No Authorization header |
| `AUTH_TOKEN_INVALID` | 401 | Token validation failed |
| `AUTH_TOKEN_EXPIRED` | 401 | Token has expired |

### Testing Strategy

**Unit Tests (mocked Firebase):**
```python
import pytest
from unittest.mock import patch, MagicMock
from app.core.security import verify_firebase_token

@pytest.mark.asyncio
async def test_verify_token_valid():
    with patch("firebase_admin.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        result = await verify_firebase_token("valid-token")
        assert result["uid"] == "test-uid"
        assert result["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_verify_token_invalid():
    with patch("firebase_admin.auth.verify_id_token") as mock_verify:
        from firebase_admin.auth import InvalidIdTokenError
        mock_verify.side_effect = InvalidIdTokenError("Invalid token")
        with pytest.raises(AuthException) as exc_info:
            await verify_firebase_token("invalid-token")
        assert exc_info.value.code == "AUTH_TOKEN_INVALID"
```

**Integration Tests (mocked auth dependency):**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_me_without_token(client):
    response = client.get("/api/v1/me")
    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_TOKEN_MISSING"

def test_me_with_invalid_token(client):
    response = client.get("/api/v1/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_TOKEN_INVALID"
```

### Anti-Patterns to Avoid

1. **DO NOT** store Firebase credentials in code or commit to git
2. **DO NOT** use ORM (SQLAlchemy, SQLModel) - use asyncpg with raw SQL
3. **DO NOT** create synchronous database connections - always use async
4. **DO NOT** skip parameterized queries - always use `$1, $2` placeholders
5. **DO NOT** catch all exceptions silently - log and re-raise appropriately
6. **DO NOT** store tokens in the database - they're verified on each request
7. **DO NOT** implement custom JWT verification - use Firebase Admin SDK

### Previous Story Intelligence

From Story 1.1 implementation:
- Backend uses UV for package management (`uv sync`, `uv run`)
- FastAPI app is in `backend/app/main.py` with health endpoint at `/health`
- Pydantic settings use `model_config = SettingsConfigDict(...)` pattern (not deprecated `class Config`)
- Project structure follows modular domain-driven design
- Python 3.14 is required (specified in pyproject.toml)
- Tailwind CSS v4 is used in frontend (not directly relevant but noted)
- CI runs `uv run pytest` for backend tests

### Git Intelligence Summary

Recent commits show Story 1.1 was completed with:
- Backend structure with health endpoint
- Frontend structure with React + Vite + Tailwind
- Infrastructure with Terraform placeholders
- Code review fixes applied (Pydantic config pattern, type declarations)

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.2: Firebase Auth Backend Integration]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication Flow]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Error Handling]
- [Source: _bmad-output/planning-artifacts/architecture.md#API & Communication]
- [Source: _bmad-output/implementation-artifacts/1-1-initialize-project-structure.md#Dev Agent Record]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None - Implementation completed successfully without errors.

### Completion Notes List

- **Task 1:** Added firebase-admin>=6.0.0, asyncpg>=0.30.0, and alembic>=1.13.0 to pyproject.toml. Updated .env.example with Firebase and database configuration variables. Dependencies installed via `uv sync`.

- **Task 2:** Set up Alembic in raw SQL mode with migrations directory structure. Created initial migration `001_create_users_table.py` with users table schema including all required columns, constraints, and index on firebase_uid.

- **Task 3:** Implemented DatabasePool class in connection.py using asyncpg with async context manager for connection acquisition. Added lifespan events in main.py for pool initialization and cleanup. Updated config.py with database settings.

- **Task 4:** Created users.py with parameterized SQL queries: get_user_by_firebase_uid, create_user, and update_last_login. All queries use $1, $2 placeholders for SQL injection prevention.

- **Task 5:** Implemented verify_firebase_token in security.py with Firebase Admin SDK initialization supporting both file-based (dev) and JSON-based (production) credentials. Proper error handling for expired, invalid, and generic token errors.

- **Task 6:** Implemented get_current_user dependency using HTTPBearer for token extraction. Handles missing token (AUTH_TOKEN_MISSING) and invalid token (AUTH_TOKEN_INVALID) cases. Creates new user on first login or updates last_login for existing users.

- **Task 7:** Created AppException base class and AuthException subclass in exceptions.py. Implemented app_exception_handler in middleware.py returning structured JSON with code, detail, and timestamp.

- **Task 8:** Created auth module with router.py containing /api/v1/me endpoint. Returns authenticated user info (id, email, role, last_login). Wired to main.py via include_router.

- **Task 9:** Created comprehensive test suite with 10 tests (4 unit tests for security.py, 5 integration tests for /api/v1/me endpoint, 1 health check test). All tests pass using mocked Firebase SDK and database connections.

### File List

**New Files:**
- backend/app/db/queries/users.py
- backend/app/db/migrations/alembic.ini
- backend/app/db/migrations/env.py
- backend/app/db/migrations/script.py.mako
- backend/app/db/migrations/versions/__init__.py
- backend/app/db/migrations/versions/001_create_users_table.py
- backend/app/modules/auth/__init__.py
- backend/app/modules/auth/router.py
- backend/app/modules/auth/schemas.py
- backend/tests/unit/__init__.py
- backend/tests/unit/test_security.py
- backend/tests/integration/__init__.py
- backend/tests/integration/api/__init__.py
- backend/tests/integration/api/test_auth.py
- backend/tests/conftest.py

**Modified Files:**
- backend/pyproject.toml
- backend/uv.lock
- backend/.env.example
- backend/app/config.py
- backend/app/main.py
- backend/app/core/security.py
- backend/app/core/dependencies.py
- backend/app/core/exceptions.py
- backend/app/core/middleware.py
- backend/app/db/connection.py

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-02-05 | Initial implementation of Firebase Auth Backend Integration - all 9 tasks completed | Claude Opus 4.5 |
| 2026-02-05 | Code review fixes: (1) Fixed stale last_login by re-fetching user after update, (2) Fixed blocking event loop by using asyncio.to_thread for Firebase SDK call, (3) Added missing test assertions for update_last_login and create_user args, (4) Moved client fixture to conftest.py, (5) Added uv.lock to File List, (6) Added schemas.py to auth module with UserResponse, (7) Added logging to exception handler | Claude Opus 4.5 |
