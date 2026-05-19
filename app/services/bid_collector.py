from __future__ import annotations
"""
DSP bid collector.

Fans out an OpenRTB bid request to all registered DSP endpoints in parallel,
with per-DSP timeout enforcement. Returns all valid BidCandidates.
"""
import uuid
import asyncio

import httpx

from app.models.auction import BidCandidate, DspEndpoint
from app.services import publisher_service


async def _call_dsp(
    client: httpx.AsyncClient,
    dsp: DspEndpoint,
    bid_request: dict,
) -> list[BidCandidate]:
    try:
        response = await client.post(
            dsp.bid_endpoint_url,
            json=bid_request,
            timeout=dsp.timeout_ms / 1000.0,
        )
        if response.status_code == 204:
            return []
        if response.status_code != 200:
            return []
        return _parse_response(dsp, response.json())
    except (httpx.TimeoutException, httpx.RequestError):
        return []


def _parse_response(dsp: DspEndpoint, data: dict) -> list[BidCandidate]:
    candidates = []
    for seatbid in data.get("seatbid", []):
        seat = seatbid.get("seat") or dsp.seat or dsp.id
        for bid in seatbid.get("bid", []):
            price = float(bid.get("price", 0))
            if price <= 0:
                continue
            candidates.append(BidCandidate(
                dsp_id=dsp.id,
                dsp_seat=seat,
                bid_id=bid.get("id", uuid.uuid4().hex),
                imp_id=bid.get("impid", ""),
                price=price,
                adm=bid.get("adm"),
                adomain=bid.get("adomain", []),
                crid=bid.get("crid"),
                deal_id=bid.get("dealid"),
                w=bid.get("w"),
                h=bid.get("h"),
            ))
    return candidates


async def collect_bids(bid_request: dict) -> list[BidCandidate]:
    dsps = publisher_service.list_dsps(active_only=True)
    if not dsps:
        return []
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[_call_dsp(client, dsp, bid_request) for dsp in dsps]
        )
    return [c for batch in results for c in batch]
