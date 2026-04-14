"""
Tick-based simulation engine. NOT autonomous — admin triggers each action.
When admin dispatches a mission, the engine animates agent movement
automatically at a configurable tick rate.

Each running mission advances one node per tick.
Admin can pause/resume/reset.
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from simulation.state import sim_state


class SimulationEngine:
    def __init__(self, tick_interval_seconds: float = 1.5) -> None:
        self.tick_interval = tick_interval_seconds
        self.running = False
        self._loop_task: asyncio.Task | None = None

    async def run_loop(self) -> None:
        while True:
            if self.running and sim_state.running:
                await self._tick()
                await asyncio.sleep(self.tick_interval)
            else:
                await asyncio.sleep(0.05)

    async def _tick(self) -> None:
        with sim_state.lock:
            delta_min = float(self.tick_interval)
            finished: list[dict] = []
            for mission in sim_state.active_missions:
                st = mission.get("status")
                if st == "en_route":
                    self._advance_mission(mission, delta_min)
                elif st == "arrived":
                    pass
                elif st == "returning":
                    self._advance_return(mission, delta_min)
                if mission.get("status") == "complete":
                    finished.append(mission)
            for m in finished:
                sim_state.active_missions.remove(m)

            sim_state.tick += 1
            sim_state.sim_time_min += delta_min
            sim_state.persist_missions()
            sim_state.persist_rescue_units()

    def _advance_mission(self, mission: dict, delta_min: float) -> None:
        path = mission.get("path") or []
        step = int(mission.get("current_step", 0))
        if not path:
            return
        if step >= len(path) - 1:
            mission["status"] = "arrived"
            mission.setdefault("arrived_at", datetime.now().isoformat(timespec="seconds"))
            return
        mission["current_step"] = step + 1
        cur = path[mission["current_step"]]
        team_id = mission.get("team_id")
        if team_id and team_id in sim_state.rescue_units:
            sim_state.rescue_units[team_id]["current_node"] = cur
        if mission["current_step"] >= len(path) - 1:
            mission["status"] = "arrived"
            mission["arrived_at"] = datetime.now().isoformat(timespec="seconds")

    def _advance_return(self, mission: dict, delta_min: float) -> None:
        path = mission.get("path") or []
        step = int(mission.get("current_step", 0))
        if len(path) < 2 or step >= len(path) - 1:
            mission["status"] = "complete"
            mission["completed_at"] = datetime.now().isoformat(timespec="seconds")
            team_id = mission.get("team_id")
            if team_id and team_id in sim_state.rescue_units:
                sim_state.rescue_units[team_id]["status"] = "available"
                sim_state.rescue_units[team_id]["current_node"] = path[-1] if path else ""
            return
        mission["current_step"] = step + 1
        cur = path[mission["current_step"]]
        team_id = mission.get("team_id")
        if team_id and team_id in sim_state.rescue_units:
            sim_state.rescue_units[team_id]["current_node"] = cur

    def pause(self) -> None:
        self.running = False
        sim_state.running = False

    def resume(self) -> None:
        self.running = True
        sim_state.running = True

    def set_speed(self, seconds: float) -> None:
        self.tick_interval = max(0.1, float(seconds))


engine = SimulationEngine()
