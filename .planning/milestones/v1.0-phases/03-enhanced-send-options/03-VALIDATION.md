---
phase: 3
slug: enhanced-send-options
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-06
validated: 2026-03-06
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest 4.x (frontend), Pytest 9.x (backend) |
| **Config file** | `frontend/vite.config.ts` (test section), `backend/pyproject.toml` |
| **Quick run command** | `cd frontend && npx vitest run src/components/dashboard/ && cd ../backend && uv run pytest tests/unit/email/ -x` |
| **Full suite command** | `cd frontend && npx vitest run && cd ../backend && uv run pytest -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npx vitest run src/components/dashboard/ && cd ../backend && uv run pytest tests/unit/email/ -x`
- **After every plan wave:** Run `cd frontend && npx vitest run && cd ../backend && uv run pytest -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | SEND-03 | unit | `cd frontend && npx vitest run src/components/dashboard/EmailChipInput.test.tsx` | ✅ | ✅ green |
| 03-01-02 | 01 | 1 | SEND-03 | unit | `cd backend && uv run pytest tests/unit/email/test_service.py -x -k multi` | ✅ | ✅ green |
| 03-01-03 | 01 | 1 | SEND-04 | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx` | ✅ | ✅ green |
| 03-01-04 | 01 | 1 | SEND-04 | unit | `cd backend && uv run pytest tests/unit/email/test_service.py -x -k cc` | ✅ | ✅ green |
| 03-01-05 | 01 | 1 | SEND-05 | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx` | ✅ | ✅ green |
| 03-01-06 | 01 | 1 | SEND-05 | unit | `cd backend && uv run pytest tests/unit/email/test_template.py -x -k note` | ✅ | ✅ green |
| 03-01-07 | 01 | 1 | CONT-07 | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx` | ✅ | ✅ green |
| 03-01-08 | 01 | 1 | CONT-07 | unit | `cd backend && uv run pytest tests/unit/email/test_service.py -x -k preview` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Email preview renders correctly in iframe | CONT-07 | Visual rendering in iframe can't be fully automated | Open dialog, expand preview, verify images and note display |
| BCC recipients not visible to other recipients | SEND-04 | Requires actual email delivery inspection | Send test email with BCC, check received email headers |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated

---

## Validation Audit 2026-03-06

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

All 8 task requirements have automated test coverage. Backend: 96 tests passing. Frontend dashboard: 50 tests passing.
