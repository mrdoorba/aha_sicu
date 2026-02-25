## 1. Fix mass update lookup

- [x] 1.1 Add first-match guard in `_build_mass_update_lookup()` — change `name_to_kode[label] = kode_variasi` to only set if `label not in name_to_kode`

## 2. Tests

- [x] 2.1 Add unit test for duplicate labels in mass update data — verify first Kode Variasi is used and correct stock is returned
- [x] 2.2 Run existing test suite to confirm no regressions
