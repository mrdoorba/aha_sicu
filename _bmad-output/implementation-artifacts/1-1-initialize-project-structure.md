# Story 1.1: Initialize Project Structure

Status: review

## Story

As a **developer**,
I want **the project scaffolded with the lean modular structure**,
So that **all future development has a consistent foundation to build upon**.

## Acceptance Criteria

1. **Backend structure exists and runs:**
   - `backend/app/main.py` - FastAPI app with health check endpoint returning `{"status": "healthy"}`
   - `backend/app/config.py` - Pydantic BaseSettings for configuration
   - `backend/app/core/` - Contains `dependencies.py`, `exceptions.py`, `middleware.py`, `security.py` (all as placeholder files with basic structure)
   - `backend/app/db/` - Contains `connection.py`, `queries/` directory, `migrations/` directory
   - `backend/app/modules/` - Contains `__init__.py` placeholder
   - `backend/app/calculators/` - Contains `__init__.py` placeholder
   - `backend/pyproject.toml` - UV project config with dependencies
   - `backend/Dockerfile` - Container configuration for Cloud Run
   - `backend/.env.example` - Example environment variables
   - Backend starts locally with `uv run uvicorn app.main:app` returning `{"status": "healthy"}` at `/health`

2. **Frontend structure exists and runs:**
   - `frontend/src/main.tsx` - React app entry point
   - `frontend/src/App.tsx` - Root component with placeholder content
   - `frontend/src/index.css` - Tailwind CSS imports
   - `frontend/src/components/` - Empty directory for components
   - `frontend/src/pages/` - Empty directory for pages
   - `frontend/src/hooks/` - Empty directory for hooks
   - `frontend/src/services/` - Empty directory for API client
   - `frontend/src/firebase/` - Empty directory for Firebase config
   - `frontend/src/context/` - Empty directory for React Context
   - `frontend/package.json` - Dependencies including React, Vite, TypeScript, Tailwind, TanStack Query
   - `frontend/vite.config.ts` - Vite configuration
   - `frontend/tailwind.config.js` - Tailwind configuration
   - `frontend/tsconfig.json` - TypeScript configuration (strict mode)
   - Frontend starts locally with `npm run dev` showing a placeholder page

3. **Infrastructure structure exists:**
   - `infrastructure/terraform/main.tf` - Provider config placeholder
   - `infrastructure/terraform/variables.tf` - Variables placeholder
   - `.github/workflows/ci.yml` - CI workflow stub

4. **Root project files:**
   - `README.md` - Basic project documentation
   - `.gitignore` - Appropriate ignores for Python, Node, Terraform

## Tasks / Subtasks

- [x] Task 1: Initialize Backend Structure (AC: #1)
  - [x] Create `backend/` directory with Python package structure
  - [x] Create `backend/pyproject.toml` with UV config and dependencies (FastAPI, uvicorn, pydantic-settings)
  - [x] Create `backend/app/__init__.py`
  - [x] Create `backend/app/main.py` with FastAPI app and health endpoint
  - [x] Create `backend/app/config.py` with Pydantic BaseSettings
  - [x] Create `backend/app/core/` directory with placeholder files
  - [x] Create `backend/app/db/` directory with connection.py, queries/, migrations/
  - [x] Create `backend/app/modules/__init__.py`
  - [x] Create `backend/app/calculators/__init__.py`
  - [x] Create `backend/Dockerfile` for Cloud Run
  - [x] Create `backend/.env.example`
  - [x] Verify backend runs with `uv run uvicorn app.main:app`

- [x] Task 2: Initialize Frontend Structure (AC: #2)
  - [x] Create `frontend/` using Vite React TypeScript template
  - [x] Install and configure Tailwind CSS
  - [x] Install TanStack Query, React Hook Form, openapi-fetch
  - [x] Create directory structure: components/, pages/, hooks/, services/, firebase/, context/
  - [x] Configure `tsconfig.json` with strict mode
  - [x] Update `vite.config.ts` for project needs
  - [x] Create placeholder App.tsx with basic content
  - [x] Verify frontend runs with `npm run dev`

- [x] Task 3: Initialize Infrastructure Structure (AC: #3)
  - [x] Create `infrastructure/terraform/` directory
  - [x] Create `main.tf` with provider placeholder
  - [x] Create `variables.tf` with basic variables
  - [x] Create `.github/workflows/ci.yml` stub

- [x] Task 4: Root Project Setup (AC: #4)
  - [x] Create `README.md` with project overview
  - [x] Create `.gitignore` for Python, Node, Terraform, environment files

## Dev Notes

### Technical Stack Requirements

| Component | Technology | Version |
|-----------|------------|---------|
| Backend Language | Python | 3.14 |
| Backend Framework | FastAPI | latest |
| Package Manager (Backend) | UV | latest |
| Frontend Framework | React | 18.x |
| Frontend Build Tool | Vite | 5.x |
| Frontend Language | TypeScript | 5.x (strict mode) |
| Styling | Tailwind CSS | 3.x |
| State Management | TanStack Query | 5.x |
| Forms | React Hook Form | 7.x |
| API Client | openapi-fetch | latest |

### Backend Structure Pattern

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Pydantic BaseSettings
│   ├── core/                      # Core infrastructure (shared)
│   │   ├── __init__.py
│   │   ├── dependencies.py        # DI: auth, db connections
│   │   ├── exceptions.py          # Custom exceptions
│   │   ├── middleware.py          # Logging, error handling
│   │   └── security.py            # Firebase Auth validation
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py          # Neon connection pool
│   │   ├── queries/               # Raw SQL or query builders
│   │   └── migrations/            # Schema migrations
│   ├── modules/                   # Feature modules (domain-driven)
│   │   └── __init__.py
│   └── calculators/               # Calculation engine (isolated)
│       └── __init__.py
├── tests/
├── Dockerfile
├── pyproject.toml
└── .env.example
```

### Frontend Structure Pattern

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css                  # Tailwind imports
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── services/                  # API client
│   ├── firebase/                  # Firebase Auth config
│   └── context/                   # React Context (auth only)
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

### Naming Conventions (MUST FOLLOW)

| Element | Pattern | Example |
|---------|---------|---------|
| Python files | `snake_case.py` | `brand_service.py` |
| Python functions | `snake_case` | `get_brand_by_id()` |
| Python classes | `PascalCase` | `BrandService` |
| TypeScript files (components) | `PascalCase.tsx` | `BrandCard.tsx` |
| TypeScript files (utilities) | `camelCase.ts` | `apiClient.ts` |
| TypeScript functions | `camelCase` | `getBrands()` |
| TypeScript components | `PascalCase` | `<BrandCard />` |

### Key Configuration Details

**pyproject.toml minimum dependencies:**
```toml
[project]
name = "store-icu-backend"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic-settings>=2.6.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**package.json minimum dependencies:**
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@tanstack/react-query": "^5.0.0",
    "react-hook-form": "^7.0.0",
    "openapi-fetch": "^0.12.0"
  },
  "devDependencies": {
    "typescript": "^5.6.0",
    "vite": "^5.4.0",
    "@vitejs/plugin-react": "^4.3.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

**Dockerfile pattern:**
```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install UV
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**main.py pattern:**
```python
from fastapi import FastAPI

app = FastAPI(title="Store ICU API", version="0.1.0")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Resource Naming Convention

- Resource prefix: `aha_sicu_`
- Region: `asia-southeast1` (Singapore)
- Firebase uses hyphens: `aha-sicu`

### Project Structure Notes

- This is a **greenfield project** - no existing code to maintain compatibility with
- Backend and frontend are **separate deployables** (Cloud Run + Firebase Hosting)
- Use **modular domain-driven structure** for backend to support future feature modules
- **No ORM** - will use asyncpg + parameterized SQL in later stories
- **Calculators are isolated** - pure functions with no I/O dependencies

### Anti-Patterns to Avoid

1. **DO NOT** use SQLModel, SQLAlchemy, or any ORM - project uses asyncpg + raw SQL
2. **DO NOT** install Firebase SDK yet - that's Story 1.2
3. **DO NOT** create database tables yet - migrations come in Story 1.2
4. **DO NOT** add authentication middleware yet - that's Story 1.2
5. **DO NOT** create actual API endpoints beyond health check - those come in later epics
6. **DO NOT** use pip or poetry - use UV for backend package management
7. **DO NOT** add dark mode to frontend - light mode only per UX spec

### Verification Commands

**Backend verification:**
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
# Then visit http://localhost:8000/health
# Expected response: {"status": "healthy"}
```

**Frontend verification:**
```bash
cd frontend
npm install
npm run dev
# Then visit http://localhost:5173
# Expected: Placeholder page loads without errors
```

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure]
- [Source: _bmad-output/planning-artifacts/architecture.md#Starter Template Evaluation]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1: Initialize Project Structure]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Tailwind CSS v4 required @tailwindcss/postcss plugin and @import syntax instead of v3 directives

### Completion Notes List

- Task 1: Created backend structure with FastAPI, health endpoint, and modular package layout
- Task 2: Scaffolded frontend with Vite + React + TypeScript, configured Tailwind CSS v4, installed TanStack Query/RHF/openapi-fetch
- Task 3: Created Terraform structure with GCP provider and GitHub Actions CI workflow
- Task 4: Added README with project overview and getting started guide

### File List

**New Files:**
- backend/pyproject.toml
- backend/Dockerfile
- backend/.env.example
- backend/uv.lock
- backend/app/__init__.py
- backend/app/main.py
- backend/app/config.py
- backend/app/core/__init__.py
- backend/app/core/dependencies.py
- backend/app/core/exceptions.py
- backend/app/core/middleware.py
- backend/app/core/security.py
- backend/app/db/__init__.py
- backend/app/db/connection.py
- backend/app/db/queries/__init__.py
- backend/app/db/migrations/__init__.py
- backend/app/modules/__init__.py
- backend/app/calculators/__init__.py
- backend/tests/__init__.py
- backend/tests/test_main.py
- frontend/ (scaffolded via Vite template)
- frontend/package.json
- frontend/vite.config.ts
- frontend/postcss.config.js
- frontend/tsconfig.json
- frontend/tsconfig.app.json
- frontend/tsconfig.node.json
- frontend/src/main.tsx
- frontend/src/App.tsx
- frontend/src/index.css
- frontend/src/components/.gitkeep
- frontend/src/pages/.gitkeep
- frontend/src/hooks/.gitkeep
- frontend/src/services/.gitkeep
- frontend/src/firebase/.gitkeep
- frontend/src/context/.gitkeep
- infrastructure/terraform/main.tf
- infrastructure/terraform/variables.tf
- .github/workflows/ci.yml
- README.md

## Change Log

- 2026-02-05: Story 1.1 implemented - project structure initialized with backend, frontend, infrastructure
