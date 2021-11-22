from contexts import Context
from contexts.combat import CombatContext
from contexts.explore import ExploreContext
from contexts.explore.stageview import StageView
from contexts.dungeon.camera import Camera
from config import WINDOW_SIZE

class DungeonContext(Context):
  def __init__(ctx, store, stage, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = store
    ctx.stage = stage
    ctx.camera = Camera(WINDOW_SIZE)
    ctx.stage_view = StageView(stage=stage, camera=ctx.camera)

  def enter(ctx):
    ctx.handle_explore()

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

  def update(ctx):
    for elem in ctx.stage.elems:
      elem.update(ctx)

    ctx.camera.update()
    ctx.stage_view.update()
    super().update()

  def view(ctx):
    return ctx.stage_view.view()
