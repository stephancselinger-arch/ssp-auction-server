from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.publisher import Site, SiteCreate, AdSlot, AdSlotCreate
from app.services import publisher_service

router = APIRouter(tags=["Inventory"])


# ── Sites ─────────────────────────────────────────────────────────────────────

@router.post("/sites", response_model=Site, status_code=201)
def create_site(data: SiteCreate):
    if not publisher_service.get_publisher(data.publisher_id):
        raise HTTPException(status_code=404, detail="Publisher not found")
    return publisher_service.create_site(data)


@router.get("/sites", response_model=list[Site])
def list_sites(publisher_id: Optional[str] = None):
    return publisher_service.list_sites(publisher_id)


@router.get("/sites/{site_id}", response_model=Site)
def get_site(site_id: str):
    site = publisher_service.get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.delete("/sites/{site_id}", status_code=204)
def delete_site(site_id: str):
    if not publisher_service.delete_site(site_id):
        raise HTTPException(status_code=404, detail="Site not found")


# ── Ad Slots ──────────────────────────────────────────────────────────────────

@router.post("/slots", response_model=AdSlot, status_code=201)
def create_ad_slot(data: AdSlotCreate):
    if not publisher_service.get_site(data.site_id):
        raise HTTPException(status_code=404, detail="Site not found")
    return publisher_service.create_ad_slot(data)


@router.get("/slots", response_model=list[AdSlot])
def list_ad_slots(site_id: Optional[str] = None):
    return publisher_service.list_ad_slots(site_id)


@router.get("/slots/{slot_id}", response_model=AdSlot)
def get_ad_slot(slot_id: str):
    slot = publisher_service.get_ad_slot(slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Ad slot not found")
    return slot


@router.delete("/slots/{slot_id}", status_code=204)
def delete_ad_slot(slot_id: str):
    if not publisher_service.delete_ad_slot(slot_id):
        raise HTTPException(status_code=404, detail="Ad slot not found")
