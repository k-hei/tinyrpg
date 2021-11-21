import pygame
from pygame import Surface, SRCALPHA
from lib.sprite import Sprite
import lib.input as input
from contexts import Context
from contexts.explore.stageview import StageView
from tiles import Tile

input.config({
  pygame.K_w: "up",
  pygame.K_a: "left",
  pygame.K_s: "down",
  pygame.K_d: "right",
  pygame.K_UP: "up",
  pygame.K_LEFT: "left",
  pygame.K_DOWN: "down",
  pygame.K_RIGHT: "right",
})

class ExploreContext(Context):
  def __init__(ctx, hero=None,stage=None, stage_view=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.party = [hero]
    ctx.stage = stage
    ctx.stage_view = stage_view or StageView(stage=stage)
    ctx.debug = False

  @property
  def hero(ctx):
    return ctx.party[0] if ctx.party else None

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

  def update(ctx):
    for elem in ctx.stage.elems:
      elem.update(ctx)

  def view(ctx):
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
