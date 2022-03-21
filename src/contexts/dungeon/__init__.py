import pygame
from copy import deepcopy
from lib.cell import neighborhood
import lib.vector as vector
import lib.input as input
import debug

from contexts.explore import ExploreContext
from contexts.explore.base import ExploreBase
from contexts.explore.stageview import StageView
from contexts.combat import CombatContext, animate_snap
from comps.store import ComponentStore
from comps.damage import DamageValue
from comps.hud import Hud
from comps.minilog import Minilog
from comps.minimap import Minimap
from comps.miniskill import Miniskill as SkillBadge
from comps.skillbanner import SkillBanner
from comps.spmeter import SpMeter
from comps.floorno import FloorNo
from dungeon.fov import shadowcast
from dungeon.room import Blob as Room
from dungeon.actors import DungeonActor
from dungeon.props.door import Door
from dungeon.props.palm import Palm
from dungeon.data import DungeonData
from helpers.actor import manifest_actor
from helpers.stage import find_tile
from locations.default.tile import Tile
import locations.default.tileset as tileset
from anims.pause import PauseAnim
from anims.step import StepAnim
from anims.warpin import WarpInAnim
from colors.palette import GREEN, CYAN
from config import WINDOW_HEIGHT, VISION_RANGE

from dungeon.floors.floor1 import Floor1
from dungeon.floors.floor2 import Floor2
from dungeon.floors.floor3 import Floor3
from dungeon.floors.genericfloor import GenericFloor
from dungeon.gen.floorgraph import FloorGraph
from helpers.stage import find_tile

FLOOR_SEQUENCE = [Floor1, Floor2, Floor3]

class DungeonContext(ExploreBase):
  def __init__(ctx, store, stage, floor_index=0, graph=None, memory=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = store
    ctx.stage = stage
    ctx.stage_view = StageView(stage)
    ctx.floor_index = floor_index
    ctx.graph = graph
    ctx.memory = memory or {}
    ctx.hero_cell = None
    ctx.hero_facing = None
    ctx.comps = []
    ctx.rooms = []
    ctx.rooms_entered = set()
    ctx.cache_room_focused = None
    ctx.cache_room_entered = None

  def enter(ctx):
    heroes = [manifest_actor(c) for c in ctx.store.party]
    stage_entrance = ctx.stage.entrance or find_tile(ctx.stage, tileset.Entrance)
    if stage_entrance:
      for i, hero in enumerate(heroes):
        ctx.stage.spawn_elem_at(stage_entrance, hero)
        hero.pos = vector.add(hero.pos, (0, -i))
    else:
      raise LookupError("Failed to find Entrance tile to spawn hero")

    ctx.comps = ComponentStore(
      hud=Hud(party=ctx.store.party, hp=True),
      minilog=Minilog(pos=(8, WINDOW_HEIGHT - 8 - Minilog.sprite.get_height() / 2)),
      minimap=Minimap(parent=ctx),
      skill_badge=SkillBadge(ctx.store.get_selected_skill(ctx.hero.core)),
      skill_banner=SkillBanner(),
      sp_meter=SpMeter(store=ctx.store),
      floor_no=FloorNo(parent=ctx),
    )
    ctx.construct_graph()
    ctx.handle_explore()

  def find_floor_no(ctx):
    floor = next((f for f in FLOOR_SEQUENCE if f.__name__ == ctx.stage.generator), None)
    if floor is None:
      return 0
    return FLOOR_SEQUENCE.index(floor) + 1

  def save(ctx):
    return DungeonData(
      floor_index=ctx.graph.nodes.index(ctx.stage),
      floors=deepcopy(ctx.graph),
      memory=deepcopy(ctx.memory),
    )

  def construct_graph(ctx):
    floor_names = [f.__name__ for f in FLOOR_SEQUENCE]

    if not ctx.stage: # or ctx.stage.generator not in floor_names:
      return

    ctx.graph = ctx.graph or FloorGraph()
    ctx.graph.nodes.append(ctx.stage)

    try:
      prev_floor = FLOOR_SEQUENCE[floor_names.index(ctx.stage.generator) - 1]
    except (ValueError, IndexError):
      prev_floor = None

    try:
      next_floor = FLOOR_SEQUENCE[floor_names.index(ctx.stage.generator) + 1]
    except (ValueError, IndexError):
      next_floor = GenericFloor

    stage_entrance = ctx.stage.entrance or find_tile(ctx.stage, tileset.Entrance)
    stage_entrance and prev_floor and ctx.graph.connect(ctx.stage, prev_floor, stage_entrance)

    stage_exit = find_tile(ctx.stage, tileset.Exit)
    stage_exit and next_floor and ctx.graph.connect(ctx.stage, next_floor, stage_exit)

  def use_stage(ctx, stage, stairs=None):
    ctx.hero and ctx.stage.remove_elem(ctx.hero)
    ctx.ally and ctx.stage.remove_elem(ctx.ally)

    ctx.stage = stage
    ctx.construct_graph()
    ctx.parent.save()

    heroes = [manifest_actor(c) for c in ctx.store.party]
    stage_entrance = find_tile(stage, stairs) if stairs else stage.entrance
    if stage_entrance:
      for i, hero in enumerate(heroes):
        stage.spawn_elem_at(stage_entrance, hero)
        hero.pos = vector.add(hero.pos, (0, -i))
    else:
      raise LookupError("Failed to find Entrance tile to spawn hero")

    ctx.child.stage = stage
    ctx.stage_view.stage = stage
    ctx.stage_view.reset_cache()
    ctx.comps.minimap.sprite = None
    ctx.time = 0
    ctx.camera.reset()
    ctx.camera.focus(ctx.hero)
    ctx.cache_room_focused = None
    ctx.cache_room_entered = None
    ctx.refresh_fov()
    ctx.redraw_tiles()

  def refresh_fov(ctx, reset_cache=False):
    hero = ctx.hero
    if not hero:
      return False

    room_entered = next((r for r in ctx.stage.rooms if hero.cell in r.cells), None)
    if room_entered is not ctx.cache_room_entered:
      ctx.cache_room_entered = room_entered
      if room_entered:
        room_entered not in ctx.rooms_entered and ctx.rooms_entered.add(room_entered)
        if room_entered.has_hook("on_enter") or room_entered.get_enemies(ctx.stage):
          animate_snap(
            actor=hero,
            anims=ctx.anims,
            on_end=lambda: room_entered.on_enter(ctx),
          )

    room_focused = next((r for r in ctx.stage.rooms if hero.cell in (r.cells)), None) # + r.border)), None)
    if room_focused:
      visible_cells = room_focused.cells + room_focused.visible_outline
      if room_focused not in ctx.camera.target:
        ctx.camera.focus(room_focused)
      if room_focused not in ctx.rooms:
        ctx.rooms.append(room_focused)
        room_focused.on_focus(ctx)
    else:
      visible_cells = shadowcast(ctx.stage, hero.cell, VISION_RANGE)
      room_focused = next((t for t in ctx.camera.target if isinstance(t, Room)), None)
      if room_focused:
        ctx.camera.blur(room_focused)
      ctx.camera.focus(hero)

    visible_cells += neighborhood(hero.cell)

    if ctx.cache_room_focused is not room_focused or reset_cache:
      ctx.cache_room_focused = room_focused
      hero.visible_cells = visible_cells
      ctx.extend_visited_cells(visible_cells)

  def handle_press(ctx, button):
    if input.get_state(pygame.K_LCTRL):
      if button == pygame.K_c:
        return print(
          ctx.anims,
          *([ctx.hero.anims] if ctx.hero else []),
          *([ctx.ally.anims] if ctx.ally else [])
        )

      if button == pygame.K_t:
        return print(ctx.camera.target_groups)

    if ctx.child:
      return ctx.child.handle_press(button)

  def handle_hallway(ctx):
    hallway = ctx.find_hallway(ctx.hero.cell)
    room = next((r for r in ctx.stage.rooms if hallway[-1] in r.edges), None)
    door = next((e for e in ctx.stage.get_elems_at(hallway[-1]) if isinstance(e, Door)), None)
    if door:
      if not door.opened:
        door.open()
      if door.hidden:
        door.hidden = False

    rooms = [*ctx.rooms, *([room] if room else [])]
    rooms_cells = [c for r in rooms for c in r.cells]
    rooms_borders = [] # [c for r in rooms for c in r.border]

    illuminate_hallway = lambda: (
      setattr(ctx.hero, "visible_cells", [
        *set([
          n for c in hallway
            for n in neighborhood(c, diagonals=True) + [
              n for n in neighborhood(vector.add(c, (0, -1)))
                if n not in rooms_borders
            ] if n not in rooms_cells
        ])
      ]),
      ctx.extend_visited_cells(ctx.hero.visible_cells)
    )

    handle_start = lambda: (
      illuminate_hallway(),
      ctx.child.handle_hallway(),
      setattr(ctx.stage_view, "transitioning", True),
    )

    handle_end = lambda: (
      setattr(ctx.stage_view, "transitioning", False),
      ctx.refresh_fov(),
    )

    ctx.hero.cell = hallway[-1]
    if ctx.ally:
      ctx.ally.cell = hallway[-2]
      ctx.ally.facing = vector.subtract(hallway[-1], hallway[-2])

    tween_duration = ctx.camera.tween(target=[room, ctx.hero])
    if tween_duration:
      not ctx.anims and ctx.anims.append([])
      ctx.anims[0].append(PauseAnim(
        target=ctx,
        duration=tween_duration,
        on_start=handle_start,
      ))
    else:
      handle_start()

    room_cells = room.cells + room.visible_outline
    if room not in ctx.rooms:
      ctx.anims.extend([
        [PauseAnim(
          target=ctx,
          duration=15,
          on_start=lambda: ctx.extend_visited_cells(room_cells),
          on_end=handle_end,
        )]
      ])
    elif tween_duration:
      ctx.anims[0][-1].on_end = handle_end
    else:
      handle_end()

  def find_hallway(ctx, cell):
    if not issubclass(ctx.stage.get_tile_at(cell), tileset.Hallway):
      return []

    hallways = []
    stack = []
    for neighbor in neighborhood(cell, diagonals=True):
      if issubclass(ctx.stage.get_tile_at(neighbor), tileset.Hallway):
        hallway = [cell]
        hallways.append(hallway)
        stack.append((hallway, neighbor))

    if not hallways:
      return []

    while stack:
      hallway, cell = stack.pop()
      hallway.append(cell)
      neighbors = [n for n in neighborhood(cell) if (
        issubclass(ctx.stage.get_tile_at(n), tileset.Hallway)
        and n not in hallway
      )]
      for neighbor in neighbors:
        stack.append((hallway, neighbor))

    if len(hallways) == 1:
      return hallways[0]

    hallways.sort(key=len)
    return list(reversed(hallways[0]))[:-1] + hallways[1]

  def handle_oasis(ctx):
    ctx.handle_restore()

  def handle_restore(ctx):
    if (ctx.store.sp == ctx.store.sp_max
    and (not ctx.hero
      or ctx.hero.hp == ctx.hero.hp_max
      and ctx.hero.ailment == None)
    and (not ctx.ally
      or ctx.ally.hp == ctx.ally.hp_max
      and ctx.ally.ailment == None)
    ):
      return False

    palm = next((e for e in ctx.stage.elems if type(e) is Palm), None)
    if not palm:
      return False
    palm.vanish(ctx)

    if len(ctx.store.party) == 2:
      if not ctx.ally:
        ally_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
        ally = manifest_actor(ctx.store.party[1])
        ally.revive()
        ctx.stage.spawn_elem_at(ally_cell, ally)
        not ctx.anims and ctx.anims.append([])
        ctx.anims[-1].append(WarpInAnim(target=ally))
      ctx.comps.minilog.print("The party's HP and SP are restored.")
    else:
      ctx.comps.minilog.print("Your HP and SP are restored.")

    ctx.store.sp = ctx.store.sp_max
    ctx.hero and ctx.restore_actor(ctx.hero)
    ctx.ally and ctx.restore_actor(ctx.ally)

    ctx.comps.hud.enter()
    not ctx.anims and ctx.anims.append([])
    ctx.anims[-1].append(PauseAnim(
      duration=180,
      on_end=ctx.comps.hud.exit
    ))

    return True

  def restore_actor(ctx, actor):
    actor.hp = actor.hp_max
    actor.dispel_ailment()
    ctx.vfx.append(DamageValue(
      text=ctx.store.sp_max,
      pos=actor.pos,
      color=CYAN,
    ))
    ctx.vfx.append(DamageValue(
      text=actor.hp_max,
      pos=vector.add(actor.pos, (0, -8)),
      color=GREEN,
    ))

  def handle_explore(ctx):
    ctx.open(ExploreContext(
      store=ctx.store,
      stage=ctx.stage,
      stage_view=ctx.stage_view,
      time=ctx.time,
    ), on_close=ctx.handle_combat)
    ctx.comps.minimap.enter()
    ctx.comps.floor_no.enter()

  def handle_combat(ctx, path=False):
    if type(ctx.child) is CombatContext:
      return

    ctx.open(CombatContext(
      store=ctx.store,
      stage=ctx.stage,
      stage_view=ctx.stage_view,
      path=path,
    ), on_close=ctx.handle_explore)
    ctx.comps.minimap.exit()
    ctx.comps.floor_no.exit()
    ctx.comps.hud.enter()
    ctx.comps.sp_meter.enter()
    if type(ctx.get_tail()) is CombatContext:
      ctx.reload_skill_badge(delay=30)

  def update_hero_cell(ctx):
    if ctx.hero_cell == ctx.hero.cell:
      return

    is_travelling = False
    if ctx.hero_cell:
      old_door = next((e for e in ctx.stage.get_elems_at(ctx.hero_cell) if isinstance(e, Door)), None)
      new_door = next((e for e in ctx.stage.get_elems_at(ctx.hero.cell) if isinstance(e, Door) and e.opened), None)
      new_tile = ctx.stage.get_tile_at(ctx.hero.cell)

      if ctx.stage.is_tile_at_hallway(ctx.hero_cell) and (new_door or old_door) and not (new_door and old_door):
        ctx.handle_hallway()
        is_travelling = True
        step_anim = next((a for g in ctx.anims for a in g if a.target is ctx.hero and isinstance(a, StepAnim)), None)
        if step_anim:
          step_anim.done = True

    if not is_travelling:
      ctx.refresh_fov()

    if ctx.hero_cell:
      if ctx.stage.is_tile_at_oasis(ctx.hero_cell):
        ctx.handle_oasis()

      if ctx.find_enemies_in_range() and isinstance(ctx.get_tail(), (ExploreContext, CombatContext)):
        ctx.handle_combat(path=True)

    ctx.hero_cell = ctx.hero.cell
    ctx.update_bubble()

    if ctx.room and ctx.room.has_hook("on_walk"):
      ctx.room.on_walk(ctx, cell=ctx.hero_cell)
      # animate_snap(
      #   actor=ctx.hero,
      #   anims=ctx.anims,
      #   on_end=lambda: ctx.room.on_walk(ctx, cell=ctx.hero_cell)
      # )

  def update(ctx):
    for elem in ctx.stage.elems:
      ctx.vfx.extend(elem.update(ctx) or [])

    for comp in ctx.comps:
      comp.update()

    if ctx.hero and ctx.hero_facing != ctx.hero.facing:
      ctx.hero_facing = ctx.hero.facing
      ctx.update_bubble()

    if ctx.hero and ctx.hero_cell != ctx.hero.cell:
      ctx.update_hero_cell()

    ctx.camera.update()
    ctx.stage_view.update()
    super().update()

  def view(ctx):
    return ctx.stage_view.view(
      hero=ctx.hero,
      visited_cells=ctx.visited_cells,
    ) + [c.view() for c in ctx.comps] + super().view()
