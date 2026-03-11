# Ads Calculator i18n Design

## Goal

Add full translation support to the ads keyword calculator output, following the same `TranslatableText` pattern used by the scoring calculator.

## Current State

- Sheet 1 (AK2, AK3, AK4) already returns `_i18n` objects but they're unused by the frontend
- Sheet 2 (AL2-AL9: TOP/BOTTOM ads, flags) has zero i18n support — hardcoded Indonesian only
- Frontend `AdsKeywordResults.tsx` renders raw `output_text` as a single `<pre>` block, ignoring all i18n data

## Design

### Scope

- **Output only** — no changes to CSV parsing/input normalization
- Translate labels, headers, and CSV-origin display values (e.g., "Iklan Produk" → "Product Ad")
- Keep product names and numeric values as-is
- Visual output stays identical (single `<pre>` block)

### 1. Backend — `ads_keyword.py`

Add `TranslatableText` i18n objects for all Sheet 2 outputs:

**AL2 (TOP ads):**
- Header: `ads.topHeader` / `ads.topHeaderFallback`
- Each ad entry: `ads.topAd` with vars: `name`, `gmv`, `roas`, `bidding`, `placement`, `keyword`

**AL3 (top recommendation):**
- `ads.topRecommendation.auto` / `ads.topRecommendation.manual`

**AL5 (BOTTOM ads):**
- Header: `ads.bottomHeader` / `ads.bottomHeaderFallback`
- Each ad entry: `ads.bottomAd` / `ads.bottomAdFallback` with vars: `name`, `cost`, `roas`, `bidding`, `placement`, `keyword`

**AL6-AL9 (bottom flags):**
- `ads.flag.autoUncontrolled`
- `ads.flag.manualUncontrolled`
- `ads.flag.keywordUncontrolled`
- `ads.flag.autoBiddingUncontrolled`

**AK4 flags (already have i18n as single object, split into individual flags):**
- `ads.flag.productLow` / `ads.flag.productGood`
- `ads.flag.activeLow` / `ads.flag.activeGood`
- `ads.flag.noShopAd`

Return all `_i18n` objects in the `details` dict alongside existing text fields.

### 2. Frontend — Locale Files

Add keys to `id.json`, `en.json`, `th.json`:

**Headers:**
- `ads.topHeader`: "• TOP Ads (highest GMV with best ROAS):"
- `ads.bottomHeader`: "• BOTTOM Ads (highest cost with lowest ROAS):"

**Ad entries (templated):**
- `ads.topAd`: "  ▶ {{name}}\n    GMV: {{gmv}} {ROAS: {{roas}}}\n    {{bidding}}\n    {{placement}}: {{keyword}}"
- `ads.bottomAd`: "  ▶ {{name}}\n    Cost: {{cost}} {ROAS: {{roas}}}\n    {{bidding}}\n    {{placement}}: {{keyword}}"

**Flags:**
- `ads.flag.productLow`: "📌 Product participation in ads is not optimal (recommended >50%)."
- `ads.flag.productGood`: "📌 Product participation in ads is good enough."
- `ads.flag.activeLow`: "📌 Number of active ads is not optimal (recommended >50%)."
- `ads.flag.activeGood`: "📌 Number of active ads is good enough."
- `ads.flag.noShopAd`: "📌 Shop Ads have not been utilized."
- `ads.topRecommendation.auto`: "📌 Best performing ads rely on automatic settings (manual shop ads may be underutilized)."
- `ads.topRecommendation.manual`: "📌 Best performing ads already rely on manual settings."
- `ads.flag.autoUncontrolled`: "📌 There are auto-bidding ads with uncontrolled costs (monitor 1-2x daily)."
- `ads.flag.manualUncontrolled`: "📌 There are manual-bidding ads with uncontrolled costs (monitor 1-2x daily)."
- `ads.flag.keywordUncontrolled`: "📌 There are manual keyword ads with uncontrolled costs (monitor 1-2x daily)."

**CSV value translations:**
- `ads.value.iklanProduk`: "Product Ad"
- `ads.value.iklanToko`: "Shop Ad"
- `ads.value.semuaPenempatan`: "All Placement"
- `ads.value.biddingOtomatis`: "Auto Bidding"
- `ads.value.biddingManual`: "Manual Bidding"
- `ads.value.gmvMaxAuto`: "GMV Max Auto"
- `ads.value.gmvMaxRoas`: "GMV Max ROAS"

### 3. Frontend — `AdsKeywordResults.tsx`

Rewrite to render each section individually using `renderTranslatable()`:

```tsx
<pre>
  {renderTranslatable(details.ak2, details.ak2_i18n, t)}
  {"\n\n"}
  {renderTranslatable(details.ak3, details.ak3_i18n, t)}
  {"\n\n"}
  {renderTranslatable(details.ak4, details.ak4_i18n, t)}
  {/* ... al2, al3, al5, al6-al9 ... */}
</pre>
```

Visual output remains identical — same `<pre>` block, same spacing.

### 4. API Response

No schema change needed. The `details` dict already exists — just adding `_i18n` keys alongside existing text fields.

## Pattern Reference

Follows the exact same pattern as the scoring calculator:
- Backend: `TranslatableText(key="...", vars={...})`
- Frontend: `renderTranslatable(fallbackText, i18nObj, t)`
- Locale files: `"key": "template with {{vars}}"`
