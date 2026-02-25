## Context

The project already has a working i18n setup (`react-i18next`, locale `id`, translations in `id.json`). Many components already use `t()` correctly. The problem is incomplete coverage — ~60 strings were left hardcoded in English during initial development or feature additions.

Current `id.json` has ~320 keys. This change adds ~60 more.

## Goals / Non-Goals

**Goals:**
- 100% of user-visible strings use `t()` with Indonesian translations
- Consistent i18n key naming following existing conventions in `id.json`
- Tests updated to match new translated text

**Non-Goals:**
- Multi-language support (only Indonesian locale exists, no plans for others)
- Translating technical terms commonly used in English (e.g., Dashboard, Brand, Email, ROAS, GMV, SKU, CSV, Content, Mall, Fashion, Non-Fashion)
- Refactoring the i18n system itself
- Translating developer-facing strings (console.log, error stack traces)

## Decisions

### 1. Key naming convention
Follow existing flat dot-notation pattern in `id.json`: `<page/component>.<section>.<key>`

Examples:
- `presentation.loading` for PresentationDashboard loading text
- `brandTable.header.brandName` for BrandTable column headers
- `fileUpload.status.preparing` for FileUploadSlot status messages

### 2. Terms kept in English
These are industry/technical terms commonly used as-is in Indonesian e-commerce context:
- Dashboard, Brand, Content, Mall, Fashion, Non-Fashion
- Email, Password, Login
- ROAS, GMV, SKU, CSV, WhatsApp
- Calculator, Ads, Campaign

### 3. Hardcoded Indonesian strings in RulesPage
RulesPage has strings hardcoded in Indonesian but not going through `t()`. These should also be moved to `id.json` for consistency, even though they're already in the correct language.

### 4. Test updates
Tests that query by text content (e.g., `getByRole('button', { name: /english text/i })`) need updating to match the new Indonesian translations.

## Risks / Trade-offs

- **Risk**: Missing a hardcoded string → Mitigation: Thorough audit already done, grep for remaining English text after implementation
- **Risk**: Breaking tests → Mitigation: Update tests in same commit as component changes, run full test suite
- **Risk**: Key naming inconsistency → Mitigation: Follow existing patterns, review `id.json` holistically
