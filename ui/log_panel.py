from __future__ import annotations

import pygame

from ui import theme


class LogPanel:
    """Bottom-right scrolling event log panel."""

    RECT = pygame.Rect(
        theme.MAP_PANEL_W - theme.LOG_PANEL_H,
        theme.MAP_PANEL_H,
        theme.CONTROL_PANEL_W + theme.LOG_PANEL_H,
        theme.CHART_PANEL_H,
    )
    LEVEL_COLORS = {
        "info": theme.TEXT_SECONDARY,
        "success": theme.ACCENT_GREEN,
        "warning": theme.ACCENT_YELLOW,
        "error": theme.ACCENT_RED,
    }

    def __init__(self, screen, app_state):
        self.screen = screen
        self.state = app_state
        self.scroll_offset = 0
        self.last_log_count = 0
        self.font = pygame.font.SysFont("consolas", 12)

    def update(self):
        if len(self.state.log_entries) > self.last_log_count:
            self.scroll_offset = 0
            self.last_log_count = len(self.state.log_entries)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.RECT.collidepoint(getattr(event, "pos", (-1, -1))):
            if event.button == 4:
                self.scroll_offset += 20
            if event.button == 5:
                self.scroll_offset = max(0, self.scroll_offset - 20)

    def draw(self):
        surf = pygame.Surface((self.RECT.w, self.RECT.h))
        surf.fill((18, 22, 34))
        pygame.draw.rect(surf, theme.PANEL_BORDER, surf.get_rect(), 1)
        title = self.font.render("Event Log", True, theme.TEXT_PRIMARY)
        surf.blit(title, (8, 6))
        y = self.RECT.h - 20 + self.scroll_offset
        for entry in reversed(self.state.log_entries):
            level = entry.get("level", "info")
            msg = f"[{entry.get('time', '--:--:--')}] {entry.get('message', '')}"
            txt = self.font.render(msg, True, self.LEVEL_COLORS.get(level, theme.TEXT_SECONDARY))
            y -= 16
            if y < 24:
                break
            surf.blit(txt, (8, y))
        self.screen.blit(surf, self.RECT.topleft)

