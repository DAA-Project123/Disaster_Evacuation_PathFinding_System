"""Disaster Control page - Admin sets disaster events, stranded people."""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

from core.graph_engine import load_city_graph, build_graph, get_positions, save_city_graph
from core.dynamic_obstacles import get_all_roads, block_road, unblock_road, check_mission_impact
from core.algorithms.prims import prims_mst, mst_connectivity_impact
from core.mission_manager import load_missions, block_affects_mission
from utils.visualizer import build_city_map


def render():
    st.title("Disaster Control")
    st.caption("Create disaster events and manage road blocks")
    
    # Get selected map
    selected_map = st.session_state.get("selected_map", "Map 1")
    map_file = f"data/city_map{selected_map.split()[-1]}.json"
    
    # Load city data
    try:
        city_data = load_city_graph(map_file)
        G = build_graph(city_data)
        positions = get_positions(city_data)
    except Exception as e:
        st.error(f"Error loading map: {e}")
        return
    
    # Initialize disaster events in session state
    if "disaster_events" not in st.session_state:
        st.session_state["disaster_events"] = {}
    
    if "blocked_edges" not in st.session_state:
        st.session_state["blocked_edges"] = set()
    
    # SECTION 1: Active Disaster Events
    st.subheader("Active Disaster Events")
    
    # Get current disaster nodes
    disaster_nodes = [n for n in city_data.get("nodes", []) if n.get("people_stranded", 0) > 0]
    
    if disaster_nodes:
        events_data = []
        for n in disaster_nodes:
            events_data.append({
                "Node": n["id"],
                "Zone": n.get("zone", ""),
                "Type": n.get("type", ""),
                "People Stranded": n.get("people_stranded", 0),
                "Injury Level": n.get("injury_level", "none"),
                "Survival Chance": f"{n.get('survival_chance', 1.0):.0%}",
                "Display Name": n.get("display_name", n["id"])
            })
        
        events_df = pd.DataFrame(events_data)
        st.dataframe(events_df, use_container_width=True, hide_index=True)
        
        # Clear event buttons
        st.write("**Clear Events:**")
        cols = st.columns(min(4, len(disaster_nodes)))
        for idx, node in enumerate(disaster_nodes):
            with cols[idx % 4]:
                if st.button(f"Clear {node['id']}", key=f"clear_{node['id']}"):
                    # Reset node
                    node["people_stranded"] = 0
                    node["injury_level"] = "none"
                    node["survival_chance"] = 1.0
                    save_city_graph(city_data, map_file)
                    st.success(f"Cleared disaster at {node['id']}")
                    st.rerun()
    else:
        st.info("No active disaster events")
    
    # SECTION 2: Create Disaster Event
    st.subheader("Create Disaster Event")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        # Get non-safe-zone nodes
        available_nodes = [n for n in city_data.get("nodes", []) 
                          if not n.get("is_safe_zone", False)]
        
        node_options = [n["id"] for n in available_nodes]
        node_display = [f"{n['id']} - {n.get('display_name', n['id'])}" for n in available_nodes]
        
        selected_node_display = st.selectbox("Select Node", node_display)
        selected_node = selected_node_display.split(" - ")[0] if selected_node_display else None
        
        selected_node_data = next((n for n in available_nodes if n["id"] == selected_node), None)
        
        people_stranded = st.slider("People Stranded", 0, 500, 50)
        injury_level = st.selectbox("Injury Level", ["none", "low", "medium", "high", "critical"])
        disaster_type = st.selectbox("Disaster Type", 
                                     ["flood", "fire", "earthquake", "landslide", "building_collapse"])
        survival_chance = st.slider("Survival Chance", 0.1, 1.0, 0.8, step=0.05)
        
        if st.button("Create Disaster Event", type="primary"):
            if selected_node_data:
                selected_node_data["people_stranded"] = people_stranded
                selected_node_data["injury_level"] = injury_level
                selected_node_data["survival_chance"] = survival_chance
                # Store disaster type in a custom field
                selected_node_data["disaster_type"] = disaster_type
                
                save_city_graph(city_data, map_file)
                st.success(f"Disaster event created at {selected_node}")
                st.rerun()
    
    with col_right:
        # Show city map with disasters highlighted
        st.write("**Map Preview**")
        
        # Create preview data
        preview_data = json.loads(json.dumps(city_data))  # Deep copy
        if selected_node:
            for n in preview_data["nodes"]:
                if n["id"] == selected_node:
                    n["people_stranded"] = people_stranded
        
        preview_G = build_graph(preview_data)
        
        fig = build_city_map(
            preview_G, positions, preview_data,
            blocked_edges=st.session_state.get("blocked_edges", set()),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # SECTION 3: Dynamic Road Blocks
    st.subheader("Dynamic Road Blocks")
    
    # Get all roads
    all_roads = get_all_roads(G)
    blocked_edges = st.session_state.get("blocked_edges", set())
    
    # Show currently blocked roads
    blocked_roads = [r for r in all_roads if r["blocked"]]
    for edge_tuple in blocked_edges:
        for r in all_roads:
            if (r["source"], r["target"]) == edge_tuple or (r["target"], r["source"]) == edge_tuple:
                r["blocked"] = True
    
    blocked_roads = [r for r in all_roads if r["blocked"]]
    
    if blocked_roads:
        st.write("**Currently Blocked Roads:**")
        blocked_df = pd.DataFrame([
            {"Road": r["road_name"], "From": r["source"], "To": r["target"], "Distance": f"{r['distance_km']:.1f} km"}
            for r in blocked_roads
        ])
        st.dataframe(blocked_df, use_container_width=True, hide_index=True)
        
        # Unblock buttons
        cols = st.columns(min(3, len(blocked_roads)))
        for idx, road in enumerate(blocked_roads):
            with cols[idx % 3]:
                if st.button(f"Unblock {road['source']}-{road['target']}", 
                           key=f"unblock_{road['source']}_{road['target']}"):
                    unblock_road(G, road["source"], road["target"])
                    edge_key = tuple(sorted([road["source"], road["target"]]))
                    blocked_edges.discard((road["source"], road["target"]))
                    blocked_edges.discard((road["target"], road["source"]))
                    st.session_state["blocked_edges"] = blocked_edges
                    st.success(f"Unblocked {road['road_name']}")
                    st.rerun()
    else:
        st.info("No roads currently blocked")
    
    # Block new road
    unblocked_roads = [r for r in all_roads if not r["blocked"] and not r["air_only"]]
    
    if unblocked_roads:
        road_options = [f"{r['source']} - {r['target']} ({r['road_name']})" for r in unblocked_roads]
        selected_road = st.selectbox("Select Road to Block", road_options)
        
        if selected_road and st.button("Block Road"):
            # Parse selection
            road_part = selected_road.split(" (")[0]
            u, v = road_part.split(" - ")
            
            # Block in graph
            block_road(G, u, v)
            
            # Add to session state
            blocked_edges.add((u, v))
            blocked_edges.add((v, u))
            st.session_state["blocked_edges"] = blocked_edges
            
            # Check mission impact
            active_missions = [m for m in load_missions() if m["status"] in ["en_route", "returning"]]
            affected = check_mission_impact(active_missions, u, v)
            
            if affected:
                st.warning(f"This blocks {len(affected)} active mission(s): {', '.join(affected)}")
                
                # Offer replan
                for mission_id in affected:
                    if st.button(f"Replan Mission {mission_id}", key=f"replan_{mission_id}"):
                        from core.mission_manager import replan_mission
                        replan_mission(mission_id, G, blocked_edges, positions, city_data)
                        st.success(f"Replanned mission {mission_id}")
                        st.rerun()
            
            # Check MST impact
            mst_result = prims_mst(G)
            mst_impact = mst_connectivity_impact(G, mst_result, blocked_edges)
            
            if mst_impact["blocked_mst_edges"]:
                st.warning(f"Blocking a critical infrastructure road (part of MST). "
                          f"Connectivity score: {mst_impact['connectivity_score']:.1%}")
            
            st.rerun()
    
    # SECTION 4: Map Preview
    st.subheader("Full Map Preview")
    
    fig = build_city_map(
        G, positions, city_data,
        blocked_edges=blocked_edges,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("""
    **Legend:** 
    Red nodes = Disaster events | 
    Gray nodes = No disaster | 
    Red dashed = Blocked roads | 
    Blue dashed = Air corridors | 
    Green nodes = Safe zones
    """)
