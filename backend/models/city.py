from __future__ import annotations

from pydantic import BaseModel, Field


class CitySwitchBody(BaseModel):
    city: str = Field(..., description="City display name, e.g. Veridian City")
