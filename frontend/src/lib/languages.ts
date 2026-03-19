export const LANGUAGES = [
  { code: 'id' as const, flag: '🇮🇩', label: 'ID' },
  { code: 'en' as const, flag: '🇬🇧', label: 'EN' },
  { code: 'th' as const, flag: '🇹🇭', label: 'TH' },
];

export type LanguageCode = (typeof LANGUAGES)[number]['code'];
