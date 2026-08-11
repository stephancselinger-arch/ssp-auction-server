# SSP Auction Server

OpenRTB 2.6 compliant Supply-Side Platform (SSP) with header bidding support. Manages publisher inventory, fans bid requests out to registered DSPs in parallel, runs first/second-price auctions, enforces floor prices, and supports Private Marketplace (PMP) deals.

## Features

- **OpenRTB 2.6 Compliance** — generates standard BidRequests, parses BidResponses from DSPs
- **Header Bidding** — Prebid.js-compatible `/v1/auction/header-bid` endpoint
- **Auction Engine** — first-price and second-price (Vickrey) auctions with floor price enforcement
- **PMP Deals** — Private Marketplace deal matching with buyer seat and floor price controls
- **Dynamic Floor Prices** — per-slot base CPM with geo and device-type multipliers
- **DSP Fan-out** — async parallel bid collection with per-DSP timeout (default 150ms)
- **Publisher Management** — Publisher → Site → AdSlot hierarchy with CRUD
- **Multi-format** — banner (IAB sizes), VAST video, native ad slots

## Architecture

```
Publisher Page / Header Bidding Wrapper
    │  POST /v1/auction/header-bid  (AdRequest)
    ▼
SSP Auction Server
    ├── AdSlot lookup → floor price + deals
    ├── Build OpenRTB BidRequest
    ├── Fan-out to DSPs (async, parallel, 150ms timeout)
    │       ├── DSP 1 → BidResponse
    │       ├── DSP 2 → BidResponse
    │       └── DSP N → BidResponse
    ├── Parse + validate BidCandidates
    └── Auction Engine
            ├── PMP deal check (priority)
            └── Open auction (2nd price / Vickrey)
    │
    ▼  AuctionResult { winner, clearing_price, ... }
```

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8004 --reload
```

API docs: http://localhost:8004/docs

## Docker

```bash
docker compose up
```

## API Reference

### Auctions

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/auction` | Standard auction (server-side / ad tag) |
| `POST` | `/v1/auction/header-bid` | Header bidding endpoint (Prebid.js compatible) |

### Publisher Inventory

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/publishers` | Register a publisher |
| `GET` | `/v1/publishers` | List publishers |
| `POST` | `/v1/sites` | Create a site |
| `GET` | `/v1/sites` | List sites (filter by publisher_id) |
| `POST` | `/v1/slots` | Create an ad slot |
| `GET` | `/v1/slots` | List ad slots (filter by site_id) |

### Deals & DSPs

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/deals` | Create a PMP deal |
| `GET` | `/v1/deals` | List deals |
| `POST` | `/v1/dsps` | Register a DSP endpoint |
| `GET` | `/v1/dsps` | List DSP endpoints |

### Reports

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/reports/publishers/{id}/summary` | Publisher summary (sites, slots, deals) |
| `GET` | `/v1/reports/publishers/{id}/slots` | Slot detail report with floor prices |

## Example: End-to-End Auction

```bash
# 1. Register a publisher
curl -X POST http://localhost:8004/v1/publishers \
  -H 'Content-Type: application/json' \
  -d '{"name": "Acme Media", "domain": "acmemedia.com", "revenue_share": 0.70}'

# 2. Create a site
curl -X POST http://localhost:8004/v1/sites \
  -H 'Content-Type: application/json' \
  -d '{"publisher_id": "pub_xxx", "name": "Acme Homepage", "domain": "acmemedia.com", "cat": ["IAB1"]}'

# 3. Create an ad slot
curl -X POST http://localhost:8004/v1/slots \
  -H 'Content-Type: application/json' \
  -d '{
    "site_id": "site_xxx",
    "name": "Leaderboard",
    "ad_format": "banner",
    "sizes": [{"w": 728, "h": 90}],
    "floor_price": {
      "base_cpm_usd": 1.50,
      "geo_multipliers": {"USA": 2.0},
      "device_multipliers": {"mobile": 0.75}
    }
  }'

# 4. Register a DSP
curl -X POST http://localhost:8004/v1/dsps \
  -H 'Content-Type: application/json' \
  -d '{"name": "My DSP", "bid_endpoint_url": "http://dsp:8002/v1/bid/request", "timeout_ms": 150}'

# 5. Run an auction
curl -X POST http://localhost:8004/v1/auction \
  -H 'Content-Type: application/json' \
  -d '{
    "ad_slot_id": "slot_xxx",
    "user_id": "usr_abc123",
    "user_agent": "Mozilla/5.0...",
    "ip": "12.34.56.78",
    "page_url": "https://acmemedia.com/"
  }'
```

Auction response:
```json
{
  "auction_id": "a1b2c3d4...",
  "ad_slot_id": "slot_xxx",
  "status": "won",
  "winner": {
    "dsp_id": "dsp_abc1",
    "dsp_seat": "seat_dsp01",
    "bid_id": "bid_xyz",
    "imp_id": "slot_xxx",
    "price": 4.50,
    "adm": "<div>...</div>",
    "crid": "cr_123"
  },
  "clearing_price": 3.20,
  "floor_price": 1.50,
  "bids_received": 3,
  "bids_eligible": 3,
  "auction_type": 2
}
```

## Example: PMP Deal

```bash
# Create a deal
curl -X POST http://localhost:8004/v1/deals \
  -H 'Content-Type: application/json' \
  -d '{
    "publisher_id": "pub_xxx",
    "buyer_seat": "seat_premium_dsp",
    "name": "Premium Deal Q2",
    "at": 1,
    "floor_cpm_usd": 5.00,
    "wseat": ["seat_premium_dsp"]
  }'

# Attach deal to slot by updating the slot's deal_ids list
```

Deal bids (those with `dealid` in their OpenRTB response) are evaluated first
and win if they clear the deal floor, even if a higher open-auction bid exists.

## Floor Price Mechanics

```
effective_floor = base_cpm_usd
                × geo_multipliers[country]   (if present)
                × device_multipliers[type]   (if present)
```

Example: `base=1.00`, `geo["USA"]=2.0`, `device["mobile"]=0.75`
→ US mobile floor = `1.00 × 2.0 × 0.75 = $1.50 CPM`

## Running Tests

```bash
pytest tests/ -v
```

## Production Considerations

| Component | Dev (current) | Production |
|-----------|--------------|------------|
| Publisher/slot store | In-memory dict | PostgreSQL |
| DSP bid fan-out | httpx async | httpx + circuit breaker |
| Floor price rules | Static config | ML-driven dynamic floors |
| Bid timeout | 150ms fixed | Adaptive per-DSP p95 latency |
| Deal store | In-memory | PostgreSQL + Redis cache |

## Tech Stack

- **FastAPI** — async REST, concurrent auction handling
- **Pydantic v2** — OpenRTB model validation
- **httpx** — async DSP bid fan-out with timeout
- Python 3.12+

<!-- Last updated: 2026-05-21 -->

<!-- Last updated: 2026-05-23 -->

<!-- Last updated: 2026-05-25 -->

<!-- Last updated: 2026-05-27 -->

<!-- Last updated: 2026-05-29 -->

<!-- Last updated: 2026-05-31 -->

<!-- Last updated: 2026-06-01 -->

<!-- Last updated: 2026-06-03 -->

<!-- Last updated: 2026-06-05 -->

<!-- Last updated: 2026-06-07 -->

<!-- Last updated: 2026-06-09 -->

<!-- Last updated: 2026-06-11 -->

<!-- Last updated: 2026-06-13 -->

<!-- Last updated: 2026-06-15 -->

<!-- Last updated: 2026-06-17 -->

<!-- Last updated: 2026-06-19 -->

<!-- Last updated: 2026-06-21 -->

<!-- Last updated: 2026-06-23 -->

<!-- Last updated: 2026-06-25 -->

<!-- Last updated: 2026-06-27 -->

<!-- Last updated: 2026-06-29 -->

<!-- Last updated: 2026-07-01 -->

<!-- Last updated: 2026-07-03 -->

<!-- Last updated: 2026-07-05 -->

<!-- Last updated: 2026-07-07 -->

<!-- Last updated: 2026-07-09 -->

<!-- Last updated: 2026-07-11 -->

<!-- Last updated: 2026-07-13 -->

<!-- Last updated: 2026-07-15 -->

<!-- Last updated: 2026-07-17 -->

<!-- Last updated: 2026-07-19 -->

<!-- Last updated: 2026-07-21 -->

<!-- Last updated: 2026-07-23 -->

<!-- Last updated: 2026-07-25 -->

<!-- Last updated: 2026-07-27 -->

<!-- Last updated: 2026-07-29 -->

<!-- Last updated: 2026-07-31 -->

<!-- Last updated: 2026-08-01 -->

<!-- Last updated: 2026-08-03 -->

<!-- Last updated: 2026-08-05 -->

<!-- Last updated: 2026-08-07 -->

<!-- Last updated: 2026-08-09 -->

<!-- Last updated: 2026-08-11 -->
