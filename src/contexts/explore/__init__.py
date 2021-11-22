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
from tiles import Tile
from config import WINDOW_SIZE

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
    input.CONTROLS_CONFIRM: [input.BUTTON_A],
    input.CONTROLS_CANCEL: [input.BUTTON_B],
    input.CONTROLS_MANAGE: [input.BUTTON_Y],
    input.CONTROLS_RUN: [input.BUTTON_B],
    input.CONTROLS_TURN: [input.BUTTON_R],
    input.CONTROLS_ITEM: [input.BUTTON_R, input.BUTTON_X],
    input.CONTROLS_WAIT: [input.BUTTON_R, input.BUTTON_A],
    input.CONTROLS_SHORTCUT: [input.BUTTON_R, input.BUTTON_Y],
    input.CONTROLS_ALLY: [input.BUTTON_L],
    input.CONTROLS_SKILL: [input.BUTTON_Y],
    input.CONTROLS_INVENTORY: [input.BUTTON_X],
    input.CONTROLS_PAUSE: [input.BUTTON_START],
    input.CONTROLS_MINIMAP: [input.BUTTON_SELECT],
  }
)

class ExploreContext(Context):
  COMBAT_THRESHOLD = 112

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

  def handle_press(ctx, button):
    delta = input.resolve_delta(button)
    if delta:
      return ctx.handle_move(delta)

  def handle_release(ctx, button):
    delta = input.resolve_delta(button)
    if delta:
      return ctx.hero.stop_move()

  def handle_move(ctx, delta):
    if not ctx.hero:
      return

    ctx.move(ctx.hero, delta)
    ctx.collide(ctx.hero, delta)

    room = next((r for r in ctx.stage.rooms if r.collidepoint(ctx.hero.pos)), None)
    if room:
      ctx.camera.focus(room)
    else:
      ctx.camera.focus(ctx.hero)

    enemy = next((e for e in ctx.stage.elems if
      isinstance(e, DungeonActor)
      and e.faction == DungeonActor.FACTION_ENEMY
      and vector.distance(ctx.hero.pos, e.pos) < ExploreContext.COMBAT_THRESHOLD
    ), None)
    if enemy:
      ctx.handle_combat()

  def handle_combat(ctx):
    ctx.on_end and ctx.on_end()

  def move(ctx, actor, delta):
    actor.move(delta)

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
