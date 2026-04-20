"""
FastAPI Backend for Disaster Evacuation PathFinding System
"""
from __future__ import annotations

import json
import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Import core modules
from core.data_loader import (
    load_city_graph, save_city_graph,
    load_disaster_events, save_disaster_events,
    load_rescue_units, save_rescue_units,
    load_safe_zones, save_safe_zones,
    load_resources, save_resources,
    load_evacuation_zones, CITY_MAP, CITY_DISPLAY_NAMES
)
from core.graph_engine import load_graph, get_adjacency_list, get_unweighted_adjacency, get_positions
from core.disaster_manager import spread_disaster, block_road, unblock_road, get_all_blocked_edges, compute_risk_score
from core.algorithm_selector import select_and_run
from core.mission_manager import MissionManager
from core.resource_manager import ResourceManager
from core.algorithm_visualizer import run_algorithm_with_steps
from core.greedy_selector import nearest_team_to_target

# Store active WebSocket connections and animation state
active_connections: list[WebSocket] = []
animation_state: dict[str, Any] = {}




# Pydantic models
class DisasterCreate(BaseModel):
    city: str
    disaster_type: str
    epicenter: str
    radius: int
    severity: str


class StrandedUpdate(BaseModel):
    city: str
    node_id: str
    people_stranded: int
    injury_level: str
    survival_chance: float
    rescue_cost: int


class DispatchRequest(BaseModel):
    city: str
    team_id: str
    target_node: str
    algorithm: str = "auto"


class ResourceDispatch(BaseModel):
    resource_id: str
    quantity: int
    safe_zone_id: str
    city: str


class RoadBlockRequest(BaseModel):
    city: str
    node_a: str
    node_b: str
    reason: str = "manual"


class AlgorithmCompareRequest(BaseModel):
    city: str
    start: str
    goal: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: ensure data directories exist
    Path("data/cities").mkdir(parents=True, exist_ok=True)
    Path("static").mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown cleanup
    active_connections.clear()


app = FastAPI(
    title="Disaster Evacuation PathFinding System",
    description="FastAPI backend with live algorithm visualization",
    version="2.0.0",
    lifespan=lifespan
)

# Mount static files
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the main application."""
    return FileResponse("static/index.html")


# ==================== City Endpoints ====================

@app.get("/api/cities")
async def get_cities():
    """Get list of available cities/maps."""
    return {
        "cities": [
            {"id": "Map 1", "name": "Veridian City", "file": "city_map1.json"},
            {"id": "Map 2", "name": "Harborfield", "file": "city_map2.json"},
            {"id": "Map 3", "name": "Maplecrest", "file": "city_map3.json"},
        ]
    }


@app.get("/api/city/{city_id}")
async def get_city(city_id: str):
    """Get full city graph data."""
    try:
        city_data = load_city_graph(city_id)
        events = load_disaster_events(city_id)
        zones = load_evacuation_zones(city_id)
        safe_zones = load_safe_zones(city_id)
        
        G = load_graph(city_data)
        blocked = get_all_blocked_edges(events)
        
        # Compute risk scores for all nodes
        for node in city_data.get("nodes", []):
            node["risk_score"] = compute_risk_score(node["id"], events, G)
        
        return {
            "city": city_data,
            "events": events,
            "zones": zones,
            "safe_zones": safe_zones,
            "blocked_edges": list(blocked),
            "active_disasters": len([e for e in events if e.get("active", False)])
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"City not found: {str(e)}")


@app.get("/api/city/{city_id}/nodes")
async def get_city_nodes(city_id: str):
    """Get all nodes for a city."""
    try:
        city_data = load_city_graph(city_id)
        events = load_disaster_events(city_id)
        G = load_graph(city_data)
        
        nodes = []
        for node in city_data.get("nodes", []):
            nodes.append({
                "id": node["id"],
                "name": node.get("name", node["id"]),
                "type": node.get("type", "intersection"),
                "x": node.get("x", 0),
                "y": node.get("y", 0),
                "zone": node.get("zone", ""),
                "people_stranded": node.get("people_stranded", 0),
                "injury_level": node.get("injury_level", "none"),
                "helipad": node.get("helipad", False),
                "risk_score": compute_risk_score(node["id"], events, G)
            })
        return {"nodes": nodes}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/city/{city_id}/edges")
async def get_city_edges(city_id: str):
    """Get all edges for a city."""
    try:
        city_data = load_city_graph(city_id)
        events = load_disaster_events(city_id)
        blocked = get_all_blocked_edges(events)
        
        edges = []
        for edge in city_data.get("edges", []):
            u, v = edge["source"], edge["target"]
            key = tuple(sorted((u, v)))
            edges.append({
                "source": u,
                "target": v,
                "distance_km": edge.get("distance_km", 1.0),
                "base_travel_time_min": edge.get("base_travel_time_min", 1.0),
                "blocked": key in blocked,
                "air_only": edge.get("air_only", False),
                "road_type": edge.get("road_type", "local"),
                "road_name": edge.get("road_name", f"{u}-{v}")
            })
        return {"edges": edges, "blocked_count": len(blocked)}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Disaster Endpoints ====================

@app.get("/api/city/{city_id}/disasters")
async def get_disasters(city_id: str):
    """Get all disaster events for a city."""
    events = load_disaster_events(city_id)
    return {"events": events, "active_count": len([e for e in events if e.get("active", False)])}


@app.post("/api/disasters/create")
async def create_disaster(data: DisasterCreate):
    """Create a new disaster event."""
    try:
        city_data = load_city_graph(data.city)
        G = load_graph(city_data)
        
        new_event = spread_disaster(
            G, data.epicenter, data.radius,
            data.disaster_type, data.severity
        )
        
        events = load_disaster_events(data.city)
        events.append(new_event)
        save_disaster_events(events, data.city)
        
        return {
            "success": True,
            "event": new_event,
            "message": f"Disaster created: {len(new_event['blocked_edges'])} roads blocked, {len(new_event['affected_nodes'])} nodes affected"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/disasters/{event_id}/resolve")
async def resolve_disaster(city_id: str, event_id: str):
    """Mark a disaster as resolved."""
    events = load_disaster_events(city_id)
    for e in events:
        if e.get("event_id") == event_id:
            e["active"] = False
            e["resolved_at"] = datetime.now().isoformat(timespec="seconds")
            save_disaster_events(events, city_id)
            return {"success": True, "message": "Disaster resolved"}
    raise HTTPException(status_code=404, detail="Event not found")


@app.post("/api/city/{city_id}/stranded")
async def update_stranded(city_id: str, data: StrandedUpdate):
    """Update stranded people at a node."""
    try:
        city_data = load_city_graph(city_id)
        for node in city_data.get("nodes", []):
            if node["id"] == data.node_id:
                node["people_stranded"] = data.people_stranded
                node["injury_level"] = data.injury_level
                node["survival_chance"] = data.survival_chance
                node["rescue_cost"] = data.rescue_cost
                save_city_graph(city_data, city_id)
                return {"success": True, "node": node}
        raise HTTPException(status_code=404, detail="Node not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/city/{city_id}/block-road")
async def block_road_endpoint(city_id: str, data: RoadBlockRequest):
    """Block a road manually."""
    try:
        events = load_disaster_events(city_id)
        events = block_road(data.node_a, data.node_b, data.reason, events)
        save_disaster_events(events, city_id)
        
        # Check affected missions
        mm = MissionManager()
        affected = mm.block_affects_mission(data.node_a, data.node_b)
        
        return {
            "success": True,
            "blocked": [data.node_a, data.node_b],
            "affected_missions": affected
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/city/{city_id}/unblock-road")
async def unblock_road_endpoint(city_id: str, data: RoadBlockRequest):
    """Unblock a road."""
    try:
        events = load_disaster_events(city_id)
        events = unblock_road(data.node_a, data.node_b, events)
        save_disaster_events(events, city_id)
        return {"success": True, "unblocked": [data.node_a, data.node_b]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Algorithm Endpoints ====================

@app.get("/api/city/{city_id}/algorithms/compare")
async def compare_algorithms(city_id: str, start: str, goal: str, unit_type: str = "ground"):
    """Run all algorithms and return comparison results."""
    try:
        city_data = load_city_graph(city_id)
        events = load_disaster_events(city_id)
        G = load_graph(city_data)
        positions = get_positions(city_data)
        
        result = select_and_run(
            G, start, goal, events, positions, city_data, unit_type
        )
        
        return {
            "recommended": result["recommended"],
            "all_results": result["all_results"],
            "start": start,
            "goal": goal
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/city/{city_id}/algorithms/animate/{algorithm}")
async def animate_algorithm(city_id: str, algorithm: str, start: str, goal: str, unit_type: str = "ground"):
    """Get step-by-step animation data for an algorithm."""
    try:
        city_data = load_city_graph(city_id)
        events = load_disaster_events(city_id)
        G = load_graph(city_data)
        positions = get_positions(city_data)
        
        if algorithm in ["BFS", "DFS"]:
            graph = get_unweighted_adjacency(G, events, unit_type=unit_type)
        else:
            graph = get_adjacency_list(G, "balanced", events, positions, unit_type=unit_type)
        
        result = run_algorithm_with_steps(algorithm, graph, start, goal, positions)
        return {
            "algorithm": algorithm,
            "start": start,
            "goal": goal,
            "path": result["path"],
            "steps": result["steps"],
            "visited_count": result["visited_count"],
            "cost": result.get("cost")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/city/{city_id}/algorithms/race")
async def algorithm_race(city_id: str, start: str, goal: str, unit_type: str = "ground"):
    """Run all 5 algorithms simultaneously for comparison visualization."""
    try:
        city_data = load_city_graph(city_id)
        events = load_disaster_events(city_id)
        G = load_graph(city_data)
        positions = get_positions(city_data)
        
        algorithms = ["BFS", "DFS", "Dijkstra", "A*", "UCS"]
        results = {}
        
        for algo in algorithms:
            try:
                if algo in ["BFS", "DFS"]:
                    graph = get_unweighted_adjacency(G, events, unit_type=unit_type)
                else:
                    graph = get_adjacency_list(G, "balanced", events, positions, unit_type=unit_type)
                
                result = run_algorithm_with_steps(algo, graph, start, goal, positions)
                results[algo] = result
            except Exception as ex:
                results[algo] = {"error": str(ex)}
        
        return {
            "start": start,
            "goal": goal,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Evacuation Wave Simulation ====================

@app.get("/api/city/{city_id}/evacuation-wave")
async def evacuation_wave(city_id: str, epicenter: str, max_hops: int = 5):
    """Get wave propagation data for evacuation simulation."""
    try:
        from collections import deque
        
        city_data = load_city_graph(city_id)
        G = load_graph(city_data)
        
        visited = {epicenter: 0}
        q = deque([epicenter])
        waves = []
        
        while q:
            node = q.popleft()
            depth = visited[node]
            if depth >= max_hops:
                continue
            
            wave_data = {
                "hop": depth,
                "nodes": [],
                "timestamp": depth * 2  # Simulated time
            }
            
            for nbr in G.neighbors(node):
                if nbr not in visited:
                    visited[nbr] = depth + 1
                    q.append(nbr)
                    wave_data["nodes"].append(nbr)
            
            if wave_data["nodes"]:
                waves.append(wave_data)
        
        return {
            "epicenter": epicenter,
            "max_hops": max_hops,
            "waves": waves,
            "total_affected": len(visited),
            "affected_nodes": list(visited.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Heatmap Endpoints ====================

@app.get("/api/city/{city_id}/heatmap")
async def get_heatmap(city_id: str):
    """Get risk heatmap data for all nodes."""
    try:
        city_data = load_city_graph(city_id)
        events = load_disaster_events(city_id)
        G = load_graph(city_data)
        
        heatmap = []
        for node in city_data.get("nodes", []):
            risk = compute_risk_score(node["id"], events, G)
            heatmap.append({
                "node_id": node["id"],
                "x": node.get("x", 0),
                "y": node.get("y", 0),
                "risk_score": risk,
                "risk_level": "critical" if risk > 0.8 else "high" if risk > 0.5 else "medium" if risk > 0.2 else "low",
                "people_stranded": node.get("people_stranded", 0)
            })
        
        return {"heatmap": heatmap}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Rescue Operations Endpoints ====================

@app.get("/api/city/{city_id}/rescue-teams")
async def get_rescue_teams(city_id: str):
    """Get all rescue teams for a city."""
    try:
        teams = load_rescue_units(city_id)
        return {"teams": teams, "available": len([t for t in teams if t.get("status") == "available"])}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/city/{city_id}/missions")
async def get_missions(city_id: str):
    """Get all missions for a city."""
    try:
        mm = MissionManager()
        all_missions = mm.load()
        city_missions = [m for m in all_missions if m.get("city") == city_id]
        
        active = [m for m in city_missions if m.get("status") in {"en_route", "arrived", "returning", "rescued"}]
        completed = [m for m in city_missions if m.get("status") == "complete"]
        
        return {
            "active": active,
            "completed": completed,
            "all": city_missions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/missions/dispatch")
async def dispatch_team(data: DispatchRequest):
    """Dispatch a rescue team to a target."""
    try:
        city_data = load_city_graph(data.city)
        events = load_disaster_events(data.city)
        G = load_graph(city_data)
        positions = get_positions(city_data)
        mm = MissionManager()
        
        teams = load_rescue_units(data.city)
        team = next((t for t in teams if t["unit_id"] == data.team_id), None)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Find target node data
        target_node = None
        for node in city_data.get("nodes", []):
            if node["id"] == data.target_node:
                target_node = node
                break
        
        if not target_node:
            raise HTTPException(status_code=404, detail="Target node not found")
        
        unit_type = "helicopter" if team.get("unit_type") == "helicopter" else "ground"
        
        # Run algorithm selection
        result = select_and_run(
            G, team["current_node"], data.target_node, events, positions, city_data, unit_type
        )
        
        algo_result = result["recommended"] if data.algorithm == "auto" else next(
            (r for r in result["all_results"] if r["Algorithm"] == data.algorithm),
            result["recommended"]
        )
        
        # Create mission
        mission = mm.create_mission(
            team,
            data.target_node,
            target_node.get("name", data.target_node),
            algo_result["path"],
            [target_node.get("name", data.target_node)],
            algo_result,
            target_node.get("people_stranded", 0),
            target_node.get("injury_level", "low"),
            data.city
        )
        
        return {
            "success": True,
            "mission": mission,
            "algorithm_used": algo_result["algorithm"],
            "path": algo_result["path"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/missions/{mission_id}/advance")
async def advance_mission(mission_id: str):
    """Advance a mission by one step."""
    try:
        mm = MissionManager()
        mission = mm.advance_step(mission_id)
        return {"success": True, "mission": mission}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/missions/{mission_id}/confirm-rescue")
async def confirm_rescue(mission_id: str, people_rescued: int):
    """Confirm rescue at target location."""
    try:
        mm = MissionManager()
        mission = mm.confirm_rescue(mission_id, people_rescued)
        return {"success": True, "mission": mission}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/missions/{mission_id}/return")
async def start_return(mission_id: str):
    """Start return journey to safe zone."""
    try:
        mm = MissionManager()
        mission = mm.start_return(mission_id)
        return {"success": True, "mission": mission}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/missions/{mission_id}/complete")
async def complete_mission(mission_id: str):
    """Complete a mission."""
    try:
        mm = MissionManager()
        mission = mm.complete_mission(mission_id)
        return {"success": True, "mission": mission}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/city/{city_id}/closest-team")
async def get_closest_team(city_id: str, target_node: str, unit_type: str = "ground"):
    """Find the closest available rescue team to a target node with algorithm comparison."""
    try:
        city_data = load_city_graph(city_id)
        events = load_disaster_events(city_id)
        G = load_graph(city_data)
        positions = get_positions(city_data)
        teams = load_rescue_units(city_id)
        available_teams = [t for t in teams if t.get("status") == "available"]
        
        if not available_teams:
            return {"success": False, "message": "No available teams"}
        
        # Build unit types map
        unit_types = {t["unit_id"]: ("helicopter" if t.get("unit_type") == "helicopter" else "ground") 
                      for t in available_teams}
        
        # Find best team
        best = nearest_team_to_target(G, target_node, available_teams, events, unit_types)
        
        if not best:
            return {"success": False, "message": "No reachable team found"}
        
        # Get algorithm comparison for this team
        team = best["team"]
        team_unit_type = unit_types.get(team["unit_id"], "ground")
        
        result = select_and_run(
            G, team["current_node"], target_node, events, positions, city_data, team_unit_type
        )
        
        return {
            "success": True,
            "recommended_team": team,
            "team_distance": best["cost"],
            "path": best["path"],
            "algorithm_comparison": result["all_results"],
            "recommended_algorithm": result["recommended"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/missions/{mission_id}/step-visualization")
async def get_mission_step_visualization(mission_id: str):
    """Get step-by-step visualization data for a mission's current path."""
    try:
        mm = MissionManager()
        all_missions = mm.load()
        mission = next((m for m in all_missions if m.get("mission_id") == mission_id), None)
        
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        city_id = mission.get("city")
        city_data = load_city_graph(city_id)
        events = load_disaster_events(city_id)
        G = load_graph(city_data)
        positions = get_positions(city_data)
        
        # Get current position and next step
        path = mission.get("path", [])
        current_step = mission.get("current_step", 0)
        
        if current_step >= len(path) - 1:
            return {"success": True, "message": "Mission complete", "visualization": None}
        
        current_node = path[current_step]
        next_node = path[current_step + 1]
        
        # Determine algorithm used
        algo = mission.get("algorithm_used", "Dijkstra")
        
        # Get full algorithm steps from start to current position
        team = load_rescue_units(city_id)
        team_data = next((t for t in team if t.get("unit_id") == mission.get("team_id")), None)
        unit_type = "helicopter" if team_data and team_data.get("unit_type") == "helicopter" else "ground"
        
        if algo in ["BFS", "DFS"]:
            graph = get_unweighted_adjacency(G, events, unit_type=unit_type)
        else:
            graph = get_adjacency_list(G, "balanced", events, positions, unit_type=unit_type)
        
        # Get full animation steps
        algo_result = run_algorithm_with_steps(algo, graph, path[0], path[-1], positions)
        
        # Filter steps up to and including current position
        filtered_steps = []
        visited_nodes = set()
        for step in algo_result.get("steps", []):
            if step.get("type") == "visit":
                visited_nodes.add(step.get("node"))
                filtered_steps.append(step)
                if step.get("node") == current_node:
                    break
            elif step.get("type") == "goal_found":
                filtered_steps.append(step)
        
        # Add current step highlight
        current_step_data = {
            "current_node": current_node,
            "next_node": next_node,
            "step_number": current_step,
            "total_steps": len(path) - 1,
            "visited_nodes": list(visited_nodes),
            "path_so_far": path[:current_step + 1],
            "remaining_path": path[current_step + 1:],
            "algorithm": algo,
            "visualization_steps": filtered_steps
        }
        
        return {
            "success": True,
            "mission_id": mission_id,
            "visualization": current_step_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Resource Hub Endpoints ====================

@app.get("/api/resources")
async def get_resources():
    """Get all resources."""
    try:
        rm = ResourceManager()
        data = rm.load()
        inventory = rm.get_inventory().to_dict(orient="records")
        summary = rm.get_hub_summary()
        
        return {
            "hub": data.get("hub", {}),
            "inventory": inventory,
            "summary": summary,
            "allocations": data.get("safe_zone_allocations", []),
            "distribution_log": data.get("distribution_log", [])[-50:]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/city/{city_id}/safe-zones")
async def get_safe_zones(city_id: str):
    """Get safe zones for a city."""
    try:
        zones = load_safe_zones(city_id)
        return {"safe_zones": zones}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/resources/dispatch")
async def dispatch_resources(data: ResourceDispatch):
    """Dispatch resources to a safe zone."""
    try:
        rm = ResourceManager()
        zones = load_safe_zones(data.city)
        zone = next((z for z in zones if z["id"] == data.safe_zone_id), None)
        
        if not zone:
            raise HTTPException(status_code=404, detail="Safe zone not found")
        
        alloc = rm.distribute(
            data.resource_id,
            data.quantity,
            data.safe_zone_id,
            zone.get("name", "Unknown"),
            data.city
        )
        
        return {"success": True, "allocation": alloc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/resources/confirm-delivery")
async def confirm_delivery(allocation_id: str, city: str):
    """Confirm resource delivery."""
    try:
        rm = ResourceManager()
        rm.confirm_delivery(allocation_id, city)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/resources/recovery-cycle")
async def run_recovery_cycle(city: str):
    """Run recovery cycle for safe zones."""
    try:
        rm = ResourceManager()
        result = rm.apply_recovery_cycle(city)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/resources/restock")
async def restock_resource(resource_id: str, quantity: int, reason: str = ""):
    """Restock a resource."""
    try:
        rm = ResourceManager()
        rm.restock(resource_id, quantity, reason)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== WebSocket for Real-time Updates ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time algorithm animation updates."""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle different message types
            if data.get("type") == "animation_step":
                # Broadcast animation step to all clients
                for conn in active_connections:
                    await conn.send_json(data)
            elif data.get("type") == "subscribe":
                # Client subscribing to updates
                await websocket.send_json({"status": "subscribed"})
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        if websocket in active_connections:
            active_connections.remove(websocket)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
