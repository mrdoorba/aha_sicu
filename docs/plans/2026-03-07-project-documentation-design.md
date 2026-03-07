# Project Documentation Design

## Goal

Create comprehensive project documentation in two sets:
1. **Engineer docs** — for human engineers to understand, onboard, and contribute
2. **Agent docs** — for AI coding agents to navigate the codebase and make correct changes

## Decisions

- **Fresh start** — no existing docs to preserve
- **Flat file structure** — `docs/engineer/` and `docs/agent/` with flat markdown files
- **Layered approach** — agent docs reference engineer docs for architecture/domain; focus on codebase-specific context
- **Stable features only** — email feature (in-progress) excluded; documented when shipped
- **Approach A (Mirrored Structure)** — engineer docs by system layer, agent docs as thin focused layer

## Engineer Documentation (`docs/engineer/`)

10 files covering the full system:

| File | Scope |
|------|-------|
| `project-overview.md` | Executive summary, domain (Shopee brand health evaluation), core workflow (sync > upload > calculate > score > report), tech stack, environments, project structure |
| `architecture-backend.md` | FastAPI module layout (`modules/`, `calculators/`, `db/queries/`, `core/`), request lifecycle, dependency injection, dual auth (Firebase + OIDC), error handling, async DB pooling |
| `architecture-frontend.md` | React SPA structure, pages/routes, component organization (feature folders + UI primitives), React Query state management, openapi-fetch API client, auth flow, i18n, form management |
| `architecture-infrastructure.md` | GCP resource inventory, Terraform modules, service accounts/roles, Workload Identity Federation, Cloud SQL setup, Secret Manager, GCS uploads, Cloud Scheduler, security model |
| `api-reference.md` | All ~40 endpoints by module (auth, brands, evaluations, calculators, scoring, upload, rules, sync, email, accounts) with method, path, auth, roles, request/response shapes |
| `data-models.md` | 9 database tables with columns/types/constraints, relationships, ER diagram, migration summary (22 migrations), key patterns (mutable inputs vs immutable snapshots) |
| `scoring-engine.md` | 10 scoring categories, fashion/non-fashion templates, dynamic rules, verdict thresholds, calculator pipeline (dependencies, readiness, auto-execution), individual calculator logic |
| `development-guide.md` | Local setup (uv, npm), env vars, running tests (pytest, vitest), linting (ruff, eslint), local upload fallback, DB migrations (alembic), useful commands |
| `deployment-guide.md` | CI/CD pipeline (3 GitHub Actions workflows), deployment flow (PR > CI > merge > auto-deploy dev > manual prod), Terraform bootstrap, secret management, smoke tests |
| `onboarding-guide.md` | BD team walkthrough: user provisioning workflow, daily usage workflow, manual verification checklist |

## Agent Documentation (`docs/agent/`)

3 files optimized for coding agents:

| File | Scope |
|------|-------|
| `CODEBASE.md` | Complete file map with one-line purpose per file/directory, key entry points (main.py, App.tsx), module boundaries, "where to find X" quick reference. References engineer docs for deeper context. |
| `CONVENTIONS.md` | Naming patterns, file organization rules, import conventions, test patterns, commit style, TypeScript/Python style guidelines. Everything needed to write code that fits the existing codebase. |
| `PATTERNS.md` | Step-by-step recipes for common changes: add API endpoint, add page/route, add calculator, add form section, add DB migration. Each recipe lists files to create/modify and the pattern to follow. |

## What's NOT Included

- Email feature documentation (in-progress, document when shipped)
- Operational runbooks (no production incidents yet to document)
- ADRs (no formal architecture decision records needed at this stage)

## Implementation

Use the writing-plans skill to create a detailed task-by-task implementation plan for writing all 13 documentation files.
