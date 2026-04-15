"""Greedy selector for nearest team and priority queue rescue ordering."""
import heapq
from typing import List, Dict, Any

from core.graph_engine import get_adjacency_list_weighted
from core.algorithms.dijkstra import dijkstra


def nearest_team_to_target(G, target_node: str, available_teams: List[Dict], 
                           blocked_edges: set = None, unit_type: str = "ground") -> Dict:
    """
    Find the nearest available team to a target node using Dijkstra.
    
    Args:
        G: NetworkX graph
        target_node: Target node ID
        available_teams: List of available team dicts
        blocked_edges: Set of blocked (u, v) tuples
        unit_type: Team type for edge filtering
    
    Returns:
        Dict with recommended team and distance info
    """
    adj = get_adjacency_list_weighted(G, blocked_edges, unit_type)
    
    best_team = None
    best_distance = float('inf')
    best_path = None
    
    for team in available_teams:
        current_node = team.get("current_node")
        if not current_node:
            continue
        
        result = dijkstra(adj, current_node, target_node)
        
        if result.get("found"):
            distance = result.get("path_cost", float('inf'))
            if distance < best_distance:
                best_distance = distance
                best_team = team
                best_path = result.get("path")
    
    if best_team:
        return {
            "team": best_team,
            "team_name": best_team.get("name"),
            "team_id": best_team.get("id"),
            "distance": best_distance,
            "path": best_path,
            "reason": f"Closest via Dijkstra ({best_distance:.1f} km)"
        }
    
    return {
        "team": None,
        "team_name": None,
        "team_id": None,
        "distance": float('inf'),
        "path": None,
        "reason": "No available team can reach this target"
    }


def highest_resources_team(available_teams: List[Dict]) -> Dict:
    """
    Select team with highest combined resources (fuel + kits).
    
    Args:
        available_teams: List of available team dicts
    
    Returns:
        Dict with recommended team
    """
    if not available_teams:
        return {
            "team": None,
            "team_name": None,
            "reason": "No available teams"
        }
    
    def resource_score(team):
        fuel = team.get("fuel_remaining", 0)
        fuel_cap = team.get("fuel_capacity", 1)
        fuel_pct = fuel / fuel_cap if fuel_cap > 0 else 0
        
        kits = team.get("medical_kits", 0)
        tools = team.get("rescue_tools", 0)
        
        return fuel_pct * 100 + kits + tools
    
    best_team = max(available_teams, key=resource_score)
    
    return {
        "team": best_team,
        "team_name": best_team.get("name"),
        "team_id": best_team.get("id"),
        "reason": f"Highest resources (fuel: {best_team.get('fuel_remaining', 0)}%, kits: {best_team.get('medical_kits', 0)})"
    }


def priority_queue_teams_by_proximity(G, target_node: str, available_teams: List[Dict],
                                       blocked_edges: set = None) -> List[Dict]:
    """
    Use heapq to order teams by proximity to target.
    
    Args:
        G: NetworkX graph
        target_node: Target node ID
        available_teams: List of available team dicts
        blocked_edges: Set of blocked (u, v) tuples
    
    Returns:
        List of teams ordered by distance (closest first)
    """
    heap = []
    adj = get_adjacency_list_weighted(G, blocked_edges, "ground")
    
    for team in available_teams:
        team_type = team.get("type", "ground")
        adj_team = get_adjacency_list_weighted(G, blocked_edges, team_type)
        
        current_node = team.get("current_node")
        if not current_node:
            continue
        
        result = dijkstra(adj_team, current_node, target_node)
        
        if result.get("found"):
            distance = result.get("path_cost", float('inf'))
            heapq.heappush(heap, (distance, team.get("id"), {
                "team": team,
                "team_name": team.get("name"),
                "distance": distance,
                "path": result.get("path")
            }))
    
    ordered = []
    while heap:
        _, _, item = heapq.heappop(heap)
        ordered.append(item)
    
    return ordered
