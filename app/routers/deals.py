from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.publisher import Deal, DealCreate
from app.models.auction import DspEndpoint, DspEndpointCreate
from app.services import publisher_service

router = APIRouter(tags=["Deals & DSPs"])


# ── PMP Deals ─────────────────────────────────────────────────────────────────

@router.post("/deals", response_model=Deal, status_code=201)
def create_deal(data: DealCreate):
    if not publisher_service.get_publisher(data.publisher_id):
        raise HTTPException(status_code=404, detail="Publisher not found")
    return publisher_service.create_deal(data)


@router.get("/deals", response_model=list[Deal])
def list_deals(publisher_id: Optional[str] = None):
    return publisher_service.list_deals(publisher_id)


@router.get("/deals/{deal_id}", response_model=Deal)
def get_deal(deal_id: str):
    deal = publisher_service.get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.delete("/deals/{deal_id}", status_code=204)
def delete_deal(deal_id: str):
    if not publisher_service.delete_deal(deal_id):
        raise HTTPException(status_code=404, detail="Deal not found")


# ── DSP Endpoints ─────────────────────────────────────────────────────────────

@router.post("/dsps", response_model=DspEndpoint, status_code=201)
def register_dsp(data: DspEndpointCreate):
    return publisher_service.register_dsp(data)


@router.get("/dsps", response_model=list[DspEndpoint])
def list_dsps():
    return publisher_service.list_dsps(active_only=False)


@router.get("/dsps/{dsp_id}", response_model=DspEndpoint)
def get_dsp(dsp_id: str):
    dsp = publisher_service.get_dsp(dsp_id)
    if not dsp:
        raise HTTPException(status_code=404, detail="DSP not found")
    return dsp


@router.delete("/dsps/{dsp_id}", status_code=204)
def deregister_dsp(dsp_id: str):
    if not publisher_service.deregister_dsp(dsp_id):
        raise HTTPException(status_code=404, detail="DSP not found")
