## 1. Backend — Endpoint Grouped Evaluations

- [x] 1.1 Tambah query `list_grouped_evaluations` di `backend/app/db/queries/evaluations.py` — GROUP BY brand_id dengan COUNT, MAX(final_score), MAX(created_at), paginasi per brand, sort by latest date DESC, mendukung search dan date filter
- [x] 1.2 Tambah query `count_grouped_evaluations` di `backend/app/db/queries/evaluations.py` — count distinct brand yang cocok dengan filter
- [x] 1.3 Tambah query `list_evaluations_by_brand` di `backend/app/db/queries/evaluations.py` — fetch evaluasi individual per brand_id dengan optional limit, sort by created_at DESC, mendukung date filter
- [x] 1.4 Tambah Pydantic schemas di `backend/app/modules/evaluations/schemas.py` — `GroupedEvaluationItem`, `GroupedEvaluationListResponse`, `BrandEvaluationItem`, `BrandEvaluationListResponse`
- [x] 1.5 Tambah service functions `list_grouped_evaluations` dan `list_evaluations_by_brand` di `backend/app/modules/evaluations/service.py`
- [x] 1.6 Tambah endpoint `GET /api/v1/evaluations/grouped` di `backend/app/modules/evaluations/router.py` — paginasi per brand, search, date filter
- [x] 1.7 Tambah endpoint `GET /api/v1/evaluations/grouped/{brand_id}` di `backend/app/modules/evaluations/router.py` — evaluasi per brand dengan optional limit dan date filter

## 2. Backend — Endpoint Delete Evaluation

- [x] 2.1 Tambah query `delete_evaluation` di `backend/app/db/queries/evaluations.py` — hard delete by evaluation_id, return True/False
- [x] 2.2 Tambah service function `delete_evaluation` di `backend/app/modules/evaluations/service.py` — validasi existence, panggil query delete
- [x] 2.3 Tambah endpoint `DELETE /api/v1/evaluations/{evaluation_id}` di `backend/app/modules/evaluations/router.py` — require_role("leader", "admin"), return 204 atau 404

## 3. Backend — Tests

- [x] 3.1 Tambah integration tests untuk `GET /api/v1/evaluations/grouped` — paginasi per brand, search, date filter, response shape
- [x] 3.2 Tambah integration tests untuk `GET /api/v1/evaluations/grouped/{brand_id}` — limit 5, tanpa limit, date filter, brand tidak ditemukan
- [x] 3.3 Tambah integration tests untuk `DELETE /api/v1/evaluations/{evaluation_id}` — sukses (leader/admin), forbidden (member), not found, unauthorized

## 4. Frontend — Hook dan API Client

- [x] 4.1 Tambah hook `useGroupedEvaluations` — fetch `GET /api/v1/evaluations/grouped` dengan paginasi, search, date filter
- [x] 4.2 Tambah hook `useBrandEvaluations` — fetch `GET /api/v1/evaluations/grouped/{brand_id}` dengan limit, dipanggil on demand saat expand
- [x] 4.3 Tambah hook `useDeleteEvaluation` — mutation `DELETE /api/v1/evaluations/{id}` dengan invalidasi cache React Query

## 5. Frontend — Komponen Accordion Riwayat Evaluasi

- [x] 5.1 Refactor `EvaluationHistoryTable` menjadi tampilan accordion per brand — baris ringkasan dengan kolom BRAND, EVALUASI, SKOR TERTINGGI, TERBARU
- [x] 5.2 Implementasi expand/collapse per brand — lazy load evaluasi via `useBrandEvaluations`, tampilkan skor, evaluator, tanggal per baris
- [x] 5.3 Implementasi limit 5 evaluasi terbaru saat expand — tombol "Tampilkan semua (N)" jika lebih dari 5
- [x] 5.4 Implementasi paginasi per brand — 20 brand per halaman, collapse semua accordion saat pindah halaman
- [x] 5.5 Sesuaikan search dan date filter agar menggunakan endpoint grouped — pastikan filter berfungsi dengan benar
- [x] 5.6 Ganti semua teks UI ke Bahasa Indonesia — label kolom, tombol, pesan kosong, pesan error, placeholder pencarian, label filter

## 6. Frontend — Dialog Hapus Evaluasi

- [x] 6.1 Buat komponen `DeleteEvaluationDialog` — modal dengan pesan peringatan, input ketik nama brand (case-insensitive matching), tombol copy nama brand, tombol Batal dan Hapus (nonaktif sampai nama cocok)
- [x] 6.2 Tambahkan tombol "Hapus Evaluasi" di `EvaluationDetailPage` — tampilkan hanya untuk role leader/admin, klik membuka `DeleteEvaluationDialog`
- [x] 6.3 Implementasi flow hapus — panggil `useDeleteEvaluation`, tampilkan loading state, redirect ke `/history` setelah berhasil, tampilkan error jika gagal

## 7. Frontend — Tests

- [x] 7.1 Tambah tests untuk komponen accordion — render grouped data, expand/collapse, lazy load, limit 5, tampilkan semua, paginasi
- [x] 7.2 Tambah tests untuk `DeleteEvaluationDialog` — render dialog, input validation, copy button, hapus berhasil, batal
- [x] 7.3 Tambah tests untuk tombol hapus di detail page — tampil untuk leader/admin, tidak tampil untuk member
