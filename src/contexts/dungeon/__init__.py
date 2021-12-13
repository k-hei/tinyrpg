import pygame
from lib.cell import neighborhood
import lib.vector as vector
import lib.input as input

from contexts.explore import ExploreContext
from contexts.explore.base import ExploreBase
from contexts.explore.stageview import StageView
from contexts.combat import CombatContext
from comps.hud import Hud
from comps.minilog import Minilog
from comps.minimap import Minimap
from comps.skillbanner import SkillBanner
from dungeon.actors.knight import Knight
from dungeon.props.door import Door
from dungeon.fov import shadowcast
from dungeon.room import Blob as Room
import tiles.default as tileset
from anims.pause import PauseAnim
from anims.step import StepAnim
from config import WINDOW_HEIGHT, VISION_RANGE

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

  def enter(ctx):
    hero = Knight(core=ctx.store.party[0])
    stage_entrance = next((cell for cell, tile in ctx.stage.tiles.enumerate() if issubclass(tile, tileset.Entrance)), None)
    if stage_entrance:
      ctx.stage.spawn_elem_at(stage_entrance, hero)
    else:
      raise LookupError("Failed to find Entrance tile to spawn hero")

    ctx.comps = [
      Hud(party=ctx.store.party, hp=True),
      Minilog(pos=(8, WINDOW_HEIGHT - 8 - Minilog.sprite.get_height() / 2)),
      Minimap(
        stage=ctx.stage,
        hero=ctx.hero,
        visited_cells=ctx.visited_cells
      ),
      SkillBanner()
    ]
    ctx.handle_explore()

  def handle_press(ctx, button):
    if input.get_state(pygame.K_LCTRL):
      if button == pygame.K_c:
        return print(ctx.anims)

    if ctx.child:
      return ctx.child.handle_press(button)

  def refresh_fov(ctx):
    room = next((r for r in ctx.stage.rooms if ctx.hero.cell in r.cells + r.border), None)
    if room:
      visible_cells = room.cells + room.visible_outline
      ctx.camera.focus(room)
      if room not in ctx.rooms:
        ctx.rooms.append(room)
    else:
      visible_cells = shadowcast(ctx.stage, ctx.hero.cell, VISION_RANGE)
      room = next((t for t in ctx.camera.target if isinstance(t, Room)), None)
      if room:
        ctx.camera.blur(room)
      ctx.camera.focus(ctx.hero)

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

    update_visible_cells = lambda: (
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
      update_visible_cells(),
      isinstance(ctx.child, CombatContext) and not ctx.find_enemies_in_range() and ctx.child.exit(),
    )

    handle_end = lambda: (
      ctx.refresh_fov(),
    )

    ctx.hero.cell = hallway[-1]
    tween_duration = ctx.camera.tween(
      target=[room, ctx.hero],
      force=True
    )
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

  def handle_explore(ctx):
    ctx.open(ExploreContext(
      store=ctx.store,
      stage=ctx.stage,
      stage_view=ctx.stage_view,
    ), on_close=ctx.handle_combat)
    ctx.minimap.enter()

  def handle_combat(ctx):
    ctx.open(CombatContext(
      store=ctx.store,
      stage=ctx.stage,
      stage_view=ctx.stage_view,
    ), on_close=ctx.handle_explore)
    ctx.minimap.exit()
    ctx.hud.enter()

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
