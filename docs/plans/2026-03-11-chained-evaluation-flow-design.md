# Chained Evaluation Flow

## Problem

The evaluation flow requires 3 separate manual steps: Recalculate All → Hitung Skor → Simpan Evaluasi. Users expect "Hitung Skor" to use fresh calculator data and "Simpan Evaluasi" to produce a complete, up-to-date evaluation. Currently, scoring reads stale cached results and saving just snapshots whatever score exists.

## Design

### Button Behavior

| Button | Current | New |
|--------|---------|-----|
| Recalculate All | Runs all calculators | Same, renamed to Indonesian for consistency |
| Hitung Skor | Reads cached calculator results → scores | Runs all calculators → scores |
| Simpan Evaluasi | Saves existing score (requires score first) | Runs all calculators → scores → saves |

### Chain: Hitung Skor

1. Call `run-all` calculators endpoint
2. Wait for completion
3. Call `generate score` endpoint
4. Display result

### Chain: Simpan Evaluasi

1. Call `run-all` calculators endpoint
2. Wait for completion
3. Call `generate score` endpoint
4. Call `save evaluation` endpoint
5. Display saved confirmation

### Standalone Recalculate All

Remains as-is for users who want to refresh calculator data without scoring. Renamed to "Hitung Ulang Semua" for Indonesian consistency.

### Error Handling

- Calculator failures (missing files) are non-blocking — scoring proceeds with available results (same as current)
- If scoring fails, save is not attempted
- Loading states reflect current step: "Menghitung ulang..." → "Menghitung skor..." → "Menyimpan..."

### Translation Changes

- `calculator.calculateAll`: "Calculate All" → "Hitung Semua"
- `calculator.recalculateAll`: "Recalculate All" → "Hitung Ulang Semua"
- Add step-aware loading labels

### Files to Change

**Frontend:**
- `frontend/src/hooks/useScoring.ts` — chain `runAll` before `generateScore`
- `frontend/src/hooks/useEvaluationOrchestrator.ts` — chain full flow in `handleSaveEvaluation`
- `frontend/src/components/evaluation/scoring/ScoringSection.tsx` — update loading states
- `frontend/src/components/evaluation/EvaluationSections.tsx` — update save button loading states
- `frontend/src/locales/id.json` — Indonesian calculator button labels + step loading labels
- `frontend/src/locales/en.json` — English equivalents
- `frontend/src/locales/th.json` — Thai equivalents
