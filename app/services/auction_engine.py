from __future__ import annotations
"""
Core SSP auction engine.

Supports first-price (AT=1) and second-price / Vickrey (AT=2) auctions.
PMP deals are evaluated before open auction. Floor price is always enforced.
"""
from app.models.auction import BidCandidate, AuctionResult, AuctionStatus
from app.services import deal_service


def run_auction(
    ad_slot_id: str,
    candidates: list[BidCandidate],
    floor_price: float,
    auction_type: int = 2,
) -> AuctionResult:
    base = AuctionResult(
        ad_slot_id=ad_slot_id,
        status=AuctionStatus.NO_BID,
        floor_price=floor_price,
        bids_received=len(candidates),
        auction_type=auction_type,
    )

    if not candidates:
        return base

    eligible = [c for c in candidates if c.price >= floor_price]
    base.bids_eligible = len(eligible)

    if not eligible:
        base.status = AuctionStatus.BELOW_FLOOR
        return base

    # PMP deals take priority
    deals = deal_service.get_active_deals_for_slot(ad_slot_id)
    if deals:
        deal_bids = [c for c in eligible if c.deal_id]
        deal_winner = deal_service.find_deal_winner(deals, deal_bids)
        if deal_winner:
            clearing = _clearing_price(deal_winner, eligible, floor_price, auction_type)
            return AuctionResult(
                ad_slot_id=ad_slot_id,
                status=AuctionStatus.WON,
                winner=deal_winner,
                clearing_price=clearing,
                floor_price=floor_price,
                bids_received=base.bids_received,
                bids_eligible=base.bids_eligible,
                auction_type=auction_type,
            )

    # Open auction
    ranked = sorted(eligible, key=lambda b: b.price, reverse=True)
    winner = ranked[0]
    clearing = _clearing_price(winner, eligible, floor_price, auction_type)

    return AuctionResult(
        ad_slot_id=ad_slot_id,
        status=AuctionStatus.WON,
        winner=winner,
        clearing_price=clearing,
        floor_price=floor_price,
        bids_received=base.bids_received,
        bids_eligible=base.bids_eligible,
        auction_type=auction_type,
    )


def _clearing_price(
    winner: BidCandidate,
    all_eligible: list[BidCandidate],
    floor_price: float,
    auction_type: int,
) -> float:
    if auction_type == 1:
        return round(winner.price, 4)
    # Second price: winner pays max(floor, highest competing bid)
    others = [c.price for c in all_eligible if c.bid_id != winner.bid_id]
    second = max(others) if others else 0.0
    return round(max(floor_price, second), 4)
