# AHA SICU — Multi-Marketplace Evaluation System

## What This Is

Multi-marketplace brand evaluation system for AHA Commerce. Evaluates Shopee marketplace brands across operational health, business metrics, visitor analysis, promo tool usage, advertising performance, campaign participation, and competition. Supports Indonesian (IDR) and Thai (THB) marketplaces with marketplace-specific thresholds, currency formatting, and scoring rules.

## Core Value

Staff can evaluate brands accurately across marketplaces and share results in the language appropriate for each audience — UI, history, and email output all render in the selected language.

## Current State

- M001 complete: THB marketplace expansion — Thai brands evaluated with THB-appropriate thresholds, currency formatting, marketplace-scoped rules
- M002 complete: Evaluation results i18n — history detail page and email output render in selected language (ID/EN/TH)
- Frontend has 3-language support (ID/EN/TH) for all evaluation content via react-i18next
- Backend scoring engine generates i18n structured data (`TranslatableText` keys + variables) alongside Indonesian strings
- All evaluation pages (dashboard, history detail) render scoring text through `renderTranslatable()` with language reactivity
- All 3 email dialogs have independent language selection; email body assembles from i18n data in chosen language
- Backend email template system (`template.py`) renders HTML emails in id/en/th; preview endpoint accepts `?language=` param
- Locale files use `{{currency}}` interpolation — zero hardcoded currency codes
- `LanguageCode` type centralized in `lib/languages.ts`; adding a new language documented in `docs/adding-a-language.md`
- 602 frontend tests pass across 66 files; 11 backend evaluation detail tests pass
- All 9 M002 requirements validated (R014-R022)

## Architecture / Key Patterns

### Backend
- **Scoring engine**: `app/calculators/scoring/` — generates `ScoringResult` with both raw text and `TranslatableText` i18n structs
- **Marketplace constants**: `app/core/marketplace.py` — VALID_MARKETPLACES, MARKETPLACE_CURRENCY
- **Email template**: `app/modules/email/template.py` — HTML email renderer with `STRINGS`, `CATEGORY_MAP`, `_translate()` using frontend locale files
- **Email preview**: `app/modules/email/router.py` — preview endpoint accepts `?language=` query param for language-specific preview
- **Database**: PostgreSQL with JSONB for score_breakdown, calculator_results, manual_inputs
- **Evaluation detail API**: `GET /api/v1/evaluations/{id}` — returns marketplace field with triple-layer fallback (SQL COALESCE → service default → Pydantic default)

### Frontend
- **i18n**: react-i18next with flat key JSON files in `src/locales/{id,en,th}.json` (~600+ keys each)
- **Translation utility**: `src/utils/renderTranslatable.ts` — `renderTranslatable(fallback, i18n, t)` pattern
- **Email body assembly**: `src/utils/buildI18nEmailBody.ts` — mirrors backend `_assemble_email_body` section ordering with SECTION_DEFS declarative config
- **Category mapping**: `src/lib/categoryMap.ts` — maps Indonesian backend category names to i18n label keys
- **Language constants**: `src/lib/languages.ts` — shared LANGUAGES array and LanguageCode type (single source of truth)
- **Language toggle**: `src/components/layout/LanguageToggle.tsx` — persists preference to user profile via API
- **Email language selector**: `src/components/shared/EmailLanguageSelector.tsx` — reusable dropdown for per-email language selection
- **Scoring conclusion**: `ScoringConclusionSection` in `EvaluationDetailPage.tsx` — renders conclusion/marketing_budget/closing_message via renderTranslatable() with isScoringSummary() guard
- **Score breakdown**: `ScoreBreakdownTable` in `EvaluationDetailPage.tsx` — translates category names via CATEGORY_MAP + t() with raw-string fallback

## Capability Contract

See `.gsd/REQUIREMENTS.md` for the explicit capability contract, requirement status, and coverage mapping.

## Milestone Sequence

- [x] M001: THB Marketplace Expansion — Multi-marketplace currency support with THB thresholds
- [x] M002: Evaluation Results i18n — History page and email output render in selected language; all 9 requirements validated

---
*Last updated: 2026-03-18 — M002 complete (all 4 slices delivered, all requirements validated)*
