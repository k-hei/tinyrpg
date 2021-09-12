from copy import deepcopy
import os
import sys
import traceback
import debug
import pygame
from pygame.transform import scale
from pygame.time import get_ticks
import lib.keyboard as keyboard
import lib.gamepad as gamepad
import assets
from contexts import Context
from contexts.loading import LoadingContext
from transits.dissolve import DissolveIn, DissolveOut
from config import (
  FPS, FPS_SLOW, FPS_FAST,
  WINDOW_SIZE, WINDOW_SCALE_INIT, WINDOW_SCALE_MAX,
  ASSETS_PATH
)

class App(Context):
  def __init__(app, size=WINDOW_SIZE, title="Untitled", context=None):
    super().__init__()
    app.title = title
    app.child = context
    app.child_init = deepcopy(context)
    app.size = size
    app.size_scaled = (0, 0)
    app.scale = 0
    app.fps = FPS
    app.surface = None
    app.display = None
    app.fullscreen = False
    app.transits = []
    app.loading = False
    app.paused = False
    app.done = False

  def init(app):
    pygame.init()
    pygame.display.set_caption(app.title)
    app.rescale(WINDOW_SCALE_INIT)
    app.display.fill((0, 0, 0))
    pygame.display.flip()
    gamepad.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0) # we need this both inside and outside of the gamepad lib?
    joystick.init()
    pygame.key.set_repeat(1000 // FPS)
    app.surface = pygame.Surface(app.size)
    app.clock = pygame.time.Clock()
    if app.child:
      app.open()
      app.loop()

  def open(app, child=None):
    super().open(child or app.child, on_close=app.close)

  def close(app, *data):
    if data:
      print(*data)
    app.done = True
    try:
      super().close()
    except:
      debug.append(traceback.format_exc())
    finally:
      debug.write()

  def reset(app):
    app.open(deepcopy(app.child_init))

  def reload(app):
    pygame.quit()
    os.execl(sys.executable, sys.executable, *sys.argv)

  def loop(app):
    try:
      while not app.done:
        app.clock.tick(app.fps)
        app.redraw()
        app.update()
    except:
      debug.append(traceback.format_exc())
    finally:
      app.close()

  def update(app):
    keyboard.update()
    gamepad.update()
    if app.paused:
      return
    try:
      app.handle_events()
      super().update()
      app.handle_press()
      if app.transits:
        transit = app.transits[0]
        if transit.done:
          app.transits.remove(transit)
        elif not app.loading:
          transit.update()
    except:
      debug.append(traceback.format_exc())

  def redraw(app):
    if app.paused:
      return
    try:
      sprites = app.view()
      if app.transits:
        transit = app.transits[0]
        sprites += transit.view(sprites)
      UI_LAYERS = ["ui", "log", "transits", "hud"]
      sprites.sort(key=lambda sprite: UI_LAYERS.index(sprite.layer) + 1 if sprite.layer in UI_LAYERS else 0)
      app.surface.fill(0)
      for sprite in sprites:
        sprite.draw(app.surface)
      app.display.blit(scale(app.surface, app.size_scaled), (0, 0))
      pygame.display.flip()
    except:
      debug.append(traceback.format_exc())

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

  def transition(app, transits, loader=None, on_end=None):
    if len(transits) == 2:
      transit_in, transit_out = transits
      if loader:
        transit_in.on_end = lambda: app.load(loader, on_end)
    app.transits += transits

  def load(app, loader, on_end):
    app.loading = True
    def on_close():
      app.loading = False
    app.get_tail().open(LoadingContext(loader, on_end), on_close)

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

  def print_transits(app):
    print(app.transits)

  def toggle_fps(app, fps):
    if app.fps != fps:
      app.fps = fps
    else:
      app.fps = FPS
    pygame.key.set_repeat(1000 // app.fps)

  def toggle_speedup(app):
    app.toggle_fps(FPS_FAST)

  def toggle_slowdown(app):
    app.toggle_fps(FPS_SLOW)

  def toggle_pause(app):
    app.paused = not app.paused

  def toggle_fullscreen(app):
    app.fullscreen = not app.fullscreen
    if app.fullscreen:
      try:
        app.display = pygame.display.set_mode(app.size_scaled, pygame.FULLSCREEN | pygame.SCALED | pygame.HWSURFACE | pygame.DOUBLEBUF)
      except pygame.error:
        app.display = pygame.display.set_mode(app.size_scaled, pygame.FULLSCREEN)
        debug.append(traceback.format_exc())
    else:
      app.display = pygame.display.set_mode(app.size_scaled)

  def handle_events(app):
    pygame.event.pump()
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        app.done = True
        break
      elif event.type == pygame.KEYDOWN:
        app.handle_press(event.key)
      elif event.type == pygame.KEYUP:
        app.handle_release(event.key)
      if gamepad.handle_event(app, event): continue

  def handle_press(app, button=None):
    if button:
      keyboard.handle_press(button)
      tapping = keyboard.get_pressed(button) == 1
      ctrl = (keyboard.get_pressed(pygame.K_LCTRL)
        or keyboard.get_pressed(pygame.K_RCTRL))
      shift = (keyboard.get_pressed(pygame.K_LSHIFT)
        or keyboard.get_pressed(pygame.K_RSHIFT))
      if button == pygame.K_MINUS and ctrl:
        return tapping and app.rescale(app.scale - 1)
      if button == pygame.K_EQUALS and ctrl:
        return tapping and app.rescale(app.scale + 1)
      if button == pygame.K_r and ctrl and shift:
        return tapping and app.reload()
      if button == pygame.K_r and ctrl:
        return tapping and app.reset()
      if button == pygame.K_a and ctrl:
        return tapping and app.print_contexts()
      if button == pygame.K_BACKQUOTE and ctrl and shift:
        return tapping and app.toggle_slowdown()
      if button == pygame.K_BACKQUOTE and ctrl:
        return tapping and app.toggle_speedup()
      if button == pygame.K_f and ctrl:
        return tapping and app.toggle_fullscreen()
      if button == pygame.K_t and ctrl:
        return tapping and app.print_transits()
      if button == pygame.K_p and ctrl:
        return tapping and app.toggle_pause()
    if app.child:
      return app.child.handle_press(button)

  def handle_release(app, key):
    keyboard.handle_release(key)
    if app.child:
      return app.child.handle_release(key)
