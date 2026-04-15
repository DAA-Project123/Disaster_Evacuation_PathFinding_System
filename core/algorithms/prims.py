"""
Prim's Minimum Spanning Tree Algorithm.
Used for: Finding the optimal infrastructure backbone of the city graph.
Academic use: Show which roads form the minimum cost network connecting all nodes.
In rescue context: Used to identify the most critical road infrastructure.
If key MST edges are blocked, show impact on connectivity.
"""
import heapq
import time


def prims_mst(G, weight_attr="distance_km"):
    """
    Prim's algorithm for finding Minimum Spanning Tree.
    
    Args:
        G: NetworkX Graph
        weight_attr: Edge attribute to use for weights
    
    Returns:
        dict: {
            "mst_edges": list[tuple],      # (u, v, weight)
            "total_weight": float,
            "nodes_in_mst": list[str],
            "time_ms": float,
            "algorithm": "Prim's MST"
        }
    """
    start_time = time.perf_counter()
    
    if len(G.nodes()) == 0:
        return {
            "mst_edges": [],
            "total_weight": 0.0,
            "nodes_in_mst": [],
            "time_ms": 0.0,
            "algorithm": "Prim's MST"
        }
    
    nodes = list(G.nodes())
    start_node = nodes[0]
    
    visited = {start_node}
    mst_edges = []
    
    edges = []
    for neighbor in G.neighbors(start_node):
        edge_data = G.get_edge_data(start_node, neighbor)
        weight = edge_data.get(weight_attr, 1)
        heapq.heappush(edges, (weight, start_node, neighbor))
    
    while edges and len(visited) < len(nodes):
        weight, u, v = heapq.heappop(edges)
        
        if v in visited:
            continue
        
        visited.add(v)
        mst_edges.append((u, v, weight))
        
        for neighbor in G.neighbors(v):
            if neighbor not in visited:
                edge_data = G.get_edge_data(v, neighbor)
                w = edge_data.get(weight_attr, 1)
                heapq.heappush(edges, (w, v, neighbor))
    
    elapsed = (time.perf_counter() - start_time) * 1000
    
    return {
        "mst_edges": mst_edges,
        "total_weight": sum(e[2] for e in mst_edges),
        "nodes_in_mst": list(visited),
        "time_ms": elapsed,
        "algorithm": "Prim's MST"
    }


def mst_connectivity_impact(G, mst_result, blocked_edges):
    """
    Given current blocked edges, check how many MST edges are blocked.
    Returns which nodes become disconnected if MST edges are cut.
    Used in disaster_control.py to show infrastructure damage impact.
    
    Args:
        G: NetworkX Graph
        mst_result: Result from prims_mst
        blocked_edges: set of (u, v) tuples (order doesn't matter)
    
    Returns:
        dict: {
            "blocked_mst_edges": list,
            "disconnected_nodes": list[str],
            "connectivity_score": float   # 0.0-1.0 (1.0 = fully connected)
        }
    """
    mst_edges = mst_result.get("mst_edges", [])
    blocked_mst = []
    
    for u, v, w in mst_edges:
        if (u, v) in blocked_edges or (v, u) in blocked_edges:
            blocked_mst.append((u, v, w))
    
    if not blocked_mst:
        return {
            "blocked_mst_edges": [],
            "disconnected_nodes": [],
            "connectivity_score": 1.0
        }
    
    remaining_mst_edges = [e for e in mst_edges if e not in blocked_mst]
    
    if not remaining_mst_edges:
        all_nodes = list(G.nodes())
        return {
            "blocked_mst_edges": blocked_mst,
            "disconnected_nodes": all_nodes[1:] if all_nodes else [],
            "connectivity_score": 0.0
        }
    
    connected = set()
    if remaining_mst_edges:
        connected.add(remaining_mst_edges[0][0])
        for u, v, _ in remaining_mst_edges:
            if u in connected or v in connected:
                connected.add(u)
                connected.add(v)
    
    all_nodes = set(G.nodes())
    disconnected = list(all_nodes - connected)
    connectivity_score = len(connected) / len(all_nodes) if all_nodes else 1.0
    
    return {
        "blocked_mst_edges": blocked_mst,
        "disconnected_nodes": disconnected,
        "connectivity_score": connectivity_score
    }
