## Why

Halaman Riwayat Evaluasi saat ini menampilkan setiap evaluasi sebagai baris terpisah, sehingga brand yang sama muncul berulang kali dan menyulitkan untuk memindai daftar secara cepat. Selain itu, belum ada cara untuk menghapus evaluasi yang salah submit — pengguna harus hidup dengan data yang keliru selamanya.

## What Changes

- **Tampilan tabel diubah dari flat list menjadi accordion per brand** — setiap brand menjadi satu baris ringkasan (nama brand, jumlah evaluasi, skor tertinggi, tanggal terbaru). Klik untuk expand dan lihat evaluasi individual di dalamnya.
- **Paginasi berubah dari per evaluasi menjadi per brand** — 20 brand per halaman.
- **Expand dibatasi 5 evaluasi terbaru** — jika lebih dari 5, tampilkan tombol "Tampilkan semua".
- **Sorting disederhanakan** — hanya sort by tanggal terbaru (descending), menghilangkan opsi sort by score.
- **Fitur hapus evaluasi ditambahkan di halaman detail** — hanya untuk role `leader` dan `admin`. Hard delete dengan konfirmasi ketik nama brand.
- **Seluruh UI halaman riwayat dan dialog hapus menggunakan Bahasa Indonesia.**

## Capabilities

### New Capabilities
- `evaluation-history-grouped`: Tampilan riwayat evaluasi yang dikelompokkan per brand dengan accordion expand/collapse, paginasi per brand, dan expand limit 5 evaluasi terbaru.
- `evaluation-delete`: Kemampuan menghapus evaluasi secara permanen. Role-based (leader/admin), hard delete, konfirmasi dengan mengetik nama brand.

### Modified Capabilities

## Impact

- **Backend API**: Endpoint `GET /api/v1/evaluations` perlu diubah atau ditambah endpoint baru untuk mengembalikan data yang sudah dikelompokkan per brand. Endpoint `DELETE /api/v1/evaluations/{id}` perlu ditambahkan dengan role check.
- **Frontend**: Komponen `EvaluationHistoryTable` perlu ditulis ulang untuk mendukung accordion. Halaman `EvaluationDetailPage` perlu tombol hapus dengan dialog konfirmasi.
- **Database**: Query evaluasi perlu diubah untuk mendukung grouping dan count per brand. Query delete perlu ditambahkan.
- **Tests**: Integration tests untuk endpoint baru dan unit tests untuk komponen accordion serta dialog hapus.
