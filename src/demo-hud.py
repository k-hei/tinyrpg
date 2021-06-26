from contexts import Context
from contexts.app import App
from comps.hud import Hud
from cores.knight import Knight
from sprite import Sprite

class HudContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.hud = Hud(party=[Knight()], hp=True)

  def update(ctx):
    ctx.hud.update()

  def view(ctx):
    return ctx.hud.view()

App(
  title="hud demo",
  context=HudContext()
).init()
