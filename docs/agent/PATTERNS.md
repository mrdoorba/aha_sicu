# PATTERNS.md -- Step-by-step recipes for common code changes

Each recipe lists exact files to create or modify, with code templates extracted from real project code. Follow the steps in order.

---

## Recipe 1: Add a New API Endpoint (Backend Module)

Template module: `backend/app/modules/brands/` (simplest complete module).

### Step 1. Create the module directory

```
backend/app/modules/<name>/
```

### Step 2. Create `__init__.py`

File: `backend/app/modules/<name>/__init__.py`

```python
```

(Empty file.)

### Step 3. Create `schemas.py` with Pydantic models

File: `backend/app/modules/<name>/schemas.py`

```python
"""Pydantic schemas for <name> module."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class <Name>Item(BaseModel):
    """Individual item in response."""

    id: int
    # ... your fields ...
    updated_at: datetime


class <Name>ListResponse(BaseModel):
    """Paginated response."""

    items: list[<Name>Item]
    total: int
    page: int
    limit: int
    pages: int
```

### Step 4. Create `service.py` with business logic

File: `backend/app/modules/<name>/service.py`

```python
"""<Name> service for business logic."""

import math

from app.core.exceptions import AppException
from app.db.connection import db
from app.db.queries import <name> as <name>_queries
from app.modules.<name>.schemas import <Name>Item, <Name>ListResponse


async def get_<name>s_paginated(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
) -> <Name>ListResponse:
    """Get paginated list with optional search."""
    offset = (page - 1) * limit

    async with db.connection() as conn:
        rows = await <name>_queries.get_<name>s(conn, limit=limit, offset=offset, search=search)
        total = await <name>_queries.get_<name>s_count(conn, search=search)

    items = [<Name>Item(**row) for row in rows]
    pages = math.ceil(total / limit) if total > 0 else 0

    return <Name>ListResponse(items=items, total=total, page=page, limit=limit, pages=pages)


async def get_<name>_detail(<name>_id: int) -> <Name>Item:
    """Get a single item by ID."""
    async with db.connection() as conn:
        row = await <name>_queries.get_<name>_by_id(conn, <name>_id)

    if not row:
        raise AppException(code="<NAME>_NOT_FOUND", detail="<Name> not found", status_code=404)

    return <Name>Item(**row)
```

### Step 5. Create `router.py` with APIRouter

File: `backend/app/modules/<name>/router.py`

```python
"""<Name> API endpoints."""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user
from app.modules.<name>.schemas import <Name>Item, <Name>ListResponse
from app.modules.<name>.service import get_<name>_detail, get_<name>s_paginated

router = APIRouter(prefix="/api/v1/<name>s", tags=["<name>s"])


@router.get("", response_model=<Name>ListResponse)
async def list_<name>s(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, max_length=200, description="Search term"),
    current_user: dict = Depends(get_current_user),
) -> <Name>ListResponse:
    """Get paginated list."""
    return await get_<name>s_paginated(page=page, limit=limit, search=search)


@router.get("/{<name>_id}", response_model=<Name>Item)
async def get_<name>(
    <name>_id: int,
    current_user: dict = Depends(get_current_user),
) -> <Name>Item:
    """Get a single item by ID."""
    return await get_<name>_detail(<name>_id=<name>_id)
```

Key patterns from the existing code:
- Auth is via `Depends(get_current_user)` from `app.core.dependencies`
- Role-based access uses `Depends(require_role("leader", "admin"))` from the same module
- Router prefix follows `/api/v1/<plural_name>`

### Step 6. Register router in `app/main.py`

File: `backend/app/main.py`

Add the import (keep alphabetical order with existing imports):

```python
from app.modules.<name>.router import router as <name>_router
```

Add the registration (keep alphabetical order):

```python
app.include_router(<name>_router)
```

### Step 7. Add query functions in `app/db/queries/<name>.py`

File: `backend/app/db/queries/<name>.py`

```python
"""<Name> database queries using parameterized SQL."""

from asyncpg import Connection


async def get_<name>s(
    conn: Connection,
    limit: int = 20,
    offset: int = 0,
    search: str | None = None,
) -> list[dict]:
    """Get items with pagination and optional search."""
    rows = await conn.fetch(
        """
        SELECT id, <columns>
        FROM <table_name>
        WHERE ($1::text IS NULL OR <search_column> ILIKE '%' || $1 || '%')
        ORDER BY id ASC
        LIMIT $2 OFFSET $3
        """,
        search,
        limit,
        offset,
    )
    return [dict(row) for row in rows]


async def get_<name>s_count(conn: Connection, search: str | None = None) -> int:
    """Get total count with optional search filter."""
    result = await conn.fetchval(
        """
        SELECT COUNT(*)
        FROM <table_name>
        WHERE ($1::text IS NULL OR <search_column> ILIKE '%' || $1 || '%')
        """,
        search,
    )
    return result or 0


async def get_<name>_by_id(conn: Connection, <name>_id: int) -> dict | None:
    """Get a single item by ID."""
    row = await conn.fetchrow(
        """
        SELECT id, <columns>
        FROM <table_name>
        WHERE id = $1
        """,
        <name>_id,
    )
    return dict(row) if row else None
```

Key patterns from the existing code:
- Use `asyncpg.Connection` as the connection type
- Return `list[dict]` or `dict | None`
- Use positional parameters (`$1`, `$2`, etc.)
- For LIKE searches, use `escape_like()` from `app.db.queries.utils`

---

## Recipe 2: Add a New Frontend Page

### Step 1. Create page component

File: `frontend/src/pages/<Name>Page.tsx`

```tsx
import { useTranslation } from 'react-i18next';

export function <Name>Page() {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">{t('<name>.title')}</h2>
      {/* Page content */}
    </div>
  );
}
```

### Step 2. Add route in `src/App.tsx`

File: `frontend/src/App.tsx`

Add the import at the top:

```tsx
import { <Name>Page } from './pages/<Name>Page';
```

Add the route inside the `<Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>` block:

```tsx
{/* For a standard protected route: */}
<Route path="/<name>" element={<<Name>Page />} />

{/* For a role-restricted route: */}
<Route
  path="/<name>"
  element={
    <RoleProtectedRoute allowedRoles={['leader', 'admin']}>
      <<Name>Page />
    </RoleProtectedRoute>
  }
/>
```

### Step 3. Add navigation item in Sidebar

File: `frontend/src/components/layout/Sidebar.tsx`

Add the icon import from `lucide-react`:

```tsx
import { <IconName> } from 'lucide-react';
```

Add the nav item to the `navItems` array:

```tsx
const navItems = [
  // ... existing items ...
  {
    title: t('header.<name>'),
    href: '/<name>',
    icon: <IconName>,
  },
];
```

For role-gated items, use the conditional spread pattern already in use:

```tsx
...(canAccessRules ? [{
  title: t('header.<name>'),
  href: '/<name>',
  icon: <IconName>,
}] : []),
```

### Step 4. Create feature components

Directory: `frontend/src/components/<name>/`

Create components specific to the feature here.

### Step 5. Create hooks

File: `frontend/src/hooks/use<Name>.ts`

See Recipe 6 for the hook pattern.

### Step 6. Add translations

File: `frontend/src/locales/id.json`

Add keys under the appropriate section:

```json
{
  "header": {
    "<name>": "Display Name"
  },
  "<name>": {
    "title": "Page Title"
  }
}
```

---

## Recipe 3: Add a New Calculator

### Step 1. Create calculator pure function

File: `backend/app/calculators/<name>.py`

```python
"""<Name> Calculator -- pure function, no I/O.

Spec: logic/calculator-<n>-<name>.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class <Name>Result:
    """Structured result from the <name> calculator."""

    output_text: str
    details: dict[str, Any] = field(default_factory=dict)


def calculate_<name>(input_data: list[dict]) -> <Name>Result:
    """Execute the <Name> Calculator.

    Pure function -- no I/O, no database access.

    Args:
        input_data: Parsed rows from the upload file.

    Returns:
        <Name>Result with output_text and details.
    """
    if not input_data:
        return <Name>Result(output_text="No data", details={})

    # ... calculation logic ...

    return <Name>Result(output_text="...", details={...})
```

### Step 2. Register in `app/calculators/engine.py`

File: `backend/app/calculators/engine.py`

Add to `CALCULATOR_REQUIRED_FILES`:

```python
CALCULATOR_REQUIRED_FILES: dict[str, list[str]] = {
    # ... existing ...
    "<name>": ["<required_file_type_1>", "<required_file_type_2>"],
}
```

Add to `CALCULATOR_REQUIRED_MANUAL` if the calculator needs manual inputs:

```python
CALCULATOR_REQUIRED_MANUAL: dict[str, list[str]] = {
    # ... existing ...
    "<name>": ["<required_manual_field>"],
}
```

Add to `FILE_TO_CALCULATORS` for each file type:

```python
FILE_TO_CALCULATORS: dict[str, list[str]] = {
    # ... existing entries — append to existing lists or add new keys ...
    "<file_type>": ["<name>"],
}
```

Add runner import and registration:

```python
from app.modules.evaluations.calculator_service import run_<name>_calculator

_CALCULATOR_RUNNERS = {
    # ... existing ...
    "<name>": run_<name>_calculator,
}
```

### Step 3. Add runner in `app/modules/evaluations/calculator_service.py`

File: `backend/app/modules/evaluations/calculator_service.py`

Add the import and create an `async def run_<name>_calculator(brand_id: int) -> CalculatorResultResponse` function following the pattern of existing runners (e.g., `run_discount_calculator`). The runner:
1. Loads data from DB via `db.connection()`
2. Calls the pure calculator function
3. Stores the result via `calc_queries`
4. Returns a `CalculatorResultResponse`

### Step 4. Add frontend results component

File: `frontend/src/components/evaluation/calculators/<Name>Results.tsx`

```tsx
import type { CalculatorResult } from '../../../hooks/useCalculator';

interface <Name>ResultsProps {
  result: CalculatorResult;
}

export function <Name>Results({ result }: <Name>ResultsProps) {
  const details = result.details as <Name>Details;  // define this type in useCalculator.ts

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold"><Name> Calculator</h4>
        <time className="text-xs text-muted-foreground">
          {new Date(result.calculated_at).toLocaleString('id-ID')}
        </time>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Label</span>
          <span className="font-medium">{details.some_field}</span>
        </div>
      </div>
    </div>
  );
}
```

### Step 5. Register in `CalculatorResultsSection.tsx`

File: `frontend/src/components/evaluation/calculators/CalculatorResultsSection.tsx`

Add the import:

```tsx
import { <Name>Results } from './<Name>Results';
```

Add to `CALCULATOR_LABELS`:

```tsx
const CALCULATOR_LABELS: Record<string, string> = {
  // ... existing ...
  '<name>': 'calculator.label.<name>',
};
```

Add to `CALCULATOR_ORDER`:

```tsx
const CALCULATOR_ORDER = ['ads_keyword', 'top_sku', 'discount', '<name>'] as const;
```

Add case to `ResultRenderer`:

```tsx
case '<name>':
  return <<Name>Results result={result} />;
```

Update the barrel export in `frontend/src/components/evaluation/calculators/index.ts`:

```tsx
export { <Name>Results } from './<Name>Results';
```

---

## Recipe 4: Add a New Evaluation Form Section

### Step 1. Create form component

File: `frontend/src/components/evaluation/forms/<Name>Form.tsx`

Follow the existing pattern (e.g., `AdsForm.tsx`, `CampaignForm.tsx`). The form receives its data slice and callbacks:

```tsx
interface <Name>FormProps {
  data: <Name>Data;
  onChange: (category: string, key: string, value: number | string | null) => void;
  onBlur: () => void;
}

export function <Name>Form({ data, onChange, onBlur }: <Name>FormProps) {
  // Render form fields using the field definitions
}
```

### Step 2. Add field definitions to `formConfig.ts`

File: `frontend/src/components/evaluation/forms/formConfig.ts`

Add the TypeScript interface for the data shape:

```tsx
export interface <Name>Data {
  fieldA: number | null;
  fieldB: string | null;
}
```

Add it to the `ManualData` interface:

```tsx
export interface ManualData {
  // ... existing ...
  <name>: <Name>Data;
}
```

Add field definitions:

```tsx
export const <NAME>_FIELDS: FieldDefinition[] = [
  { key: 'fieldA', label: 'Label A', inputType: 'number', unit: '%' },
  { key: 'fieldB', label: 'Label B', inputType: 'text' },
];
```

Add to `MANUAL_DATA_FIELDS` array:

```tsx
export const MANUAL_DATA_FIELDS: CategoryDefinition[] = [
  // ... existing ...
  { key: '<name>', displayName: 'Display Name', fields: <NAME>_FIELDS },
];
```

Add defaults to `EMPTY_MANUAL_DATA`:

```tsx
export const EMPTY_MANUAL_DATA: ManualData = {
  // ... existing ...
  <name>: {
    fieldA: null,
    fieldB: null,
  },
};
```

### Step 3. Add section to `EvaluationSections.tsx`

File: `frontend/src/components/evaluation/EvaluationSections.tsx`

Import the form:

```tsx
import { <Name>Form } from './forms/<Name>Form';
```

Add within the appropriate `<section>` block:

```tsx
<<Name>Form
  data={manualData.<name>}
  onChange={onFieldChange}
  onBlur={onFieldBlur}
/>
```

### Step 4. Add section nav item in `SectionNav.tsx`

File: `frontend/src/components/evaluation/SectionNav.tsx`

If adding a new top-level section (not appending to an existing one), add to the `SECTIONS` array:

```tsx
const SECTIONS: Array<{ id: string; label: string; icon: ReactNode }> = [
  // ... existing ...
  { id: 'section-N', label: 'Your Section Label', icon: <IconName className="size-4" aria-hidden="true" /> },
];
```

### Step 5. Add translations

File: `frontend/src/locales/id.json`

Add translation keys for all labels and section headers.

---

## Recipe 5: Add a Database Migration

### Step 1. Generate migration

```bash
cd /Users/mac/HT/Project/aha_sicu/backend
uv run alembic revision --autogenerate -m "description of change"
```

### Step 2. Edit the generated migration file

File: `backend/app/db/migrations/versions/<NNN>_<description>.py`

Follow the existing pattern:

```python
"""Description of the migration

Revision ID: <NNN>
Revises: <previous>
Create Date: <date>
"""

import sqlalchemy as sa
from alembic import op

revision = "<NNN>"
down_revision = "<previous>"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "<table_name>",
        sa.Column("<column_name>", sa.String(50), server_default="", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("<table_name>", "<column_name>")
```

Conventions observed in existing migrations:
- Revision IDs are zero-padded three-digit strings: `"001"`, `"022"`, etc.
- Both `upgrade()` and `downgrade()` must be implemented
- Use `sa.Column` types from SQLAlchemy

### Step 3. Run the migration

```bash
cd /Users/mac/HT/Project/aha_sicu/backend
uv run alembic upgrade head
```

### Step 4. Add query functions if needed

See Recipe 1, Step 7 for the query file pattern.

---

## Recipe 6: Add a New React Query Hook

### Step 1. Create the hook file

File: `frontend/src/hooks/use<Name>.ts`

### For read queries (GET):

```tsx
import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface <Name>Response {
  items: <Name>Item[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface <Name>Item {
  id: number;
  // ... fields matching backend schema ...
}

export function use<Name>(page = 1, limit = 20, search = '') {
  return useQuery<<Name>Response>({
    queryKey: ['<name>', page, limit, search],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/<name>s', {
        params: {
          query: { page, limit, ...(search ? { search } : {}) },
        },
      });
      if (error) throw new Error('Failed to fetch <name>s');
      return data as <Name>Response;
    },
  });
}
```

Key patterns:
- `queryKey` is an array with the resource name and all parameters that affect the result
- API client is imported from `../services/apiClient`
- Uses `client.GET` / `client.POST` / `client.PUT` / `client.DELETE` (openapi-fetch style)
- Error handling: check `error` on the response, throw if present

### For write mutations (POST/PUT/DELETE):

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';

export function useCreate<Name>() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: Create<Name>Request) => {
      const { data, error } = await client.POST('/api/v1/<name>s', {
        body: payload,
      });
      if (error) throw new Error('Failed to create <name>');
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['<name>'] });
    },
  });
}
```

---

## Recipe 7: Add a New UI Component (shadcn pattern)

### Step 1. Check if shadcn already provides the component

Check `frontend/src/components/ui/` for existing components. Many are already available (button, card, dialog, label, badge, radio-group, etc.).

### Step 2. Create the component

File: `frontend/src/components/ui/<name>.tsx`

Follow the existing pattern from `button.tsx`:

```tsx
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "radix-ui"

import { cn } from "@/lib/utils"

const <name>Variants = cva(
  "base-classes-here",
  {
    variants: {
      variant: {
        default: "default-variant-classes",
        secondary: "secondary-variant-classes",
      },
      size: {
        default: "default-size-classes",
        sm: "small-size-classes",
        lg: "large-size-classes",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function <Name>({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"div"> &
  VariantProps<typeof <name>Variants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot.Root : "div"

  return (
    <Comp
      data-slot="<name>"
      className={cn(<name>Variants({ variant, size, className }))}
      {...props}
    />
  )
}

export { <Name>, <name>Variants }
```

Key patterns:
- Import `cn` from `@/lib/utils` for class merging
- Use `class-variance-authority` (`cva`) for variant definitions
- Use `Slot` from `radix-ui` for the `asChild` pattern
- Use `data-slot` attribute for component identification
- Export both the component and its variants
