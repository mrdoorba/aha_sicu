# Roadmap: Dashboard Email Report

## Overview

This roadmap delivers the ability to send the AHA SICU evaluation dashboard as a formatted HTML email. The work flows from backend-first (SMTP + HTML template + API endpoint, all testable without UI) to frontend integration (core send flow) to enhanced send options (CC/BCC, preview, custom notes). Three phases, each delivering a verifiable capability.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Backend Email Engine** - SMTP client, HTML email template, and API endpoint that can send a complete dashboard report
- [ ] **Phase 2: Core Send Flow** - Send button, recipient dialog, chart capture, loading/success/error states
- [ ] **Phase 3: Enhanced Send Options** - Multiple recipients, CC/BCC, custom note, and in-dialog email preview

## Phase Details

### Phase 1: Backend Email Engine
**Goal**: A working backend that can accept evaluation data and send a complete, cross-client-compatible HTML email with embedded chart image
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04, INFRA-05, INFRA-06, CONT-01, CONT-02, CONT-03, CONT-04, CONT-05, CONT-06
**Success Criteria** (what must be TRUE):
  1. A POST request to the email endpoint with evaluation ID, recipient, and chart image results in a complete HTML email arriving in the recipient's inbox
  2. The received email displays score overview, detailed evaluation breakdown, chart image, and data intelligence sections
  3. The received email renders correctly in Gmail (web), Outlook (web), and Apple Mail -- no broken layout, no missing images
  4. The chart appears as an inline image in the email body (not as a downloadable attachment)
  5. SMTP credentials are read from environment variables and the sender display name is configurable
**Plans:** 2/3 plans executed

Plans:
- [ ] 01-01-PLAN.md — SMTP config, schemas, email service with CID images
- [ ] 01-02-PLAN.md — HTML email template with all content sections
- [ ] 01-03-PLAN.md — Router endpoints and main.py wiring

### Phase 2: Core Send Flow
**Goal**: Users can send a dashboard email report through a complete UI flow with clear feedback at every step
**Depends on**: Phase 1
**Requirements**: SEND-01, SEND-02, SEND-06, SEND-07, SEND-08
**Success Criteria** (what must be TRUE):
  1. User can click a "Send Email" button in the DashboardHeader and a send dialog opens
  2. User can enter a recipient email address in the dialog and trigger sending
  3. User sees a loading indicator while the email is being sent
  4. User sees a success confirmation showing the recipient after the email sends
  5. User sees a clear error message if sending fails (e.g., invalid email, SMTP error)
**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD

### Phase 3: Enhanced Send Options
**Goal**: Users have full control over email recipients and content before sending, including preview
**Depends on**: Phase 2
**Requirements**: SEND-03, SEND-04, SEND-05, CONT-07
**Success Criteria** (what must be TRUE):
  1. User can send to multiple recipients (comma-separated or multi-input)
  2. User can add CC and BCC recipients in the send dialog
  3. User can write a custom note/message that appears above the report body in the email
  4. User can preview the HTML email content in the dialog before clicking send
**Plans**: TBD

Plans:
- [ ] 03-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Backend Email Engine | 2/3 | In Progress|  |
| 2. Core Send Flow | 0/? | Not started | - |
| 3. Enhanced Send Options | 0/? | Not started | - |
