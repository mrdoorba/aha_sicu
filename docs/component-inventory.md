# Component Inventory

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive | **Part:** Frontend

## Summary

- **Total Components:** 45+
- **Pages:** 7
- **Custom Hooks:** 13+
- **UI Primitives (Shadcn):** 15
- **Domain Components:** 30+

---

## Pages

| Component | File | Route | Purpose |
|-----------|------|-------|---------|
| LoginPage | `pages/LoginPage.tsx` | `/login` | Email/password login with react-hook-form |
| DashboardPage | `pages/DashboardPage.tsx` | `/dashboard` | Welcome page with user info |
| BrandsPage | `pages/BrandsPage.tsx` | `/brands` | Brand listing with search, pagination, sync status |
| EvaluationPage | `pages/EvaluationPage.tsx` | `/evaluation/:brandId` | Main evaluation workflow (forms, upload, scoring) |
| EvaluationDetailPage | `pages/EvaluationDetailPage.tsx` | `/history/:id` | View saved evaluation details |
| HistoryPage | `pages/HistoryPage.tsx` | `/history` | Evaluation history with filters |
| RulesPage | `pages/RulesPage.tsx` | `/rules` | Scoring rules editor (leader/admin) |

---

## Auth Components

| Component | File | Props | Purpose |
|-----------|------|-------|---------|
| ProtectedRoute | `auth/ProtectedRoute.tsx` | `{ children }` | Redirects to /login if unauthenticated |
| RoleProtectedRoute | `auth/RoleProtectedRoute.tsx` | `{ allowedRoles, children, accessDeniedMessage }` | Checks user role, redirects if unauthorized |

---

## Layout Components

| Component | File | Props | Purpose |
|-----------|------|-------|---------|
| Header | `layout/Header.tsx` | none | Navigation header with links and logout dialog |

---

## Brand Components

| Component | File | Props | Purpose |
|-----------|------|-------|---------|
| BrandTable | `brands/BrandTable.tsx` | `{ brands, isLoading }` | Paginated brand list with raw data |

---

## Evaluation Components

### Core Evaluation

| Component | File | Purpose |
|-----------|------|---------|
| EvaluationHeader | `evaluation/EvaluationHeader.tsx` | Brand name + VP & meeting data display |
| SectionNav | `evaluation/SectionNav.tsx` | Sticky sidebar with 6 section steps + progress |
| EvaluationSections | `evaluation/EvaluationSections.tsx` | Main form container with intersection observer |
| FileUploadSection | `evaluation/FileUploadSection.tsx` | 4 file upload slots container |
| FileUploadSlot | `evaluation/FileUploadSlot.tsx` | Single file upload with progress bar |
| SaveButton | `evaluation/SaveButton.tsx` | Save evaluation button |

### Form Components

| Component | File | Category | Fields |
|-----------|------|----------|--------|
| OperationalForm | `forms/OperationalForm.tsx` | Operational | 5 fields (order, shipment, chat, rating) |
| BusinessForm | `forms/BusinessForm.tsx` | Business | 7 fields (6-month sales + conversion rate) |
| ContentForm | `forms/ContentForm.tsx` | Content | 2 fields (needs improvement, good quality) |
| VisitorsForm | `forms/VisitorsForm.tsx` | Visitors | 3 fields (total, followers, returning) |
| PromoToolsForm | `forms/PromoToolsForm.tsx` | Promo Tools | 11 currency fields |
| ProductsStatusForm | `forms/ProductsStatusForm.tsx` | Products | 2 fields (count + store status select) |
| AdsForm | `forms/AdsForm.tsx` | Ads | 2 currency fields (sales, cost) |
| CampaignForm | `forms/CampaignForm.tsx` | Campaign | 2 fields (nominated, available sessions) |
| CompetitionForm | `forms/CompetitionForm.tsx` | Competition | 6 fields (3 products × keyword + price) |

### Form Field Components

| Component | File | Purpose |
|-----------|------|---------|
| NumberField | `forms/NumberField.tsx` | Numeric input with unit and benchmark |
| CurrencyField | `forms/CurrencyField.tsx` | IDR currency input with formatting |
| SelectField | `forms/SelectField.tsx` | Dropdown select with benchmark |
| SaveIndicator | `forms/SaveIndicator.tsx` | Auto-save status display |

### Calculator Result Components

| Component | File | Purpose |
|-----------|------|---------|
| CalculatorResultsSection | `calculators/CalculatorResultsSection.tsx` | Container for all calculator results |
| AdsKeywordResults | `calculators/AdsKeywordResults.tsx` | Ads/keyword analysis output display |
| TopSkuResults | `calculators/TopSkuResults.tsx` | Top SKU ranking tables |
| DiscountResults | `calculators/DiscountResults.tsx` | Discount check results |

### Scoring Components

| Component | File | Purpose |
|-----------|------|---------|
| ScoringSection | `scoring/ScoringSection.tsx` | Generate score button + stale warning |
| FinalScoreDisplay | `scoring/FinalScoreDisplay.tsx` | Score number + verdict icon (✔️/❌/⭕️) |
| ScoreBreakdown | `scoring/ScoreBreakdown.tsx` | Category-by-category score table |
| ScorePanel | `scoring/ScorePanel.tsx` | Sticky sidebar with score summary |
| VerdictSelector | `scoring/VerdictSelector.tsx` | Verdict dropdown selector |
| EmailOutput | `scoring/EmailOutput.tsx` | Generated email template with copy |
| WhatsAppLink | `scoring/WhatsAppLink.tsx` | WhatsApp message link generator |

---

## Evaluation History Components

| Component | File | Purpose |
|-----------|------|---------|
| EvaluationHistoryTable | `evaluations/EvaluationHistoryTable.tsx` | Paginated history with sort, search, date filters |

---

## Rules Components

| Component | File | Purpose |
|-----------|------|---------|
| RulesCategoryCard | `rules/RulesCategoryCard.tsx` | Collapsible category card with editable thresholds |
| PasswordConfirmDialog | `rules/PasswordConfirmDialog.tsx` | Reauthentication modal before saving rules |

---

## Sync Components

| Component | File | Purpose |
|-----------|------|---------|
| SyncStatus | `sync/SyncStatus.tsx` | Sync status badge + SSE connection + "Sync Now" button |

---

## UI Primitives (Shadcn/Radix)

All located in `components/ui/`:

| Component | Purpose |
|-----------|---------|
| Badge | Status/label badges |
| Button | Action buttons with variants |
| Calendar | Date picker calendar |
| Card | Content container cards |
| Collapsible | Expandable sections |
| Dialog | Modal dialogs |
| Input | Text input fields |
| Label | Form labels |
| Popover | Floating content |
| Progress | Progress bars |
| RadioGroup | Radio button groups |
| Select | Dropdown selects |
| Sonner | Toast notifications |
| Table | Data tables |
| Tabs | Tab navigation |

---

## Custom Hooks

| Hook | File | Purpose |
|------|------|---------|
| useAuth | `context/AuthContext.tsx` | Firebase auth state |
| useCurrentUser | `hooks/useCurrentUser.ts` | Fetch user profile from /me |
| useBrands | `hooks/useBrands.ts` | Paginated brand list |
| useBrandDetail | `hooks/useBrandDetail.ts` | Single brand detail |
| useEvaluationState | `hooks/useEvaluation.ts` | Evaluation inputs for a brand |
| useSaveEvaluationInputs | `hooks/useEvaluation.ts` | Save evaluation inputs mutation |
| useEvaluationDetail | `hooks/useEvaluationDetail.ts` | Single evaluation detail |
| useEvaluationHistory | `hooks/useEvaluationHistory.ts` | Paginated evaluation history |
| useAutoSaveForm | `hooks/useAutoSaveForm.ts` | Debounced auto-save with deep merge |
| useSaveEvaluation | `hooks/useSaveEvaluation.ts` | Save complete evaluation |
| useCalculator | `hooks/useCalculator.ts` | Run single calculator |
| useCalculatorResults | `hooks/useCalculator.ts` | Fetch stored results |
| useCalculatorStatus | `hooks/useCalculator.ts` | Check calculator readiness |
| useRunAllCalculators | `hooks/useCalculator.ts` | Run all calculators |
| useScoring | `hooks/useScoring.ts` | Generate score with staleness tracking |
| useRules | `hooks/useRules.ts` | Fetch scoring rules |
| useUpdateRule | `hooks/useUpdateRule.ts` | Update scoring rule |
| useUpload | `hooks/useUpload.ts` | Multi-step file upload (sign → XHR → process) |
| useSync | `hooks/useSync.ts` | Sync status polling and trigger |
| useSSE | `hooks/useSSE.ts` | Server-Sent Events connection |

---

## Component Hierarchy (Evaluation Page)

```
EvaluationPage
├── Header
├── EvaluationHeader
│   └── Brand info display
├── SectionNav
│   └── 6 section links with progress dots
├── EvaluationSections
│   ├── OperationalForm → NumberField ×5
│   ├── BusinessForm → CurrencyField ×6 + NumberField ×1
│   ├── ContentForm → NumberField ×2
│   ├── VisitorsForm → NumberField ×3
│   ├── PromoToolsForm → CurrencyField ×11
│   ├── ProductsStatusForm → NumberField + SelectField
│   ├── AdsForm → CurrencyField ×2
│   ├── CampaignForm → NumberField ×2
│   ├── CompetitionForm → Input ×6
│   ├── SaveIndicator
│   ├── FileUploadSection
│   │   └── FileUploadSlot ×4
│   ├── CalculatorResultsSection
│   │   ├── AdsKeywordResults
│   │   ├── TopSkuResults
│   │   └── DiscountResults
│   ├── ScoringSection
│   │   ├── FinalScoreDisplay
│   │   ├── ScoreBreakdown
│   │   └── VerdictSelector
│   ├── EmailOutput
│   ├── WhatsAppLink
│   └── SaveButton
└── ScorePanel
    ├── FinalScoreDisplay
    └── Category summary
```
