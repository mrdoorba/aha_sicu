import type { ManualData } from './types';

export const EMPTY_MANUAL_DATA: ManualData = {
  operational: {
    unfulfilledOrderRate: null,
    lateShipmentRate: null,
    preparationTime: null,
    chatResponseRate: null,
    overallRating: null,
  },
  business: {
    salesStartMonth: null,
    salesMonth0: null,
    salesMonth1: null,
    salesMonth2: null,
    salesMonth3: null,
    salesMonth4: null,
    salesMonth5: null,
    conversionRate: null,
  },
  visitors: {
    totalVisitors: null,
    totalFollowers: null,
    returningVisitors: null,
  },
  promoTools: {
    promoToko: null,
    paketDiskon: null,
    komboHemat: null,
    flashSale: null,
    voucher: null,
    shopeeLive: null,
    gameToko: null,
    brandMembership: null,
    gratisOngkir: null,
    chatBroadcast: null,
    programAfiliasi: null,
    komisiProgramAfiliasi: null,
  },
  products: {
    productCount: null,
    storeStatus: null,
  },
  ads: {
    adSales: null,
    adCost: null,
  },
  campaign: {
    nominatedSessions: null,
    availableSessions: null,
  },
  competition: {
    product1: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
  },
};
