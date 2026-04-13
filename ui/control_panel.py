from __future__ import annotations

import ui.pygame_compat  # noqa: F401 — must load before pygame_gui
import pygame
import pygame_gui

from core.algorithm_selector import select_and_run
from core.data_loader import save_disaster_events
from core.disaster_manager import block_road, spread_disaster, unblock_road
from core.dynamic_obstacles import block_road_live
from core.greedy_selector import nearest_team_to_target
from core.mission_manager import MissionManager
from core.resource_manager import ResourceManager
from ui import theme


class ControlPanel:
    """Right side operational control panel using pygame_gui widgets."""

    RECT = pygame.Rect(theme.MAP_PANEL_W, 0, theme.CONTROL_PANEL_W, theme.CONTROL_PANEL_H)

    def __init__(self, screen, app_state, ui_manager):
        self.screen = screen
        self.state = app_state
        self.manager = ui_manager
        self.active_tab = "rescue"
        self.font = pygame.font.SysFont("arial", 14)
        self.font_small = pygame.font.SysFont("consolas", 12)
        self.mission_manager = MissionManager()
        self.resource_manager = ResourceManager()
        self.widgets = {}
        self._build_widgets()

    def _wrect(self, x, y, w, h):
        return pygame.Rect(self.RECT.x + x, self.RECT.y + y, w, h)

    def _build_widgets(self):
        x = 10
        tab_w = (theme.CONTROL_PANEL_W - 25) // 4
        self.widgets["tab_city"] = pygame_gui.elements.UIButton(self._wrect(x + 0 * tab_w, 10, tab_w - 4, 30), "City", self.manager)
        self.widgets["tab_disaster"] = pygame_gui.elements.UIButton(self._wrect(x + 1 * tab_w, 10, tab_w - 4, 30), "Disaster", self.manager)
        self.widgets["tab_rescue"] = pygame_gui.elements.UIButton(self._wrect(x + 2 * tab_w, 10, tab_w - 4, 30), "Rescue", self.manager)
        self.widgets["tab_resources"] = pygame_gui.elements.UIButton(self._wrect(x + 3 * tab_w, 10, tab_w - 4, 30), "Resources", self.manager)

        self.widgets["city_dropdown"] = pygame_gui.elements.UIDropDownMenu(
            ["Veridian City", "Harborfield", "Maplecrest"],
            self.state.active_city,
            self._wrect(20, 70, 220, 30),
            self.manager,
        )
        self.widgets["load_city_btn"] = pygame_gui.elements.UIButton(self._wrect(250, 70, 120, 30), "Load City", self.manager)

        self.widgets["speed_slider"] = pygame_gui.elements.UIHorizontalSlider(
            self._wrect(20, 115, 350, 24),
            start_value=1,
            value_range=(0.5, 4.0),
            manager=self.manager,
        )

        self.widgets["disaster_type"] = pygame_gui.elements.UIDropDownMenu(
            ["Flood", "Earthquake", "Fire", "Landslide", "Congestion"],
            "Flood",
            self._wrect(20, 70, 170, 30),
            self.manager,
        )
        self.widgets["epicenter"] = pygame_gui.elements.UIDropDownMenu(
            self._node_options(),
            self._node_options()[0],
            self._wrect(200, 70, 170, 30),
            self.manager,
        )
        self.widgets["severity_slider"] = pygame_gui.elements.UIHorizontalSlider(
            self._wrect(20, 110, 170, 24), start_value=3, value_range=(1, 4), manager=self.manager
        )
        self.widgets["radius_slider"] = pygame_gui.elements.UIHorizontalSlider(
            self._wrect(200, 110, 170, 24), start_value=2, value_range=(1, 5), manager=self.manager
        )
        self.widgets["trigger_disaster"] = pygame_gui.elements.UIButton(self._wrect(20, 145, 180, 30), "Trigger Disaster", self.manager)
        self.widgets["block_road"] = pygame_gui.elements.UIButton(self._wrect(210, 145, 160, 30), "Block Selected Road", self.manager)
        self.widgets["restore_roads"] = pygame_gui.elements.UIButton(self._wrect(20, 180, 180, 30), "Restore All Roads", self.manager)

        self.widgets["team_dropdown"] = pygame_gui.elements.UIDropDownMenu(
            self._team_options() or ["No available teams"],
            (self._team_options() or ["No available teams"])[0],
            self._wrect(20, 70, 350, 30),
            self.manager,
        )
        self.widgets["pick_map_target"] = pygame_gui.elements.UIButton(self._wrect(20, 110, 170, 30), "Pick from Map", self.manager)
        self.widgets["target_dropdown"] = pygame_gui.elements.UIDropDownMenu(
            self._victim_options() or ["No targets"],
            (self._victim_options() or ["No targets"])[0],
            self._wrect(200, 110, 170, 30),
            self.manager,
        )
        self.widgets["strategy_nearest"] = pygame_gui.elements.UIButton(self._wrect(20, 145, 110, 30), "Nearest", self.manager)
        self.widgets["strategy_priority"] = pygame_gui.elements.UIButton(self._wrect(140, 145, 140, 30), "Highest Priority", self.manager)
        self.widgets["compute_paths"] = pygame_gui.elements.UIButton(self._wrect(20, 180, 170, 30), "Compute Paths", self.manager)
        self.widgets["dispatch_team"] = pygame_gui.elements.UIButton(self._wrect(200, 180, 170, 30), "Dispatch Team", self.manager)

        self.widgets["resource_dropdown"] = pygame_gui.elements.UIDropDownMenu(
            self._resource_options(),
            self._resource_options()[0],
            self._wrect(20, 70, 170, 30),
            self.manager,
        )
        self.widgets["safezone_dropdown"] = pygame_gui.elements.UIDropDownMenu(
            self._safezone_options(),
            self._safezone_options()[0],
            self._wrect(200, 70, 170, 30),
            self.manager,
        )
        self.widgets["qty_entry"] = pygame_gui.elements.UITextEntryLine(self._wrect(20, 110, 120, 30), self.manager)
        self.widgets["dispatch_supply"] = pygame_gui.elements.UIButton(self._wrect(150, 110, 220, 30), "Dispatch Supply", self.manager)
        self.widgets["qty_entry"].set_text("10")
        self._set_visibility()

    def _set_visibility(self):
        tab_map = {
            "city": ["city_dropdown", "load_city_btn", "speed_slider"],
            "disaster": [
                "disaster_type",
                "epicenter",
                "severity_slider",
                "radius_slider",
                "trigger_disaster",
                "block_road",
                "restore_roads",
            ],
            "rescue": [
                "team_dropdown",
                "pick_map_target",
                "target_dropdown",
                "strategy_nearest",
                "strategy_priority",
                "compute_paths",
                "dispatch_team",
            ],
            "resources": ["resource_dropdown", "safezone_dropdown", "qty_entry", "dispatch_supply"],
        }
        always = {"tab_city", "tab_disaster", "tab_rescue", "tab_resources"}
        visible = set(tab_map[self.active_tab]) | always
        for name, widget in self.widgets.items():
            if name in visible:
                widget.show()
            else:
                widget.hide()

    def _node_options(self):
        nodes = (self.state.city_graph_data or {}).get("nodes", [])
        out = [f"{n['id']} - {n.get('name', n['id'])}" for n in nodes]
        return out or ["N/A"]

    def _team_options(self):
        opts = []
        for u in self.state.rescue_units:
            if u.get("status", "available") != "available":
                continue
            fuel = int(u.get("fuel_remaining", 0))
            opts.append(f"{u['unit_id']} | {u['name']} ({u['unit_type']}) fuel:{fuel}%")
        return opts

    def _victim_options(self):
        out = []
        for n in (self.state.city_graph_data or {}).get("nodes", []):
            if int(n.get("people_stranded", 0)) > 0:
                out.append(f"{n['id']} - {n.get('name', n['id'])}")
        return out

    def _resource_options(self):
        inv = self.resource_manager.get_inventory().to_dict(orient="records")
        out = [f"{r['resource_id']} - {r['name']} ({int(r['available'])})" for r in inv]
        return out or ["No resources"]

    def _safezone_options(self):
        return [f"{z['id']} - {z.get('name', z['id'])}" for z in self.state.safe_zones] or ["No safe zones"]

    def _refresh_dynamic_data(self):
        self.state.active_missions = self.mission_manager.load()

    def handle_event(self, event):
        if event.type != pygame_gui.UI_BUTTON_PRESSED and event.type != pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            return
        if event.ui_element == self.widgets["tab_city"]:
            self.active_tab = "city"
            self._set_visibility()
            return
        if event.ui_element == self.widgets["tab_disaster"]:
            self.active_tab = "disaster"
            self._set_visibility()
            return
        if event.ui_element == self.widgets["tab_rescue"]:
            self.active_tab = "rescue"
            self._set_visibility()
            return
        if event.ui_element == self.widgets["tab_resources"]:
            self.active_tab = "resources"
            self._set_visibility()
            return
        if event.ui_element == self.widgets["load_city_btn"]:
            city = self.widgets["city_dropdown"].selected_option
            self.state.load_city(city)
            self.state.log(f"Loaded city {city}", "success")
            return
        if event.ui_element == self.widgets["pick_map_target"]:
            self.state.select_target_mode = True
            self.state.log("Click a node on map to select target.", "info")
            return
        if event.ui_element == self.widgets["trigger_disaster"]:
            epi = self.widgets["epicenter"].selected_option.split(" - ")[0]
            severity_names = {1: "low", 2: "medium", 3: "high", 4: "critical"}
            sev = severity_names[round(self.widgets["severity_slider"].get_current_value())]
            radius = round(self.widgets["radius_slider"].get_current_value())
            dtype = self.widgets["disaster_type"].selected_option.lower()
            ev = spread_disaster(self.state.G, epi, radius, dtype, sev)
            self.state.disaster_events.append(ev)
            save_disaster_events(self.state.disaster_events, self.state.active_city)
            self.state.log(f"Disaster triggered: {dtype} at {epi}", "warning")
            return
        if event.ui_element == self.widgets["block_road"]:
            edge = next(iter(self.state.G.edges), None)
            if edge:
                u, v = edge
                self.state.disaster_events = block_road(u, v, "manual", self.state.disaster_events)
                save_disaster_events(self.state.disaster_events, self.state.active_city)
                affected = block_road_live(self.state.G, u, v, self.state.active_missions)
                self.state.log(f"Road blocked: {u}-{v}, affected: {len(affected['affected_missions'])}", "warning")
            return
        if event.ui_element == self.widgets["restore_roads"]:
            for ev in self.state.disaster_events:
                for pair in list(ev.get("blocked_edges", [])):
                    self.state.disaster_events = unblock_road(pair[0], pair[1], self.state.disaster_events)
            save_disaster_events(self.state.disaster_events, self.state.active_city)
            self.state.log("All blocked roads restored.", "success")
            return
        if event.ui_element == self.widgets["compute_paths"]:
            self._compute_paths()
            return
        if event.ui_element == self.widgets["dispatch_team"]:
            self._dispatch_team()
            return
        if event.ui_element == self.widgets["dispatch_supply"]:
            self._dispatch_supply()
            return
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.widgets["target_dropdown"]:
                self.state.selected_target_node = event.text.split(" - ")[0]
            elif event.ui_element == self.widgets["team_dropdown"]:
                self.state.selected_team_id = event.text.split(" | ")[0]

    def _compute_paths(self):
        if not self.state.selected_team_id:
            self.state.selected_team_id = self.widgets["team_dropdown"].selected_option.split(" | ")[0]
        if not self.state.selected_target_node:
            self.state.selected_target_node = self.widgets["target_dropdown"].selected_option.split(" - ")[0]
        team = next((t for t in self.state.rescue_units if t["unit_id"] == self.state.selected_team_id), None)
        if not team or not self.state.selected_target_node:
            self.state.log("Select team and target before path computation.", "error")
            return
        out = select_and_run(
            self.state.G,
            team.get("current_node"),
            self.state.selected_target_node,
            self.state.disaster_events,
            self.state.positions,
            self.state.city_graph_data,
            unit_type="helicopter" if team.get("unit_type") == "helicopter" else "ground",
        )
        self.state.last_algorithm_results = out
        best = out["recommended"]
        self.state.log(
            f"Best algorithm {best['algorithm']} length={best['path_length']} explored={best['nodes_explored']}",
            "success",
        )

    def _dispatch_team(self):
        if self.state.last_algorithm_results is None:
            self._compute_paths()
            if self.state.last_algorithm_results is None:
                return
        team_id = self.state.selected_team_id or self.widgets["team_dropdown"].selected_option.split(" | ")[0]
        team = next((t for t in self.state.rescue_units if t["unit_id"] == team_id), None)
        target = self.state.selected_target_node or self.widgets["target_dropdown"].selected_option.split(" - ")[0]
        if not team or not target:
            return
        node_map = {n["id"]: n for n in self.state.city_graph_data.get("nodes", [])}
        best = self.state.last_algorithm_results["recommended"]
        mission = self.mission_manager.create_mission(
            team=team,
            target_node=target,
            target_name=node_map.get(target, {}).get("name", target),
            path=best["path"],
            path_names=[node_map.get(i, {}).get("name", i) for i in best["path"]],
            algorithm_result=best,
            people_at_target=int(node_map.get(target, {}).get("people_stranded", 0)),
            injury_level=node_map.get(target, {}).get("injury_level", "low"),
            city=self.state.active_city,
        )
        self._refresh_dynamic_data()
        self.state.log(
            f"Team {team['name']} dispatched to {node_map.get(target, {}).get('name', target)} via {best['algorithm']}",
            "success",
        )
        self.state.pending_action = ("mission_dispatched", mission["mission_id"])

    def _dispatch_supply(self):
        res_id = self.widgets["resource_dropdown"].selected_option.split(" - ")[0]
        zone_id = self.widgets["safezone_dropdown"].selected_option.split(" - ")[0]
        zone_name = self.widgets["safezone_dropdown"].selected_option.split(" - ")[1]
        try:
            qty = int(self.widgets["qty_entry"].get_text() or "0")
            self.resource_manager.distribute(res_id, qty, zone_id, zone_name)
            self.state.log(f"Supply dispatched: {res_id} x{qty} to {zone_name}", "success")
        except Exception as exc:
            self.state.log(f"Supply dispatch failed: {exc}", "error")

    def update(self, dt):
        del dt
        self.state.sim_speed = float(self.widgets["speed_slider"].get_current_value())
        self._refresh_dynamic_data()

    def _draw_card(self, surface, rect, title, rows, color):
        pygame.draw.rect(surface, (18, 22, 34), rect, border_radius=8)
        pygame.draw.rect(surface, theme.PANEL_BORDER, rect, 1, border_radius=8)
        title_rect = pygame.Rect(rect.x, rect.y, rect.w, 24)
        pygame.draw.rect(surface, color, title_rect, border_top_left_radius=8, border_top_right_radius=8)
        surface.blit(self.font.render(title, True, theme.TEXT_PRIMARY), (title_rect.x + 8, title_rect.y + 4))
        y = rect.y + 30
        for k, v in rows:
            surface.blit(self.font_small.render(str(k), True, theme.TEXT_MUTED), (rect.x + 8, y))
            surface.blit(self.font_small.render(str(v), True, theme.TEXT_SECONDARY), (rect.x + 170, y))
            y += 16

    def draw(self):
        surface = self.screen
        pygame.draw.rect(surface, theme.PANEL_BG, self.RECT, border_radius=8)
        pygame.draw.rect(surface, theme.PANEL_BORDER, self.RECT, 1, border_radius=8)
        self._draw_tab_content()

    def _draw_tab_content(self):
        if self.active_tab == "city":
            self._draw_city_tab()
        elif self.active_tab == "disaster":
            self._draw_disaster_tab()
        elif self.active_tab == "rescue":
            self._draw_rescue_tab()
        elif self.active_tab == "resources":
            self._draw_resources_tab()

    def _draw_city_tab(self):
        nodes = len((self.state.city_graph_data or {}).get("nodes", []))
        edges = len((self.state.city_graph_data or {}).get("edges", []))
        rows = [
            ("Nodes", nodes),
            ("Edges", edges),
            ("Safe Zones", len(self.state.safe_zones)),
            ("Rescue Teams", len(self.state.rescue_units)),
            ("Sim Speed", f"{self.state.sim_speed:.1f}x"),
        ]
        self._draw_card(self.screen, pygame.Rect(self.RECT.x + 20, 160, 360, 120), "City Stats", rows, theme.ACCENT_BLUE)

    def _draw_disaster_tab(self):
        rows = [("Active", len([e for e in self.state.disaster_events if e.get("active")])), ("Blocked roads", sum(len(e.get("blocked_edges", [])) for e in self.state.disaster_events))]
        self._draw_card(self.screen, pygame.Rect(self.RECT.x + 20, 220, 360, 90), "Disaster Summary", rows, theme.ACCENT_RED)

    def _draw_rescue_tab(self):
        target = self.state.selected_target_node or "-"
        team = self.state.selected_team_id or "-"
        rec = nearest_team_to_target(
            self.state.G,
            target,
            [u for u in self.state.rescue_units if u.get("status", "available") == "available"],
            self.state.disaster_events,
            self.state.city_graph_data,
        ) if target != "-" else {}
        rows = [("Selected Team", team), ("Target", target), ("Recommendation", rec.get("team", {}).get("unit_id", "-"))]
        self._draw_card(self.screen, pygame.Rect(self.RECT.x + 20, 220, 360, 95), "Rescue Control", rows, theme.ACCENT_GREEN)
        if self.state.last_algorithm_results:
            best = self.state.last_algorithm_results["recommended"]
            rows = [
                ("Algorithm", best["algorithm"]),
                ("Path Length", best["path_length"]),
                ("Nodes Explored", best["nodes_explored"]),
                ("Time (ms)", f"{best['runtime_ms']:.2f}"),
            ]
            self._draw_card(self.screen, pygame.Rect(self.RECT.x + 20, 320, 360, 95), "Best Result", rows, theme.ACCENT_PURPLE)

    def _draw_resources_tab(self):
        log_df = self.resource_manager.get_distribution_log(limit=5)
        rows = [("Entries", len(log_df.index)), ("Inventory Items", len(self.resource_manager.get_inventory().index))]
        self._draw_card(self.screen, pygame.Rect(self.RECT.x + 20, 160, 360, 90), "Resource Hub", rows, theme.ACCENT_ORANGE)

