"""HTML email template renderer for brand evaluation reports.

Produces cross-client-compatible HTML using table-based layout with inline CSS.
All images referenced via full src URI (cid: for send, data: for preview).
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PRIMARY_BLUE = "#1976D2"
GREEN = "#4CAF50"
ORANGE = "#FF9800"
BG_GRAY = "#f5f5f5"
WHITE = "#ffffff"
TEXT_DARK = "#212121"
TEXT_SECONDARY = "#757575"
CARD_BG = "#FAFAFA"

STRINGS: dict[str, dict[str, str]] = {
    "id": {
        "score_overview": "Ringkasan Skor",
        "detailed_evaluation": "Evaluasi Detail",
        "score_breakdown": "Rincian Skor",
        "data_intelligence": "Data Inteligensi",
        "ads_analysis": "Analisis Iklan",
        "top_sku": "Top SKU",
        "revenue_ranking": "Peringkat Omzet",
        "stock_ranking": "Peringkat Stok",
        "metric": "Metrik",
        "value": "Nilai",
        "benchmark": "Benchmark",
        "verdict": "Keputusan",
        "score": "Skor",
        "message": "Pesan",
        "approved": "Disetujui",
        "rejected": "Ditolak",
        "template_type": "Tipe Template",
        "check_count": "Lolos",
        "cross_count": "Tidak Lolos",
        "brand_report": "Laporan Evaluasi Brand",
    },
}

CATEGORY_MAP: dict[str, str] = {
    "Kesehatan Operasional Toko": "Operasional",
    "Bisnis Analisis": "Bisnis",
    "Tinjauan Pengunjung": "Pengunjung",
    "Promo Toko": "Alat Promo",
    "Jumlah Produk & Status Toko": "Produk & Status",
    "Data Iklan": "Iklan",
    "Partisipasi Campaign": "Campaign",
    "Kompetisi TOP Produk": "Kompetisi",
    "Stok": "Stok",
    "Discount": "Diskon",
}

S = STRINGS["id"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _score_color(score: float) -> str:
    """Return color hex based on score thresholds."""
    if score >= 80.0:
        return GREEN
    if score >= 50.0:
        return PRIMARY_BLUE
    return ORANGE


def _compute_verdict_counts(categories: list[dict[str, Any]]) -> dict[str, int]:
    """Count check marks and cross marks across all category rows."""
    checks = 0
    xs = 0
    for cat in categories:
        for row in cat.get("rows", []):
            verdict = row.get("verdict", "")
            if verdict == "\u2714\ufe0f":
                checks += 1
            elif verdict == "\u274c":
                xs += 1
    total = checks + xs
    return {"checks": checks, "xs": xs, "total": total}


def _esc(text: Any) -> str:
    """Escape HTML special characters."""
    s = str(text)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------------------------------------------------------------------------
# Section Renderers
# ---------------------------------------------------------------------------


def _render_header(
    header_src: str,
    brand_name: str,
    period: str,
    verdict: str,
    template: str,
) -> str:
    """Render header section: branded image + brand info."""
    return f"""\
<!-- Header Image -->
<tr>
  <td style="padding:0;margin:0;">
    <img src="{header_src}" width="600"
         style="display:block;width:100%;height:auto;border:0;"
         alt="AHA Commerce">
  </td>
</tr>
<!-- Brand Info -->
<tr>
  <td style="padding:24px 30px 16px 30px;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:24px;font-weight:bold;color:{TEXT_DARK};padding-bottom:4px;">
          {_esc(brand_name)}
        </td>
      </tr>
      <tr>
        <td style="font-size:14px;color:{TEXT_SECONDARY};padding-bottom:8px;">
          {_esc(period)}
        </td>
      </tr>
      <tr>
        <td style="padding-bottom:4px;">
          <span style="font-size:14px;color:{TEXT_DARK};font-weight:bold;">{verdict}</span>
          <span style="font-size:13px;color:{TEXT_SECONDARY};padding-left:12px;">
            {S['template_type']}: {_esc(template)}
          </span>
        </td>
      </tr>
    </table>
  </td>
</tr>"""


def _render_note(note: str) -> str:
    """Render custom note as a styled card.

    HTML-escapes the note text and converts newlines to <br> for
    line break preservation in the email.
    """
    escaped = _esc(note).replace("\n", "<br>")
    return f"""\
<!-- Custom Note -->
<tr>
  <td style="padding:8px 30px 16px 30px;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color:{CARD_BG};border-radius:6px;border-left:3px solid {PRIMARY_BLUE};">
      <tr>
        <td style="padding:14px 16px;font-size:13px;color:{TEXT_DARK};line-height:1.6;">
          {escaped}
        </td>
      </tr>
    </table>
  </td>
</tr>"""


def _render_score_overview(
    final_score: float,
    verdict: str,
    template: str,
    categories: list[dict[str, Any]],
) -> str:
    """Render score overview section: large score, progress bar, verdict counts."""
    color = _score_color(final_score)
    counts = _compute_verdict_counts(categories)
    score_pct = min(int(final_score), 100)

    return f"""\
<!-- Score Overview -->
<tr>
  <td style="padding:16px 30px 24px 30px;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <!-- Section header -->
      <tr>
        <td style="font-size:18px;font-weight:bold;color:{TEXT_DARK};padding-bottom:16px;border-bottom:2px solid {PRIMARY_BLUE};">
          {S['score_overview']}
        </td>
      </tr>
      <!-- Score number -->
      <tr>
        <td style="padding-top:16px;padding-bottom:8px;">
          <span style="font-size:48px;font-weight:bold;color:{color};">{final_score}</span>
          <span style="font-size:20px;color:{TEXT_SECONDARY};"> / 100</span>
        </td>
      </tr>
      <!-- Progress bar -->
      <tr>
        <td style="padding-bottom:16px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="background-color:#e0e0e0;border-radius:4px;height:12px;padding:0;">
                <table role="presentation" width="{score_pct}%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="background-color:{color};border-radius:4px;height:12px;font-size:0;line-height:0;">
                      &nbsp;
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <!-- Verdict counts -->
      <tr>
        <td>
          <table role="presentation" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="font-size:14px;color:{GREEN};padding-right:20px;">
                \u2714\ufe0f {S['check_count']}: {counts['checks']}
              </td>
              <td style="font-size:14px;color:{ORANGE};padding-right:20px;">
                \u274c {S['cross_count']}: {counts['xs']}
              </td>
              <td style="font-size:13px;color:{TEXT_SECONDARY};">
                {S['template_type']}: {_esc(template)}
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </td>
</tr>"""


def _render_footer(footer_src: str) -> str:
    """Render footer section: branded image."""
    return f"""\
<!-- Footer Image -->
<tr>
  <td style="padding:0;margin:0;">
    <img src="{footer_src}" width="600"
         style="display:block;width:100%;height:auto;border:0;"
         alt="AHA Commerce Footer">
  </td>
</tr>"""


# ---------------------------------------------------------------------------
# Detailed evaluation, score breakdown, data intelligence sections
# ---------------------------------------------------------------------------


def _render_metric_card(row: dict[str, Any]) -> str:
    """Render a single metric card as a table cell content block."""
    verdict_color = GREEN if row.get("verdict") == "\u2714\ufe0f" else ORANGE
    return f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background-color:{CARD_BG};border-radius:4px;margin-bottom:8px;">
  <tr>
    <td style="padding:10px 12px;font-family:Arial,Helvetica,sans-serif;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td style="font-size:13px;font-weight:bold;color:{TEXT_DARK};padding-bottom:4px;">
            {_esc(row.get('metric', ''))}
          </td>
        </tr>
        <tr>
          <td style="font-size:12px;color:{TEXT_SECONDARY};padding-bottom:2px;">
            {S['value']}: {_esc(row.get('value', ''))} | {S['benchmark']}: {_esc(row.get('benchmark', ''))}
          </td>
        </tr>
        <tr>
          <td style="font-size:12px;padding-bottom:2px;">
            <span style="color:{verdict_color};font-weight:bold;">{row.get('verdict', '')}</span>
            <span style="color:{TEXT_SECONDARY};"> | {S['score']}: {row.get('score', 0)}</span>
          </td>
        </tr>
        <tr>
          <td style="font-size:11px;color:{TEXT_SECONDARY};font-style:italic;">
            {_esc(row.get('message', ''))}
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>"""


def _render_detailed_evaluation(categories: list[dict[str, Any]]) -> str:
    """Render detailed evaluation section with all categories and metric cards."""
    if not categories:
        return ""

    sections: list[str] = []
    for cat in categories:
        cat_name = CATEGORY_MAP.get(cat.get("category", ""), cat.get("category", ""))
        cat_score = cat.get("score", 0)
        cat_max = cat.get("max_score", 0)
        cat_pct = int((cat_score / cat_max) * 100) if cat_max > 0 else 0
        cat_color = _score_color(cat_pct)

        rows = cat.get("rows", [])
        # Build 2-column grid of metric cards
        grid_rows: list[str] = []
        for i in range(0, len(rows), 2):
            left = _render_metric_card(rows[i])
            if i + 1 < len(rows):
                right = _render_metric_card(rows[i + 1])
            else:
                right = "&nbsp;"
            grid_rows.append(
                f'<tr>\n'
                f'  <td style="width:50%;padding:4px;vertical-align:top;">{left}</td>\n'
                f'  <td style="width:50%;padding:4px;vertical-align:top;">{right}</td>\n'
                f'</tr>'
            )

        grid_html = "\n".join(grid_rows)

        sections.append(f"""\
<!-- Category: {_esc(cat_name)} -->
<tr>
  <td style="padding:12px 30px 0 30px;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:15px;font-weight:bold;color:{TEXT_DARK};padding-bottom:6px;">
          {_esc(cat_name)}
          <span style="font-size:13px;color:{TEXT_SECONDARY};font-weight:normal;padding-left:8px;">
            {cat_score} / {cat_max}
          </span>
        </td>
      </tr>
      <!-- Category progress bar -->
      <tr>
        <td style="padding-bottom:10px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="background-color:#e0e0e0;border-radius:3px;height:8px;padding:0;">
                <table role="presentation" width="{cat_pct}%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="background-color:{cat_color};border-radius:3px;height:8px;font-size:0;line-height:0;">
                      &nbsp;
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <!-- Metric cards grid (2 columns) -->
      <tr>
        <td>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 class="metric-grid">
            {grid_html}
          </table>
        </td>
      </tr>
    </table>
  </td>
</tr>""")

    all_sections = "\n".join(sections)
    return f"""\
<!-- Detailed Evaluation -->
<tr>
  <td style="padding:16px 30px 8px 30px;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:18px;font-weight:bold;color:{TEXT_DARK};padding-bottom:16px;border-bottom:2px solid {PRIMARY_BLUE};">
          {S['detailed_evaluation']}
        </td>
      </tr>
    </table>
  </td>
</tr>
{all_sections}"""


def _render_score_breakdown(
    chart_src: str, categories: list[dict[str, Any]],
) -> str:
    """Render score breakdown section: chart image + category summary bars."""
    cat_bars: list[str] = []
    for cat in categories:
        cat_name = CATEGORY_MAP.get(cat.get("category", ""), cat.get("category", ""))
        cat_score = cat.get("score", 0)
        cat_max = cat.get("max_score", 0)
        cat_pct = int((cat_score / cat_max) * 100) if cat_max > 0 else 0
        cat_color = _score_color(cat_pct)

        # Per-category verdict counts
        checks = sum(1 for r in cat.get("rows", []) if r.get("verdict") == "\u2714\ufe0f")
        xs = sum(1 for r in cat.get("rows", []) if r.get("verdict") == "\u274c")

        cat_bars.append(f"""\
<tr>
  <td style="padding:4px 0;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:12px;color:{TEXT_DARK};width:120px;padding-right:8px;">
          {_esc(cat_name)}
        </td>
        <td style="padding:0;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="background-color:#e0e0e0;border-radius:3px;height:8px;padding:0;">
                <table role="presentation" width="{cat_pct}%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="background-color:{cat_color};border-radius:3px;height:8px;font-size:0;line-height:0;">
                      &nbsp;
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
        <td style="font-size:11px;color:{TEXT_SECONDARY};width:80px;text-align:right;padding-left:8px;">
          {cat_score}/{cat_max} | \u2714\ufe0f{checks} \u274c{xs}
        </td>
      </tr>
    </table>
  </td>
</tr>""")

    bars_html = "\n".join(cat_bars)
    return f"""\
<!-- Score Breakdown -->
<tr>
  <td style="padding:16px 30px 24px 30px;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:18px;font-weight:bold;color:{TEXT_DARK};padding-bottom:16px;border-bottom:2px solid {PRIMARY_BLUE};">
          {S['score_breakdown']}
        </td>
      </tr>
      <!-- Chart image -->
      <tr>
        <td style="padding-top:16px;padding-bottom:16px;">
          <img src="{chart_src}" width="600"
               style="display:block;width:100%;height:auto;border:0;"
               alt="Score Breakdown Chart">
        </td>
      </tr>
      <!-- Category summary bars -->
      {bars_html}
    </table>
  </td>
</tr>"""


def _render_ranking_table(
    title: str,
    rows: list[dict[str, Any]],
    value_key: str,
    max_rows: int = 3,
) -> str:
    """Render a ranking table (revenue or stock) limited to max_rows."""
    if not rows:
        return ""

    display_rows = rows[:max_rows]
    row_html_parts: list[str] = []
    for i, item in enumerate(display_rows):
        bg = WHITE if i % 2 == 0 else CARD_BG
        row_html_parts.append(
            f'<tr style="background-color:{bg};">'
            f'<td style="padding:6px 8px;font-size:12px;color:{TEXT_DARK};border:1px solid #e0e0e0;">{item.get("rank", i + 1)}</td>'
            f'<td style="padding:6px 8px;font-size:12px;color:{TEXT_DARK};border:1px solid #e0e0e0;">{_esc(item.get("product_name", ""))}</td>'
            f'<td style="padding:6px 8px;font-size:12px;color:{TEXT_DARK};border:1px solid #e0e0e0;text-align:right;">{item.get(value_key, "")}</td>'
            f'</tr>'
        )

    rows_html = "\n".join(row_html_parts)
    return f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="margin-top:8px;margin-bottom:12px;">
  <tr>
    <td style="font-size:13px;font-weight:bold;color:{TEXT_DARK};padding-bottom:6px;">
      {_esc(title)}
    </td>
  </tr>
  <tr>
    <td>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="border-collapse:collapse;">
        <tr style="background-color:{PRIMARY_BLUE};">
          <td style="padding:6px 8px;font-size:11px;color:{WHITE};font-weight:bold;border:1px solid #e0e0e0;width:40px;">#</td>
          <td style="padding:6px 8px;font-size:11px;color:{WHITE};font-weight:bold;border:1px solid #e0e0e0;">Produk</td>
          <td style="padding:6px 8px;font-size:11px;color:{WHITE};font-weight:bold;border:1px solid #e0e0e0;text-align:right;width:100px;">{_esc(value_key.replace('_', ' ').title())}</td>
        </tr>
        {rows_html}
      </table>
    </td>
  </tr>
</table>"""


def _render_data_intelligence(calculator_results: dict[str, Any]) -> str:
    """Render data intelligence section: ads analysis + top SKU tables."""
    if not calculator_results:
        return ""

    parts: list[str] = []

    # Ads keyword analysis
    ads = calculator_results.get("ads_keyword")
    if ads:
        output_text = ads.get("output_text", "")
        parts.append(f"""\
<tr>
  <td style="padding:8px 0;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:14px;font-weight:bold;color:{TEXT_DARK};padding-bottom:8px;">
          {S['ads_analysis']}
        </td>
      </tr>
      <tr>
        <td style="background-color:{CARD_BG};border-radius:4px;padding:12px;font-family:monospace,'Courier New',Courier;font-size:12px;color:{TEXT_DARK};white-space:pre-wrap;line-height:1.5;">
{_esc(output_text)}</td>
      </tr>
    </table>
  </td>
</tr>""")

    # Top SKU tables
    top_sku = calculator_results.get("top_sku")
    if top_sku:
        details = top_sku.get("details", {})
        revenue = details.get("revenue_ranking", [])
        stock = details.get("stock_ranking", [])

        revenue_table = _render_ranking_table(S["revenue_ranking"], revenue, "revenue")
        stock_table = _render_ranking_table(S["stock_ranking"], stock, "stock")

        parts.append(f"""\
<tr>
  <td style="padding:8px 0;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:14px;font-weight:bold;color:{TEXT_DARK};padding-bottom:8px;">
          {S['top_sku']}
        </td>
      </tr>
      <tr>
        <td>
          {revenue_table}
          {stock_table}
        </td>
      </tr>
    </table>
  </td>
</tr>""")

    if not parts:
        return ""

    all_parts = "\n".join(parts)
    return f"""\
<!-- Data Intelligence -->
<tr>
  <td style="padding:16px 30px 24px 30px;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:18px;font-weight:bold;color:{TEXT_DARK};padding-bottom:16px;border-bottom:2px solid {PRIMARY_BLUE};">
          {S['data_intelligence']}
        </td>
      </tr>
      {all_parts}
    </table>
  </td>
</tr>"""


# ---------------------------------------------------------------------------
# Main Renderer
# ---------------------------------------------------------------------------


def render_email_html(
    *,
    evaluation_data: dict[str, Any],
    chart_src: str,
    header_src: str,
    footer_src: str,
    note: str | None = None,
) -> str:
    """Render complete HTML email from evaluation data and image source URIs.

    Parameters
    ----------
    evaluation_data:
        Dict matching EvaluationDetailResponse shape.
    chart_src:
        Full src URI for the radar chart image (e.g. "cid:xxx" or "data:...").
    header_src:
        Full src URI for the header branded image.
    footer_src:
        Full src URI for the footer branded image.
    note:
        Optional custom note to render between header and score overview.

    Returns
    -------
    str
        Complete HTML document string for the email body.
    """
    brand_name: str = evaluation_data["brand_name"]
    period: str = evaluation_data["period"]
    final_score: float = evaluation_data["final_score"]
    verdict: str = evaluation_data["verdict"]
    template: str = evaluation_data["template"]
    categories: list[dict[str, Any]] = evaluation_data.get("score_breakdown", [])
    calculator_results: dict[str, Any] = evaluation_data.get("calculator_results", {})

    header = _render_header(header_src, brand_name, period, verdict, template)
    note_section = _render_note(note) if note else ""
    score_overview = _render_score_overview(final_score, verdict, template, categories)
    detailed = _render_detailed_evaluation(categories)
    breakdown = _render_score_breakdown(chart_src, categories)
    intelligence = _render_data_intelligence(calculator_results)
    footer = _render_footer(footer_src)

    return f"""\
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{_esc(brand_name)} - {S['brand_report']}</title>
<style type="text/css">
@media only screen and (max-width:620px) {{
  .metric-grid td {{ display:block !important; width:100% !important; }}
}}
</style>
</head>
<body style="margin:0;padding:0;background-color:{BG_GRAY};font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background-color:{BG_GRAY};">
  <tr>
    <td align="center" style="padding:20px 0;">
      <!-- Content table -->
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"
             style="width:100%;max-width:600px;background-color:{WHITE};border-radius:8px;">
        {header}
        {note_section}
        {score_overview}
        {detailed}
        {breakdown}
        {intelligence}
        {footer}
      </table>
    </td>
  </tr>
</table>
</body>
</html>"""
