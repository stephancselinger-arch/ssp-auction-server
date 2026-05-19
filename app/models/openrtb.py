"""
OpenRTB 2.6 bid request / response models (SSP perspective).
The SSP generates BidRequests and receives BidResponses from DSPs.
Spec: https://www.iab.com/wp-content/uploads/2022/04/OpenRTB-2-6_FINAL.pdf
"""

from typing import Optional
from pydantic import BaseModel


class Banner(BaseModel):
    w: Optional[int] = None
    h: Optional[int] = None
    format: Optional[list[dict]] = None
    pos: Optional[int] = None
    api: Optional[list[int]] = None


class Video(BaseModel):
    mimes: list[str] = ["video/mp4"]
    minduration: Optional[int] = None
    maxduration: Optional[int] = None
    protocols: Optional[list[int]] = None
    w: Optional[int] = None
    h: Optional[int] = None
    linearity: Optional[int] = None
    skip: Optional[int] = None
    placement: Optional[int] = None


class Native(BaseModel):
    request: str
    ver: Optional[str] = "1.2"


class Deal(BaseModel):
    id: str
    bidfloor: float = 0.0
    bidfloorcur: str = "USD"
    at: Optional[int] = None
    wseat: Optional[list[str]] = None
    wadomain: Optional[list[str]] = None


class Pmp(BaseModel):
    private_auction: int = 0
    deals: list[Deal] = []


class Impression(BaseModel):
    id: str
    banner: Optional[Banner] = None
    video: Optional[Video] = None
    native: Optional[Native] = None
    tagid: Optional[str] = None
    bidfloor: float = 0.0
    bidfloorcur: str = "USD"
    secure: Optional[int] = None
    pmp: Optional[Pmp] = None


class Publisher(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    domain: Optional[str] = None


class Site(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    domain: Optional[str] = None
    cat: Optional[list[str]] = None
    page: Optional[str] = None
    publisher: Optional[Publisher] = None
    keywords: Optional[str] = None


class Geo(BaseModel):
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class Device(BaseModel):
    ua: Optional[str] = None
    ip: Optional[str] = None
    geo: Optional[Geo] = None
    devicetype: Optional[int] = None
    os: Optional[str] = None
    language: Optional[str] = None


class User(BaseModel):
    id: Optional[str] = None
    keywords: Optional[str] = None


class Regs(BaseModel):
    coppa: Optional[int] = None
    gdpr: Optional[int] = None
    us_privacy: Optional[str] = None
    ext: Optional[dict] = None


class BidRequest(BaseModel):
    id: str
    imp: list[Impression]
    site: Optional[Site] = None
    device: Optional[Device] = None
    user: Optional[User] = None
    regs: Optional[Regs] = None
    at: int = 2
    tmax: Optional[int] = 150
    cur: list[str] = ["USD"]
    test: int = 0


# ── Bid Response (received from DSPs) ─────────────────────────────────────────

class Bid(BaseModel):
    id: str
    impid: str
    price: float
    adm: Optional[str] = None
    adomain: Optional[list[str]] = None
    crid: Optional[str] = None
    dealid: Optional[str] = None
    w: Optional[int] = None
    h: Optional[int] = None
    nurl: Optional[str] = None
    lurl: Optional[str] = None


class SeatBid(BaseModel):
    bid: list[Bid]
    seat: Optional[str] = None


class BidResponse(BaseModel):
    id: str
    seatbid: list[SeatBid] = []
    cur: str = "USD"
    nbr: Optional[int] = None
