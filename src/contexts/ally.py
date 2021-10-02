from math import pi, sin, cos
import pygame
from pygame import Rect
import lib.keyboard as keyboard
import lib.gamepad as gamepad
from lib.compose import compose
from easing.expo import ease_out

from contexts import Context
from contexts.skill import SkillContext
from sprite import Sprite
import assets
from anims import Anim
from anims.tween import TweenAnim
from anims.frame import FrameAnim
from filters import replace_color, outline
from colors.palette import BLACK, BLUE, GOLD
from config import TILE_SIZE

LABEL_FONT = "normal"
LABEL_OFFSET = 8

def find_relative_actor_pos(game, actor):
  actor_col, actor_row = actor.cell
  camera_x, camera_y = game.camera.pos
  cursor_x = (actor_col + 0.5) * TILE_SIZE - round(camera_x)
  cursor_y = (actor_row + 0.5) * TILE_SIZE - round(camera_y)
  return (cursor_x, cursor_y)

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

class ButtonsAnim(Anim): pass

class ButtonsEnterAnim(ButtonsAnim, TweenAnim):
  blocking = True
  duration = 15

class ButtonsExitAnim(ButtonsAnim, TweenAnim):
  blocking = True
  duration = 4

class LabelsAnim(Anim): pass

class LabelsEnterAnim(LabelsAnim, TweenAnim):
  blocking = True
  duration = 7

class AllyContext(Context):
  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.anims = []
    ctx.exiting = False
    ctx.ally = None
    ctx.button_presses = set()
    ctx.button_mappings = {
      "a": (pygame.K_SPACE,),
      "b": (pygame.K_LSHIFT, pygame.K_RSHIFT),
      "x": (pygame.K_RETURN,),
      "y": (pygame.K_q,),
    }
    ctx.cached_labels = None

  def enter(ctx):
    ctx.exiting = False
    game = ctx.parent
    ally = ctx.ally = game.ally
    game.darken()
    game.camera.focus(
      cell=ally.cell,
      force=True,
      speed=8
    )
    ctx.anims = [
      CursorEnterAnim(),
      CursorFrameAnim(),
      ButtonsEnterAnim(easing=ease_out),
      LabelsEnterAnim(easing=ease_out, delay=ButtonsEnterAnim.duration)
    ]
    ctx.cache_labels()

  def exit(ctx, blur=False, on_end=None):
    ctx.exiting = True
    game = ctx.parent
    if game and blur:
      game.camera.blur()
    game.darken_end()
    ctx.anims = [
      CursorExitAnim(),
      ButtonsExitAnim(),
    ]
    sorted(ctx.anims, key=lambda a: a.duration + a.delay)[-1].on_end = compose(ctx.close, on_end)

  def handle_press(ctx, button):
    if next((a for a in ctx.anims if a.blocking), None):
      return False

    if keyboard.get_state(button) + gamepad.get_state(button) > 1:
      return False

    if button in keyboard.ARROW_DELTAS:
      delta = keyboard.ARROW_DELTAS[button]
      return ctx.handle_face(delta)

    match = next((k for k, v in ctx.button_mappings.items() if button in v), None)
    if match:
      ctx.button_presses.add(match)
      if match == "y":
        return ctx.handle_ai()

  def handle_release(ctx, button):
    if ctx.exiting:
      return False

    if button in (pygame.K_TAB, gamepad.controls.ally):
      ctx.exit(blur=True)

    if next((a for a in ctx.anims if a.blocking), None):
      return False

    match = next((k for k, v in ctx.button_mappings.items() if button in v), None)
    if match and match in ctx.button_presses:
      ctx.button_presses.remove(match)
      if match == "a":
        return ctx.handle_switch()
      elif match == "x":
        return ctx.handle_skill()

  def handle_face(ctx, delta):
    ally = ctx.ally
    if not ally.is_immobile():
      ally.facing = delta

  def handle_switch(ctx):
    game = ctx.parent
    game.handle_switch()
    ctx.exit()

  def handle_skill(ctx):
    game = ctx.parent
    ally = ctx.ally
    ctx.exit(on_end=lambda: (
      game.open(SkillContext(
        actor=ally,
        skills=ally.get_active_skills(),
        selected_skill=game.parent.get_skill(ally.core),
        on_close=lambda skill, dest: (
          skill and ally.charge(skill, dest),
          game.camera.blur(),
        )
      ))
    ))

  def handle_ai(ctx):
    ally = ctx.ally
    if ally.behavior == "chase":
      ally.behavior = "guard"
    elif ally.behavior == "guard":
      ally.behavior = "chase"
    ctx.cache_labels()

  def cache_labels(ctx):
    ally = ctx.ally
    ctx.cached_labels = [
      outline(assets.ttf[LABEL_FONT].render(l), BLACK)
        for l in [
          "Change",
          "Move",
          "Skill",
          "AI ({})".format("Follow" if ally.behavior == "chase" else "Stay")
        ]
    ]

  def update(ctx):
    ctx.anims = [a for a in ctx.anims if not a.done and [a.update()]]

  def view(ctx):
    sprites = (
      ctx.view_cursor()
      + ctx.view_buttons()
    )
    for sprite in sprites:
      if not sprite.layer:
        sprite.layer = "ui"
    return sprites + super().view()

  def view_cursor(ctx):
    game = ctx.parent
    ally = ctx.ally
    cursor_x, cursor_y = find_relative_actor_pos(game, ally)
    cursor_anim = next((a for a in ctx.anims if isinstance(a, CursorAnim)), None)
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
      origin=Sprite.ORIGIN_CENTER,
      size=cursor_size,
    )]

  def view_buttons(ctx):
    game = ctx.parent
    ally = ctx.ally
    buttons_x, buttons_y = tuple([x + TILE_SIZE for x in find_relative_actor_pos(game, ally)])
    buttons_anim = next((a for a in ctx.anims if isinstance(a, ButtonsAnim)), None)
    buttons_dist = TILE_SIZE / 2
    buttons_rads = 0
    if type(buttons_anim) is ButtonsEnterAnim:
      buttons_dist *= buttons_anim.pos
      buttons_rads = -2 * pi + 2 * pi * buttons_anim.pos
    elif type(buttons_anim) is ButtonsExitAnim:
      buttons_dist *= 1 - buttons_anim.pos
      buttons_rads = pi / 2 * buttons_anim.pos
    elif ctx.exiting:
      return []

    labels_anim = next((a for a in ctx.anims if isinstance(a, LabelsAnim)), None)
    labels_width = labels_anim and labels_anim.pos

    return [
      *[Sprite(
        image=replace_color(assets.sprites["ring"], BLACK, BLUE),
        pos=(buttons_x - 1, buttons_y - 1),
        size=(buttons_dist * 2, buttons_dist * 2),
        origin=Sprite.ORIGIN_CENTER,
        offset=-16,
      )],
      *[Sprite(
        image=replace_color(assets.sprites[f"button_{b}"], BLACK, GOLD if b in ctx.button_presses else BLUE),
        pos=(
          buttons_x + buttons_dist * cos(buttons_rads + (pi / 2) * i),
          buttons_y + buttons_dist * sin(buttons_rads + (pi / 2) * i)
        ),
        origin=Sprite.ORIGIN_CENTER,
      ) for i, b in enumerate(["a", "b", "x", "y"])],
      *([Sprite(
        image=(l.subsurface(
          Rect(
            (0, 0) if i == 2 else (l.get_width() * (1 - labels_width), 0),
            (l.get_width() * labels_width, l.get_height())
          )
        ) if labels_anim else l),
        pos=(
          buttons_x + buttons_dist * cos(buttons_rads + (pi / 2) * i) + LABEL_OFFSET * (-1 if i == 2 else 1),
          buttons_y + buttons_dist * sin(buttons_rads + (pi / 2) * i)
        ),
        origin=(Sprite.ORIGIN_RIGHT if i == 2 else Sprite.ORIGIN_LEFT),
      ) for i, l in enumerate(ctx.cached_labels)] if not buttons_anim else []),
    ]
