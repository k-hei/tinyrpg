from lib.cell import neighborhood

from contexts.explore import ExploreContext
from contexts.explore.base import ExploreBase
from contexts.explore.stageview import StageView
from contexts.combat import CombatContext
from comps.hud import Hud
from comps.minilog import Minilog
from comps.minimap import Minimap
from dungeon.actors.knight import Knight
from dungeon.props.door import Door
from dungeon.fov import shadowcast
from dungeon.room import Blob as Room
import tiles.default as tileset
from anims.pause import PauseAnim
from vfx.talkbubble import TalkBubble
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
      )
    ]
    ctx.handle_explore()

  def refresh_fov(ctx):
    room = next((r for r in ctx.stage.rooms if ctx.hero.cell in r.cells + r.border), None)
    if room:
      visible_cells = room.cells + room.visible_outline
      ctx.camera.focus(room)
    else:
      visible_cells = shadowcast(ctx.stage, ctx.hero.cell, VISION_RANGE)
      room = next((t for t in ctx.camera.target if isinstance(t, Room)), None)
      if room:
        ctx.camera.blur(room)
      ctx.camera.focus(ctx.hero)
    ctx.rooms.append(room)

    ctx.hero.visible_cells = visible_cells
    ctx.update_visited_cells(visible_cells)

  def handle_hallway(ctx):
    hallway = ctx.find_hallway(ctx.hero.cell)
    room = next((r for r in ctx.stage.rooms if hallway[-1] in r.edges), None)
    door = next((e for e in ctx.stage.get_elems_at(hallway[-1]) if isinstance(e, Door)), None)
    if door and not door.opened:
      door.open()

    ctx.hero.cell = hallway[-1]
    ctx.hero.visible_cells = [n for c in hallway for n in neighborhood(c, inclusive=True)]
    ctx.update_visited_cells(ctx.hero.visible_cells)

    tween_duration = ctx.camera.tween(
      target=[room, ctx.hero],
      force=True
    )
    if tween_duration:
      not ctx.anims and ctx.anims.append([])
      ctx.anims[0].append(PauseAnim(duration=tween_duration))

    room_cells = room.cells + room.visible_outline
    if room not in ctx.rooms:
      ctx.anims.extend([
        [PauseAnim(
          duration=15,
          on_start=lambda: ctx.update_visited_cells(room_cells),
          on_end=ctx.refresh_fov
        )]
      ])
    elif tween_duration:
      ctx.anims[0][-1].on_end = ctx.refresh_fov
    else:
      ctx.refresh_fov()

  def find_hallway(ctx, cell):
    if not issubclass(ctx.stage.get_tile_at(cell), tileset.Hallway):
      return []

    hallways = []
    stack = []
    for neighbor in neighborhood(cell):
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

  def update_hero_cell(ctx):
    is_travelling = False
    if ctx.hero_cell:
      old_door = next((e for e in ctx.stage.get_elems_at(ctx.hero_cell) if isinstance(e, Door)), None)
      new_door = next((e for e in ctx.stage.get_elems_at(ctx.hero.cell) if isinstance(e, Door)), None)
      new_tile = ctx.stage.get_tile_at(ctx.hero.cell)
      if issubclass(new_tile, tileset.Hallway) and (new_door or old_door):
        ctx.handle_hallway()
        is_travelling = True

    ctx.hero_cell = ctx.hero.cell
    ctx.update_bubble()

    if not is_travelling:
      ctx.refresh_fov()

  def update_bubble(ctx):
    facing_elem = ctx.facing_elem
    pending_anims = [a for g in ctx.anims for a in g if not a.done]

    can_show_bubble = not pending_anims and not ctx.hero.item and not ctx.child.child
    if ctx.talkbubble and ctx.talkbubble.target is facing_elem and can_show_bubble:
      return

    if ctx.talkbubble:
      ctx.talkbubble.done = True

    if facing_elem and can_show_bubble:
      ctx.vfx.append(TalkBubble(
        target=facing_elem,
        cell=facing_elem.cell,
      ))

  def update_visited_cells(ctx, cells):
    ctx.visited_cells.extend([c for c in cells if c not in ctx.visited_cells])

  def update(ctx):
    for elem in ctx.stage.elems:
      elem.update(ctx)

    for comp in ctx.comps:
      comp.update()

    if ctx.hero_facing != ctx.hero.facing:
      ctx.hero_facing = ctx.hero.facing
      ctx.update_bubble()

    if ctx.hero.cell != ctx.hero_cell:
      ctx.update_hero_cell()

    ctx.camera.update()
    ctx.stage_view.update()
    super().update()

  def view(ctx):
    return ctx.stage_view.view(
      hero=ctx.hero,
      visited_cells=ctx.visited_cells,
    ) + [c.view() for c in ctx.comps] + super().view()
