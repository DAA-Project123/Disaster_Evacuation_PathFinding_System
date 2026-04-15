"""Dashboard page - City overview + active missions."""
import streamlit as st
import pandas as pd
import json
from pathlib import Path

from core.graph_engine import load_city_graph, build_graph, get_positions
from core.mission_manager import load_missions
from core.algorithms.prims import prims_mst
from core.algorithms.kruskals import compare_mst_algorithms
from utils.visualizer import build_city_map
from utils.styling import style_teams_df


def render():
    st.title("Dashboard")
    st.caption("City overview and mission status")
    
    # SECTION 1: City Selector
    st.subheader("Select Map")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Map 1 - Central Metro", use_container_width=True,
                     type="primary" if st.session_state.get("selected_map") == "Map 1" else "secondary"):
            st.session_state["selected_map"] = "Map 1"
            st.rerun()
    with col2:
        if st.button("Map 2 - Harbor Port", use_container_width=True,
                     type="primary" if st.session_state.get("selected_map") == "Map 2" else "secondary"):
            st.session_state["selected_map"] = "Map 2"
            st.rerun()
    with col3:
        if st.button("Map 3 - Highland Valley", use_container_width=True,
                     type="primary" if st.session_state.get("selected_map") == "Map 3" else "secondary"):
            st.session_state["selected_map"] = "Map 3"
            st.rerun()
    
    # Default to Map 1
    if "selected_map" not in st.session_state:
        st.session_state["selected_map"] = "Map 1"
    
    selected_map = st.session_state["selected_map"]
    map_file = f"data/city_map{selected_map.split()[-1]}.json"
    
    # Load city data
    try:
        city_data = load_city_graph(map_file)
        G = build_graph(city_data)
        positions = get_positions(city_data)
    except Exception as e:
        st.error(f"Error loading map: {e}")
        return
    
    # SECTION 2: Mission Overview
    st.subheader("Mission Overview")
    
    missions = load_missions()
    active_missions = [m for m in missions if m["status"] != "complete"]
    
    # Count stats
    teams_available = 0
    teams_data = []
    try:
        with open("data/rescue_units.json", 'r') as f:
            teams_data = json.load(f)
            teams_available = len([t for t in teams_data if t["status"] == "available"])
    except:
        pass
    
    people_stranded = sum(n.get("people_stranded", 0) for n in city_data.get("nodes", []))
    people_rescued = sum(n.get("people_rescued", 0) for n in city_data.get("nodes", []))
    
    # Metrics
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.metric("Active Missions", len(active_missions))
    with mcol2:
        st.metric("Teams Available", teams_available)
    with mcol3:
        st.metric("People Stranded", people_stranded)
    with mcol4:
        st.metric("People Rescued", people_rescued)
    
    # Active mission cards
    if active_missions:
        st.write("**Active Missions**")
        cols = st.columns(min(3, len(active_missions)))
        for idx, mission in enumerate(active_missions[:3]):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.write(f"**{mission['mission_id']}**")
                    st.write(f"Team: {mission['team_name']}")
                    st.write(f"Status: {mission['status'].upper()}")
                    st.write(f"Target: {mission['target_name']}")
                    path_len = len(mission.get("path_to_target", [])) if mission["phase"] == "outbound" else len(mission.get("return_path", []))
                    st.write(f"Step {mission['current_step']}/{max(path_len - 1, 1)}")
                    if st.button("View Details", key=f"goto_{mission['mission_id']}"):
                        st.session_state["goto_rescue_ops"] = True
    
    # SECTION 3: City Map
    st.subheader("City Map")
    
    # Get blocked edges from session
    blocked_edges = st.session_state.get("blocked_edges", set())
    
    # Build team positions
    team_positions = {t["id"]: t["current_node"] for t in teams_data}
    
    fig = build_city_map(
        G, positions, city_data,
        blocked_edges=blocked_edges,
        team_positions=team_positions,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Legend
    st.caption("""
    **Legend:** 
    Green circle = Safe Zone | 
    Red circle = Active Disaster | 
    Green dot = Rescued | 
    Dashed blue = Air Corridor | 
    Dashed red = Blocked Road
    """)
    
    # SECTION 4: Algorithm Comparison Summary
    completed_missions = [m for m in missions if m["status"] == "complete"]
    if completed_missions:
        st.subheader("Algorithm Comparison Summary")
        
        # Algorithm usage frequency
        algo_counts = {}
        for m in completed_missions:
            algo = m.get("algorithm_used", "Unknown")
            algo_counts[algo] = algo_counts.get(algo, 0) + 1
        
        algo_df = pd.DataFrame(list(algo_counts.items()), columns=["Algorithm", "Missions"])
        st.bar_chart(algo_df.set_index("Algorithm"), height=200)
    
    # SECTION 5: MST Infrastructure Overview
    st.subheader("MST Infrastructure Overview")
    
    mst_comparison = compare_mst_algorithms(G)
    
    ccol1, ccol2, ccol3, ccol4 = st.columns(4)
    with ccol1:
        st.metric("Total MST Weight", f"{mst_comparison['prims']['total_weight']:.1f} km")
    with ccol2:
        st.metric("Prim's Time", f"{mst_comparison['prims']['time_ms']:.2f} ms")
    with ccol3:
        st.metric("Kruskal's Time", f"{mst_comparison['kruskals']['time_ms']:.2f} ms")
    with ccol4:
        same = "Yes" if mst_comparison["same_total_weight"] else "No"
        st.metric("Same Result", same)
    
    # MST map
    mst_fig = build_city_map(
        G, positions, city_data,
        show_mst=True,
        mst_edges=mst_comparison["prims"]["mst_edges"],
        blocked_edges=blocked_edges,
        height=350
    )
    st.plotly_chart(mst_fig, use_container_width=True)
    st.caption("Orange lines show the Minimum Spanning Tree (critical infrastructure)")
