from __future__ import annotations
"""
Dynamic floor price calculation.

Applies geo and device-type multipliers from the ad slot's FloorPriceRule.
"""
from app.models.publisher import AdSlot


def calculate_floor_price(
    slot: AdSlot,
    country: str | None = None,
    device_type: str | None = None,
) -> float:
    rule = slot.floor_price
    floor = rule.base_cpm_usd

    if country and country in rule.geo_multipliers:
        floor *= rule.geo_multipliers[country]

    if device_type and device_type in rule.device_multipliers:
        floor *= rule.device_multipliers[device_type]

    return round(max(floor, 0.0), 4)


def device_type_from_openrtb(device_type_code: int | None) -> str | None:
    """Map OpenRTB device type code to floor-price multiplier key."""
    if device_type_code in (1, 4, 5):   # mobile/phone/tablet
        return "mobile"
    if device_type_code == 2:           # PC
        return "desktop"
    return None
