from fastapi import APIRouter, HTTPException

from app.models.publisher import Publisher, PublisherCreate
from app.services import publisher_service

router = APIRouter(prefix="/publishers", tags=["Publishers"])


@router.post("", response_model=Publisher, status_code=201)
def create_publisher(data: PublisherCreate):
    return publisher_service.create_publisher(data)


@router.get("", response_model=list[Publisher])
def list_publishers():
    return publisher_service.list_publishers()


@router.get("/{publisher_id}", response_model=Publisher)
def get_publisher(publisher_id: str):
    pub = publisher_service.get_publisher(publisher_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return pub


@router.delete("/{publisher_id}", status_code=204)
def delete_publisher(publisher_id: str):
    if not publisher_service.delete_publisher(publisher_id):
        raise HTTPException(status_code=404, detail="Publisher not found")
