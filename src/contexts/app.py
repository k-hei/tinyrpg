from copy import deepcopy
import pygame
import keyboard
import assets
from contexts import Context
from transits.dissolve import DissolveIn, DissolveOut
from config import (
  FPS, WINDOW_SIZE, WINDOW_SCALE_INIT, WINDOW_SCALE_MAX,
  ASSETS_PATH
)

class App(Context):
  def __init__(app, title="Untitled", context=None):
    super().__init__()
    app.title = title
    app.child = context
    app.child_init = context
    app.size = WINDOW_SIZE
    app.size_scaled = (0, 0)
    app.scale = 0
    app.fps = FPS
    app.surface = None
    app.display = None
    app.transits = []
    app.done = False

  def init(app):
    pygame.init()
    pygame.display.set_caption(app.title)
    app.surface = pygame.Surface(app.size)
    app.surface.fill(0)
    app.rescale(WINDOW_SCALE_INIT)
    pygame.key.set_repeat(1000 // FPS)
    pygame.display.flip()
    assets.load(ASSETS_PATH)
    if app.child:
      app.open()
      app.loop()

  def open(app, child=None):
    if app.child_init is None:
      app.child_init = child
    if child is None:
      child = app.child_init
    if child:
      app.child_init = child
      child = deepcopy(child)
      super().open(child, on_close=app.close)

  def close(app, data=None):
    print(data)
    app.done = True

  def reload(app):
    app.open()

  def loop(app):
    clock = pygame.time.Clock()
    while not app.done:
      clock.tick(app.fps)
      keyboard.update()
      app.handle_events()
      if app.child:
        app.child.update()
      app.render()

  def rescale(app, new_scale):
    if (new_scale == app.scale
    or new_scale < 1
    or new_scale > WINDOW_SCALE_MAX):
      return False
    app.scale = new_scale
    old_width, old_height = app.size
    new_width = old_width * new_scale
    new_height = old_height * new_scale
    new_size = (new_width, new_height)
    app.size_scaled = new_size
    app.display = pygame.display.set_mode(app.size_scaled)
    return True

  def render(app):
    app.surface.fill(0)
    app.draw(app.surface)
    if app.transits:
      transit = app.transits[0]
      if transit.done:
        app.transits.remove(transit)
      transit.update()
      transit.draw(app.surface)
    app.display.blit(pygame.transform.scale(app.surface, app.size_scaled), (0, 0))
    pygame.display.flip()

  def dissolve(app, on_clear=None, on_end=None):
    app.transits.append(DissolveIn(WINDOW_SIZE, on_clear))
    app.transits.append(DissolveOut(WINDOW_SIZE, on_end))

  def print_contexts(app):
    contexts = []
    ctx = app
    while ctx.child:
      contexts.append(ctx)
      ctx = ctx.child
    if ctx is not app:
      contexts.append(ctx)
    print(contexts)
    return True

  def toggle_fps(app):
    if app.fps != FPS // 4:
      app.fps = FPS // 4
    else:
      app.fps = FPS
    pygame.key.set_repeat(1000 // app.fps)

  def handle_events(app):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        app.done = True
        break
      elif event.type == pygame.KEYDOWN:
        app.handle_keydown(event.key)
      elif event.type == pygame.KEYUP:
        app.handle_keyup(event.key)

  def handle_keydown(app, key):
    keyboard.handle_keydown(key)
    tapping = keyboard.get_pressed(key) == 1
    ctrl = (
      keyboard.get_pressed(pygame.K_LCTRL)
      or keyboard.get_pressed(pygame.K_RCTRL)
    )

    if key == pygame.K_MINUS and ctrl:
      if tapping: app.rescale(app.scale - 1)
      return
    if key == pygame.K_EQUALS and ctrl:
      if tapping: app.rescale(app.scale + 1)
      return
    if key == pygame.K_r and ctrl:
      if tapping: app.reload()
      return
    if key == pygame.K_a and ctrl:
      if tapping: app.print_contexts()
      return
    if key == pygame.K_f and ctrl:
      if tapping: app.toggle_fps()
      return
    if app.child:
      return app.child.handle_keydown(key)

  def handle_keyup(app, key):
    keyboard.handle_keyup(key)
    if app.child:
      return app.child.handle_keyup(key)
