# S04: Frontend Currency and Marketplace UI

**Marketplace-aware currency formatting, Rules page marketplace tabs, evaluation flow marketplace wiring, and display component migration — completing the full-stack THB marketplace expansion.**

All 4 tasks delivered: T01 (currency utilities + CurrencyField currency prop), T02 (Rules page ID/TH tabs with React Query cache isolation), T03 (evaluation flow marketplace wiring through orchestrator→hooks→API), T04 (display component migration + IDR audit cleanup).

**Verification:** 63 test files, 536 tests passed, 0 failures. Grep audit clean — zero local formatIDR/formatCurrencyDisplay copies remain. All 6 frontend requirements validated (DATA-01, RULES-01, RULES-02, EVAL-01, EVAL-02, EVAL-03).

**S04 is the final slice in M001. Milestone complete.**