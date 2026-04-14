from __future__ import annotations

from pydantic import BaseModel, Field


class TriggerDisasterBody(BaseModel):
    type: str
    severity: str
    epicenter_node: str
    radius: int = Field(ge=1, le=10)
    city: str | None = None


class BlockRoadBody(BaseModel):
    u: str
    v: str


class UnblockRoadBody(BaseModel):
    u: str
    v: str
