import pygame
from contexts import Context
from contexts.choice import ChoiceContext, Choice
from comps.log import Log
from config import WINDOW_HEIGHT
from sprite import Sprite

class PromptContext(Context):
  def __init__(ctx, message, choices, required=False, on_choose=None, on_close=None):
    super().__init__(on_close=on_close)
    ctx.message = message
    ctx.choices = choices
    ctx.required = required
    ctx.on_choose = on_choose
    ctx.log = Log(autohide=False)

  def enter(ctx):
    ctx.log.print(ctx.message, on_end=ctx.open)

  def exit(ctx, choice):
    ctx.log.exit(on_end=lambda: ctx.close(choice))

  def open(ctx):
    super().open(ChoiceContext(ctx.choices,
      required=ctx.required,
      on_choose=ctx.on_choose,
      on_close=ctx.exit))

  def close(ctx, choice):
    super().close(choice)

  def view(ctx):
    sprites = []
    sprites += ctx.log.view()
    if ctx.child:
      panel = ctx.child.render()
      panel_x = ctx.log.x + ctx.log.surface.get_width() // 2 - panel.get_width() + 80
      panel_y = WINDOW_HEIGHT - ctx.log.y - panel.get_height() + 8
      sprites += [Sprite(
        image=panel,
        pos=(panel_x, panel_y),
        layer="log"
      )]
    return sprites + super().view()
