import assets
from dungeon.floors import Floor
from dungeon.gen import gen_floor

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      rooms=[
        assets.rooms["exit"],
        assets.rooms["oasis"],
        assets.rooms["mageboss"],
        assets.rooms["emerald"],
      ],
      seed=seed
    )
