from copy import deepcopy
import pygame
import keyboard
import assets
from contexts import Context
from config import (
  FPS, WINDOW_SIZE, WINDOW_SCALE_INIT, WINDOW_SCALE_MAX,
  ASSETS_PATH
)

class App(Context):
  def __init__(app, title="Untitled", context=None):
    app.title = title
    app.child = context
    app.child_init = context
    app.size = WINDOW_SIZE
    app.size_scaled = (0, 0)
    app.scale = 0
    app.surface = None
    app.display = None
    app.done = False

  def init(app):
    pygame.init()
    pygame.display.set_caption(app.title)
    app.surface = pygame.Surface(app.size)
    app.surface.fill(0)
    app.rescale(WINDOW_SCALE_INIT)
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
      if child.on_close is None:
        child.on_close = app.close
      else:
        on_close = child.on_close
        def close(data=None):
          on_close(data)
          app.close()
        child.on_close = close
      super().open(child)

  def close(app, data=None):
    app.done = True

  def reload(app):
    app.open()

  def loop(app):
    clock = pygame.time.Clock()
    while not app.done:
      clock.tick(FPS)
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
    app.display.blit(pygame.transform.scale(app.surface, app.size_scaled), (0, 0))
    pygame.display.flip()

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
    ) and tapping
    shift = (
      keyboard.get_pressed(pygame.K_LSHIFT)
      or keyboard.get_pressed(pygame.K_RSHIFT)
    ) and tapping

    if key == pygame.K_MINUS and ctrl:
      return app.rescale(app.scale - 1)
    if key == pygame.K_EQUALS and ctrl:
      return app.rescale(app.scale + 1)
    if key == pygame.K_r and ctrl:
      return app.reload()
    if app.child:
      return app.child.handle_keydown(key)

  def handle_keyup(app, key):
    keyboard.handle_keyup(key)
