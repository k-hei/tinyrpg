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
from locations.default.tile import Tile
import locations.default.tileset as tileset
from transits.dissolve import DissolveIn, DissolveOut
from config import (
  TILE_SIZE, MOVE_DURATION, RUN_DURATION,
)

# world links
from contexts.explore.roomdata import RoomData
from town.graph import WorldLink
from dungeon.gen.floorgraph import FloorGraph


class ExploreContext(ExploreBase):

  def enter(ctx):
    ctx.debug = False
    ctx.move_buffer = []
    ctx.cache_last_move = 0
    ctx.port = None

    if not ctx.stage.is_overworld:
      ctx.comps.minimap.enter()
      ctx.comps.floor_no.enter()

  def exit(ctx):
    ctx.comps.minimap.exit()
    ctx.comps.floor_no.exit()
    ctx.close()

  def open(ctx, child, on_close=None):
    _on_close = lambda *args: (
      on_close and on_close(*args),
      ctx.parent.update_bubble(),
    )

    context_comps = {
      InventoryContext: [
        (ctx.comps.hud, True),
        (ctx.comps.sp_meter, True),
        (ctx.comps.floor_no, False)
      ],
      PauseContext: [
        (ctx.comps.minimap, False),
        (ctx.comps.floor_no, False)
      ],
      CutsceneContext: [
        (ctx.comps.minimap, False),
        (ctx.comps.floor_no, False)
      ],
    }

    if type(child) not in context_comps.keys():
      super().open(child, on_close=_on_close)
      ctx.parent.update_bubble()
      return

    comps = context_comps[type(child)]
    open = super().open

    for comp, active in comps:
      on_end = (lambda: (
        open(child, on_close=lambda: (
          _on_close(),
          [(
            c.exit() if a else c.enter()
          ) for c, a in comps]
        )),
        ctx.parent.update_bubble(),
      )) if comp == comps[-1][0] else None

      if comp.active == active:
        on_end and on_end()
      elif active:
        comp.enter(on_end=on_end)
      else:
        comp.exit(on_end=on_end)

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)

    if ctx.anims or ctx.port:
      return False

    delta = input.resolve_delta_held()
    if delta != (0, 0) and input.is_delta_button(button):
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

    controls = input.resolve_controls(button)

    # TODO(?): move `handle_control_confirm(button)` into base (shared handlers with combat mode)
    if input.CONTROL_CONFIRM in controls:
      if not ctx.hero.item and input.get_state(button) == 1:
        acted = ctx.handle_action()
        if acted == False:
          ctx.buttons_rejected[button] = 0
        return acted

    if input.get_state(button) > 1:
      return False

    if input.get_state(pygame.K_LCTRL) and button == pygame.K_h:
      return ctx.handle_debug()

    if input.CONTROL_ITEM in controls:
      if not ctx.hero.item:
        return ctx.handle_pickup()

    if input.CONTROL_MINIMAP in controls:
      return ctx.handle_minimap()

    if input.CONTROL_ALLY in controls:
      return ctx.handle_charswap()

  def handle_release(ctx, button):
    if ctx.child:
      return ctx.child.handle_release(button)

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
    hero = ctx.hero
    if not hero:
      return False
    ally = ctx.ally

    if ctx.cache_last_move == ctx.time:
      return # TODO: can we block this from inside input lib?
    ctx.cache_last_move = ctx.time

    moved = ctx.move_elem(elem=hero, delta=delta, running=running)
    if not ctx.stage.is_overworld:
      prop = next((e for e in ctx.stage.elems if
        not e.solid
        and hero.cell == e.cell
        and e.rect and hero.rect.colliderect(e.rect)
      ), None)
      if prop:
        if prop.effect(ctx, hero):
          hero.stop_move()
          ally and ally.stop_move()
        ctx.update_bubble()

    if ally:
      if moved:
        ctx.move_buffer.append((delta, running))

        move_data = (
          ctx.move_buffer.pop(0)
            if len(ctx.move_buffer) > TILE_SIZE // hero.speed
            else None
        )

        if vector.distance(hero.pos, ally.pos) > TILE_SIZE + ally.speed * 1.5:
          delta_x, delta_y = delta
          ally_dest = vector.subtract(
            hero.pos,
            vector.scale(
              invert_direction(delta),
              TILE_SIZE * (sqrt(0.5) if delta_x and delta_y else 1)
            )
          )
          ctx.move_to(
            actor=ally,
            dest=ally_dest,
            running=vector.distance(ally.pos, ally_dest) > ally.speed * 1.5
          )
        elif move_data:
          delta, running = move_data
          ctx.move_elem(elem=ally, delta=delta, running=running)

      else:
        ally.stop_move()

    return moved

  def move_elem(ctx, elem, delta, running=False):
    delta_x, delta_y = delta
    leaping = False

    def move_axis(delta):
      nonlocal leaping
      old_pos = elem.pos

      is_porting = ctx.move(elem, delta=delta, diagonal=(delta_x and delta_y), running=running)
      if is_porting:
        return True

      collidee = ctx.collide(elem, delta=delta)
      new_pos = elem.pos
      if collidee and not leaping and isinstance(elem, DungeonActor) and Tile.is_of_type(collidee, tileset.Pit):
        if elem is ctx.hero and ctx.ally:
          ctx.ally.stop_move()
        leaping = ctx.leap(actor=elem, running=running)

      return new_pos != old_pos

    moved_x = delta_x and move_axis((delta_x, 0))
    moved_y = delta_y and move_axis((0, delta_y))

    return moved_x or moved_y

  def move(ctx, actor, delta, diagonal=False, running=False):
    actor.move(delta, diagonal, running)

    hero = ctx.hero
    if not hero or actor is not hero:
      return False

    if not isinstance(ctx.stage.generator, RoomData):
      return False

    room_data = ctx.stage.generator

    if ("up" in room_data.ports
    and delta[1] == -1
    and actor.pos[1] < 0):
      return ctx.handle_port("up")

    if ("right" in room_data.ports
    and delta[0] == 1
    and actor.rect.right > ctx.stage.width * ctx.stage.tile_size):
      return ctx.handle_port("right")

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
    cell_nw = (col_w, row_n)
    cell_ne = (col_e, row_n)
    cell_sw = (col_w, row_s)
    cell_se = (col_e, row_s)
    actor_cell = vector.floor(vector.scale(rect.center, 1 / stage.tile_size))
    actor_elev = stage.get_tile_at_elev(actor_cell)

    # TODO: use stage.is_cell_walkable
    # TODO: handle floating actors
    is_tile_at_walkable = lambda cell: (
      cell in stage
      and not stage.is_tile_at_solid(cell)
      and not stage.is_tile_at_pit(cell)
      and abs(stage.get_tile_at_elev(cell) - actor_elev) < 1
    )

    collidee = None

    if delta_x < 0:
      if not is_tile_at_walkable(cell_nw) or not is_tile_at_walkable(cell_sw):
        rect.left = (col_w + 1) * stage.tile_size
        if row_n == row_s and stage.is_tile_at_pit(cell_nw):
          collidee = stage.get_tile_at(cell_nw)
      elif elem:
        rect.left = elem_rect.right
    elif delta_x > 0:
      if not is_tile_at_walkable(cell_ne) or not is_tile_at_walkable(cell_se):
        rect.right = col_e * stage.tile_size
        if row_n == row_s and stage.is_tile_at_pit(cell_se):
          collidee = stage.get_tile_at(cell_se)
      elif elem:
        rect.right = elem_rect.left

    if delta_y < 0:
      if not is_tile_at_walkable(cell_nw) or not is_tile_at_walkable(cell_ne):
        rect.top = (row_n + 1) * stage.tile_size
        if col_w == col_e and stage.is_tile_at_pit(cell_nw):
          collidee = stage.get_tile_at(cell_nw)
      elif elem:
        rect.top = elem_rect.bottom
    elif delta_y > 0:
      if not is_tile_at_walkable(cell_sw) or not is_tile_at_walkable(cell_se):
        rect.bottom = row_s * stage.tile_size
        if col_w == col_e and stage.is_tile_at_pit(cell_se):
          collidee = stage.get_tile_at(cell_se)
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

    if (not ctx.stage.is_cell_walkable(collision_cell)
    or next((e for e in ctx.stage.get_elems_at(collision_cell)
      if e.solid and not (isinstance(e, DungeonActor) and e.faction == actor.faction)), None)):
      return False

    actor_cell = vector.subtract(actor_cell, (0.5, 0.5))
    target_cell = vector.subtract(target_cell, (0.5, 0.5))

    actor.facing = normalize_direction(vector.subtract(target_cell, actor_cell))
    move_duration = (RUN_DURATION if running else MOVE_DURATION) * 1.5
    jump_anims = [JumpAnim(
      target=actor,
      src=actor_cell,
      dest=target_cell,
      duration=move_duration,
      on_end=on_end,
    ), PauseAnim(duration=move_duration + 5)]
    not ctx.anims and ctx.anims.append([])
    ctx.anims[-1].extend(jump_anims)
    # (ctx.anims.append if actor is ctx.hero else actor.core.anims.extend)(jump_anims)

    return True

  def validate_port(ctx, port_id):
    graph = ctx.graph
    if graph is None:
      return False

    src_area = ctx.stage.generator
    src_link = WorldLink(src_area, port_id)
    dest_link = graph.tail(src_link)
    return dest_link is not None

  def handle_port(ctx, port_id):
    if not ctx.validate_port(port_id):
      return False

    src_area = ctx.stage.generator
    ctx.port = src_area.ports[port_id]
    ctx.get_head().transition([
      DissolveIn(on_end=lambda: ctx.use_port(port_id)),
      DissolveOut()
    ])
    return True

  def use_port(ctx, port_id):
    if not ctx.validate_port(port_id):
      return False

    graph = ctx.graph
    src_area = ctx.stage.generator
    src_link = WorldLink(src_area, port_id)
    dest_link = graph.tail(src_link)
    ctx.get_parent(cls="GameContext").load_area(dest_link.node, dest_link.port_id)

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
      return ctx.handle_stairs()

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

    if issubclass(hero_tile, tileset.Escape):
      return ctx.goto_town()

    stairs_edge = ((ctx.graph.connector_edge(ctx.stage, hero_cell)
        or ctx.graph.connector_edge(ctx.stage, (hero_tile, hero_cell)))
      if isinstance(ctx.graph, FloorGraph)
      else None)
    if not stairs_edge:
      debug.log(f"Staircase has no connecting edge from {hero_cell}"
        f" given graph of type {type(ctx.graph).__name__}")

    dest_floor = (next((n for n in stairs_edge if n is not ctx.stage), None)
      if stairs_edge
      else None)
    if not dest_floor:
      debug.log("Staircase has no destination floor")
      ctx.parent.load_floor_by_id("GenericFloor")
      return True

    stairs_dest = tileset.Entrance if issubclass(stairs, tileset.Exit) else tileset.Exit
    ctx.comps.minimap.exit()
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
        setattr(stage, "generator", floor.__name__),
        ctx.graph.disconnect(ctx.stage, floor),
        ctx.graph.connect(
          ctx.stage, stage,
          (ctx.stage.get_tile_at(ctx.hero.cell), ctx.hero.cell),
          (stairs, find_tile(stage, stairs)),
        ),
        ctx.parent.use_stage(stage, stairs),
      )
    )

    return True

  def goto_town(ctx):
    app = ctx.get_head()
    dungeon = ctx.parent
    game = dungeon.parent
    app.transition([
      DissolveIn(on_end=lambda: game.goto_town(returning=True)),
      DissolveOut()
    ])

  def handle_hallway(ctx):
    if not ctx.ally:
      return
    ctx.move_buffer = [(vector.subtract(ctx.hero.cell, ctx.ally.cell), False)] * int(TILE_SIZE / ctx.hero.speed)

  def handle_combat(ctx):
    ctx.exit()

  def handle_minimap(ctx):
    ctx.open(MinimapContext(minimap=ctx.comps.minimap))

  def handle_charswap(ctx):
    if not ctx.hero:
      return False

    if not ctx.ally or ctx.ally.dead:
      return False

    hud = ctx.comps.hud
    if not hud.active:
      hud.enter()
    ctx.store.switch_chars()
    hud.update()
    if type(hud.anims[-1]) is PauseAnim:
      hud.anims[-1].time = 0
    else:
      hud.anims.append(PauseAnim(
        duration=75,
        on_end=lambda: hud.exit()
      ))

    ctx.parent.refresh_fov(reset_cache=True)
    ctx.camera.focus(target=[*([ctx.room] if ctx.room else []), ctx.hero], force=True)
    return True

  def handle_debug(ctx):
    ctx.debug = not ctx.debug
    debug.log("Debug mode toggle:", ctx.debug)
    return True

  def update(ctx):
    super().update()

    if not (hero := ctx.hero):
      return

    if ctx.port:
      hero.move(ctx.port.direction)

  def view(ctx):
    sprites = super().view()
    if ctx.debug:
      sprites += [view_elem_hitbox(elem=e, camera=ctx.camera) for e in ctx.stage.elems]
    return sprites

def view_elem_hitbox(elem, camera):
  if not elem.rect:
    return []

  ALPHA = 128
  RED = (255, 0, 0, ALPHA)
  BLUE = (0, 0, 255, ALPHA)
  YELLOW = (255, 255, 0, ALPHA)
  GREEN = (0, 255, 0, ALPHA)
  CIRCLE_RADIUS = 2
  CIRCLE_SIZE = (CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2)

  hitbox_surface = Surface(elem.rect.size, flags=SRCALPHA)
  hitbox_surface.fill(BLUE)
  hitbox_view = [Sprite(
    image=hitbox_surface,
    pos=elem.rect.topleft,
  )] if elem.solid else []

  circle_surface = Surface(CIRCLE_SIZE, SRCALPHA)
  pygame.draw.circle(circle_surface, YELLOW, (CIRCLE_RADIUS, CIRCLE_RADIUS), CIRCLE_RADIUS)
  circle_view = [Sprite(
    image=circle_surface,
    pos=elem.pos,
    origin=Sprite.ORIGIN_CENTER,
  )]

  return Sprite.move_all(
    sprites=[*hitbox_view, *circle_view],
    offset=vector.add(
      vector.scale(camera.size, 0.5),
      vector.negate(camera.pos)
    )
  )
