"""Shared fixtures for email module tests."""

import base64

import pytest


@pytest.fixture
def sample_evaluation_data() -> dict:
    """Realistic evaluation data matching EvaluationDetailResponse shape."""
    return {
        "id": 42,
        "brand_id": 7,
        "brand_name": "Kopi Kenangan",
        "final_score": 78.5,
        "verdict": "✔️",
        "template": "fashion",
        "period": "Januari 2026",
        "evaluator_email": "evaluator@ahacommerce.id",
        "rule_version": 3,
        "email_output": None,
        "created_at": "2026-01-15T10:30:00",
        "score_breakdown": [
            {
                "category": "Content Performance",
                "weight": 0.35,
                "score": 82.0,
                "rows": [
                    {
                        "metric": "Engagement Rate",
                        "value": 4.2,
                        "benchmark": 3.5,
                        "verdict": "Above",
                        "score": 85,
                        "message": "Engagement rate di atas benchmark",
                    },
                    {
                        "metric": "Post Frequency",
                        "value": 12,
                        "benchmark": 10,
                        "verdict": "Above",
                        "score": 80,
                        "message": "Frekuensi posting memenuhi target",
                    },
                    {
                        "metric": "Content Quality",
                        "value": 7.5,
                        "benchmark": 7.0,
                        "verdict": "Above",
                        "score": 81,
                        "message": "Kualitas konten baik",
                    },
                ],
            },
            {
                "category": "Advertising",
                "weight": 0.35,
                "score": 75.0,
                "rows": [
                    {
                        "metric": "ROAS",
                        "value": 3.8,
                        "benchmark": 4.0,
                        "verdict": "Below",
                        "score": 70,
                        "message": "ROAS sedikit di bawah target",
                    },
                    {
                        "metric": "CTR",
                        "value": 2.1,
                        "benchmark": 1.8,
                        "verdict": "Above",
                        "score": 82,
                        "message": "CTR di atas rata-rata",
                    },
                    {
                        "metric": "CPC",
                        "value": 1500,
                        "benchmark": 2000,
                        "verdict": "Above",
                        "score": 73,
                        "message": "Cost per click terkontrol",
                    },
                ],
            },
            {
                "category": "Store Operations",
                "weight": 0.30,
                "score": 79.0,
                "rows": [
                    {
                        "metric": "Response Time",
                        "value": 15,
                        "benchmark": 30,
                        "verdict": "Above",
                        "score": 90,
                        "message": "Waktu respons sangat cepat",
                    },
                    {
                        "metric": "Order Fulfillment",
                        "value": 95,
                        "benchmark": 90,
                        "verdict": "Above",
                        "score": 85,
                        "message": "Fulfillment rate tinggi",
                    },
                    {
                        "metric": "Return Rate",
                        "value": 3.2,
                        "benchmark": 5.0,
                        "verdict": "Above",
                        "score": 62,
                        "message": "Return rate rendah, bagus",
                    },
                ],
            },
        ],
        "calculator_results": {
            "ads_keyword": {
                "top_keywords": ["kopi", "minuman", "promo"],
                "total_spend": 15000000,
            },
            "top_sku": {
                "items": [
                    {"name": "Kopi Susu Gula Aren", "revenue": 25000000},
                    {"name": "Es Kopi Mantap", "revenue": 18000000},
                ],
            },
        },
        "manual_inputs": {
            "notes": "Brand menunjukkan peningkatan signifikan di Q4",
        },
        "brand_raw_data": {
            "marketplace": "Tokopedia",
            "store_url": "https://tokopedia.com/kopikenangan",
        },
    }


@pytest.fixture
def sample_base64_png() -> str:
    """Minimal valid 1x1 transparent PNG as base64 string."""
    # Minimal 1x1 pixel transparent PNG
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"  # PNG signature
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return base64.b64encode(png_bytes).decode("ascii")
