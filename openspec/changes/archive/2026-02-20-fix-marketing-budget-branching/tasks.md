## 1. Add G68 left-side extraction helper

- [x] 1.1 Add `_parse_g68_left` helper in `scoring.py` that extracts the raw percentage before "~" from G68 text (e.g., "15.3% ~ 22.7%" → 0.153). Return 0.0 if no "~" found.

## 2. Fix `_compute_g72` branching logic

- [x] 2.1 Refactor `_compute_g72` to compute both `capped_value` (existing MIN/MAX chain using `g68_left`) and `ceiling_g68` (CEILING of first number to 0.01), compare them, and return `capped_value` if `capped_value > ceiling_g68`, otherwise return `ceiling_g68`
- [x] 2.2 Replace the current single `g68_first` extraction with the two distinct parsing methods: `g68_left` (raw fraction before "~") for the MIN chain, and `ceiling_g68` (`math.ceil` to nearest 0.01) for the fallback branch

## 3. Update tests

- [x] 3.1 Add test for G72=TRUE scenario: capped_value > ceiling_g68, verify capped value is returned
- [x] 3.2 Add test for G72=FALSE scenario: capped_value ≤ ceiling_g68, verify ceiling_g68 is returned (result can exceed 20% for non-fashion)
- [x] 3.3 Add test for non-fashion store with high G68 (e.g., "22.0% ~ 28.5%"), verify result is 0.22 (above 20% cap)
- [x] 3.4 Add test for empty G68 text — verify existing capped behavior is preserved
- [x] 3.5 Add test for G68 without "~" — verify ceiling_g68 is used as fallback
- [x] 3.6 Verify existing G72/G73 tests still pass after refactor (175/175 passed)
