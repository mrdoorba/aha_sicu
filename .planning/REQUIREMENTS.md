# Requirements: Dashboard Email Report

**Defined:** 2026-03-06
**Core Value:** Users can share a visually complete brand evaluation report via email without screenshots or manual formatting.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Email Sending

- [ ] **SEND-01**: User can click "Send Email" button in the DashboardHeader
- [ ] **SEND-02**: User enters recipient email address(es) in a dialog
- [ ] **SEND-03**: User can send to multiple recipients (comma-separated or multi-input)
- [ ] **SEND-04**: User can add CC and BCC recipients
- [ ] **SEND-05**: User can add a custom note/message above the report body
- [ ] **SEND-06**: User sees loading state while email is being sent
- [ ] **SEND-07**: User sees success confirmation with recipient list after sending
- [ ] **SEND-08**: User sees clear error message if sending fails

### Email Content

- [ ] **CONT-01**: Email includes score overview (brand score, verdict, template)
- [ ] **CONT-02**: Email includes detailed evaluation breakdown by category
- [ ] **CONT-03**: Email includes ScoreBreakdownChart rendered as static PNG image
- [ ] **CONT-04**: Email includes data intelligence section (calculator results)
- [ ] **CONT-05**: Email renders correctly on mobile devices (responsive tables)
- [ ] **CONT-06**: Email subject auto-generated with brand name and period
- [ ] **CONT-07**: User can preview the HTML email in-dialog before sending

### Infrastructure

- [ ] **INFRA-01**: Backend API endpoint accepts evaluation data + chart image and sends HTML email
- [ ] **INFRA-02**: SMTP credentials configured via environment variables (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)
- [ ] **INFRA-03**: Email sent via Gmail SMTP (personal or Workspace account)
- [ ] **INFRA-04**: HTML email template uses table-based layout with inline CSS for cross-client compatibility
- [ ] **INFRA-05**: Chart PNG embedded as CID inline image (not data URI)
- [ ] **INFRA-06**: Configurable sender display name via env var (SMTP_FROM_NAME)

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
| SEND-01 | — | Pending |
| SEND-02 | — | Pending |
| SEND-03 | — | Pending |
| SEND-04 | — | Pending |
| SEND-05 | — | Pending |
| SEND-06 | — | Pending |
| SEND-07 | — | Pending |
| SEND-08 | — | Pending |
| CONT-01 | — | Pending |
| CONT-02 | — | Pending |
| CONT-03 | — | Pending |
| CONT-04 | — | Pending |
| CONT-05 | — | Pending |
| CONT-06 | — | Pending |
| CONT-07 | — | Pending |
| INFRA-01 | — | Pending |
| INFRA-02 | — | Pending |
| INFRA-03 | — | Pending |
| INFRA-04 | — | Pending |
| INFRA-05 | — | Pending |
| INFRA-06 | — | Pending |

**Coverage:**
- v1 requirements: 21 total
- Mapped to phases: 0
- Unmapped: 21

---
*Requirements defined: 2026-03-06*
*Last updated: 2026-03-06 after initial definition*
