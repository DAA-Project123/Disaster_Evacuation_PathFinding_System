# QUICK CHEAT SHEET - DAA Project Viva

## 1-LINER EXPLANATIONS

**BFS:** "Spreads level by level. Finds shortest path in unweighted graphs. O(V+E)."

**DFS:** "Goes deep as possible then backtracks. Also O(V+E) but uses stack, finds any path."

**Dijkstra:** "Greedy selection of minimum distance nodes. Works on weighted graphs. O((V+E)logV)."

**A*:** "Dijkstra with heuristic bonus. f(n) = g(n) + h(n). Same complexity but much faster in practice."

**UCS:** "Like Dijkstra but explores uniform cost. Also O((V+E)logV)."

**Knapsack:** "Dynamic programming. Maximize value within capacity constraint. O(n×W). Selects best victims to rescue."

---

## TIME COMPLEXITY RANKING (Fastest to Slowest on Same Graph)

1. **BFS/DFS:** O(V+E) ← Fastest (but unweighted)
2. **A*:** O(b^d) ← With good heuristic, much faster than theory
3. **Dijkstra/UCS:** O((V+E)logV) ← Same complexity
4. **Knapsack:** O(n×W) ← Depends on capacity, not graph size

---

## WHY EACH ALGORITHM CHOSEN

| Algorithm | Why? |
|-----------|------|
| BFS | Baseline comparison, very fast |
| DFS | Alternative approach, different paths |
| Dijkstra | Guaranteed shortest weighted path |
| A* | Fastest optimal solution for pathfinding |
| UCS | Complete exploration, cost-aware |
| Knapsack | Optimal resource allocation |

---

## WHERE EACH ALGORITHM USED

- **All 5 pathfinding:** `core/algorithm_selector.py` - compares them all
- **BFS:** `algorithms/bfs.py` - unweighted graph search
- **Dijkstra:** `algorithms/dijkstra.py` - weighted shortest path
- **A*:** `algorithms/astar.py` - heuristic pathfinding (PRIMARY)
- **UCS:** `algorithms/ucs.py` - cost-based search
- **Knapsack:** `core/knapsack.py` - victim/resource optimization

---

## REAL-WORLD MAPPING

```
Rescue System          Graph Theory
─────────────         ──────────────
Intersection    →     Node
Road            →     Edge
Travel time     →     Weight
Disaster zone   →     High-cost nodes
Team location   →     Start node
Victim location →     Goal node
Rescue path     →     Optimal path
```

---

## ALGORITHM COMPARISON AT A GLANCE

```
┌────────────┬──────────────┬────────┬─────────┬──────────┐
│ Algorithm  │ Complexity   │ Optimal│ Weighted│ Heuristic│
├────────────┼──────────────┼────────┼─────────┼──────────┤
│ BFS        │ O(V+E)       │ ✓ hops │ ✗       │ ✗        │
│ DFS        │ O(V+E)       │ ✗      │ ✗       │ ✗        │
│ Dijkstra   │ O((V+E)logV) │ ✓      │ ✓       │ ✗        │
│ A*         │ O(b^d)       │ ✓      │ ✓       │ ✓        │
│ UCS        │ O((V+E)logV) │ ✓      │ ✓       │ ✗        │
│ Knapsack   │ O(n×W)       │ ✓ DP   │ N/A     │ N/A      │
└────────────┴──────────────┴────────┴─────────┴──────────┘
```

---

## COMPOSITE SCORING (HOW BEST ALGORITHM SELECTED)

```
Step 1: Run all 5 algorithms
Step 2: Score each on 4 criteria using percentile ranking:
   - Execution time (rank)
   - Path length (rank)
   - Nodes explored (rank)
   - Safety score (rank)
Step 3: Sum all 4 ranks
Step 4: Lowest sum = BEST algorithm
```

**Why?** Balances speed, optimality, and safety instead of just one factor.

---

## KEY OPTIMIZATION TECHNIQUES

1. **Algorithm comparison** → Better paths than any single algorithm
2. **Multi-mode adjacency** → Different optimizations (fastest/safest/balanced)
3. **Risk scoring** → Avoids disaster zones
4. **Knapsack optimization** → Maximizes lives saved per fuel
5. **Dynamic replanning** → Adapts when roads blocked
6. **Greedy team selection** → Nearest team to victim
7. **Atomic file I/O** → Data consistency

---

## DISASTER SYSTEM FLOW

```
User creates disaster
    ↓
Disaster spreads via BFS (radius_hops)
    ↓
All nodes in radius marked as "affected"
    ↓
All edges in radius marked as "blocked"
    ↓
Algorithms penalize these areas heavily (weight = 999999)
    ↓
Paths automatically avoid danger zones
    ↓
If mission uses blocked road → automatic replan
```

---

## FILE ORGANIZATION QUICK REFERENCE

```
algorithms/
├── bfs.py         ← Graph search #1
├── dfs.py         ← Graph search #2  
├── dijkstra.py    ← Shortest path
├── astar.py       ← Heuristic pathfinding (MAIN)
└── ucs.py         ← Uniform cost search

core/
├── algorithm_selector.py    ← RUNS ALL 5 + picks best (heart)
├── graph_engine.py          ← Builds graph from data
├── mission_manager.py       ← Creates/tracks missions
├── disaster_manager.py      ← Risk scores, spreading
├── resource_manager.py      ← Supply distribution
├── knapsack.py              ← Victim/resource optimization
├── dynamic_obstacles.py     ← Live road blocking
├── data_loader.py           ← JSON file I/O
└── greedy_selector.py       ← Team selection

pages/
├── dashboard.py        ← Overview map
├── disaster_control.py ← Create disasters
├── rescue_ops.py       ← Dispatch teams
└── resource_hub.py     ← Manage supplies

data/cities/
├── city_map1.json      ← Graph structure
├── events_*.json       ← Disasters
├── safe_zones_*.json   ← Evacuation points
└── units_*.json        ← Rescue teams
```

---

## COMMON VIVA QUESTIONS - QUICK ANSWERS

**Q: Why 5 algorithms?**
A: "Different scenarios need different approaches. Comparison gives best result. A* is fast, Dijkstra guarantees shortest, DFS is memory efficient, etc."

**Q: A* vs Dijkstra - which is better?**
A: "A* is faster (uses heuristic). Dijkstra is simpler. Both guarantee shortest path. A* is better for this use case."

**Q: Time complexity of your system?**
A: "For 100-200 node city: <50ms (all 5 algorithms run in parallel). A* alone: <10ms. Scales well."

**Q: How does replanning work?**
A: "When road blocked, check active missions. If mission affected → run algorithm selector with blocked road as invalid. Get new path instantly."

**Q: Why Knapsack?**
A: "Limited fuel = can't rescue everyone. Knapsack finds optimal subset: maximize lives saved within fuel capacity. O(n×W) time."

**Q: How do you ensure data consistency?**
A: "Atomic file operations: write to temp file, fsync, atomic move. Prevents corruption if crash during write."

**Q: Pros and cons?**
A: "✅ Multi-algorithm comparison, robust, handles disasters, real-time adaptation. ❌ No persistent database, single-threaded, JSON limitations at scale."

**Q: Can scale to million nodes?**
A: "Yes, with A* + spatial indexing. Skip slower algorithms on large graphs. Tree-based data structures instead of JSON."

---

## PRESENTATION TALKING POINTS

1. **Problem:** Disaster strikes → many people stranded → need optimal rescue routes
2. **Solution:** Model as graph → run 5 algorithms → pick best → real-time adaptation
3. **Key algorithms:** Pathfinding (BFS, DFS, Dijkstra, A*, UCS) + Optimization (Knapsack)
4. **Why A*:** Fastest optimal algorithm for this use case (heuristic pruning)
5. **Why Knapsack:** Limited resources → need optimal victim selection
6. **Architecture:** Streamlit UI → Business logic → Algorithms → Data layer
7. **Optimizations:** Algorithm comparison, risk scoring, dynamic replanning
8. **DevOps:** Dockerized for deployment, Streamlit for rapid prototyping
9. **Complexity:** O(V+E) to O(n×W) depending on algorithm
10. **Real-world impact:** Can reduce response time, save more lives, optimize resources

---

## DEMO SCRIPT (5 minutes)

1. **"Here's the system. Let me show you the city overview."** 
   - Click Dashboard tab → Show 3 maps available

2. **"Let's create a disaster."**
   - Go to Disaster Control → Create earthquake at Node A → Show spreading

3. **"Now let's dispatch a rescue team."**
   - Go to Rescue Operations → Select Team Alpha, target Node C → System shows "A* selected"

4. **"Let me show algorithm comparison."**
   - In algorithm_selector output: show A* vs Dijkstra vs BFS scores

5. **"Now let's block a road."**
   - Block road B-C → Mission automatically replans → Shows "Replanned from 12 to 14 steps"

6. **"The system saved time by using A* with heuristic and adapted when road blocked."**

---

## FINAL CHECKLIST BEFORE VIVA

- [ ] Know all 6 algorithms by heart (1-liner for each)
- [ ] Know complexity of each: O(V+E), O((V+E)logV), O(b^d), O(n×W)
- [ ] Why each chosen: speed, optimality, comparison point
- [ ] Can explain architecture: UI → Logic → Algorithms → Data
- [ ] Can show demo working
- [ ] Understand trade-offs: BFS fast but not optimal, A* slower than BFS but optimal, etc.
- [ ] Know what "composite scoring" means
- [ ] Can explain how replanning works when road blocked
- [ ] Can explain Knapsack victim selection
- [ ] Know what Docker does and why
- [ ] Have example walkthrough: "User clicks dispatch → algorithm selector runs → A* selected → path shown"

---

**YOU'VE GOT THIS! 💪**
