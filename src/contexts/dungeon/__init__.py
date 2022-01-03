import pygame
from lib.cell import neighborhood
import lib.vector as vector
import lib.input as input

from contexts.explore import ExploreContext
from contexts.explore.base import ExploreBase
from contexts.explore.stageview import StageView
from contexts.combat import CombatContext
from comps.store import ComponentStore
from comps.damage import DamageValue
from comps.hud import Hud
from comps.minilog import Minilog
from comps.minimap import Minimap
from comps.skillbanner import SkillBanner
from comps.spmeter import SpMeter
from dungeon.actors.knight import Knight
from dungeon.actors.mage import Mage
from dungeon.props.door import Door
from dungeon.props.palm import Palm
from dungeon.fov import shadowcast
from dungeon.room import Blob as Room
import tiles.default as tileset
from anims.pause import PauseAnim
from anims.step import StepAnim
from anims.warpin import WarpInAnim
from colors.palette import GREEN, CYAN
from config import WINDOW_HEIGHT, VISION_RANGE

def manifest_actor(core):
  core_id = type(core).__name__
  core_actors = {
    "Knight": Knight,
    "Mage": Mage,
  }
  return core_actors[core_id](core) if core_id in core_actors else None

class DungeonContext(ExploreBase):
  def __init__(ctx, store, stage, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = store
    ctx.stage = stage
    ctx.stage_view = StageView(stage)
    ctx.memory = {}
    ctx.hero_cell = None
    ctx.hero_facing = None
    ctx.comps = []
    ctx.rooms = []
    ctx.rooms_entered = set()

  def enter(ctx):
    heroes = [manifest_actor(c) for c in ctx.store.party]
    stage_entrance = ctx.stage.entrance or next((cell for cell, tile in ctx.stage.tiles.enumerate() if issubclass(tile, tileset.Entrance)), None)
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
      skill_banner=SkillBanner(),
      sp_meter=SpMeter(store=ctx.store),
    )
    ctx.handle_explore()

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

  def refresh_fov(ctx):
    room_entered = next((r for r in ctx.stage.rooms if ctx.hero.cell in r.cells), None)
    if room_entered and room_entered not in ctx.rooms_entered:
      ctx.rooms_entered.add(room_entered)
      room_entered.on_enter(ctx)

    room_focused = next((r for r in ctx.stage.rooms if ctx.hero.cell in r.cells + r.border), None)
    if room_focused:
      visible_cells = room_focused.cells + room_focused.visible_outline
      ctx.camera.focus(room_focused)
      if room_focused not in ctx.rooms:
        ctx.rooms.append(room_focused)
        room_focused.on_focus(ctx)
    else:
      visible_cells = shadowcast(ctx.stage, ctx.hero.cell, VISION_RANGE)
      room_focused = next((t for t in ctx.camera.target if isinstance(t, Room)), None)
      if room_focused:
        ctx.camera.blur(room_focused)
      ctx.camera.focus(ctx.hero)
    visible_cells += neighborhood(ctx.hero.cell)

    ctx.hero.visible_cells = visible_cells
    ctx.extend_visited_cells(visible_cells)

  def handle_hallway(ctx):
    hallway = ctx.find_hallway(ctx.hero.cell)
    room = next((r for r in ctx.stage.rooms if hallway[-1] in r.edges), None)
    door = next((e for e in ctx.stage.get_elems_at(hallway[-1]) if isinstance(e, Door)), None)
    if door and not door.opened:
      door.open()

    rooms = [*ctx.rooms, *([room] if room else [])]
    rooms_cells = [c for r in rooms for c in r.cells]
    rooms_borders = [c for r in rooms for c in r.border]

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
    ), on_close=ctx.handle_combat)
    ctx.comps.minimap.enter()

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
    ctx.comps.hud.enter()
    ctx.comps.sp_meter.enter()

  def extend_visited_cells(ctx, cells):
    ctx.visited_cells.extend([c for c in cells if c not in ctx.visited_cells])

  def update_hero_cell(ctx):
    if ctx.hero_cell == ctx.hero.cell:
      return

    is_travelling = False
    if ctx.hero_cell:
      old_door = next((e for e in ctx.stage.get_elems_at(ctx.hero_cell) if isinstance(e, Door)), None)
      new_door = next((e for e in ctx.stage.get_elems_at(ctx.hero.cell) if isinstance(e, Door)), None)
      new_tile = ctx.stage.get_tile_at(ctx.hero.cell)

      if issubclass(new_tile, tileset.Hallway) and (new_door or old_door) and not (new_door and old_door):
        ctx.handle_hallway()
        is_travelling = True
        step_anim = next((a for g in ctx.anims for a in g if a.target is ctx.hero and isinstance(a, StepAnim)), None)
        if step_anim:
          step_anim.done = True

      if issubclass(new_tile, tileset.Oasis):
        ctx.handle_oasis()

      if ctx.find_enemies_in_range():
        ctx.handle_combat(path=True)

    ctx.hero_cell = ctx.hero.cell
    ctx.update_bubble()

    if not is_travelling:
      ctx.refresh_fov()

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
