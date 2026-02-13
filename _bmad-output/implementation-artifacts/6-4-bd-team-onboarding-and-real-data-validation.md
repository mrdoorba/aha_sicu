# Story 6.4: BD Team Onboarding & Real-Data Validation

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team member**,
I want **to evaluate 1–2 real brands using the production app with guided support**,
so that **we validate calculator accuracy with actual client data and confirm the system is ready for wider rollout**.

## Acceptance Criteria

1. **AC1: BD team accounts provisioned and accessible** — All BD team users (1 leader + 3 members + 1 system owner = 5 accounts) have Firebase Auth accounts created in the production project. Each user can log in to the production frontend at `https://aha-sicu-prod.web.app`, reach the brands page, and see their email in the header. The team leader's account has `leader` role in the `users` table, the system owner has `admin` role, and members have `member` role.

2. **AC2: Onboarding guide document created** — A comprehensive `docs/onboarding-guide.md` exists covering: (a) how to log in, (b) full evaluation workflow walkthrough (brand selection → file upload → manual data entry → calculator review → final scoring → save), (c) file format requirements for each of the 4 upload slots (CPC Ad Report CSV, Keyword Report CSV, Order Export XLSX, Mass Update XLSX) with column expectations, (d) manual data field reference organized by scoring category, (e) how to interpret calculator results and final score/verdict, (f) FAQ and troubleshooting for common issues (upload failures, sync errors, scoring questions).

3. **AC3: Real brand evaluation completed end-to-end** — At least 1 real brand is evaluated using actual Shopee export data in the production environment. The evaluation includes: all 4 file types uploaded and processed successfully, manual data entered for all required scoring categories, all 3 calculators executed with results displayed (Ads Keyword text output, Discount Check 5 values, Top SKU tables + average stock), final score generated with verdict (Fashion or Non-Fashion template), and evaluation saved to history.

4. **AC4: Calculator output validated against manual calculations** — For each real brand evaluated, a validation report (`docs/validation-report-{brand}.md`) documents the comparison between system calculator output and the team's existing Google Sheets manual calculations. The report covers: (a) Ads Keyword Calculator — AK2 ad overview numbers match, AK4 flags match, top/bottom keyword lists match; (b) Discount Check — % Diskon TOP SKU matches within ±0.5%, range matches, voucher/paket percentages match, fake discount flag agrees; (c) Top SKU — top 20% product list matches (same products, same order by revenue), average stock matches within ±2; (d) Final Scoring — per-category scores match, total score matches within ±1 point, verdict agrees. Any discrepancy is documented with root cause analysis.

5. **AC5: Discrepancy tracking and go/no-go documented** — A `docs/launch-readiness.md` document exists containing: (a) summary of all discrepancies found during validation (if any), (b) severity classification for each (critical = blocks launch, minor = acceptable variance, cosmetic = display-only), (c) GitHub issue links for any critical bugs requiring fix, (d) go/no-go recommendation for wider rollout with explicit criteria: zero critical discrepancies, all calculator outputs within tolerance, all 5 users can log in and complete workflow.

## Tasks / Subtasks

- [x] Task 1: Create account provisioning script and guide (AC: #1)
  - [x] 1.1 Create `scripts/provision-users.py` — Python script using Firebase Admin SDK to create user accounts from a YAML/JSON config file, with email, password, and display name
  - [x] 1.2 Create `scripts/assign-roles.sql` — SQL script to insert/update user roles in the `users` table (leader, admin, member) matching provisioned Firebase UIDs
  - [x] 1.3 Create `scripts/users-config.example.yaml` — Example config file with placeholder accounts (DO NOT commit real credentials — add `scripts/users-config.yaml` to `.gitignore`)
  - [x] 1.4 Document provisioning process in script headers: (1) fill in users-config.yaml, (2) run provision-users.py, (3) run assign-roles.sql against production DB
  - [x] 1.5 Add `scripts/users-config.yaml` to `.gitignore`

- [x] Task 2: Create comprehensive onboarding guide (AC: #2)
  - [x] 2.1 Create `docs/onboarding-guide.md`
  - [x] 2.2 Write Section 1 — Getting Started: production URL, how to log in with Firebase Auth, first-time login experience, password reset flow
  - [x] 2.3 Write Section 2 — Brand Data & Sync: navigating to brands page, understanding sync status, triggering manual sync, searching for a brand
  - [x] 2.4 Write Section 3 — Starting an Evaluation: selecting a brand, understanding the evaluation page layout (file upload slots, manual input sections, calculator results, final score)
  - [x] 2.5 Write Section 4 — File Upload Guide: detailed format requirements for each of the 4 file types with column expectations:
    - CPC Ad Report CSV: Nama Produk, Nama Iklan, Tipe Iklan, Penempatan, Tipe Biaya, Biaya
    - Keyword Report CSV: Kata Kunci Pencarian, Klik, Kunjungan, Pesanan, Pendapatan, Biaya Iklan, ROAS
    - Order Export XLSX: No. Pesanan, Nama Produk, Nama Variasi, Harga Awal, Harga Setelah Diskon, Jumlah, etc.
    - Mass Update XLSX: Kode Variasi, Nama Produk, Nama Variasi, SKU, Stok (headers at row 3)
  - [x] 2.6 Write Section 5 — Manual Data Entry: field reference table organized by scoring category (Operational, Business, Content, Visitors, Promo Tools, Products/Status, Ads, Campaign, Competition, Stock, Discount), input types, benchmark values, percentage convention (0.5 = 0.5%)
  - [x] 2.7 Write Section 6 — Understanding Results: how to read Ads Keyword text output (AK2 overview, AK3 breakdown, AK4 flags, top/bottom keywords), Discount Check values (5 outputs + flag), Top SKU tables (revenue + stock), average stock
  - [x] 2.8 Write Section 7 — Final Scoring & Verdict: how Fashion vs Non-Fashion templates differ, per-category score breakdown, verdict meanings (checkmark/X/circle), email and WhatsApp output generation
  - [x] 2.9 Write Section 8 — Saving & History: saving evaluation, viewing history, searching by brand/date/category, evaluation detail view
  - [x] 2.10 Write Section 9 — FAQ & Troubleshooting: common issues (upload format errors, sync failures, "stale" scoring, login problems) with resolutions

- [ ] Task 3: Create calculator validation checklist template (AC: #4)
  - [ ] 3.1 Create `docs/validation-report-template.md` — reusable template for per-brand validation
  - [ ] 3.2 Include Ads Keyword validation section: fields to compare (AK2 product count, AK3 type breakdown, AK4 seven flags, top/bottom keyword lists, ROAS median flag)
  - [ ] 3.3 Include Discount Check validation section: fields to compare (% Diskon TOP SKU, Range, Voucher %, Paket Diskon %, fake discount flag) with tolerance ±0.5%
  - [ ] 3.4 Include Top SKU validation section: fields to compare (top product list matches, revenue ranking order, average stock) with tolerance ±2 for stock
  - [ ] 3.5 Include Final Scoring validation section: per-category scores, total score (tolerance ±1), verdict agreement, email output sanity check
  - [ ] 3.6 Include discrepancy log table (field, expected, actual, delta, severity, root cause)

- [ ] Task 4: Create launch readiness document template (AC: #5)
  - [ ] 4.1 Create `docs/launch-readiness.md` with sections: Executive Summary, Validation Summary, Discrepancy Log, Go/No-Go Criteria, Recommendation, Sign-off
  - [ ] 4.2 Define go/no-go criteria explicitly: zero critical discrepancies, all calculator outputs within tolerance, all 5 users can log in, full workflow completes E2E, no data loss on save
  - [ ] 4.3 Include bug/fix fast-track process: create GitHub issue with `bug/critical` label → feature branch → fix → deploy → re-validate
  - [ ] 4.4 Include rollout plan section: phased rollout (pilot with 1 user → expand to team) or big-bang (all users at once)

- [ ] Task 5: Execute real brand evaluation (AC: #3, #4) — REQUIRES HUMAN COLLABORATION
  - [ ] 5.1 Coordinate with BD team to select 1–2 real brands for validation
  - [ ] 5.2 Collect real Shopee export files from BD team (CPC Ad Report, Keyword Report, Order Export, Mass Update)
  - [ ] 5.3 Collect BD team's existing manual Google Sheets calculations for the same brand(s) as ground truth
  - [ ] 5.4 Execute full evaluation workflow in production (login → brand select → upload 4 files → enter manual data → review calculators → generate score → save)
  - [ ] 5.5 Fill in validation report using `docs/validation-report-template.md` for each brand evaluated
  - [ ] 5.6 If discrepancies found: document root cause, create GitHub issues for critical bugs, apply fixes and re-validate

- [ ] Task 6: Finalize launch readiness and sign-off (AC: #5) — REQUIRES HUMAN COLLABORATION
  - [ ] 6.1 Complete `docs/launch-readiness.md` with actual validation findings
  - [ ] 6.2 Verify all 5 user accounts can log in successfully
  - [ ] 6.3 Confirm go/no-go criteria are met (or document blockers)
  - [ ] 6.4 Get sign-off from BD team leader on validation results

## Dev Notes

### Technical Requirements & Constraints

- **Primarily a documentation + operational story** — The majority of this story produces markdown documents and helper scripts, not application code. The dev agent should NOT modify any backend or frontend application code unless a bug is discovered during validation (Task 5).
- **Firebase Admin SDK for provisioning** — The `provision-users.py` script uses `firebase-admin` Python SDK to create user accounts. This requires the Firebase Admin SDK credentials (same `FIREBASE_ADMIN_CREDENTIALS` or service account JSON used by the backend). The script runs locally, NOT in production.
- **Production database access for role assignment** — The `assign-roles.sql` script needs to run against the production Neon PostgreSQL database. Use the production `DATABASE_URL` from Secret Manager (`aha_sicu_prod_db_url`). The backend auto-creates user records on first login (Story 1.2), so the SQL script should UPDATE existing records after users have logged in once, not INSERT.
- **Credential security** — `scripts/users-config.yaml` containing real user emails and passwords MUST NEVER be committed. Add to `.gitignore` immediately. The example file (`users-config.example.yaml`) uses placeholder values only.
- **No application code changes** — This story creates ONLY new files (scripts, docs). Zero modifications to existing `backend/`, `frontend/`, or `infrastructure/` code. If bugs are found during validation, they get separate GitHub issues and feature branches — not mixed into this story's branch.
- **Onboarding guide language** — Write in **English** (document_output_language) but include Indonesian field names exactly as they appear in the app (e.g., "Pesanan Tidak Terselesaikan", "Harga Awal") since the BD team works with Shopee Indonesia data.
- **Calculator validation tolerances** — Floating-point arithmetic and rounding differences between Polars (Python) and Google Sheets (Excel) are expected. Defined tolerances: Discount percentages ±0.5%, stock averages ±2 units, final score ±1 point. Exact string matches for flags and verdicts.
- **Percentage convention** — Confirm the onboarding guide and validation templates use the project convention: `0.5` = 0.5% (NOT 0.005 = 0.5%). This was a known gap from Epic 3 retrospective.
- **Existing manual checklist reuse** — `smoke-tests/MANUAL_CHECKLIST.md` from Story 6.3 covers the same workflow steps. The onboarding guide should reference it but provide MORE detail (field-by-field guidance vs. checkbox verification). Do NOT duplicate — link to the checklist for quick reference.

### Architecture Compliance

**This story is purely additive** — creates new files only, no modifications to existing application code:

| Aspect | Compliance |
|--------|------------|
| Backend code | No changes — provisioning script is standalone |
| Frontend code | No changes — guide documents existing UI |
| CI workflows | No changes — scripts run locally |
| Infrastructure | No changes — accounts created via Firebase Console/SDK |
| Database | Role UPDATE only (after user auto-creation on first login) |

**Account provisioning follows existing patterns:**

| Pattern | How This Story Follows It |
|---------|--------------------------|
| Firebase Auth for all access (FR36-FR37) | Users created via Firebase Admin SDK, same auth flow |
| Role-based authorization (Architecture) | Roles set in `users` table: `member`, `leader`, `admin` |
| User auto-creation on first login (Story 1.2) | Script creates Firebase accounts, SQL updates roles AFTER first login |
| Secret Manager for credentials (Architecture) | Provisioning script reads Firebase Admin credentials from local env or Secret Manager |

**Calculator validation against authoritative specs:**

| Calculator | Authoritative Spec | Key Validation Points |
|------------|--------------------|-----------------------|
| Ads Keyword | `logic/calculator-1-kata-kunci-iklan-shopee.md` | AK2 overview count, AK3 type breakdown, AK4 seven flags, top/bottom keyword lists |
| Discount Check | `logic/calculator-3-discount-checkup.md` | % Diskon TOP SKU, Range, Voucher %, Paket Diskon %, fake discount flag |
| Top SKU | `logic/calculator-2-penjualan.md` | Top 20% products by revenue, Kode Variasi lookup, average stock |
| Final Scoring | `logic/scoring-system-template-sicu.md` | Per-category scores (11 categories), total score, verdict (F75), Fashion vs Non-Fashion thresholds |

### Library & Framework Requirements

| Package | Version | Purpose | Install Location |
|---------|---------|---------|-----------------|
| `firebase-admin` | `^6.6` | Create Firebase Auth user accounts programmatically | `scripts/` (standalone, use `uv run` or `pip install`) |

**No new dependencies in `backend/` or `frontend/`** — the provisioning script is standalone and runs locally. It can use the backend's existing `firebase-admin` dependency if run from within the backend virtualenv, or install independently.

**Why `firebase-admin` for provisioning:**
- Firebase Console can create users manually, but scripting ensures reproducibility and documents the exact accounts created
- The backend already uses `firebase-admin` for JWT token verification (`backend/app/core/security.py`), so the team is familiar with it
- Script can be re-run for additional environments or if accounts need recreation

**Alternative: Manual Firebase Console** — If the dev agent cannot obtain Firebase Admin credentials locally, all 5 accounts can be created manually via the Firebase Console (Authentication → Add User). The script is a convenience, not a hard requirement. Document both approaches in the provisioning guide.

### File Structure Requirements

**Files to CREATE:**
```
scripts/
├── provision-users.py          # Firebase Admin SDK: create user accounts
├── assign-roles.sql            # SQL: update user roles in users table
└── users-config.example.yaml   # Example config (placeholder values only)

docs/
├── onboarding-guide.md         # Comprehensive BD team onboarding guide
├── validation-report-template.md  # Reusable per-brand validation template
└── launch-readiness.md         # Go/no-go document with criteria and sign-off
```

**Files to MODIFY:**
```
.gitignore                      # Add scripts/users-config.yaml
```

**Files to REFERENCE (do NOT modify):**
```
smoke-tests/MANUAL_CHECKLIST.md         # Reuse as quick-reference from onboarding guide
logic/calculator-1-kata-kunci-iklan-shopee.md  # Ads Keyword spec for validation fields
logic/calculator-2-penjualan.md                # Top SKU spec for validation fields
logic/calculator-3-discount-checkup.md         # Discount Check spec for validation fields
logic/scoring-system-template-sicu.md          # Scoring system spec for validation fields
backend/app/core/security.py                   # Firebase Admin SDK usage pattern
backend/app/db/queries/users.py                # User table schema and role handling
_bmad-output/planning-artifacts/prd.md         # Target user roles and counts
_bmad-output/planning-artifacts/architecture.md # Auth flow, role-based access patterns
```

**Directory notes:**
- `scripts/` is a NEW top-level directory (same level as `backend/`, `frontend/`, `docs/`)
- `docs/` directory may already exist — if not, create it (architecture.md references `docs/` for project knowledge)
- No changes to `backend/`, `frontend/`, `infrastructure/`, or `smoke-tests/`

### Testing Requirements

**This story has NO automated test requirements** — it produces documentation and operational scripts, not application code.

**Validation approach instead of automated tests:**

| What to Verify | How | When |
|----------------|-----|------|
| Provisioning script runs without error | Manual execution against dev Firebase project first | Task 1 |
| Role assignment SQL is syntactically valid | Dry-run against dev database first | Task 1 |
| Onboarding guide accuracy | Walk through guide steps against production app | Task 2, verified in Task 5 |
| Validation report template completeness | Confirm all calculator output fields are covered against `logic/*.md` specs | Task 3 |
| Real brand evaluation succeeds | Execute full workflow in production | Task 5 |
| Calculator outputs match manual calculations | Side-by-side comparison documented in validation report | Task 5 |

**Regression check:**
- Run existing test suites BEFORE starting this story to confirm baseline:
  - Backend: `cd backend && uv run python -m pytest -v` (expect ~627+ tests pass)
  - Frontend: `cd frontend && npx vitest run --reporter=verbose` (expect ~321+ tests pass)
- If any bugs are found during validation (Task 5) and fixed, re-run full suites to confirm zero regressions

**No new test files created** — this is an operational readiness story, not a feature implementation story.

### Previous Story Intelligence

**From Story 6.3 (Production Smoke Testing) — Critical learnings:**

| Learning | Impact on This Story |
|----------|---------------------|
| `smoke-tests/MANUAL_CHECKLIST.md` covers full E2E workflow (10 steps) | Onboarding guide (Task 2) should reference this checklist, NOT duplicate it. Guide adds detail (field-by-field), checklist stays as quick-reference |
| 19 smoke tests (14 unauth, 5 auth) all pass | Confirms production infrastructure works — onboarding can proceed with confidence |
| `SMOKE_AUTH_TOKEN` obtained via Firebase Auth REST API | Same approach for provisioning script auth — document in script header |
| Cloud Run service publicly accessible (no IAM auth) | BD team browsers hit Cloud Run directly — no VPN or special network config needed |
| GCS signed URL uploads verified in smoke tests (AC5) | File upload flow confirmed working — onboarding guide can describe it confidently |
| SSE endpoint verified (AC6) | Real-time sync status works — include in onboarding guide |
| `brand_id: 1` assumption fragile for fresh envs (M5 finding) | Real data validation must use actual brand IDs from synced data, not hardcoded |
| Story 6.3 code review had 9 issues (1H, 5M, 3L) | Expect similar review scope for documentation quality |

**From Story 6.2 (CI/CD Pipeline Activation) — Relevant context:**

| Learning | Impact on This Story |
|----------|---------------------|
| Deploy workflows include health check step | Production is verified healthy on every deploy — no manual health check needed before onboarding |
| Firebase CLI deploys via WIF (no SA keys) | Deployment is automated — if bugs found in Task 5, fix → push → auto-deploy cycle is fast |
| Environment prefix `aha-sicu-{env}-*` on all resources | Provisioning script must target production Firebase project (`aha-sicu-prod` or similar) — NOT dev |
| `firebase.json` uses multi-target config | Production frontend URL is `https://aha-sicu-prod.web.app` — use this in onboarding guide |

**From Story 6.1 (Infrastructure Provisioning) — Relevant context:**

| Learning | Impact on This Story |
|----------|---------------------|
| GCS bucket `aha_sicu_{env}_uploads` with 24h auto-delete lifecycle | Real validation uploads auto-clean — no manual cleanup needed after testing |
| Secret Manager stores credentials with env prefix | Provisioning script needs `aha_sicu_prod_firebase_admin` secret for Admin SDK |
| Bootstrap ordering: secrets need values before services work | All secrets should already have values from 6.1 — verify before provisioning |

**From Lessons Learned — Directly applicable:**

| Learning | How It Applies |
|----------|----------------|
| Percentage convention: 0.5 = 0.5% (NOT 0.005) | Onboarding guide MUST explain this clearly — BD team uses spreadsheets where conventions differ |
| Indonesian number formatting: comma for thousands in output | Onboarding guide should show examples of expected output format (e.g., `IDR 26,433,781`) |
| Category name mapping: Indonesian internally, English in UI | Onboarding guide should map both — BD team thinks in Indonesian field names |
| Response schemas must match ACs field-by-field | Validation report template must check every output field, not just summary values |
| File List must include ALL changed files | Story File List below must match actual `git diff` output |

### Git Intelligence Summary

**Recent commit patterns (last 10 commits):**
```
26380af Merge feature/story-6-3-production-smoke-testing into develop
2d02b2a Fix code review findings for Story 6.3 (9 issues)
6ee70d8 Mark Story 6.3 complete — all tasks done, status → review
99c5709 Add smoke test README with setup and run instructions (Task 9)
2776785 Create manual walkthrough checklist (Task 8)
4aaec6f Implement all automated smoke test specs (Tasks 2-7)
5598fc8 Set up Playwright smoke test infrastructure (Task 1)
1a53ab5 Create story 6.3: Production Smoke Testing
93695aa Merge feature/story-6-2-cicd-pipeline-activation into develop
8f5531f Fix code review findings for Story 6.2 (11 issues)
```

**Insights:**
- All recent work is Epic 6 — this is the final story, completing the epic
- Branching pattern: `feature/story-6-4-bd-team-onboarding-and-real-data-validation` → merge to `develop`
- Story commit pattern: create story → implement → fix review findings → merge
- This story is documentation-heavy — expect fewer commits than code-heavy stories (6.2 had ~8, 6.3 had ~7)
- Expected commit cadence: (1) provisioning scripts, (2) onboarding guide, (3) validation templates, (4) launch readiness doc, (5) review fixes
- After merge to develop, Epic 6 is COMPLETE — update `epic-6` status to `done` in sprint-status.yaml

### Latest Tech Information

**Firebase Admin SDK (Python) — Account Creation:**
```python
from firebase_admin import auth, credentials, initialize_app

# Initialize with service account
cred = credentials.Certificate("path/to/service-account.json")
initialize_app(cred)

# Create user
user = auth.create_user(
    email="user@company.com",
    password="initial-password",
    display_name="User Name"
)
print(f"Created user: {user.uid}")
```

- `firebase-admin` v6.6+ supports Python 3.12+ (confirm 3.14 compatibility)
- `auth.create_user()` returns `UserRecord` with `.uid` needed for role assignment
- If user already exists, raises `auth.EmailAlreadyExistsError` — script should handle gracefully (skip or update)
- Password requirements: Firebase default minimum is 6 characters
- Users receive NO email notification on account creation — BD team leader should distribute credentials securely

**Production URLs (from Story 6.1/6.2):**
- Frontend: `https://aha-sicu-prod.web.app`
- Backend: Get via `gcloud run services describe aha-sicu-prod-api --region=asia-southeast1 --format="value(status.url)"`
- These go in the onboarding guide

**User Role Assignment (from Story 1.2 — `backend/app/db/queries/users.py`):**
- Backend auto-creates user record with `role = 'member'` on first login
- To promote to leader/admin: `UPDATE users SET role = 'leader' WHERE firebase_uid = '<uid>'`
- No API endpoint for role management exists — direct DB update required

### Project Structure Notes

- `scripts/` is a new top-level directory — standalone operational scripts, not part of backend or frontend
- `docs/` aligns with `project_knowledge: "{project-root}/docs"` from config.yaml — this is the intended location for project documentation
- All new files are documentation/scripts — no impact on build, test, or deploy pipelines
- After this story completes and merges, Epic 6 is done — the project transitions from "development" to "operational"

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 6 - Story 6.4]
- [Source: _bmad-output/planning-artifacts/prd.md#Target Users — 1 leader, 3 members, 1 system owner]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication Flow, #Role-based Authorization]
- [Source: _bmad-output/planning-artifacts/architecture.md#Firebase Auth with JWT validation middleware]
- [Source: _bmad-output/planning-artifacts/architecture.md#Secret Manager stores credentials]
- [Source: logic/calculator-1-kata-kunci-iklan-shopee.md — Ads Keyword Calculator authoritative spec]
- [Source: logic/calculator-2-penjualan.md — Top SKU Calculator authoritative spec]
- [Source: logic/calculator-3-discount-checkup.md — Discount Check Calculator authoritative spec]
- [Source: logic/scoring-system-template-sicu.md — Scoring system template authoritative spec]
- [Source: smoke-tests/MANUAL_CHECKLIST.md — 10-step manual walkthrough (reuse in onboarding)]
- [Source: backend/app/core/security.py — Firebase Admin SDK usage pattern]
- [Source: backend/app/db/queries/users.py — User table schema and auto-creation logic]
- [Source: _bmad-output/implementation-artifacts/6-3-production-smoke-testing.md — Previous story learnings]
- [Source: _bmad-output/implementation-artifacts/6-2-cicd-pipeline-activation.md — CI/CD patterns]
- [Source: _bmad-output/implementation-artifacts/6-1-infrastructure-provisioning.md — Infrastructure context]
- [Source: _bmad-output/lessons-learned.md — Percentage convention, Indonesian formatting, category mapping]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

### Completion Notes List

- Ultimate context engine analysis completed — comprehensive developer guide created

### Change Log

### File List
