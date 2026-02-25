### Requirement: Downtime warning modal dialog
The frontend SHALL display a centered modal dialog with a dimmed overlay when an API call returns HTTP 500, informing the user that the system may be unavailable and showing the operating hours (08:00–18:30 WIB). The modal SHALL include a "Mengerti" button to dismiss it.

#### Scenario: Modal appears on first API 500 error
- **WHEN** any API call (query or mutation) returns HTTP 500
- **THEN** a centered modal dialog appears with a dimmed background overlay, displaying a warning message with operating hours (08:00–18:30 WIB) and a "Mengerti" dismiss button

#### Scenario: Modal does not reappear after dismissal
- **WHEN** the user clicks the "Mengerti" button to dismiss the modal
- **AND** subsequent API calls also return HTTP 500
- **THEN** the modal SHALL NOT appear again for the remainder of the browser session

#### Scenario: Modal reappears on page refresh
- **WHEN** the user refreshes the browser page
- **AND** an API call returns HTTP 500
- **THEN** the modal SHALL appear again (session state is reset)

#### Scenario: Modal does not appear for non-500 errors
- **WHEN** an API call returns a non-500 error (e.g., 400, 401, 403, 404)
- **THEN** the downtime warning modal SHALL NOT appear

### Requirement: Modal blocks interaction until dismissed
The modal dialog SHALL prevent interaction with the page content behind it until the user dismisses it by clicking "Mengerti".

#### Scenario: Overlay blocks background interaction
- **WHEN** the downtime warning modal is visible
- **THEN** the user SHALL NOT be able to click or interact with elements behind the overlay

#### Scenario: Dismiss restores interaction
- **WHEN** the user clicks "Mengerti"
- **THEN** the modal and overlay disappear and the user can interact with the page normally
