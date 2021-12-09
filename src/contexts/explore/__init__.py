import pygame
from pygame import Surface, SRCALPHA
import lib.vector as vector
from lib.sprite import Sprite
import lib.input as input
from lib.compose import compose
from contexts.explore.base import ExploreBase
from contexts.inventory import InventoryContext
from dungeon.actors import DungeonActor
from dungeon.props.itemdrop import ItemDrop
from anims.attack import AttackAnim
from tiles import Tile
import debug

class ExploreContext(ExploreBase):
  def enter(ctx):
    ctx.camera.focus(ctx.hero)
    ctx.debug = False

  def exit(ctx):
    ctx.close()

  def open(ctx, child, on_close=None):
    on_close = compose(on_close, ctx.parent.update_bubble)
    if type(child) is InventoryContext:
      if not ctx.hud.anims:
        open = super().open
        ctx.hud.enter(on_end=lambda: (
          open(child, on_close=compose(on_close, ctx.hud.exit))
        ))
    else:
      return super().open(child, on_close)

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)

    if ctx.anims:
      return

    if not button:
      delta = input.resolve_delta()
      if delta != (0, 0):
        return ctx.handle_move(
          delta=delta,
          running=input.get_state(input.CONTROL_RUN) > 0
        )
      else:
        return False

    if input.get_state(button) > 1:
      return False

    if input.get_state(pygame.K_LCTRL) and button == pygame.K_h:
      return ctx.handle_debug()

    control = input.resolve_control(button)
    if control == input.CONTROL_CONFIRM:
      ctx.handle_action()

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
      isinstance(e, ItemDrop) # TODO: design generic model for steppables
      and ctx.hero.rect.colliderect(e.rect)
    ), None)
    if prop:
      prop.effect(ctx, ctx.hero)
      ctx.hero.stop_move()

    if ctx.find_enemies_in_range():
      return ctx.handle_combat()

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
      if not Tile.is_walkable(tile_nw) or not Tile.is_walkable(tile_sw):
        rect.left = (col_w + 1) * stage.tile_size
      elif elem:
        rect.left = elem_rect.right
    elif delta_x > 0:
      if not Tile.is_walkable(tile_ne) or not Tile.is_walkable(tile_se):
        rect.right = col_e * stage.tile_size
      elif elem:
        rect.right = elem_rect.left

    if delta_y < 0:
      if not Tile.is_walkable(tile_nw) or not Tile.is_walkable(tile_ne):
        rect.top = (row_n + 1) * stage.tile_size
      elif elem:
        rect.top = elem_rect.bottom
    elif delta_y > 0:
      if not Tile.is_walkable(tile_sw) or not Tile.is_walkable(tile_se):
        rect.bottom = row_s * stage.tile_size
      elif elem:
        rect.bottom = elem_rect.top

    if rect.center != init_center:
      actor.pos = rect.midtop
      return True
    else:
      return False

  def handle_action(ctx):
    facing_elem = ctx.facing_elem
    if facing_elem is None:
      return False

    facing_elem.effect(ctx, ctx.hero)
    ctx.parent.update_bubble()

    not ctx.anims and ctx.anims.append([])
    ctx.anims[0].append(AttackAnim(
      target=ctx.hero,
      src=ctx.hero.cell,
      dest=facing_elem.cell,
    ))

    return True

  def handle_combat(ctx):
    ctx.exit()

  def handle_debug(ctx):
    ctx.debug = not ctx.debug
    debug.log("Debug mode toggle:", ctx.debug)
    return True

  def view(ctx):
    sprites = super().view()
    if ctx.debug:
      sprites += [debug_view_elem(elem=e, camera=ctx.camera) for e in ctx.stage.elems]
    return sprites

def debug_view_elem(elem, camera):
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

  return Sprite.move_all(
    sprites=[Sprite(
      image=hitbox_surface,
      pos=elem.rect.topleft,
    ), Sprite(
      image=origin_circle,
      pos=elem.pos,
      origin=Sprite.ORIGIN_CENTER,
    )],
    offset=vector.add(
      vector.scale(camera.size, 0.5),
      vector.negate(camera.pos)
    )
  )
