## Context

The competition section of the evaluation form (`CompetitionForm.tsx`) has three product slots, each with five fields: `productName`, `sellingPrice`, `keyword`, `link`, and `marketPrice`. Currently `link` is a free-text input. The identical Shopee search URL is already used in the team's Excel workflow via a `HYPERLINK`+`ENCODEURL` formula. Moving this computation into the app removes a manual step.

## Goals / Non-Goals

**Goals:**
- Auto-compute the Shopee search link from `sellingPrice` and `keyword`
- Display the link as a clickable hyperlink instead of a text input
- Persist the computed link value to the database via existing auto-save

**Non-Goals:**
- Changing the `CompetitionProduct` data model or backend schema
- Making the link user-editable or overridable
- Supporting marketplaces other than Shopee

## Decisions

### 1. Compute link in a pure helper function

Create a `buildShopeeSearchUrl(sellingPrice, keyword)` function that returns the URL string or `null`. This keeps the logic testable and reusable.

URL pattern:
```
https://shopee.co.id/search
  ?keyword={encodeURIComponent(keyword)}
  &maxPrice={Math.round(sellingPrice * 1.10)}
  &minPrice={Math.round(sellingPrice * 0.75)}
  &noCorrection=true
  &page=0
  &ratingFilter=4
  &sortBy=sales
```

**Why**: A pure function is trivially testable and keeps the component clean.

### 2. Trigger link update on sellingPrice/keyword change

When either `sellingPrice` or `keyword` changes in the form, immediately recompute the link and call `onChange('competition', '<productKey>.link', computedLink)`. This piggybacks on the existing auto-save mechanism — no new save path needed.

**Alternative considered**: Using `useEffect` to watch for changes and compute. Rejected because inline computation on each relevant onChange is simpler and avoids extra render cycles.

### 3. Replace input with clickable anchor

Replace the `<Input>` element for link with:
- A clickable `<a>` tag with `target="_blank"` and `rel="noopener noreferrer"` when both inputs are present
- A muted placeholder text when either input is missing

**Why**: Matches the pattern already used in `clickable-header-links` spec. Users never need to type the link manually.

## Risks / Trade-offs

- **Existing manual links overwritten**: When the form loads with existing data where both `sellingPrice` and `keyword` are present, the old manual `link` value will be replaced by the computed one on first field change. → Acceptable because the formula produces the same URL the team was manually entering.
- **Price rounding**: `maxPrice` and `minPrice` are rounded to integers via `Math.round`. → Shopee search params accept integers; fractional rupiah is not meaningful.
