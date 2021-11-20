from contexts import Context
from contexts.explore.stageview import StageView

class DungeonContext(Context):
  def __init__(ctx, stage):
    ctx.stage = None
    ctx.stage_view = StageView()
