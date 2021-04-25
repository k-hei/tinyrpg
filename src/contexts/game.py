import config
from contexts import Context
from contexts.dungeon import DungeonContext
from transits.dissolve import DissolveIn, DissolveOut

class GameContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.child = DungeonContext(parent=ctx)
    ctx.transits = [DissolveOut(config.window_size)]

  def dissolve(ctx, on_clear, on_end=None):
    ctx.transits.append(DissolveIn(config.window_size, on_clear))
    ctx.transits.append(DissolveOut(config.window_size, on_end))

  def handle_keydown(ctx, key):
    if len(ctx.transits):
      return False
    return super().handle_keydown(key)

  def draw(ctx, surface):
    super().draw(surface)
    if len(ctx.transits):
      transit = ctx.transits[0]
      transit.update()
      transit.draw(surface)
      if transit.done:
        ctx.transits.remove(transit)
