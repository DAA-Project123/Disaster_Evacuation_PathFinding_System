from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pygame

from ui import theme


class ChartPanel:
    """Renders algorithm comparison charts into a pygame surface."""

    RECT = pygame.Rect(0, theme.MAP_PANEL_H, theme.MAP_PANEL_W - theme.LOG_PANEL_H, theme.CHART_PANEL_H)

    def __init__(self, screen, app_state):
        self.screen = screen
        self.state = app_state
        self.font = pygame.font.SysFont("arial", 14)
        self.surface = self._render_placeholder()
        self.last_results_id = None

    def update(self):
        if self.state.last_algorithm_results is None:
            self.surface = self._render_placeholder()
            self.last_results_id = None
            return
        rid = id(self.state.last_algorithm_results)
        if rid != self.last_results_id:
            self.last_results_id = rid
            self.surface = self._render_comparison_chart()

    def _render_comparison_chart(self) -> pygame.Surface:
        results = self.state.last_algorithm_results.get("all_results", [])
        algos = [r["Algorithm"] for r in results]
        nodes = [r["Nodes Explored"] for r in results]
        times = [r["Time (ms)"] for r in results]
        lengths = [r["Path Length"] if r["Path Found"] else 0 for r in results]
        found = [r["Path Found"] for r in results]
        best = self.state.last_algorithm_results["recommended"]["algorithm"]
        colors = []
        color_cycle = list(theme.AGENT_COLORS.values())
        for i, algo in enumerate(algos):
            if not found[i]:
                colors.append("#5a6478")
            elif algo == best:
                colors.append("#7fffd4")
            else:
                c = color_cycle[i % len(color_cycle)]
                colors.append("#%02x%02x%02x" % c)
        fig, axes = plt.subplots(1, 3, figsize=(12, 3.1))
        fig.patch.set_facecolor("#161b2a")
        data = [nodes, times, lengths]
        titles = ["Nodes Explored", "Execution Time ms", "Path Length"]
        for idx, ax in enumerate(axes):
            ax.set_facecolor("#1a1f35")
            ax.barh(algos, data[idx], color=colors)
            ax.set_title(titles[idx], color="white", fontsize=10)
            ax.tick_params(axis="x", colors="white")
            ax.tick_params(axis="y", colors="white")
            for i, f in enumerate(found):
                if not f:
                    ax.text(0.05, i, "No path", color="#bbbbbb", va="center", transform=ax.get_yaxis_transform())
        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(
            buf,
            format="png",
            dpi=100,
            facecolor=fig.get_facecolor(),
            edgecolor="none",
            bbox_inches="tight",
            pad_inches=0.05,
        )
        plt.close(fig)
        buf.seek(0)
        surface = pygame.image.load(buf, "chart.png")
        if surface.get_alpha() is None:
            surface = surface.convert_alpha()
        return pygame.transform.smoothscale(surface, (self.RECT.w, self.RECT.h))

    def _render_placeholder(self) -> pygame.Surface:
        surface = pygame.Surface((self.RECT.w, self.RECT.h))
        surface.fill(theme.PANEL_BG)
        title = self.font.render("Select a team and target, then click Compute Paths", True, theme.TEXT_SECONDARY)
        sub = self.font.render("Algorithm comparison will appear here", True, theme.TEXT_MUTED)
        surface.blit(title, ((self.RECT.w - title.get_width()) // 2, self.RECT.h // 2 - 20))
        surface.blit(sub, ((self.RECT.w - sub.get_width()) // 2, self.RECT.h // 2 + 5))
        return surface

    def draw(self):
        self.screen.blit(self.surface, self.RECT.topleft)
        pygame.draw.rect(self.screen, theme.PANEL_BORDER, self.RECT, 1)
        txt = self.font.render(
            "Algorithm Comparison - Time(ms) | Nodes Explored | Path Length",
            True,
            theme.TEXT_SECONDARY,
        )
        self.screen.blit(txt, (self.RECT.x + 8, self.RECT.y + 6))

