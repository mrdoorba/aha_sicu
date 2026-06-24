// Barrel re-export for backward compatibility
export type {
  AdsData,
  BusinessData,
  CampaignData,
  CategoryDefinition,
  CompetitionData,
  CompetitionProduct,
  FieldDefinition,
  InputType,
  ManualData,
  OperationalData,
  ProductsData,
  PromoToolsData,
  SectionProgress,
  SelectOption,
  VisitorsData,
} from './types';
export { EMPTY_MANUAL_DATA } from './defaults';
export {
  ADS_FIELDS,
  BUSINESS_FIELDS,
  CAMPAIGN_FIELDS,
  COMPETITION_FIELDS,
  GENERIC_LABELS,
  MONTHS,
  MANUAL_DATA_FIELDS,
  OPERATIONAL_FIELDS,
  PROMO_TOOLS_FIELDS,
  PRODUCTS_FIELDS,
  STORE_STATUS_OPTIONS,
  VISITORS_FIELDS,
  getSectionLinks,
  getSellerBaseUrl,
  localizeSellerLink,
} from './fields';
export {
  computeSectionProgress,
  formatCurrency,
  generateMonthLabels,
  getCurrencyCode,
  parseCurrency,
} from './formUtils';
