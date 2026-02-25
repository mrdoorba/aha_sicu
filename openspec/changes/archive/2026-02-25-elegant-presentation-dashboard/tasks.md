## 1. Foundational Theme System

- [x] 1.1 Update `frontend/src/index.css` to standardize colors using CSS variables (e.g., `--primary`, `--background`) that support theme switching.
- [x] 1.2 Update `frontend/src/main.tsx` to wrap the application in a `ThemeProvider` from `next-themes`.

## 2. Global Sidebar & Layout Implementation

- [x] 2.1 Create a new `Sidebar` component in `frontend/src/components/layout/` with collapsible state and navigation links.
- [x] 2.2 Create a `MainLayout` component that includes the Sidebar and a main content area.
- [x] 2.3 Update `frontend/src/App.tsx` to wrap protected routes with `MainLayout` and remove manual `Header` imports from pages.
- [x] 2.4 Add a `ThemeToggle` component to the sidebar footer to switch between Light and Dark modes.

## 3. Search-First Dashboard & Presentation Hub

- [x] 3.1 Implement a minimalist "Search for Brand" landing state in `DashboardPage.tsx`.
- [x] 3.2 Create presentation-optimized components for showing Score, Verdict, and Breakdown on the dashboard.
- [x] 3.3 Integrate the `EmailOutput` component into the Dashboard's presentation view.
- [x] 3.4 Wire up the dashboard presentation state to the `brandId` URL query parameter.

## 4. Premium Login Experience Redesign

- [x] 4.1 Update `LoginPage.tsx` to use a 60/40 split-screen layout with a visual branding pane.
- [x] 4.2 Apply glassmorphism styling to the login form container.

## 5. Polish & Verification

- [x] 5.1 Perform a global style pass to ensure consistent spacing, shadows, and typography hierarchy.
- [x] 5.2 Verify that the Sidebar and Dashboard Presentation Hub are fully responsive on mobile/tablet devices.
