"""Unit tests for _ensure_dict helper and JSONB data integrity."""

import json

from app.core.utils import ensure_dict as _ensure_dict


class TestEnsureDict:
    """Tests for _ensure_dict defensive JSON parsing."""

    def test_dict_passthrough(self):
        """Properly-encoded JSONB (dict) is returned as-is."""
        data = {"business": {"salesMonth0": 500_000_000}, "operational": {"unfulfilledOrderRate": 0.5}}
        assert _ensure_dict(data) is data

    def test_double_encoded_string(self):
        """Legacy double-encoded JSONB (string) is parsed to dict."""
        data = {"business": {"salesMonth0": 500_000_000}, "visitors": {"totalFollowers": 60000}}
        encoded = json.dumps(data)
        result = _ensure_dict(encoded)
        assert isinstance(result, dict)
        assert result["business"]["salesMonth0"] == 500_000_000
        assert result["visitors"]["totalFollowers"] == 60000

    def test_none_returns_empty_dict(self):
        """None value returns empty dict."""
        assert _ensure_dict(None) == {}

    def test_empty_string_returns_empty_dict(self):
        """Empty string returns empty dict."""
        assert _ensure_dict("") == {}

    def test_invalid_json_string_returns_empty_dict(self):
        """Non-JSON string returns empty dict."""
        assert _ensure_dict("not json") == {}

    def test_json_array_string_returns_empty_dict(self):
        """JSON array string returns empty dict (not a dict)."""
        assert _ensure_dict("[1, 2, 3]") == {}

    def test_empty_dict_passthrough(self):
        """Empty dict is returned as-is."""
        data = {}
        assert _ensure_dict(data) == {}

    def test_integer_returns_empty_dict(self):
        """Non-dict, non-string types return empty dict."""
        assert _ensure_dict(42) == {}


class TestScoringWithDoubleEncodedData:
    """Integration-style tests verifying scoring handles both data formats."""

    SAMPLE_MANUAL_DATA = {
        "operational": {"unfulfilledOrderRate": 0.5, "lateShipmentRate": 0.3, "preparationTime": 0.8,
                        "chatResponseRate": 97.0, "overallRating": 4.8},
        "business": {"salesMonth0": 500_000_000, "salesMonth1": 400_000_000, "salesMonth2": 300_000_000,
                     "salesMonth3": 350_000_000, "salesMonth4": 250_000_000, "salesMonth5": 200_000_000,
                     "conversionRate": 4.0, "salesStartMonth": "2026-02"},
        "visitors": {"totalVisitors": 100000, "returningVisitors": 10000, "totalFollowers": 60000},
        "products": {"productCount": 50, "storeStatus": "Star+"},
        "ads": {"adSales": 100_000_000, "adCost": 10_000_000},
        "campaign": {"nominatedSessions": 5, "availableSessions": 10},
        "promoTools": {},
        "content": {},
        "competition": {},
    }

    def test_dict_data_produces_nonzero_business_score(self):
        """With dict manual_data, business section scores > 0."""
        from app.calculators.scoring.categories import _score_business
        data = _ensure_dict(self.SAMPLE_MANUAL_DATA)
        result = _score_business(data)
        assert result.score > 0, "Business score should be > 0 with real data"

    def test_string_data_produces_nonzero_business_score(self):
        """With double-encoded (string) manual_data, _ensure_dict recovers the dict."""
        from app.calculators.scoring.categories import _score_business
        encoded = json.dumps(self.SAMPLE_MANUAL_DATA)
        data = _ensure_dict(encoded)
        result = _score_business(data)
        assert result.score > 0, "Business score should be > 0 after parsing string"

    def test_dict_data_produces_nonzero_visitors_score(self):
        """With dict manual_data, visitors section scores > 0."""
        from app.calculators.scoring.categories import _score_visitors
        data = _ensure_dict(self.SAMPLE_MANUAL_DATA)
        result = _score_visitors(data)
        assert result.score > 0, "Visitors score should be > 0 with 60K followers"

    def test_string_data_produces_nonzero_visitors_score(self):
        """With double-encoded (string) manual_data, visitors section recovers."""
        from app.calculators.scoring.categories import _score_visitors
        encoded = json.dumps(self.SAMPLE_MANUAL_DATA)
        data = _ensure_dict(encoded)
        result = _score_visitors(data)
        assert result.score > 0, "Visitors score should be > 0 after parsing string"

    def test_both_formats_produce_identical_scores(self):
        """Dict and string manual_data produce identical scoring results."""
        from app.calculators.scoring.categories import _score_business, _score_visitors, _score_products

        dict_data = _ensure_dict(self.SAMPLE_MANUAL_DATA)
        string_data = _ensure_dict(json.dumps(self.SAMPLE_MANUAL_DATA))

        assert _score_business(dict_data).score == _score_business(string_data).score
        assert _score_visitors(dict_data).score == _score_visitors(string_data).score
        assert _score_products(dict_data).score == _score_products(string_data).score
