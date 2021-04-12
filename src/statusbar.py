import pygame
from pygame import Surface, Rect
from assets import load as use_assets
from text import render as render_text
from filters import recolor

class StatusBar:
  def __init__(bar):
    bar.message = None
    bar.surface = None
    bar.index = 0

  def print(bar, message):
    bar.message = message
    bar.index = 0

  def update(bar):
    if bar.message and bar.index < len(bar.message):
      bar.index += 1

  def render(bar):
    assets = use_assets()

    if not bar.surface:
      bar.surface = assets.sprites["statusbar"].copy()

    if bar.message and bar.index <= len(bar.message):
      bar.surface = assets.sprites["statusbar"].copy()
      content = bar.message[0:bar.index]
      text = render_text(content, assets.fonts["standard"])
      message = recolor(text, (0xFF, 0xFF, 0xFF))
      bar.surface.blit(message, (12, 11))
    return bar.surface
