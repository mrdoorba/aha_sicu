# Roadmap: aha_sicu

## Overview
Fullstack web app enabling business development teams to evaluate store/lead viability through calculators and present findings via dashboards.

## Current Milestone
**v0.2 AEGIS Security Remediation** (v0.2.0)
Status: Complete
Phases: 7 of 7 complete

Based on AEGIS diagnostic audit (2026-03-19): 136 findings (4 critical, 20 high, 45 medium, 30 low). Remediation organized by priority and blast radius.

## Phases

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 1 | Critical Security & Config | 1 | Complete | 2026-03-19 |
| 2 | Infrastructure Isolation | 1 | Complete | 2026-03-19 |
| 3 | Defensive Hardening | 1 | Complete | 2026-03-19 |
| 4 | Observability & Audit | 2 | Complete | 2026-03-19 |
| 5 | Testing Infrastructure | 1 | Complete | 2026-03-19 |
| 6 | Data & API Integrity | 3 | Complete | 2026-03-19 |
| 7 | Remaining Hardening | 1 | Complete | 2026-03-19 |

## Phase Details

### Phase 1 — Critical Security & Config
**Goal:** Fix the 4 CRITICAL findings and highest-impact HIGH findings with minimal code changes.
**Findings:** F-04-001, F-04-002, F-00-001, F-00-002, F-00-003, F-07-001, F-04-005, F-01-005, F-00-006, F-10-004
**Key changes:** OIDC activation (Terraform + Python fail-closed), real health check, deploy verification fix, GCS hardening, environment-driven CORS.

### Phase 2 — Infrastructure Isolation
**Goal:** Eliminate shared credentials and single-point-of-failure infrastructure state.
**Findings:** F-12-002, F-01-006, F-07-006, F-05-011, F-01-002, F-07-007, F-00-008
**Key changes:** Terraform state migration to GCS, per-environment DB credentials. Requires manual infrastructure steps (checkpoints).

### Phase 3 — Defensive Hardening
**Goal:** Container security, SQL defense-in-depth, error handling, email validation.
**Findings:** F-04-006, F-10-001, F-02-001, F-04-009, F-07-005, F-05-008, F-DA-015, F-03-001
**Key changes:** Non-root Dockerfile, SQL sort allowlist, catch-all exception handler, email domain validation, ScoringRequest fix.

### Phase 4 — Observability & Audit
**Goal:** Enable post-deploy validation and incident investigation.
**Findings:** F-10-002, F-05-002, F-10-003, F-05-001, F-05-003, F-07-010
**Key changes:** Structured JSON logging, request correlation IDs, admin audit log table, PostgreSQL logging flags.

### Phase 5 — Testing Infrastructure
**Goal:** Fill test coverage gaps and strengthen CI.
**Findings:** F-06-001, F-06-002, F-06-004, F-06-005, F-06-006, F-10-008, F-00-007
**Key changes:** pytest-cov with fail_under, email integration tests, CI PostgreSQL service, shared test conftest.

### Phase 6 — Data & API Integrity
**Goal:** Fix data pipeline fragility and eliminate manual type maintenance.
**Findings:** F-02-006, F-08-002, F-08-001, F-00-005, F-11-002, F-09-004, F-10-009
**Key changes:** Sync transactional atomicity, batch upserts, stateful upload to DB, auto-generated API types, deploy rollback.

### Phase 7 — Remaining Hardening
**Goal:** Address 3 remaining AEGIS planning-level playbooks missed in earlier phases.
**Playbooks:** PB-04-008, PB-04-004, PB-03-001
**Key changes:** WIF branch restriction on Workload Identity, Cloud SQL authorized_networks lockdown, evaluation response schema Literal types.

---
*Roadmap created: 2026-03-19*
*Updated: 2026-03-19 — v0.2 milestone complete, all 7 phases done*
