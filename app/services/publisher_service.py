from __future__ import annotations
"""
In-memory registry for publishers, sites, ad slots, deals, and DSP endpoints.
"""
from app.models.publisher import (
    Publisher, PublisherCreate,
    Site, SiteCreate,
    AdSlot, AdSlotCreate,
    Deal, DealCreate,
)
from app.models.auction import DspEndpoint, DspEndpointCreate

_publishers: dict[str, Publisher] = {}
_sites: dict[str, Site] = {}
_ad_slots: dict[str, AdSlot] = {}
_deals: dict[str, Deal] = {}
_dsp_endpoints: dict[str, DspEndpoint] = {}


# ── Publishers ────────────────────────────────────────────────────────────────

def create_publisher(data: PublisherCreate) -> Publisher:
    pub = Publisher(**data.model_dump())
    _publishers[pub.id] = pub
    return pub


def get_publisher(pub_id: str) -> Publisher | None:
    return _publishers.get(pub_id)


def list_publishers() -> list[Publisher]:
    return list(_publishers.values())


def delete_publisher(pub_id: str) -> bool:
    return _publishers.pop(pub_id, None) is not None


# ── Sites ─────────────────────────────────────────────────────────────────────

def create_site(data: SiteCreate) -> Site:
    site = Site(**data.model_dump())
    _sites[site.id] = site
    return site


def get_site(site_id: str) -> Site | None:
    return _sites.get(site_id)


def list_sites(publisher_id: str | None = None) -> list[Site]:
    sites = list(_sites.values())
    if publisher_id:
        sites = [s for s in sites if s.publisher_id == publisher_id]
    return sites


def delete_site(site_id: str) -> bool:
    return _sites.pop(site_id, None) is not None


# ── Ad Slots ──────────────────────────────────────────────────────────────────

def create_ad_slot(data: AdSlotCreate) -> AdSlot:
    slot = AdSlot(**data.model_dump())
    _ad_slots[slot.id] = slot
    return slot


def get_ad_slot(slot_id: str) -> AdSlot | None:
    return _ad_slots.get(slot_id)


def list_ad_slots(site_id: str | None = None) -> list[AdSlot]:
    slots = list(_ad_slots.values())
    if site_id:
        slots = [s for s in slots if s.site_id == site_id]
    return slots


def delete_ad_slot(slot_id: str) -> bool:
    return _ad_slots.pop(slot_id, None) is not None


# ── Deals ─────────────────────────────────────────────────────────────────────

def create_deal(data: DealCreate) -> Deal:
    deal = Deal(**data.model_dump())
    _deals[deal.id] = deal
    return deal


def get_deal(deal_id: str) -> Deal | None:
    return _deals.get(deal_id)


def list_deals(publisher_id: str | None = None) -> list[Deal]:
    deals = list(_deals.values())
    if publisher_id:
        deals = [d for d in deals if d.publisher_id == publisher_id]
    return deals


def delete_deal(deal_id: str) -> bool:
    return _deals.pop(deal_id, None) is not None


# ── DSP Endpoints ─────────────────────────────────────────────────────────────

def register_dsp(data: DspEndpointCreate) -> DspEndpoint:
    dsp = DspEndpoint(**data.model_dump())
    _dsp_endpoints[dsp.id] = dsp
    return dsp


def get_dsp(dsp_id: str) -> DspEndpoint | None:
    return _dsp_endpoints.get(dsp_id)


def list_dsps(active_only: bool = True) -> list[DspEndpoint]:
    dsps = list(_dsp_endpoints.values())
    if active_only:
        dsps = [d for d in dsps if d.active]
    return dsps


def deregister_dsp(dsp_id: str) -> bool:
    return _dsp_endpoints.pop(dsp_id, None) is not None
