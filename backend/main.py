from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import algorithms, cities, disasters, missions, resources, simulation
from simulation.state import bootstrap_state

app = FastAPI(title="DAA Disaster System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cities.router, prefix="/api/cities", tags=["cities"])
app.include_router(disasters.router, prefix="/api/disasters", tags=["disasters"])
app.include_router(missions.router, prefix="/api/missions", tags=["missions"])
app.include_router(resources.router, prefix="/api/resources", tags=["resources"])
app.include_router(algorithms.router, prefix="/api/algorithms", tags=["algorithms"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])


@app.on_event("startup")
def _startup() -> None:
    bootstrap_state()
