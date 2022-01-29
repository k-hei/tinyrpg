from random import random
from lib.cell import manhattan, upscale, downscale
import lib.vector as vector
import lib.input as input
from lib.direction import invert as invert_direction, normal as normalize_direction
from helpers.findactor import find_actor
from contexts import Context
from anims.item import ItemAnim
from anims.step import StepAnim
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.jump import JumpAnim
from items.materials import MaterialItem
from dungeon.actors import DungeonActor
from dungeon.props.itemdrop import ItemDrop
from tiles import Tile
import tiles.default as tileset
from vfx.talkbubble import TalkBubble
from config import MOVE_DURATION, PUSH_DURATION, SKILL_BADGE_POS_SOLO, SKILL_BADGE_POS_ALLY

COMMAND_MOVE = "move"
COMMAND_MOVE_TO = "move_to"
COMMAND_ATTACK = "attack"
COMMAND_SKILL = "use_skill"
COMMAND_WAIT = "wait"

class ExploreBase(Context):
  def __init__(ctx, store=None, stage=None, stage_view=None, time=0, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = store
    ctx.stage = stage
    ctx.stage_view = stage_view
    ctx.time = time
    ctx.buttons_rejected = {}

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
    if "_room" not in dir(ctx) or not ctx._room:
      ctx._room = ctx.hero and ctx.find_room(ctx.hero.cell)
    return ctx._room

  @room.setter
  def room(ctx, room):
    ctx._room = room

  def find_room(ctx, cell):
    return next((r for r in ctx.stage.rooms if cell in r.cells), None)

  @property
  def visited_cells(ctx):
    stage_id = ctx.graph.nodes.index(ctx.stage)
    visited_cells = ctx.memory[stage_id] if stage_id in ctx.memory else None # next((cs for (s, cs) in ctx.memory if s is ctx.stage), None)
    if visited_cells is None:
      ctx.memory[stage_id] = (visited_cells := [])
    return visited_cells

  def extend_visited_cells(ctx, cells):
    if cells != ctx.visited_cells:
      ctx.visited_cells.extend([c for c in cells if c not in ctx.visited_cells])

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
  def graph(ctx):
    return ctx._graph if "_graph" in dir(ctx) else ctx.parent.graph

  @graph.setter
  def graph(ctx, graph):
    ctx._graph = graph

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
    if not ctx.hero:
      return None
    facing_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    facing_elems = ctx.stage.get_elems_at(facing_cell)
    return next((e for e in facing_elems if (
      e.active
      and not e.expires
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

  def reload_skill_badge(ctx, delay=0):
    if not ctx.hero:
      return
    ctx.comps.skill_badge.pos = SKILL_BADGE_POS_ALLY if ctx.store.ally else SKILL_BADGE_POS_SOLO
    ctx.comps.skill_badge.reload(skill=ctx.store.get_selected_skill(ctx.hero.core), delay=delay)

  def move_cell(ctx, actor, delta, duration=0, jump=False, fixed=True, on_end=None):
    target_cell = vector.add(actor.cell, delta)
    target_tile = ctx.stage.get_tile_at(target_cell)
    origin_tile = ctx.stage.get_tile_at(actor.cell)
    if (not Tile.is_walkable(target_tile)
    or abs(target_tile.elev - origin_tile.elev) >= 1):
      return False

    target_elem = (
      next((e for e in ctx.stage.get_elems_at(target_cell) if e.solid), None)
      or next((e for e in ctx.stage.get_elems_at(target_cell)), None)
    )

    if target_elem and target_elem.solid and not (target_elem is ctx.ally and not ctx.ally.command):
      return False

    move_command = (actor, (COMMAND_MOVE, delta))
    has_command_queue = "command_queue" in dir(ctx)
    has_command_queue and ctx.command_queue.append(move_command)

    move_src = actor.cell if fixed else downscale(actor.pos, ctx.stage.tile_size)
    move_dest = target_cell if fixed else vector.add(move_src, delta)
    move_duration = duration or MOVE_DURATION
    move_duration = move_duration * 1.5 if jump else move_duration
    move_kind = JumpAnim if jump else StepAnim
    move_anim = move_kind(
      target=actor,
      src=move_src,
      dest=move_dest,
      duration=move_duration,
      on_end=lambda: (
        has_command_queue and move_command in ctx.command_queue and ctx.command_queue.remove(move_command),
        on_end and on_end(),
      )
    )
    move_anim.update() # initial update to ensure walk animation loops seamlessly

    move_group = next((g for g in ctx.anims for a in g if isinstance(a, StepAnim) and isinstance(a.target, DungeonActor)), None)
    not move_group and ctx.anims.append(move_group := [])
    move_group.append(move_anim)
    if jump:
      ctx.anims[-1].append(PauseAnim(duration=move_duration + 5))

    ctx.update_bubble()
    actor.cell = target_cell
    actor.facing = normalize_direction(delta)
    actor.command = move_command

    if target_elem and target_elem is ctx.ally:
      ctx.move_cell(actor=ctx.ally, delta=invert_direction(delta))

    return True

  def handle_push(ctx):
    target_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    target_elem = next((e for e in ctx.stage.get_elems_at(target_cell) if e.solid and not e.static), None)
    if not target_elem:
      return False

    return ctx.push(
      actor=ctx.hero,
      target=target_elem,
      on_end=lambda: (
        ctx.update_bubble(),
        "step" in dir(ctx) and ctx.step(),
      )
    )

  def push(ctx, actor, target, on_end=None):
    src_cell = target.cell
    dest_cell = vector.add(src_cell, actor.facing)
    dest_tile = ctx.stage.get_tile_at(dest_cell)
    dest_elem = next((e for e in ctx.stage.get_elems_at(dest_cell) if e.solid), None)
    if (target.static
    or dest_tile is None
    or dest_tile.solid
    or dest_tile.pit
    or dest_elem):
      return False

    target.cell = dest_cell
    ctx.move_cell(actor, delta=actor.facing, duration=PUSH_DURATION, fixed=False, on_end=on_end)
    not ctx.anims and ctx.anims.append([])
    ctx.anims[-1].extend([
      StepAnim(
        target=target,
        src=src_cell,
        dest=dest_cell,
        duration=PUSH_DURATION,
      ),
      PauseAnim(duration=15)
    ])
    target.on_push(ctx)
    return True

  def handle_obtain(ctx, item, target, on_start=None, on_end=None):
    if not ctx.hero:
      return False

    obtained = ctx.store.obtain(item)
    if obtained:
      old_facing = ctx.hero.facing
      ctx.hero.facing = (0, 1)
      hero_group = next((g for g in ctx.anims for a in g if a.target is ctx.hero), [])
      hero_index = ctx.anims.index(hero_group) if hero_group in ctx.anims else -1
      next_anim_group = []
      ctx.anims.insert(hero_index + 1, next_anim_group) if hero_group in ctx.anims else ctx.anims.append(next_anim_group)
      next_anim_group.append(ItemAnim(
        target=target,
        item=item(),
        duration=60,
        on_start=lambda: (
          ctx.comps.minilog.print(message=("Obtained ", item().token(), ".")),
          on_start and on_start(),
        ),
        on_end=lambda: (
          setattr(ctx.hero, "facing", old_facing),
          on_end and on_end(),
        )
      ))
    return obtained

  def handle_pickup(ctx):
    if not ctx.hero:
      return False
    success = ctx.pickup_item(actor=ctx.hero)
    ctx.update_bubble()
    return success

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
    ctx.buttons_rejected[input.get_latest_button()] = 0
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
        response and ctx.comps.minilog.print(response)
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

  def use_item(ctx, item, discard=True):
    hero = ctx.hero
    if not hero:
      return False, "The hero is dead!"

    carry_item = hero.item
    if carry_item and item and carry_item is not item:
      return False, "Your hands are full!"
    elif carry_item and not discard:
      item = carry_item
      hero.item = None

    if not item:
      return False, "No item to use."

    if discard:
      ctx.anims.append([
        ItemAnim(
          duration=30,
          target=hero,
          item=item()
        ),
        PauseAnim(duration=60),
      ])

    if issubclass(item, MaterialItem):
      success, message = False, "You can't use this item!"
    else:
      success, message = ctx.store.use_item(item, discard=discard)

    if success is False:
      ctx.anims.pop()
      return False, message
    elif success is True:
      ctx.comps.minilog.print(("Used", item.token(item)))
      ctx.comps.minilog.print(message)
      return True, ""
    else:
      return None, ("Used ", item.token(item), "\n", message)

  def recruit_actor(game, actor):
    actor.reset_charge()
    game.store.recruit(actor.core)

  def update(ctx):
    super().update()
    ctx.update_buttons_rejected()
    ctx.time += 1

  def update_buttons_rejected(ctx):
    for button in ctx.buttons_rejected:
      ctx.buttons_rejected[button] += 1

  def update_bubble(ctx):
    if not ctx.hero:
      if ctx.talkbubble:
        ctx.talkbubble.done = True
      return

    facing_elem = ctx.facing_elem
    facing_cell = facing_elem and facing_elem.cell
    if not facing_elem:
      facing_cell = ctx.hero.cell
      facing_tile = ctx.stage.get_tile_at(facing_cell)
      if facing_tile and issubclass(facing_tile, (tileset.Entrance, tileset.Exit)):
        facing_elem = facing_tile

    pending_anims = [a for g in ctx.anims for a in g if not a.done]

    can_show_bubble = not pending_anims and not ctx.hero.item and not (ctx.child and ctx.child.child)
    if ctx.talkbubble and ctx.talkbubble.target is facing_elem and can_show_bubble:
      return

    if ctx.talkbubble:
      ctx.talkbubble.done = True

    if facing_elem and can_show_bubble:
      ctx.vfx.append(TalkBubble(
        target=facing_elem,
        cell=facing_cell,
        flipped=ctx.camera.is_pos_beyond_yrange(pos=vector.scale(facing_cell, ctx.stage.tile_size)),
      ))

  def darken(ctx):
    ctx.stage_view.darken()
    ctx.redraw_tiles()

  def undarken(ctx):
    ctx.stage_view.undarken()
    ctx.redraw_tiles()

  def redraw_tiles(ctx):
    ctx.stage_view.redraw_tiles(hero=ctx.hero, visited_cells=ctx.visited_cells)
