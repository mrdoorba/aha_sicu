## Why

The competition section in the evaluation page requires users to manually type or paste a Shopee search link for each product. This link is fully deterministic — it's built from the selling price and search keyword, both of which are already entered in the form. Manual entry is tedious and error-prone. Auto-computing the link removes a redundant step and ensures consistency.

## What Changes

- Replace the manual text input for the LINK field in the competition form with an auto-computed clickable hyperlink
- The link is generated from `sellingPrice` and `keyword` using the Shopee search URL pattern with price range filters (75%–110% of selling price), rating ≥4, sorted by sales
- The computed link value is stored in the `link` field of `CompetitionProduct` so it persists in the database and appears in evaluation results
- When either `sellingPrice` or `keyword` is missing, the link is `null` and no hyperlink is displayed

## Capabilities

### New Capabilities
- `competition-auto-link`: Auto-computation of Shopee search links from selling price and keyword in the competition form

### Modified Capabilities

_(none — no existing spec-level requirements change)_

## Impact

- **Frontend**: `CompetitionForm.tsx` — replace `<Input>` for link with computed `<a>` element; add auto-compute logic
- **Data model**: No schema change — `CompetitionProduct.link` remains as-is
- **Backend**: No change — link is computed client-side and saved via existing auto-save
- **Section progress**: `link` continues to count as a filled field in `computeSectionProgress` when auto-generated
