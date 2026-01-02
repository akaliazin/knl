"""Datetime utilities using pendulum for consistent timezone handling.

This module provides a clean interface for datetime operations, ensuring all
datetimes are timezone-aware and use UTC by default. Uses pendulum internally
but returns standard datetime objects for type compatibility.
"""

from datetime import datetime
from typing import Any

import pendulum


def now() -> datetime:
    """
    Get current UTC time (timezone-aware).

    Returns:
        Current datetime in UTC

    Example:
        >>> dt = now()
        >>> dt.tzinfo is not None
        True
    """
    return pendulum.now("UTC")


def parse(dt_input: str | datetime | Any) -> datetime:
    """
    Parse datetime from various inputs.

    Handles:
    - ISO format strings (with or without timezone)
    - datetime objects (converts to UTC if needed)
    - Pendulum objects
    - Any other datetime-like object

    Args:
        dt_input: Datetime string, datetime object, or datetime-like object

    Returns:
        Timezone-aware datetime in UTC

    Example:
        >>> dt = parse("2026-01-02T15:30:00+03:00")
        >>> dt.hour  # Converted to UTC
        12
        >>> dt = parse("2026-01-02 15:30:00")  # Naive - assumes UTC
        >>> dt.hour
        15
    """
    if isinstance(dt_input, datetime):
        return ensure_utc(dt_input)

    if isinstance(dt_input, str):
        try:
            parsed = pendulum.parse(dt_input)
            if parsed is None:
                raise ValueError(f"Could not parse datetime: {dt_input}")
            return ensure_utc(parsed)
        except Exception as e:
            raise ValueError(f"Could not parse datetime: {dt_input}") from e

    # Try to convert pendulum or other datetime-like objects
    try:
        return ensure_utc(pendulum.instance(dt_input))
    except (TypeError, ValueError, AttributeError) as e:
        raise ValueError(f"Could not parse datetime from {type(dt_input)}: {dt_input}") from e


def ensure_utc(dt: datetime) -> datetime:
    """
    Ensure datetime is timezone-aware and in UTC.

    If datetime is naive, assumes it's UTC.
    If datetime has a timezone, converts to UTC.

    Args:
        dt: Datetime to ensure is UTC

    Returns:
        Timezone-aware datetime in UTC

    Example:
        >>> from datetime import datetime, timezone, timedelta
        >>> naive = datetime(2026, 1, 2, 15, 30)
        >>> aware = ensure_utc(naive)
        >>> aware.tzinfo is not None
        True
        >>> # With timezone
        >>> moscow_tz = timezone(timedelta(hours=3))
        >>> moscow_dt = datetime(2026, 1, 2, 15, 30, tzinfo=moscow_tz)
        >>> utc_dt = ensure_utc(moscow_dt)
        >>> utc_dt.hour
        12
    """
    pdt = pendulum.instance(dt)

    if pdt.timezone_name is None:
        # Naive datetime - assume UTC
        pdt = pdt.in_timezone("UTC")
    elif pdt.timezone_name != "UTC":
        # Has timezone but not UTC - convert
        pdt = pdt.in_timezone("UTC")

    return pdt


def to_iso(dt: datetime) -> str:
    """
    Format datetime as ISO 8601 string.

    Args:
        dt: Datetime to format

    Returns:
        ISO 8601 formatted string

    Example:
        >>> dt = parse("2026-01-02T15:30:00Z")
        >>> iso = to_iso(dt)
        >>> "2026-01-02T15:30:00" in iso
        True
    """
    return pendulum.instance(dt).to_iso8601_string()


def from_timestamp(ts: float | int) -> datetime:
    """
    Create datetime from Unix timestamp.

    Args:
        ts: Unix timestamp (seconds since epoch)

    Returns:
        Timezone-aware datetime in UTC

    Example:
        >>> dt = from_timestamp(1735826400)
        >>> dt.year
        2025
    """
    return pendulum.from_timestamp(ts, tz="UTC")


def to_timestamp(dt: datetime) -> float:
    """
    Convert datetime to Unix timestamp.

    Args:
        dt: Datetime to convert

    Returns:
        Unix timestamp (seconds since epoch)

    Example:
        >>> dt = parse("2026-01-02T00:00:00Z")
        >>> ts = to_timestamp(dt)
        >>> ts > 0
        True
    """
    return pendulum.instance(dt).timestamp()


def human_diff(dt: datetime, other: datetime | None = None) -> str:
    """
    Get human-readable difference between datetimes.

    Args:
        dt: Datetime to compare
        other: Other datetime (defaults to now)

    Returns:
        Human-readable string like "2 hours ago" or "in 3 days"

    Example:
        >>> past = parse("2026-01-01T00:00:00Z")
        >>> now_dt = parse("2026-01-02T00:00:00Z")
        >>> diff = human_diff(past, now_dt)
        >>> "day" in diff or "hour" in diff
        True
    """
    pdt = pendulum.instance(dt)
    if other is None:
        return pdt.diff_for_humans()
    return pdt.diff_for_humans(pendulum.instance(other))


def is_aware(dt: datetime) -> bool:
    """
    Check if datetime is timezone-aware.

    Args:
        dt: Datetime to check

    Returns:
        True if timezone-aware, False if naive

    Example:
        >>> aware = now()
        >>> is_aware(aware)
        True
        >>> from datetime import datetime
        >>> naive = datetime(2026, 1, 2)
        >>> is_aware(naive)
        False
    """
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None
