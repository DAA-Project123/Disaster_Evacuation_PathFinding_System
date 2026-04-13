"""
UCS — Uniform Cost Search. Tree search with explicit frontier/explored.
Identical optimality guarantee to Dijkstra, different implementation.
Time: O((V+E) log V).
"""

import heapq


def ucs(graph: dict, start: str, goal: str, _counter=None) -> tuple[list[str] | None, float]:
    # Min-heap: (cost, node, path)
    # explored set, no re-expansion
    if start == goal:
        return [start], 0.0

    frontier: list[tuple[float, str, list[str]]] = [(0.0, start, [start])]
    explored: set[str] = set()

    while frontier:
        cost, node, path = heapq.heappop(frontier)
        if _counter is not None:
            _counter[0] += 1
        if node in explored:
            continue
        explored.add(node)
        if node == goal:
            return path, float(cost)

        for nbr, w in graph.get(node, []):
            if nbr in explored:
                continue
            heapq.heappush(frontier, (cost + float(w), nbr, path + [nbr]))

    return None, float("inf")
