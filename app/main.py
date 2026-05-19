from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import publishers, inventory, auctions, deals, reports

app = FastAPI(
    title="SSP Auction Server",
    description=(
        "OpenRTB 2.6 compliant Supply-Side Platform. "
        "Publisher and inventory management, header bidding support, "
        "first/second-price auctions, PMP deals, and DSP bid fan-out."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(publishers.router, prefix="/v1")
app.include_router(inventory.router, prefix="/v1")
app.include_router(auctions.router, prefix="/v1")
app.include_router(deals.router, prefix="/v1")
app.include_router(reports.router, prefix="/v1")


@app.get("/health")
def health():
    return {"status": "ok", "openrtb_version": "2.6", "service": "ssp-auction-server"}
