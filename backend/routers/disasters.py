from __future__ import annotations

import copy

from fastapi import APIRouter, HTTPException

from core.data_loader import load_city_graph, load_disaster_events, save_disaster_events
from core.disaster_manager import block_road, spread_disaster, unblock_road
from core.dynamic_obstacles import block_road_live, restore_road_live
from core.graph_engine import get_positions
from core.mission_manager import MissionManager
from models.disaster import BlockRoadBody, TriggerDisasterBody, UnblockRoadBody
from simulation.state import sim_state

router = APIRouter()


@router.get("")
def list_disasters() -> list:
    with sim_state.lock:
        return list(sim_state.disaster_events)


@router.post("/trigger")
def trigger_disaster(body: TriggerDisasterBody) -> dict:
    city = body.city or sim_state.active_city
    from core.graph_engine import load_graph

    if city == sim_state.active_city and sim_state.G is not None:
        G = sim_state.G
    else:
        cg = load_city_graph(city)
        G = load_graph(cg)
    event = spread_disaster(G, body.epicenter_node, body.radius, body.type, body.severity)
    events = list(load_disaster_events(city))
    events.append(event)
    save_disaster_events(events, city)
    with sim_state.lock:
        if city == sim_state.active_city:
            sim_state.disaster_events = events
    return {"event": event}


@router.post("/block-road")
def block_road_endpoint(body: BlockRoadBody) -> dict:
    with sim_state.lock:
        if sim_state.G is None:
            raise HTTPException(status_code=503, detail="Simulation not initialized")
        events = block_road(body.u, body.v, "congestion", sim_state.disaster_events)
        save_disaster_events(events, sim_state.active_city)
        sim_state.disaster_events = events
        sim_state.persist_missions()
        affected = block_road_live(sim_state.G, body.u, body.v, sim_state.active_missions)["affected_missions"]
        replans = []
        mm = MissionManager()
        for mid in affected:
            if not mid:
                continue
            try:
                old = next(m for m in sim_state.active_missions if m.get("mission_id") == mid)
                old_len = len(old.get("path", []))
                m = mm.replan_mission(
                    mid,
                    sim_state.G,
                    sim_state.disaster_events,
                    get_positions(sim_state.city_graph_data),
                    sim_state.city_graph_data,
                )
                for i, am in enumerate(sim_state.active_missions):
                    if am.get("mission_id") == mid:
                        sim_state.active_missions[i] = m
                        break
                replans.append(
                    {
                        "mission_id": mid,
                        "old_steps": old_len,
                        "new_steps": len(m.get("path", [])),
                        "algorithm": m.get("algorithm_used"),
                    }
                )
            except (StopIteration, ValueError):
                continue
        sim_state.persist_missions()
    return {"ok": True, "replans": replans}


@router.post("/unblock-road")
def unblock_road_endpoint(body: UnblockRoadBody) -> dict:
    with sim_state.lock:
        events = unblock_road(body.u, body.v, sim_state.disaster_events)
        save_disaster_events(events, sim_state.active_city)
        sim_state.disaster_events = events
        if sim_state.G and sim_state.G.has_edge(body.u, body.v):
            sim_state.G.edges[body.u, body.v]["blocked_live"] = False
    return {"ok": True}


@router.delete("/{event_id}")
def resolve_disaster(event_id: str) -> dict:
    city = sim_state.active_city
    events = load_disaster_events(city)
    target = next((e for e in events if e.get("event_id") == event_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Event not found")
    for pair in list(target.get("blocked_edges", [])):
        if len(pair) >= 2:
            events = unblock_road(pair[0], pair[1], events)
    for e in events:
        if e.get("event_id") == event_id:
            e["active"] = False
            break
    save_disaster_events(events, city)
    with sim_state.lock:
        sim_state.disaster_events = copy.deepcopy(events)
    return {"ok": True}
