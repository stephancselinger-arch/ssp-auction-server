"""
Publisher reporting: inventory summary and slot details.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import publisher_service

router = APIRouter(prefix="/reports", tags=["Reports"])


class SlotReport(BaseModel):
    slot_id: str
    slot_name: str
    site_id: str
    ad_format: str
    floor_cpm_usd: float
    active: bool


class PublisherSummary(BaseModel):
    publisher_id: str
    publisher_name: str
    domain: str
    revenue_share: float
    site_count: int
    slot_count: int
    deal_count: int


@router.get("/publishers/{publisher_id}/summary", response_model=PublisherSummary)
def publisher_summary(publisher_id: str):
    pub = publisher_service.get_publisher(publisher_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publisher not found")
    sites = publisher_service.list_sites(publisher_id)
    slot_count = sum(len(publisher_service.list_ad_slots(s.id)) for s in sites)
    deal_count = len(publisher_service.list_deals(publisher_id))
    return PublisherSummary(
        publisher_id=pub.id,
        publisher_name=pub.name,
        domain=pub.domain,
        revenue_share=pub.revenue_share,
        site_count=len(sites),
        slot_count=slot_count,
        deal_count=deal_count,
    )


@router.get("/publishers/{publisher_id}/slots", response_model=list[SlotReport])
def publisher_slots(publisher_id: str):
    pub = publisher_service.get_publisher(publisher_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publisher not found")
    sites = publisher_service.list_sites(publisher_id)
    reports = []
    for site in sites:
        for slot in publisher_service.list_ad_slots(site.id):
            reports.append(SlotReport(
                slot_id=slot.id,
                slot_name=slot.name,
                site_id=site.id,
                ad_format=slot.ad_format.value,
                floor_cpm_usd=slot.floor_price.base_cpm_usd,
                active=slot.active,
            ))
    return reports
