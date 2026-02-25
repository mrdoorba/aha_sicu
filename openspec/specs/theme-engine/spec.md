## ADDED Requirements

### Requirement: Theme Selection Toggle
The system SHALL provide a user-accessible toggle to switch between Light and Dark visual themes.

#### Scenario: User toggles theme
- **WHEN** user clicks the theme toggle in the sidebar
- **THEN** system immediately switches the UI colors to match the selected theme (Light or Dark)

### Requirement: Theme Persistence
The system SHALL remember the user's theme preference across sessions.

#### Scenario: User reloads page
- **WHEN** user previously selected Dark mode and reloads the application
- **THEN** system initializes with the Dark theme active

### Requirement: Theme-Aware Layout Components
Common layout components (cards, headers, sidebars) SHALL adapt their background and text colors based on the active theme.

#### Scenario: Switching to Dark mode
- **WHEN** Dark mode is activated
- **THEN** system uses Deep Navy backgrounds and light text as defined in the AHA brand dark palette
