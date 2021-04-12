from contexts import Context
from transits.dissolve import DissolveIn, DissolveOut
import config

class GameContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.transits = [DissolveOut(config.window_size)]

  def dissolve(ctx, on_clear):
    ctx.transits.append(DissolveIn(config.window_size, on_clear))
    ctx.transits.append(DissolveOut(config.window_size))

  def handle_keydown(ctx, key):
    if len(ctx.transits):
      return False
    return super().handle_keydown(key)

  def render(ctx, surface):
    super().render(surface)
    if len(ctx.transits):
      transit = ctx.transits[0]
      transit.update()
      transit.render(surface)
      if transit.done:
        ctx.transits.remove(transit)
