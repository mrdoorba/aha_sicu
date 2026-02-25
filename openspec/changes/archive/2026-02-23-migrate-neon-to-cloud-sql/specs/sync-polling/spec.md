## MODIFIED Requirements

### Requirement: Cloud Run on-demand CPU
The CI/CD pipeline SHALL deploy Cloud Run with CPU throttling enabled (`--cpu-throttling`) for the dev environment, so that CPU is only allocated during request processing.

#### Scenario: Dev deployment uses on-demand CPU
- **WHEN** the backend deploys to dev environment via CI/CD
- **THEN** the Cloud Run service runs with `cpu-throttling: true`

#### Scenario: Dev deployment targets Jakarta region
- **WHEN** the backend deploys to dev environment via CI/CD
- **THEN** the Cloud Run service is deployed to `asia-southeast2` (Jakarta)
