from __future__ import annotations

from pydantic import BaseModel, Field


class SpeedBody(BaseModel):
    seconds: float = Field(..., ge=0.1, le=10.0)
