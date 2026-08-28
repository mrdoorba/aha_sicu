# Domain glossary — aha_sicu

Names for the seams worth naming. Add terms here as the model sharpens; don't
catalogue every noun.

## Evaluation & scoring

- **Evaluation** — one brand's scored report for a period. Produced by the
  scoring calculator from manual inputs + uploaded calculator data.
- **ScoringResult** — the computed evaluation: category scores, verdict,
  conclusion, marketing estimate, and the assembled email fields.
- **Real Benchmark** — the revenue figure a partnership is actually judged on:
  order-list omset *less cancellations*. Computable only once the brand submits
  the registration form, so an evaluation never carries it. Distinct from a
  `RowScore`'s **benchmark**, which is the threshold a metric is scored against.
- **Seller Center omset** — the revenue read off Seller Center and plotted as
  the sales trend. Decides the cooperation scheme only; it is never the Real
  Benchmark, and the trend card and email say so in as many words.
- **Category** — one scored section of an evaluation (operational, business,
  visitors, promo tools, products/status, ads, campaign, competition, stock).
  Carries `RowScore` rows.

## Email report

- **Email report** — the evaluation rendered for sending to a brand. Two
  surfaces, one layout: a **branded HTML** mail (dashboard flow) and a
  **plain-text** mail (evaluation-page flow, via Gmail SMTP). Neither carries a
  chart; the trend chart is a dashboard-only view.
- **Email layout** — the single ordered description of the report: which
  categories appear, in what order, their header label + emoji, and the row
  filters per category (e.g. business shows rows 13 & 20). The deep module
  `email layout` owns this; HTML and plain-text renderers both read it and
  must never re-encode it. One source, two emitters.
- **Section note** — a standing disclaimer closing a section, about *how to read*
  its numbers rather than about this brand. Fixed copy, so it renders whenever
  its section does, regardless of which rows are present. Declared on the email
  layout and read by both emitters and the dashboard card, so one wording
  reaches the prospect on every surface.
- **Email renderer** — turns a `ScoringResult` + language + format into the
  report text/HTML. The seam the frontend crosses (via `/email/preview`)
  instead of re-assembling the layout itself.

## Brand lookup

- **Brand lookup** — finding *one* brand by typed text, to open it. Distinct
  from **brand browsing**, which pages through the whole roster. Both read the
  same brand list, but lookup is judged on whether the brand you meant is
  visible without paging; browsing is judged on stable, predictable order.
- **Match tier** — how closely a brand's name answers the typed text: **exact**,
  then **prefix**, then **substring**. Lookup orders by tier first and
  alphabetically within a tier; browsing (no text typed) is alphabetical only.
  A name that *is* the query outranks 49 names that merely contain it.
- **Marketplace** — the storefront a brand sells on (`ID`, `TH`). A brand is
  identified by name *and* marketplace, never name alone: the same name can
  exist in both, and lookup results must show which one is which.
