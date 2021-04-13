from contexts import Context

class SkillContext(Context):
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close

  def draw(ctx, surface):
    print(ctx.parent.hero.cell)
