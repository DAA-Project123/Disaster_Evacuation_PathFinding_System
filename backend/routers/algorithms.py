from __future__ import annotations

from fastapi import APIRouter, HTTPException

from core.algorithm_selector import select_and_run
from core.data_loader import load_city_graph, load_disaster_events, load_rescue_units
from core.graph_engine import get_positions, load_graph
from core.greedy_selector import highest_priority_first, nearest_victim_first
from core.knapsack import build_victim_list, knapsack_01
from models.algorithm import CompareAlgorithmsBody, GreedyBody, KnapsackBody
from simulation.state import sim_state

router = APIRouter()


@router.post("/compare")
def compare_algorithms(body: CompareAlgorithmsBody) -> dict:
    city = body.city or sim_state.active_city
    with sim_state.lock:
        if sim_state.active_city == city and sim_state.G is not None:
            G = sim_state.G
            cg = sim_state.city_graph_data
            events = list(sim_state.disaster_events)
        else:
            cg = load_city_graph(city)
            G = load_graph(cg)
            events = list(load_disaster_events(city))
    positions = get_positions(cg)
    out = select_and_run(
        G,
        body.start_node,
        body.goal_node,
        events,
        positions,
        cg,
        unit_type=body.unit_type,
    )
    rec = out["recommended"]
    scenario = {"city": city, "start": body.start_node, "goal": body.goal_node, "unit_type": body.unit_type}
    return {
        "recommended": rec,
        "all_results": out["all_results"],
        "scenario": scenario,
    }


@router.post("/greedy")
def run_greedy(body: GreedyBody) -> list[dict]:
    with sim_state.lock:
        if sim_state.G is None:
            raise HTTPException(status_code=503, detail="Simulation not initialized")
        team = sim_state.rescue_units.get(body.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Unknown team")
        cg = sim_state.city_graph_data
        victims = [n for n in cg.get("nodes", []) if int(n.get("people_stranded", 0)) > 0]
        if body.strategy == "nearest":
            df = nearest_victim_first(sim_state.G, team["current_node"], victims, sim_state.disaster_events)
        else:
            df = highest_priority_first(victims, cg)
    return df.to_dict(orient="records")


@router.post("/knapsack")
def run_knapsack(body: KnapsackBody) -> dict:
    city = body.city or sim_state.active_city
    cg = load_city_graph(city)
    victim_ids = [n["id"] for n in cg.get("nodes", []) if int(n.get("people_stranded", 0)) > 0]
    victims = build_victim_list(cg, victim_ids, [])
    capacity = 50
    if body.team_id:
        with sim_state.lock:
            t = sim_state.rescue_units.get(body.team_id) if sim_state.active_city == city else None
        if not t:
            t = next((u for u in load_rescue_units(city) if u.get("unit_id") == body.team_id), None)
        if t:
            capacity = int(t.get("capacity", 50))
    result = knapsack_01(victims, capacity)
    return {
        "selected": result["selected"],
        "not_selected": result["not_selected"],
        "total_value": result["total_value"],
        "dp_table": result["dp_table"],
        "traceback": result["traceback"],
        "capacity": capacity,
    }
