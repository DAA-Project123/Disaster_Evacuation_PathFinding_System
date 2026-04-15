"""Rescue Operations page - Core rescue page (most important)."""
import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from pathlib import Path
import numpy as np

from core.graph_engine import load_city_graph, build_graph, get_positions, get_nodes_with_disaster, get_safe_zones
from core.mission_manager import (
    load_missions, get_active_missions, advance_step, confirm_rescue, 
    start_return, complete_mission, create_mission
)
from core.algorithm_selector import select_and_run
from core.knapsack import build_rescue_items, knapsack_01, priority_queue_rescue_order
from core.greedy_selector import nearest_team_to_target, highest_resources_team
from core.algorithms.prims import prims_mst
from core.algorithms.kruskals import compare_mst_algorithms
from utils.visualizer import build_city_map, create_mini_mission_map
from utils.styling import style_teams_df, style_disaster_events, style_knapsack_result


def render():
    # AUTO REFRESH toggle
    auto_refresh = st.toggle("Live Updates (5s auto-refresh)", value=False)
    
    st.title("Rescue Operations")
    st.caption("Dispatch teams and track rescue missions")
    
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
    
    # Load teams
    try:
        with open("data/rescue_units.json", 'r') as f:
            teams_data = json.load(f)
    except:
        teams_data = []
    
    # Get blocked edges
    blocked_edges = st.session_state.get("blocked_edges", set())
    
    # SECTION 1: TEAM STATUS BAR
    st.subheader("Team Status")
    
    teams_df_data = []
    for team in teams_data:
        fuel_pct = (team.get("fuel_remaining", 0) / team.get("fuel_capacity", 1)) * 100
        teams_df_data.append({
            "Team": team["name"],
            "Type": team["type"],
            "Location": team["current_node"],
            "Status": team["status"].upper(),
            "Fuel %": f"{fuel_pct:.0f}%",
            "Kits": team.get("medical_kits", 0),
            "Rescued": team.get("people_rescued_total", 0)
        })
    
    if teams_df_data:
        teams_df = pd.DataFrame(teams_df_data)
        st.dataframe(teams_df, use_container_width=True, hide_index=True)
    
    # SECTION 2: MISSION TRACKER
    st.subheader("Active Missions")
    
    active_missions = get_active_missions()
    
    if active_missions:
        for mission in active_missions:
            with st.container(border=True):
                # CARD TOP ROW
                c1, c2, c3 = st.columns([2, 2, 2])
                with c1:
                    st.write(f"**{mission['mission_id']}** | {mission['team_name']} ({mission['team_type']})")
                    st.caption(f"Algorithm: {mission['algorithm_used']}")
                with c2:
                    status_colors = {
                        "en_route": "#f39c12",
                        "arrived": "#9b59b6",
                        "rescued": "#2ecc71",
                        "returning": "#3498db"
                    }
                    color = status_colors.get(mission["status"], "#95a5a6")
                    st.markdown(f"<span style='color:{color}; font-weight:bold;'>{mission['status'].upper()}</span>", 
                               unsafe_allow_html=True)
                with c3:
                    if mission.get("replanned"):
                        st.warning("Replanned")
                
                # CARD MIDDLE - Path Step Visualizer
                path = mission.get("path_to_target", []) if mission["phase"] == "outbound" else mission.get("return_path", [])
                path_names = mission.get("path_names_to_target", []) if mission["phase"] == "outbound" else [mission["target_name"]] + [mission["path_names_to_target"][0]] if mission["path_names_to_target"] else []
                current_step = mission["current_step"]
                
                # HTML Path Visualizer
                path_html = "<div style='display:flex; align-items:center; gap:8px; flex-wrap:wrap; padding:12px;'>"
                for i, node in enumerate(path):
                    if i < current_step:
                        bg = "#2d6a4f"  # Visited
                        color = "white"
                    elif i == current_step:
                        bg = "#1e90ff"  # Current
                        color = "white"
                    else:
                        bg = "#333333"  # Future
                        color = "#888888"
                    
                    name = path_names[i] if i < len(path_names) else node
                    short_name = name.split(" - ")[0] if " - " in name else name
                    
                    path_html += f"<div style='background:{bg}; color:{color}; border-radius:8px; padding:8px 14px; font-size:13px; font-weight:bold;'>{short_name}</div>"
                    
                    if i < len(path) - 1:
                        path_html += "<div style='color:#666; font-size:16px;'>></div>"
                
                path_html += "</div>"
                st.markdown(path_html, unsafe_allow_html=True)
                
                # Progress bar
                max_steps = max(len(path) - 1, 1)
                progress = current_step / max_steps
                st.progress(progress)
                
                current_node_name = path_names[current_step] if current_step < len(path_names) else path[current_step]
                st.caption(f"Step {current_step} of {max_steps} — Currently at: {current_node_name}")
                
                if mission.get("replanned"):
                    orig = mission.get("original_path_length", 0)
                    new_len = mission.get("path_length", 0)
                    st.warning(f"Path replanned. Original: {orig} steps. Replanned: {new_len} steps.")
                
                # CARD BOTTOM - Action Buttons
                st.divider()
                
                if mission["status"] == "en_route":
                    acol1, acol2 = st.columns([1, 2])
                    with acol1:
                        if st.button("Advance Step", key=f"adv_{mission['mission_id']}"):
                            advance_step(mission["mission_id"])
                            st.rerun()
                
                elif mission["status"] == "arrived":
                    # Check if people still stranded
                    target_node = mission["target_node"]
                    target_data = None
                    for n in city_data.get("nodes", []):
                        if n["id"] == target_node:
                            target_data = n
                            break
                    
                    if target_data:
                        people = target_data.get("people_stranded", 0)
                        injury = target_data.get("injury_level", "none")
                        st.info(f"Arrived at {mission['target_name']}. {people} people waiting. Injury: {injury}")
                        
                        can_rescue = people > 0 and target_data.get("people_rescued", 0) == 0
                        
                        if st.button(f"Confirm Rescue", key=f"rescue_{mission['mission_id']}", 
                                    disabled=not can_rescue):
                            if not can_rescue:
                                st.error("No people to rescue at this node.")
                            else:
                                try:
                                    confirm_rescue(mission["mission_id"], city_data)
                                    st.success(f"Rescued {people} people!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                
                elif mission["status"] == "rescued":
                    st.info("Rescue complete. Team ready to return.")
                    if st.button("Start Return Journey", key=f"return_{mission['mission_id']}"):
                        team_type = mission["team_type"]
                        start_return(mission["mission_id"], G, blocked_edges, team_type)
                        st.rerun()
                
                elif mission["status"] == "returning":
                    # Show return path
                    return_path = mission.get("return_path", [])
                    if return_path:
                        return_html = "<div style='display:flex; align-items:center; gap:8px; flex-wrap:wrap; padding:12px;'>"
                        for i, node in enumerate(return_path):
                            if i < current_step:
                                bg = "#2d6a4f"
                                color = "white"
                            elif i == current_step:
                                bg = "#1e90ff"
                                color = "white"
                            else:
                                bg = "#333333"
                                color = "#888888"
                            
                            name = node
                            short_name = name.split(" - ")[0] if " - " in name else name
                            return_html += f"<div style='background:{bg}; color:{color}; border-radius:8px; padding:8px 14px; font-size:13px; font-weight:bold;'>{short_name}</div>"
                            if i < len(return_path) - 1:
                                return_html += "<div style='color:#666; font-size:16px;'>></div>"
                        return_html += "</div>"
                        st.markdown(return_html, unsafe_allow_html=True)
                    
                    rcol1, rcol2 = st.columns([1, 2])
                    with rcol1:
                        if st.button("Advance Return Step", key=f"ret_adv_{mission['mission_id']}"):
                            advance_step(mission["mission_id"])
                            st.rerun()
                    
                    if current_step >= len(return_path) - 1:
                        with rcol2:
                            if st.button("Complete Mission", key=f"complete_{mission['mission_id']}"):
                                complete_mission(mission["mission_id"], teams_data, city_data)
                                # Save updated city data with rescued people at safe zone
                                from core.graph_engine import save_city_graph
                                save_city_graph(city_data, map_file)
                                st.success("Mission complete! Rescued people delivered to safe zone.")
                                st.rerun()
                
                # MINI MAP
                mini_fig = create_mini_mission_map(G, positions, mission, height=250)
                st.plotly_chart(mini_fig, use_container_width=True)
    else:
        st.info("No active missions")
    
    # SECTION 3: DISPATCH NEW MISSION
    st.subheader("Dispatch Rescue Team")
    
    left_col, right_col = st.columns([2, 3])
    
    with left_col:
        st.write("**Step 1 - Select Target**")
        
        # Get victim locations
        victim_nodes = [n for n in city_data.get("nodes", []) 
                       if n.get("people_stranded", 0) > 0 and n.get("people_rescued", 0) == 0]
        
        if victim_nodes:
            # Calculate priority scores
            victims_data = []
            for n in victim_nodes:
                injury_mult = {"critical": 4, "high": 3, "medium": 2, "low": 1, "none": 0}.get(n.get("injury_level", "none"), 1)
                priority = n.get("survival_chance", 1.0) * injury_mult * n.get("people_stranded", 0)
                victims_data.append({
                    "Node": n["id"],
                    "Zone": n.get("zone", ""),
                    "Stranded": n.get("people_stranded", 0),
                    "Injury": n.get("injury_level", "none"),
                    "Survival %": f"{n.get('survival_chance', 1.0):.0%}",
                    "Priority Score": round(priority, 1)
                })
            
            victims_df = pd.DataFrame(victims_data)
            victims_df = victims_df.sort_values("Priority Score", ascending=False)
            
            # Style injury levels
            def style_injury(val):
                colors = {"critical": "red", "high": "orange", "medium": "yellow"}
                return f"color: {colors.get(val, 'white')}"
            
            styled_df = victims_df.style.map(style_injury, subset=["Injury"])
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Select victim
            victim_options = [f"{v['Node']} - {v['Stranded']} people ({v['Injury']})" for _, v in victims_df.iterrows()]
            selected_victim = st.selectbox("Select Victim Location", victim_options, key="select_victim")
            selected_victim_id = selected_victim.split(" - ")[0] if selected_victim else None
            
            # Show victim details
            selected_victim_data = next((n for n in victim_nodes if n["id"] == selected_victim_id), None)
            if selected_victim_data:
                mcol1, mcol2, mcol3 = st.columns(3)
                with mcol1:
                    st.metric("People Stranded", selected_victim_data.get("people_stranded", 0))
                with mcol2:
                    st.metric("Injury Level", selected_victim_data.get("injury_level", "none"))
                with mcol3:
                    st.metric("Survival Chance", f"{selected_victim_data.get('survival_chance', 1.0):.0%}")
        else:
            st.info("No victims waiting for rescue")
            selected_victim_id = None
            selected_victim_data = None
        
        st.write("**Step 2 - Team Recommendation**")
        
        strategy = st.radio("Recommendation Strategy", 
                           ["Nearest team to target", "Highest resources"],
                           key="team_strategy")
        
        available_teams = [t for t in teams_data if t["status"] == "available"]
        
        if selected_victim_id and available_teams:
            if strategy == "Nearest team to target":
                rec = nearest_team_to_target(G, selected_victim_id, available_teams, blocked_edges)
            else:
                rec = highest_resources_team(available_teams)
            
            if rec.get("team"):
                st.info(f"Recommended: **{rec['team_name']}** | Reason: {rec['reason']}")
                recommended_team_id = rec["team_id"]
            else:
                st.warning("No suitable team found")
                recommended_team_id = None
        else:
            recommended_team_id = None
        
        st.write("**Step 3 - Select Team**")
        
        if available_teams:
            team_options = [f"{t['name']} ({t['type']}) - {t['current_node']}" for t in available_teams]
            selected_team_display = st.selectbox("Select Team", team_options, 
                                               index=next((i for i, t in enumerate(available_teams) 
                                                          if t["id"] == recommended_team_id), 0) if recommended_team_id else 0)
            selected_team_id = available_teams[team_options.index(selected_team_display)]["id"]
            selected_team = next((t for t in available_teams if t["id"] == selected_team_id), None)
            
            if selected_team:
                st.caption(f"Fuel: {selected_team.get('fuel_remaining', 0)}/{selected_team.get('fuel_capacity', 0)} | "
                          f"Kits: {selected_team.get('medical_kits', 0)} | Type: {selected_team['type']}")
                
                # Check helicopter constraint
                if selected_team["type"] == "helicopter" and selected_victim_data:
                    if not selected_victim_data.get("helipad", False):
                        st.error(f"{selected_team['name']} (helicopter) cannot land at this location.")
                        selected_team = None
        else:
            st.warning("No available teams")
            selected_team = None
    
    with right_col:
        # Algorithm Comparison and Path Preview
        if selected_victim_id and selected_team:
            st.write("**Algorithm Comparison**")
            
            # Run algorithms
            start_node = selected_team["current_node"]
            unit_type = "helicopter" if selected_team["type"] == "helicopter" else "ground"
            if selected_team["type"] == "mountain_rescue":
                unit_type = "mountain_rescue"
            
            result = select_and_run(G, start_node, selected_victim_id, {}, positions, city_data, unit_type)
            
            # Show comparison table
            comp_data = []
            for r in result["results"]:
                comp_data.append({
                    "Algorithm": r["algorithm"],
                    "Found": "Yes" if r["found"] else "No",
                    "Steps": r["path_length"],
                    "Nodes Explored": r["nodes_explored"],
                    "Time (ms)": f"{r['time_ms']:.2f}",
                    "Score": f"{r['score']:.4f}",
                    "Recommended": "Yes" if r["recommended"] else ""
                })
            
            comp_df = pd.DataFrame(comp_data)
            
            # Style
            def highlight_recommended(val):
                if val == "Yes":
                    return "background-color: #2d6a4f"
                return ""
            
            styled_comp = comp_df.style.map(highlight_recommended, subset=["Recommended"])
            st.dataframe(styled_comp, use_container_width=True, hide_index=True)
            
            # Charts
            chart_col1, chart_col2, chart_col3 = st.columns(3)
            
            with chart_col1:
                nodes_df = comp_df[comp_df["Found"] == "Yes"][["Algorithm", "Nodes Explored"]].copy()
                if not nodes_df.empty:
                    st.bar_chart(nodes_df.set_index("Algorithm"), height=150)
            
            with chart_col2:
                time_df = comp_df[comp_df["Found"] == "Yes"][["Algorithm", "Time (ms)"]].copy()
                if not time_df.empty:
                    # Convert back to float for chart
                    time_df["Time (ms)"] = time_df["Time (ms)"].str.replace(" ms", "").astype(float)
                    st.bar_chart(time_df.set_index("Algorithm"), height=150)
            
            with chart_col3:
                steps_df = comp_df[comp_df["Found"] == "Yes"][["Algorithm", "Steps"]].copy()
                if not steps_df.empty:
                    st.bar_chart(steps_df.set_index("Algorithm"), height=150)
            
            # MST Infrastructure Panel
            with st.expander("MST Infrastructure Analysis"):
                mst_comparison = compare_mst_algorithms(G)
                
                st.write("**MST Comparison**")
                mst_df = pd.DataFrame([
                    {"Algorithm": "Prim's", "Total Weight": mst_comparison["prims"]["total_weight"], 
                     "Time (ms)": f"{mst_comparison['prims']['time_ms']:.2f}"},
                    {"Algorithm": "Kruskal's", "Total Weight": mst_comparison["kruskals"]["total_weight"], 
                     "Time (ms)": f"{mst_comparison['kruskals']['time_ms']:.2f}"},
                ])
                st.dataframe(mst_df, use_container_width=True, hide_index=True)
                
                st.write(f"Same total weight: {mst_comparison['same_total_weight']}")
                st.write(f"Time difference: {mst_comparison['time_diff_ms']:.2f} ms")
                
                from core.algorithms.prims import mst_connectivity_impact
                impact = mst_connectivity_impact(G, mst_comparison["prims"], blocked_edges)
                st.metric("Connectivity Score", f"{impact['connectivity_score']:.1%}")
                
                if impact["blocked_mst_edges"]:
                    st.warning(f"{len(impact['blocked_mst_edges'])} MST edges are blocked!")
                
                st.caption("Prim's and Kruskal's both find the minimum cost road network. "
                          "If MST edges are blocked, these nodes lose optimal connectivity.")
            
            # Path Preview Map
            st.write("**Path Preview**")
            
            recommended = result.get("recommended")
            if recommended:
                highlight_paths = []
                for r in result["results"]:
                    if r["found"]:
                        highlight_paths.append({
                            "path": r["path"],
                            "color": "#2ecc71" if r["recommended"] else "#666666",
                            "width": 4 if r["recommended"] else 2,
                            "label": r["algorithm"],
                            "show_steps": r["recommended"]
                        })
                
                preview_fig = build_city_map(
                    G, positions, city_data,
                    highlight_paths=highlight_paths,
                    target_node=selected_victim_id,
                    start_node=start_node,
                    height=400
                )
                st.plotly_chart(preview_fig, use_container_width=True)
                
                # Recommended Algorithm Card
                st.metric("Recommended Algorithm", recommended["algorithm"], 
                         f"Score: {recommended['score']:.4f}")
                st.write(result.get("why_selected", ""))
                
                path_display = " -> ".join(recommended.get("path_names", []))
                st.write(f"**Path:** {path_display}")
                
                # Dispatch button
                st.divider()
                
                # Algorithm override
                all_algos = [r["algorithm"] for r in result["results"] if r["found"]]
                override_algo = st.selectbox("Override algorithm (optional)", 
                                            ["Use Recommended"] + all_algos,
                                            key="override_algo")
                
                final_algo = recommended if override_algo == "Use Recommended" else \
                            next((r for r in result["results"] if r["algorithm"] == override_algo), recommended)
                
                if st.button(f"Dispatch {selected_team['name']} via {final_algo['algorithm']}", type="primary"):
                    # Get base node (safe zone)
                    safe_zones = get_safe_zones(G)
                    base_node = selected_team["current_node"]
                    
                    # Create mission
                    mission = create_mission(
                        selected_map,
                        selected_team,
                        base_node,
                        selected_victim_id,
                        selected_victim_data.get("display_name", selected_victim_id),
                        final_algo["path"],
                        final_algo.get("path_names", []),
                        final_algo,
                        selected_victim_data.get("people_stranded", 0),
                        selected_victim_data.get("injury_level", "none")
                    )
                    
                    # Update team status
                    for t in teams_data:
                        if t["id"] == selected_team["id"]:
                            t["status"] = "dispatched"
                            break
                    
                    with open("data/rescue_units.json", 'w') as f:
                        json.dump(teams_data, f, indent=2)
                    
                    st.success(f"Mission created. {selected_team['name']} dispatched to {selected_victim_data.get('display_name', selected_victim_id)}.")
                    st.rerun()
    
    # SECTION 4: KNAPSACK OPTIMIZATION
    st.subheader("Knapsack Optimization")
    
    with st.expander("Knapsack Optimization — Prioritize Rescue Targets"):
        st.write("Given total rescue capacity across all available teams, "
                "which victims should be rescued to maximize total survival value?")
        
        available_teams = [t for t in teams_data if t["status"] == "available"]
        capacity = sum(t.get("capacity", 0) for t in available_teams)
        
        victim_nodes = [n for n in city_data.get("nodes", []) 
                       if n.get("people_stranded", 0) > 0 and n.get("people_rescued", 0) == 0]
        
        if victim_nodes and capacity > 0:
            items = build_rescue_items(victim_nodes, available_teams)
            
            knapsack_result = knapsack_01(items, capacity)
            priority_order = priority_queue_rescue_order(victim_nodes)
            
            tab1, tab2 = st.tabs(["Knapsack Selection", "Priority Queue Order"])
            
            with tab1:
                # Problem setup
                setup_df = pd.DataFrame([{
                    "Victim": i["node_name"],
                    "People": i["people"],
                    "Weight": i["weight"],
                    "Value": f"{i['value']:.1f}",
                    "Injury": i["injury_level"]
                } for i in items])
                st.write("**Problem Setup**")
                st.dataframe(setup_df, use_container_width=True, hide_index=True)
                
                # DP Table heatmap (show subset)
                dp_table = knapsack_result["dp_table"]
                if len(dp_table) > 0 and len(dp_table[0]) > 0:
                    # Show a subset if too large
                    import numpy as np
                    dp_np = np.array(dp_table)
                    show_rows = min(20, dp_np.shape[0])
                    show_cols = min(20, dp_np.shape[1])
                    dp_df = pd.DataFrame(dp_np[:show_rows, :show_cols])
                    st.write("**DP Table (subset)**")
                    st.dataframe(dp_df.style.background_gradient(cmap="YlOrRd"))
                
                # Result
                selected_items = knapsack_result["selected_items"]
                not_selected = knapsack_result["not_selected"]
                
                result_df_data = []
                for i in selected_items:
                    result_df_data.append({
                        "Victim": i["node_name"],
                        "People": i["people"],
                        "Selected": "Yes",
                        "Value": f"{i['value']:.1f}"
                    })
                for i in not_selected:
                    result_df_data.append({
                        "Victim": i["node_name"],
                        "People": i["people"],
                        "Selected": "No",
                        "Value": f"{i['value']:.1f}"
                    })
                
                result_df = pd.DataFrame(result_df_data)
                
                def highlight_selected(val):
                    if val == "Yes":
                        return "background-color: #2d6a4f"
                    return "background-color: #333333"
                
                styled_result = result_df.style.map(highlight_selected, subset=["Selected"])
                st.write("**Result**")
                st.dataframe(styled_result, use_container_width=True, hide_index=True)
                
                # Metrics
                mcol1, mcol2, mcol3 = st.columns(3)
                with mcol1:
                    st.metric("Total Value", f"{knapsack_result['total_value']:.1f}")
                with mcol2:
                    st.metric("Capacity Used", f"{knapsack_result['capacity_used']}/{capacity}")
                with mcol3:
                    st.metric("Victims Selected", len(selected_items))
            
            with tab2:
                # Priority queue order
                pq_df = pd.DataFrame([{
                    "Rank": idx + 1,
                    "Node": p["node_id"],
                    "People": p["people"],
                    "Injury": p["injury_level"],
                    "Survival %": f"{p['survival_chance']:.0%}",
                    "Priority Score": f"{p['priority_score']:.2f}"
                } for idx, p in enumerate(priority_order)])
                
                st.dataframe(pq_df, use_container_width=True, hide_index=True)
                
                # Bar chart
                chart_data = pd.DataFrame({
                    "Victim": [p["node_id"] for p in priority_order],
                    "Priority": [p["priority_score"] for p in priority_order]
                })
                st.bar_chart(chart_data.set_index("Victim"), height=200)
            
            st.caption("Note: This is academic guidance. You make the final dispatch decision.")
        else:
            st.info("No victims or no available team capacity")
    
    # SECTION 5: RESCUE LOG
    st.subheader("Rescue Log")
    
    with st.expander("Rescue Log"):
        try:
            log_df = pd.read_csv("data/rescue_log.csv")
            if not log_df.empty:
                # Filters
                fcol1, fcol2, fcol3 = st.columns(3)
                with fcol1:
                    teams_filter = st.multiselect("Team", log_df["team_name"].unique().tolist())
                with fcol2:
                    algo_filter = st.multiselect("Algorithm", log_df["algorithm_used"].unique().tolist())
                with fcol3:
                    status_filter = st.multiselect("Status", log_df["status"].unique().tolist())
                
                filtered = log_df.copy()
                if teams_filter:
                    filtered = filtered[filtered["team_name"].isin(teams_filter)]
                if algo_filter:
                    filtered = filtered[filtered["algorithm_used"].isin(algo_filter)]
                if status_filter:
                    filtered = filtered[filtered["status"].isin(status_filter)]
                
                st.dataframe(filtered, use_container_width=True, hide_index=True)
                
                # Aggregate
                if not filtered.empty:
                    st.divider()
                    acol1, acol2, acol3, acol4 = st.columns(4)
                    with acol1:
                        st.metric("Total Rescued", filtered["people_rescued"].sum())
                    with acol2:
                        avg_path = filtered["path_length"].mean()
                        st.metric("Avg Path Length", f"{avg_path:.1f}")
                    with acol3:
                        most_used = filtered["algorithm_used"].mode().iloc[0] if not filtered["algorithm_used"].empty else "N/A"
                        st.metric("Most Used Algorithm", most_used)
                    with acol4:
                        st.metric("Total Missions", len(filtered))
            else:
                st.info("No rescue log entries yet")
        except Exception as e:
            st.info("No rescue log available")
    
    # Auto refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()
