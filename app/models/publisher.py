"""
Publisher inventory models: Publisher, Site, AdSlot, Deal.
"""
from typing import Optional
from enum import Enum
import uuid

from pydantic import BaseModel, Field


class AuctionType(int, Enum):
    FIRST_PRICE = 1
    SECOND_PRICE = 2


class AdFormat(str, Enum):
    BANNER = "banner"
    VIDEO = "video"
    NATIVE = "native"


class AdSlotSize(BaseModel):
    w: int
    h: int


class FloorPriceRule(BaseModel):
    base_cpm_usd: float = 0.50
    geo_multipliers: dict[str, float] = Field(default_factory=dict)   # country -> multiplier
    device_multipliers: dict[str, float] = Field(default_factory=dict)  # mobile/desktop -> multiplier


class Publisher(BaseModel):
    id: str = Field(default_factory=lambda: f"pub_{uuid.uuid4().hex[:10]}")
    name: str
    domain: str
    revenue_share: float = 0.70  # publisher keeps this fraction
    active: bool = True


class PublisherCreate(BaseModel):
    name: str
    domain: str
    revenue_share: float = 0.70


class Site(BaseModel):
    id: str = Field(default_factory=lambda: f"site_{uuid.uuid4().hex[:10]}")
    publisher_id: str
    name: str
    domain: str
    page_url: Optional[str] = None
    cat: list[str] = Field(default_factory=list)
    keywords: Optional[str] = None
    active: bool = True


class SiteCreate(BaseModel):
    publisher_id: str
    name: str
    domain: str
    page_url: Optional[str] = None
    cat: list[str] = Field(default_factory=list)
    keywords: Optional[str] = None


class AdSlot(BaseModel):
    id: str = Field(default_factory=lambda: f"slot_{uuid.uuid4().hex[:10]}")
    site_id: str
    name: str
    ad_format: AdFormat = AdFormat.BANNER
    sizes: list[AdSlotSize] = Field(default_factory=list)
    floor_price: FloorPriceRule = Field(default_factory=FloorPriceRule)
    deal_ids: list[str] = Field(default_factory=list)
    position: int = 0   # 0=unknown, 1=above fold, 3=below fold
    secure: int = 1
    active: bool = True


class AdSlotCreate(BaseModel):
    site_id: str
    name: str
    ad_format: AdFormat = AdFormat.BANNER
    sizes: list[AdSlotSize] = Field(default_factory=list)
    floor_price: FloorPriceRule = Field(default_factory=FloorPriceRule)
    deal_ids: list[str] = Field(default_factory=list)
    position: int = 0
    secure: int = 1


class Deal(BaseModel):
    id: str = Field(default_factory=lambda: f"deal_{uuid.uuid4().hex[:10]}")
    publisher_id: str
    buyer_seat: str
    name: str
    at: AuctionType = AuctionType.FIRST_PRICE
    floor_cpm_usd: float = 0.0
    wseat: list[str] = Field(default_factory=list)
    wadomain: list[str] = Field(default_factory=list)
    active: bool = True


class DealCreate(BaseModel):
    publisher_id: str
    buyer_seat: str
    name: str
    at: AuctionType = AuctionType.FIRST_PRICE
    floor_cpm_usd: float = 0.0
    wseat: list[str] = Field(default_factory=list)
    wadomain: list[str] = Field(default_factory=list)
