from collections import deque
import time


def bfs(adj, start, goal):
    """
    Breadth-First Search algorithm.
    
    Args:
        adj: Adjacency list {node: [neighbor, ...]}
        start: Starting node
        goal: Target node
    
    Returns:
        dict: {
            "path": list[str] | None,
            "nodes_explored": int,
            "time_ms": float,
            "found": bool
        }
    """
    start_time = time.perf_counter()
    
    if start == goal:
        return {
            "path": [start],
            "nodes_explored": 1,
            "time_ms": 0.0,
            "found": True
        }
    
    visited = {start}
    queue = deque([(start, [start])])
    nodes_explored = 1
    
    while queue:
        current, path = queue.popleft()
        
        for neighbor in adj.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                nodes_explored += 1
                new_path = path + [neighbor]
                
                if neighbor == goal:
                    elapsed = (time.perf_counter() - start_time) * 1000
                    return {
                        "path": new_path,
                        "nodes_explored": nodes_explored,
                        "time_ms": elapsed,
                        "found": True
                    }
                
                queue.append((neighbor, new_path))
    
    elapsed = (time.perf_counter() - start_time) * 1000
    return {
        "path": None,
        "nodes_explored": nodes_explored,
        "time_ms": elapsed,
        "found": False
    }
