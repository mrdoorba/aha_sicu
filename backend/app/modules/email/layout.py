"""Single source of truth for the brand-evaluation email layout.

This module owns the ONE ordered section layout (``EMAIL_SECTIONS``) and the ONE
renderer entry point (:func:`render_email`) that emits the report in either of
the two output formats recipients see:

* ``fmt="text"`` — the plain-text body shown on the evaluation page and sent via
  Gmail SMTP. Reproduces, byte-for-byte, the output of the former frontend
  ``buildI18nEmailBody`` builder (frozen as golden fixtures).
* ``fmt="html"`` — the styled HTML body shown on the dashboard preview and sent
  via Gmail SMTP. Reproduces the former ``render_email_html`` output exactly.

All i18n resolution lives here (the ``_t``/``_resolve_*`` helpers), so the three
former renderers collapse into this one interface.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

# ---------------------------------------------------------------------------
# i18n — shared locale files with the frontend
# ---------------------------------------------------------------------------

# Local dev: resolve relative to source tree.  Docker: /app/locales mount.
_LOCALES_CANDIDATES = [
    Path(__file__).resolve().parent.parent.parent.parent.parent / "frontend" / "src" / "locales",
    Path("/app/locales"),
]
_LOCALES_DIR = next((p for p in _LOCALES_CANDIDATES if p.is_dir()), _LOCALES_CANDIDATES[0])


@lru_cache(maxsize=4)
def _load_locale(lang: str) -> dict[str, Any]:
    """Load a frontend locale JSON, returning its (possibly nested) dict."""
    path = _LOCALES_DIR / f"{lang}.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _lookup(locale: dict[str, Any], key: str) -> str | None:
    """Resolve a key the way i18next does: descend by '.', else flat fallback.

    The frontend locale files mix flat dotted keys (``"closing.potential"``)
    with one nested object (``emailBody.section.*``).  i18next descends the key
    path first and falls back to the literal flat key, so we replicate both.
    """
    cur: Any = locale
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            cur = None
            break
    if isinstance(cur, str):
        return cur
    flat = locale.get(key)
    return flat if isinstance(flat, str) else None


_DOLLAR_T_RE = re.compile(r"\$t\(([^)]+)\)")
_INTERP_RE = re.compile(r"\{\{([^}]+)\}\}")


def _t(key: str, vars_: dict[str, str] | None, lang: str) -> str:
    """Translate like i18next's ``t()``: interpolate, resolve ``$t()``, key-fallback.

    Returns the *key itself* when the key is missing from the locale (matching
    i18next's default ``returnNull: false`` behaviour).  Unmatched ``{{var}}``
    placeholders are left verbatim, also matching i18next.
    """
    locale = _load_locale(lang) or _load_locale("id")
    template = _lookup(locale, key)
    if template is None:
        return key
    if vars_:
        for var_name, var_value in vars_.items():
            template = template.replace(f"{{{{{var_name}}}}}", str(var_value))

    def _resolve_ref(m: re.Match) -> str:
        ref_key = m.group(1)
        return _lookup(locale, ref_key) or ref_key

    return _DOLLAR_T_RE.sub(_resolve_ref, template)


def _translate(key: str, vars_: dict[str, str] | None, lang: str) -> str | None:
    """Like :func:`_t` but returns ``None`` (not the key) when missing.

    Used by the HTML renderers where a missing translation should fall back to
    a raw value rather than surface the key.
    """
    locale = _load_locale(lang) or _load_locale("id")
    if _lookup(locale, key) is None:
        return None
    return _t(key, vars_, lang)


# ---------------------------------------------------------------------------
# TranslatableText-style resolution helpers (shared by text + HTML paths)
# ---------------------------------------------------------------------------


def _resolve_metric_name(row: dict[str, Any], lang: str) -> str:
    """Get the display name for a metric row, using metric_i18n when available."""
    i18n = row.get("metric_i18n")
    if i18n and isinstance(i18n, dict) and i18n.get("key"):
        translated = _translate(i18n["key"], i18n.get("vars"), lang)
        if translated:
            return translated
    return row.get("metric", "")


def _resolve_translatable_text(
    i18n: dict[str, Any] | None, fallback: str, lang: str,
) -> str:
    """Resolve a TranslatableText-style dict to a translated string.

    Falls back to *fallback* when *i18n* is absent, malformed, or the key is
    missing from the locale file.
    """
    if i18n and isinstance(i18n, dict) and i18n.get("key"):
        translated = _translate(i18n["key"], i18n.get("vars"), lang)
        if translated is not None:
            return translated
    return fallback


def _resolve_ads_output_text(details: dict[str, Any], lang: str) -> str | None:
    """Resolve ads_keyword i18n sections into a single translated text block.

    Returns ``None`` when details lack i18n keys or any section fails (atomic
    fallback — caller should use raw output_text).  Used by the HTML data
    intelligence section.
    """
    _SECTION_KEYS = ("ak2", "ak3", "ak4", "al2", "al3", "al5", "al6", "al7", "al8", "al9")

    has_any = any(details.get(f"{k}_i18n") for k in _SECTION_KEYS)
    if not has_any:
        return None

    sections: list[str] = []
    for key in _SECTION_KEYS:
        i18n = details.get(f"{key}_i18n")
        if not i18n:
            continue

        if isinstance(i18n, list):
            flag_lines: list[str] = []
            for item in i18n:
                t = _resolve_translatable_text(item, "", lang)
                if not t:
                    return None
                flag_lines.append(t)
            sections.append("\n".join(flag_lines))

        elif isinstance(i18n, dict) and "header" in i18n:
            header = _resolve_translatable_text(i18n["header"], "", lang)
            if not header:
                return None
            ad_lines: list[str] = []
            for ad_item in i18n.get("ads", []):
                t = _resolve_translatable_text(ad_item, "", lang)
                if not t:
                    return None
                ad_lines.append(t)
            sections.append(header + "\n" + "\n".join(ad_lines) if ad_lines else header)

        elif isinstance(i18n, dict) and i18n.get("key"):
            t = _resolve_translatable_text(i18n, "", lang)
            if not t:
                return None
            sections.append(t)

    return "\n\n".join(sections) if sections else None


# ---------------------------------------------------------------------------
# Plain-text helpers — mirror the frontend renderTranslatable family exactly.
# ---------------------------------------------------------------------------


def _render_translatable_text(fallback: str, i18n: dict[str, Any] | None, lang: str) -> str:
    """Mirror frontend ``renderTranslatable``: use i18n if present, else fallback.

    Unlike :func:`_resolve_translatable_text`, when ``i18n`` is present this
    returns ``_t(...)`` (key-on-miss), matching ``t(i18n.key, i18n.vars)``.
    """
    if i18n and isinstance(i18n, dict) and i18n.get("key"):
        return _t(i18n["key"], i18n.get("vars"), lang)
    return fallback


def _render_ad_list_text(i18n: dict[str, Any] | None, lang: str) -> str:
    """Mirror frontend ``renderAdList``: header + ad lines (key-on-miss)."""
    if not i18n:
        return ""
    header_i18n = i18n.get("header", {})
    header = _t(header_i18n.get("key", ""), header_i18n.get("vars"), lang)
    ads = "\n".join(
        _t(ad.get("key", ""), ad.get("vars"), lang) for ad in i18n.get("ads", [])
    )
    return f"{header}\n{ads}"


def _render_flag_list_text(i18n: list[dict[str, Any]] | None, lang: str) -> str:
    """Mirror frontend ``renderFlagList``: one translated line per flag."""
    if not i18n:
        return ""
    return "\n".join(_t(flag.get("key", ""), flag.get("vars"), lang) for flag in i18n)


def _build_ads_keyword_text(calculator_results: dict[str, Any], lang: str) -> str:
    """Mirror frontend ``buildAdsKeywordI18nText`` for the row-53 ads section.

    Returns ``""`` when the ads_keyword i18n fields are unavailable.
    """
    ak = calculator_results.get("ads_keyword")
    if not isinstance(ak, dict):
        return ""
    details = ak.get("details")
    if not isinstance(details, dict) or not details.get("ak2_i18n"):
        return ""

    parts: list[str] = []
    parts.append(_render_translatable_text("", details.get("ak2_i18n"), lang))
    parts.append(_render_translatable_text("", details.get("ak3_i18n"), lang))
    if details.get("ak4_i18n") is not None:
        parts.append(_render_flag_list_text(details.get("ak4_i18n"), lang))
    parts.append(_render_ad_list_text(details.get("al2_i18n"), lang))
    parts.append(_render_translatable_text("", details.get("al3_i18n"), lang))
    parts.append(_render_ad_list_text(details.get("al5_i18n"), lang))
    for key in ("al6_i18n", "al7_i18n", "al8_i18n", "al9_i18n"):
        if details.get(key) is not None:
            parts.append(_render_translatable_text("", details.get(key), lang))

    return "\n\n".join(p for p in parts if p)


# The backend hardcodes the fake-discount marker into the marketing estimation
# (G68); the frontend detected and translated it.  We replicate that detection.
_FAKE_DISCOUNT_RE = re.compile(r"📌\s*Berpotensi menggunakan 'fake discount'")


def _translate_marketing_estimation(raw: str, lang: str) -> str:
    """Translate the embedded fake-discount line within marketing estimation."""
    if not _FAKE_DISCOUNT_RE.search(raw):
        return raw
    return _FAKE_DISCOUNT_RE.sub(_t("discount.output.fakeDiscount", None, lang), raw)


# ---------------------------------------------------------------------------
# EMAIL_SECTIONS — the ONE ordered layout source of truth.
# ---------------------------------------------------------------------------

SectionKind = Literal["normal", "promo"]


@dataclass(frozen=True)
class EmailSection:
    """One ordered category section of the email body.

    Attributes
    ----------
    category:
        Canonical Indonesian category name as stored in ``score_breakdown``.
    emoji:
        Section-header prefix emoji.
    header_key:
        i18n key for the section header label.
    rows:
        Explicit row-number filter; ``None`` means include every row.
    kind:
        ``"normal"`` for plain row extraction, ``"promo"`` for the special
        promo-tool range (31..41) + summary rows (42, 43).
    """

    category: str
    emoji: str
    header_key: str
    rows: tuple[int, ...] | None = None
    kind: SectionKind = "normal"


# Promo tool rows start at 31 and span 11 tools (31-41), plus summary rows 42, 43.
_PROMO_START_ROW = 31
_PROMO_TOOL_COUNT = 11
_PROMO_SUMMARY_ROWS = (42, 43)

EMAIL_SECTIONS: tuple[EmailSection, ...] = (
    EmailSection("Kesehatan Operasional Toko", "📊", "emailBody.section.operational"),
    EmailSection("Bisnis Analisis", "📈", "emailBody.section.business", rows=(13, 20)),
    EmailSection("Tinjauan Pengunjung", "👥", "emailBody.section.visitors", rows=(28, 29)),
    EmailSection("Promo Toko", "🏷️", "emailBody.section.promoTools", kind="promo"),
    EmailSection("Jumlah Produk & Status Toko", "📦", "emailBody.section.productsStatus"),
    EmailSection("Data Iklan", "📣", "emailBody.section.ads", rows=(50, 51, 52, 53)),
    EmailSection("Partisipasi Campaign", "🎯", "emailBody.section.campaign", rows=(57,)),
    EmailSection("Kompetisi TOP Produk", "🏆", "emailBody.section.competition"),
)


# ---------------------------------------------------------------------------
# Plain-text renderer — mirrors frontend buildI18nEmailBody byte-for-byte.
# ---------------------------------------------------------------------------


def _category_by_name(categories: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((c for c in categories if c.get("category") == name), None)


def _section_messages(
    cat: dict[str, Any],
    section: EmailSection,
    lang: str,
    calculator_results: dict[str, Any] | None,
) -> list[str]:
    """Extract a section's translated messages, applying its row filter/kind."""
    if section.kind == "promo":
        return _promo_messages(cat, lang)

    msgs: list[str] = []
    for r in cat.get("rows", []):
        row_num = r.get("row")
        if section.rows is not None and row_num not in section.rows:
            continue
        # Row 53: ads keyword output — use calculator details i18n if available.
        if row_num == 53 and not r.get("message_i18n") and calculator_results:
            translated = _build_ads_keyword_text(calculator_results, lang)
            if translated:
                msgs.append(translated)
                continue
        text = _render_translatable_text(r.get("message", ""), r.get("message_i18n"), lang)
        if not text:
            continue
        # Append product link for competition rows when i18n drops it.
        link = None
        m_i18n = r.get("message_i18n")
        if isinstance(m_i18n, dict):
            link = (m_i18n.get("vars") or {}).get("link")
        msgs.append(f"{text}\n↪{link}" if link else text)
    return msgs


def _promo_messages(cat: dict[str, Any], lang: str) -> list[str]:
    """Promo tool rows (31-41) followed by summary rows (42, 43)."""
    msgs: list[str] = []
    for r in cat.get("rows", []):
        row_num = r.get("row")
        if _PROMO_START_ROW <= row_num <= _PROMO_START_ROW + _PROMO_TOOL_COUNT - 1:
            text = _render_translatable_text(r.get("message", ""), r.get("message_i18n"), lang)
            if text:
                msgs.append(text)
    for r in cat.get("rows", []):
        if r.get("row") in _PROMO_SUMMARY_ROWS:
            text = _render_translatable_text(r.get("message", ""), r.get("message_i18n"), lang)
            if text:
                msgs.append(text)
    return msgs


def _render_text(result: dict[str, Any], language: str) -> str:
    """Render the plain-text email body in *language*."""
    categories: list[dict[str, Any]] = result.get("score_breakdown", []) or []
    calculator_results: dict[str, Any] = result.get("calculator_results", {}) or {}
    summary = calculator_results.get("scoring_summary")
    if not isinstance(summary, dict):
        summary = None

    sections: list[str] = []

    # Category sections, in canonical order.
    for section in EMAIL_SECTIONS:
        cat = _category_by_name(categories, section.category)
        if not cat:
            continue
        msgs = _section_messages(cat, section, language, calculator_results)
        if not msgs:
            continue
        sections.append(f"{section.emoji} {_t(section.header_key, None, language)}")
        sections.extend(msgs)
        sections.append("")

    # Conclusion / marketing / budget / closing.
    if summary:
        conclusion = _render_conclusion(summary, language)
        if conclusion:
            sections.append(f"📋 {_t('emailBody.section.conclusion', None, language)}")
            sections.append(conclusion)
            sections.append("")

        raw_marketing = summary.get("marketing_estimation")
        marketing_i18n = summary.get("marketing_estimation_i18n")
        if raw_marketing:
            raw_marketing = _translate_marketing_estimation(raw_marketing, language)
        marketing = _render_translatable_text(raw_marketing or "", marketing_i18n, language)
        if marketing:
            sections.append(f"📌 {_t('emailBody.section.marketingEstimation', None, language)}")
            sections.append(marketing)
            sections.append("")

        budget = _render_translatable_text(
            summary.get("marketing_budget", "") or "",
            summary.get("marketing_budget_i18n"),
            language,
        )
        if budget:
            sections.append(budget)
            sections.append("")

        closing = _render_translatable_text(
            summary.get("closing_message", "") or "",
            summary.get("closing_message_i18n"),
            language,
        )
        if closing:
            sections.append(closing)

    return "\n".join(sections)


def _render_conclusion(summary: dict[str, Any], lang: str) -> str:
    """Render the conclusion bullets from conclusion_i18n, else raw conclusion."""
    conclusion_i18n = summary.get("conclusion_i18n")
    if isinstance(conclusion_i18n, list) and conclusion_i18n:
        return "\n".join(
            f"- {_t(item.get('key', ''), item.get('vars'), lang)}"
            for item in conclusion_i18n
        )
    return summary.get("conclusion", "") or ""


# ---------------------------------------------------------------------------
# Public renderer
# ---------------------------------------------------------------------------


def render_email_subject(result: dict[str, Any], language: str = "id") -> str:
    """Build the localised email subject line (mirrors buildI18nEmailSubject)."""
    return _t(
        "sendMailUtils.subject",
        {"brandName": result.get("brand_name", ""), "period": result.get("period", "")},
        language,
    )


def render_plain_email_message(
    result: dict[str, Any], language: str = "id", pic_email: str | None = None
) -> str:
    """Compose the full plain-text email body (greeting wrapper + section body).

    Reproduces the frontend ``buildBody`` wrapper around the unified
    ``render_email(fmt="text")`` section body, so the SMTP-sent text is rendered
    entirely server-side and matches what recipients saw before consolidation.

    ``pic_email`` is the (possibly user-edited) PIC address shown in the dialog;
    when omitted it falls back to the evaluation's stored brand email.
    """
    raw = result.get("brand_raw_data") or {}
    brand_name = result.get("brand_name", "")
    if pic_email is None:
        pic_email = raw.get("email") or ""
    salutation = _t(
        "sendMailUtils.salutation",
        {"brandName": brand_name, "picName": raw.get("pic_name") or ""},
        language,
    )
    intro = _t(
        "sendMailUtils.intro",
        {
            "brandName": brand_name,
            "storeLink": raw.get("store_link") or "",
            "kategori": raw.get("kategori") or "",
        },
        language,
    )
    body = render_email(result, language=language, fmt="text")
    return f"[EMAIL TO: {pic_email}]\n\n{salutation}\n\n{intro}\n\n{body}"


def render_email(
    result: dict[str, Any],
    *,
    language: str = "id",
    fmt: Literal["html", "text"] = "html",
    chart_src: str = "",
    header_src: str = "",
    footer_src: str = "",
    syb_src: str = "",
    note: str | None = None,
) -> str:
    """Render the evaluation email in *language* as ``fmt`` ("text" or "html").

    *result* is the evaluation dict (EvaluationDetailResponse-shaped):
    ``brand_name``, ``period``, ``score_breakdown`` and ``calculator_results``.

    The text format consumes only ``score_breakdown`` and
    ``calculator_results`` (incl. ``scoring_summary``).  The HTML format also
    needs the image ``*_src`` URIs and an optional ``note``.
    """
    if fmt == "text":
        return _render_text(result, language)

    # HTML path delegates to the styled section renderers in template.py.
    from app.modules.email import template as _template

    return _template.render_email_html_body(
        evaluation_data=result,
        chart_src=chart_src,
        header_src=header_src,
        footer_src=footer_src,
        syb_src=syb_src,
        note=note,
        language=language,
    )
