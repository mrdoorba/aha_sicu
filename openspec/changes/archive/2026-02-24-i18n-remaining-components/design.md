## Context

Change `i18n-bahasa-indonesia` sudah setup react-i18next dan migrasi 14 komponen utama. File `id.json` sudah berisi 107 key. Pattern sudah established: `useTranslation()` hook, flat JSON dot-notation keys, istilah teknis tetap Inggris. Sisa ~16 komponen masih hardcoded — perlu migrasi ke pattern yang sama.

## Goals / Non-Goals

**Goals:**
- Migrasi semua sisa komponen ke `t()` calls mengikuti pattern yang sudah ada
- Tambahkan ~150 key baru ke `id.json` yang sudah ada
- Update test yang assert hardcoded string

**Non-Goals:**
- Mengubah pattern i18n yang sudah established (library, config, key naming)
- Refactor komponen selain migrasi string
- Menambah bahasa baru

## Decisions

### 1. Ikuti pattern yang sudah ada
Semua keputusan arsitektural sudah dibuat di change sebelumnya. Migrasi ini hanya menambah komponen baru ke pattern yang sama: `const { t } = useTranslation()`, flat key `component.key` di `id.json`.

### 2. Key naming untuk komponen baru
Key baru mengikuti konvensi yang sudah ada, berdasarkan lokasi komponen:
- Form evaluasi: `evaluationSections.*`, `saveIndicator.*`, `forms.operational.*`, `forms.business.*`, `forms.visitors.*`, `forms.content.*`, `forms.promoTools.*`, `forms.ads.*`, `forms.campaign.*`, `forms.competition.*`, `forms.products.*`
- File upload: `fileUpload.*`
- Calculator: `calculator.*`
- Accounts: `accounts.*`
- Rules: `rules.*`, `passwordConfirm.*`

### 3. Shared aria-label keys
String `"Buka Shopee Seller Center (tab baru)"` muncul di 6+ form — gunakan satu shared key `common.aria.openSellerCenter` untuk menghindari duplikasi.

### 4. RulesCategoryCard: label dictionary tetap sebagai constant
`CATEGORY_LABELS` dan `RULE_LABELS` di RulesCategoryCard.tsx adalah mapping dari backend rule key ke display label. Migrate value-nya ke `t()` calls sambil mempertahankan struktur dictionary — key mapping tetap sama, hanya value yang berubah dari hardcoded string ke `t('rules.label.xxx')`.

## Risks / Trade-offs

- **[Banyak file sekaligus]** → Mitigasi: migrasi per grup (forms, accounts, rules) secara atomic
- **[Test update volume]** → Mitigasi: test files yang terpengaruh perlu update assertion — jalankan vitest setelah setiap grup
- **[id.json semakin besar]** → Acceptable — single file masih manageable di skala ini (~250 key total)
