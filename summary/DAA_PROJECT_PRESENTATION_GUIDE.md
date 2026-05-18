# DAA Project: Disaster Evacuation Pathfinding System
## Complete Presentation & Viva Guide

---

## 1. PROJECT FOLDER STRUCTURE & PURPOSE

```
Disaster_Evacuation_PathFinding_System/
│
├── app.py                          # Main Streamlit entry point - UI controller
├── requirements.txt                # Python dependencies (streamlit, networkx, pandas, etc.)
├── Dockerfile                      # Docker containerization for deployment
│
├── algorithms/                     # CORE: DAA ALGORITHM IMPLEMENTATIONS
│   ├── astar.py                   # A* algorithm (heuristic pathfinding)
│   ├── bfs.py                     # BFS algorithm (unweighted search)
│   ├── dfs.py                     # DFS algorithm (alternative exploration)
│   ├── dijkstra.py                # Dijkstra (weighted shortest path)
│   └── ucs.py                     # Uniform Cost Search (cost-based)
│
├── core/                          # MAIN BUSINESS LOGIC
│   ├── algorithm_selector.py      # Selects & runs all 5 algorithms, scores best path
│   ├── graph_engine.py            # NetworkX graph operations (loads city map)
│   ├── disaster_manager.py        # Manages disasters, calculates risk scores
│   ├── mission_manager.py         # Creates, tracks, and replans missions
│   ├── resource_manager.py        # Distributes supplies to safe zones
│   ├── dynamic_obstacles.py       # Handles live road blockages
│   ├── knapsack.py                # 0/1 Knapsack (victim/resource optimization)
│   ├── greedy_selector.py         # Nearest team selection logic
│   └── data_loader.py             # JSON file I/O operations
│
├── pages/                         # FRONTEND PAGES (Streamlit multi-page)
│   ├── dashboard.py               # Real-time city overview with map visualization
│   ├── disaster_control.py        # Create/manage disasters and blockages
│   ├── rescue_ops.py              # Mission dispatch & real-time tracking
│   └── resource_hub.py            # Resource distribution interface
│
├── utils/                         # UTILITY FUNCTIONS
│   └── visualizer.py              # Plotly map rendering (displays paths, blocked roads)
│
└── data/                          # DATA STORAGE (JSON files + CSV logs)
    ├── active_missions.json       # Current missions in progress
    ├── rescue_log.csv             # Historical rescue records
    ├── resources.json             # Central resource inventory
    └── cities/
        ├── city_map1/2/3.json     # City graph structure (nodes, edges, coordinates)
        ├── events_*.json          # Disaster events for each city
        ├── safe_zones_*.json      # Safe zone capacity & resources
        ├── zones_*.json           # Evacuation zone definitions
        ├── units_*.json           # Rescue team configurations
        └── units_*.json           # Unit specifications
```

### **Simple Summary:**
- **algorithms/** = Heart of project (5 pathfinding algorithms)
- **core/** = Logic that uses algorithms (selects best one, manages missions)
- **pages/** = User interface (4 different screens)
- **data/** = All information stored (cities, missions, resources)

---

## 2. MAIN DAA ALGORITHMS LOCATION & PURPOSE

| Algorithm | File | Used For | Type |
|-----------|------|----------|------|
| **BFS** | algorithms/bfs.py | Quick unweighted paths | Graph Search |
| **DFS** | algorithms/dfs.py | Alternative exploration | Graph Search |
| **Dijkstra** | algorithms/dijkstra.py | Optimal weighted paths | Shortest Path |
| **A*** | algorithms/astar.py | Fast heuristic pathfinding | Heuristic Search |
| **UCS** | algorithms/ucs.py | Cost-aware exploration | Graph Search |
| **Knapsack 0/1** | core/knapsack.py | Best victim/resource selection | Optimization |

---

## 3. DETAILED ALGORITHM ANALYSIS

### **Algorithm 1: A* (A-Star) Search**

**Location:** `algorithms/astar.py`

**Where Used in Project:**
- Primary algorithm for rescue team pathfinding
- Selected by `algorithm_selector.py` for multi-criteria scoring
- Uses euclidean distance heuristic to nearest safe zone

**Why This Algorithm Was Chosen:**
- ✅ Faster than Dijkstra (uses heuristic)
- ✅ Guarantees shortest path (if heuristic is admissible)
- ✅ Good for real-time rescue (balances speed & optimality)
- ✅ Handles weighted edges (dangerous roads have higher cost)

**Time Complexity:** 
- **Average:** O(b^d) where b=branching factor, d=depth
- **Worst Case:** O(n log n) with proper priority queue
- **In Practice:** Much faster than Dijkstra for this use case

**Space Complexity:** O(n) for storing visited nodes

**Real-World Explanation (Simple):**
Imagine you're navigating to a hospital during a disaster. Instead of checking every street (Dijkstra), A* is like using GPS - you know where the hospital is, so you prioritize roads that point toward it. When a road is blocked, it recalculates quickly using remaining distance.

**Flow of Execution:**
1. Start at rescue team's location
2. Calculate f(n) = g(n) + h(n)
   - g(n) = actual distance traveled
   - h(n) = euclidean distance to goal (heuristic)
3. Always explore node with smallest f(n) first
4. Mark visited nodes to avoid loops
5. Reconstruct path when goal reached
6. Return [path, total_cost]

**Code Example Logic:**
```python
def astar(graph, start, goal, heuristic, positions):
    # g_score = actual distance from start
    # h(n) = estimated distance to goal using heuristic
    # Always pick node with lowest g(n) + h(n)
    while frontier has nodes:
        pick node with minimum f(n) value
        if node == goal:
            return reconstructed_path
        explore neighbors, update their scores
    return None (no path found)
```

---

### **Algorithm 2: Dijkstra's Algorithm**

**Location:** `algorithms/dijkstra.py`

**Where Used in Project:**
- Backup pathfinding algorithm (compared with A*)
- Used for computing all distances from one node (dijkstra_all_distances function)
- Baseline for safety comparison

**Why This Algorithm Was Chosen:**
- ✅ Guaranteed shortest path in weighted graphs
- ✅ Works on all positive-weight edges
- ✅ Good reference point for algorithm comparison
- ✅ Simpler than A* (no heuristic needed)

**Time Complexity:**
- **With Binary Heap:** O((V + E) log V)
- **V** = vertices (intersections), **E** = edges (roads)
- For city map: ~100-200 nodes = very fast

**Space Complexity:** O(V) for distance tracking

**Real-World Explanation:**
Like a flood that spreads from a point. Start at rescue base, then gradually explore nearby areas, keeping track of shortest distance to each location. When you reach the victim, that's guaranteed to be the shortest route.

**Flow of Execution:**
1. Initialize all distances to infinity except start (0)
2. Put start in priority queue (by distance)
3. While queue has nodes:
   - Pick node with minimum distance
   - Check all its neighbors
   - If neighbor's distance improves, update it
   - Add neighbor to queue
4. Reconstruct path from parent pointers
5. Return [path, total_distance]

---

### **Algorithm 3: BFS (Breadth-First Search)**

**Location:** `algorithms/bfs.py`

**Where Used in Project:**
- Quick pathfinding on unweighted graphs (ignores edge costs)
- Algorithm comparison baseline
- Good for fast-response scenarios where all paths are equally risky

**Why This Algorithm Was Chosen:**
- ✅ Finds shortest path (in number of hops) instantly
- ✅ Very simple O(V+E) linear time
- ✅ Provides comparison point for other algorithms
- ✅ Good for grid-based maps

**Time Complexity:** O(V + E) - optimal for unweighted graphs

**Space Complexity:** O(V) for queue storage

**Real-World Explanation:**
Imagine spreading a circle of rescue teams around a point, all moving equally fast. The first team to reach the victim shows you the quickest route (in terms of number of turns, not distance).

**Flow of Execution:**
1. Add start node to queue
2. While queue not empty:
   - Take first node from queue
   - Check all unvisited neighbors
   - If neighbor is goal, return path
   - Otherwise, add neighbor to queue and mark as visited
3. Return None if goal unreachable

---

### **Algorithm 4: UCS (Uniform Cost Search)**

**Location:** `algorithms/ucs.py`

**Where Used in Project:**
- Alternative weighted pathfinding
- Included in algorithm comparison
- Similar to Dijkstra but with full path tracking

**Why This Algorithm Was Chosen:**
- ✅ Finds lowest-cost path (considers road conditions)
- ✅ Complete exploration strategy
- ✅ Better than BFS for weighted roads
- ✅ Simpler to understand than A*

**Time Complexity:** O((V + E) log V) similar to Dijkstra

**Real-World Explanation:**
Like planning the shortest distance route. Check all roads, but prioritize roads with less travel time or safer conditions first. Keep expanding until you find the victim location via the cheapest path.

---

### **Algorithm 5: DFS (Depth-First Search)**

**Location:** `algorithms/dfs.py`

**Where Used in Project:**
- Alternative exploration method
- Included in multi-algorithm comparison
- Shows different approach to pathfinding

**Why This Algorithm Was Chosen:**
- ✅ Finds *a* path quickly (not necessarily shortest)
- ✅ Memory efficient (stack-based)
- ✅ Good for exploring unknown areas
- ✅ Shows algorithm diversity in project

**Time Complexity:** O(V + E)

**Real-World Explanation:**
Go as far as possible down one street. If it's wrong, backtrack and try another street. First complete path found, but might not be the best route.

---

### **Algorithm 6: 0/1 Knapsack (Dynamic Programming)**

**Location:** `core/knapsack.py`

**Where Used in Project:**
- Selects which stranded victims to rescue (maximize lives saved)
- Optimizes resource distribution (maximize impact with limited supplies)
- Considers rescue_cost (fuel needed) vs rescue_value (priority × survival chance)

**Why This Algorithm Was Chosen:**
- ✅ Solves resource-constrained optimization
- ✅ Cannot rescue everyone due to time/fuel limits
- ✅ Prioritizes high-injury victims
- ✅ Maximizes total rescue value within constraints

**Time Complexity:**
- **O(n × W)** where n = victims, W = capacity (fuel/budget)
- For 50 victims & 1000 fuel units = ~50,000 operations (instant)

**Space Complexity:** O(n × W) for DP table

**Real-World Explanation:**
You have limited fuel (knapsack capacity). You cannot rescue everyone. So you pick the victims based on:
- How many people? (more = higher value)
- How injured? (critical = high priority)
- How far? (more distance = more fuel cost)
- What's your chance to save them? (low survival chance = lower value)

Choose the best combination that maximizes lives saved with fuel available.

**Flow of Execution:**
1. Create DP table: rows = victims, columns = fuel amounts
2. For each victim and fuel level:
   - Option 1: Don't rescue (take value from previous victim)
   - Option 2: Rescue if enough fuel (previous value + this victim value)
   - Choose option that gives higher total value
3. Traceback through table to find which victims selected
4. Return: selected victims, not_selected, total_value, total_cost

---

## 4. BACKEND WORKFLOW: REQUEST TO RESPONSE

### **Step-by-Step Flow:**

```
USER ACTION (Frontend - Streamlit)
    ↓
1. USER CLICKS "DISPATCH TEAM TO VICTIM"
    ↓
2. STREAMLIT PAGE TRIGGERS (rescue_ops.py):
    - Gets selected team & target victim location
    - Loads city graph from data/cities/city_map*.json
    - Loads current disasters from events_*.json
    ↓
3. ALGORITHM SELECTOR RUNS (core/algorithm_selector.py - core logic):
    - Calls graph_engine.py to build adjacency lists in 3 ways:
      a) "fastest" mode: weight = time × congestion
      b) "safest" mode: weight = time + (risk_score × 100)
      c) "balanced" mode: 0.5×time + 0.3×risk + 0.2×distance
    ↓
4. ALL 5 ALGORITHMS EXECUTE IN PARALLEL:
    a) BFS(unweighted_graph) → fastest but may be unsafe
    b) DFS(unweighted_graph) → alternative exploration
    c) Dijkstra(weighted_graph) → guaranteed shortest
    d) A*(weighted_graph, heuristic) → fast + optimal
    e) UCS(weighted_graph) → uniform cost approach
    ↓
5. RESULTS SCORED (Composite scoring):
    - Rank each algorithm on 4 criteria:
      * Execution time (fast = good)
      * Path length (short = good)
      * Nodes explored (few = good)
      * Safety score (high = good)
    - Calculate composite score for each
    ↓
6. BEST ALGORITHM SELECTED (lowest composite score):
    - Example: "A* wins with balanced safety vs speed"
    ↓
7. MISSION CREATED (mission_manager.py):
    - Create Mission object with:
      * Team ID, target node, algorithm used
      * Full path, step count, timestamps
      * People to rescue, injury level
    - Save to data/active_missions.json
    ↓
8. RESPONSE SENT TO USER:
    - Mission ID: M[timestamp]
    - Algorithm chosen: A*
    - Path: [node1 → node2 → node3 → victim]
    - Estimated time: 15 minutes
    - Safety score: 0.85
    ↓
USER SEES:
    - Team dispatched ✓
    - Real-time map showing mission progress
    - Each step can be advanced manually
    - If road blocked → automatic replanning
```

### **Mission Execution Loop:**

```
Mission "en_route" status:
    ↓
USER CLICKS "ADVANCE STEP":
    - Current step incremented
    - Team moves to next node on path
    - Check if arrived at victim location
    ↓
Mission status: "arrived" → "rescued" → "returning" → "complete"
    ↓
MISSION LOGGED to data/rescue_log.csv
```

---

## 5. OPTIMIZATION TECHNIQUES USED

### **1. Algorithm Comparison & Composite Scoring**
```python
# Instead of using ONE algorithm, run ALL 5:
# Score each on: time, path_length, nodes_explored, safety
# Pick the one with best COMBINATION
# Result: Better paths than any single algorithm
```

**Why it matters:** No single algorithm is best for all scenarios. A* is fast but DFS might be safer.

### **2. Multi-Mode Adjacency Lists**
```python
Mode 1: "fastest"  → weight = time × traffic_congestion
Mode 2: "safest"   → weight = time + (risk_score × 100)  
Mode 3: "balanced" → 0.5×time + 0.3×risk + 0.2×distance

A* uses "safest" mode (avoids disaster zones)
Dijkstra uses "balanced" mode (considers all factors)
```

**Why it matters:** Same algorithm, different edge weights = different optimal paths.

### **3. Risk Scoring**
```python
Risk Score Calculation:
- If node is in disaster zone → high risk (1.0 × severity)
- If node adjacent to blocked road → medium risk (0.8 × severity)
- If node near affected area → low risk (0.6 × severity)
- Severity multiplier: critical=1.0, high=0.75, medium=0.5, low=0.25
```

**Why it matters:** Avoid disaster zones even if it takes longer.

### **4. Knapsack Optimization for Victim Selection**
```python
def calculate_rescue_value(person):
    return injury_weight × survival_chance × log(people_count)
    
Keep only victims with best value/cost ratio
```

**Why it matters:** Can't rescue everyone, so maximize total lives saved per unit fuel.

### **5. Dynamic Path Replanning**
```python
When USER BLOCKS A ROAD:
1. Check if any active mission uses that road
2. If yes → immediately replan mission
3. Run algorithm selector again
4. Get new path
5. Update mission in real-time

Example: 
Old path: A → B → C (12 steps via Dijkstra)
Road B-C blocked
New path: A → B → D → C (14 steps via A*)
Mission updates automatically
```

**Why it matters:** System adapts to real disasters instantly.

### **6. Greedy Team Selection**
```python
For each victim:
    Find nearest available rescue team
    Assign to that team
    Reduces total response time
```

### **7. Atomic File Operations**
```python
Write to temporary file
Sync to disk
Atomic move to real file
```

**Why it matters:** Prevents data corruption if system crashes mid-write.

---

## 6. DEVOPS & DEPLOYMENT EXPLANATION

### **What is DevOps?**
DevOps = Development + Operations. Tools to build, test, and deploy code automatically.

### **A. DOCKERFILE (Container Setup)**

**Location:** `Dockerfile`

**Purpose:** Package entire application into a portable container

**What it does:**
```dockerfile
FROM python:3.11-slim
# Use Python 3.11 (lightweight version)

RUN apt-get install build-essential gcc
# Install system libraries needed for numpy/matplotlib

COPY requirements.txt .
RUN pip install -r requirements.txt
# Install Python dependencies

COPY . .
# Copy entire project into container

EXPOSE 8501
# Open port 8501 (Streamlit default)

CMD ["streamlit", "run", "app.py"]
# Start the application
```

**Why Docker?**
- ✅ Works on professor's machine same way as yours
- ✅ No "works on my machine" problems
- ✅ Deployment ready (push to AWS/Azure instantly)
- ✅ Lightweight environment

**How to build:**
```bash
docker build -t disaster-app .
docker run -p 8501:8501 disaster-app
```

**Result:** Application runs on http://localhost:8501

### **B. Docker Compose (NOT PRESENT - Could be added)**

**If it existed, it would do:**
```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data  # Persist data across restarts
  
  database: (if needed)
    image: postgres
    environment:
      POSTGRES_PASSWORD: secret
```

**Why Compose?** 
- Run multiple services (app + database + cache) together
- Single command: `docker-compose up`

---

### **C. GitHub / GitHub Actions (CI/CD Pipeline)**

**NOT IMPLEMENTED in your project, but here's what you could do:**

**GitHub Actions = Automated testing & deployment**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Azure

on: 
  push:
    branches: [main]  # When you push code...

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t app .
      - name: Run tests
        run: python -m pytest
      - name: Deploy to Azure
        run: az container create --image app:latest ...
```

**What happens:**
1. You push code to GitHub
2. GitHub automatically runs tests
3. If tests pass → builds Docker image
4. If image builds → deploys to Azure
5. If deployment works → app is live

**Why it matters:**
- ✅ Zero manual deployment
- ✅ Can't accidentally deploy broken code
- ✅ Every push is tested before going live

### **D. Deployment Strategy**

**Currently:** Runs locally on your machine

**Could be deployed to:**
1. **Azure Container Instances** - Quick, simple
2. **Azure App Service** - Managed service
3. **Kubernetes (AKS)** - For large scale
4. **AWS Elastic Container Service** - Amazon alternative

**Steps:**
1. Push Docker image to registry
2. Create container instance
3. Assign public IP
4. Point domain to it
5. App is live!

---

## 7. PROJECT EXPLAINED IN SIMPLE LANGUAGE (College Presentation)

### **Title Slide:**
"Disaster Evacuation Pathfinding System: Real-Time Rescue Coordination Using Data Structures & Algorithms"

### **What's the Problem?**

When a disaster strikes (earthquake, flood, fire):
- ❌ Many people stranded in different locations
- ❌ Limited rescue teams & fuel
- ❌ Roads might be blocked by debris
- ❌ Need to maximize lives saved in minimum time

**Question:** Which rescue team should go where? Which route is safest? How to use limited resources optimally?

### **Our Solution:**

We built a system that:

1. **Models the city as a graph**
   - Each intersection = node
   - Each road = edge (with travel time, safety, capacity)

2. **Uses 5 algorithms to find optimal rescue paths**
   - BFS: Quick exploration
   - DFS: Alternative routes
   - Dijkstra: Shortest distance
   - A*: Fast + smart (uses position hints)
   - UCS: Cost-aware

3. **Compares all 5 algorithms**
   - Ranks on: speed, safety, path quality
   - Picks the best one for that specific scenario
   - Better than any single algorithm!

4. **Optimizes victim selection**
   - Uses Knapsack algorithm
   - Can't rescue everyone in one trip
   - Prioritizes: high-injury people, high survival chance
   - Maximizes total lives saved with limited fuel

5. **Handles real-time disasters**
   - Road blocked? → Automatically replan mission
   - New disaster detected? → Mark zone as high-risk
   - Teams adapt instantly

### **System Features:**

**Dashboard:**
- Real-time city overview
- Show disaster zones, blocked roads
- Metrics: # stranded, # safe zones, active disasters

**Disaster Control:**
- Create disasters (earthquake, fire, floods)
- Disasters spread to nearby areas
- Block roads automatically

**Rescue Operations:**
- Select team & victim
- System picks best algorithm
- Show path on map with progress
- Manually advance steps or auto-play

**Resource Hub:**
- Manage supplies (medical kits, food, water, blankets)
- Distribute to safe zones
- Track what's in transit

---

## 8. PROBABLE VIVA QUESTIONS & ANSWERS

### **Q1: Why did you choose 5 pathfinding algorithms instead of just one?**

**Answer:**
"No single algorithm is optimal for all scenarios. A* is fast but DFS might find a safer route through disaster zones. By running all 5 and scoring them on multiple criteria (speed, safety, path length, nodes explored), we get the best path for that specific situation. It's more robust and adaptive."

---

### **Q2: Explain A* algorithm in 1 minute.**

**Answer:**
"A* combines actual path cost (Dijkstra) with a heuristic guess (euclidean distance to goal). We calculate f(n) = g(n) + h(n) where g is distance traveled, h is estimated distance remaining. Always expand the node with lowest f(n). This makes it faster than Dijkstra while still guaranteeing the shortest path. Time complexity is O((V+E) log V)."

---

### **Q3: Why is Knapsack used in your project?**

**Answer:**
"After we find a path to a victim, we have limited fuel to rescue multiple people. Knapsack solves: which people should we rescue first to maximize lives saved with available fuel? Each victim has a cost (fuel needed) and value (injury level × survival chance × people count). The DP algorithm finds the optimal combination that maximizes total rescue value within fuel capacity - O(n×W) complexity."

---

### **Q4: What happens when a road is blocked in the middle of a mission?**

**Answer:**
"We check if any active mission uses that road. If yes, we immediately trigger replanning: run algorithm selector again with the blocked road marked as invalid (weight = 999999). The system finds an alternate route and updates the mission in real-time. User sees: 'Path replanned from 12 steps via Dijkstra to 14 steps via A*'."

---

### **Q5: How do you compare 5 algorithms fairly?**

**Answer:**
"We run each algorithm on different adjacency list modes (fastest, safest, balanced). Then score each result on 4 criteria using percentile ranking:
- Execution time rank
- Path length rank  
- Nodes explored rank
- Safety score rank
Sum these 4 ranks for composite score. Lowest score wins. This ensures a fair comparison."

---

### **Q6: What's the time complexity of your pathfinding?**

**Answer:**
"For city with ~100-200 nodes and ~300-500 edges:
- BFS: O(V+E) = ~500 operations
- Dijkstra: O((V+E) log V) = ~2000 operations
- A*: O(b^d) ≈ O((V+E) log V) = ~2000 operations
All run in <50ms, so real-time response is instant."

---

### **Q7: How do you handle multiple disasters at once?**

**Answer:**
"Each disaster is an event object with: affected_nodes, blocked_edges, severity, type. When computing risk scores, we check all active events and sum their effects. A node adjacent to multiple disasters has higher risk. All 5 algorithms automatically consider this when computing paths. A* and Dijkstra will avoid high-risk areas even if longer."

---

### **Q8: Why use Streamlit instead of a traditional web framework?**

**Answer:**
"Streamlit is designed for data applications. It lets us:
- Build UI in pure Python (no JavaScript needed)
- Automatic caching of data (fast reruns)
- Interactive widgets instantly
- Beautiful responsive design
- Deploy in seconds
For a DAA project demonstration, Streamlit is perfect because focus is on algorithms, not UI complexity."

---

### **Q9: How do you ensure data consistency when multiple missions update simultaneously?**

**Answer:**
"We use atomic file operations: write to temporary file, fsync to disk, then atomic move to actual file. This prevents corruption if system crashes mid-write. Missions are loaded fresh each time from persistent JSON, so there's no race condition. Sequential processing ensures consistency."

---

### **Q10: What optimizations did you implement?**

**Answer:**
"1. Algorithm comparison with composite scoring - gets best path
2. Risk-based edge weighting - avoids disaster zones
3. Multi-mode adjacency lists - different optimizations
4. Knapsack for victim selection - maximizes lives saved
5. Dynamic replanning - adapts to new road blockages
6. Lazy evaluation - only compute what's needed
7. Atomic file I/O - data consistency"

---

### **Q11: Can this system scale to larger cities?**

**Answer:**
"Yes, with optimizations:
- BFS/DFS scale linearly O(V+E)
- A* with good heuristic scales well (skips irrelevant nodes)
- Dijkstra scales O((V+E) log V)
- Current system: 100-200 nodes = instant
- For 10,000 nodes: still <500ms with A* + spatial indexing
- For real-time: use A* only (skip slower algorithms on large graphs)"

---

### **Q12: What if two teams need same victim?**

**Answer:**
"In rescue_ops.py, we check team availability. If a team is already 'dispatched', it's not available. Greedy selector picks the nearest available team. If all teams busy, user is warned. Alternatively, could implement team resource reservation system to prevent double-booking."

---

### **Q13: How do disasters spread?**

**Answer:**
"In disaster_manager.py, spread_disaster() function uses BFS:
- Start at epicenter
- Explore radius_hops levels
- Block all edges within that radius
- Mark all nodes as affected
- Each affected node gets higher risk score
- Algorithms avoid these areas"

---

### **Q14: Why is safety_score used instead of just path_length?**

**Answer:**
"Because fastest path might go through disaster zone. We calculate safety_score = 1 - (sum of risk scores on path / path length). A safe path through disaster zone: 0.4. A short path through danger: 0.2. Algorithms optimize both: speed AND safety, not just one."

---

### **Q15: Can you add real-time traffic data?**

**Answer:**
"Yes! Currently, congestion_factor = 1.0 + min(1.5, edge_load/capacity). We could:
1. Connect to traffic API
2. Update edge_load in real-time
3. Algorithms automatically adapt
4. Routes would avoid congested areas
The system is designed for this - just need data source."

---

## 9. ARCHITECTURE EXPLANATION: HOW COMPONENTS CONNECT

### **Layered Architecture:**

```
┌─────────────────────────────────────────────┐
│           STREAMLIT UI (Frontend)           │
│    4 Pages: Dashboard, Control, Ops, Hub   │
└─────────────────┬───────────────────────────┘
                  │ User requests
                  ↓
┌─────────────────────────────────────────────┐
│      Business Logic Layer (core/)           │
│  • mission_manager → orchestrates missions  │
│  • algorithm_selector → picks best path     │
│  • disaster_manager → tracks disasters      │
│  • resource_manager → distributes supplies  │
│  • graph_engine → handles map structure     │
└─────────┬──────────────┬──────────┬─────────┘
          │              │          │
          ↓              ↓          ↓
┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐
│   Algorithms    │  │  Data Loaders    │  │  Utilities         │
│                 │  │                  │  │                    │
│ • BFS           │  │ • JSON parsing   │  │ • visualizer       │
│ • DFS           │  │ • CSV logging    │  │ • graph rendering  │
│ • Dijkstra      │  │ • File I/O       │  │                    │
│ • A*            │  │ • Atomicity      │  │                    │
│ • UCS           │  │                  │  │                    │
│ • Knapsack      │  │                  │  │                    │
└─────────────────┘  └──────────────────┘  └────────────────────┘
          │              │                       │
          └──────────────┴───────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────┐
        │   Data Layer (data/cities/)    │
        │  • City graphs (nodes, edges)  │
        │  • Disaster events             │
        │  • Safe zones                  │
        │  • Rescue units                │
        │  • Resources                   │
        │  • Mission logs                │
        └───────────────────────────────┘
```

### **Data Flow in Action:**

```
User Action: "Dispatch Team Alpha to rescue people at Node C"
    ↓
Streamlit Page (rescue_ops.py):
    - User selects: Team Alpha, Target Node C
    ↓
mission_manager.create_mission():
    - Create mission object
    - Call algorithm_selector.select_and_run()
    ↓
algorithm_selector.select_and_run():
    - Load city graph via graph_engine.load_graph()
    - Create 3 adjacency lists (fastest, safest, balanced)
    - Run all 5 algorithms in sequence
    ↓
Each Algorithm:
    - BFS: returns [path], cost
    - Dijkstra: returns [path], distance
    - A*: returns [path], distance
    ↓
Composite Scoring:
    - Rank each on 4 criteria
    - Return best algorithm + path
    ↓
mission_manager.create_mission() continues:
    - Save mission to data/active_missions.json
    - Update team status to "dispatched"
    - Log to data/rescue_log.csv
    ↓
Streamlit receives mission object:
    - Display mission ID, path, algorithm
    - Show map with path highlighted
    - Enable step-by-step advance
    ↓
User advances steps:
    - Team moves along path
    - visualizer.py renders progress
    - When arrived: confirm rescue
    ↓
Rescue confirmed:
    - knapsack.py selects victims (if multiple)
    - resource_manager.distribute() adds supplies to safe zone
    - Mission logged as complete
```

### **How Frontend ↔ Backend Connect:**

**Frontend (Streamlit):**
- User clicks button → triggers Python function
- Data loaded from JSON files
- Displays results

**Backend (Python):**
- Receives request
- Runs algorithms
- Updates JSON data
- Returns results to frontend

**Database (JSON files):**
- Persistent storage
- Read/write via atomic operations
- No external database needed (simple for DAA project)

---

## 10. KEY POINTS TO REMEMBER FOR VIVA

### **Conceptual Understanding:**

✅ **BFS** = Level-by-level search (unweighted)
✅ **DFS** = Go deep then backtrack (unweighted)
✅ **Dijkstra** = Greedy best-first (weighted)
✅ **A*** = Dijkstra + heuristic (fast + optimal)
✅ **UCS** = Uniform cost expansion
✅ **Knapsack** = Dynamic programming optimization

### **Complexity Quick Reference:**

| Algorithm | Time | Space | Why? |
|-----------|------|-------|------|
| BFS | O(V+E) | O(V) | No priority queue |
| DFS | O(V+E) | O(V) | Stack-based |
| Dijkstra | O((V+E)logV) | O(V) | Priority queue |
| A* | O(b^d) | O(V) | Heuristic pruning |
| UCS | O((V+E)logV) | O(V) | Like Dijkstra |
| Knapsack | O(n×W) | O(n×W) | DP table |

### **Real-World Mapping:**

| Component | Represents |
|-----------|-----------|
| Nodes | Intersections, safe zones, victim locations |
| Edges | Roads (with distance, travel time, capacity) |
| Path | Rescue team's route from base to victim to safe zone |
| Risk Score | How dangerous is this area (affected by disasters) |
| Cost | Fuel needed to travel this route |
| Algorithm | Method to find optimal path |

### **Why This Project is a Good DAA Project:**

✅ Uses 6 different algorithms
✅ Demonstrates time complexity differences in practice
✅ Shows optimization techniques (composite scoring, DP)
✅ Real-world applicable
✅ Shows algorithm selection based on scenario
✅ Combines multiple data structures (graphs, queues, heaps, DP tables)

---

## PRESENTATION FLOW SUGGESTION

**15-20 minute presentation:**

1. **Intro (2 min):** Problem statement (disaster rescue needs optimization)
2. **Architecture (3 min):** Show folder structure, explain layers
3. **Algorithms (8 min):** Deep dive: A*, Dijkstra, Knapsack (with visuals)
4. **Live Demo (4 min):** Show system in action (dispatch team, see path)
5. **Optimization (2 min):** Explain composite scoring, dynamic replanning
6. **Conclusion (1 min):** Impact, scalability, future work

**Have ready for Demo:**
- Multiple disaster scenarios
- Show algorithm comparison (A* vs Dijkstra)
- Show replanning when road blocked
- Show victim selection via Knapsack

**Slides to show:**
- Problem visualization
- Architecture diagram
- Algorithm complexity charts
- Real-time mission screenshot
- Disaster zone visualization

---

## FINAL TIPS FOR VIVA

1. **Know complexity by heart:** O(V+E), O((V+E)logV), O(b^d), O(n×W)
2. **Have 1-liner for each algorithm:** What it does, why chosen
3. **Prepare "show, don't tell":** Demo the system, not just slides
4. **Know trade-offs:** Speed vs Safety, Optimality vs Simplicity
5. **Be ready for "What if":** Road blocked? → replanning. City 10x bigger? → use A* only
6. **Understand every line:** Don't memorize, understand the logic
7. **Connect to theory:** Greedy algorithms, DP, heuristics, graph theory
8. **Have a killer ending:** "This system can save lives in real disasters"

---

**Good Luck with your presentation! 🎓**
