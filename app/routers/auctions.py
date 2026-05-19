"""
Auction endpoints.

POST /v1/auction            — standard auction (ad tags / server-side)
POST /v1/auction/header-bid — header bidding (Prebid.js compatible)
"""
from fastapi import APIRouter, HTTPException

from app.models.auction import AdRequest, AuctionResult
from app.services import publisher_service, bid_collector, auction_engine
from app.services.floor_price import calculate_floor_price
from app.services import deal_service
from app.utils.openrtb_builder import build_bid_request

router = APIRouter(prefix="/auction", tags=["Auctions"])


async def _execute_auction(ad_request: AdRequest) -> AuctionResult:
    slot = publisher_service.get_ad_slot(ad_request.ad_slot_id)
    if not slot or not slot.active:
        raise HTTPException(status_code=404, detail="Ad slot not found or inactive")

    site = publisher_service.get_site(slot.site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    publisher = publisher_service.get_publisher(site.publisher_id)
    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")

    deals = deal_service.get_active_deals_for_slot(slot.id)
    floor = calculate_floor_price(slot)
    bid_request_dict = build_bid_request(slot, site, publisher, ad_request, deals)
    candidates = await bid_collector.collect_bids(bid_request_dict)

    return auction_engine.run_auction(
        ad_slot_id=slot.id,
        candidates=candidates,
        floor_price=floor,
        auction_type=2,
    )


@router.post("", response_model=AuctionResult)
async def run_auction(ad_request: AdRequest):
    return await _execute_auction(ad_request)


@router.post("/header-bid", response_model=AuctionResult)
async def header_bid(ad_request: AdRequest):
    """Prebid.js-compatible header bidding endpoint."""
    return await _execute_auction(ad_request)
