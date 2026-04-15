import heapq
import time


def dijkstra(adj_weighted, start, goal):
    """
    Dijkstra's algorithm for finding shortest path in weighted graph.
    
    Args:
        adj_weighted: Adjacency list {node: [(neighbor, weight), ...]}
        start: Starting node
        goal: Target node
    
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
    
    distances = {start: 0}
    previous = {}
    pq = [(0, start)]
    nodes_explored = 0
    visited = set()
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
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
                "path_cost": current_dist
            }
        
        for neighbor, weight in adj_weighted.get(current, []):
            if neighbor not in visited:
                new_dist = current_dist + weight
                if neighbor not in distances or new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    heapq.heappush(pq, (new_dist, neighbor))
    
    elapsed = (time.perf_counter() - start_time) * 1000
    return {
        "path": None,
        "nodes_explored": nodes_explored,
        "time_ms": elapsed,
        "found": False,
        "path_cost": float('inf')
    }
