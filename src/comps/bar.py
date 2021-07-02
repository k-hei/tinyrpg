import pygame
from pygame import Surface, Rect
from assets import load as use_assets
from text import render as render_text
from filters import recolor
from palette import WHITE
from config import WINDOW_HEIGHT
from sprite import Sprite

from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp

class Bar:
  MARGIN = 8
  PADDING_X = 12
  PADDING_Y = 11
  ENTER_DURATION = 8
  EXIT_DURATION = 6

  def __init__(bar):
    bar.index = 0
    bar.message = None
    bar.surface = None
    bar.anim = None
    bar.exiting = False

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
      message = recolor(text, WHITE)
      bar.surface.blit(message, (Bar.PADDING_X, Bar.PADDING_Y))
    return bar.surface

  def enter(bar, on_end=None):
    bar.exiting = False
    bar.anim = TweenAnim(duration=Bar.ENTER_DURATION, on_end=on_end)

  def exit(bar, on_end=None):
    bar.exiting = True
    bar.anim = TweenAnim(duration=Bar.EXIT_DURATION, on_end=on_end)

  def view(bar):
    assets = use_assets()
    sprite = bar.render()
    start_y = WINDOW_HEIGHT
    end_y = WINDOW_HEIGHT - bar.surface.get_height() - Bar.MARGIN
    x = Bar.MARGIN
    y = start_y if bar.exiting else end_y
    if bar.anim:
      t = bar.anim.update()
      if bar.exiting:
        t = 1 - t
      else:
        t = ease_out(t)
      y = lerp(start_y, end_y, t)
      if bar.anim.done:
        bar.anim = None
    else:
      bar.update()
    return [Sprite(
      image=bar.surface,
      pos=(x, y),
      layer="ui"
    )]
