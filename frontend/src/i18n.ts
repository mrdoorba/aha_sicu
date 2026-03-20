import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const localeModules = import.meta.glob('./locales/*.json', { eager: true }) as Record<
  string,
  { default: Record<string, string> }
>;

const resources: Record<string, { translation: Record<string, string> }> = {};
for (const [path, module] of Object.entries(localeModules)) {
  const code = path.match(/\.\/locales\/(.+)\.json$/)?.[1];
  if (code) {
    resources[code] = { translation: module.default };
  }
}

i18n.use(initReactI18next).init({
  resources,
  lng: 'id',
  fallbackLng: 'id',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
