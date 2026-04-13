from __future__ import annotations

import math

import pygame

from core.disaster_manager import get_all_blocked_edges
from ui import theme


class MapPanel:
    """City graph render and agent animation layer."""

    RECT = pygame.Rect(0, 0, theme.MAP_PANEL_W, theme.MAP_PANEL_H)

    def __init__(self, screen, app_state, ui_manager):
        self.screen = screen
        self.state = app_state
        self.surface = pygame.Surface((theme.MAP_PANEL_W, theme.MAP_PANEL_H), pygame.SRCALPHA)
        self.agents = {}
        self.hover_node = None
        self.selected_node = None
        self.font_small = pygame.font.SysFont("arial", theme.FONT_SMALL[1])
        self.font_label = pygame.font.SysFont("arial", theme.FONT_LABEL[1])

    def _to_view(self, pos):
        x, y = pos
        ox, oy = self.state.map_offset
        z = self.state.map_zoom
        return (x * z + ox, y * z + oy)

    def draw(self):
        self.surface.fill(theme.PANEL_BG)
        self._draw_grid_bg()
        self._draw_edges()
        self._draw_active_paths()
        self._draw_nodes()
        self._draw_agents()
        self._draw_node_labels()
        self._draw_hover_tooltip()
        self._draw_panel_border()
        self.screen.blit(self.surface, self.RECT.topleft)

    def _draw_grid_bg(self):
        grid = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        for y in range(0, theme.MAP_PANEL_H, 30):
            for x in range(0, theme.MAP_PANEL_W, 30):
                pygame.draw.circle(grid, (*theme.TEXT_MUTED, 40), (x, y), 1)
        self.surface.blit(grid, (0, 0))

    def _draw_dashed_line(self, surface, color, start, end, width=1, dash_len=8):
        sx, sy = start
        ex, ey = end
        dx, dy = ex - sx, ey - sy
        dist = math.hypot(dx, dy)
        if dist <= 0:
            return
        ux, uy = dx / dist, dy / dist
        for i in range(0, int(dist), dash_len * 2):
            s = (sx + ux * i, sy + uy * i)
            e = (sx + ux * min(i + dash_len, dist), sy + uy * min(i + dash_len, dist))
            pygame.draw.line(surface, color, s, e, width)

    def _draw_edges(self):
        if not self.state.city_graph_data:
            return
        blocked = get_all_blocked_edges(self.state.disaster_events)
        for edge in self.state.city_graph_data.get("edges", []):
            u = edge["source"]
            v = edge["target"]
            pu = self._to_view(self.state.positions.get(u, (0, 0)))
            pv = self._to_view(self.state.positions.get(v, (0, 0)))
            edge_key = (u, v) if u <= v else (v, u)
            if edge_key in blocked:
                color = theme.EDGE_COLOR_BLOCKED
            elif edge.get("road_type") == "air" or bool(edge.get("air_only", False)):
                color = theme.EDGE_COLOR_AIR
            else:
                color = theme.EDGE_COLOR_NORMAL
            if edge.get("road_type") == "air" or bool(edge.get("air_only", False)):
                self._draw_dashed_line(self.surface, color, pu, pv, 1)
            else:
                pygame.draw.line(self.surface, color, pu, pv, theme.EDGE_WIDTH_NORMAL)
            if self.state.map_zoom > 1.2:
                mx, my = (pu[0] + pv[0]) / 2, (pu[1] + pv[1]) / 2
                txt = self.font_small.render(str(edge.get("base_travel_time_min", 1)), True, theme.TEXT_MUTED)
                self.surface.blit(txt, (mx, my))

    def _draw_nodes(self):
        if not self.state.city_graph_data:
            return
        for node in self.state.city_graph_data.get("nodes", []):
            node_id = node["id"]
            pos = self._to_view(self.state.positions.get(node_id, (0, 0)))
            ntype = node.get("type", "intersection")
            radius = theme.NODE_RADIUS.get(ntype, 10)
            color = theme.NODE_COLORS.get(ntype, theme.NODE_COLORS["intersection"])
            if int(node.get("people_stranded", 0)) > 0:
                self._draw_pulsing_ring(pos, radius + 4, theme.ACCENT_RED)
            if node_id == self.selected_node:
                pygame.draw.circle(self.surface, theme.TEXT_PRIMARY, pos, radius + 5, 2)
            elif node_id == self.hover_node:
                pygame.draw.circle(self.surface, theme.TEXT_SECONDARY, pos, radius + 4, 2)
            pygame.draw.circle(self.surface, color, pos, radius)
            pygame.draw.circle(self.surface, theme.PANEL_BORDER, pos, radius, 1)
            if ntype == "safe_zone":
                cap = max(1, int(node.get("capacity", 1)))
                occ = int(node.get("current_occupancy", 0))
                frac = max(0.0, min(1.0, occ / cap))
                bar = pygame.Rect(pos[0] - 15, pos[1] + radius + 3, 30, 4)
                pygame.draw.rect(self.surface, theme.TEXT_MUTED, bar, border_radius=2)
                fill = pygame.Rect(bar.x, bar.y, int(bar.w * frac), bar.h)
                pygame.draw.rect(self.surface, theme.ACCENT_GREEN, fill, border_radius=2)

    def _draw_pulsing_ring(self, pos, base_radius, color):
        pulse = math.sin(pygame.time.get_ticks() / 400.0) * 4
        overlay = pygame.Surface((base_radius * 4, base_radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(overlay, (*color, 90), (base_radius * 2, base_radius * 2), max(1, int(base_radius + pulse)), 2)
        self.surface.blit(overlay, (pos[0] - base_radius * 2, pos[1] - base_radius * 2))

    def _draw_arrow(self, surface, color, start, end):
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ang = math.atan2(end[1] - start[1], end[0] - start[0])
        size = 6
        p1 = (mx + math.cos(ang) * size, my + math.sin(ang) * size)
        p2 = (mx + math.cos(ang + 2.4) * size, my + math.sin(ang + 2.4) * size)
        p3 = (mx + math.cos(ang - 2.4) * size, my + math.sin(ang - 2.4) * size)
        pygame.draw.polygon(surface, color, [p1, p2, p3])

    def _draw_active_paths(self):
        for mission in self.state.active_missions:
            path = mission.get("path", [])
            step = int(mission.get("current_step", 0))
            for i in range(len(path) - 1):
                a = self._to_view(self.state.positions.get(path[i], (0, 0)))
                b = self._to_view(self.state.positions.get(path[i + 1], (0, 0)))
                color = theme.AGENT_COLORS.get(mission.get("team_type", ""), theme.EDGE_COLOR_PATH)
                if i < step:
                    color = tuple(max(0, c - 120) for c in color)
                pygame.draw.line(self.surface, color, a, b, theme.EDGE_WIDTH_PATH)
                self._draw_arrow(self.surface, color, a, b)
                label = self.font_small.render(str(i + 1), True, color)
                self.surface.blit(label, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))

    def _draw_agents(self):
        for agent in self.agents.values():
            agent.draw(self.surface)

    def _draw_node_labels(self):
        for node in (self.state.city_graph_data or {}).get("nodes", []):
            ntype = node.get("type", "intersection")
            if ntype not in {"safe_zone", "hospital", "shelter"} and self.state.map_zoom <= 1.5:
                continue
            pos = self._to_view(self.state.positions.get(node["id"], (0, 0)))
            txt = self.font_small.render(node.get("name", node["id"]), True, theme.TEXT_SECONDARY)
            self.surface.blit(txt, (pos[0] - txt.get_width() // 2, pos[1] - 22))

    def _draw_hover_tooltip(self):
        if not self.hover_node or not self.state.city_graph_data:
            return
        node = next((n for n in self.state.city_graph_data.get("nodes", []) if n["id"] == self.hover_node), None)
        if not node:
            return
        lines = [
            node.get("name", node["id"]),
            f"type: {node.get('type', 'intersection')}",
            f"zone: {node.get('zone', '-')}",
            f"stranded: {int(node.get('people_stranded', 0))}",
            f"risk: {float(node.get('survival_chance', 0.0)):.2f}",
        ]
        w = max(self.font_small.size(line)[0] for line in lines) + 14
        h = 8 + (len(lines) * 16)
        mx, my = pygame.mouse.get_pos()
        mx -= self.RECT.x
        my -= self.RECT.y
        box = pygame.Rect(mx + 12, my + 12, w, h)
        pygame.draw.rect(self.surface, (12, 15, 25), box, border_radius=6)
        pygame.draw.rect(self.surface, theme.PANEL_BORDER, box, 1, border_radius=6)
        for i, line in enumerate(lines):
            txt = self.font_small.render(line, True, theme.TEXT_PRIMARY)
            self.surface.blit(txt, (box.x + 6, box.y + 4 + (i * 16)))

    def _draw_panel_border(self):
        pygame.draw.rect(self.surface, theme.PANEL_BORDER, self.surface.get_rect(), 1, border_radius=8)

    def _sync_agents_to_missions(self):
        active_ids = set()
        for mission in self.state.active_missions:
            mid = mission.get("mission_id")
            unit_id = mission.get("team_id", mid)
            if not mission.get("path"):
                continue
            active_ids.add(unit_id)
            if unit_id not in self.agents:
                start = self._to_view(self.state.positions.get(mission["path"][0], (0, 0)))
                self.agents[unit_id] = AgentSprite(
                    unit_id=unit_id,
                    unit_type=mission.get("team_type", "ambulance"),
                    color=theme.AGENT_COLORS.get(mission.get("team_type", ""), theme.ACCENT_GREEN),
                    start_pos=start,
                )
            screen_path = [self._to_view(self.state.positions.get(n, (0, 0))) for n in mission.get("path", [])]
            self.agents[unit_id].set_path(screen_path, int(mission.get("current_step", 0)))
            self.agents[unit_id].status = mission.get("status", "idle")
        stale = [uid for uid in self.agents if uid not in active_ids]
        for uid in stale:
            self.agents.pop(uid, None)

    def update(self, dt: float):
        self._sync_agents_to_missions()
        for agent in self.agents.values():
            agent.update(dt, self.state.sim_speed)

    def _update_hover(self, mouse_pos):
        local = (mouse_pos[0] - self.RECT.x, mouse_pos[1] - self.RECT.y)
        closest = None
        closest_d = 20
        for node_id, pos in self.state.positions.items():
            px, py = self._to_view(pos)
            d = math.hypot(local[0] - px, local[1] - py)
            if d <= closest_d:
                closest = node_id
                closest_d = d
        self.hover_node = closest

    def _handle_click(self, mouse_pos):
        if not self.RECT.collidepoint(mouse_pos):
            return
        if not self.hover_node:
            return
        if self.state.select_target_mode:
            self.state.selected_target_node = self.hover_node
            self.state.select_target_mode = False
            self.state.log(f"Target selected from map: {self.hover_node}", "info")
            return
        self.selected_node = self.hover_node
        self.state.selected_target_node = self.hover_node

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._handle_click(event.pos)
            elif event.button == 4:
                self.state.map_zoom = min(3.0, self.state.map_zoom + 0.1)
            elif event.button == 5:
                self.state.map_zoom = max(0.5, self.state.map_zoom - 0.1)


class AgentSprite:
    """Visual actor that interpolates along a mission path."""

    def __init__(self, unit_id, unit_type, color, start_pos):
        self.unit_id = unit_id
        self.unit_type = unit_type
        self.color = color
        self.pos = list(start_pos)
        self.target_pos = list(start_pos)
        self.path_screen = [tuple(start_pos)]
        self.path_index = 0
        self.moving = False
        self.progress = 0.0
        self.status = "idle"
        self.carrying = 0
        self.trail = []

    def set_path(self, screen_positions, start_index: int):
        if not screen_positions:
            return
        self.path_screen = list(screen_positions)
        self.path_index = max(0, min(start_index, len(self.path_screen) - 1))
        self.pos = list(self.path_screen[self.path_index])
        if self.path_index < len(self.path_screen) - 1:
            self.target_pos = list(self.path_screen[self.path_index + 1])
            self.moving = True
        else:
            self.target_pos = list(self.path_screen[self.path_index])
            self.moving = False

    def lerp(self, a, b, t):
        return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]

    def update(self, dt: float, sim_speed: float):
        if not self.moving or len(self.path_screen) < 2:
            return
        cur = self.path_screen[self.path_index]
        nxt = self.path_screen[self.path_index + 1]
        distance = max(1e-6, math.hypot(nxt[0] - cur[0], nxt[1] - cur[1]))
        pixels_per_second = theme.AGENT_SPEED * sim_speed * 60
        self.progress += (pixels_per_second * dt) / distance
        self.pos = self.lerp(cur, nxt, min(1.0, self.progress))
        if self.progress >= 1.0:
            self.path_index += 1
            self.progress = 0.0
            if self.path_index >= len(self.path_screen) - 1:
                self.moving = False
                self.status = "arrived"
            else:
                self.target_pos = list(self.path_screen[self.path_index + 1])
        self.trail.append(tuple(self.pos))
        self.trail = self.trail[-20:]

    def draw(self, surface):
        for i, tpos in enumerate(self.trail):
            frac = (i + 1) / max(1, len(self.trail))
            r = max(2, int(theme.AGENT_RADIUS * frac * 0.6))
            col = (*self.color, int(200 * frac))
            ghost = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(ghost, col, (r * 2, r * 2), r)
            surface.blit(ghost, (tpos[0] - r * 2, tpos[1] - r * 2))
        pygame.draw.circle(surface, theme.TEXT_PRIMARY, self.pos, theme.AGENT_RADIUS + 3)
        pygame.draw.circle(surface, self.color, self.pos, theme.AGENT_RADIUS)
        status_color = {
            "en_route": theme.ACCENT_YELLOW,
            "rescued": theme.ACCENT_GREEN,
            "returning": theme.ACCENT_BLUE,
            "arrived": theme.ACCENT_GREEN,
        }.get(self.status, theme.TEXT_MUTED)
        pygame.draw.circle(surface, status_color, (self.pos[0] + 7, self.pos[1] - 7), 4)
        if self.unit_type == "helicopter":
            pygame.draw.line(surface, theme.TEXT_PRIMARY, (self.pos[0] - 10, self.pos[1] - 12), (self.pos[0] + 10, self.pos[1] - 12), 1)
            pygame.draw.line(surface, theme.TEXT_PRIMARY, (self.pos[0], self.pos[1] - 20), (self.pos[0], self.pos[1] - 4), 1)

