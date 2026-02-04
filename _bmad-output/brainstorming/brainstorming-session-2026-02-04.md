---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: []
session_topic: 'Brand Qualification Tool migration - Google Sheets to Web App'
session_goals: 'Architecture decisions within constraints, Migration strategy, Future AI integration planning, All-in-one BD platform vision'
selected_approach: 'AI-Recommended Techniques'
techniques_used: ['First Principles Thinking', 'Morphological Analysis', 'Reverse Brainstorming', 'Cross-Pollination']
ideas_generated: 26
context_file: ''
session_active: false
workflow_completed: true
---

# Brainstorming Session Results

**Facilitator:** Mr. Door
**Date:** 2026-02-04

## Session Overview

**Topic:** Brand Qualification Tool migration - Google Sheets to Web App

**Goals:**
- Architecture decisions within GCP/Firebase/Neon/Polars constraints
- Migration strategy approaches
- Future AI integration touchpoints
- "All-in-one" BD tool feature expansion

### Technical Constraints (Fixed)
- Google Cloud Platform
- Infrastructure as Code (IaC)
- Firebase for hosting
- Neon for database
- Polars for data processing

### Context
Business Development team uses Google Sheets to evaluate/qualify brands as candidates for company services. Current pain points: no persistent storage, new spreadsheets when full (unmaintainable), no scalability, need for AI integration, desire for all-in-one integrated tool.

### Session Setup
- **Approach Selected:** AI-Recommended Techniques
- **Focus Areas:** Systems architecture, migration planning, workflow preservation, future-proofing for AI

## Technique Selection

**Approach:** AI-Recommended Techniques
**Analysis Context:** Brand Qualification Tool migration with focus on architecture, migration strategy, and future vision

### Recommended Technique Sequence

1. **First Principles Thinking** *(creative)* — Strip away Google Sheets mental model, identify fundamental truths about what BD team actually needs for brand qualification
2. **Morphological Analysis** *(deep)* — Systematically map architecture parameters within GCP/Firebase/Neon/Polars constraints, explore all viable combinations
3. **Reverse Brainstorming** *(creative)* — "How could this migration fail?" to build robust migration strategy and risk mitigation
4. **Cross-Pollination** *(creative)* — Draw from successful BD/sales platforms (Salesforce, HubSpot, Notion patterns) for all-in-one and AI integration vision

### AI Rationale
Technical migration project with defined constraints requires structured + deep techniques for architecture decisions. Creative techniques applied strategically for risk identification and future vision. Sequence flows: Fundamentals → Architecture → Risks → Future.

---

## Technique Execution

### Technique 1: First Principles Thinking

**Focus:** Strip away Google Sheets mental model, identify fundamental truths

#### Current System Architecture Discovered:

```
BRAND DATABASE SHEET (Central)
    │ IMPORTRANGE
    ├──▶ Ads Keyword Calculator
    ├──▶ % Discount Check Up
    └──▶ Top SKU Calculator
              │ Copy-Paste
              ▼
        FINAL SCORING SHEET
        ├─ Fashion Template
        └─ Non-Fashion Template
              │
              ▼
        Team Leader Decision
```

#### Fundamental Truths Identified:

| # | Truth | Design Implication |
|---|-------|-------------------|
| 1 | Tool is filter + context provider, not decision-maker | Surface confidence signals, not just scores |
| 2 | Real pain is data management, not data entry | Prioritize history, search, persistence |
| 3 | File upload preferred over copy-paste | Excel parser is core feature |
| 4 | Rules must be explicit and evolvable | Configurable rule engine needed |
| 5 | Migration fidelity first | Recreate calculations exactly before improvements |
| 6 | System fragmented across 4-5 sheets | Consolidation is the "all-in-one" vision |
| 7 | Two scoring templates (Fashion/Non-Fashion) | Category-based conditional logic |
| 8 | Brand Database = central data concept | Natural mapping to Neon database |

#### Ideas Generated:

1. **Upload-First Data Ingestion** - Excel file upload with automatic parsing as primary input method
2. **Explicit Rule Engine** - Scoring rules as configurable data, not hard-coded logic
3. **Persistent Evaluation History** - Every evaluation stored permanently with full context
4. **Migration Fidelity Philosophy** - Recreate before improving, respect BD team's domain expertise

---

### Technique 2: Morphological Analysis

**Focus:** Systematically map architecture parameters within GCP/Firebase/Neon/Polars constraints

#### Architecture Decision Matrix:

| Parameter | Decision | Rationale |
|-----------|----------|-----------|
| **A. Frontend** | Hybrid SPA + Cloud Functions | Anticipates UI iteration, clean separation |
| **B. Backend** | FastAPI on Cloud Run + Firebase Auth | Python-first, decoupled, modern stack |
| **C. Calculator Engine** | Modular now + Rule engine later | Migration fidelity first, evolve second |
| **D. Polars Integration** | Full pipeline (upload + calculations) | Complex formulas need proper data processing |
| **E. File Upload** | Synchronous | 2MB/7K rows is trivial for Polars |
| **F. Rule Configuration** | Hybrid (code + DB thresholds) | Complex logic in code, simple values in DB |
| **G. Template Handling** | Config in database | Fashion/Non-Fashion = parameter sets, not code branches |

#### Architecture Diagram:

```
FRONTEND: SPA (Firebase Hosting) + Firebase Auth SDK
    │ JWT Token
    ▼
BACKEND: FastAPI on Cloud Run
    ├── /upload (Excel → Polars)
    ├── /calculate (Polars engine)
    ├── /brands (CRUD)
    └── /rules (Config management)
    │
    ├── CALCULATORS (Python modules)
    │   ads_keyword.py | discount.py | top_sku.py | scoring.py
    │
    ▼
DATABASE: Neon (Postgres)
    ├── brands (central)
    ├── evaluations (history)
    ├── rules_config (templates: fashion/non-fashion)
    └── upload_history (audit trail)
```

#### Ideas Generated:

5. **Hybrid Frontend** - SPA + Cloud Functions for heavy lifting
6. **Decoupled Python API** - FastAPI on Cloud Run, Firebase Auth for tokens only
7. **FastAPI + Firebase Auth** - Modern Python stack, production-ready
8. **Modular Calculators** - One module per sheet, future rule engine layer
9. **Polars Full Pipeline** - Both file parsing AND calculations
10. **Synchronous Upload** - No async complexity needed for 2MB files
11. **Hybrid Rule Config** - Complex logic in code, thresholds in DB
12. **Template-as-Configuration** - Fashion/Non-Fashion as DB parameter sets

---

### Technique 3: Reverse Brainstorming

**Focus:** "How could this migration fail spectacularly?" - identifying risks proactively

#### Risks Identified:

| # | Risk | Mitigation |
|---|------|------------|
| 1 | Calculation mismatch with original sheets | Test against historical evaluation data |
| 2 | Historical migration requested later | Build import capability now, use as test suite |
| 3 | Big reveal mismatch with BD expectations | Soft launch with team leader first |
| 4 | Silent production errors | Basic observability (Cloud Logging + alerts) |
| 5 | Google Sheets sync failure unnoticed | Show "last synced" timestamp + alert on failure |
| 6 | Scope/expectation mismatch | Write one-pager scope doc before building |
| 7 | Formula migration underestimated (10+ monsters) | Formula-first development in notebook |

#### Key Discovery: Hybrid Architecture

BD team keeps using "Brand Database" Google Sheet for data input. Web app syncs from it:
- Daily automatic sync (Cloud Scheduler)
- On-demand "Sync Now" button
- One-way sync: Sheet → App (never reverse)
- Sheet owns brand data, App owns evaluations

#### Additional Architecture Decisions:

| # | Concept |
|---|---------|
| 13 | Emoji as output formatting only (clean enums in DB) |
| 14 | Structured logging from day 1 |
| 15 | Google Sheets API as input layer (one-way sync) |
| 16 | AI-ready data model (rich history for future features) |

#### Strategic Decisions:

- ✅ Rough MVP in 1 week is acceptable (fallback to sheets exists)
- ✅ Formula-first development approach (prove calculations before infrastructure)
- ✅ Write scope one-pager before building
- ✅ Soft launch with leader before full team reveal

---

### Technique 4: Cross-Pollination

**Focus:** Borrow patterns from successful platforms (Salesforce, Airtable, Retool)

#### Key Discovery: Post-Qualification Pipeline Exists

Brand qualification → Email sent → Meeting scheduled → Outcome
(Currently implicit, potential future "all-in-one" expansion)

#### Patterns Stolen for Current Build (No New Features):

| Pattern | Source | Implementation |
|---------|--------|----------------|
| Schema flexibility | Airtable | JSONB metadata column for future fields |
| Audit trail | Salesforce | Evaluation history + rule version tracking |
| Function > Form | Retool | Ugly MVP is fine, focus on calculation accuracy |

#### Architecture Additions:

| # | Concept |
|---|---------|
| 17 | Flexible evaluation schema (JSONB metadata column) |
| 18 | Score version tracking (which rules produced each score) |

#### Philosophy Addition:

- **Function Over Form for MVP** - Working ugly > Pretty broken. Focus on calculations, not CSS.

---

## Idea Organization and Prioritization

### Theme 1: Architecture Stack (Decided)

| Layer | Decision | Rationale |
|-------|----------|-----------|
| Frontend | SPA on Firebase Hosting | Decoupled, iteratable |
| Backend | FastAPI on Cloud Run | Python-first, Polars-native |
| Auth | Firebase Auth (tokens only) | Simple, decoupled |
| Database | Neon (Postgres) | Project constraint |
| Processing | Polars (full pipeline) | Complex formulas need proper data processing |
| Data Input | Google Sheets API sync | BD team keeps familiar workflow |

### Theme 2: Data Model Design

| Table | Purpose | Ownership |
|-------|---------|-----------|
| brands | Brand data synced from Google Sheet | Sheet is source of truth |
| evaluations | Full evaluation history + JSONB metadata | App-owned |
| rules_config | Template + rule_key + value | App-owned, BD-editable |
| sync_log | Track sync history | App-owned |

Key: Score version tracking - store which rules produced each evaluation.

### Theme 3: Calculator Architecture

```
calculators/
├── ads_keyword.py      # From Ads Keyword Calculator sheet
├── discount.py         # From % Discount Check Up sheet
├── top_sku.py          # From Top SKU Calculator sheet
└── scoring.py          # Final scoring (Fashion/Non-Fashion)
    └── get_rules(template) → pulls thresholds from DB
```

Complex logic in code, simple thresholds in database.

### Theme 4: Migration Strategy

| Phase | Focus | Approach |
|-------|-------|----------|
| Week 1 (MVP) | Formulas + basic flow | Formula-first in notebook, then FastAPI |
| Pre-launch | Validation | Same inputs → same outputs vs historical |
| Launch | Soft launch | Team leader first, then full team |
| Post-launch | Support | Sheets remain as fallback |

### Theme 5: Risk Checklist

**Before Building:**
- [ ] Write one-pager scope doc, share with BD leader
- [ ] Start with hardest formula in Jupyter notebook
- [ ] Set up basic Cloud Logging from day 1

**Before Launch:**
- [ ] Test all calculations against historical evaluations
- [ ] Show "last synced" timestamp in UI
- [ ] Demo to team leader privately first

---

## Action Plan: Week 1 MVP

### Day 1-2: Prove the Hard Part
- [ ] Export historical evaluation data from sheets
- [ ] Migrate nastiest formula in Jupyter notebook
- [ ] Verify output matches original
- [ ] Repeat for remaining formulas

### Day 3-4: Wrap in API
- [ ] FastAPI skeleton on Cloud Run
- [ ] Neon database with basic schema
- [ ] /sync endpoint (Google Sheets API)
- [ ] /calculate endpoint (formula modules)
- [ ] Test with real data

### Day 5-6: Basic UI
- [ ] Simple SPA (function over form)
- [ ] Upload/sync flow
- [ ] Evaluation form
- [ ] Results display
- [ ] History list

### Day 7: Validate + Prep Launch
- [ ] Run historical data through system
- [ ] Compare outputs, fix discrepancies
- [ ] Demo to team leader

---

## Session Summary

### Key Achievements

- **26 ideas generated** across 4 techniques
- **Architecture fully decided** within GCP/Firebase/Neon/Polars constraints
- **Migration strategy defined** with formula-first approach
- **Risk mitigations identified** with actionable checklist
- **Week 1 MVP plan** with day-by-day breakdown

### Session Insights

1. **Real problem is data management** - not the spreadsheet itself
2. **Formulas are the product** - everything else is plumbing
3. **BD team workflow partly unchanged** - they keep Brand Database sheet
4. **One-way sync is key** - Sheet → App, clear ownership
5. **10+ monster formulas = critical path** - this is where time goes

### Breakthrough Discovery

The architecture simplified when the Google Sheet stays as input. Not replacing data entry - just calculation + storage. This reduces adoption friction significantly.

### Creative Facilitation Notes

- User demonstrated strong pragmatic thinking (MVP focus, no feature creep)
- Clear technical background enabled deep architecture discussions
- "Rough MVP is OK" mindset with fallback safety net is healthy approach
- Formula-first development recommendation well-received
