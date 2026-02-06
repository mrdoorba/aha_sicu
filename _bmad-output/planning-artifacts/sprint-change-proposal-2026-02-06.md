# Sprint Change Proposal — 2026-02-06

**Project:** Store ICU
**Author:** Mr. Door
**Date:** 2026-02-06
**Status:** Approved
**Change Scope:** Minor — Direct Adjustment (artifact updates + one setup task)

---

## 1. Issue Summary

Three categories of changes were implemented during Epic 1 (Stories 1.1, 1.3) and Epic 2 (Story 2.1) that diverge from the original planning artifacts:

### Change 1: Two-Sheet Data Model (VP + Meeting)
- **Trigger:** Story 2.1 — Google Sheets Sync Backend
- **Type:** New requirement emerged during implementation
- **Description:** The original architecture assumed one "Brand Database" Google Sheet. During Story 2.1, it was discovered that brand data comes from TWO separate sheets (VP and 1st Meeting). The database schema was redesigned from a single `brands` table to `brand_vp_data` (primary) + `brand_meeting_data` (supplementary).
- **Evidence:** Git commit `a53dd9d`, migrations 004-005, dual config in `config.py`

### Change 2: No shadcn/ui Component Library (to be restored)
- **Trigger:** Story 1.1 — Initialize Project Structure
- **Type:** Misalignment between planning and implementation
- **Description:** The UX Design Specification designates shadcn/ui as the design system (14+ components), but no story ever included it as a task. Combined with an unplanned Tailwind v4 upgrade, pure Tailwind was used. **Decision: Add shadcn/ui before Story 2.3.**
- **Evidence:** `package.json` has no shadcn dependencies; Epic 1 retro notes Tailwind v4 surprise

### Change 3: Major Tech Stack Version Bumps
- **Trigger:** Story 1.1 — Initialize Project Structure
- **Type:** Technical evolution during implementation
- **Description:** Vite scaffolding pulled significantly newer versions than planned. All working and tested.
- **Details:**

| Component | Planned | Actual |
|-----------|---------|--------|
| React | 18.x | 19.2.0 |
| Vite | 5.x | 7.2.4 |
| Tailwind CSS | 3.x | 4.1.18 |
| TypeScript | 5.x | 5.9.3 |
| Vitest | — | 4.0.18 |

---

## 2. Impact Analysis

### Epic Impact

| Epic | Status | Impact Level | Details |
|------|--------|-------------|---------|
| Epic 1 | Done | None | Complete. Historical record unchanged. |
| Epic 2 | In Progress | Medium | Stories 2.2-2.5 need dual-table model updates. shadcn/ui setup added to 2.3. |
| Epic 3 | Backlog | High | All 10 stories reference `brands(id)` FK — needs updating to `brand_vp_data(id)`. |
| Epic 4 | Backlog | Medium | Search/filter needs to reference `brand_vp_data`. Meeting data as optional enrichment. |
| Epic 5 | Backlog | Low | Rules are brand-independent. Version refs only. |

### Artifact Conflicts

| Artifact | Conflicts Found | Changes Required |
|----------|----------------|-----------------|
| PRD | 4 sections reference single "Brand Database" sheet | 4 text updates |
| Architecture | Schema, sync design, versions outdated | 5 updates (schema rewrite, sync description, versions) |
| UX Design Spec | Design system section references shadcn/ui setup | 2 updates (Tailwind v4 note, brand data references) |
| Epics | FK references, story ACs, FR coverage map | 4 bulk updates across Epic 2-4 stories |

### Technical Impact

- **Database:** Schema change already implemented (migrations 004-005). No further migration needed.
- **Backend code:** Sync service already handles dual sheets. No code changes needed.
- **Frontend code:** No changes needed for existing code. shadcn/ui will be added as new setup.
- **Infrastructure:** No changes needed.

---

## 3. Recommended Approach

### Selected: Direct Adjustment

Update planning artifacts to match implemented reality and prepare remaining stories for the new data model. No rollbacks, no scope reduction.

### Rationale

| Factor | Assessment |
|--------|-----------|
| Implementation effort | Low — update artifact text, add shadcn/ui setup task |
| Timeline impact | Negligible — no stories restarted or removed |
| Technical risk | Low — changes align with working code |
| Team momentum | Preserved — no rollbacks, no scope cuts |
| Long-term sustainability | Improved — artifacts match reality |
| Business value | Unchanged — all MVP features still delivered |

### Alternatives Considered

| Option | Verdict | Why |
|--------|---------|-----|
| Rollback to single brands table | Rejected | Doesn't match business reality (two sheets exist) |
| Skip shadcn/ui entirely | Rejected | Would slow UI development, repeat accessibility gaps |
| Downgrade tech versions | Rejected | High regression risk for zero benefit |
| MVP scope reduction | Unnecessary | All features still deliverable |

---

## 4. Detailed Change Proposals

### 4.1 PRD Updates (4 edits)

**Edit 1 — Solution description:**
- OLD: "Syncs brand data from the existing Brand Database Google Sheet"
- NEW: "Syncs brand data from two existing Google Sheets — VP sheet (primary brand list) and 1st Meeting sheet (supplementary data)"

**Edit 2 — Key Differentiators:**
- OLD: "Brand Database syncs from Google Sheets"
- NEW: "Brand data syncs from two Google Sheets (VP + Meeting)"

**Edit 3 — MVP Scope:**
- OLD: "One-way sync from Brand Database sheet"
- NEW: "One-way sync from two Google Sheets — VP (primary brand list) and 1st Meeting (supplementary)"

**Edit 4 — FR1 + Tech Stack:**
- FR1 OLD: "sync brand data from Google Sheets Brand Database"
- FR1 NEW: "sync brand data from two Google Sheets (VP and 1st Meeting)"
- Tech stack: Add "React 19 + Vite 7 + Tailwind v4 + shadcn/ui" to frontend row

### 4.2 Architecture Updates (5 edits)

**Edit 1 — Database schema:** Replace `brands` table definition with `brand_vp_data` + `brand_meeting_data` tables. Document VP as primary brand source, Meeting as supplementary.

**Edit 2 — Sync service:** Update external dependencies, module boundaries, and integration points to reference dual-sheet sync with `sheets_client.py`.

**Edit 3 — Tech versions:** Pin TypeScript 5.9, Vite 7, Tailwind v4. Add shadcn/ui as UI component library decision.

**Edit 4 — Downstream FKs:** Update all planned table schemas (brand_uploads, evaluation_inputs, calculator_results, evaluations) to reference `brand_vp_data(id)` instead of `brands(id)`.

**Edit 5 — Sync status schema:** Add `sync_details` JSONB column and document dual-sheet configuration pattern.

### 4.3 UX Design Spec Updates (2 edits)

**Edit 1 — Design system:** Add Tailwind v4 compatibility note to shadcn/ui section. Add setup timing (before Story 2.3).

**Edit 2 — Brand data references:** Clarify brand list comes from VP sheet, Meeting data enriches when available.

### 4.4 Epics Updates (4 bulk edits)

**Edit 1 — Story 2.1:** Update story description and schema to match implemented dual-sheet model.

**Edit 2 — Story 2.3:** Add shadcn/ui setup as pre-requisite task. Update brand list to reference VP data. Add per-sheet sync status display.

**Edit 3 — Epic 2-3 bulk:** Update FR coverage map, epic description, all FK references in Stories 3.2/3.3/3.4/3.10 to `brand_vp_data(id)`.

**Edit 4 — Epic 4:** Update Stories 4.1/4.2/4.5 to reference `brand_vp_data` for search/filter/detail views.

---

## 5. Implementation Handoff

### Change Scope Classification: Minor

All changes are documentation updates + one setup task. No architectural rework required.

### Action Plan

| # | Action | Priority | Owner | Status |
|---|--------|----------|-------|--------|
| 1 | Apply PRD text updates (4 edits) | P1 | PM/PO | Pending |
| 2 | Apply Architecture updates (5 edits) | P1 | Architect | Pending |
| 3 | Apply UX spec updates (2 edits) | P1 | UX | Pending |
| 4 | Apply Epics updates (4 bulk edits) | P1 | SM | Pending |
| 5 | Setup shadcn/ui in frontend | P1 | Dev Team | Before Story 2.3 |

### Success Criteria

- [ ] All 15 edit proposals applied to planning artifacts
- [ ] Artifacts consistent with implemented codebase
- [ ] shadcn/ui initialized and working before Story 2.3 begins
- [ ] No references to old `brands` table remain in backlog stories
- [ ] sprint-status.yaml updated if needed

### Next Steps

1. Apply all approved edits to planning artifacts
2. Continue Epic 2 with updated stories (Story 2.2 next)
3. Initialize shadcn/ui as pre-requisite for Story 2.3
4. Epic 3+ stories are ready with correct schema references

---

Author: Mr. Door
