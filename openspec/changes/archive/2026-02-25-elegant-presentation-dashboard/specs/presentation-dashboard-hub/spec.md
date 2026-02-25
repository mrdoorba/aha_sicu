## ADDED Requirements

### Requirement: Search-First Dashboard Landing
The dashboard SHALL default to a minimalist search interface when no brand is selected for presentation.

#### Scenario: User visits dashboard
- **WHEN** user lands on the dashboard with no active brand selection
- **THEN** system displays a prominent search bar to find a brand

### Requirement: Read-Only Presentation View
The dashboard SHALL display a comprehensive, read-only presentation of a selected brand's latest evaluation.

#### Scenario: User selects a brand to present
- **WHEN** user searches for and selects a brand
- **THEN** system displays the brand's latest evaluation score, verdict, category breakdown, and recommendation text (email/WhatsApp output)

### Requirement: Dashboard Logic Isolation
The Presentation Hub on the dashboard SHALL not allow direct editing of evaluation inputs.

#### Scenario: User attempts to edit on dashboard
- **WHEN** user is viewing a brand presentation on the dashboard
- **THEN** system displays data in a non-editable format and provides a "Edit Evaluation" button to navigate to the full evaluation page
