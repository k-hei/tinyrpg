import config
from contexts import Context
from contexts.dungeon import DungeonContext
from contexts.town import TownContext
from transits.dissolve import DissolveIn, DissolveOut

class GameContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.transits = [DissolveOut(config.WINDOW_SIZE)]

  def goto_dungeon(ctx):
    ctx.child = DungeonContext(parent=ctx)

  def goto_town(ctx):
    ctx.child = TownContext(parent=ctx)

  def dissolve(ctx, on_clear, on_end=None):
    ctx.transits.append(DissolveIn(config.WINDOW_SIZE, on_clear))
    ctx.transits.append(DissolveOut(config.WINDOW_SIZE, on_end))

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
