import heapq
import time
import math


def greedy_bfs(adj_weighted, start, goal, positions):
    """
    Greedy Best-First Search algorithm.
    Uses heuristic only (no g-cost consideration).
    
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
    
    previous = {start: None}
    pq = [(heuristic(start), start)]
    nodes_explored = 0
    visited = {start}
    
    while pq:
        _, current = heapq.heappop(pq)
        nodes_explored += 1
        
        if current == goal:
            path = []
            node = goal
            while node is not None:
                path.append(node)
                node = previous[node]
            path.reverse()
            
            path_cost = 0
            for i in range(len(path) - 1):
                for neighbor, weight in adj_weighted.get(path[i], []):
                    if neighbor == path[i + 1]:
                        path_cost += weight
                        break
            
            elapsed = (time.perf_counter() - start_time) * 1000
            return {
                "path": path,
                "nodes_explored": nodes_explored,
                "time_ms": elapsed,
                "found": True,
                "path_cost": path_cost
            }
        
        for neighbor, _ in adj_weighted.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                previous[neighbor] = current
                heapq.heappush(pq, (heuristic(neighbor), neighbor))
    
    elapsed = (time.perf_counter() - start_time) * 1000
    return {
        "path": None,
        "nodes_explored": nodes_explored,
        "time_ms": elapsed,
        "found": False,
        "path_cost": float('inf')
    }
