---
stepsCompleted: [1, 2, 3, 4, 5, 6]
workflowComplete: true
inputDocuments:
  - '_bmad-output/brainstorming/brainstorming-session-2026-02-04.md'
date: 2026-02-04
author: Mr. Door
---

# Product Brief: Store ICU

## Executive Summary

**Store ICU (Store Internal Check Up)** is a web application that modernizes the Business Development team's brand qualification process. It replaces fragmented Google Sheets workflows with a professional, persistent system while preserving the trusted calculation logic the team already relies on.

The core value proposition: **Same trusted process, properly built.**

---

## Core Vision

### Problem Statement

The BD team evaluates and qualifies brands as candidates for company services using a fragmented Google Sheets system. Data has no persistent storage, spreadsheets become unmaintainable when full, and the workflow relies on tedious copy-paste between multiple sheets. The result is lost evaluation history, inefficient processes, and an unprofessional toolset.

### Problem Impact

- **No historical record** - Past evaluations are lost or buried in abandoned spreadsheets
- **Tedious manual work** - Copy-paste workflows waste BD team time
- **Unprofessional perception** - The tooling doesn't reflect the quality of the team's work
- **No scalability** - System breaks down as evaluation volume grows

### Why Existing Solutions Fall Short

Google Sheets served as a quick solution but was never designed for persistent data management. It lacks:
- Permanent storage with searchable history
- Centralized evaluation records
- Professional interface appropriate for business operations
- Foundation for future AI integration

### Proposed Solution

Store ICU is a web application that:
- **Syncs from existing Brand Database Google Sheet** - BD team keeps familiar data entry for brand data
- **Replicates all calculator logic exactly** - Ads Keyword, Discount Check, Top SKU, Scoring (Fashion/Non-Fashion)
- **Stores all evaluations permanently** - Searchable history in Neon database
- **Provides modern professional UI** - Clean interface hosted on Firebase

### Key Differentiators

| Differentiator | Description |
|----------------|-------------|
| **Migration Fidelity** | Same trusted calculations, exact same results - no surprises |
| **Persistent History** | Every evaluation stored forever, fully searchable |
| **Professional Interface** | Modern web app replaces spreadsheet chaos |
| **Unified Data Entry** | Excel upload + direct input in one place, Brand Database syncs from Google Sheets |
| **Future-Ready Architecture** | Built on GCP/FastAPI/Neon for AI integration when needed |

---

## Target Users

### Primary Users

**BD Team (4 people)**

| Role | Description |
|------|-------------|
| **Team Leader** | Reviews evaluations, makes final qualification decisions, needs visibility into team's work and historical data |
| **BD Team Members (3)** | Perform daily brand evaluations - upload Excel files, run calculations, record scores. Currently suffer through copy-paste workflows and lost data |

**User Context:**
- Small, focused team that requested this tool
- Already familiar with the evaluation logic (they built the spreadsheets)
- Primary pain: data management chaos, not calculation complexity
- Success = same trusted results, properly stored, professional interface

### Secondary Users

N/A - This is a focused internal tool for the BD team only.

### User Journey

| Stage | Experience |
|-------|------------|
| **Discovery** | Internal deployment: "Here is the tool you requested" |
| **Onboarding** | Minimal - team already knows the evaluation process, just new interface |
| **Core Usage** | Upload Excel → Run calculations → View/store results → Search history |
| **Aha Moment** | First time they search for a past evaluation and find it instantly |
| **Long-term** | Evaluations become searchable institutional knowledge |

---

## Success Metrics

### User Success

**Primary Success Indicator:** BD team uses Store ICU instead of Google Sheets for brand evaluations.

**Success Signals:**
- Team stops creating new spreadsheets for evaluations
- Evaluations are being stored in the system
- Team can search and find past evaluations when needed
- No complaints about calculation accuracy (migration fidelity achieved)

### Business Objectives

**3-Month Objective:** It works and they use it.

This is an internal tool built at the team's request. Success is straightforward:
- Tool is deployed and functional
- BD team has adopted it for daily workflow
- Google Sheets fallback is no longer needed

### Key Performance Indicators

N/A - This is a focused internal tool. Formal KPIs are unnecessary overhead.

**Informal tracking (if curious):**
- Number of evaluations stored (shows adoption)
- Last sync timestamp (shows system health)

---

## MVP Scope

### Core Features

| Feature | Description |
|---------|-------------|
| **Google Sheets Sync** | One-way sync from Brand Database sheet (daily auto + on-demand) |
| **Excel File Upload** | Upload Excel files for calculator processing via Polars |
| **Ads Keyword Calculator** | Replicate existing spreadsheet logic exactly |
| **Discount Check Calculator** | Replicate existing spreadsheet logic exactly |
| **Top SKU Calculator** | Replicate existing spreadsheet logic exactly |
| **Final Scoring** | Fashion and Non-Fashion templates with configurable thresholds |
| **Evaluation Storage** | All evaluations saved permanently to Neon database |
| **Evaluation History** | Search and view past evaluations |
| **Basic UI** | Functional web interface - function over form |

### Out of Scope for MVP

| Deferred Feature | Rationale |
|------------------|-----------|
| **AI Integration** | Future capability - architecture is ready, not needed for MVP |
| **Configurable Rule Engine** | Complex logic in code first, thresholds in DB - full configurability later |
| **Post-Qualification Pipeline** | Email/meeting tracking is future "all-in-one" expansion |
| **Advanced Reporting** | Basic history search is sufficient for MVP |
| **Pretty UI** | Function over form - working ugly beats pretty broken |

### MVP Success Criteria

- Calculations match original Google Sheets exactly (migration fidelity)
- BD team uses Store ICU instead of spreadsheets
- All evaluations stored and searchable

### Future Vision

**All-in-One BD Platform**

Store ICU evolves from a brand qualification tool into a comprehensive Business Development platform:
- AI-powered brand recommendations and scoring insights
- Post-qualification pipeline (email tracking, meeting scheduling, outcomes)
- Configurable rule engine for non-technical users
- Advanced analytics and reporting dashboard
- Integration with other company systems

