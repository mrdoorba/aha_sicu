## Why

The current user interface follows a standard SaaS boilerplate aesthetic which, while functional, lacks the "premium" and "elegant" feel required for professional presentations to brand partners. To position Store ICU as a high-value tool, the dashboard must transition from a simple landing page to a polished "Presentation Hub" that effectively showcases evaluation results, verdicts, and recommendations.

## What Changes

- **Global Navigation Overhaul**: Replace the current top header with a professional, collapsible sidebar navigation system to maximize content space and improve organizational feel.
- **Search-First Dashboard**: Redesign the default dashboard state to a minimalist "Search for Brand" interface, similar to a command center.
- **Presentation Mode Dashboard**: Implement a read-only, high-fidelity dashboard view for selected brands that aggregates scores, category breakdowns, and the generated email/WhatsApp outputs for partner presentations.
- **Modern Login Experience**: Redesign the login page using a split-screen layout with premium visual assets and glassmorphism elements.
- **Dual-Theme Support**: Implement a system-wide Light and Dark mode toggle to adapt to different presentation environments (e.g., bright offices vs. large screen presentations).

## Capabilities

### New Capabilities
- `sidebar-navigation`: A global sidebar system that supports collapsing, active state tracking, and a theme toggle integration.
- `presentation-dashboard-hub`: A read-only dashboard view that pulls latest evaluation data and presents it in a high-fidelity report format.
- `theme-engine`: A system-wide styling layer supporting Light and Dark modes using Tailwind CSS 4 variables and `next-themes`.

### Modified Capabilities
- `calculator-run-ux`: Requirements expanded to include presenting results on the main dashboard hub, not just in history or the evaluation page.

## Impact

- **Frontend**: Significant changes to `App.tsx` (routing/layout), `Header.tsx` (replacement), and the creation of new layout/dashboard components.
- **Styling**: Migration of hardcoded white/navy colors to CSS variables that support theme switching in `index.css`.
- **User Experience**: Improved first impression (Login) and clearer presentation flow (Dashboard).
