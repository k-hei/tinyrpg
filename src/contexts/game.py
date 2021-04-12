from contexts import Context
from transits.dissolve import DissolveIn, DissolveOut

class GameContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.transits = []
    ctx.inited = False

  def dissolve(ctx, on_clear):
    ctx.transits.append(DissolveIn(surface, on_clear))
    ctx.transits.append(DissolveOut(surface))

  def handle_keydown(ctx, key):
    if len(ctx.transits):
      return False
    return super().render(surface)

  def render(ctx, surface):
    if not ctx.inited:
      ctx.inited = True
      ctx.transits.append(DissolveOut(surface))
    super().render(surface)
    if len(ctx.transits):
      transit = ctx.transits[0]
      transit.update()
      transit.render()
      if transit.done:
        ctx.transits.remove(transit)
