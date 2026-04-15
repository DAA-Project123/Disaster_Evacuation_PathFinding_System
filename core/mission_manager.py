"""Mission CRUD, advance step, replan operations."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

MISSIONS_FILE = Path("data/active_missions.json")
RESCUE_LOG_FILE = Path("data/rescue_log.csv")


def load_missions() -> List[Dict]:
    """Load all missions from file."""
    if not MISSIONS_FILE.exists():
        return []
    with open(MISSIONS_FILE, 'r') as f:
        return json.load(f)


def save_missions(missions: List[Dict]):
    """Save missions to file."""
    with open(MISSIONS_FILE, 'w') as f:
        json.dump(missions, f, indent=2)


def create_mission(map_name: str, team: Dict, base_node: str, target_node: str, 
                   target_name: str, path: List[str], path_names: List[str], 
                   algorithm_result: Dict, people_at_target: int, injury_level: str) -> Dict:
    """
    Create a new rescue mission.
    
    A mission is: safe_zone -> disaster_node -> safe_zone (round trip).
    """
    missions = load_missions()
    
    mission_id = f"M{int(datetime.now().timestamp())}"
    now = datetime.now().isoformat()
    
    mission = {
        "mission_id": mission_id,
        "map": map_name,
        "team_id": team["id"],
        "team_name": team["name"],
        "team_type": team["type"],
        "base_node": base_node,
        "target_node": target_node,
        "target_name": target_name,
        "path_to_target": path,
        "path_names_to_target": path_names,
        "return_path": [],
        "current_step": 0,
        "phase": "outbound",
        "algorithm_used": algorithm_result["algorithm"],
        "why_selected": algorithm_result.get("why_selected", ""),
        "nodes_explored": algorithm_result["nodes_explored"],
        "time_ms": algorithm_result["time_ms"],
        "path_length": algorithm_result["path_length"],
        "people_at_target": people_at_target,
        "injury_level": injury_level,
        "status": "en_route",
        "replanned": False,
        "original_path_length": algorithm_result["path_length"],
        "dispatched_at": now,
        "arrived_at": None,
        "rescued_at": None,
        "completed_at": None,
        "fuel_used": 0,
        "used_air_edges": algorithm_result.get("used_air_edges", False),
        "people_rescued": 0
    }
    
    missions.append(mission)
    save_missions(missions)
    
    return mission


def get_mission(mission_id: str) -> Optional[Dict]:
    """Get a specific mission by ID."""
    missions = load_missions()
    return next((m for m in missions if m["mission_id"] == mission_id), None)


def get_active_missions() -> List[Dict]:
    """Get all non-complete missions."""
    missions = load_missions()
    return [m for m in missions if m["status"] != "complete"]


def get_completed_missions() -> List[Dict]:
    """Get all completed missions."""
    missions = load_missions()
    return [m for m in missions if m["status"] == "complete"]


def advance_step(mission_id: str) -> Dict:
    """Advance mission by one step."""
    missions = load_missions()
    mission = next((m for m in missions if m["mission_id"] == mission_id), None)
    
    if not mission:
        raise ValueError(f"Mission {mission_id} not found")
    
    path = mission["path_to_target"] if mission["phase"] == "outbound" else mission["return_path"]
    
    if mission["current_step"] < len(path) - 1:
        mission["current_step"] += 1
    
    # Check if arrived
    if mission["current_step"] == len(path) - 1:
        if mission["phase"] == "outbound":
            mission["status"] = "arrived"
            mission["arrived_at"] = datetime.now().isoformat()
        elif mission["phase"] == "returning":
            mission["status"] = "complete"
            mission["completed_at"] = datetime.now().isoformat()
    
    save_missions(missions)
    return mission


def confirm_rescue(mission_id: str, city_graph_data: Dict) -> Dict:
    """
    Confirm rescue at target node.
    CRITICAL GUARD: Check node's people_stranded > 0 and people_rescued == 0.
    """
    missions = load_missions()
    mission = next((m for m in missions if m["mission_id"] == mission_id), None)
    
    if not mission:
        raise ValueError(f"Mission {mission_id} not found")
    
    target_node_id = mission["target_node"]
    
    # Find target node in city data
    target_node = None
    for n in city_graph_data.get("nodes", []):
        if n["id"] == target_node_id:
            target_node = n
            break
    
    if not target_node:
        raise ValueError(f"Target node {target_node_id} not found in city data")
    
    # CRITICAL GUARDS
    people_stranded = target_node.get("people_stranded", 0)
    people_rescued = target_node.get("people_rescued", 0)
    
    if people_stranded == 0:
        raise ValueError(f"No people to rescue at node {target_node_id}")
    
    if people_rescued > 0:
        raise ValueError(f"Node {target_node_id} already rescued")
    
    # Update node data
    target_node["people_rescued"] = people_stranded
    target_node["people_stranded"] = 0
    
    # Update mission
    mission["people_rescued"] = people_stranded
    mission["status"] = "rescued"
    mission["rescued_at"] = datetime.now().isoformat()
    
    # Calculate fuel used
    path_length = mission["path_length"]
    used_air = mission.get("used_air_edges", False)
    mission["fuel_used"] = path_length * (3 if used_air else 2)
    
    save_missions(missions)
    
    # Log to rescue_log.csv
    _append_to_rescue_log(mission)
    
    return mission


def _append_to_rescue_log(mission: Dict):
    """Append mission completion to rescue log CSV."""
    import csv
    
    # Check if already logged
    if RESCUE_LOG_FILE.exists():
        with open(RESCUE_LOG_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("mission_id") == mission["mission_id"]:
                    return  # Already logged
    
    # Append new entry
    fieldnames = [
        "timestamp", "mission_id", "team_id", "team_name", "base_node", "target_node",
        "target_name", "algorithm_used", "nodes_explored", "time_ms", "path_length",
        "path_cost", "people_rescued", "fuel_used", "used_air_edges", "status"
    ]
    
    row = {
        "timestamp": datetime.now().isoformat(),
        "mission_id": mission["mission_id"],
        "team_id": mission["team_id"],
        "team_name": mission["team_name"],
        "base_node": mission["base_node"],
        "target_node": mission["target_node"],
        "target_name": mission["target_name"],
        "algorithm_used": mission["algorithm_used"],
        "nodes_explored": mission["nodes_explored"],
        "time_ms": mission["time_ms"],
        "path_length": mission["path_length"],
        "path_cost": mission["path_length"],  # Simplified
        "people_rescued": mission["people_rescued"],
        "fuel_used": mission["fuel_used"],
        "used_air_edges": mission.get("used_air_edges", False),
        "status": mission["status"]
    }
    
    file_exists = RESCUE_LOG_FILE.exists()
    with open(RESCUE_LOG_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def start_return(mission_id: str, G, blocked_edges: set = None, unit_type: str = "ground") -> Dict:
    """
    Start return journey from target back to base.
    Compute return path using Dijkstra.
    """
    from core.algorithms.dijkstra import dijkstra
    from core.graph_engine import get_adjacency_list_weighted
    
    missions = load_missions()
    mission = next((m for m in missions if m["mission_id"] == mission_id), None)
    
    if not mission:
        raise ValueError(f"Mission {mission_id} not found")
    
    # Compute return path
    adj = get_adjacency_list_weighted(G, blocked_edges, unit_type)
    result = dijkstra(adj, mission["target_node"], mission["base_node"])
    
    if not result.get("found"):
        # Fallback: reverse the original path
        return_path = list(reversed(mission["path_to_target"]))
    else:
        return_path = result["path"]
    
    # Update mission
    mission["return_path"] = return_path
    mission["phase"] = "returning"
    mission["status"] = "returning"
    mission["current_step"] = 0
    
    save_missions(missions)
    return mission


def complete_mission(mission_id: str, teams_data: List[Dict], city_graph_data: Dict = None) -> Dict:
    """
    Complete mission and update team status.
    Also update safe zone node with rescued people count.
    """
    missions = load_missions()
    mission = next((m for m in missions if m["mission_id"] == mission_id), None)
    
    if not mission:
        raise ValueError(f"Mission {mission_id} not found")
    
    mission["status"] = "complete"
    mission["completed_at"] = datetime.now().isoformat()
    
    # Update team
    for team in teams_data:
        if team["id"] == mission["team_id"]:
            team["status"] = "available"
            team["current_node"] = mission["base_node"]
            team["people_rescued_total"] = team.get("people_rescued_total", 0) + mission["people_rescued"]
            team["missions_completed"] = team.get("missions_completed", 0) + 1
            break
    
    # Update safe zone node's people_rescued count
    if city_graph_data and mission.get("people_rescued", 0) > 0:
        base_node_id = mission["base_node"]
        for n in city_graph_data.get("nodes", []):
            if n["id"] == base_node_id:
                n["people_rescued"] = n.get("people_rescued", 0) + mission["people_rescued"]
                break
    
    save_missions(missions)
    return mission


def block_affects_mission(blocked_u: str, blocked_v: str) -> List[str]:
    """
    Check if a blocked edge affects any active mission.
    Returns list of affected mission IDs.
    """
    affected = []
    missions = load_missions()
    
    for mission in missions:
        if mission["status"] not in ["en_route", "returning"]:
            continue
        
        path = mission["path_to_target"] if mission["phase"] == "outbound" else mission["return_path"]
        current_step = mission["current_step"]
        remaining_path = path[current_step:]
        
        for i in range(len(remaining_path) - 1):
            if (remaining_path[i] == blocked_u and remaining_path[i+1] == blocked_v) or \
               (remaining_path[i] == blocked_v and remaining_path[i+1] == blocked_u):
                affected.append(mission["mission_id"])
                break
    
    return affected


def replan_mission(mission_id: str, G, blocked_edges: set, positions: Dict, 
                    city_graph_data: Dict, unit_type: str = "ground") -> Dict:
    """
    Replan an active mission with current road conditions.
    """
    from core.algorithm_selector import select_and_run
    
    missions = load_missions()
    mission = next((m for m in missions if m["mission_id"] == mission_id), None)
    
    if not mission:
        raise ValueError(f"Mission {mission_id} not found")
    
    # Get current position
    if mission["phase"] == "outbound":
        current_node = mission["path_to_target"][mission["current_step"]]
        target = mission["target_node"]
    else:
        current_node = mission["return_path"][mission["current_step"]]
        target = mission["base_node"]
    
    # Run algorithms again
    result = select_and_run(G, current_node, target, {}, positions, city_graph_data, unit_type)
    
    recommended = result["recommended"]
    if not recommended:
        return mission  # Cannot replan
    
    # Get display names
    node_map = {n["id"]: n["display_name"] for n in city_graph_data.get("nodes", [])}
    new_path_names = [node_map.get(n, n) for n in recommended["path"]]
    
    # Update mission
    if mission["phase"] == "outbound":
        old_path_length = len(mission["path_to_target"]) - 1
        mission["path_to_target"] = recommended["path"]
        mission["path_names_to_target"] = new_path_names
    else:
        old_path_length = len(mission["return_path"]) - 1
        mission["return_path"] = recommended["path"]
    
    mission["algorithm_used"] = recommended["algorithm"]
    mission["why_selected"] = result.get("why_selected", "")
    mission["current_step"] = 0
    mission["path_length"] = recommended["path_length"]
    mission["nodes_explored"] = recommended["nodes_explored"]
    mission["time_ms"] = recommended["time_ms"]
    mission["used_air_edges"] = recommended.get("used_air_edges", False)
    mission["replanned"] = True
    mission["original_path_length"] = old_path_length
    
    save_missions(missions)
    return mission
