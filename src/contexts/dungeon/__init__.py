from contexts import Context
from contexts.combat import CombatContext
from contexts.explore import ExploreContext
from contexts.explore.stageview import StageView
from contexts.dungeon.camera import Camera
from dungeon.fov import shadowcast
from helpers.findactor import find_actor
from config import WINDOW_SIZE, VISION_RANGE

class DungeonContext(Context):
  def __init__(ctx, store, stage, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = store
    ctx.stage = stage
    ctx.camera = Camera(WINDOW_SIZE)
    ctx.memory = []
    ctx.stage_view = StageView(stage=stage, camera=ctx.camera)
    ctx.hero_cell = None

  @property
  def hero(ctx):
    return find_actor(
      char=ctx.store.party[0],
      stage=ctx.stage
    ) if ctx.store.party else None

  @property
  def visited_cells(ctx):
    visited_cells = next((cs for s, cs in ctx.memory if s is ctx.stage), None)
    if not visited_cells:
      ctx.memory.append((ctx.stage, visited_cells := []))
    return visited_cells

  def enter(ctx):
    ctx.handle_explore()

  def refresh_fov(ctx):
    ctx.hero.visible_cells = shadowcast(ctx.stage, ctx.hero.cell, VISION_RANGE)
    ctx.update_visited_cells(ctx.hero.visible_cells)

  def handle_explore(ctx):
    ctx.open(ExploreContext(
      store=ctx.store,
      stage=ctx.stage,
      stage_view=ctx.stage_view,
      on_end=ctx.handle_combat,
    ))

  def handle_combat(ctx):
    ctx.open(CombatContext(
      store=ctx.store,
      stage=ctx.stage,
      stage_view=ctx.stage_view,
      on_end=ctx.handle_explore,
    ))

  def update_visited_cells(ctx, cells):
    ctx.visited_cells.extend([c for c in cells if c not in ctx.visited_cells])

  def update(ctx):
    for elem in ctx.stage.elems:
      elem.update(ctx)

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
    ) + super().view()
