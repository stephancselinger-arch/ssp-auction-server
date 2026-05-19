from __future__ import annotations
"""
PMP (Private Marketplace) deal matching.

Deals are evaluated before the open auction. A deal bid gets priority if it
clears the deal floor and the buyer seat is whitelisted.
"""
from app.models.publisher import Deal
from app.models.auction import BidCandidate
from app.services import publisher_service


def get_active_deals_for_slot(slot_id: str) -> list[Deal]:
    slot = publisher_service.get_ad_slot(slot_id)
    if not slot or not slot.deal_ids:
        return []
    deals = []
    for deal_id in slot.deal_ids:
        deal = publisher_service.get_deal(deal_id)
        if deal and deal.active:
            deals.append(deal)
    return deals


def is_deal_eligible(deal: Deal, candidate: BidCandidate) -> bool:
    if deal.wseat and candidate.dsp_seat not in deal.wseat:
        return False
    if candidate.price < deal.floor_cpm_usd:
        return False
    return True


def find_deal_winner(deals: list[Deal], candidates: list[BidCandidate]) -> BidCandidate | None:
    eligible: list[tuple[float, BidCandidate]] = []
    for candidate in candidates:
        if not candidate.deal_id:
            continue
        deal = next((d for d in deals if d.id == candidate.deal_id), None)
        if deal and is_deal_eligible(deal, candidate):
            eligible.append((candidate.price, candidate))
    if not eligible:
        return None
    eligible.sort(key=lambda x: x[0], reverse=True)
    return eligible[0][1]
