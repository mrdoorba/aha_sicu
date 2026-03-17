# AHA SICU — Multi-Marketplace Evaluation System

## What This Is

Multi-marketplace brand evaluation system for AHA Commerce. Evaluates Shopee marketplace brands across operational health, business metrics, visitor analysis, promo tool usage, advertising performance, campaign participation, and competition. Supports Indonesian (IDR) and Thai (THB) marketplaces with marketplace-specific thresholds, currency formatting, and scoring rules.

## Core Value

Staff can evaluate brands accurately across marketplaces and share results in the language appropriate for each audience — UI, history, and email output all render in the selected language.

## Current State

- M001 complete: THB marketplace expansion — Thai brands evaluated with THB-appropriate thresholds, currency formatting, marketplace-scoped rules
- Frontend has 3-language support (ID/EN/TH) for UI chrome via react-i18next
- Backend scoring engine generates i18n structured data (`TranslatableText` keys + variables) alongside Indonesian strings
- Presentation dashboard renders evaluation results in active language via `renderTranslatable()`
- Backend email template system (`template.py`) already renders HTML emails in id/en/th
- **Gap:** EvaluationDetailPage (history view) renders raw Indonesian text regardless of language toggle
- **Gap:** Email send dialogs don't let user pick email language independently of UI language
- **Gap:** 6 locale keys have hardcoded "IDR" instead of `{{currency}}` variable

## Architecture / Key Patterns

### Backend
- **Scoring engine**: `app/calculators/scoring/` — generates `ScoringResult` with both raw text and `TranslatableText` i18n structs
- **Marketplace constants**: `app/core/marketplace.py` — VALID_MARKETPLACES, MARKETPLACE_CURRENCY
- **Email template**: `app/modules/email/template.py` — HTML email renderer with `STRINGS`, `CATEGORY_MAP`, `_translate()` using frontend locale files
- **Database**: PostgreSQL with JSONB for score_breakdown, calculator_results, manual_inputs

### Frontend
- **i18n**: react-i18next with flat key JSON files in `src/locales/{id,en,th}.json` (588 keys each)
- **Translation utility**: `src/utils/renderTranslatable.ts` — `renderTranslatable(fallback, i18n, t)` pattern
- **Category mapping**: `src/lib/categoryMap.ts` — maps Indonesian backend category names to i18n label keys
- **Language toggle**: `src/components/layout/LanguageToggle.tsx` — persists preference to user profile via API

## Capability Contract

See `.gsd/REQUIREMENTS.md` for the explicit capability contract, requirement status, and coverage mapping.

## Milestone Sequence

- [x] M001: THB Marketplace Expansion — Multi-marketplace currency support with THB thresholds
- [ ] M002: Evaluation Results i18n — History page and email output render in selected language

---
*Last updated: 2026-03-17 — M002 planning*
