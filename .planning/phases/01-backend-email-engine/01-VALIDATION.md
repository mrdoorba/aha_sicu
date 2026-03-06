---
phase: 1
slug: backend-email-engine
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.0+ with pytest-asyncio |
| **Config file** | backend/pyproject.toml `[tool.pytest.ini_options]` |
| **Quick run command** | `cd backend && uv run pytest tests/unit/email/ -x -q` |
| **Full suite command** | `cd backend && uv run pytest -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd backend && uv run pytest tests/unit/email/ -x -q`
- **After every plan wave:** Run `cd backend && uv run pytest -v && uv run ruff check .`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | INFRA-02 | unit | `uv run pytest tests/unit/email/test_config.py -x` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | INFRA-01, INFRA-03 | unit | `uv run pytest tests/unit/email/test_service.py -x` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | INFRA-05, INFRA-06 | unit | `uv run pytest tests/unit/email/test_service.py::test_cid_images -x` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | INFRA-04, CONT-01 | unit | `uv run pytest tests/unit/email/test_template.py::test_score_overview -x` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 1 | CONT-02 | unit | `uv run pytest tests/unit/email/test_template.py::test_detailed_evaluation -x` | ❌ W0 | ⬜ pending |
| 01-02-03 | 02 | 1 | CONT-03, CONT-04 | unit | `uv run pytest tests/unit/email/test_template.py::test_data_intelligence -x` | ❌ W0 | ⬜ pending |
| 01-02-04 | 02 | 1 | CONT-05, CONT-06 | unit | `uv run pytest tests/unit/email/test_template.py::test_responsive -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/unit/email/` — directory does not exist
- [ ] `backend/tests/unit/email/__init__.py` — package init
- [ ] `backend/tests/unit/email/test_template.py` — covers INFRA-04, CONT-01 through CONT-05
- [ ] `backend/tests/unit/email/test_service.py` — covers INFRA-01, INFRA-03, INFRA-05, INFRA-06, CONT-03, CONT-06
- [ ] `backend/tests/unit/email/conftest.py` — shared fixtures (mock evaluation data, mock SMTP, sample base64 image)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Email renders correctly in Gmail (web) | CONT-05 | Requires real email client rendering | Send test email, open in Gmail, verify layout |
| Email renders correctly in Outlook (web) | CONT-05 | Requires real email client rendering | Send test email, open in Outlook, verify layout |
| Email renders correctly in Apple Mail | CONT-05 | Requires real email client rendering | Send test email, open in Apple Mail, verify layout |
| CID images display inline (not as attachments) | INFRA-05 | Requires real email client to verify display | Send test email, verify chart/header/footer show inline |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
