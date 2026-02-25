## 1. Add translation keys to id.json

- [x] 1.1 Add PresentationDashboard keys (~20 keys: loading, empty state, verdict labels, card titles/subtitles, badges, buttons, footer)
- [x] 1.2 Add BrandTable keys (~8 keys: table headers, badges, buttons, fallback)
- [x] 1.3 Add FinalScoreDisplay keys (~7 keys: verdict labels, total score)
- [x] 1.4 Add ScorePanel keys (~2 keys: score summary, total score)
- [x] 1.5 Add FileUploadSlot keys (~9 keys: status messages, buttons)
- [x] 1.6 Add ScoreBreakdown keys (~3 keys: table headers)
- [x] 1.7 Add RulesPage keys (~15 keys: hardcoded English + move hardcoded Indonesian strings to i18n)
- [x] 1.8 Add ScoringSection key (~1 key: error prefix)

## 2. Update components to use t()

- [x] 2.1 Update PresentationDashboard.tsx — replace all hardcoded English strings with t() calls
- [x] 2.2 Update BrandTable.tsx — replace table headers, badges, buttons with t() calls
- [x] 2.3 Update FinalScoreDisplay.tsx — replace verdict config labels and "Total Score" with t() calls
- [x] 2.4 Update ScorePanel.tsx — replace "Score Summary" and "Total Score" with t() calls
- [x] 2.5 Update FileUploadSlot.tsx — replace status messages and button labels with t() calls
- [x] 2.6 Update ScoreBreakdown.tsx — replace table headers with t() calls
- [x] 2.7 Update RulesPage.tsx — replace all hardcoded strings (English and Indonesian) with t() calls
- [x] 2.8 Update ScoringSection.tsx — replace "Error:" prefix with t() call

## 3. Update tests

- [x] 3.1 Update test files that reference changed English strings to match new Indonesian translations
- [x] 3.2 Run full test suite and fix any remaining failures

## 4. Verify

- [x] 4.1 Run lint, typecheck, and full test suite — all must pass
- [x] 4.2 Grep for remaining hardcoded English strings to confirm full coverage
