from random import random
from lib.cell import manhattan, upscale
import lib.vector as vector
from helpers.findactor import find_actor
from contexts import Context
from anims.item import ItemAnim
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from dungeon.actors import DungeonActor
from dungeon.props.itemdrop import ItemDrop
from tiles import Tile
import tiles.default as tileset
from vfx.talkbubble import TalkBubble

class ExploreBase(Context):
  def __init__(ctx, store=None, stage=None, stage_view=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = store
    ctx.stage = stage
    ctx.stage_view = stage_view

  @property
  def hero(ctx):
    return find_actor(
      char=ctx.store.party[0],
      stage=ctx.stage
    ) if ctx.store.party else None

  @property
  def ally(ctx):
    return find_actor(
      char=ctx.store.party[1],
      stage=ctx.stage
    ) if len(ctx.store.party) >= 2 else None

  @property
  def party(ctx):
    return [
      *([ctx.hero] if ctx.hero else []),
      *([ctx.ally] if ctx.ally else []),
    ]

  @property
  def room(ctx):
    return ctx.hero and next((r for r in ctx.stage.rooms if ctx.hero.cell in r.cells), None)

  @property
  def visited_cells(ctx):
    stage_id = ctx.stage.__hash__()
    visited_cells = ctx.memory[stage_id] if stage_id in ctx.memory else None # next((cs for (s, cs) in ctx.memory if s is ctx.stage), None)
    if visited_cells is None:
      ctx.memory[stage_id] = (visited_cells := [])
    return visited_cells

  @property
  def camera(ctx):
    return ctx.stage_view.camera

  @property
  def anims(ctx):
    return ctx.stage_view.anims

  @property
  def vfx(ctx):
    return ctx.stage_view.vfx

  @property
  def memory(ctx):
    return ctx._memory if "_memory" in dir(ctx) else ctx.parent.memory

  @memory.setter
  def memory(ctx, memory):
    ctx._memory = memory

  @property
  def comps(ctx):
    return ctx._comps if "_comps" in dir(ctx) else ctx.parent.comps

  @comps.setter
  def comps(ctx, comps):
    ctx._comps = comps

  @property
  def talkbubble(ctx):
    return next((v for v in ctx.vfx if type(v) is TalkBubble), None)

  @property
  def facing_elem(ctx):
    facing_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    facing_elems = ctx.stage.get_elems_at(facing_cell)
    return next((e for e in facing_elems if (
      e.active
      and e.solid
      and (not isinstance(e, DungeonActor) or e.faction == "ally")
    )), None)

  @property
  def facing_actor(ctx):
    facing_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    facing_elems = ctx.stage.get_elems_at(facing_cell)
    return next((e for e in facing_elems if isinstance(e, DungeonActor)), None)

  def find_closest_enemy(ctx, actor, elems=None):
    enemies = [e for e in (elems or ctx.stage.elems) if (
      isinstance(e, DungeonActor)
      and not e.is_dead()
      and not e.allied(actor)
    )]

    if not enemies:
      return None

    if len(enemies) > 1:
      enemies.sort(key=lambda e: manhattan(e.cell, actor.cell) + random() / 2)

    return enemies[0]

  def find_enemies_in_range(ctx):
    room = next((r for r in ctx.stage.rooms if ctx.hero.cell in r.cells), None)
    return [e for e in ctx.stage.elems if
      isinstance(e, DungeonActor)
      and e.faction == DungeonActor.FACTION_ENEMY
      and not e.dead
      and room and e.cell in room.cells
    ]

  def handle_obtain(ctx, item, target, on_end=None):
    obtained = ctx.store.obtain(item)
    if obtained:
      old_facing = ctx.hero.facing
      ctx.hero.facing = (0, 1)
      not ctx.anims and ctx.anims.append([])
      ctx.anims[0].append(ItemAnim(
        target=target,
        item=item(),
        duration=60,
        on_end=lambda: (
          setattr(ctx.hero, "facing", old_facing),
          on_end and on_end(),
        )
      ))
      ctx.comps.minilog.print(message=("Obtained ", item().token(), "."))
    return obtained

  def handle_pickup(ctx):
    if not ctx.hero:
      return False
    return ctx.pickup_item(actor=ctx.hero)

  def pickup_item(ctx, actor, itemdrop=None):
    if not actor or actor.item:
      return False

    facing_cell = vector.add(actor.cell, actor.facing)
    target_elems = ctx.stage.get_elems_at(facing_cell)
    itemdrop = itemdrop or next((e for e in target_elems if isinstance(e, ItemDrop)), None)
    if not itemdrop or next((e for e in target_elems if e.solid), None):
      return False

    ctx.stage.remove_elem(itemdrop)
    ctx.hero.item = itemdrop.item
    ctx.anims.append([AttackAnim(
      target=ctx.hero,
      src=ctx.hero.cell,
      dest=facing_cell
    )])
    return False

  def handle_place(ctx):
    if not ctx.hero:
      return False
    return ctx.place_item(actor=ctx.hero)

  def place_item(ctx, actor):
    if not actor or not actor.item:
      return False

    facing_cell = vector.add(actor.cell, actor.facing)
    if (Tile.is_solid(ctx.stage.get_tile_at(facing_cell))
    or next((e for e in ctx.stage.get_elems_at(facing_cell) if
      isinstance(e, ItemDrop)
      or not isinstance(e, DungeonActor)
      and e.solid
    ), None)):
      return False

    ctx.stage.spawn_elem_at(facing_cell, ItemDrop(actor.item))
    actor.item = None
    not ctx.anims and ctx.anims.append([AttackAnim(
      target=actor,
      src=actor.cell,
      dest=facing_cell,
    )])
    return True

  def handle_carry(ctx, item):
    if not ctx.hero:
      return False, "No character to use!"
    return ctx.carry_item(actor=ctx.hero, item=item)

  def carry_item(ctx, actor, item):
    if actor.item:
      return False, "You can't carry any more."
    actor.item = item
    return True, None

  def handle_throw(ctx):
    return ctx.throw_item(actor=ctx.hero)

  def find_throw_target(ctx, actor):
    target_elem = None
    target_cell = actor.cell
    nonpit_cell = actor.cell

    throwing = True
    while throwing:
      next_cell = vector.add(target_cell, actor.facing)
      next_tile = ctx.stage.get_tile_at(next_cell)
      next_elem = next((e for e in ctx.stage.get_elems_at(next_cell) if
        e.solid
        and not (ctx.hero and ctx.ally and actor is ctx.hero and e is ctx.ally)
      ), None)

      if (not isinstance(next_tile, tileset.Pit) and Tile.is_solid(next_tile)
      or next((e for e in ctx.stage.get_elems_at(next_cell) if (
        e.solid
        and not isinstance(e, DungeonActor)
        and not isinstance(e, ItemDrop)
      )), None)):
        throwing = False
        break
      elif next_elem:
        target_elem = next_elem
        throwing = False

      target_cell = next_cell
      if not isinstance(next_tile, tileset.Pit):
        nonpit_cell = next_cell

    if not isinstance(ctx.stage.get_tile_at(target_cell), tileset.Pit):
      target_cell = nonpit_cell

    return target_cell, target_elem

  def throw_item(ctx, actor, item=None):
    if not item and not actor.item:
      return False
    item = actor.item
    target_cell, target_elem = ctx.find_throw_target(actor)

    if target_cell == actor.cell:
      ctx.anims.append([AttackAnim(
        target=actor,
        src=actor.cell,
        dest=vector.add(actor.cell, actor.facing),
      )])
      return False

    def handle_effect():
      ctx.anims[0].append(PauseAnim(
        duration=30,
        on_end=ctx.camera.blur
      ))
      if "effect" in dir(item) and target_elem and isinstance(target_elem, DungeonActor):
        response = item().effect(ctx, actor=target_elem, cell=target_cell)
        response and ctx.log.print(response)
        ctx.stage.remove_elem(itemdrop)
      elif item.fragile:
        item().effect(ctx, cell=target_cell)
        ctx.stage.remove_elem(itemdrop)
      else:
        itemdrop.cell = target_cell

    def handle_throw():
      actor.item = None
      ctx.stage.spawn_elem_at(actor.cell, itemdrop)
      ctx.anims[0].append(ItemDrop.ThrownAnim(
        target=itemdrop,
        src=actor.cell,
        dest=target_cell,
        on_end=handle_effect,
      ))
      ctx.camera.focus(upscale(target_cell, ctx.stage.tile_size), force=True)

    itemdrop = ItemDrop(item)
    ctx.anims.append([
      AttackAnim(
        target=actor,
        src=actor.cell,
        dest=vector.add(actor.cell, actor.facing),
        on_connect=handle_throw
      )
    ])
    return True

  def update_bubble(ctx):
    facing_elem = ctx.facing_elem
    pending_anims = [a for g in ctx.anims for a in g if not a.done]

    can_show_bubble = not pending_anims and not ctx.hero.item and not (ctx.child and ctx.child.child)
    if ctx.talkbubble and ctx.talkbubble.target is facing_elem and can_show_bubble:
      return

    if ctx.talkbubble:
      ctx.talkbubble.done = True

    if facing_elem and can_show_bubble:
      ctx.vfx.append(TalkBubble(
        target=facing_elem,
        cell=facing_elem.cell,
        flipped=ctx.camera.is_pos_beyond_yrange(pos=vector.scale(facing_elem.cell, ctx.stage.tile_size)),
      ))

  def darken(ctx):
    ctx.stage_view.darken()
    ctx.stage_view.redraw_tiles(hero=ctx.hero, visited_cells=ctx.visited_cells)

  def undarken(ctx):
    ctx.stage_view.undarken()
    ctx.stage_view.redraw_tiles(hero=ctx.hero, visited_cells=ctx.visited_cells)
