## ADDED Requirements

### Requirement: Hapus evaluasi secara permanen
Sistem HARUS menyediakan kemampuan untuk menghapus evaluasi secara permanen (hard delete) dari database.

#### Scenario: Evaluasi berhasil dihapus
- **WHEN** pengguna dengan role `leader` atau `admin` menghapus evaluasi
- **THEN** record evaluasi dihapus secara permanen dari database dan tidak lagi muncul di riwayat evaluasi

#### Scenario: Redirect setelah berhasil menghapus
- **WHEN** evaluasi berhasil dihapus
- **THEN** pengguna diarahkan kembali ke halaman riwayat evaluasi (`/history`) dan data riwayat diperbarui

### Requirement: Hanya role leader dan admin yang dapat menghapus
Sistem HARUS membatasi akses fitur hapus evaluasi hanya untuk pengguna dengan role `leader` atau `admin`.

#### Scenario: Pengguna leader dapat menghapus
- **WHEN** pengguna dengan role `leader` mengakses halaman detail evaluasi
- **THEN** tombol hapus ditampilkan

#### Scenario: Pengguna admin dapat menghapus
- **WHEN** pengguna dengan role `admin` mengakses halaman detail evaluasi
- **THEN** tombol hapus ditampilkan

#### Scenario: Pengguna member tidak dapat menghapus
- **WHEN** pengguna dengan role `member` mengakses halaman detail evaluasi
- **THEN** tombol hapus TIDAK ditampilkan

#### Scenario: API menolak request hapus dari member
- **WHEN** pengguna dengan role `member` mengirim request `DELETE /api/v1/evaluations/{id}`
- **THEN** API mengembalikan HTTP 403 Forbidden

### Requirement: Konfirmasi hapus dengan mengetik nama brand
Sistem HARUS menampilkan dialog konfirmasi yang mengharuskan pengguna mengetik nama brand sebelum evaluasi dapat dihapus.

#### Scenario: Dialog konfirmasi muncul saat klik hapus
- **WHEN** pengguna mengklik tombol hapus di halaman detail evaluasi
- **THEN** dialog modal ditampilkan dengan pesan peringatan, nama brand yang harus diketik, kolom input teks, dan tombol hapus yang nonaktif

#### Scenario: Tombol hapus aktif setelah nama brand diketik dengan benar
- **WHEN** pengguna mengetik nama brand yang cocok (case-insensitive) di kolom input
- **THEN** tombol hapus menjadi aktif dan dapat diklik

#### Scenario: Tombol hapus tetap nonaktif jika nama brand tidak cocok
- **WHEN** pengguna mengetik teks yang tidak cocok dengan nama brand
- **THEN** tombol hapus tetap nonaktif

#### Scenario: Tombol copy tersedia untuk nama brand
- **WHEN** dialog konfirmasi hapus ditampilkan
- **THEN** terdapat tombol copy di samping nama brand yang menyalin nama brand ke clipboard saat diklik

#### Scenario: Batal menghapus
- **WHEN** pengguna mengklik tombol "Batal" pada dialog konfirmasi
- **THEN** dialog ditutup dan evaluasi tidak dihapus

### Requirement: Endpoint API hapus evaluasi
Sistem HARUS menyediakan endpoint `DELETE /api/v1/evaluations/{evaluation_id}` untuk menghapus evaluasi.

#### Scenario: Hapus evaluasi yang ada
- **WHEN** request `DELETE /api/v1/evaluations/{evaluation_id}` dikirim untuk evaluasi yang ada
- **THEN** evaluasi dihapus dari database dan API mengembalikan HTTP 204 No Content

#### Scenario: Hapus evaluasi yang tidak ditemukan
- **WHEN** request `DELETE /api/v1/evaluations/{evaluation_id}` dikirim untuk ID yang tidak ada
- **THEN** API mengembalikan HTTP 404 Not Found

#### Scenario: Request tanpa autentikasi
- **WHEN** request `DELETE /api/v1/evaluations/{evaluation_id}` dikirim tanpa token autentikasi
- **THEN** API mengembalikan HTTP 401 Unauthorized

### Requirement: UI hapus menggunakan Bahasa Indonesia
Seluruh teks pada dialog hapus dan tombol hapus HARUS menggunakan Bahasa Indonesia.

#### Scenario: Teks dialog konfirmasi dalam Bahasa Indonesia
- **WHEN** dialog konfirmasi hapus ditampilkan
- **THEN** judul dialog adalah "Hapus Evaluasi", pesan peringatan menjelaskan bahwa tindakan permanen dan tidak dapat dibatalkan, label input adalah "Ketik nama brand untuk konfirmasi:", tombol aksi adalah "Batal" dan "Hapus"

#### Scenario: Tombol hapus di halaman detail dalam Bahasa Indonesia
- **WHEN** halaman detail evaluasi ditampilkan untuk pengguna leader/admin
- **THEN** tombol hapus bertuliskan "Hapus Evaluasi"
