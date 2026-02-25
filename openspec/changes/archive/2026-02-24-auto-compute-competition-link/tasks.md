## 1. Helper Function

- [x] 1.1 Create `buildShopeeSearchUrl(sellingPrice: number | null, keyword: string | null): string | null` helper in `CompetitionForm.tsx` (or a shared util). Returns the full Shopee search URL when both inputs are present, `null` otherwise. URL-encodes keyword via `encodeURIComponent`, rounds `maxPrice` (×1.10) and `minPrice` (×0.75) to integers.
- [x] 1.2 Add unit tests for `buildShopeeSearchUrl` — covers: both present, sellingPrice null, keyword null, both null, keyword with spaces, keyword with special characters (&, etc.)

## 2. Form Integration

- [x] 2.1 In `CompetitionForm.tsx`, update the `sellingPrice` and `keyword` onChange handlers to also compute and emit the link value via `onChange('competition', '<productKey>.link', computedLink)` whenever either field changes.
- [x] 2.2 Replace the `<Input>` element for the LINK field with a clickable `<a href={link} target="_blank" rel="noopener noreferrer">` when the link is present, or muted placeholder text when null. Use the existing i18n label for the link field.

## 3. Testing

- [x] 3.1 Add/update component tests for `CompetitionForm` — verify that changing `sellingPrice` or `keyword` triggers an `onChange` call for the `link` field with the correct computed URL.
- [x] 3.2 Verify existing `CompetitionForm` tests still pass and update any that reference the old link input element.
