## Context

The current Store ICU frontend uses a traditional top-bar navigation and a simple white-background dashboard. The UI is built with React 19, Tailwind CSS 4, and Radix UI. Branding colors (Dark Navy and Primary Blue) are defined in `index.css` but are currently static.

## Goals / Non-Goals

**Goals:**
- Transition the application layout to a professional sidebar-based navigation.
- Implement a search-first, read-only "Presentation Hub" on the Dashboard.
- Provide a seamless Light/Dark theme transition.
- Elevate the Login page to a premium visual standard.

**Non-Goals:**
- Modifying the core evaluation logic or backend scoring engines.
- Adding new administrative features beyond UI/UX improvements.
- Changing the existing mobile responsiveness (though it must be maintained).

## Decisions

### 1. Unified Layout System
- **Decision**: Introduce a `MainLayout` component that wraps all protected routes.
- **Rationale**: Currently, each page imports `Header` manually. Moving to a global layout ensures the sidebar persists during navigation and simplifies state management for the collapsible sidebar.
- **Alternatives**: Keeping the top header but making it "sticky" (rejected as it doesn't solve the content-cramping issue on data-heavy pages).

### 2. Search-First Dashboard with Presentation State
- **Decision**: The `DashboardPage` will have two primary states: `Default` (Search UI) and `Presented` (Brand Result UI).
- **Rationale**: Users need a clear entry point to find brands for presentation. Using URL params (`?presentingBrandId=...`) allows sharing specific presentations and maintains browser history.
- **Alternatives**: Creating a separate `/presentation` route (rejected to keep the Dashboard as the central hub).

### 3. CSS Variable Driven Theming
- **Decision**: Standardize all color usage in `index.css` using Tailwind 4 CSS variables and `next-themes` for detection.
- **Rationale**: `next-themes` is already in `package.json`. Leveraging native CSS variables ensures zero-runtime overhead for theme switching and works perfectly with Tailwind's `@theme` block.
- **Alternatives**: Using a CSS-in-JS theme provider (rejected as Tailwind 4's native support is more performant).

### 4. Split-Screen Login
- **Decision**: 60/40 Split layout for `LoginPage`.
- **Rationale**: 60% visual/branding space and 40% functional login form provides a "Premium" first impression without overwhelming the user.

## Risks / Trade-offs

- **[Risk]**: Sidebar might take up too much space on smaller desktop screens. → **Mitigation**: Implement a "Collapsed" state with icon-only navigation and a clear toggle button.
- **[Risk]**: Dark mode accessibility with existing charts/tables. → **Mitigation**: Use a specific "Deep Navy" dark palette (already defined in `index.css`) that maintains high contrast with Primary Blue.
