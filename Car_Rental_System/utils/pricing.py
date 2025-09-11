# utils/pricing.py
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

def parse_yyyy_mm_dd(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

def rental_days(start: date, end: date) -> int:
    """Inclusive day count (e.g., 2025-09-06..08 = 3 days)."""
    return (end - start).days + 1

def money(x) -> Decimal:
    return (Decimal(str(x))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def compute_total(
    daily_rate: Decimal | float | str,
    start: date,
    end: date,
    min_days: int | None = None,
    max_days: int | None = None,
    fees: list[Decimal | float | str] | None = None,
    tax_rate: Decimal | float | str | None = None,  # e.g., 0.15 for 15%
):
    days = rental_days(start, end)
    if min_days and days < min_days:
        days = min_days
    if max_days and days > max_days:
        raise ValueError("Requested period exceeds car's maximum rent period")

    base = money(Decimal(str(daily_rate)) * days)
    fee_total = money(sum(Decimal(str(f)) for f in (fees or [])))
    subtotal = base + fee_total
    tax = money(subtotal * Decimal(str(tax_rate))) if tax_rate is not None else money(0)
    total = money(subtotal + tax)

    return {
        "days": days,
        "base": base,
        "fees": fee_total,
        "tax": tax,
        "total": total,
    }
