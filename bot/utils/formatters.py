"""Formatting helpers."""

from __future__ import annotations

from datetime import datetime


def fmt_money(value: float | int) -> str:
    """Format number as money with spaces."""
    return f"{value:,.0f}".replace(",", " ") + " ₸"


def fmt_date(dt: datetime) -> str:
    """Format datetime to DD.MM.YYYY."""
    return dt.strftime("%d.%m.%Y")


def parse_date(value: str) -> datetime:
    """Parse date in DD.MM.YYYY format."""
    return datetime.strptime(value.strip(), "%d.%m.%Y")
