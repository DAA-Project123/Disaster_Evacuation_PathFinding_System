"""Patches pygame for libraries that expect symbols on the package root."""

import os
import sys

# macOS: two copies of libSDL2 (Homebrew + pygame wheel) register duplicate ObjC classes
# and often crash. Strip DYLD overrides before native code loads.
if sys.platform == "darwin":
    os.environ.pop("DYLD_LIBRARY_PATH", None)
    os.environ.pop("DYLD_FALLBACK_LIBRARY_PATH", None)

import pygame

# pygame_gui imports DIRECTION_LTR from pygame; some pygame builds only expose these
# on pygame.font (e.g. certain Python 3.14 wheels).
if not hasattr(pygame, "DIRECTION_LTR"):
    try:
        from pygame.font import DIRECTION_LTR as _LTR, DIRECTION_RTL as _RTL
    except ImportError:
        _LTR, _RTL = 0, 1
    pygame.DIRECTION_LTR = _LTR
    pygame.DIRECTION_RTL = _RTL

# pygame_gui imports FRect from pygame; some builds only register it on pygame.rect.
if not hasattr(pygame, "FRect"):
    try:
        from pygame.rect import FRect as _FRect
    except ImportError:
        _FRect = pygame.Rect
    pygame.FRect = _FRect
