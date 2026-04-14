from __future__ import annotations

from pydantic import BaseModel, Field


class DispatchResourceBody(BaseModel):
    resource_id: str
    quantity: int = Field(ge=1)
    safe_zone_id: str
    safe_zone_name: str


class DeliverBody(BaseModel):
    allocation_id: str


class RestockBody(BaseModel):
    resource_id: str
    quantity: int = Field(ge=1)
    reason: str = ""
