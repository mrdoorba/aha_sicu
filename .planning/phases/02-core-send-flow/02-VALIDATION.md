---
phase: 2
slug: core-send-flow
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest ^4.0.18 + @testing-library/react ^16.3.2 |
| **Config file** | `frontend/vite.config.ts` (test section) |
| **Quick run command** | `cd frontend && npx vitest run --reporter=verbose` |
| **Full suite command** | `cd frontend && npx vitest run` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npx vitest run --reporter=verbose`
- **After every plan wave:** Run `cd frontend && npx vitest run && npm run lint && tsc --noEmit`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | SEND-01 | unit | `cd frontend && npx vitest run src/components/dashboard/DashboardHeader.test.tsx -x` | No — W0 | pending |
| 02-01-02 | 01 | 1 | SEND-02 | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx -x` | No — W0 | pending |
| 02-01-03 | 01 | 1 | SEND-06 | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx -x` | No — W0 | pending |
| 02-01-04 | 01 | 1 | SEND-07 | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx -x` | No — W0 | pending |
| 02-01-05 | 01 | 1 | SEND-08 | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx -x` | No — W0 | pending |

*Status: pending · green · red · flaky*

---

## Wave 0 Requirements

- [ ] `frontend/src/components/dashboard/SendEmailDialog.test.tsx` — stubs for SEND-02, SEND-06, SEND-07, SEND-08
- [ ] `frontend/src/components/dashboard/DashboardHeader.test.tsx` — stubs for SEND-01 (button render and click)
- [ ] `frontend/src/hooks/useSendEmail.test.ts` — mutation hook behavior
- [ ] html-to-image mock setup in test environment (toPng returns fake base64)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Chart PNG visual quality | SEND-02 | Visual inspection of captured chart colors/layout | 1. Open dashboard 2. Click send 3. Inspect captured PNG in network tab or email |
| CSS variable resolution in capture | SEND-02 | html-to-image SVG serialization compat | 1. Send email 2. Check received email chart has correct colors |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
