from __future__ import annotations

from fastapi import APIRouter, HTTPException

from core.data_loader import CITY_MAP, load_city_graph, load_disaster_events
from models.city import CitySwitchBody
from simulation.state import sim_state

router = APIRouter()


@router.get("")
def list_cities() -> list[dict]:
    out = []
    for name in CITY_MAP:
        try:
            cg = load_city_graph(name)
            ev = load_disaster_events(name)
            active_disasters = sum(1 for e in ev if e.get("active"))
            out.append(
                {
                    "name": name,
                    "slug": CITY_MAP[name],
                    "node_count": len(cg.get("nodes", [])),
                    "edge_count": len(cg.get("edges", [])),
                    "active_disasters": active_disasters,
                    "description": cg.get("description", ""),
                }
            )
        except OSError:
            continue
    return out


@router.get("/{city_name}/graph")
def get_city_graph(city_name: str) -> dict:
    try:
        return load_city_graph(city_name)
    except OSError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/switch")
def switch_city(body: CitySwitchBody) -> dict:
    if body.city not in CITY_MAP:
        raise HTTPException(status_code=400, detail="Unknown city")
    sim_state.load_city(body.city)
    return {"ok": True, "active_city": sim_state.active_city}
