import pygame
from pygame import Surface
from lib.sprite import Sprite
import lib.vector as vector

import assets
from contexts import Context
from config import WINDOW_SIZE, WINDOW_HEIGHT
import debug

class DebugContext(Context):
  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.time = 0

  def handle_press(ctx, button):
    if button == pygame.K_ESCAPE:
      return ctx.close()

  def update(ctx):
    ctx.time += 1

  def view(ctx):
    sprites = []

    bg_image = Surface(WINDOW_SIZE)
    bg_image.fill((0, 0, 255))
    sprites += [Sprite(image=bg_image)]

    stdout = debug.buffer
    if stdout:
      sprites += [Sprite(
        image=assets.ttf["normal"].render(stdout),
        pos=(0, 0),
      )]
    else:
      sprites += [Sprite(
        image=assets.ttf["normal"].render("No messages to show."),
        pos=vector.scale(WINDOW_SIZE, 1 / 2),
        origin=Sprite.ORIGIN_CENTER,
      )]

    if ctx.time % 60 < 30:
      sprites += [Sprite(
        image=assets.ttf["normal"].render("[Press ESC to return]"),
        pos=(0, WINDOW_HEIGHT),
        origin=Sprite.ORIGIN_BOTTOMLEFT,
      )]

    return [sprites]
