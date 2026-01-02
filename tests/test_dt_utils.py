"""Tests for datetime utilities."""

from datetime import UTC, datetime, timedelta, timezone

import pendulum
import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.knl.utils.dt import (
    ensure_utc,
    from_timestamp,
    human_diff,
    is_aware,
    now,
    parse,
    to_iso,
    to_timestamp,
)


def get_tzname(dt: datetime) -> str:
    """Get timezone name, asserting tzinfo is not None."""
    assert dt.tzinfo is not None, "datetime must be timezone-aware"
    return dt.tzinfo.tzname(dt)  # type: ignore[return-value]


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
        assert get_tzname(result) == "UTC"

    def test_close_to_current_time(self):
        """Should return time close to actual current time."""
        before = datetime.now(UTC)
        result = now()
        after = datetime.now(UTC)

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
        assert get_tzname(result) == "UTC"

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
        assert get_tzname(result) == "UTC"

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
        assert get_tzname(result) == "UTC"

    def test_aware_utc_unchanged(self):
        """Should keep UTC datetime unchanged."""
        utc_dt = datetime(2026, 1, 2, 15, 30, tzinfo=UTC)
        result = ensure_utc(utc_dt)

        assert result.year == 2026
        assert result.hour == 15
        assert get_tzname(result) == "UTC"

    def test_aware_non_utc_converts(self):
        """Should convert non-UTC timezone to UTC."""
        tokyo_tz = timezone(timedelta(hours=9))
        tokyo_dt = datetime(2026, 1, 2, 15, 30, tzinfo=tokyo_tz)
        result = ensure_utc(tokyo_dt)

        assert result.year == 2026
        assert result.hour == 6  # 15:30 JST = 06:30 UTC
        assert get_tzname(result) == "UTC"

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
        dt = datetime(2026, 1, 2, 15, 30, 0, tzinfo=UTC)
        result = to_iso(dt)

        assert "2026-01-02" in result
        assert "15:30:00" in result

    def test_includes_timezone(self):
        """Should include timezone information."""
        dt = datetime(2026, 1, 2, 15, 30, 0, tzinfo=UTC)
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

        assert get_tzname(result) == "UTC"

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
        dt = datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC)
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
        original = datetime(2026, 1, 2, 15, 30, 45, tzinfo=UTC)
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
        past = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
        now_dt = datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC)

        result = human_diff(past, now_dt)

        assert isinstance(result, str)
        # Should mention it's in the past
        assert "ago" in result or "day" in result

    def test_diff_with_future_datetime(self):
        """Should describe future datetime."""
        future = datetime(2026, 1, 3, 0, 0, 0, tzinfo=UTC)
        now_dt = datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC)

        result = human_diff(future, now_dt)

        assert isinstance(result, str)

    def test_diff_without_other_uses_now(self):
        """Should use current time if other is None."""
        # Create a datetime a few seconds ago
        past = datetime.now(UTC) - timedelta(seconds=5)

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
        aware_dt = datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC)
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
        assert get_tzname(dt1) == "UTC"
        assert get_tzname(dt2) == "UTC"
        assert get_tzname(dt3) == "UTC"
        assert get_tzname(dt4) == "UTC"

    def test_comparison_works_correctly(self):
        """Should be able to compare datetimes from different sources."""
        dt1 = parse("2026-01-02T15:30:00Z")
        dt2 = parse("2026-01-02T18:30:00+03:00")  # Same as dt1 in UTC

        # Should be equal
        assert dt1 == dt2

        dt3 = parse("2026-01-02T16:30:00Z")
        assert dt3 > dt1

class TestTimezones:
    """Tests for various timezone handling."""

    def test_edt_conversion(self):
        """Should correctly convert EDT (US Eastern Daylight Time) to UTC."""
        # EDT is UTC-4
        edt_str = "2026-06-15T14:30:00-04:00"
        result = parse(edt_str)

        assert result.hour == 18  # 14:30 EDT = 18:30 UTC
        assert result.minute == 30
        assert get_tzname(result) == "UTC"

    def test_est_conversion(self):
        """Should correctly convert EST (US Eastern Standard Time) to UTC."""
        # EST is UTC-5
        est_str = "2026-01-15T14:30:00-05:00"
        result = parse(est_str)

        assert result.hour == 19  # 14:30 EST = 19:30 UTC
        assert result.minute == 30
        assert get_tzname(result) == "UTC"

    def test_london_bst_conversion(self):
        """Should correctly convert London BST (British Summer Time) to UTC."""
        # BST is UTC+1
        bst_str = "2026-06-15T14:30:00+01:00"
        result = parse(bst_str)

        assert result.hour == 13  # 14:30 BST = 13:30 UTC
        assert result.minute == 30
        assert get_tzname(result) == "UTC"

    def test_london_gmt_conversion(self):
        """Should correctly convert London GMT to UTC."""
        # GMT is UTC+0
        gmt_str = "2026-01-15T14:30:00+00:00"
        result = parse(gmt_str)

        assert result.hour == 14  # 14:30 GMT = 14:30 UTC
        assert result.minute == 30
        assert get_tzname(result) == "UTC"

    def test_singapore_conversion(self):
        """Should correctly convert Singapore time (SGT) to UTC."""
        # SGT is UTC+8
        sgt_str = "2026-01-15T14:30:00+08:00"
        result = parse(sgt_str)

        assert result.hour == 6  # 14:30 SGT = 06:30 UTC
        assert result.minute == 30
        assert get_tzname(result) == "UTC"

    def test_tokyo_conversion(self):
        """Should correctly convert Tokyo time (JST) to UTC."""
        # JST is UTC+9
        jst_str = "2026-01-15T14:30:00+09:00"
        result = parse(jst_str)

        assert result.hour == 5  # 14:30 JST = 05:30 UTC
        assert result.minute == 30
        assert get_tzname(result) == "UTC"

    def test_comparison_across_timezones(self):
        """Should correctly compare datetimes from different timezones."""
        edt = parse("2026-06-15T10:00:00-04:00")  # 14:00 UTC
        london = parse("2026-06-15T15:00:00+01:00")  # 14:00 UTC
        singapore = parse("2026-06-15T22:00:00+08:00")  # 14:00 UTC
        tokyo = parse("2026-06-15T23:00:00+09:00")  # 14:00 UTC

        # All should be equal when converted to UTC
        assert edt == london == singapore == tokyo

    def test_timestamp_consistency_across_timezones(self):
        """Timestamps should be same regardless of source timezone."""
        edt = parse("2026-06-15T10:00:00-04:00")
        singapore = parse("2026-06-15T22:00:00+08:00")

        ts_edt = to_timestamp(edt)
        ts_singapore = to_timestamp(singapore)

        assert ts_edt == ts_singapore


class TestDSTTransitions:
    """Tests for daylight saving time transitions."""

    def test_us_spring_forward(self):
        """Should handle US spring DST transition (2nd Sunday in March)."""
        # In 2026, DST starts March 8 at 2:00 AM (spring forward to 3:00 AM)
        before_dst = parse("2026-03-08T01:59:00-05:00")  # EST (06:59 UTC)
        after_dst = parse("2026-03-08T03:00:00-04:00")   # EDT (07:00 UTC)

        # Should be 1 minute apart in UTC (clock jumps from 01:59 to 03:00)
        diff = (after_dst - before_dst).total_seconds()
        assert diff == 60  # 60 seconds difference in UTC

    def test_us_fall_back(self):
        """Should handle US fall DST transition (1st Sunday in November)."""
        # In 2026, DST ends November 1 at 2:00 AM (fall back to 1:00 AM)
        before_dst = parse("2026-11-01T01:59:00-04:00")  # EDT (05:59 UTC)
        after_dst = parse("2026-11-01T01:00:00-05:00")   # EST (06:00 UTC)

        # They should be 1 minute apart in UTC
        diff_seconds = (after_dst - before_dst).total_seconds()
        assert diff_seconds == 60  # 60 seconds

    def test_eu_spring_forward(self):
        """Should handle EU spring DST transition (last Sunday in March)."""
        # In 2026, EU DST starts March 29 at 1:00 AM UTC (spring forward)
        before_dst = parse("2026-03-29T00:59:00+00:00")  # GMT (00:59 UTC)
        after_dst = parse("2026-03-29T02:00:00+01:00")   # BST (01:00 UTC)

        # Should be 1 minute apart in UTC (clock jumps from 01:00 to 02:00)
        diff = (after_dst - before_dst).total_seconds()
        assert diff == 60  # 60 seconds

    def test_eu_fall_back(self):
        """Should handle EU fall DST transition (last Sunday in October)."""
        # In 2026, EU DST ends October 25 at 1:00 AM UTC (fall back)
        before_dst = parse("2026-10-25T01:59:00+01:00")  # BST (00:59 UTC)
        after_dst = parse("2026-10-25T01:00:00+00:00")   # GMT (01:00 UTC)

        # They should be 1 minute apart in UTC
        diff_seconds = (after_dst - before_dst).total_seconds()
        assert diff_seconds == 60  # 60 seconds

    def test_dst_aware_comparison(self):
        """Should correctly compare times around DST transitions."""
        # Times during different DST periods but same clock time
        summer = parse("2026-06-15T12:00:00-04:00")  # EDT
        winter = parse("2026-12-15T12:00:00-05:00")  # EST

        # Summer time should be 1 hour earlier in UTC
        assert summer.hour == 16  # 12:00 EDT = 16:00 UTC
        assert winter.hour == 17  # 12:00 EST = 17:00 UTC
        assert winter > summer

    def test_timestamp_across_dst_boundary(self):
        """Timestamps should be monotonic across DST changes."""
        times = [
            parse("2026-03-08T01:00:00-05:00"),  # Before DST
            parse("2026-03-08T01:30:00-05:00"),
            parse("2026-03-08T03:00:00-04:00"),  # After DST (skipped 2:00-3:00)
            parse("2026-03-08T03:30:00-04:00"),
        ]

        timestamps = [to_timestamp(t) for t in times]

        # Timestamps should be strictly increasing
        for i in range(len(timestamps) - 1):
            assert timestamps[i] < timestamps[i + 1]


class TestGitTimestampHandling:
    """Tests for handling timestamps as Git produces them."""

    def test_git_iso_format_with_offset(self):
        """Should parse Git's ISO format with timezone offset."""
        # Git format: 2026-01-02T15:30:00+03:00
        git_timestamp = "2026-01-02T15:30:00+03:00"
        result = parse(git_timestamp)

        assert result.year == 2026
        assert result.month == 1
        assert result.day == 2
        assert result.hour == 12  # Converted to UTC
        assert get_tzname(result) == "UTC"

    def test_git_format_variations(self):
        """Should handle various Git timestamp formats."""
        # Test ISO format with offset
        iso_offset = parse("2026-01-02T15:30:00+03:00")
        assert iso_offset.hour == 12  # 15:30+03:00 = 12:30 UTC
        assert get_tzname(iso_offset) == "UTC"

        # Test ISO format with Z
        iso_z = parse("2026-01-02T15:30:00Z")
        assert iso_z.hour == 15  # Already UTC
        assert get_tzname(iso_z) == "UTC"

        # Test ISO format with microseconds
        iso_micro = parse("2026-01-02T15:30:00.123456+03:00")
        assert iso_micro.hour == 12
        assert iso_micro.microsecond == 123456
        assert get_tzname(iso_micro) == "UTC"

    def test_git_commit_date_comparison(self):
        """Should correctly compare Git commit dates."""
        commit1 = parse("2026-01-02T10:00:00-05:00")  # EST
        commit2 = parse("2026-01-02T16:00:00+01:00")  # CET
        commit3 = parse("2026-01-02T15:00:00Z")       # UTC

        # All are same time in UTC
        assert commit1 == commit2 == commit3

    def test_git_timestamp_to_unix_timestamp(self):
        """Should convert Git timestamps to Unix timestamps correctly."""
        git_ts = "2026-01-02T00:00:00Z"
        dt = parse(git_ts)
        unix_ts = to_timestamp(dt)

        # Should be valid Unix timestamp
        assert unix_ts > 0
        assert unix_ts == 1767312000.0

    def test_git_author_vs_committer_timezone(self):
        """Should handle different timezones for author vs committer."""
        author_tz = parse("2026-01-02T15:00:00+09:00")    # Tokyo
        committer_tz = parse("2026-01-02T01:00:00-05:00") # EST

        # Both should represent same UTC time
        assert author_tz == committer_tz
        assert author_tz.hour == 6  # 15:00 JST = 06:00 UTC
        assert committer_tz.hour == 6  # 01:00 EST = 06:00 UTC


class TestPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(st.integers(min_value=0, max_value=2**31 - 1))
    def test_timestamp_roundtrip(self, unix_timestamp):
        """Any valid Unix timestamp should roundtrip correctly."""
        dt = from_timestamp(unix_timestamp)
        ts = to_timestamp(dt)

        # Should roundtrip (allow small floating point difference)
        assert abs(ts - unix_timestamp) < 0.001

    @given(st.datetimes(
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2100, 1, 1)
    ))
    def test_datetime_always_aware(self, dt):
        """Any datetime processed should become timezone-aware."""
        result = ensure_utc(dt)

        assert is_aware(result)
        assert get_tzname(result) == "UTC"

    @given(st.integers(min_value=-12, max_value=14))
    def test_timezone_offset_handling(self, offset_hours):
        """Should handle any valid timezone offset."""
        # Create a datetime with the given offset
        tz = timezone(timedelta(hours=offset_hours))
        dt = datetime(2026, 1, 15, 12, 0, 0, tzinfo=tz)

        result = ensure_utc(dt)

        # Should be converted to UTC
        assert get_tzname(result) == "UTC"
        # Hour should be adjusted by offset
        expected_hour = (12 - offset_hours) % 24
        assert result.hour == expected_hour

    @given(
        st.datetimes(
            min_value=datetime(2000, 1, 1),
            max_value=datetime(2100, 1, 1)
        ),
        st.datetimes(
            min_value=datetime(2000, 1, 1),
            max_value=datetime(2100, 1, 1)
        )
    )
    def test_comparison_transitivity(self, dt1, dt2):
        """Datetime comparison should be transitive."""
        # Convert both to UTC
        utc1 = ensure_utc(dt1)
        utc2 = ensure_utc(dt2)

        # Comparison should work
        if utc1 < utc2:
            assert not (utc1 > utc2)
            assert not (utc1 == utc2)
        elif utc1 > utc2:
            assert not (utc1 < utc2)
            assert not (utc1 == utc2)
        else:
            assert utc1 == utc2

    @given(st.text(min_size=1, max_size=100))
    def test_parse_invalid_strings_fail_gracefully(self, random_string):
        """Parsing invalid strings should raise ValueError, not crash."""
        # Skip strings that might actually be valid dates
        assume(not any(char.isdigit() for char in random_string))

        with pytest.raises(ValueError):
            parse(random_string)

    @given(st.integers(min_value=0, max_value=2**31 - 1))
    def test_any_integer_timestamp_parseable(self, timestamp):
        """Any reasonable Unix timestamp should be parseable."""
        dt = from_timestamp(timestamp)

        # Should be timezone-aware
        assert is_aware(dt)
        # Should be in valid range
        assert dt.year >= 1970
        assert dt.year < 2100

    @given(
        st.datetimes(
            min_value=datetime(2000, 1, 1),
            max_value=datetime(2100, 1, 1)
        )
    )
    def test_iso_roundtrip(self, dt):
        """Any datetime should survive ISO string roundtrip."""
        iso = to_iso(dt)
        parsed = parse(iso)

        # Should be same time (within a second due to precision)
        diff = abs((parsed - ensure_utc(dt)).total_seconds())
        assert diff < 1.0

    def test_dst_transitions_monotonic(self):
        """Timestamps should be monotonic even across DST."""
        # Create times around DST transition
        times = []
        # US Spring forward 2026: March 8, 2:00 AM -> 3:00 AM
        base = datetime(2026, 3, 8, 0, 0, 0, tzinfo=UTC)

        for hour in range(24):
            times.append(base + timedelta(hours=hour))

        timestamps = [to_timestamp(t) for t in times]

        # All timestamps should be strictly increasing
        for i in range(len(timestamps) - 1):
            assert timestamps[i] < timestamps[i + 1]


class TestEdgeCases:
    """Tests for edge cases and corner scenarios."""

    def test_midnight_utc(self):
        """Should handle midnight UTC correctly."""
        midnight = parse("2026-01-01T00:00:00Z")

        assert midnight.hour == 0
        assert midnight.minute == 0
        assert midnight.second == 0

    def test_leap_second_handling(self):
        """Should handle dates near leap seconds gracefully."""
        # June 30 and December 31 are when leap seconds can occur
        near_leap = parse("2025-12-31T23:59:59Z")

        assert near_leap.month == 12
        assert near_leap.day == 31
        assert is_aware(near_leap)

    def test_year_boundaries(self):
        """Should handle year boundaries correctly."""
        new_year = parse("2026-01-01T00:00:00Z")
        old_year = parse("2025-12-31T23:59:59Z")

        diff = (new_year - old_year).total_seconds()
        assert diff == 1  # One second apart

    def test_february_29_leap_year(self):
        """Should handle leap year dates."""
        leap_day = parse("2024-02-29T12:00:00Z")

        assert leap_day.month == 2
        assert leap_day.day == 29
        assert leap_day.year == 2024

    def test_extreme_timezone_offsets(self):
        """Should handle extreme timezone offsets."""
        # Kiribati: UTC+14 (eastern-most timezone)
        kiribati = parse("2026-01-02T14:00:00+14:00")
        assert kiribati.hour == 0  # 14:00+14 = 00:00 next day UTC

        # Baker Island: UTC-12 (western-most timezone)
        baker = parse("2026-01-02T14:00:00-12:00")
        assert baker.hour == 2  # 14:00-12 = 02:00 next day UTC
        assert baker.day == 3  # Crosses into next day

    def test_microsecond_precision(self):
        """Should preserve microsecond precision."""
        precise = parse("2026-01-02T15:30:45.123456Z")

        assert precise.microsecond == 123456

    def test_comparison_with_microseconds(self):
        """Should correctly compare datetimes differing only by microseconds."""
        dt1 = parse("2026-01-02T15:30:45.123456Z")
        dt2 = parse("2026-01-02T15:30:45.123457Z")

        assert dt2 > dt1
        assert (dt2 - dt1).total_seconds() < 0.001

    def test_human_diff_at_boundaries(self):
        """Should handle human diff at day/month boundaries."""
        jan_31 = parse("2026-01-31T23:59:59Z")
        feb_01 = parse("2026-02-01T00:00:00Z")

        diff = human_diff(jan_31, feb_01)
        assert isinstance(diff, str)
        # Should mention seconds or minutes, not days
        assert "second" in diff or "minute" in diff
