/**
 * Reducing the email's verdict sentence to the part the row hasn't said yet.
 *
 * The email writes a verdict as a whole sentence — "✔️ Tingkat Pesanan Tidak
 * Terselesaikan = 0.0% [Sudah Baik]" — because an email has no layout to lean
 * on. On the page the metric name and its value are already printed on the
 * same row, so the sentence repeats them a third of the way down every card.
 * That repetition is what made the first build of this page unreadable.
 *
 * Nothing is lost: only the duplicated prefix goes. The full sentence is still
 * carried on the element's `title`, so the exact wording BD asked us to match
 * is one hover away and present in the DOM.
 */

const LEADING_GLYPH = /^[✔✅❌✗×]️?\s*/u;

/** `[clause]` plus whatever follows it — a tip line, usually. */
const BRACKETED = /\[([^\]]*)\]\s*([\s\S]*)$/;

export function verdictClause(full: string): string {
  const text = full.replace(LEADING_GLYPH, '').trim();
  const match = text.match(BRACKETED);
  if (!match) return text;

  const [, clause, trailing] = match;
  // A verdict can carry a 💡 tip after the bracket (storeStatus does). Dropping
  // it would lose advice the brand was given, so it is kept on its own line.
  return [clause.trim(), trailing.trim()].filter(Boolean).join('\n');
}
