## ADDED Requirements

### Requirement: Global Sidebar Navigation
The system SHALL provide a persistent sidebar navigation on the left side of the screen for all authenticated routes.

#### Scenario: Navigation links display
- **WHEN** user is logged in
- **THEN** user sees a sidebar containing links to Dashboard, Brands, History, Rules, and Accounts (based on role)

### Requirement: Collapsible Sidebar
The sidebar SHALL support a collapsed state to maximize screen space for content.

#### Scenario: User collapses sidebar
- **WHEN** user clicks the collapse toggle button
- **THEN** sidebar transitions to icon-only mode and the main content area expands

### Requirement: Active Route Highlighting
The sidebar SHALL visually indicate which route is currently active.

#### Scenario: User navigates to Brands page
- **WHEN** user clicks the "Brands" link in the sidebar
- **THEN** the sidebar highlights the Brands link and the browser navigates to `/brands`
