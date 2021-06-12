from contexts.app import App
from contexts import Context
from comps.textbubble import TextBubble
import pygame
import keyboard

class BubbleContext(Context):
  def __init__(ctx, messages):
    super().__init__()
    ctx.messages = messages
    ctx.message_index = 0
    ctx.bubble = TextBubble(width=96, pos=(128, 112))

  def message(ctx):
    return ctx.messages[ctx.message_index]

  def init(ctx):
    ctx.bubble.print(ctx.message())

  def handle_keydown(ctx, key):
    if key == pygame.K_SPACE and keyboard.get_pressed(key) == 1:
      return ctx.handle_next()

  def handle_next(ctx):
    ctx.message_index = (ctx.message_index + 1) % len(ctx.messages)
    ctx.bubble.print(ctx.message())

  def update(ctx):
    ctx.bubble.update()

  def draw(ctx, surface):
    ctx.bubble.draw(surface)

App(
  title="text bubble demo",
  context=BubbleContext(messages=[
    "Short line of text",
    "Slightly longer line of text"
  ])
).init()
