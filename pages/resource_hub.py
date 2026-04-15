"""Resource Hub page - Resource distribution from main hub."""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

from core.graph_engine import load_city_graph, build_graph, get_positions
from utils.visualizer import build_city_map


def render():
    st.title("Resource Hub")
    st.caption("Distribute resources from main hub to teams and nodes")
    
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
    
    # Load resources
    resources_file = Path("data/resources.json")
    if resources_file.exists():
        with open(resources_file, 'r') as f:
            resources_data = json.load(f)
    else:
        resources_data = {
            "hub_node": "A1",
            "inventory": {
                "medical_kits": 100,
                "food_packs": 200,
                "water_units": 300,
                "fuel_canisters": 50,
                "fire_suppressant": 40,
                "rope_kits": 30
            }
        }
        with open(resources_file, 'w') as f:
            json.dump(resources_data, f, indent=2)
    
    # Load teams
    try:
        with open("data/rescue_units.json", 'r') as f:
            teams_data = json.load(f)
    except:
        teams_data = []
    
    # Initialize distribution log
    if "distribution_log" not in st.session_state:
        st.session_state["distribution_log"] = []
    
    hub_node = resources_data.get("hub_node", "A1")
    inventory = resources_data.get("inventory", {})
    
    # SECTION 1: Hub Inventory
    st.subheader("Hub Inventory")
    
    inv_cols = st.columns(len(inventory) if inventory else 1)
    starting_amounts = {
        "medical_kits": 100,
        "food_packs": 200,
        "water_units": 300,
        "fuel_canisters": 50,
        "fire_suppressant": 40,
        "rope_kits": 30
    }
    
    for idx, (resource, amount) in enumerate(inventory.items()):
        with inv_cols[idx % len(inv_cols)]:
            max_amount = starting_amounts.get(resource, 100)
            pct = (amount / max_amount) * 100 if max_amount > 0 else 0
            
            delta_color = "normal"
            if pct < 20:
                delta_color = "inverse"
            
            st.metric(
                resource.replace("_", " ").title(),
                amount,
                delta=f"{pct:.0f}%" if pct < 100 else None,
                delta_color=delta_color
            )
    
    # SECTION 2: Team Resource Status
    st.subheader("Team Resource Status")
    
    teams_resource_data = []
    for team in teams_data:
        fuel_pct = (team.get("fuel_remaining", 0) / team.get("fuel_capacity", 1)) * 100
        teams_resource_data.append({
            "Team": team["name"],
            "Fuel %": f"{fuel_pct:.0f}%",
            "Medical Kits": team.get("medical_kits", 0),
            "Food": team.get("food_packs", 0),
            "Water": team.get("water_units", 0),
            "Rope": team.get("rope_kits", 0),
            "Fire Suppressant": team.get("fire_suppressant", 0)
        })
    
    if teams_resource_data:
        teams_df = pd.DataFrame(teams_resource_data)
        
        # Style low fuel
        def color_fuel(val):
            try:
                pct = float(val.replace("%", ""))
                if pct < 20:
                    return "color: #e74c3c"
            except:
                pass
            return ""
        
        styled_teams = teams_df.style.map(color_fuel, subset=["Fuel %"])
        st.dataframe(styled_teams, use_container_width=True, hide_index=True)
    
    # SECTION 3: Distribute Resources
    st.subheader("Distribute Resources")
    
    dist_col1, dist_col2 = st.columns([2, 3])
    
    with dist_col1:
        # Select team
        team_options = [f"{t['name']} ({t['type']})" for t in teams_data]
        selected_team_display = st.selectbox("Select Team", team_options)
        selected_team = teams_data[team_options.index(selected_team_display)] if team_options else None
        
        # Select resource
        resource_options = list(inventory.keys())
        selected_resource = st.selectbox("Select Resource", resource_options)
        
        # Amount
        max_available = inventory.get(selected_resource, 0)
        amount = st.number_input("Amount", min_value=1, max_value=max_available, value=1)
        
        if st.button("Distribute Resource", type="primary"):
            if selected_team and selected_resource and amount > 0:
                if inventory.get(selected_resource, 0) >= amount:
                    # Deduct from hub
                    inventory[selected_resource] -= amount
                    resources_data["inventory"] = inventory
                    
                    with open(resources_file, 'w') as f:
                        json.dump(resources_data, f, indent=2)
                    
                    # Add to team
                    team_field = selected_resource
                    current_amount = selected_team.get(team_field, 0)
                    selected_team[team_field] = current_amount + amount
                    
                    with open("data/rescue_units.json", 'w') as f:
                        json.dump(teams_data, f, indent=2)
                    
                    # Log distribution
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "team": selected_team["name"],
                        "resource": selected_resource,
                        "amount": amount
                    }
                    st.session_state["distribution_log"].append(log_entry)
                    
                    st.success(f"Distributed {amount} {selected_resource} to {selected_team['name']}")
                    st.rerun()
                else:
                    st.error(f"Insufficient {selected_resource} in hub inventory")
    
    with dist_col2:
        # Distribution log
        st.write("**Distribution Log (Last 10)**")
        
        log = st.session_state.get("distribution_log", [])
        if log:
            log_df = pd.DataFrame(log[-10:])
            log_df = log_df.iloc[::-1]  # Reverse to show newest first
            st.dataframe(log_df, use_container_width=True, hide_index=True)
        else:
            st.info("No distributions yet")
    
    # SECTION 4: Resource Flow Map
    st.subheader("Resource Flow Map")
    
    # Build team positions for map
    team_positions = {t["id"]: t["current_node"] for t in teams_data}
    
    # Create map with hub highlighted
    fig = build_city_map(
        G, positions, city_data,
        team_positions=team_positions,
        height=500
    )
    
    # Add hub annotation
    if hub_node in positions:
        x, y = positions[hub_node]
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers',
            marker=dict(size=30, color='gold', symbol='star', line=dict(width=3, color='white')),
            name='Main Hub',
            showlegend=True
        ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(f"Main Hub: {hub_node} (gold star). Team positions shown as colored markers.")


# Need to import go for the hub marker
import plotly.graph_objects as go
