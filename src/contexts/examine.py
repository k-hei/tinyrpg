from assets import load as use_assets

class ExamineContext:
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close

  def draw(ctx, surface):
    pass
