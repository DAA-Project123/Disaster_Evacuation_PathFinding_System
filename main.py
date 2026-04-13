import ui.pygame_compat  # noqa: F401 — env + pygame shims before pygame_gui
import pygame

from ui import theme
from ui.window import Window


def main():
    pygame.init()
    pygame.display.set_caption("Veridian Rescue - Disaster Management System")
    screen = pygame.display.set_mode((theme.WINDOW_W, theme.WINDOW_H))
    clock = pygame.time.Clock()
    window = Window(screen, clock)
    window.run()
    pygame.quit()


if __name__ == "__main__":
    main()

