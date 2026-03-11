# Ads Calculator i18n Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:executing-plans to implement this plan task-by-task.

**Goal:** Add full translation support to the ads keyword calculator output, following the existing `TranslatableText` pattern.

**Architecture:** Backend returns `_i18n` objects (key + vars) alongside hardcoded text for every section. Frontend renders each section via `renderTranslatable()` in a single `<pre>` block. Locale files contain all translation templates.

**Tech Stack:** Python (backend calculator), TypeScript/React (frontend), i18next (translations)

---

### Task 0: Add i18n keys for AK4 individual flags in locale files

Currently AK4 uses a single `ads.recommendations` key. We need individual flag keys.

**Files:**
- Modify: `frontend/src/locales/id.json:557-559`
- Modify: `frontend/src/locales/en.json:557-559`
- Modify: `frontend/src/locales/th.json:557-559`

**Step 1: Add keys to `id.json`**

Before `"email.subject"`, add after `"ads.recommendations"`:

```json
  "ads.flag.productLow": "📌 Jumlah produk yang dipartisipasikan ke dalam iklan kurang maksimal (saran >50%).",
  "ads.flag.productGood": "📌 Jumlah produk yang dipartisipasikan ke dalam iklan sudah cukup baik.",
  "ads.flag.activeLow": "📌 Jumlah iklan dengan status aktif kurang maksimal (saran >50%).",
  "ads.flag.activeGood": "📌 Jumlah iklan dengan status aktif sudah cukup baik.",
  "ads.flag.noShopAd": "📌 Iklan Toko belum dimanfaatkan.",
```

**Step 2: Add keys to `en.json`**

```json
  "ads.flag.productLow": "📌 Product participation in ads is not optimal (recommended >50%).",
  "ads.flag.productGood": "📌 Product participation in ads is good enough.",
  "ads.flag.activeLow": "📌 Number of active ads is not optimal (recommended >50%).",
  "ads.flag.activeGood": "📌 Number of active ads is good enough.",
  "ads.flag.noShopAd": "📌 Shop Ads have not been utilized.",
```

**Step 3: Add keys to `th.json`**

```json
  "ads.flag.productLow": "📌 จำนวนสินค้าที่เข้าร่วมโฆษณายังไม่เต็มที่ (แนะนำ >50%)",
  "ads.flag.productGood": "📌 จำนวนสินค้าที่เข้าร่วมโฆษณาอยู่ในระดับดี",
  "ads.flag.activeLow": "📌 จำนวนโฆษณาที่ใช้งานยังไม่เต็มที่ (แนะนำ >50%)",
  "ads.flag.activeGood": "📌 จำนวนโฆษณาที่ใช้งานอยู่ในระดับดี",
  "ads.flag.noShopAd": "📌 ยังไม่ได้ใช้โฆษณาร้านค้า",
```

**Step 4: Commit**

```bash
git add frontend/src/locales/{id,en,th}.json
git commit -m "Add AK4 individual flag i18n keys to locale files"
```

---

### Task 1: Add i18n keys for Sheet 2 (AL2-AL9) in locale files

**Files:**
- Modify: `frontend/src/locales/id.json`
- Modify: `frontend/src/locales/en.json`
- Modify: `frontend/src/locales/th.json`

**Step 1: Add TOP/BOTTOM ad keys to `id.json`**

Add after the flag keys from Task 0:

```json
  "ads.topHeader": "• TOP Iklan (GMV tertinggi dengan ROAS terbaik):",
  "ads.topHeaderFallback": "• TOP Iklan [fallback] (GMV tertinggi dengan ROAS terbaik):",
  "ads.topAd": "  ▶ {{name}}\n    GMV: {{gmv}} {ROAS: {{roas}}}\n    {{bidding}}\n    {{placement}}: {{keyword}}",
  "ads.topRecommendation.auto": "📌 Iklan dengan performa terbaik mengandalkan pengaturan otomatis (Iklan toko manual berpotensi belum dimanfaatkan).",
  "ads.topRecommendation.manual": "📌 Iklan dengan performa terbaik sudah mengandalkan pengaturan manual.",
  "ads.bottomHeader": "• BOTTOM Iklan (biaya tertinggi dengan ROAS terendah):",
  "ads.bottomHeaderFallback": "• BOTTOM Iklan [fallback] (biaya tertinggi dengan ROAS terendah):",
  "ads.bottomAd": "  ▶ {{name}}\n    Biaya: {{cost}} {ROAS: {{roas}}}\n    {{bidding}}\n    {{placement}}: {{keyword}}",
  "ads.bottomAdFallback": "  ▶ {{name}}\n    Biaya: {{cost}} {ROAS: {{roas}}}\n    {{bidding}} {{placement}}: {{keyword}}",
  "ads.flag.autoUncontrolled": "📌 Terdapat iklan dengan pengaturan otomatis yang tidak terkontrol biayanya (disarankan dimonitor 1-2x setiap hari).",
  "ads.flag.manualUncontrolled": "📌 Terdapat iklan dengan pengaturan manual yang tidak terkontrol biayanya (disarankan dimonitor 1-2x setiap hari).",
  "ads.flag.keywordUncontrolled": "📌 Terdapat kata kunci dengan pengaturan manual yang tidak terkontrol biayanya (disarankan dipantau 1-2x setiap hari).",
  "ads.flag.autoBiddingUncontrolled": "📌 Terdapat iklan dengan pengaturan otomatis yang tidak terkontrol biayanya (disarankan dimonitor 1-2x setiap hari).",
  "ads.value.iklanProduk": "Iklan Produk",
  "ads.value.iklanToko": "Iklan Toko",
  "ads.value.semuaPenempatan": "Semua Penempatan",
  "ads.value.halamanPencarian": "Halaman Pencarian",
  "ads.value.halamanRekomendasi": "Halaman Rekomendasi",
  "ads.value.biddingOtomatis": "Bidding Otomatis",
  "ads.value.biddingManual": "Bidding Manual",
  "ads.value.gmvMaxAuto": "GMV Max Auto",
  "ads.value.gmvMaxRoas": "GMV Max ROAS",
```

**Step 2: Add corresponding keys to `en.json`**

```json
  "ads.topHeader": "• TOP Ads (highest GMV with best ROAS):",
  "ads.topHeaderFallback": "• TOP Ads [fallback] (highest GMV with best ROAS):",
  "ads.topAd": "  ▶ {{name}}\n    GMV: {{gmv}} {ROAS: {{roas}}}\n    {{bidding}}\n    {{placement}}: {{keyword}}",
  "ads.topRecommendation.auto": "📌 Best performing ads rely on automatic settings (manual shop ads may be underutilized).",
  "ads.topRecommendation.manual": "📌 Best performing ads already rely on manual settings.",
  "ads.bottomHeader": "• BOTTOM Ads (highest cost with lowest ROAS):",
  "ads.bottomHeaderFallback": "• BOTTOM Ads [fallback] (highest cost with lowest ROAS):",
  "ads.bottomAd": "  ▶ {{name}}\n    Cost: {{cost}} {ROAS: {{roas}}}\n    {{bidding}}\n    {{placement}}: {{keyword}}",
  "ads.bottomAdFallback": "  ▶ {{name}}\n    Cost: {{cost}} {ROAS: {{roas}}}\n    {{bidding}} {{placement}}: {{keyword}}",
  "ads.flag.autoUncontrolled": "📌 There are auto-bidding ads with uncontrolled costs (monitor 1-2x daily).",
  "ads.flag.manualUncontrolled": "📌 There are manual-bidding ads with uncontrolled costs (monitor 1-2x daily).",
  "ads.flag.keywordUncontrolled": "📌 There are manual keyword ads with uncontrolled costs (monitor 1-2x daily).",
  "ads.flag.autoBiddingUncontrolled": "📌 There are auto-bidding ads with uncontrolled costs (monitor 1-2x daily).",
  "ads.value.iklanProduk": "Product Ad",
  "ads.value.iklanToko": "Shop Ad",
  "ads.value.semuaPenempatan": "All Placement",
  "ads.value.halamanPencarian": "Search Page",
  "ads.value.halamanRekomendasi": "Recommendation Page",
  "ads.value.biddingOtomatis": "Auto Bidding",
  "ads.value.biddingManual": "Manual Bidding",
  "ads.value.gmvMaxAuto": "GMV Max Auto",
  "ads.value.gmvMaxRoas": "GMV Max ROAS",
```

**Step 3: Add corresponding keys to `th.json`**

```json
  "ads.topHeader": "• โฆษณา TOP (GMV สูงสุดพร้อม ROAS ดีที่สุด):",
  "ads.topHeaderFallback": "• โฆษณา TOP [fallback] (GMV สูงสุดพร้อม ROAS ดีที่สุด):",
  "ads.topAd": "  ▶ {{name}}\n    GMV: {{gmv}} {ROAS: {{roas}}}\n    {{bidding}}\n    {{placement}}: {{keyword}}",
  "ads.topRecommendation.auto": "📌 โฆษณาที่มีประสิทธิภาพดีที่สุดใช้การตั้งค่าอัตโนมัติ (โฆษณาร้านค้าแบบตั้งเองอาจยังไม่ได้ใช้งาน)",
  "ads.topRecommendation.manual": "📌 โฆษณาที่มีประสิทธิภาพดีที่สุดใช้การตั้งค่าเองแล้ว",
  "ads.bottomHeader": "• โฆษณา BOTTOM (ค่าใช้จ่ายสูงสุดพร้อม ROAS ต่ำสุด):",
  "ads.bottomHeaderFallback": "• โฆษณา BOTTOM [fallback] (ค่าใช้จ่ายสูงสุดพร้อม ROAS ต่ำสุด):",
  "ads.bottomAd": "  ▶ {{name}}\n    ค่าใช้จ่าย: {{cost}} {ROAS: {{roas}}}\n    {{bidding}}\n    {{placement}}: {{keyword}}",
  "ads.bottomAdFallback": "  ▶ {{name}}\n    ค่าใช้จ่าย: {{cost}} {ROAS: {{roas}}}\n    {{bidding}} {{placement}}: {{keyword}}",
  "ads.flag.autoUncontrolled": "📌 มีโฆษณาแบบอัตโนมัติที่ค่าใช้จ่ายไม่สามารถควบคุมได้ (แนะนำให้ตรวจสอบ 1-2 ครั้งต่อวัน)",
  "ads.flag.manualUncontrolled": "📌 มีโฆษณาแบบตั้งเองที่ค่าใช้จ่ายไม่สามารถควบคุมได้ (แนะนำให้ตรวจสอบ 1-2 ครั้งต่อวัน)",
  "ads.flag.keywordUncontrolled": "📌 มีคำค้นหาแบบตั้งเองที่ค่าใช้จ่ายไม่สามารถควบคุมได้ (แนะนำให้ตรวจสอบ 1-2 ครั้งต่อวัน)",
  "ads.flag.autoBiddingUncontrolled": "📌 มีโฆษณาแบบอัตโนมัติที่ค่าใช้จ่ายไม่สามารถควบคุมได้ (แนะนำให้ตรวจสอบ 1-2 ครั้งต่อวัน)",
  "ads.value.iklanProduk": "โฆษณาสินค้า",
  "ads.value.iklanToko": "โฆษณาร้านค้า",
  "ads.value.semuaPenempatan": "การจัดวางทั้งหมด",
  "ads.value.halamanPencarian": "หน้าค้นหา",
  "ads.value.halamanRekomendasi": "หน้าแนะนำ",
  "ads.value.biddingOtomatis": "บิดอัตโนมัติ",
  "ads.value.biddingManual": "บิดเอง",
  "ads.value.gmvMaxAuto": "GMV Max Auto",
  "ads.value.gmvMaxRoas": "GMV Max ROAS",
```

**Step 4: Commit**

```bash
git add frontend/src/locales/{id,en,th}.json
git commit -m "Add Sheet 2 (AL2-AL9) i18n keys to locale files"
```

---

### Task 2: Refactor AK4 backend to return individual flag i18n objects

Replace the single `ak4_i18n` object with a list of individual `TranslatableText` flag objects.

**Files:**
- Modify: `backend/app/calculators/ads_keyword.py:186-261`
- Test: `backend/tests/unit/calculators/test_ads_keyword_i18n.py`

**Step 1: Write failing tests**

Add new test class to `test_ads_keyword_i18n.py`:

```python
class TestSheet1I18nAk4Individual:
    """AK4 i18n: individual flag objects instead of single key."""

    def test_ak4_i18n_is_list_when_product_pct_below_50(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 100)  # 1/100 = 1% < 50%
        assert isinstance(result["ak4_i18n"], list)

    def test_ak4_i18n_first_flag_is_product_low_when_below_50(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 100)
        assert result["ak4_i18n"][0]["key"] == "ads.flag.productLow"

    def test_ak4_i18n_first_flag_is_product_good_when_above_50(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": f"Ad {i}",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"}
            for i in range(6)
        ]
        result = calculate_sheet1(rows, 10)  # 6/10 = 60% > 50%
        assert result["ak4_i18n"][0]["key"] == "ads.flag.productGood"

    def test_ak4_i18n_has_active_low_flag_when_below_50(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
            {"Status": "Berakhir", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 2",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
            {"Status": "Berakhir", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 3",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 100)  # 1/3 active = 33% < 50%
        keys = [f["key"] for f in result["ak4_i18n"]]
        assert "ads.flag.activeLow" in keys

    def test_ak4_i18n_has_no_shop_ad_flag_when_no_toko(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 100)
        keys = [f["key"] for f in result["ak4_i18n"]]
        assert "ads.flag.noShopAd" in keys

    def test_ak4_i18n_no_shop_ad_flag_absent_when_toko_exists(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Toko", "Nama Iklan": "Shop Ad",
             "Penempatan Iklan": "Halaman Pencarian", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 100)
        keys = [f["key"] for f in result["ak4_i18n"]]
        assert "ads.flag.noShopAd" not in keys
```

**Step 2: Run tests to verify they fail**

```bash
cd backend && uv run pytest tests/unit/calculators/test_ads_keyword_i18n.py::TestSheet1I18nAk4Individual -v
```

Expected: FAIL — `ak4_i18n` is a dict, not a list.

**Step 3: Implement — refactor `calculate_sheet1` AK4 i18n section**

In `ads_keyword.py`, replace lines 249-256 (the single `ak4_i18n = {...}` block) with:

```python
    # --- AK4 i18n: individual flag objects ---
    ak4_i18n_flags: list[dict[str, Any]] = []

    if product_pct < 0.5:
        ak4_i18n_flags.append({"key": "ads.flag.productLow", "vars": {}})
    else:
        ak4_i18n_flags.append({"key": "ads.flag.productGood", "vars": {}})

    if active_ratio < 0.5:
        ak4_i18n_flags.append({"key": "ads.flag.activeLow", "vars": {}})
    elif product_pct >= 0.5:
        ak4_i18n_flags.append({"key": "ads.flag.activeGood", "vars": {}})

    if not any(j == "Iklan Toko" for j in all_jenis):
        ak4_i18n_flags.append({"key": "ads.flag.noShopAd", "vars": {}})

    ak4_i18n = ak4_i18n_flags
```

Update the return dict to use `ak4_i18n` (variable name stays the same).

**Step 4: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/unit/calculators/test_ads_keyword_i18n.py -v
```

Expected: All pass. Note: old `TestSheet1I18nAk4` tests that check `ak4_i18n["key"]` will now fail — update them to check `ak4_i18n[0]["key"]` etc., or remove them since the new tests are more complete.

**Step 5: Fix broken old AK4 i18n tests**

Remove the old `TestSheet1I18nAk4` class from `test_ads_keyword_i18n.py` since `TestSheet1I18nAk4Individual` supersedes it.

**Step 6: Run all ads keyword tests**

```bash
cd backend && uv run pytest tests/unit/calculators/test_ads_keyword.py tests/unit/calculators/test_ads_keyword_i18n.py -v
```

Expected: All pass.

**Step 7: Commit**

```bash
git add backend/app/calculators/ads_keyword.py backend/tests/unit/calculators/test_ads_keyword_i18n.py
git commit -m "Refactor AK4 i18n to return individual flag objects"
```

---

### Task 3: Add Sheet 2 i18n objects to backend calculator

Add `_i18n` objects for AL2, AL3, AL5, AL6-AL9 in `calculate_sheet2`.

**Files:**
- Modify: `backend/app/calculators/ads_keyword.py:268-516`
- Create: `backend/tests/unit/calculators/test_ads_keyword_sheet2_i18n.py`

**Step 1: Write failing tests for AL2 (TOP ads) i18n**

Create `backend/tests/unit/calculators/test_ads_keyword_sheet2_i18n.py`:

```python
"""Tests for Sheet 2 i18n structured data in ads keyword calculator."""

from app.calculators.ads_keyword import calculate_sheet2


def _kw_row(name="Ad 1", jenis="Iklan Produk", penempatan="Semua Penempatan",
            bidding="GMV Max Auto", biaya=50000, gmv=200000, roas=5.0,
            kata="Pilih Otomatis", status="Berjalan"):
    return {
        "Nama Iklan": name,
        "Jenis Iklan": jenis,
        "Penempatan Iklan": penempatan,
        "Mode Bidding": bidding,
        "Biaya": biaya,
        "Omzet Penjualan": gmv,
        "Efektifitas Iklan": roas,
        "Kata Pencarian/Penempatan": kata,
        "Status": status,
    }


class TestSheet2I18nAl2:
    """AL2 i18n: TOP ads."""

    def test_has_al2_i18n_key(self):
        rows = [_kw_row(gmv=500000, roas=12)]
        result = calculate_sheet2(rows)
        assert "al2_i18n" in result

    def test_al2_i18n_has_header_key(self):
        rows = [_kw_row(gmv=500000, roas=12)]
        result = calculate_sheet2(rows)
        assert result["al2_i18n"]["header"]["key"] == "ads.topHeader"

    def test_al2_i18n_has_ads_list(self):
        rows = [_kw_row(gmv=500000, roas=12)]
        result = calculate_sheet2(rows)
        assert isinstance(result["al2_i18n"]["ads"], list)
        assert len(result["al2_i18n"]["ads"]) >= 1

    def test_al2_i18n_ad_has_name_var(self):
        rows = [_kw_row(name="Test Product", gmv=500000, roas=12)]
        result = calculate_sheet2(rows)
        assert result["al2_i18n"]["ads"][0]["vars"]["name"] == "Test Product"

    def test_al2_i18n_empty_when_no_top_ads(self):
        rows = [_kw_row(gmv=0, roas=0)]
        result = calculate_sheet2(rows)
        assert result["al2_i18n"] is None


class TestSheet2I18nAl3:
    """AL3 i18n: top recommendation."""

    def test_has_al3_i18n_key(self):
        rows = [_kw_row(gmv=500000, roas=12, bidding="Bidding Otomatis")] * 4
        result = calculate_sheet2(rows)
        assert "al3_i18n" in result

    def test_al3_i18n_is_auto_when_auto_count_gte_3(self):
        rows = [_kw_row(gmv=500000, roas=12, bidding="Bidding Otomatis")] * 4
        result = calculate_sheet2(rows)
        assert result["al3_i18n"]["key"] == "ads.topRecommendation.auto"

    def test_al3_i18n_is_manual_when_not_auto(self):
        rows = [_kw_row(gmv=500000, roas=12, bidding="Bidding Manual")] * 4
        result = calculate_sheet2(rows)
        assert result["al3_i18n"]["key"] == "ads.topRecommendation.manual"


class TestSheet2I18nAl5:
    """AL5 i18n: BOTTOM ads."""

    def test_has_al5_i18n_key(self):
        rows = [_kw_row(biaya=200000, roas=0.5, gmv=10000)]
        result = calculate_sheet2(rows)
        assert "al5_i18n" in result

    def test_al5_i18n_empty_when_no_bottom_ads(self):
        rows = [_kw_row(biaya=100, roas=10, gmv=500000)]
        result = calculate_sheet2(rows)
        assert result["al5_i18n"] is None


class TestSheet2I18nAl6Al9:
    """AL6-AL9 i18n: bottom flags."""

    def test_has_al6_i18n_key(self):
        rows = [_kw_row(biaya=200000, roas=0.5, gmv=10000, bidding="GMV Max Auto")]
        result = calculate_sheet2(rows)
        assert "al6_i18n" in result

    def test_al6_i18n_is_auto_uncontrolled(self):
        rows = [_kw_row(biaya=200000, roas=0.5, gmv=10000, bidding="GMV Max Auto")]
        result = calculate_sheet2(rows)
        if result["al6_i18n"]:
            assert result["al6_i18n"]["key"] == "ads.flag.autoUncontrolled"

    def test_al7_i18n_is_manual_uncontrolled(self):
        rows = [_kw_row(biaya=200000, roas=0.5, gmv=10000, bidding="Bidding Manual")]
        result = calculate_sheet2(rows)
        if result["al7_i18n"]:
            assert result["al7_i18n"]["key"] == "ads.flag.manualUncontrolled"
```

**Step 2: Run tests to verify they fail**

```bash
cd backend && uv run pytest tests/unit/calculators/test_ads_keyword_sheet2_i18n.py -v
```

Expected: FAIL — `al2_i18n` not in result.

**Step 3: Implement — add i18n to `calculate_sheet2`**

In `ads_keyword.py`, after the AL2 text generation (around line 408), add i18n:

```python
    # --- AL2 i18n ---
    if top_ads:
        header_key = "ads.topHeaderFallback" if is_top_fallback else "ads.topHeader"
        al2_i18n = {
            "header": {"key": header_key, "vars": {}},
            "ads": [
                {
                    "key": "ads.topAd",
                    "vars": {
                        "name": clean_name(_safe_str(ad.get("Nama Iklan"))),
                        "gmv": _format_idr(_safe_num(ad.get("Omzet Penjualan"))),
                        "roas": _format_roas(_safe_num(ad.get("Efektifitas Iklan"))),
                        "bidding": _safe_str(ad.get("Mode Bidding")),
                        "placement": f"{_safe_str(ad.get('Jenis Iklan'))} {_safe_str(ad.get('Penempatan Iklan'))}",
                        "keyword": _safe_str(ad.get("Kata Pencarian/Penempatan")),
                    },
                }
                for ad in top_ads
            ],
        }
    else:
        al2_i18n = None
```

After AL3 text (around line 425):

```python
    # --- AL3 i18n ---
    if auto_count >= 3 or gmv_max_count >= 3:
        al3_i18n = {"key": "ads.topRecommendation.auto", "vars": {}}
    else:
        al3_i18n = {"key": "ads.topRecommendation.manual", "vars": {}}
```

After AL5 text (around line 472):

```python
    # --- AL5 i18n ---
    if bottom_ads:
        header_key = "ads.bottomHeaderFallback" if is_bottom_fallback else "ads.bottomHeader"
        ad_key = "ads.bottomAdFallback" if is_bottom_fallback else "ads.bottomAd"
        al5_i18n = {
            "header": {"key": header_key, "vars": {}},
            "ads": [
                {
                    "key": ad_key,
                    "vars": {
                        "name": clean_name(_safe_str(ad.get("Nama Iklan"))),
                        "cost": _format_idr(_safe_num(ad.get("Biaya"))),
                        "roas": _format_roas(_safe_num(ad.get("Efektifitas Iklan"))),
                        "bidding": _safe_str(ad.get("Mode Bidding")),
                        "placement": f"{_safe_str(ad.get('Jenis Iklan'))} {_safe_str(ad.get('Penempatan Iklan'))}",
                        "keyword": _safe_str(ad.get("Kata Pencarian/Penempatan")),
                    },
                }
                for ad in bottom_ads
            ],
        }
    else:
        al5_i18n = None
```

After AL6-AL9 text (around line 503):

```python
    # --- AL6-AL9 i18n ---
    al6_i18n = {"key": "ads.flag.autoUncontrolled", "vars": {}} if al6 else None
    al7_i18n = {"key": "ads.flag.manualUncontrolled", "vars": {}} if al7 else None
    al8_i18n = {"key": "ads.flag.keywordUncontrolled", "vars": {}} if al8 else None
    al9_i18n = {"key": "ads.flag.autoBiddingUncontrolled", "vars": {}} if al9 else None
```

Add all `_i18n` keys to the return dict:

```python
    return {
        "al2": al2, "al3": al3, "al5": al5,
        "al6": al6, "al7": al7, "al8": al8, "al9": al9,
        "al2_i18n": al2_i18n, "al3_i18n": al3_i18n, "al5_i18n": al5_i18n,
        "al6_i18n": al6_i18n, "al7_i18n": al7_i18n, "al8_i18n": al8_i18n, "al9_i18n": al9_i18n,
        "thresholds": thresholds,
        "is_top_fallback": is_top_fallback,
        "is_bottom_fallback": is_bottom_fallback,
    }
```

**Step 4: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/unit/calculators/test_ads_keyword_sheet2_i18n.py tests/unit/calculators/test_ads_keyword.py -v
```

Expected: All pass.

**Step 5: Commit**

```bash
git add backend/app/calculators/ads_keyword.py backend/tests/unit/calculators/test_ads_keyword_sheet2_i18n.py
git commit -m "Add Sheet 2 (AL2-AL9) i18n objects to ads keyword calculator"
```

---

### Task 4: Pass i18n objects through to `details` dict

Ensure all `_i18n` keys from both sheets are included in the `details` dict returned by `calculate_ads_keyword()`.

**Files:**
- Modify: `backend/app/calculators/ads_keyword.py:547-586` (the `calculate_ads_keyword` function)
- Modify: `backend/tests/unit/calculators/test_ads_keyword.py` (add integration-level check)

**Step 1: Write failing test**

Add to `test_ads_keyword.py`:

```python
class TestCalculateAdsKeywordI18nPassthrough:
    """Verify i18n objects flow through to details dict."""

    def test_details_contains_ak2_i18n(self):
        cpc = [_mnd_cpc_row("Berjalan", "Iklan Produk", "Ad 1", "Semua Penempatan", "Bidding Otomatis")]
        kw = [_mnd_kw_row("Ad 1", "Iklan Produk", "Semua Penempatan", "GMV Max Auto", 50000, 200000, 5.0, "Pilih Otomatis")]
        result = calculate_ads_keyword(cpc, kw, 100)
        assert "ak2_i18n" in result.details

    def test_details_contains_al2_i18n(self):
        cpc = [_mnd_cpc_row("Berjalan", "Iklan Produk", "Ad 1", "Semua Penempatan", "Bidding Otomatis")]
        kw = [_mnd_kw_row("Ad 1", "Iklan Produk", "Semua Penempatan", "GMV Max Auto", 50000, 500000, 12.0, "Pilih Otomatis")]
        result = calculate_ads_keyword(cpc, kw, 100)
        assert "al2_i18n" in result.details
```

**Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/unit/calculators/test_ads_keyword.py::TestCalculateAdsKeywordI18nPassthrough -v
```

Expected: FAIL — `ak2_i18n` not in details.

**Step 3: Update `calculate_ads_keyword` to pass i18n through**

In `ads_keyword.py`, update the `details` dict construction (~line 571):

```python
    details = {
        "ak2": sheet1["ak2"],
        "ak3": sheet1["ak3"],
        "ak4": sheet1["ak4"],
        "ak2_i18n": sheet1["ak2_i18n"],
        "ak3_i18n": sheet1["ak3_i18n"],
        "ak4_i18n": sheet1["ak4_i18n"],
        "al2": sheet2["al2"],
        "al3": sheet2["al3"],
        "al5": sheet2["al5"],
        "al6": sheet2["al6"],
        "al7": sheet2["al7"],
        "al8": sheet2["al8"],
        "al9": sheet2["al9"],
        "al2_i18n": sheet2["al2_i18n"],
        "al3_i18n": sheet2["al3_i18n"],
        "al5_i18n": sheet2["al5_i18n"],
        "al6_i18n": sheet2["al6_i18n"],
        "al7_i18n": sheet2["al7_i18n"],
        "al8_i18n": sheet2["al8_i18n"],
        "al9_i18n": sheet2["al9_i18n"],
        "thresholds": sheet2["thresholds"],
    }
```

**Step 4: Run all backend tests**

```bash
cd backend && uv run pytest tests/unit/calculators/test_ads_keyword.py tests/unit/calculators/test_ads_keyword_i18n.py tests/unit/calculators/test_ads_keyword_sheet2_i18n.py -v
```

Expected: All pass.

**Step 5: Commit**

```bash
git add backend/app/calculators/ads_keyword.py backend/tests/unit/calculators/test_ads_keyword.py
git commit -m "Pass all i18n objects through to calculator details dict"
```

---

### Task 5: Update frontend TypeScript types for i18n fields

Add i18n fields to `AdsKeywordDetails` interface.

**Files:**
- Modify: `frontend/src/hooks/useCalculator.ts:4-21`

**Step 1: Update `AdsKeywordDetails` interface**

```typescript
export interface AdsKeywordDetails {
  ak2: string;
  ak3: string;
  ak4: string;
  al2: string;
  al3: string;
  al5: string;
  al6: string;
  al7: string;
  al8: string;
  al9: string;
  ak2_i18n?: { key: string; vars: Record<string, string> } | null;
  ak3_i18n?: { key: string; vars: Record<string, string> } | null;
  ak4_i18n?: Array<{ key: string; vars: Record<string, string> }> | null;
  al2_i18n?: {
    header: { key: string; vars: Record<string, string> };
    ads: Array<{ key: string; vars: Record<string, string> }>;
  } | null;
  al3_i18n?: { key: string; vars: Record<string, string> } | null;
  al5_i18n?: {
    header: { key: string; vars: Record<string, string> };
    ads: Array<{ key: string; vars: Record<string, string> }>;
  } | null;
  al6_i18n?: { key: string; vars: Record<string, string> } | null;
  al7_i18n?: { key: string; vars: Record<string, string> } | null;
  al8_i18n?: { key: string; vars: Record<string, string> } | null;
  al9_i18n?: { key: string; vars: Record<string, string> } | null;
  thresholds: {
    am6: number;
    am7: number;
    am9: number;
    am10: number;
  };
}
```

**Step 2: Commit**

```bash
git add frontend/src/hooks/useCalculator.ts
git commit -m "Add i18n fields to AdsKeywordDetails TypeScript interface"
```

---

### Task 6: Rewrite AdsKeywordResults component to use renderTranslatable

**Files:**
- Modify: `frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx`
- Modify: `frontend/src/components/evaluation/calculators/AdsKeywordResults.test.tsx`

**Step 1: Write failing test**

Update `AdsKeywordResults.test.tsx` — add test that verifies i18n rendering:

```tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AdsKeywordResults } from './AdsKeywordResults';
import type { CalculatorResult } from '../../../hooks/useCalculator';

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, vars?: Record<string, string>) => {
      // Simple mock: return key for flag keys, interpolate for others
      if (key.startsWith('ads.flag.')) return `[${key}]`;
      if (key.startsWith('ads.value.')) return `[${key}]`;
      if (vars && Object.keys(vars).length > 0) {
        let result = key;
        for (const [k, v] of Object.entries(vars)) {
          result += ` ${k}=${v}`;
        }
        return result;
      }
      return key;
    },
  }),
}));

const SAMPLE_RESULT_WITH_I18N: CalculatorResult = {
  calculator_type: 'ads_keyword',
  output_text: '• Total Iklan: 1 Aktif, 0 Dijeda dan 0 Berakhir.\n• Melibatkan 1 produk',
  details: {
    ak2: '• Total Iklan: 1 Aktif',
    ak3: 'breakdown',
    ak4: 'flags',
    al2: '',
    al3: '',
    al5: '',
    al6: '',
    al7: '',
    al8: '',
    al9: '',
    ak2_i18n: { key: 'ads.summary', vars: { active: '1', paused: '0', ended: '0', unique_count: '1', product_pct: '10.0%', total_products: '10' } },
    ak3_i18n: { key: 'ads.typeBreakdown', vars: { semua_total: '1', toko_total: '0', toko_auto: '0', toko_manual: '0' } },
    ak4_i18n: [{ key: 'ads.flag.productLow', vars: {} }],
    al2_i18n: null,
    al3_i18n: null,
    al5_i18n: null,
    al6_i18n: null,
    al7_i18n: null,
    al8_i18n: null,
    al9_i18n: null,
    thresholds: { am6: 0, am7: 0, am9: 0, am10: 0 },
  },
  calculated_at: '2026-02-11T10:00:00Z',
};

describe('AdsKeywordResults', () => {
  it('renders output_text preserving line breaks', () => {
    render(<AdsKeywordResults result={SAMPLE_RESULT_WITH_I18N} />);
    const pre = screen.getByRole('presentation');
    expect(pre).toBeInTheDocument();
    expect(pre.tagName).toBe('PRE');
  });

  it('renders translated content when i18n data is present', () => {
    render(<AdsKeywordResults result={SAMPLE_RESULT_WITH_I18N} />);
    // The mock t() returns key with vars, so we should see the translation key used
    expect(screen.getByRole('presentation').textContent).toContain('ads.summary');
  });

  it('renders calculated_at timestamp', () => {
    render(<AdsKeywordResults result={SAMPLE_RESULT_WITH_I18N} />);
    const time = screen.getByRole('time');
    expect(time).toBeInTheDocument();
  });

  it('falls back to raw text when no i18n data', () => {
    const resultNoI18n: CalculatorResult = {
      ...SAMPLE_RESULT_WITH_I18N,
      details: {
        ak2: 'raw ak2 text',
        ak3: 'raw ak3',
        ak4: 'raw ak4',
        al2: '', al3: '', al5: '', al6: '', al7: '', al8: '', al9: '',
        thresholds: { am6: 0, am7: 0, am9: 0, am10: 0 },
      },
    };
    render(<AdsKeywordResults result={resultNoI18n} />);
    expect(screen.getByRole('presentation').textContent).toContain('raw ak2 text');
  });
});
```

**Step 2: Run test to verify it fails**

```bash
cd frontend && npx vitest run src/components/evaluation/calculators/AdsKeywordResults.test.tsx
```

Expected: FAIL — component doesn't use `renderTranslatable`.

**Step 3: Implement — rewrite `AdsKeywordResults.tsx`**

```tsx
import { useTranslation } from 'react-i18next';
import type { CalculatorResult, AdsKeywordDetails } from '../../../hooks/useCalculator';
import { renderTranslatable } from '../../../utils/renderTranslatable';
import type { TranslatableText } from '../../../utils/renderTranslatable';

interface AdsKeywordResultsProps {
  result: CalculatorResult;
}

function renderAdList(
  fallbackText: string,
  i18n: { header: TranslatableText; ads: TranslatableText[] } | null | undefined,
  t: (key: string, vars?: Record<string, string>) => string,
): string {
  if (!i18n) return fallbackText;

  const header = t(i18n.header.key, i18n.header.vars);
  const ads = i18n.ads.map((ad) => t(ad.key, ad.vars)).join('\n');
  return `${header}\n${ads}`;
}

function renderFlagList(
  fallbackText: string,
  i18n: TranslatableText[] | null | undefined,
  t: (key: string, vars?: Record<string, string>) => string,
): string {
  if (!i18n) return fallbackText;
  return i18n.map((flag) => t(flag.key, flag.vars)).join('\n');
}

export function AdsKeywordResults({ result }: AdsKeywordResultsProps) {
  const { t } = useTranslation();
  const d = result.details as AdsKeywordDetails;

  const sections: string[] = [];

  // Sheet 1
  sections.push(renderTranslatable(d.ak2, d.ak2_i18n as TranslatableText | null | undefined, t));
  sections.push(renderTranslatable(d.ak3, d.ak3_i18n as TranslatableText | null | undefined, t));

  const ak4Text = renderFlagList(d.ak4, d.ak4_i18n, t);
  if (ak4Text) sections.push(ak4Text);

  // Sheet 2
  const al2Text = renderAdList(d.al2, d.al2_i18n, t);
  if (al2Text) sections.push(al2Text);

  const al3Text = renderTranslatable(d.al3, d.al3_i18n as TranslatableText | null | undefined, t);
  if (al3Text) sections.push(al3Text);

  const al5Text = renderAdList(d.al5, d.al5_i18n, t);
  if (al5Text) sections.push(al5Text);

  // Bottom flags
  for (const key of ['al6', 'al7', 'al8', 'al9'] as const) {
    const i18nKey = `${key}_i18n` as const;
    const text = renderTranslatable(d[key], d[i18nKey] as TranslatableText | null | undefined, t);
    if (text) sections.push(text);
  }

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold">Ads Keyword Calculator</h4>
        <time className="text-xs text-muted-foreground">
          {new Date(result.calculated_at).toLocaleString('id-ID')}
        </time>
      </div>
      <pre
        role="presentation"
        className="whitespace-pre-wrap break-words rounded-md bg-muted p-3 text-sm leading-relaxed"
      >
        {sections.filter(Boolean).join('\n\n')}
      </pre>
    </div>
  );
}
```

**Step 4: Run tests**

```bash
cd frontend && npx vitest run src/components/evaluation/calculators/AdsKeywordResults.test.tsx
```

Expected: All pass.

**Step 5: Run all frontend tests to check no regressions**

```bash
cd frontend && npx vitest run
```

Expected: All pass.

**Step 6: Commit**

```bash
git add frontend/src/components/evaluation/calculators/AdsKeywordResults.tsx frontend/src/components/evaluation/calculators/AdsKeywordResults.test.tsx
git commit -m "Rewrite AdsKeywordResults to use renderTranslatable for i18n"
```

---

### Task 7: Add CSV value translation keys for ad entry vars

The ad entry i18n vars contain raw Indonesian values like "Iklan Produk", "Bidding Otomatis". The backend passes these as vars, and the frontend needs to translate them using `$t()` nested references or by mapping them through `ads.value.*` keys.

**Approach:** In the backend, instead of passing raw Indonesian strings for bidding/placement, pass the i18n key reference. The frontend `ads.topAd` / `ads.bottomAd` templates use `$t()` to resolve them.

**Files:**
- Modify: `backend/app/calculators/ads_keyword.py` — change vars to use i18n key references
- Modify: `frontend/src/locales/id.json` — update ad templates to use `$t()`
- Modify: `frontend/src/locales/en.json` — update ad templates to use `$t()`
- Modify: `frontend/src/locales/th.json` — update ad templates to use `$t()`

**Step 1: Define value key mapping in backend**

Add a helper dict near the top of `ads_keyword.py`:

```python
# Mapping from Indonesian CSV values to i18n keys for frontend $t() resolution
_VALUE_I18N_KEYS: dict[str, str] = {
    "Iklan Produk": "ads.value.iklanProduk",
    "Iklan Toko": "ads.value.iklanToko",
    "Semua Penempatan": "ads.value.semuaPenempatan",
    "Halaman Pencarian": "ads.value.halamanPencarian",
    "Halaman Rekomendasi": "ads.value.halamanRekomendasi",
    "Bidding Otomatis": "ads.value.biddingOtomatis",
    "Bidding Manual": "ads.value.biddingManual",
    "GMV Max Auto": "ads.value.gmvMaxAuto",
    "GMV Max ROAS": "ads.value.gmvMaxRoas",
}


def _i18n_value(raw: str) -> str:
    """Return i18n key for a known CSV value, or the raw string."""
    return _VALUE_I18N_KEYS.get(raw, raw)
```

**Step 2: Use `_i18n_value()` in the ad entry i18n vars**

In the AL2/AL5 i18n construction, wrap bidding/jenis/penempatan:

```python
"bidding": _i18n_value(_safe_str(ad.get("Mode Bidding"))),
"placement": f"{_i18n_value(_safe_str(ad.get('Jenis Iklan')))} {_i18n_value(_safe_str(ad.get('Penempatan Iklan')))}",
```

Wait — for `$t()` interpolation to work with i18next, placement needs to be split. Update the template and vars:

Change ad vars to pass separate fields:

```python
"biddingKey": _i18n_value(_safe_str(ad.get("Mode Bidding"))),
"jenisKey": _i18n_value(_safe_str(ad.get("Jenis Iklan"))),
"penempatanKey": _i18n_value(_safe_str(ad.get("Penempatan Iklan"))),
```

**Step 3: Update locale templates to use `$t()`**

In all three locale files, update the ad templates:

```json
"ads.topAd": "  ▶ {{name}}\n    GMV: {{gmv}} {ROAS: {{roas}}}\n    $t({{biddingKey}})\n    $t({{jenisKey}}) $t({{penempatanKey}}): {{keyword}}",
"ads.bottomAd": "  ▶ {{name}}\n    $t(ads.label.cost): {{cost}} {ROAS: {{roas}}}\n    $t({{biddingKey}})\n    $t({{jenisKey}}) $t({{penempatanKey}}): {{keyword}}",
"ads.bottomAdFallback": "  ▶ {{name}}\n    $t(ads.label.cost): {{cost}} {ROAS: {{roas}}}\n    $t({{biddingKey}}) $t({{jenisKey}}) $t({{penempatanKey}}): {{keyword}}",
```

Also add `"ads.label.cost"` to each locale:
- id: `"ads.label.cost": "Biaya"`
- en: `"ads.label.cost": "Cost"`
- th: `"ads.label.cost": "ค่าใช้จ่าย"`

**Step 4: Run backend tests**

```bash
cd backend && uv run pytest tests/unit/calculators/ -v -k ads_keyword
```

**Step 5: Run frontend tests**

```bash
cd frontend && npx vitest run
```

**Step 6: Commit**

```bash
git add backend/app/calculators/ads_keyword.py frontend/src/locales/{id,en,th}.json
git commit -m "Add CSV value translation via i18next nested $t() references"
```

---

### Task 8: End-to-end verification

**Step 1: Run all backend tests**

```bash
cd backend && uv run pytest tests/unit/calculators/ -v
```

**Step 2: Run all frontend tests**

```bash
cd frontend && npx vitest run
```

**Step 3: Manual visual check**

If a dev server is available, load an evaluation with ads calculator results and verify:
- Indonesian text looks identical to before
- Switching to English shows translated labels/headers/flags
- Product names and numeric values remain unchanged

**Step 4: Final commit if any fixes needed**

```bash
git add -A && git commit -m "Fix any issues from e2e verification"
```
