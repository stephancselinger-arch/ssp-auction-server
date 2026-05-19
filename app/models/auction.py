"""
Auction result models and DSP endpoint registry.
"""
from typing import Optional
from enum import Enum
import uuid

from pydantic import BaseModel, Field


class DspEndpoint(BaseModel):
    id: str = Field(default_factory=lambda: f"dsp_{uuid.uuid4().hex[:8]}")
    name: str
    bid_endpoint_url: str
    timeout_ms: int = 150
    seat: str = ""
    active: bool = True


class DspEndpointCreate(BaseModel):
    name: str
    bid_endpoint_url: str
    timeout_ms: int = 150
    seat: str = ""


class BidCandidate(BaseModel):
    dsp_id: str
    dsp_seat: str
    bid_id: str
    imp_id: str
    price: float
    adm: Optional[str] = None
    adomain: list[str] = Field(default_factory=list)
    crid: Optional[str] = None
    deal_id: Optional[str] = None
    w: Optional[int] = None
    h: Optional[int] = None


class AuctionStatus(str, Enum):
    WON = "won"
    NO_BID = "no_bid"
    BELOW_FLOOR = "below_floor"
    NO_FILL = "no_fill"


class AuctionResult(BaseModel):
    auction_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    ad_slot_id: str
    status: AuctionStatus
    winner: Optional[BidCandidate] = None
    clearing_price: float = 0.0
    floor_price: float = 0.0
    bids_received: int = 0
    bids_eligible: int = 0
    auction_type: int = 2   # 1=first price, 2=second price


class AdRequest(BaseModel):
    """Incoming request from a publisher page or header bidding wrapper."""
    ad_slot_id: str
    user_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip: Optional[str] = None
    page_url: Optional[str] = None
    gdpr_consent: Optional[str] = None
    us_privacy: Optional[str] = None
    test: int = 0
