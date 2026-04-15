import heapq
import time
import math


def astar(adj_weighted, start, goal, positions):
    """
    A* algorithm for finding shortest path using heuristic.
    
    Args:
        adj_weighted: Adjacency list {node: [(neighbor, weight), ...]}
        start: Starting node
        goal: Target node
        positions: dict of {node_id: (x, y)} for heuristic calculation
    
    Returns:
        dict: {
            "path": list[str] | None,
            "nodes_explored": int,
            "time_ms": float,
            "found": bool,
            "path_cost": float
        }
    """
    start_time = time.perf_counter()
    
    if start == goal:
        return {
            "path": [start],
            "nodes_explored": 1,
            "time_ms": 0.0,
            "found": True,
            "path_cost": 0.0
        }
    
    def heuristic(node):
        if node not in positions or goal not in positions:
            return 0
        x1, y1 = positions[node]
        x2, y2 = positions[goal]
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2) * 10
    
    g_scores = {start: 0}
    f_scores = {start: heuristic(start)}
    previous = {}
    pq = [(f_scores[start], start)]
    nodes_explored = 0
    visited = set()
    
    while pq:
        current_f, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        visited.add(current)
        nodes_explored += 1
        
        if current == goal:
            path = []
            node = goal
            while node in previous:
                path.append(node)
                node = previous[node]
            path.append(start)
            path.reverse()
            elapsed = (time.perf_counter() - start_time) * 1000
            return {
                "path": path,
                "nodes_explored": nodes_explored,
                "time_ms": elapsed,
                "found": True,
                "path_cost": g_scores[goal]
            }
        
        for neighbor, weight in adj_weighted.get(current, []):
            if neighbor not in visited:
                tentative_g = g_scores[current] + weight
                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    previous[neighbor] = current
                    g_scores[neighbor] = tentative_g
                    f_scores[neighbor] = tentative_g + heuristic(neighbor)
                    heapq.heappush(pq, (f_scores[neighbor], neighbor))
    
    elapsed = (time.perf_counter() - start_time) * 1000
    return {
        "path": None,
        "nodes_explored": nodes_explored,
        "time_ms": elapsed,
        "found": False,
        "path_cost": float('inf')
    }
