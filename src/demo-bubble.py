from contexts import Context
from contexts.app import App
from contexts.choice import Choice
from comps.textbubble import TextBubble
import pygame
import lib.keyboard as keyboard
from config import WINDOW_WIDTH, WINDOW_HEIGHT

class BubbleContext(Context):
  def __init__(ctx, messages):
    super().__init__()
    ctx.messages = messages
    ctx.message_index = 0
    ctx.bubble = TextBubble(width=104, pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

  def message(ctx):
    return ctx.messages[ctx.message_index]

  def init(ctx):
    ctx.bubble.print(ctx.message())

  def handle_press(ctx, key):
    if super().handle_press(key) != None:
      return
    if keyboard.get_pressed(key) > 1:
      return
    if key == pygame.K_SPACE:
      return ctx.handle_next()
    if key == pygame.K_ESCAPE:
      return ctx.handle_exit()

  def handle_next(ctx):
    ctx.message_index = (ctx.message_index + 1) % len(ctx.messages)
    if type(ctx.message()) is str:
      ctx.bubble.print(ctx.message())
    elif type(ctx.message()) is tuple:
      message, choices = ctx.message()
      ctx.open(ctx.bubble.prompt(message, choices), on_close=lambda choice: ctx.handle_next())

  def handle_exit(ctx):
    ctx.bubble.exit(on_end=ctx.close)

  def view(ctx):
    return ctx.bubble.view()

App(
  title="text bubble demo",
  context=BubbleContext(messages=[
    "Short line of text",
    "Slightly longer line of text",
    ("This is a prompt", [
      Choice(text="Yes"),
      Choice(text="No", closing=True),
    ])
  ])
).init()
