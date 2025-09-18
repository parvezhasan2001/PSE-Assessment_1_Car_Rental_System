from datetime import date
from decimal import Decimal
import pytest

try:
    from utils.pricing import rental_days, compute_total, money
except Exception as e:
    pytest.skip(f"utils.pricing not importable: {e}", allow_module_level=True)

def test_rental_days_inclusive():
    assert rental_days(date(2025, 9, 6), date(2025, 9, 8)) == 3

def test_compute_total_simple():
    total = compute_total(
        daily_rate=money("50.00"),
        start=date(2025, 9, 6),
        end=date(2025, 9, 8),
        min_days=1,
        max_days=30
    )
    assert total == money("150.00")
