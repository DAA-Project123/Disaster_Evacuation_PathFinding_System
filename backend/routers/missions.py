from __future__ import annotations

import copy

from fastapi import APIRouter, HTTPException

from core.algorithm_selector import select_and_run
from core.data_loader import load_city_graph, load_rescue_units
from core.graph_engine import get_positions
from core.mission_manager import MissionManager
from models.mission import ConfirmRescueBody, DispatchMissionBody
from simulation.state import sim_state

router = APIRouter()


def _algorithm_row_to_result(row: dict, why: str) -> dict:
    return {
        "algorithm": row["Algorithm"],
        "why_selected": why,
        "nodes_explored": int(row["Nodes Explored"]),
        "runtime_ms": float(row["Time (ms)"]),
        "used_air_edges": bool(row.get("used_air_edges", False)),
    }


@router.get("")
def list_missions(city: str | None = None) -> list:
    c = city or sim_state.active_city
    mm = MissionManager()
    return [m for m in mm.load() if m.get("city") == c]


@router.post("/dispatch")
def dispatch_mission(body: DispatchMissionBody) -> dict:
    city = body.city or sim_state.active_city
    with sim_state.lock:
        if sim_state.G is None:
            raise HTTPException(status_code=503, detail="Simulation not initialized")
        team = sim_state.rescue_units.get(body.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Unknown team")
        if team.get("status") != "available":
            raise HTTPException(status_code=400, detail="Team not available")

        cg = sim_state.city_graph_data
        node_map = {n["id"]: n for n in cg.get("nodes", [])}
        target = node_map.get(body.target_node)
        if not target:
            raise HTTPException(status_code=404, detail="Unknown target node")

        unit_type = "helicopter" if team.get("unit_type") == "helicopter" else "ground"
        positions = get_positions(cg)
        result = select_and_run(
            sim_state.G,
            team["current_node"],
            body.target_node,
            sim_state.disaster_events,
            positions,
            cg,
            unit_type=unit_type,
        )
        algo_key = body.algorithm.strip()
        if algo_key == "recommended" or algo_key.lower() == "recommended":
            rec = result["recommended"]
            path = rec["path"]
            algo_result = {
                "algorithm": rec["algorithm"],
                "why_selected": rec["why_selected"],
                "nodes_explored": rec["nodes_explored"],
                "runtime_ms": rec["runtime_ms"],
                "used_air_edges": rec["used_air_edges"],
            }
        else:

            def _norm_algo(s: str) -> str:
                return s.strip().lower().replace("*", "").replace(" ", "")

            want = _norm_algo(algo_key)
            match = next((r for r in result["all_results"] if _norm_algo(r["Algorithm"]) == want), None)
            if not match or not match.get("Path Found"):
                raise HTTPException(status_code=400, detail=f"No path for algorithm {body.algorithm}")
            path = match["Path"]
            algo_result = _algorithm_row_to_result(match, f"Manually selected {match['Algorithm']}.")

        mm = MissionManager()
        mission = mm.create_mission(
            team,
            body.target_node,
            target.get("name", body.target_node),
            path,
            [node_map.get(n, {}).get("name", n) for n in path],
            algo_result,
            int(target.get("people_stranded", 0)),
            str(target.get("injury_level", "none")),
            city,
        )
        sim_state.rescue_units[body.team_id] = dict(team)
        sim_state.rescue_units[body.team_id]["status"] = "dispatched"
        sim_state.active_missions.append(mission)
        sim_state.persist_missions()
        sim_state.persist_rescue_units()
        return mission


@router.post("/{mission_id}/confirm-rescue")
def confirm_rescue(mission_id: str, body: ConfirmRescueBody) -> dict:
    sim_state.persist_missions()
    mm = MissionManager()
    mission = mm.confirm_rescue(mission_id, body.people_rescued)
    with sim_state.lock:
        sim_state.city_graph_data = copy.deepcopy(load_city_graph(sim_state.active_city))
        sim_state.node_people = {
            n["id"]: int(n.get("people_stranded", 0)) for n in sim_state.city_graph_data.get("nodes", [])
        }
        teams = {t["unit_id"]: t for t in load_rescue_units(sim_state.active_city)}
        for uid, t in teams.items():
            if uid in sim_state.rescue_units:
                sim_state.rescue_units[uid].update(t)
        for i, m in enumerate(sim_state.active_missions):
            if m.get("mission_id") == mission_id:
                sim_state.active_missions[i] = mission
                break
    return mission


@router.post("/{mission_id}/start-return")
def start_return(mission_id: str) -> dict:
    sim_state.persist_missions()
    mm = MissionManager()
    mission = mm.start_return(mission_id)
    with sim_state.lock:
        for i, m in enumerate(sim_state.active_missions):
            if m.get("mission_id") == mission_id:
                sim_state.active_missions[i] = mission
                break
    return mission


@router.post("/{mission_id}/complete")
def complete_mission(mission_id: str) -> dict:
    sim_state.persist_missions()
    mm = MissionManager()
    mission = mm.complete_mission(mission_id)
    with sim_state.lock:
        sim_state.active_missions = [m for m in sim_state.active_missions if m.get("mission_id") != mission_id]
        teams = {t["unit_id"]: t for t in load_rescue_units(sim_state.active_city)}
        for uid, t in teams.items():
            if uid in sim_state.rescue_units:
                sim_state.rescue_units[uid].update(t)
        sim_state.persist_missions()
        sim_state.persist_rescue_units()
    return mission
