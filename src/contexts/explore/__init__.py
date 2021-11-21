import lib.input as input
from contexts import Context
from contexts.explore.stageview import StageView

class ExploreContext(Context):
  def __init__(ctx, stage=None, stage_view=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.hero = None
    ctx.stage = stage
    ctx.stage_view = stage_view or StageView(stage=stage)

  def handle_press(ctx, button):
    delta = input.resolve_delta(button)
    if delta:
      return ctx.handle_move(delta)

  def handle_move(ctx, delta):
    if not ctx.hero:
      return

    ctx.hero.move(delta)

  def update(ctx):
    for elem in ctx.stage.elems:
      elem.update(ctx)

  def view(ctx):
    return ctx.stage_view.view()
