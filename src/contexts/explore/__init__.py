from math import sqrt
import pygame
from pygame import Surface, SRCALPHA
import lib.vector as vector
from lib.sprite import Sprite
import lib.input as input
from lib.direction import invert as invert_direction, normal as normalize_direction
from helpers.stage import find_tile
import debug

from contexts.explore.base import ExploreBase
from contexts.inventory import InventoryContext
from contexts.pause import PauseContext
from contexts.minimap import MinimapContext
from contexts.cutscene import CutsceneContext
from dungeon.actors import DungeonActor
from dungeon.props.itemdrop import ItemDrop
from anims.attack import AttackAnim
from anims.jump import JumpAnim
from anims.pause import PauseAnim
from tiles import Tile
import tiles.default as tileset
from config import TILE_SIZE, MOVE_DURATION, RUN_DURATION
from transits.dissolve import DissolveIn, DissolveOut

class ExploreContext(ExploreBase):
  def enter(ctx):
    ctx.camera.focus(ctx.hero)
    ctx.debug = False
    ctx.move_buffer = []

  def exit(ctx):
    ctx.close()

  def open(ctx, child, on_close=None):
    _on_close = lambda *args: (
      on_close and on_close(*args),
      ctx.parent.update_bubble(),
    )

    context_comps = {
      InventoryContext: [ctx.comps.hud, ctx.comps.sp_meter],
      PauseContext: [ctx.comps.minimap],
      CutsceneContext: [ctx.comps.minimap],
    }

    if type(child) not in context_comps.keys():
      return super().open(child, _on_close)

    comps = context_comps[type(child)]
    open = super().open

    # if next((c for c in comps if c.anims), None):
    #   return super().open(child, _on_close)

    for comp in comps:
      on_end = (lambda: (
        open(child, on_close=lambda: (
          _on_close(),
          [(
            c.exit()
              if c.active
              else c.enter()
          ) for c in comps]
        ))
      )) if comp == comps[-1] else None

      if comp.active:
        comp.exit(on_end=on_end)
      else:
        comp.enter(on_end=on_end)

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)

    if ctx.anims:
      return

    if button:
      delta = input.resolve_delta()
      if delta != (0, 0):
        if button not in ctx.buttons_rejected:
          moved = ctx.handle_move(
            delta=delta,
            running=input.get_state(input.CONTROL_RUN) > 0
          )
          if moved == False:
            ctx.buttons_rejected[button] = 0
          return moved
        elif ctx.buttons_rejected[button] >= 30:
          return ctx.handle_push()

    control = input.resolve_control(button)

    # TODO: move `handle_control_confirm(button)` into base? (shared handlers with combat mode)
    if control == input.CONTROL_CONFIRM:
      if not ctx.hero.item:
        acted = ctx.handle_action()
        if acted == False:
          ctx.buttons_rejected[button] = 0
        return acted
      elif input.get_state(button) >= 30 and not button in ctx.buttons_rejected:
        return ctx.handle_throw()

    if input.get_state(button) > 1:
      return False

    if input.get_state(pygame.K_LCTRL) and button == pygame.K_h:
      return ctx.handle_debug()

    if control == input.CONTROL_MINIMAP:
      return ctx.handle_minimap()

  def handle_release(ctx, button):
    buttons_rejected = ctx.buttons_rejected.copy()
    if button in ctx.buttons_rejected:
      del ctx.buttons_rejected[button]

    delta = input.resolve_delta(button)
    if delta != (0, 0):
      ctx.hero.stop_move()
      ctx.ally and ctx.ally.stop_move()

    control = input.resolve_control(button)
    if control == input.CONTROL_MINIMAP:
      if isinstance(ctx.child, MinimapContext):
        ctx.child.exit()

    if control == input.CONTROL_CONFIRM and input.get_state(button) < 15 and not button in buttons_rejected and ctx.hero.item:
      ctx.handle_place()

  def handle_move(ctx, delta, running=False):
    if not ctx.hero:
      return

    moved = ctx.move_elem(elem=ctx.hero, delta=delta, running=running)

    prop = next((e for e in ctx.stage.elems if
      not e.solid
      and e.active
      and ctx.hero.rect.colliderect(e.rect)
    ), None)
    if prop:
      prop.effect(ctx, ctx.hero)
      ctx.hero.stop_move()

    if ctx.ally:
      if moved:
        ctx.move_buffer.append((delta, running))

        move_data = (
          ctx.move_buffer.pop(0)
            if len(ctx.move_buffer) > TILE_SIZE // ctx.hero.speed
            else None
        )

        if vector.distance(ctx.hero.pos, ctx.ally.pos) > TILE_SIZE + ctx.ally.speed * 1.5:
          delta_x, delta_y = delta
          ally_dest = vector.subtract(
            ctx.hero.pos,
            vector.scale(
              invert_direction(delta),
              TILE_SIZE * (sqrt(0.5) if delta_x and delta_y else 1)
            )
          )
          ctx.move_to(
            actor=ctx.ally,
            dest=ally_dest,
            running=vector.distance(ctx.ally.pos, ally_dest) > ctx.ally.speed * 1.5
          )
        elif move_data:
          delta, running = move_data
          ctx.move_elem(elem=ctx.ally, delta=delta, running=running)

      else:
        ctx.ally.stop_move()

    return moved

  def move_elem(ctx, elem, delta, running=False):
    delta_x, delta_y = delta
    leaping = False

    def move_axis(delta):
      nonlocal leaping
      old_pos = elem.pos
      ctx.move(elem, delta=delta, diagonal=(delta_x and delta_y), running=running)
      collidee = ctx.collide(elem, delta=delta)
      new_pos = elem.pos
      if collidee and not leaping and isinstance(elem, DungeonActor) and issubclass(collidee, tileset.Pit):
        if elem is ctx.hero and ctx.ally:
          ctx.ally.stop_move()
        leaping = ctx.leap(actor=elem, running=running)
      return new_pos != old_pos

    moved_x = delta_x and move_axis((delta_x, 0))
    moved_y = delta_y and move_axis((0, delta_y))

    return moved_x or moved_y

  def move(ctx, actor, delta, diagonal=False, running=False):
    actor.move(delta, diagonal, running)

  def move_to(ctx, actor, dest, speed=None, running=False):
    speed = speed or actor.speed
    actor_x, actor_y = actor.pos
    dest_x, dest_y = dest

    if dest_x - actor_x < -actor.speed:
      delta_x = -1
    elif dest_x - actor_x > actor.speed:
      delta_x = 1
    else:
      delta_x = 0

    if dest_y - actor_y < -actor.speed:
      delta_y = -1
    elif dest_y - actor_y > actor.speed:
      delta_y = 1
    else:
      delta_y = 0

    return ctx.move_elem(actor, (delta_x, delta_y), running)

  def collide(ctx, actor, delta):
    if delta == (0, 0):
      return None

    delta_x, delta_y = delta
    stage = ctx.stage
    rect = actor.rect
    init_center = rect.center
    elem_rects = [(e, e.rect) for e in stage.elems if
      e is not actor
      and e.solid
      and not (isinstance(e, DungeonActor) and e.faction == actor.faction)]
    elem, elem_rect = next(((e, r) for (e, r) in elem_rects if r.colliderect(rect)), (None, None))
    col_w = rect.left // stage.tile_size
    row_n = rect.top // stage.tile_size
    col_e = (rect.right - 1) // stage.tile_size
    row_s = (rect.bottom - 1) // stage.tile_size
    tile_nw = stage.get_tile_at((col_w, row_n))
    tile_ne = stage.get_tile_at((col_e, row_n))
    tile_sw = stage.get_tile_at((col_w, row_s))
    tile_se = stage.get_tile_at((col_e, row_s))
    tile_c = stage.get_tile_at(vector.floor(vector.scale(rect.center, 1 / stage.tile_size)))

    is_walkable = lambda tile: (
      Tile.is_walkable(tile)
      and abs(tile.elev - tile_c.elev) < 1
    )

    collidee = None

    if delta_x < 0:
      if not is_walkable(tile_nw) or not is_walkable(tile_sw):
        rect.left = (col_w + 1) * stage.tile_size
        if row_n == row_s and issubclass(tile_nw, tileset.Pit):
          collidee = tile_nw
      elif elem:
        rect.left = elem_rect.right
    elif delta_x > 0:
      if not is_walkable(tile_ne) or not is_walkable(tile_se):
        rect.right = col_e * stage.tile_size
        if row_n == row_s and issubclass(tile_se, tileset.Pit):
          collidee = tile_se
      elif elem:
        rect.right = elem_rect.left

    if delta_y < 0:
      if not is_walkable(tile_nw) or not is_walkable(tile_ne):
        rect.top = (row_n + 1) * stage.tile_size
        if col_w == col_e and issubclass(tile_nw, tileset.Pit):
          collidee = tile_nw
      elif elem:
        rect.top = elem_rect.bottom
    elif delta_y > 0:
      if not is_walkable(tile_sw) or not is_walkable(tile_se):
        rect.bottom = row_s * stage.tile_size
        if col_w == col_e and issubclass(tile_se, tileset.Pit):
          collidee = tile_se
      elif elem:
        rect.bottom = elem_rect.top

    if rect.center != init_center:
      actor.pos = rect.midtop

    return collidee

  def leap(ctx, actor, running=False, on_end=None):
    target_pos = vector.add(
      actor.pos,
      vector.scale(actor.facing, TILE_SIZE * 1.5)
    )

    downscale_cell = lambda pos: vector.scale(pos, 1 / TILE_SIZE)

    actor_cell = downscale_cell(actor.pos)
    target_cell = downscale_cell(target_pos)
    collision_cell = vector.floor(target_cell)

    if (not ctx.stage.is_tile_walkable(collision_cell)
    or next((e for e in ctx.stage.get_elems_at(collision_cell)
      if e.solid and not (isinstance(e, DungeonActor) and e.faction == actor.faction)), None)):
      return False

    actor_cell = vector.subtract(actor_cell, (0.5, 0.5))
    target_cell = vector.subtract(target_cell, (0.5, 0.5))

    actor.facing = normalize_direction(vector.subtract(target_cell, actor_cell))
    move_duration = (RUN_DURATION if running else MOVE_DURATION) * 1.5
    ctx.anims.append([JumpAnim(
      target=actor,
      src=actor_cell,
      dest=target_cell,
      duration=move_duration,
      on_end=on_end,
    ), PauseAnim(duration=move_duration + 5)])

    return True

  def handle_action(ctx):
    if not ctx.hero:
      return False

    facing_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    itemdrop = next((e for e in ctx.stage.get_elems_at(facing_cell) if isinstance(e, ItemDrop)), None)
    if ctx.hero.item:
      return ctx.handle_place()
    elif itemdrop:
      return ctx.handle_pickup()

    facing_elem = ctx.facing_elem
    if facing_elem is None:
      used_stairs = ctx.handle_stairs()
      if used_stairs:
        return True
      else:
        return False

    success = facing_elem.effect(ctx, ctx.hero)
    if success:
      ctx.hero.stop_move()
      ctx.ally and ctx.ally.stop_move()
    ctx.parent.update_bubble()

    not ctx.anims and ctx.anims.append([])
    ctx.anims[0].append(AttackAnim(
      target=ctx.hero,
      src=ctx.hero.cell,
      dest=facing_elem.cell,
    ))

    return True

  def handle_stairs(ctx):
    if not ctx.hero:
      return False

    app = ctx.get_head()
    if app.transits:
      return False

    hero_cell = ctx.hero.cell
    hero_tile = ctx.stage.get_tile_at(hero_cell)
    stairs = hero_tile if issubclass(hero_tile, (tileset.Entrance, tileset.Exit)) else None
    if not stairs:
      return False

    stairs_edge = ctx.parent.graph.connector_edge((hero_tile, hero_cell))
    if not stairs_edge:
      return False # link doesn't exist in graph - how to handle besides ignore?

    dest_floor = next((n for n in stairs_edge if n is not ctx.stage), None)
    if not dest_floor:
      return False # generate random floor in infinite dungeon

    stairs_dest = tileset.Entrance if issubclass(stairs, tileset.Exit) else tileset.Exit
    if type(dest_floor) is type:
      ctx.goto_floor(dest_floor, stairs_dest)
    else:
      app.transition([
        DissolveIn(on_end=lambda: ctx.parent.use_stage(dest_floor, stairs_dest)),
        DissolveOut()
      ])

    return True

  def goto_floor(ctx, floor, stairs):
    app = ctx.get_head()
    if app.transits:
      return False

    app.transition(
      transits=[DissolveIn(), DissolveOut()],
      loader=floor.generate(ctx.store),
      on_end=lambda stage: (
        ctx.parent.graph.disconnect(ctx.stage, floor),
        ctx.parent.graph.connect(
          ctx.stage, stage,
          (ctx.stage.get_tile_at(ctx.hero.cell), ctx.hero.cell),
          (stairs, find_tile(stage, stairs)),
        ),
        ctx.parent.use_stage(stage, stairs)
      )
    )
    return True

  def handle_hallway(ctx):
    if not ctx.ally:
      return
    ctx.move_buffer = [(vector.subtract(ctx.hero.cell, ctx.ally.cell), False)] * int(TILE_SIZE / ctx.hero.speed)

  def handle_combat(ctx):
    ctx.exit()

  def handle_minimap(ctx):
    ctx.open(MinimapContext(minimap=ctx.comps.minimap))

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
