import pygame
from pygame.time import get_ticks
import debug
from contexts import Context
from contexts.data import view_ticks
from comps.minimap import Minimap
import assets
from sprite import Sprite
from colors import darken_color
from colors.palette import WHITE, GRAY, GREEN, RED, GOLD
from config import WINDOW_WIDTH, WINDOW_HEIGHT

RESULT_COLORS = {
  None: GOLD,
  False: RED,
  True: GREEN
}

class GenContext(Context):
  def __init__(ctx, generator, seed=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.generator = generator
    ctx.seed = seed
    ctx.floor = None
    ctx.minimap = None
    ctx.log = []
    ctx.iters = 0
    ctx.attempts = 0
    ctx.result = None
    ctx.ms_start = 0
    ctx.ms_now = 0
    ctx.ms_end = 0
    ctx.updates = 0

  def handle_press(ctx, button):
    if ctx.result is False and button in (pygame.K_SPACE, pygame.K_RETURN):
      ctx.start()

  def print(ctx, message):
    ctx.log.append(message)
    debug.log(message)

  def start(ctx):
    if ctx.iters:
      ctx.attempts += 1
    if not ctx.attempts:
      ctx.generator = ctx.generator.generate(seed=ctx.seed)
    ctx.iters = 0
    ctx.result = None
    ctx.ms_start = get_ticks()
    ctx.ms_end = 0

  def complete(ctx):
    ctx.ms_end = get_ticks()
    ctx.result = True
    ctx.print(f"Completed generation #{ctx.floor.seed} in {view_ticks(ctx.ms_end - ctx.ms_start, ms=True)}")

  def fail(ctx):
    ctx.ms_end = get_ticks()
    ctx.result = False
    ctx.print(f"Failed generation #{ctx.floor.seed} in {view_ticks(ctx.ms_end - ctx.ms_start, ms=True)}")

  def update(ctx):
    ctx.updates += 1
    if ctx.result != None:
      return False
    if not ctx.ms_start:
      ctx.start()
    try:
      floor, message = next(ctx.generator)
      if floor:
        ctx.floor = floor
        ctx.minimap = None
      if message:
        ctx.print(message)
        if message.startswith("Failed"):
          ctx.fail()
      ctx.iters += 1
    except StopIteration:
      ctx.complete()

  def view(ctx):
    sprites = []
    font = assets.ttf["normal"]

    # FPS counter
    ms_elapsed = get_ticks() - ctx.ms_now
    if ctx.ms_now and ms_elapsed:
      fps = int(1000 / ms_elapsed)
      sprites.append(Sprite(
        image=font.render(f"FPS: {fps}"),
        pos=(WINDOW_WIDTH, 0),
        origin=Sprite.ORIGIN_TOPRIGHT
      ))
    ctx.ms_now = get_ticks()

    # Elapsed time
    ms_elapsed = (ctx.ms_end or get_ticks()) - ctx.ms_start
    time_text = view_ticks(ms_elapsed, ms=True)
    time_color = RESULT_COLORS[ctx.result] if ctx.result != None else WHITE
    time_color = darken_color(time_color) if ctx.result != None and ctx.updates % 60 >= 30 else time_color
    sprites.append(Sprite(
      image=font.render(time_text, color=time_color),
      pos=(WINDOW_WIDTH - font.width("00:00:00.00"), WINDOW_HEIGHT),
      origin=Sprite.ORIGIN_BOTTOMLEFT
    ))

    # Message log
    numbers_width = 0
    for i, message in enumerate(ctx.log):
      numbers_text = f"[{i}] "
      numbers_width = max(numbers_width, font.width(numbers_text))
      message_index = len(ctx.log) - 1 - i
      message_y = message_index * font.height()
      if message_index >= 4:
        continue
      numbers_color = RESULT_COLORS[ctx.result] if message_index == 0 else GOLD
      numbers_image = font.render(numbers_text, color=darken_color(numbers_color) if message_index else numbers_color)
      message_image = font.render(message, color=GRAY if message_index else WHITE)
      sprites += [
        Sprite(
          image=numbers_image,
          pos=(numbers_width - numbers_image.get_width(), message_y)
        ),
        Sprite(
          image=message_image,
          pos=(numbers_width, message_y)
        )
      ]

    floor = ctx.floor
    if floor:
      # Minimap
      if not ctx.minimap:
        ctx.minimap = Minimap.render_surface(floor)
      floor_image = ctx.minimap
      sprites.insert(0, Sprite(
        image=floor_image,
        pos=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
        origin=Sprite.ORIGIN_CENTER,
        size=(floor_image.get_width() * 3, floor_image.get_height() * 3)
      ))

      # Floor size
      sprites.append(Sprite(
        image=font.render(f"{floor.get_width()}x{floor.get_height()}"),
        pos=(0, WINDOW_HEIGHT),
        origin=Sprite.ORIGIN_BOTTOMLEFT
      ))

    return sprites + super().view()
