# S04 — Locale hardcode cleanup & future-proofing — Research

**Date:** 2026-03-18
**Depth:** Light — cleanup, documentation, and verification of established patterns

## Summary

S04 is a cleanup and documentation slice. The core work (R017 — replacing hardcoded IDR with `{{currency}}` in locale files) was already completed and validated in S03. What remains is:

1. **Verification sweep** — confirm no hardcoded language assumptions remain that would break when adding a 4th language
2. **Documentation** — write a "How to add a new language" checklist documenting every file that needs a new entry
3. **Optional cleanup** — replace scattered `'id' | 'en' | 'th'` literal types with the existing `LanguageCode` type from `lib/languages.ts`

The sweep found that adding a 4th language currently requires touching **7 locations** across frontend and backend:
- Frontend: `locales/<code>.json` (new file), `i18n.ts` (import + resources entry), `lib/languages.ts` (LANGUAGES array entry)
- Frontend type annotations: `LanguageToggle.tsx` line 32, `apiClient.ts` lines 34 & 963 (manual `'id' | 'en' | 'th'` union types)
- Backend: `modules/auth/schemas.py` (`Literal["id", "en", "th"]`), `modules/email/schemas.py` (`pattern="^(id|en|th)$"`), `modules/email/template.py` (STRINGS + CATEGORY_MAP dicts)

The frontend type annotations (items 4-5) could be cleaned up by importing `LanguageCode` from `lib/languages.ts`, but `apiClient.ts` has inline path types and `LanguageToggle.tsx` has an inline union on a handler parameter — these are minor. The backend `Literal` and regex patterns are true config points that must be updated for a new language.

R020 states adding a language requires "only locale JSON + config additions — no schema changes, no migrations, no new components." The current state satisfies this. All touch points are config-level additions (new entries in arrays/dicts/unions), not structural changes.

## Recommendation

**Task 1: Documentation.** Write `docs/adding-a-language.md` with a step-by-step checklist of every file to modify when adding a 4th language. Group by frontend vs backend. Include the specific line/section to edit in each file.

**Task 2: Verification & optional type cleanup.** Run a final hardcode sweep, replace frontend `'id' | 'en' | 'th'` literals with `LanguageCode` where practical (LanguageToggle.tsx and apiClient.ts), and verify the full test suite passes. The `unit: 'IDR'` values in `fields.ts` are **not** user-visible currency labels (they're inert metadata for field type classification) — leave them as-is. The `formatIDR`/`parseIDR` deprecations in `formUtils.ts` are already done correctly.

Both tasks are independent and low-risk. Documentation first is natural since the sweep informs what the checklist contains.

## Implementation Landscape

### Key Files

- `docs/adding-a-language.md` — **new file** — the primary deliverable documenting the language addition checklist
- `frontend/src/lib/languages.ts` — defines `LANGUAGES` array and `LanguageCode` type; single source of truth for supported languages
- `frontend/src/i18n.ts` — imports locale JSONs and configures i18next resources; touch point for new language
- `frontend/src/components/layout/LanguageToggle.tsx` — line 32 has inline `'id' | 'en' | 'th'` that could use `LanguageCode`
- `frontend/src/services/apiClient.ts` — lines 34 and 963 have inline `'id' | 'en' | 'th'` union types; manually maintained (not auto-generated)
- `backend/app/modules/auth/schemas.py` — `Literal["id", "en", "th"]` on `UpdateLanguageRequest`
- `backend/app/modules/email/schemas.py` — regex `pattern="^(id|en|th)$"` on `SendEmailRequest.language`
- `backend/app/modules/email/template.py` — `STRINGS` and `CATEGORY_MAP` dicts keyed by language code
- `frontend/src/locales/{id,en,th}.json` — locale files; already clean (no hardcoded IDR)

### Things That Look Like Problems But Aren't

- `fields.ts` has `unit: 'IDR'` on ~25 field definitions — these are **not** used for currency display. The `unit` field is only consumed by `getBenchmarkFromRules` for percentage/count formatting logic. Currency display comes from the `currency` prop pipeline (`getCurrencyCode(marketplace)`). Leave as-is.
- `formatIDR`/`parseIDR` in `formUtils.ts` — already `@deprecated` with redirects to `formatCurrency`/`parseCurrency`. Leave as-is.
- `INDO_MONTHS` and `GENERIC_LABELS` in `fields.ts` — Indonesian month abbreviations for the data entry form. These are evaluation form labels, not scoring results. Out of scope for i18n scoring (they're input-side, not output-side).
- `getSellerBaseUrl` / `SECTION_LINKS` — marketplace-specific Shopee URLs, not language-related.
- `EvaluationSections.tsx` lines 156/160 — UI labels "🇮🇩 Indonesia (IDR)" and "🇹🇭 Thailand (THB)" for marketplace selector radio buttons. These are marketplace identifiers, not language labels.

### Build Order

1. **T01: Write the "adding a language" documentation** — enumerate all 7+ touch points as a checklist. This is the primary R020 deliverable. No code changes.
2. **T02: Type cleanup + verification sweep** — replace inline `'id' | 'en' | 'th'` with `LanguageCode` in `LanguageToggle.tsx` and `apiClient.ts`. Run full test suite. Confirm R017 still holds (grep locale files). This validates R020's "no new components" claim.

### Verification Approach

- `grep -c "IDR" frontend/src/locales/*.json` → all return 0 (R017 still valid)
- `grep -c "{{currency}}" frontend/src/locales/*.json` → all return 6 (R017 still valid)
- `grep -rn "'id' | 'en' | 'th'" frontend/src/ --include='*.ts' --include='*.tsx' | grep -v '.test.'` → reduced or eliminated after cleanup
- Full frontend test suite passes: `cd frontend && npx vitest run`
- `docs/adding-a-language.md` exists and covers all touch points

## Constraints

- R017 is already validated — locale file currency cleanup was done in S03. Do NOT re-modify locale files.
- `apiClient.ts` inline path types are manually maintained — the `'id' | 'en' | 'th'` in the `paths` interface at line 34 is inside a type definition that mirrors the OpenAPI schema. Changing it to use `LanguageCode` is valid since it's manually maintained, but the type must remain compatible with `openapi-fetch`'s type system.
- Backend `Literal` and regex patterns are genuine config that must be manually updated when adding a language — there's no way to derive these from a central list without over-engineering. Document them; don't try to DRY them.
