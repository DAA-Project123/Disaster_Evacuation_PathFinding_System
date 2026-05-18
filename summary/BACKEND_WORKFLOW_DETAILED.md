# BACKEND WORKFLOW DEEP DIVE - Visual Flow

## REQUEST FLOW: From User Click to Response

```
USER INTERFACE (Streamlit - rescue_ops.py)
═══════════════════════════════════════════════

┌──────────────────────────────────────────────────────┐
│ User selects:                                        │
│  ✓ Team: "Alpha"                                    │
│  ✓ Target: "Node C" (victim location)               │
│  ✓ Clicks: "DISPATCH RESCUE TEAM"                   │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓
BUSINESS LOGIC LAYER (core/mission_manager.py)
═════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────┐
│ mission_manager.create_mission()                    │
│  1. Load city graph from JSON                        │
│  2. Load current disasters                           │
│  3. Call select_and_run() for pathfinding            │
│  4. Create mission object with results              │
│  5. Save to active_missions.json                    │
│  6. Update team status to "dispatched"              │
│  7. Log to rescue_log.csv                           │
│  8. Return mission object to UI                     │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓
ALGORITHM SELECTION LAYER (core/algorithm_selector.py)
════════════════════════════════════════════════════════════

select_and_run(Graph, StartNode, GoalNode, DisasterEvents, Positions)
│
├─→ Load city graph via graph_engine.load_graph()
│   Returns: NetworkX graph with nodes and edges
│
├─→ Create 3 ADJACENCY LISTS (different weightings):
│   ├─ "fastest":  weight = base_time × congestion_factor
│   ├─ "safest":   weight = base_time + (risk_score × 100)
│   └─ "balanced": weight = 0.5×time + 0.3×risk + 0.2×distance
│
├─→ RUN ALL 5 ALGORITHMS IN SEQUENCE:
│   │
│   ├─ BFS (unweighted)
│   │  Input: adj_unweighted, start, goal
│   │  Output: [path], execution_time
│   │  Example: ["BaseNode", "Node_A", "Node_B", "Node_C"] (victim)
│   │
│   ├─ DFS (unweighted)
│   │  Input: adj_unweighted, start, goal
│   │  Output: [path], execution_time
│   │
│   ├─ Dijkstra (weighted, balanced mode)
│   │  Input: adj_weighted (balanced), start, goal
│   │  Output: [path, total_cost], execution_time
│   │  Cost = sum of edge weights = total travel time
│   │
│   ├─ A* (weighted safest mode, with heuristic)
│   │  Input: adj_safest, start, goal, euclidean_distance, positions
│   │  Output: [path, total_cost], execution_time
│   │  Heuristic = straight-line distance to goal
│   │
│   └─ UCS (weighted, balanced mode)
│      Input: adj_weighted (balanced), start, goal
│      Output: [path, total_cost], execution_time
│
├─→ SCORE EACH RESULT on 4 Criteria:
│   │
│   For each algorithm result:
│   ├─ Calculate path_length (number of edges)
│   ├─ Count nodes_explored (visited nodes)
│   ├─ Measure execution_time_ms (wall-clock time)
│   ├─ Compute safety_score (1 - avg_risk_on_path)
│   │
│   Then RANK each criterion:
│   ├─ execution_time: rank 1-5 (1=fastest)
│   ├─ path_length: rank 1-5 (1=shortest)
│   ├─ nodes_explored: rank 1-5 (1=fewest)
│   ├─ safety_score: rank 1-5 (1=safest)
│   │
│   Composite Score = sum of 4 ranks
│   (Lower score = better overall)
│
└─→ SELECT BEST ALGORITHM
    │
    ├─ Pick result with LOWEST composite score
    ├─ This is the algorithm that balances ALL factors
    └─ Return: {algorithm: "A*", path: [...], why_selected: "..."}

EXAMPLE RESULTS:
═════════════════════════════════════════════════════════════════

BFS:       Time=5ms, PathLen=8, Nodes=20, Safety=0.4 → Composite=18
DFS:       Time=4ms, PathLen=10, Nodes=25, Safety=0.3 → Composite=20
Dijkstra:  Time=8ms, PathLen=7, Nodes=15, Safety=0.6 → Composite=16 ← WINNER
A*:        Time=6ms, PathLen=7, Nodes=12, Safety=0.65 → Composite=15 ← BETTER
UCS:       Time=9ms, PathLen=7, Nodes=14, Safety=0.6 → Composite=17

SELECTED: A* (path via nodes 0→2→4→5→6 (victim), safety score 0.65)

BACK TO MISSION MANAGER (core/mission_manager.py)
═════════════════════════════════════════════════════════

mission = {
    "mission_id": "M1734567890",
    "team_id": "ALPHA",
    "target_node": "Node_C",
    "path": ["Base", "Node_A", "Node_B", "Node_C"],  ← FROM A*
    "algorithm_used": "A*",
    "why_selected": "Best balance of speed & safety",
    "path_length": 3,
    "nodes_explored": 12,
    "time_ms": 6.2,
    "safety_score": 0.65,
    "status": "en_route",
    "current_step": 0,
    "people_at_target": 5,
    "injury_level": "high"
}

SAVE MISSION:
├─ Write to data/active_missions.json
├─ Update Team Alpha status: "dispatched"
├─ Log to data/rescue_log.csv:
│  "M1734567890,2024-01-20T10:30:00,Map1,ALPHA,AlphaTeam,
│   Ground,Base,Node_C,A*,3,12,6.2,5,10,en_route"
└─ Reset UI

BACK TO FRONTEND (Streamlit - rescue_ops.py)
═══════════════════════════════════════════════════

Display to User:
┌──────────────────────────────────────────────────────┐
│ ✓ Mission Created: M1734567890                      │
│ ✓ Algorithm: A* (balanced safety vs speed)          │
│ ✓ Path: Base → Node_A → Node_B → Node_C (victim)  │
│ ✓ Steps: 3 legs                                     │
│ ✓ Estimated Time: 6.2 minutes                       │
│ ✓ Safety Score: 0.65 (good)                        │
│ ✓ Status: Team dispatched, en_route                │
│                                                      │
│ [Advance Step] [Auto-Play] [Replan] [Block Road]  │
└──────────────────────────────────────────────────────┘

   ↓ (Shows map with path highlighted)

   ┌─────────────────────────────────────────────────────┐
   │        CITY MAP (Plotly visualization)             │
   │                                                     │
   │   [Base]────[A]────[B]────[C]victim               │
   │      ●──────●────────●────────●                  │
   │      Visited Remaining                            │
   │   (green)   (blue)                                │
   └─────────────────────────────────────────────────────┘

REAL-TIME MISSION TRACKING
═════════════════════════════════════════════════════════

Scenario: User clicks "Advance Step"
│
├─→ mission_manager.advance_step(mission_id)
│   ├─ current_step: 0 → 1 (Team moves Base → Node_A)
│   ├─ Update mission JSON
│   ├─ Broadcast to UI
│   └─ Team still en_route
│
├─→ User clicks "Advance Step" again
│   ├─ current_step: 1 → 2 (Team moves Node_A → Node_B)
│   ├─ Update mission JSON
│   └─ Team still en_route
│
├─→ User clicks "Advance Step" again
│   ├─ current_step: 2 → 3 (Team moves Node_B → Node_C)
│   ├─ current_step == len(path) - 1 (reached goal!)
│   ├─ mission["status"] = "arrived"
│   ├─ mission["arrived_at"] = current_timestamp
│   └─ UI now shows "Confirm Rescue" button
│
└─→ User clicks "Confirm Rescue"
    ├─ mission_manager.confirm_rescue(mission_id, people_rescued=5)
    ├─ mission["status"] = "rescued"
    ├─ mission["phase"] = "to_safe_zone"
    ├─ knapsack optimization runs (if multiple victims)
    ├─ Select best victims to rescue with fuel available
    ├─ resource_manager allocates supplies if needed
    └─ Mission phase 2 starts: return to safe zone

Return Trip (Phase 2)
│
├─→ algorithm_selector runs again (route to nearest safe zone)
├─→ Select best algorithm for return path
├─→ Team advances step by step on return path
├─→ When arrives at safe zone: status = "complete"
└─→ Mission logged with statistics:
    {
      "mission_id": "M1734567890",
      "duration_minutes": 42,
      "people_rescued": 5,
      "algorithm_used": "A*",
      "total_distance": 15.3,
      "fuel_used": 12.4,
      "status": "complete"
    }

EXCEPTION HANDLING: Road Blocked Mid-Mission
══════════════════════════════════════════════════

Scenario: User blocks road "B-C" while team at Node_A
│
├─→ dynamic_obstacles.block_road_live(G, "B", "C", active_missions)
│   ├─ Check all active missions
│   ├─ Find missions that USE edge B-C on remaining path
│   ├─ Identify affected missions (this one!)
│   └─ Return: {"blocked": ("B", "C"), "affected_missions": [M1734567890]}
│
├─→ IF mission affected:
│   ├─ mission_manager.replan_mission(mission_id)
│   ├─ Call algorithm_selector AGAIN with blocked_edge marked invalid
│   │  (weight = 999999 on edge B-C)
│   ├─ Get new path: Base → Node_A → Node_D → Node_C
│   ├─ Update mission:
│   │  {old_path: [...B-C...], new_path: [...D...], replanned: True}
│   ├─ Show user: "Path replanned from 3 steps via A* to 4 steps via Dijkstra"
│   └─ Team continues on new route
│
└─→ Automatic adaptation complete!

DATA PERSISTENCE LAYER
═══════════════════════════════════════════════════════

All data saved in JSON files:

1. CITY GRAPH STORAGE (data/cities/city_map1.json):
   {
     "nodes": [
       {"id": "Base", "x": 0, "y": 0, "name": "Rescue Base"},
       {"id": "Node_A", "x": 1, "y": 1, ...},
       ...
     ],
     "edges": [
       {"source": "Base", "target": "Node_A", 
        "distance_km": 1.5, "base_travel_time_min": 2.0, ...},
       ...
     ]
   }

2. MISSION TRACKING (data/active_missions.json):
   {"missions": [
     {mission object with current step, status, path, etc},
     ...
   ]}

3. DISASTER EVENTS (data/cities/events_map1.json):
   [
     {
       "event_id": "EVT-001",
       "type": "earthquake",
       "severity": "high",
       "affected_nodes": ["Node_B", "Node_C"],
       "blocked_edges": [["Node_B", "Node_C"], ["Node_C", "Node_E"]],
       "active": true
     }
   ]

4. LOGS (data/rescue_log.csv):
   mission_id,timestamp,team_id,target_node,algorithm,
   path_length,people_rescued,fuel_used,status
   M1734567890,2024-01-20T10:30:00,ALPHA,Node_C,A*,3,5,12.4,complete

ATOMIC FILE OPERATIONS (core/data_loader.py)
════════════════════════════════════════════════

To prevent data corruption if system crashes:

def _atomic_write_json(path, data):
    1. Create temporary file in same directory
    2. Write JSON data to temp file
    3. Flush to disk (fsync)
    4. Atomically move temp → real file
    5. If error: delete temp file
    
This ensures JSON is never partially written!

SUMMARY OF BACKEND FLOW
═════════════════════════════════════════════════════════

User Request
    ↓
Load data from JSON
    ↓
Run all 5 algorithms
    ↓
Compare & score results
    ↓
Select best algorithm
    ↓
Create mission object
    ↓
Save mission to JSON (atomic)
    ↓
Log to CSV
    ↓
Return to UI
    ↓
UI displays mission & path
    ↓
User advances steps
    ↓
Mission state updates
    ↓
When complete: log statistics
    ↓
System ready for next mission
```

---

## ALGORITHM EXECUTION DETAILS

### A* ALGORITHM STEP-BY-STEP

```
START: Base, GOAL: Node_C

INITIALIZATION:
├─ g_score["Base"] = 0
├─ h("Base") = euclidean_distance(Base, Node_C) = 5.2
├─ f("Base") = 0 + 5.2 = 5.2
├─ priority_queue = [(5.2, "Base")]
└─ closed_set = {}

ITERATION 1:
├─ Pop min from queue: "Base" (f=5.2)
├─ Mark "Base" as closed
├─ Explore neighbors: [Node_A, Node_X]
│
├─ For Node_A:
│  ├─ g_score["Node_A"] = g["Base"] + weight(Base, A) = 0 + 2.0 = 2.0
│  ├─ h("Node_A") = euclidean_distance(A, Node_C) = 4.1
│  ├─ f("Node_A") = 2.0 + 4.1 = 6.1
│  └─ Add (6.1, "Node_A") to queue
│
├─ For Node_X:
│  ├─ g_score["Node_X"] = 0 + 5.0 = 5.0
│  ├─ h("Node_X") = 8.0 (far from goal)
│  ├─ f("Node_X") = 5.0 + 8.0 = 13.0
│  └─ Add (13.0, "Node_X") to queue

ITERATION 2:
├─ Pop min from queue: "Node_A" (f=6.1)
├─ Mark "Node_A" as closed
├─ Explore neighbors: [Base (closed), Node_B]
│
├─ For Node_B:
│  ├─ g_score["Node_B"] = 2.0 + 2.5 = 4.5
│  ├─ h("Node_B") = 2.8
│  ├─ f("Node_B") = 4.5 + 2.8 = 7.3
│  └─ Add (7.3, "Node_B") to queue

ITERATION 3:
├─ Pop min from queue: "Node_B" (f=7.3)
├─ Mark "Node_B" as closed
├─ Explore neighbors: [Node_A (closed), Node_C]
│
├─ For Node_C:
│  ├─ g_score["Node_C"] = 4.5 + 2.0 = 6.5
│  ├─ h("Node_C") = 0 (AT GOAL!)
│  ├─ f("Node_C") = 6.5 + 0 = 6.5
│  ├─ Add (6.5, "Node_C") to queue

ITERATION 4:
├─ Pop min from queue: "Node_C" (f=6.5)
├─ Node_C == Goal → FOUND!
├─ Reconstruct path:
│  ├─ parent["Node_C"] = "Node_B"
│  ├─ parent["Node_B"] = "Node_A"
│  ├─ parent["Node_A"] = "Base"
│  └─ Path: ["Base", "Node_A", "Node_B", "Node_C"]
└─ Return: [path, total_cost=6.5]

KEY INSIGHT:
A* explored only 4 nodes (Base, A, B, C) with heuristic guidance.
Dijkstra might have explored 15+ nodes before finding goal!
Heuristic saved time by pointing toward Node_C.
```

---

## KNAPSACK OPTIMIZATION EXAMPLE

```
Scenario: Multiple victims at Node_C, but fuel limited to 20 units

VICTIMS AT NODE_C:
┌────────────────────────────────────────────────────────────┐
│ Victim │ Rescue_Cost │ Injury_Level │ People │ Rescue_Value │
├────────┼─────────────┼──────────────┼────────┼──────────────┤
│ V1     │ 5           │ Critical     │ 1      │ 5.0          │
│ V2     │ 6           │ High         │ 3      │ 7.2          │
│ V3     │ 4           │ Low          │ 2      │ 2.1          │
│ V4     │ 8           │ Critical     │ 1      │ 5.5          │
│ V5     │ 3           │ Medium       │ 1      │ 1.8          │
└────────┴─────────────┴──────────────┴────────┴──────────────┘

KNAPSACK DP TABLE (capacity = 20):
(Rows = victims, Columns = fuel capacity)

       0   1   2   3   4   5   6   ...  20
     ┌───┬───┬───┬───┬───┬───┬───┬────┬───┐
  0  │ 0 │ 0 │ 0 │ 0 │ 0 │ 0 │ 0 │    │ 0 │
  1  │ 0 │ 0 │ 0 │ 0 │ 0 │ 5 │ 5 │    │ 5 │ (V1: cost=5, value=5)
  2  │ 0 │ 0 │ 0 │ 0 │ 0 │ 5 │ 6 │    │12 │ (V2: cost=6, value=7.2)
  3  │ 0 │ 0 │ 0 │ 0 │ 2 │ 5 │ 6 │    │12 │ (V3: cost=4, value=2.1)
  4  │ 0 │ 0 │ 0 │ 0 │ 2 │ 5 │ 6 │    │12 │ (V4: cost=8, value=5.5)
  5  │ 0 │ 0 │ 0 │ 1 │ 2 │ 5 │ 6 │    │13 │ (V5: cost=3, value=1.8)
     └───┴───┴───┴───┴───┴───┴───┴────┴───┘

DP[5][20] = 13 (maximum rescue value with 20 fuel)

TRACEBACK (which victims to rescue?):
├─ At DP[5][20]=13: Did we include V5?
│  ├─ Check: DP[4][20] vs DP[4][20-3] + value(V5)
│  ├─ 12 vs (9 + 1.8) = 12 vs 10.8
│  ├─ Took from row above → V5 NOT included
│
├─ At DP[4][20]=12: Did we include V4?
│  ├─ Check: DP[3][20] vs DP[3][20-8] + value(V4)
│  ├─ 12 vs (7.2 + 5.5) = 12 vs 12.7
│  ├─ Took from row above → V4 NOT included
│
├─ At DP[3][20]=12: Did we include V3?
│  ├─ Check: DP[2][20] vs DP[2][20-4] + value(V3)
│  ├─ 12 vs (12 + 2.1) = 12 vs 14.1
│  ├─ Took from row above → V3 NOT included
│
├─ At DP[2][20]=12: Did we include V2?
│  ├─ Check: DP[1][20] vs DP[1][20-6] + value(V2)
│  ├─ 5 vs (5 + 7.2) = 5 vs 12.2
│  ├─ TOOK V2! (fuel left: 20-6=14)
│
└─ At DP[1][14]=5: Did we include V1?
   ├─ Check: DP[0][14] vs DP[0][14-5] + value(V1)
   ├─ 0 vs (0 + 5) = 0 vs 5
   ├─ TOOK V1! (fuel left: 14-5=9)

RESULT:
├─ Selected Victims: V1, V2
├─ Total Rescue Value: 5 + 7.2 = 12.2
├─ Total Fuel Cost: 5 + 6 = 11 (out of 20)
├─ Not Selected: V3, V4, V5
│  ├─ V3: low value (2.1) despite low cost
│  ├─ V4: high cost (8) for medium value (5.5)
│  ├─ V5: low value (1.8) doesn't help

EXPLANATION:
Rescue V1 (critical, 1 person) + V2 (high, 3 people) = maximize 4 lives
Skip V4 (critical but only 1 person, expensive)
Skip V3 (low injury, few people)
Skip V5 (low value)
```

---

That's the complete flow! The system chains all these components together for real-time disaster rescue optimization.
