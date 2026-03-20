"""HTML email template renderer for brand evaluation reports.

Produces cross-client-compatible HTML using table-based layout with inline CSS.
All images referenced via full src URI (cid: for send, data: for preview).
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# AHA Brand palette — matches the presentation dashboard (light theme).
PRIMARY_BLUE = "#325FEC"
PRIMARY_LIGHT = "#EEF2FD"    # ~primary/10
GREEN = "#22C55E"
GREEN_LIGHT = "#DCFCE7"
ORANGE = "#F97316"
ORANGE_LIGHT = "#FFF7ED"
BG_GRAY = "#F4F4F5"          # neutral-100
WHITE = "#ffffff"
TEXT_DARK = "#1D388B"         # dark navy — foreground
TEXT_SECONDARY = "#71717A"    # neutral-500
CARD_BG = "#FFFFFF"
BORDER_LIGHT = "#E4E4E7"     # neutral-200

# Font stack: Manrope (dashboard font) with safe fallbacks.
# Gmail won't load @font-face but will use Manrope if installed locally.
FONT_STACK = "'Manrope',Arial,Helvetica,sans-serif"

# Expected email string keys for defensive fallback.
_EMAIL_STRING_KEYS: frozenset[str] = frozenset({
    "score_overview", "detailed_evaluation", "score_breakdown",
    "data_intelligence", "ads_analysis", "top_sku", "revenue_ranking",
    "stock_ranking", "average_stock", "product_code", "product_name",
    "kesimpulan", "marketing_budget", "metric", "value", "benchmark",
    "verdict", "score", "message", "approved", "rejected",
    "check_count", "cross_count", "performance_verdict", "brand_report",
    "subject", "plain_score", "plain_period", "chart_placeholder",
})

# Indonesian category names are the canonical keys used in evaluation data.
_CATEGORY_KEYS: dict[str, str] = {
    "operational": "Kesehatan Operasional Toko",
    "business": "Bisnis Analisis",
    "visitors": "Tinjauan Pengunjung",
    "promo": "Promo Toko",
    "products": "Jumlah Produk & Status Toko",
    "ads": "Data Iklan",
    "campaign": "Partisipasi Campaign",
    "competition": "Kompetisi TOP Produk",
    "stock": "Stok",
    "discount": "Discount",
}


# ---------------------------------------------------------------------------
# i18n — shared locale files with frontend
# ---------------------------------------------------------------------------

# Local dev: resolve relative to source tree.  Docker: /app/locales mount.
_LOCALES_CANDIDATES = [
    Path(__file__).resolve().parent.parent.parent.parent.parent / "frontend" / "src" / "locales",
    Path("/app/locales"),
]
_LOCALES_DIR = next((p for p in _LOCALES_CANDIDATES if p.is_dir()), _LOCALES_CANDIDATES[0])


@lru_cache(maxsize=4)
def _load_locale(lang: str) -> dict[str, str]:
    """Load a frontend locale JSON, returning a flat key→value dict."""
    path = _LOCALES_DIR / f"{lang}.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _get_strings(language: str = "id") -> dict[str, str]:
    """Get email string translations from locale file.

    Falls back to key name if locale file is missing/incomplete,
    preventing KeyError crashes in template rendering.
    """
    locale = _load_locale(language) or _load_locale("id")
    result: dict[str, str] = {}
    for k, v in locale.items():
        if k.startswith("email.") and not k.startswith("email.category."):
            result[k[len("email."):]] = v
    # Ensure all expected keys exist — fall back to key name itself
    for key in _EMAIL_STRING_KEYS:
        if key not in result:
            result[key] = key
    return result


def _get_category_map(language: str = "id") -> dict[str, str]:
    """Get category label map from locale file."""
    locale = _load_locale(language) or _load_locale("id")
    return {
        indo_name: locale.get(f"email.category.{key}", indo_name)
        for key, indo_name in _CATEGORY_KEYS.items()
    }


def _translate(key: str, vars_: dict[str, str] | None, lang: str) -> str | None:
    """Resolve an i18n key with {{var}} interpolation, like the frontend's t()."""
    locale = _load_locale(lang) or _load_locale("id")
    template = locale.get(key)
    if template is None:
        return None
    if vars_:
        for var_name, var_value in vars_.items():
            template = template.replace(f"{{{{{var_name}}}}}", str(var_value))
    return template


def _resolve_metric_name(row: dict[str, Any], lang: str) -> str:
    """Get the display name for a metric row, using metric_i18n when available."""
    i18n = row.get("metric_i18n")
    if i18n and isinstance(i18n, dict) and i18n.get("key"):
        translated = _translate(i18n["key"], i18n.get("vars"), lang)
        if translated:
            return translated
    return row.get("metric", "")


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
    """Count check marks and cross marks across all category rows.

    Also computes the **partner score** (dashboard score) as a simple
    pass-ratio percentage: ``round(checks / total * 100)``.  This is the
    score shown on the presentation dashboard and must be used in the
    email instead of the internal ``final_score``.
    """
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
    score = round((checks / total) * 100) if total > 0 else 0
    return {"checks": checks, "xs": xs, "total": total, "score": score}


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
    <td>
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


def _format_display_value(metric: str, value: Any) -> str:
    """Format a metric value for display, matching the dashboard logic.

    Rules (uses original Indonesian metric name for stable matching):
      1. Metric starts with '%' → value is a 0-1 ratio → ``f'{value*100:.1f}%'``
      2. Metric contains 'Tingkat' or 'Persentase' → append '%'
      3. Numeric → thousand-separated
      4. Fallback → str()
    """
    if value is None:
        return "-"
    if isinstance(value, (int, float)):
        if metric.startswith("%"):
            return f"{value * 100:.1f}%"
        if "Tingkat" in metric or "Persentase" in metric:
            return f"{value}%"
        return f"{value:,}" if isinstance(value, int) else f"{value:,.2f}".rstrip("0").rstrip(".")
    return str(value)


# ---------------------------------------------------------------------------
# Section Renderers
# ---------------------------------------------------------------------------


def _render_header(
    header_src: str,
    brand_name: str,
    period: str,
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
  <td style="padding:24px 30px 16px 30px;">
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
  <td style="padding:8px 30px 16px 30px;">
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
    categories: list[dict[str, Any]],
    S: dict[str, str],
) -> str:
    """Render score overview section: large score, progress bar, verdict counts.

    Uses the **partner score** (pass-ratio from verdicts) instead of the
    internal ``final_score`` to match the presentation dashboard display.
    """
    counts = _compute_verdict_counts(categories)
    partner_score = counts["score"]

    return f"""\
<!-- Score Overview -->
<tr>
  <td style="padding:16px 30px 24px 30px;">
    {_section_header("01", S['score_overview'])}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color:{CARD_BG};border-radius:8px;border:1px solid {BORDER_LIGHT};">
      <tr>
        <td style="padding:32px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <!-- Score number -->
            <tr>
              <td style="padding-bottom:20px;">
                <span style="font-size:64px;font-weight:900;color:{TEXT_DARK};letter-spacing:-3px;line-height:1;">{partner_score}</span>
                <span style="font-size:22px;color:{TEXT_SECONDARY};font-weight:500;"> /100</span>
              </td>
            </tr>
            <!-- Verdict counts -->
            <tr>
              <td style="padding-bottom:20px;">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="padding-right:20px;font-size:16px;font-weight:bold;color:{GREEN};">
                      ⊘ {counts['checks']}
                    </td>
                    <td style="font-size:16px;font-weight:bold;color:{ORANGE};">
                      ⊗ {counts['xs']}
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <!-- Performance badge -->
            <tr>
              <td>
                <table role="presentation" cellpadding="0" cellspacing="0" border="0"
                       style="background-color:{PRIMARY_LIGHT};border:1px solid {PRIMARY_BLUE}30;border-radius:6px;">
                  <tr>
                    <td style="padding:8px 16px;font-size:13px;font-weight:bold;color:{PRIMARY_BLUE};letter-spacing:0.3px;">
                      ↗ {S['performance_verdict']}
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


def _render_metric_card(row: dict[str, Any], S: dict[str, str], lang: str = "id") -> str:
    """Render a single metric card matching the dashboard CategoryMetricCard style."""
    is_pass = row.get("verdict") == "\u2714\ufe0f"
    verdict_color = GREEN if is_pass else ORANGE
    message = _esc(row.get("message", "")).replace("\n", "<br>")
    raw_metric = row.get("metric", "")
    display_metric = _resolve_metric_name(row, lang)
    display_value = _format_display_value(raw_metric, row.get("value"))

    benchmark = row.get("benchmark", "")
    if raw_metric == "Biaya (iklan)":
        benchmark = "-"
    has_benchmark = bool(benchmark) and benchmark != "-"
    has_detail = has_benchmark or bool(message)

    detail_html = ""
    if has_detail:
        detail_parts: list[str] = []
        if has_benchmark:
            detail_parts.append(
                f'<div class="sm" style="padding-bottom:3px">Benchmark: {_esc(benchmark)}</div>'
            )
        if message:
            detail_parts.append(
                f'<div style="font-size:11px;color:{verdict_color};line-height:1.5">{message}</div>'
            )
        detail_html = (
            f'<tr><td colspan="2" style="border-top:1px solid {BORDER_LIGHT};padding-top:8px">'
            + "".join(detail_parts)
            + "</td></tr>"
        )

    is_multiline_value = "\n" in display_value
    if is_multiline_value:
        escaped_value = _esc(display_value).replace("\n", "<br>")
        val_style = "text-align:left;word-break:break-word"
    else:
        escaped_value = _esc(display_value)
        val_style = "text-align:right;white-space:nowrap"

    pb = 10 if has_detail else 0
    return (
        f'<table width="100%" cellpadding="0" cellspacing="0" border="0" class="mc">'
        f'<tr><td style="padding:14px 16px">'
        f'<table width="100%" cellpadding="0" cellspacing="0" border="0">'
        f'<tr><td class="lbl" style="padding-bottom:{pb}px">{_esc(display_metric)}</td>'
        f'<td class="val" style="{val_style};padding-bottom:{pb}px">{escaped_value}</td></tr>'
        f'{detail_html}'
        f'</table></td></tr></table>'
    )


def _render_detailed_evaluation(
    categories: list[dict[str, Any]],
    S: dict[str, str],
    cat_map: dict[str, str],
    lang: str = "id",
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

        # Metrics that trigger a full-width divider after their card
        # (matches dashboard DetailedEvaluation.tsx logic).
        _DIVIDER_AFTER = {"Program Afiliasi", "ROI"}

        def _needs_divider(row: dict[str, Any]) -> bool:
            m = row.get("metric", "")
            return m in _DIVIDER_AFTER or m.startswith("Rata² Penjualan")

        _DIVIDER_HTML = (
            f'<tr><td colspan="2" style="padding:8px 4px">'
            f'<div style="border-top:1px solid {PRIMARY_BLUE}4D"></div>'
            f'</td></tr>'
        )

        _HALF = 'style="width:50%;padding:4px;vertical-align:top"'

        # Build 2-column grid of metric cards with optional dividers.
        grid_rows: list[str] = []
        pending_left: str | None = None
        for row in rows:
            card = _render_metric_card(row, S, lang)
            if pending_left is None:
                if _needs_divider(row):
                    grid_rows.append(f'<tr><td {_HALF}>{card}</td><td {_HALF}>&nbsp;</td></tr>')
                    grid_rows.append(_DIVIDER_HTML)
                else:
                    pending_left = card
            else:
                grid_rows.append(f'<tr><td {_HALF}>{pending_left}</td><td {_HALF}>{card}</td></tr>')
                pending_left = None
                if _needs_divider(row):
                    grid_rows.append(_DIVIDER_HTML)

        if pending_left is not None:
            grid_rows.append(f'<tr><td {_HALF}>{pending_left}</td><td {_HALF}>&nbsp;</td></tr>')

        grid_html = "\n".join(grid_rows)

        sections.append(
            f'<tr><td style="padding:12px 30px 0 30px">'
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0" class="card" style="padding:16px">'
            f'<tr><td style="padding:16px 16px 8px 16px">'
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td class="hdr">{_esc(cat_name)}</td>'
            f'<td style="text-align:right;font-size:13px;font-weight:bold">'
            f'<span style="color:{GREEN}">✔️ {checks}</span>'
            f'<span style="color:{TEXT_SECONDARY}"> / </span>'
            f'<span style="color:{ORANGE}">❌ {xs}</span>'
            f'</td></tr></table></td></tr>'
            f'<tr><td style="padding:0 16px 16px 16px">'
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td class="bar-bg">'
            f'<table width="{cat_pct}%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="background:{cat_color};border-radius:4px;height:8px;font-size:0;line-height:0">&nbsp;</td>'
            f'</tr></table></td></tr></table></td></tr>'
            f'<tr><td style="padding:0 12px 12px 12px">'
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0" class="metric-grid">'
            f'{grid_html}</table></td></tr></table></td></tr>'
        )

    if not sections:
        return ""

    all_sections = "".join(sections)
    return (
        f'<tr><td style="padding:16px 30px 8px 30px">'
        f'{_section_header("02", S["detailed_evaluation"])}'
        f'</td></tr>{all_sections}'
    )


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

        checks = sum(1 for r in cat.get("rows", []) if r.get("verdict") == "\u2714\ufe0f")
        xs = sum(1 for r in cat.get("rows", []) if r.get("verdict") == "\u274c")
        total = checks + xs
        cat_pct = round((checks / total) * 100) if total > 0 else 0
        cat_color = _score_color(cat_pct)

        cat_bars.append(
            f'<tr><td style="padding:6px 0">'
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td class="lbl" style="width:120px;padding-right:12px">{_esc(cat_name)}</td>'
            f'<td style="padding:0"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td class="bar-bg10">'
            f'<table width="{cat_pct}%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="background:{cat_color};border-radius:4px;height:10px;font-size:0;line-height:0">&nbsp;</td>'
            f'</tr></table></td></tr></table></td>'
            f'<td style="font-size:12px;width:90px;text-align:right;padding-left:12px">'
            f'<span style="color:{GREEN};font-weight:bold">\u2714\ufe0f{checks}</span>'
            f'<span style="color:{TEXT_SECONDARY}"> / </span>'
            f'<span style="color:{ORANGE};font-weight:bold">\u274c{xs}</span>'
            f'</td></tr></table></td></tr>'
        )

    bars_html = "".join(cat_bars)
    chart_html = ""
    if chart_src:
        chart_html = (
            f'<tr><td style="padding-top:8px;padding-bottom:16px">'
            f'<img src="{chart_src}" width="540" '
            f'style="display:block;width:100%;height:auto;border:0;border-radius:8px" '
            f'alt="Score Breakdown Chart"></td></tr>'
        )

    return (
        f'<tr><td style="padding:16px 30px 24px 30px">'
        f'{_section_header("03", S["score_breakdown"])}'
        f'<table width="100%" cellpadding="0" cellspacing="0" border="0" class="card">'
        f'<tr><td style="padding:20px">'
        f'<table width="100%" cellpadding="0" cellspacing="0" border="0">'
        f'{chart_html}{bars_html}'
        f'</table></td></tr></table></td></tr>'
    )


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
  <td style="padding:8px 0;">
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
  <td style="padding:8px 0;">
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
  <td style="padding:16px 30px 24px 30px;">
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
              <td style="padding:4px 0;">
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
              <td style="padding:16px 18px;">
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
              <td style="padding:16px 18px;font-size:13px;color:{TEXT_DARK};line-height:1.7;">
                {escaped_closing}
              </td>
            </tr>
          </table>""")

    all_parts = "\n".join(parts)
    return f"""\
<!-- Kesimpulan -->
<tr>
  <td style="padding:16px 30px 24px 30px;">
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
# HTML minification — strip comments, collapse whitespace to stay under
# Gmail's ~102 KB clipping threshold.
# ---------------------------------------------------------------------------

_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_WHITESPACE_BETWEEN_TAGS_RE = re.compile(r">\s+<")
_LEADING_WHITESPACE_RE = re.compile(r"^\s+", re.MULTILINE)


def _minify_html(html: str) -> str:
    """Aggressively minify HTML for email delivery.

    Removes HTML comments, collapses inter-tag whitespace, and strips leading
    indentation.  The visual rendering is identical since email clients ignore
    source formatting.
    """
    html = _HTML_COMMENT_RE.sub("", html)
    html = _LEADING_WHITESPACE_RE.sub("", html)
    html = _WHITESPACE_BETWEEN_TAGS_RE.sub("><", html)
    return html.strip()


# ---------------------------------------------------------------------------
# CSS classes — shared styles extracted to reduce repeated inline bytes.
# Gmail supports <style> in <head> and rewrites class names with a prefix.
# ---------------------------------------------------------------------------

_EMAIL_CSS = f"""\
body,td,th{{font-family:{FONT_STACK};}}
.T{{border-collapse:collapse;}}
.card{{background:{CARD_BG};border-radius:8px;border:1px solid {BORDER_LIGHT};}}
.mc{{background:{WHITE};border-radius:8px;border:1px solid {BORDER_LIGHT};margin-bottom:8px;}}
.hdr{{font-size:15px;font-weight:bold;color:{TEXT_DARK};}}
.lbl{{font-size:13px;font-weight:600;color:{TEXT_DARK};}}
.val{{font-size:13px;font-weight:bold;color:{TEXT_SECONDARY};}}
.sm{{font-size:11px;color:{TEXT_SECONDARY};}}
.bar-bg{{background:{BORDER_LIGHT};border-radius:4px;height:8px;padding:0;}}
.bar-bg10{{background:{BORDER_LIGHT};border-radius:4px;height:10px;padding:0;}}
"""


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
    categories: list[dict[str, Any]] = evaluation_data.get("score_breakdown", [])
    # Filter out "Iklan check up" metric to match dashboard display
    # (dashboard: PresentationDashboard.tsx filters this metric from rows).
    categories = [
        {**cat, "rows": [r for r in cat.get("rows", []) if r.get("metric") != "Iklan check up"]}
        for cat in categories
    ]
    calculator_results: dict[str, Any] = evaluation_data.get("calculator_results", {})

    header = _render_header(header_src, brand_name, period, S)
    note_section = _render_note(note) if note else ""
    score_overview = _render_score_overview(categories, S)
    detailed = _render_detailed_evaluation(categories, S, cat_map, language)
    breakdown = _render_score_breakdown(chart_src, categories, S, cat_map)
    intelligence = _render_data_intelligence(calculator_results, S)
    kesimpulan = _render_kesimpulan(calculator_results, S)
    footer = _render_footer(footer_src)

    lang_code = language if language in ("id", "en", "th") else "id"
    raw = f"""\
<!DOCTYPE html>
<html lang="{lang_code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{_esc(brand_name)} - {S['brand_report']}</title>
<style type="text/css">
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&display=swap');
{_EMAIL_CSS}
@media only screen and (max-width:620px) {{
  .metric-grid td {{ display:block !important; width:100% !important; }}
}}
</style>
</head>
<body style="margin:0;padding:0;background-color:{BG_GRAY};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background-color:{BG_GRAY};">
  <tr>
    <td align="center" style="padding:20px 0;">
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
    return _minify_html(raw)
