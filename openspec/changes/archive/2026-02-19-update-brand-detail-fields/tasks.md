## 1. Update EvaluationHeader Display Logic

- [x] 1.1 Replace `getDisplayFields()` with a curated field list constant defining the 9 fields in order: BD, Link Shopee Mall / LazMall, Kategori, Shopee Mall, No OPEX Issue, Omset >100jt, Score VP, No WA, Email
- [x] 1.2 Update the VP fields rendering to map over the curated list, extracting values from `raw_data` and skipping fields that are missing/empty/null

## 2. Verify

- [x] 2.1 Run frontend linting and type-check (`npm run lint` + `tsc --noEmit`)
- [x] 2.2 Run frontend tests (`npx vitest run`)
