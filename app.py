"""Main entry point for Disaster Response System."""
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime

from pages import dashboard, disaster_control, rescue_ops, resource_hub

st.set_page_config(
    layout="wide",
    page_title="Disaster Response System",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
[data-testid="stSidebar"] { 
    width: 260px !important; 
    min-width: 260px !important; 
    background: #13152a; 
}
.card { 
    background: #1a1d2e; 
    border: 1px solid #2d3154; 
    border-radius: 12px; 
    padding: 16px; 
}
.badge-green { 
    background:#2ecc71; 
    color:#0f1117; 
    padding:3px 10px; 
    border-radius:999px; 
    font-weight:700; 
    font-size:0.85rem; 
}
.badge-red { 
    background:#e74c3c; 
    color:#ffffff; 
    padding:3px 10px; 
    border-radius:999px; 
    font-weight:700; 
    font-size:0.85rem; 
}
.badge-yellow { 
    background:#f39c12; 
    color:#0f1117; 
    padding:3px 10px; 
    border-radius:999px; 
    font-weight:700; 
    font-size:0.85rem; 
}
.badge-blue { 
    background:#3498db; 
    color:#ffffff; 
    padding:3px 10px; 
    border-radius:999px; 
    font-weight:700; 
    font-size:0.85rem; 
}
</style>
""", unsafe_allow_html=True)

# Session state defaults
if "selected_map" not in st.session_state:
    st.session_state["selected_map"] = "Map 1"

if "disaster_events" not in st.session_state:
    st.session_state["disaster_events"] = {}

if "blocked_edges" not in st.session_state:
    st.session_state["blocked_edges"] = set()

if "selected_target" not in st.session_state:
    st.session_state["selected_target"] = None

if "selected_team" not in st.session_state:
    st.session_state["selected_team"] = None

if "graph_data" not in st.session_state:
    st.session_state["graph_data"] = {}

if "G" not in st.session_state:
    st.session_state["G"] = None

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="font-size:1.35rem;font-weight:800;color:#ffffff;">Disaster Response System</div>
    <div style="color:#a0a8c0;margin-top:4px;">DAA Academic Project</div>
    <hr style="border:0;border-top:1px solid #2d3154;margin:12px 0;" />
    """, unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Disaster Control", "Rescue Operations", "Resource Hub"],
        icons=["", "", "", ""],
        menu_icon=None,
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "#13152a"},
            "nav-link": {
                "font-size": "0.95rem", 
                "text-align": "left", 
                "margin": "2px 0", 
                "--hover-color": "#1e2140"
            },
            "nav-link-selected": {
                "background-color": "#3498db", 
                "color": "#ffffff", 
                "border-radius": "8px"
            },
            "icon": {"display": "none"},
        },
    )
    
    st.markdown(f"""
    <hr style="border:0;border-top:1px solid #2d3154;margin:12px 0;" />
    <div style="color:#a0a8c0;font-size:0.82rem;">
      DAA Project<br/>
      {datetime.now().strftime("%b %d, %Y")}
    </div>
    """, unsafe_allow_html=True)

# Route to selected page
if selected == "Dashboard":
    dashboard.render()
elif selected == "Disaster Control":
    disaster_control.render()
elif selected == "Rescue Operations":
    rescue_ops.render()
elif selected == "Resource Hub":
    resource_hub.render()
