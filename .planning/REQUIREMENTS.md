# Requirements: Dashboard Email Report

**Defined:** 2026-03-06
**Core Value:** Users can share a visually complete brand evaluation report via email without screenshots or manual formatting.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Email Sending

- [x] **SEND-01**: User can click "Send Email" button in the DashboardHeader
- [x] **SEND-02**: User enters recipient email address(es) in a dialog
- [x] **SEND-03**: User can send to multiple recipients (comma-separated or multi-input)
- [x] **SEND-04**: User can add CC and BCC recipients
- [x] **SEND-05**: User can add a custom note/message above the report body
- [x] **SEND-06**: User sees loading state while email is being sent
- [x] **SEND-07**: User sees success confirmation with recipient list after sending
- [x] **SEND-08**: User sees clear error message if sending fails

### Email Content

- [x] **CONT-01**: Email includes score overview (brand score, verdict, template)
- [x] **CONT-02**: Email includes detailed evaluation breakdown by category
- [x] **CONT-03**: Email includes ScoreBreakdownChart rendered as static PNG image
- [x] **CONT-04**: Email includes data intelligence section (calculator results)
- [x] **CONT-05**: Email renders correctly on mobile devices (responsive tables)
- [x] **CONT-06**: Email subject auto-generated with brand name and period
- [x] **CONT-07**: User can preview the HTML email in-dialog before sending

### Infrastructure

- [x] **INFRA-01**: Backend API endpoint accepts evaluation data + chart image and sends HTML email
- [x] **INFRA-02**: SMTP credentials configured via environment variables (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)
- [x] **INFRA-03**: Email sent via Gmail SMTP (personal or Workspace account)
- [x] **INFRA-04**: HTML email template uses table-based layout with inline CSS for cross-client compatibility
- [x] **INFRA-05**: Chart PNG embedded as CID inline image (not data URI)
- [x] **INFRA-06**: Configurable sender display name via env var (SMTP_FROM_NAME)

## v2 Requirements

### Convenience

- **CONV-01**: Recently used recipients stored in localStorage for quick selection
- **CONV-02**: Email delivery status tracking

## Out of Scope

| Feature | Reason |
|---------|--------|
| Scheduled/recurring emails | Massive scope increase (cron, scheduling UI, timezones) |
| PDF attachment | Separate rendering pipeline, doubles maintenance |
| Replacing History page mailto | Explicitly separate per project scope |
| Template customization | Fixed template matching dashboard; customization breaks consistency |
| Non-Gmail providers | Env vars allow future swap, but only Gmail tested |
| Inline editing of report data | Email must reflect actual evaluation data |
| Contact/address book | Full CRUD for contacts is overkill for internal tool |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SEND-01 | Phase 2 | Complete |
| SEND-02 | Phase 2 | Complete |
| SEND-03 | Phase 3 | Complete |
| SEND-04 | Phase 3 | Complete |
| SEND-05 | Phase 3 | Complete |
| SEND-06 | Phase 2 | Complete |
| SEND-07 | Phase 2 | Complete |
| SEND-08 | Phase 2 | Complete |
| CONT-01 | Phase 1 | Complete |
| CONT-02 | Phase 1 | Complete |
| CONT-03 | Phase 1 | Complete |
| CONT-04 | Phase 1 | Complete |
| CONT-05 | Phase 1 | Complete |
| CONT-06 | Phase 1 | Complete |
| CONT-07 | Phase 3 | Complete |
| INFRA-01 | Phase 1 | Complete |
| INFRA-02 | Phase 1 | Complete |
| INFRA-03 | Phase 1 | Complete |
| INFRA-04 | Phase 1 | Complete |
| INFRA-05 | Phase 1 | Complete |
| INFRA-06 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0

---
*Requirements defined: 2026-03-06*
*Last updated: 2026-03-06 after roadmap creation*
