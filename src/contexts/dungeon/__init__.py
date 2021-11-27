import assets
from helpers.findactor import find_actor
from contexts import Context
from contexts.combat import CombatContext
from contexts.explore import ExploreContext
from contexts.explore.stageview import StageView
from contexts.dungeon.camera import Camera
from comps.minilog import Minilog
from comps.minimap import Minimap
from dungeon.fov import shadowcast
from dungeon.room import Blob as Room
from config import WINDOW_SIZE, WINDOW_HEIGHT, VISION_RANGE

class DungeonContext(Context):
  def __init__(ctx, store, stage, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = store
    ctx.stage = stage
    ctx.camera = Camera(WINDOW_SIZE)
    ctx.memory = {}
    ctx.stage_view = StageView(stage=stage, camera=ctx.camera)
    ctx.hero_cell = None
    ctx.comps = [
      Minilog(pos=(8, WINDOW_HEIGHT - 8 - Minilog.sprite.get_height() / 2)),
      Minimap(
        stage=stage,
        hero=ctx.hero,
        visited_cells=ctx.visited_cells
      )
    ]

  @property
  def hero(ctx):
    return find_actor(
      char=ctx.store.party[0],
      stage=ctx.stage
    ) if ctx.store.party else None

  @property
  def visited_cells(ctx):
    stage_id = ctx.stage.__hash__()
    visited_cells = ctx.memory[stage_id] if stage_id in ctx.memory else None # next((cs for (s, cs) in ctx.memory if s is ctx.stage), None)
    if visited_cells is None:
      ctx.memory[stage_id] = (visited_cells := [])
    return visited_cells

  @property
  def minilog(ctx):
    return next((c for c in ctx.comps if type(c) is Minilog), None)

  @property
  def minimap(ctx):
    return next((c for c in ctx.comps if type(c) is Minimap), None)

  def enter(ctx):
    ctx.handle_explore()

  def refresh_fov(ctx):
    room = next((r for r in ctx.stage.rooms if ctx.hero.cell in r.cells), None)
    if room:
      visible_cells = room.cells + room.visible_outline
      ctx.camera.focus(room)
    else:
      visible_cells = shadowcast(ctx.stage, ctx.hero.cell, VISION_RANGE)
      room = next((t for t in ctx.camera.target if isinstance(t, Room)), None)
      if room:
        ctx.camera.blur(room)
      ctx.camera.focus(ctx.hero)

    ctx.hero.visible_cells = visible_cells
    ctx.update_visited_cells(visible_cells)

  def handle_explore(ctx):
    ctx.open(ExploreContext(
      store=ctx.store,
      stage=ctx.stage,
      stage_view=ctx.stage_view,
      on_end=ctx.handle_combat,
    ))
    ctx.minimap.enter()

  def handle_combat(ctx):
    ctx.open(CombatContext(
      store=ctx.store,
      stage=ctx.stage,
      stage_view=ctx.stage_view,
      on_end=ctx.handle_explore,
    ))
    ctx.minimap.exit()

  def update_visited_cells(ctx, cells):
    ctx.visited_cells.extend([c for c in cells if c not in ctx.visited_cells])

  def update(ctx):
    for elem in ctx.stage.elems:
      elem.update(ctx)

    for comp in ctx.comps:
      comp.update()

    if ctx.hero.cell != ctx.hero_cell:
      ctx.hero_cell = ctx.hero.cell
      ctx.refresh_fov()

    ctx.camera.update()
    ctx.stage_view.update()
    super().update()

  def view(ctx):
    return ctx.stage_view.view(
      hero=ctx.hero,
      visited_cells=ctx.visited_cells,
    ) + [c.view() for c in ctx.comps] + super().view()
