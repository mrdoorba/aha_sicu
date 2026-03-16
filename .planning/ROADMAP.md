# Roadmap: THB Marketplace Expansion

## Overview

This project extends the AHA SICU evaluation system from single-marketplace (IDR/Indonesia) to dual-marketplace (IDR and THB/Thailand). The work proceeds in four phases: first establishing the database schema foundation with marketplace as an evaluation-level attribute, then wiring the scoring engine to select rules by marketplace, then hardening CSV parsing for Thai number formats, and finally surfacing marketplace context throughout the frontend. Each phase delivers a verifiable capability and the phases are strictly ordered by dependency.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Data Model Foundation** - Evaluation stores marketplace; scoring rules support IDR and THB side-by-side
- [ ] **Phase 2: Scoring Engine Marketplace Awareness** - Scoring reads marketplace from evaluation and selects correct rule set
- [ ] **Phase 3: CSV THB Parsing** - Thai number formats parsed correctly without corrupting IDR parsing
- [ ] **Phase 4: Frontend Currency and Marketplace UI** - Rules page, evaluation page, and currency display reflect selected marketplace

## Phase Details

### Phase 1: Data Model Foundation
**Goal**: The database carries marketplace as a first-class dimension on evaluations and scoring rules, with all existing IDR data preserved and THB thresholds seeded
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03
**Success Criteria** (what must be TRUE):
  1. A user creating an evaluation can store a marketplace selection (ID or TH) against that evaluation record
  2. The scoring rules table contains both IDR and THB rows for every rule template, queryable by marketplace
  3. All existing evaluations and brands remain fully functional with no data loss after migration
  4. THB threshold values exist as reasonable starting values (derived from IDR conversion) and are editable by admins
**Plans:** 2 plans
Plans:
- [ ] 01-01-PLAN.md — Schema migration + marketplace constants (marketplace column on 3 tables, THB rules seed, app/core/marketplace.py)
- [ ] 01-02-PLAN.md — Query layer + service + API updates (marketplace-aware queries, rules API ?marketplace= param, generate_score wiring)

### Phase 2: Scoring Engine Marketplace Awareness
**Goal**: The scoring engine reads marketplace from the evaluation and produces scores against the correct rule set, with all currency labels correct in output messages
**Depends on**: Phase 1
**Requirements**: SCORE-01, SCORE-02, SCORE-03
**Success Criteria** (what must be TRUE):
  1. Running a TH evaluation scores the brand against THB thresholds, not IDR thresholds
  2. Running an ID evaluation continues to score against IDR thresholds with no regression
  3. Scoring output messages show "THB" currency labels for TH evaluations and "IDR" for ID evaluations
  4. All revenue-related score components use the marketplace-specific threshold values
**Plans**: TBD

### Phase 3: CSV THB Parsing
**Goal**: Uploading Shopee Thailand CSV files produces correct numeric values throughout the evaluation pipeline
**Depends on**: Phase 1
**Requirements**: CSV-01, CSV-02
**Success Criteria** (what must be TRUE):
  1. A Thai CSV with prices like "1,250.50" parses to the value 1250.50, not 125050
  2. An Indonesian CSV with prices like "1.250,50" continues to parse to 1250.50 with no regression
  3. Both ID and TH CSVs produce valid evaluation inputs that the scoring engine can process
**Plans**: TBD

### Phase 4: Frontend Currency and Marketplace UI
**Goal**: Users can select marketplace on the evaluation page, admins can manage IDR and THB thresholds separately on the rules page, and all currency values display in the correct format
**Depends on**: Phase 2
**Requirements**: RULES-01, RULES-02, EVAL-01, EVAL-02, EVAL-03
**Success Criteria** (what must be TRUE):
  1. On the evaluation page, a user can select "Indonesia (IDR)" or "Thailand (THB)" before running an evaluation
  2. Currency fields on the evaluation page display the correct currency code (IDR or THB) based on the selected marketplace
  3. Evaluation results show revenue values formatted correctly for the marketplace (IDR: period-thousands comma-decimal; THB: comma-thousands period-decimal)
  4. The rules page shows separate IDR and THB threshold tabs; editing a THB threshold does not change the IDR threshold
  5. An admin can update a THB threshold value and the change persists independently from IDR thresholds
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4
(Phase 3 depends only on Phase 1 and may be developed in parallel with Phase 2)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Model Foundation | 0/2 | Planning complete | - |
| 2. Scoring Engine Marketplace Awareness | 0/TBD | Not started | - |
| 3. CSV THB Parsing | 0/TBD | Not started | - |
| 4. Frontend Currency and Marketplace UI | 0/TBD | Not started | - |
