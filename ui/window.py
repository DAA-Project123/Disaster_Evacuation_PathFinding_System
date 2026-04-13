from __future__ import annotations

import ui.pygame_compat  # noqa: F401 — must load before pygame_gui
import pygame
import pygame_gui

from ui import theme
from ui.chart_panel import ChartPanel
from ui.control_panel import ControlPanel
from ui.log_panel import LogPanel
from ui.map_panel import MapPanel


class AppState:
    """Single shared mutable state consumed by every panel."""

    def __init__(self):
        self.running = True
        self.active_city = "Veridian City"
        self.city_graph_data = None
        self.G = None
        self.positions = {}
        self.disaster_events = []
        self.safe_zones = []
        self.rescue_units = []
        self.active_missions = []
        self.selected_team_id = None
        self.selected_target_node = None
        self.last_algorithm_results = None
        self.sim_speed = 1.0
        self.show_algo_comparison = False
        self.log_entries = []
        self.map_offset = [0, 0]
        self.map_zoom = 1.0
        self.select_target_mode = False
        self.pending_action = None

    def load_city(self, city_name: str):
        from core.data_loader import (
            load_city_graph,
            load_disaster_events,
            load_rescue_units,
            load_safe_zones,
        )
        from core.graph_engine import load_graph
        from core.mission_manager import MissionManager

        self.active_city = city_name
        self.city_graph_data = load_city_graph(city_name)
        self.G = load_graph(self.city_graph_data)
        self.positions = self._compute_screen_positions()
        self.disaster_events = load_disaster_events(city_name)
        self.safe_zones = load_safe_zones(city_name)
        self.rescue_units = load_rescue_units(city_name)
        self.active_missions = MissionManager().load()
        self.selected_team_id = None
        self.selected_target_node = None
        self.last_algorithm_results = None
        self.log(f"City loaded: {city_name}", "info")

    def _compute_screen_positions(self) -> dict:
        nodes = (self.city_graph_data or {}).get("nodes", [])
        if not nodes:
            return {}
        xs = [float(n.get("x", 0.0)) for n in nodes]
        ys = [float(n.get("y", 0.0)) for n in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(1.0, max_x - min_x)
        span_y = max(1.0, max_y - min_y)
        pad = 40
        out = {}
        for n in nodes:
            nx = (float(n.get("x", 0.0)) - min_x) / span_x
            ny = (float(n.get("y", 0.0)) - min_y) / span_y
            px = pad + nx * (theme.MAP_PANEL_W - (2 * pad))
            py = pad + ny * (theme.MAP_PANEL_H - (2 * pad))
            out[n["id"]] = (px, py)
        return out

    def log(self, message: str, level: str = "info"):
        import datetime

        self.log_entries.append(
            {
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "message": message,
                "level": level,
            }
        )
        if len(self.log_entries) > 200:
            self.log_entries = self.log_entries[-200:]


class Window:
    """Main window, event routing, update loop, and render orchestration."""

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.ui_manager = pygame_gui.UIManager(
            (theme.WINDOW_W, theme.WINDOW_H),
            "ui/theme.json",
        )
        self.app_state = AppState()
        self.app_state.load_city(self.app_state.active_city)
        self.map_panel = MapPanel(screen, self.app_state, self.ui_manager)
        self.control_panel = ControlPanel(screen, self.app_state, self.ui_manager)
        self.chart_panel = ChartPanel(screen, self.app_state)
        self.log_panel = LogPanel(screen, self.app_state)

    def run(self):
        while self.app_state.running:
            dt = self.clock.tick(theme.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.app_state.running = False
                self.ui_manager.process_events(event)
                self.control_panel.handle_event(event)
                self.map_panel.handle_event(event)
                self.log_panel.handle_event(event)
            self.ui_manager.update(dt)
            self.map_panel.update(dt)
            self.control_panel.update(dt)
            self.chart_panel.update()
            self.log_panel.update()

            self.screen.fill(theme.BG_DARK)
            self.map_panel.draw()
            self.chart_panel.draw()
            self.control_panel.draw()
            self.log_panel.draw()
            self.ui_manager.draw_ui(self.screen)
            pygame.display.flip()

