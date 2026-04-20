"""
Algorithm Visualizer - Provides step-by-step tracking for algorithm animations.
Wraps the algorithm functions to capture exploration steps.
"""
from __future__ import annotations

import heapq
import math
from collections import deque
from typing import Any, Callable

from algorithms.astar import euclidean_distance


def bfs_with_steps(graph: dict, start: str, goal: str) -> dict:
    """BFS with step tracking for visualization."""
    steps = []
    visited_order = []
    
    if start == goal:
        return {"path": [start], "steps": [{"node": start, "type": "goal_found", "path": [start]}], "visited_count": 1}
    
    q = deque([start])
    parent = {start: None}
    visited_order.append(start)
    steps.append({"node": start, "type": "visit", "frontier": list(q)})
    
    while q:
        node = q.popleft()
        for nbr in graph.get(node, []):
            if nbr in parent:
                continue
            parent[nbr] = node
            visited_order.append(nbr)
            steps.append({"node": nbr, "type": "visit", "frontier": list(q) + [nbr], "from": node})
            if nbr == goal:
                path = [goal]
                cur = goal
                while parent[cur] is not None:
                    cur = parent[cur]
                    path.append(cur)
                path.reverse()
                steps.append({"node": goal, "type": "goal_found", "path": path})
                return {"path": path, "steps": steps, "visited_count": len(visited_order)}
            q.append(nbr)
    
    return {"path": None, "steps": steps, "visited_count": len(visited_order)}


def dfs_with_steps(graph: dict, start: str, goal: str) -> dict:
    """DFS with step tracking for visualization."""
    steps = []
    visited_order = []
    
    if start == goal:
        return {"path": [start], "steps": [{"node": start, "type": "goal_found", "path": [start]}], "visited_count": 1}
    
    stack = [(start, [start])]
    visited = {start}
    visited_order.append(start)
    steps.append({"node": start, "type": "visit", "frontier": [s[0] for s in stack]})
    
    while stack:
        node, path_so_far = stack.pop()
        for nbr in graph.get(node, []):
            if nbr == goal:
                final_path = path_so_far + [nbr]
                steps.append({"node": nbr, "type": "goal_found", "path": final_path})
                return {"path": final_path, "steps": steps, "visited_count": len(visited_order)}
            if nbr not in visited:
                visited.add(nbr)
                visited_order.append(nbr)
                stack.append((nbr, path_so_far + [nbr]))
                steps.append({"node": nbr, "type": "visit", "frontier": [s[0] for s in stack], "from": node})
    
    return {"path": None, "steps": steps, "visited_count": len(visited_order)}


def dijkstra_with_steps(graph: dict, start: str, goal: str) -> dict:
    """Dijkstra with step tracking for visualization."""
    steps = []
    visited_order = []
    
    if start == goal:
        return {"path": [start], "steps": [{"node": start, "type": "goal_found", "path": [start], "total_cost": 0.0}], 
                "visited_count": 1, "cost": 0.0}
    
    dist = {start: 0.0}
    parent = {start: None}
    pq = [(0.0, start)]
    visited_order.append(start)
    steps.append({"node": start, "type": "visit", "frontier": [n for _, n in pq], "distance": 0.0})
    
    while pq:
        d, node = heapq.heappop(pq)
        if d != dist.get(node, float('inf')):
            continue
        for nbr, w in graph.get(node, []):
            nd = d + float(w)
            if nd < dist.get(nbr, float('inf')):
                dist[nbr] = nd
                parent[nbr] = node
                if nbr not in visited_order:
                    visited_order.append(nbr)
                    steps.append({"node": nbr, "type": "visit", "distance": nd, 
                                 "frontier": [n for _, n in pq], "from": node})
                if nbr == goal:
                    path = []
                    cur = goal
                    while cur is not None:
                        path.append(cur)
                        cur = parent.get(cur)
                    path.reverse()
                    steps.append({"node": goal, "type": "goal_found", "path": path, "total_cost": nd})
                    return {"path": path, "steps": steps, "visited_count": len(visited_order), "cost": nd}
                heapq.heappush(pq, (nd, nbr))
    
    return {"path": None, "steps": steps, "visited_count": len(visited_order)}


def ucs_with_steps(graph: dict, start: str, goal: str) -> dict:
    """UCS with step tracking for visualization."""
    steps = []
    visited_order = []
    
    if start == goal:
        return {"path": [start], "steps": [{"node": start, "type": "goal_found", "path": [start], "total_cost": 0.0}],
                "visited_count": 1, "cost": 0.0}
    
    frontier = [(0.0, start, [start])]
    explored = set()
    visited_order.append(start)
    steps.append({"node": start, "type": "visit", "frontier": [n for _, n, _ in frontier], "cost": 0.0})
    
    while frontier:
        cost, node, path = heapq.heappop(frontier)
        if node in explored:
            continue
        explored.add(node)
        if node == goal:
            steps.append({"node": goal, "type": "goal_found", "path": path, "total_cost": cost})
            return {"path": path, "steps": steps, "visited_count": len(visited_order), "cost": cost}
        for nbr, w in graph.get(node, []):
            if nbr not in explored:
                if nbr not in visited_order:
                    visited_order.append(nbr)
                    steps.append({"node": nbr, "type": "visit", "cost": cost + float(w),
                                 "frontier": [n for _, n, _ in frontier], "from": node})
                heapq.heappush(frontier, (cost + float(w), nbr, path + [nbr]))
    
    return {"path": None, "steps": steps, "visited_count": len(visited_order)}


def astar_with_steps(graph: dict, start: str, goal: str, positions: dict) -> dict:
    """A* with step tracking for visualization."""
    steps = []
    visited_order = []
    
    if start == goal:
        return {"path": [start], "steps": [{"node": start, "type": "goal_found", "path": [start], "total_cost": 0.0}],
                "visited_count": 1, "cost": 0.0}
    
    def h(n: str) -> float:
        pa = positions.get(n)
        pb = positions.get(goal)
        if pa is None or pb is None:
            return 0.0
        return float(euclidean_distance(pa, pb))
    
    g_score = {start: 0.0}
    parent = {start: None}
    pq = [(h(start), 0.0, start)]
    closed = set()
    visited_order.append(start)
    steps.append({"node": start, "type": "visit", "f_score": h(start), "g_score": 0.0, 
                 "frontier": [n for _, _, n in pq]})
    
    while pq:
        _, g, node = heapq.heappop(pq)
        if node in closed:
            continue
        closed.add(node)
        if node == goal:
            path = []
            cur = goal
            while cur is not None:
                path.append(cur)
                cur = parent.get(cur)
            path.reverse()
            steps.append({"node": goal, "type": "goal_found", "path": path, "total_cost": g})
            return {"path": path, "steps": steps, "visited_count": len(visited_order), "cost": g}
        for nbr, w in graph.get(node, []):
            if nbr in closed:
                continue
            ng = g_score[node] + float(w)
            if ng < g_score.get(nbr, float('inf')):
                g_score[nbr] = ng
                parent[nbr] = node
                f = ng + h(nbr)
                if nbr not in visited_order:
                    visited_order.append(nbr)
                    steps.append({"node": nbr, "type": "visit", "f_score": f, "g_score": ng, 
                                 "h_score": h(nbr), "frontier": [n for _, _, n in pq], "from": node})
                heapq.heappush(pq, (f, ng, nbr))
    
    return {"path": None, "steps": steps, "visited_count": len(visited_order)}


def run_algorithm_with_steps(algorithm: str, graph: dict, start: str, goal: str, positions: dict = None) -> dict:
    """Run any algorithm with step tracking."""
    algorithms = {
        "BFS": bfs_with_steps,
        "DFS": dfs_with_steps,
        "Dijkstra": dijkstra_with_steps,
        "UCS": ucs_with_steps,
        "A*": lambda g, s, go: astar_with_steps(g, s, go, positions or {})
    }
    
    fn = algorithms.get(algorithm)
    if not fn:
        return {"path": None, "steps": [], "visited_count": 0, "error": f"Unknown algorithm: {algorithm}"}
    
    return fn(graph, start, goal)
