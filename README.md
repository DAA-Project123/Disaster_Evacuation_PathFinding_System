# Disaster Evacuation PathFinding System

A FastAPI-based disaster evacuation and rescue pathfinding system with interactive algorithm visualization.

## Features

- **Live Graph Traversal Animation**: Watch BFS, DFS, A*, Dijkstra, and UCS explore nodes in real-time
- **Comparative Algorithm Race**: Run all 5 algorithms simultaneously on the same source-target pair
- **Evacuation Wave Simulation**: Visualize disaster spread from epicenter hop by hop
- **Heatmap Overlay**: Dynamic risk heatmap based on disaster events
- **Interactive Disaster Management**: Create, manage, and resolve disaster events
- **Rescue Operations**: Dispatch teams with algorithm-optimized paths
- **Resource Hub**: Manage and distribute resources to safe zones

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **NetworkX**: Graph library for pathfinding algorithms
- **Pandas**: Data manipulation and analysis

### Frontend
- **Alpine.js**: Lightweight JavaScript framework for reactivity
- **Vis.js**: Dynamic, browser-based visualization library for network graphs
- **Chart.js**: Simple yet flexible JavaScript charting
- **Tailwind CSS**: Utility-first CSS framework

## Installation

1. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access the application at: http://localhost:8000

## Project Structure

```
daa/
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── algorithms/             # Pathfinding algorithms
│   ├── __init__.py
│   ├── bfs.py
│   ├── dfs.py
│   ├── dijkstra.py
│   ├── astar.py
│   └── ucs.py
├── core/                   # Core business logic
│   ├── algorithm_selector.py
│   ├── data_loader.py
│   ├── disaster_manager.py
│   ├── dynamic_obstacles.py
│   ├── graph_engine.py
│   ├── greedy_selector.py
│   ├── knapsack.py
│   ├── mission_manager.py
│   └── resource_manager.py
├── data/                   # Data storage
│   ├── cities/            # City graph data (JSON)
│   ├── resources.json
│   ├── active_missions.json
│   └── rescue_log.csv
└── static/                # Frontend assets
    ├── index.html
    └── js/
        └── app.js
```

## Available Cities/Maps

1. **Map 1 (Veridian City)**: Default city with comprehensive node network
2. **Map 2 (Harborfield)**: Coastal city scenario
3. **Map 3 (Maplecrest)**: Mountain/suburban scenario

## API Endpoints

### Cities
- `GET /api/cities` - List available cities
- `GET /api/city/{city_id}` - Get city data with disasters and zones
- `GET /api/city/{city_id}/nodes` - Get all nodes
- `GET /api/city/{city_id}/edges` - Get all edges

### Disasters
- `GET /api/city/{city_id}/disasters` - Get disaster events
- `POST /api/disasters/create` - Create new disaster
- `POST /api/disasters/{id}/resolve` - Resolve disaster
- `POST /api/city/{city_id}/stranded` - Update stranded people
- `POST /api/city/{city_id}/block-road` - Block a road
- `POST /api/city/{city_id}/unblock-road` - Unblock a road

### Algorithms
- `GET /api/city/{city_id}/algorithms/compare` - Compare all algorithms
- `GET /api/city/{city_id}/algorithms/animate/{algorithm}` - Get animation steps
- `GET /api/city/{city_id}/algorithms/race` - Run algorithm race

### Visualization
- `GET /api/city/{city_id}/heatmap` - Get risk heatmap data
- `GET /api/city/{city_id}/evacuation-wave` - Get evacuation wave data

### Rescue Operations
- `GET /api/city/{city_id}/rescue-teams` - Get rescue teams
- `GET /api/city/{city_id}/missions` - Get missions
- `POST /api/missions/dispatch` - Dispatch team
- `POST /api/missions/{id}/advance` - Advance mission
- `POST /api/missions/{id}/confirm-rescue` - Confirm rescue
- `POST /api/missions/{id}/return` - Start return journey

### Resources
- `GET /api/resources` - Get all resources
- `GET /api/city/{city_id}/safe-zones` - Get safe zones
- `POST /api/resources/dispatch` - Dispatch resources
- `POST /api/resources/confirm-delivery` - Confirm delivery
- `POST /api/resources/recovery-cycle` - Run recovery cycle

## Algorithm Implementations

### BFS (Breadth-First Search)
Explores all nodes at the present depth before moving to nodes at the next depth level. Guarantees shortest path in unweighted graphs.

### DFS (Depth-First Search)
Explores as far as possible along each branch before backtracking. May not find shortest path but explores deep paths quickly.

### Dijkstra's Algorithm
Finds the shortest path in weighted graphs with non-negative weights. Uses a priority queue for efficiency.

### A* (A-Star)
Best-first search algorithm that uses heuristics to guide the search toward the goal. More efficient than Dijkstra when good heuristic available.

### UCS (Uniform Cost Search)
Similar to Dijkstra but expands the least-cost path first. Guarantees optimal path in weighted graphs.

## Data Files

City data is stored in `data/cities/` with consistent naming:
- `city_map{1,2,3}.json` - City graph (nodes and edges)
- `safe_zones_map{1,2,3}.json` - Safe zone locations
- `units_map{1,2,3}.json` - Rescue team data
- `events_map{1,2,3}.json` - Disaster events
- `zones_map{1,2,3}.json` - Evacuation zones

## License

MIT License
