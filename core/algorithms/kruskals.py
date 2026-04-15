"""
Kruskal's Minimum Spanning Tree Algorithm.
Used for: Same as Prim's but demonstrates different approach (union-find).
Academic comparison: Show Prim's vs Kruskal's on same graph.
Additional use: Identify minimum cost evacuation network.
"""
import time


class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}
    
    def make_set(self, x):
        self.parent[x] = x
        self.rank[x] = 0
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False
        
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        return True


def kruskals_mst(G, weight_attr="distance_km"):
    """
    Kruskal's algorithm for finding Minimum Spanning Tree using union-find.
    
    Args:
        G: NetworkX Graph
        weight_attr: Edge attribute to use for weights
    
    Returns:
        dict: {
            "mst_edges": list[tuple],      # (u, v, weight)
            "total_weight": float,
            "nodes_in_mst": list[str],
            "time_ms": float,
            "algorithm": "Kruskal's MST",
            "union_find_steps": int
        }
    """
    start_time = time.perf_counter()
    
    if len(G.nodes()) == 0:
        return {
            "mst_edges": [],
            "total_weight": 0.0,
            "nodes_in_mst": [],
            "time_ms": 0.0,
            "algorithm": "Kruskal's MST",
            "union_find_steps": 0
        }
    
    edges = []
    for u, v, data in G.edges(data=True):
        weight = data.get(weight_attr, 1)
        edges.append((weight, u, v))
    
    edges.sort(key=lambda x: x[0])
    
    uf = UnionFind()
    for node in G.nodes():
        uf.make_set(node)
    
    mst_edges = []
    union_steps = 0
    
    for weight, u, v in edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            mst_edges.append((u, v, weight))
            union_steps += 1
            
            if len(mst_edges) == len(G.nodes()) - 1:
                break
    
    nodes_in_mst = set()
    for u, v, _ in mst_edges:
        nodes_in_mst.add(u)
        nodes_in_mst.add(v)
    
    elapsed = (time.perf_counter() - start_time) * 1000
    
    return {
        "mst_edges": mst_edges,
        "total_weight": sum(e[2] for e in mst_edges),
        "nodes_in_mst": list(nodes_in_mst),
        "time_ms": elapsed,
        "algorithm": "Kruskal's MST",
        "union_find_steps": union_steps
    }


def compare_mst_algorithms(G, weight_attr="distance_km"):
    """
    Run both Prim's and Kruskal's, return comparison for display.
    
    Args:
        G: NetworkX Graph
        weight_attr: Edge attribute to use for weights
    
    Returns:
        dict: {
            "prims": prims_result,
            "kruskals": kruskals_result,
            "same_total_weight": bool,
            "time_diff_ms": float
        }
    """
    from .prims import prims_mst
    
    prims_result = prims_mst(G, weight_attr)
    kruskals_result = kruskals_mst(G, weight_attr)
    
    same_weight = abs(prims_result["total_weight"] - kruskals_result["total_weight"]) < 0.001
    time_diff = abs(prims_result["time_ms"] - kruskals_result["time_ms"])
    
    return {
        "prims": prims_result,
        "kruskals": kruskals_result,
        "same_total_weight": same_weight,
        "time_diff_ms": time_diff
    }
