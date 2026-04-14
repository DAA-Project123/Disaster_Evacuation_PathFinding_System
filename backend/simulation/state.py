"""
Global in-memory simulation state. One instance per server lifetime.
Holds the live networkx graph, active missions, agent positions,
node people counts. FastAPI routes read/write this state.
"""

from __future__ import annotations

import copy
import threading
from typing import Any

import networkx as nx

from core.data_loader import (
    load_city_graph,
    load_disaster_events,
    load_rescue_units,
    load_safe_zones,
)
from core.graph_engine import load_graph
from core.mission_manager import MissionManager


class SimulationState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.active_city: str = "Veridian City"
        self.G: nx.Graph | None = None
        self.city_graph_data: dict[str, Any] = {}
        self.disaster_events: list = []
        self.safe_zones: list = []
        self.rescue_units: dict = {}
        self.node_people: dict = {}
        self.active_missions: list = []
        self.tick: int = 0
        self.sim_time_min: float = 0.0
        self.running: bool = False

    def load_city(self, city_name: str) -> None:
        """Load all data for a city into memory. Called on startup and city switch."""
        with self.lock:
            self.active_city = city_name
            self.city_graph_data = copy.deepcopy(load_city_graph(city_name))
            self.G = load_graph(self.city_graph_data)
            self.disaster_events = list(load_disaster_events(city_name))
            self.safe_zones = list(load_safe_zones(city_name))
            units = load_rescue_units(city_name)
            self.rescue_units = {u["unit_id"]: dict(u) for u in units}
            self.node_people = {
                n["id"]: int(n.get("people_stranded", 0))
                for n in self.city_graph_data.get("nodes", [])
            }
            mm = MissionManager()
            self.active_missions = [m for m in mm.load() if m.get("city") == city_name and m.get("status") != "complete"]
            self.tick = 0
            self.sim_time_min = 0.0
            self.running = False

    def get_snapshot(self) -> dict:
        """Return serializable snapshot of full state for frontend polling."""
        with self.lock:
            return {
                "active_city": self.active_city,
                "tick": self.tick,
                "sim_time_min": self.sim_time_min,
                "running": self.running,
                "city_graph": self.city_graph_data,
                "disaster_events": list(self.disaster_events),
                "safe_zones": list(self.safe_zones),
                "rescue_units": dict(self.rescue_units),
                "node_people": dict(self.node_people),
                "missions": [copy.deepcopy(m) for m in self.active_missions],
            }

    def get_light_snapshot(self) -> dict:
        """Agent positions and mission statuses for high-frequency polling."""
        with self.lock:
            agent_positions = {uid: u.get("current_node", "") for uid, u in self.rescue_units.items()}
            missions_brief = [
                {
                    "mission_id": m.get("mission_id"),
                    "status": m.get("status"),
                    "current_step": m.get("current_step", 0),
                    "team_id": m.get("team_id"),
                    "path": list(m.get("path", [])),
                }
                for m in self.active_missions
            ]
            return {
                "tick": self.tick,
                "sim_time_min": self.sim_time_min,
                "running": self.running,
                "agent_positions": agent_positions,
                "missions": missions_brief,
                "node_people": dict(self.node_people),
            }

    def persist_missions(self) -> None:
        mm = MissionManager()
        all_m = mm.load()
        completed_this_city = [m for m in all_m if m.get("city") == self.active_city and m.get("status") == "complete"]
        other_cities = [m for m in all_m if m.get("city") != self.active_city]
        mm.save(other_cities + completed_this_city + self.active_missions)

    def persist_rescue_units(self) -> None:
        from core.data_loader import save_rescue_units

        save_rescue_units(list(self.rescue_units.values()), self.active_city)


sim_state = SimulationState()


def bootstrap_state() -> None:
    sim_state.load_city(sim_state.active_city)
