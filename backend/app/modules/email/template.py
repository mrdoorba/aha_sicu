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
PRIMARY_LIGHT = "#E3F2FD"
GREEN = "#4CAF50"
GREEN_LIGHT = "#E8F5E9"
ORANGE = "#FF9800"
ORANGE_LIGHT = "#FFF3E0"
BG_GRAY = "#f5f5f5"
WHITE = "#ffffff"
TEXT_DARK = "#212121"
TEXT_SECONDARY = "#757575"
CARD_BG = "#FAFAFA"
BORDER_LIGHT = "#e0e0e0"

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
        "average_stock": "Rata-rata Stok",
        "product_code": "Kode Variasi",
        "product_name": "Nama Produk",
        "kesimpulan": "Kesimpulan",
        "marketing_budget": "Est. Biaya Marketing",
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
        "subject": "Laporan Evaluasi Brand: {brand_name} - {period}",
        "plain_score": "Skor Akhir",
        "plain_period": "Periode",
        "chart_placeholder": "Chart akan ditampilkan di email",
    },
    "en": {
        "score_overview": "Score Overview",
        "detailed_evaluation": "Detailed Evaluation",
        "score_breakdown": "Score Breakdown",
        "data_intelligence": "Data Intelligence",
        "ads_analysis": "Ads Analysis",
        "top_sku": "Top SKU",
        "revenue_ranking": "Revenue Ranking",
        "stock_ranking": "Stock Ranking",
        "average_stock": "Average Stock",
        "product_code": "Variant Code",
        "product_name": "Product Name",
        "kesimpulan": "Conclusion",
        "marketing_budget": "Est. Marketing Budget",
        "metric": "Metric",
        "value": "Value",
        "benchmark": "Benchmark",
        "verdict": "Verdict",
        "score": "Score",
        "message": "Message",
        "approved": "Approved",
        "rejected": "Rejected",
        "template_type": "Template Type",
        "check_count": "Pass",
        "cross_count": "Fail",
        "brand_report": "Brand Evaluation Report",
        "subject": "Brand Evaluation Report: {brand_name} - {period}",
        "plain_score": "Final Score",
        "plain_period": "Period",
        "chart_placeholder": "Chart will be displayed in email",
    },
    "th": {
        "score_overview": "\u0e20\u0e32\u0e1e\u0e23\u0e27\u0e21\u0e04\u0e30\u0e41\u0e19\u0e19",
        "detailed_evaluation": "\u0e01\u0e32\u0e23\u0e1b\u0e23\u0e30\u0e40\u0e21\u0e34\u0e19\u0e42\u0e14\u0e22\u0e25\u0e30\u0e40\u0e2d\u0e35\u0e22\u0e14",
        "score_breakdown": "\u0e23\u0e32\u0e22\u0e25\u0e30\u0e40\u0e2d\u0e35\u0e22\u0e14\u0e04\u0e30\u0e41\u0e19\u0e19",
        "data_intelligence": "\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25\u0e40\u0e0a\u0e34\u0e07\u0e25\u0e36\u0e01",
        "ads_analysis": "\u0e27\u0e34\u0e40\u0e04\u0e23\u0e32\u0e30\u0e2b\u0e4c\u0e42\u0e06\u0e29\u0e13\u0e32",
        "top_sku": "Top SKU",
        "revenue_ranking": "\u0e2d\u0e31\u0e19\u0e14\u0e31\u0e1a\u0e23\u0e32\u0e22\u0e44\u0e14\u0e49",
        "stock_ranking": "\u0e2d\u0e31\u0e19\u0e14\u0e31\u0e1a\u0e2a\u0e15\u0e47\u0e2d\u0e01",
        "average_stock": "\u0e2a\u0e15\u0e47\u0e2d\u0e01\u0e40\u0e09\u0e25\u0e35\u0e48\u0e22",
        "product_code": "\u0e23\u0e2b\u0e31\u0e2a\u0e15\u0e31\u0e27\u0e41\u0e1b\u0e23",
        "product_name": "\u0e0a\u0e37\u0e48\u0e2d\u0e2a\u0e34\u0e19\u0e04\u0e49\u0e32",
        "kesimpulan": "\u0e2a\u0e23\u0e38\u0e1b\u0e1c\u0e25",
        "marketing_budget": "\u0e07\u0e1a\u0e01\u0e32\u0e23\u0e15\u0e25\u0e32\u0e14\u0e42\u0e14\u0e22\u0e1b\u0e23\u0e30\u0e21\u0e32\u0e13",
        "metric": "\u0e15\u0e31\u0e27\u0e0a\u0e35\u0e49\u0e27\u0e31\u0e14",
        "value": "\u0e04\u0e48\u0e32",
        "benchmark": "\u0e40\u0e01\u0e13\u0e11\u0e4c\u0e21\u0e32\u0e15\u0e23\u0e10\u0e32\u0e19",
        "verdict": "\u0e1c\u0e25\u0e01\u0e32\u0e23\u0e15\u0e31\u0e14\u0e2a\u0e34\u0e19",
        "score": "\u0e04\u0e30\u0e41\u0e19\u0e19",
        "message": "\u0e02\u0e49\u0e2d\u0e04\u0e27\u0e32\u0e21",
        "approved": "\u0e1c\u0e48\u0e32\u0e19",
        "rejected": "\u0e44\u0e21\u0e48\u0e1c\u0e48\u0e32\u0e19",
        "template_type": "\u0e1b\u0e23\u0e30\u0e40\u0e20\u0e17\u0e40\u0e17\u0e21\u0e40\u0e1e\u0e25\u0e15",
        "check_count": "\u0e1c\u0e48\u0e32\u0e19",
        "cross_count": "\u0e44\u0e21\u0e48\u0e1c\u0e48\u0e32\u0e19",
        "brand_report": "\u0e23\u0e32\u0e22\u0e07\u0e32\u0e19\u0e1b\u0e23\u0e30\u0e40\u0e21\u0e34\u0e19\u0e41\u0e1a\u0e23\u0e19\u0e14\u0e4c",
        "subject": "\u0e23\u0e32\u0e22\u0e07\u0e32\u0e19\u0e1b\u0e23\u0e30\u0e40\u0e21\u0e34\u0e19\u0e41\u0e1a\u0e23\u0e19\u0e14\u0e4c: {brand_name} - {period}",
        "plain_score": "\u0e04\u0e30\u0e41\u0e19\u0e19\u0e2a\u0e38\u0e14\u0e17\u0e49\u0e32\u0e22",
        "plain_period": "\u0e0a\u0e48\u0e27\u0e07\u0e40\u0e27\u0e25\u0e32",
        "chart_placeholder": "\u0e41\u0e1c\u0e19\u0e20\u0e39\u0e21\u0e34\u0e08\u0e30\u0e41\u0e2a\u0e14\u0e07\u0e43\u0e19\u0e2d\u0e35\u0e40\u0e21\u0e25",
    },
}

CATEGORY_MAP: dict[str, dict[str, str]] = {
    "id": {
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
    },
    "en": {
        "Kesehatan Operasional Toko": "Operations",
        "Bisnis Analisis": "Business",
        "Tinjauan Pengunjung": "Visitors",
        "Promo Toko": "Promo Tools",
        "Jumlah Produk & Status Toko": "Products & Status",
        "Data Iklan": "Ads",
        "Partisipasi Campaign": "Campaign",
        "Kompetisi TOP Produk": "Competition",
        "Stok": "Stock",
        "Discount": "Discount",
    },
    "th": {
        "Kesehatan Operasional Toko": "\u0e14\u0e33\u0e40\u0e19\u0e34\u0e19\u0e07\u0e32\u0e19",
        "Bisnis Analisis": "\u0e18\u0e38\u0e23\u0e01\u0e34\u0e08",
        "Tinjauan Pengunjung": "\u0e1c\u0e39\u0e49\u0e40\u0e22\u0e35\u0e48\u0e22\u0e21\u0e0a\u0e21",
        "Promo Toko": "\u0e40\u0e04\u0e23\u0e37\u0e48\u0e2d\u0e07\u0e21\u0e37\u0e2d\u0e42\u0e1b\u0e23\u0e42\u0e21\u0e15",
        "Jumlah Produk & Status Toko": "\u0e2a\u0e34\u0e19\u0e04\u0e49\u0e32\u0e41\u0e25\u0e30\u0e2a\u0e16\u0e32\u0e19\u0e30",
        "Data Iklan": "\u0e42\u0e06\u0e29\u0e13\u0e32",
        "Partisipasi Campaign": "\u0e41\u0e04\u0e21\u0e40\u0e1b\u0e0d",
        "Kompetisi TOP Produk": "\u0e01\u0e32\u0e23\u0e41\u0e02\u0e48\u0e07\u0e02\u0e31\u0e19",
        "Stok": "\u0e2a\u0e15\u0e47\u0e2d\u0e01",
        "Discount": "\u0e2a\u0e48\u0e27\u0e19\u0e25\u0e14",
    },
}


def _get_strings(language: str = "id") -> dict[str, str]:
    """Get string translations for the given language, falling back to Indonesian."""
    return STRINGS.get(language, STRINGS["id"])


def _get_category_map(language: str = "id") -> dict[str, str]:
    """Get category label map for the given language, falling back to Indonesian."""
    return CATEGORY_MAP.get(language, CATEGORY_MAP["id"])


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


def _score_bg_color(score: float) -> str:
    """Return light background color based on score thresholds."""
    if score >= 80.0:
        return GREEN_LIGHT
    if score >= 50.0:
        return PRIMARY_LIGHT
    return ORANGE_LIGHT


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


def _section_header(number: str, title: str) -> str:
    """Render a section header with number badge matching dashboard style."""
    return f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="margin-bottom:16px;">
  <tr>
    <td style="font-family:Arial,Helvetica,sans-serif;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td style="font-size:11px;font-weight:900;color:{PRIMARY_BLUE};opacity:0.4;letter-spacing:3px;padding-right:8px;vertical-align:middle;">
            {number}
          </td>
          <td style="font-size:18px;font-weight:bold;color:{TEXT_DARK};vertical-align:middle;">
            {title}
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>"""


def _format_number(value: Any) -> str:
    """Format a numeric value with thousand separators."""
    if isinstance(value, (int, float)):
        return f"{value:,.0f}" if isinstance(value, float) else f"{value:,}"
    return str(value)


# ---------------------------------------------------------------------------
# Section Renderers
# ---------------------------------------------------------------------------


def _render_header(
    header_src: str,
    brand_name: str,
    period: str,
    verdict: str,
    template: str,
    S: dict[str, str],
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
    S: dict[str, str],
) -> str:
    """Render score overview section: large score, progress bar, verdict counts."""
    color = _score_color(final_score)
    bg_color = _score_bg_color(final_score)
    counts = _compute_verdict_counts(categories)
    score_pct = min(int(final_score), 100)

    return f"""\
<!-- Score Overview -->
<tr>
  <td style="padding:16px 30px 24px 30px;font-family:Arial,Helvetica,sans-serif;">
    {_section_header("01", S['score_overview'])}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color:{CARD_BG};border-radius:8px;border:1px solid {BORDER_LIGHT};">
      <tr>
        <td style="padding:24px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <!-- Score number -->
            <tr>
              <td style="padding-bottom:16px;">
                <span style="font-size:56px;font-weight:900;color:{color};letter-spacing:-2px;">{final_score}</span>
                <span style="font-size:20px;color:{TEXT_SECONDARY};font-weight:500;"> / 100</span>
              </td>
            </tr>
            <!-- Progress bar -->
            <tr>
              <td style="padding-bottom:20px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="background-color:{BORDER_LIGHT};border-radius:6px;height:12px;padding:0;">
                      <table role="presentation" width="{score_pct}%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td style="background-color:{color};border-radius:6px;height:12px;font-size:0;line-height:0;">
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
                    <td style="padding-right:16px;">
                      <table role="presentation" cellpadding="0" cellspacing="0" border="0"
                             style="background-color:{GREEN_LIGHT};border-radius:6px;">
                        <tr>
                          <td style="padding:6px 12px;font-size:14px;font-weight:bold;color:{GREEN};">
                            \u2714\ufe0f {S['check_count']}: {counts['checks']}
                          </td>
                        </tr>
                      </table>
                    </td>
                    <td style="padding-right:16px;">
                      <table role="presentation" cellpadding="0" cellspacing="0" border="0"
                             style="background-color:{ORANGE_LIGHT};border-radius:6px;">
                        <tr>
                          <td style="padding:6px 12px;font-size:14px;font-weight:bold;color:{ORANGE};">
                            \u274c {S['cross_count']}: {counts['xs']}
                          </td>
                        </tr>
                      </table>
                    </td>
                    <td>
                      <table role="presentation" cellpadding="0" cellspacing="0" border="0"
                             style="background-color:{bg_color};border-radius:6px;border:1px solid {color}40;">
                        <tr>
                          <td style="padding:6px 12px;font-size:13px;font-weight:bold;color:{color};">
                            {S['template_type']}: {_esc(template)}
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
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


def _render_metric_card(row: dict[str, Any], S: dict[str, str]) -> str:
    """Render a single metric card as a table cell content block."""
    is_pass = row.get("verdict") == "\u2714\ufe0f"
    verdict_color = GREEN if is_pass else ORANGE
    verdict_bg = GREEN_LIGHT if is_pass else ORANGE_LIGHT
    return f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background-color:{WHITE};border-radius:8px;border:1px solid {BORDER_LIGHT};margin-bottom:8px;">
  <tr>
    <td style="padding:12px 14px;font-family:Arial,Helvetica,sans-serif;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td style="padding-bottom:6px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="font-size:13px;font-weight:bold;color:{TEXT_DARK};">
                  {_esc(row.get('metric', ''))}
                </td>
                <td style="text-align:right;width:40px;">
                  <span style="display:inline-block;background-color:{verdict_bg};color:{verdict_color};font-size:11px;font-weight:bold;padding:2px 8px;border-radius:4px;">
                    {row.get('verdict', '')}
                  </span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="font-size:12px;color:{TEXT_SECONDARY};padding-bottom:4px;">
            {S['value']}: <strong style="color:{TEXT_DARK};">{_esc(row.get('value', ''))}</strong>
            &nbsp;&middot;&nbsp;
            {S['benchmark']}: {_esc(row.get('benchmark', ''))}
          </td>
        </tr>
        <tr>
          <td style="font-size:11px;color:{TEXT_SECONDARY};font-style:italic;line-height:1.4;">
            {_esc(row.get('message', ''))}
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>"""


def _render_detailed_evaluation(
    categories: list[dict[str, Any]],
    S: dict[str, str],
    cat_map: dict[str, str],
) -> str:
    """Render detailed evaluation section with all categories and metric cards."""
    if not categories:
        return ""

    sections: list[str] = []
    for cat in categories:
        cat_name = cat_map.get(cat.get("category", ""), cat.get("category", ""))

        rows = cat.get("rows", [])
        if not rows:
            continue

        # Use verdict-based counts to match the dashboard display
        checks = sum(1 for r in rows if r.get("verdict") == "\u2714\ufe0f")
        xs = sum(1 for r in rows if r.get("verdict") == "\u274c")
        total = checks + xs
        cat_pct = round((checks / total) * 100) if total > 0 else 0
        cat_color = _score_color(cat_pct)

        # Build 2-column grid of metric cards
        grid_rows: list[str] = []
        for i in range(0, len(rows), 2):
            left = _render_metric_card(rows[i], S)
            if i + 1 < len(rows):
                right = _render_metric_card(rows[i + 1], S)
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
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color:{CARD_BG};border-radius:8px;border:1px solid {BORDER_LIGHT};padding:16px;">
      <tr>
        <td style="padding:16px 16px 8px 16px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="font-size:15px;font-weight:bold;color:{TEXT_DARK};">
                {_esc(cat_name)}
              </td>
              <td style="text-align:right;font-size:13px;font-weight:bold;">
                <span style="color:{GREEN};">✔️ {checks}</span>
                <span style="color:{TEXT_SECONDARY};"> / </span>
                <span style="color:{ORANGE};">❌ {xs}</span>
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <!-- Category progress bar -->
      <tr>
        <td style="padding:0 16px 16px 16px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="background-color:{BORDER_LIGHT};border-radius:4px;height:8px;padding:0;">
                <table role="presentation" width="{cat_pct}%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="background-color:{cat_color};border-radius:4px;height:8px;font-size:0;line-height:0;">
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
        <td style="padding:0 12px 12px 12px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 class="metric-grid">
            {grid_html}
          </table>
        </td>
      </tr>
    </table>
  </td>
</tr>""")

    if not sections:
        return ""

    all_sections = "\n".join(sections)
    return f"""\
<!-- Detailed Evaluation -->
<tr>
  <td style="padding:16px 30px 8px 30px;font-family:Arial,Helvetica,sans-serif;">
    {_section_header("02", S['detailed_evaluation'])}
  </td>
</tr>
{all_sections}"""


def _render_score_breakdown(
    chart_src: str,
    categories: list[dict[str, Any]],
    S: dict[str, str],
    cat_map: dict[str, str],
) -> str:
    """Render score breakdown section: chart image + category summary bars."""
    if not categories:
        return ""

    cat_bars: list[str] = []
    for cat in categories:
        cat_name = cat_map.get(cat.get("category", ""), cat.get("category", ""))

        # Per-category verdict counts
        checks = sum(1 for r in cat.get("rows", []) if r.get("verdict") == "\u2714\ufe0f")
        xs = sum(1 for r in cat.get("rows", []) if r.get("verdict") == "\u274c")
        total = checks + xs
        cat_pct = round((checks / total) * 100) if total > 0 else 0
        cat_color = _score_color(cat_pct)

        cat_bars.append(f"""\
<tr>
  <td style="padding:6px 0;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:13px;font-weight:600;color:{TEXT_DARK};width:120px;padding-right:12px;">
          {_esc(cat_name)}
        </td>
        <td style="padding:0;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="background-color:{BORDER_LIGHT};border-radius:4px;height:10px;padding:0;">
                <table role="presentation" width="{cat_pct}%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="background-color:{cat_color};border-radius:4px;height:10px;font-size:0;line-height:0;">
                      &nbsp;
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
        <td style="font-size:12px;width:90px;text-align:right;padding-left:12px;">
          <span style="color:{GREEN};font-weight:bold;">\u2714\ufe0f{checks}</span>
          <span style="color:{TEXT_SECONDARY};"> / </span>
          <span style="color:{ORANGE};font-weight:bold;">\u274c{xs}</span>
        </td>
      </tr>
    </table>
  </td>
</tr>""")

    bars_html = "\n".join(cat_bars)
    chart_html = ""
    if chart_src:
        chart_html = f"""\
      <!-- Chart image -->
      <tr>
        <td style="padding-top:8px;padding-bottom:16px;">
          <img src="{chart_src}" width="540"
               style="display:block;width:100%;height:auto;border:0;border-radius:8px;"
               alt="Score Breakdown Chart">
        </td>
      </tr>"""

    return f"""\
<!-- Score Breakdown -->
<tr>
  <td style="padding:16px 30px 24px 30px;font-family:Arial,Helvetica,sans-serif;">
    {_section_header("03", S['score_breakdown'])}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color:{CARD_BG};border-radius:8px;border:1px solid {BORDER_LIGHT};">
      <tr>
        <td style="padding:20px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
{chart_html}
            <!-- Category summary bars -->
            {bars_html}
          </table>
        </td>
      </tr>
    </table>
  </td>
</tr>"""


def _render_ranking_table(
    title: str,
    rows: list[dict[str, Any]],
    value_key: str,
    value_label: str,
    code_label: str,
    name_label: str,
    code_key: str = "kode_variasi",
    name_key: str = "product_name",
    max_rows: int = 5,
    value_color: str = PRIMARY_BLUE,
) -> str:
    """Render a ranking table (revenue or stock) limited to max_rows."""
    if not rows:
        return ""

    display_rows = rows[:max_rows]
    row_html_parts: list[str] = []
    for i, item in enumerate(display_rows):
        bg = WHITE if i % 2 == 0 else CARD_BG
        formatted_value = _format_number(item.get(value_key, ""))
        row_html_parts.append(
            f'<tr style="background-color:{bg};">'
            f'<td style="padding:8px 10px;font-size:12px;color:{TEXT_DARK};border-bottom:1px solid {BORDER_LIGHT};font-weight:500;">{_esc(item.get(code_key, "-"))}</td>'
            f'<td style="padding:8px 10px;font-size:12px;color:{TEXT_DARK};border-bottom:1px solid {BORDER_LIGHT};max-width:200px;">{_esc(item.get(name_key, ""))}</td>'
            f'<td style="padding:8px 10px;font-size:12px;color:{value_color};border-bottom:1px solid {BORDER_LIGHT};text-align:right;font-weight:bold;">{formatted_value}</td>'
            f'</tr>'
        )

    rows_html = "\n".join(row_html_parts)
    return f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="margin-top:12px;margin-bottom:16px;">
  <tr>
    <td style="font-size:13px;font-weight:bold;color:{TEXT_DARK};padding-bottom:8px;text-transform:uppercase;letter-spacing:1px;">
      {_esc(title)}
    </td>
  </tr>
  <tr>
    <td>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="border-collapse:collapse;border-radius:8px;overflow:hidden;border:1px solid {BORDER_LIGHT};">
        <tr style="background-color:{CARD_BG};">
          <td style="padding:8px 10px;font-size:11px;color:{TEXT_SECONDARY};font-weight:bold;border-bottom:2px solid {BORDER_LIGHT};text-transform:uppercase;letter-spacing:0.5px;">{_esc(code_label)}</td>
          <td style="padding:8px 10px;font-size:11px;color:{TEXT_SECONDARY};font-weight:bold;border-bottom:2px solid {BORDER_LIGHT};text-transform:uppercase;letter-spacing:0.5px;">{_esc(name_label)}</td>
          <td style="padding:8px 10px;font-size:11px;color:{TEXT_SECONDARY};font-weight:bold;border-bottom:2px solid {BORDER_LIGHT};text-align:right;text-transform:uppercase;letter-spacing:0.5px;width:100px;">{_esc(value_key.replace('_', ' ').title())}</td>
        </tr>
        {rows_html}
      </table>
    </td>
  </tr>
</table>"""


def _render_data_intelligence(calculator_results: dict[str, Any], S: dict[str, str]) -> str:
    """Render data intelligence section: ads analysis + top SKU tables."""
    if not calculator_results:
        return ""

    parts: list[str] = []

    # Ads keyword analysis
    ads = calculator_results.get("ads_keyword")
    if ads:
        output_text = ads.get("output_text", "")
        if output_text:
            parts.append(f"""\
<tr>
  <td style="padding:8px 0;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:14px;font-weight:bold;color:{TEXT_DARK};padding-bottom:10px;text-transform:uppercase;letter-spacing:1px;">
          {S['ads_analysis']}
        </td>
      </tr>
      <tr>
        <td style="background-color:{WHITE};border-radius:8px;border:1px solid {BORDER_LIGHT};padding:14px 16px;font-family:monospace,'Courier New',Courier;font-size:12px;color:{TEXT_DARK};white-space:pre-wrap;line-height:1.6;">
{_esc(output_text)}</td>
      </tr>
    </table>
  </td>
</tr>""")

    # Top SKU tables (use output_1/output_2 keys from calculator)
    top_sku = calculator_results.get("top_sku")
    if top_sku:
        details = top_sku.get("details", {})
        avg_stock = details.get("average_stock")

        # Revenue ranking (output_1)
        revenue = details.get("output_1", [])
        # Stock ranking (output_2)
        stock = details.get("output_2", [])

        if revenue or stock or avg_stock is not None:
            avg_stock_html = ""
            if avg_stock is not None:
                avg_stock_html = f"""\
      <tr>
        <td style="padding-bottom:12px;">
          <table role="presentation" cellpadding="0" cellspacing="0" border="0"
                 style="background-color:{PRIMARY_LIGHT};border-radius:6px;border:1px solid {PRIMARY_BLUE}40;">
            <tr>
              <td style="padding:8px 14px;font-size:13px;font-weight:600;color:{TEXT_DARK};">
                {S['average_stock']}: <span style="color:{PRIMARY_BLUE};font-weight:bold;">{_format_number(avg_stock)}</span>
              </td>
            </tr>
          </table>
        </td>
      </tr>"""

            revenue_table = _render_ranking_table(
                S["revenue_ranking"],
                revenue,
                "total_omzet",
                value_label=S["revenue_ranking"],
                code_label=S["product_code"],
                name_label=S["product_name"],
                code_key="kode_variasi",
                name_key="product_name",
                value_color=PRIMARY_BLUE,
            )
            stock_table = _render_ranking_table(
                S["stock_ranking"],
                stock,
                "stok",
                value_label=S["stock_ranking"],
                code_label=S["product_code"],
                name_label=S["product_name"],
                code_key="kode_variasi",
                name_key="nama_produk",
                value_color=ORANGE,
            )

            parts.append(f"""\
<tr>
  <td style="padding:8px 0;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="font-size:14px;font-weight:bold;color:{TEXT_DARK};padding-bottom:10px;text-transform:uppercase;letter-spacing:1px;">
          {S['top_sku']}
        </td>
      </tr>
{avg_stock_html}
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
    {_section_header("04", S['data_intelligence'])}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color:{CARD_BG};border-radius:8px;border:1px solid {BORDER_LIGHT};">
      <tr>
        <td style="padding:20px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            {all_parts}
          </table>
        </td>
      </tr>
    </table>
  </td>
</tr>"""


# ---------------------------------------------------------------------------
# Kesimpulan (Conclusion) section
# ---------------------------------------------------------------------------


def _parse_bullet_points(text: str) -> list[str]:
    """Parse bullet-pointed text into a list of points."""
    return [
        line.lstrip("-\u2022 ").strip()
        for line in text.split("\n")
        if line.strip()
    ]


def _render_kesimpulan(calculator_results: dict[str, Any], S: dict[str, str]) -> str:
    """Render kesimpulan (conclusion) section: bullet points, marketing budget, closing message."""
    if not calculator_results:
        return ""

    summary = calculator_results.get("scoring_summary")
    if not isinstance(summary, dict):
        return ""

    conclusion = summary.get("conclusion", "")
    marketing_budget = summary.get("marketing_budget", "")
    closing_message = summary.get("closing_message", "")

    # Skip entirely if no content
    if not conclusion and not marketing_budget and not closing_message:
        return ""

    parts: list[str] = []

    # Conclusion bullet points
    if conclusion:
        bullets = _parse_bullet_points(conclusion)
        bullet_html_parts: list[str] = []
        for bullet in bullets:
            bullet_html_parts.append(f"""\
            <tr>
              <td style="padding:4px 0;font-family:Arial,Helvetica,sans-serif;">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="width:20px;vertical-align:top;padding-top:7px;">
                      <div style="width:6px;height:6px;border-radius:50%;background-color:{PRIMARY_BLUE};"></div>
                    </td>
                    <td style="font-size:13px;color:{TEXT_DARK};line-height:1.6;">
                      {_esc(bullet)}
                    </td>
                  </tr>
                </table>
              </td>
            </tr>""")
        bullets_html = "\n".join(bullet_html_parts)
        parts.append(f"""\
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="margin-bottom:16px;">
{bullets_html}
          </table>""")

    # Marketing budget card
    if marketing_budget:
        parts.append(f"""\
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="background-color:{CARD_BG};border-radius:8px;border:1px solid {BORDER_LIGHT};margin-bottom:16px;">
            <tr>
              <td style="padding:16px 18px;font-family:Arial,Helvetica,sans-serif;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="font-size:11px;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px;color:{TEXT_SECONDARY};padding-bottom:6px;">
                      {S['marketing_budget']}
                    </td>
                  </tr>
                  <tr>
                    <td style="font-size:18px;font-weight:bold;color:{PRIMARY_BLUE};">
                      {_esc(marketing_budget)}
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>""")

    # Closing message
    if closing_message:
        escaped_closing = _esc(closing_message).replace("\n", "<br>")
        parts.append(f"""\
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="border-left:4px solid {PRIMARY_BLUE}40;background-color:{PRIMARY_LIGHT};border-radius:0 8px 8px 0;">
            <tr>
              <td style="padding:16px 18px;font-size:13px;color:{TEXT_DARK};line-height:1.7;font-family:Arial,Helvetica,sans-serif;">
                {escaped_closing}
              </td>
            </tr>
          </table>""")

    all_parts = "\n".join(parts)
    return f"""\
<!-- Kesimpulan -->
<tr>
  <td style="padding:16px 30px 24px 30px;font-family:Arial,Helvetica,sans-serif;">
    {_section_header("05", S['kesimpulan'])}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color:{WHITE};border-radius:8px;border:1px solid {BORDER_LIGHT};">
      <tr>
        <td style="padding:20px;">
{all_parts}
        </td>
      </tr>
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
    language: str = "id",
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
    language:
        Language code for translations ('id', 'en', 'th'). Defaults to 'id'.

    Returns
    -------
    str
        Complete HTML document string for the email body.
    """
    S = _get_strings(language)
    cat_map = _get_category_map(language)

    brand_name: str = evaluation_data["brand_name"]
    period: str = evaluation_data["period"]
    final_score: float = evaluation_data["final_score"]
    verdict: str = evaluation_data["verdict"]
    template: str = evaluation_data["template"]
    categories: list[dict[str, Any]] = evaluation_data.get("score_breakdown", [])
    calculator_results: dict[str, Any] = evaluation_data.get("calculator_results", {})

    header = _render_header(header_src, brand_name, period, verdict, template, S)
    note_section = _render_note(note) if note else ""
    score_overview = _render_score_overview(final_score, verdict, template, categories, S)
    detailed = _render_detailed_evaluation(categories, S, cat_map)
    breakdown = _render_score_breakdown(chart_src, categories, S, cat_map)
    intelligence = _render_data_intelligence(calculator_results, S)
    kesimpulan = _render_kesimpulan(calculator_results, S)
    footer = _render_footer(footer_src)

    lang_code = language if language in ("id", "en", "th") else "id"
    return f"""\
<!DOCTYPE html>
<html lang="{lang_code}">
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
        {kesimpulan}
        {footer}
      </table>
    </td>
  </tr>
</table>
</body>
</html>"""
