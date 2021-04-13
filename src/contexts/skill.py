from contexts import Context
from comps.bar import Bar

class SkillContext(Context):
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close

  def draw(ctx, surface):
    game = ctx.parent # may not always be true
    hero = game.hero
    print(hero.cell, hero.facing)
