# Adding a New Language

This checklist documents **every file** that must be modified when adding a new language to the AHA SICU evaluation system. Follow the steps in order — a developer can complete this mechanically without searching the codebase.

> **Current languages:** Indonesian (`id`), English (`en`), Thai (`th`)

---

## Prerequisites

Before starting, prepare the following:

1. **Translated frontend locale strings** — a complete translation of all UI labels, metric names, and messages. Use `frontend/src/locales/en.json` as the reference template.
2. **Translated backend email strings** — subject line, section headings, verdict labels, and all other email template text (see Step 5 below).
3. **Translated category names** — the 10 evaluation category labels used in the email body (see Step 6 below).
4. **A flag emoji** and **uppercase label** for the language toggle (e.g., `🇯🇵` and `JP`).
5. **The ISO 639-1 language code** (e.g., `ja`, `vi`, `ko`).

---

## Frontend Changes (3 files)

### 1. Create locale file

**File:** `frontend/src/locales/<code>.json` _(new file)_

Copy an existing locale file (e.g., `en.json`) and translate all values. The key structure must stay identical.

**Critical:** All `{{currency}}` interpolation variables must be preserved exactly as-is. The system injects the correct currency symbol at runtime — do **not** replace `{{currency}}` with a hardcoded currency string like `IDR` or `THB`.

```bash
# Start from the English file as a translation template
cp frontend/src/locales/en.json frontend/src/locales/<code>.json
# Then translate all values in the new file
```

### 2. Register locale in i18next config

**File:** `frontend/src/i18n.ts`

Two changes:

1. Add an **import** at the top (after the existing locale imports):

```ts
import <code> from './locales/<code>.json';
```

2. Add an **entry** in the `resources` object inside `i18n.use(initReactI18next).init({...})`:

```ts
resources: {
  id: { translation: id },
  en: { translation: en },
  th: { translation: th },
  <code>: { translation: <code> },  // ← add this line
},
```

### 3. Add language to the LANGUAGES array

**File:** `frontend/src/lib/languages.ts`

Add a new entry to the `LANGUAGES` array:

```ts
export const LANGUAGES = [
  { code: 'id' as const, flag: '🇮🇩', label: 'ID' },
  { code: 'en' as const, flag: '🇬🇧', label: 'EN' },
  { code: 'th' as const, flag: '🇹🇭', label: 'TH' },
  { code: '<code>' as const, flag: '<emoji>', label: '<CODE>' },  // ← add this line
];
```

**This automatically extends the `LanguageCode` type** — the type is derived from the array:

```ts
export type LanguageCode = (typeof LANGUAGES)[number]['code'];
// After your change, this becomes: 'id' | 'en' | 'th' | '<code>'
```

No other frontend type changes are needed. All components that use `LanguageCode` will accept the new code automatically.

---

## Backend Changes (3 files)

### 4. Update auth language validation

**File:** `backend/app/modules/auth/schemas.py` — line ~22

Add the new code to the `Literal` type on `UpdateLanguageRequest.language`:

```python
class UpdateLanguageRequest(BaseModel):
    """Request body for updating language preference."""

    language: Literal["id", "en", "th", "<code>"]  # ← add "<code>"
```

This controls which language codes the `PATCH /auth/me/language` endpoint accepts. Without this change, the API will return a **422 validation error** when a user tries to switch to the new language.

### 5. Update email language validation

**File:** `backend/app/modules/email/schemas.py` — line ~17

Add the new code to the regex pattern on `SendEmailRequest.language`:

```python
language: str = Field(default="id", pattern="^(id|en|th|<code>)$")  # ← add |<code>
```

This controls which language codes the email-sending endpoint accepts. Without this change, sending an evaluation email in the new language will return a **422 validation error**.

### 6. Add email template translations

**File:** `backend/app/modules/email/template.py`

Two dicts need a new language key:

#### 6a. `STRINGS` dict (starts at ~line 37)

Add a new top-level key with all email template strings translated. Copy the `"en"` block as a starting point:

```python
STRINGS: dict[str, dict[str, str]] = {
    "id": { ... },
    "en": { ... },
    "th": { ... },
    "<code>": {
        "score_overview": "<translated>",
        "detailed_evaluation": "<translated>",
        "score_breakdown": "<translated>",
        "data_intelligence": "<translated>",
        "ads_analysis": "<translated>",
        "top_sku": "<translated>",
        "revenue_ranking": "<translated>",
        "stock_ranking": "<translated>",
        "average_stock": "<translated>",
        "product_code": "<translated>",
        "product_name": "<translated>",
        "kesimpulan": "<translated>",
        "marketing_budget": "<translated>",
        "metric": "<translated>",
        "value": "<translated>",
        "benchmark": "<translated>",
        "verdict": "<translated>",
        "score": "<translated>",
        "message": "<translated>",
        "approved": "<translated>",
        "rejected": "<translated>",
        "check_count": "<translated>",
        "cross_count": "<translated>",
        "performance_verdict": "<translated>",
        "brand_report": "<translated>",
        "subject": "<translated>: {brand_name} - {period}",
        "plain_score": "<translated>",
        "plain_period": "<translated>",
        "chart_placeholder": "<translated>",
    },
}
```

> **Note:** The `"subject"` value must include `{brand_name}` and `{period}` placeholders — these are Python format variables, not i18next interpolation.

#### 6b. `CATEGORY_MAP` dict (starts at ~line 133)

Add a new top-level key mapping the 10 Indonesian category names to their translations:

```python
CATEGORY_MAP: dict[str, dict[str, str]] = {
    "id": { ... },
    "en": { ... },
    "th": { ... },
    "<code>": {
        "Kesehatan Operasional Toko": "<translated>",
        "Bisnis Analisis": "<translated>",
        "Tinjauan Pengunjung": "<translated>",
        "Promo Toko": "<translated>",
        "Jumlah Produk & Status Toko": "<translated>",
        "Data Iklan": "<translated>",
        "Partisipasi Campaign": "<translated>",
        "Kompetisi TOP Produk": "<translated>",
        "Stok": "<translated>",
        "Discount": "<translated>",
    },
}
```

> **Important:** The dict keys (left side) are the **original Indonesian category names** from the database — do **not** change them. Only translate the values (right side).

---

## What You Do NOT Need to Change

- **No database migrations** — language preference is stored as a plain string, no schema change needed
- **No new API endpoints** — all existing endpoints already accept a language parameter
- **No new React components** — the `LanguageToggle` reads from the `LANGUAGES` array automatically
- **No router or page changes** — i18next handles all translations via the `t()` function
- **No Docker or deployment config changes** — locale files are bundled at build time

All changes are **config-level additions** to existing arrays, dicts, and type unions.

---

## Verification

After making all changes, run these commands to confirm everything works:

### Frontend

```bash
# Run the full test suite
cd frontend && npx vitest run

# Verify locale file has no hardcoded currency symbols
grep -c "IDR" frontend/src/locales/<code>.json
# Expected: 0

grep -c "THB" frontend/src/locales/<code>.json
# Expected: 0

# Verify currency interpolation variables are present
grep -c "{{currency}}" frontend/src/locales/<code>.json
# Expected: 6 (same count as other locale files)
```

### Backend

```bash
# Run backend tests
cd backend && uv run pytest

# Quick smoke test — the language code should be accepted by Pydantic
uv run python -c "
from app.modules.auth.schemas import UpdateLanguageRequest
UpdateLanguageRequest(language='<code>')
print('✓ Auth schema accepts <code>')
"

uv run python -c "
from app.modules.email.schemas import SendEmailRequest
SendEmailRequest(evaluation_id=1, recipients=['test@example.com'], language='<code>')
print('✓ Email schema accepts <code>')
"
```

### Manual Check

1. Start the dev server and switch to the new language in the UI
2. Verify all evaluation labels, metric names, and section headers display in the new language
3. Send a test evaluation email and verify the email body renders in the new language

---

## Summary of Touch Points

| # | Layer    | File                                         | What to Add                              |
|---|----------|----------------------------------------------|------------------------------------------|
| 1 | Frontend | `frontend/src/locales/<code>.json`           | New locale file (copy + translate)       |
| 2 | Frontend | `frontend/src/i18n.ts`                       | Import + resources entry                 |
| 3 | Frontend | `frontend/src/lib/languages.ts`              | Entry in `LANGUAGES` array               |
| 4 | Backend  | `backend/app/modules/auth/schemas.py`        | Code in `Literal` union (~line 22)       |
| 5 | Backend  | `backend/app/modules/email/schemas.py`       | Code in regex pattern (~line 17)         |
| 6 | Backend  | `backend/app/modules/email/template.py`      | Keys in `STRINGS` + `CATEGORY_MAP` dicts |

**Auto-derived (no manual action):** The `LanguageCode` TypeScript type in `frontend/src/lib/languages.ts` is automatically derived from the `LANGUAGES` array — adding an entry in step 3 extends the type throughout the frontend.
