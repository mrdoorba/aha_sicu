## 1. Fix CardContent width constraint

- [x] 1.1 Add `min-w-0` to CardContent className in `frontend/src/components/ui/card.tsx`

## 2. Update tests

- [x] 2.1 Update card overflow test in `frontend/src/components/ui/card.test.tsx` to verify CardContent has `min-w-0` and table scrolls within Card > CardContent chain

## 3. Verify

- [x] 3.1 Run frontend lint + typecheck + tests to confirm no regressions
