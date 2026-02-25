## Context

Halaman Riwayat Evaluasi (`/history`) saat ini menampilkan daftar flat semua evaluasi dengan kolom BRAND, SCORE, EVALUATOR, DATE. Setiap evaluasi adalah satu baris — brand yang sama muncul berulang. Tidak ada fitur hapus evaluasi.

**Arsitektur saat ini:**
- Backend: `GET /api/v1/evaluations` — flat list dengan paginasi per evaluasi, sorting by `created_at` atau `final_score`, search by brand name, date range filter.
- Frontend: `EvaluationHistoryTable` — tabel flat, klik baris navigasi ke detail.
- Database: Tabel `evaluations` — immutable, INSERT-only. JOIN ke `brand_vp_data` (brand name) dan `users` (evaluator email).
- Role system: `member`, `leader`, `admin`, `scheduler`. Role check via `require_role()` dependency.

## Goals / Non-Goals

**Goals:**
- Tampilan riwayat evaluasi yang dikelompokkan per brand (accordion)
- Paginasi per brand (20 brand per halaman)
- Expand accordion dibatasi 5 evaluasi terbaru per brand, dengan opsi tampilkan semua
- Fitur hapus evaluasi (hard delete) untuk role leader dan admin
- Dialog konfirmasi hapus dengan mengetik nama brand
- UI full Bahasa Indonesia

**Non-Goals:**
- Soft delete / audit trail untuk evaluasi yang dihapus
- Bulk delete (pilih banyak evaluasi sekaligus)
- Sorting selain tanggal terbaru pada level brand
- Edit evaluasi yang sudah tersimpan
- Perubahan pada halaman evaluasi (form input) — hanya riwayat dan detail

## Decisions

### 1. Endpoint baru vs modifikasi endpoint yang ada

**Keputusan:** Buat endpoint baru `GET /api/v1/evaluations/grouped` untuk tampilan accordion. Endpoint lama `GET /api/v1/evaluations` tetap ada untuk backward compatibility.

**Alasan:** Struktur response berbeda secara fundamental — grouped endpoint mengembalikan brand-level summary dengan nested evaluations, sedangkan endpoint lama mengembalikan flat list. Memisahkan endpoint lebih bersih daripada menambahkan parameter `?grouped=true` yang mengubah shape response.

**Alternatif yang dipertimbangkan:**
- Modifikasi endpoint lama dengan query param `grouped` — ditolak karena response shape berbeda, membingungkan API consumer.
- Grouping di frontend saja — ditolak karena pagination per brand harus dilakukan di database level agar akurat.

### 2. Query strategy untuk grouped data

**Keputusan:** Gunakan dua query:
1. Query brand summary — `GROUP BY brand_id` dengan `COUNT`, `MAX(final_score)`, `MAX(created_at)`, dipaginasi dan di-sort by `MAX(created_at) DESC`.
2. Query evaluasi per brand — saat expand, fetch evaluasi untuk brand tersebut (limit 5, atau semua jika "Tampilkan semua" diklik).

**Alasan:** Memisahkan summary query dan detail query lebih efisien — summary hanya fetch aggregate data untuk halaman saat ini, detail hanya di-fetch on demand saat user expand.

**Alternatif yang dipertimbangkan:**
- Single query dengan window functions — ditolak karena lebih kompleks dan memuat semua evaluasi individual upfront meskipun accordion belum di-expand.

### 3. Fetch evaluasi saat expand — lazy load

**Keputusan:** Evaluasi individual di-fetch on demand saat accordion di-expand via `GET /api/v1/evaluations/grouped/{brand_id}?limit=5`. Tombol "Tampilkan semua" fetch ulang tanpa limit.

**Alasan:** Lazy loading mengurangi payload awal. Mayoritas user hanya akan expand beberapa brand, tidak semua.

### 4. Delete endpoint dengan role check

**Keputusan:** `DELETE /api/v1/evaluations/{evaluation_id}` dengan `require_role("leader", "admin")`. Hard delete — row dihapus dari database.

**Alasan:** User memilih hard delete karena state evaluasi sudah tersimpan di form evaluate, sehingga penggantian data yang salah mudah dilakukan. Konsisten dengan pattern role check yang sudah ada di modul rules.

**Alternatif yang dipertimbangkan:**
- Soft delete dengan kolom `deleted_at` — ditolak oleh user, dianggap tidak perlu.

### 5. Dialog konfirmasi hapus

**Keputusan:** Modal dialog di halaman detail evaluasi. User harus mengetik nama brand persis (case-insensitive) untuk mengaktifkan tombol hapus. Sediakan tombol copy di samping nama brand agar mudah di-paste.

**Alasan:** Mengetik nama brand adalah friction yang disengaja untuk mencegah penghapusan tidak sengaja. Copy button mengurangi frustasi tanpa mengurangi intensionalitas.

### 6. Redirect setelah delete

**Keputusan:** Setelah berhasil menghapus, redirect ke halaman riwayat (`/history`) dengan invalidasi cache React Query.

## Risks / Trade-offs

- **[Perubahan API breaking untuk frontend]** → Mitigasi: Endpoint baru (`/grouped`) terpisah dari endpoint lama. Frontend diubah untuk menggunakan endpoint baru. Endpoint lama tidak diubah.
- **[Hard delete tidak bisa di-undo]** → Mitigasi: Dialog konfirmasi dengan ketik nama brand. Hanya leader/admin yang bisa. Ini trade-off yang diterima user.
- **[Expand banyak brand sekaligus = banyak request]** → Mitigasi: React Query caching — expand yang sama tidak fetch ulang. Limit 5 per expand menjaga response kecil.
- **[Search & date filter tetap berfungsi]** → Filter diterapkan di level evaluasi individual, kemudian di-group. Brand yang tidak punya evaluasi matching filter tidak muncul.
