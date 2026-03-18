# AHA SICU — Multi-Marketplace Evaluation System

## What This Is

Multi-marketplace brand evaluation system for AHA Commerce. Evaluates Shopee marketplace brands across operational health, business metrics, visitor analysis, promo tool usage, advertising performance, campaign participation, and competition. Supports Indonesian (IDR) and Thai (THB) marketplaces with marketplace-specific thresholds, currency formatting, and scoring rules.

## Core Value

Staff can evaluate brands accurately across marketplaces and share results in the language appropriate for each audience — UI, history, and email output all render in the selected language.

## Current State

- M001 complete: THB marketplace expansion — Thai brands evaluated with THB-appropriate thresholds, currency formatting, marketplace-scoped rules
- M002 complete: Evaluation results i18n — history detail page and email output render in selected language (ID/EN/TH)
- M003 complete: Hardcoded IDR cleanup — follower threshold uses international comma convention (>50,000), val_str uses comma separator, ads BOTTOM min_cost is marketplace-aware (190 THB / 100,000 IDR), juta convention preserved for ID
- M004 complete: Full frontend i18n extraction — all hardcoded Indonesian extracted to locale files, 720 keys in sync across 3 languages (id/en/th), zero rendered Indonesian in source, 612/612 frontend tests pass
- Frontend has 3-language support (ID/EN/TH) for all evaluation content via react-i18next
- Backend scoring engine generates i18n structured data (`TranslatableText` keys + variables) alongside Indonesian strings
- All evaluation pages (dashboard, history detail) render scoring text through `renderTranslatable()` with language reactivity
- All 3 email dialogs have independent language selection; email body assembles from i18n data in chosen language
- Backend email template system (`template.py`) renders HTML emails in id/en/th; preview endpoint accepts `?language=` param
- Locale files use `{{currency}}` interpolation — zero hardcoded currency codes
- `LanguageCode` type centralized in `lib/languages.ts`; adding a new language documented in `docs/adding-a-language.md`
- Number formatting uses international comma convention consistently across all scoring output
- 1097 backend tests pass; 612 frontend tests pass
- All 20 tracked requirements validated (R014–R032); no active or deferred requirements remain

## Architecture / Key Patterns

### Backend
- **Scoring engine**: `app/calculators/scoring/` — generates `ScoringResult` with both raw text and `TranslatableText` i18n structs
- **Marketplace constants**: `app/core/marketplace.py` — VALID_MARKETPLACES, MARKETPLACE_CURRENCY, IDR_TO_THB_RATE
- **Email template**: `app/modules/email/template.py` — HTML email renderer with `STRINGS`, `CATEGORY_MAP`, `_translate()` using frontend locale files
- **Migration drift test**: `TestMigrationTemplatesDrift` replays migrations 012→019→020→021→027→028 to verify DB templates match DEFAULT_RULES
- **Ads calculator**: `app/calculators/ads_keyword.py` — marketplace-aware min_cost for BOTTOM ads (190 THB / 100,000 IDR)

### Frontend
- **i18n**: react-i18next with `id.json`, `en.json`, `th.json` locale files — single source of truth for all UI text
- **Locale mapping**: `lib/localeMap.ts` — `getIntlLocale()` maps i18next codes (id/en/th) to Intl locale codes (id-ID/en-US/th-TH)
- **Language toggle**: `lib/languages.ts` defines `LANGUAGES` array and `LanguageCode` type
- **renderTranslatable()**: `utils/renderTranslatable.ts` — resolves i18n keys from backend scoring data with raw-text fallback
- **Form system**: `evaluation/forms/fields.ts` defines field metadata with `labelKey` i18n keys; form components render labels via `t(field.labelKey!)`
- **Currency formatting**: `formUtils.ts` — `formatCurrency()` / `parseCurrency()` with marketplace param

## Capability Contract

See `.gsd/REQUIREMENTS.md` for the explicit capability contract, requirement status, and coverage mapping.

## Milestone Sequence

- [x] M001: THB Marketplace Expansion — Thai marketplace with THB thresholds, currency, and scoring rules
- [x] M002: Evaluation Results i18n — History detail and email output render in selected language
- [x] M003: Hardcoded IDR Cleanup — International number convention, marketplace-aware ads thresholds
- [x] M004: Frontend i18n Completion — Extract all remaining hardcoded Indonesian from source into locale files
