# Roadmap: aha_sicu

## Overview
Fullstack web app enabling business development teams to evaluate store/lead viability through calculators and present findings via dashboards.

## Current Milestone
**v0.3 i18n Completeness**
Status: In Progress
Phases: 1 of 2 complete

Make the entire UI respect the language toggle and make adding future languages frictionless.

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 8 | Calculator Output i18n | 2 | ✅ Complete | 2026-03-20 |
| 9 | Language Addition Streamlining | TBD | Not started | - |

### Phase 8: Calculator Output i18n

Focus: Convert Ads Keyword, Discount, and Email Output from raw backend text to structured i18n data + translation keys. Refactor scoring calculator to read from `details` instead of regex-parsing `output_text`. Backward-compatible fallback for old evaluations.
Plans:
- **08-01** (wave 1): Backend — Discount i18n + G68 refactor [TDD, autonomous]
- **08-02** (wave 2): Frontend — AdsKeyword/Discount/Email i18n rendering [human-verify checkpoint]

### Phase 9: Language Addition Streamlining

Focus: Reduce the 4-file process for adding a new language to a single registration point or auto-discovery pattern.
Plans: TBD (defined during /paul:plan)

## Completed Milestones

<details>
<summary>v0.2 AEGIS Security Remediation — 2026-03-19 (7 phases)</summary>

| Phase | Name | Plans | Completed |
|-------|------|-------|-----------|
| 1 | Critical Security & Config | 1 | 2026-03-19 |
| 2 | Infrastructure Isolation | 1 | 2026-03-19 |
| 3 | Defensive Hardening | 1 | 2026-03-19 |
| 4 | Observability & Audit | 2 | 2026-03-19 |
| 5 | Testing Infrastructure | 1 | 2026-03-19 |
| 6 | Data & API Integrity | 3 | 2026-03-19 |
| 7 | Remaining Hardening | 1 | 2026-03-19 |

Full archive: `.paul/milestones/v0.2.0-ROADMAP.md`

</details>

---
*Roadmap created: 2026-03-19*
*Updated: 2026-03-20 — v0.3 i18n Completeness milestone created*
