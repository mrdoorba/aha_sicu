import { describe, expect, it } from 'vitest';
import en from './en.json';
import id from './id.json';
import th from './th.json';

type Tree = Record<string, unknown>;

/**
 * The files are flat dotted keys with one exception (`emailBody` is nested), so
 * flatten before comparing rather than special-casing the one nesting.
 */
function flatten(tree: Tree, prefix = ''): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(tree)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === 'object') Object.assign(out, flatten(v as Tree, key));
    else out[key] = String(v);
  }
  return out;
}

const BASE = flatten(id as Tree);
const LOCALES: Record<string, Record<string, string>> = {
  id: BASE,
  en: flatten(en as Tree),
  th: flatten(th as Tree),
};

const placeholders = (s: string) => (s.match(/\{\{\s*\w+\s*\}\}/g) ?? []).sort().join();

/**
 * The three files must carry the same keys.
 *
 * A key present in id.json and missing from th.json does not throw — i18next
 * falls back to the key itself, so a Thai brand reads
 * 'onboarding.sub.hintPick' on the button hint and nothing anywhere reports it.
 * These files are also read by the backend's email renderer, so a gap here is a
 * gap in the email too.
 */
describe('locale files stay in step', () => {
  const baseKeys = Object.keys(BASE).sort();

  for (const [code, dict] of Object.entries(LOCALES)) {
    it(`${code}.json has exactly the same keys as id.json`, () => {
      expect(Object.keys(dict).filter((k) => !(k in BASE)), `extra in ${code}`).toEqual([]);
      expect(baseKeys.filter((k) => !(k in dict)), `missing from ${code}`).toEqual([]);
    });

    it(`${code}.json has no blank values`, () => {
      expect(Object.entries(dict).filter(([, v]) => v.trim() === '').map(([k]) => k)).toEqual([]);
    });

    it(`${code}.json keeps every placeholder id.json uses`, () => {
      // A dropped {{brandName}} silently prints a sentence with a hole in it.
      expect(
        baseKeys.filter((k) => k in dict && placeholders(BASE[k]) !== placeholders(dict[k])),
      ).toEqual([]);
    });
  }
});
