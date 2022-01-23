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
import lib.input as input
from lib.sprite import Sprite
import game.controls as controls
import assets
from contexts import Context
from contexts.loading import LoadingContext
from contexts.debug import DebugContext
from config import (
  FPS, FPS_SLOW, FPS_FAST,
  WINDOW_WIDTH, WINDOW_SIZE, WINDOW_SCALE_INIT, WINDOW_SCALE_MAX,
)

gamepad.config(preset=controls.TYPE_NULL)

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
    app.fps_shown = False
    app.surface = None
    app.display = None
    app.fullscreen = False
    app.transits = []
    app.loading = False
    app.paused = False
    app.done = False
    app.time = 0

  def init(app):
    pygame.init()
    pygame.display.set_caption(app.title)
    app.rescale(WINDOW_SCALE_INIT)
    app.display.fill((0, 0, 0))
    pygame.display.flip()
    gamepad.init()
    pygame.joystick.init()
    if pygame.joystick.get_count(): # we need this both inside and outside of the gamepad lib?
      joystick = pygame.joystick.Joystick(0)
      joystick.init()
      debug.log("Found joystick", joystick)
    else:
      debug.log("No joysticks found")
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
        app.update()
        app.redraw()
    except:
      debug.append(traceback.format_exc())
    finally:
      app.close()

  def update(app):
    keyboard.update()
    gamepad.update()
    input.update()
    if app.paused:
      return
    try:
      super().update()
      app.handle_events()
      # app.handle_press()
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

      UI_LAYERS = ["ui", "log", "transits", "hud", "selection"]
      sprites = [s for g in sprites for s in (g if type(g) is list else [g])]
      sprites.sort(key=lambda sprite: (
        UI_LAYERS.index(sprite.layer) + 1
          if sprite.layer in UI_LAYERS
          else 0
      ))

      if app.fps_shown:
        sprites += app.view_fps()

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

  def load(app, loader, on_end, child=None):
    app.loading = True
    child = child or app.get_tail()
    child.open(
      child=LoadingContext(loader, on_end),
      on_close=lambda: setattr(app, "loading", False)
    )

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

  def view_fps(app):
    sprites = []
    time_elapsed = get_ticks() - app.time
    if app.time and time_elapsed:
      fps = int(1000 / time_elapsed)
      sprites.append(Sprite(
        image=assets.ttf["normal"].render(f"FPS: {fps}"),
        pos=(WINDOW_WIDTH, 0),
        origin=Sprite.ORIGIN_TOPRIGHT
      ))
    app.time = get_ticks()
    return sprites

  def toggle_fps(app):
    app.fps_shown = not app.fps_shown

  def toggle_speedup(app):
    if app.fps == FPS_SLOW:
      app.fps = FPS
    elif app.fps == FPS:
      app.fps = FPS_FAST
    pygame.key.set_repeat(1000 // app.fps)

  def toggle_slowdown(app):
    if app.fps == FPS_FAST:
      app.fps = FPS
    elif app.fps == FPS:
      app.fps = FPS_SLOW
    pygame.key.set_repeat(1000 // app.fps)

  def toggle_pause(app):
    app.paused = not app.paused

  def toggle_debug(app):
    app.get_tail().open(DebugContext())

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
      input.handle_press(button)
      tapping = keyboard.get_state(button) == 1
      ctrl = (keyboard.get_state(pygame.K_LCTRL)
        or keyboard.get_state(pygame.K_RCTRL))
      shift = (keyboard.get_state(pygame.K_LSHIFT)
        or keyboard.get_state(pygame.K_RSHIFT))
      alt = (keyboard.get_state(pygame.K_LALT)
        or keyboard.get_state(pygame.K_RALT))
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
        return tapping and app.toggle_fps()
      if button == pygame.K_ESCAPE and ctrl:
        return tapping and app.toggle_debug()
      if button == pygame.K_RETURN and alt:
        return tapping and app.toggle_fullscreen()
      if button == pygame.K_p and ctrl:
        return tapping and app.toggle_pause()
    if app.child:
      return app.child.handle_press(button)

  def handle_release(app, key):
    if app.child:
      app.child.handle_release(key)
    keyboard.handle_release(key)
    input.handle_release(key)
