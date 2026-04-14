from __future__ import annotations

from pydantic import BaseModel, Field


class DispatchMissionBody(BaseModel):
    team_id: str
    target_node: str
    algorithm: str = Field(default="recommended")
    city: str | None = None


class ConfirmRescueBody(BaseModel):
    people_rescued: int = Field(ge=0)
