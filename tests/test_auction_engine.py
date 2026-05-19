from __future__ import annotations
"""
Tests for the SSP auction engine.
"""
import pytest

from app.models.auction import BidCandidate, AuctionStatus
from app.services.auction_engine import run_auction


def make_bid(bid_id: str, price: float, deal_id: str | None = None) -> BidCandidate:
    return BidCandidate(
        dsp_id="dsp_test",
        dsp_seat="seat_test",
        bid_id=bid_id,
        imp_id="imp_1",
        price=price,
        deal_id=deal_id,
    )


# ── Second-price auction ──────────────────────────────────────────────────────

def test_second_price_winner_pays_second_price():
    candidates = [make_bid("b1", 5.0), make_bid("b2", 3.0), make_bid("b3", 1.0)]
    result = run_auction("slot_x", candidates, floor_price=0.50, auction_type=2)
    assert result.status == AuctionStatus.WON
    assert result.winner.bid_id == "b1"
    assert result.clearing_price == 3.0


def test_second_price_single_bid_pays_floor():
    candidates = [make_bid("b1", 5.0)]
    result = run_auction("slot_x", candidates, floor_price=1.0, auction_type=2)
    assert result.status == AuctionStatus.WON
    assert result.clearing_price == 1.0


def test_second_price_floor_beats_second_bid():
    # b2 is below floor so only b1 is eligible — clears at floor
    candidates = [make_bid("b1", 5.0), make_bid("b2", 0.10)]
    result = run_auction("slot_x", candidates, floor_price=0.50, auction_type=2)
    assert result.status == AuctionStatus.WON
    assert result.clearing_price == 0.50


# ── First-price auction ───────────────────────────────────────────────────────

def test_first_price_winner_pays_own_bid():
    candidates = [make_bid("b1", 5.0), make_bid("b2", 3.0)]
    result = run_auction("slot_x", candidates, floor_price=0.50, auction_type=1)
    assert result.status == AuctionStatus.WON
    assert result.winner.bid_id == "b1"
    assert result.clearing_price == 5.0


# ── Floor price enforcement ───────────────────────────────────────────────────

def test_all_bids_below_floor():
    candidates = [make_bid("b1", 0.10), make_bid("b2", 0.20)]
    result = run_auction("slot_x", candidates, floor_price=1.00, auction_type=2)
    assert result.status == AuctionStatus.BELOW_FLOOR
    assert result.winner is None


def test_no_bids_returns_no_bid():
    result = run_auction("slot_x", [], floor_price=0.50, auction_type=2)
    assert result.status == AuctionStatus.NO_BID
    assert result.winner is None


# ── Bid count tracking ────────────────────────────────────────────────────────

def test_bid_count_tracking():
    candidates = [make_bid("b1", 5.0), make_bid("b2", 0.10)]
    result = run_auction("slot_x", candidates, floor_price=1.00, auction_type=2)
    assert result.bids_received == 2
    assert result.bids_eligible == 1


def test_highest_bidder_wins():
    candidates = [make_bid("b1", 2.0), make_bid("b2", 8.5), make_bid("b3", 4.0)]
    result = run_auction("slot_x", candidates, floor_price=0.50, auction_type=2)
    assert result.winner.bid_id == "b2"
    assert result.clearing_price == 4.0
