## ADDED Requirements

### Requirement: All PresentationDashboard strings use i18n
The PresentationDashboard component SHALL render all user-visible text through the `t()` translation function with Indonesian translations.

#### Scenario: Loading state shows Indonesian text
- **WHEN** the dashboard is loading
- **THEN** the loading message SHALL display the Indonesian translation (e.g., "Mengumpulkan data evaluasi...")

#### Scenario: Empty state shows Indonesian text
- **WHEN** no evaluation exists for a brand
- **THEN** the heading, description, and button labels SHALL display in Indonesian

#### Scenario: Verdict labels show Indonesian text
- **WHEN** a verdict is displayed (Approved/Rejected/Pending)
- **THEN** the verdict label SHALL display the Indonesian translation

#### Scenario: Card titles and subtitles show Indonesian text
- **WHEN** the dashboard renders score breakdown, operation intelligence, and email output cards
- **THEN** all card titles, subtitles, badge labels, and footer text SHALL use `t()` with Indonesian translations

### Requirement: All BrandTable strings use i18n
The BrandTable component SHALL render all user-visible text through the `t()` translation function.

#### Scenario: Table headers show Indonesian text
- **WHEN** the brand table renders
- **THEN** column headers (Brand Name, Key Info, Meeting Data, Action) SHALL display Indonesian translations

#### Scenario: Status badges and buttons show Indonesian text
- **WHEN** meeting data availability or evaluate buttons render
- **THEN** "Available", "Not available", "Evaluate", and "No data" SHALL display Indonesian translations

### Requirement: All FinalScoreDisplay strings use i18n
The FinalScoreDisplay component SHALL render verdict labels and score heading through `t()`.

#### Scenario: Verdict config labels use translations
- **WHEN** a verdict badge renders (Approved, Rejected, Non Mall, No Brand, Opex Issue, No Verdict)
- **THEN** the label SHALL come from `t()` with Indonesian translations

#### Scenario: Total score label uses translation
- **WHEN** the total score display renders
- **THEN** "Total Score" SHALL display as "Skor Total" via `t()`

### Requirement: All ScorePanel strings use i18n
The ScorePanel component SHALL render heading and score label through `t()`.

#### Scenario: Score summary heading uses translation
- **WHEN** the score panel renders
- **THEN** "Score Summary" and "Total Score" SHALL display Indonesian translations

### Requirement: All FileUploadSlot strings use i18n
The FileUploadSlot component SHALL render all status messages and button labels through `t()`.

#### Scenario: Upload status messages show Indonesian text
- **WHEN** a file is being uploaded
- **THEN** status messages (preparing, uploading, processing, verifying) SHALL display Indonesian translations

#### Scenario: Upload buttons show Indonesian text
- **WHEN** upload action buttons render
- **THEN** "Upload File", "Re-upload", "Retry" SHALL display Indonesian translations

### Requirement: All ScoreBreakdown table headers use i18n
The ScoreBreakdown component SHALL render table headers through `t()`.

#### Scenario: Score breakdown table renders Indonesian headers
- **WHEN** the score breakdown table renders
- **THEN** "Category", "Score", "Max" headers SHALL display Indonesian translations

### Requirement: RulesPage hardcoded strings use i18n
The RulesPage component SHALL render all user-visible strings through `t()` instead of hardcoded text (whether English or Indonesian).

#### Scenario: English strings in RulesPage use translations
- **WHEN** the rules page renders
- **THEN** "Updated", "Label", "Good Candidate", "Needs Review" SHALL display Indonesian translations via `t()`

#### Scenario: Hardcoded Indonesian strings in RulesPage use t()
- **WHEN** the rules page renders labels, headings, and buttons
- **THEN** all hardcoded Indonesian strings SHALL be replaced with `t()` calls referencing keys in `id.json`

### Requirement: ScoringSection error prefix uses i18n
The ScoringSection component SHALL render the error prefix through `t()`.

#### Scenario: Error message prefix is translated
- **WHEN** a scoring error is displayed
- **THEN** the "Error:" prefix SHALL display the Indonesian translation via `t()`

### Requirement: All new translation keys exist in id.json
The locale file `id.json` SHALL contain all new translation keys with proper Indonesian translations.

#### Scenario: id.json contains all required keys
- **WHEN** the application loads
- **THEN** every `t()` call across all modified components SHALL resolve to a valid Indonesian translation string

### Requirement: Tests updated for translated text
All test files referencing modified English strings SHALL be updated to match the new Indonesian translations.

#### Scenario: Tests pass with new translations
- **WHEN** the test suite runs
- **THEN** all tests SHALL pass with the updated Indonesian text matchers
