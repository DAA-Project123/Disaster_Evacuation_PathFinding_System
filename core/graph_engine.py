"""Graph loading and adjacency list management."""
from typing import Any
import json
import networkx as nx


def load_city_graph(filepath: str) -> dict:
    """Load city graph JSON from file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def build_graph(city_graph_data: dict) -> nx.Graph:
    """
    Build networkx Graph from city_map JSON dict.
    Edge weight = base_travel_time_min by default.
    """
    G = nx.Graph()
    for n in city_graph_data.get("nodes", []):
        G.add_node(
            n["id"],
            id=n["id"],
            display_name=n.get("display_name", n["id"]),
            type=n.get("type", "intersection"),
            x=float(n.get("x", 0.0)),
            y=float(n.get("y", 0.0)),
            zone=n.get("zone", ""),
            population_density=int(n.get("population_density", 0)),
            people_stranded=int(n.get("people_stranded", 0)),
            people_rescued=int(n.get("people_rescued", 0)),
            injury_level=n.get("injury_level", "none"),
            survival_chance=float(n.get("survival_chance", 1.0)),
            helipad=bool(n.get("helipad", False)),
            is_safe_zone=bool(n.get("is_safe_zone", False)),
        )
    for e in city_graph_data.get("edges", []):
        u = e["source"]
        v = e["target"]
        G.add_edge(
            u, v,
            road_name=e.get("road_name", f"{u}-{v}"),
            distance_km=float(e.get("distance_km", 1.0)),
            base_travel_time_min=float(e.get("base_travel_time_min", 1.0)),
            capacity=int(e.get("capacity", 4)),
            road_type=e.get("road_type", "road"),
            air_only=bool(e.get("air_only", False)),
            bidirectional=bool(e.get("bidirectional", True)),
            blocked=bool(e.get("blocked", False)),
        )
    return G


def get_positions(city_graph_data: dict) -> dict:
    """Get node positions as {node_id: (x, y)}."""
    return {n["id"]: (float(n.get("x", 0.0)), float(n.get("y", 0.0))) for n in city_graph_data.get("nodes", [])}


def get_node_data(G: nx.Graph, node_id: str) -> dict:
    """Get node metadata."""
    if node_id in G.nodes:
        return dict(G.nodes[node_id])
    return {}


def get_edge_data(G: nx.Graph, u: str, v: str) -> dict:
    """Get edge metadata."""
    if G.has_edge(u, v):
        return dict(G.edges[u, v])
    return {}


def get_adjacency_list_unweighted(G: nx.Graph, blocked_edges: set = None, unit_type: str = "ground") -> dict:
    """
    Get unweighted adjacency list for BFS/DFS.
    
    Args:
        G: NetworkX graph
        blocked_edges: Set of (u, v) tuples representing blocked roads
        unit_type: "ground" (no air edges), "helicopter" (all edges), "mountain_rescue" (blocked edges with penalty)
    
    Returns:
        dict: {node_id: [neighbor_id, ...]}
    """
    blocked = blocked_edges or set()
    adj = {n: [] for n in G.nodes}
    
    for u, v, data in G.edges(data=True):
        # Skip blocked edges for all except mountain_rescue
        if unit_type != "mountain_rescue":
            if (u, v) in blocked or (v, u) in blocked:
                continue
        
        # Ground units can't use air_only edges
        if unit_type == "ground" and data.get("air_only", False):
            continue
        
        adj[u].append(v)
        adj[v].append(u)
    
    return adj


def get_adjacency_list_weighted(G: nx.Graph, blocked_edges: set = None, unit_type: str = "ground") -> dict:
    """
    Get weighted adjacency list for Dijkstra/A*.
    Weight is base_travel_time_min.
    
    Args:
        G: NetworkX graph
        blocked_edges: Set of (u, v) tuples representing blocked roads
        unit_type: "ground" (no air edges), "helicopter" (all edges), "mountain_rescue" (blocked edges * 1.5)
    
    Returns:
        dict: {node_id: [(neighbor_id, weight), ...]}
    """
    blocked = blocked_edges or set()
    adj = {n: [] for n in G.nodes}
    
    for u, v, data in G.edges(data=True):
        base_time = float(data.get("base_travel_time_min", 1.0))
        
        # Check if blocked
        is_blocked = (u, v) in blocked or (v, u) in blocked
        
        if is_blocked:
            if unit_type == "mountain_rescue":
                # Mountain rescue can traverse at 1.5x penalty
                weight = base_time * 1.5
            else:
                # Other units cannot use blocked edges
                continue
        else:
            weight = base_time
        
        # Ground units can't use air_only edges
        if unit_type == "ground" and data.get("air_only", False):
            continue
        
        adj[u].append((v, weight))
        adj[v].append((u, weight))
    
    return adj


def get_safe_zones(G: nx.Graph) -> list:
    """Return list of safe zone node IDs."""
    return [n for n in G.nodes if G.nodes[n].get("is_safe_zone", False)]


def get_nodes_with_disaster(city_graph_data: dict) -> list:
    """Return list of node dicts where people_stranded > 0."""
    return [n for n in city_graph_data.get("nodes", []) if n.get("people_stranded", 0) > 0]


def update_node_stranded(city_graph_data: dict, node_id: str, count: int):
    """Update people_stranded count for a node."""
    for n in city_graph_data.get("nodes", []):
        if n["id"] == node_id:
            n["people_stranded"] = count
            break


def update_node_rescued(city_graph_data: dict, node_id: str, count: int):
    """Update people_rescued count for a node."""
    for n in city_graph_data.get("nodes", []):
        if n["id"] == node_id:
            n["people_rescued"] = count
            n["people_stranded"] = 0
            break


def save_city_graph(city_graph_data: dict, filepath: str):
    """Save city graph to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(city_graph_data, f, indent=2)


def get_all_edges_list(city_graph_data: dict) -> list:
    """Get list of all edges with full data."""
    return city_graph_data.get("edges", [])


def get_blocked_edges_from_data(city_graph_data: dict) -> set:
    """Get set of blocked edges from city data."""
    blocked = set()
    for e in city_graph_data.get("edges", []):
        if e.get("blocked", False):
            blocked.add((e["source"], e["target"]))
            blocked.add((e["target"], e["source"]))
    return blocked
