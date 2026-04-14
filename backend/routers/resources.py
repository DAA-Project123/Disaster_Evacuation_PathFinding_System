from __future__ import annotations

from fastapi import APIRouter, HTTPException

from core.resource_manager import ResourceManager
from models.resource import DeliverBody, DispatchResourceBody, RestockBody

router = APIRouter()
_rm = ResourceManager()


@router.get("")
def get_resources() -> dict:
    return _rm.load()


@router.post("/dispatch")
def dispatch_resource(body: DispatchResourceBody) -> dict:
    try:
        return _rm.distribute(body.resource_id, body.quantity, body.safe_zone_id, body.safe_zone_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/deliver")
def deliver(body: DeliverBody) -> dict:
    try:
        _rm.confirm_delivery(body.allocation_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/restock")
def restock(body: RestockBody) -> dict:
    try:
        _rm.restock(body.resource_id, body.quantity, body.reason)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
