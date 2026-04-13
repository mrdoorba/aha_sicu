import type { FileSlotConfig } from './FileUploadSlot';

export const FILE_UPLOAD_SLOTS: FileSlotConfig[] = [
  {
    label: 'fileUpload.slot.cpcAdReport',
    fileType: 'cpc_ad_report',
    accept: '.csv',
    format: '.csv',
    calculator: 'fileUpload.slot.cpcAdReportCalc',
    link: 'https://seller.shopee.co.id/portal/marketing/pas/assembly?&type=all&group=last-thirty-days',
  },
  {
    label: 'fileUpload.slot.keywordReport',
    fileType: 'keyword_report',
    accept: '.csv',
    format: '.csv',
    calculator: 'fileUpload.slot.keywordReportCalc',
    link: 'https://seller.shopee.co.id/portal/marketing/pas/assembly?&type=all&group=last-thirty-days',
  },
  {
    label: 'fileUpload.slot.orderExport',
    fileType: 'order_export',
    accept: '.xlsx,.zip',
    format: '.xlsx, .zip',
    calculator: 'fileUpload.slot.orderExportCalc',
    link: 'https://seller.shopee.co.id/portal/sale/order',
  },
  {
    label: 'fileUpload.slot.massUpdate',
    fileType: 'mass_update',
    accept: '.xlsx,.zip',
    format: '.xlsx, .zip',
    calculator: 'fileUpload.slot.massUpdateCalc',
    link: 'https://seller.shopee.co.id/portal/product-mass/mass-update/download',
  },
];

export const REQUIRED_UPLOAD_FILE_TYPES = FILE_UPLOAD_SLOTS.map((slot) => slot.fileType);
