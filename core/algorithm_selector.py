"""Algorithm selector for rescue pathfinding."""
import time
import networkx as nx

from core.algorithms.bfs import bfs
from core.algorithms.dfs import dfs
from core.algorithms.dijkstra import dijkstra
from core.algorithms.astar import astar
from core.algorithms.greedy_bfs import greedy_bfs
from core.graph_engine import get_adjacency_list_unweighted, get_adjacency_list_weighted


def _path_uses_air_edges(G, path):
    """Check if path uses any air-only edges."""
    if not path or len(path) < 2:
        return False
    for i in range(len(path) - 1):
        if G.has_edge(path[i], path[i+1]):
            edge_data = G.edges[path[i], path[i+1]]
            if edge_data.get("air_only", False):
                return True
    return False


def _get_node_names(path, G):
    """Get display names for path nodes."""
    if not path:
        return []
    names = []
    for node_id in path:
        node_data = G.nodes.get(node_id, {})
        names.append(node_data.get("display_name", node_id))
    return names


def select_and_run(G, start, goal, disaster_events, positions, city_graph_data, unit_type="ground"):
    """
    Run all 5 pathfinding algorithms (BFS, DFS, Dijkstra, A*, Greedy BFS).
    Select best using composite score.
    
    Args:
        G: NetworkX graph
        start: Starting node
        goal: Target node  
        disaster_events: Dict of node_id -> event dict
        positions: Dict of node_id -> (x, y)
        city_graph_data: Full city graph data
        unit_type: "ground", "helicopter", or "mountain_rescue"
    
    Returns:
        dict: {
            "results": [...],
            "recommended": {...},
            "why_selected": str
        }
    """
    # Get blocked edges from session state or disaster events
    blocked_edges = set()
    for node_id, event in (disaster_events or {}).items():
        if event.get("blocked_edges"):
            for u, v in event.get("blocked_edges", []):
                blocked_edges.add((u, v))
                blocked_edges.add((v, u))
    
    # Get adjacency lists
    adj_unweighted = get_adjacency_list_unweighted(G, blocked_edges, unit_type)
    adj_weighted = get_adjacency_list_weighted(G, blocked_edges, unit_type)
    
    results = []
    algorithms = [
        ("BFS", lambda: bfs(adj_unweighted, start, goal)),
        ("DFS", lambda: dfs(adj_unweighted, start, goal)),
        ("Dijkstra", lambda: dijkstra(adj_weighted, start, goal)),
        ("A*", lambda: astar(adj_weighted, start, goal, positions)),
        ("Greedy BFS", lambda: greedy_bfs(adj_weighted, start, goal, positions)),
    ]
    
    for name, algo_fn in algorithms:
        result = algo_fn()
        
        path = result.get("path")
        found = result.get("found", False)
        nodes_explored = result.get("nodes_explored", 0)
        time_ms = result.get("time_ms", 0.0)
        path_cost = result.get("path_cost", 0.0) if "path_cost" in result else (len(path) - 1 if path else 0)
        
        # Calculate score
        if not found:
            score = 0.0
        else:
            path_length = len(path) - 1 if path else 0
            # Penalize DFS if it explored too many nodes
            dfs_penalty = 1.0
            if name == "DFS":
                # Get Dijkstra's nodes explored for comparison
                dij_result = next((r for r in results if r["algorithm"] == "Dijkstra"), None)
                if dij_result and dij_result.get("nodes_explored", 0) > 0:
                    if nodes_explored > 2 * dij_result["nodes_explored"]:
                        dfs_penalty = 0.5
            
            score = (
                (1.0 / max(nodes_explored, 1) * 0.3) +
                (1.0 / max(path_length, 1) * 0.4) +
                (1.0 / max(time_ms, 0.1) * 0.3)
            ) * dfs_penalty
        
        results.append({
            "algorithm": name,
            "path": path,
            "path_names": _get_node_names(path, G),
            "nodes_explored": nodes_explored,
            "time_ms": time_ms,
            "path_length": len(path) - 1 if path else 0,
            "path_cost": path_cost,
            "found": found,
            "used_air_edges": _path_uses_air_edges(G, path) if path else False,
            "score": score,
            "recommended": False
        })
    
    # Find best algorithm
    found_results = [r for r in results if r["found"]]
    if found_results:
        recommended = max(found_results, key=lambda x: x["score"])
        recommended["recommended"] = True
        
        # Build why_selected explanation
        why_parts = []
        if recommended["algorithm"] == "A*":
            why_parts.append("A* found the optimal path using heuristic guidance")
        elif recommended["algorithm"] == "Dijkstra":
            why_parts.append("Dijkstra found the shortest weighted path")
        elif recommended["algorithm"] == "BFS":
            why_parts.append("BFS found the shortest path in unweighted edges")
        elif recommended["algorithm"] == "Greedy BFS":
            why_parts.append("Greedy BFS found a path quickly using pure heuristic")
        elif recommended["algorithm"] == "DFS":
            why_parts.append("DFS found a valid path through deep exploration")
        
        why_parts.append(f"with {recommended['nodes_explored']} nodes explored")
        why_parts.append(f"and path length {recommended['path_length']}")
        why_selected = " ".join(why_parts) + "."
    else:
        recommended = None
        why_selected = "No path found by any algorithm."
    
    return {
        "results": results,
        "recommended": recommended,
        "why_selected": why_selected
    }
