"""Tests for datetime utilities."""

import pytest
from datetime import datetime, timezone, timedelta
import pendulum

from src.knl.utils.dt import (
    now,
    parse,
    ensure_utc,
    to_iso,
    from_timestamp,
    to_timestamp,
    human_diff,
    is_aware,
)


class TestNow:
    """Tests for now() function."""

    def test_returns_datetime(self):
        """Should return datetime object."""
        result = now()
        assert isinstance(result, datetime)

    def test_is_timezone_aware(self):
        """Should return timezone-aware datetime."""
        result = now()
        assert result.tzinfo is not None

    def test_is_utc(self):
        """Should return UTC timezone."""
        result = now()
        assert result.tzinfo.tzname(result) == "UTC"

    def test_close_to_current_time(self):
        """Should return time close to actual current time."""
        before = datetime.now(timezone.utc)
        result = now()
        after = datetime.now(timezone.utc)

        assert before <= result <= after


class TestParse:
    """Tests for parse() function."""

    def test_parse_iso_with_timezone(self):
        """Should parse ISO string with timezone."""
        result = parse("2026-01-02T15:30:00+03:00")

        assert result.year == 2026
        assert result.month == 1
        assert result.day == 2
        # Should be converted to UTC (15:30 +03:00 = 12:30 UTC)
        assert result.hour == 12
        assert result.minute == 30

    def test_parse_iso_without_timezone(self):
        """Should parse ISO string without timezone (assumes UTC)."""
        result = parse("2026-01-02T15:30:00")

        assert result.year == 2026
        assert result.hour == 15
        assert result.tzinfo is not None

    def test_parse_iso_z_suffix(self):
        """Should parse ISO string with Z suffix."""
        result = parse("2026-01-02T15:30:00Z")

        assert result.year == 2026
        assert result.hour == 15
        assert result.tzinfo.tzname(result) == "UTC"

    def test_parse_datetime_object_naive(self):
        """Should convert naive datetime to UTC."""
        naive_dt = datetime(2026, 1, 2, 15, 30)
        result = parse(naive_dt)

        assert result.year == 2026
        assert result.hour == 15
        assert result.tzinfo is not None

    def test_parse_datetime_object_with_timezone(self):
        """Should convert aware datetime to UTC."""
        moscow_tz = timezone(timedelta(hours=3))
        moscow_dt = datetime(2026, 1, 2, 15, 30, tzinfo=moscow_tz)
        result = parse(moscow_dt)

        assert result.year == 2026
        assert result.hour == 12  # Converted from Moscow to UTC
        assert result.tzinfo.tzname(result) == "UTC"

    def test_parse_pendulum_object(self):
        """Should handle pendulum objects."""
        pdt = pendulum.parse("2026-01-02T15:30:00+03:00")
        result = parse(pdt)

        assert isinstance(result, datetime)
        assert result.hour == 12  # Converted to UTC

    def test_parse_invalid_string(self):
        """Should raise ValueError for invalid string."""
        with pytest.raises(ValueError, match="Could not parse"):
            parse("not a date")

    def test_parse_invalid_type(self):
        """Should raise ValueError for invalid type."""
        with pytest.raises(ValueError, match="Could not parse"):
            parse(12345)  # Just a number


class TestEnsureUtc:
    """Tests for ensure_utc() function."""

    def test_naive_datetime_assumes_utc(self):
        """Should treat naive datetime as UTC."""
        naive_dt = datetime(2026, 1, 2, 15, 30)
        result = ensure_utc(naive_dt)

        assert result.year == 2026
        assert result.hour == 15
        assert result.tzinfo.tzname(result) == "UTC"

    def test_aware_utc_unchanged(self):
        """Should keep UTC datetime unchanged."""
        utc_dt = datetime(2026, 1, 2, 15, 30, tzinfo=timezone.utc)
        result = ensure_utc(utc_dt)

        assert result.year == 2026
        assert result.hour == 15
        assert result.tzinfo.tzname(result) == "UTC"

    def test_aware_non_utc_converts(self):
        """Should convert non-UTC timezone to UTC."""
        tokyo_tz = timezone(timedelta(hours=9))
        tokyo_dt = datetime(2026, 1, 2, 15, 30, tzinfo=tokyo_tz)
        result = ensure_utc(tokyo_dt)

        assert result.year == 2026
        assert result.hour == 6  # 15:30 JST = 06:30 UTC
        assert result.tzinfo.tzname(result) == "UTC"

    def test_preserves_datetime_type(self):
        """Should return datetime (not pendulum) object."""
        dt = datetime(2026, 1, 2, 15, 30)
        result = ensure_utc(dt)

        # Should be datetime, though might be pendulum.DateTime subclass
        assert isinstance(result, datetime)


class TestToIso:
    """Tests for to_iso() function."""

    def test_formats_to_iso8601(self):
        """Should format datetime as ISO 8601 string."""
        dt = datetime(2026, 1, 2, 15, 30, 0, tzinfo=timezone.utc)
        result = to_iso(dt)

        assert "2026-01-02" in result
        assert "15:30:00" in result

    def test_includes_timezone(self):
        """Should include timezone information."""
        dt = datetime(2026, 1, 2, 15, 30, 0, tzinfo=timezone.utc)
        result = to_iso(dt)

        # Should have either Z or +00:00
        assert "Z" in result or "+00:00" in result

    def test_handles_naive_datetime(self):
        """Should handle naive datetime (treats as UTC)."""
        dt = datetime(2026, 1, 2, 15, 30, 0)
        result = to_iso(dt)

        assert isinstance(result, str)
        assert "2026-01-02" in result


class TestFromTimestamp:
    """Tests for from_timestamp() function."""

    def test_creates_datetime_from_timestamp(self):
        """Should create datetime from Unix timestamp."""
        # 2026-01-02 00:00:00 UTC
        ts = 1767312000
        result = from_timestamp(ts)

        assert result.year == 2026
        assert result.month == 1
        assert result.day == 2

    def test_result_is_utc(self):
        """Should create UTC datetime."""
        ts = 1767312000
        result = from_timestamp(ts)

        assert result.tzinfo.tzname(result) == "UTC"

    def test_handles_integer_timestamp(self):
        """Should handle integer timestamps."""
        result = from_timestamp(1767312000)
        assert isinstance(result, datetime)

    def test_handles_float_timestamp(self):
        """Should handle float timestamps."""
        result = from_timestamp(1767312000.123)
        assert isinstance(result, datetime)


class TestToTimestamp:
    """Tests for to_timestamp() function."""

    def test_converts_datetime_to_timestamp(self):
        """Should convert datetime to Unix timestamp."""
        dt = datetime(2026, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        result = to_timestamp(dt)

        assert isinstance(result, float)
        assert result == 1767312000.0

    def test_handles_naive_datetime(self):
        """Should handle naive datetime (treats as UTC)."""
        dt = datetime(2026, 1, 2, 0, 0, 0)
        result = to_timestamp(dt)

        assert isinstance(result, float)
        assert result > 0

    def test_roundtrip_timestamp(self):
        """Should roundtrip: datetime -> timestamp -> datetime."""
        original = datetime(2026, 1, 2, 15, 30, 45, tzinfo=timezone.utc)
        ts = to_timestamp(original)
        restored = from_timestamp(ts)

        assert restored.year == original.year
        assert restored.month == original.month
        assert restored.day == original.day
        assert restored.hour == original.hour
        assert restored.minute == original.minute
        assert restored.second == original.second


class TestHumanDiff:
    """Tests for human_diff() function."""

    def test_diff_with_past_datetime(self):
        """Should describe past datetime."""
        past = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        now_dt = datetime(2026, 1, 2, 0, 0, 0, tzinfo=timezone.utc)

        result = human_diff(past, now_dt)

        assert isinstance(result, str)
        # Should mention it's in the past
        assert "ago" in result or "day" in result

    def test_diff_with_future_datetime(self):
        """Should describe future datetime."""
        future = datetime(2026, 1, 3, 0, 0, 0, tzinfo=timezone.utc)
        now_dt = datetime(2026, 1, 2, 0, 0, 0, tzinfo=timezone.utc)

        result = human_diff(future, now_dt)

        assert isinstance(result, str)

    def test_diff_without_other_uses_now(self):
        """Should use current time if other is None."""
        # Create a datetime a few seconds ago
        past = datetime.now(timezone.utc) - timedelta(seconds=5)

        result = human_diff(past)

        assert isinstance(result, str)
        assert "second" in result or "moment" in result or "ago" in result

    def test_handles_naive_datetimes(self):
        """Should handle naive datetimes."""
        dt1 = datetime(2026, 1, 1, 0, 0, 0)
        dt2 = datetime(2026, 1, 2, 0, 0, 0)

        result = human_diff(dt1, dt2)

        assert isinstance(result, str)


class TestIsAware:
    """Tests for is_aware() function."""

    def test_aware_datetime_returns_true(self):
        """Should return True for timezone-aware datetime."""
        aware_dt = datetime(2026, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        assert is_aware(aware_dt) is True

    def test_naive_datetime_returns_false(self):
        """Should return False for naive datetime."""
        naive_dt = datetime(2026, 1, 2, 0, 0, 0)
        assert is_aware(naive_dt) is False

    def test_now_result_is_aware(self):
        """Result from now() should be aware."""
        dt = now()
        assert is_aware(dt) is True

    def test_parsed_result_is_aware(self):
        """Result from parse() should be aware."""
        dt = parse("2026-01-02T00:00:00")
        assert is_aware(dt) is True


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_parse_to_iso_roundtrip(self):
        """Should roundtrip: parse -> to_iso -> parse."""
        original = "2026-01-02T15:30:00+03:00"

        dt = parse(original)
        iso_str = to_iso(dt)
        restored = parse(iso_str)

        # Times should match (both in UTC)
        assert dt.hour == restored.hour
        assert dt.minute == restored.minute

    def test_ensure_consistency_across_operations(self):
        """All operations should produce consistent UTC datetimes."""
        # Create datetime in different ways
        dt1 = now()
        dt2 = parse("2026-01-02T15:30:00+03:00")
        dt3 = ensure_utc(datetime(2026, 1, 2, 12, 30, 0))
        dt4 = from_timestamp(1767225600)

        # All should be timezone-aware
        assert is_aware(dt1)
        assert is_aware(dt2)
        assert is_aware(dt3)
        assert is_aware(dt4)

        # All should be UTC
        assert dt1.tzinfo.tzname(dt1) == "UTC"
        assert dt2.tzinfo.tzname(dt2) == "UTC"
        assert dt3.tzinfo.tzname(dt3) == "UTC"
        assert dt4.tzinfo.tzname(dt4) == "UTC"

    def test_comparison_works_correctly(self):
        """Should be able to compare datetimes from different sources."""
        dt1 = parse("2026-01-02T15:30:00Z")
        dt2 = parse("2026-01-02T18:30:00+03:00")  # Same as dt1 in UTC

        # Should be equal
        assert dt1 == dt2

        dt3 = parse("2026-01-02T16:30:00Z")
        assert dt3 > dt1
