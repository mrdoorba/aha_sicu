## ADDED Requirements

### Requirement: Tampilan riwayat evaluasi dikelompokkan per brand
Sistem HARUS menampilkan riwayat evaluasi yang dikelompokkan berdasarkan brand dalam format accordion. Setiap brand menjadi satu baris ringkasan yang bisa di-expand untuk melihat evaluasi individual di dalamnya.

#### Scenario: Baris ringkasan brand menampilkan data agregat
- **WHEN** halaman riwayat evaluasi dimuat
- **THEN** setiap brand ditampilkan sebagai satu baris dengan kolom: nama brand, jumlah evaluasi, skor tertinggi (dengan verdict), dan tanggal evaluasi terbaru

#### Scenario: Brand dengan satu evaluasi
- **WHEN** sebuah brand hanya memiliki satu evaluasi
- **THEN** brand tetap ditampilkan sebagai baris ringkasan dengan jumlah "1 evaluasi"

### Requirement: Accordion expand/collapse per brand
Sistem HARUS menyediakan mekanisme expand/collapse pada setiap baris brand untuk menampilkan evaluasi individual di dalamnya.

#### Scenario: Expand brand menampilkan evaluasi individual
- **WHEN** pengguna mengklik baris ringkasan brand untuk expand
- **THEN** sistem menampilkan evaluasi individual dengan kolom: skor (dengan verdict), email evaluator, dan tanggal evaluasi — diurutkan dari yang terbaru

#### Scenario: Collapse brand menyembunyikan evaluasi
- **WHEN** pengguna mengklik baris ringkasan brand yang sedang expanded
- **THEN** evaluasi individual disembunyikan dan baris kembali ke tampilan ringkasan

#### Scenario: Evaluasi individual dapat diklik ke halaman detail
- **WHEN** pengguna mengklik salah satu baris evaluasi individual di dalam accordion yang ter-expand
- **THEN** sistem menavigasi ke halaman detail evaluasi tersebut (`/history/{id}`)

### Requirement: Expand dibatasi 5 evaluasi terbaru
Sistem HARUS membatasi tampilan awal expand accordion maksimal 5 evaluasi terbaru per brand. Jika brand memiliki lebih dari 5 evaluasi, tampilkan tombol untuk melihat semua.

#### Scenario: Brand dengan 5 evaluasi atau kurang
- **WHEN** pengguna expand brand yang memiliki 5 evaluasi atau kurang
- **THEN** semua evaluasi ditampilkan tanpa tombol "Tampilkan semua"

#### Scenario: Brand dengan lebih dari 5 evaluasi
- **WHEN** pengguna expand brand yang memiliki lebih dari 5 evaluasi
- **THEN** hanya 5 evaluasi terbaru yang ditampilkan, dengan tombol "Tampilkan semua (N)" di bawah, dimana N adalah total jumlah evaluasi

#### Scenario: Klik tampilkan semua memuat seluruh evaluasi
- **WHEN** pengguna mengklik tombol "Tampilkan semua (N)"
- **THEN** semua evaluasi untuk brand tersebut ditampilkan menggantikan tampilan 5 terbaru, dan tombol "Tampilkan semua" menghilang

### Requirement: Paginasi per brand
Sistem HARUS melakukan paginasi berdasarkan jumlah brand, bukan jumlah evaluasi individual.

#### Scenario: Paginasi menampilkan 20 brand per halaman
- **WHEN** terdapat lebih dari 20 brand dengan evaluasi
- **THEN** halaman pertama menampilkan 20 brand pertama (diurutkan berdasarkan tanggal terbaru) dengan kontrol paginasi untuk halaman berikutnya

#### Scenario: Navigasi halaman brand
- **WHEN** pengguna berpindah ke halaman berikutnya
- **THEN** semua accordion di-collapse dan 20 brand berikutnya ditampilkan

### Requirement: Sorting berdasarkan tanggal terbaru
Sistem HARUS mengurutkan brand berdasarkan tanggal evaluasi terbaru secara descending (brand dengan evaluasi terbaru muncul di atas).

#### Scenario: Brand diurutkan berdasarkan evaluasi terbaru
- **WHEN** halaman riwayat evaluasi dimuat
- **THEN** brand dengan evaluasi paling baru muncul di posisi teratas

### Requirement: Pencarian dan filter tetap berfungsi
Sistem HARUS mempertahankan fungsi pencarian berdasarkan nama brand dan filter rentang tanggal. Filter diterapkan pada level evaluasi individual, kemudian hasilnya dikelompokkan per brand.

#### Scenario: Pencarian nama brand memfilter daftar
- **WHEN** pengguna mengetik nama brand di kolom pencarian
- **THEN** hanya brand yang namanya cocok (case-insensitive) yang ditampilkan, dengan jumlah evaluasi dan skor tertinggi yang sesuai

#### Scenario: Filter tanggal mempengaruhi data per brand
- **WHEN** pengguna memilih rentang tanggal
- **THEN** hanya evaluasi dalam rentang tersebut yang dihitung, dan brand yang tidak memiliki evaluasi dalam rentang tersebut tidak ditampilkan

#### Scenario: Kombinasi pencarian dan filter tanggal
- **WHEN** pengguna menerapkan pencarian nama brand DAN filter rentang tanggal
- **THEN** kedua filter diterapkan bersamaan — hanya brand yang cocok dengan pencarian DAN memiliki evaluasi dalam rentang tanggal yang ditampilkan

### Requirement: Endpoint API untuk data terkelompok
Sistem HARUS menyediakan endpoint API `GET /api/v1/evaluations/grouped` yang mengembalikan data evaluasi yang sudah dikelompokkan per brand.

#### Scenario: Response endpoint grouped berisi ringkasan per brand
- **WHEN** endpoint `GET /api/v1/evaluations/grouped` dipanggil dengan parameter `page=1&limit=20`
- **THEN** response berisi daftar brand dengan field: `brand_id`, `brand_name`, `evaluation_count`, `top_score`, `top_verdict`, `latest_date`, beserta informasi paginasi (`total`, `page`, `limit`, `pages`)

#### Scenario: Endpoint mendukung parameter pencarian dan filter tanggal
- **WHEN** endpoint dipanggil dengan parameter `search`, `date_from`, dan/atau `date_to`
- **THEN** filter diterapkan pada evaluasi individual sebelum pengelompokan, dan hanya brand dengan evaluasi yang cocok yang dikembalikan

### Requirement: Endpoint API untuk evaluasi per brand
Sistem HARUS menyediakan endpoint API `GET /api/v1/evaluations/grouped/{brand_id}` yang mengembalikan evaluasi individual untuk brand tertentu.

#### Scenario: Fetch evaluasi dengan limit
- **WHEN** endpoint dipanggil dengan `limit=5`
- **THEN** response berisi maksimal 5 evaluasi terbaru untuk brand tersebut, beserta field `total` yang menunjukkan total evaluasi untuk brand ini

#### Scenario: Fetch semua evaluasi brand
- **WHEN** endpoint dipanggil tanpa parameter limit
- **THEN** response berisi semua evaluasi untuk brand tersebut, diurutkan dari yang terbaru

#### Scenario: Filter tanggal diterapkan pada evaluasi brand
- **WHEN** endpoint dipanggil dengan parameter `date_from` dan/atau `date_to`
- **THEN** hanya evaluasi dalam rentang tanggal tersebut yang dikembalikan

### Requirement: UI menggunakan Bahasa Indonesia
Seluruh teks pada halaman riwayat evaluasi HARUS menggunakan Bahasa Indonesia.

#### Scenario: Label kolom dalam Bahasa Indonesia
- **WHEN** halaman riwayat evaluasi ditampilkan
- **THEN** kolom tabel menggunakan label: "BRAND", "EVALUASI", "SKOR TERTINGGI", "TERBARU"

#### Scenario: Teks pagination dan status dalam Bahasa Indonesia
- **WHEN** halaman riwayat evaluasi ditampilkan
- **THEN** teks seperti jumlah evaluasi ("3 evaluasi"), tombol ("Tampilkan semua"), pesan kosong, dan label filter menggunakan Bahasa Indonesia
