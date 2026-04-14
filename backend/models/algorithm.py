from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CompareAlgorithmsBody(BaseModel):
    start_node: str
    goal_node: str
    unit_type: Literal["ground", "helicopter"] = "ground"
    city: str | None = None


class GreedyBody(BaseModel):
    team_id: str
    strategy: Literal["nearest", "priority"] = "nearest"


class KnapsackBody(BaseModel):
    team_id: str | None = None
    city: str | None = None
