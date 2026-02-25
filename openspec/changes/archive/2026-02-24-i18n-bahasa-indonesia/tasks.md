## 1. Setup i18n

- [x] 1.1 Install `react-i18next` dan `i18next` di frontend
- [x] 1.2 Buat file konfigurasi `frontend/src/i18n.ts`
- [x] 1.3 Buat file terjemahan `frontend/src/locales/id.json` dengan semua string UI
- [x] 1.4 Import `i18n.ts` di `main.tsx` sebelum app render

## 2. Migrasi Halaman

- [x] 2.1 Migrasi `LoginPage.tsx` — ganti hardcoded string ke `t()`
- [x] 2.2 Migrasi `DashboardPage.tsx` — ganti hardcoded string ke `t()`
- [x] 2.3 Migrasi `BrandsPage.tsx` — ganti hardcoded string ke `t()`
- [x] 2.4 Migrasi `EvaluationPage.tsx` — ganti hardcoded string ke `t()`
- [x] 2.5 Migrasi `EvaluationDetailPage.tsx` — ganti hardcoded string ke `t()`
- [x] 2.6 Migrasi `HistoryPage.tsx` — ganti hardcoded string ke `t()`

## 3. Migrasi Komponen Layout

- [x] 3.1 Migrasi `Header.tsx` — nav items, logout dialog, button states

## 4. Migrasi Komponen Evaluasi

- [x] 4.1 Migrasi `EvaluationHeader.tsx` — error messages, button labels
- [x] 4.2 Migrasi `ScoringSection.tsx` — labels, headings
- [x] 4.3 Migrasi `VerdictSelector.tsx` — verdict options
- [x] 4.4 Migrasi `EmailOutput.tsx` — copy button, label
- [x] 4.5 Migrasi `WhatsAppLink.tsx` — link text

## 5. Migrasi Komponen Lain

- [x] 5.1 Migrasi `SyncStatus.tsx` — sync status messages, button
- [x] 5.2 Migrasi `TopSkuResults.tsx` — table headers, labels

## 6. Verifikasi

- [x] 6.1 Jalankan `npm run lint` dan `tsc --noEmit` — pastikan tidak ada error
- [x] 6.2 Jalankan `vitest run` — pastikan semua test pass
- [x] 6.3 Build production (`npm run build`) — pastikan berhasil
