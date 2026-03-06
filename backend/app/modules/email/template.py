"""HTML email template renderer for brand evaluation reports.

Produces cross-client-compatible HTML using table-based layout with inline CSS.
All images referenced via CID (Content-ID) for inline embedding.
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
    header_cid: str,
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
    <img src="cid:{header_cid}" width="600"
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


def _render_footer(footer_cid: str) -> str:
    """Render footer section: branded image."""
    return f"""\
<!-- Footer Image -->
<tr>
  <td style="padding:0;margin:0;">
    <img src="cid:{footer_cid}" width="600"
         style="display:block;width:100%;height:auto;border:0;"
         alt="AHA Commerce Footer">
  </td>
</tr>"""


# ---------------------------------------------------------------------------
# Stub sections (Task 2 fills these in)
# ---------------------------------------------------------------------------


def _render_detailed_evaluation(categories: list[dict[str, Any]]) -> str:
    """Render detailed evaluation section. Stub -- implemented in Task 2."""
    return ""


def _render_score_breakdown(
    chart_cid: str, categories: list[dict[str, Any]],
) -> str:
    """Render score breakdown section. Stub -- implemented in Task 2."""
    return ""


def _render_data_intelligence(calculator_results: dict[str, Any]) -> str:
    """Render data intelligence section. Stub -- implemented in Task 2."""
    return ""


# ---------------------------------------------------------------------------
# Main Renderer
# ---------------------------------------------------------------------------


def render_email_html(
    *,
    evaluation_data: dict[str, Any],
    chart_cid: str,
    header_cid: str,
    footer_cid: str,
) -> str:
    """Render complete HTML email from evaluation data and CID references.

    Parameters
    ----------
    evaluation_data:
        Dict matching EvaluationDetailResponse shape.
    chart_cid:
        Content-ID for the radar chart image (without angle brackets).
    header_cid:
        Content-ID for the header branded image.
    footer_cid:
        Content-ID for the footer branded image.

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

    header = _render_header(header_cid, brand_name, period, verdict, template)
    score_overview = _render_score_overview(final_score, verdict, template, categories)
    detailed = _render_detailed_evaluation(categories)
    breakdown = _render_score_breakdown(chart_cid, categories)
    intelligence = _render_data_intelligence(calculator_results)
    footer = _render_footer(footer_cid)

    return f"""\
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{_esc(brand_name)} - {S['brand_report']}</title>
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
