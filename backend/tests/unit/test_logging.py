"""Tests for structured JSON logging module."""

import json
import logging

from app.core.logging import JSONFormatter, request_id_var, setup_logging


class TestJSONFormatter:
    """Tests for JSONFormatter."""

    def test_format_produces_valid_json_with_required_keys(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=None,
            exc_info=None,
        )

        result = json.loads(formatter.format(record))

        assert result["severity"] == "INFO"
        assert result["message"] == "test message"
        assert result["logger"] == "test.logger"
        assert "timestamp" in result
        assert "request_id" in result

    def test_request_id_var_appears_in_output(self) -> None:
        formatter = JSONFormatter()
        token = request_id_var.set("req-abc-123")
        try:
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg="with request id",
                args=None,
                exc_info=None,
            )

            result = json.loads(formatter.format(record))

            assert result["request_id"] == "req-abc-123"
        finally:
            request_id_var.reset(token)

    def test_default_request_id_when_not_set(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="no request context",
            args=None,
            exc_info=None,
        )

        result = json.loads(formatter.format(record))

        assert result["request_id"] == "no-request"

    def test_exception_info_included_when_present(self) -> None:
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="error occurred",
            args=None,
            exc_info=exc_info,
        )

        result = json.loads(formatter.format(record))

        assert "exception" in result
        assert "ValueError: test error" in result["exception"]

    def test_no_exception_key_when_no_exc_info(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="no error",
            args=None,
            exc_info=None,
        )

        result = json.loads(formatter.format(record))

        assert "exception" not in result

    def test_output_is_single_line(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="single line check",
            args=None,
            exc_info=None,
        )

        output = formatter.format(record)

        assert "\n" not in output

    def test_timestamp_is_iso_8601(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="timestamp check",
            args=None,
            exc_info=None,
        )

        result = json.loads(formatter.format(record))

        from datetime import datetime

        # Should parse without error
        datetime.fromisoformat(result["timestamp"])


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_sets_json_formatter_on_root_logger(self) -> None:
        setup_logging("INFO")
        root = logging.getLogger()

        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JSONFormatter)

    def test_respects_configured_log_level(self) -> None:
        setup_logging("DEBUG")
        root = logging.getLogger()

        assert root.level == logging.DEBUG

        # Reset to INFO
        setup_logging("INFO")

    def test_invalid_level_falls_back_to_info(self) -> None:
        setup_logging("BOGUS")
        root = logging.getLogger()

        assert root.level == logging.INFO

    def test_clears_previous_handlers(self) -> None:
        root = logging.getLogger()
        root.addHandler(logging.StreamHandler())
        root.addHandler(logging.StreamHandler())
        assert len(root.handlers) >= 2

        setup_logging("INFO")

        assert len(root.handlers) == 1
