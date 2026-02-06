# Pre-Epic 3 Execution Checklist

**Complete ALL steps before starting any Epic 3 implementation:**

1. **Run correct-course workflow** (`/bmad-bmm-correct-course`) — Update PRD, architecture, and Epic 3 stories for calculator spec changes. Use the prompt below.
2. **Create and implement Story 2.6** — Retrofit accessibility basics on existing UI (BrandsPage, SyncStatus, SSE indicators, Layout/Nav). Audit against the 7-item accessibility checklist in dev-story DoD.
3. **Begin Epic 3 implementation** — Only after steps 1 and 2 are complete.

---

# Correct-Course Workflow Prompt — Epic 3 Calculator Changes

> The BD team has made changes to the calculator specifications in their Google Sheets process. This was discovered during the Epic 2 retrospective.
>
> **What's NOT affected:**
> - VP Sheet and Meeting Sheet are unchanged
> - All Epic 2 work (brand data sync, SSE, daily scheduler) is safe
>
> **What IS affected:**
> - Calculator logic/formulas — specifically the Ads Keyword Calculator, Discount Check Calculator, Top SKU Calculator, and Final Scoring
> - This impacts Epic 3 stories 3.4 through 3.9
>
> **What needs updating:**
> - PRD — functional requirements related to calculators (FR8-FR13, FR15-FR17)
> - Architecture — calculator data flows and computation patterns if they changed
> - Epics/Stories — acceptance criteria, dev notes, and task breakdowns for stories 3.4-3.9
>
> I will explain the full calculator specification changes so we can correct the planning artifacts before starting Epic 3 implementation.
