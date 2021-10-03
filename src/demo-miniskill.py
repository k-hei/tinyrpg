import pygame
from pygame import Surface
import lib.keyboard as keyboard
from contexts import Context
from contexts.app import App
from comps.miniskill import Miniskill
from skills.attack.blitzritter import Blitzritter
from skills.magic.glacio import Glacio
from skills.ailment.virus import Virus
from skills.support.sana import Sana
from colors.palette import WHITE
from lib.sprite import Sprite

WINDOW_SIZE = (128, 32)

class MiniskillContext(Context):
  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.skills = [Blitzritter, Glacio, Virus, Sana]
    ctx.skill = ctx.skills[0]

  def enter(ctx):
    super().enter()
    ctx.miniskill = Miniskill(skill=ctx.skill)
    ctx.miniskill.enter()
    ctx.skill = ctx.skills[(ctx.skills.index(ctx.skill) + 1) % len(ctx.skills)]

  def handle_press(ctx, button):
    if ctx.miniskill and ctx.miniskill.anims:
      return False

    if keyboard.get_state(button) > 1:
      return False

    if button in (pygame.K_SPACE, pygame.K_RETURN):
      if ctx.miniskill:
        ctx.miniskill.exit(on_end=lambda: setattr(ctx, "miniskill", None))
      else:
        ctx.enter()

  def update(ctx):
    ctx.miniskill and ctx.miniskill.update()

  def view(ctx):
    bg_image = Surface(WINDOW_SIZE)
    bg_image.fill(WHITE)
    return (
      [Sprite(image=bg_image)]
      + (Sprite.move_all(ctx.miniskill.view(), (4, WINDOW_SIZE[1] / 2)) if ctx.miniskill else [])
      + super().view()
    )

App(
  title="miniskill demo",
  context=MiniskillContext(),
  size=WINDOW_SIZE,
).init()
