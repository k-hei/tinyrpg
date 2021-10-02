import pygame
import lib.keyboard as keyboard
import lib.gamepad as gamepad

from contexts import Context
from sprite import Sprite
import assets
from config import TILE_SIZE
from anims import Anim
from anims.tween import TweenAnim
from anims.frame import FrameAnim

class CursorAnim(Anim): pass

class CursorEnterAnim(CursorAnim, TweenAnim):
  blocking = True
  duration = 10

class CursorExitAnim(CursorAnim, TweenAnim):
  blocking = True
  duration = 7

class CursorFrameAnim(CursorAnim, FrameAnim):
  frames = assets.sprites["cursor_cell"]
  frames_duration = 10
  loop = True

class AllyContext(Context):
  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.anims = []
    ctx.exiting = False

  def enter(ctx):
    ctx.exiting = False
    game = ctx.parent
    ally = game.ally
    game.camera.focus(
      cell=ally.cell,
      force=True,
      speed=8
    )
    ctx.anims = [CursorEnterAnim(), CursorFrameAnim()]

  def exit(ctx):
    ctx.exiting = True
    game = ctx.parent
    if game:
      game.camera.blur()
    ctx.anims = [CursorExitAnim()]
    ctx.anims[-1].on_end = ctx.close

  def handle_press(ctx, button):
    if next((a for a in ctx.anims if a.blocking), None):
      return False

    if button in keyboard.ARROW_DELTAS:
      delta = keyboard.ARROW_DELTAS[button]
      ctx.handle_face(delta)

  def handle_release(ctx, button):
    if button in (pygame.K_TAB, gamepad.controls.ally):
      ctx.exit()

  def handle_face(ctx, delta):
    game = ctx.parent
    ally = game.ally
    ally.facing = delta

  def update(ctx):
    ctx.anims = [a for a in ctx.anims if not a.done and [a.update()]]

  def view(ctx):
    sprites = []
    sprites += ctx.view_cursor()
    for sprite in sprites:
      if not sprite.layer:
        sprite.layer = "ui"
    return sprites + super().view()

  def view_cursor(ctx):
    game = ctx.parent
    ally = game.ally
    ally_col, ally_row = ally.cell
    camera_x, camera_y = game.camera.pos
    cursor_x = (ally_col + 0.5) * TILE_SIZE - round(camera_x)
    cursor_y = (ally_row + 0.5) * TILE_SIZE - round(camera_y)
    cursor_anim = next((a for a in ctx.anims if isinstance(a, CursorAnim)))
    cursor_image = assets.sprites["cursor_cell"][0]
    cursor_size = cursor_image.get_size()
    if type(cursor_anim) is CursorEnterAnim:
      cursor_size = tuple([x * cursor_anim.pos for x in cursor_size])
    elif type(cursor_anim) is CursorExitAnim:
      cursor_size = tuple([x * (1 - cursor_anim.pos) for x in cursor_size])
    elif type(cursor_anim) is CursorFrameAnim:
      cursor_image = cursor_anim.frame()
    elif ctx.exiting:
      return []
    return [Sprite(
      image=cursor_image,
      pos=(cursor_x, cursor_y),
      size=cursor_size,
      origin=Sprite.ORIGIN_CENTER,
    )]
