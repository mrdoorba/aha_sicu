---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish']
inputDocuments:
  - '_bmad-output/planning-artifacts/product-brief-BMAD-Method-2026-02-04.md'
  - '_bmad-output/brainstorming/brainstorming-session-2026-02-04.md'
documentCounts:
  briefs: 1
  research: 0
  brainstorming: 1
  projectDocs: 0
classification:
  projectType: web_app
  domain: internal_business_tools
  complexity: low
  projectContext: greenfield
  industryContext: e-commerce enabler
workflowType: 'prd'
date: 2026-02-04
author: Mr. Door
---

# Product Requirements Document - Store ICU

**Author:** Mr. Door
**Date:** 2026-02-04

## Executive Summary

### Product Vision

**Store ICU (Store Internal Check Up)** is a web application that modernizes the Business Development team's brand qualification process. It replaces fragmented Google Sheets workflows with a professional, persistent system while preserving the trusted calculation logic the team already relies on.

### Core Value Proposition

**Same trusted process, properly built.**

### Problem Statement

The BD team evaluates and qualifies brands as candidates for company e-commerce enablement services using a fragmented Google Sheets system. Data has no persistent storage, spreadsheets become unmaintainable when full, and the workflow relies on tedious copy-paste between multiple sheets.

### Solution

Store ICU is a web application that:
- Syncs brand data from two existing Google Sheets — VP sheet (primary brand list) and 1st Meeting sheet (supplementary data) — BD team keeps familiar data entry
- Accepts CSV and Excel file uploads and manual data input directly in the app
- Replicates all calculator logic exactly (Ads Keyword, Discount Check, Top SKU, Scoring)
- Stores all evaluations permanently in a searchable database
- Provides configurable scoring rules without code changes

### Target Users

| User | Count | Role |
|------|-------|------|
| **BD Team Leader** | 1 | Reviews evaluations, makes final qualification decisions, searches historical data |
| **BD Team Members** | 3 | Perform daily brand evaluations, upload data, run calculations |
| **System Owner** | 1 | Monitors sync health, manages rule configuration |

### Key Differentiators

| Differentiator | Description |
|----------------|-------------|
| **Migration Fidelity** | Same trusted calculations, exact same results |
| **Persistent History** | Every evaluation stored forever, fully searchable |
| **Configurable Rules** | Scoring thresholds editable without code deployment |
| **Unified Data Flow** | Brand data syncs from two Google Sheets (VP + Meeting); Excel uploads and manual input go directly to app |

## Success Criteria

### User Success

**Primary Indicator:** BD team uses Store ICU instead of Google Sheets for brand evaluations.

**Success Signals:**
- Team stops creating new spreadsheets for evaluations
- Evaluations are stored in the system
- Team can search and find past evaluations when needed
- No complaints about calculation accuracy

**Aha Moment:** First time they search for a past evaluation and find it instantly.

### Business Success

**3-Month Objective:** It works and they use it.

- Tool is deployed and functional
- BD team has adopted it for daily workflow
- Google Sheets fallback is no longer needed

### Technical Success

**Migration Fidelity Requirement:** 100% calculation match with original Google Sheets logic.

- Ads Keyword Calculator: exact match
- Discount Check Calculator: exact match
- Top SKU Calculator: exact match
- Final Scoring (Fashion/Non-Fashion): exact match

**Validation Method:** Test all calculations against historical evaluation data before launch.

### Measurable Outcomes

| Metric | Target |
|--------|--------|
| Calculation accuracy | 100% match with original sheets |
| Adoption timeline | ASAP after deployment |
| Data persistence | All evaluations stored permanently |
| Search functionality | Past evaluations retrievable |

## Product Scope

### MVP (Phase 1)

| Feature | Description |
|---------|-------------|
| Google Sheets Sync | One-way sync from two Google Sheets — VP (primary brand list) and 1st Meeting (supplementary) — daily auto + on-demand |
| Excel File Upload | Upload data files (CSV and Excel) for calculator processing via Polars |
| Ads Keyword Calculator | Replicate existing spreadsheet logic exactly |
| Discount Check Calculator | Replicate existing spreadsheet logic exactly |
| Top SKU Calculator | Replicate existing spreadsheet logic exactly |
| Final Scoring | Fashion and Non-Fashion templates |
| Configurable Rule Engine | Scoring thresholds and rules editable without code changes |
| Evaluation Storage | All evaluations saved permanently to Neon database |
| Evaluation History | Search and view past evaluations |
| Real-time Updates | Live sync status, evaluation updates without refresh |
| Basic UI | Functional web interface — function over form |

### Phase 2 (Growth)

- Advanced reporting and analytics dashboard
- Post-qualification pipeline (email tracking, meeting scheduling, outcomes)

### Phase 3 (Vision)

**All-in-One BD Platform:**
- AI-powered brand recommendations and scoring insights
- Full post-qualification workflow management
- Integration with other company systems

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Technical:** Complex formula migration | Formula-first development; validate against historical data before building API |
| **Adoption:** Team prefers old workflow | Soft launch with team leader; keep Google Sheets as fallback during transition |
| **Data:** Sync failures go unnoticed | Display "last synced" timestamp prominently; alert on sync errors |
| **Scope:** Rule engine adds complexity | Keep rule engine simple — editable thresholds in DB, not a full DSL |

## User Journeys

### Journey 1: BD Team Member — Daily Brand Evaluation

**Persona:** Rina, BD Team Member

**Situation:** Rina evaluates 5-10 brands daily to determine if they're good candidates for the company's e-commerce enablement services.

**The Journey:**

1. **Brand Selection:** Rina opens Store ICU. The brand list is already there (synced from Brand Database sheet). She picks a brand from the list.

2. **Data Entry:** She enters manual values that can't be pulled automatically — marketplace-specific metrics or qualitative notes.

3. **Excel Upload:** She uploads the Excel file containing the brand's data. Polars processes it.

4. **Automatic Calculation:** The system runs all calculators automatically:
   - Ads Keyword Calculator → results appear
   - Discount Check Calculator → results appear
   - Top SKU Calculator → results appear

5. **Final Scoring:** Calculator results combine with her manual inputs. She selects the scoring template (Fashion or Non-Fashion). Final score is generated.

6. **Save:** Evaluation is saved permanently. She can edit inputs if needed (upsert). She moves to the next brand.

**Capabilities Revealed:** FR1-FR22, FR27

---

### Journey 2: Team Leader — Historical Lookup & Review

**Persona:** Pak Budi, BD Team Leader

**Situation:** A brand reaches out saying "you contacted us 3 months ago." Pak Budi needs to find that evaluation quickly.

**The Journey:**

1. **Search:** Pak Budi opens Store ICU and searches by partial brand name or filters by date range/category.

2. **Review:** The evaluation appears with full history — scores, calculator results, who evaluated it, when.

3. **Action:** He has the context needed to continue the conversation with the brand.

**Capabilities Revealed:** FR28-FR33

---

### Journey 3: System Owner — Sync & Health Check

**Persona:** Mr. Door, Technical Owner

**Situation:** Monday morning. Need to ensure the system is healthy and Brand Database is synced.

**The Journey:**

1. **Status Check:** Dashboard shows "Last synced: 2 hours ago" — automatic sync is working.

2. **Manual Sync:** If needed, hit "Sync Now" to pull latest brand data.

3. **Rule Management:** Review or adjust scoring thresholds if needed.

**Capabilities Revealed:** FR1-FR4, FR23-FR26, FR34

## Technical Architecture

### Stack Overview

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | React 19 + Vite 7 + Tailwind v4 + shadcn/ui (Firebase Hosting) | Modern UI, GCP ecosystem |
| **Backend** | FastAPI on Cloud Run | Python-first for Polars integration |
| **Database** | Neon (PostgreSQL) | Project constraint, persistent storage |
| **Auth** | Firebase Auth | Token-based, decoupled |
| **Data Processing** | Polars | Fast Excel parsing and calculations |

### Browser Support

| Browser | Support Level |
|---------|---------------|
| Chrome (latest) | Full support |
| Firefox (latest) | Full support |
| Safari/Edge/IE | Not required |

### Design Constraints

- **Primary viewport:** Desktop (1024px+ width)
- **Offline support:** Not required
- **SEO:** Not applicable (internal tool)
- **Accessibility:** Standard web accessibility (semantic HTML, keyboard navigation)

## Functional Requirements

*Each FR traces back to user journeys documented above.*

### Brand Data Management

- **FR1:** System can sync brand data from two Google Sheets (VP and 1st Meeting) automatically (daily)
- **FR2:** BD team member can trigger manual sync of brand data on-demand
- **FR3:** BD team member can view current sync status (last synced timestamp)
- **FR4:** System can display sync errors when sync fails
- **FR5:** BD team member can browse and select a brand from the synced brand list to evaluate

### Data Input & Upload (Per Brand)

- **FR6:** BD team member can upload data files (CSV and Excel) for a specific brand's calculator processing — multiple files per evaluation, each routed to its target calculator
- **FR7:** System can parse uploaded data files (CSV and Excel) using Polars
- **FR8:** BD team member can enter manual data values for a specific brand, organized by scoring system categories (~40+ fields across operational, business, content, visitors, promo, ads, campaign, competition, stock, and discount sections)
- **FR9:** System can validate uploaded file format and per-calculator column schema before processing
- **FR10:** BD team member can re-upload Excel files for a brand (upsert — replaces previous upload)
- **FR11:** BD team member can edit previously entered manual data for a brand

### Calculators (Per Brand)

- **FR12:** System can execute Ads Keyword Calculator using CPC Ad Report CSV and Keyword Placement Report CSV, producing text-based ad analysis with overview, type breakdown, recommendations, top/bottom performers, and flags
- **FR13:** System can execute Discount Check Calculator using Order Export data, producing discount percentage analysis, range, voucher/bundle percentages, and fake discount detection flag
- **FR14:** System can execute Top SKU Calculator using Order Export and Mass Update data, producing top 20% selling SKU tables (with revenue and stock) and average stock metric
- **FR15:** System can execute applicable calculators when their required input files become available for a brand
- **FR16:** BD team member can view individual calculator results for a brand — text summaries with flags (Ads Keyword), ranked product tables (Top SKU), and discount analysis text (Discount Check)
- **FR17:** System can combine calculator results with manual input data for a brand using the 75-row scoring system template (Fashion/Non-Fashion variants) to produce final score, category breakdowns, and output messages
- **FR18:** System can recalculate results when data is updated for a brand

### Final Scoring (Per Brand)

- **FR19:** BD team member can select scoring template (Fashion or Non-Fashion) for a brand
- **FR20:** System can generate final score for a brand based on calculator results and manual inputs
- **FR21:** System can display final score with breakdown of contributing factors for a brand
- **FR22:** System can recalculate final score when underlying data changes

### Rule Configuration

- **FR23:** System owner can view current scoring thresholds and rules
- **FR24:** System owner can modify scoring thresholds without code deployment
- **FR25:** System can store rule configurations in database
- **FR26:** System can apply configured rules during score calculation

### Evaluation Storage & History

- **FR27:** System can save completed evaluations permanently (one evaluation per brand per session)
- **FR28:** BD team member can search evaluations by brand name (partial match)
- **FR29:** BD team member can filter evaluations by date range
- **FR30:** BD team member can filter evaluations by category (Fashion/Non-Fashion)
- **FR31:** BD team member can view full evaluation details (scores, inputs, who evaluated, when)
- **FR32:** System can track which user performed each evaluation
- **FR33:** System can maintain evaluation history (previous evaluations for same brand are preserved)

### Real-Time Updates

- **FR34:** System can update sync status in real-time without page refresh
- **FR35:** System can display new evaluations to other users without page refresh

### Authentication & Access

- **FR36:** BD team member can authenticate using Firebase Auth
- **FR37:** System can restrict access to authenticated users only

## Non-Functional Requirements

### Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR1 | Page initial load | < 3 seconds |
| NFR2 | Excel file upload + processing (2MB) | < 5 seconds |
| NFR3 | Calculator execution | < 2 seconds |
| NFR4 | Search results | < 1 second |
| NFR5 | Real-time update propagation | < 500ms |

### Security

| ID | Requirement |
|----|-------------|
| NFR6 | Authentication required for all access (Firebase Auth) |
| NFR7 | API endpoints protected by JWT validation |
| NFR8 | Database credentials never exposed to frontend |
| NFR9 | HTTPS enforced for all connections |
| NFR10 | Google Sheets API credentials secured (service account) |

### Integration

| ID | Requirement |
|----|-------------|
| NFR11 | Google Sheets sync handles API rate limits gracefully (retry with backoff) |
| NFR12 | Sync failures logged with actionable error messages |
| NFR13 | Excel file parsing handles .xlsx and .xls formats |

### Reliability

| ID | Requirement |
|----|-------------|
| NFR14 | No data loss on evaluation save (database transaction integrity) |
| NFR15 | Sync status accurately reflects last successful sync |
| NFR16 | System recovers gracefully from temporary failures |
| NFR17 | Evaluation history is immutable (past evaluations cannot be accidentally deleted) |
