"""Pydantic schemas for brands module."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, computed_field, field_validator

from app.calculators.package_fit import read_package_fit


def _parse_json(v: Any) -> dict[str, Any] | None:
    """Parse JSONB value that asyncpg may return as a string."""
    if v is None:
        return None
    if isinstance(v, str):
        return json.loads(v)
    return v


class PackageFitSchema(BaseModel):
    """A brand's VP read against the bar its package sets.

    ``adjustment`` is the points the AHA Compatibility Score gains or loses
    (``-10.0`` on a shortfall). ``bar`` is null for an unrecognised package and
    ``vp`` is null when the sheet carries no usable number; ``met`` is null
    whenever there was nothing to judge.
    """

    package: str | None
    vp: float | None
    bar: float | None
    adjustment: float
    met: bool | None


class BrandListItem(BaseModel):
    """Individual brand item in paginated list."""

    id: int
    brand_name: str
    raw_data: dict[str, Any]
    updated_at: datetime
    marketplace: str = "ID"
    meeting_raw_data: dict[str, Any] | None = None

    @field_validator("raw_data", "meeting_raw_data", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any] | None:
        return _parse_json(v)


class BrandDetailResponse(BaseModel):
    """Single brand detail response."""

    id: int
    brand_name: str
    raw_data: dict[str, Any]
    updated_at: datetime
    marketplace: str = "ID"
    meeting_raw_data: dict[str, Any] | None = None

    @field_validator("raw_data", "meeting_raw_data", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any] | None:
        return _parse_json(v)

    @computed_field
    @property
    def package_fit(self) -> PackageFitSchema:
        """Derived from raw_data, so the header can show it before scoring runs."""
        fit = read_package_fit(self.raw_data)
        return PackageFitSchema(
            package=fit.package,
            vp=fit.vp,
            bar=fit.bar,
            adjustment=fit.adjustment,
            met=fit.met,
        )


class BrandListResponse(BaseModel):
    """Paginated response for brand list."""

    items: list[BrandListItem]
    total: int
    page: int
    limit: int
    pages: int
