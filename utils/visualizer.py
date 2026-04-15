"""All Plotly map rendering functions."""
import plotly.graph_objects as go
import networkx as nx
from typing import Dict, List, Optional, Tuple, Any


# Node colors by type
NODE_COLORS = {
    "safe_zone": "#2ecc71",  # Green
    "hospital": "#3498db",  # Blue
    "shelter": "#f39c12",  # Orange
    "intersection": "#95a5a6",  # Gray
    "bridge": "#8e44ad",  # Purple
}

DISASTER_COLOR = "#e74c3c"  # Red
RESCUED_COLOR = "#27ae60"  # Dark green
CURRENT_MISSION_COLOR = "#1e90ff"  # Bright blue


def build_city_map(
    G: nx.Graph,
    positions: Dict[str, Tuple[float, float]],
    city_graph_data: Dict,
    highlight_paths: Optional[List[Dict]] = None,
    step_annotations: Optional[List[Dict]] = None,
    blocked_edges: Optional[set] = None,
    show_mst: bool = False,
    mst_edges: Optional[List[Tuple]] = None,
    team_positions: Optional[Dict[str, str]] = None,
    target_node: Optional[str] = None,
    start_node: Optional[str] = None,
    height: int = 500
) -> go.Figure:
    """
    Build a comprehensive city map visualization.
    
    Map rendering order (bottom to top):
      1. All road edges (gray, solid, thin)
      2. MST edges if show_mst (orange, thin, behind)
      3. Blocked edges (red, dashed)
      4. Air edges (blue, dashed)
      5. Highlighted paths with step annotations
      6. Node markers (colored by type and state)
      7. Step number text on path edges
      8. Directional arrows on recommended path
      9. Team markers (star shape)
      10. Legend
    """
    fig = go.Figure()
    
    # 1. All road edges (gray, solid, thin)
    road_x, road_y = [], []
    for u, v, data in G.edges(data=True):
        if data.get("air_only", False):
            continue  # Air edges drawn separately
        if blocked_edges and ((u, v) in blocked_edges or (v, u) in blocked_edges):
            continue  # Blocked edges drawn separately
        
        x0, y0 = positions[u]
        x1, y1 = positions[v]
        road_x.extend([x0, x1, None])
        road_y.extend([y0, y1, None])
    
    if road_x:
        fig.add_trace(go.Scatter(
            x=road_x, y=road_y,
            mode='lines',
            line=dict(color='#666666', width=1),
            hoverinfo='skip',
            showlegend=True,
            name='Road'
        ))
    
    # 2. MST edges if show_mst (orange, thin, behind)
    if show_mst and mst_edges:
        mst_x, mst_y = [], []
        for u, v, w in mst_edges:
            if u in positions and v in positions:
                x0, y0 = positions[u]
                x1, y1 = positions[v]
                mst_x.extend([x0, x1, None])
                mst_y.extend([y0, y1, None])
        
        if mst_x:
            fig.add_trace(go.Scatter(
                x=mst_x, y=mst_y,
                mode='lines',
                line=dict(color='#ff8c00', width=1),
                hoverinfo='skip',
                showlegend=True,
                name='MST Edge'
            ))
    
    # 3. Blocked edges (red, dashed)
    if blocked_edges:
        blocked_x, blocked_y = [], []
        for u, v in blocked_edges:
            if G.has_edge(u, v) and u in positions and v in positions:
                x0, y0 = positions[u]
                x1, y1 = positions[v]
                blocked_x.extend([x0, x1, None])
                blocked_y.extend([y0, y1, None])
        
        if blocked_x:
            fig.add_trace(go.Scatter(
                x=blocked_x, y=blocked_y,
                mode='lines',
                line=dict(color='#e74c3c', width=2, dash='dash'),
                hoverinfo='skip',
                showlegend=True,
                name='Blocked Road'
            ))
    
    # 4. Air edges (blue, dashed)
    air_x, air_y = [], []
    for u, v, data in G.edges(data=True):
        if data.get("air_only", False):
            if u in positions and v in positions:
                x0, y0 = positions[u]
                x1, y1 = positions[v]
                air_x.extend([x0, x1, None])
                air_y.extend([y0, y1, None])
    
    if air_x:
        fig.add_trace(go.Scatter(
            x=air_x, y=air_y,
            mode='lines',
            line=dict(color='#3498db', width=1.5, dash='dash'),
            hoverinfo='skip',
            showlegend=True,
            name='Air Corridor'
        ))
    
    # 5. Highlighted paths
    if highlight_paths:
        for idx, path_info in enumerate(highlight_paths):
            path = path_info.get("path", [])
            color = path_info.get("color", "#2ecc71")
            width = path_info.get("width", 2)
            dash = path_info.get("dash", "solid")
            label = path_info.get("label", f"Path {idx+1}")
            show_steps = path_info.get("show_steps", False)
            
            if len(path) < 2:
                continue
            
            path_x, path_y = [], []
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                if u in positions and v in positions:
                    x0, y0 = positions[u]
                    x1, y1 = positions[v]
                    path_x.extend([x0, x1, None])
                    path_y.extend([y0, y1, None])
                    
                    # Add step annotations if requested
                    if show_steps:
                        mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
                        edge_data = G.get_edge_data(u, v) if G.has_edge(u, v) else {}
                        dist = edge_data.get("distance_km", 0)
                        
                        fig.add_annotation(
                            x=mid_x, y=mid_y,
                            text=f"{i+1}",
                            showarrow=False,
                            font=dict(size=10, color=color),
                            bgcolor='rgba(0,0,0,0.7)',
                            bordercolor=color,
                            borderwidth=1,
                            borderpad=2
                        )
            
            if path_x:
                fig.add_trace(go.Scatter(
                    x=path_x, y=path_y,
                    mode='lines',
                    line=dict(color=color, width=width, dash=dash),
                    hoverinfo='skip',
                    showlegend=idx == 0,  # Only show first path in legend
                    name=label if idx == 0 else None
                ))
            
            # Add directional arrows for first (recommended) path
            if idx == 0:
                for i in range(len(path) - 1):
                    u, v = path[i], path[i+1]
                    if u in positions and v in positions:
                        x0, y0 = positions[u]
                        x1, y1 = positions[v]
                        
                        fig.add_annotation(
                            x=x1, y=y1,
                            ax=x0, ay=y0,
                            xref='x', yref='y',
                            axref='x', ayref='y',
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1,
                            arrowwidth=1.5,
                            arrowcolor=color
                        )
    
    # 6. Node markers
    node_x, node_y, node_colors, node_sizes, node_symbols, node_texts, hover_texts = [], [], [], [], [], [], []
    
    for node_id in G.nodes():
        node_data = G.nodes[node_id]
        x, y = positions[node_id]
        
        # Determine node color based on state
        people_stranded = node_data.get("people_stranded", 0)
        people_rescued = node_data.get("people_rescued", 0)
        node_type = node_data.get("type", "intersection")
        is_safe_zone = node_data.get("is_safe_zone", False)
        
        if people_stranded > 0:
            color = DISASTER_COLOR  # Red for disaster
            size = 20
            symbol = "circle"
        elif people_rescued > 0:
            color = RESCUED_COLOR  # Green for rescued
            size = 18
            symbol = "circle-dot"
        elif is_safe_zone:
            color = NODE_COLORS.get("safe_zone", "#2ecc71")
            size = 18
            symbol = "circle"
        else:
            color = NODE_COLORS.get(node_type, "#95a5a6")
            size = 12 if node_type == "intersection" else 14
            symbol = "circle"
        
        # Special markers
        if node_id == target_node:
            size = 24
            symbol = "circle"
        elif node_id == start_node:
            size = 22
            symbol = "circle"
        
        node_x.append(x)
        node_y.append(y)
        node_colors.append(color)
        node_sizes.append(size)
        node_symbols.append(symbol)
        node_texts.append(node_id)
        
        display_name = node_data.get("display_name", node_id)
        hover_text = f"{display_name}<br>Type: {node_type}<br>People Stranded: {people_stranded}<br>People Rescued: {people_rescued}"
        if node_data.get("helipad"):
            hover_text += "<br>Helipad: Yes"
        hover_texts.append(hover_text)
    
    if node_x:
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                symbol=node_symbols,
                line=dict(width=2, color='white')
            ),
            text=node_texts,
            textposition='top center',
            textfont=dict(size=10, color='white'),
            hoverinfo='text',
            hovertext=hover_texts,
            showlegend=False
        ))
    
    # 7. Step annotations
    if step_annotations:
        for anno in step_annotations:
            node_id = anno.get("node_id")
            if node_id not in positions:
                continue
            
            x, y = positions[node_id]
            step_num = anno.get("step_number", 0)
            visited = anno.get("visited", False)
            current = anno.get("current", False)
            
            if current:
                fill_color = CURRENT_MISSION_COLOR
                border_color = "white"
                border_width = 3
                size = 24
            elif visited:
                fill_color = "#2d6a4f"
                border_color = "white"
                border_width = 1
                size = 18
            else:
                fill_color = "#333333"
                border_color = "#888888"
                border_width = 1
                size = 16
            
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers+text',
                marker=dict(
                    size=size,
                    color=fill_color,
                    symbol='circle',
                    line=dict(width=border_width, color=border_color)
                ),
                text=[str(step_num)],
                textposition='middle center',
                textfont=dict(size=12, color='white', weight='bold'),
                hoverinfo='skip',
                showlegend=False
            ))
    
    # 8. Team markers (star shape)
    if team_positions:
        team_x, team_y, team_colors, team_names = [], [], [], []
        team_colors_map = {
            "U001": "#3498db",  # Alpha-1: Blue
            "U002": "#9b59b6",  # Eagle-1: Purple
            "U003": "#2c3e50",  # Shield-1: Dark
            "U004": "#e74c3c",  # Blaze-1: Red
            "U005": "#f39c12",  # Peak-1: Orange
        }
        
        for team_id, node_id in team_positions.items():
            if node_id in positions:
                x, y = positions[node_id]
                team_x.append(x)
                team_y.append(y)
                team_colors.append(team_colors_map.get(team_id, "#ffffff"))
                team_names.append(team_id)
        
        if team_x:
            fig.add_trace(go.Scatter(
                x=team_x, y=team_y,
                mode='markers',
                marker=dict(
                    size=18,
                    color=team_colors,
                    symbol='star',
                    line=dict(width=2, color='white')
                ),
                text=team_names,
                hoverinfo='text',
                hovertext=[f"Team: {name}" for name in team_names],
                showlegend=False
            ))
    
    # 9. Legend (annotations at bottom-right)
    fig.add_annotation(
        x=0.98, y=0.02,
        xref='paper', yref='paper',
        text="Road: <span style='color:#666666;'>━━</span><br>Air Corridor: <span style='color:#3498db;'>- - -</span><br>Blocked Road: <span style='color:#e74c3c;'>- - -</span><br>MST Edge: <span style='color:#ff8c00;'>━━</span><br>Recommended Path: <span style='color:#2ecc71;'>━━</span>",
        showarrow=False,
        xanchor='right',
        yanchor='bottom',
        font=dict(size=10, color='white'),
        bgcolor='rgba(0,0,0,0.5)',
        borderpad=4
    )
    
    # Layout
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor='x', scaleratio=1)
    )
    
    return fig


def create_mini_mission_map(G, positions, mission, height=300):
    """Create a small map for a single mission."""
    path = mission.get("path_to_target", []) if mission.get("phase") == "outbound" else mission.get("return_path", [])
    current_step = mission.get("current_step", 0)
    target = mission.get("target_node")
    base = mission.get("base_node")
    
    highlight_paths = []
    if path:
        # Build color-coded path segments
        colored_path = []
        colors = []
        
        for i, node in enumerate(path):
            if i < current_step:
                colors.append("#2d6a4f")  # Visited (green)
            elif i == current_step:
                colors.append("#1e90ff")  # Current (blue)
            else:
                colors.append("#666666")  # Future (gray)
        
        highlight_paths.append({
            "path": path,
            "color": "#2ecc71",
            "width": 3,
            "label": "Mission Path",
            "show_steps": True
        })
    
    step_annotations = []
    for i, node in enumerate(path):
        step_annotations.append({
            "node_id": node,
            "step_number": i,
            "visited": i < current_step,
            "current": i == current_step
        })
    
    team_positions = {mission["team_id"]: path[current_step] if current_step < len(path) else base}
    
    return build_city_map(
        G, positions, {},
        highlight_paths=highlight_paths,
        step_annotations=step_annotations,
        team_positions=team_positions,
        target_node=target,
        start_node=base,
        height=height
    )
