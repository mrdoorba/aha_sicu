# Architecture - Frontend

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive | **Part:** frontend | **Type:** web

## Overview

The frontend is a React 19 Single Page Application (SPA) built with TypeScript 5.9 and Vite 7.2. It provides the user-facing interface for brand health evaluation, including data entry forms, file upload, calculator execution, scoring, and evaluation history.

## Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Framework | React | 19.2 |
| Language | TypeScript | 5.9 |
| Bundler | Vite | 7.2 |
| Styling | Tailwind CSS | 4.1 |
| UI Primitives | Radix UI | 1.4 |
| Data Fetching | TanStack React Query | 5.90 |
| Tables | TanStack React Table | 8.21 |
| Forms | React Hook Form | 7.71 |
| Routing | React Router DOM | 7.13 |
| Auth | Firebase | 12.8 |
| API Client | openapi-fetch | 0.15 |
| Icons | Lucide React | 0.563 |
| Date | date-fns | 4.1 |
| Date Picker | react-day-picker | 9.13 |
| i18n | i18next + react-i18next | 25.8 / 16.5 |
| Toasts | Sonner | 2.0 |
| Theme | next-themes | 0.4 |
| Testing | Vitest + Testing Library | 4.0 / 16.3 |

## Architecture Pattern

**Component-based SPA** with:
- Client-side routing (React Router)
- Server state management (React Query)
- Context-based auth (Firebase Auth)
- Typed API client (openapi-fetch)

## Application Bootstrap

```
main.tsx
  └── StrictMode
      └── App.tsx
          ├── BrowserRouter (routing)
          ├── QueryClientProvider (React Query)
          ├── AuthProvider (Firebase auth state)
          ├── Toaster (notifications)
          └── Routes
              ├── /login → LoginPage
              └── MainLayout (nested layout)
                  ├── /dashboard → ProtectedRoute → DashboardPage
                  ├── /brands → ProtectedRoute → BrandsPage
                  ├── /evaluation/:brandId → ProtectedRoute → EvaluationPage
                  ├── /history/:id → ProtectedRoute → EvaluationDetailPage
                  ├── /history → ProtectedRoute → HistoryPage
                  ├── /rules → RoleProtectedRoute(leader/admin) → RulesPage
                  ├── /accounts → RoleProtectedRoute(admin) → AccountsPage
                  └── / → redirect to /dashboard
```

## State Management

### Authentication (React Context)
- `AuthContext` provides `{ user, loading, login, logout }`
- Subscribes to Firebase `onAuthStateChanged` on mount
- `useAuth()` hook for consuming components

### Server State (React Query)
All API data is managed via React Query hooks:
- Automatic caching, deduplication, and background refetch
- Query invalidation on mutations (e.g., saving inputs invalidates evaluation state)
- Pagination support with `keepPreviousData`

### Local State (React useState)
- UI-only state (form focus, modals, tabs)
- No Redux, MobX, or other state libraries

## Key Architectural Patterns

### Auto-Save with Debouncing
`useAutoSaveForm` implements 500ms debounced auto-save:
- Uses refs to avoid stale closures
- Deep merges partial updates with server defaults
- Tracks save status: `idle` → `saving` → `saved` / `error`

### Upload Flow (3-Step)
1. `useRequestSignedUrl` → Get GCS signed URL from backend
2. XHR PUT to signed URL with progress tracking
3. `useProcessUpload` → Backend parses file and auto-runs dependent calculators

### Role-Based Access
- `ProtectedRoute` — Redirects to /login if not authenticated
- `RoleProtectedRoute` — Checks user role, shows toast and redirects if unauthorized

## Page Architecture

| Page | Route | Purpose | Key Components |
|------|-------|---------|---------------|
| LoginPage | `/login` | Email/password login | react-hook-form |
| DashboardPage | `/dashboard` | Welcome + brand search | BrandSearch, PresentationDashboard |
| BrandsPage | `/brands` | Brand listing + sync | BrandTable, SyncStatus, Pagination |
| EvaluationPage | `/evaluation/:brandId` | Main evaluation workflow | SectionNav, EvaluationSections, ScorePanel, FileUploadSection |
| EvaluationDetailPage | `/history/:id` | View saved evaluation | Score breakdown tables |
| HistoryPage | `/history` | Evaluation history list | EvaluationHistoryTable, DeleteEvaluationDialog |
| RulesPage | `/rules` | Edit scoring rules | RulesCategoryCard, PasswordConfirmDialog |
| AccountsPage | `/accounts` | User account management | Admin-only account CRUD |

## Evaluation Page Architecture (Primary Workflow)

The evaluation page is the core of the application with 6 sections:

```
EvaluationPage
├── EvaluationHeader (brand info display)
├── SectionNav (sticky sidebar with 6 steps + progress)
├── EvaluationSections (main content)
│   ├── Section 1: Manual Forms (9 domain forms)
│   │   ├── OperationalForm, BusinessForm, ContentForm
│   │   ├── VisitorsForm, PromoToolsForm, ProductsStatusForm
│   │   ├── AdsForm, CampaignForm, CompetitionForm
│   │   └── Auto-save via useAutoSaveForm
│   ├── Section 2: File Upload (4 file types)
│   │   ├── FileUploadSection → FileUploadSlot ×4
│   │   └── 3-step upload: sign → XHR → process
│   ├── Section 3: Calculator Results
│   │   ├── AdsKeywordResults, TopSkuResults, DiscountResults
│   │   └── Run individually or all at once
│   ├── Section 4: Scoring
│   │   ├── ScoringSection (generate button, stale warning)
│   │   ├── FinalScoreDisplay (score + verdict icon)
│   │   └── ScoreBreakdown (category table)
│   ├── Section 5: Output (email)
│   │   └── EmailOutput (copy button)
│   └── Section 6: Save
│       └── SaveButton
└── ScorePanel (sticky sidebar with score summary)
```

## API Client Architecture

Uses `openapi-fetch` with TypeScript path types for type-safe API calls:
- Base URL from `VITE_API_BASE_URL` env var
- Auth middleware automatically injects Firebase Bearer token
- All hooks use `useQuery`/`useMutation` from React Query

## Form Data Architecture

The `ManualData` interface in `formConfig.ts` defines 9 form sections with ~40 fields total:
- All fields are nullable (allows partial saves)
- `EMPTY_MANUAL_DATA` provides defaults
- `computeSectionProgress()` calculates fill percentage per section
- Currency fields formatted as IDR with `formatIDR`/`parseIDR` helpers

## Accessibility

- Skip-to-main-content link
- ARIA labels on interactive elements
- `aria-busy`, `aria-invalid` on form states
- `aria-live` regions for status updates
- Semantic HTML (main, header, nav, aside)

## Build & Development

```bash
npm run dev        # Start Vite dev server
npm run build      # TypeScript check + Vite build
npm run test       # Run Vitest in watch mode
npm run test:run   # Run Vitest once
npm run lint       # ESLint
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend API URL |
| `VITE_FIREBASE_API_KEY` | Firebase API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | Firebase auth domain |
| `VITE_FIREBASE_PROJECT_ID` | Firebase project ID |
