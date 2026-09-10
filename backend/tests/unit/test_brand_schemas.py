"""Brand detail carries the package fit, so the header can show it early."""

from datetime import datetime

from app.modules.brands.schemas import BrandDetailResponse


def _detail(raw_data: dict) -> BrandDetailResponse:
    return BrandDetailResponse(
        id=1,
        brand_name="Lem Castol",
        raw_data=raw_data,
        updated_at=datetime(2026, 9, 10, 12, 0),
        marketplace="ID",
    )


def test_package_fit_is_derived_from_the_vp_row():
    fit = _detail({"Package": "New Star", "VP": "65"}).package_fit

    assert (fit.package, fit.vp, fit.bar) == ("New Star", 65.0, 65.0)
    assert fit.adjustment == 0.0
    assert fit.met is True


def test_shortfall_is_reported_with_the_bar_it_missed():
    fit = _detail({"Package": "Superstar", "VP": "50"}).package_fit

    assert fit.bar == 80.0
    assert fit.adjustment == -10.0
    assert fit.met is False


def test_row_without_the_columns_still_serialises():
    fit = _detail({"PIC": "Jeffrey Handono"}).package_fit

    assert (fit.package, fit.vp, fit.bar, fit.met) == (None, None, None, None)
    assert fit.adjustment == 0.0


def test_package_fit_is_part_of_the_serialised_response():
    payload = _detail({"Package": "Rising Star", "VP": "65"}).model_dump()

    assert payload["package_fit"] == {
        "package": "Rising Star",
        "vp": 65.0,
        "bar": 80.0,
        "adjustment": -10.0,
        "met": False,
    }
