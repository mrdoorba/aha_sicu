"""Package fit — a brand's VP score read against the bar its package sets.

The BD sheet ships two columns per brand: ``Package`` (New Star / Rising Star /
Superstar) and ``VP`` (0-110). Each package sets a minimum VP; a brand whose VP
falls short of it loses 10 points off its AHA Compatibility Score.

Everything the rule needs is in the brand's VP ``raw_data``, so this module
takes that dict and answers with the whole verdict — bar, shortfall and
adjustment together. Sheet quirks stay inside: a blank, non-numeric or ``0`` VP
means "not yet scored" (it marks a duplicate row whose real data lives on the
brand's other row), and an unrecognised package has no bar at all. Neither is
penalised — a brand never loses points over the sheet's own bookkeeping.
"""

from dataclasses import dataclass

# Minimum VP per package. Keys are the sheet's own spelling.
PACKAGE_BARS: dict[str, float] = {
    "New Star": 65.0,
    "Rising Star": 80.0,
    "Superstar": 80.0,
}

#: Points deducted when VP falls below the package's bar.
VP_SHORTFALL_PENALTY = 10.0

_PACKAGE_COLUMN = "Package"
_VP_COLUMN = "VP"


@dataclass(frozen=True)
class PackageFit:
    """How a brand's VP sits against its package's bar.

    ``adjustment`` is what the scoring calculator adds to the category total:
    ``0.0`` when the bar is met or cannot be judged, ``-10.0`` when VP falls
    short. ``bar`` is ``None`` for an unrecognised package and ``vp`` is
    ``None`` when the sheet carries no usable number.
    """

    package: str | None
    vp: float | None
    bar: float | None
    adjustment: float

    @property
    def judged(self) -> bool:
        """True when both a bar and a VP number were available to compare."""
        return self.bar is not None and self.vp is not None

    @property
    def met(self) -> bool | None:
        """True/False when judged, ``None`` when there was nothing to judge."""
        if not self.judged:
            return None
        return self.adjustment == 0.0


def _read_vp(raw_value: object) -> float | None:
    """Parse the sheet's VP cell, or ``None`` when it carries no real number."""
    text = str(raw_value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        vp = float(text)
    except ValueError:
        return None
    # 0 marks a duplicate row, not a brand that scored zero.
    return None if vp == 0.0 else vp


def has_scored_vp(raw_data: dict | None) -> bool:
    """True when a VP sheet row carries a real VP number.

    The sheet lists some brands on two rows: the real one scored, the leftover
    one blank or ``0``. Sync reads this to keep the scored row, so the same fact
    about what counts as a VP decides both the penalty and which row survives.
    """
    return _read_vp((raw_data or {}).get(_VP_COLUMN)) is not None


def read_package_fit(raw_data: dict | None) -> PackageFit:
    """Judge a brand's VP against its package, from its VP sheet row."""
    raw_data = raw_data or {}
    package = str(raw_data.get(_PACKAGE_COLUMN) or "").strip() or None
    bar = PACKAGE_BARS.get(package) if package else None
    vp = _read_vp(raw_data.get(_VP_COLUMN))

    short = bar is not None and vp is not None and vp < bar
    return PackageFit(
        package=package,
        vp=vp,
        bar=bar,
        adjustment=-VP_SHORTFALL_PENALTY if short else 0.0,
    )
