from assets import load as use_assets
from contexts import Context
import config
import pygame
import keyboard

class ExamineContext(Context):
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close
    ctx.cursor = Cursor(ctx.parent.hero.cell)
    ctx.anims = None

  def handle_keydown(ctx, key):
    if ctx.anims:
      return False

    if ctx.child:
      return ctx.child.handle_keydown(key)

    key_time = keyboard.get_pressed(key)
    if key in keyboard.ARROW_DELTAS and (
      key_time == 1
      or (key_time > 30 and key_time % 2)
    ):
      delta = keyboard.ARROW_DELTAS[key]
      ctx.handle_move(delta)

    if key == pygame.K_BACKSPACE or key == pygame.K_ESCAPE:
      ctx.handle_close()

  def handle_close(ctx):
    ctx.close()

  def handle_move(ctx, delta):
    ctx.cursor.move(delta)
    ctx.parent.camera.focus(ctx.cursor.target_cell)

  def draw(ctx, surface):
    assets = use_assets()
    sprite = assets.sprites["cursor_cell"]
    game = ctx.parent
    camera = game.camera
    camera_x, camera_y = camera.pos
    col, row = ctx.cursor.update()
    x = col * config.TILE_SIZE - round(camera_x)
    y = row * config.TILE_SIZE - round(camera_y)
    surface.blit(sprite, (x, y))
    pass

class Cursor:
  def __init__(cursor, cell):
    cursor.cell = cell
    cursor.target_cell = cell
    cursor.time = 0

  def move(cursor, delta, bounds=None):
    cursor_x, cursor_y = cursor.cell
    delta_x, delta_y = delta
    target_x, target_y = cursor.target_cell
    cursor.target_cell = (target_x + delta_x, target_y + delta_y)

  def update(cursor):
    cursor_x, cursor_y = cursor.cell
    target_x, target_y = cursor.target_cell
    cursor_x += (target_x - cursor_x) / 8
    cursor_y += (target_y - cursor_y) / 8
    cursor.cell = (cursor_x, cursor_y)
    return cursor.cell

  def render(cursor):
    pass
