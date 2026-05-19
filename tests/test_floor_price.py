from __future__ import annotations
"""
Tests for dynamic floor price calculation.
"""
import pytest

from app.models.publisher import AdSlot, FloorPriceRule, AdFormat
from app.services.floor_price import calculate_floor_price, device_type_from_openrtb


def make_slot(
    base_cpm: float = 1.0,
    geo_multipliers: dict | None = None,
    device_multipliers: dict | None = None,
) -> AdSlot:
    return AdSlot(
        id="slot_test",
        site_id="site_test",
        name="Test Slot",
        ad_format=AdFormat.BANNER,
        floor_price=FloorPriceRule(
            base_cpm_usd=base_cpm,
            geo_multipliers=geo_multipliers or {},
            device_multipliers=device_multipliers or {},
        ),
    )


def test_base_floor_no_multipliers():
    slot = make_slot(base_cpm=1.50)
    assert calculate_floor_price(slot) == 1.50


def test_geo_multiplier_applied():
    slot = make_slot(base_cpm=1.00, geo_multipliers={"USA": 2.5})
    assert calculate_floor_price(slot, country="USA") == 2.50


def test_device_multiplier_applied():
    slot = make_slot(base_cpm=1.00, device_multipliers={"mobile": 0.8})
    assert calculate_floor_price(slot, device_type="mobile") == 0.80


def test_both_multipliers_applied():
    slot = make_slot(
        base_cpm=1.00,
        geo_multipliers={"GBR": 1.5},
        device_multipliers={"desktop": 2.0},
    )
    result = calculate_floor_price(slot, country="GBR", device_type="desktop")
    assert result == 3.00


def test_unknown_country_uses_base():
    slot = make_slot(base_cpm=1.00, geo_multipliers={"USA": 2.5})
    assert calculate_floor_price(slot, country="XYZ") == 1.00


def test_floor_never_negative():
    slot = make_slot(base_cpm=1.00, device_multipliers={"mobile": -1.0})
    result = calculate_floor_price(slot, device_type="mobile")
    assert result >= 0.0


def test_device_type_from_openrtb_mobile():
    assert device_type_from_openrtb(1) == "mobile"
    assert device_type_from_openrtb(4) == "mobile"
    assert device_type_from_openrtb(5) == "mobile"


def test_device_type_from_openrtb_desktop():
    assert device_type_from_openrtb(2) == "desktop"


def test_device_type_from_openrtb_unknown():
    assert device_type_from_openrtb(None) is None
    assert device_type_from_openrtb(99) is None
