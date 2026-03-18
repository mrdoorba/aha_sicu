---
estimated_steps: 5
estimated_files: 5
---

# T02: Add labelKey to all 51 field definitions and displayNameKey to all 8 categories

**Slice:** S02 — Locale-aware dates, field labels, and month constants
**Milestone:** M004

## Description

Add the `labelKey` property to the `FieldDefinition` type and `displayNameKey` to `CategoryDefinition`, then populate these properties across all 51 field definitions and 8 category definitions in `fields.ts`. Add corresponding ~59 locale keys to all 3 JSON files. This is pure data work — no component changes. The keys will be consumed by form components in T03.

**Relevant skills:** none (mechanical data work)

## Steps

1. **In `frontend/src/components/evaluation/forms/types.ts`:**
   - Add `labelKey?: string` to the `FieldDefinition` interface
   - Add `displayNameKey?: string` to the `CategoryDefinition` interface

2. **In `frontend/src/components/evaluation/forms/fields.ts`:**
   - Add `labelKey` to every field definition across all 8 field arrays. The naming convention is `fields.<category>.<camelCaseKey>`. Complete list:

   **OPERATIONAL_FIELDS (5):**
   - `unfulfilledOrderRate` → `labelKey: 'fields.operational.unfulfilledOrderRate'`
   - `lateShipmentRate` → `labelKey: 'fields.operational.lateShipmentRate'`
   - `preparationTime` → `labelKey: 'fields.operational.preparationTime'`
   - `chatResponseRate` → `labelKey: 'fields.operational.chatResponseRate'`
   - `overallRating` → `labelKey: 'fields.operational.overallRating'`

   **BUSINESS_FIELDS (7):**
   - `salesMonth0` → `labelKey: 'fields.business.salesMonth0'`
   - `salesMonth1` → `labelKey: 'fields.business.salesMonth1'`
   - `salesMonth2` → `labelKey: 'fields.business.salesMonth2'`
   - `salesMonth3` → `labelKey: 'fields.business.salesMonth3'`
   - `salesMonth4` → `labelKey: 'fields.business.salesMonth4'`
   - `salesMonth5` → `labelKey: 'fields.business.salesMonth5'`
   - `conversionRate` → `labelKey: 'fields.business.conversionRate'`

   **VISITORS_FIELDS (3):**
   - `totalVisitors` → `labelKey: 'fields.visitors.totalVisitors'`
   - `returningVisitors` → `labelKey: 'fields.visitors.returningVisitors'`
   - `totalFollowers` → `labelKey: 'fields.visitors.totalFollowers'`

   **PROMO_TOOLS_FIELDS (11):**
   - `promoToko` → `labelKey: 'fields.promoTools.promoToko'`
   - `paketDiskon` → `labelKey: 'fields.promoTools.paketDiskon'`
   - `komboHemat` → `labelKey: 'fields.promoTools.komboHemat'`
   - `flashSale` → `labelKey: 'fields.promoTools.flashSale'`
   - `voucher` → `labelKey: 'fields.promoTools.voucher'`
   - `shopeeLive` → `labelKey: 'fields.promoTools.shopeeLive'`
   - `gameToko` → `labelKey: 'fields.promoTools.gameToko'`
   - `brandMembership` → `labelKey: 'fields.promoTools.brandMembership'`
   - `gratisOngkir` → `labelKey: 'fields.promoTools.gratisOngkir'`
   - `chatBroadcast` → `labelKey: 'fields.promoTools.chatBroadcast'`
   - `programAfiliasi` → `labelKey: 'fields.promoTools.programAfiliasi'`

   **PRODUCTS_FIELDS (2):**
   - `productCount` → `labelKey: 'fields.products.productCount'`
   - `storeStatus` → `labelKey: 'fields.products.storeStatus'`

   **ADS_FIELDS (2):**
   - `adSales` → `labelKey: 'fields.ads.adSales'`
   - `adCost` → `labelKey: 'fields.ads.adCost'`

   **CAMPAIGN_FIELDS (2):**
   - `nominatedSessions` → `labelKey: 'fields.campaign.nominatedSessions'`
   - `availableSessions` → `labelKey: 'fields.campaign.availableSessions'`

   **COMPETITION_FIELDS (15):**
   - `product1.productName` → `labelKey: 'fields.competition.product1.productName'`
   - `product1.sellingPrice` → `labelKey: 'fields.competition.product1.sellingPrice'`
   - `product1.keyword` → `labelKey: 'fields.competition.product1.keyword'`
   - `product1.link` → `labelKey: 'fields.competition.product1.link'`
   - `product1.marketPrice` → `labelKey: 'fields.competition.product1.marketPrice'`
   - (Same pattern for product2.* and product3.*)

   **MANUAL_DATA_FIELDS displayNameKey (8):**
   - `operational` → `displayNameKey: 'categories.operational'`
   - `business` → `displayNameKey: 'categories.business'`
   - `visitors` → `displayNameKey: 'categories.visitors'`
   - `promoTools` → `displayNameKey: 'categories.promoTools'`
   - `products` → `displayNameKey: 'categories.products'`
   - `ads` → `displayNameKey: 'categories.ads'`
   - `campaign` → `displayNameKey: 'categories.campaign'`
   - `competition` → `displayNameKey: 'categories.competition'`

3. **Add locale keys to all 3 JSON files** (`frontend/src/locales/{id,en,th}.json`):
   - Add `"fields"` namespace with sub-namespaces for each category
   - Add `"categories"` namespace with 8 entries
   - Indonesian values = the current hardcoded `label`/`displayName` strings (preserving exact text)
   - English values = professional English translations
   - Thai values = professional Thai translations
   - Total: 47 field labelKeys (51 minus 4 already keyed elsewhere) + 8 category displayNameKeys ≈ 55+ new keys per file

   **Key translations for categories:**
   | Key | id | en | th |
   |-----|----|----|-----|
   | categories.operational | Kesehatan Operasional Toko | Store Operational Health | สุขภาพการดำเนินงานร้านค้า |
   | categories.business | Bisnis Analisis | Business Analysis | การวิเคราะห์ธุรกิจ |
   | categories.visitors | Tinjauan Pengunjung | Visitor Overview | ภาพรวมผู้เข้าชม |
   | categories.promoTools | Alat Promosi | Promotion Tools | เครื่องมือโปรโมชั่น |
   | categories.products | Produk/Status | Products/Status | สินค้า/สถานะ |
   | categories.ads | Data Iklan | Ads Data | ข้อมูลโฆษณา |
   | categories.campaign | Partisipasi Campaign | Campaign Participation | การเข้าร่วมแคมเปญ |
   | categories.competition | Kompetisi TOP Produk | Top Product Competition | การแข่งขันสินค้ายอดนิยม |

4. **Verify type safety:**
   - Run `cd frontend && npx tsc --noEmit` to ensure no type errors from the new optional properties
   - The `labelKey` is optional, so existing code using `field.label` continues to work

5. **Run tests:**
   - `cd frontend && npm run test:run` — all 612+ tests still pass (this is additive, nothing should break)

## Must-Haves

- [ ] `FieldDefinition` has `labelKey?: string` property
- [ ] `CategoryDefinition` has `displayNameKey?: string` property
- [ ] All 51 field definitions have `labelKey` populated with correct namespace keys
- [ ] All 8 MANUAL_DATA_FIELDS entries have `displayNameKey` populated
- [ ] All 3 locale files have matching new keys with correct translations
- [ ] All existing tests still pass

## Verification

- `cd frontend && npm run test:run` — all 612+ tests pass (additive change, nothing breaks)
- `cd frontend && npx tsc --noEmit` — no type errors
- Spot-check: `grep -c "labelKey" frontend/src/components/evaluation/forms/fields.ts` — should be ≥51
- Spot-check: `grep -c "displayNameKey" frontend/src/components/evaluation/forms/fields.ts` — should be 8

## Observability Impact

- **New signals:** `labelKey` and `displayNameKey` properties on field/category definitions. When a key is missing from a locale JSON file, `react-i18next` returns the raw key string (e.g. `"fields.operational.unfulfilledOrderRate"`) instead of translated text — this is the primary failure signal visible in the UI.
- **Inspection commands:**
  - `grep -c "labelKey" frontend/src/components/evaluation/forms/fields.ts` — should return ≥51
  - `grep -c "displayNameKey" frontend/src/components/evaluation/forms/fields.ts` — should return 8
  - `python3 -c "import json; [print(f'{f}: {len(json.load(open(f)))}') for f in ['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']]"` — all 3 files should have equal key counts
- **Failure state:** If any `fields.*` or `categories.*` key is missing from a locale file, the UI renders the raw key string. TypeScript compilation catches type errors on the new optional properties.

## Inputs

- T01 completed: `MONTHS` renamed, `GENERIC_LABELS` has i18n keys, 6 `generic.*` locale keys added
- `frontend/src/components/evaluation/forms/types.ts` — `FieldDefinition` and `CategoryDefinition` interfaces to extend
- `frontend/src/components/evaluation/forms/fields.ts` — 51 field definitions + 8 category definitions to annotate
- `frontend/src/locales/{id,en,th}.json` — locale files to extend (currently ~630 keys each)

## Expected Output

- `frontend/src/components/evaluation/forms/types.ts` — `labelKey?: string` on FieldDefinition, `displayNameKey?: string` on CategoryDefinition
- `frontend/src/components/evaluation/forms/fields.ts` — all 51 fields have `labelKey`, all 8 categories have `displayNameKey`
- `frontend/src/locales/{id,en,th}.json` — ~55+ new keys each under `fields.*` and `categories.*` namespaces
