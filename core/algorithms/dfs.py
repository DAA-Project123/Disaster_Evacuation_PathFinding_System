import time


def dfs(adj, start, goal):
    """
    Depth-First Search algorithm.
    
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
    
    visited = set()
    nodes_explored = 0
    
    def dfs_recursive(current, path):
        nonlocal nodes_explored
        visited.add(current)
        nodes_explored += 1
        
        if current == goal:
            return path
        
        for neighbor in adj.get(current, []):
            if neighbor not in visited:
                result = dfs_recursive(neighbor, path + [neighbor])
                if result is not None:
                    return result
        
        return None
    
    result_path = dfs_recursive(start, [start])
    elapsed = (time.perf_counter() - start_time) * 1000
    
    return {
        "path": result_path,
        "nodes_explored": nodes_explored,
        "time_ms": elapsed,
        "found": result_path is not None
    }
