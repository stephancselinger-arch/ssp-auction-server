from __future__ import annotations
"""
Build OpenRTB 2.6 bid requests from SSP ad slot context.
"""
import uuid
from typing import Optional

from app.models.publisher import AdSlot, Site, Publisher, AdFormat, Deal
from app.models.auction import AdRequest


def build_bid_request(
    slot: AdSlot,
    site: Site,
    publisher: Publisher,
    ad_request: AdRequest,
    deals: list[Deal] | None = None,
) -> dict:
    return {
        "id": uuid.uuid4().hex,
        "imp": [_build_impression(slot, deals)],
        "site": _build_site(site, publisher, ad_request),
        "device": _build_device(ad_request),
        "user": _build_user(ad_request),
        "at": 2,
        "tmax": 150,
        "cur": ["USD"],
        "test": ad_request.test,
        **_build_regs(ad_request),
    }


def _build_impression(slot: AdSlot, deals: list[Deal] | None) -> dict:
    imp: dict = {
        "id": slot.id,
        "bidfloor": slot.floor_price.base_cpm_usd,
        "bidfloorcur": "USD",
        "secure": slot.secure,
        "tagid": slot.id,
    }

    if slot.ad_format == AdFormat.BANNER:
        imp["banner"] = {
            "format": [{"w": s.w, "h": s.h} for s in slot.sizes],
            "pos": slot.position,
        }
        if slot.sizes:
            imp["banner"]["w"] = slot.sizes[0].w
            imp["banner"]["h"] = slot.sizes[0].h
    elif slot.ad_format == AdFormat.VIDEO:
        imp["video"] = {
            "mimes": ["video/mp4"],
            "protocols": [2, 3, 5, 6],   # VAST 2.0/3.0 and wrapped
            "minduration": 5,
            "maxduration": 30,
        }
    elif slot.ad_format == AdFormat.NATIVE:
        imp["native"] = {"request": '{"ver":"1.2","layout":1}', "ver": "1.2"}

    if deals:
        imp["pmp"] = {
            "private_auction": 0,
            "deals": [
                {
                    "id": d.id,
                    "bidfloor": d.floor_cpm_usd,
                    "bidfloorcur": "USD",
                    "at": d.at.value,
                    "wseat": d.wseat,
                    "wadomain": d.wadomain,
                }
                for d in deals
            ],
        }

    return imp


def _build_site(site: Site, publisher: Publisher, ad_request: AdRequest) -> dict:
    return {
        "id": site.id,
        "name": site.name,
        "domain": site.domain,
        "page": ad_request.page_url or site.page_url,
        "cat": site.cat,
        "keywords": site.keywords,
        "publisher": {
            "id": publisher.id,
            "name": publisher.name,
            "domain": publisher.domain,
        },
    }


def _build_device(ad_request: AdRequest) -> dict:
    device: dict = {}
    if ad_request.user_agent:
        device["ua"] = ad_request.user_agent
    if ad_request.ip:
        device["ip"] = ad_request.ip
    return device


def _build_user(ad_request: AdRequest) -> dict:
    user: dict = {}
    if ad_request.user_id:
        user["id"] = ad_request.user_id
    return user


def _build_regs(ad_request: AdRequest) -> dict:
    if not ad_request.gdpr_consent and not ad_request.us_privacy:
        return {}
    return {
        "regs": {
            "gdpr": 1 if ad_request.gdpr_consent else 0,
            "us_privacy": ad_request.us_privacy,
            "ext": {"consent": ad_request.gdpr_consent} if ad_request.gdpr_consent else {},
        }
    }
