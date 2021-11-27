import pygame
from pygame import Surface, SRCALPHA
from lib.sprite import Sprite
import lib.input as input
import lib.vector as vector
from helpers.findactor import find_actor
from contexts import Context
from contexts.explore.stageview import StageView
from contexts.dungeon.camera import Camera
from dungeon.actors import DungeonActor
from dungeon.props import Prop
from anims.item import ItemAnim
from tiles import Tile
from config import WINDOW_SIZE, COMBAT_THRESHOLD

input.config(
  buttons={
    input.BUTTON_UP: [pygame.K_UP, pygame.K_w],
    input.BUTTON_LEFT: [pygame.K_LEFT, pygame.K_a],
    input.BUTTON_DOWN: [pygame.K_DOWN, pygame.K_s],
    input.BUTTON_RIGHT: [pygame.K_RIGHT, pygame.K_d],
    input.BUTTON_A: [pygame.K_RETURN, pygame.K_SPACE],
    input.BUTTON_B: [pygame.K_RSHIFT, pygame.K_LSHIFT],
    input.BUTTON_X: [pygame.K_q],
    input.BUTTON_Y: [pygame.K_e],
    input.BUTTON_L: [pygame.K_TAB],
    input.BUTTON_R: [pygame.K_LALT, pygame.K_RALT],
    input.BUTTON_START: [pygame.K_ESCAPE, pygame.K_BACKSPACE],
    input.BUTTON_SELECT: [pygame.K_BACKQUOTE, pygame.K_BACKSLASH],
  },
  controls={
    input.CONTROL_CONFIRM: [input.BUTTON_A],
    input.CONTROL_CANCEL: [input.BUTTON_B],
    input.CONTROL_MANAGE: [input.BUTTON_Y],
    input.CONTROL_RUN: [input.BUTTON_B],
    input.CONTROL_TURN: [input.BUTTON_R],
    input.CONTROL_ITEM: [input.BUTTON_R, input.BUTTON_X],
    input.CONTROL_WAIT: [input.BUTTON_R, input.BUTTON_A],
    input.CONTROL_SHORTCUT: [input.BUTTON_R, input.BUTTON_Y],
    input.CONTROL_ALLY: [input.BUTTON_L],
    input.CONTROL_SKILL: [input.BUTTON_Y],
    input.CONTROL_INVENTORY: [input.BUTTON_X],
    input.CONTROL_PAUSE: [input.BUTTON_START],
    input.CONTROL_MINIMAP: [input.BUTTON_SELECT],
  }
)

class ExploreContext(Context):
  def __init__(ctx, store, stage, stage_view=None, on_end=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx._headless = stage_view is None
    if stage_view:
      ctx.stage = stage_view.stage
      ctx.camera = stage_view.camera
      ctx.stage_view = stage_view
    else:
      ctx.stage = stage
      ctx.camera = Camera(WINDOW_SIZE)
      ctx.stage_view = StageView(stage=stage, camera=ctx.camera)
    ctx.store = store
    ctx.on_end = on_end
    ctx.debug = False

  def enter(ctx):
    ctx.camera.focus(ctx.hero)

  @property
  def hero(ctx):
    return find_actor(
      char=ctx.store.party[0],
      stage=ctx.stage
    ) if ctx.store.party else None

  @property
  def anims(ctx):
    return ctx.stage_view.anims

  def handle_press(ctx, button):
    if button or ctx.anims:
      return

    delta_x = 0
    delta_y = 0
    last_direction = 0
    running = False

    if (input.get_state(input.BUTTON_LEFT)
    and (not input.get_state(input.BUTTON_RIGHT)
      or input.get_state(input.BUTTON_LEFT) < input.get_state(input.BUTTON_RIGHT)
    )):
      delta_x = -1
      last_direction = max(last_direction, input.get_state(input.BUTTON_LEFT))
    elif (input.get_state(input.BUTTON_RIGHT)
    and (not input.get_state(input.BUTTON_LEFT)
      or input.get_state(input.BUTTON_RIGHT) < input.get_state(input.BUTTON_LEFT)
    )):
      delta_x = 1
      last_direction = max(last_direction, input.get_state(input.BUTTON_RIGHT))

    if (input.get_state(input.BUTTON_UP)
    and (not input.get_state(input.BUTTON_DOWN)
      or input.get_state(input.BUTTON_UP) < input.get_state(input.BUTTON_DOWN)
    )):
      delta_y = -1
      last_direction = max(last_direction, input.get_state(input.BUTTON_UP))
    elif (input.get_state(input.BUTTON_DOWN)
    and (not input.get_state(input.BUTTON_UP)
      or input.get_state(input.BUTTON_DOWN) < input.get_state(input.BUTTON_UP)
    )):
      delta_y = 1
      last_direction = max(last_direction, input.get_state(input.BUTTON_DOWN))

    if input.get_state(input.CONTROL_RUN) and input.get_state(input.CONTROL_RUN) > last_direction:
      running = True

    if delta_x or delta_y:
      ctx.handle_move(delta=(delta_x, delta_y), running=running)

  def handle_release(ctx, button):
    delta = input.resolve_delta(button)
    if delta:
      return ctx.hero.stop_move()

  def handle_move(ctx, delta, running=False):
    if not ctx.hero:
      return

    delta_x, delta_y = delta
    diagonal = delta_x and delta_y

    if delta_x:
      ctx.move(ctx.hero, delta=(delta_x, 0), diagonal=diagonal, running=running)
      ctx.collide(ctx.hero, delta=(delta_x, 0))

    if delta_y:
      ctx.move(ctx.hero, delta=(0, delta_y), diagonal=diagonal, running=running)
      ctx.collide(ctx.hero, delta=(0, delta_y))

    prop = next((e for e in ctx.stage.elems if
      isinstance(e, Prop)
      and ctx.hero.rect.collidepoint(e.pos)
    ), None)
    if prop:
      prop.effect(ctx, ctx.hero)
      ctx.hero.stop_move()

    enemy = next((e for e in ctx.stage.elems if
      isinstance(e, DungeonActor)
      and e.faction == DungeonActor.FACTION_ENEMY
      and vector.distance(ctx.hero.pos, e.pos) <= COMBAT_THRESHOLD
    ), None)
    if enemy:
      return ctx.handle_combat()

  def handle_combat(ctx):
    ctx.on_end and ctx.on_end()

  def handle_obtain(ctx, item, target, on_end=None):
    obtained = ctx.store.obtain(item)
    if obtained:
      old_facing = ctx.hero.facing
      ctx.hero.facing = (0, 1)
      ctx.anims.append([
        ItemAnim(
          target=target,
          item=item(),
          duration=60,
          on_end=lambda: (
            setattr(ctx.hero, "facing", old_facing),
            on_end and on_end(),
          )
        )
      ])
      ctx.parent.minilog.print(message=("Obtained ", item().token(), "."))
    return obtained

  def move(ctx, actor, delta, diagonal=False, running=False):
    actor.move(delta, diagonal, running)

  def collide(ctx, actor, delta):
    delta_x, delta_y = delta
    stage = ctx.stage
    rect = actor.rect
    init_center = rect.center
    elem_rects = [(e, e.rect) for e in stage.elems if e is not actor and e.solid]
    elem, elem_rect = next(((e, r) for (e, r) in elem_rects if r.colliderect(rect)), (None, None))
    col_w = rect.left // stage.tile_size
    row_n = rect.top // stage.tile_size
    col_e = (rect.right - 1) // stage.tile_size
    row_s = (rect.bottom - 1) // stage.tile_size
    tile_nw = stage.get_tile_at((col_w, row_n))
    tile_ne = stage.get_tile_at((col_e, row_n))
    tile_sw = stage.get_tile_at((col_w, row_s))
    tile_se = stage.get_tile_at((col_e, row_s))

    if delta_x < 0:
      if Tile.is_solid(tile_nw) or Tile.is_solid(tile_sw):
        rect.left = (col_w + 1) * stage.tile_size
      elif elem:
        rect.left = elem_rect.right
    elif delta_x > 0:
      if Tile.is_solid(tile_ne) or Tile.is_solid(tile_se):
        rect.right = col_e * stage.tile_size
      elif elem:
        rect.right = elem_rect.left

    if delta_y < 0:
      if Tile.is_solid(tile_nw) or Tile.is_solid(tile_ne):
        rect.top = (row_n + 1) * stage.tile_size
      elif elem:
        rect.top = elem_rect.bottom
    elif delta_y > 0:
      if Tile.is_solid(tile_sw) or Tile.is_solid(tile_se):
        rect.bottom = row_s * stage.tile_size
      elif elem:
        rect.bottom = elem_rect.top

    if rect.center != init_center:
      actor.pos = rect.midtop
      return True
    else:
      return False

  def view(ctx):
    if not ctx._headless:
      return []

    sprites = ctx.stage_view.view()
    if ctx.debug:
      sprites += [debug_view_elem(e) for e in ctx.stage.elems]

    return sprites

def debug_view_elem(elem):
  ALPHA = 128
  RED = (255, 0, 0, ALPHA)
  BLUE = (0, 0, 255, ALPHA)
  YELLOW = (255, 255, 0, ALPHA)
  GREEN = (0, 255, 0, ALPHA)
  CIRCLE_RADIUS = 2
  CIRCLE_SIZE = (CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2)

  hitbox_surface = Surface(elem.rect.size, flags=SRCALPHA)
  hitbox_surface.fill(BLUE)

  origin_circle = Surface(CIRCLE_SIZE, SRCALPHA)
  pygame.draw.circle(origin_circle, YELLOW, (CIRCLE_RADIUS, CIRCLE_RADIUS), CIRCLE_RADIUS)

  return [Sprite(
    image=hitbox_surface,
    pos=elem.rect.topleft,
  ), Sprite(
    image=origin_circle,
    pos=elem.pos,
    origin=Sprite.ORIGIN_CENTER,
  )]
