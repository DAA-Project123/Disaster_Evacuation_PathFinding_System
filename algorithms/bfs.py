"""
BFS — shortest path in unweighted graphs.
Time: O(V+E), Space: O(V). Optimal for unweighted.
"""

from collections import deque


def bfs(graph: dict, start: str, goal: str, _counter=None) -> list[str] | None:
    # deque-based BFS, returns path or None
    if start == goal:
        return [start]

    q = deque([start])
    parent: dict[str, str | None] = {start: None}

    while q:
        node = q.popleft()
        if _counter is not None:
            _counter[0] += 1
        for nbr in graph.get(node, []):
            if nbr in parent:
                continue
            parent[nbr] = node
            if nbr == goal:
                # Reconstruct
                path = [goal]
                cur: str | None = goal
                while cur is not None:
                    cur = parent[cur]
                    if cur is not None:
                        path.append(cur)
                return list(reversed(path))
            q.append(nbr)

    return None