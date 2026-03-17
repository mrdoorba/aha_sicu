# Quick Task: Localize Shopee Seller Centre links by marketplace

**Date:** 2026-03-17
**Branch:** gsd/quick/1-in-the-evaluation-page-there-is-a-link-l

## What Changed
- Converted static `SECTION_LINKS` object to `getSectionLinks(marketplace)` function
- Added `localizeSellerLink()` and `getSellerBaseUrl()` utilities in `fields.ts`
- All 6 form components (Operational, Business, Visitors, PromoTools, Ads, Campaign) now accept `marketplace` prop
- PromoTools per-field links (Brand Membership, Gratis Ongkir, Chat Broadcast, Program Afiliasi) also localized
- FileUploadSection localizes all 4 file upload slot links (CPC Ad Report, Keyword Report, Order Export, Mass Update)
- EvaluationSections passes `marketplace` to all form components
- When marketplace=TH: `seller.shopee.co.id` → `seller.shopee.co.th`
- When marketplace=ID (default): links remain `seller.shopee.co.id`

## Files Modified
- `frontend/src/components/evaluation/forms/fields.ts` — new utilities + deprecated old constant
- `frontend/src/components/evaluation/forms/formConfig.ts` — barrel export updates
- `frontend/src/components/evaluation/forms/OperationalForm.tsx` — marketplace prop
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — marketplace prop
- `frontend/src/components/evaluation/forms/VisitorsForm.tsx` — marketplace prop
- `frontend/src/components/evaluation/forms/AdsForm.tsx` — marketplace prop
- `frontend/src/components/evaluation/forms/CampaignForm.tsx` — marketplace prop
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — marketplace prop + per-field link localization
- `frontend/src/components/evaluation/FileUploadSection.tsx` — marketplace prop + slot link localization
- `frontend/src/components/evaluation/EvaluationSections.tsx` — passes marketplace to all forms
- `frontend/src/components/evaluation/forms/sellerLinks.test.ts` — 10 new tests

## Verification
- 546 frontend tests pass (536 existing + 10 new)
- Visual browser verification: switching marketplace radio ID↔TH toggles all 14 seller links between co.id and co.th
