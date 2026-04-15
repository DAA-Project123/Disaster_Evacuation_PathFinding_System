"""Dynamic obstacles - block/unblock roads, check mission impact."""
from typing import List, Dict, Set, Tuple
import networkx as nx


def path_uses_edge(path: List[str], u: str, v: str) -> bool:
    """Check if a path uses a specific edge."""
    if not path or len(path) < 2:
        return False
    for i in range(len(path) - 1):
        if (path[i] == u and path[i+1] == v) or (path[i] == v and path[i+1] == u):
            return True
    return False


def block_road(G: nx.Graph, u: str, v: str) -> bool:
    """
    Block a road in the graph.
    
    Args:
        G: NetworkX graph
        u: Source node
        v: Target node
    
    Returns:
        bool: True if successfully blocked
    """
    if G.has_edge(u, v):
        G.edges[u, v]["blocked"] = True
        return True
    return False


def unblock_road(G: nx.Graph, u: str, v: str) -> bool:
    """
    Unblock a road in the graph.
    
    Args:
        G: NetworkX graph
        u: Source node
        v: Target node
    
    Returns:
        bool: True if successfully unblocked
    """
    if G.has_edge(u, v):
        G.edges[u, v]["blocked"] = False
        return True
    return False


def is_road_blocked(G: nx.Graph, u: str, v: str) -> bool:
    """Check if a road is blocked."""
    if G.has_edge(u, v):
        return G.edges[u, v].get("blocked", False)
    return False


def get_blocked_edges(G: nx.Graph) -> Set[Tuple[str, str]]:
    """Get set of all blocked edges."""
    blocked = set()
    for u, v, data in G.edges(data=True):
        if data.get("blocked", False):
            blocked.add((u, v))
            blocked.add((v, u))  # Add both directions
    return blocked


def get_all_roads(G: nx.Graph) -> List[Dict]:
    """Get list of all roads with their status."""
    roads = []
    seen = set()
    
    for u, v, data in G.edges(data=True):
        edge_key = tuple(sorted([u, v]))
        if edge_key in seen:
            continue
        seen.add(edge_key)
        
        roads.append({
            "source": u,
            "target": v,
            "road_name": data.get("road_name", f"{u}-{v}"),
            "distance_km": data.get("distance_km", 0),
            "blocked": data.get("blocked", False),
            "air_only": data.get("air_only", False),
            "road_type": data.get("road_type", "road")
        })
    
    return roads


def check_mission_impact(active_missions: List[Dict], blocked_u: str, blocked_v: str) -> List[str]:
    """
    Check which active missions are affected by a blocked road.
    
    Args:
        active_missions: List of active mission dicts
        blocked_u: Blocked edge source
        blocked_v: Blocked edge target
    
    Returns:
        List of affected mission IDs
    """
    affected = []
    
    for mission in active_missions:
        if mission.get("status") not in ["en_route", "returning"]:
            continue
        
        phase = mission.get("phase", "outbound")
        path = mission.get("path_to_target", []) if phase == "outbound" else mission.get("return_path", [])
        current_step = mission.get("current_step", 0)
        
        # Check remaining path
        remaining = path[current_step:] if current_step < len(path) else []
        
        if path_uses_edge(remaining, blocked_u, blocked_v):
            affected.append(mission["mission_id"])
    
    return affected


def get_mst_blocked_edges(mst_edges: List[Tuple], blocked_edges: Set[Tuple[str, str]]) -> List[Tuple]:
    """
    Check which MST edges are blocked.
    
    Args:
        mst_edges: List of (u, v, weight) MST edges
        blocked_edges: Set of blocked (u, v) tuples
    
    Returns:
        List of blocked MST edges
    """
    blocked_mst = []
    for u, v, w in mst_edges:
        if (u, v) in blocked_edges or (v, u) in blocked_edges:
            blocked_mst.append((u, v, w))
    return blocked_mst
