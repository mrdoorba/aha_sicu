## Why

The frontend uses `react-i18next` with `lng: 'id'` (Indonesian), but ~60+ user-facing strings across 12 component files are still hardcoded in English. This creates an inconsistent bilingual UI that looks unfinished. All user-visible text should go through the i18n system with proper Indonesian translations.

## What Changes

- Add ~60 new translation keys to `frontend/src/locales/id.json`
- Replace all hardcoded English strings in 12 component/page files with `t()` calls
- Files affected:
  - `PresentationDashboard.tsx` — loading, headings, buttons, badges, card titles/subtitles, footer
  - `BrandTable.tsx` — table headers, badges, buttons, fallback text
  - `FinalScoreDisplay.tsx` — verdict labels, "Total Score"
  - `ScorePanel.tsx` — category map labels, headings
  - `FileUploadSlot.tsx` — upload status messages, buttons
  - `ScoreBreakdown.tsx` — table headers
  - `Header.tsx` — navigation labels
  - `Sidebar.tsx` — navigation labels
  - `AdsKeywordResults.tsx` — title
  - `RulesPage.tsx` — hardcoded labels not using `t()`
  - `EvaluationDetailPage.tsx` — category labels
  - `ScoringSection.tsx` — error prefix
- Update corresponding test files to match new Indonesian text

## Capabilities

### New Capabilities
- `i18n-full-coverage`: Ensure all user-facing UI strings use the i18n translation system with Indonesian locale

### Modified Capabilities
<!-- None — no existing specs to modify -->

## Impact

- **Frontend components**: 12 TSX files modified to use `t()` instead of hardcoded strings
- **Locale file**: `id.json` expanded with ~60 new keys
- **Tests**: Test files referencing English strings need updating to match Indonesian translations
- **No API/backend changes**
- **No breaking changes** — purely cosmetic/text change
