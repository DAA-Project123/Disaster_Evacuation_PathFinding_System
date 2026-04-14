from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException

from core.mission_manager import MissionManager
from models.simulation import SpeedBody
from simulation.engine import engine
from simulation.state import bootstrap_state, sim_state

router = APIRouter()

_loop_task: asyncio.Task | None = None


@router.get("/state")
def get_state() -> dict:
    return sim_state.get_snapshot()


@router.get("/snapshot")
def get_snapshot() -> dict:
    return sim_state.get_light_snapshot()


@router.post("/start")
async def start_sim() -> dict:
    global _loop_task
    engine.resume()
    if _loop_task is None or _loop_task.done():
        _loop_task = asyncio.create_task(engine.run_loop())
    return {"ok": True, "running": True}


@router.post("/pause")
def pause_sim() -> dict:
    engine.pause()
    return {"ok": True, "running": False}


@router.post("/resume")
async def resume_sim() -> dict:
    global _loop_task
    engine.resume()
    if _loop_task is None or _loop_task.done():
        _loop_task = asyncio.create_task(engine.run_loop())
    return {"ok": True, "running": True}


@router.post("/reset")
def reset_sim() -> dict:
    engine.pause()
    mm = MissionManager()
    all_m = mm.load()
    rest = [m for m in all_m if m.get("city") != sim_state.active_city]
    mm.save(rest)
    bootstrap_state()
    return {"ok": True}


@router.post("/speed")
def set_speed(body: SpeedBody) -> dict:
    engine.set_speed(body.seconds)
    return {"ok": True, "seconds": engine.tick_interval}


@router.post("/advance-mission/{mission_id}")
def advance_mission_manual(mission_id: str) -> dict:
    with sim_state.lock:
        mission = next((m for m in sim_state.active_missions if m.get("mission_id") == mission_id), None)
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        st = mission.get("status")
        if st == "en_route":
            engine._advance_mission(mission, 0)  # noqa: SLF001
        elif st == "returning":
            engine._advance_return(mission, 0)  # noqa: SLF001
        else:
            raise HTTPException(status_code=400, detail="Mission not advancing in this state")
        if mission.get("status") == "complete":
            try:
                sim_state.active_missions.remove(mission)
            except ValueError:
                pass
        sim_state.persist_missions()
        sim_state.persist_rescue_units()
        return mission
