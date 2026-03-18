# M005: Evaluation Detail Page Content i18n

**Vision:** All scoring content on the evaluation history detail page renders in the user's selected language, bringing the detail page to full i18n parity with the dashboard.

## Success Criteria

- All calculator output sections (ads keyword, discount, top SKU) on the evaluation detail page render through the i18n system in the active UI language
- The email output section renders translated scoring messages (section headers, per-row messages, conclusion, marketing budget, closing message) in the active language
- Pre-i18n evaluations (saved before M002) display raw Indonesian text without errors
- All existing frontend tests pass (612+)

## Key Risks / Unknowns

- Discount section i18n data lives on `value_i18n` of row 73 in `score_breakdown`, not on `details` like ads keyword — different rendering path needed
- Pre-i18n evaluations may have incomplete `details` in `calculator_results` — fallback must be robust

## Proof Strategy

- Discount i18n data path → retire in S01 by proving the discount section renders translated text from score_breakdown row 73's value_i18n
- Pre-i18n backward compat → retire in S01 by proving evaluations without i18n data fall back to raw text

## Verification Classes

- Contract verification: frontend tests, `tsc -b --noEmit` type check
- Integration verification: visual verification in browser with language toggle
- Operational verification: none
- UAT / human verification: toggle language on detail page with real evaluation data

## Milestone Definition of Done

This milestone is complete only when all are true:

- All calculator output sections render through i18n on the detail page
- Email output section reconstructs translated content via buildI18nEmailBody
- Pre-i18n evaluations display gracefully with raw text fallback
- All frontend tests pass (612+)
- `tsc -b --noEmit` passes

## Requirement Coverage

- Covers: R034, R035, R036, R037, R038
- Partially covers: none
- Leaves for later: none
- Orphan risks: none

## Slices

- [ ] **S01: Calculator sections i18n rendering** `risk:medium` `depends:[]`
  > After this: Ads keyword, discount, and top SKU output on the evaluation detail page render in the active UI language; pre-i18n evaluations fall back to raw text. Proven by switching language and observing translated calculator output.

- [ ] **S02: Email output i18n rendering** `risk:low` `depends:[S01]`
  > After this: Email output card on the evaluation detail page reconstructs scoring messages in the active language using buildI18nEmailBody. All 612+ frontend tests pass. Proven by switching language and observing translated email output content.

## Boundary Map

### S01 → S02

Produces:
- Updated `AdsKeywordSection` component that renders from structured i18n details with output_text fallback
- Updated `DiscountSection` component that renders from score_breakdown i18n data with output_text fallback
- Established pattern for accessing score_breakdown rows from calculator_results context on the detail page
- `isAdsKeywordDetails` type guard reuse from calculatorGuards.ts

Consumes:
- nothing (first slice)

### S02 consumes from S01:

Consumes from S01:
- Pattern for i18n rendering on the detail page (fallback strategy, hasI18nData guard)
- Any shared type imports or utility reuse established in S01
