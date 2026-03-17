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
  INDO_MONTHS,
  MANUAL_DATA_FIELDS,
  OPERATIONAL_FIELDS,
  PROMO_TOOLS_FIELDS,
  PRODUCTS_FIELDS,
  SECTION_LINKS,
  STORE_STATUS_OPTIONS,
  VISITORS_FIELDS,
} from './fields';
export {
  computeSectionProgress,
  formatCurrency,
  formatIDR,
  generateMonthLabels,
  getCurrencyCode,
  parseCurrency,
  parseIDR,
} from './formUtils';
