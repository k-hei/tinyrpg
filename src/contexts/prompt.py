import pygame
from contexts import Context
from contexts.choice import ChoiceContext
from comps.log import Log

class Choice:
  def __init__(choice, text, on_choose=None, default=False):
    choice.text = text
    choice.on_choose = on_choose or (lambda _: None)
    choice.default = default

class PromptContext(Context):
  def __init__(ctx, text, choices):
    super().__init__()
    ctx.choices = choices
    ctx.log = Log(autohide=False)
    ctx.log.print(text, on_end=ctx.open)

  def exit(ctx):
    ctx.log.exit(on_end=ctx.close)

  def open(ctx):
    super().open(ChoiceContext(ctx.choices, on_close=ctx.exit))

  def draw(ctx, surface):
    ctx.log.draw(surface)
    if ctx.child:
      panel = ctx.child.render()
      log_x = ctx.log.x + ctx.log.surface.get_width() // 2 + 16
      log_y = surface.get_height() - ctx.log.y - 32
      surface.blit(panel, (log_x, log_y))
