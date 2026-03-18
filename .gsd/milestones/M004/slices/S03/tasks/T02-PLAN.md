---
estimated_steps: 8
estimated_files: 1
---

# T02: Run milestone DoD verification gate and document results

**Slice:** S03 — Verification sweep and test hardening
**Milestone:** M004

## Description

This is the final verification gate for the entire M004 milestone. After T01 extracted all residual hardcoded Indonesian strings, this task runs every milestone Definition of Done check, documents the results, catalogs any remaining known exceptions with justification, updates requirement statuses to validated, and writes the S03 summary. No code changes are expected unless T01 missed something — this is purely a verification and documentation task.

## Steps

1. **Run full `rg` sweep for common Indonesian words** in non-test, non-locale `.tsx`/`.ts` files:
   ```bash
   cd frontend && rg -n --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src \
     "Penjualan|Bulan|Evaluasi|Hapus|Gagal|Berhasil|Terjadi|Tidak|Pilih|Cari|Batal|Simpan|Kirim|Tambah|Ubah|Lihat|Kembali|Memuat|Riwayat|Konfirmasi|Tutup|Peringatan|Halaman|Berikutnya|Sebelumnya|Akses|ditolak|Rata|Afiliasi|Ongkir|Diskon|Iklan|Pesanan|Pengunjung|Tingkat|Sinkronisasi|Sistem|Garansi|Omzet|Pengemasan|Pengiriman|Dibalas|Penilaian|Konversi|Pengikut|Produk|Toko|Sesi|Dinominasikan|Tersedia|hari|dari" \
     src --glob '!*.test.*' --glob '!*locales*' --glob '!*locale*' --glob '!*localeMap*'
   ```
   - For every hit, classify: (a) inert `label` property in `fields.ts` — OK, dead code; (b) code comment — OK; (c) backend column name matcher — OK; (d) `labelKey`/`displayNameKey`/`benchmarkKey` key string containing Indonesian — OK, it's a key not rendered text; (e) rendered UI text — NOT OK, must be fixed before proceeding
   - If any rendered UI text is found, fix it immediately (add locale key, update source, update tests)

2. **Run `rg "id-ID"` sweep:**
   ```bash
   rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src \
     | grep -v test | grep -v locale | grep -v localeMap
   ```
   - Expected: zero hits (confirmed zero since S01/S02)

3. **Run full test suite:**
   ```bash
   cd frontend && npm run test:run
   ```
   - Expected: 612+ tests pass. The RulesPage.test.tsx 5s timeout flake may fail intermittently — note it as pre-existing, unrelated to i18n.

4. **Run locale file sync check:**
   ```bash
   python3 -c "import json; fs=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; cs=[len(json.load(open(f))) for f in fs]; print(f'Key counts: {cs}'); assert len(set(cs))==1, f'Mismatch: {cs}'"
   ```
   - Expected: all 3 files have 714 keys (698 from S01/S02 + 16 from T01)

5. **Run type check:**
   ```bash
   cd frontend && npx tsc --noEmit
   ```
   - Expected: zero errors

6. **Re-check each milestone success criterion** (from M004-ROADMAP.md):
   - ✅/❌ Switching to TH renders zero Indonesian strings on any page → verified by `rg` sweep + locale file completeness
   - ✅/❌ Switching to EN renders zero Indonesian strings on any page → verified by `rg` sweep + locale file completeness
   - ✅/❌ `rg` for common Indonesian words in non-test, non-locale source returns zero hits → verified in step 1
   - ✅/❌ `rg "id-ID"` in non-test, non-locale source returns zero hits → verified in step 2
   - ✅/❌ All frontend tests pass (602+ baseline) → verified in step 3
   - ✅/❌ A translator only needs to edit their `{lang}.json` to fully localize the app → verified by locale file structure + zero hardcoded rendered strings

7. **Update requirement statuses** using `gsd_update_requirement`:
   - R031 (zero hardcoded Indonesian UI text): status → `validated`, validation → describe the `rg` sweep results and exception list
   - R032 (all frontend tests pass after extraction): status → `validated`, validation → describe test pass count and the lockstep update approach
   - R027, R028, R029, R030 should already be validated from S01/S02. Confirm their status and update if needed.

8. **Write S03 summary** to `.gsd/milestones/M004/slices/S03/S03-SUMMARY.md` following the established summary format from S01/S02. Include:
   - What happened (T01 extraction + T02 verification)
   - Verification results table (all 6+ checks)
   - Requirements advanced/validated
   - Known exceptions list with justification (inert `label` property, code comments, backend column matchers, `shortLabel` regex)
   - Forward Intelligence (what the milestone closure should know)

## Must-Haves

- [ ] `rg` sweep for Indonesian text returns zero rendered-string hits (only inert/comment/backend-matcher exceptions)
- [ ] `rg "id-ID"` returns zero hits in non-test/non-locale source
- [ ] All 612+ frontend tests pass
- [ ] All 3 locale files have equal key count
- [ ] `npx tsc --noEmit` has zero errors
- [ ] All 6 milestone success criteria re-checked and documented
- [ ] R031 status updated to `validated`
- [ ] R032 status updated to `validated`
- [ ] S03-SUMMARY.md written with verification results and known exceptions

## Verification

- All milestone success criteria pass — documented in summary
- R031 and R032 show status `validated` in REQUIREMENTS.md
- S03-SUMMARY.md exists with complete verification table

## Inputs

- T01 completed: all residual Indonesian strings extracted, ~16 new locale keys, all tests passing
- S01 summary: 34 locale keys added, 612 tests passing baseline established
- S02 summary: 74 locale keys added, 698 total keys, zero `id-ID` in non-test/non-locale source
- Milestone roadmap: 6 success criteria to verify
- REQUIREMENTS.md: R027-R032 requirement definitions

## Observability Impact

- **No new runtime signals** — this task is purely verification and documentation.
- **Inspection surface:** S03-SUMMARY.md contains the complete verification results table with every DoD check, its command, exit code, and pass/fail verdict. A future agent can re-run any individual command from that table to re-verify.
- **Failure visibility:** If any check fails, the S03-SUMMARY.md Known Issues section documents what failed and why. R031/R032 remain at status `active` in REQUIREMENTS.md until all checks pass.
- **Diagnostic commands:** All 5 verification commands (rg sweep, id-ID sweep, test suite, locale sync, tsc) are documented in the S03-SUMMARY.md verification table and can be re-run independently.

## Expected Output

- `.gsd/milestones/M004/slices/S03/S03-SUMMARY.md` — complete slice summary with verification results, known exceptions, and forward intelligence
- REQUIREMENTS.md updated with R031 and R032 status = validated
