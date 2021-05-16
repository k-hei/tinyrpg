from dataclasses import dataclass
import pygame
from contexts import Context
from contexts.choice import ChoiceContext
from comps.log import Log

@dataclass
class Choice:
  text: str
  default: bool = False
  closing: bool = False

class PromptContext(Context):
  def __init__(ctx, message, choices, on_choose=None, on_close=None):
    super().__init__(on_close=on_close)
    ctx.message = message
    ctx.choices = choices
    ctx.on_choose = on_choose
    ctx.log = Log(autohide=False)
    ctx.enter()

  def enter(ctx):
    ctx.log.print(ctx.message, on_end=ctx.open)

  def exit(ctx, choice):
    ctx.log.exit(on_end=lambda: ctx.close(choice))

  def open(ctx):
    super().open(ChoiceContext(ctx.choices,
      on_choose=ctx.on_choose,
      on_close=ctx.exit))

  def close(ctx, choice):
    ctx.parent.child = None
    if ctx.on_close:
      ctx.on_close(choice)

  def draw(ctx, surface):
    ctx.log.draw(surface)
    if ctx.child:
      panel = ctx.child.render()
      log_x = ctx.log.x + ctx.log.surface.get_width() // 2 - panel.get_width() + 80
      log_y = surface.get_height() - ctx.log.y - panel.get_height() + 8
      surface.blit(panel, (log_x, log_y))
